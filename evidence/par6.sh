#!/bin/bash
# par6: six pr_args.sh --self-test runs in parallel in worktree $1, label $2
W=/tmp/tmp.0yIqpWX7DG; cd $1
for i in 1 2 3 4 5 6; do ( HOME=$(mktemp -d) bash tools/audit/seat/pr_args.sh --self-test > $W/ev/par6-$2-$i.log 2>&1; echo $? > $W/ev/par6-$2-$i.rc ) & done; wait
red=0; for i in 1 2 3 4 5 6; do [ "$(cat $W/ev/par6-$2-$i.rc)" = 0 ] || red=$((red+1)); done
echo "RESULT par6 $2 $(git rev-parse HEAD) red=$red runs=6" | tee -a $W/ev/RESULT.txt
