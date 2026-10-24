#!/bin/bash
# monitor.sh <run-dir|-> <held-pr-regex>: every 120 s touch merge.alive; stop on train end,
# a queue line not in <held>, or the window end (17:42Z).
D=/Users/timmalmstrom/hpo-orch/r10s5; R=$1; HELD=$2; END=1792777320
while :; do
  touch $D/merge.alive
  [ "$R" != - ] && [ -f $R/rc ] && { echo "TRAIN ENDED rc=$(cat $R/rc) $(date -u +%FT%TZ)"; tail -15 $R/train.log; exit 0; }
  new=$(grep -E '[0-9]' $D/merge-queue.txt | grep -vE "^(direct )?($HELD) ")
  [ -n "$new" ] && { echo "NEW QUEUE $(date -u +%FT%TZ)"; echo "$new"; [ "$R" != - ] && tail -5 $R/train.log; exit 0; }
  [ $(date +%s) -ge $END ] && { echo "WINDOW END $(date -u +%FT%TZ)"; [ "$R" != - ] && tail -15 $R/train.log; exit 0; }
  sleep 120
done
