#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export MPLCONFIGDIR="${TMPDIR:-/tmp}/retro-cad-matplotlib"
export XDG_CACHE_HOME="${TMPDIR:-/tmp}/retro-cad-cache"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME"
python cad/layout.py
