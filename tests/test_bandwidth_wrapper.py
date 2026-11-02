"""bench/bandwidth/run_bandwidth.py record assembly, B(t) and the ADR-021 validity check, on fake
program output."""

import json

import pytest

from bench.bandwidth import run_bandwidth as rb
from edge_llm.bandwidth import (
    VALID_RATIO,
    b_of_record,
    b_of_t,
    valid_variants,
    validity_table,
)
from edge_llm.schema import BandwidthPoint, BandwidthRecord, SchemaError

# read speed relative to one stream, and to 8 accumulators: more of either helps a little
STREAM_GAIN = {1: 1.0, 2: 1.2, 4: 1.3, 8: 1.25}
ACC_GAIN = {8: 1.0, 16: 1.02}
VARIANTS = [(a, k) for a in (8, 16) for k in (1, 2, 4, 8)]
L1_PASSES = 100_000  # 32 KiB x 100 000 = 3.3 GB per timed repetition: tens of milliseconds


def fake_result(
    kernel, t, k=1, acc=16, base=10e9, reps=25, ok=True, hugepage=False, l1=False, l1_factor=3.0
):
    scale = STREAM_GAIN[k] * ACC_GAIN[acc] if kernel == "read" else 1.0
    rate = base * t * scale * (l1_factor if l1 else 1.0)
    samples = [rate * (1 + 0.001 * (i % 5)) for i in range(reps)]
    buffer = 32768 * t if l1 else 1 << 30
    return {
        "kernel": kernel,
        "acc": acc if kernel == "read" else 0,
        "streams": k if kernel == "read" else 0,
        "hugepage": hugepage,
        "l1": l1,
        "passes": L1_PASSES if l1 else 1,
        "anon_huge_kb": 1048576 if hugepage else 0,
        "buffer_bytes": buffer,
        "bytes_per_rep": buffer * (L1_PASSES if l1 else 1),
        "reps_warmup": 3,
        "reps_timed": reps,
        "checksum_ok": ok,
        "getcpu_ok": True,
        "observed_cpus": list(range(t)),
        "samples_bytes_per_s": samples,
    }


def run_dict(t, results):
    return {
        "threads": t,
        "process_cpus": list(range(t)),
        "taskset_cpus": f"0-{t - 1}",
        "returncode": 0,
        "results": results,
    }


def fake_run(t, streams=(1, 2, 4, 8), accs=(8, 16), **kw):
    """A 1 GiB run of every variant plus the triad."""
    results = [fake_result("read", t, k, a, **kw) for a in accs for k in streams]
    return run_dict(t, results + [fake_result("triad", t, **kw)])


def fake_l1_run(factors=None, accs=(8, 16), streams=(1, 2, 4, 8)):
    """The validity runs at one thread; `factors[(acc, k)]` = L1 rate / 1 GiB rate."""
    factors = factors or {}
    return run_dict(
        1,
        [
            fake_result("read", 1, k, a, l1=True, l1_factor=factors.get((a, k), 3.0))
            for a in accs
            for k in streams
        ],
    )


def record(points, **extra):
    rec = {
        "schema_version": 1,
        "kind": "bandwidth",
        "session_id": "S",
        "phase": "start",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "binary": {},
        "host": {},
        "points": points,
        "objdump_file": "x.s",
    }
    rec.update(extra)
    return rec


def all_points(l1=True, l1_factors=None, **kw):
    pts = []
    for t in (1, 2, 4, 8):
        run = fake_run(t, **kw)
        pts += [rb.to_point(run, r) for r in run["results"]]
    if l1:
        run = fake_l1_run(l1_factors)
        pts += [rb.to_point(run, r) for r in run["results"]]
    return pts


def read_loop_text(name, spill=False, store=False, loads=True):
    """objdump-style text of a read function: a loop of vector loads and adds."""
    body = ["movi\tv0.2d, #0x0"]
    top = 0x780 + 4 * len(body)
    if loads:
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


def full_record(points, loops=None):
    return record(points, validity=rb.make_validity(points, loops or good_loops()))


# --- the record -------------------------------------------------------------------------------


def test_a_good_run_validates_and_summaries_match_the_samples():
    rec = BandwidthRecord.from_dict(json.loads(json.dumps(record(all_points()))))
    read8 = next(p for p in rec.points if p.kernel == "read" and p.threads == 8)
    assert read8.median > read8.q1 and read8.iqr == pytest.approx(read8.q3 - read8.q1)
    assert read8.pinning["getcpu_ok"] is True


def test_to_point_keeps_the_variant_and_the_l1_fields():
    run = fake_l1_run()
    pt = rb.to_point(run, run["results"][0])
    assert (pt["accumulators"], pt["streams"], pt["l1"], pt["passes"]) == (8, 1, True, L1_PASSES)
    assert pt["bytes_per_rep"] == 32768 * L1_PASSES and "validity check" in pt["note"]


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


def test_an_l1_repetition_must_last_at_least_10_ms():
    pts = all_points()
    l1 = next(p for p in pts if p["l1"])
    l1["passes"] = 100  # 3.3 MB per repetition at tens of GB/s: about 0.1 ms
    l1["bytes_per_rep"] = 32768 * 100
    with pytest.raises(SchemaError, match="under 10 ms"):
        BandwidthRecord.from_dict(record(pts))


def test_an_l1_run_must_say_how_many_bytes_it_moved():
    pts = all_points()
    next(p for p in pts if p["l1"])["bytes_per_rep"] += 1
    with pytest.raises(SchemaError, match="bytes_per_rep"):
        BandwidthRecord.from_dict(record(pts))


def test_accumulators_are_8_or_16():
    run = fake_run(1)
    pt = rb.to_point(run, run["results"][0])
    pt["accumulators"] = 24
    with pytest.raises(SchemaError, match="accumulators"):
        BandwidthPoint.from_dict(pt)


def test_thread_counts_must_share_the_same_variants():
    pts = [
        p
        for p in all_points()
        if not (
            p["kernel"] == "read"
            and p["threads"] == 4
            and (p["accumulators"], p["streams"]) == (16, 8)
        )
    ]
    with pytest.raises(SchemaError, match="same read variants"):
        BandwidthRecord.from_dict(record(pts))


def test_the_l1_runs_must_cover_the_same_variants_as_the_1_gib_runs():
    pts = all_points()
    pts = [p for p in pts if not (p["l1"] and (p["accumulators"], p["streams"]) == (16, 4))]
    with pytest.raises(SchemaError, match="L1 validity runs"):
        BandwidthRecord.from_dict(full_record_unchecked(pts))


def full_record_unchecked(points):
    """A record with a validity table built from whatever points exist."""
    return record(points, validity=rb.make_validity(points, good_loops()))


# --- the validity check -----------------------------------------------------------------------


def test_the_ratio_is_the_l1_median_over_the_1_gib_median():
    table = validity_table(BandwidthPoint.from_dict(p) for p in all_points())
    assert [(r["accumulators"], r["streams"]) for r in table] == VARIANTS
    row = next(r for r in table if (r["accumulators"], r["streams"]) == (16, 4))
    assert row["ratio"] == pytest.approx(row["l1_median"] / row["dram_median"])
    assert row["ratio"] == pytest.approx(3.0, rel=1e-6) and row["valid"] is True


def test_a_variant_is_valid_from_a_ratio_of_1_5():
    assert VALID_RATIO == 1.5

    def valid_with(factor):
        pts = all_points(l1_factors={(8, 1): factor})
        rows = validity_table(BandwidthPoint.from_dict(p) for p in pts)
        return next(r for r in rows if (r["accumulators"], r["streams"]) == (8, 1))["valid"]

    assert valid_with(1.5001) and valid_with(3.0)
    assert not valid_with(1.49) and not valid_with(1.0)


def test_a_variant_without_an_l1_run_is_not_valid():
    pts = [p for p in all_points() if not (p["l1"] and p["accumulators"] == 16)]
    rows = validity_table(BandwidthPoint.from_dict(p) for p in pts)
    assert {(r["accumulators"], r["streams"]) for r in rows if r["valid"]} == {
        (8, k) for k in (1, 2, 4, 8)
    }
    assert all(r["ratio"] is None for r in rows if r["accumulators"] == 16)


def test_b_of_t_is_the_best_1_gib_median_over_the_valid_variants():
    rec = BandwidthRecord.from_dict(json.loads(json.dumps(full_record(all_points()))))
    b = b_of_record(rec)
    assert sorted(b) == [1, 2, 4, 8]
    assert (b[8].accumulators, b[8].streams) == (16, 4)  # fastest in the fake data
    assert b[8].b > b[8].b1 and (b[8].b1_accumulators) == 16
    assert len(b[8].medians_by_variant) == 8


def test_an_invalid_variant_is_left_out_even_if_it_is_the_fastest():
    pts = all_points(l1_factors={(16, 4): 1.0})  # the fastest variant is limited by its loop
    rec = BandwidthRecord.from_dict(full_record(pts))
    b = b_of_record(rec)
    assert (b[8].accumulators, b[8].streams) != (16, 4)
    assert (b[8].accumulators, b[8].streams) == (
        8,
        4,
    )  # next best: 1.3 x 1.0 beats 16 x 8 at 1.25 x 1.02
    # without the validity table the fastest would win
    assert b_of_t(rec.points)[8].streams == 4


def test_b1_is_the_best_valid_variant_at_one_stream():
    pts = all_points(l1_factors={(16, 1): 1.0})  # 16 x 1 is invalid; 8 x 1 remains
    b = b_of_record(BandwidthRecord.from_dict(full_record(pts)))
    assert all(v.b1_accumulators == 8 for v in b.values())
    assert b[1].b1 == pytest.approx(rec_median(pts, 1, 8, 1))


def rec_median(pts, t, acc, k):
    return next(
        BandwidthPoint.from_dict(p).median
        for p in pts
        if p["kernel"] == "read"
        and not p["l1"]
        and not p["hugepage"]
        and (p["threads"], p["accumulators"], p["streams"]) == (t, acc, k)
    )


def test_the_winners_are_recorded_for_every_thread_count():
    rec = full_record(all_points())
    w = rec["validity"]["winners"]
    assert sorted(w) == ["1", "2", "4", "8"]
    assert (w["8"]["accumulators"], w["8"]["streams"]) == (16, 4)
    assert w["8"]["b"] > w["8"]["b1"] and w["8"]["b1_accumulators"] == 16
    assert rec["validity"]["any_valid"] is True and rec["validity"]["min_ratio"] == 1.5


def test_the_run_fails_only_if_no_variant_is_valid():
    flat = {v: 1.0 for v in VARIANTS}
    none = rb.make_validity(all_points(l1_factors=flat), good_loops())
    assert none["any_valid"] is False and none["winners"] == {}
    one = rb.make_validity(all_points(l1_factors={**flat, (8, 2): 2.0}), good_loops())
    assert one["any_valid"] is True
    assert {(w["accumulators"], w["streams"]) for w in one["winners"].values()} == {(8, 2)}
    # no valid one-stream variant: B(t) still exists, B1(t) does not
    assert all(w["b1"] is None and w["b1_accumulators"] is None for w in one["winners"].values())
    assert sorted(one["winners"]) == ["1", "2", "4", "8"]


def test_valid_variants_come_from_the_table():
    table = validity_table(
        BandwidthPoint.from_dict(p) for p in all_points(l1_factors={(8, 2): 1.0})
    )
    assert valid_variants(table) == set(VARIANTS) - {(8, 2)}


# --- the loops --------------------------------------------------------------------------------


def test_the_check_covers_eight_loops_8_and_16_accumulators_at_every_k():
    assert rb.READ_LOOP_FUNCTIONS == tuple(
        f"read_slice_acc{a}_k{k}" for a in (8, 16) for k in (1, 2, 4, 8)
    )


def test_stack_accesses_are_reported_but_do_not_fail_a_loop():
    spill = rb.check_read_loop("f", read_loop_text("f", spill=True))
    assert spill["ok"] and spill["stack_accesses"] == ["str q3, [sp, #16]", "ldr q3, [sp, #16]"]
    assert len(spill["stores"]) == 1 and spill["vector_loads"] == 9
    store = rb.check_read_loop("f", read_loop_text("f", store=True))
    assert store["ok"] and store["stores"] == ["str q4, [x9]"]


def test_a_clean_loop_reports_its_loads_and_no_stack_access():
    ok = rb.check_read_loop("f", read_loop_text("f"))
    assert ok["ok"] and ok["vector_loads"] == 8 and ok["stack_accesses"] == []


def test_ldp_counts_two_vector_loads():
    text = "0000 <f>:\n  780:\tldp\tq0, q1, [x1]\n  784:\tsubs\tx0, x0, #0x1\n  788:\tb.ne\t780 <f+0x0>\n"
    assert rb.check_read_loop("f", text)["vector_loads"] == 2


def test_a_missing_loop_or_a_loop_without_vector_loads_is_an_error():
    assert not rb.check_read_loop("f", "0000 <f>:\n  780:\tret\n")["ok"]
    assert not rb.check_read_loop("f", read_loop_text("f", loads=False))["ok"]


# --- records from before ADR-021 --------------------------------------------------------------


def test_a_day2_record_without_the_newer_fields_still_validates():
    new = ("streams", "hugepage", "anon_huge_kb", "accumulators", "l1", "passes")
    pts = []
    for t in (1, 2):
        run = fake_run(t, streams=(1,), accs=(8,))
        pts += [
            {k: v for k, v in rb.to_point(run, r).items() if k not in new} for r in run["results"]
        ]
    rec = BandwidthRecord.from_dict(record(pts, acc_check={"pass": True}))
    assert {(p.accumulators, p.streams) for p in rec.points if p.kernel == "read"} == {(8, 1)}
    b = b_of_record(rec)  # no validity table: every variant counts
    assert sorted(b) == [1, 2] and b[2].b == b[2].b1


def test_huge_page_runs_are_diagnostics_and_do_not_enter_b_of_t():
    pts = all_points()
    hp_run = run_dict(1, [fake_result("read", 1, 1, 16, base=99e9, hugepage=True)])
    pts += [rb.to_point(hp_run, r) for r in hp_run["results"]]
    rec = BandwidthRecord.from_dict(full_record(pts))
    assert b_of_record(rec)[1].b < 99e9
    bad = rb.to_point(hp_run, hp_run["results"][0])
    bad["streams"] = 2
    with pytest.raises(SchemaError, match="huge-page"):
        BandwidthRecord.from_dict(record(all_points() + [bad]))
