"""gguf_table on a tiny GGUF written by the test, checked against the CLAUDE.md §8 anchors."""

import json

import gguf
import numpy as np
import pytest
from gguf import GGMLQuantizationType as Q

from edge_llm import gguf_table
from edge_llm.schema import ModelTable, SchemaError

SHA = "a" * 64
ARCH = "qwen3"

# CLAUDE.md §8 known answers: bytes per block of weights, as ggml defines the blocks.
ANCHORS = {
    Q.Q4_0: (32, 18),  # 4.5 bits/weight
    Q.Q8_0: (32, 34),  # 8.5
    Q.Q4_K: (256, 144),  # 4.5
    Q.Q6_K: (256, 210),  # 6.5625
    Q.F16: (1, 2),  # 16
    Q.F32: (1, 4),
}


def add_quantised(w: gguf.GGUFWriter, name: str, qtype: Q, rows: int, cols: int) -> None:
    """Add a rows x cols (logical) tensor of the given type with zeroed raw block data.

    rows == 0 makes a 1-D vector of `cols` values, like the norm weights in a real model.
    """
    block, type_size = gguf.GGML_QUANT_SIZES[qtype]
    if rows == 0:
        w.add_tensor(name, np.zeros(cols, dtype=np.float32))
    elif qtype in (Q.F16, Q.F32):
        dtype = np.float16 if qtype == Q.F16 else np.float32
        w.add_tensor(name, np.zeros((rows, cols), dtype=dtype))
    else:
        raw = np.zeros((rows, cols // block * type_size), dtype=np.uint8)
        w.add_tensor(name, raw, raw_dtype=qtype)


def write_tiny(path, tied: bool, key_length: bool = True, n_heads=4, n_kv=2, head_dim=64):
    """A 2-layer model: 1-D norms, a type per anchor format, optional output.weight."""
    n_embd, n_ff, vocab = 256, 512, 512
    w = gguf.GGUFWriter(str(path), ARCH)
    w.add_block_count(2)
    w.add_head_count(n_heads)
    w.add_head_count_kv(n_kv)
    w.add_embedding_length(n_embd)
    w.add_feed_forward_length(n_ff)
    w.add_context_length(128)
    if key_length:
        w.add_key_length(head_dim)
        w.add_value_length(head_dim)
    add_quantised(w, "token_embd.weight", Q.Q6_K, vocab, n_embd)
    if not tied:
        add_quantised(w, "output.weight", Q.Q8_0, vocab, n_embd)
    add_quantised(w, "output_norm.weight", Q.F32, 0, n_embd)
    add_quantised(w, "blk.0.attn_k.weight", Q.Q4_0, n_kv * head_dim, n_embd)
    add_quantised(w, "blk.0.attn_q.weight", Q.Q4_K, n_heads * head_dim, n_embd)
    add_quantised(w, "blk.0.ffn_down.weight", Q.Q6_K, n_embd, n_ff)
    add_quantised(w, "blk.0.ffn_up.weight", Q.F16, n_ff, n_embd)
    add_quantised(w, "blk.0.attn_norm.weight", Q.F32, 0, n_embd)
    add_quantised(w, "blk.1.attn_k.weight", Q.Q8_0, n_kv * head_dim, n_embd)
    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()
    return path


def rows_by_name(table):
    return {t["name"]: t for t in table["tensors"]}


def test_bytes_match_the_ggml_block_anchors(tmp_path):
    table = gguf_table.build_table(
        write_tiny(tmp_path / "m.gguf", tied=True), "small", "mix", SHA, {}
    )
    rows = rows_by_name(table)
    anchor = {
        "blk.0.attn_k.weight": Q.Q4_0,
        "blk.0.attn_q.weight": Q.Q4_K,
        "blk.0.ffn_down.weight": Q.Q6_K,
        "blk.0.ffn_up.weight": Q.F16,
        "blk.0.attn_norm.weight": Q.F32,
        "blk.1.attn_k.weight": Q.Q8_0,
    }
    for name, qtype in anchor.items():
        block, type_size = ANCHORS[qtype]
        r = rows[name]
        assert r["type"] == qtype.name
        assert r["bytes"] == r["n_params"] // block * type_size  # exact, not approximate
    # bits per weight, straight from the spec's table
    bits = lambda n: 8 * rows[n]["bytes"] / rows[n]["n_params"]
    assert bits("blk.0.attn_k.weight") == 4.5
    assert bits("blk.1.attn_k.weight") == 8.5
    assert bits("blk.0.attn_q.weight") == 4.5
    assert bits("blk.0.ffn_down.weight") == 6.5625
    assert bits("blk.0.ffn_up.weight") == 16


def test_roles_tied_embeddings(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    assert table["tied_embeddings"] is True
    rows = rows_by_name(table)
    assert rows["token_embd.weight"]["role"] == "out"  # the tied table IS the output projection
    assert rows["output_norm.weight"]["role"] == "other"
    assert rows["blk.0.attn_norm.weight"]["role"] == "other"  # 1-D, not a weight matrix
    assert rows["blk.0.ffn_up.weight"]["role"] == "blk"
    t = table["totals"]
    assert t["W_out"] == rows["token_embd.weight"]["bytes"]
    assert t["W_emb"] == 0


def test_roles_untied_embeddings(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=False), "s", "x", SHA, {})
    assert table["tied_embeddings"] is False
    rows = rows_by_name(table)
    assert rows["output.weight"]["role"] == "out"
    assert rows["token_embd.weight"]["role"] == "emb"
    assert table["totals"]["W_out"] == rows["output.weight"]["bytes"]
    assert table["totals"]["W_emb"] == rows["token_embd.weight"]["bytes"]


def test_totals_and_type_mix(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    t = table["totals"]
    assert t["W_all"] == sum(r["bytes"] for r in table["tensors"])
    assert t["W_all"] == t["W_blk"] + t["W_out"] + t["W_emb"] + t["W_other"]
    assert t["N_all"] == sum(r["n_params"] for r in table["tensors"])
    assert set(table["type_mix"]) == {"Q4_0", "Q4_K", "Q6_K", "F16", "F32", "Q8_0"}
    assert table["type_mix"]["Q6_K"]["n_tensors"] == 2  # embedding + ffn_down
    assert set(table["type_mix_by_role"]["blk"]) == {"Q4_0", "Q4_K", "Q6_K", "F16", "Q8_0"}
    assert table["layout_check"]["ok"]
    assert table["file_bytes"] >= t["W_all"]


def test_head_dim_from_key_length_not_hidden_over_heads(tmp_path):
    # n_embd / n_heads = 256 / 4 = 64, but this model has head size 32 (as Qwen3-0.6B has
    # 128 where 1024 / 16 = 64).
    path = write_tiny(tmp_path / "m.gguf", tied=True, head_dim=32)
    table = gguf_table.build_table(path, "s", "x", SHA, {})
    assert table["head_dim"] == 32
    assert table["head_dim"] != table["n_embd"] // table["n_heads"]  # 32 != 64
    assert table["head_dim_source"].endswith("attention.key_length")


def test_head_dim_falls_back_to_attn_k_shape(tmp_path):
    path = write_tiny(tmp_path / "m.gguf", tied=True, key_length=False, head_dim=32)
    table = gguf_table.build_table(path, "s", "x", SHA, {})
    assert table["head_dim"] == 32
    assert "attn_k" in table["head_dim_source"]


def test_model_shape_numbers(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    assert (table["n_layers"], table["n_heads"], table["n_kv_heads"]) == (2, 4, 2)
    assert (table["n_embd"], table["n_ff"], table["vocab_size"]) == (256, 512, 512)


def test_table_survives_json_round_trip_and_schema(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    text = gguf_table.dumps_table(table)
    again = json.loads(text)
    assert again == table
    ModelTable.from_dict(again)  # valid


def test_schema_rejects_inconsistent_totals(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    table["totals"]["W_blk"] += 1
    with pytest.raises(SchemaError, match="W_blk"):
        ModelTable.from_dict(table)


def test_schema_rejects_unknown_role_and_missing_key(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    bad = json.loads(json.dumps(table))
    bad["tensors"][0]["role"] = "weights"
    with pytest.raises(SchemaError, match="role"):
        ModelTable.from_dict(bad)
    del table["vocab_size"]
    with pytest.raises(SchemaError, match="missing keys"):
        ModelTable.from_dict(table)


def test_write_table_refuses_a_different_file(tmp_path):
    table = gguf_table.build_table(write_tiny(tmp_path / "m.gguf", tied=True), "s", "x", SHA, {})
    out = tmp_path / "out" / "s_x.json"
    assert gguf_table.write_table(out, table, force=False) == "written"
    assert gguf_table.write_table(out, table, force=False) == "up to date"
    changed = dict(table, sha256="b" * 64)
    with pytest.raises(SystemExit):
        gguf_table.write_table(out, changed, force=False)
    assert gguf_table.write_table(out, changed, force=True) == "written"


def test_assign_role_rules():
    ar = gguf_table.assign_role
    assert ar("blk.3.ffn_gate.weight", 2, tied=True) == "blk"
    assert ar("blk.3.attn_q_norm.weight", 1, tied=True) == "other"
    assert ar("output_norm.weight", 1, tied=False) == "other"
    assert ar("rope_freqs.weight", 1, tied=False) == "other"
    assert ar("token_embd.weight", 2, tied=True) == "out"
    assert ar("token_embd.weight", 2, tied=False) == "emb"
    assert ar("output.weight", 2, tied=False) == "out"
