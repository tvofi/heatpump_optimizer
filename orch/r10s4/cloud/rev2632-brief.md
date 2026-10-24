Fix reviewer, PR #2632 (tvofi/heatpump_optimizer), group R10-LOOP-CPU (production code, opus). Head 86b3fe71d656949c8bd07e802c284316acbe825f. Follow dev/governance/roles/fix-review.md from a detached worktree at that head; finder harness per the group brief, never the fixer harness. Re-read the head first; a moved head is blocked.

Check:
1. The CPU fix against the group brief (read: git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json, group R10-LOOP-CPU). Mutate the fix and show the check catches the mutant; include a null control that passes on the unmutated code.
2. The LIVESTATE carry is on the roster at cccbf4fb5 as the group's carry, with wording matching the finding, and the PR body names it.
3. The diff does not edit dev/programme/rosters/wave-r10-groups.json (git diff $(git merge-base origin/main HEAD)...HEAD).
4. CI at the head: read check-runs; a red nightly-status is not this PR unless its diff reaches what it reads.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
