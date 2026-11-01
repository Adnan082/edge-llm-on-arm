"""Schemas for the build record and the check-builds (smoke) record."""

import copy

import pytest

from edge_llm.schema import BuildRecord, CheckBuildsRecord, SchemaError

PIN = "d" * 40


def build_record():
    return {
        "schema_version": 1,
        "kind": "build",
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "llama_cpp": {"commit": PIN, "dirty": False, "expected_commit": PIN},
        "kleidiai": {"tag": "v1.32.0", "url": "https://example/k.tar.gz", "md5": "0" * 32},
        "cache_diff": {"unexpected_keys": [], "kleidiai_keys": ["GGML_CPU_KLEIDIAI"]},
        "builds": {
            "baseline": {"cmake_options": {"GGML_CPU_KLEIDIAI": "OFF"}},
            "kleidiai": {"cmake_options": {"GGML_CPU_KLEIDIAI": "ON"}},
        },
    }


def test_good_build_record():
    BuildRecord.from_dict(build_record())


def test_build_record_needs_the_pinned_commit():
    r = build_record()
    r["llama_cpp"]["commit"] = "e" * 40
    with pytest.raises(SchemaError, match="pinned commit"):
        BuildRecord.from_dict(r)


def test_build_record_needs_kleidiai_off_in_baseline_and_on_in_the_other():
    r = build_record()
    r["builds"]["baseline"]["cmake_options"]["GGML_CPU_KLEIDIAI"] = "ON"
    with pytest.raises(SchemaError, match="baseline"):
        BuildRecord.from_dict(r)
    r = build_record()
    r["builds"]["kleidiai"]["cmake_options"]["GGML_CPU_KLEIDIAI"] = "OFF"
    with pytest.raises(SchemaError, match="kleidiai build"):
        BuildRecord.from_dict(r)


def test_build_record_rejects_unexpected_cache_differences_and_unknown_keys():
    r = build_record()
    r["cache_diff"]["unexpected_keys"] = ["GGML_OPENMP: baseline='ON' kleidiai='OFF'"]
    with pytest.raises(SchemaError, match="differ"):
        BuildRecord.from_dict(r)
    r = build_record()
    r["extra"] = 1
    with pytest.raises(SchemaError, match="unknown keys"):
        BuildRecord.from_dict(r)


def smoke_run(**over):
    run = {
        "model_alias": "small",
        "quant": "Q4_0",
        "build": "kleidiai",
        "command": ["llama-bench"],
        "returncode": 0,
        "buffers_mib": {"CPU_KLEIDIAI": 300.0},
        "buffers_total_mib": 300.0,
        "tensor_bytes_total": 123,
        "tensor_bytes_by_type": {"Q4_0": 123},
        "kleidiai_lines": [],
        "notable_lines": [],
        "bench_json": [],
        "memory_vs_file": {},
    }
    run.update(over)
    return run


def smoke_record(**over):
    rec = {
        "schema_version": 1,
        "kind": "check_builds",
        "purpose": "smoke",
        "use_for_analysis": False,
        "session_id": "S",
        "captured_utc": "2026-11-02T09:00:00+00:00",
        "repo": {"commit": "a" * 40, "dirty": False},
        "llama_cpp_commit": PIN,
        "builds": {},
        "runs": [smoke_run()],
    }
    rec.update(over)
    return rec


def test_good_smoke_record():
    rec = CheckBuildsRecord.from_dict(copy.deepcopy(smoke_record()))
    assert rec.use_for_analysis is False


def test_smoke_records_can_never_be_marked_usable_for_analysis():
    with pytest.raises(SchemaError, match="use_for_analysis"):
        CheckBuildsRecord.from_dict(smoke_record(use_for_analysis=True))
    with pytest.raises(SchemaError, match="smoke"):
        CheckBuildsRecord.from_dict(smoke_record(purpose="bench"))


def test_smoke_run_must_have_succeeded_and_shown_buffers():
    with pytest.raises(SchemaError, match="exited"):
        CheckBuildsRecord.from_dict(smoke_record(runs=[smoke_run(returncode=1)]))
    with pytest.raises(SchemaError, match="buffer size"):
        CheckBuildsRecord.from_dict(smoke_record(runs=[smoke_run(buffers_mib={})]))
