CLOSURE STEP (tvofi 2026-10-18), the VERY LAST step of round 10 — after R10-ARCH-DOCS, after every PR is merged or closed, after the final stamp, before the closing #201 comment.
GOAL: on origin, only `main` plus at most 2 other branches remain; same for the local clone (~/heatpump_optimizer) and every worktree is removed.
Measured 2026-10-18 11:3xZ: local 543 branches, remote 515 heads (wip-sync 228, handoff 86, handoff-body 62, review 62, verdict 62, fix 11, study 2, record 1, main 1); 506 archive/* tags already exist (r9 precedent: refs archived-as-tags, r9-closed).
METHOD (seat: sonnet, orchestrator runs the deletes):
1. Enumerate every non-main head; classify: merged into main (git merge-base --is-ancestor), superseded, or carrying unmerged work. Unmerged work: list it for tvofi first; never delete it unasked.
2. Keep at most 2 extra branches — default choice: handoff/audit-r10-roster (if the next round needs it) and the state/plan ref state_docs.py writes; otherwise none.
3. Archive each head being deleted as refs/tags/archive/<branch> (as round 9 did) unless an identical archive tag exists, then delete the remote head; delete local branches the same way; `git worktree prune`; remove ~/hpo-seats/r10s3 worktrees (keep cited evidence dirs).
4. Stop/disable the instruments that recreate branches first: wt_sync.sh loop (wip-sync/*), record autofix (record/autofix) — check none is running.
5. Read back: `git ls-remote --heads origin | wc -l` <= 3 and `git branch | wc -l` <= 3; post the counts on #201.
Never delete main, never force-push, never touch tags other than adding archive/*.
