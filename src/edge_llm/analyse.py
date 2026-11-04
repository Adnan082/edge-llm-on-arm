"""Raw -> processed tables: median / IQR, ratio to the v1 prediction, KleidiAI speed-ups.

    python -m edge_llm.analyse [--session 2026-11-02T2215Z]        (make analyse)

Reads results/raw/bench/<session>/, results/raw/bandwidth/<session>_{start,end}.json and the frozen
predictions results/predictions/v1.csv. Writes results/processed/{points,kleidiai,
session_bandwidth}.csv. Nothing under results/raw/ or results/predictions/ is ever written
(ARCHITECTURE.md rules 1 and 2): a run is left out only by a named rule in this file.

The one exclusion rule is RERUN_RULE (CLAUDE.md §7.4), see `apply_rerun_rule`.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from edge_llm import bandwidth, sweep
from edge_llm.schema import BandwidthRecord, BenchRecord
from edge_llm.stats import is_noisy, summarise

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = "2026-11-02T2215Z"
PREDICTIONS = Path("results/predictions/v1.csv")
BENCH_DIR = Path("results/raw/bench")
BANDWIDTH_DIR = Path("results/raw/bandwidth")
PROCESSED_DIR = Path("results/processed")
EXPECTED_POINTS = 144  # the full sweep (ADR-024): 4 formats x 2 builds x 18 tests

# How much of a format KleidiAI takes on this CPU (CLAUDE.md §5, ADR-013). F16 is the negative
# control; Q4_K_M is partial (only its Q6_K tensors move).
KLEIDIAI_COVERAGE = {
    "F16": "none (negative control)",
    "Q8_0": "full",
    "Q4_0": "full",
    "Q4_K_M": "partial (Q6_K tensors only)",
}

# Columns of v1.csv that are numbers; the rest are copied as text.
_PREDICTION_TEXT = {
    "config_id", "pair_id", "model", "quant", "build", "test", "phase",
    "C_weight_class", "binding", "C_weight_class_sustained", "binding_sustained",
}  # fmt: skip

POINT_COLUMNS = [
    "config_id", "pair_id", "model", "quant", "build", "threads", "test", "phase", "tokens",
    # the measurement (CLAUDE.md §7.4)
    "measured_median", "q1", "q3", "iqr", "iqr_over_median", "n_reps",
    "attempt_used", "noisy_first_attempt", "still_noisy", "source_file",
    # the frozen v1 prediction and the two sensitivity ratios
    "predicted_tps", "ratio", "binding",
    "predicted_tps_sustained", "ratio_sustained", "binding_sustained",
    "B_session", "predicted_tps_session_B", "ratio_session_B",
    # what the prediction was built from (copied from v1.csv)
    "bytes", "weight_flops", "attention_flops", "arith_intensity",
    "B", "B1", "C_weight_class", "C_weight", "C_attn",
    "C_weight_class_sustained", "C_weight_sustained", "C_attn_sustained",
    "t_memory", "t_compute", "t_compute_sustained",
    # what the machine actually did
    "achieved_GBps", "fraction_of_B", "achieved_GOPS", "fraction_of_C", "fraction_of_C_sustained",
]  # fmt: skip

KLEIDIAI_COLUMNS = [
    "pair_id", "model", "quant", "threads", "test", "phase", "coverage",
    "baseline_median", "baseline_q1", "baseline_q3", "baseline_iqr_over_median",
    "baseline_still_noisy",
    "kleidiai_median", "kleidiai_q1", "kleidiai_q3", "kleidiai_iqr_over_median",
    "kleidiai_still_noisy",
    "speedup", "speedup_lo", "speedup_hi",
]  # fmt: skip

SESSION_BANDWIDTH_COLUMNS = [
    "threads", "start_GBps", "end_GBps", "drift_pct", "session_B_GBps", "v1_B_GBps",
    "session_over_v1", "start_variant", "end_variant",
]  # fmt: skip


# --- the rules ------------------------------------------------------------------------------


def apply_rerun_rule(samples_by_attempt: dict[int, Sequence[float]]) -> tuple[int, bool]:
    """RERUN_RULE (CLAUDE.md §7.4): which attempt of a point is used, and is it still noisy.

    - attempt 1 is not noisy                    -> use attempt 1
    - attempt 1 is noisy and attempt 2 exists   -> use attempt 2; still_noisy if it is noisy too
    - attempt 1 is noisy and there is no attempt 2 -> use attempt 1, still_noisy (it was never
      re-run; the caller prints a warning)

    Returns (attempt_used, still_noisy). Both attempts stay on disk either way.
    """
    if 1 not in samples_by_attempt:
        raise ValueError("a point has a re-run but no first attempt")
    if not is_noisy(samples_by_attempt[1]):
        return 1, False
    second = samples_by_attempt.get(2)
    if second is None:
        return 1, True
    return 2, is_noisy(second)


def speedup_range(
    base: tuple[float, float, float], kl: tuple[float, float, float]
) -> tuple[float, float, float]:
    """(speedup, lo, hi) from (q1, median, q3) of each build.

    speedup = kleidiai median / baseline median. The conservative range pairs the worst case of
    one build with the best case of the other: lo = kleidiai Q1 / baseline Q3, hi = kleidiai Q3 /
    baseline Q1.
    """
    b_q1, b_med, b_q3 = base
    k_q1, k_med, k_q3 = kl
    return k_med / b_med, k_q1 / b_q3, k_q3 / b_q1


def tokens_per_unit(phase: str, prompt_tokens: int) -> int:
    """Tokens that one prediction row's bytes and FLOPs cover: P for a prefill, 1 for a token."""
    return prompt_tokens if phase == "prefill" else 1


def achieved_rates(row: dict, measured_tps: float) -> dict:
    """Bandwidth and arithmetic rates a measured speed implies (decode: per token; prefill: the
    prompt's bytes and FLOPs spread over its P tokens)."""
    tokens = tokens_per_unit(row["phase"], row["prompt_tokens"])
    units_per_s = measured_tps / tokens  # tokens/s over tokens per unit = units per second
    bytes_per_s = row["bytes"] * units_per_s
    flops_per_s = (row["weight_flops"] + row["attention_flops"]) * units_per_s
    weight_flops_per_s = row["weight_flops"] * units_per_s
    return {
        "achieved_GBps": bytes_per_s / 1e9,
        "fraction_of_B": bytes_per_s / row["B"],
        "achieved_GOPS": flops_per_s / 1e9,
        "fraction_of_C": weight_flops_per_s / row["C_weight"],
        "fraction_of_C_sustained": weight_flops_per_s / row["C_weight_sustained"],
    }


def session_prediction(row: dict, b_session: float) -> float:
    """The v1 prediction with only the memory term recomputed from this session's bandwidth."""
    tokens = tokens_per_unit(row["phase"], row["prompt_tokens"])
    t_memory = row["bytes"] / b_session
    return tokens / max(t_memory, row["t_compute"])


# --- loading --------------------------------------------------------------------------------


def load_predictions(path: Path) -> dict[str, dict]:
    """v1.csv as {config_id: row} with numbers converted. An empty cell becomes None."""
    out: dict[str, dict] = {}
    with open(path, newline="") as f:
        for raw in csv.DictReader(f):
            row = {
                k: (v if k in _PREDICTION_TEXT else (float(v) if v != "" else None))
                for k, v in raw.items()
            }
            for k in ("threads", "prompt_tokens", "gen_tokens", "depth"):
                row[k] = int(row[k])
            out[row["config_id"]] = row
    return out


def load_bench_session(
    bench_dir: Path, session: str
) -> dict[str, dict[int, tuple[BenchRecord, Path]]]:
    """Every point record of a session, validated: {config_id: {attempt: (record, path)}}.

    Files starting with `_` (the pilot summary) are not points. A file `<id>__2.json` must hold
    attempt 2 of `<id>`; anything else is an error, never a silent skip.
    """
    found: dict[str, dict[int, tuple[BenchRecord, Path]]] = defaultdict(dict)
    for path in sorted(bench_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        stem = path.stem
        file_attempt = 2 if stem.endswith("__2") else 1
        config_id = stem[: -len("__2")] if file_attempt == 2 else stem
        record = BenchRecord.from_dict(json.loads(path.read_text()))  # raises on a bad record
        if record.config_id != config_id or record.attempt != file_attempt:
            raise ValueError(f"{path.name}: holds {record.config_id} attempt {record.attempt}")
        if record.session_id != session:
            raise ValueError(f"{path.name}: belongs to session {record.session_id}, not {session}")
        found[config_id][file_attempt] = (record, path)
    return dict(found)


def join_check(measured_ids: set[str], predicted_ids: set[str]) -> None:
    """Fail loudly unless the measured and predicted points are the same set."""
    no_prediction = sorted(measured_ids - predicted_ids)
    no_measurement = sorted(predicted_ids - measured_ids)
    if no_prediction or no_measurement:
        raise ValueError(
            f"measurements and v1 predictions do not match: {len(no_measurement)} predicted points"
            f" with no measurement {no_measurement[:10]}, {len(no_prediction)} measured points"
            f" with no prediction {no_prediction[:10]}"
        )


def session_bandwidth(root: Path, session: str, v1_b: dict[int, float]) -> list[dict]:
    """B(t) at the start and end of the session (best valid read variant per t, the v1 rule)."""
    at = {}
    for phase in ("start", "end"):
        path = root / BANDWIDTH_DIR / f"{session}_{phase}.json"
        at[phase] = bandwidth.b_of_record(BandwidthRecord.from_dict(json.loads(path.read_text())))
    rows = []
    for t in sorted(at["start"]):
        if t not in at["end"] or t not in v1_b:
            raise ValueError(f"t = {t} is missing from the session's end bandwidth or from v1")
        s, e = at["start"][t], at["end"][t]
        mid = statistics.median([s.b, e.b])
        rows.append(
            {
                "threads": t,
                "start_GBps": s.b / 1e9,
                "end_GBps": e.b / 1e9,
                "drift_pct": 100 * (e.b - s.b) / s.b,
                "session_B_GBps": mid / 1e9,
                "v1_B_GBps": v1_b[t] / 1e9,
                "session_over_v1": mid / v1_b[t],
                "start_variant": f"{s.accumulators}acc_{s.streams}streams",
                "end_variant": f"{e.accumulators}acc_{e.streams}streams",
            }
        )
    return rows


# --- building the tables --------------------------------------------------------------------


def build_points(
    attempts: dict[str, dict[int, tuple[BenchRecord, Path]]],
    predictions: dict[str, dict],
    b_session: dict[int, float],
    root: Path,
) -> list[dict]:
    """One row per config_id: the measurement, the prediction, the ratios and the rates."""
    join_check(set(attempts), set(predictions))
    rows = []
    for config_id in sorted(attempts):
        by_attempt = attempts[config_id]
        samples = {a: rec.llama_bench[0]["samples_ts"] for a, (rec, _) in by_attempt.items()}
        used, still_noisy = apply_rerun_rule(samples)
        record, path = by_attempt[used]
        s = summarise(samples[used])  # from the per-repetition samples, not llama-bench's mean
        pred = predictions[config_id]
        if (pred["model"], pred["quant"], pred["build"], pred["threads"], pred["test"]) != (
            record.model_alias, record.quant, record.build, record.threads, record.test,
        ):  # fmt: skip
            raise ValueError(f"{config_id}: prediction row describes a different point")
        med = s["median"]
        b_s = b_session[pred["threads"]]
        pred_session = session_prediction(pred, b_s)
        row = {
            **{k: pred[k] for k in POINT_COLUMNS if k in pred},
            "tokens": tokens_per_unit(pred["phase"], pred["prompt_tokens"]),
            "measured_median": med,
            "q1": s["q1"],
            "q3": s["q3"],
            "iqr": s["iqr"],
            "iqr_over_median": s["iqr_over_median"],
            "n_reps": s["n"],
            "attempt_used": used,
            "noisy_first_attempt": is_noisy(samples[1]),
            "still_noisy": still_noisy,
            "source_file": path.relative_to(root).as_posix(),
            "ratio": med / pred["predicted_tps"],
            "ratio_sustained": med / pred["predicted_tps_sustained"],
            "B_session": b_s,
            "predicted_tps_session_B": pred_session,
            "ratio_session_B": med / pred_session,
            "arith_intensity": (pred["weight_flops"] + pred["attention_flops"]) / pred["bytes"],
            **achieved_rates(pred, med),
        }
        rows.append(row)
    return rows


def build_kleidiai(points: list[dict]) -> list[dict]:
    """One row per pair_id with both builds: medians, IQRs and the speed-up with its range."""
    by_pair: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in points:
        by_pair[r["pair_id"]][r["build"]] = r
    rows = []
    for pair_id in sorted(by_pair):
        builds = by_pair[pair_id]
        if set(builds) != set(sweep.BUILDS):
            raise ValueError(f"{pair_id}: needs both builds, has {sorted(builds)}")
        b, k = builds["baseline"], builds["kleidiai"]
        speedup, lo, hi = speedup_range(
            (b["q1"], b["measured_median"], b["q3"]), (k["q1"], k["measured_median"], k["q3"])
        )
        row = {
            "pair_id": pair_id,
            "model": b["model"],
            "quant": b["quant"],
            "threads": b["threads"],
            "test": b["test"],
            "phase": b["phase"],
            "coverage": KLEIDIAI_COVERAGE[b["quant"]],
            "speedup": speedup,
            "speedup_lo": lo,
            "speedup_hi": hi,
        }
        for name, r in (("baseline", b), ("kleidiai", k)):
            row[f"{name}_median"] = r["measured_median"]
            row[f"{name}_q1"] = r["q1"]
            row[f"{name}_q3"] = r["q3"]
            row[f"{name}_iqr_over_median"] = r["iqr_over_median"]
            row[f"{name}_still_noisy"] = r["still_noisy"]
        rows.append(row)
    return rows


# --- output ---------------------------------------------------------------------------------


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _spread(values: list[float]) -> str:
    if not values:
        return "no points"
    return f"min {min(values):.3f}  median {statistics.median(values):.3f}  max {max(values):.3f}"


def summary_lines(points: list[dict]) -> list[str]:
    """Short printout: ratio spread per phase, noisy points, and a WARNING for every ratio > 1
    (CLAUDE.md §8: a ratio above 1 means the model is wrong somewhere and is never hidden)."""
    lines = [f"{len(points)} points"]
    for column, label in (
        ("ratio", "ratio (v1)"),
        ("ratio_sustained", "ratio vs sustained-C prediction"),
        ("ratio_session_B", "ratio with this session's B"),
    ):
        for phase in ("prefill", "decode"):
            vals = [r[column] for r in points if r["phase"] == phase]
            lines.append(f"{label:<34} {phase:<8} n={len(vals):<3} {_spread(vals)}")
    noisy = [r["config_id"] for r in points if r["still_noisy"]]
    rerun = sum(1 for r in points if r["attempt_used"] == 2)
    lines.append(f"re-run used for {rerun} points; still noisy after the rule: {len(noisy)}")
    lines += [f"  noisy: {c}" for c in noisy]
    never_rerun = [
        r["config_id"] for r in points if r["noisy_first_attempt"] and r["attempt_used"] == 1
    ]
    lines += [f"WARNING noisy first attempt never re-run: {c}" for c in never_rerun]
    for column in ("ratio", "ratio_sustained", "ratio_session_B"):
        over = [r for r in points if r[column] > 1]
        lines.append(f"{column} > 1: {len(over)} points")
        lines += [
            f"WARNING {column} = {r[column]:.3f} > 1: {r['config_id']}"
            f" (measured {r['measured_median']:.2f}, predicted {r['predicted_tps']:.2f},"
            f" {r['binding']}-bound)"
            for r in sorted(over, key=lambda r: -r[column])
        ]
    return lines


def run(root: Path = REPO_ROOT, session: str = DEFAULT_SESSION, out_dir: Path | None = None):
    """Read the session, write the three processed tables, return (points, pairs, bandwidth)."""
    predictions = load_predictions(root / PREDICTIONS)
    if len(predictions) != EXPECTED_POINTS:
        raise ValueError(f"v1.csv has {len(predictions)} rows, expected {EXPECTED_POINTS}")
    attempts = load_bench_session(root / BENCH_DIR / session, session)
    v1_b = {int(r["threads"]): r["B"] for r in predictions.values()}
    bw_rows = session_bandwidth(root, session, v1_b)
    b_session = {r["threads"]: r["session_B_GBps"] * 1e9 for r in bw_rows}
    points = build_points(attempts, predictions, b_session, root)
    pairs = build_kleidiai(points)
    out = out_dir or root / PROCESSED_DIR
    write_csv(out / "points.csv", POINT_COLUMNS, points)
    write_csv(out / "kleidiai.csv", KLEIDIAI_COLUMNS, pairs)
    write_csv(out / "session_bandwidth.csv", SESSION_BANDWIDTH_COLUMNS, bw_rows)
    return points, pairs, bw_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", default=DEFAULT_SESSION)
    parser.add_argument("--out-dir", type=Path, help="default: results/processed")
    args = parser.parse_args()
    points, pairs, bw_rows = run(session=args.session, out_dir=args.out_dir)
    print("\n".join(summary_lines(points)))
    print(f"{len(pairs)} KleidiAI pairs; session bandwidth:")
    for r in bw_rows:
        print(
            f"  t={r['threads']}: start {r['start_GBps']:.2f}  end {r['end_GBps']:.2f} GB/s"
            f"  drift {r['drift_pct']:+.2f} %  session/v1 {r['session_over_v1']:.3f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
