"""analyse.py on synthetic records and hand-worked numbers (no hardware), plus the real session.

Known answers are worked by hand in the comments; the real-data tests pin numbers that CLAUDE.md
§11 and the Progress Log already record.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from edge_llm import analyse, sweep
from edge_llm.schema import SchemaError
from tests.bench_fixtures import fake_bench_record

CLEAN = [100.0, 100.1, 99.9, 100.0, 100.0]  # IQR/median 0.1 %
NOISY = [80.0, 90.0, 100.0, 110.0, 120.0]  # IQR/median 20 %


# --- the re-run rule (CLAUDE.md §7.4) -------------------------------------------------------


def test_a_clean_first_attempt_is_used_even_if_a_second_exists():
    assert analyse.apply_rerun_rule({1: CLEAN, 2: NOISY}) == (1, False)


def test_a_noisy_first_attempt_gives_way_to_a_clean_second():
    assert analyse.apply_rerun_rule({1: NOISY, 2: CLEAN}) == (2, False)


def test_two_noisy_attempts_keep_the_second_and_flag_it():
    assert analyse.apply_rerun_rule({1: NOISY, 2: NOISY}) == (2, True)


def test_a_noisy_point_that_was_never_rerun_is_flagged():
    assert analyse.apply_rerun_rule({1: NOISY}) == (1, True)


def test_a_rerun_without_a_first_attempt_is_an_error():
    with pytest.raises(ValueError, match="no first attempt"):
        analyse.apply_rerun_rule({2: CLEAN})


# --- synthetic sessions on disk -------------------------------------------------------------


def write_record(folder: Path, config_id: str, attempt: int = 1, **kw) -> None:
    rec = fake_bench_record(config_id, attempt=attempt, **kw)
    name = f"{config_id}__2.json" if attempt == 2 else f"{config_id}.json"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(rec))


def fake_prediction(config_id: str, **kw) -> dict:
    """A v1.csv row with round numbers: decode, 1 GB and 2 GFLOP per token."""
    p = sweep.parse_config_id(config_id)
    te = sweep.parse_test(p.test)
    row = {
        "config_id": config_id, "pair_id": p.pair_id, "model": p.model, "quant": p.quant,
        "build": p.build, "threads": p.threads, "test": p.test, "phase": te.phase,
        "prompt_tokens": te.tokens if te.kind == "pp" else 0, "gen_tokens": 0, "depth": te.depth,
        "bytes": 1e9, "weight_flops": 2e9, "attention_flops": 0.5e9,
        "B": 100e9, "B1": 80e9, "C_weight_class": "sdot", "C_weight": 400e9, "C_attn": 50e9,
        "t_memory": 0.01, "t_compute": 0.005, "predicted_tps": 100.0, "binding": "memory",
        "C_weight_class_sustained": "sdot", "C_weight_sustained": 200e9,
        "C_attn_sustained": 25e9, "t_compute_sustained": 0.01, "predicted_tps_sustained": 100.0,
        "binding_sustained": "memory",
    }  # fmt: skip
    row.update(kw)
    return row


def points_for(tmp_path: Path, cid: str, attempts: dict[int, dict], **pred) -> dict:
    """Write the given attempts of one point, run build_points, return its single row."""
    folder = tmp_path / "bench"
    for attempt, kw in attempts.items():
        write_record(folder, cid, attempt, **kw)
    found = analyse.load_bench_session(folder, "S")
    rows = analyse.build_points(
        found, {cid: fake_prediction(cid, **pred)}, {1: 100e9, 8: 100e9}, tmp_path
    )
    assert len(rows) == 1
    return rows[0]


def test_median_iqr_and_ratio_come_from_the_samples(tmp_path):
    # fake samples at tps = 100 are 99.92, 99.96, 100, 100.04, 100.08 -> Q1 99.96, Q3 100.04
    row = points_for(tmp_path, "small_Q4_0_baseline_t1_tg128", {1: {"tps": 100.0}})
    assert row["measured_median"] == pytest.approx(100.0)
    assert (row["q1"], row["q3"]) == pytest.approx((99.96, 100.04))
    assert row["iqr"] == pytest.approx(0.08)
    assert row["ratio"] == pytest.approx(1.0)  # 100 measured / 100 predicted
    assert row["ratio_sustained"] == pytest.approx(1.0)
    assert (row["attempt_used"], row["noisy_first_attempt"], row["still_noisy"]) == (
        1,
        False,
        False,
    )
    assert row["source_file"] == "bench/small_Q4_0_baseline_t1_tg128.json"


def test_a_noisy_point_uses_its_rerun_and_says_so(tmp_path):
    row = points_for(
        tmp_path,
        "small_Q4_0_baseline_t1_tg128",
        {1: {"tps": 50.0, "noisy": True}, 2: {"tps": 100.0}},
    )
    assert row["attempt_used"] == 2
    assert row["measured_median"] == pytest.approx(100.0)
    assert row["noisy_first_attempt"] is True and row["still_noisy"] is False
    assert row["source_file"].endswith("__2.json")


def test_two_noisy_attempts_are_kept_and_labelled(tmp_path):
    row = points_for(
        tmp_path,
        "small_Q4_0_baseline_t1_tg128",
        {1: {"tps": 50.0, "noisy": True}, 2: {"tps": 60.0, "noisy": True}},
    )
    assert (row["attempt_used"], row["still_noisy"]) == (2, True)
    assert row["measured_median"] == pytest.approx(60.0)


def test_a_bad_record_stops_the_load(tmp_path):
    write_record(tmp_path, "small_Q4_0_baseline_t1_tg128")
    path = tmp_path / "small_Q4_0_baseline_t1_tg128.json"
    rec = json.loads(path.read_text())
    rec["returncode"] = 1
    path.write_text(json.dumps(rec))
    with pytest.raises(SchemaError, match="exited with 1"):
        analyse.load_bench_session(tmp_path, "S")


def test_a_rerun_file_must_hold_attempt_2_and_the_right_session(tmp_path):
    write_record(tmp_path, "small_Q4_0_baseline_t1_tg128", attempt=1)
    (tmp_path / "small_Q4_0_baseline_t1_tg128.json").rename(
        tmp_path / "small_Q4_0_baseline_t1_tg128__2.json"
    )
    with pytest.raises(ValueError, match="attempt 1"):
        analyse.load_bench_session(tmp_path, "S")
    (tmp_path / "small_Q4_0_baseline_t1_tg128__2.json").unlink()
    write_record(tmp_path, "small_Q4_0_baseline_t1_tg128")
    with pytest.raises(ValueError, match="not OTHER"):
        analyse.load_bench_session(tmp_path, "OTHER")


def test_underscore_files_are_not_points(tmp_path):
    write_record(tmp_path, "small_Q4_0_baseline_t1_tg128")
    (tmp_path / "_pilot_summary.json").write_text("{}")
    assert list(analyse.load_bench_session(tmp_path, "S")) == ["small_Q4_0_baseline_t1_tg128"]


# --- the join -------------------------------------------------------------------------------


def test_join_fails_loudly_on_a_missing_prediction_or_measurement(tmp_path):
    cid = "small_Q4_0_baseline_t1_tg128"
    write_record(tmp_path, cid)
    found = analyse.load_bench_session(tmp_path, "S")
    other = "small_Q4_0_kleidiai_t1_tg128"
    with pytest.raises(ValueError, match="1 predicted points with no measurement"):
        analyse.build_points(
            found, {cid: fake_prediction(cid), other: fake_prediction(other)}, {1: 1e11}, tmp_path
        )
    with pytest.raises(ValueError, match="1 measured points with no prediction"):
        analyse.build_points(found, {}, {1: 1e11}, tmp_path)


def test_a_prediction_for_a_different_point_is_refused(tmp_path):
    cid = "small_Q4_0_baseline_t1_tg128"
    write_record(tmp_path, cid)
    found = analyse.load_bench_session(tmp_path, "S")
    wrong = fake_prediction(cid, quant="Q8_0")
    with pytest.raises(ValueError, match="different point"):
        analyse.build_points(found, {cid: wrong}, {1: 1e11}, tmp_path)


# --- KleidiAI speed-up ----------------------------------------------------------------------


def test_speedup_range_pairs_the_worst_case_with_the_best_case():
    # baseline Q1/median/Q3 = 90/100/110, kleidiai = 108/120/132:
    # speedup 120/100 = 1.2; lo = 108/110; hi = 132/90
    s, lo, hi = analyse.speedup_range((90, 100, 110), (108, 120, 132))
    assert s == pytest.approx(1.2)
    assert lo == pytest.approx(108 / 110)
    assert hi == pytest.approx(132 / 90)
    assert lo <= s <= hi


def test_kleidiai_table_has_one_row_per_pair(tmp_path):
    cids = [
        "small_Q4_0_baseline_t1_tg128",
        "small_Q4_0_kleidiai_t1_tg128",
        "small_F16_baseline_t1_tg128",
        "small_F16_kleidiai_t1_tg128",
    ]
    folder = tmp_path / "bench"
    for cid, tps in zip(cids, (100.0, 120.0, 50.0, 50.0)):
        write_record(folder, cid, tps=tps)
    found = analyse.load_bench_session(folder, "S")
    points = analyse.build_points(found, {c: fake_prediction(c) for c in cids}, {1: 1e11}, tmp_path)
    pairs = analyse.build_kleidiai(points)
    assert [p["pair_id"] for p in pairs] == ["small_F16_t1_tg128", "small_Q4_0_t1_tg128"]
    f16, q4 = pairs
    assert f16["speedup"] == pytest.approx(1.0) and f16["coverage"].startswith("none")
    assert q4["speedup"] == pytest.approx(1.2) and q4["coverage"] == "full"
    assert q4["baseline_median"] == pytest.approx(100.0)
    assert q4["speedup_lo"] <= q4["speedup"] <= q4["speedup_hi"]
    with pytest.raises(ValueError, match="needs both builds"):
        analyse.build_kleidiai([p for p in points if p["config_id"] != cids[1]])


# --- achieved rates and the session-B sensitivity -------------------------------------------


def test_achieved_rates_of_a_decode_point_by_hand():
    # 1 GB per token at 100 tokens/s = 100 GB/s, half of B = 200 GB/s.
    # (2 + 0.5) GFLOP per token x 100 = 250 GOPS; weights alone 200 GOPS = half of C = 400 GOPS.
    row = fake_prediction("small_Q4_0_baseline_t1_tg128", B=200e9, C_weight=400e9)
    r = analyse.achieved_rates(row, 100.0)
    assert r["achieved_GBps"] == pytest.approx(100.0)
    assert r["fraction_of_B"] == pytest.approx(0.5)
    assert r["fraction_of_C"] == pytest.approx(0.5)
    assert r["fraction_of_C_sustained"] == pytest.approx(1.0)  # 200 GOPS of 200 GOPS sustained


def test_achieved_rates_of_a_prefill_point_spread_over_the_prompt():
    # The prompt's 1 GB is read once for 512 tokens: at 256 tokens/s the prompt takes 2 s,
    # so 0.5 GB/s; (2 + 0.5) GFLOP in 2 s = 1.25 GOPS.
    row = fake_prediction("small_Q4_0_baseline_t1_pp512")
    r = analyse.achieved_rates(row, 256.0)
    assert r["achieved_GBps"] == pytest.approx(0.5)
    assert r["achieved_GOPS"] == pytest.approx(1.25)


def test_session_prediction_changes_only_the_memory_term():
    row = fake_prediction("small_Q4_0_baseline_t1_tg128")  # t_compute 0.005 s
    assert analyse.session_prediction(row, 100e9) == pytest.approx(100.0)  # memory 0.01 s
    assert analyse.session_prediction(row, 400e9) == pytest.approx(200.0)  # compute-bound now
    row = fake_prediction("small_Q4_0_baseline_t1_pp512", t_compute=2.0)
    assert analyse.session_prediction(row, 100e9) == pytest.approx(256.0)  # 512 tokens / 2 s


def test_summary_warns_about_every_ratio_above_one(tmp_path):
    cid = "small_Q4_0_baseline_t1_tg128"
    row = points_for(tmp_path, cid, {1: {"tps": 150.0}})  # 150 measured vs 100 predicted
    text = "\n".join(analyse.summary_lines([row]))
    assert f"WARNING ratio = 1.500 > 1: {cid}" in text
    row = points_for(tmp_path / "x", cid, {1: {"tps": 50.0}})
    assert "WARNING" not in "\n".join(analyse.summary_lines([row]))


# --- the real session -----------------------------------------------------------------------


@pytest.fixture(scope="module")
def real(tmp_path_factory):
    out = tmp_path_factory.mktemp("processed")
    points, pairs, bw = analyse.run(out_dir=out)
    return out, points, pairs, bw


def test_the_real_session_has_144_points_and_72_pairs(real):
    _, points, pairs, _ = real
    assert len(points) == 144 and len(pairs) == 72
    assert [p["config_id"] for p in points] == sorted(p["config_id"] for p in points)
    assert sum(p["attempt_used"] == 2 for p in points) == 6  # the six noisy t = 8 re-runs
    assert not any(p["still_noisy"] for p in points)


def test_the_real_session_bandwidth_matches_the_progress_log(real):
    *_, bw = real
    at8 = next(r for r in bw if r["threads"] == 8)
    assert at8["start_GBps"] == pytest.approx(254.51, abs=0.005)
    assert at8["end_GBps"] == pytest.approx(254.45, abs=0.005)
    assert max(abs(r["drift_pct"]) for r in bw) < 1.7  # "drift <= 1.6 %"
    assert at8["session_over_v1"] == pytest.approx(254.48 / 237.23, abs=0.001)  # "7 % above v1"


def test_the_committed_tables_are_what_the_code_gives(real):
    out, *_ = real
    committed = Path(__file__).resolve().parents[1] / "results" / "processed"
    for name in ("points.csv", "kleidiai.csv", "session_bandwidth.csv"):
        assert (committed / name).read_bytes() == (out / name).read_bytes(), name


def test_f16_is_a_negative_control_in_the_real_pairs(real):
    _, _, pairs, _ = real
    f16 = [p["speedup"] for p in pairs if p["quant"] == "F16"]
    assert len(f16) == 18 and all(math.isclose(s, 1.0, abs_tol=0.02) for s in f16)


def test_analyse_has_one_writer_and_it_writes_csv_only():
    src = (Path(__file__).resolve().parents[1] / "src" / "edge_llm" / "analyse.py").read_text(
        encoding="utf8"
    )
    assert "write_text" not in src and "write_bytes" not in src
    assert src.count('"w"') == 1  # write_csv; every output goes through it
