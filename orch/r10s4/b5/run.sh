W=/Users/timmalmstrom/hpo-seats/r10s4/route-b5-edit; B=/Users/timmalmstrom/hpo-orch/r10s4/b5
for p in "pi R10-FLOW-DESIGN-STAGES" "pk R10-FLOW-TOOLKIT-MODEL" "pl R10-MUTATION-ANCHOR" "pm R10-FLOW-WIP" "pf R10-POLICY-LINT-FAMILY"; do set -- $p
python3 tools/audit/seat/roster_edit.py append-carry $2 @$B/$1.txt --roster-ref handoff/audit-r10-roster --checkout . --worktree $W --push --message "roster_edit append-carry $2 (triage batch 5 $1)" 2>&1 | tail -3; echo "== $2"; done
