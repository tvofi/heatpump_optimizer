#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/r11/rev-3805/wt2 || exit 2
E="env PYTHONPATH=tests/hastub:custom_components:tests"
S='R.section("R11-OUTSIDE-HONEST-DHW-RUNS'
END='R.section("#3616'
P="exec(open('/Users/timmalmstrom/hpo-seats/r11/rev-3805/prelude3.py').read())"
F=custom_components/heatpump_optimizer/dhw_planner.py
$E python3 tools/audit/seat/features_block.py --prelude "$P" "$S" "$END" > ../ev2/dhw-null.txt 2>&1; echo "rc=$?" >> ../ev2/dhw-null.txt
python3 - <<'PY'
p='custom_components/heatpump_optimizer/dhw_planner.py'
s=open(p).read(); o="        row = lengths[0] - 1 if self.running else sum(lengths) - 1"
assert s.count(o)==1; open(p,'w').write(s.replace(o,"        row = sum(lengths) - 1"))
PY
git diff --stat
$E python3 tools/audit/seat/features_block.py --prelude "$P" "$S" "$END" > ../ev2/dhw-RUNNING_INIT.txt 2>&1; echo "rc=$?" >> ../ev2/dhw-RUNNING_INIT.txt
git checkout -- $F; git status --short | head
