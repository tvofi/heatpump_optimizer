#!/bin/bash
# usage: mut.sh <runner> <line> <old> <new> <label>
cd ~/hpo-seats/1865-review/wt
F=custom_components/heatpump_optimizer/notifier.py
python3 - "$F" "$2" "$3" "$4" <<'PY' || { echo "MUTANT $5: APPLY-FAILED"; exit 1; }
import sys
f,ln,old,new=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(f).read().split('\n')
assert old in L[ln-1], (ln, L[ln-1])
L[ln-1]=L[ln-1].replace(old,new,1)
open(f,'w').write('\n'.join(L))
PY
out=$(PYTHONPATH=tests/hastub:custom_components:tests ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/$1 2>&1)
git checkout -q -- $F
fails=$(echo "$out" | grep -c '^  FAIL')
echo "MUTANT $5 [$1]: $( [ "$fails" -gt 0 ] && echo KILLED || echo SURVIVED ) fails=$fails :: $(echo "$out" | tail -1)"
echo "$out" | grep '^  FAIL' | cut -c1-140 | sed 's/^/    /'
