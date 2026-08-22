#!/usr/bin/env bash
#
# Run the whole test suite in dependency order.
#
#   ./tests/run.sh
#
# The Home Assistant stub lives in `tests/hastub` and is version-controlled, so
# the suite is reproducible; it used to sit in /tmp and vanish on reboot.
# `plan_view.py` writes /tmp/plandata.json, which `card.mjs` then reads, so the
# order below is not arbitrary.
set -u

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi
export PYTHONPATH="$PWD/tests/hastub:${PYTHONPATH:-}"

failed=0
run() {
  echo
  echo "########## $* ##########"
  if ! "$@"; then
    echo ">>> FAILED: $*"
    failed=$((failed + 1))
  fi
}

# Unit-style checks first: they are fast, and a failure here explains any
# end-to-end failure that follows.
run "$PYTHON" tests/features.py
run "$PYTHON" tests/entities.py
run "$PYTHON" tests/open_meteo.py
run "$PYTHON" tests/solar_alignment.py

# End-to-end optimizer behaviour.
run "$PYTHON" tests/validate.py
run "$PYTHON" tests/edge.py
run "$PYTHON" tests/backtest.py

# Plan payloads, then the card that renders them.
run "$PYTHON" tests/plan_view.py
if command -v node >/dev/null 2>&1; then
  run node tests/card.mjs
else
  echo "SKIP: node not found, skipping tests/card.mjs"
fi

echo
if [ "$failed" -ne 0 ]; then
  echo "$failed TEST SCRIPT(S) FAILED"
  exit 1
fi
echo "ALL TEST SCRIPTS PASSED"
