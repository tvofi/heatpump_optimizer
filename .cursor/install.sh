#!/usr/bin/env bash
# Idempotent bootstrap for the Heat Pump Cost Optimizer test/dev environment.
# The base image already ships Python 3 and Node 22; this only adds the
# pinned Python stack the test suite imports, plus Playwright + Chromium for
# the real-browser layout lane (tests/card_browser.mjs).
set -euo pipefail

# --- Python test/runtime stack -------------------------------------------
# Ensure pip exists for the system interpreter (older/minimal images may lack it).
python3 -m pip --version >/dev/null 2>&1 || python3 -m ensurepip --upgrade

# Install the exact versions CI pins (numpy/scipy/voluptuous/aiohttp/pyyaml/
# threadpoolctl) into the user site, so `python3 tests/<script>.py` runs
# without activating a virtualenv. The pins keep the golden-drift solver
# stack identical to CI.
python3 -m pip install --user --break-system-packages -r tests/requirements-ci.txt

# --- Playwright + Chromium for the real-browser lane ---------------------
# tests/card_browser.mjs resolves `playwright` via NODE_PATH and launches the
# bundled Chromium found under PLAYWRIGHT_BROWSERS_PATH. Both the npm package
# and the browser live outside the repository (the repo has no node_modules
# and should not grow one for a single lane). Versions and the browsers path
# match .github/workflows/tests.yml so a local run mirrors CI.
PW_VERSION="1.49.0"
PW_DIR="${HOME}/.cache/heatpump_optimizer/pwlane"
export PLAYWRIGHT_BROWSERS_PATH="${HOME}/.cache/pw-browsers"

if command -v npm >/dev/null 2>&1; then
  mkdir -p "${PW_DIR}"
  # npm install is idempotent; re-running just verifies the pinned package.
  npm install --prefix "${PW_DIR}" "playwright@${PW_VERSION}"
  # `--with-deps` also installs the OS libraries Chromium needs (via sudo);
  # fall back to a browser-only install if that step is not permitted, since
  # the desktop base image already carries most of them.
  "${PW_DIR}/node_modules/.bin/playwright" install --with-deps chromium \
    || "${PW_DIR}/node_modules/.bin/playwright" install chromium
else
  echo "WARNING: npm not found; skipping Playwright/Chromium setup." >&2
fi

echo "heatpump_optimizer environment ready."
echo "Run a script:      PYTHONPATH=tests/hastub python3 tests/<script>.py"
echo "Whole gate:        ./tests/run.sh   (scoped: GATE_SCOPE=auto ./tests/run.sh)"
echo "Real-browser lane: bash .cursor/browser-lane.sh"
