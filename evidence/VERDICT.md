Fix review: merge 4666a7dd8d43e7bd8d5cae9c51268c31db031dd9
bus-nonce: 350314353015cc73b94f8b372c66e811
reviewer: r10-d15-reviewer, round 1

Measured at 4666a7dd8d43e7bd8d5cae9c51268c31db031dd9 (merge base 554e2ecfa), from a detached worktree, with the head's own graders.

RESULT check_scopes --ref HEAD rc=0, ok D15 mode=cells seats=3; --self-test rc=0. The seats are disjoint by step: s1 M1-M4, s2 M5-M6, s3 M7-M8.
RESULT check-wave-script.mjs with the grader from #2214 merged in: 180 passed, 0 failed.
RESULT policy_lint rc=0 (0 errors, 41 files). --budgets rc=0: D15.md 39/39 lines and 728/728 tokens; corpus 61026 against cap 61026.
RESULT rules_sync --check rc=0. brief_lint rc=0. tests/structure.py PASSED. tests/layout.py ok.
RESULT mutation proof: the two named mutants are killed (each gives 179/1). merge-tree against origin/main c698d504a is clean.

The brief is in the owner's terms:
- It debugs a real install from the hpo-debug/1 download, and the synthetic bundle is the null control.
- It states the version-attribution rule: the newest release tag dated before the last restart that precedes the cycle. Each anomaly is then re-checked at the baseline.
- The bundle stays out of tree: absolute paths, never copied, and audit-find.js refuses a relative path.
- Every symbol the method cites exists at the head. Steps 3 and 8 state their perturbations.

Red checks, all answered in the body:
- wave-script: pending on #2214. CI restores the grader from the base (job 116154063244: 173/3). The three failures are exactly the ones #2214's grader fixes.
- budget-raise-gate: this is a raise (corpus_tokens 60449 -> 61026, plus new D15 caps). It merges only on tvofi's approving review at the head, under mandate 6175172275's rules. The commit message 21ef4cdbf justifies it.
- nightly-status: this is main's check (#2205).

Non-blocking:
- (a) The raise is only partly avoidable. Without it the head exceeds cap+band by 77 tokens. About 38 tokens of D15.md do no work for a finder: the moratorium-override sentence and the fix-phase lead. Even cut, the raise would not be avoided.
- (b) A surviving mutant in #2214's grader: with BUNDLE_DIMS = new Set([]) the result is 180/0. The check reads the set from the driver it grades, so D15's membership is not pinned. Carried to #2214's review.
- (c) M1 sets no gap threshold for a restart. An upgrade restart shorter than the cycle interval would be attributed to the older version. The baseline re-check bounds this.
- (d) The bundle-specific v6.7.17/v7.0.0 case belongs in the D15 dispatch prompt. The rule itself is carried in M1.

Merge preconditions: #2214 merged and main merged in (judged as a resolution delta), and tvofi's approving review at the final head.
