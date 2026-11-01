"""What the Day 3 pilot tells us: repeat noise per point, and the full sweep's wall time.

Input is a list of bench records (dicts, schema BenchRecord) from the pilot session. Nothing here
calls hardware or reads files, so it is tested in CI; bench/run_sweep.py feeds it and writes the
result next to the pilot's records.

Wall-time method (CLAUDE.md §7 item 10), stated so it can be argued with:

  One llama-bench call costs   overhead + warm-up + repetitions x rep_time (+ depth fill).
    pp<N>      warm-up is one full prompt run, so (reps + 1) x N / prefill_tps
    tg<N>      warm-up is one token (negligible), so reps x N / decode_tps
    tg<N>d<D>  as tg, plus the D-token context filled once before the first timed run
  `overhead` is everything else (model load, repacking or KleidiAI conversion, context set-up);
  it is taken from the pilot calls as wall - the terms above, divided by the model file size, and
  scaled to a file's size. The median over the pilot calls of a build is used (a first load from a
  cold disk is in the maximum, reported as the upper bound).

  Speeds for points the pilot did not run are scaled from the pilot's, per build:
    quantisation  a format the pilot did not run takes the speed of the slowest pilot format of
                  that model (an upper bound on time: Q8_0 and Q4_K_M files are smaller than F16)
    threads       t = 2 and 4 by log-log interpolation between t = 1 and t = 8
    model size    prefill is compute-bound: tokens/s scales as N_blk of the reference model over
                  N_blk of the model; decode is bandwidth-bound: tokens/s scales as the file's
                  weight bytes (W_all) of the reference over the model's
    prompt length prefill tokens/s is taken as independent of N, except at N >= 2048, where it is
                  multiplied by the factor (<= 1) that the pilot's extra long-prompt point showed
  Re-runs of noisy points add the pilot's noisy fraction of the total.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

from edge_llm import sweep
from edge_llm.stats import summarise

GIB = 1024**3
HIGH_PROMPT = 2048  # prompt lengths at or above this get the long-prompt correction


# --- repeat noise --------------------------------------------------------------------------


def latest_records(records: Sequence[dict]) -> dict[str, dict]:
    """{config_id: record}: a re-run (attempt 2) supersedes the first run (ARCHITECTURE.md rule 2)."""
    out: dict[str, dict] = {}
    for r in sorted(records, key=lambda r: r["attempt"]):
        out[r["config_id"]] = r
    return out


def noise_rows(records: Sequence[dict]) -> list[dict]:
    """One row per record (both attempts): tokens/s median, IQR and IQR/median."""
    rows = []
    for r in sorted(records, key=lambda r: (r["config_id"], r["attempt"])):
        s = summarise(r["llama_bench"][0]["samples_ts"])
        rows.append(
            {
                "config_id": r["config_id"],
                "attempt": r["attempt"],
                "repetitions": r["repetitions"],
                "median_tps": s["median"],
                "iqr_tps": s["iqr"],
                "iqr_over_median": s["iqr_over_median"],
                "noisy": r["noisy"],
                "wall_seconds": r["wall_seconds"],
            }
        )
    return rows


# --- wall-time estimate --------------------------------------------------------------------


def _tokens(test: sweep.Test) -> int:
    return test.tokens


def _rep_seconds(test: sweep.Test, tps: float) -> float:
    return _tokens(test) / tps


def _call_seconds(test: sweep.Test, reps: int, tps: float, prefill_tps: float | None) -> float:
    """Everything in a call except its overhead."""
    rep = _rep_seconds(test, tps)
    if test.kind == "pp":
        return (reps + 1) * rep
    fill = test.depth / prefill_tps if test.depth and prefill_tps else 0.0
    return reps * rep + fill


def _loglog(t: int, t1: float, t8: float, lo: int = 1, hi: int = 8) -> float:
    """Speed at t threads between speeds at lo and hi, a straight line on log-log axes."""
    return t1 * (t8 / t1) ** (math.log(t / lo) / math.log(hi / lo))


class _Reference:
    """Median tokens/s of the pilot's points, with the scaling rules of the module docstring."""

    def __init__(self, records: dict[str, dict], cfg: dict, sizes: dict):
        self.cfg, self.sizes = cfg, sizes
        self.tps = {
            (r["model_alias"], r["quant"], r["build"], r["threads"], r["test"]): r["summary"][
                "median"
            ]
            for r in records.values()
        }
        pilot = cfg["pilot"]
        self.ref_model = pilot["models"][0]
        self.quants = list(pilot["quants"])
        self.pilot_threads = sorted(pilot["threads"])
        self.corr: dict[str, float] = {}

    def _at(self, model: str, quant: str, build: str, t: int, test: str) -> float:
        lo, hi = self.pilot_threads[0], self.pilot_threads[-1]

        def key(th: int) -> tuple:
            return (model, quant, build, th, test)

        if key(t) in self.tps:
            return self.tps[key(t)]
        if key(lo) not in self.tps or key(hi) not in self.tps:
            raise KeyError(
                f"the pilot has no {test} for {model}_{quant}_{build} at t={lo} and {hi}"
            )
        return _loglog(t, self.tps[key(lo)], self.tps[key(hi)], lo, hi)

    def _quant_ref(self, quant: str, build: str, t: int, base_test: str) -> str:
        if quant in self.quants:
            return quant
        return min(self.quants, key=lambda q: self._at(self.ref_model, q, build, t, base_test))

    def speed(self, model: str, quant: str, build: str, t: int, test: str, corrected: bool = True):
        te = sweep.parse_test(test)
        base_test = (
            "pp512" if te.kind == "pp" else f"tg{te.tokens}" + (f"d{te.depth}" if te.depth else "")
        )
        # the pilot runs tg128; other decode lengths are not in the sweep
        qr = self._quant_ref(quant, build, t, base_test)
        ref = self._at(self.ref_model, qr, build, t, base_test)
        if te.kind == "pp":
            scale = self.sizes[(self.ref_model, qr)]["N_blk"] / self.sizes[(model, qr)]["N_blk"]
            corr = self.corr.get(build, 1.0) if (corrected and te.tokens >= HIGH_PROMPT) else 1.0
            return ref * scale * corr
        scale = self.sizes[(self.ref_model, qr)]["W_all"] / self.sizes[(model, qr)]["W_all"]
        return ref * scale


def estimate_full_sweep(records: Sequence[dict], cfg: dict, sizes: dict) -> dict:
    """Estimated wall time of the `full` sweep from the pilot records.

    `sizes[(model, quant)]` = {"file_bytes", "N_blk", "W_all"} from results/models/.
    """
    recs = latest_records(records)
    ref = _Reference(recs, cfg, sizes)
    notes: list[str] = []

    # 1. long-prompt correction from the pilot's extra point, per build
    for p in cfg["pilot"].get("extra_points", []):
        te = sweep.parse_test(p["test"])
        if te.kind != "pp" or te.tokens < HIGH_PROMPT:
            continue
        for build in sweep.BUILDS:
            cid = sweep.config_id(p["model"], p["quant"], build, p["threads"], p["test"])
            if cid not in recs:
                continue
            guess = ref.speed(p["model"], p["quant"], build, p["threads"], p["test"], False)
            ref.corr[build] = min(1.0, recs[cid]["summary"]["median"] / guess)
            notes.append(
                f"{build}: long-prompt correction {ref.corr[build]:.3f} "
                f"(measured {recs[cid]['summary']['median']:.2f} tok/s at {cid}, "
                f"scaling alone predicts {guess:.2f})"
            )
    if not ref.corr:
        notes.append("no long-prompt point in the pilot: prompt-length correction is 1.0")

    # 2. per-call overhead per GiB of model file, per build
    per_gib: dict[str, list[float]] = defaultdict(list)
    for r in recs.values():
        te = sweep.parse_test(r["test"])
        tps = r["summary"]["median"]
        prefill = None
        if te.kind == "tg" and te.depth:
            key = (r["model_alias"], r["quant"], r["build"], r["threads"], "pp512")
            prefill = ref.tps.get(key)
        work = _call_seconds(te, r["repetitions"], tps, prefill)
        overhead = max(0.0, r["wall_seconds"] - work)
        per_gib[r["build"]].append(overhead / (r["model"]["file_bytes"] / GIB))
    typical = {b: sorted(v)[len(v) // 2] for b, v in per_gib.items()}
    worst = {b: max(v) for b, v in per_gib.items()}

    # 3. every point of the full sweep
    total = total_hi = 0.0
    by_group: dict[str, float] = defaultdict(float)
    for pair in sweep.pairs(cfg, "full"):
        reps = sweep.repetitions(cfg, pair)
        te = sweep.parse_test(pair.test)
        for build in sweep.BUILDS:
            tps = ref.speed(pair.model, pair.quant, build, pair.threads, pair.test)
            prefill = None
            if te.kind == "tg" and te.depth:
                prefill = ref.speed(pair.model, pair.quant, build, pair.threads, "pp512")
            work = _call_seconds(te, reps, tps, prefill)
            gib = sizes[(pair.model, pair.quant)]["file_bytes"] / GIB
            seconds = work + typical[build] * gib
            total += seconds
            total_hi += work + worst[build] * gib
            by_group[f"{pair.model}_{pair.quant}_{te.phase}"] += seconds

    firsts = [r for r in records if r["attempt"] == 1]
    noisy_fraction = sum(1 for r in firsts if r["noisy"]) / len(firsts) if firsts else 0.0
    est = total * (1 + noisy_fraction)
    est_hi = total_hi * (1 + noisy_fraction)
    return {
        "method": __doc__,
        "pilot_wall_seconds": sum(r["wall_seconds"] for r in records),
        "pilot_calls": len(records),
        "overhead_seconds_per_gib": {"typical_median": typical, "worst": worst},
        "long_prompt_correction": ref.corr,
        "noisy_fraction_of_pilot": noisy_fraction,
        "full_sweep_points": 2 * len(sweep.pairs(cfg, "full")),
        "estimate_seconds": est,
        "estimate_hours": est / 3600,
        "upper_bound_hours": est_hi / 3600,
        "hours_by_group": {k: v * (1 + noisy_fraction) / 3600 for k, v in sorted(by_group.items())},
        "notes": notes,
    }


def render_markdown(session_id: str, noise: list[dict], est: dict) -> str:
    lines = [
        f"# Pilot summary, session {session_id}",
        "",
        "Written by `bench/run_sweep.py` after the pilot. Not a measurement of the sweep itself.",
        "",
        "## Repeat noise (IQR / median of tokens/s over the repetitions)",
        "",
        "| config_id | attempt | reps | median tok/s | IQR tok/s | IQR/median | noisy | wall s |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in noise:
        lines.append(
            f"| {r['config_id']} | {r['attempt']} | {r['repetitions']} | {r['median_tps']:.2f}"
            f" | {r['iqr_tps']:.2f} | {100 * r['iqr_over_median']:.2f} % | "
            f"{'yes' if r['noisy'] else 'no'} | {r['wall_seconds']:.0f} |"
        )
    lines += [
        "",
        "## Estimated wall time of the full sweep",
        "",
        f"- points: {est['full_sweep_points']} (calls of llama-bench, both builds)",
        (
            f"- estimate: **{est['estimate_hours']:.1f} h** (upper bound "
            f"{est['upper_bound_hours']:.1f} h, with the largest per-GiB overhead seen in the pilot)"
        ),
        (
            f"- the pilot itself took {est['pilot_wall_seconds'] / 60:.0f} min for "
            f"{est['pilot_calls']} calls"
        ),
        (
            f"- noisy points in the pilot: {100 * est['noisy_fraction_of_pilot']:.0f} % "
            "(the same share is added for re-runs)"
        ),
        "",
    ]
    lines += [f"- {n}" for n in est["notes"]]
    lines += ["", "### By model, format and phase (hours, both builds)", ""]
    lines += [f"- {k}: {v:.2f}" for k, v in est["hours_by_group"].items()]
    lines += ["", "### Method", "", "```", est["method"].strip(), "```", ""]
    return "\n".join(lines)
