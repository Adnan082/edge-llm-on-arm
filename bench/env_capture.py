"""Capture everything CLAUDE.md §7 item 1 asks for, before a sweep session.

Writes results/raw/env/<session_id>.json. Standard library only, so it runs on a fresh VM
before any pip install. Every probe is best-effort: a missing tool or file is recorded as
null (or "not exposed" for the CPU governor) with a note, never guessed and never fatal.

Run on the Arm VM:  python3 bench/env_capture.py   (or: make env)
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = REPO_ROOT / "work"
LLAMACPP_DIR = WORK_DIR / "llama.cpp"
MODELS_DIR = WORK_DIR / "models"

# CPU feature flags the spec cares about (§5, §11). Names are as /proc/cpuinfo prints them.
KEY_FLAGS = ("asimd", "asimddp", "asimdhp", "bf16", "i8mm", "sve", "sve2", "sme", "sme2")

# llama.cpp CMake options worth recording from each build's CMakeCache.txt.
CACHE_KEYS = (
    "CMAKE_BUILD_TYPE",
    "CMAKE_C_COMPILER",
    "CMAKE_CXX_COMPILER",
    "CMAKE_C_FLAGS",
    "CMAKE_CXX_FLAGS",
    "GGML_NATIVE",
    "GGML_CPU_KLEIDIAI",
    "GGML_CPU_AARCH64",
    "GGML_CPU_ARM_ARCH",
    "GGML_LLAMAFILE",
    "GGML_OPENMP",
    "GGML_CCACHE",
    "LLAMA_CURL",
)

PR_SVE_GET_VL = 51  # linux/prctl.h
PR_SVE_VL_LEN_MASK = 0xFFFF
GCE_METADATA = "http://metadata.google.internal/computeMetadata/v1/instance/"


def make_session_id(now: datetime | None = None) -> str:
    """UTC start time, `YYYY-MM-DDTHHMMZ` (ARCHITECTURE.md §3)."""
    now = now or datetime.now(UTC)
    return now.astimezone(UTC).strftime("%Y-%m-%dT%H%MZ")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> str | None:
    """Return stdout+stderr of a command, or None if it is missing or fails."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout + proc.stderr).strip()


def read_text(path: str | Path) -> str | None:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


# --- machine identity -------------------------------------------------------------------


def gce_metadata(key: str) -> str | None:
    """One value from the GCE metadata server; None off Google Cloud."""
    req = urllib.request.Request(GCE_METADATA + key, headers={"Metadata-Flavor": "Google"})
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.read().decode().strip()
    except (OSError, ValueError):
        return None


def machine_identity() -> dict:
    # Metadata values look like "projects/123/machineTypes/c4a-highcpu-8"; keep the last part.
    def last(v: str | None) -> str | None:
        return v.rsplit("/", 1)[-1] if v else None

    return {
        "machine_type": last(gce_metadata("machine-type")),
        "zone": last(gce_metadata("zone")),
        "hostname": platform.node(),
        "note": "machine_type/zone are null when the GCE metadata server is unreachable",
    }


# --- CPU ---------------------------------------------------------------------------------


def parse_cpuinfo_features(cpuinfo: str) -> list[str]:
    """Feature flags of the first CPU in /proc/cpuinfo (AArch64 calls the line `Features`)."""
    for line in cpuinfo.splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() in ("features", "flags"):
            return value.split()
    return []


def key_flag_presence(features: list[str]) -> dict[str, bool]:
    present = set(features)
    return {flag: flag in present for flag in KEY_FLAGS}


def threads_per_core(lscpu_json: dict | None) -> str | None:
    """`Thread(s) per core` from `lscpu -J`; 1 means no SMT (spec §5, verify)."""
    for entry in (lscpu_json or {}).get("lscpu", []):
        if entry.get("field", "").startswith("Thread(s) per core"):
            return entry.get("data")
    return None


def cpu_info() -> dict:
    cpuinfo = read_text("/proc/cpuinfo") or ""
    features = parse_cpuinfo_features(cpuinfo)
    raw_json = run(["lscpu", "-J"])
    try:
        lscpu_json = json.loads(raw_json) if raw_json else None
    except json.JSONDecodeError:
        lscpu_json = None
    return {
        "logical_cpus": os.cpu_count(),
        "threads_per_core": threads_per_core(lscpu_json),
        "lscpu_text": run(["lscpu"]),
        "lscpu_json": lscpu_json,
        "features": features,
        "key_flags": key_flag_presence(features),
        # The model name and caches are inside lscpu_text/lscpu_json; the scaling governor is
        # reported separately because cloud VMs usually do not expose cpufreq at all.
        "governor": read_text("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        or "not exposed",
    }


def sve_vector_length() -> dict:
    """SVE vector length in bits, asked of the kernel for this process.

    prctl(PR_SVE_GET_VL) gives the length the process actually runs with; the /proc file is
    only the default for new processes, so both are recorded.
    """
    out: dict = {"prctl_bits": None, "default_bits": None, "note": None}
    default = read_text("/proc/sys/abi/sve_default_vector_length")
    if default and default.isdigit():
        out["default_bits"] = int(default) * 8  # the file holds bytes
    if not sys.platform.startswith("linux"):
        out["note"] = "prctl unavailable (not Linux)"
        return out
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        ret = libc.prctl(PR_SVE_GET_VL, 0, 0, 0, 0)
    except (OSError, AttributeError):
        out["note"] = "could not call prctl"
        return out
    if ret >= 0:
        out["prctl_bits"] = (ret & PR_SVE_VL_LEN_MASK) * 8
    else:
        out["note"] = "prctl(PR_SVE_GET_VL) failed: SVE not available to this kernel/CPU"
    return out


def memory_info() -> dict:
    meminfo = read_text("/proc/meminfo") or ""
    m = re.search(r"MemTotal:\s+(\d+) kB", meminfo)
    return {"mem_total_kb": int(m.group(1)) if m else None}


# --- toolchain ---------------------------------------------------------------------------


def tool_version(cmd: list[str]) -> str | None:
    """First line of `<tool> --version`, or None if the tool is not installed."""
    if shutil.which(cmd[0]) is None:
        return None
    out = run(cmd)
    return out.splitlines()[0] if out else None


def compilers() -> dict:
    return {
        "gcc": tool_version(["gcc", "--version"]),
        "g++": tool_version(["g++", "--version"]),
        "clang": tool_version(["clang", "--version"]),
        "cmake": tool_version(["cmake", "--version"]),
        "make": tool_version(["make", "--version"]),
        "ld": tool_version(["ld", "--version"]),
        "python": sys.version.split()[0],
    }


# --- llama.cpp, builds, models -----------------------------------------------------------


def git_state(repo: Path) -> dict:
    """Commit and cleanliness of a git checkout; all null if it is not one."""
    if not (repo / ".git").exists():
        return {"commit": None, "dirty": None}
    status = run(["git", "status", "--porcelain"], cwd=repo)
    return {
        "commit": run(["git", "rev-parse", "HEAD"], cwd=repo),
        "dirty": None if status is None else bool(status),
    }


def parse_cmake_cache(text: str, keys: tuple[str, ...] = CACHE_KEYS) -> dict[str, str]:
    """Pick `KEY:TYPE=value` entries out of a CMakeCache.txt."""
    wanted = set(keys)
    found: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith(("//", "#")) or "=" not in line:
            continue
        name_type, _, value = line.partition("=")
        name = name_type.split(":", 1)[0]
        if name in wanted:
            found[name] = value
    return found


def builds_info() -> dict:
    """One entry per work/build-* directory: flags from CMakeCache, `--version` output."""
    builds: dict = {}
    for build in sorted(WORK_DIR.glob("build-*")):
        cache = read_text(build / "CMakeCache.txt")
        cli = build / "bin" / "llama-cli"
        version_out = run([str(cli), "--version"]) if cli.exists() else None
        # The "system_info" line (CPU features the build uses) is also printed when a model
        # is loaded; pick it up here if --version shows it, otherwise it stays null.
        system_info = None
        for line in (version_out or "").splitlines():
            if "system_info" in line or line.strip().startswith("CPU :"):
                system_info = line.strip()
        builds[build.name.removeprefix("build-")] = {
            "dir": str(build.relative_to(REPO_ROOT)),
            "cmake_flags": parse_cmake_cache(cache) if cache else None,
            "version_output": version_out,
            "system_info_line": system_info,
        }
    return builds


def parse_sha256sums(text: str) -> dict[str, str]:
    """`sha256sum` output (`<hash>  <file>`) -> {file: hash}."""
    sums: dict[str, str] = {}
    for line in text.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            sums[parts[1].lstrip("*").strip()] = parts[0]
    return sums


def model_hashes() -> dict | None:
    """SHA256 of each model file, read from work/models/SHA256SUMS.

    infra/make_models.sh writes that file (hashing a multi-GB GGUF is too slow to repeat at
    every session start). None means the models have not been made yet.
    """
    text = read_text(MODELS_DIR / "SHA256SUMS")
    return parse_sha256sums(text) if text else None


# --- assemble ----------------------------------------------------------------------------


def capture(session_id: str, phase: str) -> dict:
    now = datetime.now(UTC)
    return {
        "session_id": session_id,
        "phase": phase,
        "captured_utc": now.isoformat(timespec="seconds"),
        "machine": machine_identity(),
        "os": {
            "platform": platform.platform(),
            "kernel": platform.release(),
            "uname": " ".join(platform.uname()),
            "machine_arch": platform.machine(),
            "os_release": read_text("/etc/os-release"),
        },
        "cpu": cpu_info(),
        "sve_vector_length": sve_vector_length(),
        "memory": memory_info(),
        "compilers": compilers(),
        "repo": git_state(REPO_ROOT),
        "llama_cpp": git_state(LLAMACPP_DIR),
        "builds": builds_info(),
        "model_sha256": model_hashes(),
        "loadavg_1_5_15": list(os.getloadavg()) if hasattr(os, "getloadavg") else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session-id", help="reuse an existing session id (default: now, UTC)")
    parser.add_argument(
        "--phase",
        choices=("start", "end"),
        default="start",
        help="start/end of a sweep session; `end` is written as <session_id>_end.json",
    )
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "results" / "raw" / "env")
    args = parser.parse_args()

    session_id = args.session_id or make_session_id()
    suffix = "" if args.phase == "start" else "_end"
    out_path = args.out_dir / f"{session_id}{suffix}.json"
    if out_path.exists():
        # Raw records are append-only (ARCHITECTURE.md rule 2).
        print(f"refusing to overwrite {out_path}", file=sys.stderr)
        return 1

    record = capture(session_id, args.phase)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"wrote {out_path}")

    flags = record["cpu"]["key_flags"]
    print("key CPU flags:", ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in flags.items()))
    print("threads per core:", record["cpu"]["threads_per_core"])
    print("SVE vector length (bits):", record["sve_vector_length"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
