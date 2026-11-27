#!/bin/bash
cd /tmp/hpo-rev-3932/wt; export PYTHONPATH=tests/hastub; F=custom_components/heatpump_optimizer/store.py; B='# R11-SEAM-store-p2 (round-11 sweep P1'
run(){ echo "== $1 ($(git diff --numstat $F | awk '{print $1"+/"$2"-"}'))"; python3 tools/audit/seat/features_block.py "$B" 2>&1 | grep -E "FAIL|PASSED|failed" | cut -c1-200; git checkout -q -- $F; }
run "M0 unmutated"
sed -i '' 's/^            data = _unflag_numbers(data, node)$/            pass/' $F; run "M1 boundary call deleted"
sed -i '' 's/"choice": lambda v, d: any(v == m and isinstance(v, bool) == isinstance(m, bool) for m in d.choices),/"choice": lambda v, d: v in d.choices,/' $F; run "M2 choice reverted"
sed -i '' 's/    return domain.kind == "choice" and bool(domain.choices) and all(_number(m, real) for m in domain.choices)/    return False/' $F; run "M3 choice arm false"
sed -i '' 's/    return None if numeric and isinstance(value, bool) else value/    return value/' $F; run "M4 unflag identity"
sed -i '' 's/    if isinstance(value, list):/    if False:/' $F; run "M5 list walk off"
sed -i '' 's/    if isinstance(value, dict):/    if False:/' $F; run "M6 dict walk off"
git status --short
