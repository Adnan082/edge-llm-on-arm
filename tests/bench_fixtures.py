"""Synthetic bench records and model sizes shared by the Day 3 tests (no hardware, no llama.cpp)."""

from __future__ import annotations

from pathlib import Path

import yaml

from edge_llm import sweep
from edge_llm.stats import is_noisy, summarise

REPO = Path(__file__).resolve().parents[1]


def real_cfg() -> dict:
    return yaml.safe_load((REPO / "configs" / "sweep.yaml").read_text())


# parameters (all tensors) and block parameters, so that W_all follows the format's bits/weight
_PARAMS = {"small": (0.60e9, 0.44e9), "large": (1.72e9, 1.41e9)}
_BITS = {"F16": 16.0, "Q8_0": 8.5, "Q4_0": 4.5, "Q4_K_M": 5.0}


def fake_sizes(cfg: dict | None = None) -> dict:
    cfg = cfg or real_cfg()
    out = {}
    for m in cfg["models"]:
        n_all, n_blk = _PARAMS[m]
        for q in cfg["quants"]:
            w = n_all * _BITS[q] / 8
            out[(m, q)] = {"file_bytes": int(w * 1.01), "N_blk": n_blk, "W_all": int(w)}
    return out


def fake_bench_record(
    config_id: str,
    tps: float = 100.0,
    reps: int = 5,
    wall: float = 60.0,
    attempt: int = 1,
    noisy: bool = False,
    file_bytes: int = 1_000_000,
    pair_index: int = 0,
) -> dict:
    """A record that passes BenchRecord validation. `noisy` widens the samples to ~20 % IQR."""
    point = sweep.parse_config_id(config_id)
    test = sweep.parse_test(point.test)
    spread = 0.2 if noisy else 0.002
    samples = [tps * (1 + spread * (i - (reps - 1) / 2) / reps) for i in range(reps)]
    assert is_noisy(samples) == noisy
    tokens = test.tokens
    row = {
        "n_prompt": tokens if test.kind == "pp" else 0,
        "n_gen": tokens if test.kind == "tg" else 0,
        "n_depth": test.depth,
        "n_threads": point.threads,
        "n_batch": 2048,
        "n_ubatch": 512,
        "flash_attn": 1,
        "cpu_mask": sweep.cpu_mask(point.threads),
        "cpu_strict": True,
        "samples_ns": [int(1e9 * tokens / s) for s in samples],
        "samples_ts": samples,
    }
    s = summarise(samples)
    order = sweep.build_order(pair_index).index(point.build) + 1
    return {
        "schema_version": 1,
        "kind": "bench",
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "config_id": config_id,
        "pair_id": point.pair_id,
        "model_alias": point.model,
        "quant": point.quant,
        "build": point.build,
        "threads": point.threads,
        "test": point.test,
        "attempt": attempt,
        "repetitions": reps,
        "pair_index": pair_index,
        "order_in_pair": order,
        "repo": {"commit": "a" * 40, "dirty": False},
        "llama_cpp": {"commit": "d" * 40, "dirty": False},
        "model": {
            "file": f"work/models/{point.model}_{point.quant}.gguf",
            "sha256": "b" * 64,
            "file_bytes": file_bytes,
            "table_file_bytes": file_bytes,
            "table": f"results/models/{point.model}_{point.quant}.json",
        },
        "settings": {"n_batch": 2048, "n_ubatch": 512, "flash_attn": 1, "warmup": True},
        "command": ["taskset", "-c", "0", "llama-bench"],
        "pinning": {"cpu_mask": sweep.cpu_mask(point.threads), "cpu_strict": 1},
        "loadavg_before": [0.1, 0.1, 0.1],
        "loadavg_after": [0.2, 0.1, 0.1],
        "wall_seconds": wall,
        "returncode": 0,
        "summary": s,
        "noisy": noisy,
        "llama_bench": [row],
        "stderr_notable": [],
    }
