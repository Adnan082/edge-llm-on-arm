"""Run the sweep: one llama-bench call per point, builds back to back, one raw JSON per call.

    python -m bench.run_sweep --set pilot|full      (make bench SET=pilot|full)

For every pair (model, format, threads, test) of configs/sweep.yaml the two builds run one after
the other, and which build goes first alternates from pair to pair (CLAUDE.md §7.7). Each call
writes results/raw/bench/<session_id>/<config_id>.json: llama-bench's JSON output, unchanged,
inside a record (schema BenchRecord) that also holds the session, repo commit, llama.cpp commit,
model SHA256, the exact command, the pinning and the load average before and after.

Fixed settings (ADR-019) come from configs/sweep.yaml `bench_settings` and are written on every
command line. Pinning (ADR-014): `taskset -c 0-(t-1)` plus `-t t --cpu-mask <first t cores>
--cpu-strict 1`, so thread i runs on core i, as in the bandwidth and peak programs.

Median and IQR come from llama-bench's per-repetition samples (`samples_ts`). If IQR/median is
above 5 %, the point is run once more after its pair, saved as <config_id>__2.json and both stay
(CLAUDE.md §7.4). Nothing is overwritten: points already done in this session are skipped, so a
crashed run, or one cut off by a VM restart, is resumed by running the same command again (do not
run `make env` first: it would start a new session). After a pilot, the repeat noise of every
point and an estimate of the full sweep's wall time are written next to the records.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

from bench import common
from bench.common import MODELS_DIR, REPO_ROOT, WORK_DIR
from edge_llm import pilot, sweep
from edge_llm.schema import SCHEMA_VERSION, BenchRecord
from edge_llm.stats import is_noisy, summarise

OUT_ROOT = common.RESULTS_DIR / "raw" / "bench"
ENV_DIR = common.RESULTS_DIR / "raw" / "env"
NOTABLE_RE = re.compile(
    r"model buffer size|load_mode|kleidi|repack|warn|error|fail|flash|fallback", re.IGNORECASE
)
CALL_TIMEOUT_S = 6 * 3600  # a single llama-bench call; the slowest expected is minutes


def load_cfg() -> dict:
    return yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())


# --- the command line ----------------------------------------------------------------------


def bench_command(
    cfg: dict, point: sweep.Point, model_path: Path, repetitions: int, llama_bench: Path
) -> list[str]:
    """The exact command for one call: fixed settings spelt out, pinned to cores 0..t-1."""
    s = cfg["bench_settings"]
    te = sweep.parse_test(point.test)
    n_prompt, n_gen = (te.tokens, 0) if te.kind == "pp" else (0, te.tokens)
    return [
        "taskset", "-c", sweep.taskset_cpus(point.threads),
        str(llama_bench),
        "-m", str(model_path),
        "-p", str(n_prompt), "-n", str(n_gen), "-d", str(te.depth),
        "-t", str(point.threads),
        "-C", sweep.cpu_mask(point.threads), "--cpu-strict", "1",
        "-b", str(s["n_batch"]), "-ub", str(s["n_ubatch"]),
        "-ctk", s["type_k"], "-ctv", s["type_v"],
        "-fa", str(s["flash_attn"]),
        "-lm", s["load_mode"], "--repack", str(s["repack"]),
        "--poll", str(s["poll"]), "--prio", str(s["prio"]), "--delay", str(s["delay"]),
        "-r", str(repetitions),
        "-o", "json",
    ]  # fmt: skip


# --- model files ---------------------------------------------------------------------------


def read_sums(path: Path) -> dict[str, str]:
    """{file name: sha256} from a sha256sum-format file."""
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


def model_info(alias: str, quant: str, models_dir: Path = MODELS_DIR) -> dict:
    """Model file, its SHA256 (from SHA256SUMS), and the checks against the tensor table."""
    name = f"{alias}_{quant}.gguf"
    path = models_dir / name
    table_path = common.RESULTS_DIR / "models" / f"{alias}_{quant}.json"
    table = json.loads(table_path.read_text())
    sums = read_sums(models_dir / "SHA256SUMS")
    if name not in sums:
        raise SystemExit(f"{name} has no entry in {models_dir / 'SHA256SUMS'}: run make models")
    if sums[name] != table["sha256"]:
        raise SystemExit(f"{name}: SHA256SUMS differs from {common.rel(table_path)}")
    size = path.stat().st_size
    if size != table["file_bytes"]:
        raise SystemExit(f"{name}: {size} bytes, tensor table says {table['file_bytes']}")
    return {
        "file": common.rel(path),
        "sha256": sums[name],
        "file_bytes": size,
        "table_file_bytes": table["file_bytes"],
        "table": common.rel(table_path),
    }


# --- one call ------------------------------------------------------------------------------


def record_path(session_id: str, config_id: str, attempt: int) -> Path:
    suffix = "" if attempt == 1 else f"__{attempt}"
    return OUT_ROOT / session_id / f"{config_id}{suffix}.json"


def run_call(
    cfg: dict,
    session_id: str,
    point: sweep.Point,
    pair: sweep.Pair,
    attempt: int,
    repetitions: int,
    context: dict,
) -> dict:
    """Run llama-bench once, return the validated record dict (not yet written)."""
    llama_bench = WORK_DIR / f"build-{point.build}" / "bin" / "llama-bench"
    info = model_info(point.model, point.quant)
    model_path = REPO_ROOT / info["file"]
    cmd = bench_command(cfg, point, model_path, repetitions, llama_bench)
    print(f"[{pair.index}] {point.config_id} (attempt {attempt}): {' '.join(cmd[4:])}", flush=True)

    load_before = common.loadavg()
    started = datetime.now(UTC)
    t0 = time.monotonic()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=CALL_TIMEOUT_S,
    )
    wall = time.monotonic() - t0
    load_after = common.loadavg()

    log_dir = WORK_DIR / "bench-logs" / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{point.config_id}__{attempt}.stderr.txt").write_text(proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(
            f"{point.config_id}: llama-bench exited {proc.returncode}\n{proc.stderr[-2000:]}"
        )
    rows = json.loads(proc.stdout)
    samples = rows[0]["samples_ts"]
    notable = [ln.strip() for ln in proc.stderr.splitlines() if NOTABLE_RE.search(ln)][:60]
    order = sweep.build_order(pair.index).index(point.build) + 1
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "bench",
        "session_id": session_id,
        "captured_utc": started.isoformat(timespec="seconds"),
        "config_id": point.config_id,
        "pair_id": point.pair_id,
        "model_alias": point.model,
        "quant": point.quant,
        "build": point.build,
        "threads": point.threads,
        "test": point.test,
        "attempt": attempt,
        "repetitions": repetitions,
        "pair_index": pair.index,
        "order_in_pair": order,
        "repo": context["repo"],
        "llama_cpp": context["llama_cpp"],
        "model": info,
        "settings": {**cfg["bench_settings"], "warmup": True},
        "command": cmd,
        "pinning": {
            "method": "taskset -c 0-(t-1); llama-bench -t t --cpu-mask <first t cores> --cpu-strict 1",
            "taskset_cpus": sweep.taskset_cpus(point.threads),
            "cpu_mask": sweep.cpu_mask(point.threads),
            "cpu_strict": 1,
            "threads": point.threads,
        },
        "loadavg_before": load_before,
        "loadavg_after": load_after,
        "wall_seconds": wall,
        "returncode": proc.returncode,
        "summary": summarise(samples),
        "noisy": is_noisy(samples),
        "llama_bench": rows,
        "stderr_notable": notable,
    }
    BenchRecord.from_dict(record)  # raises if llama-bench did not run what we asked for
    return record


def write_record(path: Path, record: dict) -> None:
    """Write a record, never over an existing one, and all-or-nothing.

    The JSON goes to a temporary file first and is renamed into place, so a crash or a VM restart
    in the middle of a write cannot leave a half file that would break the resumed run.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    tmp = path.with_name(f".{path.name}.tmp")  # not *.json: never read as a record
    with open(tmp, "w") as f:
        f.write(json.dumps(record, indent=2) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def status(session_id: str, config_id: str) -> str:
    """'todo', 'rerun' (first run noisy, no second yet) or 'done'."""
    first = record_path(session_id, config_id, 1)
    if not first.exists():
        return "todo"
    if (
        json.loads(first.read_text())["noisy"]
        and not record_path(session_id, config_id, 2).exists()
    ):
        return "rerun"
    return "done"


def run_pair(cfg: dict, session_id: str, pair: sweep.Pair, context: dict) -> list[dict]:
    """Both builds of a pair in order, then one re-run of every noisy point. Returns new records."""
    reps = sweep.repetitions(cfg, pair)
    new: list[dict] = []
    points = pair.points()
    for point in points:
        if status(session_id, point.config_id) == "todo":
            rec = run_call(cfg, session_id, point, pair, 1, reps, context)
            write_record(record_path(session_id, point.config_id, 1), rec)
            new.append(rec)
            report(rec)
    for point in points:
        if status(session_id, point.config_id) == "rerun":
            rec = run_call(cfg, session_id, point, pair, 2, reps, context)
            write_record(record_path(session_id, point.config_id, 2), rec)
            new.append(rec)
            report(rec)
    return new


def report(rec: dict) -> None:
    s = rec["summary"]
    flag = "  NOISY" if rec["noisy"] else ""
    print(
        f"    median {s['median']:.2f} tok/s, IQR/median {100 * s['iqr_over_median']:.2f} %,"
        f" wall {rec['wall_seconds']:.0f} s{flag}",
        flush=True,
    )


# --- pilot summary -------------------------------------------------------------------------


def model_sizes(cfg: dict) -> dict:
    sizes = {}
    for alias in cfg["models"]:
        for quant in cfg["quants"]:
            t = json.loads((common.RESULTS_DIR / "models" / f"{alias}_{quant}.json").read_text())
            sizes[(alias, quant)] = {
                "file_bytes": t["file_bytes"],
                "N_blk": t["totals"]["N_blk"],
                "W_all": t["totals"]["W_all"],
            }
    return sizes


def load_session_records(session_id: str) -> list[dict]:
    folder = OUT_ROOT / session_id
    return [
        json.loads(p.read_text())
        for p in sorted(folder.glob("*.json"))
        if not p.name.startswith("_")
    ]


def write_pilot_summary(cfg: dict, session_id: str) -> None:
    pilot_ids = {p.config_id for pair in sweep.pairs(cfg, "pilot") for p in pair.points()}
    records = [r for r in load_session_records(session_id) if r["config_id"] in pilot_ids]
    missing = pilot_ids - {r["config_id"] for r in records}
    if missing:
        print(f"pilot summary skipped: {len(missing)} pilot points have no record", file=sys.stderr)
        return
    noise = pilot.noise_rows(records)
    estimate = pilot.estimate_full_sweep(records, cfg, model_sizes(cfg))
    folder = OUT_ROOT / session_id
    # A leading underscore keeps these out of analyse.py's per-point records.
    (folder / "_pilot_summary.json").write_text(
        json.dumps({"session_id": session_id, "noise": noise, "estimate": estimate}, indent=2)
        + "\n"
    )
    (folder / "_pilot_summary.md").write_text(pilot.render_markdown(session_id, noise, estimate))
    print(f"wrote {folder / '_pilot_summary.md'}")
    print(
        f"estimated wall time of the full sweep: {estimate['estimate_hours']:.1f} h"
        f" (upper bound {estimate['upper_bound_hours']:.1f} h)"
    )


# --- main ----------------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", dest="set_name", choices=("pilot", "full"), required=True)
    parser.add_argument("--allow-dirty", action="store_true", help="run from uncommitted code")
    parser.add_argument("--only", help="run only pairs whose pair_id contains this text")
    args = parser.parse_args()

    cfg = load_cfg()
    session_id = common.current_session_id()
    if not (ENV_DIR / f"{session_id}.json").exists():
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

    pairs = sweep.pairs(cfg, args.set_name)
    if args.only:
        pairs = [p for p in pairs if args.only in p.pair_id]
    todo = [p for p in pairs if any(status(session_id, x.config_id) != "done" for x in p.points())]
    print(
        f"session {session_id}, set {args.set_name}: {len(pairs)} pairs, "
        f"{len(pairs) - len(todo)} already done, {len(todo)} to run"
    )
    start = time.monotonic()
    for n, pair in enumerate(todo, 1):
        run_pair(cfg, session_id, pair, context)
        print(
            f"  pair {n}/{len(todo)} done, {(time.monotonic() - start) / 60:.1f} min elapsed",
            flush=True,
        )

    if args.set_name == "pilot" and not args.only:
        write_pilot_summary(cfg, session_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
