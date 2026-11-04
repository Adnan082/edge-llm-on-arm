"""Day 8 investigation: one targeted check per KleidiAI surprise of ADR-025.

    python -m edge_llm.day8 [--session <id>]            (make day8-analyse; the VM part is `make day8`)

These checks are labelled "Day 8 investigation". They never enter the v1 comparison or the
headline figure: they read other files, write `results/processed/day8_*.csv`, and `analyse.py`
never sees them. No hardware calls here, so all of it runs in CI.

CHECK A - does the Q6_K output layer explain Q4_K_M's large KleidiAI decode gain? (surprise 2)
    Hypothesis: the Q4_0 and Q4_K_M files keep `output.weight` (121.7 MiB) in Q6_K; KleidiAI
    converts it to 8-bit at load and its GEMV decodes faster than ggml's Q6_K GEMV, although it
    reads more bytes. Test: the same Q4_0 file with only the output layer changed to Q8_0
    (`small_Q4_0outq8`) or Q4_0 (`small_Q4_0outq4`), tg128 at t = 1 and 8, both builds, next to
    the unchanged Q4_0 file measured again in the same session.

    PREDICTION, written before any Check A run (the rule below is the one the code applies):
        If the hypothesis holds, the KleidiAI decode speed-up (kleidiai / baseline median) is
        clearly smaller for `Q4_0outq8` and for `Q4_0outq4` than for `Q4_0`, at the thread count
        considered. "Clearly smaller" = the variant's conservative upper bound (`speedup_hi`,
        kleidiai Q3 / baseline Q1) is below the reference's conservative lower bound
        (`speedup_lo`), the same range convention as `kleidiai.csv`. Overlapping ranges mean the
        output layer does not explain the gain (hypothesis not supported); a clearly larger
        speed-up means the opposite of the prediction. Nothing else is read into the numbers.

CHECK B - is the prefill difference a fixed cost per call? (surprises 1 and 3)
    From `results/processed/kleidiai.csv` only. Per format and thread count, the time to process
    a prompt of P tokens is P / (tokens per second); `delta_t = t_baseline - t_kleidiai`
    (positive = KleidiAI faster). A fixed per-call or per-chunk cost (e.g. activation packing)
    gives a `delta_t` that does not grow with P (growth 2048/128 close to 1); a per-token kernel
    difference gives `delta_t` proportional to P (growth close to 16). Numbers only.

CHECK C - perf profile of pp128 at t = 1: see `bench/day8.py`; `perf_summary` reads its records.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

from edge_llm.analyse import apply_rerun_rule, load_bench_session, speedup_range
from edge_llm.stats import summarise

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = Path("results/processed")
BENCH_DIR = Path("results/raw/bench")
PERF_DIR = Path("results/raw/perf")

# --- Check A: the variants --------------------------------------------------------------------

REFERENCE = "Q4_0"
# quant name in config_id -> the --output-tensor-type that makes it, and the tensor type it must
# end up with. The reference keeps the default mix (Q6_K output layer, ADR-010).
VARIANTS: dict[str, dict[str, str | None]] = {
    "Q4_0": {"quantize_arg": None, "output_type": "Q6_K"},
    "Q4_0outq8": {"quantize_arg": "q8_0", "output_type": "Q8_0"},
    "Q4_0outq4": {"quantize_arg": "q4_0", "output_type": "Q4_0"},
}
PREDICTION_A = (
    "If the Q6_K output layer explains Q4_K_M's KleidiAI decode gain, the KleidiAI decode speed-up "
    "(tg128, kleidiai / baseline median) is clearly smaller for Q4_0outq8 and Q4_0outq4 than for "
    "Q4_0 (variant speedup_hi < Q4_0 speedup_lo), at the thread count considered."
)
CHECK_A_THREADS = (1, 8)
CHECK_A_TEST = "tg128"
CHECK_A_ALIAS = "small"


def check_a_pair_specs() -> list[tuple[str, int]]:
    """(variant, threads) in running order.

    Threads are the outer loop so that, with the sweep's rule (the build that runs first alternates
    with the pair index), each thread count sees both build orders, and so does each variant.
    """
    return [(v, t) for t in CHECK_A_THREADS for v in VARIANTS]


def check_variant_table(variant: dict, reference: dict, output_type: str) -> list[str]:
    """Problems with a variant's tensor table (empty list = fine).

    `output.weight` must have `output_type`; every other tensor must be present in both files with
    the same type and shape as in the reference. Compared by name, so a changed token embedding or
    a changed block tensor is caught.
    """
    problems: list[str] = []
    v = {t["name"]: t for t in variant["tensors"]}
    r = {t["name"]: t for t in reference["tensors"]}
    if "output.weight" not in v:
        problems.append("output.weight is missing (tied embeddings?)")
    elif v["output.weight"]["type"] != output_type:
        problems.append(f"output.weight is {v['output.weight']['type']}, wanted {output_type}")
    for name in sorted(set(v) ^ set(r)):
        problems.append(f"{name} is only in the {'variant' if name in v else 'reference'}")
    for name in sorted(set(v) & set(r) - {"output.weight"}):
        if (v[name]["type"], v[name]["shape"]) != (r[name]["type"], r[name]["shape"]):
            problems.append(
                f"{name}: {v[name]['type']} {v[name]['shape']} differs from the reference "
                f"{r[name]['type']} {r[name]['shape']}"
            )
    if (
        "output.weight" in v
        and "output.weight" in r
        and v["output.weight"]["shape"] != r["output.weight"]["shape"]
    ):
        problems.append("output.weight changed shape")
    return problems


def compare_to_reference(row: dict, ref: dict) -> str:
    """'smaller' / 'larger' / 'overlap' by the conservative speed-up ranges (see module docstring)."""
    if row["speedup_hi"] < ref["speedup_lo"]:
        return "smaller"
    if row["speedup_lo"] > ref["speedup_hi"]:
        return "larger"
    return "overlap"


CHECK_A_COLUMNS = [
    "variant", "threads", "output_type", "file_bytes",
    "baseline_median", "baseline_iqr_over_median", "baseline_still_noisy",
    "kleidiai_median", "kleidiai_iqr_over_median", "kleidiai_still_noisy",
    "speedup", "speedup_lo", "speedup_hi",
    "vs_reference", "prediction_holds_at_t", "sweep_speedup",
]  # fmt: skip


def _used_summary(attempts: dict) -> tuple[dict, bool, int]:
    """Summary of the attempt the re-run rule picks, whether it is still noisy, bytes of the file."""
    samples = {a: rec.llama_bench[0]["samples_ts"] for a, (rec, _p) in attempts.items()}
    used, still_noisy = apply_rerun_rule(samples)
    return summarise(samples[used]), still_noisy, attempts[used][0].model["file_bytes"]


def sweep_speedup(processed: Path, quant: str, threads: int) -> float | None:
    """The full sweep's tg128 speed-up for the same file, if kleidiai.csv has it (context only)."""
    path = processed / "kleidiai.csv"
    if not path.exists():
        return None
    for row in csv.DictReader(path.open()):
        if row["pair_id"] == f"{CHECK_A_ALIAS}_{quant}_t{threads}_{CHECK_A_TEST}":
            return float(row["speedup"])
    return None


def check_a_rows(session_dir: Path, session: str, processed: Path | None = None) -> list[dict]:
    """One row per (variant, threads) from a session folder of Day 8 bench records."""
    processed = processed if processed is not None else REPO_ROOT / PROCESSED_DIR
    found = load_bench_session(session_dir, session)
    per: dict[tuple[str, int], dict[str, tuple[dict, bool, int]]] = defaultdict(dict)
    for attempts in found.values():
        rec = attempts[1][0]
        if rec.model_alias != CHECK_A_ALIAS or rec.test != CHECK_A_TEST:
            continue
        if rec.quant not in VARIANTS:
            continue
        per[(rec.quant, rec.threads)][rec.build] = _used_summary(attempts)

    rows: list[dict] = []
    for (variant, threads), builds in sorted(per.items()):
        if set(builds) != {"baseline", "kleidiai"}:
            raise ValueError(f"{variant} t{threads}: needs both builds, has {sorted(builds)}")
        (b, b_noisy, b_bytes), (k, k_noisy, _k_bytes) = builds["baseline"], builds["kleidiai"]
        sp, lo, hi = speedup_range((b["q1"], b["median"], b["q3"]), (k["q1"], k["median"], k["q3"]))
        rows.append(
            {
                "variant": variant,
                "threads": threads,
                "output_type": VARIANTS[variant]["output_type"],
                "file_bytes": b_bytes,
                "baseline_median": b["median"],
                "baseline_iqr_over_median": b["iqr_over_median"],
                "baseline_still_noisy": b_noisy,
                "kleidiai_median": k["median"],
                "kleidiai_iqr_over_median": k["iqr_over_median"],
                "kleidiai_still_noisy": k_noisy,
                "speedup": sp,
                "speedup_lo": lo,
                "speedup_hi": hi,
                "vs_reference": "",
                "prediction_holds_at_t": "",
                "sweep_speedup": sweep_speedup(processed, variant, threads),
            }
        )

    for t in sorted({r["threads"] for r in rows}):
        at_t = [r for r in rows if r["threads"] == t]
        ref = next((r for r in at_t if r["variant"] == REFERENCE), None)
        if ref is None:
            raise ValueError(f"t{t}: the reference {REFERENCE} was not measured in this session")
        others = [r for r in at_t if r["variant"] != REFERENCE]
        for r in at_t:
            r["vs_reference"] = "reference" if r is ref else compare_to_reference(r, ref)
        holds = bool(others) and all(r["vs_reference"] == "smaller" for r in others)
        for r in at_t:
            r["prediction_holds_at_t"] = holds
    return rows


# --- Check B: delta-t per prompt ----------------------------------------------------------------

PREFILL_LENGTHS = (128, 512, 2048)
CHECK_B_QUANTS = ("Q4_0", "Q8_0")

CHECK_B_COLUMNS = [
    "quant", "threads", "prompt_tokens", "baseline_tps", "kleidiai_tps", "speedup",
    "t_baseline_s", "t_kleidiai_s", "delta_t_s", "delta_t_lo_s", "delta_t_hi_s",
    "delta_ms_per_token",
]  # fmt: skip
CHECK_B_FIT_COLUMNS = [
    "quant", "threads", "fixed_s", "per_token_ms", "growth_2048_over_128",
    "per_token_ms_max_over_min", "sign_changes",
]  # fmt: skip


def delta_t_row(quant: str, threads: int, prompt_tokens: int, kl: dict) -> dict:
    """Time per prompt in both builds and their difference, from one kleidiai.csv row.

    Time = P / tokens-per-second (the median of the rates maps to the median time). The range
    pairs the baseline's fastest with KleidiAI's slowest repetition-quartile and vice versa:
    lo = P/baseline_q3 - P/kleidiai_q1, hi = P/baseline_q1 - P/kleidiai_q3 (the speed-up range's
    convention).
    """
    p = prompt_tokens
    bm, km = float(kl["baseline_median"]), float(kl["kleidiai_median"])
    tb, tk = p / bm, p / km
    return {
        "quant": quant,
        "threads": threads,
        "prompt_tokens": p,
        "baseline_tps": bm,
        "kleidiai_tps": km,
        "speedup": float(kl["speedup"]),
        "t_baseline_s": tb,
        "t_kleidiai_s": tk,
        "delta_t_s": tb - tk,
        "delta_t_lo_s": p / float(kl["baseline_q3"]) - p / float(kl["kleidiai_q1"]),
        "delta_t_hi_s": p / float(kl["baseline_q1"]) - p / float(kl["kleidiai_q3"]),
        "delta_ms_per_token": 1000 * (tb - tk) / p,
    }


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Least squares y = a + b x: (a, b)."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / sxx
    return my - b * mx, b


def fit_row(rows: list[dict]) -> dict:
    """Fixed + per-token split of delta_t for one (format, threads), over the prompt lengths."""
    rows = sorted(rows, key=lambda r: r["prompt_tokens"])
    ps = [r["prompt_tokens"] for r in rows]
    dts = [r["delta_t_s"] for r in rows]
    a, b = linear_fit([float(p) for p in ps], dts)
    per_tok = [abs(d) / p for d, p in zip(dts, ps, strict=True)]
    same_sign = all(d > 0 for d in dts) or all(d < 0 for d in dts)
    nan = float("nan")
    return {
        "quant": rows[0]["quant"],
        "threads": rows[0]["threads"],
        "fixed_s": a,
        "per_token_ms": 1000 * b,
        "growth_2048_over_128": dts[-1] / dts[0] if same_sign else nan,
        "per_token_ms_max_over_min": max(per_tok) / min(per_tok) if same_sign else nan,
        "sign_changes": not same_sign,
    }


def check_b(kleidiai_csv: Path) -> tuple[list[dict], list[dict]]:
    """(per-prompt rows, per-(format, threads) fit rows) for Q4_0 and Q8_0 prefill."""
    rows: list[dict] = []
    for kl in csv.DictReader(kleidiai_csv.open()):
        if kl["quant"] not in CHECK_B_QUANTS or not kl["test"].startswith("pp"):
            continue
        p = int(kl["test"][2:])
        if p not in PREFILL_LENGTHS:
            continue
        rows.append(delta_t_row(kl["quant"], int(kl["threads"]), p, kl))
    rows.sort(key=lambda r: (r["quant"], r["threads"], r["prompt_tokens"]))
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["quant"], r["threads"])].append(r)
    for key, g in groups.items():
        if sorted(r["prompt_tokens"] for r in g) != list(PREFILL_LENGTHS):
            raise ValueError(f"{key}: expected prompt lengths {PREFILL_LENGTHS}")
    return rows, [fit_row(g) for _k, g in sorted(groups.items())]


# --- Check C: perf report ---------------------------------------------------------------------

NEWLINE = chr(10)
_PERF_ROW = re.compile(r"^\s*(\d+(?:\.\d+)?)%\s+(\S+)\s+\[(.)\]\s+(.+?)\s*$")
_PERF_SAMPLES = re.compile(
    r"^#\s*Samples:\s*([\d.]+[KMG]?)\s+of event\s+'?([^'\n]+?)'?\s*$", re.MULTILINE
)


def parse_perf_report(text: str, top: int = 20) -> list[dict]:
    """The first `top` rows of `perf report --stdio --no-children --sort dso,symbol`."""
    rows = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = _PERF_ROW.match(line)
        if m:
            rows.append(
                {
                    "percent": float(m.group(1)),
                    "dso": m.group(2),
                    "kind": m.group(3),  # '.' user space, 'k' kernel
                    "symbol": m.group(4),
                }
            )
        if len(rows) == top:
            break
    return rows


def trim_perf_report(text: str, top: int = 20) -> str:
    """The report's header comments and its first `top` rows, as perf printed them."""
    kept, rows = [], 0
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            kept.append(line)
        elif _PERF_ROW.match(line):
            kept.append(line)
            rows += 1
            if rows == top:
                break
    return NEWLINE.join(kept) + NEWLINE


def perf_samples(text: str) -> tuple[str | None, str | None]:
    """(sample count text, event) from the report's '# Samples: ... of event ...' header."""
    m = _PERF_SAMPLES.search(text)
    return (m.group(1), m.group(2)) if m else (None, None)


REQUIRED_PERF_KEYS = {
    "kind", "session_id", "config_id", "build", "quant", "threads", "test", "event",
    "perf_version", "command", "samples", "top", "use_for_analysis", "caveat", "captured_utc",
}  # fmt: skip


def validate_perf_record(rec: dict) -> None:
    """Raise ValueError if a perf record is malformed (these records have no schema class)."""
    if rec.get("kind") == "perf_unavailable":
        for key in ("session_id", "reason", "captured_utc"):
            if not rec.get(key):
                raise ValueError(f"perf_unavailable record: {key} missing")
        return
    if rec.get("kind") != "perf":
        raise ValueError(f"unknown perf record kind {rec.get('kind')!r}")
    missing = REQUIRED_PERF_KEYS - rec.keys()
    if missing:
        raise ValueError(f"perf record: missing {sorted(missing)}")
    if rec["use_for_analysis"] is not False:
        raise ValueError("perf record: its timing must never be used for analysis")
    if not rec["top"]:
        raise ValueError("perf record: empty profile")
    total = sum(r["percent"] for r in rec["top"])
    if not 0 < total <= 100.0 + 1e-6:
        raise ValueError(f"perf record: top rows add up to {total}%")


def perf_summary(folder: Path, names: int = 3) -> list[str]:
    """One line per perf record: its hottest symbols. Says so if perf was not available."""
    lines = []
    for path in sorted(folder.glob("*.json")):
        rec = json.loads(path.read_text())
        validate_perf_record(rec)
        if rec["kind"] == "perf_unavailable":
            lines.append(f"perf not available: {rec['reason']}")
            continue
        hot = ", ".join(f"{r['symbol']} {r['percent']:.1f}%" for r in rec["top"][:names])
        lines.append(f"{rec['config_id']}: {hot}")
    return lines


# --- output and main --------------------------------------------------------------------------


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _f(x: float, digits: int = 3) -> str:
    return "n/a" if isinstance(x, float) and math.isnan(x) else f"{x:.{digits}f}"


def render_check_b(rows: list[dict], fits: list[dict]) -> list[str]:
    out = ["CHECK B - prefill time saved by KleidiAI per prompt (delta_t = baseline - kleidiai)"]
    out.append(
        "quant   t    P   speedup  t_base[s]  t_kl[s]   delta_t[s]  [lo, hi]            ms/token"
    )
    for r in rows:
        out.append(
            f"{r['quant']:<6} {r['threads']:>2} {r['prompt_tokens']:>5}  {r['speedup']:.3f}"
            f"  {r['t_baseline_s']:>9.4f} {r['t_kleidiai_s']:>8.4f}  {r['delta_t_s']:>10.4f}"
            f"  [{r['delta_t_lo_s']:.4f}, {r['delta_t_hi_s']:.4f}]  {r['delta_ms_per_token']:>8.4f}"
        )
    out.append("")
    out.append(
        "fit delta_t = fixed + per_token * P; growth 2048/128: 1 = fixed cost, 16 = per token"
    )
    out.append("quant   t   fixed[s]  per_token[ms]  growth  per-token max/min  sign changes")
    for f in fits:
        out.append(
            f"{f['quant']:<6} {f['threads']:>2}  {f['fixed_s']:>8.4f}  {f['per_token_ms']:>12.4f}"
            f"  {_f(f['growth_2048_over_128'], 2):>6}  {_f(f['per_token_ms_max_over_min'], 2):>16}"
            f"  {f['sign_changes']}"
        )
    return out


def render_check_a(rows: list[dict]) -> list[str]:
    out = ["CHECK A - KleidiAI decode speed-up (tg128) with the output layer changed"]
    out.append(
        "variant     t  out    base tok/s  kl tok/s  speedup  [lo, hi]         vs Q4_0   "
        "sweep  noisy"
    )
    for r in rows:
        noisy = "yes" if r["baseline_still_noisy"] or r["kleidiai_still_noisy"] else ""
        sw = "" if r["sweep_speedup"] is None else f"{r['sweep_speedup']:.3f}"
        out.append(
            f"{r['variant']:<10} {r['threads']:>2}  {r['output_type']:<5}"
            f"  {r['baseline_median']:>9.2f}  {r['kleidiai_median']:>8.2f}  {r['speedup']:.3f}"
            f"  [{r['speedup_lo']:.3f}, {r['speedup_hi']:.3f}]  {r['vs_reference']:<9} {sw:>6}  {noisy}"
        )
    for t in sorted({r["threads"] for r in rows}):
        holds = next(r["prediction_holds_at_t"] for r in rows if r["threads"] == t)
        out.append(f"t={t}: prediction (both variants clearly smaller than Q4_0) holds: {holds}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", help="the VM session of the Day 8 checks A and C")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root: Path = args.root
    processed = root / PROCESSED_DIR

    rows, fits = check_b(processed / "kleidiai.csv")
    write_csv(processed / "day8_check_b.csv", CHECK_B_COLUMNS, rows)
    write_csv(processed / "day8_check_b_fit.csv", CHECK_B_FIT_COLUMNS, fits)
    print("\n".join(render_check_b(rows, fits)))

    if args.session:
        a_dir = root / BENCH_DIR / args.session
        if any(a_dir.glob("*Q4_0outq*.json")):
            a_rows = check_a_rows(a_dir, args.session, processed)
            write_csv(processed / "day8_check_a.csv", CHECK_A_COLUMNS, a_rows)
            print("\n" + "\n".join(render_check_a(a_rows)))
        else:
            print(f"\nCHECK A: no Day 8 records in {a_dir} (run `make day8` on the VM)")
        p_dir = root / PERF_DIR / args.session
        if p_dir.exists():
            print("\nCHECK C:\n" + "\n".join(perf_summary(p_dir)))
        else:
            print(f"\nCHECK C: no perf records in {p_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
