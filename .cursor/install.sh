#!/usr/bin/env bash
# Idempotent bootstrap for the Heat Pump Cost Optimizer test/dev environment.
# The base image already ships Python 3 and Node 22; this only adds the
# pinned Python stack the test suite imports.
set -euo pipefail

# Ensure pip exists for the system interpreter (older/minimal images may lack it).
python3 -m pip --version >/dev/null 2>&1 || python3 -m ensurepip --upgrade

# Install the exact versions CI pins (numpy/scipy/voluptuous/aiohttp/pyyaml/
# threadpoolctl) into the user site, so `python3 tests/<script>.py` runs
# without activating a virtualenv. The pins keep the golden-drift solver
# stack identical to CI.
python3 -m pip install --user --break-system-packages -r tests/requirements-ci.txt

echo "heatpump_optimizer environment ready."
echo "Run tests with: PYTHONPATH=tests/hastub python3 tests/<script>.py"
echo "Or the whole gate: ./tests/run.sh   (scoped: GATE_SCOPE=auto ./tests/run.sh)"
