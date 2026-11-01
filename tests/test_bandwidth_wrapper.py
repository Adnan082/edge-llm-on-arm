"""bench/bandwidth/run_bandwidth.py record assembly, on fake program output."""

import json

import pytest

from bench.bandwidth import run_bandwidth as rb
from edge_llm.schema import BandwidthRecord, SchemaError

# read speed relative to one stream: more streams help until the memory system is full
STREAM_GAIN = {1: 1.0, 2: 1.2, 4: 1.3, 8: 1.25}


def fake_result(kernel, t, k=1, acc=16, base=10e9, reps=25, ok=True, hugepage=False):
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


def acc_result(acc, base, streams=1):
    return {"acc": acc, "streams": streams, "samples_bytes_per_s": [base] * 5}


def read_loop_text(name, spill=False, store=False):
    """objdump-style text of a read function: a loop of vector loads and adds."""
    body = ["movi\tv0.2d, #0x0"]
    top = 0x780 + 4 * len(body)
    body += [f"ldr\tq{i % 28 + 1}, [x{i % 8 + 1}, #{16 * i}]" for i in range(8)]
    body += [f"add\tv{i % 24}.2d, v{i % 24}.2d, v{i % 8 + 1}.2d" for i in range(8)]
    if spill:
        body += ["str\tq3, [sp, #16]", "ldr\tq3, [sp, #16]"]
    if store:
        body += ["str\tq4, [x9]"]
    body += ["subs\tx0, x0, #0x1", f"b.ne\t{top:x} <{name}+0x8>", "ret"]
    lines = [f"0000000000000780 <{name}>:"]
    lines += [f"  {0x780 + 4 * i:x}:\t{t}" for i, t in enumerate(body)]
    return "\n".join(lines) + "\n"


def good_loops(**kw):
    return [rb.check_read_loop(n, read_loop_text(n, **kw)) for n in rb.READ_LOOP_FUNCTIONS]


def test_the_check_compares_24_accumulators_with_the_16_the_kernel_uses():
    assert (rb.BASE_ACC, rb.LARGE_ACC) == (16, 24)
    ok = rb.acc_check_summary(
        {"threads": 1, "results": [acc_result(16, 12e9), acc_result(24, 12.01e9)]}
    )
    assert ok["pass"] and ok["ratio_24_over_16"] == pytest.approx(12.01 / 12)
    assert set(ok["median_bytes_per_s_by_accumulators"]) == {"16", "24"}


def test_3_percent_is_the_limit_in_both_directions():
    def ratio_pass(ratio):
        run = {"threads": 1, "results": [acc_result(16, 10e9), acc_result(24, ratio * 10e9)]}
        return rb.acc_check_summary(run)["pass"]

    assert ratio_pass(1.029) and ratio_pass(0.971)
    assert not ratio_pass(1.038)  # the VM result at k = 8 with 8 vs 16 accumulators
    assert not ratio_pass(0.96)


def test_acc_check_all_records_every_k_and_passes_only_if_all_do():
    def run_with(ratios):
        results = []
        for k, ratio in ratios.items():
            results += [acc_result(16, 12e9, k), acc_result(24, 12e9 * ratio, k)]
        return {"threads": 1, "results": results}

    flat = {1: 1.001, 2: 1.0, 4: 0.99, 8: 1.02}
    out = rb.acc_check_all(run_with(flat), good_loops())
    assert out["pass"] is True and set(out["by_streams"]) == {"1", "2", "4", "8"}
    assert [c["streams"] for c in out["by_streams"].values()] == [1, 2, 4, 8]
    assert out["base_accumulators"] == 16 and out["large_accumulators"] == 24
    # one k outside 3 % fails the whole check, and the other k are still recorded
    bad = rb.acc_check_all(run_with({**flat, 8: 1.038}), good_loops())
    assert bad["pass"] is False
    assert [k for k, c in bad["by_streams"].items() if not c["pass"]] == ["8"]


def test_a_loop_that_spills_to_the_stack_fails_the_check_even_if_the_timing_agrees():
    results = [acc_result(a, 12e9, k) for k in (1, 2, 4, 8) for a in (16, 24)]
    loops = good_loops()
    loops[-1] = rb.check_read_loop("read_slice_acc24_k8", read_loop_text("x", spill=True))
    out = rb.acc_check_all({"threads": 1, "results": results}, loops)
    assert all(c["pass"] for c in out["by_streams"].values()) and out["pass"] is False
    assert out["loops"][-1]["stack_accesses"] == ["str q3, [sp, #16]", "ldr q3, [sp, #16]"]


def test_read_loop_check_finds_the_loop_and_rejects_stack_access_and_stores():
    ok = rb.check_read_loop("f", read_loop_text("f"))
    assert (
        ok["ok"] and ok["vector_loads"] == 8 and ok["stack_accesses"] == [] and ok["stores"] == []
    )
    assert not rb.check_read_loop("f", read_loop_text("f", spill=True))["ok"]
    assert not rb.check_read_loop("f", read_loop_text("f", store=True))["ok"]
    assert not rb.check_read_loop("f", "0000 <f>:\n  780:\tret\n")["ok"]  # no loop at all


def test_the_check_covers_eight_loops_16_and_24_accumulators_at_every_k():
    assert rb.READ_LOOP_FUNCTIONS == tuple(
        f"read_slice_acc{a}_k{k}" for a in (16, 24) for k in (1, 2, 4, 8)
    )


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
