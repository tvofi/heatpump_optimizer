#!/bin/bash
# usage: mut.sh <name> <file> <python-literal-old> <python-literal-new> <cmd...>
name=$1; f=$2; old=$3; new=$4; shift 4
cp "$f" /tmp/mut.bak
python3 - "$f" "$old" "$new" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1, ("count",s.count(o)); open(p,"w").write(s.replace(o,n))
PY
[ $? -ne 0 ] && { echo "MUTANT $name: NOT APPLIED"; cp /tmp/mut.bak "$f"; exit; }
out=$(timeout 200 "$@" 2>&1); rc=$?
cp /tmp/mut.bak "$f"
if [ $rc -ne 0 ]; then echo "MUTANT $name: KILLED rc=$rc :: $(echo "$out" | grep -m2 -E 'FAIL|Error' | tr '\n' ' ')"; else echo "MUTANT $name: SURVIVED"; fi
