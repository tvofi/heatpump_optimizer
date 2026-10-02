#!/bin/bash
# For each first-parent solver-touching merge: count production calls at the merge and at its first parent.
W=/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/rca-perf-work
R=/home/claude/heatpump_optimizer
cd $R
for m in $(git log --first-parent --format='%h' v6.5.0..1936d5ca -- custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/thermal_model.py custom_components/heatpump_optimizer/tariff.py custom_components/heatpump_optimizer/dhw_schedule.py custom_components/heatpump_optimizer/mixing_valve.py); do
  for rev in $m $(git rev-parse --short $m^1); do
    out=$W/hist/$rev.txt; [ -s $out ] && continue
    wt=$W/hist/wt-$rev; git worktree add --detach $wt $rev >/dev/null 2>&1
    (cd $wt && PYTHONPATH=tests/hastub timeout 900 /home/claude/venv314/bin/python $W/rows2.py winter/1z/dhw winter/2z/space winter/tariff > $out 2>&1)
    git worktree remove --force $wt
  done
  echo "$m $(git rev-parse --short $m^1)" >> $W/hist/pairs.txt
done
echo DONE >> $W/hist/pairs.txt
