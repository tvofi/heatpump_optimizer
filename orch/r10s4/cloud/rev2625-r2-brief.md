Fix reviewer, round 2, PR #2625 (tvofi/heatpump_optimizer), group R10-RCA-BODY-LINT (RP, policy, sonnet). Head 960135738416bf6b23cc6552923c392ca9cedc2c (r2 0bcc7d4e plus a merge of main). Follow dev/governance/roles/fix-review.md from a detached worktree at that head; finder harness per the group brief, never the fixer harness. Re-read the head first; a moved head is blocked.

Check:
1. Round 1's block is resolved: its carry-missing/RCA demonstration finding is answered in the body and by the r2 diff (null control plus planted defect caught).
2. The two R10-FLOW-JIDOKA carries are on the roster at a46a37a8 and 5ba47bff as named in the PR body. Read: git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json
3. The diff does not touch dev/programme/rosters/wave-r10-groups.json (git diff $(git merge-base origin/main HEAD)...HEAD).
4. CI at the head: read check-runs; a red nightly-status is not this PR unless its diff reaches what it reads.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
