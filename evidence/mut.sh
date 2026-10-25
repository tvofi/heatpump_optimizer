#!/bin/bash
# usage: mut.sh <W> <name> <python-expr-mutation-file-or-none>
W=$1; n=$2; H=042c60c8ad01d5f66858955c653ddd6a08c1e177
d=$W/m-$n; git -C /home/user/heatpump_optimizer worktree add -q --detach "$d" $H
if [ -n "$3" ]; then python3 -I "$3" "$d/tools/pr/prepr.sh" || { echo "PATTERN NOT FOUND $n" > $W/ev/mut-$n.txt; exit 1; }; fi
git -C "$d" diff > $W/ev/mut-$n.diff
cd "$d" && bash tools/pr/prepr.sh --self-test > $W/ev/mut-$n.log 2>&1; echo "rc=$? wall=$SECONDS s" >> $W/ev/mut-$n.log
