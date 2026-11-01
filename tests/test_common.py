"""bench/common.py: the dirty check, the session id file, and never-overwrite writes."""

import json
import subprocess

import pytest

from bench import common


def git(repo, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    "porcelain, dirty",
    [
        ("", False),
        ("?? results/raw/bench/x.json\n", False),  # a new result file is not "dirty"
        ("?? results/\n", False),  # git collapses a new folder to its name
        (" M results/models/small_Q4_0.json\n", False),
        (" M src/edge_llm/roofline.py\n", True),
        ("?? infra/new_script.sh\n", True),
        ("M  src/a.py\n?? results/x.json\n", True),  # one real change is enough
        ("R  old.py -> results/new.py\n", True),  # the rename's source is outside results/
        ("M Makefile\n", True),  # first line with its leading space stripped by run()
        ("?? results_old/x\n", True),  # only the exact folder is exempt
        ("?? micro/disasm/peak_sdot.s\n", False),  # `make peak` output, committed with results
        ("?? micro/peak.cpp\n", True),  # but not the code beside it
    ],
)
def test_is_dirty(porcelain, dirty):
    assert common.is_dirty(porcelain) is dirty


def test_porcelain_paths_both_sides_of_a_rename():
    assert common.porcelain_paths("R  a/b.py -> c/d.py\n") == ["a/b.py", "c/d.py"]


def test_git_state_on_a_real_repo(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "code.py").write_text("x = 1\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")

    clean = common.git_state(tmp_path)
    assert clean["dirty"] is False and len(clean["commit"]) == 40

    (tmp_path / "results" / "raw").mkdir(parents=True)
    (tmp_path / "results" / "raw" / "a.json").write_text("{}")
    assert common.git_state(tmp_path)["dirty"] is False  # untracked file under results/

    (tmp_path / "code.py").write_text("x = 2\n")
    assert common.git_state(tmp_path)["dirty"] is True  # tracked file edited

    git(tmp_path, "checkout", "--", "code.py")
    (tmp_path / "stray.txt").write_text("hi")
    assert common.git_state(tmp_path)["dirty"] is True  # untracked file outside results/
    assert common.git_state(tmp_path, ignore_prefixes=("stray", "results/"))["dirty"] is False


def test_git_state_of_a_non_repo(tmp_path):
    assert common.git_state(tmp_path) == {"commit": None, "dirty": None}


def test_session_id_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "SESSION_FILE", tmp_path / "work" / "session_id")
    with pytest.raises(SystemExit, match="make env"):
        common.current_session_id()
    common.save_session_id("2026-11-02T0900Z")
    assert common.current_session_id() == "2026-11-02T0900Z"


def test_write_new_json_never_overwrites(tmp_path):
    p = tmp_path / "d" / "rec.json"
    first = common.write_new_json(p, {"n": 1})
    second = common.write_new_json(p, {"n": 2})
    third = common.write_new_json(p, {"n": 3})
    assert [x.name for x in (first, second, third)] == ["rec.json", "rec__2.json", "rec__3.json"]
    assert json.loads(first.read_text()) == {"n": 1}
    assert json.loads(second.read_text()) == {"n": 2}
