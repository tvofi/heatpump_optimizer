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
#
# GOLDEN_MODE picks how the characterization fixtures are checked:
#   strict (default) — exact comparison against the committed fixtures, plus
#     the five-fixture env_drift gate against GOLDEN_REF (default origin/main).
#   drift — no exact comparison at all; instead env_drift.py --all captures
#     every scenario from this tree AND from GOLDEN_REF in the same
#     environment and requires them identical. This is what CI runs: solver
#     floats are not bit-stable across BLAS builds, so comparing this
#     machine's output against fixtures recorded on another would cry wolf.
set -u

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi
export PYTHONPATH="$PWD/tests/hastub:${PYTHONPATH:-}"

GOLDEN_MODE="${GOLDEN_MODE:-strict}"
GOLDEN_REF="${GOLDEN_REF:-origin/main}"

failed=0
run() {
  echo
  echo "########## $* ##########"
  if ! "$@"; then
    echo ">>> FAILED: $*"
    failed=$((failed + 1))
  fi
}

# Every test script must be wired into this file or deliberately allow-listed;
# a script added to tests/ and forgotten here would otherwise silently never
# run — which is exactly how optimality.py sat dormant for a year.
for f in tests/*.py; do
  base=$(basename "$f")
  case "$base" in
    harness.py|profiles.py) continue ;;  # shared plumbing, not tests
    # Run by features.py in a subprocess: HASTUB_TZ must be set before the
    # dt stub is imported, which an in-process import cannot arrange.
    dst_checks.py) continue ;;
  esac
  if ! grep -q "$base" tests/run.sh; then
    echo "UNWIRED TEST: tests/$base is not referenced by tests/run.sh"
    failed=$((failed + 1))
  fi
done

# Unit-style checks first: they are fast, and a failure here explains any
# end-to-end failure that follows.
run "$PYTHON" tests/features.py
run "$PYTHON" tests/entities.py
run "$PYTHON" tests/manual_plan.py
run "$PYTHON" tests/open_meteo.py
run "$PYTHON" tests/solar_alignment.py

# The characterization harness: exact behaviour, pinned. Runs before the
# outcome-based scripts because when both fail, this one says *what* changed.
if [ "$GOLDEN_MODE" = "drift" ]; then
  run "$PYTHON" tests/env_drift.py --all "$GOLDEN_REF"
else
  run "$PYTHON" tests/golden.py
  # The five machine-sensitive fixtures get their real check here: identical
  # to GOLDEN_REF when captured twice in THIS environment (G4b). Skipped
  # when the ref is unreachable (tarball checkouts, offline clones).
  if ! git rev-parse --verify --quiet "${GOLDEN_REF}^{commit}" >/dev/null 2>&1; then
    echo
    echo "SKIP: tests/env_drift.py ($GOLDEN_REF is not available here)"
  elif [ "$(git rev-parse "${GOLDEN_REF}^{commit}")" = "$(git rev-parse HEAD)" ]; then
    # A checkout sitting on the comparison ref itself: comparing a tree to
    # itself proves nothing, so there is nothing to run. env_drift fails on
    # this rather than passing vacuously; here it is just where a developer
    # on an up-to-date main lands, so say so and carry on.
    echo
    echo "SKIP: tests/env_drift.py ($GOLDEN_REF is this commit; use GOLDEN_REF=HEAD^1 to check it)"
  else
    run "$PYTHON" tests/env_drift.py "$GOLDEN_REF"
  fi
fi

# End-to-end optimizer behaviour.
run "$PYTHON" tests/validate.py
run "$PYTHON" tests/edge.py
run "$PYTHON" tests/backtest.py
run "$PYTHON" tests/stress.py
run "$PYTHON" tests/optimality.py

# The closed-loop simulation runs hundreds of solves and takes about a quarter
# of an hour, so it is opt-in: a test that slow would simply stop being run if
# it sat in the default path. Run it before a release, or after touching the
# optimizer or the learners.
if [ "${SLOW:-0}" = "1" ]; then
  run "$PYTHON" tests/rolling.py
else
  echo
  echo "SKIP: tests/rolling.py (set SLOW=1 to include the closed-loop simulation)"
fi

# Plan payloads, then the card that renders them, and how it reaches the page.
run "$PYTHON" tests/plan_view.py
run "$PYTHON" tests/frontend.py
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
