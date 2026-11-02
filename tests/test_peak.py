"""Peak throughput: operations per instruction, C(t), the hot-loop check and the peak record."""

import copy
import json
import re

import pytest

from edge_llm import peak
from edge_llm.schema import GgmlInstructionRecord, PeakPoint, PeakRecord, SchemaError
from micro import run_peak
from tests.bench_fixtures import REJECTED_PEAK, disasm_section

# --- the operation counts (CLAUDE.md §8: one multiply-accumulate = 2 operations) --------------


def test_operations_per_instruction_are_the_spec_numbers():
    assert peak.OPS_PER_INSTRUCTION == {
        "sdot": 32,
        "smmla": 64,
        "fmla_f16": 16,
        "fmlal": 8,
        "fma32": 8,
    }


def test_the_counts_follow_from_the_instruction_shapes():
    # SDOT: 4 lanes x a 4-way int8 dot = 16 MACs; SMMLA: a 2x8 by 8x2 tile = 2*2*8 = 32 MACs;
    # FP16 FMLA: 8 lanes; FMLALB or FMLALT: 4 widened lanes of a 128-bit vector;
    # F32 FMLA: 4 lanes of a 128-bit vector
    macs = {"sdot": 4 * 4, "smmla": 2 * 2 * 8, "fmla_f16": 8, "fmlal": 4, "fma32": 4}
    assert {k: 2 * v for k, v in macs.items()} == peak.OPS_PER_INSTRUCTION


def test_only_the_sve_class_scales_with_the_vector_length():
    assert peak.ops_per_instruction("fmlal", 128) == 8
    assert peak.ops_per_instruction("fmlal", 256) == 16
    for cls in ("sdot", "smmla", "fmla_f16", "fma32"):
        assert peak.ops_per_instruction(cls, 256) == peak.OPS_PER_INSTRUCTION[cls]


# --- the program's output -> a point -----------------------------------------------------------


def fake_run(t=1, cls="sdot", acc=16, base=1.0e10, reps=20, sve_bits=128, instr_per_iter=None):
    instr_per_iter = instr_per_iter or acc * run_peak.INSTR_PER_ACC[cls]
    return {
        "threads": t,
        "sve_vector_bits": sve_bits,
        "process_cpus": list(range(t)),
        "taskset_cpus": f"0-{t - 1}",
        "returncode": 0,
        "results": [
            {
                "class": cls,
                "accumulators": acc,
                "instr_per_iter": instr_per_iter,
                "iters": 1000,
                "reps_warmup": 3,
                "reps_timed": reps,
                "getcpu_ok": True,
                "checksum": "0x1",
                "observed_cpus": list(range(t)),
                "samples_instr_per_s": [base * t * (1 + 0.001 * (i % 4)) for i in range(reps)],
            }
        ],
    }


def test_to_point_multiplies_instructions_by_ops_per_instruction():
    run = fake_run(cls="smmla")
    pt = run_peak.to_point(run, run["results"][0])
    assert pt["ops_per_instruction"] == 64
    assert pt["samples_ops_per_s"][0] == pytest.approx(pt["samples_instr_per_s"][0] * 64)
    assert PeakPoint.from_dict(pt).median == pytest.approx(pt["median"])


def test_the_sve_class_uses_the_reported_vector_length():
    run = fake_run(cls="fmlal", sve_bits=256)
    assert run_peak.to_point(run, run["results"][0])["ops_per_instruction"] == 16


def test_a_point_needs_enough_repeats_and_a_consistent_conversion():
    run = fake_run(reps=10)
    with pytest.raises(SchemaError, match="at least 20"):
        PeakPoint.from_dict(run_peak.to_point(run, run["results"][0]))
    run = fake_run()
    pt = run_peak.to_point(run, run["results"][0])
    pt["ops_per_instruction"] = 16  # the stored ops/s no longer follow
    with pytest.raises(SchemaError, match="ops/s is not"):
        PeakPoint.from_dict(pt)
    pt = run_peak.to_point(run, run["results"][0])
    pt["median"] *= 1.1
    with pytest.raises(SchemaError, match="median"):
        PeakPoint.from_dict(pt)


# --- C(t): the best median over the chain counts that passed the disassembly check ------------


def build_points(rates=None, threads=(1, 2, 4, 8)):
    """Points for every class, thread count and chain count; `rates[(cls, t, acc)]` or
    `rates[(cls, acc)]` sets the per-thread instructions/s."""
    rates = rates or {}
    pts = []
    for cls in peak.PEAK_CLASSES:
        for t in threads:
            for acc in peak.CHAIN_COUNTS:
                base = rates.get((cls, t, acc), rates.get((cls, acc), 1.0e10))
                run = fake_run(t, cls, acc, base)
                pts.append(run_peak.to_point(run, run["results"][0]))
    return pts


def objs(points):
    return [PeakPoint.from_dict(p) for p in points]


def all_valid():
    return {cls: set(peak.CHAIN_COUNTS) for cls in peak.PEAK_CLASSES}


def test_c_of_t_is_the_best_median_over_the_chain_counts_at_every_thread_count():
    rates = {("sdot", 1, 28): 1.2e10, ("sdot", 4, 8): 1.1e10}  # per-thread instructions/s
    summary = peak.c_summary(objs(build_points(rates)), all_valid())
    assert summary["sdot"]["1"]["accumulators"] == 28
    assert summary["sdot"]["4"]["accumulators"] == 8
    c = peak.c_of_t(summary)
    assert set(c) == set(peak.PEAK_CLASSES) and set(c["sdot"]) == {1, 2, 4, 8}
    assert c["sdot"][1] == pytest.approx(32 * 1.2e10 * 1.0015, rel=1e-3)  # 32 ops x instr/s
    assert c["sdot"][4] == pytest.approx(32 * 4 * 1.1e10 * 1.0015, rel=1e-3)
    assert c["smmla"][8] == pytest.approx(64 * 8 * 1.0e10 * 1.0015, rel=1e-3)


def test_c_summary_keeps_every_median_as_information():
    rates = {("fma32", 1, 8): 0.6e10, ("fma32", 1, 28): 1.2e10}
    s = peak.c_summary(objs(build_points(rates)), all_valid())["fma32"]["1"]
    assert s["by_accumulators"].keys() == {"8", "16", "28"}
    assert s["by_accumulators"]["28"] / s["by_accumulators"]["16"] == pytest.approx(1.2, rel=1e-3)
    assert s["median"] == s["by_accumulators"]["28"]


def test_a_tie_goes_to_the_smaller_chain_count():
    s = peak.c_summary(objs(build_points()), all_valid())  # all counts equal
    assert all(v["accumulators"] == 8 for by_t in s.values() for v in by_t.values())


def test_a_chain_count_whose_loop_failed_the_check_does_not_count():
    rates = {("fmla_f16", 28): 2.0e10}  # fastest, but its loop is not what was assumed
    valid = all_valid() | {"fmla_f16": {8, 16}}
    s = peak.c_summary(objs(build_points(rates)), valid)["fmla_f16"]
    assert all(v["accumulators"] != 28 for v in s.values())
    assert all(v["by_accumulators"].keys() == {"8", "16", "28"} for v in s.values())  # kept


def test_a_class_without_any_valid_loop_has_no_c_of_t():
    valid = all_valid() | {"smmla": set()}
    s = peak.c_summary(objs(build_points()), valid)
    assert "smmla" not in s and "sdot" in s


def test_valid_chain_counts_reads_the_disassembly_checks():
    disasm = {
        "sdot": {
            "checks": [
                {"accumulators": 8, "ok": True},
                {"accumulators": 16, "ok": False},
                {"accumulators": 28, "ok": True},
            ]
        }
    }
    assert peak.valid_chain_counts(disasm) == {"sdot": {8, 28}}


# --- disassembly: finding the hot loop and checking it -----------------------------------------


def objdump(body, name="peak_sdot_a8"):
    lines = [f"0000000000000780 <{name}>:"]
    addr = 0x780
    for text in body:
        lines.append(f"  {addr:x}:\t{text}")
        addr += 4
    return "\n".join(lines) + "\n"


def sdot_function(n, extra=()):
    body = ["movi\tv0.4s, #0x1", "dup\tv31.16b, w1"]
    loop_start = 0x780 + 4 * len(body)
    body += [f"sdot\tv{i}.4s, v30.16b, v31.16b" for i in range(n)]
    body += list(extra)
    body += ["subs\tx0, x0, #0x1", f"b.ne\t{loop_start:x} <peak_sdot_a8+0x8>", "ret"]
    return objdump(body)


def loop_of(text):
    return peak.hot_loop(peak.parse_instructions(text))


def test_the_hot_loop_is_everything_from_the_branch_target_to_the_branch():
    loop = loop_of(sdot_function(8))
    assert len(loop) == 8 + 2 and loop[0].startswith("sdot") and loop[-1].startswith("b.ne")
    assert "ret" not in loop and not any(i.startswith("movi") for i in loop)


def test_a_function_without_a_backward_branch_has_no_loop():
    assert loop_of(objdump(["movi\tv0.4s, #0x1", "ret"])) == []


def test_a_good_loop_passes():
    check = peak.check_loop("sdot", loop_of(sdot_function(8)), 8, 8)
    assert check["ok"] and check["counts"] == {"sdot": 8}


def test_a_loop_with_the_wrong_instruction_or_count_fails():
    loop = loop_of(sdot_function(8))
    assert not peak.check_loop("smmla", loop, 8, 8)["ok"]  # wrong instruction
    assert not peak.check_loop("sdot", loop_of(sdot_function(7)), 8, 8)["ok"]  # too few
    assert not peak.check_loop("sdot", loop_of(sdot_function(16)), 8, 8)["ok"]  # unrolled twice


def test_a_loop_that_touches_memory_is_not_register_only():
    loop = loop_of(sdot_function(8, extra=["ldr\tq5, [sp, #16]"]))
    check = peak.check_loop("sdot", loop, 8, 8)
    assert not check["ok"] and check["memory_instructions"] == ["ldr q5, [sp, #16]"]


def test_fp16_fmla_counts_one_per_chain_and_matches_only_the_8h_form():
    insns = [f"fmla	v{i}.8h, v30.8h, v31.8h" for i in range(8)]
    insns += [
        "fmla	v9.4s, v30.4s, v31.4s",
        "subs	x0, x0, #0x1",
        "b.ne	788 <peak_fmla_f16_a8+0x8>",
    ]
    text = objdump(["nop", "nop"] + insns)
    check = peak.check_loop("fmla_f16", loop_of(text), 8, 8)
    assert check["counts"] == {"fmla .8h": 8} and check["ok"]


def test_every_class_expects_one_instruction_per_chain():
    assert run_peak.INSTR_PER_ACC == dict.fromkeys(peak.PEAK_CLASSES, 1)


def test_fmlal_needs_half_bottom_and_half_top():
    ins = [f"fmlalb\tz{i}.s, z30.h, z31.h" if i % 2 == 0 else f"fmlalt\tz{i}.s, z30.h, z31.h"
           for i in range(8)]  # fmt: skip
    text = objdump(["nop", "nop"] + ins + ["subs\tx0, x0, #0x1", "b.ne\t788 <peak_fmlal_a8+0x8>"])
    assert peak.check_loop("fmlal", loop_of(text), 8, 8)["ok"]
    lopsided = [f"fmlalb\tz{i}.s, z30.h, z31.h" for i in range(8)]
    text = objdump(["nop", "nop"] + lopsided + ["subs\tx0, x0, #0x1", "b.ne\t788 <x+0x8>"])
    check = peak.check_loop("fmlal", loop_of(text), 8, 8)
    assert check["counts"] == {"fmlalb": 8, "fmlalt": 0} and not check["ok"]


def test_check_disassembly_saves_one_file_per_class(tmp_path, monkeypatch):
    def fake_objdump(binary, name):
        cls = name.split("_", 1)[1].rsplit("_a", 1)[0]
        acc = int(name.rsplit("_a", 1)[1])
        n = acc * run_peak.INSTR_PER_ACC[cls]
        mnemonic = {
            "sdot": "sdot\tv{i}.4s, v30.16b, v31.16b",
            "smmla": "smmla\tv{i}.4s, v30.16b, v31.16b",
            "fmla_f16": "fmla\tv{i}.8h, v30.8h, v31.8h",
            "fma32": "fmla\tv{i}.4s, v30.4s, v31.4s",
            "fmlal": None,
        }[cls]
        if mnemonic:
            body = [mnemonic.format(i=i % 28) for i in range(n)]
        else:
            body = [
                ("fmlalb" if i % 2 == 0 else "fmlalt") + f"\tz{i}.s, z30.h, z31.h" for i in range(n)
            ]
        return objdump(
            ["nop", "nop"] + body + ["subs\tx0, x0, #0x1", "b.ne\t788 <x+0x8>", "ret"], name
        )

    monkeypatch.setattr(run_peak, "objdump_function", fake_objdump)
    out = run_peak.check_disassembly("ignored", tmp_path)
    assert set(out) == set(peak.PEAK_CLASSES)
    assert all(c["ok"] for d in out.values() for c in d["checks"])
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "peak_fma32.s", "peak_fmla_f16.s", "peak_fmlal.s", "peak_sdot.s", "peak_smmla.s"
    ]  # fmt: skip
    assert "peak_sdot_a16" in (tmp_path / "peak_sdot.s").read_text()


# --- the peak record ---------------------------------------------------------------------------


def disasm_for(failed=()):
    """A disassembly part: one passing check per chain count, except the (class, count) in failed."""
    return {
        c: {
            "file": f"micro/disasm/peak_{c}.s",
            "checks": [
                {
                    "function": f"peak_{c}_a{a}",
                    "accumulators": a,
                    "loop_instructions": a + 3,
                    "counts": {c: a},
                    "expected_per_iteration": a,
                    "ok": (c, a) not in failed,
                }
                for a in peak.CHAIN_COUNTS
            ],
        }
        for c in peak.PEAK_CLASSES
    }


def record(points=None, failed=(), **over):
    points = points or build_points()
    disasm = disasm_for(failed)
    rec = {
        "schema_version": 1,
        "kind": "peak",
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "binary": {},
        "host": {},
        "sve_vector_bits": 128,
        "points": points,
        "disasm": disasm,
        "c_of_t": peak.c_summary(objs(points), peak.valid_chain_counts(disasm)),
    }
    rec.update(over)
    return rec


def test_a_good_peak_record_validates():
    rec = PeakRecord.from_dict(copy.deepcopy(record()))
    assert len(rec.points) == len(peak.PEAK_CLASSES) * 4 * len(peak.CHAIN_COUNTS)
    assert set(rec.c_of_t) == set(peak.PEAK_CLASSES)


def test_a_record_without_a_class_is_rejected():
    r = record()
    r["points"] = [p for p in r["points"] if p["instr_class"] != "smmla"]
    with pytest.raises(SchemaError, match="every peak class"):
        PeakRecord.from_dict(r)


def test_a_record_needs_every_chain_count_at_every_thread_count():
    r = record()
    r["points"] = [
        p
        for p in r["points"]
        if not (p["instr_class"] == "sdot" and p["threads"] == 8 and p["accumulators"] == 28)
    ]
    with pytest.raises(SchemaError, match="every chain count"):
        PeakRecord.from_dict(r)


def test_a_record_with_a_failed_disassembly_check_is_kept_and_leaves_the_loop_out_of_c():
    """The data are saved (ADR-022); the failing loop just does not count."""
    rates = {("fmlal", 28): 2.0e10}
    points = build_points(rates)
    rec = PeakRecord.from_dict(record(points, failed={("fmlal", 28)}))
    assert all(v["accumulators"] != 28 for v in rec.c_of_t["fmlal"].values())
    assert any(
        v["accumulators"] == 28 for v in peak.c_summary(objs(points), all_valid())["fmlal"].values()
    )  # it would have won had it counted


def test_a_record_whose_c_of_t_includes_a_failed_loop_is_rejected():
    rates = {("fmlal", 28): 2.0e10}
    points = build_points(rates)
    r = record(points, failed={("fmlal", 28)})
    r["c_of_t"] = peak.c_summary(objs(points), all_valid())  # counted the failed loop
    with pytest.raises(SchemaError, match="c_of_t"):
        PeakRecord.from_dict(r)


def test_a_record_whose_c_of_t_is_not_the_best_median_is_rejected():
    r = record()
    r["c_of_t"]["sdot"]["1"]["median"] *= 0.5
    with pytest.raises(SchemaError, match="c_of_t"):
        PeakRecord.from_dict(r)


def test_a_record_needs_one_disassembly_check_per_chain_count():
    r = record()
    r["disasm"]["sdot"]["checks"].pop()
    with pytest.raises(SchemaError, match="one disassembly check per chain count"):
        PeakRecord.from_dict(r)


def test_a_record_needs_the_same_threads_for_every_class():
    r = record()
    r["points"] = [
        p for p in r["points"] if not (p["instr_class"] == "fmlal" and p["threads"] == 8)
    ]
    with pytest.raises(SchemaError, match="same thread counts"):
        PeakRecord.from_dict(r)


# --- F16 instructions in ggml's library (ADR-015 evidence) -------------------------------------

OBJDUMP_SAMPLE = """
0000000000001000 <ggml_vec_dot_f16>:
    1000:\tfmlalb\tz0.s, z1.h, z2.h
    1004:\tfmlalt\tz3.s, z1.h, z2.h
    1008:\tfmlalb\tz0.s, z4.h, z5.h
    100c:\tfmla\tv0.4s, v1.4s, v2.4s
    1010:\tret

0000000000002000 <tinyBLAS_f16>:
    2000:\tfmla\tv0.8h, v1.8h, v2.8h
    2004:\tfmla\tv3.8h, v4.8h, v5.h[0]
    2008:\tfmla\tv6.4h, v7.4h, v8.4h
    200c:\tfmlalb\tz9.s, z1.h, z2.h
"""


def test_count_f16_instructions_counts_each_form_and_ranks_symbols():
    counts, top = run_peak.count_f16_instructions(OBJDUMP_SAMPLE.splitlines())
    assert counts == {"fmlalb": 3, "fmlalt": 1, "fmla_8h": 2}  # .4s and .4h forms do not count
    assert top[0] == {"symbol": "ggml_vec_dot_f16", "fmlalb": 2, "fmlalt": 1, "fmla_8h": 0}
    assert top[1]["symbol"] == "tinyBLAS_f16" and top[1]["fmla_8h"] == 2


def test_the_ggml_instruction_record_needs_both_builds_and_integer_counts():
    side = {
        "files": [],
        "counts": {"fmlalb": 1, "fmlalt": 1, "fmla_8h": 0},
        "flash_attn_tiled": {"found": False},
    }
    rec = {
        "schema_version": 1,
        "kind": "ggml_f16_instructions",
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {},
        "builds": {"baseline": side, "kleidiai": side},
    }
    GgmlInstructionRecord.from_dict(rec)
    bad = copy.deepcopy(rec)
    bad["builds"]["kleidiai"]["counts"]["fmla_8h"] = "many"
    with pytest.raises(SchemaError, match="fmla_8h"):
        GgmlInstructionRecord.from_dict(bad)
    del rec["builds"]["kleidiai"]
    with pytest.raises(SchemaError, match="baseline \\+ kleidiai"):
        GgmlInstructionRecord.from_dict(rec)


def test_f32_fmla_counts_only_the_4s_form_one_per_chain():
    insns = [f"fmla\tv{i}.4s, v30.4s, v31.4s" for i in range(8)]
    insns += ["fmla\tv9.8h, v30.8h, v31.8h", "subs\tx0, x0, #0x1", "b.ne\t788 <peak_fma32_a8+0x8>"]
    text = objdump(["nop", "nop"] + insns)
    check = peak.check_loop("fma32", loop_of(text), 8, 8)
    assert check["counts"] == {"fmla .4s": 8}
    assert check["ok"]  # the stray .8h form is not an F32 FMLA and is not counted


# --- the tiled flash-attention function in ggml's library (ADR-020) ----------------------------


def fn(name, insns):
    lines = [f"0000000000004000 <{name}>:"]
    lines += [f"    {0x4000 + 4 * i:x}:\t{t}" for i, t in enumerate(insns)]
    return lines


SCALAR_GEMM = ["ldr\ts0, [x1]", "ldr\ts1, [x2]", "fmadd\ts2, s0, s1, s2", "fmadd\ts3, s0, s1, s3"]
TILED = (
    "ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)"
)


def capture(*functions):
    lines = [line for f in functions for line in f]
    return run_peak.scan_objdump(lines)[2]


def test_the_tiled_function_is_found_and_its_scalar_fmas_are_counted():
    cap = capture(
        fn(TILED, SCALAR_GEMM + ["fmla\tv0.4s, v1.4s, v2.4s", "ret"]),
        fn("other", ["fmadd\ts0, s1, s2, s3"]),
    )
    assert list(cap) == [TILED]  # `other` is not an attention function
    ev, text = run_peak.attention_evidence(cap)
    assert ev["found"] and ev["target_kind"] == "tiled"
    assert ev["counts"]["fmadd_s"] == 2 and ev["counts"]["fmla_4s"] == 1
    assert ev["counts"]["instructions"] == 6 and ev["dominant_fma"] == "scalar"
    assert "fmadd" in text and TILED in text


def test_a_vectorised_fallback_is_reported_as_vector():
    body = ["fmla\tv0.4s, v1.4s, v2.4s"] * 5 + ["fmadd\ts0, s1, s2, s3"]
    ev, _ = run_peak.attention_evidence(capture(fn(TILED, body)))
    assert ev["dominant_fma"] == "vector"
    sve = ["fmla\tz0.s, p0/m, z1.s, z2.s"] * 3
    ev, _ = run_peak.attention_evidence(capture(fn(TILED, sve)))
    assert ev["counts"]["fmla_sve_s"] == 3 and ev["dominant_fma"] == "vector"


def test_an_inlined_tiled_function_falls_back_to_the_function_it_went_into():
    f16 = "ggml_compute_forward_flash_attn_ext_f16(ggml_compute_params const*, ggml_tensor*)"
    one_chunk = "ggml_compute_forward_flash_attn_ext_f16_one_chunk(...)"
    cap = capture(fn(f16, SCALAR_GEMM), fn(one_chunk, ["fmla\tv0.4s, v1.4s, v2.4s"] * 9))
    assert one_chunk not in cap  # the per-element kernel is not the tiled one
    ev, _ = run_peak.attention_evidence(cap)
    assert ev["target_kind"] == "inlined_into_f16" and ev["counts"]["fmadd_s"] == 2


def test_a_separate_simd_gemm_symbol_is_counted_with_the_tiled_function():
    gemm = "simd_gemm(float*, float const*, float const*, int, int, int)"
    ev, _ = run_peak.attention_evidence(capture(fn(TILED, ["ret"]), fn(gemm, SCALAR_GEMM)))
    assert [s["symbol"] for s in ev["symbols"]] == [TILED, gemm]
    assert ev["counts"]["fmadd_s"] == 2


def test_no_attention_symbol_means_no_evidence_not_a_guess():
    ev, text = run_peak.attention_evidence(capture(fn("something_else", ["ret"])))
    assert ev == {"found": False, "target_kind": None, "symbols": [], "counts": {}} and text == ""


def test_scan_objdump_still_counts_the_f16_instructions_in_the_same_pass():
    cap_lines = fn(TILED, ["fmla\tv0.8h, v1.8h, v2.8h"]) + fn("g", ["fmlalb\tz0.s, z1.h, z2.h"])
    counts, top, cap = run_peak.scan_objdump(cap_lines)
    assert counts == {"fmlalb": 1, "fmlalt": 0, "fmla_8h": 1} and len(top) == 2
    assert list(cap) == [TILED]


def test_the_record_needs_the_attention_evidence_for_both_builds():
    found = {
        "found": True,
        "target_kind": "tiled",
        "symbols": [],
        "counts": {"fmadd_s": 4, "fmla_4s": 0, "fmla_sve_s": 0},
        "disasm_file": "micro/disasm/ggml_flash_attn_tiled_baseline.s",
    }
    side = {
        "files": [],
        "counts": {"fmlalb": 1, "fmlalt": 1, "fmla_8h": 0},
        "flash_attn_tiled": found,
    }
    rec = {
        "schema_version": 1,
        "kind": "ggml_f16_instructions",
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {},
        "builds": {"baseline": side, "kleidiai": copy.deepcopy(side)},
    }
    GgmlInstructionRecord.from_dict(copy.deepcopy(rec))
    del rec["builds"]["kleidiai"]["flash_attn_tiled"]
    with pytest.raises(SchemaError, match="flash_attn_tiled missing"):
        GgmlInstructionRecord.from_dict(rec)
    # not found is allowed (a stripped library), and says so
    rec["builds"]["kleidiai"]["flash_attn_tiled"] = {"found": False}
    GgmlInstructionRecord.from_dict(rec)


# --- the loop finder: conditional backward branches only ---------------------------------------


def loop_function(body_before, loop_body, after, name="f"):
    """objdump-style text: code, a loop ending in b.ne, then code that ends in an unconditional
    backward `b` (GCC's zero-iteration path returns to the code after the loop this way)."""
    lines = [f"0000000000000780 <{name}>:"]
    addr = 0x780
    for text in body_before:
        lines.append(f"  {addr:x}:\t{text}")
        addr += 4
    top = addr
    for text in loop_body:
        lines.append(f"  {addr:x}:\t{text}")
        addr += 4
    lines.append(f"  {addr:x}:\tsubs\tx0, x0, #0x1")
    addr += 4
    lines.append(f"  {addr:x}:\tb.ne\t{top:x} <{name}+0x8>")
    addr += 4
    after_top = addr
    for text in after:
        lines.append(f"  {addr:x}:\t{text.format(target=after_top)}")
        addr += 4
    return "\n".join(lines) + "\n"


def test_an_unconditional_backward_branch_is_not_a_loop():
    after = ["fadd\tv0.4s, v1.4s, v2.4s"] * 20 + ["b\t{target:x} <f+0x20>"]
    text = loop_function(["nop"], ["fmla\tv0.8h, v1.8h, v2.8h"] * 4, after)
    loop = loop_of(text)
    assert [i.split(" ")[0] for i in loop].count("fmla") == 4 and len(loop) == 6
    assert not any(i.startswith("fadd") for i in loop)  # the code after the loop is not in it


@pytest.mark.parametrize(
    "branch", ["b.ne", "b.hi", "cbnz x0,", "cbz x1,", "tbnz w2, #3,", "tbz w2, #3,"]
)
def test_every_conditional_form_ends_a_loop(branch):
    text = "\n".join(
        [
            "0000000000000780 <f>:",
            "  780:\tnop",
            "  784:\tsdot\tv0.4s, v1.16b, v2.16b",
            f"  788:\t{branch} 784 <f+0x4>",
            "  78c:\tret",
        ]
    )
    assert loop_of(text) == ["sdot v0.4s, v1.16b, v2.16b", f"{branch} 784 <f+0x4>"]


def test_a_forward_conditional_branch_is_not_a_loop():
    text = objdump(["cbz\tx0, 790 <f+0x10>", "sdot\tv0.4s, v1.16b, v2.16b", "nop", "nop", "ret"])
    assert loop_of(text) == []


def test_the_innermost_loop_holding_the_expected_instruction_wins():
    lines = [
        "0000000000000780 <f>:",
        "  780:\tmov\tx1, #0x0",
        "  784:\tfadd\tv9.4s, v9.4s, v9.4s",  # outer loop starts here
        "  788:\tsdot\tv0.4s, v1.16b, v2.16b",  # inner loop starts here
        "  78c:\tsdot\tv3.4s, v1.16b, v2.16b",
        "  790:\tsubs\tx0, x0, #0x1",
        "  794:\tb.ne\t788 <f+0x8>",
        "  798:\tsubs\tx1, x1, #0x1",
        "  79c:\tb.ne\t784 <f+0x4>",
        "  7a0:\tret",
    ]
    text = "\n".join(lines) + "\n"
    insns = peak.parse_instructions(text)
    inner = peak.hot_loop(insns, contains=peak.expected_pattern("sdot"))
    assert len(inner) == 4 and inner[0].startswith("sdot") and inner[-1].startswith("b.ne")
    assert len(peak.hot_loop(insns)) == 4  # innermost overall is the same loop here


def test_a_loop_holding_the_expected_instruction_beats_a_shorter_one_that_does_not():
    lines = [
        "0000000000000780 <f>:",
        "  780:\tnop",
        "  784:\tsubs\tx2, x2, #0x1",  # a short loop of bookkeeping
        "  788:\tb.ne\t784 <f+0x4>",
        "  78c:\tsdot\tv0.4s, v1.16b, v2.16b",
        "  790:\tsdot\tv3.4s, v1.16b, v2.16b",
        "  794:\tsubs\tx0, x0, #0x1",
        "  798:\tb.ne\t78c <f+0xc>",
        "  79c:\tret",
    ]
    insns = peak.parse_instructions("\n".join(lines) + "\n")
    assert len(peak.hot_loop(insns, contains=peak.expected_pattern("sdot"))) == 4
    assert len(peak.hot_loop(insns)) == 2  # without a hint the shortest loop is returned
    # if no loop has the instruction, the innermost loop is returned so the caller can report it
    assert len(peak.hot_loop(insns, contains=peak.expected_pattern("smmla"))) == 2


# --- regression: the real listings from the VM (committed under results/raw/) -----------------
# The first versions of the checker took the unconditional `b` that ends the zero-iteration path
# as the loop's end and examined the code after the loop. These are the files that exposed it.


def real_loop(file, cls, acc):
    name = f"peak_{cls}_a{acc}"
    insns = peak.parse_instructions(disasm_section(REJECTED_PEAK / file, name))
    return peak.hot_loop(insns, contains=peak.expected_pattern(cls))


@pytest.mark.parametrize(("acc", "count"), [(8, 16), (16, 32), (28, 56)])
def test_the_real_fp16_fmla_loops_hold_two_fmla_per_chain_in_the_first_version(acc, count):
    loop = real_loop("peak_fmla_f16.s", "fmla_f16", acc)
    assert sum(1 for i in loop if re.match(r"^fmla\s+v\d+\.8h", i)) == count
    assert count + 3 <= len(loop) <= count + 6  # the FMLAs, add, cmp, b.ne, a few register moves
    assert loop[-1].startswith("b.ne")


@pytest.mark.parametrize(("acc", "each"), [(8, 4), (16, 8), (28, 14)])
def test_the_real_fmlal_loops_hold_half_fmlalb_and_half_fmlalt(acc, each):
    loop = real_loop("peak_fmlal.s", "fmlal", acc)
    assert sum(1 for i in loop if i.startswith("fmlalb ")) == each
    assert sum(1 for i in loop if i.startswith("fmlalt ")) == each
    assert peak.check_loop("fmlal", loop, acc, acc)["ok"]


@pytest.mark.parametrize("cls", ["sdot", "smmla", "fma32"])
@pytest.mark.parametrize("acc", [8, 16, 28])
def test_the_other_real_loops_hold_one_instruction_per_chain_and_no_memory(cls, acc):
    loop = real_loop(f"peak_{cls}.s", cls, acc)
    check = peak.check_loop(cls, loop, acc, acc)
    assert check["ok"] and sum(check["counts"].values()) == acc
    assert check["memory_instructions"] == [] and len(loop) == acc + 3


def test_the_real_fmla_f16_loop_is_not_the_code_after_it():
    """The checker used `b 308c` at 0x313c: the 45 instructions after the loop, with no fmla."""
    text = disasm_section(REJECTED_PEAK / "peak_fmla_f16.s", "peak_fmla_f16_a8")
    insns = peak.parse_instructions(text)
    assert any(t.startswith("b ") and a == 0x313C for a, t in insns)  # the unconditional jump
    loop = real_loop("peak_fmla_f16.s", "fmla_f16", 8)
    first = next(a for a, t in insns if t == loop[0])
    assert first == 0x3040 and loop[-1].startswith("b.ne") and "3040" in loop[-1]


def test_a_loop_without_the_expected_instruction_is_rejected():
    junk = ["mov\tv0.16b, v1.16b"] * 20
    text = loop_function(["nop"], junk, [])
    for cls, acc in (("fmla_f16", 8), ("fmlal", 8)):
        check = peak.check_loop(cls, loop_of(text), acc, acc)
        assert not check["ok"] and sum(check["counts"].values()) == 0


# --- the run: the record is written before any failure is reported (ADR-022) -------------------


def fake_peak_main(tmp_path, monkeypatch, failed=(), rates=None):
    """run_peak.main with the compile, objdump and program runs replaced; returns (exit code,
    out dir)."""
    rates = rates or {}

    def fake_check(binary, disasm_dir=None):
        return disasm_for(failed)

    def fake_run_once(t, extra):
        accs = [int(a) for a in extra[extra.index("--acc") + 1].split(",")]
        run = fake_run(t, "sdot", accs[0])
        run["results"] = []
        for cls in peak.PEAK_CLASSES:
            for acc in accs:
                r = fake_run(t, cls, acc, rates.get((cls, t, acc), 1.0e10))["results"][0]
                run["results"].append(r)
        return run

    monkeypatch.setattr(run_peak, "ensure_binary", lambda: {"sha256": "x"})
    monkeypatch.setattr(run_peak, "check_disassembly", fake_check)
    monkeypatch.setattr(run_peak, "run_once", fake_run_once)
    monkeypatch.setattr(run_peak.common, "current_session_id", lambda: "S")
    out = tmp_path / "peak"
    monkeypatch.setattr(
        "sys.argv", ["run_peak", "--threads", "1,2", "--skip-ggml", "--out-dir", str(out)]
    )
    return run_peak.main(), out


def test_run_peak_times_every_chain_count_at_every_thread_count(tmp_path, monkeypatch):
    code, out = fake_peak_main(tmp_path, monkeypatch, rates={("sdot", 2, 28): 1.5e10})
    assert code == 0
    rec = json.loads((out / "S.json").read_text())
    assert len(rec["points"]) == len(peak.PEAK_CLASSES) * 2 * len(peak.CHAIN_COUNTS)
    assert rec["c_of_t"]["sdot"]["2"]["accumulators"] == 28
    PeakRecord.from_dict(rec)


def test_run_peak_saves_the_record_then_fails_when_a_loop_failed_its_check(
    tmp_path, monkeypatch, capsys
):
    code, out = fake_peak_main(
        tmp_path, monkeypatch, failed={("fma32", 16)}, rates={("fma32", 1, 16): 2.0e10}
    )
    assert code == 1
    rec = json.loads((out / "S.json").read_text())  # not lost
    assert rec["c_of_t"]["fma32"]["1"]["accumulators"] != 16
    assert "peak_fma32_a16" in capsys.readouterr().err


def test_run_peak_fails_but_keeps_the_record_when_a_class_has_no_valid_loop(
    tmp_path, monkeypatch, capsys
):
    code, out = fake_peak_main(tmp_path, monkeypatch, failed={("smmla", a) for a in (8, 16, 28)})
    assert code == 1 and "smmla" not in json.loads((out / "S.json").read_text())["c_of_t"]
    assert "no C(t)" in capsys.readouterr().err
