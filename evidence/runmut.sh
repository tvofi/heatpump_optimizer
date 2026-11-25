#!/bin/bash
# usage: runmut.sh NAME  -> runs in its own worktree from 7748bdc2
S=/tmp/claude-0/-home-user-heatpump-optimizer/234cf9c4-0333-58b3-abd8-cf5f256e633f/scratchpad
N=$1; W=/home/user/wt-mut-$N; H=7748bdc269efb9758d85b4ee81130a4f60534948
cd /home/user/heatpump_optimizer && git worktree add -q --detach $W $H 2>/dev/null
cd $W && git checkout -q -- . && python3 -I - "$N" <<'PY' || { echo "APPLY-FAIL $N"; exit 9; }
import sys; exec(open("/tmp/claude-0/-home-user-heatpump-optimizer/234cf9c4-0333-58b3-abd8-cf5f256e633f/scratchpad/mutants.py").read())
f,o,n=M[sys.argv[1]]; s=open(f).read(); c=s.count(o)
assert c==1,(sys.argv[1],c); open(f,"w").write(s.replace(o,n)); print("applied",sys.argv[1],f)
PY
git diff --stat | tail -1
PYTHONDONTWRITEBYTECODE=1 timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/prelude.py').read())" 'R.section("R11-SEAM-learners: the one freeze predicate")' > $S/mut_$N.log 2>&1; rc=$?
echo "MUT $N rc=$rc $(grep -c '^ *FAIL\|FAIL:' $S/mut_$N.log) $(grep -E 'FEATURES BLOCK|FAILED' $S/mut_$N.log | tail -1)"
