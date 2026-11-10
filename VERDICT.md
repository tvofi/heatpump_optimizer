Fix review: merge 1875f3ed3b0f38234ae30e11299c2e4632a4c422

bus-nonce: 714c06fa22c4ac29c5ee7fd1b38d0a81

Later round, delta scope: `git diff 71b95e42daf4d32031ce116b01c469b81f2a23a0 1875f3ed3b0f38234ae30e11299c2e4632a4c422`. Previous verdict at 71b95e42 (verdict/3379 4e0c9c856): merge, with no findings to confirm.

## Evidence

- Delta is one commit, 1875f3ed3 "ci: merge main" (parents 71b95e42d, 9ecbd4f63 = origin/main). 71b95e42 is an ancestor of the head. The 281-file two-dot stat is main's 298 commits, not the PR.
- `git show --remerge-diff` of the merge is empty: the recorded result matches git's own re-merge, with no hand resolution (ev/remerge-diff.txt). The LEDGER-MERGE driver merged tests/closures.json `inert_reads` as a set.
- The PR's own diff is unchanged. I compared `git diff <mb>...71b95e42` with `git diff 9ecbd4f6...1875f3ed` (ev/pr-diff-prev.txt, ev/pr-diff-head.txt): the only differences are hunk offsets, blob ids, one closures.json context line from main, and main's `proof_watch.verdict_nonce` context in cloud_dispatch.py. The PR's added and removed lines are the same.
- The delta's custom_components/ changes are main's (already reviewed and merged there), not this PR's, so no production-code widening applies.
- `python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` at the head (ev/mutants.txt): M0 PASS (review_packet.py, bus.sh and cloud_dispatch.py self-tests green after the merge), M1–M8 KILLED, `MUTANTS: 9 run, 0 not as required`, rc=0.
- `git merge-tree --write-tree origin/main 1875f3ed3b0f38234ae30e11299c2e4632a4c422`: rc=0, merges cleanly (ev/merge-tree.txt).
- `merge_train.py classify` (ev/classify.txt): rc=4, judged GREEN per the brief. Line: "APPROVAL-OWED 1875f3ed3b0f38234ae30e11299c2e4632a4c422 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/fix-review.md: 140 -> 143 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request". The budget raise still needs tvofi's approving review.
- `merge_train.py owed-reds` (ev/owed-reds.txt): rc=0, 23 required names. The only red among them is budget-raise-gate, which is the approval owed above.
- review_packet.py rendered with no refusals and no advisories. It rendered the full three-dot diff because it was given no `--reviewed-head`; the delta was derived by hand as above.
