"""Day 8 investigation, the VM part: Check A (output-layer variants) and Check C (perf profile).

    python -m bench.day8 tables | a | c | all [--allow-dirty]      (make day8-variants / make day8)

Labelled "Day 8 investigation": none of this enters the v1 comparison or the headline figure
(`analyse.py` reads the sweep session only). It runs in the SAME session as Day 7 (`make env` has
already been run there; do not start a new one). The analysis half, `python -m edge_llm.day8`,
also runs anywhere (`make day8-analyse`). Check B needs no VM.

tables  Tensor tables of the two Q4_0 variants (`infra/make_variants.sh` calls this). Stops if
        `output.weight` is not the intended type or any other tensor differs from small_Q4_0.
a       Check A: tg128 at t = 1 and 8, both builds, for small_Q4_0 (measured again today as the
        reference), small_Q4_0outq8 and small_Q4_0outq4. Same `bench_settings`, same pinning, same
        interleaving (the build that runs first alternates), same re-run rule as the sweep: this
        is `run_sweep.run_pair`. Records: results/raw/bench/<session_id>/<config_id>.json, e.g.
        small_Q4_0outq8_kleidiai_t1_tg128. The prediction is in `edge_llm/day8.py`, written before
        the first run.
c       Check C: `perf record` of pp128 at t = 1 for Q4_0 and Q8_0, both builds (at most 30 min).
        If perf is missing or cannot sample, writes "perf not available" and stops. Otherwise the
        top 20 of `perf report --stdio` per run go to results/raw/perf/<session_id>/. The llama-bench
        timing inside a perf run is NOT data (profiling overhead); the profile is the result.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

from bench import common, run_sweep
from bench.common import MODELS_DIR, REPO_ROOT, WORK_DIR
from edge_llm import day8, gguf_table, sweep

PERF_ROOT = common.RESULTS_DIR / "raw" / "perf"
PERF_DATA_DIR = WORK_DIR / "perf"  # perf.data files: large, never committed
PERF_QUANTS = ("Q4_0", "Q8_0")
PERF_TEST = "pp128"
PERF_REPETITIONS = 20  # the profile should be dominated by prompt processing, not model loading
PERF_EVENTS = ("cycles", "cpu-clock")  # hardware cycles if the VM exposes a PMU, else software
PERF_FREQ = 999
PERF_TIMEOUT_S = 30 * 60
TOP = 20


# --- tables -----------------------------------------------------------------------------------


def step_tables(models_dir: Path = MODELS_DIR, out_dir: Path | None = None) -> int:
    """Write results/models/small_<variant>.json, after checking it against small_Q4_0."""
    out_dir = out_dir or common.RESULTS_DIR / "models"
    sweep_cfg = yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())
    sums = gguf_table.read_sha256sums(models_dir / "SHA256SUMS")
    reference = json.loads((out_dir / f"{day8.CHECK_A_ALIAS}_{day8.REFERENCE}.json").read_text())
    status = 0
    for variant, spec in day8.VARIANTS.items():
        if variant == day8.REFERENCE:
            continue
        name = f"{day8.CHECK_A_ALIAS}_{variant}.gguf"
        if name not in sums:
            print(f"{name} is not in SHA256SUMS (run infra/make_variants.sh)", file=sys.stderr)
            status = 1
            continue
        source = gguf_table.source_info(
            models_dir, REPO_ROOT / "work", day8.CHECK_A_ALIAS, variant, sweep_cfg
        )
        table = gguf_table.build_table(
            models_dir / name, day8.CHECK_A_ALIAS, variant, sums[name], source
        )
        problems = day8.check_variant_table(table, reference, str(spec["output_type"]))
        if problems:
            print(f"{name}: NOT the intended variant, no table written:", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            status = 1
            continue
        out = out_dir / f"{day8.CHECK_A_ALIAS}_{variant}.json"
        t = table["totals"]
        print(
            f"{out.name}: {gguf_table.write_table(out, table, False)}  output.weight="
            f"{spec['output_type']}  W_out={t['W_out']:,}  W_blk={t['W_blk']:,}  "
            f"file={table['file_bytes']:,} B  (every other tensor matches small_Q4_0)"
        )
    return status


# --- Check A ----------------------------------------------------------------------------------


def check_a_pairs() -> list[sweep.Pair]:
    return [
        sweep.Pair(i, day8.CHECK_A_ALIAS, variant, threads, day8.CHECK_A_TEST)
        for i, (variant, threads) in enumerate(day8.check_a_pair_specs())
    ]


def preflight_a() -> None:
    """Every file and table is there, the variants are what they claim, sizes and hashes agree."""
    models = common.RESULTS_DIR / "models"
    reference = json.loads((models / f"{day8.CHECK_A_ALIAS}_{day8.REFERENCE}.json").read_text())
    for variant, spec in day8.VARIANTS.items():
        table_path = models / f"{day8.CHECK_A_ALIAS}_{variant}.json"
        if not table_path.exists():
            raise SystemExit(f"{table_path.name} missing: run make day8-variants first")
        if variant != day8.REFERENCE:
            problems = day8.check_variant_table(
                json.loads(table_path.read_text()), reference, str(spec["output_type"])
            )
            if problems:
                raise SystemExit(f"{table_path.name}: {'; '.join(problems)}")
        run_sweep.model_info(day8.CHECK_A_ALIAS, variant)  # file exists, SHA256 and size agree


def write_manifest(path: Path, session_id: str) -> None:
    """Names the Day 8 points in the session folder (a `_` file: never read as a point)."""
    if path.exists():
        return
    record = {
        "kind": "day8_check_a",
        "label": "Day 8 investigation (ADR-025 surprise 2); not part of the v1 comparison",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "prediction": day8.PREDICTION_A,
        "planned_config_ids": [p.config_id for pair in check_a_pairs() for p in pair.points()],
    }
    run_sweep.write_record(path, record)


def step_a(cfg: dict, session_id: str, context: dict) -> int:
    preflight_a()
    folder = run_sweep.OUT_ROOT / session_id
    write_manifest(folder / "_day8_check_a.json", session_id)
    pairs = check_a_pairs()
    todo = [
        p
        for p in pairs
        if any(run_sweep.status(session_id, x.config_id) != "done" for x in p.points())
    ]
    print(f"Check A, session {session_id}: {len(pairs)} pairs, {len(todo)} to run")
    start = time.monotonic()
    for n, pair in enumerate(todo, 1):
        run_sweep.run_pair(cfg, session_id, pair, context)
        print(f"  pair {n}/{len(todo)} done, {(time.monotonic() - start) / 60:.1f} min", flush=True)
    rows = day8.check_a_rows(folder, session_id)
    print("\n".join(["", *day8.render_check_a(rows)]))
    return 0


# --- Check C ----------------------------------------------------------------------------------


def run_text(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL, timeout=timeout
    )


def pick_event(perf: str, scratch: Path) -> tuple[str | None, list[str]]:
    """The first event `perf record` can sample with here, and what was tried."""
    tried = []
    for event in PERF_EVENTS:
        proc = run_text([perf, "record", "-e", event, "-o", str(scratch), "--", "true"])
        if proc.returncode == 0:
            return event, tried
        tried.append(f"{event}: {proc.stderr.strip()[:300] or 'exit ' + str(proc.returncode)}")
    return None, tried


def write_unavailable(perf_dir: Path, session_id: str, reason: str, details: list[str]) -> None:
    rec = {
        "kind": "perf_unavailable",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "reason": reason,
        "details": details,
        "uname": common.run(["uname", "-r"]),
    }
    day8.validate_perf_record(rec)
    path = perf_dir / "_perf_unavailable.json"
    if path.exists():
        print(f"{path} already exists")
    else:
        run_sweep.write_record(path, rec)
    print(f"perf not available: {reason}")


def step_c(
    cfg: dict,
    session_id: str,
    context: dict,
    perf_dir: Path | None = None,
    data_dir: Path | None = None,
) -> int:
    perf_dir = perf_dir or PERF_ROOT / session_id
    data_dir = data_dir or PERF_DATA_DIR / session_id
    data_dir.mkdir(parents=True, exist_ok=True)
    perf = shutil.which("perf")
    if perf is None:
        write_unavailable(
            perf_dir,
            session_id,
            "perf is not installed (install linux-tools for the running kernel, or give up)",
            [],
        )
        return 0
    event, tried = pick_event(perf, data_dir / "probe.data")
    if event is None:
        write_unavailable(perf_dir, session_id, "perf cannot sample on this VM", tried)
        return 0
    version = (run_text([perf, "--version"]).stdout or "").strip()
    print(f"Check C: perf {version}, event {event}")

    for i, quant in enumerate(PERF_QUANTS):
        for build in sweep.build_order(i):
            point = sweep.Point(day8.CHECK_A_ALIAS, quant, build, 1, PERF_TEST)
            path = perf_dir / f"{point.config_id}.json"
            if path.exists():
                print(f"{path.name} exists, skipped")
                continue
            llama_bench = WORK_DIR / f"build-{build}" / "bin" / "llama-bench"
            info = run_sweep.model_info(point.model, point.quant)
            bench_cmd = run_sweep.bench_command(
                cfg, point, REPO_ROOT / info["file"], PERF_REPETITIONS, llama_bench
            )
            data = data_dir / f"{point.config_id}.data"
            cmd = [perf, "record", "-e", event, "-F", str(PERF_FREQ), "-o", str(data), "--"]
            cmd += bench_cmd
            print(
                f"  {point.config_id}: perf record ... {' '.join(bench_cmd[4:6])} ...", flush=True
            )
            rec_proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                stdin=subprocess.DEVNULL,
                timeout=PERF_TIMEOUT_S,
            )
            if rec_proc.returncode != 0:
                raise SystemExit(
                    f"{point.config_id}: perf record failed\n{rec_proc.stderr[-1500:]}"
                )
            rep = run_text(
                [
                    perf,
                    "report",
                    "--stdio",
                    "--no-children",
                    "-i",
                    str(data),
                    "--sort",
                    "dso,symbol",
                ],
                timeout=600,
            )
            if rep.returncode != 0:
                raise SystemExit(f"{point.config_id}: perf report failed\n{rep.stderr[-1500:]}")
            top = day8.parse_perf_report(rep.stdout, TOP)
            samples, _ev = day8.perf_samples(rep.stdout)
            record = {
                "kind": "perf",
                "label": "Day 8 investigation (ADR-025 surprises 1 and 3); not part of the v1 comparison",
                "session_id": session_id,
                "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                "config_id": point.config_id,
                "build": build,
                "quant": quant,
                "threads": 1,
                "test": PERF_TEST,
                "event": event,
                "frequency_hz": PERF_FREQ,
                "perf_version": version,
                "repo": context["repo"],
                "llama_cpp": context["llama_cpp"],
                "model": info,
                "command": cmd,
                "samples": samples,
                "top": top,
                "use_for_analysis": False,
                "caveat": (
                    "profile of the whole llama-bench process, so model loading (repack, KleidiAI "
                    f"conversion) is in it; {PERF_REPETITIONS} repetitions of {PERF_TEST} to "
                    "dominate it. The tokens/s inside this run is not data."
                ),
                "llama_bench_stdout": rec_proc.stdout[-4000:],
            }
            day8.validate_perf_record(record)
            run_sweep.write_record(path, record)
            (perf_dir / f"{point.config_id}.perf_report.txt").write_text(
                day8.trim_perf_report(rep.stdout, TOP)
            )
    print("\n".join(["", *day8.perf_summary(perf_dir)]))
    return 0


# --- main -------------------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("step", choices=("tables", "a", "c", "all"))
    parser.add_argument("--allow-dirty", action="store_true", help="run from uncommitted code")
    args = parser.parse_args()
    if args.step == "tables":
        return step_tables()

    cfg = run_sweep.load_cfg()
    session_id = common.current_session_id()  # the Day 7 session: no new `make env`
    if not (run_sweep.ENV_DIR / f"{session_id}.json").exists():
        raise SystemExit(f"no env record for session {session_id}: run make env first")
    repo = common.git_state(REPO_ROOT)
    llama_cpp = common.git_state(common.LLAMACPP_DIR, ignore_prefixes=())
    if repo["dirty"] and not args.allow_dirty:
        raise SystemExit(
            "the repo has uncommitted changes outside results/: commit, or --allow-dirty"
        )
    if llama_cpp["commit"] != common.read_text(REPO_ROOT / "infra" / "llamacpp.commit"):
        raise SystemExit("work/llama.cpp is not at the pinned commit")
    context = {"repo": repo, "llama_cpp": llama_cpp}

    status = 0
    if args.step in ("a", "all"):
        status |= step_a(cfg, session_id, context)
    if args.step in ("c", "all"):
        status |= step_c(cfg, session_id, context)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
