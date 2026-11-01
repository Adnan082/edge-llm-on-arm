"""bench/bandwidth/run_bandwidth.py record assembly, on fake program output."""

import json

import pytest

from bench.bandwidth import run_bandwidth as rb
from edge_llm.schema import BandwidthRecord, SchemaError

# read speed relative to one stream: more streams help until the memory system is full
STREAM_GAIN = {1: 1.0, 2: 1.2, 4: 1.3, 8: 1.25}


def fake_result(kernel, t, k=1, acc=8, base=10e9, reps=25, ok=True, hugepage=False):
    scale = STREAM_GAIN[k] if kernel == "read" else 1.0
    samples = [base * t * scale * (1 + 0.001 * (i % 5)) for i in range(reps)]
    return {
        "kernel": kernel,
        "acc": acc if kernel == "read" else 0,
        "streams": k if kernel == "read" else 0,
        "hugepage": hugepage,
        "anon_huge_kb": 1048576 if hugepage else 0,
        "buffer_bytes": 1 << 30,
        "bytes_per_rep": 1 << 30,
        "reps_warmup": 3,
        "reps_timed": reps,
        "checksum_ok": ok,
        "getcpu_ok": True,
        "observed_cpus": list(range(t)),
        "samples_bytes_per_s": samples,
    }


def fake_run(t, streams=(1, 2, 4, 8), **kw):
    return {
        "threads": t,
        "process_cpus": list(range(t)),
        "taskset_cpus": f"0-{t - 1}",
        "returncode": 0,
        "results": [fake_result("read", t, k, **kw) for k in streams]
        + [fake_result("triad", t, **kw)],
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
    def r(acc, base, streams=1):
        return {"acc": acc, "streams": streams, "samples_bytes_per_s": [base] * 5}

    ok = rb.acc_check_summary({"threads": 1, "results": [r(4, 9e9), r(8, 12e9), r(16, 12.1e9)]})
    assert ok["pass"] and ok["ratio_16_over_8"] == pytest.approx(12.1 / 12)
    bad = rb.acc_check_summary({"threads": 1, "results": [r(4, 6e9), r(8, 9e9), r(16, 12e9)]})
    assert not bad["pass"]


def test_acc_check_all_needs_every_stream_count_to_pass():
    def r(acc, base, streams):
        return {"acc": acc, "streams": streams, "samples_bytes_per_s": [base] * 5}

    good = [r(a, 12e9, k) for k in (1, 8) for a in (4, 8, 16)]
    run = {"threads": 1, "results": good}
    assert rb.acc_check_all(run)["pass"] is True
    # k = 8 is add-chain bound: 16 accumulators go faster than 8
    bad = [x for x in good if not (x["streams"] == 8 and x["acc"] == 16)] + [r(16, 16e9, 8)]
    result = rb.acc_check_all({"threads": 1, "results": bad})
    assert result["pass"] is False and result["by_streams"]["1"]["pass"] is True


def test_the_record_keeps_every_stream_count_and_b_of_t_is_the_best_of_them():
    from edge_llm.bandwidth import b_of_t

    rec = BandwidthRecord.from_dict(json.loads(json.dumps(record(all_points()))))
    b = b_of_t(rec.points)
    assert sorted(b) == [1, 2, 4, 8]
    assert b[8].streams == 4 and b[8].b > b[8].b1  # k = 4 is the fastest in the fake data
    assert b[8].medians_by_streams.keys() == {1, 2, 4, 8}


def test_a_day2_record_without_stream_fields_still_validates():
    pts = []
    for t in (1, 2):
        run = fake_run(t, streams=(1,))
        for r in run["results"]:
            for key in ("streams", "hugepage", "anon_huge_kb"):
                r.pop(key)
        pts += [
            {
                k: v
                for k, v in rb.to_point(run, r).items()
                if k not in ("streams", "hugepage", "anon_huge_kb")
            }
            for r in run["results"]
        ]
    rec = BandwidthRecord.from_dict(record(pts))
    assert {p.streams for p in rec.points if p.kernel == "read"} == {1}


def test_huge_page_runs_are_diagnostics_and_do_not_enter_b_of_t():
    from edge_llm.bandwidth import b_of_t

    pts = all_points()
    hp_run = {
        **fake_run(1, streams=()),
        "results": [fake_result("read", 1, 1, base=99e9, hugepage=True)],
    }
    pts += [rb.to_point(hp_run, r) for r in hp_run["results"]]
    rec = BandwidthRecord.from_dict(record(pts))
    assert b_of_t(rec.points)[1].b < 99e9
    bad = rb.to_point(hp_run, hp_run["results"][0])
    bad["streams"] = 2
    with pytest.raises(SchemaError, match="huge-page"):
        BandwidthRecord.from_dict(record(all_points() + [bad]))


def test_thread_counts_must_share_the_same_stream_counts():
    pts = [
        p
        for p in all_points()
        if not (p["kernel"] == "read" and p["threads"] == 4 and p["streams"] == 8)
    ]
    with pytest.raises(SchemaError, match="same read stream counts"):
        BandwidthRecord.from_dict(record(pts))
