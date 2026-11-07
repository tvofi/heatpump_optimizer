#!/bin/bash
# run2.sh name old new  -- in its own worktree /root/wt_<name>
cd /root/wt_$1 || exit 9
F=custom_components/heatpump_optimizer/coordinator.py
python3 - "$2" "$3" <<'PY' || { echo "MUT $1 APPLY-FAILED"; exit 1; }
import sys
f="custom_components/heatpump_optimizer/coordinator.py"
s=open(f).read(); old,new=sys.argv[1],sys.argv[2]
assert s.count(old)==1, (s.count(old), old)
open(f,"w").write(s.replace(old,new))
PY
git diff --stat
start=$(date +%s)
PYTHONPATH=tests/hastub timeout 1500 python3 tests/features.py > /root/ev/mut_$1.log 2>&1; rc=$?
git checkout -q -- $F
echo "MUT $1 rc=$rc $(( $(date +%s)-start ))s $(tail -1 /root/ev/mut_$1.log)"
grep -E "^  FAIL" /root/ev/mut_$1.log | head -8
