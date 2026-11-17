#!/bin/bash
# usage: attack.sh <name> <python edit snippet operating on p (plan dict)>; runs from F3
set -u
P=dev/audit/rounds/round11/PLAN
CMD="python3 tools/audit/seat/plan_audit.py objective-check --plan $P/PLAN.json --register dev/audit/rounds/round10/JUDGE.json"
C="git -c user.name=rev -c user.email=rev@example.invalid commit -q"
git checkout -q --detach 8d8e431cdd2b05367fbd3cc54b27136249671b5a
python3 - <<PY
import json, subprocess
sh=lambda *a: subprocess.check_output(a, text=True).strip()
p=json.load(open('$P/PLAN.json'))
$2
json.dump(p,open('$P/PLAN.json','w'),indent=1)
PY
git add -A -f . >/dev/null; $C -m "attack $1"; X=$(git rev-parse HEAD)
echo "## attack $1 at $X: --write"; $CMD --ref $X --write 2>&1 | grep -E "FAIL|PASS|refused|projection A|floor cost|Error" | cut -c1-300; 
git add -f $P/PROJECTION.json; $C -m "attack $1 projection" 2>/dev/null; X=$(git rev-parse HEAD)
echo "## attack $1 at $X: check"; $CMD --ref $X 2>&1 | grep -E "FAIL|PASS|refused|projection A|floor cost|Error" | cut -c1-300; echo "rc=${PIPESTATUS[0]}"
