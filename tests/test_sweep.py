"""config_id / pair_id, the sweep enumeration, build-order alternation, and the command line."""

import json

import pytest

from bench import run_sweep
from edge_llm import sweep
from tests.bench_fixtures import fake_bench_record, real_cfg


def test_config_id_and_pair_id_round_trip():
    cid = sweep.config_id("small", "Q4_K_M", "kleidiai", 8, "tg128d2048")
    assert cid == "small_Q4_K_M_kleidiai_t8_tg128d2048"
    p = sweep.parse_config_id(cid)
    assert (p.model, p.quant, p.build, p.threads, p.test) == (
        "small", "Q4_K_M", "kleidiai", 8, "tg128d2048"
    )  # fmt: skip
    assert p.config_id == cid
    # the pair id is the config id without the build: how the two builds are joined
    assert p.pair_id == "small_Q4_K_M_t8_tg128d2048"
    other = sweep.parse_config_id(cid.replace("kleidiai", "baseline"))
    assert other.pair_id == p.pair_id and other.config_id != p.config_id


@pytest.mark.parametrize(
    "bad", ["small_Q4_0_t8_pp512", "small_Q4_0_gpu_t8_pp512", "x_y_baseline_t8_zz"]
)
def test_bad_config_ids_are_rejected(bad):
    with pytest.raises(ValueError):
        sweep.parse_config_id(bad)


def test_test_names():
    assert sweep.parse_test("pp512") == sweep.Test("pp", 512)
    assert sweep.parse_test("tg128") == sweep.Test("tg", 128, 0)
    t = sweep.parse_test("tg128d2048")
    assert (t.kind, t.tokens, t.depth, t.name, t.phase) == ("tg", 128, 2048, "tg128d2048", "decode")
    assert sweep.parse_test("pp2048").phase == "prefill"
    with pytest.raises(ValueError):
        sweep.parse_test("pp128d2048")  # a depth only makes sense for decode


def test_pinning_helpers():
    assert [sweep.cpu_mask(t) for t in (1, 2, 4, 8)] == ["0x1", "0x3", "0xf", "0xff"]
    assert sweep.taskset_cpus(1) == "0-0" and sweep.taskset_cpus(8) == "0-7"


def test_build_order_alternates_every_pair():
    orders = [sweep.build_order(i) for i in range(6)]
    assert orders[0] == ("baseline", "kleidiai") and orders[1] == ("kleidiai", "baseline")
    assert all(orders[i] != orders[i + 1] for i in range(5))
    assert all(set(o) == {"baseline", "kleidiai"} for o in orders)


def test_pair_points_follow_the_alternating_order():
    cfg = real_cfg()
    ps = sweep.pairs(cfg, "full")
    first_builds = [p.points()[0].build for p in ps[:6]]
    assert first_builds == ["baseline", "kleidiai"] * 3
    assert {x.pair_id for x in ps[0].points()} == {ps[0].pair_id}


def test_the_full_sweep_has_144_points_all_of_the_small_model():
    cfg = real_cfg()
    ps = sweep.pairs(cfg, "full")
    # 1 model (ADR-024) x 4 formats x 4 thread counts x 4 tests, plus decode at depth for t in {1, 8}
    assert len(ps) * 2 == 4 * 4 * 4 * 2 + 4 * 2 * 2 == 144
    assert {p.model for p in ps} == {"small"}
    ids = [p.config_id for pair in ps for p in pair.points()]
    assert len(set(ids)) == len(ids)
    depth = [p for p in ps if "d2048" in p.test]
    assert {p.threads for p in depth} == {1, 8}


def test_the_pilot_is_the_small_model_plus_the_slowest_point():
    cfg = real_cfg()
    ps = sweep.pairs(cfg, "pilot")
    assert len(ps) == 2 * 2 * 3 + 1
    assert {p.model for p in ps[:-1]} == {"small"} and {p.quant for p in ps[:-1]} == {"F16", "Q4_0"}
    assert {p.threads for p in ps[:-1]} == {1, 8}
    last = ps[-1]
    assert (last.model, last.quant, last.threads, last.test) == ("large", "F16", 1, "pp2048")
    # every small-model pilot point is a point of the full sweep, so the timings carry over; the
    # large-model point stays in the pilot as evidence but is not in the full sweep (ADR-024)
    full = {p.pair_id for p in sweep.pairs(cfg, "full")}
    assert {p.pair_id for p in ps[:-1]} <= full
    assert last.pair_id not in full


def test_slow_points_get_fewer_repetitions():
    cfg = real_cfg()
    ps = {p.pair_id: p for p in sweep.pairs(cfg, "full")}
    assert sweep.repetitions(cfg, ps["small_F16_t1_pp512"]) == 5  # none listed on Day 4
    cfg["slow_points"] = [{"point": "small_F16_t1_pp2048", "reason": "test"}]
    assert sweep.repetitions(cfg, ps["small_F16_t1_pp2048"]) == 3
    assert sweep.repetitions(cfg, ps["small_F16_t1_pp512"]) == 5


def test_unknown_sets_and_points_are_rejected():
    cfg = real_cfg()
    with pytest.raises(ValueError):
        sweep.pairs(cfg, "tiny")
    cfg["pilot"]["extra_points"] = [{"model": "huge", "quant": "F16", "threads": 1, "test": "pp1"}]
    with pytest.raises(ValueError):
        sweep.pairs(cfg, "pilot")


# --- the command line (ADR-014, ADR-019) -----------------------------------------------------


def command(test, threads, build="kleidiai"):
    cfg = real_cfg()
    p = sweep.Point("small", "Q4_0", build, threads, test)
    return run_sweep.bench_command(cfg, p, "/m/small_Q4_0.gguf", 5, "/b/llama-bench")


def option(cmd, flag):
    return cmd[cmd.index(flag) + 1]


def test_command_writes_out_the_fixed_settings_and_the_pinning():
    cmd = command("pp512", 4)
    assert cmd[:3] == ["taskset", "-c", "0-3"]
    assert option(cmd, "-t") == "4" and option(cmd, "-C") == "0xf"
    assert option(cmd, "--cpu-strict") == "1"
    for flag, value in [("-b", "2048"), ("-ub", "512"), ("-ctk", "f16"), ("-ctv", "f16"),
                        ("-fa", "1"), ("-lm", "auto"), ("--repack", "1"), ("-r", "5"),
                        ("-o", "json")]:  # fmt: skip
        assert option(cmd, flag) == value
    assert "--no-warmup" not in cmd  # the one unmeasured warm-up stays on


def test_command_selects_the_test():
    pp = command("pp2048", 1)
    assert (option(pp, "-p"), option(pp, "-n"), option(pp, "-d")) == ("2048", "0", "0")
    tg = command("tg128", 8)
    assert (option(tg, "-p"), option(tg, "-n"), option(tg, "-d")) == ("0", "128", "0")
    deep = command("tg128d2048", 8)
    assert (option(deep, "-p"), option(deep, "-n"), option(deep, "-d")) == ("0", "128", "2048")


def test_both_builds_get_the_same_command_except_the_binary():
    a, b = command("pp512", 8, "baseline"), command("pp512", 8, "kleidiai")
    assert a == b  # the binary path is a parameter of the caller, not of the build name


# --- skipping, re-running and never overwriting ----------------------------------------------


@pytest.fixture
def out_root(tmp_path, monkeypatch):
    monkeypatch.setattr(run_sweep, "OUT_ROOT", tmp_path / "bench")
    return tmp_path / "bench"


def test_status_and_paths(out_root):
    cid = "small_F16_baseline_t1_pp512"
    assert run_sweep.status("S", cid) == "todo"
    assert run_sweep.record_path("S", cid, 1).name == f"{cid}.json"
    assert run_sweep.record_path("S", cid, 2).name == f"{cid}__2.json"
    run_sweep.write_record(run_sweep.record_path("S", cid, 1), {"noisy": False})
    assert run_sweep.status("S", cid) == "done"


def test_a_noisy_first_run_asks_for_exactly_one_rerun(out_root):
    cid = "small_F16_baseline_t1_pp512"
    run_sweep.write_record(run_sweep.record_path("S", cid, 1), {"noisy": True})
    assert run_sweep.status("S", cid) == "rerun"
    run_sweep.write_record(run_sweep.record_path("S", cid, 2), {"noisy": True})
    assert (
        run_sweep.status("S", cid) == "done"
    )  # a second noisy run is kept and labelled, not repeated


def test_write_record_never_overwrites(out_root):
    path = run_sweep.record_path("S", "small_F16_baseline_t1_pp512", 1)
    run_sweep.write_record(path, {"a": 1})
    with pytest.raises(FileExistsError):
        run_sweep.write_record(path, {"a": 2})
    assert json.loads(path.read_text()) == {"a": 1}


def test_a_write_cut_off_midway_leaves_no_record_and_the_resume_redoes_the_point(out_root):
    cid = "small_F16_baseline_t1_pp512"
    path = run_sweep.record_path("S", cid, 1)
    # what a crash leaves behind: a half-written temporary file, never a half-written record
    path.parent.mkdir(parents=True)
    path.with_name(f".{path.name}.tmp").write_text('{"noisy": fal')
    assert not path.exists() and run_sweep.status("S", cid) == "todo"
    run_sweep.write_record(path, {"noisy": False})
    assert json.loads(path.read_text()) == {"noisy": False}
    assert sorted(p.name for p in path.parent.iterdir()) == [path.name]  # the temporary is gone


def fake_run_call(script, calls):
    """A run_call that returns scripted noisy flags and records the order of the calls."""

    def run_call(cfg, session_id, point, pair, attempt, repetitions, context):
        calls.append((point.build, attempt))
        noisy = script.get((point.build, attempt), False)
        rec = fake_bench_record(
            point.config_id, noisy=noisy, attempt=attempt, pair_index=pair.index
        )
        return rec

    return run_call


def test_run_pair_runs_builds_back_to_back_in_the_alternating_order(out_root, monkeypatch):
    cfg = real_cfg()
    pairs = sweep.pairs(cfg, "full")
    calls: list = []
    monkeypatch.setattr(run_sweep, "run_call", fake_run_call({}, calls))
    run_sweep.run_pair(cfg, "S", pairs[0], {})
    run_sweep.run_pair(cfg, "S", pairs[1], {})
    assert calls == [("baseline", 1), ("kleidiai", 1), ("kleidiai", 1), ("baseline", 1)]


def test_run_pair_reruns_a_noisy_point_once_after_its_pair(out_root, monkeypatch):
    cfg = real_cfg()
    pair = sweep.pairs(cfg, "full")[0]
    calls: list = []
    monkeypatch.setattr(run_sweep, "run_call", fake_run_call({("baseline", 1): True}, calls))
    run_sweep.run_pair(cfg, "S", pair, {})
    assert calls == [("baseline", 1), ("kleidiai", 1), ("baseline", 2)]
    names = sorted(p.name for p in (out_root / "S").iterdir())
    assert names == [
        "small_F16_baseline_t1_pp128.json",
        "small_F16_baseline_t1_pp128__2.json",
        "small_F16_kleidiai_t1_pp128.json",
    ]


def test_a_crashed_run_resumes_without_repeating_or_overwriting(out_root, monkeypatch):
    cfg = real_cfg()
    pair = sweep.pairs(cfg, "full")[0]
    calls: list = []
    monkeypatch.setattr(run_sweep, "run_call", fake_run_call({}, calls))
    # only the baseline half of the pair was written before the crash
    first = pair.points()[0]
    run_sweep.write_record(
        run_sweep.record_path("S", first.config_id, 1), {"noisy": False, "marker": "kept"}
    )
    run_sweep.run_pair(cfg, "S", pair, {})
    assert calls == [("kleidiai", 1)]
    kept = json.loads(run_sweep.record_path("S", first.config_id, 1).read_text())
    assert kept["marker"] == "kept"
    run_sweep.run_pair(cfg, "S", pair, {})
    assert calls == [("kleidiai", 1)]  # nothing left to do
