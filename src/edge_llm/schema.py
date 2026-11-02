"""Schemas for the records the pipeline writes (ARCHITECTURE.md §4).

Plain dataclasses, no third-party validation library. Each `from_dict` rejects missing or
unknown keys and checks the invariants a downstream step relies on; `to_dict` gives back the
JSON-ready form. Day 2 covers: model tensor tables, bandwidth records, build records and
check-builds (smoke) records. Day 3 adds the peak record, the ggml F16-instruction counts
and the bench record (llama-bench output).
"""

from __future__ import annotations

import dataclasses
import math
import re
from dataclasses import dataclass, field, fields
from typing import Any

from edge_llm.peak import BASE_ACCUMULATORS, PEAK_CLASSES
from edge_llm.stats import NOISY_THRESHOLD, summarise

SCHEMA_VERSION = 1
ROLES = ("blk", "out", "emb", "other")
BANDWIDTH_KERNELS = ("read", "triad")
READ_STREAMS = (1, 2, 4, 8)  # interleaved read streams per thread (ADR-017)
READ_ACCUMULATORS = (8, 16)  # vector accumulators in the read loop (ADR-021)
MIN_L1_REP_SECONDS = 0.010  # a timed repetition of the L1 validity check lasts at least this
MIN_BANDWIDTH_REPS = 20  # CLAUDE.md-style rule from the Day 2 brief: at least 20 timed repeats
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SchemaError(ValueError):
    """A record does not match its schema."""


def _check_keys(cls: type, d: dict, where: str) -> None:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: expected an object, got {type(d).__name__}")
    names = {f.name for f in fields(cls)}
    # Fields with a default may be absent: that is how Day 2 records (written before a field
    # existed) stay valid.
    required = {
        f.name
        for f in fields(cls)
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    }
    missing, extra = required - d.keys(), d.keys() - names
    if missing or extra:
        raise SchemaError(f"{where}: missing keys {sorted(missing)}, unknown keys {sorted(extra)}")


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise SchemaError(message)


def _is_sha256(x: Any) -> bool:
    return isinstance(x, str) and bool(SHA256_RE.match(x))


# --- model tensor table (results/models/<alias>_<quant>.json) ----------------------------


@dataclass
class TensorRow:
    name: str
    type: str  # ggml type name: "F16", "Q4_0", "Q6_K", ...
    shape: list[int]  # ggml order: shape[0] is the contiguous (input) dimension
    n_dims: int
    n_params: int
    bytes: int
    role: str  # one of ROLES; see edge_llm.gguf_table for the rule

    def __post_init__(self) -> None:
        _require(self.role in ROLES, f"{self.name}: role {self.role!r} not in {ROLES}")
        _require(self.n_dims == len(self.shape), f"{self.name}: n_dims != len(shape)")
        _require(
            self.n_params == math.prod(self.shape), f"{self.name}: n_params != product of shape"
        )
        _require(self.bytes > 0, f"{self.name}: bytes must be positive")


TOTAL_KEYS = tuple(f"{k}_{r}" for r in ("blk", "out", "emb", "other", "all") for k in ("W", "N"))


@dataclass
class ModelTable:
    schema_version: int
    kind: str
    alias: str
    quant: str
    file: str
    file_bytes: int
    sha256: str
    arch: str
    n_layers: int
    n_heads: int
    n_kv_heads: int
    head_dim: int
    head_dim_source: str
    n_embd: int
    n_ff: int
    vocab_size: int
    tied_embeddings: bool
    layout_check: dict
    totals: dict
    type_mix: dict
    type_mix_by_role: dict
    source: dict
    tensors: list[TensorRow] = field(default_factory=list)

    def __post_init__(self) -> None:
        _require(self.kind == "model_table", f"kind must be 'model_table', got {self.kind!r}")
        _require(_is_sha256(self.sha256), "sha256 must be 64 lowercase hex characters")
        _require(
            all(v > 0 for v in (self.n_layers, self.n_heads, self.n_kv_heads, self.head_dim)),
            "layer/head counts must be positive",
        )
        _require(self.tensors, "no tensors")
        _require(self.layout_check.get("ok") is True, "tensor data layout check did not pass")
        names = [t.name for t in self.tensors]
        _require(len(set(names)) == len(names), "duplicate tensor names")
        _require(
            self.tied_embeddings == ("output.weight" not in names),
            "tied_embeddings disagrees with the presence of output.weight",
        )
        for r in ("blk", "out", "emb", "other"):
            rows = [t for t in self.tensors if t.role == r]
            _require(
                self.totals.get(f"W_{r}") == sum(t.bytes for t in rows),
                f"totals.W_{r} does not equal the sum of tensor bytes",
            )
            _require(
                self.totals.get(f"N_{r}") == sum(t.n_params for t in rows),
                f"totals.N_{r} does not equal the sum of tensor parameters",
            )
        _require(
            self.totals.get("W_all") == sum(t.bytes for t in self.tensors),
            "totals.W_all does not equal the sum of tensor bytes",
        )
        _require(
            self.totals.get("W_all", 0) <= self.file_bytes,
            "tensor bytes exceed the file size",
        )
        _require(
            sum(v["bytes"] for v in self.type_mix.values()) == self.totals["W_all"],
            "type_mix bytes do not add up to W_all",
        )
        _require(
            self.vocab_size > 0 and self.n_embd > 0 and self.n_ff > 0, "bad embedding shape data"
        )

    @classmethod
    def from_dict(cls, d: dict) -> ModelTable:
        _check_keys(cls, d, "model table")
        d = dict(d)
        d["tensors"] = [_row(t) for t in d["tensors"]]
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _row(t: Any) -> TensorRow:
    _check_keys(TensorRow, t, "tensor row")
    return TensorRow(**t)


# --- bandwidth record (results/raw/bandwidth/<session_id>_<start|end>.json) ---------------


@dataclass
class BandwidthPoint:
    kernel: str  # "read" (roofline input) or "triad" (STREAM-style, for comparison)
    threads: int
    pinning: dict
    buffer_bytes: int  # total working set of the kernel
    bytes_per_rep: int  # bytes counted as moved in one timed repetition
    reps_warmup: int
    reps_timed: int
    samples_bytes_per_s: list[float]
    median: float
    q1: float
    q3: float
    iqr: float
    max: float
    checksum_ok: bool
    note: str | None = None
    # Added on Day 3 (ADR-017). Day 2 records have one read stream and no huge-page runs.
    streams: int = 1  # read streams per thread (k); the triad ignores it
    hugepage: bool = False  # diagnostic run with madvise(MADV_HUGEPAGE); never part of B(t)
    anon_huge_kb: int | None = None  # AnonHugePages after the first touch
    # Added with ADR-021. Day 2 records used 8 accumulators and had no L1 runs.
    accumulators: int = 8  # vector accumulators in the read loop; 0 for the triad
    l1: bool = False  # the validity check: a 32 KiB buffer read in repeated passes
    passes: int = 1  # passes over the buffer in one timed repetition

    def __post_init__(self) -> None:
        w = f"bandwidth point {self.kernel} t={self.threads} acc={self.accumulators} k={self.streams}"
        _require(self.kernel in BANDWIDTH_KERNELS, f"{w}: unknown kernel")
        _require(self.threads > 0, f"{w}: threads must be positive")
        if self.kernel == "read":
            _require(self.streams in READ_STREAMS, f"{w}: streams must be in {READ_STREAMS}")
            _require(
                self.accumulators in READ_ACCUMULATORS,
                f"{w}: accumulators must be in {READ_ACCUMULATORS}",
            )
        if self.hugepage:
            _require(
                self.kernel == "read" and self.streams == 1,
                f"{w}: huge-page diagnostics are one-stream read runs",
            )
        if self.l1:
            _require(self.kernel == "read" and not self.hugepage, f"{w}: bad L1 run")
            _require(
                self.bytes_per_rep == self.buffer_bytes * self.passes,
                f"{w}: bytes_per_rep != buffer_bytes x passes",
            )
        _require(
            self.reps_timed >= MIN_BANDWIDTH_REPS,
            f"{w}: needs at least {MIN_BANDWIDTH_REPS} timed repeats, has {self.reps_timed}",
        )
        _require(len(self.samples_bytes_per_s) == self.reps_timed, f"{w}: sample count != reps")
        _require(all(s > 0 for s in self.samples_bytes_per_s), f"{w}: non-positive sample")
        _require(self.checksum_ok is True, f"{w}: checksum did not match the known answer")
        _require(self.pinning.get("getcpu_ok") is True, f"{w}: sched_getcpu() pin check failed")
        if self.l1:  # the shortest repetition is the one with the highest rate
            shortest = self.bytes_per_rep / max(self.samples_bytes_per_s)
            _require(
                shortest >= MIN_L1_REP_SECONDS,
                f"{w}: a timed L1 repetition lasted {shortest * 1e3:.1f} ms, under 10 ms",
            )
        # The summary must be recomputable from the samples (spec §9: every number traceable).
        s = summarise(self.samples_bytes_per_s)
        for name in ("median", "q1", "q3", "iqr", "max"):
            _require(
                math.isclose(getattr(self, name), s[name], rel_tol=1e-9),
                f"{w}: {name} does not match the samples",
            )

    @classmethod
    def from_dict(cls, d: dict) -> BandwidthPoint:
        _check_keys(cls, d, "bandwidth point")
        return cls(**d)


@dataclass
class BandwidthRecord:
    schema_version: int
    kind: str
    session_id: str
    phase: str
    captured_utc: str
    repo: dict
    binary: dict
    host: dict
    points: list[BandwidthPoint]
    objdump_file: str
    # Day 2 records have acc_check (an accumulator-doubling check, dropped by ADR-021); newer ones
    # have validity: the per-variant L1 check, the winners and the loop reports.
    acc_check: dict = field(default_factory=dict)
    validity: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(self.kind == "bandwidth", f"kind must be 'bandwidth', got {self.kind!r}")
        _require(self.phase in ("start", "end"), f"phase must be start or end: {self.phase!r}")
        _require(self.points, "no bandwidth points")
        seen = {
            (p.kernel, p.threads, p.accumulators, p.streams, p.hugepage, p.l1) for p in self.points
        }
        _require(
            len(seen) == len(self.points),
            "duplicate (kernel, threads, accumulators, streams, hugepage, l1) points",
        )
        _require(
            {k for k, *_ in seen} == set(BANDWIDTH_KERNELS),
            f"expected both kernels {BANDWIDTH_KERNELS}",
        )
        # Every thread count has the same set of plain 1 GiB read variants, k = 1 among them
        # (a Day 2 record has the one variant 8 accumulators x 1 stream).
        by_t: dict[int, set[tuple[int, int]]] = {}
        for p in self.points:
            if p.kernel == "read" and not p.hugepage and not p.l1:
                by_t.setdefault(p.threads, set()).add((p.accumulators, p.streams))
        _require(
            all(any(k == 1 for _, k in vs) for vs in by_t.values())
            and len({frozenset(vs) for vs in by_t.values()}) == 1,
            "every thread count needs the same read variants, with a one-stream one",
        )
        if self.validity:  # every variant has an L1 run at one thread, and the table says so
            l1 = {(p.accumulators, p.streams) for p in self.points if p.l1 and p.threads == 1}
            _require(
                l1 == by_t.get(1, set()) and {p.threads for p in self.points if p.l1} == {1},
                "the L1 validity runs must cover exactly the 1 GiB variants, at one thread",
            )
            rows = self.validity.get("variants") or []
            _require(
                {(r["accumulators"], r["streams"]) for r in rows} == l1,
                "validity table does not list the same variants",
            )

    @classmethod
    def from_dict(cls, d: dict) -> BandwidthRecord:
        _check_keys(cls, d, "bandwidth record")
        d = dict(d)
        d["points"] = [BandwidthPoint.from_dict(p) for p in d["points"]]
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# --- build record (results/raw/build/<session_id>_build.json) -----------------------------


@dataclass
class BuildRecord:
    schema_version: int
    kind: str
    session_id: str
    captured_utc: str
    repo: dict
    llama_cpp: dict
    kleidiai: dict
    cache_diff: dict
    builds: dict

    def __post_init__(self) -> None:
        _require(self.kind == "build", f"kind must be 'build', got {self.kind!r}")
        lc = self.llama_cpp
        _require(
            lc.get("commit") and lc.get("commit") == lc.get("expected_commit"),
            "llama.cpp checkout is not at the pinned commit",
        )
        _require(set(self.builds) == {"baseline", "kleidiai"}, "need exactly baseline + kleidiai")
        base, kai = self.builds["baseline"], self.builds["kleidiai"]
        _require(
            base["cmake_options"].get("GGML_CPU_KLEIDIAI") != "ON",
            "baseline build has KleidiAI on",
        )
        _require(kai["cmake_options"].get("GGML_CPU_KLEIDIAI") == "ON", "kleidiai build is off")
        _require(
            isinstance(self.cache_diff.get("unexpected_keys"), list)
            and not self.cache_diff["unexpected_keys"],
            "the two CMake caches differ in more than KleidiAI entries and paths",
        )
        for k in ("tag", "url", "md5"):
            _require(bool(self.kleidiai.get(k)), f"kleidiai.{k} missing")

    @classmethod
    def from_dict(cls, d: dict) -> BuildRecord:
        _check_keys(cls, d, "build record")
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# --- check-builds record (results/raw/build/<session_id>_check_builds.json) ---------------


@dataclass
class SmokeRun:
    model_alias: str
    quant: str
    build: str
    command: list[str]
    returncode: int
    buffers_mib: dict
    buffers_total_mib: float
    tensor_bytes_total: int
    tensor_bytes_by_type: dict
    kleidiai_lines: list[str]
    notable_lines: list[str]
    bench_json: Any
    memory_vs_file: dict

    def __post_init__(self) -> None:
        w = f"smoke run {self.model_alias}_{self.quant}_{self.build}"
        _require(self.returncode == 0, f"{w}: llama-bench exited with {self.returncode}")
        _require(bool(self.buffers_mib), f"{w}: no 'model buffer size' lines were found")

    @classmethod
    def from_dict(cls, d: dict) -> SmokeRun:
        _check_keys(cls, d, "smoke run")
        return cls(**d)


@dataclass
class CheckBuildsRecord:
    schema_version: int
    kind: str
    purpose: str
    use_for_analysis: bool
    session_id: str
    captured_utc: str
    repo: dict
    llama_cpp_commit: str | None
    builds: dict
    runs: list[SmokeRun]

    def __post_init__(self) -> None:
        _require(self.kind == "check_builds", f"kind must be 'check_builds', got {self.kind!r}")
        # These are smoke runs: the speeds in them are one repetition of a tiny test and must
        # never reach analyse.py.
        _require(self.purpose == "smoke", "purpose must be 'smoke'")
        _require(self.use_for_analysis is False, "use_for_analysis must be false")
        _require(self.runs, "no runs")

    @classmethod
    def from_dict(cls, d: dict) -> CheckBuildsRecord:
        _check_keys(cls, d, "check-builds record")
        d = dict(d)
        d["runs"] = [SmokeRun.from_dict(r) for r in d["runs"]]
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# --- peak record (results/raw/peak/<session_id>.json) ---------------------------------------

MIN_PEAK_REPS = 20


def _summary_matches(obj: Any, samples: list[float], where: str) -> None:
    """The stored median/quartiles/IQR/max must be recomputable from the samples."""
    s = summarise(samples)
    for name in ("median", "q1", "q3", "iqr", "max"):
        _require(
            math.isclose(getattr(obj, name), s[name], rel_tol=1e-9),
            f"{where}: {name} does not match the samples",
        )


@dataclass
class PeakPoint:
    instr_class: str
    threads: int
    accumulators: int  # independent dependency chains in the loop
    instr_per_iter: int  # instructions of the class per loop iteration
    iters: int
    pinning: dict
    reps_warmup: int
    reps_timed: int
    ops_per_instruction: float
    samples_instr_per_s: list[float]
    samples_ops_per_s: list[float]
    median: float  # of samples_ops_per_s
    q1: float
    q3: float
    iqr: float
    max: float
    checksum: str

    def __post_init__(self) -> None:
        w = f"peak point {self.instr_class} t={self.threads} acc={self.accumulators}"
        _require(self.instr_class in PEAK_CLASSES, f"{w}: unknown class")
        _require(self.threads > 0 and self.accumulators > 0, f"{w}: bad threads/accumulators")
        _require(
            self.reps_timed >= MIN_PEAK_REPS,
            f"{w}: needs at least {MIN_PEAK_REPS} timed repeats, has {self.reps_timed}",
        )
        _require(
            len(self.samples_instr_per_s) == self.reps_timed == len(self.samples_ops_per_s),
            f"{w}: sample count != reps",
        )
        _require(all(s > 0 for s in self.samples_instr_per_s), f"{w}: non-positive sample")
        _require(
            all(
                math.isclose(o, i * self.ops_per_instruction, rel_tol=1e-9)
                for i, o in zip(self.samples_instr_per_s, self.samples_ops_per_s, strict=True)
            ),
            f"{w}: ops/s is not instructions/s times ops per instruction",
        )
        _require(self.pinning.get("getcpu_ok") is True, f"{w}: sched_getcpu() pin check failed")
        _summary_matches(self, self.samples_ops_per_s, w)

    @classmethod
    def from_dict(cls, d: dict) -> PeakPoint:
        _check_keys(cls, d, "peak point")
        return cls(**d)


@dataclass
class PeakRecord:
    schema_version: int
    kind: str
    session_id: str
    captured_utc: str
    repo: dict
    binary: dict
    host: dict
    sve_vector_bits: int
    points: list[PeakPoint]
    acc_check: list[dict]  # per class: does more accumulators raise the 1-thread peak?
    disasm: dict  # per class: file and the hot-loop checks

    def __post_init__(self) -> None:
        _require(self.kind == "peak", f"kind must be 'peak', got {self.kind!r}")
        _require(self.points, "no peak points")
        keys = [(p.instr_class, p.threads, p.accumulators) for p in self.points]
        _require(len(set(keys)) == len(keys), "duplicate (class, threads, accumulators) points")
        base = [p for p in self.points if p.accumulators == BASE_ACCUMULATORS]
        _require({p.instr_class for p in base} == set(PEAK_CLASSES), "need every peak class")
        threads = {c: {p.threads for p in base if p.instr_class == c} for c in PEAK_CLASSES}
        _require(
            len({frozenset(t) for t in threads.values()}) == 1 and 1 in threads["sdot"],
            "every class needs the same thread counts, 1-thread included",
        )
        _require(
            {a["instr_class"] for a in self.acc_check} == set(PEAK_CLASSES)
            and all(a["pass"] is True for a in self.acc_check),
            "accumulator check missing or failed: more chains still raise the 1-thread peak",
        )
        _require(set(self.disasm) == set(PEAK_CLASSES), "need a disassembly check per class")
        for cls_, d in self.disasm.items():
            _require(
                bool(d.get("checks")) and all(c["ok"] is True for c in d["checks"]),
                f"{cls_}: disassembly check failed (wrong instruction, count or memory access)",
            )

    @classmethod
    def from_dict(cls, d: dict) -> PeakRecord:
        _check_keys(cls, d, "peak record")
        d = dict(d)
        d["points"] = [PeakPoint.from_dict(p) for p in d["points"]]
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class GgmlInstructionRecord:
    """F16 instruction counts (ADR-015) and the tiled flash-attention function (ADR-020) of each
    build's ggml CPU library. The kind keeps its Day 3 name."""

    schema_version: int
    kind: str
    session_id: str
    captured_utc: str
    repo: dict
    builds: dict  # build -> {"files": [{path, sha256, counts, top_symbols}], "counts": {...}}

    def __post_init__(self) -> None:
        _require(self.kind == "ggml_f16_instructions", f"bad kind {self.kind!r}")
        _require(set(self.builds) == {"baseline", "kleidiai"}, "need baseline + kleidiai")
        for name, b in self.builds.items():
            for key in ("fmlalb", "fmlalt", "fmla_8h"):
                _require(
                    isinstance(b["counts"].get(key), int) and b["counts"][key] >= 0,
                    f"{name}: counts.{key} must be a non-negative integer",
                )
            attn = b.get("flash_attn_tiled")
            _require(
                isinstance(attn, dict) and "found" in attn, f"{name}: flash_attn_tiled missing"
            )
            if attn["found"]:
                _require(
                    bool(attn.get("disasm_file")), f"{name}: no disassembly file for attention"
                )
                for key in ("fmadd_s", "fmla_4s", "fmla_sve_s"):
                    _require(
                        isinstance(attn["counts"].get(key), int) and attn["counts"][key] >= 0,
                        f"{name}: flash_attn_tiled counts.{key} must be a non-negative integer",
                    )

    @classmethod
    def from_dict(cls, d: dict) -> GgmlInstructionRecord:
        _check_keys(cls, d, "ggml instruction record")
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# --- bench record (results/raw/bench/<session_id>/<config_id>.json) --------------------------

BENCH_BUILDS = ("baseline", "kleidiai")


@dataclass
class BenchRecord:
    """One llama-bench call (one point, one build). llama-bench's own JSON is kept unchanged."""

    schema_version: int
    kind: str
    session_id: str
    captured_utc: str
    config_id: str
    pair_id: str
    model_alias: str
    quant: str
    build: str
    threads: int
    test: str
    attempt: int  # 1, or 2 for the re-run of a noisy point (saved as <config_id>__2.json)
    repetitions: int
    pair_index: int
    order_in_pair: int  # 1 if this build ran first in its pair, else 2
    repo: dict
    llama_cpp: dict
    model: dict
    settings: dict
    command: list[str]
    pinning: dict
    loadavg_before: list[float] | None
    loadavg_after: list[float] | None
    wall_seconds: float
    returncode: int
    summary: dict  # summarise() of the per-repetition tokens/s samples
    noisy: bool
    llama_bench: list  # llama-bench -o json, unchanged
    stderr_notable: list[str]  # load-log lines that say who owns the weights, warnings, errors

    def __post_init__(self) -> None:
        from edge_llm import sweep  # local import: keeps this module free of sweep at load time

        w = f"bench record {self.config_id}"
        _require(self.kind == "bench", f"{w}: kind must be 'bench'")
        point = sweep.parse_config_id(self.config_id)
        _require(
            (point.model, point.quant, point.build, point.threads, point.test)
            == (self.model_alias, self.quant, self.build, self.threads, self.test),
            f"{w}: config_id does not match its own fields",
        )
        _require(self.pair_id == point.pair_id, f"{w}: pair_id does not match")
        _require(self.build in BENCH_BUILDS, f"{w}: unknown build")
        _require(self.attempt in (1, 2), f"{w}: attempt must be 1 or 2")
        _require(self.order_in_pair in (1, 2), f"{w}: order_in_pair must be 1 or 2")
        _require(self.returncode == 0, f"{w}: llama-bench exited with {self.returncode}")
        _require(_is_sha256(self.model.get("sha256")), f"{w}: model sha256 missing or malformed")
        _require(
            self.model.get("file_bytes") == self.model.get("table_file_bytes"),
            f"{w}: model file size differs from its tensor table",
        )
        _require(len(self.llama_bench) == 1, f"{w}: expected exactly one llama-bench test")
        row = self.llama_bench[0]
        test = sweep.parse_test(self.test)
        want_pp, want_tg = (test.tokens, 0) if test.kind == "pp" else (0, test.tokens)
        _require(
            (row.get("n_prompt"), row.get("n_gen"), row.get("n_depth"))
            == (want_pp, want_tg, test.depth),
            f"{w}: llama-bench ran a different test than its config_id says",
        )
        _require(row.get("n_threads") == self.threads, f"{w}: llama-bench thread count differs")
        _require(str(row.get("flash_attn")) == str(self.settings.get("flash_attn")), f"{w}: -fa")
        _require(
            str(row.get("cpu_strict")).lower() in ("true", "1"), f"{w}: --cpu-strict was not on"
        )
        for key in ("n_batch", "n_ubatch"):
            _require(row.get(key) == self.settings.get(key), f"{w}: {key} differs from settings")
        ts = row.get("samples_ts")
        ns = row.get("samples_ns")
        _require(
            isinstance(ts, list)
            and isinstance(ns, list)
            and len(ts) == len(ns) == self.repetitions,
            f"{w}: samples_ts/samples_ns must hold {self.repetitions} repetitions",
        )
        _require(all(s > 0 for s in ts) and all(s > 0 for s in ns), f"{w}: non-positive sample")
        s = summarise(ts)
        for name in ("median", "q1", "q3", "iqr"):
            _require(
                math.isclose(self.summary.get(name, math.nan), s[name], rel_tol=1e-9),
                f"{w}: summary.{name} does not match the samples",
            )
        _require(
            self.noisy == (s["iqr_over_median"] > NOISY_THRESHOLD),
            f"{w}: noisy flag disagrees with IQR/median",
        )

    @classmethod
    def from_dict(cls, d: dict) -> BenchRecord:
        _check_keys(cls, d, "bench record")
        return cls(**d)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
