#!/bin/bash
# usage: run.sh NAME FILE PYTHON-REPLACE-OLD PYTHON-REPLACE-NEW
set -u
N=$1; F=${2:-}; OLD=${3:-}; NEW=${4:-}
D="$SCRATCH"/$N; rm -rf $D; mkdir -p $D
git -C "$REPO" archive 6f41ef788f8e2c0fb814f7ed4aab255f391e617b | tar -x -C $D
cd $D
if [ -n "$F" ]; then
  "$PY" - "$F" "$OLD" "$NEW" <<'PY' || { echo "APPLY FAILED" > ../$N.log; exit 2; }
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); c=s.count(o)
assert c==1, f"count {c}"; open(f,'w').write(s.replace(o,n))
PY
fi
PYTHONPATH=tests/hastub:custom_components:tests timeout 5400 "$PY" tests/features.py > ../$N.log 2>&1
echo "rc=$?" >> ../$N.log
