#!/bin/bash
# usage: mut.sh <name> <file> <python-literal-old> <python-literal-new>; applies one mutant, runs block.sh, restores
W=/tmp/tmp.UkxZ98NRBC; cd $W/mut
python3 - "$2" "$3" "$4" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1,(p,o,s.count(o)); open(p,'w').write(s.replace(o,n))
PY
bash $W/ev/block.sh > $W/ev/mut_$1.log 2>&1; echo "rc=$?" >> $W/ev/mut_$1.log
git checkout -q -- .
echo "$1: $(grep -c '^  FAIL' $W/ev/mut_$1.log) FAIL; $(tail -2 $W/ev/mut_$1.log | tr '\n' ' ')"
grep '^  FAIL' $W/ev/mut_$1.log | head -3
