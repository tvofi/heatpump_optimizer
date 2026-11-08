Fix review: blocked 266ef2802f7b12544435faa10e27a05663d4e076 class-open: orchestrator_tick.py reads roster_lib.CLOSED_STAGES and its self-test fails at this head (PLAN: deferred E stays deferred)

bus-nonce: 0eb69f6d2ad441a1217cc2a6ab064ccb

Round: first.

## Block

- Change (b) adds `refused` and `deferred` to `roster_lib.CLOSED_STAGES`. That set has a reader the body does not handle: `tools/audit/seat/orchestrator_tick.py`, whose PLAN section stops walking a deferred group. At this head `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` prints `FAIL PLAN: deferred E stays deferred` and `283 checks, 1 failed`. At the merge base 4fe7d5934b0a it prints `283 checks, 0 failed` (ev/orchestrator_tick-head.txt, ev/orchestrator_tick-base.txt). Null control: at the head with only `CLOSED_STAGES` reverted to `DONE_STAGES + ("absorbed",)`, the tick prints `283 checks, 0 failed`, so this diff causes the failure. That is the required red `governance / instrument-self-tests` (job 128731174619), and through pr-contract it makes the required `gate` red too. The body names this seam and says the code fix is still owed: either the tick reports a deferred or refused group as closed, or the owner decides the "stays deferred" line is no longer wanted and the fixture changes. Until one of those is pushed, the class is not closed at this head. The body's class-(b) enumeration (`grep -rn "is_open\|CLOSED_STAGES\|DONE_STAGES"` over tools, tests, .claude, dev/audit/harnesses) should return this file. Re-run it after the fix and confirm that every reader it returns is either in the diff or given a disposition. Carry: R10-FLY-REPLAN-DEFECTS

## Findings

- Follow-up: no local detector runs `orchestrator_tick.py --self-test` on a `roster_lib.py` change. `tests/closures.json` puts the tick in no script's closure, so only the roughly 13-minute `instrument-self-tests` run catches it. The body states the cost test and builds nothing. The fixer of this group should either add the closure edge (roster_lib.py to the tick self-test) with its measured gate cost, or record the refusal, as defect-root-cause.md requires. Carry: R10-FLY-REPLAN-DEFECTS

## Evidence

- Head reviewed: 266ef2802f7b12544435faa10e27a05663d4e076 (ev/HEAD.txt). `## Head` in the body names this SHA. Merge base 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50.
- `git merge-tree --write-tree origin/main <head>` exits 0: no conflict.
- Role contract is current: `git diff <mb>...origin/main -- dev/governance/roles/` changes only orchestrator.md and standing-dispatch.md, not fix-review.md.
- `merge_train.py classify 266ef2802f7b12544435faa10e27a05663d4e076 --pr 3326` exits 1: `RED 266ef2802f7b12544435faa10e27a05663d4e076 pending: none red: gate`.
- Self-tests at the head all exit 0: replan.py (`self-test: 0 failed`), roster_lib.py (68 checks, 0 failed), roster_sync.py (95, 0), roster_edit.py (244, 0), handover_prompt.py (17, 0).
- Mutation proof, re-run by this reviewer with REPLAN_MUTATION_CHILD=1 and both files restored afterwards:
  - CLOSED_STAGES reverted: replan `refused:` and `deferred:` rows go red (`self-test: 2 failed`).
  - Plain `g.startswith(p)` stem match: the lane look-alike row goes red (`self-test: 1 failed`).
- The body's `## Red checks` names instrument-self-tests, gate and pr-contract with answers, and digest reds match. CI's mutation lane is green. The figures table (R10-I18N-DE lane and start, groups_open 56 to 55) depends on a roster copy that is not in the tree, so it was not re-derived. Carry: dismissed: evidence, not a finding
- `tests/entities.py` did not run in this container: under venv-ci python3 it fails with `ModuleNotFoundError: homeassistant`, and under /opt/hpo/venv-ha with `ModuleNotFoundError: paho` (ev/entities-venv-ha-tail.txt). It is not clean, and that is an environment fault, not this diff.
- No VERSION, manifest or RELEASE_NOTES.md change. The delivery row dev/programme/delivery/3326.md is in the diff. No new files beyond that row, and no budget file touched.
