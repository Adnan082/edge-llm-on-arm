"""Day 7 checks that need the Arm VM: run with `make test PYTEST_ARGS="-m hardware"`."""

import pytest

from edge_llm import micro
from micro import run_micro

pytestmark = pytest.mark.hardware


@pytest.fixture(scope="module")
def binary():
    run_micro.ensure_binary()  # compiles on the VM; raises if the flags or the code are wrong
    return run_micro.BINARY


def test_every_simd_variant_gives_the_same_integer_result_as_scalar(binary):
    out, code = run_micro.run_program(["--check", "--seeds", "6"])
    assert code == 0 and out["ok"] is True and out["cases"] > 0
    by_name = {v["variant"]: v for v in out["variants"]}
    assert set(by_name) == set(micro.VARIANTS)  # all eight are compiled in
    for name, v in by_name.items():
        assert (
            v["mismatches"] == 0
        ), f"{name}: differs from scalar (first at case {v['first_case']})"
        assert v["cases"] > 0 and v["skipped"] == 0, f"{name}: {v}"  # K = 4096 and 1152 fit all


def test_every_hot_loop_holds_its_instruction(binary, tmp_path):
    out = run_micro.check_disassembly(run_micro.BINARY, tmp_path)
    for variant, check in out.items():
        assert check["ok"], f"{variant}: {check}"
    assert out["scalar"]["simd_multiply_in_loop"] == []
    assert out["scalar"]["simd_multiply_in_function"] == []
    for variant in ("sdot_a4", "sdot_a8", "smmla_a4", "smmla_a8", "sve_a4", "sve_a8"):
        assert out[variant]["found"] == micro.VARIANTS[variant][1]
    # information, not a limit: which instructions GCC chose for the plain-C loop
    print("autovec loop:", out["autovec"]["mnemonics"], out["autovec"]["simd_multiply_in_loop"])
    assert (tmp_path / "dot_int8_smmla_a8.s").read_text().count("smmla") >= 8


def test_a_short_timing_run_is_pinned_and_every_output_matches_scalar(binary):
    out, code = run_micro.run_program(
        ["--time", "--sets", "L1", "--reps", "3", "--warmup", "1", "--target-ms", "5"]
    )
    assert code == 0 and out["pinned"] is True and out["process_cpus"] == [0]
    assert {p["variant"] for p in out["points"]} == set(micro.VARIANTS)
    for p in out["points"]:
        assert p["output_matches_scalar"] and p["getcpu_ok"] and p["observed_cpu"] == 0, p[
            "variant"
        ]
        assert all(s > 0 for s in p["samples_ns_per_call"]) and p["checksum"].startswith("0x")
        assert p["calls_per_rep"] >= 1 and p["rows"] == 4 and p["weight_bytes"] == 16384


def test_a_small_dram_run_streams_the_packed_smmla_layout_correctly(binary):
    out, code = run_micro.run_program(
        ["--time", "--sets", "DRAM", "--dram-mib", "64", "--reps", "2", "--warmup", "1",
         "--variants", "scalar,sdot_a8,smmla_a8,sve_a8"]
    )  # fmt: skip
    assert code == 0
    for p in out["points"]:
        assert p["output_matches_scalar"], p["variant"]
        assert p["rows"] == 64 * 256 and p["calls_per_rep"] >= 1
