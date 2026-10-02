#!/bin/bash
# usage: mut.sh NAME FILE PYEXPR  -- applies a python str.replace (old,new) to FILE under a copy of tests/hastub
S=/tmp/claude-0/-home-user/3464227d-12bc-5805-9927-bb99eae1da65/scratchpad
name=$1; file=$2; old=$3; new=$4
d=$S/mut/$name; rm -rf $d; mkdir -p $d; cp -r $S/head/tests/hastub $d/hastub
$S/vci/bin/python - "$d/hastub/$file" "$old" "$new" <<'PY'
import sys; p,o,n=sys.argv[1:]; t=open(p).read()
assert t.count(o)==1, (o, t.count(o)); open(p,'w').write(t.replace(o,n))
PY
cd $S/head
PYTHONPATH=$d/hastub GOLDEN_MODE=drift $S/vci/bin/python tests/_p11_block.py > $d/block.log 2>&1; b=$?
PYTHONPATH=$d/hastub $S/vci/bin/python tests/ha_contract.py > $d/contract.log 2>&1; c=$?
echo "$name block rc=$b fails=$(grep -c 'FAIL' $d/block.log) | contract rc=$c fails=$(grep -c 'FAIL' $d/contract.log)"
grep 'FAIL' $d/block.log $d/contract.log | sed 's|.*/mut/||' | head -12
