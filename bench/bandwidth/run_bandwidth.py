"""Measure B(t): build bench/bandwidth/bandwidth.cpp, run it at every thread count, save a record.

    python -m bench.bandwidth.run_bandwidth --phase start     (make bandwidth PHASE=start)

For each thread count t in configs/sweep.yaml the program runs under `taskset -c 0-(t-1)` and
pins thread i to core i itself (see bandwidth.cpp for why both). Records
results/raw/bandwidth/<session_id>_<phase>.json: per kernel and thread count the samples in
bytes/s with median, IQR and max, plus the pin check, checksum result, compile flags, load
average before/after, transparent-hugepage setting and repo state. The disassembly of the read
loop is saved next to it. Run `start` and `end` around a sitting to see drift (CLAUDE.md §7.5).

The read kernel runs with k = 1, 2, 4 and 8 interleaved streams per thread (ADR-017):
B(t) = the best median over k, B1(t) = the k = 1 median. As a diagnostic only, k = 1 is also run
with transparent huge pages at t = 1 and t = 8; those points never enter B(t).

Also checks that the 1-thread read result does not change when the number of independent
accumulators is doubled (8 -> 16), at k = 1 and k = 8: if it does, the loop was limited by its
add chain and not by memory. A failed check still writes the record, then exits non-zero.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from bench import common
from bench.common import REPO_ROOT, WORK_DIR
from edge_llm.bandwidth import HUGEPAGE_DIAGNOSTIC_THREADS, STREAM_COUNTS, b_of_t
from edge_llm.schema import SCHEMA_VERSION, BandwidthRecord
from edge_llm.stats import summarise

SOURCE = REPO_ROOT / "bench" / "bandwidth" / "bandwidth.cpp"
BINARY = WORK_DIR / "bin" / "bandwidth"
FLAGS_FILE = WORK_DIR / "bin" / "bandwidth.flags"
OUT_DIR = common.RESULTS_DIR / "raw" / "bandwidth"
COMPILE_FLAGS = ["-O3", "-mcpu=native", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]
ACC_TOLERANCE = 0.03  # doubling the accumulators may move the 1-thread result by <= 3 %
ACC_CHECK_STREAMS = (1, 8)  # the stream counts the accumulator check covers
THP_FILE = "/sys/kernel/mm/transparent_hugepage/enabled"
STREAMS_ARG = ",".join(str(k) for k in STREAM_COUNTS)


def compile_command() -> list[str]:
    return ["g++", *COMPILE_FLAGS, str(SOURCE), "-o", str(BINARY)]


def ensure_binary() -> dict:
    """Compile if the binary is missing or older than the source or the flags changed."""
    return common.ensure_binary(SOURCE, BINARY, FLAGS_FILE, compile_command())


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
    streams = result.get("streams", 1)
    if result["kernel"] == "read":
        note = f"{result['acc']} independent accumulators, {streams} read stream(s) per thread"
        if result.get("hugepage"):
            note += ", madvise(MADV_HUGEPAGE): diagnostic only"
    else:
        note = None
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
        "note": note,
        "streams": streams,
        "hugepage": bool(result.get("hugepage", False)),
        "anon_huge_kb": result.get("anon_huge_kb"),
    }


def acc_check_summary(run: dict, streams: int = 1) -> dict:
    """Compare the read result with 4, 8 and 16 accumulators at one stream count."""
    med = {
        r["acc"]: summarise(r["samples_bytes_per_s"])["median"]
        for r in run["results"]
        if r.get("streams", 1) == streams
    }
    ratio = med[16] / med[8]
    return {
        "threads": run["threads"],
        "streams": streams,
        "median_bytes_per_s_by_accumulators": {str(k): v for k, v in sorted(med.items())},
        "ratio_16_over_8": ratio,
        "tolerance": ACC_TOLERANCE,
        "pass": abs(ratio - 1.0) <= ACC_TOLERANCE,
    }


def acc_check_all(run: dict) -> dict:
    """The accumulator check at every stream count in the run; passes only if all do."""
    present = sorted({r.get("streams", 1) for r in run["results"]})
    by_k = {str(k): acc_check_summary(run, k) for k in present}
    return {
        "threads": run["threads"],
        "by_streams": by_k,
        "ratio_16_over_8": by_k["1"]["ratio_16_over_8"],
        "tolerance": ACC_TOLERANCE,
        "pass": all(c["pass"] for c in by_k.values()),
    }


def objdump_read_loop() -> str:
    out = common.run(
        [
            "objdump",
            "-d",
            "-C",
            "--no-show-raw-insn",
            "--disassemble=read_slice_acc8_k1",
            str(BINARY),
        ],
        timeout=60,
        strip=False,
    )
    return out or "objdump failed or unavailable\n"


def thread_counts() -> list[int]:
    import yaml

    return list(yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())["threads"])


def print_table(record: BandwidthRecord, threads: list[int]) -> None:
    b = b_of_t(record.points)
    triad = {p.threads: p for p in record.points if p.kernel == "triad"}
    hp = {p.threads: p for p in record.points if p.hugepage}
    gb = 1e9
    print(
        f"{'threads':>7} {'B(t) GB/s':>10} {'best k':>6} {'B1(t) GB/s':>11} {'B/B1':>6}"
        f" {'triad GB/s':>11} {'k=1 +THP':>9}"
    )
    for t in threads:
        h = f"{hp[t].median / gb:>9.2f}" if t in hp else f"{'-':>9}"
        print(
            f"{t:>7} {b[t].b / gb:>10.2f} {b[t].streams:>6} {b[t].b1 / gb:>11.2f}"
            f" {b[t].b / b[t].b1:>6.3f} {triad[t].median / gb:>11.2f} {h}"
        )
    for t, p in sorted(hp.items()):
        print(f"  t={t}: AnonHugePages after first touch = {p.anon_huge_kb} kB (0 = no huge pages)")


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
        run = run_once(t, ["--kernel", "both", "--streams", STREAMS_ARG, *extra])
        failed = failed or run["returncode"] != 0
        points += [to_point(run, r) for r in run["results"]]
    for t in HUGEPAGE_DIAGNOSTIC_THREADS:  # diagnostic only: never part of B(t)
        if t in threads:
            run = run_once(t, ["--kernel", "read", "--streams", "1", "--hugepage", *extra])
            failed = failed or run["returncode"] != 0
            points += [to_point(run, r) for r in run["results"]]
    acc_streams = ",".join(str(k) for k in ACC_CHECK_STREAMS)
    acc = acc_check_all(run_once(1, ["--acc-check", "--streams", acc_streams, *extra]))
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
    validated = BandwidthRecord.from_dict(record)  # raises on a bad checksum, pin check or count

    args.out_dir.mkdir(parents=True, exist_ok=True)
    objdump_path.write_text(objdump_read_loop())
    common.write_new_json(record_path, record)
    print(f"wrote {record_path} and {objdump_path.name}")

    print_table(validated, threads)
    for k, c in acc["by_streams"].items():
        print(
            f"accumulator check (1 thread, k={k}, 16 vs 8): ratio {c['ratio_16_over_8']:.3f}",
            "PASS" if c["pass"] else "FAIL",
        )
    if not acc["pass"]:
        print(
            "the read loop is limited by its add chain, not by memory: do not use B(t) yet",
            file=sys.stderr,
        )
    return 0 if acc["pass"] and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
