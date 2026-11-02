"""Measure B(t): build bench/bandwidth/bandwidth.cpp, run it at every thread count, save a record.

    python -m bench.bandwidth.run_bandwidth --phase start     (make bandwidth PHASE=start)

For each thread count t in configs/sweep.yaml the program runs under `taskset -c 0-(t-1)` and
pins thread i to core i itself (see bandwidth.cpp for why both). Records
results/raw/bandwidth/<session_id>_<phase>.json: per kernel and thread count the samples in
bytes/s with median, IQR and max, plus the pin check, checksum result, compile flags, load
average before/after, transparent-hugepage setting and repo state. The disassembly of the read
loop is saved next to it. Run `start` and `end` around a sitting to see drift (CLAUDE.md §7.5).

The read kernel runs as eight variants: 8 or 16 accumulators x k = 1, 2, 4, 8 interleaved streams
per thread (ADR-017, ADR-021). A read test can only under-measure memory, so the fastest valid
variant is the best estimate; "valid" is checked at one thread by running every variant on a 32 KiB
buffer (fits in L1, repeated passes so each timed repetition lasts at least 10 ms) as well as on
1 GiB: the L1 median must be at least 1.5 times the 1 GiB median, or the loop itself is the limit.
B(t) = the best 1 GiB median over the valid variants, B1(t) = the best valid one at k = 1, and the
winning variant at each t is recorded. The run fails only if no variant is valid. As a diagnostic
only, k = 1 is also run with transparent huge pages at t = 1 and t = 8; those never enter B(t).

The disassembly of all eight loops is saved next to the record, and each loop's vector loads and
stack accesses are reported as information (GCC may spill at 16 accumulators); a loop that cannot
be found, or has no vector loads, is an error. A failed run still writes the record, then exits
non-zero.
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
from bench.common import REPO_ROOT, WORK_DIR
from edge_llm import peak
from edge_llm.bandwidth import (
    ACCUMULATOR_COUNTS,
    HUGEPAGE_DIAGNOSTIC_THREADS,
    L1_BUFFER_BYTES,
    STREAM_COUNTS,
    VALID_RATIO,
    b_of_t,
    valid_variants,
    validity_table,
)
from edge_llm.schema import SCHEMA_VERSION, BandwidthPoint, BandwidthRecord
from edge_llm.stats import summarise

SOURCE = REPO_ROOT / "bench" / "bandwidth" / "bandwidth.cpp"
BINARY = WORK_DIR / "bin" / "bandwidth"
FLAGS_FILE = WORK_DIR / "bin" / "bandwidth.flags"
OUT_DIR = common.RESULTS_DIR / "raw" / "bandwidth"
COMPILE_FLAGS = ["-O3", "-mcpu=native", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]
READ_LOOP_FUNCTIONS = tuple(
    f"read_slice_acc{a}_k{k}" for a in ACCUMULATOR_COUNTS for k in STREAM_COUNTS
)
ACC_ARG = ",".join(str(a) for a in ACCUMULATOR_COUNTS)
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
        if result.get("l1"):
            note += f", 32 KiB buffer x {result.get('passes', 1)} passes: validity check"
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
        "accumulators": result["acc"],
        "l1": bool(result.get("l1", False)),
        "passes": result.get("passes", 1),
    }


def check_read_loop(name: str, objdump_text: str) -> dict:
    """The hot loop of one read function. Vector loads and stack accesses are information (GCC may
    spill at 16 accumulators); only a missing loop, or one with no vector loads, is an error."""
    loop = peak.hot_loop(peak.parse_instructions(objdump_text))
    stack = [i for i in loop if re.search(r"\[sp[,\]]", i)]
    stores = [i for i in loop if re.match(r"^(st\w*)\s", i)]
    vector_loads = sum(
        (2 if i.startswith("ldp") else 1) for i in loop if re.match(r"^(ldr|ldp|ld1)\s+q", i)
    )
    return {
        "function": name,
        "loop_instructions": len(loop),
        "vector_loads": vector_loads,
        "stack_accesses": stack,
        "stores": stores,
        "ok": bool(loop) and vector_loads > 0,
    }


def winners(points: list, valid: set) -> dict[str, dict]:
    """The winning variant at each thread count: B(t), B1(t) and which variants gave them."""
    out = {}
    for t, b in b_of_t(points, valid).items():
        out[str(t)] = {
            "b": b.b,
            "accumulators": b.accumulators,
            "streams": b.streams,
            "b1": b.b1,
            "b1_accumulators": b.b1_accumulators,
        }
    return out


def make_validity(point_dicts: list[dict], loops: list[dict]) -> dict:
    """The validity part of the record: the per-variant L1 check, the winners, the loop reports."""
    points = [BandwidthPoint.from_dict(d) for d in point_dicts]
    table = validity_table(points)
    valid = valid_variants(table)
    return {
        "threads": 1,
        "l1_buffer_bytes": L1_BUFFER_BYTES,
        "min_ratio": VALID_RATIO,
        "variants": table,
        "any_valid": bool(valid),
        "winners": winners(points, valid),
        "loops": loops,
    }


def disassemble_read_loops() -> dict[str, str]:
    """objdump of every read function: {name: text}."""
    out = {}
    for name in READ_LOOP_FUNCTIONS:
        text = common.run(
            ["objdump", "-d", "-C", "--no-show-raw-insn", f"--disassemble={name}", str(BINARY)],
            timeout=60,
            strip=False,
        )
        out[name] = text or "objdump failed or unavailable\n"
    return out


def thread_counts() -> list[int]:
    import yaml

    return list(yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())["threads"])


def print_table(record: BandwidthRecord, threads: list[int]) -> None:
    valid = valid_variants(record.validity["variants"])
    b = b_of_t(record.points, valid)
    triad = {p.threads: p for p in record.points if p.kernel == "triad"}
    hp = {}
    for p in record.points:
        if p.hugepage and (p.threads not in hp or p.median > hp[p.threads].median):
            hp[p.threads] = p
    gb = 1e9
    print(
        f"{'threads':>7} {'B(t) GB/s':>10} {'acc/k':>6} {'B1(t) GB/s':>11} {'acc':>4}"
        f" {'B/B1':>6} {'triad GB/s':>11} {'k=1 +THP':>9}"
    )
    for t in threads:
        if t not in b:
            print(f"{t:>7} {'no valid variant':>10}")
            continue
        h = f"{hp[t].median / gb:>9.2f}" if t in hp else f"{'-':>9}"
        b1 = f"{b[t].b1 / gb:>11.2f}" if b[t].b1 is not None else f"{'-':>11}"
        b1a = b[t].b1_accumulators if b[t].b1_accumulators is not None else "-"
        ratio = f"{b[t].b / b[t].b1:>6.3f}" if b[t].b1 is not None else f"{'-':>6}"
        print(
            f"{t:>7} {b[t].b / gb:>10.2f} {f'{b[t].accumulators}/{b[t].streams}':>6}"
            f" {b1} {b1a:>4} {ratio} {triad[t].median / gb:>11.2f} {h}"
        )
    for t, p in sorted(hp.items()):
        print(f"  t={t}: AnonHugePages after first touch = {p.anon_huge_kb} kB (0 = no huge pages)")
    print(f"validity at 1 thread (L1 must be >= {VALID_RATIO}x the 1 GiB median):")
    print(f"  {'acc':>3} {'k':>2} {'L1 GB/s':>9} {'1 GiB GB/s':>11} {'ratio':>6}")
    for r in record.validity["variants"]:
        ratio = f"{r['ratio']:.2f}" if r["ratio"] is not None else "-"
        print(
            f"  {r['accumulators']:>3} {r['streams']:>2} {(r['l1_median'] or 0) / gb:>9.1f}"
            f" {(r['dram_median'] or 0) / gb:>11.1f} {ratio:>6}  "
            f"{'valid' if r['valid'] else 'INVALID'}"
        )


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
        run = run_once(t, ["--kernel", "both", "--streams", STREAMS_ARG, "--acc", ACC_ARG, *extra])
        failed = failed or run["returncode"] != 0
        points += [to_point(run, r) for r in run["results"]]
    for t in HUGEPAGE_DIAGNOSTIC_THREADS:  # diagnostic only: never part of B(t)
        if t in threads:
            run = run_once(
                t,
                ["--kernel", "read", "--streams", "1", "--acc", ACC_ARG, "--hugepage", *extra],
            )
            failed = failed or run["returncode"] != 0
            points += [to_point(run, r) for r in run["results"]]
    # the validity check: every variant over a 32 KiB buffer at one thread
    run = run_once(
        1, ["--kernel", "read", "--streams", STREAMS_ARG, "--acc", ACC_ARG, "--l1", *extra]
    )
    failed = failed or run["returncode"] != 0
    points += [to_point(run, r) for r in run["results"]]
    disassembly = disassemble_read_loops()
    loops = [check_read_loop(name, text) for name, text in disassembly.items()]
    validity = make_validity(points, loops)
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
        "objdump_file": "",
        "validity": validity,
    }
    # Fill in the objdump name once we know the final record name, then validate and write.
    record_path = common.next_free_path(target)
    objdump_path = record_path.with_name(record_path.stem + "_read_loop.s")
    record["objdump_file"] = common.rel(objdump_path)
    validated = BandwidthRecord.from_dict(record)  # raises on a bad checksum, pin check or count

    args.out_dir.mkdir(parents=True, exist_ok=True)
    objdump_path.write_text(
        "\n".join(f"# ===== {name} =====\n{text}" for name, text in disassembly.items())
    )
    common.write_new_json(record_path, record)
    print(f"wrote {record_path} and {objdump_path.name}")

    print_table(validated, threads)
    for lp in loops:
        print(
            f"  {lp['function']:<20} loop {lp['loop_instructions']:>4} insns, "
            f"{lp['vector_loads']:>3} vector loads, {len(lp['stack_accesses'])} stack accesses, "
            f"{len(lp['stores'])} stores{'' if lp['ok'] else ': LOOP NOT FOUND OR NO LOADS'}"
        )
    if not validity["any_valid"]:
        print("no read variant is valid: do not use B(t)", file=sys.stderr)
    if not all(lp["ok"] for lp in loops):
        print("a read loop could not be found in the disassembly", file=sys.stderr)
    ok = validity["any_valid"] and all(lp["ok"] for lp in loops) and not failed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
