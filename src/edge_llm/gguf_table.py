"""Per-tensor name / type / shape / bytes from a GGUF file (CLAUDE.md §8 inputs).

    python -m edge_llm.gguf_table            # every model in configs/sweep.yaml (make models)
    python -m edge_llm.gguf_table --gguf F.gguf --alias small --quant Q4_0 --sha256 <hex>

Writes results/models/<alias>_<quant>.json (schema: edge_llm.schema.ModelTable). Reads only
the GGUF header and tensor index, never the weights.

Roles (which roofline term a tensor feeds):

* ``blk``   - 2-D (or higher) tensors named ``blk.*``: the transformer-block weight matrices
              (attn q/k/v/output, ffn gate/up/down). These are W_blk / N_blk.
* ``out``   - the output projection: ``output.weight`` if the file has one, otherwise (tied
              embeddings) ``token_embd.weight``, because the output matmul reads that whole
              table every token. These are W_out / N_out.
* ``emb``   - ``token_embd.weight`` when embeddings are NOT tied. Decoding reads one row of
              it per token, so it does not enter the roofline.
* ``other`` - everything else: the 1-D norm vectors (``blk.*_norm.weight`` and
              ``output_norm.weight``) and ``rope_freqs.weight``. They are read once per token
              but are not matmul weights and total well under 1 % of the file, so spec §8
              counts them in neither W_blk nor W_out; their bytes are kept in W_other so the
              claim can be checked.

Head size is taken from ``<arch>.attention.key_length`` when the file has it, otherwise from
the attn_k shape, never from hidden size / heads (they differ for some Qwen3 sizes). Shapes
are in ggml order: shape[0] is the contiguous dimension, i.e. the matmul input width.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from importlib.metadata import version
from pathlib import Path

import gguf
from gguf import GGMLQuantizationType, GGUFReader

from edge_llm.schema import SCHEMA_VERSION, ModelTable, SchemaError

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIGNMENT = 32  # gguf default when general.alignment is absent


def assign_role(name: str, n_dims: int, tied: bool) -> str:
    """Role of a tensor; the rule is spelled out in the module docstring."""
    if name == "output.weight":
        return "out"
    if name == "token_embd.weight":
        return "out" if tied else "emb"
    if name.startswith("blk.") and n_dims >= 2:
        return "blk"
    return "other"


def _field(reader: GGUFReader, key: str):
    f = reader.fields.get(key)
    return None if f is None else f.contents()


def _expected_bytes(n_params: int, qtype: GGMLQuantizationType) -> int:
    """Bytes a tensor of this type and size occupies, from the ggml block definition."""
    block, type_size = gguf.GGML_QUANT_SIZES[qtype]
    if n_params % block:
        raise SchemaError(
            f"{n_params} elements is not a multiple of the {qtype.name} block {block}"
        )
    return n_params // block * type_size


def layout_check(reader: GGUFReader, file_bytes: int, alignment: int) -> dict:
    """Check that the file's own tensor offsets agree with the byte counts.

    The reader computes n_bytes from shape and type, so on its own that would be circular. The
    data offsets come from the file: each tensor must start where the previous one ends
    (plus alignment padding), and the last one must end inside the file.
    """
    tensors = sorted(reader.tensors, key=lambda t: t.data_offset)
    ok, problems = True, []
    for prev, nxt in itertools.pairwise(tensors):
        gap = int(nxt.data_offset) - int(prev.data_offset) - int(prev.n_bytes)
        if gap < 0 or gap >= alignment:
            ok = False
            problems.append(f"{prev.name} -> {nxt.name}: gap {gap}")
    last = tensors[-1]
    end = int(last.data_offset) + int(last.n_bytes)
    if end > file_bytes:
        ok = False
        problems.append(f"last tensor ends at {end}, file has {file_bytes} bytes")
    return {"ok": ok, "alignment": alignment, "problems": problems[:5]}


def _head_dim(reader: GGUFReader, arch: str, tensors: dict, n_kv_heads: int) -> tuple[int, str]:
    """(head size, where it came from). attn_k is [n_embd, n_kv_heads * head_dim]."""
    key_length = _field(reader, f"{arch}.attention.key_length")
    from_shape = None
    k = tensors.get("blk.0.attn_k.weight")
    if k is not None and len(k.shape) == 2 and int(k.shape[1]) % n_kv_heads == 0:
        from_shape = int(k.shape[1]) // n_kv_heads
    if key_length is not None:
        if from_shape is not None and int(key_length) != from_shape:
            raise SchemaError(f"key_length {key_length} disagrees with attn_k shape ({from_shape})")
        return int(key_length), f"{arch}.attention.key_length"
    if from_shape is not None:
        return from_shape, "blk.0.attn_k.weight shape"
    raise SchemaError("cannot determine the head size")


def build_table(path: Path, alias: str, quant: str, sha256: str, source: dict) -> dict:
    """Read one GGUF file and return its (validated) table as a JSON-ready dict."""
    reader = GGUFReader(str(path))
    arch = str(_field(reader, "general.architecture"))
    by_name = {t.name: t for t in reader.tensors}
    tied = "output.weight" not in by_name
    file_bytes = path.stat().st_size

    rows = []
    for t in reader.tensors:
        shape = [int(x) for x in t.shape]
        n_params = math.prod(shape)
        nbytes = int(t.n_bytes)
        if nbytes != _expected_bytes(n_params, t.tensor_type):
            raise SchemaError(f"{t.name}: reader bytes {nbytes} != block-size formula")
        rows.append(
            {
                "name": t.name,
                "type": t.tensor_type.name,
                "shape": shape,
                "n_dims": len(shape),
                "n_params": n_params,
                "bytes": nbytes,
                "role": assign_role(t.name, len(shape), tied),
            }
        )

    n_heads = int(_field(reader, f"{arch}.attention.head_count"))
    n_kv_heads = int(_field(reader, f"{arch}.attention.head_count_kv"))
    head_dim, head_dim_source = _head_dim(reader, arch, by_name, n_kv_heads)
    embd = by_name["token_embd.weight"]  # shape [n_embd, vocab]

    totals: dict[str, int] = {}
    for role in ("blk", "out", "emb", "other"):
        sel = [r for r in rows if r["role"] == role]
        totals[f"W_{role}"] = sum(r["bytes"] for r in sel)
        totals[f"N_{role}"] = sum(r["n_params"] for r in sel)
    totals["W_all"] = sum(r["bytes"] for r in rows)
    totals["N_all"] = sum(r["n_params"] for r in rows)

    def mix(selected: list[dict]) -> dict:
        out: dict[str, dict] = {}
        for r in selected:
            m = out.setdefault(r["type"], {"n_tensors": 0, "n_params": 0, "bytes": 0})
            m["n_tensors"] += 1
            m["n_params"] += r["n_params"]
            m["bytes"] += r["bytes"]
        return out

    table = {
        "schema_version": SCHEMA_VERSION,
        "kind": "model_table",
        "alias": alias,
        "quant": quant,
        "file": path.name,
        "file_bytes": file_bytes,
        "sha256": sha256,
        "arch": arch,
        "n_layers": int(_field(reader, f"{arch}.block_count")),
        "n_heads": n_heads,
        "n_kv_heads": n_kv_heads,
        "head_dim": head_dim,
        "head_dim_source": head_dim_source,
        "n_embd": int(embd.shape[0]),
        "n_ff": int(_field(reader, f"{arch}.feed_forward_length")),
        "vocab_size": int(embd.shape[1]),
        "tied_embeddings": tied,
        "layout_check": layout_check(
            reader, file_bytes, int(_field(reader, "general.alignment") or DEFAULT_ALIGNMENT)
        ),
        "totals": totals,
        "type_mix": mix(rows),
        "type_mix_by_role": {
            r: mix([x for x in rows if x["role"] == r])
            for r in ("blk", "out", "emb", "other")
            if totals[f"W_{r}"]
        },
        "source": {**source, "gguf_py_version": version("gguf")},
        "tensors": rows,
    }
    ModelTable.from_dict(table)  # raises SchemaError if anything is inconsistent
    return table


def dumps_table(table: dict) -> str:
    """JSON with one tensor per line: readable and small enough to review in a diff."""
    parts = []
    for key, value in table.items():
        if key == "tensors":
            body = ",\n".join("    " + json.dumps(t) for t in value)
            parts.append(f'  "tensors": [\n{body}\n  ]')
        else:
            text = json.dumps(value, indent=2).replace("\n", "\n  ")
            parts.append(f"  {json.dumps(key)}: {text}")
    return "{\n" + ",\n".join(parts) + "\n}\n"


# --- the `make models` driver --------------------------------------------------------------


def read_sha256sums(path: Path) -> dict[str, str]:
    sums = {}
    for line in path.read_text().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            sums[parts[1].lstrip("*").strip()] = parts[0]
    return sums


def read_sidecar(gguf_path: Path) -> str | None:
    """The command line make_models.sh stored next to a model file, if any."""
    side = gguf_path.with_name(gguf_path.name + ".cmd")
    return side.read_text().strip() if side.exists() else None


def source_info(models_dir: Path, work_dir: Path, alias: str, quant: str, sweep: dict) -> dict:
    gguf_path = models_dir / f"{alias}_{quant}.gguf"
    manifest_path = work_dir / "hf" / alias / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    spec = sweep["models"][alias]
    return {
        "hf_repo": spec["hf_repo"],
        "hf_revision": spec["hf_revision"],
        "hf_files_verified": manifest["files"] if manifest else None,
        "llama_cpp_commit": (REPO_ROOT / "infra" / "llamacpp.commit").read_text().strip(),
        "command": read_sidecar(gguf_path),
        "convert_pip_freeze": "results/models/convert_pip_freeze.txt",
    }


def write_table(out: Path, table: dict, force: bool) -> str:
    """Write unless an identical or newer-for-the-same-file table already exists."""
    if out.exists():
        old = json.loads(out.read_text())
        if old.get("sha256") != table["sha256"] and not force:
            raise SystemExit(
                f"{out} describes a different file (sha256 changed); "
                "refusing to overwrite, use --force if the model was rebuilt on purpose"
            )
        if old == json.loads(dumps_table(table)):
            return "up to date"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps_table(table))
    return "written"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gguf", type=Path, help="one file instead of everything in sweep.yaml")
    parser.add_argument("--alias")
    parser.add_argument("--quant")
    parser.add_argument("--sha256", help="with --gguf: the file's SHA256")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "results" / "models")
    parser.add_argument("--models-dir", type=Path, default=REPO_ROOT / "work" / "models")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.gguf:
        if not (args.alias and args.quant and args.sha256):
            parser.error("--gguf needs --alias, --quant and --sha256")
        table = build_table(args.gguf, args.alias, args.quant, args.sha256, {"command": None})
        out = args.out_dir / f"{args.alias}_{args.quant}.json"
        print(f"{out}: {write_table(out, table, args.force)}")
        return 0

    import yaml  # only needed here; keeps the module importable without pyyaml in tests

    sweep = yaml.safe_load((REPO_ROOT / "configs" / "sweep.yaml").read_text())
    sums = read_sha256sums(args.models_dir / "SHA256SUMS")
    status = 0
    for alias in sweep["models"]:
        for quant in sweep["quants"]:
            path = args.models_dir / f"{alias}_{quant}.gguf"
            if path.name not in sums:
                print(f"missing {path.name} in SHA256SUMS (run make models)", file=sys.stderr)
                status = 1
                continue
            source = source_info(args.models_dir, REPO_ROOT / "work", alias, quant, sweep)
            table = build_table(path, alias, quant, sums[path.name], source)
            out = args.out_dir / f"{alias}_{quant}.json"
            t = table["totals"]
            print(
                f"{out.name}: {write_table(out, table, args.force)}  "
                f"W_blk={t['W_blk']:,} W_out={t['W_out']:,} tied={table['tied_embeddings']} "
                f"types={sorted(table['type_mix'])}"
            )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
