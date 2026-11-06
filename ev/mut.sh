#!/bin/bash
# usage: mut.sh <label> <python-replace-old> <python-replace-new>
src=/tmp/wt/tests/nightly_status.py; d=/tmp/mut/$1; mkdir -p $d
/tmp/venv-t/bin/python3 - "$src" "$d/nightly_status.py" "$2" "$3" <<'PY'
import sys; s=open(sys.argv[1]).read(); o,n=sys.argv[3],sys.argv[4]
assert s.count(o)==1, ("count", s.count(o), o); open(sys.argv[2],"w").write(s.replace(o,n))
PY
out=$(/tmp/venv-t/bin/python3 -I /tmp/h/ns_check.py $d 2>&1); rc=$?
echo "MUTANT $1 rc=$rc $( [ $rc -ne 0 ] && echo KILLED || echo SURVIVED ) :: $(echo "$out" | tail -2 | tr '\n' ' ' | cut -c1-300)"
