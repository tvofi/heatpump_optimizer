#!/bin/bash
# targeted mutants on the four pinned sites, each against the block from the reference-basis checks
# through the R11-VALVE-REFERENCE checks (features_block.py); run in a worktree at the head
cd "$1"; out="$2"; S="# R10-HOTFIX-SAV-ESTIMATE: a month's reference basis"; E="# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0"
export PYTHONPATH=tests/hastub:tests:custom_components
python3 tools/audit/seat/features_block.py --emit-prelude "$out/prelude.py" "$S" "$E" > "$out/emit-prelude.txt" 2>&1; echo "emit-prelude rc=$?" >> "$out/mutants2.txt"
run(){ python3 tools/audit/seat/features_block.py --prelude "exec(open('$out/prelude.py').read())" "$S" "$E" > "$out/block-$1.txt" 2>&1; echo "$1 rc=$? $(grep -c '^ *FAIL ' "$out/block-$1.txt") FAIL: $(grep '^ *FAIL ' "$out/block-$1.txt" | cut -c1-140 | tr '\n' '|')" >> "$out/mutants2.txt"; }
run base
F=custom_components/heatpump_optimizer/ledger.py; cp $F $out/../m.bak; sed -i '80s/^REFERENCE_BASIS = 4$/REFERENCE_BASIS = 8/' $F; git diff --stat >> "$out/mutants2.txt"; run M1-L80-REFBASIS8; cp $out/../m.bak $F
F=custom_components/heatpump_optimizer/thermal_model.py; cp $F $out/../m.bak
sed -i '2280s/if not p.two_zone_enabled:/if False:/' $F; git diff --stat >> "$out/mutants2.txt"; run M2-2280-GUARD_OFF; cp $out/../m.bak $F
sed -i '3504s/if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:/if False:/' $F; git diff --stat >> "$out/mutants2.txt"; run M3-3504-GUARD_OFF; cp $out/../m.bak $F
sed -i '4312s/if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:/if False:/' $F; git diff --stat >> "$out/mutants2.txt"; run M4-4312-GUARD_OFF; cp $out/../m.bak $F
echo "tree after: $(git status --short | wc -l) changed" >> "$out/mutants2.txt"; echo done >> "$out/mutants2.txt"
