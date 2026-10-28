#!/bin/bash
# usage: mut.sh NAME 'python-replace-old' 'python-replace-new'
export PATH=/opt/hpo/venv-ci/bin:$PATH
name=$1; old=$2; new=$3
D=$(mktemp -d); git -C /tmp/rv-head archive HEAD | tar -x -C $D
F=$D/custom_components/heatpump_optimizer/config_flow.py
python3 - "$F" "$old" "$new" <<'PY'
import sys
p,o,n=sys.argv[1:]
s=open(p).read()
c=s.count(o)
assert c==1, f"count={c}"
open(p,'w').write(s.replace(o,n))
PY
[ $? -ne 0 ] && { echo "$name: APPLY FAILED"; exit 1; }
cd $D && PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py > $HOME/ev/mut_$name.txt 2>&1; rc=$?
echo "$name rc=$rc $(grep -E 'checks (PASSED|FAILED)' $HOME/ev/mut_$name.txt)"
grep '^  FAIL' $HOME/ev/mut_$name.txt | cut -c1-140 | head -8
rm -rf $D
