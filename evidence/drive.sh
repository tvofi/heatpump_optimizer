#!/bin/bash
cd "$1" || exit 2
P=$(mktemp)
PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude $P 'R.section("COP learner duty floor keys' 'R.section("R10-COP-GATE (#2262)' >/dev/null 2>&1
PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('$P').read())" 'R.section("COP learner duty floor keys' 'R.section("R10-COP-GATE (#2262)' 2>&1
rc=$?; rm -f $P; exit $rc
