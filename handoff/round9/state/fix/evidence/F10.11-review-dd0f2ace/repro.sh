#!/bin/bash
S=/tmp/claude-0/-home-user/4734ca49-ed5f-572b-b86a-c35eb6d351c9/scratchpad
for side in main head; do
  for t in $side ${side}2; do
    ( cd $S/$t && start=$(date +%s); PYTHONPATH="$PWD/tests/hastub" taskset -c 0 /tmp/claude-0/-home-user/4734ca49-ed5f-572b-b86a-c35eb6d351c9/scratchpad/venv/bin/python tests/harness_headers.py > $S/repro_$t.log 2>&1; echo "rc=$? wall=$(( $(date +%s)-start ))s" >> $S/repro_$t.log ) &
  done
  wait
done
echo done
