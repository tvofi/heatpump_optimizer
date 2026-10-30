Fix review: merge 0496699e2c4dcbc1a3d16cb5f65f2d06d8d40718

bus-nonce: 196d8d47e20dc9138970fc4c6cac9d2c

## Scope

Resolution-delta review (fix-review.md step 12) of 882da1e01b3d209cf7f8b6c02427166e7c0c7655..0496699e2c4dcbc1a3d16cb5f65f2d06d8d40718, three-dot against origin/main aced258937628590b92265eea4c01276cac43b24. Round: delta review after the round-1 repair (5cd2f86eb), not a fourth round. Measured head 0496699e2c4dcbc1a3d16cb5f65f2d06d8d40718; re-read with `git ls-remote` before writing: still the head.

## Findings

none

## Evidence

- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- review_carry.py 882da1e0 -> 0496699e prints FRESH-REVIEW: the one branch-only commit is the merge of main aced25893, and it "resolves tests/golden/claimed_drift.txt to something other than the union of its parents" (ev/review_carry.txt). Read: that is main's own edit, not a resolution. At the old merge base 26c9d22a3 the five coord_* lines already carried R10-HOUSE-GRADE (#2816), main's claim, and main has since replaced them with R10-COP-GATE (#2262) and emptied the R10-BUFFER-STORE claims, restoring their may-drift lines. The three-way merge takes main's side because the branch never touched the file. So the merge is not a union of the parents, and correctly so.
- Check 1, claim files: the branch claims nothing. `git diff 26c9d22a3 882da1e01 -- tests/golden` is empty, and at the head both tests/golden/claimed_drift.txt and tests/golden/card_claimed_drift.txt are byte-identical to origin/main aced25893 (ev/claims.txt). Main's claims plus none of the branch's: claim-files.md's "a branch that claims nothing leaves both claim files byte-identical" holds.
- Code unchanged by the delta: the branch diff against its base before the merge (26c9d22a3..882da1e01) and after it (aced25893..0496699e) differ only in one hunk header of tests/closures.json (@@ -3815 -> @@ -3969), a line offset; `git range-diff` shows the five branch commits `=` (ev/branch-diff-*.txt). The body's "## Head" statement (an automatic merge, no resolution, the reviewed code unchanged) is true.
- Merges with main: `git merge-tree --write-tree origin/main 0496699e` rc 0, tree f356bf820924bed147ac4b08c95ead3fdc6ac60e, no conflicting path (ev/merge-tree.txt).
- Re-run at this head in a detached worktree: `merge_train self-test: 355 checks, 0 failed` rc 0 (ev/selftest.txt); `MUTANTS: 20 run, 0 not as required` rc 0, M0 PASS and 19 KILLED (ev/mutants.txt; the file's leading `rc=124` belongs to a first run cut off by a 220 s timeout, superseded by the full run after it); `STRUCTURE RATCHET PASSED` (ev/structure.txt). These match the body's figures, taken at 882da1e0.
- Not re-derived by this seat: the body's `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (closure select). CI's gate and closure-scope at this head are green, and the review packet's figure_lint resolved the command.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched three-dot (ev/version-untouched.txt is empty).
- Check 2, body and red checks: the body's `## Head` names 0496699e and says how it relates to the measured 882da1e0. pr-contract / pr-contract passed in both head runs: run 41028634300, job 123987083370, completed 09:23:41Z; run 41028634788, job 123987963049, completed 09:26:03Z. Both started after every other job in those runs had concluded, and none of those had concluded red. `## Red checks` answers the only red in the range, `tests / nightly-status` at 882da1e0 (run 40993619726), as main's, and nightly-status reads nothing this diff touches. At this head nightly-status is green. No unpinned site is open: the seams list in `## Figures` dispositions every hit of the named git grep.
- Check 3, CI at this head, read from the check-runs API after both workflows concluded: 55 check runs, none failure, none in progress. Both `gate` jobs (123987306895, 123988257882) passed. tests / fast (3.14), closures, coverage, mutation, instrument-self-tests, arch-score (both runs), budget-raise-gate and codeql / Analyze (python) all passed. CodeQL itself was neutral in the packet and success on re-read. The skipped jobs are lane-conditional (replay, nightly-ha, mutation-pins, autofix lanes, kernel-points).
- Forward-carry: the body states none; this delta adds no finding to carry.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head printed `ALL 2483 ENTITY CHECKS PASSED` (ev/entities.txt). The body's 2479 was taken at 882da1e0, before main aced25893 brought in four more checks. So the body's count is a different head's figure, not a regression.
