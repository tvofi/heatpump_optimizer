#!/usr/bin/env bash
# Null control and perturbation for enum_uncleared_issue.py. Run from repo root.
set -euo pipefail
E=dev/audit/rounds/round11/D14/sweep/enum_uncleared_issue.py
T=$(mktemp -d)
mkdir -p $T/clean
cat > $T/clean/a.py <<'PY'
from homeassistant.helpers import issue_registry as ir
DOMAIN = "x"
def check(hass, bad):
    if bad:
        ir.async_create_issue(hass, DOMAIN, "thing_bad", is_fixable=False)
    else:
        ir.async_delete_issue(hass, DOMAIN, "thing_bad")
PY
echo "null: $(python3 $E $T/clean | tail -1)"
cp -r custom_components/heatpump_optimizer $T/pert
# one-line re-introduction: the recovery path of price_currency stops clearing
python3 - "$T/pert/coordinator.py" <<'PY'
import sys,re
p=sys.argv[1]; s=open(p).read()
old='ir.async_delete_issue(hass, DOMAIN, "price_currency")'
assert s.count(old)==1; open(p,'w').write(s.replace(old,'pass'))
PY
echo "main: $(python3 $E | tail -1)"
echo "perturb(drop price_currency clear): $(python3 $E $T/pert | tail -1)"
cp custom_components/heatpump_optimizer/coordinator.py $T/pert/coordinator.py
# fix-direction perturbation: _clear_worker_fallback no longer returns early on an empty latch
python3 - "$T/pert/coordinator.py" <<'PY'
import sys,ast
p=sys.argv[1]; s=open(p).read(); t=ast.parse(s)
f=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name=="_clear_worker_fallback"][0]
ifs=[n for n in ast.walk(f) if isinstance(n,ast.If) and any(isinstance(b,ast.Return) for b in n.body)]
L=s.splitlines(); i=ifs[0]
L[i.lineno-1]=L[i.lineno-1][:len(L[i.lineno-1])-len(L[i.lineno-1].lstrip())]+"if False:"
open(p,'w').write("\n".join(L)+"\n")
PY
echo "perturb(ungate _clear_worker_fallback): $(python3 $E $T/pert | tail -1)"
rm -rf $T
