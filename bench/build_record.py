"""Check the two llama.cpp builds against each other and write the build record.

    python -m bench.build_record --check-caches   # after configuring both builds
    python -m bench.build_record --write          # after building both

`infra/build_llamacpp.sh` calls both. The record (results/raw/build/<session_id>_build.json)
holds: the pinned commit and CMake options of each build; the compiler flags actually used for
the ggml-cpu and KleidiAI sources (from compile_commands.json); KleidiAI's version, URL and
hash; and the KleidiAI lines of the configure log. Standard library plus edge_llm.schema.

The only differences allowed between the two CMakeCache.txt files are KleidiAI entries (including
the nine settings its download adds, KLEIDIAI_SIDE_EFFECT_KEYS) and paths (the builds live in
different folders). Anything else means the comparison in RQ3 would
not be like for like, so `--check-caches` fails and lists the keys. If a listed key is
harmless, rerun with CACHE_DIFF_ALLOW="KEY1,KEY2"; the allowance is written to the record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import sys
from datetime import UTC, datetime
from pathlib import Path

from bench import common
from bench.common import LLAMACPP_DIR, REPO_ROOT, WORK_DIR

BUILD_BINARIES = ("llama-bench", "llama-quantize", "llama-completion")
RECORD_DIR = common.RESULTS_DIR / "raw" / "build"
PIN_FILE = REPO_ROOT / "infra" / "llamacpp.commit"

# ggml-cpu sources whose compile command matters for the results (matmul kernels, dispatch).
CPU_SOURCES = (
    "ggml/src/ggml-cpu/ggml-cpu.c",
    "ggml/src/ggml-cpu/ggml-cpu.cpp",
    "ggml/src/ggml-cpu/repack.cpp",
    "ggml/src/ggml-cpu/vec.cpp",
    "ggml/src/ggml-cpu/ops.cpp",
    "ggml/src/ggml-cpu/quants.c",
    "ggml/src/ggml-cpu/arch/arm/quants.c",
    "ggml/src/ggml-cpu/arch/arm/repack.cpp",
    "ggml/src/ggml-cpu/llamafile/sgemm.cpp",
    "ggml/src/ggml-cpu/kleidiai/kleidiai.cpp",
    "ggml/src/ggml-cpu/kleidiai/kernels.cpp",
)
PATH_KEY_SUFFIXES = ("_DIR", "_PATH", "_BINARY_DIR", "_SOURCE_DIR")
# Entries CMake itself adds to the cache when KleidiAI's source is downloaded with FetchContent
# and its sub-project is configured (seen in the Day 2 build record, where each needed a
# CACHE_DIFF_ALLOW). They are caused by -DGGML_CPU_KLEIDIAI=ON and change no compiler flag of
# ggml's own sources, so they count as KleidiAI differences, in a list of their own.
KLEIDIAI_SIDE_EFFECT_KEYS = (
    "CMAKE_NUMBER_OF_MAKEFILES",
    "CMAKE_PROJECT_VERSION",
    "CMAKE_PROJECT_VERSION_MAJOR",
    "CMAKE_PROJECT_VERSION_MINOR",
    "CMAKE_PROJECT_VERSION_PATCH",
    "CMAKE_PROJECT_VERSION_TWEAK",
    "FETCHCONTENT_FULLY_DISCONNECTED",
    "FETCHCONTENT_QUIET",
    "FETCHCONTENT_UPDATES_DISCONNECTED",
)
CONFIGURE_LINE_RE = re.compile(
    r"kleidi|ARM detected|GGML_MACHINE_SUPPORTS|OpenMP|CPU backend|llamafile|repack",
    re.IGNORECASE,
)
CODEGEN_FLAG_RE = re.compile(r"^-(O\d|Ofast|g\d?|m\S+|f\S+|D\S+|std=\S+|march=\S+|mcpu=\S+)$")


# --- CMake cache comparison ----------------------------------------------------------------


def parse_cache(text: str) -> dict[str, str]:
    """Every `KEY:TYPE=value` entry of a CMakeCache.txt, as {KEY: value}."""
    entries: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith(("//", "#")) or "=" not in line:
            continue
        name_type, _, value = line.partition("=")
        entries[name_type.split(":", 1)[0]] = value
    return entries


def is_kleidiai_key(name: str) -> bool:
    return "kleidiai" in name.lower()


def is_path_key(name: str) -> bool:
    return name.endswith(PATH_KEY_SUFFIXES) or name == "CMAKE_HOME_DIRECTORY"


def diff_caches(
    a_text: str, b_text: str, a_dir: str, b_dir: str, allow: tuple[str, ...] = ()
) -> dict:
    """Keys that differ between two caches, sorted into allowed kinds and unexpected ones.

    Each build's own folder is replaced by a placeholder first, so a path that merely contains
    the build folder (e.g. a binary dir) compares equal.
    """
    a, b = parse_cache(a_text), parse_cache(b_text)
    na = {k: v.replace(a_dir, "<BUILD_DIR>") for k, v in a.items()}
    nb = {k: v.replace(b_dir, "<BUILD_DIR>") for k, v in b.items()}
    out: dict[str, list[str]] = {
        "kleidiai_keys": [],
        "kleidiai_side_effect_keys": [],
        "path_keys": [],
        "allowed_by_user": [],
        "unexpected_keys": [],
    }
    for key in sorted(na.keys() | nb.keys()):
        if na.get(key) == nb.get(key):
            continue
        if is_kleidiai_key(key):
            out["kleidiai_keys"].append(key)
        elif key in KLEIDIAI_SIDE_EFFECT_KEYS:
            out["kleidiai_side_effect_keys"].append(key)
        elif key in allow:
            out["allowed_by_user"].append(key)
        elif is_path_key(key):
            out["path_keys"].append(key)
        else:
            out["unexpected_keys"].append(
                f"{key}: baseline={na.get(key)!r} kleidiai={nb.get(key)!r}"
            )
    return out


def build_dir(name: str) -> Path:
    return WORK_DIR / f"build-{name}"


def check_caches() -> int:
    allow = tuple(k for k in os.environ.get("CACHE_DIFF_ALLOW", "").split(",") if k)
    texts = {n: (build_dir(n) / "CMakeCache.txt").read_text() for n in common.BUILD_NAMES}
    d = diff_caches(
        texts["baseline"],
        texts["kleidiai"],
        str(build_dir("baseline")),
        str(build_dir("kleidiai")),
        allow,
    )
    print(f"cache differences: {len(d['kleidiai_keys'])} KleidiAI, {len(d['path_keys'])} path")
    base = parse_cache(texts["baseline"])
    kai = parse_cache(texts["kleidiai"])
    if base.get("GGML_CPU_KLEIDIAI") == "ON" or kai.get("GGML_CPU_KLEIDIAI") != "ON":
        print("GGML_CPU_KLEIDIAI should be OFF in baseline and ON in kleidiai", file=sys.stderr)
        return 1
    if d["unexpected_keys"]:
        print("the two builds differ in more than KleidiAI entries and paths:", file=sys.stderr)
        for line in d["unexpected_keys"]:
            print("  " + line, file=sys.stderr)
        return 1
    return 0


# --- compile commands ----------------------------------------------------------------------


def command_args(entry: dict) -> list[str]:
    return list(entry["arguments"]) if "arguments" in entry else shlex.split(entry["command"])


def codegen_flags(args: list[str]) -> list[str]:
    """The flags that change generated code (-O, -m*, -f*, -D, -std), without include paths."""
    return [a for a in args[1:] if CODEGEN_FLAG_RE.match(a)]


def compile_flags(
    entries: list[dict], source_root: Path, kleidiai_marker: str = "kleidiai"
) -> dict:
    """Flags per ggml-cpu source, and KleidiAI library sources grouped by identical flags."""
    root = str(source_root).replace("\\", "/")
    cpu: dict[str, dict] = {}
    groups: dict[tuple, list[str]] = {}
    for e in entries:
        f = e["file"].replace("\\", "/")
        rel = f[len(root) + 1 :] if f.startswith(root + "/") else f
        args = command_args(e)
        if rel in CPU_SOURCES:
            cpu[rel] = {
                "compiler": args[0],
                "flags": codegen_flags(args),
                "command": shlex.join(args),
            }
        elif "_deps/" in f and kleidiai_marker in f.lower():
            groups.setdefault(tuple(codegen_flags(args)), []).append(f.rsplit("/", 1)[-1])
    return {
        "ggml_cpu": cpu,
        "kleidiai_library": [
            {"flags": list(flags), "n_files": len(files), "files": sorted(files)}
            for flags, files in sorted(groups.items())
        ],
    }


# --- KleidiAI facts ------------------------------------------------------------------------


def kleidiai_from_cmake(text: str) -> dict:
    """Version, URL and MD5 that ggml-cpu/CMakeLists.txt pins for the KleidiAI download."""
    tag = re.search(r'set\(KLEIDIAI_COMMIT_TAG\s+"([^"]+)"\)', text)
    url = re.search(r'set\(KLEIDIAI_DOWNLOAD_URL\s+"([^"]+)"\)', text)
    md5 = re.search(r'set\(KLEIDIAI_RELEASE_ARCHIVE_MD5\s+"([0-9a-f]{32})"\)', text)
    if not (tag and url and md5):
        raise SystemExit("could not find the KleidiAI pin in ggml/src/ggml-cpu/CMakeLists.txt")
    return {
        "tag": tag.group(1),
        "url": url.group(1).replace("${KLEIDIAI_COMMIT_TAG}", tag.group(1)),
        "md5": md5.group(1),
    }


def hash_file(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def kleidiai_info() -> dict:
    cmake = (LLAMACPP_DIR / "ggml/src/ggml-cpu/CMakeLists.txt").read_text()
    info = kleidiai_from_cmake(cmake)
    info["pinned_in"] = "ggml/src/ggml-cpu/CMakeLists.txt"
    deps = build_dir("kleidiai") / "_deps"
    archives = sorted(deps.rglob("kleidiai*.tar.gz")) if deps.exists() else []
    if archives:
        info["archive_md5_computed"] = hash_file(archives[0], "md5")
        info["archive_sha256_computed"] = hash_file(archives[0], "sha256")
        info["archive_md5_matches_pin"] = info["archive_md5_computed"] == info["md5"]
    else:
        info["archive_md5_computed"] = info["archive_sha256_computed"] = None
        info["archive_md5_matches_pin"] = None
    info["source_dir"] = str(Path("work/build-kleidiai/_deps/kleidiai-src"))
    return info


# --- record --------------------------------------------------------------------------------


def one_build(name: str) -> dict:
    bdir = build_dir(name)
    cache_text = (bdir / "CMakeCache.txt").read_text()
    cache = parse_cache(cache_text)
    entries = json.loads((bdir / "compile_commands.json").read_text())
    log_path = bdir / "configure.log"
    log_text = log_path.read_text() if log_path.exists() else ""
    interesting = ("CMAKE_", "GGML_", "LLAMA_")
    return {
        "dir": common.rel(bdir),
        "cmake_options": {
            k: v
            for k, v in sorted(cache.items())
            if k.startswith(interesting) and not is_path_key(k)
        },
        "compile_flags": compile_flags(entries, LLAMACPP_DIR),
        "configure_log": common.rel(log_path) if log_path.exists() else None,
        "configure_log_kleidiai_lines": [
            ln.strip() for ln in log_text.splitlines() if "kleidiai" in ln.lower()
        ],
        "configure_log_selected_lines": [
            ln.strip() for ln in log_text.splitlines() if CONFIGURE_LINE_RE.search(ln)
        ][:60],
        "binaries": {
            b: {"sha256": hash_file(bdir / "bin" / b, "sha256")}
            for b in BUILD_BINARIES
            if (bdir / "bin" / b).exists()
        },
    }


def make_record(session_id: str) -> dict:
    allow = tuple(k for k in os.environ.get("CACHE_DIFF_ALLOW", "").split(",") if k)
    diff = diff_caches(
        (build_dir("baseline") / "CMakeCache.txt").read_text(),
        (build_dir("kleidiai") / "CMakeCache.txt").read_text(),
        str(build_dir("baseline")),
        str(build_dir("kleidiai")),
        allow,
    )
    return {
        "schema_version": 1,
        "kind": "build",
        "session_id": session_id,
        "captured_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo": common.git_state(REPO_ROOT),
        "llama_cpp": {
            **common.git_state(LLAMACPP_DIR, ignore_prefixes=()),
            "expected_commit": PIN_FILE.read_text().strip(),
        },
        "kleidiai": kleidiai_info(),
        "cache_diff": diff,
        "builds": {n: one_build(n) for n in common.BUILD_NAMES},
    }


def same_except_time(a: dict, b: dict) -> bool:
    drop = lambda r: {k: v for k, v in r.items() if k != "captured_utc"}
    return drop(a) == drop(b)


def write_record() -> int:
    from edge_llm.schema import BuildRecord  # needs the project venv (pip install -e .)

    session_id = common.current_session_id()
    record = make_record(session_id)
    BuildRecord.from_dict(record)  # stops here if the builds are not what the spec requires
    base = RECORD_DIR / f"{session_id}_build.json"
    existing = sorted(RECORD_DIR.glob(f"{session_id}_build*.json"))
    if existing and same_except_time(json.loads(existing[-1].read_text()), record):
        print(f"{existing[-1]}: already describes these builds, not rewriting")
        return 0
    print(f"wrote {common.write_new_json(base, record)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-caches", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    return check_caches() if args.check_caches else write_record()


if __name__ == "__main__":
    raise SystemExit(main())
