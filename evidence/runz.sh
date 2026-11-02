#!/bin/bash
# runz.sh <tree> <label> <HASTUB_TZ> [TZ]
tree=$1; label=$2; z=$3; tz=$4
out=/tmp/claude-0/-home-user-heatpump-optimizer/9b51e75a-394a-5bd5-b6e6-c3cb127eaf72/scratchpad/ev/features_${label}
cd "$tree"
s=$(date +%s)
if [ -n "$tz" ]; then export TZ=$tz; else unset TZ; fi
HASTUB_TZ=$z PYTHONPATH=tests/hastub python3 tests/features.py > $out.log 2>&1; rc=$?
{ echo "tree=$(git -C "$tree" rev-parse HEAD) dirty=$(git -C "$tree" status --porcelain | wc -l) HASTUB_TZ=$z TZ=${tz:-unset}"; grep -E '^\s*FAIL |FEATURE CHECKS' $out.log | grep -v 'planted' ; echo "rc=$rc wall=$(( $(date +%s)-s ))s"; } > $out.summary.txt
gzip -f $out.log
