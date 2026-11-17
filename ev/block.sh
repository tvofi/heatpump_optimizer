#!/bin/bash
# usage: block.sh <worktree>  -> runs the COP block, prints summary + first FAIL
S=/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad
cd "$1" || exit 9
START='R.section("COP learner duty floor keys on the modulation floor (live v6.7.17)")'
END='R.section("R10-COP-GATE (#2262)'
PYTHONPATH=tests/hastub timeout 900 python3 /home/user/heatpump_optimizer/tools/audit/seat/features_block.py --prelude "exec(open('$S/prelude.py').read())" "$START" "$END" > $S/blk.$$ 2>&1; rc=$?
echo "rc=$rc"; grep -m3 -E "^  FAIL|^FAIL|Traceback|^[A-Za-z]*Error" $S/blk.$$ | cut -c1-200; tail -2 $S/blk.$$ | cut -c1-200
