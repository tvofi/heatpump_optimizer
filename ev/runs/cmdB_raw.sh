#!/bin/bash
# block A with the one pre-existing block-only FAIL tolerated; any other FAIL / traceback fails
export PYTHONPATH=tests/hastub:custom_components:tests
out=$(mktemp)
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/root/ev-runs/prelude2.py").read())' 'R.section("R11-OUTSIDE-HONEST-DHW-RUNS' 'R.section("#3616 R11-OUTSIDE-ROOMS-P1' > $out 2>&1
rc=$?
cat $out

