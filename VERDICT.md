Fix review: merge 6804e9c5a29946cbef4722088b1f668de6a246a8

bus-nonce: c8b3aa208876b8c2a18fbace312988d5
pending-ci: gate

## Review

Round 2, a delta review of #3676. The previous review was at head 8daf6df1576494f49f0ac32d790dbedbb6c92d0e. This head is 6804e9c5a29946cbef4722088b1f668de6a246a8, and the merge base is 6f422812d5d8b918beace0283419c153f6df66ce. The delta (`git diff 8daf6df 6804e9c`) touches three instrument files only: `tools/plan/replan.py`, `tools/audit/seat/plan_page.py` and `tools/audit/seat/plan_phases.py`. It touches nothing under `custom_components/`, so the scope does not widen (fix-review.md step 12).

Each finding of the previous block is resolved:
1. phase_hours unwired: `replan.MODEL_FIELDS` now names `phase_hours`, and `build_plan` (replan.py:1537) copies it from durations into `generated.model`. The new self-test arm runs from durations through `replan.build_plan` to `render`. MW (field removed from `MODEL_FIELDS`), MD (key filtered out at the copy site) and MP1 (`plan_page.py:800` handing `phase_hours=None`) are each KILLED by that arm. Failing first: the head's `plan_page.py` over 8daf6df's production files gives `152 checks, 1 failed`, and the failure is that arm, `got: (2, 2)`. No other reader of `MODEL_FIELDS` exists. `size_durations.py` writes `{**old, **out}`, so a `phase_hours` written by hand into durations.json survives a re-measure. `phase_hours` is not added to the required fields, and the renderer's guard on bad figures is unchanged.
2. Surviving mutants M6, M15 and M16 are each now KILLED by the arm the body names, with the failure text the body quotes.

## Evidence

- RESULT mutation (ev/mutants.txt, driver ev/mutation_driver.py, each mutant restored, `git status` clean): M6 KILLED, M15 KILLED, M16 KILLED, MW KILLED, MP1 KILLED, MD KILLED. Each was killed by `plan_page.py --self-test`. `replan.py --self-test` passes under all six, so the kills come from plan_page's arms only, which matches the body.
- RESULT failing first (ev/failing-first.txt): `plan_page self-test: 152 checks, 1 failed` over 8daf6df's production files, matching the body.
- RESULT figures at head (ev/selftests-head.txt, ev/cheap-checks.txt): `plan_page self-test: 152 checks, 0 failed`; `beat_jobs self-test: 274 checks, 0 failed`; `self-test: 0 failed` (replan); `STRUCTURE RATCHET PASSED`; `ALL 410 checks PASSED`; `ALL 2723 ENTITY CHECKS PASSED`. Every figure in the body matches. The prepr figure was not re-run and is cited from the body.
- RESULT null controls: the body's round-2 controls are inside the passing arms. They are: `phase_hours not in plan["generated"]["model"]` and no "plan model)" on the fixture page; `check_plan(p2) == []`; and `beyond == 0` with no "more group(s) belong" text.
- RESULT merge: `git merge-tree --write-tree origin/main 6804e9c5a29946cbef4722088b1f668de6a246a8` exits 0, no conflict (ev/merge-tree.txt).
- RESULT VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff (ev/untouched.txt).
- Finder's harness: none was named. This is an owner-directed instrument group, and the harness is each carry's own self-test arm. The phase_hours end-to-end control came from the round-1 reviewer, and its arm is now in the tree.
- Head re-read: the PR head is 6804e9c5a29946cbef4722088b1f668de6a246a8, and the body's `## Head` names it. The head is a merge of the authored head 11e9a4e9644e9a468dd2522f03a8450fbed23731, and the delta diff holds only the three files above.
- CI: `merge_train.py classify 6804e9c5a29946cbef4722088b1f668de6a246a8 --pr 3676` printed `WAIT 6804e9c5a29946cbef4722088b1f668de6a246a8 pending: gate red: none` on every poll from 00:23Z to 00:55Z, when polling stopped after 30 minutes (ev/classify-log.txt, ev/classify-last.txt). Per the orchestrator's NOTE (inbox CMD 1), the runs at this head were cancelled to free runners and are being re-run. A cancelled run is a wait, not a red. The owed-reds set is in ev/owed-reds.txt; no red is present.
- Comms: seat_comms init and heartbeat ran. The inbox delivered CMD 1 NOTE (the CI cancellation), which was applied.

## Findings

none
