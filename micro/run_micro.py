"""RQ4: build micro/dot_int8.cpp, check it, time it, save the record.

    python -m micro.run_micro          (make micro; then `make micro-table` / `make figures`)

Order of work (the same shape as micro/run_peak.py):
  1. compile: dot_int8_ref.cpp twice (scalar with auto-vectorisation off, auto-vec with nothing
     forced), then dot_int8.cpp, and link; the exact flags are recorded;
  2. `dot_int8 --check`: every variant against scalar, bit for bit, on random and extreme inputs.
     If anything differs, nothing is timed and nothing is saved;
  3. disassemble every kernel, save micro/disasm/dot_int8_<variant>.s, and check that its hot loop
     holds the expected instruction (sdot v-form, smmla, sdot z-form; none in scalar; auto-vec is
     only recorded). A failed check is reported and the variant is left out of "best", but the data
     are still saved (as for the peak loops, ADR-022);
  4. `dot_int8 --time` under `taskset -c 0` (thread 0 on core 0, ADR-014): 8 variants x 2 working
     sets, 30 timed repetitions each, every timed output compared with scalar's;
  5. write results/raw/micro/<session_id>.json (validated against MicroRecord) with the bandwidth
     and peak records the fractions are taken against, named and hashed.

The bandwidth reference is the newest valid record in results/raw/bandwidth/ (by `captured_utc`),
the peak reference is the record the roofline uses (roofline.PEAK_RECORD); override either on the
command line. The fractions themselves are computed later, from the saved record, by
`python -m edge_llm.micro` (raw files hold measurements and named references, not derived ratios).
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
from edge_llm import micro, peak, roofline
from edge_llm.schema import SCHEMA_VERSION, BandwidthRecord, MicroRecord, PeakRecord, SchemaError
from edge_llm.stats import summarise
from micro.run_peak import objdump_function

SOURCE_MAIN = REPO_ROOT / "micro" / "dot_int8.cpp"
SOURCE_REF = REPO_ROOT / "micro" / "dot_int8_ref.cpp"
BIN_DIR = WORK_DIR / "bin"
BINARY = BIN_DIR / "dot_int8"
OBJ_SCALAR = BIN_DIR / "dot_int8_scalar.o"
OBJ_AUTOVEC = BIN_DIR / "dot_int8_autovec.o"
FLAGS_FILE = BIN_DIR / "dot_int8.flags"
OUT_DIR = common.RESULTS_DIR / "raw" / "micro"
BANDWIDTH_DIR = common.RESULTS_DIR / "raw" / "bandwidth"
DISASM_DIR = REPO_ROOT / "micro" / "disasm"
COMMON_FLAGS = ["-O3", "-mcpu=native", "-std=c++17", "-Wall", "-Wextra"]
# GCC 13: -fno-tree-vectorize should switch both vectorisers off; the other two are belt and braces.
# The disassembly check, not the flag, is what proves the scalar loop has no SIMD multiply.
NO_VECTORIZE = ["-fno-tree-vectorize", "-fno-tree-loop-vectorize", "-fno-tree-slp-vectorize"]


# --- building ------------------------------------------------------------------------------


def compile_commands() -> list[list[str]]:
    return [
        [
            "g++", *COMMON_FLAGS, *NO_VECTORIZE, "-DDOT_REF_NAME=dot_scalar",
            "-c", str(SOURCE_REF), "-o", str(OBJ_SCALAR),
        ],
        [
            "g++", *COMMON_FLAGS, "-DDOT_REF_NAME=dot_autovec",
            "-c", str(SOURCE_REF), "-o", str(OBJ_AUTOVEC),
        ],
        [
            "g++", *COMMON_FLAGS, str(SOURCE_MAIN), str(OBJ_SCALAR), str(OBJ_AUTOVEC),
            "-o", str(BINARY),
        ],
    ]  # fmt: skip


def ensure_binary() -> dict:
    """Compile if the binary is missing, older than a source, or the flags changed."""
    cmds = [shlex.join(c) for c in compile_commands()]
    flags_now = "\n".join(cmds)
    newest_source = max(SOURCE_MAIN.stat().st_mtime, SOURCE_REF.stat().st_mtime)
    stale = (
        not BINARY.exists()
        or BINARY.stat().st_mtime < newest_source
        or common.read_text(FLAGS_FILE) != flags_now
    )
    if stale:
        BIN_DIR.mkdir(parents=True, exist_ok=True)
        for cmd in compile_commands():
            print("compiling:", shlex.join(cmd), flush=True)
            subprocess.run(cmd, check=True)
        FLAGS_FILE.write_text(flags_now + "\n")
    return {
        "path": common.rel(BINARY),
        "sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
        "compile_commands": cmds,
        "compiler": common.run(["g++", "--version"]),
    }


# --- running the program -------------------------------------------------------------------


def run_program(args: list[str], core: int = 0) -> tuple[dict, int]:
    """One program run under `taskset -c <core>`: (parsed JSON, return code)."""
    cmd = ["taskset", "-c", str(core), str(BINARY), *args]
    print(" ".join(cmd), flush=True)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=False)  # stderr: progress
    if not proc.stdout.strip():
        raise SystemExit(f"dot_int8 produced no output (exit {proc.returncode})")
    out = json.loads(proc.stdout)
    return out, proc.returncode


def to_point(run: dict, result: dict) -> dict:
    """One variant/working-set result of the program -> a MicroPoint dict."""
    ns = result["samples_ns_per_call"]
    s = summarise(ns)
    weight_bytes = int(result["weight_bytes"])
    return {
        "variant": result["variant"],
        "family": result["family"],
        "accumulators": result["accumulators"],
        "working_set": result["working_set"],
        "rows": result["rows"],
        "k": result["k"],
        "weight_bytes": weight_bytes,
        "macs_per_call": weight_bytes * result["macs_per_weight_byte"],
        "macs_per_weight_byte": result["macs_per_weight_byte"],
        "calls_per_rep": result["calls_per_rep"],
        "pinning": {
            "method": "taskset -c 0 plus pthread_setaffinity_np: thread 0 on core 0 (ADR-014)",
            "taskset_cpus": "0",
            "process_cpus": run["process_cpus"],
            "observed_cpu": result["observed_cpu"],
            "getcpu_ok": bool(result["getcpu_ok"]) and bool(run["pinned"])
            and result["observed_cpu"] == 0,
        },
        "reps_warmup": result["reps_warmup"],
        "reps_timed": result["reps_timed"],
        "output_matches_scalar": bool(result["output_matches_scalar"]),
        "samples_ns_per_call": ns,
        "median_ns": s["median"],
        "q1_ns": s["q1"],
        "q3_ns": s["q3"],
        "iqr_ns": s["iqr"],
        "max_ns": s["max"],
        "checksum": result["checksum"],
    }  # fmt: skip


# --- disassembly ---------------------------------------------------------------------------


def check_disassembly(binary: Path, disasm_dir: Path = DISASM_DIR) -> dict:
    """Disassemble and check every kernel; save micro/disasm/dot_int8_<variant>.s for each."""
    out: dict[str, dict] = {}
    disasm_dir.mkdir(parents=True, exist_ok=True)
    for variant in micro.VARIANTS:
        name = micro.function_name(variant)
        text = objdump_function(binary, name)
        insns = peak.parse_instructions(text)
        loop = micro.hot_loop_for(variant, insns)
        check = micro.check_loop(variant, loop, [t for _, t in insns])
        header = "\n".join(f"#   {t}" for t in loop)
        path = disasm_dir / f"dot_int8_{variant}.s"
        path.write_text(
            f"# ===== {name}: hot loop = the {len(loop)} instructions of the innermost conditional"
            f" backward branch holding the expected instruction ({check['expected']}) =====\n"
            f"{header}\n# ===== whole function =====\n{text}"
        )
        check["file"] = common.rel(path)
        out[variant] = check
    return out


# --- the references the fractions are taken against ----------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest_bandwidth_record(raw_dir: Path = BANDWIDTH_DIR) -> tuple[Path, BandwidthRecord]:
    """The newest bandwidth record by `captured_utc` that validates and has the per-variant L1
    validity table (ADR-021): only those define B(t) and B1(t)."""
    best: tuple[str, Path, BandwidthRecord] | None = None
    for path in sorted(raw_dir.glob("*.json")):
        try:
            rec = BandwidthRecord.from_dict(json.loads(path.read_text()))
        except (SchemaError, ValueError, KeyError, TypeError):
            continue
        if rec.validity and (best is None or rec.captured_utc > best[0]):
            best = (rec.captured_utc, path, rec)
    if best is None:
        raise SystemExit(f"no valid bandwidth record in {raw_dir}: run `make bandwidth` first")
    return best[1], best[2]


def build_references(bw_path: Path, bw: BandwidthRecord, pk_path: Path, pk: PeakRecord) -> dict:
    """B(1), B1(1), C_sdot(1), C_smmla(1) by the same rules as the roofline (§8), with the files
    they came from."""
    hw = roofline.hardware_from_records(bw, pk)
    if hw.b1.get(1) is None:
        raise SystemExit(f"{bw_path}: no valid one-stream variant at 1 thread, so no B1(1)")
    at = hw.details["bandwidth"]["1"]
    return {
        "bandwidth_record": {
            "path": common.rel(bw_path),
            "sha256": sha256_file(bw_path),
            "session_id": bw.session_id,
            "phase": bw.phase,
            "captured_utc": bw.captured_utc,
            "threads": 1,
            "B_best_Bps": hw.b[1],
            "B_best_variant": {"accumulators": at["accumulators"], "streams": at["streams"]},
            "B_one_stream_Bps": hw.b1[1],
            "rule": "best valid read variant at 1 thread (ADR-017, ADR-021); B1 = best valid k=1",
        },
        "peak_record": {
            "path": common.rel(pk_path),
            "sha256": sha256_file(pk_path),
            "session_id": pk.session_id,
            "threads": 1,
            "C_sdot_ops_per_s": hw.c["sdot"][1],
            "C_smmla_ops_per_s": hw.c["smmla"][1],
            "rule": "1 x 90th percentile of the 1-thread rate x operations per instruction"
            " (ADR-023); one MAC = 2 operations",
        },
    }  # fmt: skip


def kernel_description() -> dict:
    return {
        "operation": "y[m] = sum_k W[m][k] * x[k], int8 x int8 -> int32 (decode-shaped"
        " matrix-vector product)",
        "k": micro.K,
        "rows": micro.ROWS,
        "weight_bytes": {ws: micro.ROWS[ws] * micro.K for ws in micro.WORKING_SETS},
        "threads": 1,
        "core": 0,
        "accumulators": "4 and 8 for every SIMD family; the best is reported (ADR-022 rule)",
        "smmla_macs_per_weight_byte": 2,
        "smmla_note": "SMMLA multiplies 2 weight rows by 2 activation vectors at once, so it does"
        " twice the MACs per weight byte of the other variants. macs_per_call counts both vectors"
        " (useful MACs); weight bytes per second is the like-for-like rate. The weights are"
        " repacked into the interleaved SMMLA layout before timing (same bytes as W).",
        "scalar_flags": "-O3 -mcpu=native " + " ".join(NO_VECTORIZE),
        "autovec_flags": "-O3 -mcpu=native (nothing forced)",
    }


# --- main ----------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reps", type=int, default=micro.MIN_REPS, help="timed repeats (>= 30)")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--seeds", type=int, default=6, help="random seeds in the --check run")
    parser.add_argument("--target-ms", type=float, default=25.0, help="length of one repetition")
    parser.add_argument("--bandwidth-record", type=Path, help="default: the newest valid one")
    parser.add_argument("--peak-record", type=Path, default=REPO_ROOT / roofline.PEAK_RECORD)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--again", action="store_true", help="save as __2 if already measured")
    args = parser.parse_args(argv)

    session_id = common.current_session_id()
    target = args.out_dir / f"{session_id}.json"
    if target.exists() and not args.again:
        print(f"{target} already exists: skipping (use --again to add a second measurement)")
        return 0

    binary = ensure_binary()

    # 1. Correctness first: no timing unless every variant is bit-identical to scalar.
    check, code = run_program(["--check", "--seeds", str(args.seeds)])
    for v in check["variants"]:
        print(f"  check {v['variant']:<9} {v['cases']} cases, {v['mismatches']} mismatches")
    if code != 0 or not check["ok"]:
        print("--check FAILED: a variant differs from scalar. Nothing was timed.", file=sys.stderr)
        return 1
    check["returncode"] = code

    # 2. Which instructions are really in the hot loops.
    disasm = check_disassembly(BINARY)
    for variant, c in disasm.items():
        if c["family"] == "autovec":
            what = f"GCC chose: {c['simd_multiply_in_loop'] or 'no SIMD multiply'}"
        else:
            what = f"expected {c['expected']}" + (
                f" x{c['expected_count']}" if "expected_count" in c else ""
            )
        status = "ok" if c["ok"] else "FAILED"
        print(f"  loop {variant:<9} {c['loop_instructions']:>3} insns  {what}  {status}")
    bad = [v for v, c in disasm.items() if not c["ok"]]

    # 3. What the fractions are taken against.
    if args.bandwidth_record:
        bw_path = args.bandwidth_record
        bw = BandwidthRecord.from_dict(json.loads(bw_path.read_text()))
    else:
        bw_path, bw = latest_bandwidth_record()
    pk = PeakRecord.from_dict(json.loads(args.peak_record.read_text()))
    references = build_references(bw_path, bw, args.peak_record, pk)
    print(f"  bandwidth reference: {references['bandwidth_record']['path']}")
    print(f"  peak reference:      {references['peak_record']['path']}")

    # 4. Time everything.
    loadavg_before = common.loadavg()
    run, code = run_program(
        [
            "--time", "--reps", str(args.reps), "--warmup", str(args.warmup),
            "--target-ms", str(args.target_ms),
        ]
    )  # fmt: skip
    loadavg_after = common.loadavg()
    if code != 0:
        print(f"dot_int8 --time exited with {code}", file=sys.stderr)

    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "micro",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "binary": binary,
        "host": {"loadavg_before": loadavg_before, "loadavg_after": loadavg_after},
        "sve_vector_bits": run["sve_vector_bits"],
        "features": run["features"],
        "kernel": kernel_description(),
        "check": check,
        "points": [to_point(run, r) for r in run["points"]],
        "disasm": disasm,
        "references": references,
    }
    try:
        validated = MicroRecord.from_dict(record)  # raises before anything is written
    except SchemaError as e:
        print(f"record rejected, nothing saved: {e}", file=sys.stderr)
        return 1
    path = common.write_new_json(target, record)
    print(f"wrote {path}")
    for line in micro.summary_lines(micro.derive_rows(validated)):
        print(line)
    if bad:
        print("hot loops that failed the check (left out of 'best'): " + ", ".join(bad),
              file=sys.stderr)  # fmt: skip
    return 1 if (bad or code != 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
