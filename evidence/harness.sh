#!/bin/bash
# usage: harness.sh <tree> <mode> ; own harness (reviewer's, not the finder's)
T=$1; M=$2; W=$(cat /tmp/W)
R=$(mktemp -d); cd $R; git init -q; git config user.email a@b; git config user.name a
printf 'def clamp(x, lo, hi):\n    if x < lo:\n        return lo\n    return min(x, hi)\n' > lib.py
printf 'from lib import clamp\nassert clamp(3,0,5)==3\n' > t.py
git add -A; git commit -qm i
cat > spec.json <<J
[{"name":"m","file":"lib.py","old":"return lo","new":"return hi"}]
J
python3 $T/tools/audit/seat/mutant_run.py --help 2>&1 | grep -E "spec|cmd" | head -3 >/dev/null
t0=$(date +%s)
( ulimit -u $(( $(ps -e|wc -l)+300 )); timeout 100 python3 $T/tools/audit/seat/mutant_run.py --root $R --spec spec.json --cmd "sh -c 'grep -q \"return lo\" lib.py && exit 0; python3 $W/ev/esc.py $M 150'" --fork-cap 32 --timeout 40 2>&1 | tail -3 )
echo "mode=$M secs=$(( $(date +%s)-t0 ))"
sleep 2; L=$(pgrep -f "esc.py $M"); echo "leftover=$(echo $L | wc -w)"; for p in $L; do kill -9 $p 2>/dev/null; done
