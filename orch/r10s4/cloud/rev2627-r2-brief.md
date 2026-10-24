Fix reviewer for PR #2627 (tvofi/heatpump_optimizer), group R10-NIGHTLY-ABSENT-NEW (IN lane, instrument, opus). Round 2. Head 48e8c29b7ffe23df442d563b7ae81d81e7475d4e. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head. Use the finder harness the group brief names, never the fixer harness. Read the group entry with `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`.

What round 2 did (verify, do not trust): f4a3ea954 reverts the fixer's own roster edit; the PR body was fixed; its CI-LAYOUT-P2 carry is landed on the roster at 0f690a952102eb8840d86764f1fbbf2d8d4d1bf1, and the body names it.

Verify:
1. The NEW/ABSENT window against the brief's control at the merge base: a workflow younger than its first cron slot is NEW, not ABSENT; a workflow past that window with no scheduled run is still ABSENT. Both arms exercised, measured at the merge base and at the head.
2. The branch's diff no longer touches dev/programme/rosters/wave-r10-groups.json (`git diff $(git merge-base origin/main HEAD)...HEAD --stat` must not list it).
3. The carry is on the roster at 0f690a952102eb8840d86764f1fbbf2d8d4d1bf1 as the group's carry (CI-LAYOUT-P2), with wording matching the finding, and the PR body names that SHA.
Re-read the head before you start; a moved head is a blocked verdict.

Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
