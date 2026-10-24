#!/bin/bash
# Runs every python closure script that reaches a LEN seam's module under the
# I1 probe hook; writes run.trace (seam outcome pairs) and rc.tsv (script, rc, s).
# Usage: bash dev/audit/rounds/round10/D14/sweep-I1/run_trace.sh   (from repo root)
S=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-$HOME/.local/state/hpo/venv-ci/bin/python}
: > "$S/run.trace"; : > "$S/rc.tsv"; mkdir -p "$S/logs"
SCRIPTS="block_duty guard_pins solar_alignment debug_collect plan_view wood_advisor manual_plan config_flow_steps validate finite_boundary features edge optimality"
for s in $SCRIPTS; do
  ( t0=$(date +%s)
    I1_TRACE="$S/run.trace" PYTHONPATH="$S/hook:tests/hastub" GATE_JOBS=1 OMP_NUM_THREADS=1 \
      "$PY" tests/$s.py > "$S/logs/$s.log" 2>&1
    rc=$?
    printf '%s\t%s\t%s\n' "$s" "$rc" "$(( $(date +%s)-t0 ))" >> "$S/rc.tsv" ) &
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do sleep 5; done
done
wait
echo done
