Fix review: blocked 6ffc3708d763dfcafb9faf5baf0de9b5cb541327 conflict: .github/CODEOWNERS and .github/workflows/codeql.yml conflict with origin/main 55dc8d9c2 (#2405); also harness: class-open governance.yml, hassfest.yml, validate.yml

bus-nonce: d25e4970e2d26b902ddd785a05b16da5

Round: first fix-review round on this PR (no earlier "Fix review:" comment or bus review exists); the fixer's round 2.
Measured head: 6ffc3708d763dfcafb9faf5baf0de9b5cb541327 (re-read before posting: still the head). Merge base be2d3676e; origin/main 55dc8d9c2.

1. Conflict (step 13). `git merge-tree --write-tree origin/main 6ffc3708d763dfcafb9faf5baf0de9b5cb541327` exits 1 with CONFLICT (content) in `.github/CODEOWNERS` and `.github/workflows/codeql.yml`. Neither is a claim file, and no MERGE-CLAIM line was printed. #2405 (54a69b23a, accf00130) added `/tools/pr/codeql_scope.py @tvofi` and a codeql `scope` job at the same spots where this PR adds its CODEOWNERS line and its `cancel-superseded` job. Both look like add/add conflicts where keeping both sides is the likely fix, but I cannot vouch for a merged tree that does not exist yet. Because the PR is DIRTY, no workflow ran at this head: the commit has 0 check-runs. So the body's "Expected on the next head: none of the three" has no CI behind it. After the resolution, CI has to run, including `tests/entities.py`'s permission-floor and undone-copy pins against the merged codeql.yml/tests.yml.

2. Class open (step 6). The enumeration rule is: workflows whose `concurrency:` group falls back to `github.run_id` for a bot-sent or dispatched run, which is the seam this PR names. That rule returns 8 workflows: arch-score, budget-raise-gate, codeql, governance, hassfest, pr-contract, tests, validate. The diff covers tests and codeql. The body gives a reason for skipping pr-contract, budget-raise-gate and arch-score. governance.yml, hassfest.yml and validate.yml have the same group expression, and the PR's own harness (`superseded_runs.py`, WORKFLOWS = tests, validate, hassfest, governance, codeql) measures them, yet the body neither quotes their RESULT lines nor gives a reason for leaving them out. Disposition each one in the body, with its measured figure or a stated reason, or extend the job to it. I did not re-run the harness for those three, so I have no figure for them.

Verified (cheap checks run here; heavy suites are CI's, and CI has not run at this head):
RESULT selftest cancel_superseded 19 checks, 0 failed at 6ffc3708d763dfcafb9faf5baf0de9b5cb541327
RESULT mutants 11/11 killed (branch, event set, active status, sha!=live, id<run_id, caller event, bot sender, main, open, same-repo, live head); this covers more than the body's 5 named mutants
RESULT inert-null-control is_inert(tools/pr/cancel_superseded.py) True at origin/main closure.py, False at head; is_inert(tools/pr/ci_predict.py) True at head; orphan_files() == []
RESULT closure-earned `closure.py select --files tools/pr/cancel_superseded.py` runs [tests/entities.py] at head; the still-INERT sibling tools/pr/ci_predict.py selects []. The INERT_EXCEPT move is earned by the read: the canceller's file sits in the recorded closure that selects entities.py.
RESULT version VERSION, manifest and notes heading are untouched (not in the merge-base diff)
RESULT head-in-body the body names 6ffc3708d763dfcafb9faf5baf0de9b5cb541327 and its merge of be2d3676e, which matches the merge base
Not re-derived: the BEFORE/AFTER figures (tail_billed_min 2042->853, 212->102). The AFTER figures are a prediction by the body's own label, and I did not re-fetch the run cache.
Not verified: the closures/closures-autofix/pr-contract answers at 72a3f1bbd. They are answered in the body (step 11 trigger met), but no run at this head confirms them.

Evidence: ~/hpo-seats/r10s3/review-2396/evidence
