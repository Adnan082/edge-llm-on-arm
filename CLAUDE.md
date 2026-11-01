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
    already has NEON / dotprod / i8mm kernels, and on this CPU it repacks Q4_0, Q4_K, Q6_K
    and Q8_0 weights at load time (verified; §11).
  - `kleidiai` — the same build with `-DGGML_CPU_KLEIDIAI=ON` (verified at the pinned
    commit; §11).

  RQ3 therefore measures KleidiAI *against ggml's own Arm kernels*. At the pinned commit, on
  this CPU (no SME), KleidiAI takes Q4_0, Q8_0 (re-quantised per row at load) and Q6_K
  (converted to 8-bit at load); its Q4_K and F16 kernels need SME2, so those formats stay on
  ggml's kernels (§11, ADR-013). **F16 is the negative control**: it should show ~1.0×, and a
  speed-up there means something other than KleidiAI differs between the builds. Q4_K_M is a
  **partial** case: only its Q6_K tensors move to KleidiAI.
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
  - `peak.cpp` — register-only loops of independent `SDOT` / `SMMLA` / FP16 `FMLA` /
    widening FP16→FP32 `FMLALB`+`FMLALT` instructions; gives `C(t)` for the roofline
    (ADR-015).
  - `dot_int8.cpp` — int8 dot product in five variants: scalar (auto-vectorisation off),
    compiler auto-vectorised, NEON `SDOT`, i8mm `SMMLA` on a 2-row tile (`SMMLA` needs at
    least two rows, which is why it suits prefill rather than decode), and SVE. Each is
    timed with an L1-resident and a DRAM-resident working set.
  - SVE width: Neoverse V2 is expected to have 128-bit SVE — the same width as NEON, so SVE
    should not win on width here (Neoverse V1, e.g. AWS Graviton3, has 256-bit). Verified
    on the machine: 128 bits (§11).
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
   absent), date/time (UTC). Stored alongside the raw results. Sweep sessions start from a
   clean, pushed commit, so the capture shows `dirty: false`.
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
  nothing. Each thread reads `k` interleaved streams, k ∈ {1, 2, 4, 8}; `B(t)` is the best
  median over `k` (the real ceiling), and the one-stream result `B₁(t)` is kept as the
  reference for simple sequential access (ADR-017). The record used is named in
  `v1.meta.json`. STREAM triad is also measured and reported for comparability; it is not a
  roofline input.
- `C(t)`: peak throughput at `t` threads from `micro/peak.cpp`, per instruction class:
  `C_sdot`, `C_smmla`, and two for F16, because ggml's F16 path uses different instructions
  in each phase (checked in the source; ADR-015): `C_hfma` for FP16 `FMLA` (prefill:
  llamafile's tinyBLAS) and `C_fmlal` for the widening FP16→FP32 `FMLALB`/`FMLALT` (decode:
  `ggml_vec_dot_f16`).
- Each model file's tensor table (name, type, shape, bytes), committed to `results/models/`.
  From it: `W_blk`, `N_blk` = bytes and parameter count of all transformer-block weight
  matrices; `W_out`, `N_out` = the same for the output projection (the embedding table, if
  tied). The input-embedding lookup reads one row per token — negligible. Bytes are the
  file's, for both builds, so v1 predicts the same speed for `baseline` and `kleidiai`;
  KleidiAI's load-time conversions change bytes in memory and are a named gap source
  (ADR-016).

**Decode** (one new token at context length `c`):

- `bytes_tok = W_blk + W_out + KV(c)`, with
  `KV(c) = c × n_layers × 2 × n_kv_heads × head_dim × bytes_per_kv_element`. llama-bench's
  `tg` test starts from an empty context, so `KV ≈ 0` unless decode-at-depth is measured
  (§14).
- `flops_tok = 2 × (N_blk + N_out) + 4 × n_layers × n_heads × head_dim × c`.
- `predicted_decode_tps = 1 / max(bytes_tok / B(t), flops_tok / C_dec(t))`, where `C_dec`
  is `C_sdot` for quantised formats (a one-row GEMV cannot use `SMMLA` efficiently) and
  `C_fmlal` for F16.

**Prefill** (prompt of `P` tokens, processed in `⌈P / n_ubatch⌉` chunks):

- `flops(P) = 2 × N_blk × P + 2 × N_out × n_logits + 2 × n_layers × n_heads × head_dim × P²`.
  `n_logits` is the number of tokens whose logits are computed (llama-bench: last token only
  — verify). The last term assumes causal attention computes only the lower triangle; if
  masked entries are computed too, double it — check and state which.
- `bytes(P) = ⌈P / n_ubatch⌉ × W_blk + W_out` (+ KV traffic).
- `predicted_prefill_tps = P / max(flops(P) / C_pre(t), bytes(P) / B(t))`, where `C_pre` is
  `max(C_sdot, C_smmla)` for quantised formats and `C_hfma` for F16.

**Known-answer anchors for tests** (ggml block definitions; re-check `ggml-common.h` at the
pinned commit): Q4_0 = 18 B per 32 weights = 4.5 bits/weight; Q8_0 = 34 B / 32 = 8.5;
Q4_K = 144 B / 256 = 4.5; Q6_K = 210 B / 256 = 6.5625; F16 = 16. Q4_K_M is a per-tensor
*mix* of Q4_K and Q6_K, and by default `llama-quantize` keeps some tensors (e.g. the output
projection) at higher precision in low-bit formats — so effective bytes always come from the
tensor table, never from the format name.

**Outputs.** For every point: `ratio = measured / predicted`. Expect ratio ≤ 1; a ratio > 1
means the model is wrong somewhere — stop and investigate (§13). On this machine the L3 is
80 MiB and the smallest quantised model is only a few times larger, so a decode ratio above
1 for that model points first at weights staying in cache between tokens. Arithmetic intensity
(FLOPs/byte) per configuration goes on a classic roofline plot with the `B(t)` and `C(t)`
ceilings.

**Expected sources of gap** (named before measuring; explain gaps with these or label them
*unexplained*): dequantisation and scale arithmetic inside quantised kernels; per-layer
thread synchronisation (grows with threads, matters most for small models); non-matmul ops
(norms, RoPE, softmax); achieved vs peak bandwidth for the kernel's real access pattern;
load-time format conversion (in the `kleidiai` build Q6_K tensors become 8-bit, so Q4_0 and
Q4_K_M files read more bytes per token than the file holds; measured in §11).

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
- Machine type / region / zone / on-demand price / date: `c4a-highcpu-8` / `us-central1` /
  `us-central1-b` / `TBD` (from the GCP price page) / first used 2026-10-31. 15.6 GiB RAM;
  Ubuntu 24.04.5 LTS, kernel `7.0.0-1014-gcp`; CPU governor not exposed. Source for this and
  the next three lines: `results/raw/env/2026-10-31T2015Z.json`.
- CPU: `Neoverse-V2` (stepping r0p1), 8 cores, 1 thread per core (no SMT, verified), 1 socket,
  1 NUMA node. Caches: L1d 64 KiB and L1i 64 KiB per core, L2 2 MiB per core, L3 80 MiB (one
  instance, probably shared with other VMs on the host). Flags: `asimddp`, `i8mm`, `sve`,
  `sve2`, `svei8mm` and `bf16` present; `sme` and `sme2` absent.
- SVE vector length: 128 bits, from both `prctl` and the `/proc` default; matches §5.
- Compiler versions: GCC/G++ 13.3.0 (`Ubuntu 13.3.0-6ubuntu2~24.04.1`), GNU ld 2.42, CMake
  3.28.3, GNU Make 4.3, Python 3.12.3; Clang not installed. Build flags, both llama.cpp builds
  (ggml-cpu, from ggml's own native detection): `-O3 -DNDEBUG -fopenmp
  -mcpu=neoverse-v2+crc+sve2-sm4+sve2-aes+sve2-sha3+nossbs+dotprod+i8mm+sve`; CMake Release
  with Ninja and default options; ggml 0.28.0. The two CMake caches differ only in KleidiAI's
  own entries, one path and nine settings that KleidiAI's download adds (listed as allowed in
  the build record). Bandwidth kernel: `g++ -O3 -mcpu=native -std=c++17 -fopenmp`. Source:
  `results/raw/build/2026-11-01T1727Z_build.json`.
- llama.cpp commit: `ddf48f85c933c1f438212a02eb21e7b001d2d37d` (HEAD of `ggml-org/llama.cpp`
  on 2026-10-31; pinned in `infra/llamacpp.commit`).
- KleidiAI: flag `-DGGML_CPU_KLEIDIAI=ON` (`ggml/CMakeLists.txt:153`, default OFF); KleidiAI
  v1.32.0 is downloaded at configure time (MD5 `05f1953428ffe8e8c7f585dc6d508887`, checked).
  Activation verified three ways: the configure log ("Using KleidiAI optimized kernels if
  applicable"); `KLEIDIAI = 1` in the system-info line of the `kleidiai` build only; and its
  load log ("primary q4 kernel feature I8MM", "primary q8 kernel feature I8MM", "no
  compatible q4_k kernels found", "SME disabled"). On this CPU it takes Q4_0 (GEMM `i8mm`,
  GEMV `dotprod`), Q8_0 (re-quantised per row at load) and Q6_K (converted to 8-bit at
  load). Its Q4_K and F16 kernels need SME2 (`kernels.cpp:813`, `:517`), so those stay on
  ggml's kernels. When KleidiAI and ggml's repack could both take a tensor, KleidiAI wins (it
  is registered first). Source: `results/raw/build/2026-11-01T1727Z_check_builds.json`
  (smoke runs; their speeds are not data).
- Other Arm paths, both builds: system info `NEON, ARM_FMA, FP16_VA, MATMUL_INT8, SVE,
  DOTPROD, SVE_CNT = 16, OPENMP, REPACK`; llamafile sgemm on. ggml's repack
  (`GGML_CPU_REPACK`, default ON) takes Q4_0 (`q4_0_4x8`; its 8x8 layout needs 256-bit SVE),
  Q4_K (`q4_K_8x8`), Q6_K (`q6_K_8x8`) and Q8_0 (`q8_0_4x8`). Weight buffers from the load
  log, MiB, small / large — Q8_0: REPACK 603.9 / 1743.3 vs KLEIDIAI 603.9 / 1743.3; Q4_0:
  REPACK 358.0 / 999.4 vs KLEIDIAI 386.4 / 1054.5; Q4_K_M: REPACK 372.4 / 1050.0 vs KLEIDIAI
  206.4 + REPACK 204.8 / KLEIDIAI 495.0 + REPACK 645.8; F16: memory-mapped in both builds.
  So the `kleidiai` build holds +28.4 / +55.1 MiB (Q4_0) and +38.8 / +90.8 MiB (Q4_K_M) more
  weights — about +8 % of the small Q4_0 model's bytes per token — from the Q6_K → 8-bit
  conversion. `token_embd` stays memory-mapped everywhere (it is only used for row lookups).
  Source: as above.
- llama-bench defaults at the pinned commit (Day 2 source reading, `llama-bench.cpp:389-423`,
  `:2415-2437`): `n_batch` 2048, `n_ubatch` 512, KV cache F16, flash attention `auto`,
  5 repetitions, one warm-up run. The sweep uses these defaults, written out on every
  command line (ADR-019); the flash-attention value and the mmap default: `TBD` (Day 3).
- Models: `small` = `Qwen/Qwen3-0.6B` @ `c1899de289a04d12100db370d81485cdf75e47ca`, `large` =
  `Qwen/Qwen3-1.7B` @ `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` (BF16 safetensors, every
  file checked against the Hub's hashes). F16 made with the pinned `convert_hf_to_gguf.py`;
  Q8_0, Q4_0 and Q4_K_M with `llama-quantize` defaults. Both models: 28 layers, 16 heads,
  8 KV heads, head size 128 (`qwen3.attention.key_length`), vocabulary 151,936;
  `n_embd`/`n_ff` = 1024/3072 (small) and 2048/6144 (large). **Embeddings:** Qwen's config
  says tied, but every GGUF has its own `output.weight` (the 1.7B checkpoint lists
  `lm_head.weight`), so they are untied in llama.cpp and the whole output layer is read every
  token (`W_out`: 121.7 MiB of the small Q4_0 model's 358.0 MiB). The output layer is Q6_K in
  the Q4_0 and Q4_K_M files; Q4_K_M's blocks are 168 Q4_K + 28 Q6_K tensors. Sizes, SHA256s
  and full tables: `results/models/<alias>_<quant>.json`.
- Measured bandwidth, session `2026-11-01T1727Z` (GB/s = 10⁹ B/s; median of 30 timed repeats
  after 3 warm-ups; thread i on core i, ADR-014). Read-only kernel, 1 GiB, 8 NEON
  accumulators, at t = 1/2/4/8: 27.47 / 52.30 / 98.00 / 172.56 at the start and 27.48 /
  53.29 / 98.19 / 174.00 at the end. STREAM-style triad, 3 × 512 MiB, 24 B per element:
  41.28 / 86.91 / 148.01 / 234.36 (start) and 43.13 / 86.59 / 146.66 / 232.36 (end). IQR ≤
  2.6 % of the median everywhere; drift ≤ 1.9 % (read) and ≤ 4.5 % (triad). The read loop is
  not limited by its add chain (4 / 8 / 16 accumulators: 27.15 / 27.48 / 27.41 at t = 1).
  Transparent huge pages: `madvise`. **Surprise:** the triad beats the read-only kernel at
  every t, so one read stream per thread does not reach the memory limit; how `B(t)` is
  defined is settled before the Day-3 pilot. Known recording bug: `process_cpus` reads `[0]`
  at every t (it is read after pinning); `taskset_cpus` is the true CPU set. Source:
  `results/raw/bandwidth/2026-11-01T1727Z_{start,end}.json`.
- Measured peaks `C(t)` (`SDOT`, `SMMLA`, FP16 `FMLA`, `FMLALB`/`FMLALT`; per thread count;
  method): `TBD` (Day 3).

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
2. **Model family and sizes** — decided: Qwen3 0.6B + 1.7B (ADR-009). Embeddings are untied
   in the GGUFs (§11).
3. **Quantisation mix** — decided: `llama-quantize` default (ADR-010).
4. **Decode at depth** — decided: also at depth 2048, at t ∈ {1, 8} (ADR-018).

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
| ADR-013 | 2026-11-01 | Negative controls revised (supersedes that part of ADR-012): F16 is the negative control; Q4_K_M is a partial case; Q4_0 and Q8_0 run fully on KleidiAI | Pinned source plus the Day 2 load logs: on this CPU KleidiAI also takes Q8_0 and Q6_K (as 8-bit), while its Q4_K and F16 kernels need SME2. So Q4_K_M's Q6_K tensors move to KleidiAI and its Q4_K tensors stay on ggml's repack in both builds; the four formats now run from "no KleidiAI" to "all KleidiAI" | A `--pure` Q4_K file as a second clean control (not what users run; ADR-010) |
| ADR-014 | 2026-11-01 | Thread pinning for every measured program: thread i on core i, cores 0…t−1. The process runs under `taskset -c 0-(t-1)` and each thread is pinned inside the program (bandwidth kernel: `pthread_setaffinity_np`; llama-bench from Day 3: `--cpu-mask` + `--cpu-strict 1`) | `B(t)` and the sweep must use the same placement (§7.5). At the pinned commit ggml pins each OpenMP thread only when t > 1 (`ggml-cpu.c:3438-3462`), so `taskset` covers t = 1 | Unpinned threads (placement unknown, noisier); `OMP_PROC_BIND`/`OMP_PLACES` (would fight ggml's own per-thread pinning) |
| ADR-015 | 2026-11-01 | F16 gets two compute peaks in §8, replacing `C_fma`: `C_hfma` (FP16 `FMLA`) for prefill and `C_fmlal` (widening FP16→FP32 `FMLALB`/`FMLALT`) for decode | Checked in the pinned source: F16 prefill runs llamafile's tinyBLAS with `vfmaq_f16` (`sgemm.cpp`), and F16 decode (fewer than 8 rows) falls back to `ggml_vec_dot_f16`, whose SVE2 path uses `svmlalb`/`svmlalt` (`vec.h`). Settled before the pilot, as §8 asked ("check the source") | One FP peak for both phases (the wrong ceiling for one of them) |
| ADR-016 | 2026-11-01 | Roofline v1 takes bytes from the file's tensor table for both builds, so it predicts the same speed for `baseline` and `kleidiai`; KleidiAI's load-time conversions are a named gap source, not part of v1 | One ceiling per point means any build difference is the kernels' doing. The conversion is measured (§11: +28 to +91 MiB) and can explain part of a KleidiAI decode change | Per-build bytes from the load log (it reports allocation sizes, which need not equal the bytes a kernel reads) |
| ADR-017 | 2026-11-01 | `B(t)` = the best median over 1, 2, 4 and 8 interleaved read streams per thread; the one-stream result `B₁(t)` is kept as a reference | Day 2 surprise: a STREAM-style triad moved more data than the one-stream read test (41 vs 27 GB/s at 1 thread; 234 vs 173 at 8), so one stream per core does not reach the memory limit, and a ceiling below what llama.cpp can reach would push ratios above 1. If llama.cpp only reaches `B₁(t)`, that gap is itself a finding | Keep the one-stream number (probably not the ceiling); use the triad (it also writes, while decode only reads) |
| ADR-018 | 2026-11-01 | Decode is also measured at a context depth of 2048 tokens (llama-bench's depth option; verify), at t ∈ {1, 8}, for every model, format and build; closes §14 item 4 | With an F16 KV cache, depth 2048 adds `KV(c)` = 224 MiB per token for both models (2048 × 28 layers × 2 × 8 KV heads × 128 × 2 B), about 63 % of the small Q4_0 model's weight bytes, so it tests the KV term that empty-context decode cannot | Empty context only (KV term untested); every thread count (twice the cost for little extra information) |
| ADR-019 | 2026-11-01 | Fixed llama-bench settings = its defaults at the pinned commit (§11), written out on every command line; flash attention fixed to the value `auto` resolves to on this CPU (from the source, before the pilot) | Defaults are what users run; spelling them out stops a different llama-bench version, or `auto`, from changing them silently | Tuned settings (would answer a different question) |

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
- 2026-10-31 — **Day 1 gate passed** (commit `b034c8e`; record
  `results/raw/env/2026-10-31T2015Z.json`). In plain English: we rented an 8-core Google Axion
  machine and confirmed it is an Arm Neoverse V2 with the instructions this project tests
  (SDOT, SMMLA, SVE2 at 128 bits), one thread per core and no SME. llama.cpp is pinned to
  `ddf48f8`. The capture shows `dirty` only because the new pin file was not committed yet.
  Next: Day 2.
- 2026-11-01 — **Day 2 gate passed** (session `2026-11-01T1727Z`; code `8d92938`, records
  `a7d8c38`). Both builds run llama-bench; KleidiAI's activation shows in the configure log,
  the system-info line and the load log; the eight tensor tables are committed; `B(t)` was
  measured at the start and end of the session. ADR-013 to ADR-016 recorded. In plain
  English: one Axion core reads memory at about 27 GB/s and all eight at about 173 GB/s,
  steady within 2% over the session. KleidiAI takes Q4_0 and Q8_0, and also turns 6-bit
  tensors into 8-bit as it loads them, so with the small Q4_0 model it reads about 8% more
  bytes per token than the baseline does; F16 is the clean control. Open surprise: a
  STREAM-style triad moves more data than our read-only test (234 vs 173 GB/s at 8 threads),
  so one read stream per core does not reach the memory limit; `B(t)` is settled on Day 3,
  before the pilot. Known issue: one VM test fails on a reporting bug (`process_cpus`), not
  on the data. Next: Day 3.
- 2026-11-01 — Before the Day-3 pilot: `B(t)` defined as the best of 1–8 read streams per
  thread (ADR-017); decode also at depth 2048 (ADR-018, closes §14); llama-bench defaults
  written out explicitly (ADR-019). §8 is final once Day 3's source checks (attention mask,
  `n_logits`, flash attention) are recorded. Next: Day 3.
