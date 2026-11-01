"""Pilot summary: repeat-noise table and the full-sweep wall-time estimate, on synthetic records."""

import math

import pytest

from edge_llm import pilot, sweep
from tests.bench_fixtures import fake_bench_record, fake_sizes, real_cfg

CFG = real_cfg()
SIZES = fake_sizes(CFG)

# tokens/s of the synthetic pilot, per (quant, test, threads); the same for both builds
TPS = {
    ("F16", "pp512", 1): 40.0,
    ("F16", "pp512", 8): 280.0,
    ("F16", "tg128", 1): 9.0,
    ("F16", "tg128", 8): 25.0,
    ("F16", "tg128d2048", 1): 8.0,
    ("F16", "tg128d2048", 8): 22.0,
    ("Q4_0", "pp512", 1): 60.0,
    ("Q4_0", "pp512", 8): 400.0,
    ("Q4_0", "tg128", 1): 30.0,
    ("Q4_0", "tg128", 8): 90.0,
    ("Q4_0", "tg128d2048", 1): 25.0,
    ("Q4_0", "tg128d2048", 8): 70.0,
}
LARGE_PP2048 = 11.0  # large F16, t = 1: the extra long-prompt point


def pilot_records(noisy_ids=(), large=LARGE_PP2048):
    recs = []
    for pair in sweep.pairs(CFG, "pilot"):
        for point in pair.points():
            if point.model == "large":
                tps = large
            else:
                tps = TPS[(point.quant, point.test, point.threads)]
            te = sweep.parse_test(point.test)
            gib = SIZES[(point.model, point.quant)]["file_bytes"] / pilot.GIB
            reps = sweep.repetitions(CFG, pair)
            work = pilot._call_seconds(
                te, reps, tps, TPS.get((point.quant, "pp512", point.threads))
            )
            wall = work + 20.0 * gib  # 20 s of load per GiB
            recs.append(
                fake_bench_record(
                    point.config_id,
                    tps=tps,
                    reps=reps,
                    wall=wall,
                    noisy=point.config_id in noisy_ids,
                    file_bytes=SIZES[(point.model, point.quant)]["file_bytes"],
                    pair_index=pair.index,
                )
            )
    return recs


def test_noise_rows_list_every_record_with_iqr_over_median():
    noisy = "small_F16_baseline_t1_pp512"
    recs = pilot_records(noisy_ids=(noisy,))
    rows = pilot.noise_rows(recs)
    assert len(rows) == len(recs) == 26
    row = next(r for r in rows if r["config_id"] == noisy)
    assert row["noisy"] and row["iqr_over_median"] > 0.05
    assert all(not r["noisy"] and r["iqr_over_median"] < 0.05 for r in rows if r is not row)


def test_a_rerun_supersedes_the_first_run_in_the_estimate():
    first = fake_bench_record("small_F16_baseline_t1_pp512", tps=40.0, noisy=True)
    second = fake_bench_record("small_F16_baseline_t1_pp512", tps=44.0, attempt=2)
    latest = pilot.latest_records([second, first])
    assert latest["small_F16_baseline_t1_pp512"]["attempt"] == 2


def reference():
    return pilot._Reference(pilot.latest_records(pilot_records()), CFG, SIZES)


def test_pilot_points_are_returned_as_measured():
    ref = reference()
    assert ref.speed("small", "F16", "kleidiai", 8, "pp512") == TPS[("F16", "pp512", 8)]
    assert ref.speed("small", "Q4_0", "baseline", 1, "tg128d2048") == TPS[("Q4_0", "tg128d2048", 1)]


def test_threads_2_and_4_are_interpolated_log_log_between_1_and_8():
    ref = reference()
    t1, t8 = TPS[("F16", "tg128", 1)], TPS[("F16", "tg128", 8)]
    t2 = ref.speed("small", "F16", "baseline", 2, "tg128")
    t4 = ref.speed("small", "F16", "baseline", 4, "tg128")
    assert t2 == pytest.approx(t1 * (t8 / t1) ** (1 / 3))
    assert t4 == pytest.approx(t1 * (t8 / t1) ** (2 / 3))
    assert t1 < t2 < t4 < t8


def test_a_format_the_pilot_did_not_run_takes_the_slowest_pilot_formats_speed():
    ref = reference()
    # F16 is the slowest of the two pilot formats in both phases
    assert ref.speed("small", "Q8_0", "baseline", 8, "tg128") == ref.speed(
        "small", "F16", "baseline", 8, "tg128"
    )
    assert ref.speed("small", "Q4_K_M", "baseline", 1, "pp512") == TPS[("F16", "pp512", 1)]


def test_model_size_scaling_compute_bound_prefill_and_bandwidth_bound_decode():
    ref = reference()
    n_ratio = SIZES[("small", "F16")]["N_blk"] / SIZES[("large", "F16")]["N_blk"]
    w_ratio = SIZES[("small", "F16")]["W_all"] / SIZES[("large", "F16")]["W_all"]
    assert ref.speed("large", "F16", "baseline", 8, "pp512") == pytest.approx(
        TPS[("F16", "pp512", 8)] * n_ratio
    )
    assert ref.speed("large", "F16", "baseline", 8, "tg128") == pytest.approx(
        TPS[("F16", "tg128", 8)] * w_ratio
    )


def test_long_prompts_get_the_correction_the_extra_point_showed():
    recs = pilot_records(large=2.0)  # much slower than size scaling alone predicts
    est = pilot.estimate_full_sweep(recs, CFG, SIZES)
    corr = est["long_prompt_correction"]
    assert set(corr) == {"baseline", "kleidiai"} and all(0 < c < 1 for c in corr.values())
    ref = pilot._Reference(pilot.latest_records(recs), CFG, SIZES)
    ref.corr = dict(corr)
    plain = ref.speed("small", "F16", "baseline", 1, "pp512")
    long_ = ref.speed("small", "F16", "baseline", 1, "pp2048")
    assert long_ == pytest.approx(plain * corr["baseline"])
    # a correction never speeds a point up
    fast = pilot.estimate_full_sweep(pilot_records(large=1e6), CFG, SIZES)
    assert all(c == 1.0 for c in fast["long_prompt_correction"].values())


def test_the_estimate_covers_the_whole_sweep_and_grows_with_noise():
    est = pilot.estimate_full_sweep(pilot_records(), CFG, SIZES)
    assert est["full_sweep_points"] == 288 and est["pilot_calls"] == 26
    assert 0 < est["estimate_hours"] <= est["upper_bound_hours"]
    assert sum(est["hours_by_group"].values()) == pytest.approx(est["estimate_hours"])
    assert est["noisy_fraction_of_pilot"] == 0
    noisy_ids = tuple(p.config_id for pair in sweep.pairs(CFG, "pilot")[:4] for p in pair.points())
    noisy = pilot.estimate_full_sweep(pilot_records(noisy_ids=noisy_ids), CFG, SIZES)
    assert noisy["noisy_fraction_of_pilot"] == pytest.approx(8 / 26)
    assert noisy["estimate_hours"] == pytest.approx(est["estimate_hours"] * (1 + 8 / 26))


def test_a_hand_computed_call_time():
    # pp512 at 40 tok/s: one run = 12.8 s; warm-up + 5 repetitions = 6 runs
    te = sweep.parse_test("pp512")
    assert pilot._call_seconds(te, 5, 40.0, None) == pytest.approx(6 * 512 / 40.0)
    # tg128 at 25 tok/s: 5 repetitions of 5.12 s, no full warm-up
    te = sweep.parse_test("tg128")
    assert pilot._call_seconds(te, 5, 25.0, None) == pytest.approx(5 * 128 / 25.0)
    # at depth 2048 the context is filled once at the prefill speed
    te = sweep.parse_test("tg128d2048")
    assert pilot._call_seconds(te, 5, 25.0, 200.0) == pytest.approx(5 * 128 / 25.0 + 2048 / 200.0)


def test_loglog_hits_the_end_points():
    assert pilot._loglog(1, 10.0, 80.0) == pytest.approx(10.0)
    assert pilot._loglog(8, 10.0, 80.0) == pytest.approx(80.0)
    assert math.isclose(pilot._loglog(2, 10.0, 80.0), 20.0)


def test_the_markdown_summary_names_the_estimate_and_every_record():
    recs = pilot_records()
    est = pilot.estimate_full_sweep(recs, CFG, SIZES)
    md = pilot.render_markdown("S", pilot.noise_rows(recs), est)
    assert "Estimated wall time" in md and f"{est['estimate_hours']:.1f} h" in md
    assert md.count("small_F16_baseline_t1_pp512") == 1
    assert "large_F16_kleidiai_t1_pp2048" in md


def test_write_pilot_summary_next_to_the_records(tmp_path, monkeypatch):
    """The whole path: records in a folder -> _pilot_summary.md/.json, using the real tensor tables."""
    import json

    from bench import run_sweep

    monkeypatch.setattr(run_sweep, "OUT_ROOT", tmp_path)
    for rec in pilot_records():
        run_sweep.write_record(run_sweep.record_path("S", rec["config_id"], 1), rec)
    run_sweep.write_pilot_summary(CFG, "S")
    summary = json.loads((tmp_path / "S" / "_pilot_summary.json").read_text())
    assert summary["estimate"]["full_sweep_points"] == 288 and len(summary["noise"]) == 26
    assert "Repeat noise" in (tmp_path / "S" / "_pilot_summary.md").read_text()
    # the summary files are not mistaken for points
    assert len(run_sweep.load_session_records("S")) == 26


def test_an_incomplete_pilot_writes_no_summary(tmp_path, monkeypatch, capsys):
    from bench import run_sweep

    monkeypatch.setattr(run_sweep, "OUT_ROOT", tmp_path)
    rec = pilot_records()[0]
    run_sweep.write_record(run_sweep.record_path("S", rec["config_id"], 1), rec)
    run_sweep.write_pilot_summary(CFG, "S")
    assert not (tmp_path / "S" / "_pilot_summary.md").exists()
    assert "skipped" in capsys.readouterr().err
