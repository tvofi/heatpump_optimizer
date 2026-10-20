#!/bin/bash
# usage: mut.sh name ; builds worktree $W/m-name with a sed mutation of update_pr.sh, runs pr_args self-test
W=$1; n=$2; d=$W/m-$n
git -C /home/user/heatpump_optimizer worktree add -q --detach $d 89f329f6 2>/dev/null
U=$d/tools/audit/seat/update_pr.sh
case $n in
  fg) sed -i '118s/ & PUSHP=\$!$/ || pr_push_failed $WT.log/; 119d' $U ;;
  holdgrp) sed -i '48s/; os.setpgid(0, 0)$//' $U ;;
  nokillpg) sed -i '57s/os.killpg(p, signal.SIGTERM)/pass/' $U ;;
  zombie) sed -i '54s/ and not st.startswith("Z")//' $U ;;
  whiletrue) sed -i '62s/while os.getppid() == p and not stop:/while not stop:/' $U ;;
  noack) sed -i '78s/.*/  :/' $U ;;
esac
git -C $d diff > $W/ev/mut-$n.diff
( cd $d && bash tools/audit/seat/pr_args.sh --self-test ) > $W/ev/mut-$n.txt 2>&1; echo rc=$? >> $W/ev/mut-$n.txt
