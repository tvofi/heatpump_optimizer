#!/bin/bash
# run_mut.sh <id>: apply reviewer mutant <id> in its own detached worktree, run the self-test, record rc and failing checks.
S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2305
id=$1; W=$S/mw/$id
git -C $S/wt worktree add -q --detach $W 3c807ab5bb62d2d4da36003d2787437d2b012b4b 2>/dev/null || git -C $W checkout -q -f 3c807ab5bb62d2d4da36003d2787437d2b012b4b
cd $W && python3 - "$id" <<'PY' || { echo "$id APPLY-FAILED" > $S/ev/mut-$id.txt; exit; }
import sys; sys.path.insert(0, sys.argv[0] and "/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2305")
from mutants import M
i,f,o,n = next(m for m in M if m[0]==sys.argv[1])
p="tools/audit/seat/"+f; s=open(p).read(); assert s.count(o)>=1
open(p,"w").write(s.replace(o,n,1))
PY
git -C $W diff --stat | tail -1 > $S/ev/mut-$id.txt
python3 tools/audit/seat/merge_train.py --self-test > $S/ev/mut-$id.log 2>&1; rc=$?
echo "RESULT mutant $id rc=$rc $(tail -1 $S/ev/mut-$id.log)" >> $S/ev/mut-$id.txt
grep -E '^\s*FAIL' $S/ev/mut-$id.log | head -6 >> $S/ev/mut-$id.txt
