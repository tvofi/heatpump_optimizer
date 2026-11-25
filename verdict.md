Fix review: merge fb86f2f77a59eaf6760397fc779f187816beef42

bus-nonce: e807558fec3d55092ec38fe438db7cd8

Round 1 (full scope, first review).

## Evidence

- RESULT: diff at fb86f2f77a59eaf6760397fc779f187816beef42 over merge base 3210fcd7 is one line of behaviour, `timeout-minutes` of governance.yml's `instrument-self-tests` (push 90 -> 120, pull request 30 -> 45), plus its comment and the delivery row dev/programme/delivery/3887.md (ev/diff.txt).
- RESULT: classify at fb86f2f77a59eaf6760397fc779f187816beef42 prints GREEN, rc 0 (ev/classify.txt). The packet's `tests / nightly-status` failure is outside the owed-reds set (ev/owed-reds.txt), so no answer is owed.
- RESULT: `git merge-tree --write-tree origin/main fb86f2f77a59eaf6760397fc779f187816beef42` exits 0, no conflict (ev/merge-tree.txt).
- RESULT: VERSION, the manifest version and RELEASE_NOTES.md are untouched across the three-dot diff.
- Mutation proof: the PR says n/a, and that holds: a cap has no branch to mutate. The revert mutant is the merge base itself, whose caps of 90 and 30 are the ones the cited runs were cancelled at.
- Class: governance.yml's other job caps (policy-docs 10, env-matrix 26, wave-script 10, record 10) are not part of this claim. merge_train.py's CODE_RUN_DEADLINE_SECONDS (150 min) still exceeds the new push cap of 120, so the train's wait bound is not undercut. No test in tests/ or tools/ pins the old 90/30 values: a git grep of the head for the expression returns nothing.
- Figure re-derived: the 8531d607 push attempt's instrument-self-tests job (run 45328633907) was cancelled at 5418 s (ev/job-8531d607.txt), which matches the comment's 5416-5418 s range. I did not re-derive the comment's other figures (2f4e32c2 and 3153a635 attempt 1, the 2958-4331 s range, #3868's 1783 s, #3880's 1812/1814 s, and 1292 s on 2026-11-23). They are not verified by this review, and the body's `## Figures` quotes none.
- Note: body-wording: the body says a FULL run follows from a diff touching tools/ci/selftest_closures.json, but the code comment says "a gate-file diff". This is paperwork and does not block.
