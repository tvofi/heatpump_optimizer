Fix review: merge 537d9f048449dc313760a6826a87d496bb4366f8

bus-nonce: 00c3a3dca041dddd1e0dce826a0e1f35

Round 2 (handoff re-review; no pull request yet). Measured head: 537d9f048449dc313760a6826a87d496bb4366f8, the handoff/r10-introduced-reds-barrier tip. The body (handoff-body 65abfeacd6) names this head under `## Head`. This round reviews only the delta fbf6c4dc..537d9f04, as `review_carry.py` prints FRESH-REVIEW and a blocked verdict never carries. The round-1 settlements (policy scope, budget payment, real-data (b)/(c), M1 to M5, M6, M8, M10) are not redone.

## What this barrier requires of a seat

- A fix reviewer blocks on any `governance / instrument-self-tests` step that is red at the head and not red at the merge base, as `merge_train.py classify --pr` and `review_packet.py` read it (INTRODUCED lines). This holds even though the job is outside `owed-reds`.
- "Red" now means any conclusion in `review_packet.RED` (failure, cancelled, timed_out, action_required, startup_failure), not only failure.
- A head job that concluded timed_out while the base's did not is itself an INTRODUCED finding: `(the job concluded timed_out)`.
- A head job still running reads WAIT (rc 3), never GREEN.
- Each of these is a Stop (rc 2), never clean, and the seat re-runs the job or waits: a job-level cancelled, startup_failure or action_required; a red job with no red step; a base job still running; any unreadable read.
- A red inherited from main stays unowed. `bus.sh dispatch` sends an INTRODUCED head back to its fixer as REPAIR-OWED, naming the INTRODUCED lines.

## Findings

none

## Evidence

- Round-1 block (class-open, failure-only domain) is closed. I used the r1 verdict's harness cases (`ev/unguarded-domain.txt` of verdict/3476), re-driven through `introduced_at` by my own driver at both ends (`ev/domain.py`, builder: reviewer; output `ev/domain-both-ends.txt`):
  - At fbf6c4dc, V1 to V4 all read `[]`, which is the defect: a failed job whose step was cancelled, a timed_out job, a cancelled job, and timed_out/cancelled steps inside a failed job.
  - At 537d9f04 they read `['hang']`, `['(the job concluded timed_out)', 'hang']`, a Stop, and `['a', 'b']`.
  - Null controls N1 to N4 read `[]` at both ends: the same step red at head and base, a head that succeeded, the same timeout inherited, and a red only on the push-only drift step.
- My added attacks at 537d9f04 (A1 to A15) all fail closed or read correctly:
  - A hang behind a step already red at the base gives the timeout line alone.
  - A queued or in_progress head gives None (WAIT).
  - action_required, stale, and completed-with-no-conclusion heads are a Stop.
  - A base still running or concluding startup_failure is a Stop.
  - With no base run, a timed_out head counts in full.
  - Unknown or None step conclusions in a red job are a Stop.
  - At fbf6c4dc, ten of these read `[]`.
- Mutation proof, my own 13 mutants plus one in bus.sh (`ev/mutants.py`, output `ev/mutants.txt`, `ev/mutant-bus.txt`, `ev/mutant-r13-raw.txt`). Each was restored by `git checkout`, and the tree was clean after. All are KILLED:
  - R1 RED_CONCLUSIONS reduced to failure only: 3 failed in review_packet.
  - R2 STEP_READ without timed_out: 1 failed.
  - R3 JOB_TIMED_OUT never added: 2 failed in merge_train and 1 in review_packet.
  - R4 timeout not subtracted by the base's timeout: 1 failed (the inherited-timeout null).
  - R5 running head reads `[]`: 2 failed.
  - R6 `selftest_job` max changed to min: 3 failed. This was r1's surviving M7 and is now killed.
  - R7 job-level cancelled/startup_failure/action_required read clean: 4 failed.
  - R8 a red job with no red step not refused: 1 failed.
  - R9 the classify --pr WAIT branch dropped: 1 failed.
  - R10 a base whose conclusion has no reading accepted: 1 failed.
  - R11 `ci_facts`' introduced reading dropped: 1 failed. This was r1's surviving M9 and is now killed.
  - R12 the packet's running-job refusal re-prefixed: 1 failed.
  - R13 `introduced_cmd`'s pending branch dropped: the self-test crashes with TypeError at the WAIT arm, rc 1. My driver first printed SURVIVED because it keyed on the summary line, which a crash does not print. The raw run in `ev/mutant-r13-raw.txt` is the reading.
  - R14 bus.sh ignoring INTRODUCED lines: 1 failed of 175. This was r1's REPAIR-OWED finding and is now killed.
- The body's own mutants N1 to N11 match the shapes of R1 to R3, R5 to R12 and R14 above. The body's kill counts agree with mine where both runs read the same self-test. I did not re-run the body's driver itself.
- Self-tests at the head (`ev/selftests-head.txt`): merge_train 638 checks with 0 failed, review_packet 109 with 0 failed, and bus.sh 175 with 0 failed. All three match the body.
- Real data (a), re-derived live through `review_packet.introduced_reading` at this head (`ev/real-data-a.txt`): 4 INTRODUCED steps, from head job 130479299736 (failure) against base job 130415622883 (failure), in 2.36 s. The body quotes 2.44 s, so the timing figure matches in order only. I did not re-derive (b), (c) or the 0.49 s figure this round, to keep REST reads few. Round 1 verified (b) and (c) on the unchanged failure-domain path.
- Cheap checks (`ev/cheap-checks.txt`):
  - `closure.py select` prints `MODE: SCOPED -- 3 script(s) run`, matching the body.
  - `policy_lint.mjs --budgets` exits 0, `rules_sync.mjs --check` is OK, and `structure.py` exits 0.
  - `owed-reds` lists tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing and validate / validate-hacs, with no instrument-self-tests.
- Policy files are unchanged in this delta, so the round-1 scope assessment stands. The policy text says "step red", and the instrument also emits the job-timeout line. That line is covered because the text defers to `classify --pr`'s INTRODUCED.
- Timeout caps are asymmetric: `governance.yml` gives instrument-self-tests 30 minutes on a pull request and 60 on push. A main whose job runs 30 to 60 minutes would therefore make every PR head that times out read `(the job concluded timed_out)` as INTRODUCED. That errs toward a block, never a clean read, and the INTRODUCED line names the timeout. This is the direction round 1 asked for, so it is not a defect of this change. It was not measured on real durations.
- `git merge-tree --write-tree origin/main <head>` against origin/main 50e4b1aa25 exits 0 with no conflict (`ev/merge-tree.txt`). VERSION, the manifest, RELEASE_NOTES and tests/golden are untouched, and the roles diff from merge-base to origin/main is empty (`ev/version-untouched.txt`).
- CI: no pull request exists, so there is no review packet and no check run at this head to read or wait on. Step 11's red-check answer can only be judged once the PR opens. The two known main reds (tests / fast (3.14), fixed by #3466; governance / instrument-self-tests, fixed by #3474) are inherited, and the body's `## Red checks` names both.
- The forward-carry is none, and the body's single Friction line carries `dismissed:`.
- Head re-read before return: the remote refs/heads/handoff/r10-introduced-reds-barrier is 537d9f048449dc313760a6826a87d496bb4366f8 (`ev/head-at-post.txt`).
