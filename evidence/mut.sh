#!/bin/bash
# usage: mut.sh NAME FILE LINE OLD NEW
cd $HOME/wtm; export PYTHONPATH=tests/hastub
S=${S_:-"# D17-s3-51 and the P2 sweep's F14 seams"}; E=${E_:-"# --- #47 through the coordinator path"}
name=$1; f=$2; ln=$3; old=$4; new=$5
out=$HOME/ev/mutant-$name.txt
if [ "$name" != base ]; then
  python3 - "$f" "$ln" "$old" "$new" <<'PY'
import sys; f,ln,old,new=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(f).read().split("\n"); assert old in L[ln-1], L[ln-1]; L[ln-1]=L[ln-1].replace(old,new,1); open(f,"w").write("\n".join(L))
PY
  git diff -- "$f" > $out
fi
timeout 230 python3 tools/audit/seat/features_block.py --prelude "exec(open('${PRE:-/root/pre.py}').read())" "$S" "$E" >> $out 2>&1; rc=$?
echo "rc=$rc" >> $out
git checkout -q -- "$f" 2>/dev/null
echo "$name rc=$rc"; grep -E "FAIL|CHECKS" $out | head -5
