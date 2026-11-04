"""Day 8 investigation: Check A tables and speed-ups, Check B arithmetic, Check C parsing.

No hardware: synthetic records on disk, a tiny GGUF written by the test, and the committed
results/processed/kleidiai.csv for the real Check B numbers.
"""

import csv
import json
import math
import subprocess
from pathlib import Path

import pytest

from bench import day8 as bench_day8
from edge_llm import day8, gguf_table, sweep
from tests.bench_fixtures import fake_bench_record
from tests.test_gguf_table import SHA, write_tiny

REPO = Path(__file__).resolve().parents[1]
KLEIDIAI_CSV = REPO / "results" / "processed" / "kleidiai.csv"

# --- Check B ----------------------------------------------------------------------------------

KL_COLUMNS = [
    "pair_id", "quant", "threads", "test", "baseline_median", "baseline_q1", "baseline_q3",
    "kleidiai_median", "kleidiai_q1", "kleidiai_q3", "speedup",
]  # fmt: skip


def kl_row(quant, threads, p, tb, tk):
    """A kleidiai.csv row for a prompt that takes tb seconds (baseline) and tk (kleidiai)."""
    b, k = p / tb, p / tk
    return {
        "pair_id": f"small_{quant}_t{threads}_pp{p}", "quant": quant, "threads": threads,
        "test": f"pp{p}", "baseline_median": b, "baseline_q1": b, "baseline_q3": b,
        "kleidiai_median": k, "kleidiai_q1": k, "kleidiai_q3": k, "speedup": k / b,
    }  # fmt: skip


def write_kl_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KL_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def test_delta_t_by_hand():
    # 100 tokens at 100 tok/s = 1.0 s; at 125 tok/s = 0.8 s: KleidiAI saves 0.2 s (2 ms/token)
    kl = {
        "baseline_median": 100, "baseline_q1": 90, "baseline_q3": 110,
        "kleidiai_median": 125, "kleidiai_q1": 110, "kleidiai_q3": 140, "speedup": 1.25,
    }  # fmt: skip
    r = day8.delta_t_row("Q8_0", 1, 100, kl)
    assert r["t_baseline_s"] == pytest.approx(1.0)
    assert r["t_kleidiai_s"] == pytest.approx(0.8)
    assert r["delta_t_s"] == pytest.approx(0.2)
    assert r["delta_ms_per_token"] == pytest.approx(2.0)
    # range: lo = P/b_q3 - P/k_q1 = 100/110 - 100/110 = 0; hi = P/b_q1 - P/k_q3 = 100/90 - 100/140
    assert r["delta_t_lo_s"] == pytest.approx(0.0, abs=1e-12)
    assert r["delta_t_hi_s"] == pytest.approx(100 / 90 - 100 / 140)


def test_linear_fit_recovers_a_line():
    a, b = day8.linear_fit([128.0, 512.0, 2048.0], [0.5 + 0.002 * p for p in (128, 512, 2048)])
    assert (a, b) == (pytest.approx(0.5), pytest.approx(0.002))


def test_fixed_cost_and_per_token_difference_are_told_apart(tmp_path):
    ps = day8.PREFILL_LENGTHS
    rows = []
    # Q4_0: KleidiAI saves a fixed 0.5 s per call, whatever P is
    for p in ps:
        tb = 1.0 + p / 100
        rows.append(kl_row("Q4_0", 1, p, tb, tb - 0.5))
    # Q8_0: KleidiAI saves 2 ms per token (a quarter of a 8 ms/token baseline)
    for p in ps:
        rows.append(kl_row("Q8_0", 1, p, p * 0.008, p * 0.006))
    write_kl_csv(tmp_path / "kleidiai.csv", rows)
    _rows, fits = day8.check_b(tmp_path / "kleidiai.csv")
    fixed, per_token = fits  # sorted by quant: Q4_0, Q8_0
    assert fixed["quant"] == "Q4_0" and per_token["quant"] == "Q8_0"
    assert fixed["growth_2048_over_128"] == pytest.approx(1.0)
    assert fixed["fixed_s"] == pytest.approx(0.5) and fixed["per_token_ms"] == pytest.approx(0.0)
    assert per_token["growth_2048_over_128"] == pytest.approx(16.0)
    assert per_token["fixed_s"] == pytest.approx(0.0, abs=1e-9)
    assert per_token["per_token_ms"] == pytest.approx(2.0)
    assert per_token["per_token_ms_max_over_min"] == pytest.approx(1.0)
    assert not fixed["sign_changes"] and not per_token["sign_changes"]


def test_growth_is_not_reported_when_delta_t_changes_sign(tmp_path):
    rows = [
        kl_row("Q4_0", 8, 128, 1.0, 1.1),  # KleidiAI slower
        kl_row("Q4_0", 8, 512, 4.0, 3.9),  # faster
        kl_row("Q4_0", 8, 2048, 16.0, 16.5),  # slower
    ]
    write_kl_csv(tmp_path / "kleidiai.csv", rows)
    _rows, fits = day8.check_b(tmp_path / "kleidiai.csv")
    assert fits[0]["sign_changes"] is True
    assert math.isnan(fits[0]["growth_2048_over_128"])


def test_check_b_ignores_other_formats_and_decode(tmp_path):
    rows = [kl_row("Q4_0", 1, p, p * 0.01, p * 0.011) for p in day8.PREFILL_LENGTHS]
    other = kl_row("F16", 1, 128, 1.0, 1.0)
    decode = {**kl_row("Q4_0", 1, 128, 1.0, 1.0), "test": "tg128"}
    write_kl_csv(tmp_path / "kleidiai.csv", [*rows, other, decode])
    out, fits = day8.check_b(tmp_path / "kleidiai.csv")
    assert len(out) == 3 and len(fits) == 1


def test_check_b_needs_all_three_prompt_lengths(tmp_path):
    write_kl_csv(tmp_path / "kleidiai.csv", [kl_row("Q4_0", 1, 128, 1.0, 1.1)])
    with pytest.raises(ValueError, match="prompt lengths"):
        day8.check_b(tmp_path / "kleidiai.csv")


def test_real_check_b_numbers():
    """Pinned to the committed sweep tables (the numbers quoted in the Day 8 report)."""
    rows, fits = day8.check_b(KLEIDIAI_CSV)
    assert len(rows) == 24 and len(fits) == 8
    by = {(r["quant"], r["threads"], r["prompt_tokens"]): r for r in rows}
    assert by[("Q4_0", 1, 128)]["delta_t_s"] == pytest.approx(-0.0620, abs=1e-4)
    assert by[("Q8_0", 1, 128)]["delta_t_s"] == pytest.approx(0.3447, abs=1e-4)
    assert by[("Q8_0", 1, 2048)]["delta_t_s"] == pytest.approx(5.3655, abs=1e-4)
    fit = {(f["quant"], f["threads"]): f for f in fits}
    assert fit[("Q8_0", 1)]["growth_2048_over_128"] == pytest.approx(15.56, abs=0.01)
    assert fit[("Q4_0", 8)]["sign_changes"] is True


def test_main_writes_only_processed_tables(tmp_path):
    (tmp_path / "results" / "processed").mkdir(parents=True)
    (tmp_path / "results" / "processed" / "kleidiai.csv").write_text(KLEIDIAI_CSV.read_text())
    assert day8.main(["--root", str(tmp_path)]) == 0
    written = sorted(p.name for p in (tmp_path / "results").rglob("*") if p.is_file())
    assert written == ["day8_check_b.csv", "day8_check_b_fit.csv", "kleidiai.csv"]


# --- Check A: the variants' tensor tables -----------------------------------------------------


def tensor(name, qtype, shape):
    return {"name": name, "type": qtype, "shape": shape}


def table(output_type="Q6_K", **overrides):
    tensors = {
        "token_embd.weight": tensor("token_embd.weight", "Q4_0", [1024, 4096]),
        "output.weight": tensor("output.weight", output_type, [1024, 4096]),
        "blk.0.ffn_up.weight": tensor("blk.0.ffn_up.weight", "Q4_0", [1024, 3072]),
        "blk.0.attn_norm.weight": tensor("blk.0.attn_norm.weight", "F32", [1024]),
    }
    tensors.update(overrides)
    return {"tensors": list(tensors.values())}


def test_variant_table_accepts_only_the_output_layer_changed():
    ref = table("Q6_K")
    assert day8.check_variant_table(table("Q8_0"), ref, "Q8_0") == []
    assert day8.check_variant_table(table("Q4_0"), ref, "Q4_0") == []
    assert day8.check_variant_table(ref, ref, "Q6_K") == []


def test_variant_table_rejects_wrong_output_type():
    problems = day8.check_variant_table(table("Q6_K"), table("Q6_K"), "Q8_0")
    assert problems == ["output.weight is Q6_K, wanted Q8_0"]


def test_variant_table_rejects_any_other_difference():
    ref = table("Q6_K")
    changed_type = table(
        "Q8_0", **{"blk.0.ffn_up.weight": tensor("blk.0.ffn_up.weight", "Q8_0", [1024, 3072])}
    )
    assert any(
        "blk.0.ffn_up.weight" in p for p in day8.check_variant_table(changed_type, ref, "Q8_0")
    )
    changed_embd = table(
        "Q8_0", **{"token_embd.weight": tensor("token_embd.weight", "Q6_K", [1024, 4096])}
    )
    assert any("token_embd" in p for p in day8.check_variant_table(changed_embd, ref, "Q8_0"))
    missing = table("Q8_0")
    missing["tensors"] = [t for t in missing["tensors"] if t["name"] != "blk.0.attn_norm.weight"]
    assert any("only in the reference" in p for p in day8.check_variant_table(missing, ref, "Q8_0"))
    tied = table("Q8_0")
    tied["tensors"] = [t for t in tied["tensors"] if t["name"] != "output.weight"]
    assert any("output.weight is missing" in p for p in day8.check_variant_table(tied, ref, "Q8_0"))


def test_real_reference_table_is_the_q6k_default():
    ref = json.loads((REPO / "results" / "models" / "small_Q4_0.json").read_text())
    assert day8.check_variant_table(ref, ref, "Q6_K") == []
    assert day8.check_variant_table(ref, ref, "Q8_0") != []
    assert day8.VARIANTS[day8.REFERENCE]["output_type"] == "Q6_K"


def test_variant_names_are_valid_config_id_parts():
    for variant in day8.VARIANTS:
        p = sweep.parse_config_id(sweep.config_id("small", variant, "kleidiai", 1, "tg128"))
        assert p.quant == variant


def test_step_tables_writes_a_good_variant_and_stops_on_a_bad_one(tmp_path, monkeypatch):
    models, out = tmp_path / "models", tmp_path / "tables"
    models.mkdir()
    out.mkdir()
    tiny = write_tiny(models / "small_Q4_0outq8.gguf", tied=False)  # output.weight is Q8_0
    sha = "c" * 64
    (models / "SHA256SUMS").write_text(f"{sha}  small_Q4_0outq8.gguf\n")
    ref = gguf_table.build_table(tiny, "small", "Q4_0", SHA, {})
    (out / "small_Q4_0.json").write_text(gguf_table.dumps_table(ref))
    monkeypatch.setattr(
        day8,
        "VARIANTS",
        {
            "Q4_0": day8.VARIANTS["Q4_0"],
            "Q4_0outq8": day8.VARIANTS["Q4_0outq8"],  # wanted Q8_0: the tiny file has it
        },
    )
    assert bench_day8.step_tables(models, out) == 0
    written = json.loads((out / "small_Q4_0outq8.json").read_text())
    assert (written["alias"], written["quant"], written["sha256"]) == ("small", "Q4_0outq8", sha)

    # the same file claimed to be the Q4_0-output variant: wrong output type, no table written
    (out / "small_Q4_0outq8.json").unlink()
    monkeypatch.setattr(
        day8,
        "VARIANTS",
        {
            "Q4_0": day8.VARIANTS["Q4_0"],
            "Q4_0outq8": {"quantize_arg": "q4_0", "output_type": "Q4_0"},
        },
    )
    assert bench_day8.step_tables(models, out) == 1
    assert not (out / "small_Q4_0outq8.json").exists()


def test_step_tables_reports_a_missing_hash(tmp_path):
    models, out = tmp_path / "models", tmp_path / "tables"
    models.mkdir()
    out.mkdir()
    (models / "SHA256SUMS").write_text("")
    real = REPO / "results" / "models" / "small_Q4_0.json"
    (out / "small_Q4_0.json").write_text(real.read_text())
    assert bench_day8.step_tables(models, out) == 1


# --- Check A: running order and speed-ups -----------------------------------------------------


def test_check_a_has_six_pairs_with_both_build_orders_everywhere():
    pairs = bench_day8.check_a_pairs()
    assert len(pairs) == 6
    first = {}
    for pair in pairs:
        first.setdefault(("t", pair.threads), set()).add(sweep.build_order(pair.index)[0])
        first.setdefault(("v", pair.quant), set()).add(sweep.build_order(pair.index)[0])
    assert all(v == {"baseline", "kleidiai"} for v in first.values())
    ids = {p.config_id for pair in pairs for p in pair.points()}
    assert len(ids) == 12
    assert "small_Q4_0outq8_kleidiai_t1_tg128" in ids
    assert "small_Q4_0outq4_baseline_t8_tg128" in ids
    assert "small_Q4_0_baseline_t1_tg128" in ids  # the reference, measured again today


def write_a_records(folder, speeds, session="S"):
    """speeds: {(variant, threads): (baseline tok/s, kleidiai tok/s)}"""
    folder.mkdir(parents=True, exist_ok=True)
    for (variant, t), (b, k) in speeds.items():
        for build, tps in (("baseline", b), ("kleidiai", k)):
            cid = sweep.config_id("small", variant, build, t, "tg128")
            rec = fake_bench_record(cid, tps=tps)
            rec["session_id"] = session
            (folder / f"{cid}.json").write_text(json.dumps(rec))


SPEEDS_SUPPORTING = {
    ("Q4_0", 1): (100, 118), ("Q4_0outq8", 1): (90, 95), ("Q4_0outq4", 1): (110, 117),
    ("Q4_0", 8): (400, 470), ("Q4_0outq8", 8): (380, 395), ("Q4_0outq4", 8): (420, 440),
}  # fmt: skip


def test_check_a_prediction_holds_when_both_variants_are_clearly_smaller(tmp_path):
    write_a_records(tmp_path, SPEEDS_SUPPORTING)
    rows = day8.check_a_rows(tmp_path, "S", processed=tmp_path)
    assert len(rows) == 6
    by = {(r["variant"], r["threads"]): r for r in rows}
    assert by[("Q4_0", 1)]["speedup"] == pytest.approx(1.18, abs=0.005)
    assert by[("Q4_0outq8", 1)]["speedup"] == pytest.approx(95 / 90, abs=0.005)
    assert by[("Q4_0", 1)]["vs_reference"] == "reference"
    assert by[("Q4_0outq8", 1)]["vs_reference"] == "smaller"
    assert by[("Q4_0outq4", 8)]["vs_reference"] == "smaller"
    assert all(r["prediction_holds_at_t"] is True for r in rows)
    assert (
        by[("Q4_0", 1)]["output_type"] == "Q6_K" and by[("Q4_0outq8", 1)]["output_type"] == "Q8_0"
    )


def test_check_a_prediction_fails_when_a_variant_overlaps_or_is_larger(tmp_path):
    speeds = dict(SPEEDS_SUPPORTING)
    speeds[("Q4_0outq4", 1)] = (110, 130)  # 1.18: same as the reference -> overlap
    speeds[("Q4_0outq8", 8)] = (380, 480)  # 1.26: larger than the reference's 1.175
    write_a_records(tmp_path, speeds)
    by = {(r["variant"], r["threads"]): r for r in day8.check_a_rows(tmp_path, "S", tmp_path)}
    assert by[("Q4_0outq4", 1)]["vs_reference"] == "overlap"
    assert by[("Q4_0outq8", 8)]["vs_reference"] == "larger"
    assert by[("Q4_0outq8", 1)]["prediction_holds_at_t"] is False  # t=1: one variant overlaps
    assert by[("Q4_0outq8", 8)]["prediction_holds_at_t"] is False  # t=8: one variant is larger


def test_check_a_uses_the_rerun_when_the_first_attempt_was_noisy(tmp_path):
    write_a_records(tmp_path, SPEEDS_SUPPORTING)
    cid = "small_Q4_0outq4_kleidiai_t1_tg128"
    noisy = fake_bench_record(cid, tps=60, noisy=True)  # attempt 1: wild
    noisy["session_id"] = "S"
    (tmp_path / f"{cid}.json").write_text(json.dumps(noisy))
    rerun = fake_bench_record(cid, tps=117, attempt=2)
    rerun["session_id"] = "S"
    (tmp_path / f"{cid}__2.json").write_text(json.dumps(rerun))
    by = {(r["variant"], r["threads"]): r for r in day8.check_a_rows(tmp_path, "S", tmp_path)}
    row = by[("Q4_0outq4", 1)]
    assert row["kleidiai_median"] == pytest.approx(117, abs=0.5)
    assert row["kleidiai_still_noisy"] is False


def test_check_a_needs_both_builds_and_the_reference(tmp_path):
    write_a_records(tmp_path, SPEEDS_SUPPORTING)
    (tmp_path / "small_Q4_0outq8_baseline_t1_tg128.json").unlink()
    with pytest.raises(ValueError, match="needs both builds"):
        day8.check_a_rows(tmp_path, "S", tmp_path)
    other = tmp_path / "other"
    write_a_records(other, {k: v for k, v in SPEEDS_SUPPORTING.items() if k[0] != "Q4_0"})
    with pytest.raises(ValueError, match="reference"):
        day8.check_a_rows(other, "S", other)


def test_check_a_ignores_the_manifest_and_other_sessions_are_rejected(tmp_path):
    write_a_records(tmp_path, SPEEDS_SUPPORTING)
    (tmp_path / "_day8_check_a.json").write_text("{}")  # `_` files are not points
    assert len(day8.check_a_rows(tmp_path, "S", tmp_path)) == 6
    with pytest.raises(ValueError, match="session"):
        day8.check_a_rows(tmp_path, "T", tmp_path)


def test_sweep_speedup_is_read_from_the_committed_table():
    assert day8.sweep_speedup(REPO / "results" / "processed", "Q4_0", 1) == pytest.approx(
        1.177, abs=0.001
    )
    assert day8.sweep_speedup(REPO / "results" / "processed", "Q4_0outq8", 1) is None


def test_prediction_is_written_down_in_code_and_report_text():
    assert "clearly smaller" in day8.PREDICTION_A
    assert "Q4_0outq8" in day8.PREDICTION_A and "Q4_0outq4" in day8.PREDICTION_A
    assert "PREDICTION" in day8.__doc__ and "speedup_hi" in day8.__doc__


# --- Check C: perf ----------------------------------------------------------------------------

PERF_REPORT = """\
# To display the perf.data header info, please use --header/--header-only options.
#
# Samples: 41K of event 'cycles'
# Event count (approx.): 31245678901
#
# Overhead  Shared Object      Symbol
# ........  .................  ......................................
#
    61.20%  libggml-cpu.so     [.] ggml_gemm_q4_0_4x8_q8_0
    12.50%  libggml-cpu.so     [.] quantize_row_q8_0
     3.10%  [kernel.kallsyms]  [k] clear_page_erms
     0.40%  llama-bench        [.] main
"""


def test_parse_perf_report():
    rows = day8.parse_perf_report(PERF_REPORT)
    assert [r["symbol"] for r in rows] == [
        "ggml_gemm_q4_0_4x8_q8_0", "quantize_row_q8_0", "clear_page_erms", "main"
    ]  # fmt: skip
    assert rows[0] == {
        "percent": 61.2, "dso": "libggml-cpu.so", "kind": ".", "symbol": "ggml_gemm_q4_0_4x8_q8_0"
    }  # fmt: skip
    assert rows[2]["kind"] == "k"
    assert len(day8.parse_perf_report(PERF_REPORT, top=2)) == 2
    assert day8.perf_samples(PERF_REPORT) == ("41K", "cycles")


def test_trim_perf_report_keeps_header_and_top_rows():
    text = day8.trim_perf_report(PERF_REPORT, top=2)
    assert "Samples: 41K" in text and "quantize_row_q8_0" in text
    assert "clear_page_erms" not in text


def perf_record(**changes):
    rec = {
        "kind": "perf", "session_id": "S", "config_id": "small_Q4_0_baseline_t1_pp128",
        "build": "baseline", "quant": "Q4_0", "threads": 1, "test": "pp128", "event": "cycles",
        "perf_version": "perf version 6", "command": ["perf"], "samples": "41K",
        "top": day8.parse_perf_report(PERF_REPORT), "use_for_analysis": False, "caveat": "x",
        "captured_utc": "2026-11-04T10:00:00+00:00",
    }  # fmt: skip
    rec.update(changes)
    return rec


def test_perf_record_validation():
    day8.validate_perf_record(perf_record())
    with pytest.raises(ValueError, match="never be used"):
        day8.validate_perf_record(perf_record(use_for_analysis=True))
    with pytest.raises(ValueError, match="empty"):
        day8.validate_perf_record(perf_record(top=[]))
    with pytest.raises(ValueError, match="missing"):
        day8.validate_perf_record({"kind": "perf"})
    with pytest.raises(ValueError, match="add up"):
        day8.validate_perf_record(perf_record(top=[{"percent": 150.0}]))
    with pytest.raises(ValueError, match="unknown"):
        day8.validate_perf_record({"kind": "x"})


def test_perf_summary_names_the_hottest_symbols(tmp_path):
    (tmp_path / "small_Q4_0_baseline_t1_pp128.json").write_text(json.dumps(perf_record()))
    (line,) = day8.perf_summary(tmp_path)
    assert line.startswith("small_Q4_0_baseline_t1_pp128: ggml_gemm_q4_0_4x8_q8_0 61.2%")


def test_step_c_without_perf_records_that_and_stops(tmp_path, monkeypatch):
    monkeypatch.setattr(bench_day8.shutil, "which", lambda _name: None)
    status = bench_day8.step_c({}, "S", {}, perf_dir=tmp_path / "perf", data_dir=tmp_path / "data")
    assert status == 0
    (line,) = day8.perf_summary(tmp_path / "perf")
    assert line.startswith("perf not available: perf is not installed")
    # the same call again does not overwrite the record
    assert bench_day8.step_c({}, "S", {}, tmp_path / "perf", tmp_path / "data") == 0


def test_step_c_with_perf_that_cannot_sample_records_that_and_stops(tmp_path, monkeypatch):
    monkeypatch.setattr(bench_day8.shutil, "which", lambda _name: "/usr/bin/perf")
    failed = subprocess.CompletedProcess([], 255, "", "event not supported")
    monkeypatch.setattr(bench_day8, "run_text", lambda *_a, **_k: failed)
    assert bench_day8.step_c({}, "S", {}, tmp_path / "perf", tmp_path / "data") == 0
    rec = json.loads((tmp_path / "perf" / "_perf_unavailable.json").read_text())
    assert rec["reason"] == "perf cannot sample on this VM"
    assert [d.split(":")[0] for d in rec["details"]] == ["cycles", "cpu-clock"]
