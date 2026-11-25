#!/bin/bash
# usage: mut.sh NAME FILE LINE OLD NEW  (NAME=base runs unmutated)
cd $HOME/wtm; export PYTHONPATH=$PWD/tests/hastub
name=$1; f=$2; ln=$3; old=$4; new=$5
out=$HOME/ev/mutant-$name.txt; : > $out
if [ "$name" != base ]; then
  python3 - "$f" "$ln" "$old" "$new" <<'PY' || exit 9
import sys; f,ln,old,new=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(f).read().split("\n"); assert old in L[ln-1], L[ln-1]; L[ln-1]=L[ln-1].replace(old,new,1); open(f,"w").write("\n".join(L))
PY
  git diff -- "$f" > $out
fi
python3 tests/features.py > $HOME/ev/full-$name.log 2>&1; rc=$?
grep -E 'FAIL' $HOME/ev/full-$name.log | head -20 >> $out; tail -3 $HOME/ev/full-$name.log >> $out
echo "rc=$rc" >> $out
git checkout -q -- "$f" 2>/dev/null
echo "$name rc=$rc fails=$(grep -c FAIL $HOME/ev/full-$name.log)"
