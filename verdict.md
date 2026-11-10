Fix review: merge 71b95e42daf4d32031ce116b01c469b81f2a23a0

bus-nonce: aac29b69018110586182969c8ca5ce1f

Body-repair re-check only (code unchanged since the ci-red block at this head). Round: a later round, delta scope.

## Evidence

- `## Red checks` names both `budget-raise-gate / budget-raise-gate` and `pr-contract / pr-contract` by full name; each is answered (cheaper detector `policy_lint.mjs --budgets` plus standing cost of one owner review; for pr-contract, the `--pr-body --red` detector run before posting, with its cause).
- `node tools/policy/policy_lint.mjs --pr-body body.md --red 'budget-raise-gate / budget-raise-gate' --red 'pr-contract / pr-contract'` (live body, ev/policy_lint.txt): rc=0, `PR-BODY: 0 error(s)` (only a skip red-history note, as --head was not a sha).
- The body does not claim the owner's approval; it says the raise stays red until tvofi approves.
- merge_train classify: rc=4 APPROVAL-OWED, the only red is the budget raise's approval; judged GREEN. Line: "APPROVAL-OWED 71b95e42daf4d32031ce116b01c469b81f2a23a0 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/fix-review.md: 140 -> 143 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request".
- git merge-tree --write-tree origin/main head: exit 0, merges cleanly (ev/merge-tree.txt).
- Code not re-reviewed, by brief scope.
