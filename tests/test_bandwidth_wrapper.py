"""bench/bandwidth/run_bandwidth.py record assembly, on fake program output."""

import json

import pytest

from bench.bandwidth import run_bandwidth as rb
from edge_llm.schema import BandwidthRecord, SchemaError


def fake_run(t, base=10e9, reps=25, ok=True):
    samples = [base * t * (1 + 0.001 * (i % 5)) for i in range(reps)]

    def result(kernel, acc):
        return {
            "kernel": kernel,
            "acc": acc,
            "buffer_bytes": 1 << 30,
            "bytes_per_rep": 1 << 30,
            "reps_warmup": 3,
            "reps_timed": reps,
            "checksum_ok": ok,
            "getcpu_ok": True,
            "observed_cpus": list(range(t)),
            "samples_bytes_per_s": samples,
        }

    return {
        "threads": t,
        "process_cpus": list(range(t)),
        "taskset_cpus": f"0-{t - 1}",
        "returncode": 0,
        "results": [result("read", 8), result("triad", 0)],
    }


def record(points):
    return {
        "schema_version": 1,
        "kind": "bandwidth",
        "session_id": "S",
        "phase": "start",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "binary": {},
        "host": {},
        "points": points,
        "acc_check": {},
        "objdump_file": "x.s",
    }


def all_points(**kw):
    pts = []
    for t in (1, 2, 4, 8):
        run = fake_run(t, **kw)
        pts += [rb.to_point(run, r) for r in run["results"]]
    return pts


def test_a_good_run_validates_and_summaries_match_the_samples():
    rec = BandwidthRecord.from_dict(json.loads(json.dumps(record(all_points()))))
    read8 = next(p for p in rec.points if p.kernel == "read" and p.threads == 8)
    assert read8.median > read8.q1 and read8.iqr == pytest.approx(read8.q3 - read8.q1)
    assert read8.pinning["getcpu_ok"] is True


def test_too_few_repeats_are_rejected():
    with pytest.raises(SchemaError, match="at least 20"):
        BandwidthRecord.from_dict(record(all_points(reps=10)))


def test_a_failed_checksum_is_rejected():
    with pytest.raises(SchemaError, match="checksum"):
        BandwidthRecord.from_dict(record(all_points(ok=False)))


def test_a_tampered_median_is_rejected():
    pts = all_points()
    pts[0]["median"] *= 1.5
    with pytest.raises(SchemaError, match="median"):
        BandwidthRecord.from_dict(record(pts))


def test_a_thread_on_the_wrong_core_is_rejected():
    run = fake_run(2)
    run["results"][0]["observed_cpus"] = [0, 5]
    pts = [rb.to_point(run, r) for r in run["results"]]
    with pytest.raises(SchemaError, match="sched_getcpu"):
        BandwidthRecord.from_dict(record(pts))


def test_acc_check_passes_when_doubling_accumulators_changes_nothing():
    def r(acc, base):
        return {"acc": acc, "samples_bytes_per_s": [base] * 5}

    ok = rb.acc_check_summary({"threads": 1, "results": [r(4, 9e9), r(8, 12e9), r(16, 12.1e9)]})
    assert ok["pass"] and ok["ratio_16_over_8"] == pytest.approx(12.1 / 12)
    bad = rb.acc_check_summary({"threads": 1, "results": [r(4, 6e9), r(8, 9e9), r(16, 12e9)]})
    assert not bad["pass"]
