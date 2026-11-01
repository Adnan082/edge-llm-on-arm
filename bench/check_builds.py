"""Show that KleidiAI is active in the kleidiai build, and which formats each build takes.

    python -m bench.check_builds        (make check-builds)

For every model file and both builds, run a tiny llama-bench (-p 64 -n 16 -r 1 -t 8 -v) and
keep what proves which code path ran: each "model buffer size" line (the buffer type names
CPU_KLEIDIAI / CPU_REPACK / CPU_Mapped say who owns each weight) and any KleidiAI or repack log
line. The build's system-info line (KLEIDIAI = 1, REPACK = 1, DOTPROD, MATMUL_INT8, SVE_CNT, ...)
comes from llama-completion, because llama-bench never prints it. Saved to
results/raw/build/<session_id>_check_builds.json.

These are SMOKE runs: one repetition of a 64-token prompt. The record says so
(`use_for_analysis: false`) and lives in results/raw/build/, which analyse.py never reads; the
speeds inside it mean nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from bench import common
from bench.common import MODELS_DIR, REPO_ROOT, WORK_DIR
from edge_llm.schema import SCHEMA_VERSION, CheckBuildsRecord

SMOKE_ARGS = ["-p", "64", "-n", "16", "-r", "1", "-t", "8", "-v", "-o", "json"]
BUFFER_RE = re.compile(r"(\S+)\s+model buffer size\s*=\s*([0-9.]+)\s*MiB")
FEATURE_RE = re.compile(r"([A-Z][A-Z0-9_]*)\s=\s(\S+)")
NOTABLE_RE = re.compile(r"kleidi|repack|warn|error|failed|fallback", re.IGNORECASE)
OUT_DIR = common.RESULTS_DIR / "raw" / "build"
MIB = 1024 * 1024


def parse_buffers(log: str) -> dict[str, float]:
    """{buffer type name: MiB} from the 'model buffer size' lines (summed if a name repeats)."""
    out: dict[str, float] = {}
    for name, mib in BUFFER_RE.findall(log):
        out[name] = round(out.get(name, 0.0) + float(mib), 2)
    return out


def parse_system_info(log: str) -> tuple[str | None, dict[str, str]]:
    """The `system_info: ... | CPU : NEON = 1 | ...` line, and its NAME = value pairs."""
    for line in log.splitlines():
        if "system_info:" in line:
            line = line[line.index("system_info:") :].strip()
            return line, dict(FEATURE_RE.findall(line.split("|", 1)[-1]))
    return None, {}


def notable_lines(log: str, limit: int = 40) -> list[str]:
    lines = [ln.strip() for ln in log.splitlines() if NOTABLE_RE.search(ln)]
    return lines[:limit]


def tensor_bytes_by_type(table: dict) -> dict[str, int]:
    return {t: m["bytes"] for t, m in table["type_mix"].items()}


def memory_vs_file(buffers_mib: dict[str, float], table: dict) -> dict:
    """Bytes in memory against bytes in the file, in MiB (the difference is explained in notes)."""
    file_mib = table["totals"]["W_all"] / MIB
    mem_mib = round(sum(buffers_mib.values()), 2)
    return {
        "file_tensor_mib": round(file_mib, 2),
        "memory_mib": mem_mib,
        "delta_mib": round(mem_mib - file_mib, 2),
        "tied_embeddings": table["tied_embeddings"],
    }


def model_list(only: list[str] | None) -> list[tuple[str, str]]:
    import yaml

    sweep = yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())
    pairs = [(a, q) for a in sweep["models"] for q in sweep["quants"]]
    if only:
        pairs = [p for p in pairs if f"{p[0]}_{p[1]}" in only]
    return pairs


def run_logged(cmd: list[str], timeout: int) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, check=False, timeout=timeout, stdin=subprocess.DEVNULL
    )
    return proc.returncode, proc.stdout, proc.stderr


def system_info(build: str, model: Path) -> dict:
    exe = WORK_DIR / f"build-{build}" / "bin" / "llama-completion"
    cmd = [str(exe), "-m", str(model), "-p", "Hi", "-n", "1", "-t", "8", "-no-cnv", "--no-warmup"]
    code, out, err = run_logged(cmd, timeout=600)
    line, features = parse_system_info(out + "\n" + err)
    return {
        "command": cmd,
        "returncode": code,
        "system_info_line": line,
        "features": features,
        "kleidiai_flag": features.get("KLEIDIAI"),
        "repack_flag": features.get("REPACK"),
    }


def smoke_run(build: str, alias: str, quant: str, session_id: str) -> dict:
    model = MODELS_DIR / f"{alias}_{quant}.gguf"
    table = json.loads((common.RESULTS_DIR / "models" / f"{alias}_{quant}.json").read_text())
    if model.stat().st_size != table["file_bytes"]:
        raise SystemExit(f"{model.name}: size differs from its tensor table: rerun make models")
    cmd = [str(WORK_DIR / f"build-{build}" / "bin" / "llama-bench"), "-m", str(model), *SMOKE_ARGS]
    print(" ".join(cmd), flush=True)
    code, out, err = run_logged(cmd, timeout=1800)
    log_dir = WORK_DIR / "smoke" / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{alias}_{quant}_{build}.stderr.txt").write_text(err)
    try:
        bench_json = json.loads(out)
    except json.JSONDecodeError:
        bench_json = None
    buffers = parse_buffers(err)
    return {
        "model_alias": alias,
        "quant": quant,
        "build": build,
        "command": cmd,
        "returncode": code,
        "buffers_mib": buffers,
        "buffers_total_mib": round(sum(buffers.values()), 2),
        "tensor_bytes_total": table["totals"]["W_all"],
        "tensor_bytes_by_type": tensor_bytes_by_type(table),
        "kleidiai_lines": [ln for ln in notable_lines(err) if "kleidi" in ln.lower()],
        "notable_lines": notable_lines(err),
        "bench_json": bench_json,
        "memory_vs_file": memory_vs_file(buffers, table),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", help="comma list like small_Q4_0,small_Q8_0 (default: all)")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    session_id = common.current_session_id()
    pairs = model_list(args.models.split(",") if args.models else None)
    for b in common.BUILD_NAMES:
        if not (WORK_DIR / f"build-{b}" / "bin" / "llama-bench").exists():
            raise SystemExit(f"work/build-{b}/bin/llama-bench missing: run make build")

    # The system-info line is a property of the build; any one model file will do.
    probe = next((MODELS_DIR / f"{a}_{q}.gguf" for a, q in pairs if q == "Q4_0"), None)
    probe = probe or MODELS_DIR / f"{pairs[0][0]}_{pairs[0][1]}.gguf"
    builds = {b: system_info(b, probe) for b in common.BUILD_NAMES}
    for b, info in builds.items():
        print(f"{b}: KLEIDIAI={info['kleidiai_flag']} REPACK={info['repack_flag']}")

    runs = [
        smoke_run(b, a, q, session_id) for a, q in pairs for b in common.BUILD_NAMES
    ]  # builds are adjacent per model so both see the same file cache state
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "check_builds",
        "purpose": "smoke",
        "use_for_analysis": False,
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "llama_cpp_commit": common.git_state(common.LLAMACPP_DIR, ignore_prefixes=())["commit"],
        "builds": builds,
        "runs": runs,
    }
    CheckBuildsRecord.from_dict(record)
    path = common.write_new_json(args.out_dir / f"{session_id}_check_builds.json", record)
    print(f"wrote {path}")

    print(f"\n{'model':<14}{'build':<10}{'file MiB':>9}{'memory MiB':>11}  buffers (MiB)")
    for r in runs:
        m = r["memory_vs_file"]
        print(
            f"{r['model_alias'] + '_' + r['quant']:<14}{r['build']:<10}"
            f"{m['file_tensor_mib']:>9.1f}{m['memory_mib']:>11.1f}  {r['buffers_mib']}"
        )
    by = {b: builds[b]["kleidiai_flag"] for b in builds}
    if by.get("kleidiai") != "1" or by.get("baseline") == "1":
        print(f"KLEIDIAI flag is wrong: {by}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
