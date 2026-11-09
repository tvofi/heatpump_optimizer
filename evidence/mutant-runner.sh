#!/bin/bash
# usage: run.sh <name> <python-replace-old> <python-replace-new>
cd $HOME/mut/wt
F=custom_components/heatpump_optimizer/optimizer.py
git checkout -q -- $F
if [ "$1" != head ]; then
python3 - "$F" "$2" "$3" <<'PY'
import sys
p,o,n=sys.argv[1:4]
s=open(p).read(); assert s.count(o)==1,(o,s.count(o)); open(p,'w').write(s.replace(o,n))
PY
fi
git diff --stat | tail -1
PYTHONPATH=tests/hastub timeout 300 python3 tools/audit/seat/features_block.py --prelude 'from datetime import datetime as _SavDT' --prelude 'import types as _sw_types' "# Item 1: the settlement books the plan's thermostat baseline" "# The start's settlement, at its limits" > $HOME/mut/$1.log 2>&1
rc=$?
echo "RESULT mutant=$1 rc=$rc $(grep -c 'FAIL' $HOME/mut/$1.log) FAIL-lines"
grep -E 'FAIL' $HOME/mut/$1.log | head -5
git checkout -q -- $F
