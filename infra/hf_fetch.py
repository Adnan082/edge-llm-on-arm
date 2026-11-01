#!/usr/bin/env python3
"""Download one Hugging Face model at a pinned revision and verify every file.

    python3 infra/hf_fetch.py --repo Qwen/Qwen3-0.6B --revision <40-hex sha> --dest work/hf/small

Standard library only. The expected hashes come from the Hub API for that exact revision:
large files (the safetensors) carry a SHA256; small files carry only their git blob id, which
is the SHA1 of "blob <size>\\0<content>", so that is what is checked for them. A file that is
already on disk is hashed again and kept only if it matches. Writes <dest>/MANIFEST.json
with the verified hashes. Safe to re-run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

API = "https://huggingface.co/api/models/{repo}/revision/{rev}?blobs=true"
FILE_URL = "https://huggingface.co/{repo}/resolve/{rev}/{name}"
SKIP = {".gitattributes", "README.md"}  # not needed to convert the model
CHUNK = 1 << 20


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    """git's object id for a file: SHA1 over "blob <size>\\0" followed by the content."""
    h = hashlib.sha1()
    h.update(f"blob {path.stat().st_size}\0".encode())
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def fetch_listing(repo: str, rev: str) -> list[dict]:
    with urllib.request.urlopen(API.format(repo=repo, rev=rev), timeout=60) as resp:
        info = json.load(resp)
    if info.get("sha") != rev:
        raise SystemExit(f"Hub returned revision {info.get('sha')}, expected {rev}")
    return [s for s in info["siblings"] if s["rfilename"] not in SKIP]


def verify(path: Path, entry: dict) -> tuple[bool, dict]:
    """Check a file against the listing; returns (ok, facts for the manifest)."""
    facts = {
        "name": entry["rfilename"],
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "git_blob_id": git_blob_sha1(path),
        "expected_sha256": (entry.get("lfs") or {}).get("sha256"),
        "expected_git_blob_id": entry.get("blobId"),
    }
    ok = facts["size"] == entry["size"]
    if facts["expected_sha256"]:
        ok = ok and facts["sha256"] == facts["expected_sha256"]
    else:
        ok = ok and facts["git_blob_id"] == facts["expected_git_blob_id"]
    return ok, facts


def download(url: str, dest: Path, tries: int = 3) -> None:
    part = dest.with_name(dest.name + ".part")
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp, open(part, "wb") as out:
                while chunk := resp.read(CHUNK):
                    out.write(chunk)
            part.replace(dest)
            return
        except OSError as exc:
            print(f"  attempt {attempt}/{tries} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit(f"could not download {url}")


def fetch(repo: str, rev: str, dest: Path) -> Path:
    if not re.fullmatch(r"[0-9a-f]{40}", rev):
        raise SystemExit(f"revision must be a full 40-character commit sha, got {rev!r}")
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    for entry in fetch_listing(repo, rev):
        path = dest / entry["rfilename"]
        ok = False
        if path.exists():
            ok, facts = verify(path, entry)
            print(f"{entry['rfilename']}: on disk, hash {'ok' if ok else 'WRONG - fetching again'}")
        if not ok:
            print(f"{entry['rfilename']}: downloading {entry['size']:,} bytes")
            download(FILE_URL.format(repo=repo, rev=rev, name=entry["rfilename"]), path)
            ok, facts = verify(path, entry)
            if not ok:
                raise SystemExit(f"{entry['rfilename']}: hash does not match the Hub listing")
        manifest.append(facts)
    out = dest / "MANIFEST.json"
    out.write_text(json.dumps({"repo": repo, "revision": rev, "files": manifest}, indent=2) + "\n")
    print(f"{repo}@{rev[:12]}: {len(manifest)} files verified -> {out}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--dest", required=True, type=Path)
    args = parser.parse_args()
    fetch(args.repo, args.revision, args.dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
