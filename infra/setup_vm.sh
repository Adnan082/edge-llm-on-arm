#!/usr/bin/env bash
# One-time setup of a fresh Ubuntu 24.04 Arm64 VM (Google Cloud C4A / Axion).
#
#   bash infra/setup_vm.sh
#
# Installs the toolchain, creates .venv with the project's pinned Python deps, and clones
# llama.cpp at a pinned commit into work/llama.cpp. Safe to re-run.
#
# llama.cpp pin: the commit comes from, in order,
#   1. $LLAMACPP_COMMIT (full 40-character SHA)
#   2. infra/llamacpp.commit (written by this script on the first run)
#   3. otherwise the current HEAD of the default branch, which is then written to
#      infra/llamacpp.commit. Commit that file and copy the SHA into CLAUDE.md §11.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$REPO_ROOT/work"
LLAMACPP_DIR="$WORK_DIR/llama.cpp"
LLAMACPP_URL="${LLAMACPP_URL:-https://github.com/ggml-org/llama.cpp.git}"
PIN_FILE="$REPO_ROOT/infra/llamacpp.commit"

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

# --- sanity: right machine ---------------------------------------------------------------
[ "$(uname -m)" = "aarch64" ] || die "expected an AArch64 machine, got $(uname -m)"
. /etc/os-release
[ "${ID:-}" = "ubuntu" ] && [ "${VERSION_ID:-}" = "24.04" ] ||
    echo "warning: written for Ubuntu 24.04, this is ${PRETTY_NAME:-unknown}" >&2

# --- packages ----------------------------------------------------------------------------
# build-essential: gcc/g++/make/binutils (objdump for the disassembly evidence).
# libcurl4-openssl-dev: llama.cpp's optional model-download support; harmless if unused.
# numactl: thread/memory pinning for the bandwidth kernel.
log "Installing packages"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build pkg-config git curl ca-certificates jq numactl \
    libcurl4-openssl-dev python3 python3-venv python3-pip

# --- python environment ------------------------------------------------------------------
log "Creating .venv and installing pinned Python dependencies"
if [ ! -d "$REPO_ROOT/.venv" ]; then
    python3 -m venv "$REPO_ROOT/.venv"
fi
"$REPO_ROOT/.venv/bin/pip" install --upgrade pip
"$REPO_ROOT/.venv/bin/pip" install -e "$REPO_ROOT[dev]"

# --- llama.cpp at a pinned commit --------------------------------------------------------
mkdir -p "$WORK_DIR"

if [ -n "${LLAMACPP_COMMIT:-}" ]; then
    COMMIT="$LLAMACPP_COMMIT"
elif [ -s "$PIN_FILE" ]; then
    COMMIT="$(tr -d '[:space:]' < "$PIN_FILE")"
else
    log "No pin found; resolving the current HEAD of $LLAMACPP_URL"
    COMMIT="$(git ls-remote "$LLAMACPP_URL" HEAD | cut -f1)"
    [ -n "$COMMIT" ] || die "could not resolve llama.cpp HEAD"
    echo "$COMMIT" > "$PIN_FILE"
    echo "pinned llama.cpp to $COMMIT (written to infra/llamacpp.commit: commit it)"
fi
echo "$COMMIT" | grep -Eq '^[0-9a-f]{40}$' || die "llama.cpp commit must be a full 40-char SHA: $COMMIT"

log "Cloning llama.cpp at $COMMIT"
if [ ! -d "$LLAMACPP_DIR/.git" ]; then
    # Blobless clone: full history for the pin, file contents fetched on checkout.
    git clone --filter=blob:none "$LLAMACPP_URL" "$LLAMACPP_DIR"
fi
git -C "$LLAMACPP_DIR" fetch --quiet origin
git -C "$LLAMACPP_DIR" checkout --quiet --detach "$COMMIT"
[ "$(git -C "$LLAMACPP_DIR" rev-parse HEAD)" = "$COMMIT" ] || die "checkout did not land on $COMMIT"

# --- summary -----------------------------------------------------------------------------
log "Done"
echo "gcc:      $(gcc --version | head -n1)"
echo "cmake:    $(cmake --version | head -n1)"
echo "python:   $("$REPO_ROOT/.venv/bin/python" --version)"
echo "llama.cpp: $(git -C "$LLAMACPP_DIR" rev-parse HEAD)"
echo "Next: make env"
