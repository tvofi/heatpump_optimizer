Fix reviewer for PR #2626 (tvofi/heatpump_optimizer), group R10-ROSTER-OPS, roster batch 15. Read the group entry with `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` (jq/python the group whose "group" is R10-ROSTER-OPS). Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head SHA 6bee9961fa8bbb90d50392fee75a64ab88a3d8e2.

This is a roster diff: check it mechanically against the batch list in the PR body (every group, stage and carry named there must match the diff; a figure in the body that describes another diff is blocking). Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads.
Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
