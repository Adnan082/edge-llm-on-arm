"""B(t) from a bandwidth record (CLAUDE.md §8, ADR-017, ADR-021).

A read *variant* is a pair (accumulators, streams): 8 or 16 vector accumulators, and k = 1, 2, 4
or 8 interleaved streams per thread. A read test can only under-measure memory speed (the
checksum proves every byte was read), so the fastest variant is the best estimate, provided the
loop itself is not the limit. That is checked per variant at one thread (ADR-021): the same loop
over a 32 KiB buffer (fits in L1) must be at least 1.5 times faster than over 1 GiB.

`B(t)` = the best 1 GiB median over the valid variants; `B1(t)` = the best valid one at k = 1.
Huge-page runs are diagnostics and never enter either. No hardware calls: runs in CI.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

STREAM_COUNTS = (1, 2, 4, 8)
ACCUMULATOR_COUNTS = (8, 16)
HUGEPAGE_DIAGNOSTIC_THREADS = (1, 8)
L1_BUFFER_BYTES = 32 * 1024
VALID_RATIO = 1.5  # a variant is valid if its L1 median is at least this times its 1 GiB median
MIN_L1_REP_SECONDS = 0.010  # each timed L1 repetition lasts at least this long

Variant = tuple[int, int]  # (accumulators, streams)


@dataclass(frozen=True)
class BandwidthAt:
    threads: int
    b: float  # bytes/s: best median over the valid variants
    accumulators: int  # the variant that gave it
    streams: int
    b1: float | None  # bytes/s: best valid median at k = 1; None if no k = 1 variant is valid
    b1_accumulators: int | None
    medians_by_variant: dict[Variant, float]  # all variants, valid or not


def read_medians(points: Iterable, l1: bool = False) -> dict[int, dict[Variant, float]]:
    """{threads: {(accumulators, streams): median bytes/s}} for plain (non-huge-page) reads.

    `l1=True` gives the 32 KiB runs of the validity check instead of the 1 GiB ones.
    """
    out: dict[int, dict[Variant, float]] = {}
    for p in points:
        if p.kernel == "read" and not p.hugepage and p.l1 == l1:
            out.setdefault(p.threads, {})[(p.accumulators, p.streams)] = p.median
    return out


def validity_table(points: Iterable) -> list[dict]:
    """One row per variant at one thread: L1 median, 1 GiB median, their ratio, valid or not.

    A variant with no L1 run is not valid.
    """
    points = list(points)
    dram = read_medians(points).get(1, {})
    l1 = read_medians(points, l1=True).get(1, {})
    rows = []
    for variant in sorted(set(dram) | set(l1)):
        a, k = variant
        d, m = dram.get(variant), l1.get(variant)
        ratio = m / d if d and m else None
        rows.append(
            {
                "accumulators": a,
                "streams": k,
                "l1_median": m,
                "dram_median": d,
                "ratio": ratio,
                "valid": ratio is not None and ratio >= VALID_RATIO,
            }
        )
    return rows


def valid_variants(table: Iterable[dict]) -> set[Variant]:
    return {(r["accumulators"], r["streams"]) for r in table if r["valid"]}


def b_of_t(points: Iterable, valid: set[Variant] | None = None) -> dict[int, BandwidthAt]:
    """B(t) and B1(t) for every thread count, from the valid variants.

    `valid=None` counts every variant (records from before ADR-021 have no validity check).
    A thread count with no valid variant is left out; with none at k = 1 it has B(t) but no B1(t).
    """
    out: dict[int, BandwidthAt] = {}
    for t, by_v in sorted(read_medians(points).items()):
        usable = {v: m for v, m in by_v.items() if valid is None or v in valid}
        one = {v: m for v, m in usable.items() if v[1] == 1}
        if not usable:
            continue
        best = max(usable, key=lambda v: usable[v])
        best1 = max(one, key=lambda v: one[v]) if one else None
        out[t] = BandwidthAt(
            threads=t,
            b=usable[best],
            accumulators=best[0],
            streams=best[1],
            b1=one[best1] if best1 else None,
            b1_accumulators=best1[0] if best1 else None,
            medians_by_variant=dict(sorted(by_v.items())),
        )
    return out


def b_of_record(record) -> dict[int, BandwidthAt]:
    """B(t) of a BandwidthRecord, using its own validity table if it has one."""
    table = (record.validity or {}).get("variants")
    return b_of_t(record.points, valid_variants(table) if table else None)
