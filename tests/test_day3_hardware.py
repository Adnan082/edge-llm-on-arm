"""Day 3 checks that need the Arm VM: run with `make test PYTEST_ARGS="-m hardware"`."""

import json
import subprocess

import pytest

from bench import common, run_sweep
from bench.bandwidth import run_bandwidth
from edge_llm import peak, sweep
from edge_llm.schema import BenchRecord
from micro import run_peak

pytestmark = pytest.mark.hardware


def run_program(binary, cpus, args):
    proc = subprocess.run(
        ["taskset", "-c", cpus, str(binary), *args], capture_output=True, text=True, check=False
    )
    assert proc.stdout.strip(), proc.stderr
    return json.loads(proc.stdout), proc.returncode


# --- peak ----------------------------------------------------------------------------------


def test_every_peak_loop_contains_its_instruction_and_nothing_else(tmp_path):
    """Disassemble the real binary: each hot loop has the expected instruction, count, no memory."""
    run_peak.ensure_binary()
    out = run_peak.check_disassembly(run_peak.BINARY, tmp_path)
    for cls in peak.PEAK_CLASSES:
        for check in out[cls]["checks"]:
            assert check["ok"], f"{check['function']}: {check}"
    # and the instruction named in the spec is really there
    sdot = (tmp_path / "peak_sdot.s").read_text()
    assert "sdot" in sdot and "smmla" in (tmp_path / "peak_smmla.s").read_text()
    assert "fmlalb" in (tmp_path / "peak_fmlal.s").read_text()
    assert "fmlalt" in (tmp_path / "peak_fmlal.s").read_text()


def test_peak_runs_pinned_and_reports_positive_rates():
    run_peak.ensure_binary()
    out, code = run_program(
        run_peak.BINARY, "0-1",
        ["--threads", "2", "--small", "--reps", "3", "--warmup", "1", "--acc", "16"],
    )  # fmt: skip
    assert code == 0 and out["process_cpus"] == [0, 1]
    assert {r["class"] for r in out["results"]} == set(peak.PEAK_CLASSES)
    for r in out["results"]:
        assert r["getcpu_ok"] and r["observed_cpus"] == [0, 1]
        assert all(s > 0 for s in r["samples_instr_per_s"])
        assert r["checksum"].startswith("0x")


# --- bandwidth -----------------------------------------------------------------------------


@pytest.mark.parametrize("threads", [1, 2])
def test_k_stream_reads_reproduce_the_checksum_on_the_right_cores(threads):
    run_bandwidth.ensure_binary()
    out, code = run_program(
        run_bandwidth.BINARY, f"0-{threads - 1}",
        ["--threads", str(threads), "--kernel", "read", "--streams", "1,2,4,8", "--acc", "8,16",
         "--small", "--reps", "3", "--warmup", "1"],
    )  # fmt: skip
    assert code == 0
    assert [(r["acc"], r["streams"]) for r in out["results"]] == [
        (a, k) for a in (8, 16) for k in (1, 2, 4, 8)
    ]
    for r in out["results"]:
        assert r["checksum_ok"], f"k={r['streams']}: the sum of the buffer is wrong"
        assert r["getcpu_ok"] and r["observed_cpus"] == list(range(threads))
        assert r["hugepage"] is False and all(s > 0 for s in r["samples_bytes_per_s"])


def test_huge_page_diagnostic_runs_and_reports_how_many_pages_it_got():
    run_bandwidth.ensure_binary()
    out, code = run_program(
        run_bandwidth.BINARY, "0",
        ["--threads", "1", "--kernel", "read", "--streams", "1", "--hugepage", "--small",
         "--reps", "3", "--warmup", "1"],
    )  # fmt: skip
    assert code == 0 and len(out["results"]) == 1
    r = out["results"][0]
    assert r["hugepage"] is True and r["checksum_ok"] and r["anon_huge_kb"] >= 0


def test_process_cpus_is_the_set_the_process_started_with():
    """Day 2 bug: it was read after pinning and showed one core at every thread count."""
    run_bandwidth.ensure_binary()
    for t in (1, 4):
        out, _ = run_program(
            run_bandwidth.BINARY, f"0-{t - 1}",
            ["--threads", str(t), "--kernel", "read", "--small", "--reps", "2", "--warmup", "1"],
        )  # fmt: skip
        assert out["process_cpus"] == list(range(t))


def test_l1_validity_runs_report_passes_that_last_at_least_10_ms():
    run_bandwidth.ensure_binary()
    out, code = run_program(
        run_bandwidth.BINARY, "0",
        ["--threads", "1", "--kernel", "read", "--l1", "--streams", "1,2,4,8", "--acc", "8,16",
         "--reps", "3"],
    )  # fmt: skip
    assert code == 0
    assert sorted((r["acc"], r["streams"]) for r in out["results"]) == [
        (a, k) for a in (8, 16) for k in (1, 2, 4, 8)
    ]
    for r in out["results"]:
        assert r["l1"] is True and r["buffer_bytes"] == 32768 and r["checksum_ok"]
        assert r["passes"] >= 1 and r["bytes_per_rep"] == r["buffer_bytes"] * r["passes"]
        shortest = r["bytes_per_rep"] / max(r["samples_bytes_per_s"])
        assert shortest >= 0.010, f"acc={r['acc']} k={r['streams']}: {shortest * 1e3:.1f} ms"


def test_all_eight_read_loops_are_found_in_the_disassembly():
    """Information, not a limit: stack accesses are printed; a missing loop or no loads fails."""
    run_bandwidth.ensure_binary()
    loops = [
        run_bandwidth.check_read_loop(name, text)
        for name, text in run_bandwidth.disassemble_read_loops().items()
    ]
    assert len(loops) == 8
    for loop in loops:
        print(loop["function"], loop["loop_instructions"], loop["vector_loads"],
              len(loop["stack_accesses"]))  # fmt: skip
        assert loop["ok"], loop


# --- llama-bench accepts the command we built ----------------------------------------------


def test_llama_bench_accepts_the_sweep_command_and_runs_what_was_asked():
    """One repetition of a small point on both builds: flags valid, JSON matches the schema."""
    models = sorted(common.MODELS_DIR.glob("small_Q4_0.gguf"))
    if not models:
        pytest.skip("no small_Q4_0 model in work/models yet: run make models")
    cfg = run_sweep.load_cfg()
    pair = sweep.Pair(0, "small", "Q4_0", 1, "pp128")
    context = {"repo": common.git_state(common.REPO_ROOT), "llama_cpp": {"commit": None}}
    for point in pair.points():
        rec = run_sweep.run_call(cfg, "hardware-test", point, pair, 1, 1, context)
        BenchRecord.from_dict(rec)  # run_call already did; keep the intent visible
        row = rec["llama_bench"][0]
        assert row["n_threads"] == 1 and row["n_prompt"] == 128 and row["n_gen"] == 0
        assert str(row["flash_attn"]) == "1" and str(row["cpu_strict"]).lower() == "true"
