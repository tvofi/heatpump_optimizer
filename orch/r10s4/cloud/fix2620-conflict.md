# Conflict fixer, PR #2620 (R10-CURRENCY), topic r10-currency. PR head 0b9431baec2ff7b57dceadf6ed5ef56da1d25a25 (branch fix/r10-currency)

#2620 is reviewed (verdict/2620: merge at 72fbab2a; 0b9431ba is that head plus a clean merge of main bfd61aaf) and approved. Main has since merged #2647 (R10-SCORES, 14405df5) and #2645, and `git merge-tree --write-tree origin/main 0b9431ba` now reports a CONTENT CONFLICT in custom_components/heatpump_optimizer/coordinator.py. tests/features.py and tests/seam_map.json auto-merge. tests/structure_budgets.json merges by the ledger driver to seam_cut_total 713, class_excess_loc 18233 and max_class_loc 8469, with "re-run the gate that owns this file".

Do:
1. In a worktree on a local branch at 0b9431ba, `git merge origin/main`. Resolve coordinator.py so BOTH intents survive: #2620 prices the plan narrative in the feed's currency; #2647 is the R10-SCORES change, so read its diff `git diff 14405df5^1 14405df5 -- custom_components/heatpump_optimizer/coordinator.py`. No behaviour of either may be lost. The resolution must be the minimal union; no refactor.
2. Prove it:
   - tests/features.py and tests/entities.py green, with PREPR_SKIP_CLOSURES=1;
   - `python3 tests/structure.py` passes, and the budget file holds the MEASURED values, which must not exceed main's caps (re-record only downward, with the reason in the commit message);
   - the scoped gate MODE line;
   - each side's own targeted tests: #2620's currency checks and #2647's score checks (find them in each PR's diff) red-on-revert of the other side's hunk inside the conflict region, showing the resolution kept both.
3. Commit the merge with a message describing the resolution. Push it fast-forward to refs/heads/handoff/r10-currency. Then fetch the live PR body (`gh pr view 2620 --json body`), prefix `## Head` with a paragraph naming the new head, the conflict, and how it was resolved hunk by hunk, keep every other section verbatim, and run `bash tools/audit/seat/body_push.sh r10-currency <body.md>`.
Follow dev/governance/roles/fixer.md and CLAUDE.md from main. Spare the GitHub API. No Claude footers, Co-Authored-By trailers or session links anywhere.
