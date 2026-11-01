"""BenchRecord: what must be true of a stored llama-bench call; median/IQR/noisy on synthetic data."""

import copy
import json

import pytest

from bench import run_sweep
from edge_llm.schema import BenchRecord, SchemaError
from edge_llm.stats import NOISY_THRESHOLD, is_noisy, summarise
from tests.bench_fixtures import fake_bench_record

CID = "small_Q4_0_kleidiai_t8_pp512"


def test_a_good_record_validates_and_round_trips():
    rec = fake_bench_record(CID)
    again = BenchRecord.from_dict(json.loads(json.dumps(rec)))
    assert again.config_id == CID and again.pair_id == "small_Q4_0_t8_pp512"
    assert again.to_dict()["llama_bench"] == rec["llama_bench"]  # llama-bench's output unchanged


def test_unknown_or_missing_fields_are_rejected():
    rec = fake_bench_record(CID)
    rec["extra"] = 1
    with pytest.raises(SchemaError, match="unknown keys"):
        BenchRecord.from_dict(rec)
    rec = fake_bench_record(CID)
    del rec["noisy"]
    with pytest.raises(SchemaError, match="missing keys"):
        BenchRecord.from_dict(rec)


def mutate(path, value):
    rec = fake_bench_record(CID)
    target = rec
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return rec


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("config_id",), "small_Q4_0_baseline_t8_pp512", "does not match its own fields"),
        (("pair_id",), "small_Q4_0_t1_pp512", "pair_id"),
        (("returncode",), 1, "exited"),
        (("attempt",), 3, "attempt"),
        (("model", "sha256"), "xyz", "sha256"),
        (("model", "table_file_bytes"), 1, "tensor table"),
        (("llama_bench", 0, "n_prompt"), 128, "different test"),
        (("llama_bench", 0, "n_depth"), 2048, "different test"),
        (("llama_bench", 0, "n_threads"), 4, "thread count"),
        (("llama_bench", 0, "flash_attn"), 0, "-fa"),
        (("llama_bench", 0, "cpu_strict"), False, "cpu-strict"),
        (("llama_bench", 0, "n_ubatch"), 256, "n_ubatch"),
        (("llama_bench", 0, "samples_ts"), [1.0, 2.0], "5 repetitions"),
        (("summary", "median"), 1.0, "summary.median"),
        (("noisy",), True, "noisy flag"),
    ],
)
def test_bad_records_are_rejected(path, value, message):
    rec = fake_bench_record(CID)
    target = rec
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(SchemaError, match=message):
        BenchRecord.from_dict(rec)


def test_a_depth_test_must_report_its_depth():
    cid = "small_Q4_0_kleidiai_t8_tg128d2048"
    rec = fake_bench_record(cid)
    BenchRecord.from_dict(rec)
    bad = copy.deepcopy(rec)
    bad["llama_bench"][0]["n_depth"] = 0
    with pytest.raises(SchemaError, match="different test"):
        BenchRecord.from_dict(bad)


def test_a_noisy_record_is_flagged_not_rejected():
    rec = fake_bench_record(CID, noisy=True)
    assert BenchRecord.from_dict(rec).noisy is True


def test_order_in_pair_follows_the_pair_index():
    first = fake_bench_record("small_F16_baseline_t1_pp512", pair_index=0)
    second = fake_bench_record("small_F16_kleidiai_t1_pp512", pair_index=0)
    assert (first["order_in_pair"], second["order_in_pair"]) == (1, 2)
    flipped = fake_bench_record("small_F16_baseline_t1_pp512", pair_index=1)
    assert flipped["order_in_pair"] == 2


# --- median, IQR and the noisy rule on synthetic samples -------------------------------------


def test_median_and_iqr_of_known_samples():
    s = summarise([10.0, 11.0, 12.0, 13.0, 14.0])
    assert s["median"] == 12.0 and s["q1"] == 11.0 and s["q3"] == 13.0 and s["iqr"] == 2.0
    assert s["iqr_over_median"] == pytest.approx(2.0 / 12.0)


def test_the_noisy_rule_is_iqr_over_median_above_five_percent():
    quiet = [100.0, 101.0, 102.0, 103.0, 104.0]  # IQR 2, median 102: 2 %
    assert not is_noisy(quiet)
    loud = [90.0, 95.0, 100.0, 105.0, 110.0]  # IQR 10, median 100: 10 %
    assert is_noisy(loud)
    assert NOISY_THRESHOLD == 0.05
    edge = [95.0, 97.5, 100.0, 102.5, 105.0]  # IQR 5, median 100: exactly 5 %, not above
    assert not is_noisy(edge)


def test_the_summary_comes_from_the_repetitions_not_llama_benchs_mean():
    samples = [100.0, 100.0, 100.0, 100.0, 200.0]  # mean 120, median 100
    assert summarise(samples)["median"] == 100.0


# --- the model file check ----------------------------------------------------------------------


def test_model_info_checks_hash_and_size(tmp_path, monkeypatch):
    models = tmp_path / "work" / "models"
    models.mkdir(parents=True)
    (models / "small_Q4_0.gguf").write_bytes(b"x" * 100)
    (models / "SHA256SUMS").write_text(f"{'c' * 64}  small_Q4_0.gguf\n")
    results = tmp_path / "results"
    (results / "models").mkdir(parents=True)
    table = {"sha256": "c" * 64, "file_bytes": 100}
    (results / "models" / "small_Q4_0.json").write_text(json.dumps(table))
    monkeypatch.setattr(run_sweep.common, "RESULTS_DIR", results)
    info = run_sweep.model_info("small", "Q4_0", models)
    assert info["sha256"] == "c" * 64 and info["file_bytes"] == info["table_file_bytes"] == 100

    (results / "models" / "small_Q4_0.json").write_text(json.dumps({**table, "file_bytes": 99}))
    with pytest.raises(SystemExit, match="tensor table says 99"):
        run_sweep.model_info("small", "Q4_0", models)
    (results / "models" / "small_Q4_0.json").write_text(json.dumps({**table, "sha256": "d" * 64}))
    with pytest.raises(SystemExit, match="SHA256SUMS differs"):
        run_sweep.model_info("small", "Q4_0", models)
