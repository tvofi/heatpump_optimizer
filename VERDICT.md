Fix review: blocked 8daf6df1576494f49f0ac32d790dbedbb6c92d0e code-unwired: a durations-file phase_hours never reaches generated.model, so the phase figure branch is unreachable and its self-test feeds it past replan; three claimed behaviours have surviving mutants

bus-nonce: 3c8ff3520f2ed7a12f87327f57b324c0
pending-ci: gate

## Block

Round 1 (first review of #3676), measured at head 8daf6df1576494f49f0ac32d790dbedbb6c92d0e, merge base 6f422812d5d8b918beace0283419c153f6df66ce.

1. **The phase-duration path is unwired (carry 6).** `plan_page.render` hands `plan_phases.section` `phase_hours=model.get("phase_hours")`, where `model` is `plan["generated"]["model"]`. `replan.build_plan` builds that model from `sizes_hours`, `live_remaining_fraction`, `sizes_provenance` and `MODEL_FIELDS` only (tools/plan/replan.py:590 and :1531), and `MODEL_FIELDS` has no `phase_hours`. So a `phase_hours` written into `tools/plan/durations.json` never reaches the page: the "N h (plan model)" branch of `_model_duration` cannot be reached in production. `ev/phase_hours_e2e.txt`: `build_plan` over durations.json plus `phase_hours={"finders": 7.5}` gives `phase_hours in generated.model: False`. Control, `ev/phase_hours_control.txt`: the same run with `"phase_hours"` added to `MODEL_FIELDS` carries `{'finders': 7.5}` and `check_plan` returns `[]`, so the harness moves under its perturbation. The self-test arm "a phase the model prices prints its figure ..." injects `phase_hours` straight into `generated.model` and skips replan, so it tests a path production cannot reach. The body's forward-carry line, "the page prints the phases unmeasured until a measurement lands in the durations file", is false at this head: a measurement landing there changes nothing on the page. The plan_phases.py comment ("`durations.json`'s `phase_hours`") states the same unwired source. Fix: carry `phase_hours` from the durations file into the model (one `MODEL_FIELDS` entry, or a refused or validated field), and add a self-test arm that goes durations, then `build_plan`, then `render`, with that line's mutant killed.
2. **Surviving mutants on production lines the body claims** (ev/mutants.txt, driver ev/mutation_driver.py, each mutant restored afterwards, worktree clean):
   - M6 `check_plan`'s `next_round` recursion (`bad += [... check_plan(nxt)]` changed to `pass`) SURVIVED both `plan_page.py` and `replan.py --self-test`. The body says the next round's plan is "a full plan that `check_plan` also checks", but the only arm asserts `check_plan(p2) == []`, which a dropped recursion also satisfies. An arm with a violating sub-plan is owed.
   - M16 `next_round_preview`'s `except PlanError` (changed to catch `ZeroDivisionError`) SURVIVED. The body says "a later round the model cannot plan is `next_round.unavailable`, drawn as an UNAVAILABLE tab". The UNAVAILABLE arm builds `next_round` by hand (`broken = {..., "unavailable": "boom"}`), so the producer that turns a `PlanError` into `unavailable` goes unchecked, and without it a later-round `PlanError` would fail the whole round's plan.
   - M15 `"beyond": len(later) - len(mine)` changed to `0` SURVIVED. The body says "groups of rounds past the nearest are only counted (`beyond`)", and no arm has a group two rounds ahead.

## Evidence

- RESULT figures re-derived at head (ev/selftests-head.txt): `plan_page self-test: 149 checks, 0 failed`; `beat_jobs self-test: 274 checks, 0 failed`; `replan self-test: 0 failed`; `STRUCTURE RATCHET PASSED`; `ALL 410 checks PASSED`. All match the body. At the base (ev/beat_jobs-base.txt): beat_jobs 271, 0 failed, matching the body; plan_page 136, 0 failed.
- RESULT mutation proof (ev/mutants.txt): the body's five mutants re-run and all killed, M1 to M5, with the failures the body names. Reviewer-added mutants: M7 (after-edge filter), M8 (next round starts at the plan start, not the closure), M9 (`r > round_n` changed to `>=`), M10 and M11 (`one_line_brief` list marker and heading cut), M12 (snap issue filter), M13 (`part` flag) and M14 (`tabbed` without `next_round`) were all killed. M6, M15 and M16 survived (see Block).
- RESULT null controls: the arms the body names are present at the head and pass (part of the 149). M1, M12 and M14 show that they detect a missing round filter, a missing issue filter and a tab with no `next_round`.
- RESULT real roster: `replan.py --out` over the in-tree roster at head (ev/real-roster-plan.txt) plans round 11 with 62 groups, closure 2026-11-22T04:28:00Z, and no `next_round`, because nothing of a later round is on the roster. The tab stays absent, as the null control predicts.
- RESULT merge: `git merge-tree --write-tree origin/main 8daf6df1576494f49f0ac32d790dbedbb6c92d0e` exits 0, no conflict (ev/merge-tree.txt).
- RESULT VERSION, manifest, RELEASE_NOTES and claim files are untouched in the three-dot diff.
- Finder's harness: none named. The work is an owner-directed instrument group (carries 0 to 6), so the harness is the carry's own control. The reviewer built the phase_hours end-to-end probe here; it is the reviewer's, not the finder's.
- CI: `merge_train.py classify 8daf6df1576494f49f0ac32d790dbedbb6c92d0e --pr 3676` still prints `WAIT ... pending: gate red: none` after about 30 minutes of polling (ev/classify-last.txt). `tests / nightly-status` reads failure in the packet digest but is not in the `owed-reds` set, so it is owed no answer.
- Head re-read: the PR head is still 8daf6df1576494f49f0ac32d790dbedbb6c92d0e, and the body's `## Head` names it.
- Comms: seat_comms init and heartbeat ran. The inbox held no command.

## Findings

none
