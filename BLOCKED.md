# BLOCKED: r11-repair-3907 (PR #3907, R11-OUTSIDE-START-APPROACH)

Question: The merge of origin/main fd93aa3e9b leaves `module_excess_loc` 49 lines above main's budget (21695 against main's 21646; the file the ledger driver merged reads 21599, because both sides were credited for one move). The excess is predecessor #3805's code (R11-OUTSIDE-HONEST-DHW-RUNS), still unmerged and carried in this branch: `optimizer.py` +40 (`_charge_runs`, the combi exchange's commit build) and `dhw_planner.py` +9 (the commit_charges/whole_charges wiring, `_DhwPlanContext.coast`). The branch paid for those lines by moving the start helpers out of `dhw_planner.py`, and main's #3863 (dhw_start.py) has since made that same move. Which should it be: (a) a raise of `module_excess_loc` to 21695 under mandate 6893738184 (scope all, in force until 2026-12-15), with a `## Raise justification`; (b) a payment in this repair, moving the combi commit build out of `optimizer.py` into `dhw_charges.py` (which diverges this branch from #3805's head); or (c) paying it in #3805 first and re-cutting this repair on #3805's merge?

## State at 4f7aaaa94b (this ref, parent of this commit)

- origin/main fd93aa3e9b is merged into handoff/r11-outside-start-approach 95c0bc2719, with every conflict resolved (see that merge's commit message). The start condition lives only in main's `dhw_start.py`. `dhw_charges.py` keeps the commit stage and imports `STARTABLE_ROUNDS`, `drop_unstartable` and `startable_steps` from it. The 17 moved ledger pins are main's, under `killed_by/dhw_start.py`.
- Paid in the merge: the `dhw_charges` import in `dhw_planner.py` collapsed to one line (21700 -> 21695).
- Green at the merge, PYTHONPATH=tests/hastub: `tests/block_duty.py` (ALL 161 BLOCK DUTY CHECKS PASSED), `tests/deployment_shape.py` (ALL DEPLOYMENT SHAPE CHECKS PASSED), `dev/audit/rounds/round4/D6/claims.py` rc 0. `tests/doc_claims.py` failed 1 of 443 checks (architecture.md HA-free count, documented 72, measured 71); the fix to 71 is in the merge commit and has not been re-run.
- Red at the merge: `tests/structure.py`, `FAIL module_excess_loc 21695 > 21599 (+96)`; the question above.

## Reds on #3907's last head 46cdd1f919 still owed a repair (in `merge_train.py owed-reds`)

- `tests / coverage-ratchet`: `COVERAGE RATCHET BREACHED`, 3 modules under the 95.0 % per-module floor: approach.py 79.13 %, runs.py 83.63 %, comfort_floor.py 90.00 %. The PR adds approach.py and changes runs.py. It does not touch comfort_floor.py (main's, R11-OUTSIDE-ROOMS-3B), and the null control on main is not yet taken: main's CI at fd93aa3e9b was in progress.
- `tests / fast (3.14)`: `1 TEST SCRIPT(S) FAILED`. The tail of the log does not name the script, so it is still to be identified at the merged head.
- `tests / mutation`, and `gate`, which names fast (3.14) and mutation.
- Not owed: `tests / mutation-autofix`, `governance / instrument-self-tests` (whether the diff's scope selects the failing step is not yet checked), `tests / nightly-status`.

## Brief conflict, pending orchestrator confirmation

The brief's step 4 says to push `handoff/r11-outside-start-approach` and `handoff-body/r11-outside-start-approach`. The seat prompt allows only this seat's return refs (`handoff/r11-repair-3907`, `handoff-wip/r11-repair-3907`). Neither ref was pushed.
