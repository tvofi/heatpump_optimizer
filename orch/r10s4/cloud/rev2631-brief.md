Fix reviewer, PR #2631 (tvofi/heatpump_optimizer), group R10-BRIEFS-FOLD (policy, opus). Head 8b33d02131529b27f2ea9848fe33d8270f8f14d0. Follow dev/governance/roles/fix-review.md from a detached worktree at that head; finder harness per the group brief, never the fixer harness. Re-read the head first; a moved head is blocked.

Check:
1. The fold against the group brief: read the group entry with git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json (R10-BRIEFS-FOLD).
2. The 6 carries: 2 routed to the roster at e381aff4 and 224dfb4e (confirm each is on the roster as its group's carry); 4 dismissed. For each dismissal, verify its stated reason holds against the tree.
3. The diff does not edit dev/programme/rosters/wave-r10-groups.json (git diff $(git merge-base origin/main HEAD)...HEAD).
4. CI at the head: read check-runs; a red nightly-status is not this PR unless its diff reaches what it reads.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
