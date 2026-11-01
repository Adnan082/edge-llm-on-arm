#!/usr/bin/env bash
# Day 2: build llama.cpp twice from the same pinned commit.
#
#   bash infra/build_llamacpp.sh        (or: make build)
#
#   work/build-baseline   Release, default options
#   work/build-kleidiai   the same, plus -DGGML_CPU_KLEIDIAI=ON  (the only intended difference)
#
# Both use the default compiler flags the project's CMake chooses (-O3 with -mcpu=native-style
# flags on AArch64: see GGML_NATIVE in ggml/CMakeLists.txt); the real flags are read back from
# compile_commands.json into the build record, not assumed.
#
# Only the three programs the project needs are built: llama-bench (the harness),
# llama-quantize (make models) and llama-completion (prints the system-info line that
# llama-bench does not). llama-cli is skipped because at this commit it drags in the whole
# server. KleidiAI is downloaded by CMake when the kleidiai build is configured.
#
# Steps: configure both -> fail if their CMake caches differ in anything but KleidiAI entries
# and paths -> build both -> write results/raw/build/<session_id>_build.json. Safe to re-run:
# CMake and Ninja only redo what changed, and an unchanged build record is not rewritten.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$REPO_ROOT/work"
LLAMACPP_DIR="$WORK_DIR/llama.cpp"
PIN="$(tr -d '[:space:]' < "$REPO_ROOT/infra/llamacpp.commit")"
TARGETS=(llama-bench llama-quantize llama-completion)

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then PY="$REPO_ROOT/.venv/bin/python"; else PY=python3; fi

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -d "$LLAMACPP_DIR/.git" ] || die "llama.cpp is not cloned: run infra/setup_vm.sh"
[ "$(git -C "$LLAMACPP_DIR" rev-parse HEAD)" = "$PIN" ] || die "work/llama.cpp is not at the pinned commit $PIN"
[ -z "$(git -C "$LLAMACPP_DIR" status --porcelain)" ] || die "work/llama.cpp has local changes"
[ -s "$WORK_DIR/session_id" ] || die "no session id: run make env first"
command -v ninja >/dev/null || die "ninja not found: run infra/setup_vm.sh"

# The option name is checked against the source rather than trusted from memory.
grep -q 'option(GGML_CPU_KLEIDIAI' "$LLAMACPP_DIR/ggml/CMakeLists.txt" ||
    die "GGML_CPU_KLEIDIAI is not an option at this commit; update this script"

configure() { # name [extra cmake args...]
    local name="$1"; shift
    local dir="$WORK_DIR/build-$name" logfile
    mkdir -p "$dir"
    # Keep the first configure log (it has the KleidiAI download lines); later ones go aside.
    if [ -f "$dir/configure.log" ]; then logfile="$dir/configure-rerun.log"; else logfile="$dir/configure.log"; fi
    log "Configuring $name"
    cmake -S "$LLAMACPP_DIR" -B "$dir" -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        "$@" 2>&1 | tee "$logfile"
}

configure baseline
configure kleidiai -DGGML_CPU_KLEIDIAI=ON

log "Comparing the two CMake caches"
(cd "$REPO_ROOT" && "$PY" -m bench.build_record --check-caches)

for name in baseline kleidiai; do
    log "Building $name ($(date -u +%H:%M:%SZ))"
    cmake --build "$WORK_DIR/build-$name" --target "${TARGETS[@]}"
done
log "Builds finished at $(date -u +%H:%M:%SZ)"

log "Writing the build record"
(cd "$REPO_ROOT" && "$PY" -m bench.build_record --write)

for name in baseline kleidiai; do
    for t in "${TARGETS[@]}"; do
        [ -x "$WORK_DIR/build-$name/bin/$t" ] || die "missing $WORK_DIR/build-$name/bin/$t"
    done
done
echo "Next: make models, then make check-builds"
