#!/bin/bash
# Reviewer's re-run of the named production mutation proof (PR #2819).
# Mutant: price_tiles.monthly_figure's cap key -> the branch's spelling.
set -u
F=custom_components/heatpump_optimizer/price_tiles.py
run() { PYTHONPATH=tests/hastub python3 tests/features.py 2>&1 | tail -3; echo "rc=${PIPESTATUS[0]}"; }
echo "--- baseline ---"; run
python3 - "$F" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]); t=p.read_text()
old='    key = "monthly_settled_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"'
new='    key = "monthly_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"'
assert t.count(old)==1, t.count(old)
p.write_text(t.replace(old,new,1))
PY
echo "--- mutant ---"; run
git checkout -- "$F"
echo "--- restored ---"; git status --porcelain -- "$F"
