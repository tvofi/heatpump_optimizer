Closes #2952. Widens the `graders` arm of `tools/pr/ci_predict.py` from governance.yml's three restoring jobs to every job the enumeration rule returns (`restoring_jobs`, keyed on each job's own restore pathspecs, `ci_tree_run` taking the job's workflow). A run line that reads the pull request's live state is run with the predictor's stand-in and noted `GRADER PARTIAL ... not a pass` (budget-raise-gate reads live reviews; its result is never a pass). Carry 1 (self-test-reads file-key plant) and carry 2(c) (BOOTSTRAP remedy on a refusal by a grader the diff itself changes; no verdict or rc change) are included.

## Head

19f57d012c61d71c851df4c42205457fb4117945 (origin/main `4b5d771bdf8f` merged). The mutant table, self-test and plant figures below were taken at `d1f3e2c67d9e` (the same code, before that merge, which touched no file of this diff); `prepr.sh` was re-run at this head.

## Mutation proof

`python3 -I dev/audit/rca/prepr-head-graders/mutants.py .` (M1-M5 existing, M6 and M7 new). Each mutant fails graders_self_test: M1 7 FAIL, M2 1, M3 1, M4 1, M5 4, M6 (ci_tree_run reads governance.yml for every job) 2, M7 (enumeration reads governance.yml only) 4. Carry 1: mutant R1 (`json.dumps({**rec, "script": host})` -> `json.dumps(rec)`) fails the new case "a read in the file's own closure but not the host's" (1 FAIL, `bad 1`). The remaining round-2 mutants R2-R7 were not re-run: their table is not in the tree.

## Null control

Unmutated tree: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`. Carry 2(c) null: the self-test asserts `BOOTSTRAP:` rides a refusal line exactly when the refusing program is in its over-list (silent on the vendored-file and spawned-gate cases). Per-job plants on the real tree (`dev/audit/rca/prepr-head-graders/plant_jobs.sh`, a comment appended to brief_lint.mjs, budget_raise_gate.py, policy_lint.mjs, preflight.sh, prepr.sh, carry_audit.py): the arm ran pr-contract, tests.yml/briefs and budget-raise-gate; the verdict-changing plants (head passes what the base refuses) exist only in the self-test's second and third planted workflows. On the real tree the plants' refusals came from the stub body, not from a verdict-changing edit: the claim "one verdict-changing plant per job" is NOT made.

## Figures

- `git grep -n -- "- name: Restore the check source from the base commit" HEAD -- .github/workflows/` returns six jobs at the merge base (governance policy-docs, env-matrix, wave-script; budget-raise-gate; pr-contract; tests briefs); graders_self_test asserts the arm's job count equals that grep's count.
- `bash tools/pr/prepr.sh` rc=0 at `d1f3e2c67d9e` (re-run at the head above: rc=0, receipt written; origin/main unmoved since 4b5d771bdf8f at that run); `python3 tests/structure.py` STRUCTURE RATCHET PASSED.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused (five ALLOW entries added for ci_predict's stand-ins for pr-contract's runner files).

## Red checks

`tmp_paths` went red in prepr on the literal runner paths; answer: it is the cheaper detector already (prepr step 16), repaired by ALLOW entries. Otherwise none.

## Forward-carry

Not landed in this PR (still owed) — Carry: R10-FLY-CIPREDICT-RESTORING: carry 0 (inline_scan arm for `parents[N]` harnesses), carry 2(a)/(b) (fixer.md, designer.md, design-review.md at their budget caps; policy, owner's review), carry 3 (tools/policy/agreement.mjs age-needle and mutant M-h), and the verdict-changing per-job plants for budget-raise-gate, pr-contract and briefs.

## Friction

none
