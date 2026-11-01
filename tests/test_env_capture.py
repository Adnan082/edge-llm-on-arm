"""env_capture: parsing helpers on synthetic text, plus one hardware check for the VM."""

import json
from datetime import UTC, datetime

import pytest

from bench import common, env_capture

CPUINFO = """processor\t: 0
BogoMIPS\t: 2000.00
Features\t: fp asimd evtstrm aes asimddp sve sve2 i8mm bf16
CPU implementer\t: 0x41

processor\t: 1
Features\t: this second block must be ignored
"""


def test_session_id_format():
    when = datetime(2026, 11, 4, 9, 7, 55, tzinfo=UTC)
    assert env_capture.make_session_id(when) == "2026-11-04T0907Z"


def test_cpuinfo_features_come_from_first_cpu_only():
    feats = env_capture.parse_cpuinfo_features(CPUINFO)
    assert feats == ["fp", "asimd", "evtstrm", "aes", "asimddp", "sve", "sve2", "i8mm", "bf16"]


def test_key_flag_presence_is_exact_match_not_substring():
    # "sve2" being present must not make "sve" or "sme" true by accident.
    flags = env_capture.key_flag_presence(["asimd", "sve2"])
    assert flags["asimd"] and flags["sve2"]
    assert not flags["sve"] and not flags["sme"] and not flags["i8mm"]


def test_cpuinfo_without_features_line():
    assert env_capture.parse_cpuinfo_features("processor : 0\n") == []


def test_threads_per_core_from_lscpu_json():
    lscpu = {"lscpu": [{"field": "Thread(s) per core:", "data": "1"}]}
    assert env_capture.threads_per_core(lscpu) == "1"
    assert env_capture.threads_per_core(None) is None


def test_parse_cmake_cache_keeps_only_wanted_keys():
    cache = (
        "// A comment\n"
        "GGML_CPU_KLEIDIAI:BOOL=ON\n"
        "CMAKE_BUILD_TYPE:STRING=Release\n"
        "UNRELATED:STRING=x\n"
        "# CMAKE_C_FLAGS:STRING=ignored comment\n"
    )
    assert env_capture.parse_cmake_cache(cache) == {
        "GGML_CPU_KLEIDIAI": "ON",
        "CMAKE_BUILD_TYPE": "Release",
    }


def test_parse_sha256sums():
    good = "a" * 64
    text = f"{good}  qwen3-0.6b-f16.gguf\n{good} *other.gguf\nnot-a-hash  bad.gguf\n"
    assert env_capture.parse_sha256sums(text) == {
        "qwen3-0.6b-f16.gguf": good,
        "other.gguf": good,
    }


def test_capture_has_every_item_the_spec_requires():
    record = env_capture.capture("2026-11-04T0907Z", "start")
    for key in (
        "machine",  # machine type and zone
        "cpu",  # lscpu + feature flags + governor
        "os",  # kernel
        "compilers",
        "llama_cpp",  # commit
        "builds",  # flags + system-info line
        "model_sha256",
        "sve_vector_length",
        "captured_utc",  # date/time (UTC)
        "loadavg_1_5_15",
        "repo",
    ):
        assert key in record
    assert record["cpu"]["governor"]  # a value or the literal "not exposed", never empty


def test_cmake_cache_keys_match_the_pinned_commit():
    # GGML_CPU_AARCH64 was renamed GGML_CPU_REPACK; LLAMA_CURL is deprecated (ggml/CMakeLists.txt,
    # CMakeLists.txt at ddf48f8).
    assert "GGML_CPU_REPACK" in env_capture.CACHE_KEYS
    assert "GGML_CPU_AARCH64" not in env_capture.CACHE_KEYS
    assert "LLAMA_CURL" not in env_capture.CACHE_KEYS
    cache = "GGML_CPU_REPACK:BOOL=ON\nGGML_CPU_AARCH64:BOOL=ON\n"
    assert env_capture.parse_cmake_cache(cache) == {"GGML_CPU_REPACK": "ON"}


def test_main_refuses_to_overwrite_a_raw_record(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "SESSION_FILE", tmp_path / "work" / "session_id")
    monkeypatch.setattr(
        "sys.argv",
        ["env_capture", "--session-id", "S", "--out-dir", str(tmp_path)],
    )
    assert env_capture.main() == 0
    assert (tmp_path / "S.json").exists()
    assert env_capture.main() == 1  # second run must not touch the first file


def test_start_saves_the_session_id_and_end_reuses_it(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "SESSION_FILE", tmp_path / "work" / "session_id")
    out = ["--out-dir", str(tmp_path)]
    monkeypatch.setattr("sys.argv", ["env_capture", *out])
    assert env_capture.main() == 0
    sid = common.current_session_id()
    assert (tmp_path / f"{sid}.json").exists()

    monkeypatch.setattr("sys.argv", ["env_capture", "--phase", "end", *out])
    assert env_capture.main() == 0
    assert (tmp_path / f"{sid}_end.json").exists()  # same session, no new id invented
    assert json.loads((tmp_path / f"{sid}_end.json").read_text())["session_id"] == sid


def test_record_dirty_flag_ignores_results_but_not_code():
    # The helper every recorder uses (bench.common.git_state) drives the record's `dirty`.
    assert env_capture.git_state is common.git_state
    assert common.is_dirty("?? results/raw/env/x.json\n") is False
    assert common.is_dirty(" M bench/env_capture.py\n") is True


def test_system_info_line_comes_from_the_newest_check_builds_record(tmp_path):
    def rec(line):
        return json.dumps({"builds": {"kleidiai": {"system_info_line": line}}})

    (tmp_path / "2026-11-02T0900Z_check_builds.json").write_text(rec("old"))
    (tmp_path / "2026-11-03T0900Z_check_builds.json").write_text(rec("new"))
    assert env_capture.latest_system_info("kleidiai", tmp_path) == "new"
    assert env_capture.latest_system_info("baseline", tmp_path) is None
    assert env_capture.latest_system_info("kleidiai", tmp_path / "missing") is None


@pytest.mark.hardware
def test_vm_is_arm_with_dotprod_and_no_smt():
    cpu = env_capture.cpu_info()
    assert env_capture.platform.machine() == "aarch64"
    assert cpu["key_flags"]["asimddp"]
    assert cpu["threads_per_core"] == "1"  # spec §5: one vCPU = one core (verify)
