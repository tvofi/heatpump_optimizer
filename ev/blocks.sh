#!/bin/bash
# usage: blocks.sh <tree>   runs the two feature blocks; prints tails; exit nonzero if either fails
cd "$1" || exit 9
export PYTHONPATH=tests/hastub
A='R.section("R10-COP-LEARNER-DRAW-FLOOR'; AE='R.section("R10-COP-GATE (#2262)'
B='# silence the learner. Synthetic numbers only.'
rc=0
timeout 90 python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/rv/pA.py").read())' "$A" "$AE" > /tmp/rv/outA.$$ 2>&1 || rc=1
timeout 90 python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/rv/pB.py").read())' "$B" "$A" > /tmp/rv/outB.$$ 2>&1 || rc=1
grep -h "^ *FAIL\|PASSED\|FAILED\|^[A-Za-z]*Error" /tmp/rv/outA.$$ /tmp/rv/outB.$$ | cut -c1-230 | head -${2:-8}
rm -f /tmp/rv/outA.$$ /tmp/rv/outB.$$
exit $rc
