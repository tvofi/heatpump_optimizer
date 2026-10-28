Fixer seat r10s6 fix-2887-s8b, PR #2887 (R10-BUFFER-STORE), fix review 1 (blocked at fa6eb482b) rework.
Worktree: ~/hpo-seats/r10s6/fix-2887-s8b/wt (locked, detached). Code commits over fa6eb482b: the reference tank law
(thermal_model.valve_charge_demand, optimizer._thermostat_demand router, optimizer._reference_cop), features.py checks,
r10_buffer_store.py `reference` mode, two triage reason corrections, golden claims (5 baseline_cost) with may-drift
suspensions, class_excess_loc re-record 17994 -> 17988, f21 continuation cell tank 25 -> 30 C.
Carry: #2499 residual appended to R10-STORE-RACES on handoff/audit-r10-roster at 5704c4048 (readback exact).
Evidence: ev-*.txt, gate3/*.log, ev-mutants.txt (16 mutants + null) in this directory.
Owed after this note: body -> BODY.md, push code to handoff/r10-buffer-store, body via body_push.sh, update_pr.sh.
