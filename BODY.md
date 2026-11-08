Three planner defects from the 2026-11-08 replan study: (a) a name-prefix lane collision, (b) refused/deferred groups still scheduled, (c) the critical-path cap exemption missing for the coordinator cap.

(a) `roster_lane` matched stems with `str.startswith`, so `R10-I1` also took `R10-I18N-DE`. The stems are now `INSTRUMENT_NAME_STEMS`, matched as the exact group or `<stem>-...`. Alternatives: classify by files only (loses the name rules for file-less groups), or an exact id set (goes stale with every new group). The boundary match keeps the rule and removes the collision.

(b) `roster_lib.CLOSED_STAGES` now includes `refused` and `deferred`. Every reader of the set follows: `is_open`, `open_groups`, after-edge closure, `CARRY_CLOSED`, `handover_prompt.in_flight`, and the `is_open` callers in `roster_sync`, `roster_edit`, `size_durations` and `ci_predict`. `sweep_gantt.CLOSED_STAGES` is a separate "merged" set and is left alone. `refuted` stays open, because it names a finding rather than a group's work. Side effect: a group that is `after` a refused or deferred group is no longer held behind it. Say so if the owner wants deferred to keep blocking.

(c) `build_plan` already exempted a ready critical-path group from the slot cap. It did not exempt it from the coordinator cap, which `orchestrator.md` section 5 lists ("a coordinator K/2 limit"). `pick` now takes `cap_exempt` in the critical-path loop. A group that starts past a full coordinator cap is flagged `exempt_coordinator`, and `check_plan` leaves flagged groups out of its coordinator count. The in-tree roster's own critical path does not contain `R10-HANDOFF-PATH`: it is a no-dependency M group, and the only chain is `R10-GENERIC-HEAT-CURVE...R10-CLOSEOUT-CLEANUP`. I could not re-derive that group waiting behind the slot cap on the current head. The 2026-11-08 plan's input is not in the tree. What I fixed is the one cap the exemption missed, and I proved it on a fixture.

## Head

266ef2802f7b12544435faa10e27a05663d4e076 (the pull request head; the code handoff was 33332e239a256b410795736d9e771a65c3d76f7e, cut from main at 2a3c05644d85b7ee5c2c314fde5aca950e4aba91, and the head adds only main merges and the delivery row). Main had not moved when I handed off the code, so there was no second prepr run.

## Mutation proof

Each mutant was applied to the production line and run against `replan.py --self-test`, with `REPLAN_MUTATION_CHILD=1` so the harness did not recurse. The restored tree is green.

- `CLOSED_STAGES` without `refused`/`deferred`: replan `refused:` and `deferred:` rows go red, and the `roster_lib` row "refused and deferred are closed" goes red.
- Plain `startswith(p)` stem match: the row "a stem names its exact group... never a look-alike" goes red.
- `and cc >= coord_cap and not cap_exempt` reduced to `and cc >= coord_cap`: "coordinator: a ready critical-path group starts at t=0 past a full coordinator cap" goes red. The critical-path group started at +1:24 instead of t=0.
- `refuted` added to `CLOSED_STAGES`: "refused (null): a refuted group is still scheduled" goes red.
- `in_flight_coord() >= coord_cap` changed to `>`: "flagged exactly when the cap is full" goes red. This kills the diff-mutant CMP_BOUND survivor at that line.
- The in-file harness also has three new mutants (`lane-stem-boundary`, `coordinator-cp-exempt`, `coordinator-cp-flag`), all killed. The existing `coordinator-cap` and `cp-first-in-tier` anchors were updated for the new signature.

## Null control

- Main, same roster, `--start 2026-11-08T12:00:00Z`, run twice: byte-identical apart from `generated_at`.
- Fixed tree, run twice: byte-identical apart from `generated_at`.
- A non-critical coordinator group in the same position still waits and reports "coordinator cap 1". A critical-path group inside the cap is not flagged. A refuted group is still scheduled. `R10-GATEWAY`, a look-alike stem, is Core model.
- `--check` still refuses two planned coordinator groups in flight when the critical-path one is unflagged.

## Figures

Before/after replan. The roster is `dev/programme/rosters/wave-r10-groups.json` with two edits: `R10-FLY-CLOUD-FRUGAL-OFF` set to `refused`, and an `R10-I18N-DE` product group added. The command is `python3 tools/plan/replan.py --roster-file <copy named wave-r10-groups.json> --start 2026-11-08T12:00:00Z --out <plan>`, run at main and at the head.

| group | main | head |
|---|---|---|
| `R10-I18N-DE` | lane Instruments, start 2026-11-11T00:30:00Z | lane Core model, start 2026-11-09T02:37:00Z |
| `R10-FLY-CLOUD-FRUGAL-OFF` | scheduled, start 2026-11-11T00:08:00Z | done, start null |
| `summary.groups_open` | 56 | 55 |

`closure` and `wall_hours` are unchanged between the two (2026-11-13T05:16:00Z, 113.27 h).

Instrument: `python3 tools/plan/replan.py --self-test` (exit 0). `roster_lib.py`, `roster_sync.py`, `roster_edit.py` and `handover_prompt.py` `--self-test` all exit 0.

Diff-mutant step: `MUTANT_CMD="env REPLAN_MUTATION_CHILD=1 python3 tools/plan/replan.py --self-test"`. Its wall time was not measured on its own: I did not time the step, and it ran inside one prepr run. There were 4 survivors, listed below.

Seams for class (b): the readers named above, enumerated with `grep -rn "is_open\|CLOSED_STAGES\|DONE_STAGES"` over `tools`, `tests`, `.claude` and `dev/audit/harnesses`.

## Unpinned sites

- `replan.py` `in_flight_coord() > coord_cap` (CMP_BOUND): killed by the added row "flagged exactly when the cap is full", checked by mutation above.
- `replan.py` `cc["groups"]["X3"]["start"] >= iso(start, 0)` and `> iso(start, 1)`: these mutate a test assertion. The row's other conjunct, the `start_reason` "coordinator cap 1", and the null control carry the pin.
- `replan.py` `coordinator_cap=3` in the `cq` fixture: a test-fixture constant. The row pins the inside-the-cap behaviour at 2, and the cap-full row pins 1.

## Red checks

Read from the check-runs of 266ef2802f7b12544435faa10e27a05663d4e076 with filter=all across all pages (68 runs), the job steps and the job logs. Five runs concluded red at the head; they are two causes.

**governance / instrument-self-tests** (job 128731174619, run 42480460139): RED, and this diff caused it. It did not time out: it ran 12 minutes and failed at the step "Show the orchestrator tick deciding its own fixtures". The log says `FAIL PLAN: deferred E stays deferred` and `orchestrator_tick self-test: 283 checks, 1 failed`. I reproduced it: `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` at 266ef2802f7b gives the same line and 1 failed; at origin/main 8a4cf2618 it gives 283 checks, 0 failed. Cause: (b) puts `deferred` in `roster_lib.CLOSED_STAGES`, so the tick's PLAN section no longer walks a deferred group and never prints "E: deferred/refused (stage deferred) -- stays deferred" (`orchestrator_tick.py` line 1515, with its fixture at line 3092). I did not name that reader in the list of readers above and did not run its self-test. It is not class A and not R10-HOTFIX-SELFTEST-TIMEOUT #3275: every earlier step passed and the cut is a real failure. This body re-take changes no code, so the red stays at this head: the code fix is to make the tick report a deferred or refused group as closed (or to decide that its "stays deferred" line is no longer wanted and change the fixture), and it needs a push to this branch by the next seat. Cheaper detector: none runs before CI. `tests/closures.json` lists `orchestrator_tick.py` in no script's closure, and `prepr.sh` runs only the self-tests its steps name, so `instrument-self-tests` is the only place that runs this file's self-test. Standing cost: one governance run per push, about 13 minutes. A detector would be a closure edge from `roster_lib.py` to the tick's self-test, whose cost is a longer scoped gate on every `roster_lib.py` change; I have not built or measured it.

**gate** (jobs 128731638734 in run 42480460487, 128732971392 in run 42480946879, 128736246575 in run 42480460139), step "Judge this head": RED three times, class R10-HOTFIX-GATE-BUSY-DEFER for the first two and a consequence for the third. The first two logs say `FAIL run(s) [42480460139] at this head are still being judged; their gate decides`: they are the edit-run and sibling-run deferral, and say nothing about this diff. The code run that decided is run 42480460139, whose gate (job 128736246575) concluded `FAIL pr-contract / pr-contract: failure (this run)`. So the third gate is red because of the two checks below, and clears with them. The deferral's answer is the one it already has: a deferred gate is red by design until the deciding run concludes, and the cheaper detector for that is reading the mode and deciding run from the log rather than the tick.

**pr-contract / pr-contract** (job 128736065819, run 42480460139): RED. Step "Check the body against the contract" refused with `check governance / instrument-self-tests is red and ## Red checks does not name it`. This body names it and the failing step, which answers the refusal. Cheaper detector: `prepr.sh --body-check`, which I run on this body with the red named.

Earlier pushes of this PR: the push ebb07fad6 had two `gate`, two `refresh` and two `prelude` runs conclude `cancelled`, not red; `cancel-superseded` cancelled them when the next push landed, and no run at ebb07fad6 or at the code handoff 33332e239 concluded red. CodeQL concluded `skipped` at the head, with no infra 504 and no alert, and `tests / closures-autofix` concluded `skipped`; neither is red here.

Before the head moved, `prepr.sh` step `closures` refused on the code handoff, and I left that answer as it was:

`prepr.sh` step `closures` REFUSES: `tests/entities.py` exits 1 with "3 of 2665 ENTITY CHECKS FAILED". The same 3 of 2665 appear at main 2a3c05644d85 in a separate worktree, run beside mine with the non-`ok` output diffed (identical apart from paths). So it is inherited, not caused by this diff. I did not isolate which 3 checks fail. The likely cause is this container (timing-sensitive `hb:` checks) rather than the code. Nothing else refused. `ci predict` predicts no red.

## Forward-carry

none

## Friction

none
