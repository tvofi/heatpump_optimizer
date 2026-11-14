Fix review: merge bc85e0900add6d276b90ba0f83fa6272b92e8d9c

bus-nonce: 67f0e88d931d09bbb0335f5af869c62b

Round 1 (handoff review; no pull request exists yet, so there is no review packet and no CI run to read: no check went red at this head and no `## Red checks` answer is owed).

## Evidence

- RESULT head measured: bc85e0900add6d276b90ba0f83fa6272b92e8d9c, equal to the body's `## Head`; merge base 9fdba3b8547f9762438dc19b98b310a63d34dcb1 (ev/HEAD.txt).
- RESULT role contracts current: `git diff <mb>...origin/main -- dev/governance/roles/` empty.
- RESULT diff scope: one file, tests/ci_ratchet.py (+58/-3). `.github/workflows`, tools/ci/gate.py, VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (ev/untouched-paths.txt), as the brief required. PUSH_REPORT_ONLY = {"tests": ("ci-ratchet",)} is at tools/ci/gate.py:74, and its commit ef4556bb42 is an ancestor of the merge base, which confirms the body's departure from the brief ("never built" is stale).
- RESULT self-test at three points (ev/selftest-three-ends.txt): merge base 67 checks, 0 failed; 990dcfaf20 (test only) 71 checks, 1 failed, the run-43602217369 arm with the `(fail closed)` refusal; head 72 checks, 0 failed. This matches the body.
- RESULT mutation (ev/mutants.txt, driver $W/mutate.py, my own run): I re-applied the body's M1-M6 and all are killed with the named FAIL lines and counts the body states. I added five reviewer mutants. R1 (the prelude name check dropped), R2 (all -> any) and R3 (the `tests / *` prefix match disabled) are killed. R4 and R5 survive; both are dispositioned under Findings as equivalent on the current workflows. Killed 9 of 11.
- RESULT null control: the body's four nulls are in the self-test and green at the head. M2, M3, M4, R1, R2 and R3 each redden one of them, so each null moves under its own perturbation.
- RESULT gate self-test at the head: `gate self-test: 106 checks, 0 failed` (equal to the body).
- RESULT scope: `closure.py select --diff <mb>` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (equal to the figure block). tests/entities.py gives `ALL 2725 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt). `STRUCTURE RATCHET PASSED` (ev/figures.txt).
- RESULT merge with origin/main: `git merge-tree --write-tree` gives rc 0, no conflict (ev/merge-tree.txt).
- Claim files: the diff touches no golden or claim file, and no solver code, so env_drift has nothing to compare.
- Not re-derived: the body's window-replay figure `21.0` and the 9fdba3b854 REFUSED replay. They come from a scratch probe the body says was not landed, so I have no enumerator for them. The self-test arm for run 43602217369 reproduces the refusal and the exclusion that replay showed. I also could not read the recorded job listing of run 43602217369 (14 jobs) from this seat, which has no actions API. I checked the fixture's shape against ci.yml: `tests` needs `prelude` with no status function, so it is skipped; `gate` and `sweep-self` use `!cancelled()`, so they are cancelled. Both match the fixture.
- Class enumeration: the body names no enumeration rule. The predicate's domain is the CI run kind × the prelude conclusion × the tests-job conclusions. The nulls cover prelude success, a tests job never completed, a failed tests caller and an absent tests job. The two unpinned cells are under Findings.
- owed-reds set read (ev/figures.txt). There is no CI at this head, so no red is owed.

## Findings

- Residual: surviving mutant R4 (the `kind == "CI"` guard dropped) is equivalent. Pre-umbrella Tests runs come from tests.yml, which has never had a top-level `prelude:` job (`git log -S` finds none), so `_cut_at_prelude` is false for every Tests-kind run. Carry: dismissed: equivalent mutant, no Tests-kind run can carry a prelude job
- Residual: surviving mutant R5 (a `cancelled` tests job accepted as `skipped`) is unpinned. A `tests / *` job that is cancelled after it completed is already excluded by the pre-existing cancelled arm. The `tests` caller (ci.yml `needs: prelude`, an `if:` with no status function) is skipped, never cancelled, when its prelude is cancelled. If ci.yml ever gives that caller `always()` or `!cancelled()`, the predicate fails closed, the conservative direction, and on push it is report-only under PUSH_REPORT_ONLY. Carry: dismissed: equivalent under current ci.yml; a change fails closed and is report-only on push
