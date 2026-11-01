"""Measure B(t): build bench/bandwidth/bandwidth.cpp, run it at every thread count, save a record.

    python -m bench.bandwidth.run_bandwidth --phase start     (make bandwidth PHASE=start)

For each thread count t in configs/sweep.yaml the program runs under `taskset -c 0-(t-1)` and
pins thread i to core i itself (see bandwidth.cpp for why both). Records
results/raw/bandwidth/<session_id>_<phase>.json: per kernel and thread count the samples in
bytes/s with median, IQR and max, plus the pin check, checksum result, compile flags, load
average before/after, transparent-hugepage setting and repo state. The disassembly of the read
loop is saved next to it. Run `start` and `end` around a sitting to see drift (CLAUDE.md §7.5).

Also checks that the 1-thread read result does not change when the number of independent
accumulators is doubled (8 -> 16): if it does, the loop was limited by its add chain and not
by memory. A failed check still writes the record, then exits non-zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from bench import common
from bench.common import REPO_ROOT, WORK_DIR
from edge_llm.schema import SCHEMA_VERSION, BandwidthRecord
from edge_llm.stats import summarise

SOURCE = REPO_ROOT / "bench" / "bandwidth" / "bandwidth.cpp"
BINARY = WORK_DIR / "bin" / "bandwidth"
FLAGS_FILE = WORK_DIR / "bin" / "bandwidth.flags"
OUT_DIR = common.RESULTS_DIR / "raw" / "bandwidth"
COMPILE_FLAGS = ["-O3", "-mcpu=native", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]
ACC_TOLERANCE = 0.03  # doubling the accumulators may move the 1-thread result by <= 3 %
THP_FILE = "/sys/kernel/mm/transparent_hugepage/enabled"


def compile_command() -> list[str]:
    return ["g++", *COMPILE_FLAGS, str(SOURCE), "-o", str(BINARY)]


def ensure_binary() -> dict:
    """Compile if the binary is missing or older than the source or the flags changed."""
    cmd = compile_command()
    flags_now = shlex.join(cmd)
    stale = (
        not BINARY.exists()
        or BINARY.stat().st_mtime < SOURCE.stat().st_mtime
        or common.read_text(FLAGS_FILE) != flags_now
    )
    if stale:
        BINARY.parent.mkdir(parents=True, exist_ok=True)
        print("compiling:", flags_now)
        subprocess.run(cmd, check=True)
        FLAGS_FILE.write_text(flags_now + "\n")
    return {
        "path": common.rel(BINARY),
        "sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
        "compile_command": flags_now,
        "compiler": common.run(["g++", "--version"]),
    }


def run_once(t: int, extra: list[str]) -> dict:
    """One program run at t threads, under taskset -c 0-(t-1). Returns the parsed JSON."""
    cpus = f"0-{t - 1}"
    cmd = ["taskset", "-c", cpus, str(BINARY), "--threads", str(t), *extra]
    print(" ".join(cmd), flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not proc.stdout.strip():
        raise SystemExit(f"bandwidth produced no output (exit {proc.returncode}): {proc.stderr}")
    out = json.loads(proc.stdout)
    out["taskset_cpus"] = cpus
    out["returncode"] = proc.returncode
    return out


def to_point(run: dict, result: dict) -> dict:
    """Turn one kernel's raw program output into a BandwidthPoint dict."""
    t = run["threads"]
    s = summarise(result["samples_bytes_per_s"])
    return {
        "kernel": result["kernel"],
        "threads": t,
        "pinning": {
            "method": "taskset -c 0-(t-1) plus pthread_setaffinity_np: thread i on core i",
            "taskset_cpus": run["taskset_cpus"],
            "process_cpus": run["process_cpus"],
            "observed_cpus": result["observed_cpus"],
            "getcpu_ok": bool(result["getcpu_ok"]) and result["observed_cpus"] == list(range(t)),
        },
        "buffer_bytes": result["buffer_bytes"],
        "bytes_per_rep": result["bytes_per_rep"],
        "reps_warmup": result["reps_warmup"],
        "reps_timed": result["reps_timed"],
        "samples_bytes_per_s": result["samples_bytes_per_s"],
        "median": s["median"],
        "q1": s["q1"],
        "q3": s["q3"],
        "iqr": s["iqr"],
        "max": s["max"],
        "checksum_ok": bool(result["checksum_ok"]),
        "note": f"{result['acc']} independent accumulators" if result["kernel"] == "read" else None,
    }


def acc_check_summary(run: dict) -> dict:
    """Compare the 1-thread read result with 4, 8 and 16 accumulators."""
    med = {r["acc"]: summarise(r["samples_bytes_per_s"])["median"] for r in run["results"]}
    ratio = med[16] / med[8]
    return {
        "threads": run["threads"],
        "median_bytes_per_s_by_accumulators": {str(k): v for k, v in sorted(med.items())},
        "ratio_16_over_8": ratio,
        "tolerance": ACC_TOLERANCE,
        "pass": abs(ratio - 1.0) <= ACC_TOLERANCE,
    }


def objdump_read_loop() -> str:
    out = common.run(
        ["objdump", "-d", "-C", "--no-show-raw-insn", "--disassemble=read_slice_acc8", str(BINARY)],
        timeout=60,
        strip=False,
    )
    return out or "objdump failed or unavailable\n"


def thread_counts() -> list[int]:
    import yaml

    return list(yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())["threads"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--phase", choices=("start", "end"), required=True)
    parser.add_argument("--reps", type=int, default=30, help="timed repeats per point (>= 20)")
    parser.add_argument("--threads", help="comma list, default: sweep.yaml")
    parser.add_argument("--small", action="store_true", help="tiny buffers: for tests only")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--again", action="store_true", help="save as __2 if already measured")
    args = parser.parse_args()

    session_id = common.current_session_id()
    target = args.out_dir / f"{session_id}_{args.phase}.json"
    if target.exists() and not args.again:
        print(f"{target} already exists: skipping (use --again to add a second measurement)")
        return 0

    threads = [int(x) for x in args.threads.split(",")] if args.threads else thread_counts()
    extra = ["--reps", str(args.reps)] + (["--small"] if args.small else [])
    binary = ensure_binary()

    loadavg_before = common.loadavg()
    points, failed = [], False
    for t in threads:
        run = run_once(t, ["--kernel", "both", *extra])
        failed = failed or run["returncode"] != 0
        points += [to_point(run, r) for r in run["results"]]
    acc = acc_check_summary(run_once(1, ["--acc-check", *extra]))
    loadavg_after = common.loadavg()

    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "bandwidth",
        "session_id": session_id,
        "phase": args.phase,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "binary": binary,
        "host": {
            "transparent_hugepage": common.read_text(THP_FILE),
            "loadavg_before": loadavg_before,
            "loadavg_after": loadavg_after,
            "small_buffers_test_run": args.small,
        },
        "points": points,
        "acc_check": acc,
        "objdump_file": "",
    }
    # Fill in the objdump name once we know the final record name, then validate and write.
    record_path = common.next_free_path(target)
    objdump_path = record_path.with_name(record_path.stem + "_read_loop.s")
    record["objdump_file"] = common.rel(objdump_path)
    BandwidthRecord.from_dict(record)  # raises if a checksum, pin check or sample count is bad

    args.out_dir.mkdir(parents=True, exist_ok=True)
    objdump_path.write_text(objdump_read_loop())
    common.write_new_json(record_path, record)
    print(f"wrote {record_path} and {objdump_path.name}")

    print(f"{'threads':>7} {'read GB/s':>10} {'IQR %':>6} {'triad GB/s':>11} {'IQR %':>6}")
    by = {(p["kernel"], p["threads"]): p for p in points}
    for t in threads:
        r, tr = by[("read", t)], by[("triad", t)]
        print(
            f"{t:>7} {r['median'] / 1e9:>10.2f} {100 * r['iqr'] / r['median']:>6.2f}"
            f" {tr['median'] / 1e9:>11.2f} {100 * tr['iqr'] / tr['median']:>6.2f}"
        )
    print(
        f"accumulator check (1 thread, 16 vs 8): ratio {acc['ratio_16_over_8']:.3f}",
        "PASS" if acc["pass"] else "FAIL",
    )
    if not acc["pass"]:
        print(
            "the read loop is limited by its add chain, not by memory: do not use B(t) yet",
            file=sys.stderr,
        )
    return 0 if acc["pass"] and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
