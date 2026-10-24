Fix reviewer, round 2, PR #2632 (tvofi/heatpump_optimizer), R10-LOOP-CPU. Head ab6216cee6b688b45d6f4b89b70f84563307cacc: 86b3fe71 plus the closures-autofix bot commit, which touches tests/closures.json only. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Round 1 (git fetch origin probe/rev-2632-a4ff6382; verdict.md) found the code sound. It blocked only on the body: closures UNDER-SCOPED was red and the body did not answer it. The body has now been patched (sha1 252b9779). Review this delta:
1. Under ## Red checks, closures is named UNDER-SCOPED and repaired by ab6216c, per ci-autofix.md; mutation is red at the three answered sites; the "has not run in CI" sentence is gone.
2. The body also names fast (3.14) and coverage-ratchet red in run 39874068348, with the sibling run 39874062299 on the same head green. It attributes them to the gate-lease priority concurrency flake in tests/entities.py, routed to R10-FLY-SUITE-ENV-FLAKES. Verify that from the job logs, and read check-runs at the head now (a rerun may have concluded).
3. ab6216c's carry-eligibility under orchestrator.md section 11.
4. pr-contract at the head passes the body.
Round 1's evidence (mutants, finder's harness, failing-test-first) carries over; do not repeat it unless the code moved.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
