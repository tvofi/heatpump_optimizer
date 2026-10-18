Fix review: merge a0c0f86652e684c7e8449b9760273a343582d4ca

bus-nonce: 6b19e5f12c1553a53c52151c68cd87ee

Round 2 for #2365. Measured head `a0c0f86652e684c7e8449b9760273a343582d4ca`; I re-read it before posting and it had not moved. Merge base `d569693ad`. Main's side has moved no file this PR touches since `48bfc6b4e`, and between the code head `7ac9bace4` and the head only `dev/programme` record files differ. Mutants ran in `git archive` exports of the head; seat-python is venv 3.14.

## Round-1 blocks: both repaired
1. **Receiver half (mutation-vacuous).** A new features check sets the attribute from outside `pump_arbiter` and requires the floorless read to stay True. My mutant m2 (only `thermal_model.py` put back to its merge-base text, so the getattr fallback returns) now prints `FAIL D7-arch3-04: the reader has no channel ... [floorless read with the attribute set: False ...]`, giving `1 of 6 FEATURES BLOCK FAILED`. The unmutated m0 prints `ALL 6 FEATURES BLOCK PASSED`.
2. **Slot-floor twin (architecture-unsound).** The repair takes option (a). A new leaf module `plan_step.py` (imports only datetime and typing, no homeassistant) owns `PLAN_STEP_MINUTES`, `PLAN_STEP_HOURS` and `plan_step_start`. `coordinator._solve_anchor`, `FORECAST_STEP_MINUTES` and `pump_arbiter._step_start` are deleted, and `_inside_silent` and `_silent_rows` no longer carry the literal 0.25 and 96. Outside the archives, `git grep` finds no reader left of the removed names.

## Half-open fix (7bb9590df), my own mutants
- h1, `>=` put back to `>`: `FAIL D7-s3-8x-slotfloor: the plan's last step covers [stamp, stamp + one plan step) ...`, so `1 of 6` fails.
- h3, the width changed to a literal 30 minutes: the same check fails, `1 of 6`.
- s1, the inline 15-minute floor put back in `_observe`: `FAIL ... the arbiter's ledger step and the solve's anchor are one function on one width ... [(15, 0, 0), (45, 30, 30)]`, `1 of 6`.
- CI's `mutation` lane (job 117612600661) prints `MUTATION TABLE PASSED`. It lists plan_step.py:41 RETURN_DEL killed by manual_plan.py, and pump_arbiter.py:342 BOOLOP, :342 CMP_BOUND and :348 BOOLOP killed by features.py.
- The behaviour change is confined to the single instant `stamps[-1]` + one step, which now returns None like every other step boundary. `env_drift` in CI fast reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`.

## RESULT lines (mine, at the head)
```
duty_floor_channel.py (finder): leaked_reads=0 null_leaked_reads=0 reflective_writes_pump_arbiter=0 load1=24.12
r10_slot_floor_twins: seams=4 folded_seams=3 (coordinator._solve_anchor, pump_arbiter._observe, pump_arbiter._step_start) driven=3 disagreeing_probes=0/10 unclassified_seams=0; --perturb 2/10; --identity 0/10
shape_slot_floor.py (finder, from 1d1974df4): implementations=2 (plan_step_start, tariff._window_slot); its driving arm raises AttributeError on coordinator._solve_anchor, because the fold deleted the names it binds
```
The base figures are round 1's: duty floor 307381 leaked against 0, and the census reading 4 implementations.

## Red checks (step 11)
I enumerated the check-runs over all 16 PR commits. The only reds are at `1386009b7`: `fast (3.14)` 117571211622, `mutation` 117570935207, `mutation-autofix` 117579526782 and `pr-contract` 117579610632. `## Red checks` names each one and answers it: for the fast red the cheaper detector existed and the seat skipped it; the mutation red is pinned; the autofix red is a consequence of the fast red; the contract red was the body being cut before those runs. Every answer is present.

## CI at the head, latest run per name
30 success, 15 skipped, 0 failure or cancelled. `fast (3.14)` (job 117612658368) prints:
- `MODE: SCOPED -- 28 script(s) run, 5 scoped out`
- `ALL 4161 FEATURE CHECKS PASSED`
- `ALL 2347 ENTITY CHECKS PASSED`
- `ALL 109 HARNESS HEADER CHECKS PASSED` (this covers the D6 claims.py 78-module header)
- `STRUCTURE RATCHET PASSED`
- `ALL 50 GUARD PIN CHECKS PASSED`

`closures`, `mutation`, `arch-score` and `pr-contract` are success.

## Other steps
- Steps 5 and 13: VERSION, the manifest, the notes heading, both claim files and every `*_budgets.json` are untouched against the merge base. `git merge-tree --write-tree origin/main HEAD` at `994695e06` exits 0, so it is clean.
- Step 7: the body's `## Head` names `a0c0f86652e684c7e8449b9760273a343582d4ca` and the code head `7ac9bace4`.
- Note for the orchestrator, not a block: this diff now touches `coordinator.py`, which is outside the roster's `files`. The touch is the import, the `FORECAST_STEP` definition, the deletion of `_solve_anchor` and five call-site renames, so architect note 11 (coordinator diffs merge smallest-first) applies on the train.
- Note, not a block: `pump_arbiter` still spells the step width as 15.0 in `_share`'s minute split and as `LOG_STEPS = 96`. These are not the slot-floor rule's seams.

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-pump-model/evidence2/
