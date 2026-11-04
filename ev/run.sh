#!/bin/bash
# usage: run.sh <name> ; applies mutant in a fresh worktree of the head and runs features.py
set -u
name=$1; W=$(cat ~/W.txt)
d=$HOME/mutwt/$name; rm -rf $d
git -C /home/user/heatpump_optimizer worktree add -q --detach $d af8ff29be58edf8c15eb146c9d9432be60899e23
python3 - "$name" "$d" <<'PY'
import sys; sys.path.insert(0, '/root/mut'); from mutants import M
name, d = sys.argv[1:]
for n,f,o,new in M:
    if n==name:
        p=f"{d}/custom_components/heatpump_optimizer/{f}"; s=open(p).read()
        assert s.count(o)==1, (n, s.count(o)); open(p,'w').write(s.replace(o,new)); print("applied",n)
PY
cd $d && PYTHONPATH=$d/tests/hastub python3 tests/features.py > $W/ev/mut_$name.log 2>&1; rc=$?
echo "MUTANT $name rc=$rc $(grep -E 'FEATURE CHECKS' $W/ev/mut_$name.log | tail -1)"
cd /; git -C /home/user/heatpump_optimizer worktree remove --force $d
