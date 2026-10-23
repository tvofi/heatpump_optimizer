#!/bin/bash
# usage: mut.sh NAME FILE PYOLD PYNEW
cd /tmp/fr-2675
export PATH=/tmp/fr-2675/tools/audit/seat/shims:$PATH
python3 - "$2" "$3" "$4" <<'P' || exit 3
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); c=s.count(o)
assert c==1, f"count={c}"; open(f,"w").write(s.replace(o,n))
P
out=$(PYTHONPATH=.:tests:tests/hastub:custom_components python3 tests/_fr_ls_block.py 2>&1)
git checkout -q -- "$2"
echo "RESULT mutant=$1 $(echo "$out" | grep -cE '^\s*FAIL') fails; $(echo "$out" | grep -E 'CHECKS (PASSED|FAILED)|Error:' | tail -1)"
echo "$out" | grep -E '^\s*FAIL' | cut -c1-150
