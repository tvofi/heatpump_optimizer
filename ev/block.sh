#!/bin/bash
# run test block R11-OUTSIDE-HONEST-DHW-RUNS of tests/features.py in the tree at cwd
export PYTHONPATH=tests/hastub
python3 tools/audit/seat/features_block.py --emit-prelude /tmp/claude-0/mut/pre.$$ "R.section(\"R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed" "R.section(\"#3616 R11-OUTSIDE-ROOMS-P1" >/dev/null 2>&1 || { echo prelude-fail; exit 9; }
python3 tools/audit/seat/features_block.py --prelude "exec(open('/tmp/claude-0/mut/pre.$$').read())" "R.section(\"R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed" "R.section(\"#3616 R11-OUTSIDE-ROOMS-P1" > /tmp/claude-0/mut/block.$$.log 2>&1; rc=$?
grep -E "FAIL|PASSED|Error" /tmp/claude-0/mut/block.$$.log | head -5; exit $rc
