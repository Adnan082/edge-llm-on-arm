"""plots.py on a synthetic processed table: it runs, reads nothing but results/processed/, and two
runs give byte-identical files (CLAUDE.md §9: figures regenerate exactly)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from edge_llm import analyse, micro, plots, sweep
from edge_llm.schema import MicroRecord
from tests.micro_fixtures import micro_record

REPO = Path(__file__).resolve().parents[1]


def synthetic_points() -> list[dict]:
    """One row per full-sweep point with made-up round numbers (structure only, not data)."""
    cfg = yaml.safe_load((REPO / "configs" / "sweep.yaml").read_text())
    rows = []
    for pair in sweep.pairs(cfg, "full"):
        for point in pair.points():
            te = sweep.parse_test(point.test)
            prefill = te.kind == "pp"
            pred = 1000.0 / point.threads**-0.5 if prefill else 100.0 * point.threads**0.5
            measured = pred * (0.1 if prefill else 0.4) * (1.05 if point.build == "kleidiai" else 1)
            cls = "smmla" if prefill else "sdot"
            rows.append(
                {
                    "config_id": point.config_id, "pair_id": point.pair_id, "model": point.model,
                    "quant": point.quant, "build": point.build, "threads": point.threads,
                    "test": point.test, "phase": te.phase,
                    "tokens": te.tokens if prefill else 1,
                    "measured_median": measured, "q1": measured * 0.99, "q3": measured * 1.01,
                    "predicted_tps": pred, "ratio": measured / pred,
                    "arith_intensity": 300.0 if prefill else 3.0,
                    "achieved_GOPS": 10.0 * point.threads, "B": 30e9 * point.threads,
                    "C_weight_class": cls, "C_weight": 300e9 * point.threads,
                    "C_weight_class_sustained": cls, "C_weight_sustained": 200e9 * point.threads,
                }
            )  # fmt: skip
    return rows


@pytest.fixture(scope="module")
def processed(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("processed")
    points = synthetic_points()
    # write_csv writes empty cells for columns the synthetic rows lack; plots does not read them.
    analyse.write_csv(folder / "points.csv", analyse.POINT_COLUMNS, points)
    pairs = analyse.build_kleidiai(
        [{**p, "iqr_over_median": 0.01, "still_noisy": False} for p in points]
    )
    analyse.write_csv(folder / "kleidiai.csv", analyse.KLEIDIAI_COLUMNS, pairs)
    return folder


def test_every_figure_is_written_as_png_and_svg(processed, tmp_path):
    written = plots.make_all(processed, tmp_path)
    names = {p.name for p in written}
    assert names == {f"{n}.{e}" for n in plots.FIGURES for e in ("png", "svg")}
    assert all(p.stat().st_size > 5_000 for p in written)


def test_two_runs_give_byte_identical_files(processed, tmp_path):
    first = plots.make_all(processed, tmp_path / "a")
    second = plots.make_all(processed, tmp_path / "b")
    for a, b in zip(first, second):
        assert a.name == b.name
        assert a.read_bytes() == b.read_bytes(), a.name


def test_files_carry_no_timestamp(processed, tmp_path):
    for path in plots.make_all(processed, tmp_path):
        data = path.read_bytes()
        if path.suffix == ".svg":
            assert b"<dc:date>" not in data and b"<dc:creator>" not in data
        else:
            assert b"Software" not in data  # matplotlib's PNG text chunk (version string)


def test_plots_reads_only_the_processed_folder():
    src = (REPO / "src" / "edge_llm" / "plots.py").read_text(encoding="utf8")
    assert "results/raw" not in src and "results/predictions" not in src


def test_the_rq4_figure_appears_only_when_micro_csv_exists_and_is_byte_stable(processed, tmp_path):
    import shutil

    assert not any(p.name.startswith("dot_int8") for p in plots.make_all(processed, tmp_path / "0"))
    folder = tmp_path / "processed"
    shutil.copytree(processed, folder)
    micro.write_csv(folder / "micro.csv", micro.derive_rows(MicroRecord.from_dict(micro_record())))
    first = plots.make_all(folder, tmp_path / "a")
    second = plots.make_all(folder, tmp_path / "b")
    assert {"dot_int8.png", "dot_int8.svg"} <= {p.name for p in first}
    for a, b in zip(first, second):
        assert a.read_bytes() == b.read_bytes(), a.name
    assert (tmp_path / "a" / "dot_int8.png").stat().st_size > 5_000
