#!/bin/bash
# Re-drive the remaining pins PR #2873 adds, fastest drivers first.
# The one features.py row was stopped after 28 min under contention (three
# concurrent features.py runs from other seats); it is re-attempted last.
set -u
cd /Users/timmalmstrom/hpo-seats/r10s6/review-2873-r1/wt || exit 1
OUT=/Users/timmalmstrom/hpo-seats/r10s6/review-2873-r1/evidence
mkdir -p "$OUT/mutants"
export PYTHONDONTWRITEBYTECODE=1
ANCHORS=(
 "custom_components/heatpump_optimizer/coordinator.py:plan_stale_limit_minutes CLAMP_DROP 8ee35b1a|tests/structure.py"
 "custom_components/heatpump_optimizer/coordinator.py:plan_stale_limit_minutes RETURN_DEL 8ee35b1a|tests/structure.py"
 "custom_components/heatpump_optimizer/coordinator.py:plan_stale_limit_minutes GUARD_OFF 482b8551|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/debugger.py:DebugCollector.as_dict BOOLOP 81d62bfa|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/debugger.py:DebugCollector.as_dict GUARD_OFF 81d62bfa|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/diagnostics.py:_inputs_at GUARD_OFF 305ddbe3|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/diagnostics.py:_inputs_at GUARD_OFF 4a6254b3|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/diagnostics.py:_inputs_at GUARD_OFF 79397f15|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/diagnostics.py:_inputs_at RETURN_DEL 02e1c03c|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/diagnostics.py:_plan_summary CMP_BOUND 7abd2715|tests/debug_collect.py"
 "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._plan_is_stale RETURN_DEL 1e075bcb|tests/features.py"
)
for row in "${ANCHORS[@]}"; do
  anchor=${row%|*}; driver=${row#*|}
  safe=$(echo "$row" | tr -c 'A-Za-z0-9._-' '_')
  echo "===== [$anchor]  driver=$driver" >> "$OUT/pins-summary2.txt"
  timeout 900 python3 tests/mutation_table.py --anchor "$anchor" --scripts "$driver" --jobs 1 \
    > "$OUT/mutants/$safe.log" 2>&1
  rc=$?
  echo "rc=$rc" >> "$OUT/pins-summary2.txt"
  grep -E "PIN RE-VERIFICATION|killed by|survived|SURVIVED|baseline .*rc=|NOT REPRODUCED|TIMEOUT|timed out" \
    "$OUT/mutants/$safe.log" | tail -6 >> "$OUT/pins-summary2.txt"
done
echo DONE >> "$OUT/pins-summary2.txt"
