#!/bin/bash
# the group's mutation command: the supply-switch sections and the early cut-off section
cd "${REPO:-/home/user/rev}"
W=/home/user/w
o1=$(timeout 900 python3 tools/audit/seat/features_block.py --prelude "exec(open('$W/pre_sa.py').read())" 'R.section("supply switch at step boundaries (#2492' '# --- R10-CEILING-PROBE' 2>&1); r1=$?
o2=$(timeout 900 python3 tools/audit/seat/features_block.py --prelude "exec(open('$W/pre_ec.py').read())" 'R.section("early cut-off — a warm room' 'R.section("°F set-points' 2>&1); r2=$?
echo "$o1" | grep -E 'FAIL|PASSED|FAILED' | tail -${TAILN:-6}
echo "$o2" | grep -E 'FAIL|PASSED|FAILED' | tail -${TAILN:-6}
[ $r1 -eq 0 ] && [ $r2 -eq 0 ]
