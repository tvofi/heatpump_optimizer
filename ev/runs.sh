#!/bin/bash
# runs.sh <script> <zone>
W=/tmp/claude-0/-home-user-heatpump-optimizer/9b51e75a-394a-5bd5-b6e6-c3cb127eaf72/scratchpad
s=$1; z=$2; l=$(basename $s .py)_$(echo $z|tr / _); cd $W/head
t=$(date +%s); HASTUB_TZ=$z TZ=$z PYTHONPATH=tests/hastub timeout 2400 python3 $s > $W/ev/other_$l.log 2>&1; rc=$?
echo "$s HASTUB_TZ=TZ=$z rc=$rc wall=$(( $(date +%s)-t ))s :: $(grep -E 'CHECKS (PASSED|FAILED)|PASSED|FAILED' $W/ev/other_$l.log | tail -1)" >> $W/ev/other_scripts.txt
gzip -f $W/ev/other_$l.log
