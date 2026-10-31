# CLAUDE.md — edge-llm-on-arm

> Working specification for this repository. Read this file in full before every session.
> It is the single source of truth for the problem, scope, conventions, measurement protocol
> and decisions. When a decision changes, update this file (and the Decision Log) in the same
> commit. Anything marked *verify* is an expectation, not a fact, until §11 records the evidence.

---

## 1. The problem we are solving

**Say it out loud.** Small language models now run on ordinary Arm CPUs, from phones to cloud
servers. The numbers usually quoted — a tokens/s figure, a kernel speed-up — say how fast one
setup ran, but not *why*, and not how far it is from what the hardware allows. This project
predicts LLM inference speed on an Arm CPU from the hardware's measured limits, measures it,
and explains the difference.

**The question.** For small LLMs on an Arm CPU: which hardware limit sets the speed of each
phase of inference, how close does llama.cpp get to that limit, and what exactly do Arm's
KleidiAI kernels change?

**Why it matters.** Without a GPU, the choices that decide speed are quantisation format, core
count and kernel library — and each one helps only if it relieves the bottleneck that is
actually binding:

- **Bandwidth-bound** — expected for decode, where every weight is fetched from memory for a
  single multiply-add per generated token. Smaller weight formats help; faster arithmetic
  does not.
- **Compute-bound** — expected for prefill, where each weight fetched is reused across every
  prompt token. Better SIMD kernels and more cores help; smaller formats help less.
- **Far below both limits** — time is lost to software overhead (dequantisation, thread
  synchronisation, non-matmul ops), and that is where an engineer should look.

Knowing which case applies — per phase, per format, per thread count — tells you which change
will help before you try it. And if the model holds, a new Arm machine needs two new
measurements (memory bandwidth and compute peak), not a full re-benchmark.

**What is missing.**

- Most published CPU inference numbers are end-to-end tokens/s for a handful of
  configurations. Without a hardware model next to them, a reader cannot tell whether a
  result is near the machine's limit or far from it.
- The standard rules of thumb — decode is memory-bound, prefill is compute-bound, decode speed
  is inversely proportional to bytes per weight — are seldom checked quantitatively on a
  specific chip, across thread counts.
- A kernel speed-up is easiest to trust, and to carry to another machine, when it is tied to
  the regime it acts in and the instructions responsible. An end-to-end ratio shows neither.

None of the underlying ideas is new (roofline models, bandwidth-bound decoding). What is
missing is a small, reproducible, end-to-end check of them on one real Arm machine.

**What "solved" looks like.**

1. For every configuration: predicted tokens/s (committed before the full sweep), measured
   median and IQR, their ratio, and an explanation of the gap — or the label *unexplained*.
2. A KleidiAI-vs-baseline comparison per format and phase, attributed to a mechanism.
3. Instruction-level evidence for that attribution (RQ4).
4. A repo from which anyone can regenerate every figure from committed data, and re-run the
   measurements with a Google Cloud account.

## 2. What we do (project in one paragraph)

**Edge LLM on Arm — measured, not guessed.** We measure how fast small open language models
run on an Arm CPU (Google Axion on Google Cloud, built on Arm Neoverse V2) and explain the
results from first principles. We sweep
quantisation format, thread count, prompt length and kernel backend (llama.cpp with and
without Arm's KleidiAI micro-kernels), measure prompt processing (prefill) and token
generation (decode) separately, and compare every measurement with a roofline prediction
built from the machine's *measured* memory bandwidth and compute peaks — predictions that are
committed before the full sweep runs. Small hand-written NEON/SVE C++ microbenchmarks show at
the instruction level where the speed-up comes from, and why it disappears once a kernel is
bandwidth-bound. The deliverable is a reproducible repo whose headline figure is **predicted
vs measured tokens/s across the whole sweep**, with every gap explained or honestly marked as
unexplained.

**Why a cloud machine for an edge question.** Axion is the lab bench, not the target: a
rentable, reproducible Arm Neoverse V2 machine whose CPU features are fully visible. What
transfers to edge devices is the method — measure bandwidth and compute peak, read the
model's tensor table, predict tokens/s. The Raspberry Pi 5 stretch goal (§5) tests that
transfer.

## 3. Owner, deadline and audience

- Owner: Adnan Haider Cheema (MSc Applied Data Science, BSc Physics). Purpose: portfolio
  project for the **Arm Graduate Program – Engineering Pathways** (ML / performance
  modelling track). **Application closes 2026-11-22; target submission 2026-11-12/14.**
- **Hard time budget: 10 working days.** Scope is fixed to fit. Anything not in §5 is out of
  scope unless the Decision Log records otherwise. If Day 1 is Mon 2026-11-02, Day 10 is
  Fri 2026-11-13, leaving about a week of slack before the deadline.
- Prior project with the same philosophy: `diloco-measured` (analytic model vs rig
  measurements). Reuse its style: measured-not-simulated, held-out validation, openly
  reported nulls, every number traceable to a committed raw record.
- Audience for README and REPORT: Arm engineers. They care about memory bandwidth, SIMD,
  quantisation, performance per watt/dollar, and honesty about limits. Write for them.
- The owner must be able to explain every line in an interview. Prefer simple, readable code
  over clever code. Leave short comments explaining *why*, not *what*.

## 4. Research questions

1. **RQ1 – Decode is bandwidth-bound.** Does measured decode throughput track
   `B(t) / bytes_tok` (§8) across quantisation formats, and from which thread count does it
   stop scaling with threads? Report measured/predicted per configuration.
2. **RQ2 – Prefill is compute-bound.** Does prefill throughput track the compute roofline,
   how close does it get, and where (if anywhere) does thread scaling break down?
3. **RQ3 – KleidiAI effect.** How much does enabling KleidiAI change prefill and decode
   throughput per format, relative to ggml's own Arm kernels (§5)? Which phase benefits
   more, and is that consistent with the roofline — large gains only where the baseline sits
   far below its ceiling?
4. **RQ4 – Instruction-level explanation.** In a microbenchmark, how much faster is an int8
   dot product with NEON `SDOT` and i8mm `SMMLA` (and SVE) than scalar code, with data in L1
   (compute-bound) and in DRAM (bandwidth-bound)? Does the in-cache gain match RQ3's prefill
   result, and the out-of-cache collapse match RQ1?

Each RQ ends with one of: **supported / partially supported / not supported / not measured**,
plus the evidence. Null results are results.

## 5. Scope

### In scope (must ship)

- **Platform:** one Google Cloud VM, `c4a-highcpu-8` (8 vCPUs, 16 GB) in `us-central1`
  (ADR-007, ADR-008). C4A runs on Google Axion, built on Arm Neoverse V2 — the same core as
  AWS Graviton4. Record exact machine type, zone, CPU (`lscpu`), kernel, compiler. Neoverse
  V2 has no SMT, so one vCPU should be one physical core (verify: `lscpu` shows 1 thread per
  core).
- **Inference engine:** llama.cpp, two builds from the **same pinned commit**:
  - `baseline` — the default CPU build. This is *not* unoptimised: ggml's CPU backend
    already has NEON / dotprod / i8mm kernels and repacks Q4_0 weights at load time
    (verify, and record in §11 which of these paths are active).
  - `kleidiai` — the same build with KleidiAI enabled (expected flag
    `-DGGML_CPU_KLEIDIAI=ON`; verify against the docs at the pinned commit).

  RQ3 therefore measures KleidiAI *against ggml's own Arm kernels*. Record which tensor
  types KleidiAI handles at the pinned commit (expected: Q4_0, possibly Q8_0 — verify).
  Formats it does not handle are a built-in **negative control**: they should show ~1.0×,
  and a speed-up there means something other than KleidiAI differs between the builds.
- **Models:** Qwen3 0.6B and Qwen3 1.7B from Hugging Face (`Qwen/Qwen3-0.6B`,
  `Qwen/Qwen3-1.7B`; ADR-009). Start from one F16 GGUF per size (converted with the pinned
  commit's tools, or an official F16 GGUF) and produce every other format locally with
  `llama-quantize` from the same commit, using its default tensor-type mix (ADR-010). Pin
  the Hugging Face revision, file names, SHA256 hashes and each file's per-tensor type mix.
- **Quantisation formats:** F16, Q8_0, Q4_0 and Q4_K_M (ADR-012). Q4_0 is required — it is
  the format Arm's optimised paths target most directly.
- **Sweep axes:** threads ∈ {1, 2, 4, 8} (8 = every core of `c4a-highcpu-8`);
  prefill prompt length ∈ {128, 512, 2048}; decode = 128 generated tokens (llama-bench
  `tg128`, which starts from an empty context); batch 1 (single sequence).
- **Tooling:** `llama-bench` as the primary harness (JSON output, which includes
  per-repetition samples), wrapped by our Python.
- **Hardware characterisation:** memory bandwidth `B(t)` and peak compute `C(t)` measured at
  every thread count in the sweep (§8).
- **Roofline model** in Python; v1 predictions committed before the full sweep starts.
- **C++ microbenchmarks:**
  - `peak.cpp` — register-only loops of independent `SDOT` / `SMMLA` / FP `FMLA`
    instructions; gives `C(t)` for the roofline.
  - `dot_int8.cpp` — int8 dot product in five variants: scalar (auto-vectorisation off),
    compiler auto-vectorised, NEON `SDOT`, i8mm `SMMLA` on a 2-row tile (`SMMLA` needs at
    least two rows, which is why it suits prefill rather than decode), and SVE. Each is
    timed with an L1-resident and a DRAM-resident working set.
  - SVE width: Neoverse V2 is expected to have 128-bit SVE — the same width as NEON, so SVE
    should not win on width here (Neoverse V1, e.g. AWS Graviton3, has 256-bit). Verify on
    the machine.
- **Report:** README headline + `report/REPORT.md` (≤ 4 pages equivalent).

### Stretch (only if Day 8 is free, in this order)

1. Raspberry Pi 5 as an edge device (same method, reduced sweep). Its Cortex-A76 is expected
   to have dotprod but no i8mm or SVE (verify) — a different feature set to test the method
   on.
2. Cost per million tokens on C4A (from the on-demand price; record date and region).
3. Energy (tokens/joule) on the Pi with a USB power meter.

### Out of scope (do not do)

- Any model training or fine-tuning.
- GPUs; x86 comparisons beyond one optional sanity data point.
- New quantisation algorithms, custom GEMM libraries, large frameworks.
- Multi-model leaderboards. Accuracy/perplexity studies (one perplexity sanity check per
  quant format is allowed, labelled as such).

## 6. Repository layout

```
edge-llm-on-arm/
├── CLAUDE.md                 # this file
├── ARCHITECTURE.md           # how the parts connect: data flow, file contracts, rules
├── README.md                 # headline result first, then how to reproduce
├── pyproject.toml            # Python 3.12, deps pinned
├── Makefile                  # make env / build / models / bandwidth / peak / predict / bench / analyse / figures / micro / test
├── configs/
│   ├── sweep.yaml            # models, quants, threads, prompt lengths, repeats, pruned points + reason
│   └── machine.yaml          # machine type, zone, price, date, VM hours
├── infra/
│   ├── setup_vm.sh           # packages, compilers, clone + pin llama.cpp
│   ├── build_llamacpp.sh     # baseline + kleidiai builds; records flags + commit
│   └── make_models.sh        # F16 GGUF -> every quant format via llama-quantize; SHA256s
├── bench/
│   ├── run_sweep.py          # wraps llama-bench; alternating build order; one raw JSON per run
│   ├── bandwidth/            # read-only kernel + STREAM triad, per thread count
│   └── env_capture.py        # lscpu, uname, compilers, governor, SVE length, commits, system info
├── micro/
│   ├── peak.cpp              # register-only SDOT / SMMLA / FMLA peaks -> C(t)
│   ├── dot_int8.cpp          # scalar / auto-vectorised / SDOT / SMMLA / SVE; L1 + DRAM sizes
│   ├── disasm/               # objdump of each variant's hot loop (committed evidence)
│   ├── CMakeLists.txt
│   └── run_micro.py
├── src/edge_llm/
│   ├── gguf_table.py         # per-tensor name / type / shape / bytes from a GGUF file
│   ├── roofline.py           # bytes and FLOPs per token, predictions
│   ├── schema.py             # pydantic/dataclass schema for raw + processed records
│   ├── analyse.py            # raw -> processed tables, medians, IQR, ratios
│   └── plots.py              # all figures; deterministic, no manual edits
├── results/
│   ├── raw/                  # one JSON per run (env, bandwidth, peak, bench, micro); never edited
│   ├── models/               # tensor table per model file (weights are never committed)
│   ├── predictions/          # roofline predictions; committed before the full sweep
│   └── processed/            # derived CSVs (regenerable)
├── figures/                  # committed PNG/SVG outputs of `make figures`
├── report/REPORT.md
├── tests/                    # pytest
└── work/                     # gitignored: llama.cpp clone + both builds, model files
```

## 7. Measurement protocol (non-negotiable)

1. **Environment capture before every sweep session:** machine type and zone, `lscpu` (incl.
   feature flags), kernel, compiler versions, llama.cpp commit and build flags, each build's
   system-info line, SVE vector length, model SHA256s, CPU governor (record "not exposed" if
   absent), date/time (UTC). Stored alongside the raw results.
2. **Fixed llama-bench settings**, recorded and never varied within the sweep: batch 1
   (single sequence), `n_batch`, `n_ubatch`, KV-cache type, flash-attention setting, mmap.
   Decode is llama-bench's `tg` test, which starts from an empty context.
3. **Warm-up:** llama-bench runs one unmeasured warm-up per test by default — verify, keep it
   on, record it.
4. **Repeats:** 5 measured repetitions per point (llama-bench's default; 3 only for slow
   points listed in `sweep.yaml`). Report **median and IQR**, computed from llama-bench's
   per-repetition samples (its own summary is mean ± stddev). If IQR/median > 5%, flag the
   point as noisy and re-run it once; if still noisy, keep it and label it.
5. **Isolation:** nothing else running; record load average before/after; pin threads and
   record how (the bandwidth kernel uses the same pinning). A cloud VM shares its physical
   machine, and that machine's memory bandwidth, with other customers, so measure `B(t)` at
   the start and end of every sweep session and report the drift.
6. **Prefill and decode are always reported separately.** Never mix them into one
   "tokens/s" number.
7. **Builds are interleaved per configuration, and the build that runs first alternates**
   (baseline→kleidiai, then kleidiai→baseline, …), so slow drift favours neither build.
8. **Raw records are immutable.** Analysis reads `results/raw/` and writes
   `results/processed/`. A bad run is excluded by a listed rule in `analyse.py`, never by
   deleting the file.
9. **Predictions first:** `make predict` writes v1 predictions for every planned point to
   `results/predictions/`, and they are committed **before the full sweep starts** (only the
   Day-3 pilot exists by then). REPORT.md cites the predictions commit and the first
   full-sweep commit so the order can be checked.
10. **Sweep budget:** before the full sweep, estimate its wall time from the pilot. If it
    does not fit, prune the lowest-value points in `sweep.yaml`, with a reason — before any
    full-sweep results exist, never after.

## 8. Roofline model (v1)

**v1 is frozen from the start of the Day-3 pilot**: after that, only its measured inputs are
filled in. Any later change to its form is v2 — keep v1, add v2, record why in the Decision
Log. Items marked *verify* or *check* below are settled from source code or documentation,
never from measured throughput. Count one multiply-accumulate as 2 operations everywhere.

**Inputs** — all measured or read from files, never taken from datasheets:

- `B(t)`: memory bandwidth at `t` threads from a **read-only** kernel (a vectorised sum over
  a buffer ≥ 4× the last-level cache), because decode reads weights and writes almost
  nothing. STREAM triad is also measured and reported for comparability; it is not a
  roofline input.
- `C(t)`: peak throughput at `t` threads from `micro/peak.cpp`, per instruction class:
  `C_sdot`, `C_smmla`, and `C_fma` for the floating-point FMA that ggml's F16 path uses
  (check the source).
- Each model file's tensor table (name, type, shape, bytes), committed to `results/models/`.
  From it: `W_blk`, `N_blk` = bytes and parameter count of all transformer-block weight
  matrices; `W_out`, `N_out` = the same for the output projection (the embedding table, if
  tied). The input-embedding lookup reads one row per token — negligible.

**Decode** (one new token at context length `c`):

- `bytes_tok = W_blk + W_out + KV(c)`, with
  `KV(c) = c × n_layers × 2 × n_kv_heads × head_dim × bytes_per_kv_element`. llama-bench's
  `tg` test starts from an empty context, so `KV ≈ 0` unless decode-at-depth is measured
  (§14).
- `flops_tok = 2 × (N_blk + N_out) + 4 × n_layers × n_heads × head_dim × c`.
- `predicted_decode_tps = 1 / max(bytes_tok / B(t), flops_tok / C_dec(t))`, where `C_dec`
  is `C_sdot` for quantised formats (a one-row GEMV cannot use `SMMLA` efficiently) and
  `C_fma` for F16.

**Prefill** (prompt of `P` tokens, processed in `⌈P / n_ubatch⌉` chunks):

- `flops(P) = 2 × N_blk × P + 2 × N_out × n_logits + 2 × n_layers × n_heads × head_dim × P²`.
  `n_logits` is the number of tokens whose logits are computed (llama-bench: last token only
  — verify). The last term assumes causal attention computes only the lower triangle; if
  masked entries are computed too, double it — check and state which.
- `bytes(P) = ⌈P / n_ubatch⌉ × W_blk + W_out` (+ KV traffic).
- `predicted_prefill_tps = P / max(flops(P) / C_pre(t), bytes(P) / B(t))`, where `C_pre` is
  `max(C_sdot, C_smmla)` for quantised formats and `C_fma` for F16.

**Known-answer anchors for tests** (ggml block definitions; re-check `ggml-common.h` at the
pinned commit): Q4_0 = 18 B per 32 weights = 4.5 bits/weight; Q8_0 = 34 B / 32 = 8.5;
Q4_K = 144 B / 256 = 4.5; Q6_K = 210 B / 256 = 6.5625; F16 = 16. Q4_K_M is a per-tensor
*mix* of Q4_K and Q6_K, and by default `llama-quantize` keeps some tensors (e.g. the output
projection) at higher precision in low-bit formats — so effective bytes always come from the
tensor table, never from the format name.

**Outputs.** For every point: `ratio = measured / predicted`. Expect ratio ≤ 1; a ratio > 1
means the model is wrong somewhere — stop and investigate (§13). Arithmetic intensity
(FLOPs/byte) per configuration goes on a classic roofline plot with the `B(t)` and `C(t)`
ceilings.

**Expected sources of gap** (named before measuring; explain gaps with these or label them
*unexplained*): dequantisation and scale arithmetic inside quantised kernels; per-layer
thread synchronisation (grows with threads, matters most for small models); non-matmul ops
(norms, RoPE, softmax); achieved vs peak bandwidth for the kernel's real access pattern.

## 9. Engineering conventions

- Python 3.12 (Ubuntu 24.04's own; ADR-011), type hints, `ruff` + `black`, `pytest`. C++17, `-O3 -mcpu=native` (on
  AArch64 this sets both architecture and tuning); record the exact flags.
- **Microbenchmark hygiene:** compile the scalar variant with auto-vectorisation off (GCC
  `-fno-tree-vectorize`; Clang `-fno-vectorize -fno-slp-vectorize`) — at `-O3` the compiler
  would otherwise vectorise the "scalar" loop, possibly into `SDOT` itself. Commit the
  disassembly of every variant's hot loop (`objdump -d`) as evidence of which instructions
  ran. Time with a monotonic clock, report the median of many runs, and consume every
  result so the compiler cannot delete the work.
- **Tests required for:** roofline arithmetic (known-answer tests, §8), tensor-table
  parsing, schema validation of raw records, analysis aggregation (median/IQR on synthetic
  data), and microbenchmark correctness (every SIMD variant must produce the same integer
  result as scalar on random inputs before its timing is trusted).
- GitHub Actions: lint + unit tests on every push (no hardware-dependent tests in CI; mark
  them `@pytest.mark.hardware`).
- Every figure is produced by `make figures` from committed data. No hand-edited figures.
- Every number in README/REPORT must be traceable: cite the processed CSV and the row's
  `config_id` (a stable key such as `<model>_<quant>_<build>_t<threads>_<test>`), or the raw
  file.
- Small commits with clear messages. Never commit model weights or builds (gitignore `*.gguf` and `work/`).
- Cost control: stop the VM when not benchmarking; log VM hours in `configs/machine.yaml`.

## 10. 10-day plan and acceptance gates

| Day | Work | Gate (must be true to move on) |
|----|------|------|
| 1 | Repo skeleton, tests scaffold, `setup_vm.sh`, create the VM | `make env` works on the VM; env-capture JSON committed |
| 2 | Both llama.cpp builds from the pinned commit; F16 models → all formats; tensor tables; bandwidth kernel | `llama-bench` runs on both builds; KleidiAI activation verified (build log + runtime output) and its formats recorded; tensor tables committed; `B(t)` recorded |
| 3 | `run_sweep.py` + schema; pilot sweep (small model, both builds); `micro/peak.cpp` | Raw JSON validates against schema; repeat noise measured; `C(t)` recorded; full-sweep wall time estimated |
| 4 | `roofline.py` + known-answer tests; **commit v1 predictions**; start the full sweep | Predictions commit exists before any full-sweep raw file |
| 5 | Full sweep runs to completion; meanwhile write `analyse.py` against pilot data | All planned points present or listed as failed with reason |
| 6 | `analyse.py` on full data; `plots.py`: measured vs predicted, KleidiAI speed-up, thread scaling, roofline | Headline figure generated by `make figures` |
| 7 | `micro/dot_int8.cpp` variants, correctness tests, L1 + DRAM timings | All variants bit-identical to scalar; disassembly committed; speed-ups recorded |
| 8 | Buffer: re-run noisy/failed points, investigate surprises; stretch only if nothing is open | Every surprise has a Decision Log entry |
| 9 | REPORT.md, RQ verdicts, limitations | Every number traceable |
| 10 | README polish, fresh-clone reproduction check, CV bullet | `git clone` → `make test` passes; README headline correct |

If the full sweep is not complete by end of Day 5: drop the larger model size, keep
everything else. If behind by end of Day 7: cut the microbenchmark to scalar vs NEON `SDOT`
(still in L1 and DRAM) and use Day 8 to catch up.

## 11. Pinned facts (fill in as discovered; never guess)

- Repository: `github.com/Adnan082/edge-llm-on-arm`, private until the project is finished
  (the owner makes it public)
- Machine type / region / zone / on-demand price / date: `c4a-highcpu-8` / `us-central1` / `TBD` / `TBD` / `TBD`
- CPU (`lscpu` model name, cores, caches; flags incl. `asimddp`, `i8mm`, `sve`, `sve2`, `sme`): `TBD`
- SVE vector length (from the machine, e.g. `/proc/sys/abi/sve_default_vector_length`): `TBD`
- Compiler versions and exact flags: `TBD`
- llama.cpp commit: `TBD`
- KleidiAI build flag, how activation was verified, tensor types it handles: `TBD`
- Other Arm paths (e.g. Q4_0 repacking) and their state in each build: `TBD`
- llama-bench fixed settings (`n_batch`, `n_ubatch`, KV type, flash attention, mmap, warm-up): `TBD`
- Models (source, file, params, size bytes, SHA256, tensor-type mix, tied embeddings y/n): `TBD`
- Measured bandwidth `B(t)` (kernel, buffer size, value per thread count, repeats; triad too): `TBD`
- Measured peaks `C(t)` (`SDOT`, `SMMLA`, FP FMA; per thread count; method): `TBD`

## 12. README headline structure

1. The problem in one sentence (§1), then the claim with the key numbers (e.g. "On Google
   Axion (Neoverse V2), decode reaches X% of the bandwidth roofline; KleidiAI speeds up Q4_0
   prefill by Y× and decode by Z×").
2. Headline figure: predicted vs measured tokens/s, all configurations.
3. Table: KleidiAI vs baseline per quant format (prefill, decode, median + IQR), negative
   controls included.
4. "What this is NOT" (scale, single machine, batch 1, no accuracy study).
5. RQ verdicts.
6. Reproduce in 5 commands.

## 13. Rules for the assistant working in this repo

- **Never commit or push.** Do not run `git commit`, `git push` or anything else that changes
  the GitHub repo; the owner makes every commit and push. Read-only git (`status`, `diff`,
  `log`) is fine. When a piece of work is ready, list the files to commit and suggest a
  commit message.
- **Never fabricate or estimate a measurement.** If a number has not been measured, write
  `not measured`. Placeholders must be obviously placeholders (`TBD`, `X`), never plausible
  numbers.
- **Ask before** spending money (creating/resizing VMs), deleting anything in
  `results/raw/`, changing scope in §5, or revising the roofline model (§8) after the Day-3
  pilot has started.
- Prefer the smallest change that meets the gate. Do not add frameworks, services,
  dashboards or LLM features — this project is about measurement quality.
- When something surprising happens (ratio > 1, KleidiAI slower, a negative control moves,
  noisy results), stop, investigate, and record it in the Decision Log before continuing.
- Keep explanations interview-ready: after passing each day's gate, append a 3–5 line
  plain-English summary to the Progress Log that the owner can say out loud.
- Verify version-sensitive facts (llama.cpp flags and defaults, KleidiAI coverage, VM CPU
  features) from current documentation, the source at the pinned commit, or the machine
  itself, and record the source in §11.

## 14. Open decisions (record each in the Decision Log when made)

1. **Instance size** — decided: `c4a-highcpu-8` (ADR-008).
2. **Model family and sizes** — decided: Qwen3 0.6B + 1.7B (ADR-009). Record in §11
   whether their embeddings are tied; it changes `bytes_tok` (§8).
3. **Quantisation mix** — decided: `llama-quantize` default (ADR-010).
4. **Decode at depth** — decide before Day 4. Decode only from an empty context (KV term
   untested), or also at one depth (e.g. 2048, via llama-bench's depth option — verify) to
   test the KV-cache term.

## 15. Decision Log

| ID | Date | Decision | Reason | Alternatives rejected |
|----|------|----------|--------|-----------------------|
| ADR-001 | 2026-10-31 | Single Graviton instance, llama.cpp baseline vs KleidiAI, roofline comparison | Fits 10-day budget; directly relevant to Arm's edge/cloud AI work | Pi-first (slower iteration), ExecuTorch (more setup), training (out of scope) |
| ADR-002 | 2026-10-31 | Baseline = default llama.cpp CPU build; RQ3 measures KleidiAI against ggml's own Arm kernels; formats KleidiAI does not handle are negative controls | ggml already has NEON/dotprod/i8mm paths, so "KleidiAI off" ≠ unoptimised; the control catches unintended build differences | Third build with Arm paths disabled (+50% sweep time; answers a different question) |
| ADR-003 | 2026-10-31 | All formats quantised locally from one F16 GGUF per model at the pinned commit | Same source weights and tool version behind every format | Pre-quantised GGUFs from different uploaders |
| ADR-004 | 2026-10-31 | Roofline v1 counts bytes and FLOPs per tensor from the GGUF tensor table, and uses `B(t)`, `C(t)` measured at each thread count (`B` from a read-only kernel) | File size × params miscounts the embedding/output tables, a large share of small models; one bandwidth number cannot predict a thread sweep; decode only reads weights | Nominal bits per weight; a single STREAM-triad number |
| ADR-005 | 2026-10-31 | v1 predictions committed on Day 4, before the full sweep; bandwidth moved to Day 2, peak compute to Day 3; Day 8 becomes buffer | Predictions needed `B` and `C`, which were scheduled after the sweep; now "predicted, then measured" is literally true, and the sweep runs while analysis code is written | Predictions after the sweep (original Day 6) |
| ADR-006 | 2026-10-31 | Microbenchmark: scalar compiled without auto-vectorisation, plus an auto-vectorised variant; every variant timed in L1 and in DRAM | At `-O3` the "scalar" loop gets vectorised; the two working sets show where SIMD gains appear (compute-bound) and where they vanish (bandwidth-bound) | Scalar at `-O3` only |
| ADR-007 | 2026-10-31 | Platform: one Google Cloud C4A VM (Google Axion, Arm Neoverse V2) instead of AWS Graviton4; supersedes the platform in ADR-001 | AWS account unavailable; Axion uses the same Neoverse V2 core as Graviton4, so the technical plan is unchanged; new-account free credit covers the cost | Waiting for AWS (days; deadline risk); Azure Cobalt 100 (Neoverse N2, smaller core); Raspberry Pi 5 (no i8mm or SVE; now costly) |
| ADR-008 | 2026-10-31 | Machine: `c4a-highcpu-8` (8 vCPUs, 16 GB) in `us-central1`; a test VM started there | Enough memory for the planned models; predictions stay valid at any size because `B(t)` and `C(t)` are measured per thread count; fits the free-trial limits | `c4a-highcpu-16` (longer thread sweep; double the cost; all-regions CPU limit unconfirmed) |
| ADR-009 | 2026-10-31 | Models: Qwen3 0.6B and Qwen3 1.7B | Ungated (reproducible without an account), Apache-2.0, well supported in llama.cpp; the sizes fit the ~0.5B / ~1.5–3B plan and the 16 GB VM even at F16 | Llama 3.2 and Gemma 3 (gated downloads); Qwen2.5 (older) |
| ADR-010 | 2026-10-31 | Quantisation mix: `llama-quantize` default (some tensors kept at higher precision) | Matches what users actually run; the per-tensor table makes the mix explicit in the roofline | `--pure` (cleaner per-format attribution, but not what users run) |
| ADR-011 | 2026-10-31 | Python 3.12 for the project, on the VM and in CI | It is Ubuntu 24.04's own Python, so the VM needs no extra install; CI should test the version the measurements run on | Python 3.11 (the original spec; needs an extra install on Ubuntu 24.04) |
| ADR-012 | 2026-10-31 | Formats: F16, Q8_0, Q4_0, Q4_K_M | Q4_0 is KleidiAI's main target and Q8_0 may also be accelerated (verify); F16 and Q4_K_M are the expected negative controls, and together the four span the heaviest format to the most popular 4-bit one | Three formats (shorter sweep, but loses a control or the popular Q4_K_M) |

## 16. Progress Log

- 2026-10-31 — Project specified. Next: Day 1 gate.
- 2026-10-31 — Spec refined: problem statement added (§1); baseline defined as ggml's own
  Arm kernels, with negative controls; roofline v1 made per-tensor and per-thread-count;
  plan re-sequenced so predictions precede the full sweep (ADR-002 to ADR-006). Next:
  settle §14 items 1–3, then the Day 1 gate.
- 2026-10-31 — Platform moved to Google Cloud C4A (ADR-007); a test `c4a-highcpu-8` VM
  started in `us-central1` (ADR-008). Spec renamed to `CLAUDE.md`. Next: confirm §14 items
  2–3, then the Day 1 gate.
- 2026-10-31 — Models (ADR-009) and quantisation mix (ADR-010) decided; §14 items 1–3
  closed. Next: the Day 1 gate.
- 2026-10-31 — Python 3.12 (ADR-011) and the four formats (ADR-012) decided. The code still
  says 3.11 in CI and marks the format list provisional; Sonnet updates both at the start of
  Day 2.
