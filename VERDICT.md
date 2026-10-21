Fix review: blocked 54bf182104e450c0ac2e6eb007da59b9315e0565 merge-conflict: the unchanged head no longer merges with origin/main f2fb1b0e9, which conflicts in tools/audit/seat/pr_args.sh

This was meant to re-issue comment 6320871704 (round 5, merge) at the same head, to route that comment's items. The re-check came back failing, so I cannot re-issue the merge.

## Re-check at this head

- The head is unchanged. `refs/pull/2567/head` is 54bf182104e450c0ac2e6eb007da59b9315e0565, and the PR API reports the same sha with `mergeable=false` and `mergeable_state=dirty` (ev/head_reread.txt).
- `git merge-tree --write-tree origin/main 54bf182104e450c0ac2e6eb007da59b9315e0565` exits 1. origin/main is f2fb1b0e950ecd047b7f08b3adef93776a622540. Git reports `CONFLICT (content): Merge conflict in tools/audit/seat/pr_args.sh`. INSTRUMENTS.md and update_pr.sh auto-merge (ev/merge_tree.txt).
- The cause is main moving, not the head. The same head merges cleanly with 49c222280, the main of round 5, giving tree 342e8c6e8 (rc=0). Since that review, main has taken e8bf2f03d (`fix(seat): open_pr.sh holds the branch lock; update_pr.sh never detaches unpushed work`) and its merge e958d53bc. Both touch pr_args.sh (ev/conflict_cause.txt).
- CI on this head: 52 check-runs, 35 success, 16 skipped, 1 failure. The failure is nightly-status (119298247901). Round 5 already answered it as not this PR's red, and the body answers it under `## Red checks` (ev/check_runs.tsv).

## What the fixer owes

Merge origin/main into the PR head and resolve pr_args.sh, without rebasing. Then re-run steps 2–8, per fixer.md (they re-execute after any merge), and push. The new head then needs a fresh review. Comment 6320871704 does not carry over to it.

## Routing of comment 6320871704's items

`carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 2567` listed 2 unrouted items (ev/carry_pr2567_before.txt). Both are dismissed below.

- Carry: dismissed: a restatement of round-4 routings already recorded on review/2567 21141036, raising no new finding (item 47cb6add)
- Carry: dismissed: the bus-nonce trailer line, which is transport metadata and not an observation (item a9388222)

bus-nonce: 7d363d3179d4917c247b34f2a4fb0303
