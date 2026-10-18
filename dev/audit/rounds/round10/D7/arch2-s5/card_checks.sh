#!/usr/bin/env bash
# ARCH2-s5: the card's own instruments over the WORKING TREE's card, against a ref.
#
#   bash dev/audit/rounds/round10/D7/arch2-s5/card_checks.sh [REF]     (default origin/main)
#
# Runs, in order: tests/plan_view.py (the payload, into a private temp root),
# tests/card_drift.mjs REF (40 rendered states, byte for byte), this seat's
# card_pages_drift.mjs REF (the Health, Savings and Advisor-inbox pages and the
# deep links, which card_drift does not render), and tests/card.mjs (the
# behaviour suite). Prints one RESULT line per instrument. Run from the repo root.
set -u
REF=${1:-origin/main}
DIR=dev/audit/rounds/round10/D7/arch2-s5
ROOT=$(mktemp -d "${TMPDIR:-/tmp}/arch2-s5.XXXXXX")
export HPO_PLANDATA="$ROOT/plandata.json"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=${PY:-python3}
echo "logs: $ROOT"
PYTHONPATH=tests/hastub "$PY" tests/plan_view.py > "$ROOT/plan_view.log" 2>&1
echo "RESULT plan_view_rc=$?"
node tests/card_drift.mjs "$REF" > "$ROOT/card_drift.log" 2>&1
rc=$?
echo "RESULT card_drift_rc=$rc $(tail -1 "$ROOT/card_drift.log")"
node "$DIR/card_pages_drift.mjs" "$REF" > "$ROOT/pages.log" 2>&1
rc=$?
echo "RESULT card_pages_drift_rc=$rc $(tail -1 "$ROOT/pages.log")"
node tests/card.mjs > "$ROOT/card.log" 2>&1
rc=$?
echo "RESULT card_mjs_rc=$rc $(tail -1 "$ROOT/card.log")"
