#!/bin/bash
# usage: run_mutant.sh <id>   -- builds worktree, applies, runs features.py, records
id=$1; cd /home/user/heatpump_optimizer
d=$HOME/mut/$id; rm -rf $d; git worktree add -q --detach -f $d 6f742a33e5216932d4fb0f4583e09b137432ea9f
cd $d && python3 - "$id" <<'PY'
import sys; exec(open(sys.argv[0] if False else __import__('os').path.expanduser('~/rv/h/mutants.py')).read())
mid=sys.argv[1]; (_,f,o,n)=[m for m in M if m[0]==mid][0]
s=open(f).read(); assert s.count(o)==1,(mid,s.count(o)); open(f,'w').write(s.replace(o,n))
PY
[ $? -ne 0 ] && { echo "$id APPLY-FAILED" >> $HOME/rv/mutants.log; exit; }
PYTHONPATH=tests/hastub timeout 2400 python3 tests/features.py > $HOME/rv/mut_$id.txt 2>&1; rc=$?
echo "$id features rc=$rc $(grep -E 'FEATURE CHECKS' $HOME/rv/mut_$id.txt | tail -1) FAILS: $(grep -E '^ *FAIL' $HOME/rv/mut_$id.txt | head -3 | tr '\n' '|')" >> $HOME/rv/mutants.log
