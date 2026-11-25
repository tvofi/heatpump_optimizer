#!/bin/bash
# usage: harness_run.sh <tag> <path> [args...]  -- runs head's copy of <path> in base and head worktrees
W=/tmp/claude-0/-home-user-heatpump-optimizer/5c1af605-2a09-5abb-995c-8c5baf685cbe/scratchpad/wt
EV=/tmp/claude-0/-home-user-heatpump-optimizer/5c1af605-2a09-5abb-995c-8c5baf685cbe/scratchpad/ev/h2
tag=$1; p=$2; shift 2
for end in base head; do
  mkdir -p $(dirname $W/${end}2/$p); [ $end = base ] && cp $W/head2/$p $W/base2/$p
  (cd $W/${end}2 && echo "start $(date -u +%FT%TZ) sha1 $(git hash-object $p)" > $EV/${tag}_$end.log && OPENBLAS_CORETYPE=Haswell PYTHONPATH=tests/hastub timeout 2400 python3 $p "$@" >> $EV/${tag}_$end.log 2>&1; echo "rc $?" >> $EV/${tag}_$end.log)
done
