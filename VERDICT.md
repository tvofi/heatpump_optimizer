Fix review: merge 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a

bus-nonce: 17080627b73addfe9d2be4af39532a41

## Scope

First round. Handoff tip 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a (branch handoff/r10-hotfix-selftest-scope-union-p1), reviewed three-dot against merge base a7628041dc02e298c5399003d4c0576391dd5c4e, which is origin/main. The diff is 9 insertions to tools/ci/selftest_closures.json and nothing else. BODY.md at handoff-body/r10-hotfix-selftest-scope-union-p1 names the same head.

## Evidence

- No pull request exists yet, so there is no review packet and no CI run to read. Required-check reds and the `## Red checks` answer cannot be judged until the PR opens. The owed-reds set is in ev/owed-reds.txt.
- Finder's harness: the drift step (`selftest_scope check` on main-push strace traces) cannot run off a Linux main push. This reviewer did not have the run artifact (selftest-closures of run 42968587919) because `gh run download` is outside this seat's tools. The measurement used here is my own driver (ev/drift_driver.txt), built independently of the fixer's scratch driver. It takes the base entry plus diagnosis section 5's measured ADD set, with prepr's REM (required-contexts.json) applied, and calls the production `selftest_scope.drift()`. Figures that rest on the artifact itself, rather than on the diagnosis's quoted set diff, are not re-derived.
- RESULT drift@base: 6 refusal(s). The 6 lines match main's job-log lines verbatim. RESULT drift@head: 0 refusal(s). The only note is prepr's over-scoped one, which the brief keeps on purpose.
- RESULT diff-matches-diagnosis: True. An independent per-step, per-field diff of head against base equals the section-5 ADD set exactly, with no removals.
- Null control: 105 of 111 step entries are identical, the step-id sets are equal, and the top-level non-step keys are equal. prepr keeps required-contexts.json and git `fetch`.
- Set check for each of the 7 (step, field) pairs: ADD minus head = [], and ADD minus base = the full ADD list.
- Mutation proof, removing each of the 9 additions one at a time: 8 KILLED, each printing exactly its own UNDER-SCOPED line. 1 SURVIVED: `-prepr.git:branch`. That matches the body's disclosure. `drift()` never reads a table's `git` field; its only readers are the fold at selftest_scope.py:598 and the self-test at :1023 (ev/checks.txt).
- write_table round-trip of the head table is byte-identical, so the format and ordering are those of the production writer.
- Body figures re-derived at this head: `static` prints 111 gated step(s), 0 problem(s). `--self-test` prints 117 checks, 0 failed. structure.py prints STRUCTURE RATCHET PASSED. diff --stat shows 1 file and 9 insertions. "105/105 untouched" corresponds to 105 of 111 steps, with 6 touched. Gate MODE FULL is the body's claim and was not re-run, since CI's heavy runs are cited, not repeated.
- VERSION, manifest, RELEASE_NOTES and both claim files are untouched (ev/untouched.txt). env_drift --all is not owed because no fixture or claim file moves.
- `git merge-tree --write-tree origin/main <head>` exits 0 (ev/merge-tree.txt).
- Roles drift: `git diff <base>...origin/main -- dev/governance/roles/` is empty.
- The forward-carry section says "none". Part 2 is already a live roster group on handoff/audit-r10-roster, so no carry was owed by this PR.
- Head re-read before return: the branch tip is still 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a.

## Findings

- Follow-up: the `prepr.git += branch` addition is pinned by no check: its mutant survives because `drift()` compares files, probes, dirs, index and objects but never `git`. The line is correct per the measured artifact but unverifiable by any gate. Part 2's barrier work should decide whether the drift check reads `git`, or drop the field from the table. Carry: R10-HOTFIX-SELFTEST-SCOPE-UNION
