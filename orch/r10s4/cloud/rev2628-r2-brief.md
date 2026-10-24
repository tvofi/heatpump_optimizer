Fix reviewer for PR #2628 (tvofi/heatpump_optimizer), group R10-FLOW-PULL (RP lane, policy, sonnet reviewer round 2). Head ced4bf66e91d3c61254066c310f1f9af7ea064ef (unmoved from round 1). Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head. Use the finder harness the group brief names, never the fixer harness.

This is round 2 of fix-review for #2628. Round 1 is review/2628 commit 6fc4c91ab, which blocked carry-missing: the carries were not routed to R10-FLOW-POSTMERGE or R10-FLOW-AUTOTRAIN.

The orchestrator's answer: the three carries are on handoff/audit-r10-roster at 5a762df2ea9c848da2fb7d806d1e38edbb8beefc: POSTMERGE 1f35f6d2, AUTOTRAIN d0b49bc6, ARCH-PLANNER 5a762df2. The body's "## Forward-carry" section names each SHA; CARRY-AUDIT reports 3 routed, 0 bad.

Verify:
1. Each carry is on the roster at its named SHA, as its group's carry (R10-FLOW-POSTMERGE for 1f35f6d2, R10-FLOW-AUTOTRAIN for d0b49bc6, ARCH-PLANNER for 5a762df2), with wording that matches the round-1 finding. Read the roster with `git show 5a762df2ea9c848da2fb7d806d1e38edbb8beefc:dev/programme/rosters/wave-r10-groups.json`.
2. The PR body names those SHAs in its Forward-carry section.
3. `node tools/policy/brief_lint.mjs` exits 0 at 5a762df2ea9c848da2fb7d806d1e38edbb8beefc.
4. Re-read the head and CI. Re-do nothing else from round 1 unless the head moved.

Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
