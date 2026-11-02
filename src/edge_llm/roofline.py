"""v1 roofline predictions: bytes and FLOPs per token, predicted tokens/s (CLAUDE.md §8).

    python -m edge_llm.roofline        (make predict)

For every point of the full sweep (configs/sweep.yaml) the time is bounded by two things, and the
slower one wins:

    t_memory  = bytes / B(t)                       B(t): measured read bandwidth
    t_compute = weight FLOPs / C_weight(t) + attention FLOPs / C_fma32(t)

    decode,  per token:   predicted_tps = 1 / max(t_memory, t_compute)
    prefill, P tokens:    predicted_tps = P / max(t_memory, t_compute)

Inputs are files only: the sweep definition, the model tensor tables, one bandwidth record and one
peak record. This module never opens results/raw/bench/, so a prediction cannot see a measured
speed (ARCHITECTURE.md rule 3; a test checks it). One multiply-accumulate counts as 2 operations
everywhere. Bytes are the model file's, for both builds (ADR-016), so a point's two builds get the
same prediction.

`C(t)` is the *unthrottled* ceiling (ADR-023): t x the per-core rate (90th percentile of the
t = 1 repetitions, best chain count) x operations per instruction. The *sustained* ceiling (mean
of the repetitions at t, best chain count) gives a second, lower prediction, `*_sustained`, for
information only: it is not v1's prediction.

Formulas and sources: CLAUDE.md §8, ADR-015 (which F16 instruction in which phase), ADR-016,
ADR-017 and ADR-021 (B(t)), ADR-018 (decode depth), ADR-019 (flash attention on), ADR-020 (the
FLOP counts), ADR-022 and ADR-023 (C(t)), ADR-024 (small model only).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from edge_llm import bandwidth, peak, sweep
from edge_llm.schema import BandwidthRecord, ModelTable, PeakRecord

REPO_ROOT = Path(__file__).resolve().parents[2]

# The measured inputs of v1 (CLAUDE.md §11: B(t) and C(t) for v1).
BANDWIDTH_RECORD = Path("results/raw/bandwidth/2026-11-02T2141Z_start.json")
PEAK_RECORD = Path("results/raw/peak/2026-11-02T2141Z.json")

ATTENTION_TILE = 64  # flash attention works in 64 x 64 tiles (ADR-020)
KV_ELEMENT_BYTES = {"f16": 2}  # the KV-cache types the formulas know
ADRS = [
    "ADR-004", "ADR-015", "ADR-016", "ADR-017", "ADR-018", "ADR-019", "ADR-020", "ADR-021",
    "ADR-022", "ADR-023", "ADR-024",
]  # fmt: skip
FORMULAS = {
    "decode": "tps = 1 / max((W_blk + W_out + KV(c)) / B(t), "
    "2(N_blk + N_out) / C_dec(t) + 4 L H d c / C_fma32(t)); c = depth + (n_gen - 1) / 2",
    "prefill": "tps = P / max((ceil(P / n_ubatch) W_blk + W_out) / B(t), "
    "F_w / C_pre(t) + F_a / C_fma32(t)); F_w = 2 N_blk P - 2 N_ffn_last (P - 1) + 2 N_out; "
    "F_a = 2 L H d P (P + 64)",
    "classes": "C_dec = sdot (quantised) or fmlal (F16); "
    "C_pre = max(sdot, smmla) (quantised) or fmla_f16 (F16)",
}


# --- the formulas (CLAUDE.md §8) ----------------------------------------------------------


def decode_context(depth: int, n_gen: int) -> float:
    """Average context length while generating `n_gen` tokens after `depth` tokens."""
    return depth + (n_gen - 1) / 2


def kv_bytes(
    context: float, n_layers: int, n_kv_heads: int, head_dim: int, elem_bytes: int
) -> float:
    """Bytes of K and V read for one new token at this context length."""
    return context * n_layers * 2 * n_kv_heads * head_dim * elem_bytes


def decode_weight_flops(n_blk: int, n_out: int) -> int:
    return 2 * (n_blk + n_out)


def decode_attention_flops(n_layers: int, n_heads: int, head_dim: int, context: float) -> float:
    return 4 * n_layers * n_heads * head_dim * context


def prefill_weight_flops(n_blk: int, n_out: int, n_ffn_last: int, p: int, n_logits: int = 1) -> int:
    """Weights applied to P prompt tokens. The last layer's FFN only runs for the output rows."""
    return 2 * n_blk * p - 2 * n_ffn_last * (p - n_logits) + 2 * n_out * n_logits


def prefill_attention_flops(n_layers: int, n_heads: int, head_dim: int, p: int) -> int:
    """Causal attention in 64 x 64 tiles: P (P + 64) / 2 query-key pairs, 4 FLOPs each."""
    return 2 * n_layers * n_heads * head_dim * p * (p + ATTENTION_TILE)


def prefill_bytes(w_blk: int, w_out: int, p: int, n_ubatch: int) -> int:
    """The block weights are read once per chunk of n_ubatch tokens; the output layer once."""
    return math.ceil(p / n_ubatch) * w_blk + w_out


def weight_ceiling(ceilings: dict[str, dict[int, float]], quant: str, phase: str, t: int):
    """(instruction class, ops/s) that bounds the weight matmuls of a format and phase at t."""
    if quant == "F16":
        cls = "fmlal" if phase == "decode" else "fmla_f16"
    elif phase == "decode":
        cls = "sdot"
    else:
        cls = max(("sdot", "smmla"), key=lambda c: ceilings[c][t])
    return cls, ceilings[cls][t]


def binding_limit(t_memory: float, t_compute: float) -> str:
    return "compute" if t_compute > t_memory else "memory"


# --- inputs ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class Model:
    """What the formulas need from a model file's tensor table (results/models/)."""

    w_blk: int
    n_blk: int
    w_out: int
    n_out: int
    n_layers: int
    n_heads: int
    n_kv_heads: int
    head_dim: int
    n_embd: int
    n_ff: int

    @property
    def n_ffn_last(self) -> int:
        """Gate, up and down matrices of one layer."""
        return 3 * self.n_embd * self.n_ff


def load_model(path: Path) -> Model:
    table = ModelTable.from_dict(json.loads(path.read_text()))
    tot = table.totals
    return Model(
        w_blk=tot["W_blk"], n_blk=tot["N_blk"], w_out=tot["W_out"], n_out=tot["N_out"],
        n_layers=table.n_layers, n_heads=table.n_heads, n_kv_heads=table.n_kv_heads,
        head_dim=table.head_dim, n_embd=table.n_embd, n_ff=table.n_ff,
    )  # fmt: skip


def percentile90(samples: list[float]) -> float:
    """90th percentile, linear interpolation (numpy's default, as in stats.py)."""
    return statistics.quantiles(samples, n=10, method="inclusive")[8]


@dataclass(frozen=True)
class Hardware:
    b: dict[int, float]  # bytes/s: best valid read variant at t threads (ADR-021)
    b1: dict[int, float | None]  # bytes/s: best valid one-stream result (reference only)
    c: dict[str, dict[int, float]]  # ops/s per class: t x p90 per-core rate x ops (ADR-023)
    c_sustained: dict[str, dict[int, float]]  # ops/s per class: mean of the repetitions at t
    details: dict  # what won, for v1.meta.json


def hardware_from_records(bw: BandwidthRecord, pk: PeakRecord) -> Hardware:
    """B(t) from the bandwidth record and C(t) from the peak record, by the rules of §8."""
    at = bandwidth.b_of_record(bw)

    # Only loops whose disassembly check passed count (ADR-022).
    valid = peak.valid_chain_counts(pk.disasm)
    points = [p for p in pk.points if p.accumulators in valid[p.instr_class]]
    threads = sorted({p.threads for p in points})
    c: dict[str, dict[int, float]] = {}
    sustained: dict[str, dict[int, float]] = {}
    peak_details: dict[str, dict] = {}
    for cls in peak.PEAK_CLASSES:
        ops = peak.ops_per_instruction(cls, pk.sve_vector_bits)
        one = [p for p in points if p.instr_class == cls and p.threads == 1]
        best = max(one, key=lambda p: percentile90(p.samples_instr_per_s))
        rate = percentile90(best.samples_instr_per_s)  # instructions/s of one core, unthrottled
        c[cls], sustained[cls], won = {}, {}, {}
        for t in threads:
            here = [p for p in points if p.instr_class == cls and p.threads == t]
            top = max(here, key=lambda p: statistics.fmean(p.samples_ops_per_s))
            c[cls][t] = t * rate * ops
            sustained[cls][t] = statistics.fmean(top.samples_ops_per_s)
            won[str(t)] = top.accumulators
        peak_details[cls] = {
            "ops_per_instruction": ops,
            "p90_instr_per_s_per_core": rate,
            "chains_at_p90": best.accumulators,
            "chains_at_sustained_mean_by_t": won,
        }
    details = {
        "bandwidth": {
            str(t): {
                "B": v.b,
                "accumulators": v.accumulators,
                "streams": v.streams,
                "B1": v.b1,
                "B1_accumulators": v.b1_accumulators,
            }
            for t, v in at.items()
        },
        "peak": peak_details,
        "sve_vector_bits": pk.sve_vector_bits,
    }
    return Hardware(
        b={t: v.b for t, v in at.items()},
        b1={t: v.b1 for t, v in at.items()},
        c=c,
        c_sustained=sustained,
        details=details,
    )


def load_hardware(root: Path = REPO_ROOT) -> Hardware:
    bw = BandwidthRecord.from_dict(json.loads((root / BANDWIDTH_RECORD).read_text()))
    pk = PeakRecord.from_dict(json.loads((root / PEAK_RECORD).read_text()))
    return hardware_from_records(bw, pk)


# --- one point ------------------------------------------------------------------------------


def predict_point(point: sweep.Point, m: Model, hw: Hardware, settings: dict) -> dict:
    """The prediction row of one point (a flat dict: one line of v1.csv)."""
    te, t = sweep.parse_test(point.test), point.threads
    if settings["flash_attn"] != 1:
        raise ValueError("the attention FLOP count assumes flash attention (ADR-019, ADR-020)")
    if te.kind == "tg":
        # llama-bench's tg test: the context grows from `depth`; use its average (ADR-020).
        ctx = decode_context(te.depth, te.tokens)
        if settings["type_k"] != settings["type_v"]:
            raise ValueError("K and V cache types differ: the KV formula assumes one size")
        elem = KV_ELEMENT_BYTES[settings["type_k"]]
        nbytes = m.w_blk + m.w_out + kv_bytes(ctx, m.n_layers, m.n_kv_heads, m.head_dim, elem)
        w_flops = decode_weight_flops(m.n_blk, m.n_out)
        a_flops = decode_attention_flops(m.n_layers, m.n_heads, m.head_dim, ctx)
        tokens = 1  # time per generated token
    else:
        if te.tokens > settings["n_batch"]:
            raise ValueError("the prefill formulas assume the prompt is one batch (P <= n_batch)")
        ctx = None
        nbytes = prefill_bytes(m.w_blk, m.w_out, te.tokens, settings["n_ubatch"])
        w_flops = prefill_weight_flops(m.n_blk, m.n_out, m.n_ffn_last, te.tokens)
        a_flops = prefill_attention_flops(m.n_layers, m.n_heads, m.head_dim, te.tokens)
        tokens = te.tokens

    t_memory = nbytes / hw.b[t]
    row = {
        "config_id": point.config_id,
        "pair_id": point.pair_id,
        "model": point.model,
        "quant": point.quant,
        "build": point.build,
        "threads": t,
        "test": point.test,
        "phase": te.phase,
        "prompt_tokens": te.tokens if te.kind == "pp" else 0,
        "gen_tokens": te.tokens if te.kind == "tg" else 0,
        "depth": te.depth,
        "avg_context": ctx,
        "bytes": nbytes,
        "weight_flops": w_flops,
        "attention_flops": a_flops,
        "B": hw.b[t],
        "B1": hw.b1[t],
        "C_attn": hw.c["fma32"][t],
        "t_memory": t_memory,
    }
    for suffix, ceilings in (("", hw.c), ("_sustained", hw.c_sustained)):
        cls, c_weight = weight_ceiling(ceilings, point.quant, te.phase, t)
        t_compute = w_flops / c_weight + a_flops / ceilings["fma32"][t]
        row[f"C_weight_class{suffix}"] = cls
        row[f"C_weight{suffix}"] = c_weight
        if suffix:
            row[f"C_attn{suffix}"] = ceilings["fma32"][t]
        row[f"t_compute{suffix}"] = t_compute
        row[f"predicted_tps{suffix}"] = tokens / max(t_memory, t_compute)
        row[f"binding{suffix}"] = binding_limit(t_memory, t_compute)
    return row


COLUMNS = [
    "config_id", "pair_id", "model", "quant", "build", "threads", "test", "phase",
    "prompt_tokens", "gen_tokens", "depth", "avg_context",
    "bytes", "weight_flops", "attention_flops",
    "B", "B1", "C_weight_class", "C_weight", "C_attn",
    "t_memory", "t_compute", "predicted_tps", "binding",
    "C_weight_class_sustained", "C_weight_sustained", "C_attn_sustained",
    "t_compute_sustained", "predicted_tps_sustained", "binding_sustained",
]  # fmt: skip


def predict_all(cfg: dict, models: dict[tuple[str, str], Model], hw: Hardware) -> list[dict]:
    """One row per point of the full sweep (both builds of every pair)."""
    return [
        predict_point(point, models[(point.model, point.quant)], hw, cfg["bench_settings"])
        for pair in sweep.pairs(cfg, "full")
        for point in pair.points()
    ]


# --- files ----------------------------------------------------------------------------------


def sha256(path: Path) -> str:
    """SHA256 of a text file with CRLF read as LF, the way git stores it (.gitattributes: eol=lf),
    so a Windows checkout and the VM's agree."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def git_head(root: Path) -> dict:
    def run(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=root, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    status = run("status", "--porcelain")
    return {"commit": run("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def model_paths(cfg: dict, root: Path) -> dict[tuple[str, str], Path]:
    return {
        (m, q): root / "results" / "models" / f"{m}_{q}.json"
        for m in cfg["full"]["models"]
        for q in cfg["quants"]
    }


def write_predictions(rows: list[dict], meta: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "v1.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "v1.meta.json").write_text(json.dumps(meta, indent=2) + "\n")


def run(root: Path = REPO_ROOT, out_dir: Path | None = None) -> list[dict]:
    """Read the inputs, predict every point of the full sweep, write v1.csv and v1.meta.json."""
    cfg_path = root / "configs" / "sweep.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    paths = model_paths(cfg, root)
    models = {key: load_model(p) for key, p in paths.items()}
    hw = load_hardware(root)
    rows = predict_all(cfg, models, hw)

    inputs = [cfg_path, root / BANDWIDTH_RECORD, root / PEAK_RECORD, *paths.values()]
    meta = {
        "version": "v1",
        "rows": len(rows),
        "repo_head_when_generated": git_head(root),
        "note": "the predictions are committed together with the code that made them, so the "
        "commit that adds this file is the one that follows the head above",
        "inputs_sha256": {p.relative_to(root).as_posix(): sha256(p) for p in inputs},
        "inputs_sha256_note": "SHA256 of the file as git stores it (line endings LF)",
        "bandwidth_record": BANDWIDTH_RECORD.as_posix(),
        "peak_record": PEAK_RECORD.as_posix(),
        "bench_settings": cfg["bench_settings"],
        "adrs": ADRS,
        "formulas": FORMULAS,
        "hardware": hw.details,
    }
    write_predictions(rows, meta, out_dir or root / "results" / "predictions")
    return rows


def summary_lines(rows: list[dict]) -> list[str]:
    lines = [f"{len(rows)} rows"]
    for quant in ("Q4_0", "F16"):
        for t in (1, 8):
            for test in ("pp512", "tg128"):
                r = next(
                    r
                    for r in rows
                    if (r["quant"], r["threads"], r["test"], r["build"])
                    == (quant, t, test, "baseline")
                )
                lines.append(
                    f"small_{quant} t={t} {test}: {r['predicted_tps']:.1f} tok/s ({r['binding']}-bound;"
                    f" sustained C: {r['predicted_tps_sustained']:.1f}, {r['binding_sustained']})"
                )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", type=Path, help="default: results/predictions")
    args = parser.parse_args()
    rows = run(out_dir=args.out_dir)
    print("\n".join(summary_lines(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
