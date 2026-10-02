Fix review: merge 46a708150f35534344039ef0ada7f12c81c77af6

PR #1838, R9-F10.4. This is a carry of round 3's merge verdict on ce12cbd1 (F10.4-review-ce12cbd1), not a new review round. The new head is 46a70815, which merges main c168ec0a (#1840) into ce12cbd1.

## Strict carry predicate (orchestrator.md section 11)

- tree(46a70815) = c62ba3ae = `git merge-tree --write-tree c168ec0a ce12cbd1`.
- Since the merge base 777c2318, no file changed on both sides; the intersection of the two sides' changed-file lists is empty.
- Main's side is #1840's card, docs, the card drift claims and carry-1795.json. None of it is in this PR's diff.
- docs/delivery/1838.md is already in the tree and is unchanged by the merge.
- See carry_check.txt in this directory.

Every round-3 measurement therefore describes this PR's own files unchanged at 46a70815.

## Still owed to tvofi

- The two budget re-baselines.
- The `briefs` red, which comes from the base-pinned linter.
- Approval of the brief_lint.mjs policy edit.

CI on the PR head still has to be green.
