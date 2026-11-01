"""B(t) from a bandwidth record (CLAUDE.md §8, ADR-017).

`B(t)` is the best median over k = 1, 2, 4, 8 interleaved read streams per thread; `B1(t)`, the
one-stream (k = 1) median, is kept as the reference for simple sequential access. Huge-page runs
are diagnostics and never enter B(t). No hardware calls: runs in CI.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

STREAM_COUNTS = (1, 2, 4, 8)
HUGEPAGE_DIAGNOSTIC_THREADS = (1, 8)


@dataclass(frozen=True)
class BandwidthAt:
    threads: int
    b: float  # bytes/s: best median over the stream counts
    streams: int  # the k that gave it
    b1: float  # bytes/s: the k = 1 median
    medians_by_streams: dict[int, float]


def read_medians(points: Iterable) -> dict[int, dict[int, float]]:
    """{threads: {streams: median bytes/s}} for the plain (non-huge-page) read points."""
    out: dict[int, dict[int, float]] = {}
    for p in points:
        if p.kernel == "read" and not p.hugepage:
            out.setdefault(p.threads, {})[p.streams] = p.median
    return out


def b_of_t(points: Iterable) -> dict[int, BandwidthAt]:
    """B(t) and B1(t) for every thread count that has a one-stream read point."""
    out: dict[int, BandwidthAt] = {}
    for t, by_k in sorted(read_medians(points).items()):
        if 1 not in by_k:
            raise ValueError(f"t={t}: no one-stream read median, so no B1(t)")
        k_best = max(by_k, key=lambda k: by_k[k])
        out[t] = BandwidthAt(
            threads=t,
            b=by_k[k_best],
            streams=k_best,
            b1=by_k[1],
            medians_by_streams=dict(sorted(by_k.items())),
        )
    return out
