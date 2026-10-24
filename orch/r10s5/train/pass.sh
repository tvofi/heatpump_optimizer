#!/bin/bash
# pass.sh <run-dir> [sleep-s]: sleep, touch merge.alive, print train state and new queue tail.
R=/Users/timmalmstrom/hpo-orch/r10s5; sleep ${2:-120}; touch $R/merge.alive
echo "$(date -u +%TZ) rc=$(cat $1/rc 2>/dev/null || echo live)"; grep -vE 'TRAIN HOLD' $1/train.log 2>/dev/null | tail -${3:-6}; echo "queue tail:"; tail -2 $R/merge-queue.txt
