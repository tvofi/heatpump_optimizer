#!/bin/bash
# usage: run_mutant.sh ID ; runs in its own worktree, writes $W/ev/mut_ID.txt
set -u
W=$(cat /tmp/claude-0/W); ID=$1; H=21eeb5b2325bf6a99f2a282f2e38bafbee44ab70
source /etc/profile.d/hpo-toolchain.sh
D=$W/mt/$ID; rm -rf $D; git -C /home/user/heatpump_optimizer worktree add -q --detach $D $H
OUT=$W/ev/mut_$ID.txt
TEST=$(cd $D && python3 - "$ID" "$W/tools" <<'PY'
import sys; sys.path.insert(0, sys.argv[2]); from mutants import M
for i,f,old,new,t in M:
    if i==sys.argv[1]:
        s=open(f).read(); n=s.count(old)
        assert n==1, f"{i}: {n} matches"
        open(f,"w").write(s.replace(old,new)); print(t)
PY
) || { echo "APPLY FAILED" > $OUT; exit 1; }
cd $D; { echo "mutant $ID at $H"; git diff; } > $OUT
case $TEST in
 card) HPO_PLANDATA=$(ls /tmp/plandata-*.json | head -1) node tests/card.mjs > $W/mt/$ID.log 2>&1; echo "card rc=$?" >> $OUT;;
 features) PYTHONPATH=tests/hastub python3 tests/features.py > $W/mt/$ID.log 2>&1; echo "features rc=$?" >> $OUT;;
 features+fb) PYTHONPATH=tests/hastub python3 tests/features.py > $W/mt/$ID.log 2>&1; echo "features rc=$?" >> $OUT
   PYTHONPATH=tests/hastub python3 tests/finite_boundary.py > $W/mt/$ID.fb.log 2>&1; echo "finite_boundary rc=$?" >> $OUT
   grep -E "^ *FAIL|FAILED" $W/mt/$ID.fb.log | head -20 >> $OUT;;
esac
grep -E "^ *FAIL|FAILED|PASSED" $W/mt/$ID.log | head -30 >> $OUT
