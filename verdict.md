Fix review: merge c93903f075212c86bdef7b011776d5570d776630

bus-nonce: a7ac54c9756a9e5d723e1db76fef9f01

## Evidence

- review_carry.py c6becb31 c93903f0 answers CARRY. The range is one commit, c93903f07, a merge of origin/main into the branch. It has no non-merge branch-only commits (ev/checks.txt).
- CI: `merge_train.py classify c93903f0 --pr 3425` prints `GREEN c93903f075212c86bdef7b011776d5570d776630 pending: none red: none`. No `## Red checks` answer is owed.
- Merges with main: `git merge-tree --write-tree origin/main c93903f0` exits 0, tree e76054ca0ccc09abf9bb90c53a35a2528ab8dadc.
- Review carried from head c6becb3175c5979f1c117755161b1950aee2d821, whose verdict was "Fix review: merge c6becb31", without a pending-ci line now that CI is green. That review's content, verbatim:
  - Round 2 was a delta re-review of the repair since the blocked head 779c9432. The delta is 18 added self-test lines in tools/audit/seat/orchestrator_tick.py and changes no production lines.
  - Self-test at head: `orchestrator_tick.py --self-test` gives `308 checks, 0 failed`, matching the body.
  - The previous block's survivors are killed. M3 (delete the two one_pr lines that clear `_red[n]`) gives 1 failed, `FAIL carry 9 one_pr: WAIT clears the red`. M4 (the `_classify_red` except-branch returns False) gives 1 failed, `FAIL carry 9 one_pr: an unread classify keeps it`.
  - Extra mutants of the reviewer's own, all killed: M5 (`_classify_red` returns True always) 2 failed; M8 (`not` dropped from the one_pr condition) 3 failed; M9 (clear made unconditional) 2 failed.
  - The new pin is not vacuous. Its three arms want different `_red[77]` values, and the RED null control fails under M8 and M9.
  - VERSION, the manifest and the release notes are untouched. No golden fixture or claim file moved.
  - Finder's harness: none. This is a roster-carry group whose instruments are the fixer's own self-tests.

## Findings

none
