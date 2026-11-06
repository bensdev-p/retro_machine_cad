#!/usr/bin/env bash
# Rebuild the P2 concept: CAD + checks, offline viewer, preview renders (needs Node + Playwright Chromium).
set -euo pipefail
cd -- "$(dirname -- "$0")"
python cad/p2_concept.py
python tools/package_p2.py
if command -v node >/dev/null; then NODE_PATH="${NODE_PATH:-$(npm root -g)}" node tools/render_p2.js || echo "Preview render skipped (Playwright not available)"; fi
