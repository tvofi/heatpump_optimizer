Fix review: blocked e456ff01323580d4390f964483a17dbdb6cff5bf ci-red: governance / instrument-self-tests fails on queue_pre_flight self-test 1 of 43, caused by this diff's Train.freeable ancestor check

bus-nonce: ef0c5a905a607435061c32014019e0cc

## Block

Round 2, at the same head as round 1 (e456ff01323580d4390f964483a17dbdb6cff5bf). The head is still live on fix/r10-train-overlap-grade-p3 (ev/head-live.txt).

The round-1 block (carry-missing) is cleared. Carry 21 of R10-TRAIN-OVERLAP-GRADE at handoff/audit-r10-roster 78c0bb77b052649fe08c99df98b226b8e3cb8f8a records the `_batch` admission head-set seam. Its control is stated as a precondition, and it lists the round-1 survivors R3, R5, R8 and R9 (ev/roster-78c0bb77-carry21.txt). 78c0bb77 is an ancestor of the roster tip.

New block: the head's `governance / instrument-self-tests` check (job 124070275423) concluded **failure** at 13:11:17Z, with `queue_pre_flight self-test: 43 checks, 1 failed` and `##[error]Process completed with exit code 1.` (ev/instrument-self-tests.log). The failing check is `... and one whose HEAD is not origin/<branch> still PARKs (unpushed work)` (tools/audit/seat/queue_pre_flight.py:429).

This PR causes the failure:
- I ran `python3 tools/audit/seat/queue_pre_flight.py --self-test` at the head and got 43 checks, 1 failed (ev/qpf-head.txt).
- I ran the same command with only `merge_train.py` swapped back to 507a9ec2 and got 43 checks, 0 failed (ev/qpf-base.txt).

queue_pre_flight.py:241 calls `Train.freeable`. Its fixture stub answers any argv containing `merge-base` with rc 0 (queue_pre_flight.py:326). So the new `merge-base --is-ancestor` probe in `freeable` reads "HEAD 1.. is an ancestor of origin 2..", and the holder is freed instead of parked.

This is also an open class (step 6). The body's class rule for P184 lists no caller of `Train.freeable`, and queue_pre_flight is a second caller that the diff neither touches nor dispositions.

To clear: update queue_pre_flight's fixture so `--is-ancestor` answers non-ancestor for that arm. Add a twin arm in which an ancestor holder passes under `--free-holders`, mirroring merge_train's P184 pair. Then name the red check and its answer in the body (defect-root-cause.md's second trigger). The cheaper detector is `python3 tools/audit/seat/queue_pre_flight.py --self-test`, which takes seconds locally. The body's `## Red checks: none` predates CI.

## Findings

- New surviving mutant: in `land`, `if approval and not carried:` changed to `if approval:` leaves 376 checks, 0 failed. Nothing pins that the approval carry is offered only once per landing. Owed: an arm in which a second policy refusal after a carried approval parks without a second carry. Carry: R10-TRAIN-OVERLAP-GRADE
- New surviving mutant: in `policy_refusal`, the green set `("SUCCESS", "SKIPPED", "NEUTRAL")` narrowed to `("SUCCESS",)` leaves 0 failed. No arm has a required context reading SKIPPED or NEUTRAL, so such a context would read as pending and retry forever without a test noticing. Owed: one arm with a SKIPPED required context and a missing review that parks. Carry: R10-TRAIN-OVERLAP-GRADE
- New surviving mutant: `policy_refusal`'s `n not in self.ignore` dropped from the red list leaves 0 failed. No arm pins that an `--ignore`d red context does not park the car. Owed: one null arm. Carry: R10-TRAIN-OVERLAP-GRADE
- Round-1 survivors re-confirmed at this head: R3 (serial's `except Stop:` sweep, my R-a), R5 (CHANGES_REQUESTED, R-d), R9 (BLOCKED+APPROVED, R-e) and R8 (`_critical` except, R-j). All are already written in carry 21 at 78c0bb77. Carry: R10-TRAIN-OVERLAP-GRADE
- No finder harness exists: the instances are train logs on the orchestrator's host. The body discloses this, and the fixtures are the measurement. The only instrument I built is the mutation driver, a one-off scratch script outside the tree. Carry: dismissed: instrument carries with no committed finder harness; the fixtures are the measurement, as the body's Friction item records

## Evidence

- RESULT head self-test: `merge_train self-test: 376 checks, 0 failed` (ev/selftest-head.txt), as the body says.
- RESULT mutation proof, re-run by me with exact single-occurrence replaces into a copy and `--self-test` (ev/mutants.txt). Every body mutant is killed: M1 (7 failed), M2 (2), M3 (2), M4 (5), M6 (3), M7 (2), M8 (1), M9 (1), M10 (1) and M12 (1). My own extras killed: R-b swept-once (2), R-f wait->park (2), R-i unreadable->park (1), R-k BOT returns None (1), R-l batch post-sweep (1) and R-m freeable unreadable (1). Survivors are listed under Findings. M5 and M7b were not re-run.
- RESULT gate checks at the head: `tests/structure.py` prints STRUCTURE RATCHET PASSED; `tests/harness_headers.py` prints ALL 112 HARNESS HEADER CHECKS PASSED; `tests/env_drift.py --claims-only 507a9ec2` exits 0 (ev/checks.txt).
- Steps 4 and 5: the diff touches no claim file, golden, VERSION, manifest or RELEASE_NOTES.md. The three-dot diff covers 3 files.
- Step 13: `git merge-tree --write-tree origin/main HEAD` exits 0 with tree e96e69f3, where origin/main is 1afdef88. There is no conflict.
- Role files: `git diff <mb>...origin/main -- dev/governance/roles/` is empty.
- CI re-read live from check-runs: `governance / instrument-self-tests` failed (the Block). Successes include tests / fast (3.14), closures, mutation, closure-scope, typing, browser, briefs, env-matrix, arch-score, policy-docs, delivery-status and nightly-status. Still running at verdict time: tests / coverage, codeql / Analyze (python) and a second prelude.
- Step 14: the body reports archscore dS +0.0000 NULL, and no budget, ledger, closures or INERT moved.
- Step 15: the P34 head-set read in `serial` and the widened carry through `_carry_owner_approval` are sound.
