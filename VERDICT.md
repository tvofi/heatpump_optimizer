Fix review: merge 47810de38785ec8563d97c89d5c6dfdb822c6288

bus-nonce: cc77aa1364442dd0f6c2443647115593

## Summary

Round 1, the first adversarial fix review of #3259 (R10-HOTFIX-GATE-STALE-JOBS part 2), measured at head 47810de38785ec8563d97c89d5c6dfdb822c6288 from a detached worktree. The merge base is 57958d6a44c4f489384705ba64e8f65a8507f6b7. Each of the three carries is answered. e67341cc was already built by #3205 and I verified it here. e350d851 is built, with a failing test, a mutation proof and null controls. d0916ca4 is not built, and the body records a reason. The code supports that reason: pr-contract runs only after every unit job, and gate turns red on a real failure without waiting. So a red left off the list cannot merge green. That case is covered by fix-review step 11's live re-read.

## Findings

- The job-level `skipped`/`cancelled` exemption in `settled()` (codescan_wait.py, added line) has no test. Mutant M5 removes it, and all 20 self-test checks still pass (ev/mutants.txt). Harness: `python3 -I tools/ci/codescan_wait.py --self-test`. Metric: checks failed, 0 with the mutant and 0 without it. Perturbation: the M5 sed in ev/mutants.txt. The branch is reachable only for an `Analyze` job skipped or cancelled at job level. codeql.yml gives that job `if: ${{ !cancelled() }}`, so this happens only when the run is cancelled, and pr-contract (ci.yml:266, `!cancelled()`) does not run then. The behaviour also matches the base: a cancelled leg is dropped, not passed fresh. This is a test gap, not a fail-open. Carry: R10-HOTFIX-GATE-STALE-JOBS | dismissed: unreachable while pr-contract runs, same as base behaviour; a test would pin a path no live run takes

## Evidence

- Head: the body's `## Head` names 47810de38785ec8563d97c89d5c6dfdb822c6288, the head I measured. It also has a stray line holding 4f478a78c9c72d1976e9eefe03421df96ce287f0, the fix commit, which is harmless. tools/ci/codescan_wait.py is byte-identical between 4f478a78 and the head, so the body's figure for 4f478a78 holds at the head.
- RESULT: codescan_wait self-test at the head: 20 checks, 0 failed (ev/head-runs.txt).
- RESULT: gate self-test: 57 checks, 0 failed at both the merge base and the head (the diff does not touch gate.py). The body measured at 4b7e1770, which is an ancestor of the head, and got the same figures.
- RESULT: finder's harness dev/audit/harnesses/r10_gate_stale_jobs/harness.py: mismatches 0 of 9 at both the merge base and the head. Its rows include prelude listed unfinished, own ABSENT (pr-contract absent, 20 s), real red unwaited (FAIL, waited 0 s), and pending past the bound (FAIL). These are the null controls for e67341cc. bc806747b is an ancestor of the merge base, so it was built by #3205 as the body says (ev/base-runs.txt).
- RESULT: mutation proof (ev/mutants.txt). M1, the body's mutant (`if settled(jobs)` changed to `if True`), makes checks 18 and 19 fail: 2 failed. M2 restores the base single read and fails 18 and 19, which shows the test fails at the base. M3 (the exhausted bound returns instead of FAIL) fails check 19, so exhausted waiting fails and never passes. M4 (settled ignores the step row) fails 18 and 19. M5 survives (finding above). M6, which drops the job `status` check, survives too. I count M6 as equivalent: `legs_uploaded` reads only the analysis step's conclusion, so a leg whose step has concluded is final either way. The file was restored after each mutant, and `git status` is clean.
- Budget: the own-run poll uses the same `stop` as step 4, so WAIT_MAX_S = 600 s bounds the whole wait (self-test 17). That fits inside pr-contract's `timeout-minutes: 20`.
- d0916ca4: ci.yml:265 makes pr-contract need prelude, tests, codeql, governance, hassfest, validate, kernel-points, arch-score and budget-raise-gate. gate.py's `lag_bound` returns 0 unless every reason is OWN_PENDING or OWN_ABSENT, so a completed failure makes gate red with no wait (harness row 41870522291 FAIL). The RCA's 143-probe figure is quoted from dev/audit/rca/r10-gate-stale-jobs.md section 3. I did not re-run the probe.
- Class: the RCA's section 3 table names exactly two fail-open rows, the codescan_wait own-run path and the pr-contract red list. The body dispositions both.
- Scope: `tests/closure.py select` prints `MODE: FULL -- every test script runs`, so CI ran the full suite.
- CI: `merge_train.py classify` exited 0 with `GREEN 47810de38785ec8563d97c89d5c6dfdb822c6288 pending: none red: none`. Every check-run page at the head, read through the commit API, shows 31 completed success and 17 completed skipped, and nothing failed, was cancelled or timed out. `## Red checks: none` is correct.
- Merge: `git merge-tree --write-tree origin/main 47810de3` (main 9cbd7dd0d) exited 0 with no conflict.
- Untouched: the three-dot diff touches only tools/ci/codescan_wait.py and dev/programme/delivery/3259.md. That is the delivery row; VERSION, the manifest, RELEASE_NOTES.md, the claim files, custom_components/ and any budget file are untouched. The brief says this PR changes .github/workflows, but the three-dot diff touches no workflow, so no workflow guard is weakened.
- Roles current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
