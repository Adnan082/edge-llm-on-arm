"""infra/hf_fetch.py hashing: git blob ids must equal what `git hash-object` would give."""

import hashlib

from infra import hf_fetch


def test_git_blob_sha1_known_answers(tmp_path):
    empty = tmp_path / "empty"
    empty.write_bytes(b"")
    hello = tmp_path / "hello"
    hello.write_bytes(b"hello\n")
    # Values printed by `git hash-object` for these contents.
    assert hf_fetch.git_blob_sha1(empty) == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert hf_fetch.git_blob_sha1(hello) == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_verify_checks_sha256_for_lfs_files_and_blob_id_for_small_ones(tmp_path):
    data = b"some weights" * 1000
    f = tmp_path / "model.safetensors"
    f.write_bytes(data)
    good = {
        "rfilename": "model.safetensors",
        "size": len(data),
        "lfs": {"sha256": hashlib.sha256(data).hexdigest()},
        "blobId": "unused-for-lfs",
    }
    assert hf_fetch.verify(f, good)[0]
    assert not hf_fetch.verify(f, {**good, "lfs": {"sha256": "0" * 64}})[0]
    assert not hf_fetch.verify(f, {**good, "size": len(data) + 1})[0]

    small = tmp_path / "config.json"
    small.write_bytes(b"hello\n")
    entry = {
        "rfilename": "config.json",
        "size": 6,
        "blobId": "ce013625030ba8dba906f756967f9e9ca394464a",
    }
    assert hf_fetch.verify(small, entry)[0]
    assert not hf_fetch.verify(small, {**entry, "blobId": "e" * 40})[0]
