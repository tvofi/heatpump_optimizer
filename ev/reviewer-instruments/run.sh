#!/bin/bash
# run.sh <label> <kind:r1|r2|own> <name>
W=$(cat /tmp/claude-0/W); F=/tmp/claude-0/finder; S=/tmp/claude-0/mut; d=$S/$1; rm -rf $d; mkdir -p $d
cp -r /tmp/claude-0/wt/tests /tmp/claude-0/wt/.gitattributes $d/ 2>/dev/null; mkdir -p $d/custom_components; cp -r /tmp/claude-0/wt/custom_components/heatpump_optimizer $d/custom_components/
case $2 in r1) python3 $F/r1/mut.py $3 $d/tests/env_drift.py || { echo "RESULT $1 NO-ANCHOR"; exit; } ;; r2) python3 $F/r2/plant.py $3 $d/tests/env_drift.py || { echo "RESULT $1 NO-ANCHOR"; exit; } ;; own) python3 $S/own.py $3 $d/tests/env_drift.py || { echo "RESULT $1 NO-ANCHOR"; exit; } ;; none) ;; esac
out=$(python3 $F/r1/cmrun.py $d 2>&1); rc=$?
echo "RESULT $1 cm_rc=$rc fails=$(echo "$out" | grep -c FAIL) last=$(echo "$out" | tail -1)"; echo "$out" | grep FAIL | head -3 | cut -c1-200
