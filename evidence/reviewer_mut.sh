#!/bin/bash
# usage: mut.sh <file> <old> <new> <label> <runner>
f=$1; old=$2; new=$3; label=$4; shift 4
cd <W>/wt
python3 - "$f" "$old" "$new" <<'PY'
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); c=s.count(o); assert c==1, (o,c); open(f,'w').write(s.replace(o,n))
PY
out=$("$@" 2>&1 | tail -15)
git checkout -q -- "$f"
echo "== MUTANT $label"; echo "$out" | grep -E "RESULT grid|Error|VIOL|FAIL" | head -6
