#!/bin/bash
# lane.sh <worktree> <mutant>...  : apply each mutant alone, run its driver, record summary
S=/tmp/claude-0/-home-user-heatpump-optimizer/03dae863-1169-5933-8977-305f1796f360/scratchpad
P=/opt/hpo/venv-ci/bin/python
W=$1; shift
cd $W
for m in "$@"; do
  git checkout -q -- custom_components
  python3 $S/tools/mut.py $m $W > $S/ev/mut-$m.log 2>&1 || { echo "$m APPLY-FAILED" >> $S/ev/mutants.txt; continue; }
  git diff -- custom_components > $S/ev/mut-$m.diff
  case $m in
    C*) node tests/card.mjs >> $S/ev/mut-$m.log 2>&1; rc=$? ;;
    *) PYTHONPATH=tests/hastub $P tests/features.py >> $S/ev/mut-$m.log 2>&1; rc=$? ;;
  esac
  summ=$(grep -E 'CHECK\(S\)? (FAILED|PASSED)|CHECKS (FAILED|PASSED)|Traceback|Error:' $S/ev/mut-$m.log | tail -2 | tr '\n' ' ')
  echo "$m rc=$rc $summ" >> $S/ev/mutants.txt
done
git checkout -q -- custom_components
echo "LANE-DONE $W" >> $S/ev/mutants.txt
