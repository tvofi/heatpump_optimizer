Fix review: merge c447cf9ddb5d75bdaece68737ed21d1e837d520f

Round 2, F1.10 (#1808). Code head 0928349199895387481b76972d09c99eea62a9ab; PR head c447cf9d (main f67f598a merged in, then the inherited-claims drop).

- Round-1 block cleared. Re-ran my own round-1 mutants at 09283491. Dropping the floor in cop_nominal_floored now FAILS "R9-P3: cop_nominal_floored holds its floor below it" (0.4 -> 0.4, want 1.0). Dropping it in emitter_design_delta_t_floored FAILS the same way (0.3 -> 0.3, want 1.0). The unmutated control: ALL 3645 PASSED, rc 0.
- Ledger at 09283491 over the whole inventory: 3537 unpinned against 3564 at base 404a5fb0, 0 new unpinned sites, no ledger form problems. All 19 new sites have a disposition: 18 killed_by, 1 survivor_triage.
- Survivor triage (_buffer_charge_ceiling.net CLAMP_DROP, verdict equivalent): accepted. It is written by hand with a measured reason (20736 inputs, minimum tank temperature 20.0 C, 0 ceilings differ), not automated. Caveat: the equivalence rests on lo = max(20.0, ...) being written as a literal 20.0 while the clamp reads TANK_ROOM_AMBIENT_TEMP = 20.0. If either value changes, the triage is void. Non-blocking.
- No ruff churn: 12269398..09283491 touches only tests/features.py (+84) and 8 ledger json files, with no production file.
- Merge delta: f2fd5b71's tree equals a clean git merge-tree(f67f598a, 09283491), rc 0 with the claimnotes driver installed. c447cf9d differs from it only by 5 deleted F6.4 lines in tests/golden/claimed_drift.txt, which is env_drift --drop-inherited. That is accepted record loss in the #634 class, tracked by R9-F10.8.
- No resume files in the code-head ancestry; transport 3cd6ecfa sits directly above 09283491.
- Carried from round 1, still holding: finder p3_floors 22 -> 21 groups; the 3 barrier mutants are caught; structure.py passes; F6.4 had no conflict and has now merged.
- CI at c447cf9d, 12:53Z: typing, briefs, policy-docs, env-matrix, browser, hassfest, pr-contract, budget-raise-gate, delivery-status and nightly-status are green. mutation, fast, coverage and closures are still running. The mutation lane is the authority: the merge seat merges only on green.
- Not verified: the finder's comment_numbers.py crashes at both base and head (harness/tree mismatch), so D5-s2-02 rests on the fixer's evidence.
