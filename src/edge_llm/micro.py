"""RQ4 int8 dot-product microbenchmark: what was run, how its loops are checked, how its numbers
are derived (CLAUDE.md §4 RQ4, §5, §9).

micro/dot_int8.cpp times a decode-shaped matrix-vector product (W: M rows x K int8, x: K int8) in
five instruction variants with two working sets, on one core. micro/run_micro.py saves the raw
record (results/raw/micro/<session_id>.json). This module holds everything that needs no hardware,
so CI tests it:

  * the variant table and the kernel shape (one place for the constants);
  * the disassembly check of each hot loop (found by conditional backward branches only, like
    peak.py): the expected instruction is in the loop, and scalar has no SIMD multiply at all;
  * the arithmetic: GMAC/s, weight GB/s, ratio to scalar, fraction of the matching peak C(1) (L1)
    and of the measured bandwidth B(1) and B1(1) (DRAM);
  * `python -m edge_llm.micro`: raw record -> results/processed/micro.csv (what plots.py reads).

One multiply-accumulate (MAC) = 2 operations, as everywhere (§8).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path

from edge_llm import peak

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = Path("results/raw/micro")
PROCESSED_DIR = Path("results/processed")

# --- what is measured -----------------------------------------------------------------------

K = 4096  # a row's int32 sum cannot overflow: |sum| <= 4096 * 128 * 128 = 2^26
WORKING_SETS = ("L1", "DRAM")
ROWS = {"L1": 4, "DRAM": 262_144}  # W = 16 KiB, and W = 1 GiB
L1D_BYTES = 64 * 1024  # Neoverse V2 L1d per core
L3_BYTES = 80 * 2**20  # 80 MiB, shared (CLAUDE.md §11)
MIN_REPS = 30
MIN_REP_SECONDS = 0.010  # every timed repetition lasts at least this long (CLAUDE.md brief)

FAMILIES = ("scalar", "autovec", "sdot", "smmla", "sve")
FAMILY_LABEL = {
    "scalar": "scalar (no auto-vec)",
    "autovec": "auto-vectorised",
    "sdot": "NEON SDOT",
    "smmla": "i8mm SMMLA (2 rows × 2 vectors)",
    "sve": "SVE SDOT",
}
# name -> (family, accumulators). The accumulator count is 0 where it does not apply. Both 4 and 8
# are run for every SIMD family and the best is reported (the ADR-022 rule, as for the peak chains).
VARIANTS: dict[str, tuple[str, int]] = {
    "scalar": ("scalar", 0),
    "autovec": ("autovec", 0),
    "sdot_a4": ("sdot", 4),
    "sdot_a8": ("sdot", 8),
    "smmla_a4": ("smmla", 4),
    "smmla_a8": ("smmla", 8),
    "sve_a4": ("sve", 4),
    "sve_a8": ("sve", 8),
}
# SMMLA multiplies 2 weight rows by 2 activation vectors at once, so it does two MACs per weight
# byte; every other variant does one (one activation vector).
MACS_PER_WEIGHT_BYTE = {"scalar": 1, "autovec": 1, "sdot": 1, "smmla": 2, "sve": 1}
# The peak (record results/raw/peak/...) each family is compared with in the L1 case. SVE SDOT is
# the same operation as NEON SDOT, so it has the same ceiling; the plain-C variants have no matching
# peak (what GCC chose for auto-vec is a finding, not an assumption).
PEAK_CLASS = {"sdot": "sdot", "sve": "sdot", "smmla": "smmla"}


def function_name(variant: str) -> str:
    """The symbol of a variant's kernel in the binary."""
    return f"dot_{variant}"


def macs_per_call(variant: str, working_set: str, k: int = K) -> int:
    """Useful multiply-accumulates in one call (SMMLA: both activation vectors count)."""
    return ROWS[working_set] * k * MACS_PER_WEIGHT_BYTE[VARIANTS[variant][0]]


# --- disassembly check -----------------------------------------------------------------------

# Any SIMD multiply, vector or SVE form. Scalar multiplies (`mul w1, w2, w3`, `madd`, `smaddl`) use
# w/x registers and do not match.
SIMD_MULTIPLY_RE = re.compile(
    r"^(sdot|udot|usdot|sudot|smmla|ummla|usmmla|smlal2?|umlal2?|smull2?|umull2?|smlalb|smlalt"
    r"|smullb|smullt|mla|mls|mul)\s+[vz]\d"
)
# What must be in the hot loop of each SIMD family (regex on "mnemonic operands"), once per
# accumulator.
EXPECTED_IN_LOOP: dict[str, tuple[str, str]] = {
    "sdot": (r"^sdot\s+v\d+\.4s, v\d+\.16b, v\d+\.16b", "sdot v-form"),
    "smmla": (r"^smmla\s+v\d+\.4s, v\d+\.16b, v\d+\.16b", "smmla"),
    "sve": (r"^sdot\s+z\d+\.s, z\d+\.b, z\d+\.b", "sdot z-form"),
}


def hot_loop_for(variant: str, insns: Sequence[tuple[int, str]]) -> list[str]:
    """The hot loop of a variant's kernel: the innermost loop (shortest conditional backward
    branch span, peak.hot_loop) holding the expected instruction.

    Scalar has no expected instruction, so its hot loop is the innermost loop; auto-vec prefers a
    loop holding any SIMD multiply (its vector main loop rather than the scalar remainder loop).
    """
    family = VARIANTS[variant][0]
    if family in EXPECTED_IN_LOOP:
        contains = EXPECTED_IN_LOOP[family][0]
    elif family == "autovec":
        contains = SIMD_MULTIPLY_RE.pattern
    else:
        contains = None
    return peak.hot_loop(insns, contains=contains)


def _mnemonic(text: str) -> str:
    return text.split(" ", 1)[0]


def check_loop(variant: str, loop: Sequence[str], function_insns: Sequence[str] = ()) -> dict:
    """Check a kernel's hot loop against what the variant must contain.

    SIMD families: exactly one expected instruction per accumulator in the loop. Scalar: the loop
    exists and neither it nor anything else in the function is a SIMD multiply. Auto-vec: nothing
    is asserted (`asserted: false`); the loop's instructions are recorded, because which ones GCC
    chose (SDOT or not) is a finding. `function_insns` is the whole function, for the scalar test.
    """
    family, acc = VARIANTS[variant]
    mnemonics = Counter(_mnemonic(t) for t in loop)
    simd_in_loop = sorted({_mnemonic(t) for t in loop if SIMD_MULTIPLY_RE.match(t)})
    out: dict = {
        "variant": variant,
        "family": family,
        "function": function_name(variant),
        "asserted": family != "autovec",
        "loop_instructions": len(loop),
        "mnemonics": dict(sorted(mnemonics.items())),
        "simd_multiply_in_loop": simd_in_loop,
        "loop": list(loop),
    }
    if family in EXPECTED_IN_LOOP:
        pattern, label = EXPECTED_IN_LOOP[family]
        found = sum(1 for t in loop if re.match(pattern, t))
        out.update(expected=label, expected_count=acc, found=found)
        out["ok"] = bool(loop) and found == acc
    elif family == "scalar":
        in_function = sorted({_mnemonic(t) for t in function_insns if SIMD_MULTIPLY_RE.match(t)})
        out.update(expected="no SIMD multiply", simd_multiply_in_function=in_function)
        out["ok"] = bool(loop) and not simd_in_loop and not in_function
    else:  # autovec: record, do not assert
        out.update(
            expected="none (recorded)",
            uses_sdot=any(m.startswith("sdot") for m in simd_in_loop),
        )
        out["ok"] = bool(loop)
    return out


# --- the arithmetic --------------------------------------------------------------------------

SLOW_THRESHOLD = 0.75  # a repetition is "slow" if its rate is under this share of the p90 rate


def percentile90(samples: Sequence[float]) -> float:
    """90th percentile, linear interpolation (as roofline.py and stats.py)."""
    return statistics.quantiles(samples, n=10, method="inclusive")[8]


def gmacs(macs: float, ns: float) -> float:
    """MAC per ns is GMAC/s."""
    return macs / ns


def weight_gbs(weight_bytes: float, ns: float) -> float:
    """Bytes per ns is GB/s (10^9 B/s). Equals GMAC/s divided by MACs per weight byte."""
    return weight_bytes / ns


def slow_share(samples_ns: Sequence[float], threshold: float = SLOW_THRESHOLD) -> float:
    """Share of repetitions whose rate is under `threshold` x the p90 rate.

    The peak runs were two-state (ADR-023: a repetition at 4 instructions per cycle or at exactly
    half), so the share of slow repetitions says how throttled the run was. Rates, not times:
    the reference is the 90th percentile of 1/ns, the unthrottled state.
    """
    rates = [1.0 / s for s in samples_ns]
    ref = percentile90(rates)
    return sum(1 for r in rates if r < threshold * ref) / len(rates)


def best_variants(points: Iterable, ok_variants: set[str]) -> dict[tuple[str, str], str]:
    """{(family, working_set): variant} with the lowest median time among the variants whose
    disassembly check passed (the ADR-022 rule); a tie goes to the smaller accumulator count."""
    best: dict[tuple[str, str], tuple[float, int, str]] = {}
    for p in points:
        if p.variant not in ok_variants:
            continue
        key = (p.family, p.working_set)
        cand = (p.median_ns, p.accumulators, p.variant)
        if key not in best or cand < best[key]:
            best[key] = cand
    return {key: v[2] for key, v in best.items()}


MICRO_COLUMNS = [
    "variant", "family", "accumulators", "working_set", "disasm_ok", "is_best",
    "rows", "k", "weight_bytes", "macs_per_call", "macs_per_weight_byte", "calls_per_rep", "reps",
    "median_ns", "q1_ns", "q3_ns", "iqr_over_median", "slow_share",
    "gmacs", "gmacs_lo", "gmacs_hi", "gmacs_p90", "weight_gbs",
    "speedup_vs_scalar", "speedup_vs_scalar_per_weight_byte",
    "peak_class", "peak_gmacs", "fraction_of_peak", "fraction_of_peak_p90",
    "ref_B_GBps", "ref_B1_GBps", "fraction_of_B", "fraction_of_B1",
    "ref_C_sdot_GMACs", "ref_C_smmla_GMACs",
    "bandwidth_record", "peak_record", "source_file",
]  # fmt: skip


def derive_rows(record, source_file: str | None = None) -> list[dict]:
    """One row per (variant, working set) of a MicroRecord: the output table of the brief.

    gmacs is the median rate in useful MACs (SMMLA: both activation vectors); weight_gbs is weight
    bytes per second, which is the like-for-like rate across variants because SMMLA does twice the
    MACs per weight byte. `speedup_vs_scalar` is the ratio of gmacs, and
    `speedup_vs_scalar_per_weight_byte` the ratio of weight_gbs, both against scalar in the same
    working set. L1 rows get the fraction of the matching peak C(1) (median rate, and the p90 rate
    that C(1) itself is built from, ADR-023); DRAM rows get the fraction of B(1) and B1(1).
    """
    ref = record.references
    b_best = ref["bandwidth_record"]["B_best_Bps"]
    b_one = ref["bandwidth_record"]["B_one_stream_Bps"]
    c_ops = {
        "sdot": ref["peak_record"]["C_sdot_ops_per_s"],
        "smmla": ref["peak_record"]["C_smmla_ops_per_s"],
    }
    ok_variants = {v for v, d in record.disasm.items() if d.get("ok") is True}
    best = best_variants(record.points, ok_variants)
    scalar = {p.working_set: p for p in record.points if p.variant == "scalar"}
    source = source_file or f"results/raw/micro/{record.session_id}.json"

    rows = []
    for p in sorted(
        record.points, key=lambda q: (q.working_set, FAMILIES.index(q.family), q.accumulators)
    ):
        gm = gmacs(p.macs_per_call, p.median_ns)
        gm_p90 = gmacs(p.macs_per_call, p90_rate_ns(p.samples_ns_per_call))
        wg = weight_gbs(p.weight_bytes, p.median_ns)
        s = scalar[p.working_set]
        peak_class = PEAK_CLASS.get(p.family)
        row = {
            "variant": p.variant,
            "family": p.family,
            "accumulators": p.accumulators,
            "working_set": p.working_set,
            "disasm_ok": p.variant in ok_variants,
            "is_best": best.get((p.family, p.working_set)) == p.variant,
            "rows": p.rows,
            "k": p.k,
            "weight_bytes": p.weight_bytes,
            "macs_per_call": p.macs_per_call,
            "macs_per_weight_byte": p.macs_per_weight_byte,
            "calls_per_rep": p.calls_per_rep,
            "reps": p.reps_timed,
            "median_ns": p.median_ns,
            "q1_ns": p.q1_ns,
            "q3_ns": p.q3_ns,
            "iqr_over_median": p.iqr_ns / p.median_ns,
            "slow_share": slow_share(p.samples_ns_per_call),
            "gmacs": gm,
            "gmacs_lo": gmacs(p.macs_per_call, p.q3_ns),  # slower quartile
            "gmacs_hi": gmacs(p.macs_per_call, p.q1_ns),
            "gmacs_p90": gm_p90,
            "weight_gbs": wg,
            "speedup_vs_scalar": gm / gmacs(s.macs_per_call, s.median_ns),
            "speedup_vs_scalar_per_weight_byte": wg / weight_gbs(s.weight_bytes, s.median_ns),
            "peak_class": peak_class,
            "peak_gmacs": None,
            "fraction_of_peak": None,
            "fraction_of_peak_p90": None,
            "ref_B_GBps": b_best / 1e9,
            "ref_B1_GBps": b_one / 1e9,
            "fraction_of_B": None,
            "fraction_of_B1": None,
            "ref_C_sdot_GMACs": c_ops["sdot"] / 2e9,
            "ref_C_smmla_GMACs": c_ops["smmla"] / 2e9,
            "bandwidth_record": ref["bandwidth_record"]["path"],
            "peak_record": ref["peak_record"]["path"],
            "source_file": source,
        }
        if p.working_set == "L1" and peak_class:
            row["peak_gmacs"] = c_ops[peak_class] / 2e9  # ops -> MACs, per ns
            row["fraction_of_peak"] = gm / row["peak_gmacs"]
            row["fraction_of_peak_p90"] = gm_p90 / row["peak_gmacs"]
        if p.working_set == "DRAM":
            row["fraction_of_B"] = wg * 1e9 / b_best
            row["fraction_of_B1"] = wg * 1e9 / b_one
        rows.append(row)
    return rows


def p90_rate_ns(samples_ns: Sequence[float]) -> float:
    """The time per call that goes with the p90 *rate* (the 10th percentile of the times)."""
    return 1.0 / percentile90([1.0 / s for s in samples_ns])


def write_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=MICRO_COLUMNS, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({c: ("" if row[c] is None else row[c]) for c in MICRO_COLUMNS})


def summary_lines(rows: Sequence[dict]) -> list[str]:
    """A readable table: one line per variant and working set, with the best of each family marked."""
    header = (
        f"{'variant':<10} {'set':<5} {'median ns':>12} {'GMAC/s':>9} {'GB/s(W)':>9}"
        f" {'x scalar':>9} {'x scalar/B':>10} {'% peak':>7} {'% B(1)':>7} {'% B1(1)':>8}"
        f" {'slow':>5}  notes"
    )
    lines = [header]

    def pct(v):
        return "-" if v is None else f"{100 * v:.1f}"

    for r in rows:
        notes = []
        if r["is_best"]:
            notes.append("best of family")
        if not r["disasm_ok"]:
            notes.append("DISASSEMBLY CHECK FAILED (left out of 'best')")
        if r["macs_per_weight_byte"] != 1:
            notes.append(f"{r['macs_per_weight_byte']} MACs per weight byte")
        lines.append(
            f"{r['variant']:<10} {r['working_set']:<5} {r['median_ns']:>12.1f} {r['gmacs']:>9.2f}"
            f" {r['weight_gbs']:>9.2f} {r['speedup_vs_scalar']:>9.2f}"
            f" {r['speedup_vs_scalar_per_weight_byte']:>10.2f} {pct(r['fraction_of_peak']):>7}"
            f" {pct(r['fraction_of_B']):>7} {pct(r['fraction_of_B1']):>8}"
            f" {100 * r['slow_share']:>4.0f}%  " + "; ".join(notes)
        )
    return lines


# --- command line: raw record -> results/processed/micro.csv ----------------------------------


def newest_record(raw_dir: Path) -> Path:
    """The newest micro record by file name (session ids are UTC timestamps; `__2` sorts after)."""
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        raise SystemExit(f"no micro record in {raw_dir}: run `make micro` on the VM first")
    return files[-1]


def main(argv: list[str] | None = None) -> int:
    from edge_llm.schema import MicroRecord  # local import: schema imports this module

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--record", type=Path, help="default: the newest in results/raw/micro/")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / PROCESSED_DIR)
    args = parser.parse_args(argv)

    path = args.record or newest_record(REPO_ROOT / RAW_DIR)
    record = MicroRecord.from_dict(json.loads(path.read_text()))
    try:
        source = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source = str(path)
    rows = derive_rows(record, source)
    out = args.out_dir / "micro.csv"
    write_csv(out, rows)
    print(f"{source} -> {out}")
    for line in summary_lines(rows):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
