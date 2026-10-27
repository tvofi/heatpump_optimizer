#!/bin/bash
set -u
F=custom_components/heatpump_optimizer/price_tiles.py
python3 - "$F" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]); t=p.read_text()
old='    key = "monthly_settled_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"'
new='    key = "monthly_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"'
assert t.count(old)==1
p.write_text(t.replace(old,new,1))
PY
PYTHONPATH=tests/hastub python3 tests/features.py > /tmp/verdict-2819/evidence/price_tiles_mutant_full.txt 2>&1
echo "rc=$?"
git checkout -- "$F"
grep -E "FAIL|FEATURE CHECKS" /tmp/verdict-2819/evidence/price_tiles_mutant_full.txt | tail -8
