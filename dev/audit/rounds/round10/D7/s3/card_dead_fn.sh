#!/bin/sh
# Runs card_dead_fn.mjs with a private HPO_PLANDATA. From the repo root:
#   PYTHONPATH=tests/hastub sh dev/audit/rounds/round10/D7/s3/card_dead_fn.sh
set -e
T=$(mktemp -d)
export HPO_PLANDATA="$T/plandata.json"
${PY:-python3} tests/plan_view.py >/dev/null
node dev/audit/rounds/round10/D7/s3/card_dead_fn.mjs
