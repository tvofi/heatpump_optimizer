`tests / nightly-status` graded main red with "NIGHTLY FAILED: slow failed in the last verification dispatch" because the check judges the newest CONCLUDED nightly run, while the ~3.5 h nightly is routinely still in flight when it reads: dispatch 42235215315 failed `slow`, newer dispatches 42242870295 and 42247578523 passed `slow` while their mutation lanes ran on, and the check kept naming the stale failure. Fix (`tests/nightly_status.py`, `verdict`): a failed job is superseded only when a strictly newer in-flight run has already concluded the SAME job `success`; pending, failed, skipped, absent or older-run jobs supersede nothing, so a really red lane stays red. `main` fetches the in-flight run's jobs only when the concluded run has failing jobs. The lane itself (`nightly.yml`) is untouched: the scheduled-run failures 41555367389, 41749544997, 41943946464 are earlier real `slow` failures already answered by later green runs; this change grades only the stale-failure case. The main-wide `instrument-self-tests` 30-min cancel is f-3245-nightly's (handoff/r10-process-slim, `timeout-minutes` 40), not duplicated here.

The delivery row `dev/programme/delivery/<N>.md` is added by the opener, which alone knows the pull-request number.

## Head

99556a1e3d28b7e5aa4ce2133fc4af2e62ebd2c6 (merge of origin/main 28482eceeb6b9809e44b12d80fc994282cc21645, 2026-11-06T22:17Z, into the first seat's d0be1c5cd25970853ebbea50645edf772da2d8c8; the code diff is unchanged by the merge, three-dot 2 files, +73/-1).

## Mutation proof

Predicate mutated in `verdict` (`if bad and in_flight is not None ...` to `if False and bad and in_flight is not None ...`), `python3 tests/entities.py` at the head: 1 of 2638 ENTITY CHECKS FAILED, check name "a failed lane is superseded only by a NEWER in-flight run that concluded the same job green; every other arm stays FAILED", states `superseded: FAILED` instead of PASSED. Restored: ALL 2638 ENTITY CHECKS PASSED. The new check was written first against the unfixed `verdict` (no `in_flight_jobs` parameter), where it cannot pass.

## Null control

The same check drives four arms that must stay FAILED at the head (and are FAILED unmutated and mutated alike): the same failure with nothing newer, with a newer `slow` failed, with a newer `slow` still pending, and with a newer in-flight run that is OLDER than the failed one. Only the `superseded` arm flips (FAILED at the baseline predicate, PASSED with the fix), so the flip is the fix and not a general loosening.

## Figures

- `python3 tests/entities.py` at 99556a1e: ALL 2638 ENTITY CHECKS PASSED (rc 0); same command with the predicate mutated: 1 failed, rc 1.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at the first seat's head: MODE: SCOPED, runs `tests/entities.py` and `tests/harness_headers.py`.
- `git diff --stat origin/main...HEAD`: 2 files, 73 insertions, 1 deletion; `git diff origin/main -- VERSION RELEASE_NOTES.md tests/golden .github | wc -l` prints 0 (no version, claim, golden or workflow change).

## Red checks

none. A red this head can show is `governance / instrument-self-tests` cancelled at its 30-min timeout: class main-wide, cure R10-PROCESS-SLIM #3245 (timeout 40); not caused by this diff.

## Forward-carry

none

## Friction

none
