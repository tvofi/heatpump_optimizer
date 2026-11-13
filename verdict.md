Fix review: merge 4980c565b0eed7463e081494bb9ad933b6747252

bus-nonce: f86a3249a5396fbd4e28df99c96cc933
pending-ci: gate

## Round

Later round over the merge-verdicted head 3d56953499ef23b0d51f2eee7d0cc782d05b572a. Scope is the delta `git diff 3d56953499ef 4980c565b0ee` (fix-review.md step 12). The branch's own commits in it are 1e1dae07d7 (tests/features.py, the #3420 part E rows with the minimum pause engaged) and 6ef4eda767 (dev/programme/delivery/3512.md). Everything else comes from merges of origin/main (#3530, #3534, #3524, #3441, #3505 and the v7.1.13/v7.1.14 stamps). review_carry.py was not needed: the head is not a carry of the reviewed patch, so this is a delta review.

The one production conflict in the delta is coordinator.py `_write_supply`, resolved in 754a2b022d (merge of main 17ae732a4e, #3530). `git show --remerge-diff` keeps main's `pump_arbiter.write_supply(self, ...)` and this branch's `elif switch_entity and not held.supply_held:` (ev/remerge_754a2b022d_coordinator.diff). The other merges (4980c565b0, d5eb9f80e2, 4ae424099c, 390113cc66, 94421017fe) show no remerge diff under custom_components/, only the ledger drivers on tests/closures.json and tests/structure_budgets.json. That includes the merges that brought #3441 and #3505, up to main 3b9749dac5. Dropped clauses on either side: the branch's own production patch over each merge base (`git diff 43e95474559c...3d56953499ef` against `git diff 3b9749dac5...4980c565b0ee`, custom_components/) has byte-identical added and removed lines. Only the index and hunk-offset lines differ (ev/branch_patch_old_vs_new.diff). So no branch clause was lost, and no main line appears as removed by the branch.

Widened to exactly one path: the coordinator.py `_write_supply` write path (the hold sits ahead of main's new `_lead_mode` mode write). The risk is that a pause-held switch-on writes the select mode with no switch write, or writes it again on the step tick that lands. That is behaviour the earlier review never saw, because `write_supply` did not exist at 3d56953499ef. Part E's new rows pin it, and the mutants below show the rows detect it.

## Evidence

- Head reviewed: 4980c565b0eed7463e081494bb9ad933b6747252 (ev/HEAD.txt). `git ls-remote` shows refs/pull/3512/head and the branch at this SHA. The body's `## Head` names it.
- RESULT features_head: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py` printed `ALL 5466 FEATURE CHECKS PASSED`, rc 0 (ev/features_head.log).
- RESULT mutant m1 (`_write_supply` bypasses `supply_hold.hold_supply` and writes `supply_write`'s value directly; ev/m1.diff): rc 1. FAIL `a cycle switch-on the minimum pause holds back writes no mode and no switch` [[select_option, turn_on]], FAIL `a switch-on held on one tick and landing on a later one writes the mode immediately before the switch on that later tick` (nothing written at any minute), and two older min-run checks (ev/features_m1.log).
- RESULT mutant m2 (the lead mode written ahead of the hold, then a bare `switch_supply`; ev/m2.diff): rc 1, 4 FAILs, including both new part E rows and `with the minimum pause engaged too, a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back` [[select_option, turn_off]] (ev/features_m2.log). The test commit's three checks are not vacuous.
- RESULT entities: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2711 ENTITY CHECKS PASSED`, rc 0 (ev/entities.log). Its `  FAIL a3:*` lines are self-test output over planted states (`sensor.x`, `sensor.not_ours`); the suite passes. The body's `ALL 2709` is quoted for 3d56953499ef. Main's merges added the two checks since then.
- RESULT structure: `tests/structure.py` printed `STRUCTURE RATCHET PASSED`, with `class_excess_loc=17522` and `max_class_loc=7916` at their budgets (ev/structure.log). Against the merge base 3b9749dac5, `tests/structure_budgets.json` only lowers values (17523 to 17522 and 7918 to 7916), so no budget is raised. The body's `max_class_loc was recorded at 7919` is the 3d56953499ef figure. At this head the merge driver summed both sides' deltas to 7916, and the ratchet confirms that value.
- Versions and claims: `git diff 3b9749dac5...4980c565b0ee` over VERSION, manifest.json, RELEASE_NOTES.md and both claim files is empty.
- Merge with main: `git merge-tree --write-tree origin/main 4980c565b0ee` returned exit 0. origin/main is 3b9749dac5, the head's own base (ev/merge_tree.txt).
- Evidence judged, not widened: since #3530, `async_publish_current_action(..., heat_pump_on=on)` sends the ECL110 legacy payload the cycle's pre-hold `on`. At 3d56953499ef the payload carried the action's equally pre-hold `heat_pump_on`. The payload was not hold-aware before the delta and is not after it. The delta changes which unheld value it carries, not whether it is held, so this does not widen the review.
- Mutation table, golden drift, closures and the closed-loop harness were not re-run: no production line of the branch moved (the patch identity above), and fix-review.md step 11 has CI's heavy runs cited, not re-run.
- Owed reds: `merge_train.py owed-reds` printed the 22 required contexts. CI at this head was still pending at every poll (`merge_train.py classify 4980c565b0ee --pr 3512`: `WAIT ... pending: gate red: none`), so no red at this head is read or answered here. Polled 11:18 to 11:47 UTC; last line `WAIT 4980c565b0eed7463e081494bb9ad933b6747252 pending: gate red: none`, hence the pending-ci line. The body's `## Red checks` answers the earlier heads' reds.

## Findings

- Carried from the 701a18e26661 verdict, still open: rule three (`supply_hold._ends_soon`) awaits the owner's ruling. The body still states its cost (0.82 kWh/day booked and not delivered on LIGHT winter, and a HOT flat day with no run) and how to remove it. Carry: dismissed: surfaced in the PR body for the owner's code-owner review; no later stage changes
