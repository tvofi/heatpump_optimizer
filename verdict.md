Fix review: merge b173995ad456981d0736b74066126207f16949aa

bus-nonce: 7ad5e84cc941d5d52f21211c8ebd90ea

## Findings

- The round-1 surviving mutants are still alive at this head. R9: dropping `policy_refusal`'s ` or ms == "BLOCKED"` leaves 380 checks, 0 failed. R5: changing `rd != "CHANGES_REQUESTED"` to `True` leaves 380 checks, 0 failed (ev/mutants.txt). R3 and R8 were not re-run. All four are already written in carry 21 of R10-TRAIN-OVERLAP-GRADE at handoff/audit-r10-roster 78c0bb77 (ev/roster-carry21.txt). Carry: R10-TRAIN-OVERLAP-GRADE
- The `_batch` admission head-set seam (`self.required()` at merge_train.py:3054 feeding `admit`) is the P34 sibling. It is dispositioned to carry 21, which states its control as a precondition, and it is not settled here. Carry: R10-TRAIN-OVERLAP-GRADE
- Part (3) of the brief, carries 7 and 10, is not built in this PR. It stays in the group's roster entry as written. Carry: R10-TRAIN-OVERLAP-GRADE
- Carry 2's "pass --approval-carry in the live launch" belongs in the orchestrator's launch line, not in this diff. Carry: R10-TRAIN-OVERLAP-GRADE
- No finder harness exists: the instances are train logs on the orchestrator's host, and the body discloses this. The self-test fixtures are the measurement. The only instrument I built is a one-off mutation driver (scratchpad mut.py: exact single-occurrence replace in place, run `--self-test`, restore). It is not in the tree. Carry: dismissed: instrument carries with no committed finder harness; the fixtures are the measurement, as the body's Friction item records

## Evidence

- Round 3. Measured at head b173995ad456981d0736b74066126207f16949aa. At verdict time this is still the live head of fix/r10-train-overlap-grade-p3 and of refs/pull/2992/head (ev/head-live.txt).
- The round-2 block (ci-red, instrument-self-tests caused by queue_pre_flight's fixture) is cleared at this head:
  - `python3 tools/audit/seat/queue_pre_flight.py --self-test` prints `queue_pre_flight self-test: 44 checks, 0 failed` (ev/selftest-head.txt).
  - Q1 (the fixture's `--is-ancestor` stub removed) gives 44 checks, 1 failed: `... HEAD is not origin/<branch> still PARKs`. This is the round-2 red, reproduced.
  - Q2 (M10 applied to merge_train.py, queue_pre_flight self-test run) gives 1 failed: the new ancestor twin arm.
  - The body's `## Red checks` names the check, says this diff caused it, and gives the cheaper detector with its standing cost. Step 11 is answered.
- RESULT head self-tests: `merge_train self-test: 380 checks, 0 failed` and `queue_pre_flight self-test: 44 checks, 0 failed` (ev/selftest-head.txt).
- RESULT base self-tests at 507a9ec2: `355 checks, 0 failed` and `43 checks, 0 failed` (ev/checks.txt). All four figures match the body.
- RESULT figure: `git diff 507a9ec2...HEAD -- merge_train.py | grep -c '^+.*check('` prints 19, and the same command on queue_pre_flight.py prints 1. Both match the body.
- RESULT mutation proof, re-run by me (ev/mutants.txt).
  - The round-2 survivors are now pinned and each is killed: S1 1 failed, S2 2 failed, S3 1 failed.
  - The body's mutants are killed: M10 1, M1 10, M2 2, M4 6, M7 2, M9 1.
  - M1 and M4 kill more than the body's 7 and 5 because of the new round-2 arms. The body says those two counts were taken against the 376-check head.
  - Not re-run this round: M3, M5, M6, M7b, M8 and M12. Round 2's review killed them at e456ff01, and ee438e5 changes only self-test and fixture lines.
- RESULT class rule, the body's own commands (ev/checks.txt), every site in the diff or dispositioned:
  - Merge sites: 2 (1263 and 2010).
  - `.required(`: 3 (1883 serial pr_head, 2072 policy_refusal pr_head, 3054 _batch, carried).
  - `self.sweep_bots()`: 6.
  - `.freeable(`: 2 (merge_train.py:1210, queue_pre_flight.py:242). Both are now pinned.
- Resolution delta: 920d365 has the same tree as the authored code head ee438e5 (6be2cb70). b173995's tree equals `git merge-tree --write-tree 920d365 origin/main` (7e0acd2c). So the main merge carries no hand resolution.
- Step 13: `git merge-tree --write-tree origin/main b173995` exits 0, with origin/main at e77418f9, which is the head's merge base. There is no conflict.
- Gate checks at the head:
  - `tests/structure.py` prints STRUCTURE RATCHET PASSED.
  - `PYTHONPATH=tests/hastub tests/harness_headers.py` prints ALL 112 HARNESS HEADER CHECKS PASSED.
  - `tests/env_drift.py --claims-only 507a9ec2` exits 0.
- Steps 4 and 5: the three-dot diff covers 4 files. None is a claim file, golden, VERSION, the manifest or RELEASE_NOTES.md.
- Role files: `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Step 10: carry 21 is in the tree at 78c0bb77, which is an ancestor of the handoff/audit-r10-roster tip 5a8c3e64. It states the admission seam's control as a precondition (ev/roster-carry21.txt).
- Step 14: no budget, ledger, closures, INERT, golden or archscore file moves. The new arms add checks, and they are earned by the pinned survivors.
- Step 15: round 2 adds only self-test arms and a fixture branch. These are sound.
- Review packet: no refusals and no advisories. carry_audit routes 5 of 5. figure_lint gives 11 resolved, 2 unverified (git flags), 0 refused.
- CI on this head, re-read live from the check-runs API at about 14:50Z (ev/ci.txt). No check is red.
  - `governance / instrument-self-tests` (job 124116570542) concluded success at 14:46:47Z. This was round 2's red check.
  - Also success: tests / fast (3.14), closures, coverage, coverage-ratchet, mutation, closure-scope, typing, browser, briefs, arch-instrument, lane-proofs, graders-head-copy, env-matrix, arch-score, policy-docs, delivery-status, nightly-status, wave-script, budget-raise-gate, hassfest and validate-hacs.
  - CodeQL is neutral.
  - Still in progress at verdict time: `codeql / Analyze (python)` and one `prelude` run of the refresh workflow.
- Step 11: the body answers the one red this PR ever had (instrument-self-tests at e456ff01). No check is red at this head.
