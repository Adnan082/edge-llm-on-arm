"""Helpers shared by every recorder that runs on the VM. Standard library only.

Run recorders from the repo root as modules (`python -m bench.env_capture`) so that
`from bench.common import ...` works the same way in scripts and in tests.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = REPO_ROOT / "work"
LLAMACPP_DIR = WORK_DIR / "llama.cpp"
MODELS_DIR = WORK_DIR / "models"
RESULTS_DIR = REPO_ROOT / "results"
BUILD_NAMES = ("baseline", "kleidiai")  # work/build-<name>

# `make env` writes the session id here and every later step on the same VM sitting reuses it
# (ARCHITECTURE.md §3).
SESSION_FILE = WORK_DIR / "session_id"

# Changes under these folders do not make a record "dirty": every recorder adds files there, so
# counting them would make each record after the first one show `dirty: true` (CLAUDE.md §7.1
# wants the sweep to start from a clean pushed commit). micro/disasm/ holds the disassembly that
# `make peak` writes: evidence produced on the VM, committed with the results.
DIRTY_IGNORE_PREFIXES = ("results/", "micro/disasm/")


def run(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 30,
    strip: bool = True,
) -> str | None:
    """Return stdout+stderr of a command, or None if it is missing or fails."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    out = proc.stdout + proc.stderr
    return out.strip() if strip else out


def loadavg() -> list[float] | None:
    """1/5/15-minute load average; None where the OS has none (the laptop's Windows)."""
    return list(os.getloadavg()) if hasattr(os, "getloadavg") else None


def read_text(path: str | Path) -> str | None:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


# --- git state ---------------------------------------------------------------------------


def porcelain_paths(porcelain: str) -> list[str]:
    """Paths named in `git status --porcelain` output (both sides of a rename)."""
    paths: list[str] = []
    for line in porcelain.splitlines():
        # "XY path", "?? path" or "R  old -> new"; tolerate a stripped leading space.
        m = re.match(r"^[ MADRCU?!]{1,2}\s+(.+)$", line)
        if not m:
            continue
        for part in m.group(1).split(" -> "):
            paths.append(part.strip().strip('"'))
    return paths


def is_dirty(porcelain: str, ignore_prefixes: tuple[str, ...] = DIRTY_IGNORE_PREFIXES) -> bool:
    """True if any changed path lies outside the ignored folders."""
    return any(not p.startswith(ignore_prefixes) for p in porcelain_paths(porcelain))


def git_state(repo: Path, ignore_prefixes: tuple[str, ...] = DIRTY_IGNORE_PREFIXES) -> dict:
    """Commit and cleanliness of a git checkout; both null if it is not one.

    This is the one place that decides what "dirty" means. For the llama.cpp checkout pass
    `ignore_prefixes=()`: nothing is ever written inside it.
    """
    if not (repo / ".git").exists():
        return {"commit": None, "dirty": None}
    status = run(["git", "status", "--porcelain"], cwd=repo, strip=False)
    return {
        "commit": run(["git", "rev-parse", "HEAD"], cwd=repo),
        "dirty": None if status is None else is_dirty(status, ignore_prefixes),
    }


# --- session id --------------------------------------------------------------------------


def save_session_id(session_id: str) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(session_id + "\n")


def current_session_id() -> str:
    """The id `make env` saved for this sitting; stops the program if there is none."""
    sid = read_text(SESSION_FILE)
    if not sid:
        raise SystemExit(f"no session id at {SESSION_FILE}: run `make env` first")
    return sid


# --- writing records ---------------------------------------------------------------------


def next_free_path(path: Path) -> Path:
    """`x.json` if free, else `x__2.json`, `x__3.json`, ... (ARCHITECTURE.md rule 2)."""
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}__{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def write_new_json(path: Path, record: dict) -> Path:
    """Write a record, never overwriting: an existing file is kept and the next free name used."""
    target = next_free_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x") as f:  # "x" fails instead of truncating if a race made it exist
        f.write(json.dumps(record, indent=2) + "\n")
    return target


def rel(path: Path) -> str:
    """Repo-relative path as a string, for records."""
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# --- compiling the small C++ programs ------------------------------------------------------


def ensure_binary(source: Path, binary: Path, flags_file: Path, cmd: list[str]) -> dict:
    """Compile `source` with `cmd` if the binary is missing, older than the source, or the flags
    changed since the last build; return what a record needs to say about the binary."""
    import hashlib
    import shlex
    import subprocess

    flags_now = shlex.join(cmd)
    stale = (
        not binary.exists()
        or binary.stat().st_mtime < source.stat().st_mtime
        or read_text(flags_file) != flags_now
    )
    if stale:
        binary.parent.mkdir(parents=True, exist_ok=True)
        print("compiling:", flags_now)
        subprocess.run(cmd, check=True)
        flags_file.write_text(flags_now + "\n")
    return {
        "path": rel(binary),
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "compile_command": flags_now,
        "compiler": run(["g++", "--version"]),
    }
