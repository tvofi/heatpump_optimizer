Fix reviewer, PR #2638 (tvofi/heatpump_optimizer). This is the R10-CI-LAYOUT-P2 pre-PR and it is critical path: policy_lint treats a reusable-workflow caller of pr-contract as a caller, not as its definition. Head 3f5400667c3a726b1d63c2f861f83488a80fadf4. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Check:
1. tools/policy/policy_lint.mjs definesJob and contractWorkflowFiles. A job whose own body has a job-level uses: is a caller. The "exactly one file defines pr-contract" rule is unchanged.
2. The two new tests/entities.py checks fail against main's policy_lint and pass at the head. Run your own mutants, including these three:
   - drop the caller rule;
   - let a job body run into the next job;
   - treat a step-level uses: as a call.
   The nulls must hold:
   - the real job still counts when its steps use actions or when the next job is a caller;
   - two real definers still read as two;
   - the real tree has exactly one, pr-contract.yml.
3. On U0c's tree (git fetch origin handoff/r10-ci-layout-p2-u0c; head d22b5f303), main's lint returns rc 1 ("2 files define pr-contract") and the head's lint returns rc 0. On main, the head's lint returns rc 0.
4. This is a policy instrument. Say whether it is policy under CLAUDE.md, so the orchestrator can approve under the mandate at merge.
5. Read CI at the head from check-runs; policy-docs grades with main's lint. Check that the body's figures hold at this head (the opener merged main after the fixer measured).

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
