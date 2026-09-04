#!/usr/bin/env bash
# Convenience runner for the real-browser layout lane (tests/card_browser.mjs).
# It sets the same NODE_PATH / PLAYWRIGHT_BROWSERS_PATH the CI `browser` job
# uses, writes the plan payload the card renders against, then runs the lane.
# Requires .cursor/install.sh to have installed Playwright + Chromium first.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

PW_DIR="${HOME}/.cache/heatpump_optimizer/pwlane"
export PLAYWRIGHT_BROWSERS_PATH="${HOME}/.cache/pw-browsers"
export NODE_PATH="${PW_DIR}/node_modules"

if [ ! -d "${NODE_PATH}/playwright" ]; then
  echo "Playwright is not installed. Run: bash .cursor/install.sh" >&2
  exit 1
fi

# card_browser.mjs reads the payload plan_view.py writes (per-checkout default).
PYTHONPATH=tests/hastub python3 tests/plan_view.py >/dev/null

exec node tests/card_browser.mjs "$@"
