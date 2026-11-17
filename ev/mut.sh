#!/bin/bash
# targeted mutants on the four pinned sites; run from the worktree at the head
cd "$1"; out="$2"
run(){ timeout 900 env PYTHONPATH=tests/hastub python3 tests/features.py > "$out/features-$1.txt" 2>&1; echo "$1 rc=$? fails=$(grep -c 'FAIL' "$out/features-$1.txt")" >> "$out/mutants.txt"; }
run base
F=custom_components/heatpump_optimizer/ledger.py; cp $F /tmp/m.bak; sed -i '80s/REFERENCE_BASIS = 4/REFERENCE_BASIS = 8/' $F; run M1-REFBASIS8; cp /tmp/m.bak $F
F=custom_components/heatpump_optimizer/thermal_model.py; cp $F /tmp/m.bak
sed -i '2280s/if not p.two_zone_enabled:/if False:/' $F; run M2-2280-GUARD_OFF; cp /tmp/m.bak $F
sed -i '3504s/if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:/if False:/' $F; run M3-3504-GUARD_OFF; cp /tmp/m.bak $F
sed -i '4312s/if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:/if False:/' $F; run M4-4312-GUARD_OFF; cp /tmp/m.bak $F
git status --short >> "$out/mutants.txt"; echo done >> "$out/mutants.txt"
