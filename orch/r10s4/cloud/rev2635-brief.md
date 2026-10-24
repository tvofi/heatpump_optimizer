Fix reviewer, PR #2635 (tvofi/heatpump_optimizer), roster batch 17 (roster ops, sonnet). Head 7a3e640d01ffdfe3e74c64fc4e3ede06c087489c. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Check:
1. Every op in the body's op list lands as stated. Use git show <sha> per op, or diff dev/programme/rosters/wave-r10-groups.json against origin/main three-dot. Check the counts: 154 to 165 groups, 11 new, 18 changed, and the stage counts.
2. The R10-ORCH-MACHINERY re-cut. Every carry of the old group lands in exactly one new group or among its 12 no-build carries, apart from carry 13, which is copied to A, B, C and E. None is lost and none is duplicated otherwise. Compare against the design note at origin/design/R10-ORCH-MACHINERY:dev/programme/designs/R10-ORCH-MACHINERY.md section 4.
3. The after-edges. Moving R10-FLOW-TOOLKIT-MODEL and R10-ROUND-PLAYBOOK off the absorbed group leaves no cycle, and no group is blocked by a non-done stage that can never finish.
4. The roster lint (brief_lint.mjs) reports 0 errors, ref_privacy --check reports 0 refused, and the null control is real.
5. CI at the head: read check-runs. nightly-status grades main.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
