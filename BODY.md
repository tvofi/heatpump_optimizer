R10-PREPR-CAP part 2 (topic r10-prepr-cap-2), round 3 (minimal repair of one defect). Round 2's self-test rows wrote `wiring-body.md` into the tracked `tools/policy/fixtures/policy-rot/prepr/` directory and never removed it, so every prepr run left the worktree dirty and app_push refused. That dirty-worktree defect is fixed: the body file now lives under a `mktemp -d` directory inside the self-test's own temp root (removed by its existing EXIT trap), and a new row asserts `git status --porcelain` is unchanged across the red-check-arm rows, with a null control. Round 2: the round-1 verdict (`Fix review: blocked 755949528b55769455419754a8ba57e5154d5cbd mutation-survivor`) is answered by behavioural self-test rows for the two surviving mutants of carry 5's wiring, and the body's diff figure is restated three-dot. Carries 5, 6 and 7 are otherwise unchanged from round 1.

## Head

New handoff head d5ee2e631d5354c63840808857f1b3755d5db971 (the code head, one commit on r2's handoff head 24bd0ea3e3e29af1f4343da3f4bcec90d28b31c8; the PR head is 755949528b55769455419754a8ba57e5154d5cbd, its ancestor). origin/main is 78dd34354e8300bdff2f660db9cc778ab4a9e4d7 and `git merge-tree --write-tree origin/main HEAD` reports no conflict (exit 0), so no merge was made.

## Carries

Roster ref origin/handoff/audit-r10-roster, stage carries-open, 27 carries (1-based).

- 1-4: answered by #3051 (see round 1's body: `WAIT_BOUND_RC`/`wait_bound_for`, `recorder_python`, the `flock_wrap` refresh arm, `OWED_CARRY`).
- 5 (red-check before the slot, P351): built in round 1 (`reds_arm`, step 1a2, `--body-check --pr-branch`, `body_push.sh`); this round adds its behavioural pins (the verdict's finding).
- 6 (`dq_backticks` heredocs): built in round 1, unchanged.
- 7 (6g CLAIMS_INPUTS trigger): built in round 1, unchanged. The 5 s cost cap on a strings.json-only diff is UNMEASURED: neither this seat nor the reviewer could time 6g (the claims generator needs scipy/homeassistant, absent from the seat venvs), and this pull request does not claim it. Carry: R10-PREPR-CAP
- 8-27: not in this pull request, owed by R10-PREPR-CAP part 3 in roster order. Carry: R10-PREPR-CAP

## Mutation proof

New assertion (`the red-check-arm rows leave git status --porcelain unchanged`), mutant C: the write restored to `: >"$DABS/wiring-body.md"` in the tracked dir. Null (committed head): 460 passed, 0 failed. Mutant C: 454 passed, 6 failed, rc 2, including FAIL `the red-check-arm rows leave git status --porcelain unchanged` (the five other fails follow from the rows' file path being absent). Restored afterwards with `git checkout` and the stray file removed; `git status --porcelain` is empty.
The reviewer's mutants (`verdict/3150` evidence `mutant-a.diff`, `mutant-b.diff`) re-run in detached worktrees at this head both stay killed: A 457 passed, 3 failed, rc 2 (the three step 1a2 rows); B 458 passed, 2 failed, rc 2 (the two `--body-check --pr-branch` rows). Worktrees discarded.

## Null control

The new row has its own null control: a row that deliberately writes a file into the tracked fixture directory must make the porcelain comparison differ (it does; the clean path compares equal). The earlier rows' null controls (stub rc 0 and 3, `--body-check` rc 0) are unchanged.

## Figures

- Self-test at the head: `bash tools/pr/prepr.sh --self-test` prints `460 passed, 0 failed` (r2: 458), and `git status --porcelain` is empty afterwards.
- Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget raised.
- Diff size: `git diff --stat origin/main...HEAD` (three-dot, origin/main 78dd34354e8300bdff2f660db9cc778ab4a9e4d7, at head d5ee2e631d5354c63840808857f1b3755d5db971) prints `3 files changed, 181 insertions(+), 26 deletions(-)`: prepr.sh, body_push.sh and the delivery row.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run`.

## Red checks

none. The whole check-run set of the PR head 755949528b55769455419754a8ba57e5154d5cbd (55 runs across all pages of the check-runs listing: 38 success, 17 skipped) has no run concluded failure, cancelled or timed out; every concluded run is success or skipped.

## Unpinned sites

none

## Forward-carry

Carries 8-27 of the R10-PREPR-CAP entry in dev/programme/rosters/wave-r10-groups.json, per the Carries section above, and the 5 s cost-cap measure of carry 7. Carry: R10-PREPR-CAP

## Friction

none
