Fix reviewer, PR #2633 (tvofi/heatpump_optimizer), group R10-FLOW-ARCH-PLANNER (policy and budget raise, opus). Head 7804d813a7134b9a03ae39c64a7d24dedba69e6c. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Use the finder harness per the group brief, never the fixer's. Re-read the head first; if it moved, the verdict is blocked.

Check:
1. The group brief (git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json, group R10-FLOW-ARCH-PLANNER) against the diff. It adds 7 role contracts and touches orchestrator.md and CLAUDE.md. Is each change a sound policy change with an owner, and not a restatement?
2. The budget raise: policy_budgets corpus_tokens goes from 62892 to 66443, and new caps are added. The body's `## Raise justification` must record each payment it tried and an `Architecture score: dS` line, per CLAUDE.md rule 2. Try at least one payment yourself: could existing policy text be cut or folded to pay for it?
3. The fast (3.14) fix: dev/audit/harnesses/r10_triage_gate_replay.py uses the canonical repo_root walk. Check that tests/harness_headers.py passes, and that re-inserting parents[3] turns it red.
4. The diff does not edit dev/programme/rosters/wave-r10-groups.json (git diff $(git merge-base origin/main HEAD)...HEAD).
5. CI at the head: read check-runs. budget-raise-gate is red by design until approval. nightly-status grades main.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
