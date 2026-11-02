"""Roofline v1 (CLAUDE.md §8): every formula on small hand-worked fixtures, the B(t) and C(t) rules
on synthetic records, the real inputs against the numbers pinned in §11, and rule 3 (the
prediction never opens results/raw/bench/). No hardware: runs in CI."""

import ast
import builtins
import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from edge_llm import peak, roofline, sweep
from tests.bench_fixtures import real_cfg

REPO = Path(__file__).resolve().parents[1]
SETTINGS = {"flash_attn": 1, "type_k": "f16", "type_v": "f16", "n_batch": 2048, "n_ubatch": 512}

# A tiny model whose numbers are easy to work by hand.
#   per-layer KV bytes per context token = 2 (K, V) x 2 KV heads x 8 x 2 B = 64; x 2 layers = 128
#   N_ffn_last = 3 x 16 x 32 = 1536
M = roofline.Model(
    w_blk=1000, n_blk=2000, w_out=500, n_out=800,
    n_layers=2, n_heads=4, n_kv_heads=2, head_dim=8, n_embd=16, n_ff=32,
)  # fmt: skip


# --- bytes and FLOPs, one formula at a time -----------------------------------------------


@pytest.mark.parametrize("quant, bits", [("F16", 16.0), ("Q8_0", 8.5), ("Q4_0", 4.5)])
def test_the_block_weight_bytes_follow_the_ggml_block_sizes(quant, bits):
    # §8 anchors: Q4_0 18 B / 32 weights = 4.5 bits, Q8_0 34 B / 32 = 8.5 bits, F16 16 bits.
    m = roofline.load_model(REPO / "results" / "models" / f"small_{quant}.json")
    assert m.w_blk == m.n_blk * bits / 8


def test_kv_bytes_for_the_real_model_match_adr_018():
    # 28 layers x 2 x 8 KV heads x 128 x 2 B = 114,688 B per context token; 2048 of them = 224 MiB
    per_token = roofline.kv_bytes(1, 28, 8, 128, 2)
    assert per_token == 114_688
    assert roofline.kv_bytes(2048, 28, 8, 128, 2) == 224 * 1024**2


def test_kv_bytes_of_the_tiny_model():
    assert roofline.kv_bytes(10, M.n_layers, M.n_kv_heads, M.head_dim, 2) == 1280


def test_the_average_decode_context():
    assert roofline.decode_context(0, 128) == 63.5
    assert roofline.decode_context(2048, 128) == 2111.5
    assert roofline.decode_context(0, 1) == 0  # one token generated from an empty context


def test_decode_flops():
    assert roofline.decode_weight_flops(M.n_blk, M.n_out) == 2 * (2000 + 800) == 5600
    # 4 x 2 layers x 4 heads x 8 x c
    assert roofline.decode_attention_flops(2, 4, 8, 63.5) == 256 * 63.5 == 16256


def test_attention_is_counted_in_64_tiles_not_as_a_triangle():
    # 2 x L x H x d x P x (P + 64) = 128 x 128 x 192
    assert roofline.prefill_attention_flops(2, 4, 8, 128) == 3_145_728
    # the same as 4 FLOPs-per-dim x L x H x d x (P (P + 64) / 2 query-key pairs)
    assert 4 * 2 * 4 * 8 * (128 * 192 // 2) == 3_145_728
    # a plain triangle (P^2 / 2 pairs) would count a third less at P = 128
    assert 4 * 2 * 4 * 8 * (128 * 128 // 2) < 3_145_728


def test_the_last_layers_ffn_runs_for_the_output_row_only():
    assert M.n_ffn_last == 1536
    # P = 10: 2 x 2000 x 10 - 2 x 1536 x 9 + 2 x 800 x 1
    assert roofline.prefill_weight_flops(2000, 800, 1536, 10) == 40000 - 27648 + 1600 == 13952
    # a one-token prompt is a decode step: both formulas agree
    assert roofline.prefill_weight_flops(2000, 800, 1536, 1) == roofline.decode_weight_flops(
        2000, 800
    )


def test_prefill_bytes_read_the_block_weights_once_per_ubatch():
    assert roofline.prefill_bytes(1000, 500, 128, 512) == 1500
    assert roofline.prefill_bytes(1000, 500, 512, 512) == 1500
    assert roofline.prefill_bytes(1000, 500, 513, 512) == 2500
    assert roofline.prefill_bytes(1000, 500, 2048, 512) == 4500


# --- which ceiling applies ----------------------------------------------------------------

CEIL = {  # ops/s at t = 1
    "sdot": {1: 100.0}, "smmla": {1: 50.0}, "fmla_f16": {1: 30.0}, "fmlal": {1: 10.0},
    "fma32": {1: 5.0},
}  # fmt: skip


def test_the_weight_ceiling_per_format_and_phase():
    assert roofline.weight_ceiling(CEIL, "Q4_0", "decode", 1) == ("sdot", 100.0)
    assert roofline.weight_ceiling(CEIL, "Q4_K_M", "decode", 1) == ("sdot", 100.0)
    assert roofline.weight_ceiling(CEIL, "F16", "decode", 1) == ("fmlal", 10.0)
    assert roofline.weight_ceiling(CEIL, "F16", "prefill", 1) == ("fmla_f16", 30.0)
    # quantised prefill takes the larger of SDOT and SMMLA
    assert roofline.weight_ceiling(CEIL, "Q8_0", "prefill", 1) == ("sdot", 100.0)
    bigger_smmla = {**CEIL, "smmla": {1: 200.0}}
    assert roofline.weight_ceiling(bigger_smmla, "Q8_0", "prefill", 1) == ("smmla", 200.0)


def test_the_binding_limit_and_its_tie():
    assert roofline.binding_limit(t_memory=2.0, t_compute=1.0) == "memory"
    assert roofline.binding_limit(t_memory=1.0, t_compute=2.0) == "compute"
    assert roofline.binding_limit(t_memory=1.0, t_compute=1.0) == "memory"


# --- one whole point ----------------------------------------------------------------------


def fake_hardware(b: float, scale: float = 1.0) -> roofline.Hardware:
    """Ceilings that make t = 2 hand-computable; `scale` makes the sustained ones lower."""
    c = {
        "sdot": 1000.0, "smmla": 500.0, "fmla_f16": 1e6, "fmlal": 800.0, "fma32": 3200.0,
    }  # fmt: skip
    ts = (1, 2, 4, 8)
    return roofline.Hardware(
        b={t: b for t in ts},
        b1={t: b / 2 for t in ts},
        c={k: {t: v for t in ts} for k, v in c.items()},
        c_sustained={k: {t: v * scale for t in ts} for k, v in c.items()},
        details={},
    )


def point(quant, test, t=2, build="baseline"):
    return sweep.Point("small", quant, build, t, test)


def test_a_decode_point_worked_by_hand_compute_bound():
    # c = 63.5; bytes = 1000 + 500 + 63.5 x 128 = 9628; weights 5600 / 1000 = 5.6 s;
    # attention 4 x 2 x 4 x 8 x 63.5 = 16256 / 3200 = 5.08 s; compute 10.68 s; memory 9628 / 2000.
    r = roofline.predict_point(point("Q4_0", "tg128"), M, fake_hardware(b=2000.0), SETTINGS)
    assert r["bytes"] == 9628 and r["weight_flops"] == 5600 and r["attention_flops"] == 16256
    assert r["avg_context"] == 63.5
    assert r["t_memory"] == pytest.approx(4.814)
    assert r["t_compute"] == pytest.approx(10.68)
    assert r["predicted_tps"] == pytest.approx(1 / 10.68)
    assert r["binding"] == "compute" and r["C_weight_class"] == "sdot"


def test_a_decode_point_worked_by_hand_memory_bound():
    r = roofline.predict_point(point("Q4_0", "tg128"), M, fake_hardware(b=500.0), SETTINGS)
    assert r["t_memory"] == pytest.approx(9628 / 500)
    assert r["predicted_tps"] == pytest.approx(500 / 9628)
    assert r["binding"] == "memory"


def test_decode_at_depth_reads_more_kv_and_does_more_attention():
    r = roofline.predict_point(point("Q4_0", "tg128d2048", t=1), M, fake_hardware(2000), SETTINGS)
    assert r["avg_context"] == 2111.5
    assert r["bytes"] == 1500 + 2111.5 * 128
    assert r["attention_flops"] == 256 * 2111.5


def test_f16_decode_uses_the_widening_fmlal_ceiling():
    r = roofline.predict_point(point("F16", "tg128"), M, fake_hardware(b=1e9), SETTINGS)
    assert r["C_weight_class"] == "fmlal"
    assert r["t_compute"] == pytest.approx(5600 / 800 + 16256 / 3200)


def test_a_prefill_point_worked_by_hand():
    # P = 512: F_w = 2 x 2000 x 512 - 2 x 1536 x 511 + 2 x 800 = 479,808;
    # F_a = 128 x 512 x 576 = 37,748,736; F16 prefill weights run on the FMLA .8h ceiling.
    # b is huge, so the 1500 bytes of memory traffic cannot bind.
    r = roofline.predict_point(point("F16", "pp512"), M, fake_hardware(b=1e9), SETTINGS)
    assert r["weight_flops"] == 479_808 and r["attention_flops"] == 37_748_736
    assert r["bytes"] == 1500 and r["avg_context"] is None
    assert r["C_weight_class"] == "fmla_f16"
    t_compute = 479_808 / 1e6 + 37_748_736 / 3200
    assert r["t_compute"] == pytest.approx(t_compute)
    assert r["predicted_tps"] == pytest.approx(512 / t_compute)  # tokens/s counts all P tokens
    assert r["binding"] == "compute"


def test_a_long_prompt_reads_the_block_weights_once_per_chunk():
    # a tiny b makes memory bind: 4 chunks x 1000 + 500 = 4500 bytes at 0.001 bytes/s
    r = roofline.predict_point(point("Q4_0", "pp2048"), M, fake_hardware(b=0.001), SETTINGS)
    assert r["bytes"] == 4 * 1000 + 500
    assert r["binding"] == "memory"
    assert r["predicted_tps"] == pytest.approx(2048 / (4500 / 0.001))


def test_the_sustained_prediction_uses_the_sustained_ceilings_and_is_lower():
    r = roofline.predict_point(point("Q4_0", "pp512"), M, fake_hardware(1e9, scale=0.5), SETTINGS)
    assert r["t_compute_sustained"] == pytest.approx(2 * r["t_compute"])
    assert r["predicted_tps_sustained"] == pytest.approx(r["predicted_tps"] / 2)


def test_the_two_builds_get_the_same_prediction():
    a = roofline.predict_point(
        point("Q4_0", "tg128", build="baseline"), M, fake_hardware(2000), SETTINGS
    )
    b = roofline.predict_point(
        point("Q4_0", "tg128", build="kleidiai"), M, fake_hardware(2000), SETTINGS
    )
    assert a["predicted_tps"] == b["predicted_tps"]
    assert a["config_id"] != b["config_id"] and a["pair_id"] == b["pair_id"]


def test_settings_the_formulas_do_not_cover_are_rejected():
    hw = fake_hardware(1000)
    with pytest.raises(ValueError):  # the 64 x 64 tile count is flash attention's
        roofline.predict_point(point("Q4_0", "pp512"), M, hw, {**SETTINGS, "flash_attn": 0})
    with pytest.raises(ValueError):  # a prompt split over several batches is not covered
        roofline.predict_point(point("Q4_0", "pp2048"), M, hw, {**SETTINGS, "n_batch": 1024})
    with pytest.raises(ValueError):
        roofline.predict_point(point("Q4_0", "tg128"), M, hw, {**SETTINGS, "type_v": "q8_0"})


def test_predict_all_has_one_row_per_full_sweep_point():
    cfg = real_cfg()
    models = {("small", q): M for q in cfg["quants"]}
    rows = roofline.predict_all(cfg, models, fake_hardware(1000.0))
    expected = [p.config_id for pair in sweep.pairs(cfg, "full") for p in pair.points()]
    assert [r["config_id"] for r in rows] == expected and len(rows) == 144
    assert all(set(r) == set(roofline.COLUMNS) for r in rows)


# --- B(t) and C(t) from records -----------------------------------------------------------


def bw_point(t, acc, streams, median, hugepage=False):
    return SimpleNamespace(
        kernel="read", threads=t, accumulators=acc, streams=streams, median=median,
        hugepage=hugepage, l1=False,
    )  # fmt: skip


def peak_point(cls, t, chains, samples_instr):
    ops = peak.ops_per_instruction(cls, 128)
    return SimpleNamespace(
        instr_class=cls, threads=t, accumulators=chains, samples_instr_per_s=samples_instr,
        samples_ops_per_s=[s * ops for s in samples_instr],
    )  # fmt: skip


TWO_STATE = [100.0] * 10 + [200.0] * 10  # half the repetitions throttled: p90 = 200, mean = 150


def synthetic_peak(failed_chains=(28,)):
    """Every class, t in {1, 4}, chains 8/16/28. The 16-chain loop is the real best; the 28-chain
    loop looks faster but fails its disassembly check; the 8-chain loop is slower."""
    points = []
    for cls in peak.PEAK_CLASSES:
        for t in (1, 4):
            slow = [0.5 * s for s in TWO_STATE]
            fast = [2.0 * s for s in TWO_STATE] if t == 4 else TWO_STATE
            points += [
                peak_point(cls, t, 8, slow),
                peak_point(cls, t, 16, fast),
                peak_point(cls, t, 28, [2 * s for s in fast]),
            ]
    disasm = {
        cls: {"checks": [{"accumulators": a, "ok": a not in failed_chains} for a in (8, 16, 28)]}
        for cls in peak.PEAK_CLASSES
    }
    return SimpleNamespace(points=points, disasm=disasm, sve_vector_bits=128)


def synthetic_bandwidth():
    points = [
        bw_point(1, 8, 1, 27e9), bw_point(1, 16, 4, 37e9), bw_point(1, 16, 8, 99e9),  # 99: invalid
        bw_point(1, 8, 1, 50e9, hugepage=True),  # a diagnostic run never counts
        bw_point(4, 8, 1, 100e9), bw_point(4, 16, 4, 135e9), bw_point(4, 16, 8, 140e9),
    ]  # fmt: skip
    validity = {
        "variants": [
            {"accumulators": 8, "streams": 1, "valid": True},
            {"accumulators": 16, "streams": 4, "valid": True},
            {"accumulators": 16, "streams": 8, "valid": False},
        ]
    }
    return SimpleNamespace(points=points, validity=validity)


def test_b_of_t_is_the_best_valid_variant_and_keeps_the_one_stream_result():
    hw = roofline.hardware_from_records(synthetic_bandwidth(), synthetic_peak())
    # t = 1: 99 GB/s is not valid and the huge-page 50 GB/s is a diagnostic: the best is 37
    assert hw.b[1] == 37e9 and hw.b1[1] == 27e9
    # t = 4: the invalid 16 x 8 variant (140) is skipped; the valid best is 135
    assert hw.b[4] == 135e9 and hw.b1[4] == 100e9
    assert hw.details["bandwidth"]["4"]["streams"] == 4


def test_c_of_t_is_t_times_the_p90_of_one_thread_times_ops_per_instruction():
    hw = roofline.hardware_from_records(synthetic_bandwidth(), synthetic_peak())
    # p90 of {100 x 10, 200 x 10} = 200 instr/s; best valid chain count at t = 1 is 16 (not 28)
    assert roofline.percentile90(TWO_STATE) == 200.0
    assert hw.c["sdot"][1] == 1 * 200.0 * 32
    assert hw.c["sdot"][4] == 4 * 200.0 * 32  # t x the t = 1 rate, whatever the t = 4 samples say
    assert hw.c["smmla"][4] == 4 * 200.0 * 64
    assert hw.c["fmlal"][1] == 200.0 * 8  # widening FMLALB/T: 8 operations per instruction
    assert hw.c["fma32"][1] == 200.0 * 8
    assert hw.details["peak"]["sdot"]["chains_at_p90"] == 16


def test_the_sustained_ceiling_is_the_mean_of_the_repetitions_of_the_best_valid_chain_count():
    hw = roofline.hardware_from_records(synthetic_bandwidth(), synthetic_peak())
    assert hw.c_sustained["sdot"][1] == 150.0 * 32  # mean of the two-state samples
    # at t = 4 the valid 16-chain loop runs at twice the speed: mean 300 instr/s
    assert hw.c_sustained["sdot"][4] == 300.0 * 32
    assert hw.c_sustained["sdot"][4] < hw.c["sdot"][4]


def test_a_chain_count_that_failed_its_disassembly_check_never_counts():
    # without the failure the 28-chain loops would win everywhere
    ok = roofline.hardware_from_records(synthetic_bandwidth(), synthetic_peak(failed_chains=()))
    bad = roofline.hardware_from_records(synthetic_bandwidth(), synthetic_peak())
    assert ok.c["sdot"][1] == 2 * bad.c["sdot"][1]
    assert ok.details["peak"]["sdot"]["chains_at_p90"] == 28


def test_percentile_90_interpolates_like_numpy():
    assert roofline.percentile90([float(i) for i in range(1, 11)]) == pytest.approx(9.1)


# --- the real inputs, against the numbers pinned in CLAUDE.md §11 ---------------------------


@pytest.fixture(scope="module")
def real_hw():
    return roofline.load_hardware(REPO)


def test_real_b_of_t_matches_section_11(real_hw):
    for t, gbs in {1: 37.32, 2: 73.13, 4: 135.72, 8: 237.23}.items():
        assert real_hw.b[t] / 1e9 == pytest.approx(gbs, abs=0.01)
    for t, gbs in {1: 27.96, 2: 54.27, 4: 100.41, 8: 181.84}.items():
        assert real_hw.b1[t] / 1e9 == pytest.approx(gbs, abs=0.01)


def test_real_c_of_t_matches_section_11(real_hw):
    # per-core ceilings: SDOT 382, SMMLA 765, FP16 FMLA 191, FMLALB/T 95.6, F32 FMLA 95.6 GOPS
    for cls, gops in {
        "sdot": 382, "smmla": 765, "fmla_f16": 191, "fmlal": 95.6, "fma32": 95.6
    }.items():  # fmt: skip
        assert real_hw.c[cls][1] / 1e9 == pytest.approx(gops, rel=0.005)
        assert real_hw.c[cls][8] == pytest.approx(8 * real_hw.c[cls][1])
        # the sustained ceiling at 8 threads is the lower one (throttling, ADR-023)
        assert real_hw.c_sustained[cls][8] < real_hw.c[cls][8]


# --- the files ----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    out = tmp_path_factory.mktemp("predictions")
    rows = roofline.run(REPO, out)
    return rows, out


def test_run_writes_144_rows_and_the_meta(generated):
    rows, out = generated
    assert len(rows) == 144
    with open(out / "v1.csv", newline="") as f:
        read = list(csv.DictReader(f))
    assert [r["config_id"] for r in read] == [r["config_id"] for r in rows]
    assert list(read[0]) == roofline.COLUMNS
    meta = json.loads((out / "v1.meta.json").read_text())
    assert meta["rows"] == 144 and meta["bandwidth_record"].endswith("2026-11-02T2141Z_start.json")
    assert "ADR-023" in meta["adrs"] and "ADR-024" in meta["adrs"]
    assert set(meta["inputs_sha256"]) >= {
        "configs/sweep.yaml",
        "results/raw/bandwidth/2026-11-02T2141Z_start.json",
        "results/raw/peak/2026-11-02T2141Z.json",
        "results/models/small_Q4_0.json",
    }
    assert all(len(h) == 64 for h in meta["inputs_sha256"].values())


def test_decode_is_memory_bound_and_prefill_compute_bound_on_the_real_inputs(generated):
    rows, _ = generated
    assert {r["binding"] for r in rows if r["phase"] == "decode"} == {"memory"}
    assert {r["binding"] for r in rows if r["phase"] == "prefill"} == {"compute"}
    assert all(r["predicted_tps"] > 0 for r in rows)
    assert all(r["predicted_tps_sustained"] <= r["predicted_tps"] for r in rows)


def test_the_committed_predictions_are_what_the_code_gives(generated):
    committed = REPO / "results" / "predictions" / "v1.csv"
    rows, _ = generated
    with open(committed, newline="") as f:
        read = list(csv.DictReader(f))
    assert [r["config_id"] for r in read] == [r["config_id"] for r in rows]
    for got, want in zip(read, rows, strict=True):
        assert float(got["predicted_tps"]) == pytest.approx(want["predicted_tps"], rel=1e-12)
        assert float(got["predicted_tps_sustained"]) == pytest.approx(
            want["predicted_tps_sustained"], rel=1e-12
        )


# --- rule 3: predictions never see measured speed ------------------------------------------


def test_roofline_never_opens_a_bench_record(tmp_path, monkeypatch):
    opened: list[str] = []
    real_open = builtins.open

    def spy(file, *args, **kwargs):
        opened.append(str(file).replace("\\", "/"))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", spy)
    monkeypatch.setattr(io, "open", spy)  # pathlib's read_text / read_bytes go through here
    roofline.run(REPO, tmp_path)

    # the spy sees what the code reads: the bandwidth and peak records, so it is not blind
    assert any(p.endswith("2026-11-02T2141Z_start.json") for p in opened)
    assert any(p.endswith("2026-11-02T2141Z.json") for p in opened)
    assert not [p for p in opened if "raw/bench" in p], "roofline.py opened a bench record"


def test_roofline_source_never_names_the_bench_folder():
    tree = ast.parse((REPO / "src" / "edge_llm" / "roofline.py").read_text())
    docstrings = {
        id(n.body[0].value)
        for n in ast.walk(tree)
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and n.body
        and isinstance(n.body[0], ast.Expr)
        and isinstance(n.body[0].value, ast.Constant)
    }
    strings = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
    ]
    assert not [s for s in strings if s == "bench" or "raw/bench" in s]


def test_input_hashes_do_not_depend_on_line_endings(tmp_path):
    lf, crlf = tmp_path / "lf.yaml", tmp_path / "crlf.yaml"
    lf.write_bytes(b"a: 1\nb: 2\n")
    crlf.write_bytes(b"a: 1\r\nb: 2\r\n")
    assert roofline.sha256(lf) == roofline.sha256(crlf)
