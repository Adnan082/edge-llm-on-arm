"""Schemas for the records the pipeline writes (ARCHITECTURE.md §4).

Plain dataclasses, no third-party validation library. Each `from_dict` rejects missing or
unknown keys and checks the invariants a downstream step relies on; `to_dict` gives back the
JSON-ready form. Day 2 covers: model tensor tables, bandwidth records, build records and
check-builds (smoke) records. The bench record (llama-bench output) is added on Day 3.
"""

from __future__ import annotations

import dataclasses
import math
import re
from dataclasses import dataclass, field, fields
from typing import Any

from edge_llm.stats import summarise

SCHEMA_VERSION = 1
ROLES = ("blk", "out", "emb", "other")
BANDWIDTH_KERNELS = ("read", "triad")
MIN_BANDWIDTH_REPS = 20  # CLAUDE.md-style rule from the Day 2 brief: at least 20 timed repeats
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SchemaError(ValueError):
    """A record does not match its schema."""


def _check_keys(cls: type, d: dict, where: str) -> None:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: expected an object, got {type(d).__name__}")
    names = {f.name for f in fields(cls)}
    missing, extra = names - d.keys(), d.keys() - names
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

    def __post_init__(self) -> None:
        w = f"bandwidth point {self.kernel} t={self.threads}"
        _require(self.kernel in BANDWIDTH_KERNELS, f"{w}: unknown kernel")
        _require(self.threads > 0, f"{w}: threads must be positive")
        _require(
            self.reps_timed >= MIN_BANDWIDTH_REPS,
            f"{w}: needs at least {MIN_BANDWIDTH_REPS} timed repeats, has {self.reps_timed}",
        )
        _require(len(self.samples_bytes_per_s) == self.reps_timed, f"{w}: sample count != reps")
        _require(all(s > 0 for s in self.samples_bytes_per_s), f"{w}: non-positive sample")
        _require(self.checksum_ok is True, f"{w}: checksum did not match the known answer")
        _require(self.pinning.get("getcpu_ok") is True, f"{w}: sched_getcpu() pin check failed")
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
    acc_check: dict
    objdump_file: str

    def __post_init__(self) -> None:
        _require(self.kind == "bandwidth", f"kind must be 'bandwidth', got {self.kind!r}")
        _require(self.phase in ("start", "end"), f"phase must be start or end: {self.phase!r}")
        _require(self.points, "no bandwidth points")
        seen = {(p.kernel, p.threads) for p in self.points}
        _require(len(seen) == len(self.points), "duplicate (kernel, threads) points")
        _require(
            {k for k, _ in seen} == set(BANDWIDTH_KERNELS),
            f"expected both kernels {BANDWIDTH_KERNELS}",
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
