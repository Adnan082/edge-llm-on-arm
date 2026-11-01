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
from tests.test_bandwidth_wrapper import fake_result, fake_run
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


def test_run_bandwidth_main_writes_record_and_disassembly(tmp_path, monkeypatch, session):
    out = tmp_path / "bw"
    monkeypatch.setattr(run_bandwidth, "ensure_binary", lambda: {"sha256": "x"})
    monkeypatch.setattr(run_bandwidth, "thread_counts", lambda: [1, 2, 4, 8])
    monkeypatch.setattr(run_bandwidth, "objdump_read_loop", lambda: "0000 <read_slice_acc8_k1>:\n")
    calls = []

    def fake_run_once(t, extra):
        calls.append((t, tuple(extra)))
        if "--acc-check" in extra:
            streams = [int(k) for k in extra[extra.index("--streams") + 1].split(",")]
            results = [fake_result("read", 1, k, acc=a) for k in streams for a in (4, 8, 16)]
            # flat across accumulators: only the stream count changes the level
            for r in results:
                r["samples_bytes_per_s"] = [12e9] * 25
            return {"threads": 1, "results": results}
        if "--hugepage" in extra:
            run = fake_run(t, streams=())
            run["results"] = [fake_result("read", t, 1, hugepage=True)]
            return run
        return fake_run(t)

    monkeypatch.setattr(run_bandwidth, "run_once", fake_run_once)
    monkeypatch.setattr("sys.argv", ["run_bandwidth", "--phase", "start", "--out-dir", str(out)])
    assert run_bandwidth.main() == 0
    names = sorted(p.name for p in out.iterdir())
    assert names == [
        "2026-11-02T0900Z_start.json",
        "2026-11-02T0900Z_start_read_loop.s",
    ]
    rec = json.loads((out / names[0]).read_text())
    # 4 thread counts x (4 stream counts + triad) + 2 huge-page diagnostics
    assert len(rec["points"]) == 22 and rec["acc_check"]["pass"] is True
    assert [p["threads"] for p in rec["points"] if p["hugepage"]] == [1, 8]
    assert all(p["streams"] in (1, 2, 4, 8) for p in rec["points"] if p["kernel"] == "read")
    assert rec["objdump_file"].endswith("_start_read_loop.s")
    assert (8, ("--kernel", "read", "--streams", "1", "--hugepage", "--reps", "30")) in calls

    # a second `start` in the same session is skipped, never overwritten
    assert run_bandwidth.main() == 0
    assert sorted(p.name for p in out.iterdir()) == names
