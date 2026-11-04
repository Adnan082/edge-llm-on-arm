# Architecture — edge-llm-on-arm

> How the parts of this repo fit together: what runs where, which files carry data from
> one step to the next, and the rules that keep the results honest. The spec (`CLAUDE.md`)
> says *what* we measure and *why*; this file says *how* the code is arranged to do it.
>
> **Status: Day 8.** Set-up (`env`, `build`, `models`, `check-builds`), `make bandwidth`,
> `make peak`, `make predict`, `make bench SET=pilot|full`, `make analyse`, `make figures`,
> `make micro` (+ `make micro-table`), the Day 8 investigation (`make day8-variants`, `make day8`,
> `make day8-analyse`), `make test` and `make lint` exist. The micro code is
> written and tested without hardware; its first timings come from the VM. When code changes the
> design, update this file in the same commit.

---

## 1. The big picture

The project is a pipeline: set up, then four steps, plus one side test. Each line shows a
program, what it produces, and where the result is saved.

```
 0. SET UP  (VM)
    infra/setup_vm.sh       ──► tools, llama.cpp clone     → work/llama.cpp/
    bench/env_capture.py    ──► machine details            → results/raw/env/
    infra/build_llamacpp.sh ──► baseline + kleidiai builds → work/build-*/
                                build record, flags        → results/raw/build/
    infra/make_models.sh    ──► HF → F16 → Q8_0, Q4_0, Q4_K_M → work/models/
    edge_llm/gguf_table.py  ──► model sizes, per tensor    → results/models/
    bench/check_builds.py   ──► is KleidiAI active? which buffer holds which
                                weights (smoke runs)       → results/raw/build/
                 │
                 ▼
 1. MEASURE THE CHIP  (VM)
    bench/bandwidth/        ──► B(t): memory speed         → results/raw/bandwidth/
    micro/peak.cpp          ──► C(t): maths speed          → results/raw/peak/
                 │
                 ▼
 2. PREDICT  (anywhere; committed before step 3 starts)
    edge_llm/roofline.py    ──► predicted tokens/s         → results/predictions/
                 │
                 ▼
 3. MEASURE THE MODELS  (VM)
    bench/run_sweep.py      ──► llama-bench, every point   → results/raw/bench/
                 │
                 ▼
 4. COMPARE  (anywhere)
    edge_llm/analyse.py     ──► measured ÷ predicted       → results/processed/
    edge_llm/plots.py       ──► charts                     → figures/
                 │
                 ▼
    README.md + report/REPORT.md  (every number cites a config_id)

 SIDE TEST, RQ4  (VM)
    micro/dot_int8.cpp      ──► which instructions help    → results/raw/micro/
```

`edge_llm/` is short for `src/edge_llm/`. `t` is the number of threads.

**Where code runs.**

- **The cloud VM** (Google Cloud C4A, Google Axion) runs everything that touches the hardware
  or the model files.
- **Anywhere** — your laptop or GitHub Actions — runs predict, analyse, figures and tests,
  because they read only files committed to the repo.

Results travel from the VM to the repo by committing and pushing from the VM.
Big things that are never committed — the llama.cpp clone, both builds, the model files —
live in `work/`, which is gitignored.

## 2. The steps

### Step 0 — Set up (VM)

On a fresh VM, run `bash infra/setup_vm.sh` by hand first: it installs `make`,
the compilers and Python, and clones llama.cpp at the pinned commit into `work/`. Then:

- `make env` — `bench/env_capture.py` saves the machine's details and **starts the session**:
  it writes the new `session_id` to `work/session_id`, and every later step of the same
  sitting (`bandwidth`, `build`, `check-builds`, the sweep) reuses it. It also runs
  automatically at the start of every sweep session.
- `make build` — `infra/build_llamacpp.sh` builds llama.cpp twice from the same commit,
  `baseline` and `kleidiai`; the only difference is `-DGGML_CPU_KLEIDIAI=ON`. It stops if the
  two CMake caches differ in anything else, and `bench/build_record.py` writes the build
  record (commit, CMake options, the real compiler flags from `compile_commands.json`,
  KleidiAI version/URL/hash, the KleidiAI lines of the configure log). Only `llama-bench`,
  `llama-quantize` and `llama-completion` are built.
- `make models` — `infra/make_models.sh` downloads each model's safetensors at the pinned
  revision (`infra/hf_fetch.py` checks every file against the Hub's hashes), converts to F16
  in its own venv, makes every other format listed in `sweep.yaml` with `llama-quantize`
  (default settings), and records each file's SHA256 in `work/models/SHA256SUMS`. Each model
  file has a `.cmd` sidecar with the command that made it. Then `gguf_table.py` writes each
  file's shape numbers and per-tensor sizes to `results/models/`. From here on, nothing
  downstream needs the model files.
- `make check-builds` — `bench/check_builds.py` runs a tiny llama-bench (smoke run) of every
  model file on both builds and records which buffer type (`CPU_KLEIDIAI`, `CPU_REPACK`,
  `CPU_Mapped`) holds how many MiB, plus each build's system-info line from
  `llama-completion` (llama-bench does not print one). Smoke records say
  `use_for_analysis: false`; their speeds are never used.

### Step 1 — Measure the chip (VM)

- `make bandwidth PHASE=start|end` — `bench/bandwidth/` measures memory speed at every thread
  count with a read-only kernel (the roofline input) and a STREAM-style triad (for
  comparison). The read kernel has eight variants: 8 or 16 accumulators × k = 1, 2, 4, 8
  interleaved streams per thread (ADR-017, ADR-021). At one thread every variant also runs on
  a 32 KiB buffer (fits in L1; repeated passes so a repetition lasts at least 10 ms); a variant
  is valid if its L1 median is at least 1.5× its 1 GiB median, i.e. the loop itself is not the
  limit. `B(t)` is the best 1 GiB median over the valid variants, `B1(t)` the best valid one
  at k = 1, and the winning variant at each t is recorded; the run fails only if no variant is
  valid. `edge_llm/bandwidth.py` computes all of it. Huge-page runs at t = 1 and 8 are
  diagnostics and never enter `B(t)`. Each thread count runs under `taskset -c 0-(t-1)` with thread i pinned
  to core i. Sweep sessions run it at their start and end, so drift is visible.
- `make peak` — `micro/run_peak.py` builds `micro/peak.cpp`, disassembles every hot loop
  into `micro/disasm/` and checks it (expected instruction, expected count, no memory
  access), then measures maths speed `C(t)` at every thread count for each instruction
  class: `SDOT`, `SMMLA`, FP16 `FMLA`, `FMLALB`+`FMLALT` (ADR-015) and F32 `FMLA` (`fma32`,
  the ceiling for attention; ADR-020). The program reports
  instructions per second; `edge_llm/peak.py` holds the operations per instruction (the one
  place those constants live) and turns them into operations per second. It also counts the
  `fmlalb`, `fmlalt` and `fmla .8h` instructions in each build's ggml CPU library and, in the
  same objdump pass, saves the disassembly of the tiled flash-attention function (or what it
  was inlined into) to `micro/disasm/ggml_flash_attn_tiled_<build>.s` and counts scalar
  `fmadd s` against vector `fmla .4s` in it (ADR-020: did the compiler vectorise the plain-C
  fallback?).

### Step 2 — Predict (anywhere)

- `make predict` — `roofline.py` combines `B(t)`, `C(t)` and the tensor tables into a
  predicted tokens/s for every point of the full sweep (144: the small model only, ADR-024),
  using the formulas in spec §8. `B(t)` is the best valid read variant of one named bandwidth
  record; `C(t)` is t × the 90th percentile of the one-thread repetitions × operations per
  instruction (ADR-023) from one named peak record. Both records are constants at the top of
  `roofline.py`. A second, informational prediction uses the sustained (mean) ceilings.
- The result, `results/predictions/v1.csv`, is committed **before** step 3 starts.
  `v1.meta.json` names the input files with their SHA256s, the repo commit, the ADRs and the
  `B` and `C` values that won.

### Step 3 — Measure the models (VM)

- `make bench` — `run_sweep.py` calls llama-bench once per point (`config_id`, §3). The
  baseline and kleidiai versions of a point run back to back, and which one goes first
  alternates from point to point.
- Each call writes one raw JSON file: `results/raw/bench/<session_id>/<config_id>.json`. The
  command line spells out every fixed setting from `sweep.yaml: bench_settings` (ADR-019) and
  the pinning (`taskset -c 0-(t-1)`, `-t t`, `--cpu-mask`, `--cpu-strict 1`; ADR-014). Points
  already done in the session are skipped, so a crashed run resumes: records are written to a
  temporary file and renamed into place, so a crash or VM restart never leaves a half file.
  Resume with the same `make bench SET=full`, and without `make env` (that starts a new session). If IQR/median of a
  point's repetitions is above 5 %, the point is run once more after its pair and saved as
  `<config_id>__2.json`; both files stay.
- `make bench SET=pilot` runs the small Day-3 pilot listed in the same `sweep.yaml`, then
  writes `_pilot_summary.md` and `.json` next to its records: the repeat noise of every point
  and an estimate of the full sweep's wall time (`edge_llm/pilot.py` states the method).

### Step 4 — Compare (anywhere)

- `make analyse` (`SESSION=<id>`, default `2026-11-02T2215Z`) — `analyse.py` loads every point
  record of the session and validates it with `schema.py`, then takes the median and IQR of the
  per-repetition `samples_ts` (never llama-bench's mean ± stddev; `stats.py`). One named rule
  chooses between a point's attempts, `RERUN_RULE` (`apply_rerun_rule`, spec §7.4): attempt 1 if
  it is not noisy; else attempt 2 if it exists, flagged `still_noisy` if that is noisy too; a
  noisy point that was never re-run is flagged `still_noisy` and warned about. Both files stay
  on disk. It joins the points to `results/predictions/v1.csv` on `config_id` and stops with an
  error if either side has a point the other lacks. Each row gets `ratio = measured / predicted`,
  `ratio_sustained` (against the sustained-ceiling prediction), the rates the measured speed
  implies (`achieved_GBps`, `achieved_GOPS`, `fraction_of_B`, `fraction_of_C`), and
  `ratio_session_B`: the same prediction with only its memory term recomputed from this
  session's own bandwidth (median of the start and end records' best valid read variant). v1
  stays the headline; `ratio_session_B` is a sensitivity check. Printout: ratio spread per
  phase, noisy points, and a `WARNING` for every ratio above 1 (spec §8). It never opens
  `results/raw/env/<session>_end.json` (that capture is missing for this session).
- `make figures` — `plots.py` draws five figures from `results/processed/` only, as PNG and
  SVG into `figures/`: `predicted_vs_measured` (headline), `kleidiai_speedup`, `thread_scaling`,
  `roofline`, `ratio_breakdown`; and, if `micro.csv` exists, a sixth, `dot_int8` (RQ4). Fixed
  sizes and fonts and no timestamps in the metadata, so two runs give byte-identical files.
- README.md and `report/REPORT.md` quote numbers from `results/processed/` by `config_id`.

### Side test, RQ4 — `make micro` (VM)

The kernel is a decode-shaped int8 matrix–vector product, `y[m] = Σ_k W[m][k]·x[k]`, with
K = 4096 (a row's int32 sum cannot overflow), on **one core** (thread 0 on core 0, ADR-014),
because RQ4 is compared with `B(1)` and `C(1)`. Two working sets: **L1** (4 rows, W = 16 KiB; the
call is repeated until a repetition lasts ≥ 10 ms) and **DRAM** (262144 rows, W = 1 GiB, at least
4× the 80 MiB L3).

- `micro/dot_int8_ref.cpp` is the plain-C loop, compiled twice by `run_micro.py`: as `dot_scalar`
  with auto-vectorisation off (`-fno-tree-vectorize`) and as `dot_autovec` with plain `-O3`
  (whatever GCC picks is recorded, and is a finding).
- `micro/dot_int8.cpp` holds the SIMD variants and the harness: `sdot_a4/a8` (NEON `SDOT`),
  `smmla_a4/a8` (i8mm `SMMLA` on a 2-row tile: it multiplies 2 weight rows by **2 activation
  vectors** at once, so it does twice the MACs per weight byte of the others; weights and the two
  vectors are packed into its layout before timing), `sve_a4/a8` (SVE `SDOT`, vector length read
  at run time). 4 and 8 independent accumulators are both run and the best is reported (the
  ADR-022 rule). `--check` runs every variant against scalar on random and extreme (−128 / 127)
  inputs, bit for bit (SMMLA against scalar for two vectors; scalar itself against a 64-bit
  reference). `--time` times the variants and compares each timed output with scalar's too.
- `micro/run_micro.py` (`make micro`): build → `--check` (**timing is refused if any variant
  differs**) → disassemble every kernel into `micro/disasm/dot_int8_<variant>.s` and check its hot
  loop (found by conditional backward branches only, like `peak.py`): the expected instruction ×
  accumulators in the loop (`sdot` v-form, `smmla`, `sdot` z-form), no SIMD multiply anywhere in
  scalar, auto-vec only recorded → time → save `results/raw/micro/<session_id>.json`. A failed
  loop check leaves the variant out of "best" and fails the run, but the record is kept.
- `edge_llm/micro.py` holds the constants, the loop check, and the arithmetic (no hardware), and
  `python -m edge_llm.micro` (`make micro-table`) turns the newest raw record into
  `results/processed/micro.csv`: GMAC/s (useful MACs), weight GB/s (the like-for-like rate),
  ratio to scalar both per MAC and per weight byte, share of slow repetitions, and fractions of
  `C(1)` (L1: median and the p90 rate that `C(1)` is built from) and of `B(1)` / `B₁(1)` (DRAM).

### Day 8 investigation — one check per KleidiAI surprise (ADR-025)

Labelled "Day 8 investigation": it never enters the v1 comparison or the headline figure
(`analyse.py` reads only the sweep session). It runs in the **same VM session as Day 7**, so there is
no new `make env`. The logic is in `edge_llm/day8.py` (no hardware, tested in CI); the VM driver is
`bench/day8.py`.

- **Check A** (surprise 2: does the Q6_K output layer explain Q4_K_M's decode gain?).
  `make day8-variants` (`infra/make_variants.sh`) makes `small_Q4_0outq8.gguf` and
  `small_Q4_0outq4.gguf` with the pinned `llama-quantize --output-tensor-type q8_0 | q4_0` from
  `small_F16.gguf`, records their SHA256s like `make_models.sh`, and `bench.day8 tables` writes their
  tensor tables and **refuses** unless `output.weight` has the intended type and every other tensor
  matches `small_Q4_0`. `make day8` then runs tg128 at t = 1 and 8, both builds, for `small_Q4_0`
  (measured again), `_outq8` and `_outq4` through `run_sweep.run_pair` (same `bench_settings`,
  pinning, alternating build order, re-run rule). Records: `results/raw/bench/<session_id>/
  small_Q4_0outq8_kleidiai_t1_tg128.json` etc., validated by `BenchRecord`; a `_day8_check_a.json`
  manifest names the points and the prediction. The prediction (written before the first run, in
  `day8.py`): the KleidiAI decode speed-up is clearly smaller for both variants than for Q4_0.
- **Check B** (surprises 1 and 3: is the prefill difference a fixed cost per call?). No VM:
  `kleidiai.csv` for Q4_0 and Q8_0 → `results/processed/day8_check_b.csv` (time per prompt in both
  builds, `delta_t = baseline − kleidiai`, with range) and `day8_check_b_fit.csv` (a fixed + per-token
  fit, and the growth of `delta_t` from P = 128 to 2048: 1 = fixed cost, 16 = per token).
- **Check C** (only if `perf` works, at most 30 min): `perf record` of pp128 at t = 1 for Q4_0 and
  Q8_0 on both builds, 20 repetitions so the profile is dominated by prompt processing. Event
  `cycles`, else `cpu-clock`. The top 20 of `perf report --stdio --no-children --sort dso,symbol`
  go to `results/raw/perf/<session_id>/<config_id>.perf_report.txt` and `.json` (`use_for_analysis:
  false`: the tokens/s inside a perf run is not data). If perf is missing or cannot sample, one
  `_perf_unavailable.json` says so and the step ends. `perf.data` files stay in `work/perf/`.
- `make day8-analyse` (anywhere) prints Check B, and Checks A and C when the session's records are
  present (`DAY8_SESSION=<id>`, default `work/session_id`) → `results/processed/day8_check_a.csv`.

## 3. Names that tie everything together

- **`session_id`** — one sitting on the VM, named by its UTC start time
  (`YYYY-MM-DDTHHMMZ`). Every raw file belongs to one session; the session's machine
  details are in `results/raw/env/<session_id>.json`.
- **`config_id`** — one measured point: `<model>_<quant>_<build>_t<threads>_<test>`, for
  example `small_Q4_0_kleidiai_t8_pp512`. `<model>` is the alias set in `sweep.yaml`
  (`small` or `large`), so IDs stay the same if the model family changes.
- **`pair_id`** — a `config_id` without the build, e.g. `small_Q4_0_t8_pp512`. It joins
  the baseline and kleidiai runs of the same point to give a speed-up.

## 4. Files that carry data between steps

Exact fields are defined in `src/edge_llm/schema.py`; this is the overview.

**Written by hand**

- `configs/sweep.yaml` — read by `run_sweep.py` and `roofline.py`. Model aliases (`small`,
  `large` → file, source, SHA256), which of them the full sweep runs (`full.models`: `small`
  only, ADR-024), formats, builds, thread counts, tests, repetitions, slow points, pruned
  points with reasons, and the pilot subset.
- `configs/machine.yaml` — machine type, zone, price, date, VM hours.

**Inputs to the prediction**

- `results/models/<model>_<quant>.json` — from `gguf_table.py`, read by `roofline.py`.
  One per model file: SHA256; number of layers, heads and KV heads; head size; vocabulary
  size; whether embeddings are tied; for every tensor its name, type, shape, parameter
  count, bytes and role; totals per role (`W_blk`, `N_blk`, `W_out`, `N_out`, ...); the mix
  of tensor types; and the source (Hugging Face revision, the commands used). The role is
  `blk` (matmul weights inside `blk.*`), `out` (the output projection: `output.weight`, or
  the token-embedding table when embeddings are tied), `emb` (an untied embedding table) or
  `other` (1-D norm vectors and `rope_freqs`; under 1 % of the bytes, kept in `W_other` so
  that can be checked). `results/models/convert_pip_freeze.txt` pins the converter's packages.
- `results/raw/bandwidth/<session_id>_<start|end>.json` — from `bench/bandwidth/`, read by
  `roofline.py` and `analyse.py`. One pass over every thread count: kernel, streams per
  thread (k), buffer size, pinning (and the `sched_getcpu()` check), at least 20 samples in
  bytes/s with median, IQR and max, compile flags, load average before/after. Next to it,
  `..._read_loop.s` is the disassembly of the eight read loops; the record's `validity` holds
  the per-variant L1 check (L1 median, 1 GiB median, ratio, valid), the winners, and each
  loop's vector loads and stack accesses (information, not a limit; only
  a missing loop or one without vector loads is an error). Records from before ADR-021 have
  one variant (8 accumulators, k = 1) and an `acc_check` instead.
- `results/raw/peak/<session_id>.json` — from `micro/run_peak.py`, read by `roofline.py`.
  Per instruction class and thread count: the independent chains in the loop (8, 16 and 28,
  all run at every thread count), at least 20 samples in instructions/s and in operations/s,
  median, IQR and max, the pin check; the disassembly check of every hot loop; compile
  flags. `C(t)` (the record's `c_of_t`, ADR-022) is the best median over the chain counts
  whose loop passed the disassembly check, with the winning count and every median kept as
  information; the schema recomputes it from the points. The record is written before any
  failure is reported: a loop that fails its check is left out of `C(t)` and makes the run
  exit non-zero, but the data are kept. Next to it, `<session_id>_ggml_f16_instructions.json` counts `fmlalb`,
  `fmlalt` and `fmla .8h` in each build's ggml library (evidence for ADR-015) and the
  scalar/vector F32 FMA counts of the tiled attention function (ADR-020); the
  disassembly itself is committed in `micro/disasm/peak_<class>.s`.

**The prediction**

- `results/predictions/v1.csv` — from `roofline.py`, read by `analyse.py`. One row per
  `config_id`: bytes, FLOPs, the `B` and `C` used, predicted tokens/s, and which limit
  binds (`memory` or `compute`). `v1.meta.json` next to it lists the exact input files.

**Measurements**

- `results/raw/env/<session_id>.json` — from `env_capture.py`. Everything listed in spec
  §7, item 1. `dirty` in this and every other record counts only changes outside `results/` and
  `micro/disasm/`
  (one helper, `bench/common.py: git_state`), so adding result files does not make later
  records look dirty.
- `results/raw/build/<session_id>_build.json` — from `bench/build_record.py` (`make build`).
- `results/raw/build/<session_id>_check_builds.json` — from `bench/check_builds.py`. Smoke
  runs of both builds; **not** read by `analyse.py`.
- `results/raw/bench/<session_id>/<config_id>.json` (and `<config_id>__2.json` for the re-run
  of a noisy point) — from `run_sweep.py`, read by `analyse.py`. llama-bench's own JSON output,
  stored unchanged under `llama_bench`, plus session, repo and llama.cpp commit, model
  SHA256 (from `work/models/SHA256SUMS`, size checked against the tensor table), the exact
  command, pinning, load average before and after, wall seconds, the build order in the pair,
  and the median/IQR/noisy flag computed from the per-repetition `samples_ts`. Files whose
  name starts with `_` in that folder (`_pilot_summary.*`) are not points.
- `results/raw/micro/<session_id>.json` — from `micro/run_micro.py`, read by `edge_llm.micro`.
  The compile commands, the `--check` result, per variant and working set (`L1` / `DRAM`) at
  least 30 per-repetition samples in ns per call (and calls per repetition, pinning, whether the
  timed output matched scalar), the disassembly check of every hot loop (instruction counts, the
  loop's instructions, the `.s` file), and the **named and hashed** bandwidth record (the newest
  valid one) and peak record (the roofline's) with the `B(1)`, `B₁(1)`, `C_sdot(1)` and
  `C_smmla(1)` taken from them. It holds measurements and references, not derived ratios.

**Results**

- `results/processed/points.csv` — from `analyse.py`, read by `plots.py`, README and REPORT.
  One row per `config_id`, sorted: median, Q1, Q3, IQR, IQR/median, which attempt was used
  (`attempt_used`), `noisy_first_attempt`, `still_noisy`, the raw file it came from
  (`source_file`); the v1 prediction and its inputs, copied from `v1.csv`; `ratio`,
  `ratio_sustained`, `ratio_session_B`; `arith_intensity` (operations per byte) and the achieved
  rates.
- `results/processed/kleidiai.csv` — one row per `pair_id`: both builds' median, Q1, Q3,
  IQR/median and noisy flag; `speedup` = kleidiai ÷ baseline median; the conservative range
  `speedup_lo` = kleidiai Q1 ÷ baseline Q3 and `speedup_hi` = kleidiai Q3 ÷ baseline Q1; and
  `coverage` (F16 negative control, Q4_K_M partial, Q4_0 and Q8_0 full; ADR-013).
- `results/processed/session_bandwidth.csv` — `B(t)` at the start and end of the sweep session
  (best valid read variant), drift in %, the session's `B(t)` (median of the two) and its ratio
  to the `B(t)` that v1 used.
- `results/processed/micro.csv` — from `python -m edge_llm.micro`, read by `plots.py` (RQ4). One
  row per variant and working set; `is_best` marks the fastest accumulator count of each family
  among the variants whose loop check passed; the reference values it was divided by are columns.
- Not written yet: `peak.csv`.

## 5. Rules the code must keep

1. **Data flows one way:** raw → processed → figures → README/REPORT. No step writes into
   an earlier step's folder.
2. **Raw is append-only.** New runs add files; nothing in `results/raw/` is edited or
   deleted. Runs are left out only by named rules in `analyse.py` — for example, a re-run
   of a noisy point supersedes the first run (spec §7). A re-run in the same session is
   saved as `<config_id>__2.json`.
3. **Predictions never see measured speed.** `roofline.py` reads only `configs/sweep.yaml`,
   `results/models/`, `results/raw/bandwidth/` and `results/raw/peak/` — never
   `results/raw/bench/`. A unit test checks this.
4. **Clone and regenerate.** Everything from `make predict` onwards runs from committed
   files: no model weights, no cloud account.
5. **One join key.** Predictions and measurements meet only through `config_id`; the two
   builds meet only through `pair_id`.
6. **Hardware code stays at the edges.** `src/edge_llm/` is plain Python with no hardware
   calls, so all of it is tested in CI. Anything that needs the Arm machine lives in
   `infra/`, `bench/` or `micro/`.
7. **Every raw file says where it came from:** session, repo commit, llama.cpp commit and
   model SHA256.

## 6. Make targets

On a fresh VM, run `bash infra/setup_vm.sh` once before any target.

| Target | Runs | Where | Writes |
|---|---|---|---|
| `make env` | `bench/env_capture.py` | VM | `results/raw/env/` |
| `make build` | `infra/build_llamacpp.sh` | VM | `work/build-*/`, `results/raw/build/` |
| `make models` | `infra/make_models.sh`, then `gguf_table.py` | VM | `work/models/`, `work/hf/`, `results/models/` |
| `make bandwidth PHASE=start` (or `end`) | `bench/bandwidth/` | VM | `results/raw/bandwidth/` |
| `make check-builds` | `bench/check_builds.py` | VM | `results/raw/build/` |
| `make peak` | `micro/run_peak.py` (`micro/peak.cpp`) | VM | `results/raw/peak/`, `micro/disasm/` |
| `make predict` | `python -m edge_llm.roofline` | anywhere | `results/predictions/` |
| `make bench SET=pilot` (or `full`) | `bench/run_sweep.py` → llama-bench | VM | `results/raw/bench/` |
| `make analyse` (`SESSION=<id>`) | `python -m edge_llm.analyse` | anywhere | `results/processed/` |
| `make figures` | `python -m edge_llm.plots` | anywhere | `figures/` |
| `make micro` | `micro/run_micro.py` (`micro/dot_int8*.cpp`), then `edge_llm.micro` | VM | `results/raw/micro/`, `micro/disasm/`, `results/processed/micro.csv` |
| `make micro-table` | `python -m edge_llm.micro` | anywhere | `results/processed/micro.csv` |
| `make day8-variants` | `infra/make_variants.sh`, then `bench.day8 tables` | VM | `work/models/`, `results/models/small_Q4_0out*.json` |
| `make day8` | `bench/day8.py` (Check A, then C), then `edge_llm.day8` | VM | `results/raw/bench/<session_id>/`, `results/raw/perf/<session_id>/`, `results/processed/day8_*.csv` |
| `make day8-analyse` | `python -m edge_llm.day8` | anywhere | `results/processed/day8_*.csv` |
| `make test` | `pytest` (hardware tests only on the VM) | anywhere | — |

## 7. Tests: what runs where

- **CI, on every push:** `ruff` + `black`, then `pytest`: tensor-table parsing on a tiny GGUF
  written by the test (bytes checked against the ggml block sizes for Q4_0, Q8_0, Q4_K, Q6_K,
  F16, F32; roles; tied embeddings), schema validation of the Day 2 and Day 3 records
  (bandwidth with streams, peak, bench), `config_id` / `pair_id` and the sweep enumeration
  (144 points; 26 in the pilot), the build-order alternation, resume / re-run / never-overwrite
  of the sweep, median/IQR and the 5 % noisy rule on synthetic data, the operations per
  instruction, `B(t)` = best over k, the disassembly parser on synthetic `objdump` text, the
  pilot's wall-time method on synthetic records, the dirty check, parsing of llama.cpp's log
  lines and CMake caches. Day 4 adds the roofline known-answer tests (spec §8: every formula on
  hand-worked fixtures, the `B(t)` and `C(t)` rules on synthetic records, the real inputs against
  the numbers pinned in §11, the committed `v1.csv` against a fresh run) and the rule-3 check
  (`roofline.py` never opens `results/raw/bench/`, and its source never names that folder).
  Day 5–6 adds: the re-run rule on synthetic samples (clean, noisy then clean, noisy twice, never
  re-run, missing first attempt), median/IQR and the ratio from synthetic records on disk, the
  join failing on a missing point on either side, the speed-up range, `achieved_GBps` and the
  session-B prediction worked by hand, the real session (144 points, 72 pairs, bandwidth drift
  against the Progress Log, F16 near 1.0, the committed tables equal a fresh run), and `plots.py`
  on a synthetic table: every figure written, byte-identical across two runs, no timestamps,
  and its source never names `results/raw` or `results/predictions`.
  Day 7 adds (no hardware): the micro record's schema (missing variant, fewer than 30 repeats,
  summary not following from the samples, a repetition under 10 ms, output differing from scalar,
  `--check` not passed, MACs per weight byte, named references), the speed-up and fraction
  arithmetic on a hand-worked synthetic record (SMMLA counted per MAC and per weight byte),
  the best-accumulator rule, the share of slow repetitions, the disassembly checker on synthetic
  snippets (right and wrong instruction forms, scalar with a SIMD multiply, auto-vec recorded,
  inner loop rather than row loop), `run_micro` gating (a failed check times and saves nothing; a
  failed loop check saves, then fails), the real bandwidth and peak files as references, and the
  RQ4 figure (written, byte-stable).
  Day 8 adds (no hardware): the variants' table check (right and wrong output type, any other
  tensor changed, missing or extra), `step_tables` writing a good variant and stopping on a bad one,
  the Check A running order (both build orders at each thread count and for each variant), speed-ups
  and the `smaller / overlap / larger` rule on synthetic records (including the re-run rule), Check B
  arithmetic by hand and on synthetic fixed-cost and per-token cases, the real Check B numbers, the
  `perf report` parser and record validation, and `perf` missing or unable to sample.
- **On the VM, `pytest -m hardware`:** the bandwidth kernels (including the k-stream reads and
  the huge-page run) reproduce their known checksums on the right cores and report the
  process CPU set correctly; each peak loop's real disassembly contains its instruction;
  llama-bench accepts the exact sweep command on both builds; both builds exist; `KLEIDIAI`
  appears only in the kleidiai build's system-info line. Day 7 adds: every SIMD variant gives
  the same integer result as scalar on random inputs.

## 8. Following one data point

How `small_Q4_0_kleidiai_t8_tg128` — decode, small model, Q4_0, KleidiAI build, 8 threads
— travels through the pipeline:

1. `make models` writes `results/models/small_Q4_0.json`, which gives `W_blk`, `W_out`
   and the parameter counts.
2. `make bandwidth` and `make peak` record `B(8)` (best over the read-stream counts) and
   `C_sdot(8)`.
3. `make predict` computes `bytes_tok` and `flops_tok`, then
   `predicted = 1 / max(bytes_tok / B(8), flops_tok / C_sdot(8))`, and writes it as one row
   of `v1.csv`, marked `memory` or `compute`.
4. `make bench` runs llama-bench for this point. Its samples land in
   `results/raw/bench/<session_id>/small_Q4_0_kleidiai_t8_tg128.json`.
5. `make analyse` takes the median and IQR of those samples (or of `__2` if the first attempt
   was noisy) and divides by the prediction: that is the point's `ratio`. Its twin `small_Q4_0_baseline_t8_tg128` (same
   `pair_id`) gives the KleidiAI speed-up.
6. `make figures` draws it as one dot on the headline figure; README and REPORT quote it
   by its `config_id`.

## 9. Changing this design

Change the code and this file in the same commit. If a change touches a rule in §5 or the
roofline model, add a Decision Log entry to the spec first.
