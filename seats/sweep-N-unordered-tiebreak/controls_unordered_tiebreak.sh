#!/usr/bin/env bash
# Null control and perturbations for enum_unordered_tiebreak.py. Run from repo root.
set -euo pipefail
E=dev/audit/rounds/round11/D14/sweep/enum_unordered_tiebreak.py
T=$(mktemp -d); mkdir -p $T/clean
cat > $T/clean/a.py <<'PY'
def reason(codes):
    return max(dict.fromkeys(codes), key=codes.count), sorted(set(codes))
PY
echo "null: $(python3 $E $T/clean | tail -1)"
echo "main: $(python3 $E | tail -1)"
cp -r custom_components/heatpump_optimizer $T/fix
sed -i 's/max(set(codes), key=codes.count)/max(dict.fromkeys(codes), key=codes.count)/' $T/fix/plan_slots.py
echo "perturb(fix plan_slots, one line): $(python3 $E $T/fix | tail -1)"
cp -r custom_components/heatpump_optimizer $T/re
python3 - $T/re/coordinator.py <<'PY'
import sys
p=sys.argv[1]; s=open(p).read(); old="sorted(set(day_types))"
assert s.count(old)==1; open(p,"w").write(s.replace(old,"[max(set(day_types), key=day_types.count)]"))
PY
echo "perturb(re-introduce at coordinator day_types, one line): $(python3 $E $T/re | tail -1)"
rm -rf $T
