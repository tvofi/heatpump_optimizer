Roster-reader predicates for R10-ROSTER-READ-SWEEP: `absorbed` is a closed stage for the open set and after-edges, a destination check that names `absorbed_into`, a `gate_kind` classifier the tick calls, and one shared REFUSED line for a missing roster ref (roster carries 1-5). Repair round 3 (head red on `governance / instrument-self-tests`): `roster_lib.is_open` now treats `absorbed` as closed, and `plan_page.build_rows` read that same predicate as "merged", so an absorbed group rendered as a done, delivered row (`folded into another group`, PR `merged`) and the `plan_page` self-test printed `66 checks, 7 failed`. This round renders merged only for `DONE_STAGES`; an absorbed group stays a `held` row naming its destination, and, being closed work the planner does not schedule (replan drops it), has no bar, tier or ETA. Two fixture checks that ranged over every not-merged row now range over the groups the plan schedules (`plan["groups"][g]["done"]` is false); that is a changed expectation, stated here, not hidden: before this PR an absorbed group was open and scheduled, and this PR deliberately made it closed. A new check pins the absorbed row itself.

Design: `DONE_STAGES` keeps meaning "merged"; `CLOSED_STAGES` is the open-set boundary and `CARRY_CLOSED` is the same object. `absorbed` stays a disposition, so `roster_sync` never rewrites it. Readers of roster stages checked under `python3 -I` at this head: plan_page, plan_table, handover_prompt, flow_metrics, merge_throughput, size_durations, replan, resume_doc, roster_lib, carry_audit, orchestrator_tick; only plan_page was wrong.

Carry map (roster entry `R10-ROSTER-READ-SWEEP`, 1-based): carries 1-5 landed in this diff (carry 1 includes the one-line `replan.is_done` call into `roster_lib.is_open`, a stated deviation from the carry text that routes replan to R10-FLOW-TOOLKIT-MODEL; carry 2 keeps `DONE_STAGES` as "merged" and puts the terminal set in `CLOSED_STAGES`). Carries 6-9 not landed; they stay on the open roster entry or route to R10-ORCH-ROSTER-SCHEMA by their own text.

## Head

`a5e19561f85b806f4eff04f39311a56f56d55233`, the final handoff code: repair commit `866221f0b` plus `origin/main` `30638cf0c8a7114019682f87051a4a282d2981ff` merged in. The PR head it repairs is `a4a11b3f05629130d4b35154725a24628bb108ae`. Main moved after the last prepr of the previous round, so prepr was rerun at this head (`PRE-PR: a5e19561f85b... rc=0`). The `handoff-wip` step ref holds an earlier, equivalent attempt authored as `seat` that the remote would not let me delete; the handoff does not descend from it.

## Mutation proof

`tools/audit/seat/plan_page.py` line `if g in merged:` reverted to `if g in done:` (the failing reader): `python3 -I tools/audit/seat/plan_page.py --self-test` prints `67 checks, 8 failed`. The PR head before the fix printed `66 checks, 7 failed`, among them `held: a disposition stage is its own class, naming the group it went to`, `defect 1: every row's status is the roster's own stage`, `defect 5: an absorbed group is not rendered done or delivered`.

## Null control

Unmutated head: `plan_page self-test: 67 checks, 0 failed` (66 plus the one new check `an absorbed group is held, unscheduled, and has no bar or tier`). Base `origin/main` 30638cf0c: `66 checks, 0 failed`, so the base fixture's absorbed-is-open expectations held there and only the two range-narrowed checks changed here.

## Figures

- `python3 -I tools/audit/seat/plan_page.py --self-test`: 67 checks, 0 failed (head); 66, 0 failed (base); 66, 7 failed (PR head a4a11b3f0).
- Other instruments at this head, each `python3 -I <tool> --self-test`: plan_table 26, handover_prompt 17, flow_metrics 16, resume_doc 15, roster_lib 64, carry_audit 365, orchestrator_tick 275, all 0 failed; `tools/plan/replan.py`, `tools/plan/size_durations.py` and `tools/audit/merge_throughput.py` print `0 failed` / `ok`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; `tests/entities.py` prints `ALL 2637 ENTITY CHECKS PASSED`; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh` at this head: `PRE-PR: a5e19561f85b806f4eff04f39311a56f56d55233 000000000000000000000000 rc=0`.

## Red checks

At PR head `a4a11b3f05629130d4b35154725a24628bb108ae`, all check-run pages read (`total_count` 68, one page of 100; page 2 empty), three concluded red:
- `governance / instrument-self-tests` (check-run 127982288611): `plan_page self-test: 66 checks, 7 failed`, this PR's own break (above). Class: a shared predicate widened to include `absorbed` with a reader of it left unchecked. Cheaper detector: run every instrument self-test the diff's imports reach, under `python3 -I`, before the handoff (done here; standing cost one run of about a dozen self-tests, seconds each). `prepr.sh` does not run them, which is the gap; I did not build the detector in this repair. No 30-minute-timeout cancel of this job occurred at this head (main-wide, cure R10-PROCESS-SLIM #3245).
- `gate` (check-runs 128001855738 and 128001831663): `FAIL run(s) ... at this head are still being judged; their gate decides`, the deferral on the red above; it follows `instrument-self-tests` and has no cause of its own.

## Forward-carry

none

## Friction

none
