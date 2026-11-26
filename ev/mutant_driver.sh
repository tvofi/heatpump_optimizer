#!/bin/bash
# targeted mutants on the shared entry rule; each runs tests/features.py from a scratch worktree
set -u
R=/home/user/heatpump_optimizer; H=4ab51be4391657b622ad008c6fb4629846bf39c4
W=$(cat $HOME/W); OUT=$W/ev/mutants.txt; : > $OUT
WT=$HOME/mutwt; rm -rf $WT; git -C $R worktree add -q --detach $WT $H
cd $WT
DL=custom_components/heatpump_optimizer/duty_legs.py
DS=custom_components/heatpump_optimizer/duty_switch.py
OP=custom_components/heatpump_optimizer/optimizer.py
mut() { # name file python-replacement-old python-replacement-new
  name=$1 f=$2
  python3 - "$f" "$3" "$4" <<'PY' || { echo "$name: APPLY-FAILED" >> $OUT; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1,(p,o); open(p,'w').write(s.replace(o,n))
PY
  start=$(date +%s)
  PYTHONPATH=tests/hastub:custom_components:tests timeout 3000 python3 tests/features.py > $HOME/mut/$name.log 2>&1; rc=$?
  fails=$(grep -c "FAIL" $HOME/mut/$name.log)
  echo "$name: rc=$rc FAIL-lines=$fails secs=$(( $(date +%s)-start )) $(grep -m3 'FAIL' $HOME/mut/$name.log | cut -c1-200 | tr '\n' '|')" >> $OUT
  git checkout -q -- .
}
mut BASELINE $DL "def entry_rule" "def entry_rule"
mut M1_heat_min_dropped $DL "heat_min=leg_minimum(cfg.mode_leg_heat_min_minutes)" "heat_min=0.0"
mut M2_dhw_min_dropped $DL "dhw_min=leg_minimum(cfg.mode_leg_dhw_min_minutes)" "dhw_min=0.0"
mut M3_before_dropped $DL "dhw_min=leg_minimum(cfg.mode_leg_dhw_min_minutes), before=before)" "dhw_min=leg_minimum(cfg.mode_leg_dhw_min_minutes))"
mut M4_planner_before_idle $OP "opt.config, opt.config.duty_leg_before)" "opt.config, duty_legs.IDLE)"
mut M5_arbiter_before_idle $DS "entry_rule(split, cfg, rec.solve_before)" "entry_rule(split, cfg, duty_legs.IDLE)"
mut M6_planner_bypass $OP "return duty_legs.entry_rule(duty_legs.leg_rule(" "return (lambda r, c, b: r)(duty_legs.leg_rule("
mut M7_arbiter_bypass $DS "return duty_legs.entry_rule(split, cfg, rec.solve_before)" "return split"
echo DONE >> $OUT
cd $R; git worktree remove --force $WT
