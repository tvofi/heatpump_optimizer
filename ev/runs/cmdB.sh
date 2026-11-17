#!/bin/bash
# block A with the one pre-existing block-only FAIL tolerated; any other FAIL / traceback fails
export PYTHONPATH=tests/hastub:custom_components:tests
out=$(mktemp)
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/root/ev-runs/prelude2.py").read())' 'R.section("R11-OUTSIDE-HONEST-DHW-RUNS' 'R.section("#3616 R11-OUTSIDE-ROOMS-P1' > $out 2>&1
rc=$?
grep -q "Traceback" $out && { grep "FAIL\|Error" $out | head -3; exit 9; }
bad=$(grep "^  FAIL" $out | grep -v "unengaged solve stops short of the cap")
if [ -n "$bad" ]; then echo "$bad" | cut -c1-250; exit 1; fi
grep -c "^  ok" $out
exit 0
