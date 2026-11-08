#!/usr/bin/env bash
# Rebuild the P3 printable parts (STL/3MF/STEP/manifest/checks) and the offline viewer + previews.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python cad/p3_print.py
python tools/package_p2.py outputs/p3
if command -v node >/dev/null; then NODE_PATH="${NODE_PATH:-$(npm root -g)}" node tools/render_p2.js outputs/p3 tools/p3_shots.json || echo "Preview render skipped"; fi
