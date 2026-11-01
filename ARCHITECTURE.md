# Architecture — edge-llm-on-arm

> How the parts of this repo fit together: what runs where, which files carry data from
> one step to the next, and the rules that keep the results honest. The spec (`CLAUDE.md`)
> says *what* we measure and *why*; this file says *how* the code is arranged to do it.
>
> **Status: Day 3.** Set-up (`env`, `build`, `models`, `check-builds`), `make bandwidth`,
> `make peak`, `make bench SET=pilot|full`, `make test` and `make lint` exist; `predict`,
> `analyse`, `figures` and `micro` are still placeholders. When code changes the design,
> update this file in the same commit.

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
  comparison). The read kernel runs with k = 1, 2, 4 and 8 interleaved streams per thread
  (ADR-017): `B(t)` is the best median over k and `B1(t)` the one-stream median;
  `edge_llm/bandwidth.py` computes both. Huge-page runs at t = 1 and 8 are diagnostics and
  never enter `B(t)`. Each thread count runs under `taskset -c 0-(t-1)` with thread i pinned
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
  predicted tokens/s for every point in `sweep.yaml`, using the formulas in spec §8.
- The result, `results/predictions/v1.csv`, is committed **before** step 3 starts.

### Step 3 — Measure the models (VM)

- `make bench` — `run_sweep.py` calls llama-bench once per point (`config_id`, §3). The
  baseline and kleidiai versions of a point run back to back, and which one goes first
  alternates from point to point.
- Each call writes one raw JSON file: `results/raw/bench/<session_id>/<config_id>.json`. The
  command line spells out every fixed setting from `sweep.yaml: bench_settings` (ADR-019) and
  the pinning (`taskset -c 0-(t-1)`, `-t t`, `--cpu-mask`, `--cpu-strict 1`; ADR-014). Points
  already done in the session are skipped, so a crashed run resumes. If IQR/median of a
  point's repetitions is above 5 %, the point is run once more after its pair and saved as
  `<config_id>__2.json`; both files stay.
- `make bench SET=pilot` runs the small Day-3 pilot listed in the same `sweep.yaml`, then
  writes `_pilot_summary.md` and `.json` next to its records: the repeat noise of every point
  and an estimate of the full sweep's wall time (`edge_llm/pilot.py` states the method).

### Step 4 — Compare (anywhere)

- `make analyse` — `analyse.py` turns raw samples into median and IQR, flags noisy
  points, applies the named exclusion rules, joins each point to its prediction, and
  computes `ratio = measured / predicted` and the KleidiAI speed-ups.
- `make figures` — `plots.py` draws every figure from `results/processed/`.
- README.md and `report/REPORT.md` quote numbers from `results/processed/` by `config_id`.

### Side test, RQ4 — `make micro` (VM)

- `micro/dot_int8.cpp` checks every int8 dot-product variant against scalar, then times
  each one (scalar, auto-vectorised, `SDOT`, `SMMLA`, SVE) with data in L1 and in DRAM.
- `micro/run_micro.py` saves the timings to `results/raw/micro/` and the disassembly of
  each hot loop to `micro/disasm/`.

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
  `large` → file, source, SHA256), formats, builds, thread counts, tests, repetitions,
  slow points, pruned points with reasons, and the pilot subset.
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
  `..._read_loop.s` is the disassembly of the read loop; the record also holds the
  accumulator check (the 1-thread result must not change when the independent accumulators
  are doubled, at k = 1 and k = 8). Records from before Day 3 have k = 1 only.
- `results/raw/peak/<session_id>.json` — from `micro/run_peak.py`, read by `roofline.py`.
  Per instruction class and thread count: the independent accumulators in the loop, at least
  20 samples in instructions/s and in operations/s, median, IQR and max, the pin check; the
  accumulator ladder at one thread (8, 16 and 28 chains: more chains must not raise the
  peak by over 3 %); the disassembly check of every hot loop; compile flags. `C(t)` is the
  16-chain point. Next to it, `<session_id>_ggml_f16_instructions.json` counts `fmlalb`,
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
- `results/raw/micro/<session_id>.json` — from `run_micro.py`, read by `analyse.py`.
  Variant, working set (`L1` or `DRAM`), samples, and the check against scalar.

**Results**

- `results/processed/bench.csv` — from `analyse.py`, read by `plots.py`, README and
  REPORT. One row per `config_id`: median, Q1, Q3, noisy flag, exclusion rule (if any),
  predicted tokens/s, ratio, and the raw file it came from.
- `results/processed/speedup.csv` — one row per `pair_id`: kleidiai ÷ baseline, and
  whether the format is a negative control (one KleidiAI does not handle).
- `results/processed/bandwidth.csv`, `peak.csv`, `micro.csv` — medians of the raw samples.

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
| `make predict` | `roofline.py` | anywhere | `results/predictions/` |
| `make bench SET=pilot` (or `full`) | `bench/run_sweep.py` → llama-bench | VM | `results/raw/bench/` |
| `make analyse` | `analyse.py` | anywhere | `results/processed/` |
| `make figures` | `plots.py` | anywhere | `figures/` |
| `make micro` | `micro/dot_int8.cpp`, `micro/run_micro.py` | VM | `results/raw/micro/`, `micro/disasm/` |
| `make test` | `pytest` (hardware tests only on the VM) | anywhere | — |

## 7. Tests: what runs where

- **CI, on every push:** `ruff` + `black`, then `pytest`: tensor-table parsing on a tiny GGUF
  written by the test (bytes checked against the ggml block sizes for Q4_0, Q8_0, Q4_K, Q6_K,
  F16, F32; roles; tied embeddings), schema validation of the Day 2 and Day 3 records
  (bandwidth with streams, peak, bench), `config_id` / `pair_id` and the sweep enumeration
  (288 points; 26 in the pilot), the build-order alternation, resume / re-run / never-overwrite
  of the sweep, median/IQR and the 5 % noisy rule on synthetic data, the operations per
  instruction, `B(t)` = best over k, the disassembly parser on synthetic `objdump` text, the
  pilot's wall-time method on synthetic records, the dirty check, parsing of llama.cpp's log
  lines and CMake caches. Day 4 adds the roofline known-answer tests (spec §8) and the rule-3
  check.
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
5. `make analyse` takes the median and IQR of those samples and divides by the
   prediction: that is the point's `ratio`. Its twin `small_Q4_0_baseline_t8_tg128` (same
   `pair_id`) gives the KleidiAI speed-up.
6. `make figures` draws it as one dot on the headline figure; README and REPORT quote it
   by its `config_id`.

## 9. Changing this design

Change the code and this file in the same commit. If a change touches a rule in §5 or the
roofline model, add a Decision Log entry to the spec first.
