#!/bin/bash
cd /private/tmp/claude-501/rev3805 || exit 9
E=/private/tmp/claude-501/ev3805; mkdir -p $E
S='# --- R10-DUTY-SWITCH-PLANNER-PRICE block start'; END='R.section("R11-OUTSIDE-HONEST-STARTS-RUNS'
export PYTHONPATH=tests/hastub:custom_components:tests
F=custom_components/heatpump_optimizer/optimizer.py
python3 tools/audit/seat/features_block.py --emit-prelude $E/prelude.py "$S" "$END" > $E/emit.log 2>&1; echo "emit=$?"
run() { python3 tools/audit/seat/features_block.py --prelude "exec(open('$E/prelude.py').read())" "$S" "$END" > $E/$1.log 2>&1; echo "$1 rc=$? $(tail -1 $E/$1.log)"; grep "^FAIL" $E/$1.log | cut -c1-160; }
run unmutated
cp $F $E/opt.orig
python3 - <<'PY'
p="custom_components/heatpump_optimizer/optimizer.py"; s=open(p).read()
old="        return min((\n            _best_runs("
assert s.count(old)==1; open(p,"w").write(s.replace(old,"        return max((\n            _best_runs("))
PY
run M1_min_to_max; cp $E/opt.orig $F
python3 - <<'PY'
p="custom_components/heatpump_optimizer/optimizer.py"; s=open(p).read()
old="            for space in relaxed\n        ), key=lambda c: c[0])[1:]"
assert s.count(old)==1; open(p,"w").write(s.replace(old,"            for space in relaxed[:1]\n        ), key=lambda c: c[0])[1:]"))
PY
run M2_first_descent_only; cp $E/opt.orig $F
git status --porcelain
