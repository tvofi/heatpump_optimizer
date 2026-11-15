#!/bin/bash
# usage: run.sh <name> <file> <python-replace-old> <new> <test: train|pr>
name=$1 file=$2 old=$3 new=$4 t=$5; W=$(cat $HOME/W.txt)
d=$HOME/mut/wt-$name; cd /home/user/heatpump_optimizer; git worktree add -q --detach $d 419fd6d2c455601cebe473bd1b8ec77e0090daa0 2>/dev/null
cd $d && python3 - "$file" "$old" "$new" <<'P' || { echo "$name: PATCH-MISS" >> $W/ev/mutants.txt; exit; }
import sys; f,o,n=sys.argv[1:4]; s=open(f).read(); c=s.count(o); assert c==1, c; open(f,"w").write(s.replace(o,n))
P
git diff --stat | tail -1 > $W/ev/mut-$name.txt; git diff >> $W/ev/mut-$name.txt
if [ $t = train ]; then python3 -I tools/audit/seat/merge_train.py --self-test > $W/ev/mut-$name.log 2>&1; else bash tools/audit/seat/merge_pr.sh --self-test > $W/ev/mut-$name.log 2>&1; fi
echo "$name rc=$? $(grep -E 'self-test: [0-9]+ checks' $W/ev/mut-$name.log | tail -1)" >> $W/ev/mutants.txt
grep -E '^\s*FAIL' $W/ev/mut-$name.log | head -8 | sed "s/^/  $name /" >> $W/ev/mutants.txt
