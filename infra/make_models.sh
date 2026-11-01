#!/usr/bin/env bash
# Day 2: Hugging Face safetensors -> F16 GGUF -> every quantisation format in configs/sweep.yaml.
#
#   bash infra/make_models.sh        (or: make models, which then writes the tensor tables)
#
# For each model alias in configs/sweep.yaml:
#   1. download the safetensors at the pinned hf_revision into work/hf/<alias>/ and check every
#      file's hash against the Hub listing (infra/hf_fetch.py);
#   2. convert to F16 with the pinned llama.cpp's convert_hf_to_gguf.py, in its own venv
#      (work/venv-convert, installed from llama.cpp's requirements file for that script);
#   3. run llama-quantize from the baseline build to every other format, with default settings
#      (no --pure, no imatrix: ADR-010).
# Files land in work/models/<alias>_<quant>.gguf; their hashes in work/models/SHA256SUMS
# (sha256sum format, read by bench/env_capture.py). A file that already exists is not rebuilt,
# but its hash is checked against SHA256SUMS every time. Each file gets a <file>.cmd sidecar with
# the exact command that made it. Safe to re-run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$REPO_ROOT/work"
LLAMACPP_DIR="$WORK_DIR/llama.cpp"
HF_DIR="$WORK_DIR/hf"
MODELS_DIR="$WORK_DIR/models"
VENV="$WORK_DIR/venv-convert"
SUMS="$MODELS_DIR/SHA256SUMS"
QUANTIZE="$WORK_DIR/build-baseline/bin/llama-quantize"
SWEEP="$REPO_ROOT/configs/sweep.yaml"
FREEZE_COPY="$REPO_ROOT/results/models/convert_pip_freeze.txt"

# The project venv has pyyaml; fall back to the system python on a machine without it.
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then PY="$REPO_ROOT/.venv/bin/python"; else PY=python3; fi

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -x "$QUANTIZE" ] || die "$QUANTIZE not found: run make build first"
[ -f "$LLAMACPP_DIR/convert_hf_to_gguf.py" ] || die "llama.cpp is not cloned: run infra/setup_vm.sh"
mkdir -p "$MODELS_DIR" "$HF_DIR" "$REPO_ROOT/results/models"

# Models need roughly 20 GB in total (safetensors, F16, four formats, the converter venv).
free_gb=$(df --output=avail -BG "$WORK_DIR" | tail -n1 | tr -dc '0-9')
echo "free disk under work/: ${free_gb} GB (this script needs about 20 GB when starting from nothing)"
[ "$free_gb" -ge 20 ] || echo "warning: less than 20 GB free; the run may fail part-way" >&2

# --- read configs/sweep.yaml -----------------------------------------------------------------
mapfile -t MODEL_ROWS < <("$PY" - "$SWEEP" <<'EOF'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1]))
for alias, m in cfg["models"].items():
    print(alias, m["hf_repo"], m["hf_revision"])
EOF
)
mapfile -t QUANTS < <("$PY" -c "import sys, yaml; print(*yaml.safe_load(open(sys.argv[1]))['quants'], sep='\n')" "$SWEEP")
[ "${#MODEL_ROWS[@]}" -gt 0 ] && [ "${#QUANTS[@]}" -gt 0 ] || die "no models or quants in sweep.yaml"

# --- SHA256SUMS helpers ----------------------------------------------------------------------
sums_get() { [ -f "$SUMS" ] && awk -v f="$1" '$2==f {print $1}' "$SUMS" || true; }
sums_set() { # name hash
    local tmp; tmp="$(mktemp "$MODELS_DIR/.sums.XXXXXX")"
    { [ -f "$SUMS" ] && awk -v f="$1" '$2!=f' "$SUMS" || true; echo "$2  $1"; } | sort -k2 > "$tmp"
    mv "$tmp" "$SUMS"
}
# Check a finished file against SHA256SUMS, or record its hash the first time it is seen.
# A mismatch stops the script: the file changed after it was hashed, and silently rebuilding
# would change the data behind every later number.
check_hash() { # name
    local name="$1" want got
    want="$(sums_get "$name")"
    got="$(sha256sum "$MODELS_DIR/$name" | cut -d' ' -f1)"
    if [ -z "$want" ]; then
        sums_set "$name" "$got"; echo "$name: hash recorded ($got)"
    elif [ "$want" != "$got" ]; then
        die "$name: SHA256 differs from SHA256SUMS (file: $got, recorded: $want); delete the file and its .cmd to rebuild on purpose"
    else
        echo "$name: hash ok"
    fi
}

# --- converter venv --------------------------------------------------------------------------
setup_convert_venv() {
    local req_dir="$LLAMACPP_DIR/requirements" stamp want
    want="$( (cat "$req_dir"/requirements-convert_hf_to_gguf.txt "$req_dir"/requirements-convert_legacy_llama.txt; python3 --version) | sha256sum | cut -d' ' -f1)"
    stamp="$VENV/.requirements-stamp"
    if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
    if [ "$(cat "$stamp" 2>/dev/null || true)" != "$want" ]; then
        log "Installing the converter's requirements into work/venv-convert (a few minutes: torch)"
        "$VENV/bin/pip" install --upgrade pip
        "$VENV/bin/pip" install -r "$req_dir/requirements-convert_hf_to_gguf.txt"
        echo "$want" > "$stamp"
    fi
    "$VENV/bin/pip" freeze > "$VENV/pip-freeze.txt"
    if [ -f "$FREEZE_COPY" ] && ! cmp -s "$VENV/pip-freeze.txt" "$FREEZE_COPY"; then
        die "converter pip freeze changed; compare $VENV/pip-freeze.txt with $FREEZE_COPY"
    fi
    cp -n "$VENV/pip-freeze.txt" "$FREEZE_COPY" || true
}
setup_convert_venv

# --- per model ---------------------------------------------------------------------------------
for row in "${MODEL_ROWS[@]}"; do
    read -r ALIAS REPO REV <<< "$row"
    case "$REV" in TBD|"") die "$ALIAS: hf_revision is TBD in sweep.yaml" ;; esac
    log "$ALIAS = $REPO @ ${REV:0:12}"

    python3 "$REPO_ROOT/infra/hf_fetch.py" --repo "$REPO" --revision "$REV" --dest "$HF_DIR/$ALIAS"

    # F16: the source for every other format (ADR-003).
    F16="${ALIAS}_F16.gguf"
    if [ ! -f "$MODELS_DIR/$F16" ]; then
        log "Converting $ALIAS to F16"
        tmp="$MODELS_DIR/.tmp-$F16"
        cmd=("$VENV/bin/python" "$LLAMACPP_DIR/convert_hf_to_gguf.py" "$HF_DIR/$ALIAS" --outtype f16 --outfile "$tmp")
        "${cmd[@]}"
        mv "$tmp" "$MODELS_DIR/$F16"
        # Record the command with the final file name (the converter ran against a temp name).
        printf '%s\n' "${cmd[*]//$tmp/$MODELS_DIR/$F16}" > "$MODELS_DIR/$F16.cmd"
    fi
    check_hash "$F16"

    for Q in "${QUANTS[@]}"; do
        [ "$Q" = "F16" ] && continue
        OUT="${ALIAS}_${Q}.gguf"
        if [ ! -f "$MODELS_DIR/$OUT" ]; then
            log "Quantising $ALIAS to $Q"
            tmp="$MODELS_DIR/.tmp-$OUT"
            # Default settings on purpose: no --pure, no --imatrix, no tensor-type overrides.
            cmd=("$QUANTIZE" "$MODELS_DIR/$F16" "$tmp" "$Q")
            "${cmd[@]}"
            mv "$tmp" "$MODELS_DIR/$OUT"
            printf '%s\n' "${cmd[*]//$tmp/$MODELS_DIR/$OUT}" > "$MODELS_DIR/$OUT.cmd"
        fi
        check_hash "$OUT"
    done
done

log "Done: $(wc -l < "$SUMS") model files in work/models"
ls -l "$MODELS_DIR"/*.gguf
echo "Next: the tensor tables (make models runs this): python -m edge_llm.gguf_table"
