#!/bin/bash
# usage: mutant.sh <name> <python-replacement-spec: old|||new>
S=/Users/timmalmstrom/hpo-seats/r9rev-2111b/scratch
F=$S/tools/audit/seat/record_row.py
NAME=$1; OLD=$2; NEW=$3
cp /Users/timmalmstrom/hpo-seats/r9rev-2111b/wt/tools/audit/seat/record_row.py $F
~/.local/state/hpo/venv-ci/bin/python3 - "$F" "$OLD" "$NEW" <<'PY'
import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
if s.count(old) != 1:
    print(f"ANCHOR-ERROR: {s.count(old)} matches"); sys.exit(9)
open(p, "w").write(s.replace(old, new))
PY
[ $? -ne 0 ] && exit 9
cd $S
OUT=$(~/.local/state/hpo/venv-ci/bin/python3 -I tools/audit/seat/record_row.py --self-test 2>&1)
RC=$?
FAILED=$(printf '%s\n' "$OUT" | grep -c "FAILED")
PASSED=$(printf '%s\n' "$OUT" | grep -c "ok:")
printf 'RESULT %s: rc=%d failed-lines=%d\n' "$NAME" "$RC" "$FAILED"
printf '%s\n' "$OUT" | grep -i "fail" | head -8
cp /Users/timmalmstrom/hpo-seats/r9rev-2111b/wt/tools/audit/seat/record_row.py $F
