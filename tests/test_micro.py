"""RQ4 int8 dot-product microbenchmark: the record schema, the speed-up and fraction arithmetic on
synthetic records, the disassembly checker on synthetic snippets, and the run's gating. No hardware
(the compiled program is tested in test_day7_hardware.py, on the VM)."""

import copy
import csv
import json

import pytest

from edge_llm import micro, peak
from edge_llm.schema import MicroPoint, MicroRecord, SchemaError
from micro import run_micro
from tests.micro_fixtures import (
    B_BEST,
    B_ONE,
    C_SDOT,
    C_SMMLA,
    DRAM_NS,
    L1_NS,
    make_point,
    micro_record,
)

# --- the table of variants and the kernel shape ------------------------------------------------


def test_the_variants_are_the_five_families_with_four_and_eight_accumulators():
    assert set(micro.FAMILIES) == {"scalar", "autovec", "sdot", "smmla", "sve"}
    assert micro.VARIANTS == {
        "scalar": ("scalar", 0),
        "autovec": ("autovec", 0),
        "sdot_a4": ("sdot", 4),
        "sdot_a8": ("sdot", 8),
        "smmla_a4": ("smmla", 4),
        "smmla_a8": ("smmla", 8),
        "sve_a4": ("sve", 4),
        "sve_a8": ("sve", 8),
    }
    assert micro.function_name("sdot_a8") == "dot_sdot_a8"


def test_the_working_sets_are_16_kib_and_1_gib_and_the_sum_cannot_overflow():
    assert micro.K == 4096 and micro.ROWS == {"L1": 4, "DRAM": 262_144}
    assert micro.ROWS["L1"] * micro.K == 16 * 1024
    assert micro.ROWS["DRAM"] * micro.K == 2**30 >= 4 * micro.L3_BYTES
    assert micro.K * 128 * 128 < 2**31  # the worst row sum (all -128 times all -128) fits int32


def test_only_smmla_does_two_macs_per_weight_byte():
    assert micro.MACS_PER_WEIGHT_BYTE == {
        "scalar": 1,
        "autovec": 1,
        "sdot": 1,
        "smmla": 2,
        "sve": 1,
    }
    assert micro.macs_per_call("smmla_a8", "L1") == 2 * 4 * 4096
    assert micro.macs_per_call("sdot_a8", "DRAM") == 262_144 * 4096


# --- the record --------------------------------------------------------------------------------


def test_a_good_record_validates():
    rec = MicroRecord.from_dict(copy.deepcopy(micro_record()))
    assert len(rec.points) == len(micro.VARIANTS) * 2


def test_a_record_with_a_missing_variant_is_rejected():
    r = micro_record()
    r["points"] = [
        p for p in r["points"] if not (p["variant"] == "smmla_a4" and p["working_set"] == "DRAM")
    ]
    with pytest.raises(SchemaError, match="every variant on both working sets"):
        MicroRecord.from_dict(r)


def test_timing_is_refused_when_the_check_did_not_pass():
    r = micro_record()
    r["check"] = {"ok": False, "cases": 66}
    with pytest.raises(SchemaError, match="timing is refused"):
        MicroRecord.from_dict(r)


def test_a_point_whose_output_differed_from_scalar_is_rejected():
    pt = make_point("sdot_a8", "L1", 128.0)
    pt["output_matches_scalar"] = False
    with pytest.raises(SchemaError, match="differs from the scalar"):
        MicroPoint.from_dict(pt)


def test_a_point_needs_30_repeats_and_a_summary_that_follows_from_its_samples():
    with pytest.raises(SchemaError, match="at least 30"):
        MicroPoint.from_dict(make_point("scalar", "L1", 4096.0, reps=20))
    pt = make_point("scalar", "L1", 4096.0)
    pt["median_ns"] *= 1.1
    with pytest.raises(SchemaError, match="median_ns"):
        MicroPoint.from_dict(pt)


def test_an_l1_repetition_shorter_than_10_ms_is_rejected():
    pt = make_point("sdot_a8", "L1", 128.0)
    pt["calls_per_rep"] = 1000  # 1000 x 128 ns = 0.13 ms
    with pytest.raises(SchemaError, match="under 10 ms"):
        MicroPoint.from_dict(pt)


def test_a_point_must_have_the_documented_shape():
    pt = make_point("scalar", "DRAM", 4.0e8)
    pt["rows"], pt["weight_bytes"], pt["macs_per_call"] = 1024, 1024 * 4096, 1024 * 4096
    with pytest.raises(SchemaError, match="rows x k must be"):
        MicroPoint.from_dict(pt)
    assert micro.ROWS["L1"] * micro.K <= micro.L1D_BYTES // 2


def test_the_macs_per_weight_byte_must_be_the_families_number():
    pt = make_point("smmla_a8", "L1", 100.0)
    pt["macs_per_weight_byte"], pt["macs_per_call"] = 1, 4 * 4096
    with pytest.raises(SchemaError, match="must be 2 for smmla"):
        MicroPoint.from_dict(pt)


def test_the_record_must_say_smmla_does_twice_the_macs():
    r = micro_record()
    r["kernel"] = {}
    with pytest.raises(SchemaError, match="smmla_macs_per_weight_byte"):
        MicroRecord.from_dict(r)


def test_the_record_names_and_hashes_the_references():
    r = micro_record()
    del r["references"]["bandwidth_record"]["sha256"]
    with pytest.raises(SchemaError, match="sha256 missing"):
        MicroRecord.from_dict(r)
    r = micro_record()
    r["references"]["peak_record"]["C_smmla_ops_per_s"] = 0
    with pytest.raises(SchemaError, match="must be positive"):
        MicroRecord.from_dict(r)


def test_a_failed_disassembly_check_keeps_the_record():
    rec = MicroRecord.from_dict(micro_record(failed={"sve_a8"}))
    assert rec.disasm["sve_a8"]["ok"] is False


# --- the arithmetic on a synthetic record ------------------------------------------------------


def rows_of(record_dict):
    rows = micro.derive_rows(MicroRecord.from_dict(record_dict))
    return {(r["variant"], r["working_set"]): r for r in rows}


def test_rates_are_macs_per_ns_and_weight_bytes_per_ns():
    rows = rows_of(micro_record())
    scalar = rows[("scalar", "L1")]
    assert scalar["gmacs"] == pytest.approx(16384 / 4096)  # 4 GMAC/s
    assert scalar["weight_gbs"] == pytest.approx(4.0)
    sdot = rows[("sdot_a8", "L1")]
    assert sdot["gmacs"] == pytest.approx(16384 / 128) and sdot["weight_gbs"] == pytest.approx(128)


def test_smmla_counts_both_vectors_in_gmacs_but_not_in_weight_bytes():
    r = rows_of(micro_record())[("smmla_a8", "L1")]
    assert r["macs_per_weight_byte"] == 2
    assert r["gmacs"] == pytest.approx(2 * 16384 / 100)
    assert r["weight_gbs"] == pytest.approx(16384 / 100)
    assert r["gmacs"] == pytest.approx(2 * r["weight_gbs"])


def test_the_speedup_is_against_scalar_in_the_same_working_set_both_ways():
    rows = rows_of(micro_record())
    s = rows[("smmla_a8", "L1")]
    assert s["speedup_vs_scalar"] == pytest.approx(4096 / 100 * 2)  # time ratio x 2 MACs per byte
    assert s["speedup_vs_scalar_per_weight_byte"] == pytest.approx(4096 / 100)
    d = rows[("sdot_a8", "DRAM")]
    assert d["speedup_vs_scalar"] == pytest.approx(4.0e8 / 33_554_432)
    assert d["speedup_vs_scalar"] == pytest.approx(d["speedup_vs_scalar_per_weight_byte"])
    assert rows[("scalar", "DRAM")]["speedup_vs_scalar"] == pytest.approx(1.0)


def test_l1_fractions_use_the_matching_peak_in_macs_and_dram_has_none():
    rows = rows_of(micro_record())
    sdot = rows[("sdot_a8", "L1")]
    assert sdot["peak_class"] == "sdot" and sdot["peak_gmacs"] == pytest.approx(C_SDOT / 2e9)
    assert sdot["fraction_of_peak"] == pytest.approx((16384 / 128) / (C_SDOT / 2e9))  # 128 / 200
    assert rows[("sve_a8", "L1")]["peak_class"] == "sdot"  # SVE SDOT is the same ceiling
    smmla = rows[("smmla_a8", "L1")]
    assert smmla["fraction_of_peak"] == pytest.approx((2 * 16384 / 100) / (C_SMMLA / 2e9))
    assert rows[("scalar", "L1")]["peak_class"] is None
    assert rows[("scalar", "L1")]["fraction_of_peak"] is None
    assert rows[("sdot_a8", "DRAM")]["fraction_of_peak"] is None


def test_dram_fractions_are_weight_bytes_per_second_over_b_and_b1():
    r = rows_of(micro_record())[("sdot_a8", "DRAM")]
    assert r["weight_gbs"] == pytest.approx(32.0)  # 2^30 B in 2^25 ns
    assert r["fraction_of_B"] == pytest.approx(32e9 / B_BEST)  # 0.8
    assert r["fraction_of_B1"] == pytest.approx(32e9 / B_ONE)  # 1.0
    assert rows_of(micro_record())[("sdot_a8", "L1")]["fraction_of_B"] is None
    # SMMLA: the fraction of B is by weight bytes, not by MACs
    s = rows_of(micro_record())[("smmla_a8", "DRAM")]
    assert s["fraction_of_B"] == pytest.approx(0.8) and s["gmacs"] == pytest.approx(64.0)


def test_the_p90_rate_fraction_is_taken_from_the_fast_repetitions():
    r = rows_of(micro_record())[("sdot_a8", "L1")]
    assert r["gmacs_p90"] > r["gmacs"]  # the 10th-percentile time is shorter than the median
    assert r["fraction_of_peak_p90"] == pytest.approx(r["gmacs_p90"] / (C_SDOT / 2e9))


def test_the_error_bar_ends_are_the_rates_at_the_slow_and_fast_quartile():
    r = rows_of(micro_record())[("sdot_a8", "L1")]
    assert r["gmacs_lo"] < r["gmacs"] < r["gmacs_hi"]
    assert r["gmacs_lo"] == pytest.approx(16384 / r["q3_ns"])


def test_the_reference_columns_carry_the_files_and_values():
    r = rows_of(micro_record())[("scalar", "L1")]
    assert r["ref_B_GBps"] == pytest.approx(40.0) and r["ref_B1_GBps"] == pytest.approx(32.0)
    assert r["ref_C_sdot_GMACs"] == pytest.approx(200.0)
    assert r["ref_C_smmla_GMACs"] == pytest.approx(400.0)
    assert r["bandwidth_record"].endswith("X_start.json") and r["peak_record"].endswith("Y.json")
    assert r["source_file"] == "results/raw/micro/S.json"


# --- best of the accumulator counts (ADR-022 rule) ----------------------------------------------


def best_of(record_dict):
    return {
        (r["family"], r["working_set"]): r["variant"]
        for r in micro.derive_rows(MicroRecord.from_dict(record_dict))
        if r["is_best"]
    }


def test_the_best_accumulator_count_is_the_fastest_one_per_family_and_working_set():
    best = best_of(micro_record())
    assert best[("sdot", "L1")] == "sdot_a8" and best[("sdot", "DRAM")] == "sdot_a8"
    assert best[("sve", "L1")] == "sve_a8" and best[("smmla", "DRAM")] == "smmla_a8"
    assert best[("scalar", "L1")] == "scalar" and len(best) == 10


def test_a_variant_that_failed_its_disassembly_check_cannot_be_best():
    assert best_of(micro_record(failed={"sdot_a8"}))[("sdot", "L1")] == "sdot_a4"


def test_a_tie_goes_to_the_smaller_accumulator_count():
    l1 = dict(L1_NS, sdot_a4=128.0)  # equal to sdot_a8
    assert best_of(micro_record(l1_ns=l1))[("sdot", "L1")] == "sdot_a4"
    # (the two are different samples in a real record; equal medians are the only tie)
    dram = dict(DRAM_NS, sve_a4=DRAM_NS["sve_a8"])
    assert best_of(micro_record(dram_ns=dram))[("sve", "DRAM")] == "sve_a4"


# --- the share of slow repetitions (two-state throttling, ADR-023) ----------------------------


def test_slow_share_counts_repetitions_running_at_about_half_the_fast_rate():
    samples = [100.0] * 20 + [200.0] * 10  # a third of the repetitions at half rate
    assert micro.slow_share(samples) == pytest.approx(10 / 30)
    assert micro.slow_share([100.0] * 30) == 0.0
    assert micro.slow_share([100.0 * (1 + 0.01 * (i % 3)) for i in range(30)]) == 0.0


def test_slow_share_is_about_rates_not_times():
    # Nine fast repetitions and one at 1/0.7 the time (rate 70 % of fast): above the 75 % bar? no,
    # 70 % is below it, so it counts as slow; 80 % is not.
    assert micro.slow_share([100.0] * 29 + [100.0 / 0.70]) == pytest.approx(1 / 30)
    assert micro.slow_share([100.0] * 29 + [100.0 / 0.80]) == 0.0


# --- the disassembly checker on synthetic snippets ---------------------------------------------


def objdump(body, name="dot_sdot_a4", start=0x780):
    lines = [f"0000000000{start:06x} <{name}>:"]
    addr = start
    for text in body:
        lines.append(f"  {addr:x}:\t{text}")
        addr += 4
    return "\n".join(lines) + "\n"


def kernel_text(variant, loop_body, name=None):
    """A function: setup, an inner loop (the body, then the counter and the branch), then the outer
    loop's own bookkeeping and branch."""
    start = 0x780
    pre = ["mov\tx5, #0x0", "movi\tv0.4s, #0x0"]
    inner_top = start + 4 * len(pre)
    body = (
        pre
        + list(loop_body)
        + ["add\tx4, x4, #0x40", "cmp\tx4, x3", f"b.ne\t{inner_top:x} <f+0x8>"]
    )
    outer = body + [
        "addv\ts1, v0.4s",
        "add\tx5, x5, #0x1",
        "cmp\tx5, x2",
        f"b.ne\t{start:x} <f>",
        "ret",
    ]
    return objdump(outer, name or micro.function_name(variant), start)


def loop_and_check(variant, loop_body):
    insns = peak.parse_instructions(kernel_text(variant, loop_body))
    loop = micro.hot_loop_for(variant, insns)
    return loop, micro.check_loop(variant, loop, [t for _, t in insns])


def sdot_v(n):
    return [f"sdot\tv{i}.4s, v{20 + i}.16b, v{10 + i}.16b" for i in range(n)]


def test_an_sdot_loop_with_one_instruction_per_accumulator_passes():
    loop, check = loop_and_check("sdot_a4", ["ldr\tq20, [x0]", "ldr\tq21, [x1]"] + sdot_v(4))
    assert check["ok"] and check["found"] == 4 and check["expected"] == "sdot v-form"
    assert loop[-1].startswith("b.ne") and len(loop) == 2 + 4 + 3
    assert "addv" not in " ".join(loop)  # the row's reduction is outside the inner loop


def test_the_loop_is_the_inner_one_not_the_row_loop():
    loop, _ = loop_and_check("sdot_a8", sdot_v(8))
    assert not any(t.startswith(("mov", "addv")) for t in loop)


def test_a_wrong_count_or_form_fails():
    assert not loop_and_check("sdot_a8", sdot_v(7))[1]["ok"]  # one missing
    assert not loop_and_check("sdot_a4", sdot_v(8))[1]["ok"]  # unrolled twice
    z_form = [f"sdot\tz{i}.s, z{20 + i}.b, z{10 + i}.b" for i in range(4)]
    assert not loop_and_check("sdot_a4", z_form)[1]["ok"]  # SVE form in a NEON variant
    assert loop_and_check("sve_a4", z_form)[1]["ok"]  # ... and the right one for SVE
    assert not loop_and_check("sve_a4", sdot_v(4))[1]["ok"]  # NEON form in the SVE variant


def test_smmla_needs_smmla_not_sdot():
    smmla = [f"smmla\tv{i}.4s, v{20 + i}.16b, v{10 + i}.16b" for i in range(4)]
    assert loop_and_check("smmla_a4", smmla)[1]["ok"]
    assert not loop_and_check("smmla_a4", sdot_v(4))[1]["ok"]


def test_scalar_must_have_no_simd_multiply_anywhere():
    scalar = ["ldrsb\tw6, [x0], #1", "ldrsb\tw7, [x1], #1", "smaddl\tx8, w6, w7, x8"]
    loop, check = loop_and_check("scalar", scalar)
    assert check["ok"] and check["simd_multiply_in_loop"] == []
    assert len(loop) == 3 + 3
    for bad in ("smull\tv0.8h, v1.8b, v2.8b", "mul\tv0.16b, v1.16b, v2.16b",
                "smlal2\tv0.4s, v1.8h, v2.8h", "sdot\tv0.4s, v1.16b, v2.16b"):  # fmt: skip
        assert not loop_and_check("scalar", scalar + [bad])[1]["ok"], bad
    # a scalar `mul` on w/x registers is fine
    assert loop_and_check("scalar", scalar + ["mul\tw9, w6, w7"])[1]["ok"]


def test_a_simd_multiply_outside_the_scalar_loop_but_in_the_function_still_fails():
    scalar = ["ldrsb\tw6, [x0], #1", "smaddl\tx8, w6, w7, x8"]
    text = kernel_text("scalar", scalar).replace("ret", "smull\tv0.8h, v1.8b, v2.8b\n  7ff:\tret")
    insns = peak.parse_instructions(text)
    check = micro.check_loop("scalar", micro.hot_loop_for("scalar", insns), [t for _, t in insns])
    assert not check["ok"] and check["simd_multiply_in_function"] == ["smull"]


def test_autovec_is_recorded_not_asserted():
    vec = ["ldr\tq1, [x0], #16", "ldr\tq2, [x1], #16", "sdot\tv0.4s, v1.16b, v2.16b"]
    _, with_sdot = loop_and_check("autovec", vec)
    assert with_sdot["ok"] and not with_sdot["asserted"] and with_sdot["uses_sdot"]
    assert with_sdot["simd_multiply_in_loop"] == ["sdot"]
    widening = ["ldr\td1, [x0], #8", "sxtl\tv1.8h, v1.8b", "smlal\tv0.4s, v1.4h, v2.4h",
                "smlal2\tv0.4s, v1.8h, v2.8h"]  # fmt: skip
    _, other = loop_and_check("autovec", widening)
    assert other["ok"] and not other["uses_sdot"]
    assert other["simd_multiply_in_loop"] == ["smlal", "smlal2"]
    assert other["mnemonics"]["sxtl"] == 1 and other["loop"][0] == "ldr d1, [x0], #8"


def test_autovec_prefers_the_vector_loop_over_a_shorter_scalar_remainder_loop():
    lines = [
        "0000000000000780 <dot_autovec>:",
        "  780:\tldr\tq1, [x0], #16",  # vector loop starts here
        "  784:\tsdot\tv0.4s, v1.16b, v2.16b",
        "  788:\tsubs\tx3, x3, #0x1",
        "  78c:\tb.ne\t780 <dot_autovec>",
        "  790:\tldrsb\tw6, [x0], #1",  # scalar remainder loop, shorter
        "  794:\tb.ne\t790 <dot_autovec+0x10>",
        "  798:\tret",
    ]
    insns = peak.parse_instructions("\n".join(lines) + "\n")
    loop = micro.hot_loop_for("autovec", insns)
    assert any(t.startswith("sdot") for t in loop)
    assert (
        len(micro.hot_loop_for("scalar", insns)) == 2
    )  # scalar: the innermost loop, whatever it is


def test_a_function_without_a_loop_fails_every_check():
    insns = peak.parse_instructions(objdump(["mov\tx0, #0x0", "ret"]))
    for variant in micro.VARIANTS:
        loop = micro.hot_loop_for(variant, insns)
        assert loop == [] and not micro.check_loop(variant, loop, [t for _, t in insns])["ok"]


def test_an_unconditional_backward_branch_is_not_a_loop_here_either():
    lines = ["0000000000000780 <f>:", "  780:\tnop", "  784:\tsdot\tv0.4s, v1.16b, v2.16b",
             "  788:\tb\t784 <f+0x4>"]  # fmt: skip
    insns = peak.parse_instructions("\n".join(lines) + "\n")
    assert micro.hot_loop_for("sdot_a4", insns) == []


# --- the CSV and the command line --------------------------------------------------------------


def test_the_csv_has_every_column_in_order_and_blank_cells_for_missing_values(tmp_path):
    rows = micro.derive_rows(MicroRecord.from_dict(micro_record()))
    out = tmp_path / "micro.csv"
    micro.write_csv(out, rows)
    table = list(csv.DictReader(out.open(encoding="utf8")))
    assert list(table[0]) == micro.MICRO_COLUMNS
    assert len(table) == 16
    scalar_l1 = next(r for r in table if r["variant"] == "scalar" and r["working_set"] == "L1")
    assert scalar_l1["fraction_of_peak"] == "" and scalar_l1["fraction_of_B"] == ""
    assert scalar_l1["is_best"] == "True" and scalar_l1["speedup_vs_scalar"] == "1.0"


def test_the_command_line_turns_the_newest_record_into_micro_csv(tmp_path, capsys):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "2026-11-05T0900Z.json").write_text(json.dumps(micro_record(failed={"sve_a8"})))
    newer = micro_record()
    newer["session_id"] = "2026-11-05T1000Z"
    (raw / "2026-11-05T1000Z.json").write_text(json.dumps(newer))
    assert micro.newest_record(raw).name == "2026-11-05T1000Z.json"
    assert (
        micro.main(["--record", str(raw / "2026-11-05T1000Z.json"), "--out-dir", str(tmp_path)])
        == 0
    )
    assert (tmp_path / "micro.csv").exists()
    out = capsys.readouterr().out
    assert "sdot_a8" in out and "best of family" in out and "2 MACs per weight byte" in out


def test_the_summary_table_says_when_a_disassembly_check_failed():
    rows = micro.derive_rows(MicroRecord.from_dict(micro_record(failed={"sve_a8"})))
    assert "DISASSEMBLY CHECK FAILED" in "\n".join(micro.summary_lines(rows))


# --- run_micro: the program's output -> points; the run's gating ------------------------------


def program_result(variant="sdot_a8", ws="L1", ns=128.0):
    pt = make_point(variant, ws, ns)
    return {
        "variant": variant, "family": pt["family"], "accumulators": pt["accumulators"],
        "working_set": ws, "rows": pt["rows"], "k": pt["k"], "weight_bytes": float(pt["weight_bytes"]),
        "macs_per_weight_byte": pt["macs_per_weight_byte"], "calls_per_rep": pt["calls_per_rep"],
        "reps_warmup": 3, "reps_timed": 30, "observed_cpu": 0, "getcpu_ok": True,
        "output_matches_scalar": True, "checksum": "0x1",
        "samples_ns_per_call": pt["samples_ns_per_call"],
    }  # fmt: skip


def test_to_point_computes_the_summary_and_the_mac_count():
    run = {"process_cpus": [0], "pinned": True}
    pt = run_micro.to_point(run, program_result("smmla_a8", "L1", 100.0))
    assert pt["macs_per_call"] == 2 * 4 * 4096 and pt["pinning"]["getcpu_ok"] is True
    assert MicroPoint.from_dict(pt).median_ns == pytest.approx(100.0)
    run["pinned"] = False  # the program could not pin: the point is invalid
    bad = run_micro.to_point(run, program_result())
    with pytest.raises(SchemaError, match="pin check"):
        MicroPoint.from_dict(bad)


def fake_main(tmp_path, monkeypatch, check_ok=True, failed=(), dram_ns=None):
    """run_micro.main with the compile, the program runs, objdump and the reference files replaced."""
    calls = []

    def fake_run_program(args, core=0):
        calls.append(args[0])
        if args[0] == "--check":
            variants = [{"variant": v, "cases": 66, "mismatches": 0 if check_ok else 1}
                        for v in micro.VARIANTS]  # fmt: skip
            return {"mode": "check", "ok": check_ok, "cases": 66, "variants": variants}, (
                0 if check_ok else 1
            )
        rec = micro_record(dram_ns=dram_ns)
        pts = [{**program_result(p["variant"], p["working_set"], p["median_ns"]),
                "samples_ns_per_call": p["samples_ns_per_call"],
                "calls_per_rep": p["calls_per_rep"]} for p in rec["points"]]  # fmt: skip
        return {"sve_vector_bits": 128, "features": {"sve": True}, "process_cpus": [0],
                "pinned": True, "points": pts}, 0  # fmt: skip

    monkeypatch.setattr(run_micro, "ensure_binary", lambda: {"sha256": "x"})
    monkeypatch.setattr(run_micro, "run_program", fake_run_program)
    monkeypatch.setattr(
        run_micro, "check_disassembly", lambda binary, d=None: micro_record(failed=failed)["disasm"]
    )
    monkeypatch.setattr(run_micro, "latest_bandwidth_record", lambda: ("bw", "BW"))
    monkeypatch.setattr(run_micro.PeakRecord, "from_dict", staticmethod(lambda d: "PK"))
    monkeypatch.setattr(run_micro, "build_references", lambda *a: micro_record()["references"])
    monkeypatch.setattr(run_micro.common, "current_session_id", lambda: "S")
    peak_file = tmp_path / "peak.json"
    peak_file.write_text("{}")
    out = tmp_path / "micro"
    code = run_micro.main(["--peak-record", str(peak_file), "--out-dir", str(out)])
    return code, out, calls


def test_a_failed_check_means_nothing_is_timed_or_saved(tmp_path, monkeypatch, capsys):
    code, out, calls = fake_main(tmp_path, monkeypatch, check_ok=False)
    assert code == 1 and calls == ["--check"]  # --time never ran
    assert not out.exists()
    assert "Nothing was timed" in capsys.readouterr().err


def test_a_good_run_saves_a_valid_record_and_prints_the_table(tmp_path, monkeypatch, capsys):
    code, out, calls = fake_main(tmp_path, monkeypatch)
    assert code == 0 and calls == ["--check", "--time"]
    rec = MicroRecord.from_dict(json.loads((out / "S.json").read_text()))
    assert rec.references["peak_record"]["C_sdot_ops_per_s"] == C_SDOT
    assert "best of family" in capsys.readouterr().out


def test_a_failed_loop_check_saves_the_record_then_fails(tmp_path, monkeypatch, capsys):
    code, out, _ = fake_main(tmp_path, monkeypatch, failed={"smmla_a4"})
    assert code == 1 and (out / "S.json").exists()  # the data are kept
    assert "smmla_a4" in capsys.readouterr().err


def test_an_existing_record_is_not_overwritten(tmp_path, monkeypatch):
    code, out, _ = fake_main(tmp_path, monkeypatch)
    assert code == 0
    before = (out / "S.json").read_text()
    assert (
        run_micro.main(["--peak-record", str(tmp_path / "peak.json"), "--out-dir", str(out)]) == 0
    )
    assert (out / "S.json").read_text() == before and list(out.iterdir()) == [out / "S.json"]


# --- the references: the real committed records ------------------------------------------------


def test_the_newest_valid_bandwidth_record_is_chosen_by_capture_time():
    path, rec = run_micro.latest_bandwidth_record()
    every = {}
    for p in run_micro.BANDWIDTH_DIR.glob("*.json"):
        try:
            r = run_micro.BandwidthRecord.from_dict(json.loads(p.read_text()))
        except (SchemaError, ValueError, KeyError, TypeError):
            continue
        if r.validity:
            every[p] = r.captured_utc
    assert rec.captured_utc == max(every.values()) and path in every


def test_the_real_references_are_b1_and_c1_by_the_roofline_rules():
    from edge_llm import roofline

    path, bw = run_micro.latest_bandwidth_record()
    pk_path = run_micro.REPO_ROOT / roofline.PEAK_RECORD
    pk = run_micro.PeakRecord.from_dict(json.loads(pk_path.read_text()))
    ref = run_micro.build_references(path, bw, pk_path, pk)
    b = ref["bandwidth_record"]
    assert 20e9 < b["B_one_stream_Bps"] < b["B_best_Bps"] < 45e9  # one core: tens of GB/s
    assert b["sha256"] == run_micro.sha256_file(path)
    c = ref["peak_record"]
    assert c["C_smmla_ops_per_s"] == pytest.approx(2 * c["C_sdot_ops_per_s"], rel=0.05)
    assert 300e9 < c["C_sdot_ops_per_s"] < 450e9  # CLAUDE.md §11: SDOT 382 GOPS per core
    MicroRecord.from_dict({**micro_record(), "references": ref})  # and the schema accepts them
