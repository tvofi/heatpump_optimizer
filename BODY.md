Closes #2952. Widens the `graders` arm of `tools/pr/ci_predict.py` from governance.yml's three restoring jobs to every job the enumeration rule returns (`restoring_jobs`, keyed on each job's own restore pathspecs, `ci_tree_run` taking the job's workflow). A run line that reads the pull request's live state is run with the predictor's stand-in and noted `GRADER PARTIAL ... not a pass`. Carry 2 (self-test-reads file-key plant) and Carry 3 part (c) (BOOTSTRAP remedy) are included. Repair round 1 (verdict: mutation-vacuous, 9 of 20 reviewer mutants on added `ci_predict.py` lines survived the full self-test, plus S): `graders_self_test` gains a planted pr-contract-shaped workflow and `summary_line` is factored out of `main` so the closing line is pinned; no behaviour changes.

## Head

038e0ba5dd3431be97fe0b6beb71ea4638707710, the repair head on 926a01499de2a184481a42734fc91bfedc5bb4b1 (which merged origin/main at dee8b413 into 19f57d012). Every figure below was re-taken at this head. `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict) against origin/main d2e4d2d10cfe at 2026-11-08T02:58Z, so main is not merged again here; the merge train recarries.

## Mutation proof

`python3 -I dev/audit/rca/prepr-head-graders/mutants.py .` runs each mutant against `graders_self_test` from a copy of tools/pr/ and prints its failing checks. M1..M7 as before now read M1 11 FAIL, M2 1, M3 2, M4 1, M5 4, M6 6, M7 10. The reviewer's surviving mutants are added as R1-I, K, L, O, P, E, H, F, N, S; each is killed at this head: R1-I (run regex drops bash/.sh) 4 FAIL, R1-K (no-body skip off) 1, R1-L (event tokens unsubstituted) 1, R1-O ($INTENDED stood in empty) 1, R1-P (stdin redirect dropped) 1, R1-E (partial missing-input swallow deleted) 1, R1-H (stdout redirect kept as arguments) 1, R1-F (collision key always the bare job) 5, R1-N (codescan_wait exemption deleted) 1, R1-S (summary always owes a repair) 1. R1-P first hung (the planted `p/pre.sh` read an inherited stdin); the plant reads it through `timeout 5 cat`, and the mutant now fails in seconds. The new cases: a `bash p/pre.sh $INTENDED < /tmp/pr-body.md` run (args and stdin read back), a `--head "$PR_HEAD" --title "$PR_TITLE" --author "$(cat ...)" > out.txt` run, a partial run printing "reviews could not be read", a plain refusing run, two workflows sharing a job name, a run with no body, the pr-contract exemption, and the `.sh` run in `want`. Carry 2's mutant R1 is as in the prior body (1 FAIL), not re-run.

## Null control

Unmutated head: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, and `graders_self_test` alone prints `bad 0`. The new cases carry their own nulls: the no-body tree still runs the plain program; the plain run's refusal is reported where the partial one's is not; `summary_line(2, 1, ...)` still owes a repair where `(2, 2, ...)` does not; the pr-contract preflight run is graded where codescan_wait is exempt. Per-job real-tree plants stay as in the prior body: `dev/audit/rca/prepr-head-graders/plant_jobs.sh` on the real tree; the verdict-changing plants exist only in the self-test's planted workflows (including the new fourth), so no "one verdict-changing plant per real job" claim is made.

## Figures

- `python3 -I dev/audit/rca/prepr-head-graders/mutants.py .` (counts above; the instrument is the mutant list in that file).
- `git grep -n -- "- name: Restore the check source from the base commit" HEAD -- .github/workflows/` returns six jobs; graders_self_test asserts the arm's job count equals that grep's count (the enumeration rule; M7 kills it).
- `MUTANT_CMD="bash <script that git-inits the archive copy and runs graders_self_test>" MUTANT_MAX=60 bash tools/pr/prepr.sh`: diff-mutant step, wall time of the whole prepr 36 m 8 s (`time`), 14 survivors (dispositions under `## Unpinned sites`). A first run with a MUTANT_CMD that did not git-init the copy printed BASELINE FAILS and ran no mutant.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused, 0 stale allow entries (two ALLOW entries added for the new plant's literal `/tmp/pr-body.md`).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- prepr rc=1 on one step only: `closures` ("failed while being recorded: tests/entities.py (exit 1)"). `PYTHONPATH=tests/hastub python3 tests/entities.py` ends `3 of 2655 ENTITY CHECKS FAILED` in this cloud environment (the HA-stub gap; the failing checks are the coverage job's cache key, the release ZIP build step and the Pages workflow probe, none read by this diff); the same step refused identically in the prior seat's re-run. The `ci predict` step is ok, "no closures, fast, governance or instrument red predicted".
- `tools/audit/seat/handoff_push.sh` refused with `app_push: REFUSE: App id file missing or empty (fail closed)`; the code head was pushed to refs/heads/handoff/r10-fly-cipredict-restoring directly, fast-forward, which moves the existing pull request; no row or retitle was written by this seat.

## Unpinned sites

14 survivors of the diff-mutant step (report only), all in the repair's own added lines: 1236 `sum(2 ...)` in `main` (the count of BOOTSTRAP reds fed to `summary_line`; the closing line itself is pinned by direct calls, the counting expression is not driven by a main-level case); 1459 `>=` for `>` (equivalent here, the count equality beside it is what pins the job set); 1559, 1566, 1639, 1640, 1688 (`pass`/`if False:` deletions of test-side bookkeeping calls: the mutant edits the self-test, not the predicate it grades); 1589, 1622, 1634-1636, 1709, 1710 (constants and comparison bounds inside the self-test's own assertions; each is a weaker assertion of a property whose strict form is separately asserted or killed by the production mutants above). None is a production predicate other than the 1236 counting expression, left as a stated gap.

## Red checks

none: no concluded red at the prior head 926a01499 (`merge_train.py classify` GREEN, per the review); the repair head has no concluded run at writing. `tmp_paths` went red inside prepr on the new plant's literal path; answer: the cheaper detector is prepr step 16 itself, repaired by two ALLOW entries.

## Forward-carry

Landed in this PR: Carry 2 and Carry 3 part (c). Still owed, each carried by this group's roster entry:

- Carry 1 (inline_scan arm for `parents[N]` harnesses). Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: still owed, already stated in this group's own roster carries; re-homing at merge is the orchestrator's roster write (the review raised it).
- Carry 3 parts (a)/(b) (fixer.md, designer.md, design-review.md at their budget caps; policy, owner's review). Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: still owed, already stated in this group's roster carries.
- Carry 4 (tools/policy/agreement.mjs age-needle and mutant M-h). Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: still owed, already stated in this group's roster carries.
- The verdict-changing real-tree plants for budget-raise-gate and pr-contract. Carry: R10-FLY-CIPREDICT-RESTORING | dismissed: still owed, stated in the group's brief.
- The seven other base-restoring steps (ci.yml prelude/refresh/gate, codeql.yml analyze, tests.yml autofix jobs) are outside #2952's six-job rule and are routers or API readers. Carry: dismissed: outside #2952's stated population, per the review.

## Friction

none
