"""All figures, drawn from results/processed/ only. No manual edits (CLAUDE.md §9).

    python -m edge_llm.plots        (make figures)

Reads points.csv and kleidiai.csv (written by analyse.py) and writes five figures as PNG and SVG
into figures/; if micro.csv exists (written by edge_llm.micro) it also writes dot_int8, the RQ4
figure. Output is deterministic: fixed sizes and fonts, sorted inputs, no timestamps or
random ids in the file metadata, so running it twice gives byte-identical files (a test checks).

Colours: phase (prefill blue, decode orange) wherever the phase is the point; four quant colours
only in the thread-scaling figure, always backed by marker shapes. Palette checked with the
dataviz validator; lines and markers are thin, grids recessive.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display needed; must come before pyplot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, NullFormatter

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = Path("results/processed")
FIGURES_DIR = Path("figures")

QUANTS = ["F16", "Q8_0", "Q4_0", "Q4_K_M"]
THREADS = [1, 2, 4, 8]
PREFILL_TESTS = ["pp128", "pp512", "pp2048"]
DECODE_TESTS = ["tg128", "tg128d2048"]
TEST_LABEL = {
    "pp128": "prefill, 128-token prompt",
    "pp512": "prefill, 512-token prompt",
    "pp2048": "prefill, 2048-token prompt",
    "tg128": "decode, empty context",
    "tg128d2048": "decode, after 2048-token context",
}
COVERAGE_TITLE = {
    "F16": "F16: negative control (no KleidiAI kernel)",
    "Q8_0": "Q8_0: fully on KleidiAI",
    "Q4_0": "Q4_0: fully on KleidiAI",
    "Q4_K_M": "Q4_K_M: partial (Q6_K tensors only)",
}
CLASS_LABEL = {"smmla": "SMMLA", "sdot": "SDOT", "fmla_f16": "FP16 FMLA", "fmlal": "FMLALB/T"}

# Light-mode tokens from the dataviz palette (references/palette.md).
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
PHASE_COLOUR = {"prefill": "#2a78d6", "decode": "#eb6834"}
QUANT_COLOUR = {"F16": "#6250d6", "Q8_0": "#1baf7a", "Q4_0": "#e34948", "Q4_K_M": "#c98500"}
QUANT_MARKER = {"F16": "o", "Q8_0": "s", "Q4_0": "^", "Q4_K_M": "D"}
# One shade per test inside a phase (blue ramp 300/450/650; two oranges), plus a marker each.
TEST_COLOUR = {
    "pp128": "#6da7ec",
    "pp512": "#2a78d6",
    "pp2048": "#104281",
    "tg128": "#eb6834",
    "tg128d2048": "#8f3513",
}
TEST_MARKER = {"pp128": "o", "pp512": "s", "pp2048": "^", "tg128": "o", "tg128d2048": "s"}
# Sequential single-hue ramp (blue 100 -> 650) for the heatmap.
RATIO_CMAP = LinearSegmentedColormap.from_list("ratio", ["#cde2fb", "#5598e7", "#104281"])

DPI = 150
_LABEL_BOX = {"facecolor": SURFACE, "edgecolor": "none", "pad": 0.6, "alpha": 0.85}


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "axes.edgecolor": AXIS,
            "axes.labelcolor": INK2,
            "axes.titlecolor": INK,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK2,
            "ytick.labelcolor": INK2,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "text.color": INK,
            "font.family": "DejaVu Sans",
            "legend.frameon": False,
            "legend.fontsize": 8,
            "legend.labelcolor": INK2,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.hashsalt": "edge-llm-on-arm",  # fixed ids, so the SVG is byte-stable
            "svg.fonttype": "path",
        }
    )


def _plain_log(ax, axis: str, minor_labels: tuple[int, ...] = ()) -> None:
    """Log axis labelled 1, 10, 100, ... (not 10^k); minor ticks labelled only at the given
    leading digits (e.g. (2, 5) labels 20, 50, 200, 500)."""
    target = ax.xaxis if axis == "x" else ax.yaxis
    target.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))

    def minor(v: float, _) -> str:
        lead = round(v / 10 ** math.floor(math.log10(v)))
        return f"{v:g}" if lead in minor_labels else ""

    target.set_minor_formatter(FuncFormatter(minor) if minor_labels else NullFormatter())


def _title(fig, title: str, subtitle: str) -> None:
    fig.text(0.01, 0.985, title, ha="left", va="top", fontsize=12, fontweight="bold", color=INK)
    fig.text(0.01, 0.945, subtitle, ha="left", va="top", fontsize=8.5, color=INK2)


def _save(fig, out_dir: Path, name: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext, meta in (("png", {"Software": None}), ("svg", {"Date": None, "Creator": None})):
        path = out_dir / f"{name}.{ext}"
        fig.savefig(path, dpi=DPI, metadata=meta)
        paths.append(path)
    plt.close(fig)
    return paths


def _read(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    points = pd.read_csv(processed_dir / "points.csv").sort_values("config_id")
    pairs = pd.read_csv(processed_dir / "kleidiai.csv").sort_values("pair_id")
    return points.reset_index(drop=True), pairs.reset_index(drop=True)


def _decade_floor(v: float) -> float:
    return 10 ** math.floor(math.log10(v))


def _decade_ceil(v: float) -> float:
    return 10 ** math.ceil(math.log10(v))


def _iqr_err(df: pd.DataFrame) -> np.ndarray:
    return np.vstack(
        [(df.measured_median - df.q1).clip(lower=0), (df.q3 - df.measured_median).clip(lower=0)]
    )


# --- (a) headline: predicted vs measured ----------------------------------------------------


def fig_predicted_vs_measured(points: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.2, 7.6))
    lo = _decade_floor(min(points.predicted_tps.min(), points.q1.min()))
    hi = _decade_ceil(max(points.predicted_tps.max(), points.q3.max()))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")

    # y = x (the roofline) and the ratio guides.
    for ratio, label in ((1.0, "1"), (0.5, "0.5"), (0.25, "0.25"), (0.1, "0.1")):
        ax.plot(
            [lo, hi],
            [lo * ratio, hi * ratio],
            color=INK if ratio == 1 else MUTED,
            lw=1.0 if ratio == 1 else 0.8,
            ls="-" if ratio == 1 else "--",
            zorder=1,
        )
        ax.text(  # just outside the right edge, where the line leaves the plot
            hi * 1.03,
            hi * ratio,
            f"ratio {label}",
            fontsize=7.5,
            color=INK2,
            ha="left",
            va="center",
            clip_on=False,
        )

    for (phase, quant, build), g in points.groupby(["phase", "quant", "build"]):
        colour = PHASE_COLOUR[phase]
        ax.errorbar(
            g.predicted_tps,
            g.measured_median,
            yerr=_iqr_err(g),
            fmt=QUANT_MARKER[quant],
            ms=6,
            mfc=colour if build == "kleidiai" else "none",
            mec=colour,
            mew=1.2,
            ecolor=colour,
            elinewidth=0.8,
            ls="none",
            zorder=3,
        )
    ax.set_xlabel("predicted tokens/s (v1 roofline, frozen before the sweep)")
    ax.set_ylabel("measured tokens/s (median of 5; bars = IQR)")
    ax.grid(True, which="major")

    # Data sit under the diagonal (ratio < 1), so the upper left is free for the legends.
    phase_h = [
        Line2D([], [], marker="s", ls="none", ms=7, color=c, label=p)
        for p, c in PHASE_COLOUR.items()
    ]
    quant_h = [
        Line2D([], [], marker=QUANT_MARKER[q], ls="none", ms=6, mfc="none", mec=INK2, label=q)
        for q in QUANTS
    ]
    build_h = [
        Line2D([], [], marker="o", ls="none", ms=6, mfc=INK2, mec=INK2, label="kleidiai (filled)"),
        Line2D(
            [], [], marker="o", ls="none", ms=6, mfc="none", mec=INK2, label="baseline (hollow)"
        ),
    ]
    legends = ((phase_h, "phase", 0.0), (quant_h, "format", 0.2), (build_h, "build", 0.4))
    for i, (handles, title, x) in enumerate(legends):
        leg = ax.legend(handles=handles, loc="upper left", title=title, bbox_to_anchor=(x, 1.0))
        leg.get_title().set_color(INK2)
        if i < len(legends) - 1:
            ax.add_artist(leg)  # ax.legend() keeps only the last one; the others are artists
    _plain_log(ax, "x", (2, 5))
    _plain_log(ax, "y", (2, 5))
    n = len(points)
    _title(
        fig,
        "Predicted vs measured tokens/s",
        f"Qwen3 0.6B on Google Axion (Neoverse V2), llama.cpp, {n} points; prefill and decode kept apart",
    )
    fig.subplots_adjust(left=0.11, right=0.9, top=0.9, bottom=0.08)
    return fig


# --- (b) KleidiAI speed-up -------------------------------------------------------------------


def fig_kleidiai_speedup(pairs: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.6), sharey=True)
    ymin = min(0.9, math.floor(pairs.speedup_lo.min() * 20) / 20)
    ymax = max(1.1, math.ceil(pairs.speedup_hi.max() * 20) / 20)
    width = 0.2
    for r, (phase, tests) in enumerate((("prefill", PREFILL_TESTS), ("decode", DECODE_TESTS))):
        for c, quant in enumerate(QUANTS):
            ax = axes[r, c]
            ax.axhline(1.0, color=INK, lw=1.0, zorder=1)
            for j, test in enumerate(tests):
                g = pairs[(pairs.quant == quant) & (pairs.test == test)].sort_values("threads")
                if g.empty:
                    continue
                x = (
                    np.array([THREADS.index(t) for t in g.threads])
                    + (j - (len(tests) - 1) / 2) * width
                )
                err = np.vstack(
                    [
                        (g.speedup - g.speedup_lo).clip(lower=0),
                        (g.speedup_hi - g.speedup).clip(lower=0),
                    ]
                )
                ax.errorbar(
                    x,
                    g.speedup,
                    yerr=err,
                    fmt=TEST_MARKER[test],
                    ms=5.5,
                    color=TEST_COLOUR[test],
                    ecolor=TEST_COLOUR[test],
                    elinewidth=1.2,
                    capsize=2.5,
                    ls="none",
                    zorder=3,
                )
            ax.set_xticks(range(len(THREADS)), [str(t) for t in THREADS])
            ax.set_xlim(-0.6, len(THREADS) - 0.4)
            ax.set_ylim(ymin, ymax)
            ax.set_title(COVERAGE_TITLE[quant] if r == 0 else "", fontsize=9, loc="left")
            if r == 1:
                ax.set_xlabel("threads")
            if c == 0:
                ax.set_ylabel(f"{phase}: kleidiai ÷ baseline")
            if quant == "F16":
                ax.text(
                    0.5, 0.04, "expected ≈ 1.0", transform=ax.transAxes, ha="center",
                    fontsize=7.5, color=INK2,
                )  # fmt: skip
    handles = [
        Line2D(
            [],
            [],
            marker=TEST_MARKER[t],
            ls="none",
            ms=6,
            color=TEST_COLOUR[t],
            label=TEST_LABEL[t],
        )
        for t in PREFILL_TESTS + DECODE_TESTS
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.0))
    _title(
        fig,
        "KleidiAI speed-up over ggml's own Arm kernels",
        "Qwen3 0.6B, Axion. Dot = ratio of medians; bar = conservative range "
        "(kleidiai Q1 ÷ baseline Q3 to kleidiai Q3 ÷ baseline Q1). Line at 1.0 = no change.",
    )
    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.14, wspace=0.08, hspace=0.18)
    return fig


# --- (c) thread scaling ----------------------------------------------------------------------


def fig_thread_scaling(points: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6))
    for ax, test, name in (
        (axes[0], "tg128", "Decode (tg128)"),
        (axes[1], "pp512", "Prefill (pp512)"),
    ):
        sub = points[points.test == test]
        for quant in QUANTS:
            for build in ("baseline", "kleidiai"):
                g = sub[(sub.quant == quant) & (sub.build == build)].sort_values("threads")
                kl = build == "kleidiai"
                ax.errorbar(
                    g.threads,
                    g.measured_median,
                    yerr=_iqr_err(g),
                    marker=QUANT_MARKER[quant],
                    ms=6,
                    mfc=QUANT_COLOUR[quant] if kl else "none",
                    mec=QUANT_COLOUR[quant],
                    mew=1.2,
                    color=QUANT_COLOUR[quant],
                    lw=1.4 if kl else 0.9,
                    elinewidth=0.8,
                    zorder=3,
                )
            # v1 prediction: the same for both builds (ADR-016), so one dashed line per format.
            p = sub[(sub.quant == quant) & (sub.build == "kleidiai")].sort_values("threads")
            ax.plot(
                p.threads, p.predicted_tps, color=QUANT_COLOUR[quant], lw=1.0, ls=(0, (4, 3)),
                alpha=0.75, zorder=2,
            )  # fmt: skip
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(THREADS, [str(t) for t in THREADS])
        ax.xaxis.set_minor_formatter(NullFormatter())
        _plain_log(ax, "y", (2, 3, 5))
        ax.set_xlabel("threads")
        ax.set_ylabel("tokens/s")
        ax.set_title(name, loc="left")
    handles = [
        Line2D([], [], marker=QUANT_MARKER[q], color=QUANT_COLOUR[q], lw=1.2, ms=6, label=q)
        for q in QUANTS
    ] + [
        Line2D([], [], marker="o", color=INK2, mfc=INK2, lw=1.4, ms=6, label="kleidiai (filled)"),
        Line2D([], [], marker="o", color=INK2, mfc="none", lw=0.9, ms=6, label="baseline (hollow)"),
        Line2D([], [], color=INK2, lw=1.0, ls=(0, (4, 3)), label="v1 prediction (both builds)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=7, bbox_to_anchor=(0.5, 0.0))
    _title(
        fig,
        "Thread scaling: measured vs v1 prediction",
        "Qwen3 0.6B, Axion. Bars = IQR. Prefill predictions for Q8_0, Q4_0 and Q4_K_M coincide "
        "(same compute ceiling).",
    )
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.17, wspace=0.16)
    return fig


# --- (d) classic roofline --------------------------------------------------------------------


def fig_roofline(points: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.0), sharey=True)
    x_lo = _decade_floor(points.arith_intensity.min()) / 2
    x_hi = _decade_ceil(points.arith_intensity.max()) * 3
    y_lo = _decade_floor(points.achieved_GOPS.min()) / 2
    y_hi = _decade_ceil(points.C_weight.max() / 1e9)
    for ax, t in zip(axes, (1, 8)):
        sub = points[points.threads == t]
        b = sub.B.iloc[0] / 1e9  # GB/s = GOPS per (op/byte)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        peaks = sub.groupby("C_weight_class").C_weight.first() / 1e9
        sustained = sub.groupby("C_weight_class_sustained").C_weight_sustained.first() / 1e9
        top = peaks.max()
        ax.plot([x_lo, top / b], [x_lo * b, top], color=INK, lw=1.2, zorder=1)
        ax.text(
            top / b / 1.2, top * 1.25, f"memory: {b:.0f} GB/s", fontsize=8, color=INK2,
            ha="right", va="bottom",
        )  # fmt: skip
        for cls, c in peaks.items():
            ax.plot([c / b, x_hi], [c, c], color=INK, lw=1.2, zorder=1)
            ax.text(
                x_hi / 1.15, c * 1.07, f"{CLASS_LABEL[cls]} peak {c:.0f}", fontsize=7.5,
                color=INK2, ha="right", va="bottom", bbox=_LABEL_BOX,
            )  # fmt: skip
        for cls, c in sustained.items():
            if abs(c - peaks.get(cls, np.nan)) / c < 0.05:
                continue  # sustained = peak (no throttling at this t): draw it once
            ax.plot([c / b, x_hi], [c, c], color=MUTED, lw=1.0, ls=":", zorder=1)
            ax.text(  # left end of the dotted line, so it never meets a peak label at the right
                max(c / b * 1.15, 4.5), c * 0.93, f"{CLASS_LABEL[cls]} sustained {c:.0f}", fontsize=7.5,
                color=INK2, ha="left", va="top", bbox=_LABEL_BOX,
            )  # fmt: skip
        for (phase, quant, build), g in sub.groupby(["phase", "quant", "build"]):
            colour = PHASE_COLOUR[phase]
            ax.plot(
                g.arith_intensity, g.achieved_GOPS, QUANT_MARKER[quant], ms=6,
                mfc=colour if build == "kleidiai" else "none", mec=colour, mew=1.2, ls="none",
                zorder=3,
            )  # fmt: skip
        _plain_log(ax, "x")
        _plain_log(ax, "y", (2, 5))
        ax.set_xlabel("arithmetic intensity (operations per byte read)")
        ax.set_title(f"{t} thread" + ("s" if t > 1 else ""), loc="left")
    axes[0].set_ylabel("achieved GOPS (weight + attention operations)")
    handles = (
        [
            Line2D([], [], marker="s", ls="none", ms=7, color=c, label=p)
            for p, c in PHASE_COLOUR.items()
        ]
        + [
            Line2D([], [], marker=QUANT_MARKER[q], ls="none", ms=6, mfc="none", mec=INK2, label=q)
            for q in QUANTS
        ]
        + [
            Line2D(
                [], [], marker="o", ls="none", ms=6, mfc=INK2, mec=INK2, label="kleidiai (filled)"
            ),
            Line2D(
                [], [], marker="o", ls="none", ms=6, mfc="none", mec=INK2, label="baseline (hollow)"
            ),
        ]
    )
    fig.legend(handles=handles, loc="lower center", ncol=8, bbox_to_anchor=(0.5, 0.0))
    _title(
        fig,
        "Roofline: where each configuration sits",
        "Qwen3 0.6B, Axion. Solid = measured ceilings B(t) and peak C(t); dotted = sustained C(t) "
        "(shown where throttling lowers it). Ceilings are the weight-format peaks.",
    )
    fig.subplots_adjust(left=0.07, right=0.99, top=0.85, bottom=0.17, wspace=0.05)
    return fig


# --- (e) ratio breakdown ---------------------------------------------------------------------


def fig_ratio_breakdown(points: pd.DataFrame) -> plt.Figure:
    rows = [(q, b) for q in QUANTS for b in ("baseline", "kleidiai")]
    groups = {"prefill": PREFILL_TESTS, "decode": DECODE_TESTS}
    # Only the (test, threads) cells that were measured: decode after 2048 tokens ran at 1 and 8.
    cols = {
        ph: [
            (test, t)
            for test in tests
            for t in THREADS
            if ((points.test == test) & (points.threads == t)).any()
        ]
        for ph, tests in groups.items()
    }
    vmax = 0.7
    fig = plt.figure(figsize=(14.5, 5.4))
    gs = fig.add_gridspec(
        1, 3, width_ratios=[len(cols["prefill"]), len(cols["decode"]), 0.5], wspace=0.04,
        left=0.1, right=0.97, top=0.85, bottom=0.17,
    )  # fmt: skip
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    cax = fig.add_subplot(gs[0, 2])
    lookup = points.set_index(["quant", "build", "test", "threads"]).ratio
    image = None
    for ax, phase in zip(axes, ("prefill", "decode")):
        grid = np.full((len(rows), len(cols[phase])), np.nan)
        for i, (q, b) in enumerate(rows):
            for j, (test, t) in enumerate(cols[phase]):
                if (q, b, test, t) in lookup.index:
                    grid[i, j] = lookup[(q, b, test, t)]
        image = ax.imshow(
            np.ma.masked_invalid(grid), cmap=RATIO_CMAP, vmin=0, vmax=vmax, aspect="auto",
            interpolation="nearest",
        )  # fmt: skip
        ax.grid(False)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                v = grid[i, j]
                if np.isnan(v):
                    continue
                ax.text(
                    j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                    color="#ffffff" if v / vmax > 0.55 else INK,
                )  # fmt: skip
        # Surface-coloured gaps between cells, wider ones between tests and between formats.
        ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
        ax.grid(which="minor", color=SURFACE, lw=1.5)
        ax.tick_params(which="minor", length=0)
        edge = -0.5
        for test in groups[phase]:
            n = sum(1 for tt, _ in cols[phase] if tt == test)
            ax.axvline(edge, color=SURFACE, lw=5)
            ax.text(
                edge + n / 2, -0.085, test, ha="center", va="top", fontsize=9, color=INK,
                fontweight="bold", transform=ax.get_xaxis_transform(),
            )  # fmt: skip
            edge += n
        for k in range(1, len(QUANTS)):
            ax.axhline(2 * k - 0.5, color=SURFACE, lw=4)
        ax.set_xticks(range(grid.shape[1]), [str(t) for _, t in cols[phase]])
        if phase == "prefill":
            ax.set_yticks(range(len(rows)), [f"{q} {b}" for q, b in rows])
        else:
            ax.set_yticks([])
        ax.set_xlabel("threads (grouped by test)", labelpad=22)
        ax.set_title(phase.capitalize(), loc="left")
        for spine in ax.spines.values():
            spine.set_visible(False)
    cbar = fig.colorbar(image, cax=cax)
    cbar.set_label("measured ÷ predicted (v1)", color=INK2, fontsize=8.5)
    cbar.ax.tick_params(labelsize=8, colors=MUTED)
    cbar.outline.set_visible(False)
    _title(
        fig,
        "Measured ÷ predicted, by phase, format, build and thread count",
        "Qwen3 0.6B, Axion. Colour scale 0 to 0.7 for both phases. "
        "Decode after a 2048-token context (tg128d2048) was measured at 1 and 8 threads only.",
    )
    return fig


# --- (f) RQ4: the int8 dot-product microbenchmark ---------------------------------------------

MICRO_FAMILIES = ["scalar", "autovec", "sdot", "smmla", "sve"]
MICRO_LABEL = {
    "scalar": "scalar\n(no auto-vec)",
    "autovec": "auto-\nvectorised",
    "sdot": "NEON\nSDOT",
    "smmla": "i8mm\nSMMLA",
    "sve": "SVE\nSDOT",
}
# Same pairing as the phases: in-cache work is compute-bound like prefill (blue), work streamed from
# DRAM is bandwidth-bound like decode (orange).
SET_COLOUR = {"L1": PHASE_COLOUR["prefill"], "DRAM": PHASE_COLOUR["decode"]}


def fig_dot_int8(micro: pd.DataFrame) -> plt.Figure:
    best = micro[micro.is_best.astype(bool) & micro.disasm_ok.astype(bool)]
    first = micro.iloc[0]
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.8), sharey=True)
    # Ceilings in GMAC/s: a peak of C ops/s is C/2 MAC/s; B bytes/s at 1 (or 2, SMMLA) MACs per
    # weight byte is B (or 2B) MAC/s. All four come from the CSV (they are the references in the raw
    # record), so this figure reads nothing else.
    lines = {
        "L1": [
            (first.ref_C_sdot_GMACs, f"SDOT peak C(1) = {first.ref_C_sdot_GMACs:.0f} GMAC/s"),
            (first.ref_C_smmla_GMACs, f"SMMLA peak C(1) = {first.ref_C_smmla_GMACs:.0f} GMAC/s"),
        ],
        "DRAM": [
            (first.ref_B_GBps, f"B(1) at 1 MAC per weight byte = {first.ref_B_GBps:.0f} GMAC/s"),
            (2 * first.ref_B_GBps, f"B(1) at 2 MACs per byte (SMMLA) = {2 * first.ref_B_GBps:.0f}"),
        ],
    }
    lo = _decade_floor(best.gmacs_lo.min()) / 2
    hi = _decade_ceil(max(best.gmacs_hi.max(), *(v for ls in lines.values() for v, _ in ls)))
    for ax, ws in zip(axes, ("L1", "DRAM")):
        colour = SET_COLOUR[ws]
        sub = best[best.working_set == ws].set_index("family")
        for value, label in lines[ws]:
            ax.axhline(value, color=INK, lw=1.0, zorder=1)
            ax.text(
                -0.45, value * 1.04, label, fontsize=7.5, color=INK2, ha="left", va="bottom",
                bbox=_LABEL_BOX,
            )  # fmt: skip
        for i, fam in enumerate(MICRO_FAMILIES):
            if fam not in sub.index:
                continue
            r = sub.loc[fam]
            ax.errorbar(
                i, r.gmacs, yerr=[[r.gmacs - r.gmacs_lo], [r.gmacs_hi - r.gmacs]], fmt="o", ms=7,
                color=colour, ecolor=colour, elinewidth=1.2, capsize=3, zorder=3,
            )  # fmt: skip
            ax.text(
                i + 0.1, r.gmacs, f"{r.gmacs:.3g}", fontsize=8, color=INK, ha="left", va="center"
            )
            if r.macs_per_weight_byte != 1:  # SMMLA: also show the rate per weight byte
                per_byte = r.gmacs / r.macs_per_weight_byte
                ax.plot([i, i], [per_byte, r.gmacs], color=colour, lw=0.8, ls=":", zorder=2)
                ax.plot(i, per_byte, "o", ms=7, mfc="none", mec=colour, mew=1.2, zorder=3)
                ax.text(
                    i, per_byte * 0.92, f"per weight byte: {per_byte:.3g}", fontsize=7.5,
                    color=INK2, ha="center", va="top",
                )  # fmt: skip
        ax.set_yscale("log")
        ax.set_ylim(lo, hi)
        ax.set_xlim(-0.5, len(MICRO_FAMILIES) - 0.4)
        ax.set_xticks(range(len(MICRO_FAMILIES)), [MICRO_LABEL[f] for f in MICRO_FAMILIES])
        _plain_log(ax, "y", (2, 5))
        weight = int(micro[micro.working_set == ws].weight_bytes.iloc[0])
        size = f"{weight / 2**30:g} GiB" if weight >= 2**30 else f"{weight / 1024:g} KiB"
        ax.set_title(
            f"{ws}: weights {size}" + (" (in cache)" if ws == "L1" else " (streamed from memory)"),
            loc="left",
        )
    axes[0].set_ylabel("GMAC/s (int8 multiply-accumulates per ns, median; bar = IQR)")
    _title(
        fig,
        "Int8 dot product, one core: what the instruction buys in cache and out of it",
        "Decode-shaped matrix-vector product, K = 4096, best of 4 and 8 accumulators. SMMLA does 2 "
        "MACs per weight byte; the hollow dot is its rate per weight byte.",
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.12, wspace=0.05)
    return fig


FIGURES = {
    "predicted_vs_measured": ("points", fig_predicted_vs_measured),
    "kleidiai_speedup": ("pairs", fig_kleidiai_speedup),
    "thread_scaling": ("points", fig_thread_scaling),
    "roofline": ("points", fig_roofline),
    "ratio_breakdown": ("points", fig_ratio_breakdown),
}
# Drawn only when its table exists: micro.csv appears once `make micro` has run on the VM (Day 7).
OPTIONAL_FIGURES = {"dot_int8": ("micro.csv", fig_dot_int8)}


def make_all(processed_dir: Path, out_dir: Path) -> list[Path]:
    """Draw every figure from the processed CSVs; returns the files written (sorted by name)."""
    _style()
    points, pairs = _read(processed_dir)
    data = {"points": points, "pairs": pairs}
    written: list[Path] = []
    for name, (source, draw) in FIGURES.items():
        written += _save(draw(data[source]), out_dir, name)
    for name, (csv_name, draw) in OPTIONAL_FIGURES.items():
        if (processed_dir / csv_name).exists():
            written += _save(draw(pd.read_csv(processed_dir / csv_name)), out_dir, name)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--processed-dir", type=Path, default=REPO_ROOT / PROCESSED_DIR)
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / FIGURES_DIR)
    args = parser.parse_args()
    for path in make_all(args.processed_dir, args.out_dir):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
