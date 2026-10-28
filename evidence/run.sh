#!/bin/bash
# usage: run.sh name file old new script
set -u
N=$1; F=$2; OLD=$3; NEW=$4; S=$5
D=/home/user/mut/$N; rm -rf $D; mkdir -p $D
git -C /home/user/rev archive HEAD | tar -x -C $D
if [ "$OLD" != "-" ]; then
  /opt/hpo/venv-ci/bin/python3 - "$D/$F" "$OLD" "$NEW" <<'PY'
import sys
p,o,n=sys.argv[1:]
s=open(p).read(); c=s.count(o)
assert c==1, f"site count {c}"
open(p,'w').write(s.replace(o,n))
PY
fi
cd $D && PYTHONPATH=tests/hastub timeout 3000 /opt/hpo/venv-ci/bin/python3 $S > /home/user/mut/$N.log 2>&1; echo "rc=$?" >> /home/user/mut/$N.log
