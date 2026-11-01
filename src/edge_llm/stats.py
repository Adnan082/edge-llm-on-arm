"""Median, quartiles and IQR of a list of samples (CLAUDE.md §7.4).

Quartiles use linear interpolation between the sorted samples (numpy's default, "type 7"), so
the numbers match what pandas/numpy would give later in analyse.py.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence


def quartiles(samples: Sequence[float]) -> tuple[float, float, float]:
    """(Q1, median, Q3) of the samples."""
    if not samples:
        raise ValueError("no samples")
    if len(samples) == 1:
        x = float(samples[0])
        return x, x, x
    q1, med, q3 = statistics.quantiles(samples, n=4, method="inclusive")
    return q1, med, q3


def summarise(samples: Sequence[float]) -> dict[str, float | int]:
    """n, min, Q1, median, Q3, IQR, max, and IQR/median (the 5 % noise rule of §7.4)."""
    q1, med, q3 = quartiles(samples)
    return {
        "n": len(samples),
        "min": min(samples),
        "q1": q1,
        "median": med,
        "q3": q3,
        "iqr": q3 - q1,
        "max": max(samples),
        "iqr_over_median": (q3 - q1) / med if med else float("nan"),
    }


NOISY_THRESHOLD = 0.05  # CLAUDE.md §7.4: IQR/median above this flags a point as noisy


def is_noisy(samples: Sequence[float], threshold: float = NOISY_THRESHOLD) -> bool:
    """True if IQR/median of the samples is above the threshold."""
    return summarise(samples)["iqr_over_median"] > threshold
