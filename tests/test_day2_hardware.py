"""Day 2 checks that need the Arm VM: run with `make test PYTEST_ARGS="-m hardware"`."""

import json
import subprocess

import pytest

from bench import common
from bench.bandwidth import run_bandwidth

pytestmark = pytest.mark.hardware

BIN_DIR = "bin"


@pytest.mark.parametrize("threads", [1, 2])
def test_bandwidth_checksums_and_pinning(threads):
    """Small buffers: both kernels must reproduce their known answers, on the right cores."""
    run_bandwidth.ensure_binary()
    cpus = f"0-{threads - 1}"
    proc = subprocess.run(
        [
            "taskset",
            "-c",
            cpus,
            str(run_bandwidth.BINARY),
            "--threads",
            str(threads),
            "--small",
            "--reps",
            "3",
            "--warmup",
            "1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    out = json.loads(proc.stdout)
    assert {r["kernel"] for r in out["results"]} == {"read", "triad"}
    for r in out["results"]:
        assert r["checksum_ok"], f"{r['kernel']} checksum wrong"
        assert r["getcpu_ok"] and r["observed_cpus"] == list(range(threads))
        assert all(s > 0 for s in r["samples_bytes_per_s"])
    assert proc.returncode == 0
    assert out["process_cpus"] == list(range(threads))


def test_both_builds_exist():
    for build in common.BUILD_NAMES:
        for exe in ("llama-bench", "llama-quantize", "llama-completion"):
            path = common.WORK_DIR / f"build-{build}" / "bin" / exe
            assert path.exists(), f"{path} missing: run make build"


def first_model():
    models = sorted(common.MODELS_DIR.glob("*_Q4_0.gguf"))
    if not models:
        pytest.skip("no Q4_0 model in work/models yet: run make models")
    return models[0]


def test_kleidiai_appears_only_in_the_kleidiai_build():
    from bench import check_builds

    model = first_model()
    flags = {b: check_builds.system_info(b, model) for b in common.BUILD_NAMES}
    for b, info in flags.items():
        assert info["system_info_line"], f"{b}: llama-completion printed no system_info line"
    assert flags["kleidiai"]["kleidiai_flag"] == "1"
    assert flags["baseline"]["kleidiai_flag"] is None
    # the build's repack path is on in both (GGML_CPU_REPACK defaults ON)
    assert flags["baseline"]["repack_flag"] == "1" and flags["kleidiai"]["repack_flag"] == "1"
