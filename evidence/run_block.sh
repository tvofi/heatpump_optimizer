#!/bin/sh
# usage: run_block.sh <tree> <out>  -- the group's block, prelude emitted from the tree itself
cd "$1" && env PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/seat/features_block.py --emit-prelude /tmp/tmp.7VbeJ7a6yl/prelude-$(basename $1).py 'R.section("R11-OUTSIDE-HONEST-DHW-RUNS' 'R.section("#3616 R11-OUTSIDE-ROOMS-P1' > "$2.prelude" 2>&1
env PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/seat/features_block.py --prelude "exec(open('/tmp/tmp.7VbeJ7a6yl/prelude-$(basename $1).py').read())" 'R.section("R11-OUTSIDE-HONEST-DHW-RUNS' 'R.section("#3616 R11-OUTSIDE-ROOMS-P1' > "$2" 2>&1; echo "rc=$?" >> "$2"
