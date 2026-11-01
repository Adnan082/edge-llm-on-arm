"""Median and IQR on synthetic samples (CLAUDE.md §9: analysis aggregation)."""

import math

import numpy as np
import pytest

from edge_llm.stats import quartiles, summarise


def test_known_answer_odd_count():
    s = summarise([1, 2, 3, 4, 5])
    assert (s["q1"], s["median"], s["q3"], s["iqr"]) == (2, 3, 4, 2)
    assert (s["min"], s["max"], s["n"]) == (1, 5, 5)
    assert s["iqr_over_median"] == pytest.approx(2 / 3)


def test_even_count_interpolates():
    assert quartiles([10, 20, 30, 40]) == (17.5, 25.0, 32.5)


def test_one_sample_has_zero_spread():
    s = summarise([7.0])
    assert s["median"] == 7.0 and s["iqr"] == 0.0


def test_unsorted_input_and_outlier_do_not_move_the_median_much():
    s = summarise([100, 101, 99, 100, 5000, 100])
    assert s["median"] == 100
    assert s["max"] == 5000


def test_matches_numpy_percentiles():
    rng = np.random.default_rng(0)
    x = rng.normal(100, 5, size=31).tolist()
    q1, med, q3 = quartiles(x)
    assert (q1, med, q3) == pytest.approx(tuple(np.percentile(x, [25, 50, 75])))


def test_empty_raises_and_zero_median_gives_nan_ratio():
    with pytest.raises(ValueError):
        quartiles([])
    assert math.isnan(summarise([-1, 0, 1])["iqr_over_median"])
