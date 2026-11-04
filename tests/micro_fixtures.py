"""A synthetic micro record with hand-picked round numbers (structure and arithmetic only: these are
not measurements). Shared by the micro tests and the figure test."""

from __future__ import annotations

import math

from edge_llm import micro
from edge_llm.stats import summarise

SHA = "a" * 64
# Median nanoseconds per call of every variant, per working set. Chosen so the arithmetic is easy
# to do by hand: L1 has 16384 weight bytes, DRAM has 2^30.
L1_NS = {
    "scalar": 4096.0, "autovec": 1024.0, "sdot_a4": 256.0, "sdot_a8": 128.0,
    "smmla_a4": 160.0, "smmla_a8": 100.0, "sve_a4": 300.0, "sve_a8": 150.0,
}  # fmt: skip
DRAM_NS = {
    "scalar": 4.0e8, "autovec": 1.0e8, "sdot_a4": 33_554_432.0 * 1.25, "sdot_a8": 33_554_432.0,
    "smmla_a4": 33_554_432.0 * 1.1, "smmla_a8": 33_554_432.0, "sve_a4": 40_000_000.0,
    "sve_a8": 36_000_000.0,
}  # fmt: skip
B_BEST, B_ONE = 40e9, 32e9  # bytes/s
C_SDOT, C_SMMLA = 400e9, 800e9  # ops/s


def make_point(variant: str, ws: str, median_ns: float, reps: int = 30) -> dict:
    family, acc = micro.VARIANTS[variant]
    weight = micro.ROWS[ws] * micro.K
    mpw = micro.MACS_PER_WEIGHT_BYTE[family]
    calls = 1 if ws == "DRAM" else math.ceil(0.02 / (median_ns * 1e-9))  # ~20 ms per repetition
    # 6 x each of -0.2 %, -0.1 %, 0, +0.1 %, +0.2 %: the median is exactly median_ns
    samples = [median_ns * (1 + 0.001 * (i % 5 - 2)) for i in range(reps)]
    s = summarise(samples)
    return {
        "variant": variant, "family": family, "accumulators": acc, "working_set": ws,
        "rows": micro.ROWS[ws], "k": micro.K, "weight_bytes": weight,
        "macs_per_call": weight * mpw, "macs_per_weight_byte": mpw, "calls_per_rep": calls,
        "pinning": {"getcpu_ok": True, "observed_cpu": 0, "taskset_cpus": "0"},
        "reps_warmup": 3, "reps_timed": reps, "output_matches_scalar": True,
        "samples_ns_per_call": samples, "median_ns": s["median"], "q1_ns": s["q1"],
        "q3_ns": s["q3"], "iqr_ns": s["iqr"], "max_ns": s["max"], "checksum": "0x1",
    }  # fmt: skip


def disasm_ok(failed=()) -> dict:
    return {
        v: {
            "ok": v not in failed, "variant": v, "family": micro.VARIANTS[v][0], "file": f"{v}.s",
            "expected": "sdot v-form", "expected_count": micro.VARIANTS[v][1],
            "loop_instructions": 9, "simd_multiply_in_loop": [],
        }
        for v in micro.VARIANTS
    }  # fmt: skip


def references() -> dict:
    return {
        "bandwidth_record": {
            "path": "results/raw/bandwidth/X_start.json", "sha256": SHA,
            "B_best_Bps": B_BEST, "B_one_stream_Bps": B_ONE,
        },
        "peak_record": {
            "path": "results/raw/peak/Y.json", "sha256": SHA,
            "C_sdot_ops_per_s": C_SDOT, "C_smmla_ops_per_s": C_SMMLA,
        },
    }  # fmt: skip


def micro_record(failed=(), dram_ns=None, l1_ns=None) -> dict:
    dram_ns = dram_ns or DRAM_NS
    l1_ns = l1_ns or L1_NS
    points = [make_point(v, "L1", l1_ns[v]) for v in micro.VARIANTS]
    points += [make_point(v, "DRAM", dram_ns[v]) for v in micro.VARIANTS]
    return {
        "schema_version": 1,
        "kind": "micro",
        "session_id": "S",
        "captured_utc": "2026-11-05T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "binary": {},
        "host": {},
        "sve_vector_bits": 128,
        "features": {"neon": True, "dotprod": True, "i8mm": True, "sve": True},
        "kernel": {"smmla_macs_per_weight_byte": 2},
        "check": {"ok": True, "cases": 66},
        "points": points,
        "disasm": disasm_ok(failed),
        "references": references(),
    }
