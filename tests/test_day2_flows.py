"""End-to-end runs of the Day 2 recorders against fake tools and folders (no hardware).

The real programs are run on the VM; these check that the glue between them - paths, session id,
record names, schema validation, never-overwrite - works.
"""

import hashlib
import json
import subprocess

import pytest

from bench import build_record, check_builds, common
from bench.bandwidth import run_bandwidth
from edge_llm import gguf_table
from tests.test_bandwidth_wrapper import (
    fake_l1_run,
    fake_result,
    fake_run,
    read_loop_text,
    run_dict,
)
from tests.test_build_record import CMAKE_SNIPPET, cache
from tests.test_gguf_table import write_tiny


def git(repo, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def session(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "SESSION_FILE", tmp_path / "work" / "session_id")
    common.save_session_id("2026-11-02T0900Z")
    return "2026-11-02T0900Z"


# --- build record --------------------------------------------------------------------------


@pytest.fixture
def fake_builds(tmp_path, monkeypatch, session):
    work = tmp_path / "work"
    llama = work / "llama.cpp"
    (llama / "ggml/src/ggml-cpu").mkdir(parents=True)
    (llama / "ggml/src/ggml-cpu/CMakeLists.txt").write_text(CMAKE_SNIPPET)
    git(llama, "init", "-q")
    git(llama, "add", ".")
    git(llama, "commit", "-q", "-m", "pin")
    pin = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=llama, capture_output=True, text=True, check=True
    ).stdout.strip()
    (tmp_path / "pin").write_text(pin + "\n")

    tarball = b"fake kleidiai source"
    for name, kai in (("baseline", False), ("kleidiai", True)):
        b = work / f"build-{name}"
        (b / "bin").mkdir(parents=True)
        (b / "CMakeCache.txt").write_text(cache(str(b), kai))
        entry = {
            "directory": str(b),
            "file": f"{llama}/ggml/src/ggml-cpu/ggml-cpu.c",
            "command": "cc -O3 -mcpu=native -fopenmp -c x.c",
        }
        (b / "compile_commands.json").write_text(json.dumps([entry]))
        (b / "configure.log").write_text(
            "-- Using KleidiAI optimized kernels if applicable\n" if kai else "-- ARM detected\n"
        )
        for exe in build_record.BUILD_BINARIES:
            (b / "bin" / exe).write_bytes(b"binary-" + name.encode())
    kdeps = work / "build-kleidiai" / "_deps" / "kleidiai-subbuild"
    kdeps.mkdir(parents=True)
    (kdeps / "kleidiai-v1.32.0-src.tar.gz").write_bytes(tarball)

    monkeypatch.setattr(build_record, "WORK_DIR", work)
    monkeypatch.setattr(build_record, "LLAMACPP_DIR", llama)
    monkeypatch.setattr(build_record, "PIN_FILE", tmp_path / "pin")
    monkeypatch.setattr(build_record, "RECORD_DIR", tmp_path / "rec")
    monkeypatch.setattr(common, "WORK_DIR", work)
    return tmp_path, hashlib.md5(tarball).hexdigest()


def test_build_record_is_written_once_and_not_rewritten(fake_builds, capsys):
    tmp_path, tar_md5 = fake_builds
    assert build_record.check_caches() == 0
    assert build_record.write_record() == 0
    files = sorted((tmp_path / "rec").glob("*.json"))
    assert [f.name for f in files] == ["2026-11-02T0900Z_build.json"]
    rec = json.loads(files[0].read_text())
    assert rec["kleidiai"]["tag"] == "v1.32.0"
    assert rec["kleidiai"]["archive_md5_computed"] == tar_md5
    assert rec["builds"]["kleidiai"]["configure_log_kleidiai_lines"] == [
        "-- Using KleidiAI optimized kernels if applicable"
    ]
    assert rec["builds"]["baseline"]["configure_log_kleidiai_lines"] == []
    assert (
        rec["builds"]["kleidiai"]["binaries"]["llama-bench"]["sha256"]
        != rec["builds"]["baseline"]["binaries"]["llama-bench"]["sha256"]
    )
    flags = rec["builds"]["kleidiai"]["compile_flags"]["ggml_cpu"]
    assert flags["ggml/src/ggml-cpu/ggml-cpu.c"]["flags"] == ["-O3", "-mcpu=native", "-fopenmp"]

    assert build_record.write_record() == 0  # nothing changed: no second file
    assert len(list((tmp_path / "rec").glob("*.json"))) == 1
    assert "not rewriting" in capsys.readouterr().out


def test_check_caches_fails_on_a_real_difference(fake_builds):
    tmp_path, _ = fake_builds
    work = tmp_path / "work"
    for name, val in (("baseline", "ON"), ("kleidiai", "OFF")):
        p = work / f"build-{name}" / "CMakeCache.txt"
        p.write_text(p.read_text() + f"GGML_OPENMP:BOOL={val}\n")
    assert build_record.check_caches() == 1


# --- check-builds --------------------------------------------------------------------------


def test_check_builds_main_writes_a_smoke_record(tmp_path, monkeypatch, session):
    work, models, results = tmp_path / "work", tmp_path / "work" / "models", tmp_path / "results"
    models.mkdir(parents=True)
    (results / "models").mkdir(parents=True)
    gguf = write_tiny(models / "small_Q4_0.gguf", tied=True)
    table = gguf_table.build_table(gguf, "small", "Q4_0", "a" * 64, {})
    (results / "models" / "small_Q4_0.json").write_text(gguf_table.dumps_table(table))
    for b in common.BUILD_NAMES:
        (work / f"build-{b}" / "bin").mkdir(parents=True)
        (work / f"build-{b}" / "bin" / "llama-bench").write_text("")

    def fake_run_logged(cmd, timeout):
        build = "kleidiai" if "build-kleidiai" in cmd[0] else "baseline"
        kai = " KLEIDIAI = 1 |" if build == "kleidiai" else ""
        buf = "CPU_KLEIDIAI" if build == "kleidiai" else "CPU_REPACK"
        if cmd[0].endswith("llama-completion"):
            return 0, "", f"system_info: n_threads = 8 / 8 | CPU : NEON = 1 | REPACK = 1 |{kai}\n"
        err = f"load_tensors:  {buf} model buffer size =     1.00 MiB\n"
        return 0, json.dumps([{"avg_ts": 1.0}]), err

    monkeypatch.setattr(check_builds, "run_logged", fake_run_logged)
    monkeypatch.setattr(check_builds, "WORK_DIR", work)
    monkeypatch.setattr(check_builds, "MODELS_DIR", models)
    monkeypatch.setattr(check_builds, "model_list", lambda only: [("small", "Q4_0")])
    monkeypatch.setattr(common, "RESULTS_DIR", results)
    monkeypatch.setattr(common, "LLAMACPP_DIR", tmp_path / "none")
    monkeypatch.setattr("sys.argv", ["check_builds", "--out-dir", str(results / "raw" / "build")])

    assert check_builds.main() == 0
    rec = json.loads((results / "raw" / "build" / "2026-11-02T0900Z_check_builds.json").read_text())
    assert rec["purpose"] == "smoke" and rec["use_for_analysis"] is False
    assert rec["builds"]["kleidiai"]["kleidiai_flag"] == "1"
    assert rec["builds"]["baseline"]["kleidiai_flag"] is None
    assert [r["build"] for r in rec["runs"]] == ["baseline", "kleidiai"]
    assert rec["runs"][1]["buffers_mib"] == {"CPU_KLEIDIAI": 1.0}
    assert rec["runs"][0]["tensor_bytes_by_type"] == check_builds.tensor_bytes_by_type(table)
    # the model-file size is compared with the tensor table before anything runs
    assert (work / "smoke" / "2026-11-02T0900Z" / "small_Q4_0_kleidiai.stderr.txt").exists()


# --- bandwidth -----------------------------------------------------------------------------


def args_of(extra, flag):
    return [int(x) for x in extra[extra.index(flag) + 1].split(",")]


def make_fake_run_once(calls=None, l1_factors=None):
    """A run_once that honours --streams, --acc, --l1 and --hugepage like the real program."""

    def fake_run_once(t, extra):
        if calls is not None:
            calls.append((t, tuple(extra)))
        streams, accs = args_of(extra, "--streams"), args_of(extra, "--acc")
        if "--l1" in extra:
            return fake_l1_run(l1_factors, accs=accs, streams=streams)
        if "--hugepage" in extra:
            results = [fake_result("read", t, 1, a, hugepage=True) for a in accs]
            return run_dict(t, results)
        return fake_run(t, streams=streams, accs=accs)

    return fake_run_once


def run_main(out, monkeypatch, loops=None, l1_factors=None, calls=None, threads=(1, 2, 4, 8)):
    monkeypatch.setattr(run_bandwidth, "ensure_binary", lambda: {"sha256": "x"})
    monkeypatch.setattr(run_bandwidth, "thread_counts", lambda: list(threads))
    loops = loops or (lambda n: read_loop_text(n))
    monkeypatch.setattr(
        run_bandwidth,
        "disassemble_read_loops",
        lambda: {n: loops(n) for n in run_bandwidth.READ_LOOP_FUNCTIONS},
    )
    monkeypatch.setattr(run_bandwidth, "run_once", make_fake_run_once(calls, l1_factors))
    monkeypatch.setattr("sys.argv", ["run_bandwidth", "--phase", "start", "--out-dir", str(out)])
    return run_bandwidth.main()


def test_run_bandwidth_main_writes_record_and_disassembly(tmp_path, monkeypatch, session):
    out, calls = tmp_path / "bw", []
    assert run_main(out, monkeypatch, calls=calls) == 0
    names = sorted(p.name for p in out.iterdir())
    assert names == [
        "2026-11-02T0900Z_start.json",
        "2026-11-02T0900Z_start_read_loop.s",
    ]
    rec = json.loads((out / names[0]).read_text())
    # 4 thread counts x (8 variants + triad) + 2 x 2 huge-page diagnostics + 8 L1 runs
    assert len(rec["points"]) == 4 * 9 + 4 + 8
    assert [p["threads"] for p in rec["points"] if p["hugepage"]] == [1, 1, 8, 8]
    assert {(p["accumulators"], p["streams"]) for p in rec["points"] if p["l1"]} == {
        (a, k) for a in (8, 16) for k in (1, 2, 4, 8)
    }
    assert "acc_check" not in rec  # the accumulator-doubling check is gone (ADR-021)
    v = rec["validity"]
    assert v["any_valid"] is True and len(v["variants"]) == 8 and len(v["loops"]) == 8
    assert sorted(v["winners"]) == ["1", "2", "4", "8"]
    assert rec["objdump_file"].endswith("_start_read_loop.s")
    listing = (out / names[1]).read_text()
    assert all(f"# ===== {n} =====" in listing for n in run_bandwidth.READ_LOOP_FUNCTIONS)
    # every program run asks for the same 8 variants; the L1 run is at one thread
    assert (
        1,
        ("--kernel", "read", "--streams", "1,2,4,8", "--acc", "8,16", "--l1", "--reps", "30"),
    ) in calls
    assert (
        8,
        ("--kernel", "read", "--streams", "1", "--acc", "8,16", "--hugepage", "--reps", "30"),
    ) in calls

    # a second `start` in the same session is skipped, never overwritten
    assert run_bandwidth.main() == 0
    assert sorted(p.name for p in out.iterdir()) == names


def test_stack_accesses_in_a_loop_are_information_only(tmp_path, monkeypatch, session):
    out = tmp_path / "bw"
    code = run_main(
        out, monkeypatch, loops=lambda n: read_loop_text(n, spill=n.startswith("read_slice_acc16"))
    )
    assert code == 0
    rec = json.loads((out / "2026-11-02T0900Z_start.json").read_text())
    spilling = [lp["function"] for lp in rec["validity"]["loops"] if lp["stack_accesses"]]
    assert spilling == [f"read_slice_acc16_k{k}" for k in (1, 2, 4, 8)]


def test_a_variant_limited_by_its_loop_is_dropped_but_the_run_succeeds(
    tmp_path, monkeypatch, session
):
    out = tmp_path / "bw"
    assert run_main(out, monkeypatch, l1_factors={(16, 4): 1.0}) == 0
    rec = json.loads((out / "2026-11-02T0900Z_start.json").read_text())
    invalid = [
        (r["accumulators"], r["streams"]) for r in rec["validity"]["variants"] if not r["valid"]
    ]
    assert invalid == [(16, 4)]
    assert all(
        (w["accumulators"], w["streams"]) != (16, 4) for w in rec["validity"]["winners"].values()
    )


def test_with_no_valid_variant_the_record_is_written_and_the_run_fails(
    tmp_path, monkeypatch, session
):
    out = tmp_path / "bw"
    flat = {(a, k): 1.0 for a in (8, 16) for k in (1, 2, 4, 8)}
    assert run_main(out, monkeypatch, l1_factors=flat) == 1
    rec = json.loads((out / "2026-11-02T0900Z_start.json").read_text())
    assert rec["validity"]["any_valid"] is False and rec["validity"]["winners"] == {}


def test_a_loop_that_cannot_be_found_fails_the_run(tmp_path, monkeypatch, session):
    out = tmp_path / "bw"
    no_loop = "0000 <f>:" + chr(10) + "  780:" + chr(9) + "ret" + chr(10)
    code = run_main(
        out, monkeypatch, loops=lambda n: no_loop if n.endswith("acc8_k2") else read_loop_text(n)
    )
    assert code == 1
    rec = json.loads((out / "2026-11-02T0900Z_start.json").read_text())
    assert [lp["function"] for lp in rec["validity"]["loops"] if not lp["ok"]] == [
        "read_slice_acc8_k2"
    ]
