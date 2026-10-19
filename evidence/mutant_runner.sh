#!/bin/bash
# run.sh <name> <python-replace-old> <new>  : mutate cloud_relay.sh in wt, self-test, restore
F=/tmp/seat/rev2419/wt/tools/audit/seat/cloud_relay.sh
cp "$F" /tmp/seat/rev2419/mut/orig.sh
python3 - "$F" "$2" "$3" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read()
assert s.count(o)==1, ("count",s.count(o),o); open(p,'w').write(s.replace(o,n))
PY
[ $? = 0 ] || { echo "MUTANT $1: APPLY-FAILED"; exit; }
out=$(bash "$F" --self-test 2>&1); rc=$?
cp /tmp/seat/rev2419/mut/orig.sh "$F"
echo "MUTANT $1: rc=$rc $(echo "$out"|tail -1) :: $(echo "$out"|grep FAIL|sed 's/  FAIL //;s/ (rc.*//'|tr '\n' '|')"
