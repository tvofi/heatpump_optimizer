#!/bin/bash
# usage: run.sh label 'old' 'new'  -- applies to a copy of the head worktree file, runs --self-test
set -u
W=$HOME/mwt; F=$W/tools/ci/selftest_scope.py
cp $HOME/wt/tools/ci/selftest_scope.py "$F"
python3 - "$F" "$2" "$3" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); c=s.count(o)
assert c==1, f"anchor count {c}"; open(p,'w').write(s.replace(o,n))
PY
[ $? -ne 0 ] && { echo "NOANCHOR $1"; exit; }
out=$(cd $W && timeout 200 python3 -I tools/ci/selftest_scope.py --self-test 2>&1 | tail -1)
case "$out" in *" 0 failed"*) echo "SURVIVED $1 :: $out";; *) echo "KILLED $1 :: $out";; esac
cp $HOME/wt/tools/ci/selftest_scope.py "$F"
