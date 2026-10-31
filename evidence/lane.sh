#!/bin/bash
# usage: lane.sh <lane> <mutant>...
L=$1; shift; W=$HOME/mut$L
cd /home/user/heatpump_optimizer && git worktree add -q --detach $W dfb981d7a0066c472ef408467a88630e77227f70 2>/dev/null
for m in "$@"; do
  cd $W && git checkout -q -- . && python3 $HOME/scripts/mutate.py $m > $HOME/ev/mut_$m.txt 2>&1 || { echo APPLY-FAILED >> $HOME/ev/mut_$m.txt; continue; }
  git diff >> $HOME/ev/mut_$m.txt
  PYTHONPATH=tests/hastub:custom_components:tests python3 -u tests/features.py > $HOME/ev/mut_${m}_run.txt 2>&1; echo "rc=$?" >> $HOME/ev/mut_${m}_run.txt
  { echo "--- FAIL lines"; grep -E "^\s*FAIL|FEATURE CHECKS" $HOME/ev/mut_${m}_run.txt; tail -1 $HOME/ev/mut_${m}_run.txt; } >> $HOME/ev/mut_$m.txt
  git checkout -q -- .
done
echo LANE-$L-DONE
