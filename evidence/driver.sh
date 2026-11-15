#!/bin/bash
# reviewer's driver: three blocks of tests/features.py, preludes emitted from the tree it runs on
T=$(mktemp -d); rc=0
run() { # name start end
  python3 tools/audit/seat/features_block.py --emit-prelude $T/$1.py "$2" "$3" >/dev/null 2>$T/$1.emit || { echo "EMIT-FAIL $1: $(tail -1 $T/$1.emit)"; rc=1; return; }
  out=$(python3 tools/audit/seat/features_block.py --prelude "exec(open(\"$T/$1.py\").read())" "$2" "$3" 2>&1); r=$?
  echo "$out" | grep -E 'FAIL|FEATURES BLOCK|Error' | head -8
  [ $r -ne 0 ] && rc=1
}
run draw 'R.section("R10-COP-LEARNER-DRAW-FLOOR' 'R.section("R10-COP-GATE (#2262)'
run prev '# silence the learner. Synthetic numbers only.' 'R.section("R10-COP-LEARNER-DRAW-FLOOR'
run heat 'R.section("R10-HEAT-METER: a delivered-heat counter' 'R.section("supply switch at step boundaries'
rm -rf $T; exit $rc
