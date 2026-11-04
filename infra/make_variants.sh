#!/usr/bin/env bash
# Day 8, Check A: two Q4_0 variants of the small model with ONLY the output layer changed.
#
#   bash infra/make_variants.sh        (or: make day8-variants)
#
# From work/models/small_F16.gguf, with the pinned llama-quantize (baseline build) and its default
# settings except for one option (ADR-010 still holds for everything else):
#   small_Q4_0outq8.gguf   --output-tensor-type q8_0   (output.weight Q8_0, the rest as small_Q4_0)
#   small_Q4_0outq4.gguf   --output-tensor-type q4_0   (output.weight Q4_0, the rest as small_Q4_0)
# Their SHA256s go into work/models/SHA256SUMS and each file gets a .cmd sidecar, exactly like
# infra/make_models.sh. Then `python -m bench.day8 tables` writes results/models/<file>.json and
# STOPS if output.weight is not the intended type or any other tensor differs from small_Q4_0.
# Safe to re-run: an existing file is not rebuilt, only its hash is checked.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$REPO_ROOT/work"
MODELS_DIR="$WORK_DIR/models"
SUMS="$MODELS_DIR/SHA256SUMS"
QUANTIZE="$WORK_DIR/build-baseline/bin/llama-quantize"
F16="small_F16.gguf"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then PY="$REPO_ROOT/.venv/bin/python"; else PY=python3; fi

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -x "$QUANTIZE" ] || die "$QUANTIZE not found: run make build first"
[ -f "$MODELS_DIR/$F16" ] || die "$MODELS_DIR/$F16 not found: run make models first"
[ -f "$MODELS_DIR/small_Q4_0.gguf" ] || die "small_Q4_0.gguf not found: run make models first"
# The option must exist at the pinned commit; do not assume it. llama-quantize prints its usage and
# exits 1, so the text is captured first: in a pipe, pipefail would turn that exit 1 into a failure.
QUANTIZE_HELP="$("$QUANTIZE" --help 2>&1 || true)"
grep -q -- "--output-tensor-type" <<<"$QUANTIZE_HELP" \
    || die "this llama-quantize has no --output-tensor-type option"

# Same helpers as make_models.sh: a hash is recorded the first time, then checked on every run.
sums_get() { [ -f "$SUMS" ] && awk -v f="$1" '$2==f {print $1}' "$SUMS" || true; }
sums_set() { # name hash
    local tmp; tmp="$(mktemp "$MODELS_DIR/.sums.XXXXXX")"
    { [ -f "$SUMS" ] && awk -v f="$1" '$2!=f' "$SUMS" || true; echo "$2  $1"; } | sort -k2 > "$tmp"
    mv "$tmp" "$SUMS"
}
check_hash() { # name
    local name="$1" want got
    want="$(sums_get "$name")"
    got="$(sha256sum "$MODELS_DIR/$name" | cut -d' ' -f1)"
    if [ -z "$want" ]; then
        sums_set "$name" "$got"; echo "$name: hash recorded ($got)"
    elif [ "$want" != "$got" ]; then
        die "$name: SHA256 differs from SHA256SUMS (file: $got, recorded: $want)"
    else
        echo "$name: hash ok"
    fi
}

check_hash "$F16"
make_variant() { # file-suffix type
    local out="small_$1.gguf" tmp cmd
    if [ ! -f "$MODELS_DIR/$out" ]; then
        log "Quantising small to Q4_0 with --output-tensor-type $2 -> $out"
        tmp="$MODELS_DIR/.tmp-$out"
        cmd=("$QUANTIZE" --output-tensor-type "$2" "$MODELS_DIR/$F16" "$tmp" Q4_0)
        "${cmd[@]}"
        mv "$tmp" "$MODELS_DIR/$out"
        printf '%s\n' "${cmd[*]//$tmp/$MODELS_DIR/$out}" > "$MODELS_DIR/$out.cmd"
    fi
    check_hash "$out"
}
make_variant Q4_0outq8 q8_0
make_variant Q4_0outq4 q4_0

log "Tensor tables and the 'only output.weight changed' check"
cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT/src" "$PY" -m bench.day8 tables
ls -l "$MODELS_DIR"/small_Q4_0*.gguf
