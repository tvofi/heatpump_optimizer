#!/bin/bash
# run_mut.sh <id>: apply reviewer mutant <id> in its own detached worktree, run the self-test, record rc and failing checks.
S=<scratch>/rev-2305
id=$1; W=$S/mw2/$id
git -C $S/wt worktree add -q --detach $W e01e66f0d00bdc2acfcdef725b2d4c53ff0455ac 2>/dev/null || git -C $W checkout -q -f e01e66f0d00bdc2acfcdef725b2d4c53ff0455ac
cd $W && python3 - "$id" <<'PY' || { echo "$id APPLY-FAILED" > $S/ev2/mut-$id.txt; exit; }
import sys; sys.path.insert(0, sys.argv[0] and "<scratch>/rev-2305")
from mutants import M
i,f,o,n = next(m for m in M if m[0]==sys.argv[1])
p="tools/audit/seat/"+f; s=open(p).read(); assert s.count(o)>=1
open(p,"w").write(s.replace(o,n,1))
PY
git -C $W diff --stat | tail -1 > $S/ev2/mut-$id.txt
python3 tools/audit/seat/merge_train.py --self-test > $S/ev2/mut-$id.log 2>&1; rc=$?
echo "RESULT mutant $id rc=$rc $(tail -1 $S/ev2/mut-$id.log)" >> $S/ev2/mut-$id.txt
grep -E '^\s*FAIL' $S/ev2/mut-$id.log | head -6 >> $S/ev2/mut-$id.txt
