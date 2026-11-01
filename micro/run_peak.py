"""Measure C(t): build micro/peak.cpp, check its loops, run it at every thread count, save a record.

    python -m micro.run_peak          (make peak)

Order of work (stops at the first failure so no time is spent on a wrong loop):
  1. compile peak.cpp (flags recorded);
  2. disassemble every hot loop, save micro/disasm/peak_<class>.s, and check that each loop holds
     the expected instruction the expected number of times, and no loads or stores;
  3. time every class at every thread count in configs/sweep.yaml under `taskset -c 0-(t-1)` with
     thread i on core i (ADR-014): 16 independent chains per loop at every t, plus 8 and 28 chains
     at one thread to show that more chains do not raise the peak;
  4. write results/raw/peak/<session_id>.json (validated against PeakRecord);
  5. in the same objdump pass over each build's ggml CPU library: count FMLALB, FMLALT and
     FP16 FMLA (.8h) (evidence for ADR-015); save the disassembly of the tiled flash-attention
     function (or what it was inlined into) to micro/disasm/ and count scalar `fmadd s` and
     vector `fmla .4s` in it, to see whether the compiler vectorised the plain-C GEMM
     fallback (ADR-020). Written to results/raw/peak/<session_id>_ggml_f16_instructions.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from bench import common
from bench.common import REPO_ROOT, WORK_DIR
from edge_llm import peak
from edge_llm.schema import SCHEMA_VERSION, GgmlInstructionRecord, PeakPoint, PeakRecord
from edge_llm.stats import summarise

SOURCE = REPO_ROOT / "micro" / "peak.cpp"
BINARY = WORK_DIR / "bin" / "peak"
FLAGS_FILE = WORK_DIR / "bin" / "peak.flags"
OUT_DIR = common.RESULTS_DIR / "raw" / "peak"
DISASM_DIR = REPO_ROOT / "micro" / "disasm"
COMPILE_FLAGS = ["-O3", "-mcpu=native", "-std=c++17", "-fopenmp", "-Wall", "-Wextra"]
REPS = 20
# instructions of each class per loop iteration, per accumulator count (see peak.cpp); FP16 FMLA
# issues two per chain per iteration (+x*y then -x*y), the others one.
INSTR_PER_ACC = {"sdot": 1, "smmla": 1, "fmla_f16": 2, "fmlal": 1, "fma32": 1}


def compile_command() -> list[str]:
    return ["g++", *COMPILE_FLAGS, str(SOURCE), "-o", str(BINARY)]


def ensure_binary() -> dict:
    return common.ensure_binary(SOURCE, BINARY, FLAGS_FILE, compile_command())


def run_once(t: int, extra: list[str]) -> dict:
    """One program run at t threads, under taskset -c 0-(t-1). Returns the parsed JSON."""
    cpus = f"0-{t - 1}"
    cmd = ["taskset", "-c", cpus, str(BINARY), "--threads", str(t), *extra]
    print(" ".join(cmd), flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not proc.stdout.strip():
        raise SystemExit(f"peak produced no output (exit {proc.returncode}): {proc.stderr}")
    out = json.loads(proc.stdout)
    out["taskset_cpus"] = cpus
    out["returncode"] = proc.returncode
    return out


def to_point(run: dict, result: dict) -> dict:
    """One class/accumulator result of the program -> a PeakPoint dict (instructions -> ops)."""
    t = run["threads"]
    cls = result["class"]
    opi = peak.ops_per_instruction(cls, run["sve_vector_bits"] or 128)
    instr = result["samples_instr_per_s"]
    ops = [i * opi for i in instr]
    s = summarise(ops)
    return {
        "instr_class": cls,
        "threads": t,
        "accumulators": result["accumulators"],
        "instr_per_iter": result["instr_per_iter"],
        "iters": result["iters"],
        "pinning": {
            "method": "taskset -c 0-(t-1) plus pthread_setaffinity_np: thread i on core i",
            "taskset_cpus": run["taskset_cpus"],
            "process_cpus": run["process_cpus"],
            "observed_cpus": result["observed_cpus"],
            "getcpu_ok": bool(result["getcpu_ok"]) and result["observed_cpus"] == list(range(t)),
        },
        "reps_warmup": result["reps_warmup"],
        "reps_timed": result["reps_timed"],
        "ops_per_instruction": opi,
        "samples_instr_per_s": instr,
        "samples_ops_per_s": ops,
        "median": s["median"],
        "q1": s["q1"],
        "q3": s["q3"],
        "iqr": s["iqr"],
        "max": s["max"],
        "checksum": result["checksum"],
    }


# --- disassembly ---------------------------------------------------------------------------


def objdump_function(binary: Path, name: str) -> str:
    return (
        common.run(
            ["objdump", "-d", "-C", "--no-show-raw-insn", f"--disassemble={name}", str(binary)],
            timeout=60,
            strip=False,
        )
        or ""
    )


def check_disassembly(binary: Path, disasm_dir: Path = DISASM_DIR) -> dict:
    """Disassemble and check every kernel; save one .s file per class. Returns the record part."""
    out: dict[str, dict] = {}
    for cls in peak.PEAK_CLASSES:
        sections, checks = [], []
        for acc in peak.LADDER_ACCUMULATORS:
            name = f"peak_{cls}_a{acc}"
            text = objdump_function(binary, name)
            loop = peak.hot_loop(peak.parse_instructions(text))
            check = peak.check_loop(cls, loop, acc, acc * INSTR_PER_ACC[cls])
            check["function"] = name
            checks.append(check)
            sections.append(
                f"# ===== {name}: hot loop = the {len(loop)} instructions ending in the"
                f" last backward branch =====\n{text}"
            )
        path = disasm_dir / f"peak_{cls}.s"
        disasm_dir.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sections))
        out[cls] = {"file": common.rel(path), "checks": checks}
    return out


# --- ggml's own library: F16 instructions (ADR-015) and the attention kernel (ADR-020) ------

F16_PATTERNS = {
    "fmlalb": re.compile(r"^fmlalb\s"),
    "fmlalt": re.compile(r"^fmlalt\s"),
    "fmla_8h": re.compile(r"^fmla\s+v\d+\.8h"),
}
# Scalar and vector F32 multiply-adds, to see whether the compiler vectorised the plain-C
# fallback of the tiled flash-attention GEMM (ggml-cpu/simd-gemm.h:247-264). Static counts of
# instructions in the function, not a measure of how often they run.
ATTN_PATTERNS = {
    "fmadd_s": re.compile(r"^fmadd\s+s\d"),  # scalar fused multiply-add
    "fmul_s": re.compile(r"^fmul\s+s\d"),  # scalar multiply (if the add was not fused)
    "fadd_s": re.compile(r"^fadd\s+s\d"),
    "fmla_4s": re.compile(r"^fmla\s+v\d+\.4s"),  # NEON F32 FMLA (what C_fma32 measures)
    "fmla_sve_s": re.compile(r"^fmla\s+z\d+\.s"),  # SVE F32 FMLA
}
TILED_NAME = "ggml_compute_forward_flash_attn_ext_tiled"
# tried in this order: the function itself, then the functions it may have been inlined into
ATTN_FALLBACKS = (
    (TILED_NAME, "tiled"),
    ("ggml_compute_forward_flash_attn_ext_f16", "inlined_into_f16"),
    ("ggml_compute_forward_flash_attn_ext", "inlined_into_flash_attn_ext"),
)
SYMBOL_RE = re.compile(r"^[0-9a-f]+ <(.+)>:$")


def wanted_symbol(name: str) -> bool:
    """Symbols whose disassembly is kept for the attention evidence."""
    if "one_chunk" in name:
        return False
    return "ggml_compute_forward_flash_attn_ext" in name or "simd_gemm" in name


def scan_objdump(lines) -> tuple[dict[str, int], list[dict], dict[str, list[str]]]:
    """One pass over `objdump -d -C --no-show-raw-insn` text.

    Returns the F16 instruction counts, the ten symbols holding the most of them, and the
    instruction lines of every symbol `wanted_symbol` accepts.
    """
    total = Counter()
    by_symbol: dict[str, Counter] = {}
    captured: dict[str, list[str]] = {}
    symbol = "?"
    for line in lines:
        line = line.rstrip("\n")
        m = SYMBOL_RE.match(line)
        if m:
            symbol = m.group(1)
            if wanted_symbol(symbol):
                captured.setdefault(symbol, [])
            continue
        m = peak.INSN_RE.match(line)
        if not m:
            continue
        if symbol in captured:
            captured[symbol].append(line)
        text = re.sub(r"\s+", " ", m.group(2)).strip()
        for key, pattern in F16_PATTERNS.items():
            if pattern.match(text):
                total[key] += 1
                by_symbol.setdefault(symbol, Counter())[key] += 1
    top = sorted(by_symbol.items(), key=lambda kv: -sum(kv[1].values()))[:10]
    counts = {k: total[k] for k in F16_PATTERNS}
    return counts, [{"symbol": s, **{k: c[k] for k in F16_PATTERNS}} for s, c in top], captured


def count_f16_instructions(lines) -> tuple[dict[str, int], list[dict]]:
    """Counts of the three F16 instruction forms, and the ten symbols that hold the most."""
    counts, top, _ = scan_objdump(lines)
    return counts, top


def _count_attn(insn_lines: list[str]) -> dict[str, int]:
    out = {k: 0 for k in ATTN_PATTERNS}
    out["instructions"] = 0
    for line in insn_lines:
        m = peak.INSN_RE.match(line)
        if not m:
            continue
        out["instructions"] += 1
        text = re.sub(r"\s+", " ", m.group(2)).strip()
        for key, pattern in ATTN_PATTERNS.items():
            if pattern.match(text):
                out[key] += 1
    return out


def attention_evidence(captured: dict[str, list[str]]) -> tuple[dict, str]:
    """Pick the tiled flash-attention function (or what it was inlined into) and count in it.

    Returns the record part and the disassembly text to save. `found` is False if no such
    symbol exists (a stripped library): then there is no evidence, and the record says so.
    """
    targets: list[str] = []
    kind = None
    for needle, label in ATTN_FALLBACKS:
        hits = [s for s in captured if needle in s and "simd_gemm" not in s]
        if hits:
            targets, kind = sorted(hits), label
            break
    # simd_gemm is a header function: if it was not inlined it is a symbol of its own
    targets += sorted(s for s in captured if "simd_gemm" in s)
    if not targets:
        return {"found": False, "target_kind": None, "symbols": [], "counts": {}}, ""
    symbols, total = [], Counter()
    parts = []
    for sym in targets:
        c = _count_attn(captured[sym])
        symbols.append({"symbol": sym, **c})
        total.update(c)
        parts.append(f"# ===== {sym} =====\n" + "\n".join(captured[sym]) + "\n")
    counts = dict(total)
    vec = counts["fmla_4s"] + counts["fmla_sve_s"]
    dominant = (
        "none"
        if not (vec or counts["fmadd_s"])
        else ("vector" if vec > counts["fmadd_s"] else "scalar")
    )
    return {
        "found": True,
        "target_kind": kind,
        "symbols": symbols,
        "counts": counts,
        "dominant_fma": dominant,
    }, "\n".join(parts)


def ggml_libraries(build: str) -> list[Path]:
    """The ggml CPU library of a build; the llama-bench binary itself if ggml is linked in."""
    bin_dir = WORK_DIR / f"build-{build}" / "bin"
    libs = sorted({p.resolve() for p in bin_dir.glob("libggml-cpu*.so*")})
    return libs or [bin_dir / "llama-bench"]


def ggml_f16_record(session_id: str, disasm_dir: Path = DISASM_DIR) -> dict:
    builds = {}
    for build in common.BUILD_NAMES:
        files, total = [], Counter()
        captured: dict[str, list[str]] = {}
        for lib in ggml_libraries(build):
            print(f"objdump {lib} ...", flush=True)
            proc = subprocess.Popen(
                ["objdump", "-d", "-C", "--no-show-raw-insn", str(lib)],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            counts, top, cap = scan_objdump(proc.stdout)
            proc.wait()
            if proc.returncode != 0:
                raise SystemExit(f"objdump failed on {lib}")
            total.update(counts)
            captured.update(cap)
            files.append(
                {
                    "path": common.rel(lib),
                    "sha256": hashlib.sha256(lib.read_bytes()).hexdigest(),
                    "counts": counts,
                    "top_symbols": top,
                }
            )
        attn, text = attention_evidence(captured)
        attn["disasm_file"] = None
        if attn["found"]:
            path = disasm_dir / f"ggml_flash_attn_tiled_{build}.s"
            disasm_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            attn["disasm_file"] = common.rel(path)
        builds[build] = {
            "files": files,
            "counts": {k: total[k] for k in F16_PATTERNS},
            "flash_attn_tiled": attn,
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "ggml_f16_instructions",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "builds": builds,
    }


# --- main ----------------------------------------------------------------------------------


def thread_counts() -> list[int]:
    import yaml

    return list(yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())["threads"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reps", type=int, default=REPS, help="timed repeats per point (>= 20)")
    parser.add_argument("--threads", help="comma list, default: sweep.yaml")
    parser.add_argument(
        "--skip-ggml", action="store_true", help="skip the ggml F16 instruction count"
    )
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--again", action="store_true", help="save as __2 if already measured")
    args = parser.parse_args()

    session_id = common.current_session_id()
    target = args.out_dir / f"{session_id}.json"
    if target.exists() and not args.again:
        print(f"{target} already exists: skipping (use --again to add a second measurement)")
        return 0

    threads = [int(x) for x in args.threads.split(",")] if args.threads else thread_counts()
    binary = ensure_binary()

    disasm = check_disassembly(BINARY)
    bad = [c for d in disasm.values() for c in d["checks"] if not c["ok"]]
    for d in disasm.values():
        for c in d["checks"]:
            print(
                f"  {c['function']:<22} loop {c['loop_instructions']:>3} insns  {c['counts']}"
                f"  expected {c['expected_per_iteration']}  {'ok' if c['ok'] else 'FAILED'}"
            )
    if bad:
        print(
            "a hot loop is not what peak.cpp assumes: see micro/disasm/; nothing was timed",
            file=sys.stderr,
        )
        return 1

    loadavg_before = common.loadavg()
    points, sve_bits, failed = [], 0, False
    for t in threads:
        accs = (
            ",".join(str(a) for a in peak.LADDER_ACCUMULATORS)
            if t == 1
            else str(peak.BASE_ACCUMULATORS)
        )
        run = run_once(t, ["--acc", accs, "--reps", str(args.reps)])
        failed = failed or run["returncode"] != 0
        sve_bits = run["sve_vector_bits"]
        points += [to_point(run, r) for r in run["results"]]
    loadavg_after = common.loadavg()

    ladder = peak.ladder_summary([PeakPoint.from_dict(p) for p in points])
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "peak",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "binary": binary,
        "host": {"loadavg_before": loadavg_before, "loadavg_after": loadavg_after},
        "sve_vector_bits": sve_bits,
        "points": points,
        "acc_check": ladder,
        "disasm": disasm,
    }
    validated = PeakRecord.from_dict(record)  # raises on a bad count, pin check or failed check

    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = common.write_new_json(target, record)
    print(f"wrote {path}")
    print_table(validated, threads)
    for a in ladder:
        key = next(k for k in a if k.startswith("ratio_"))
        print(
            f"accumulator check {a['instr_class']:<9} {key} = {a[key]:.3f}",
            "PASS" if a["pass"] else "FAIL",
        )

    if not args.skip_ggml:
        ggml_path = common.next_free_path(args.out_dir / f"{session_id}_ggml_f16_instructions.json")
        g = ggml_f16_record(session_id)
        GgmlInstructionRecord.from_dict(g)
        common.write_new_json(ggml_path, g)
        print(f"wrote {ggml_path}")
        for build, b in g["builds"].items():
            print(f"  {build:<9} {b['counts']}")
            attn = b["flash_attn_tiled"]
            if attn["found"]:
                print(
                    f"  {build:<9} flash_attn tiled ({attn['target_kind']}): {attn['counts']}"
                    f" -> mostly {attn['dominant_fma']} FMAs; {attn['disasm_file']}"
                )
            else:
                print(
                    f"  {build:<9} flash_attn tiled: no such symbol in the library (stripped?)",
                    file=sys.stderr,
                )
    return 1 if failed else 0


def print_table(record: PeakRecord, threads: list[int]) -> None:
    c = peak.c_of_t(record.points)
    print(f"{'class':<10}" + "".join(f"{'t=' + str(t) + ' Gop/s':>14}" for t in threads))
    for cls in peak.PEAK_CLASSES:
        print(f"{cls:<10}" + "".join(f"{c[cls][t] / 1e9:>14.1f}" for t in threads))


if __name__ == "__main__":
    raise SystemExit(main())
