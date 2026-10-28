#!/bin/bash
W=$1; m=$2
cd $W; git checkout -q -- custom_components
[ "$m" != head ] && python3 /tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad/tools/mut.py $m $W
for t in entities finite_boundary; do PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/$t.py > /tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad/ev/c2-$m-$t.log 2>&1; echo "$m $t rc=$? $(grep -E 'CHECKS? (FAILED|PASSED)' /tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad/ev/c2-$m-$t.log | tail -1)" >> /tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad/ev/closure2.txt; done
git checkout -q -- custom_components
echo "DONE $m" >> /tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad/ev/closure2.txt
