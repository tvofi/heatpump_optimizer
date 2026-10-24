# Fixer, round 3, PR #2632 (R10-LOOP-CPU), topic r10-loop-cpu. Head ab6216cee6b688b45d6f4b89b70f84563307cacc

The round-2 review (git fetch origin probe/rev-2632-cd543ceb; read verdict.md and ev/) gave a merge verdict. The merge train parked it on two unrouted findings, and the first is substantive.

1. **coverage-ratchet red is NOT the entities flake.** In run 39874068348, the coverage job (120155414070) ran tests/entities.py with exit 0 and tests/features.py with exit 0. tests/golden.py exited 1 (wall 206 s, 00:15:36Z), and the ratchet then read 85.89 % against 96.0 %. The sibling run 39874062299 on the same head passed its coverage lane.
   - This PR moves the away recovery estimate and the interval replay into a process worker. Determine whether golden.py's failure under coverage is caused by this change, for example a process worker under coverage, a timeout, a pickling problem or wall-clock behaviour. Read the job log for golden.py's own FAIL lines; never infer.
   - If the change causes it, fix it architecturally, with a failing test first and a mutation proof (fixer.md).
   - If it is a genuine flake, prove it: reproduce the pass and fail conditions, or show the failing check is wall-clock or environment dependent and fails at the merge base too. Then route it as a carry to R10-FLY-SUITE-ENV-FLAKES with golden.py named (main will land the carry text you give).
2. **CI not settled.** mutation-pins (1) (job 120155543073) has been in_progress since 23:48:19Z. Report whether it is progressing. If it finishes and mutation-autofix adds a commit, the head moves; work from the new head.
3. **Correct the body.** Fix `## Red checks` to state the real coverage-ratchet cause and its answer, and re-take every affected figure. Each finding the body hands on must end in a valid `Carry:` (finding-propagation.md; carry_audit.py must read 0 unrouted).

Rules:
- Follow dev/governance/roles/fixer.md and CLAUDE.md from main. Set PREPR_SKIP_CLOSURES=1.
- Spare the GitHub API: read the job logs once each and cache them.
- If code changes, push it fast-forward to refs/heads/handoff/r10-loop-cpu. Either way, push the body with `bash tools/audit/seat/body_push.sh r10-loop-cpu <body.md>`; that is the return signal.
- In the body's first lines, state "CODE CHANGED <sha>" or "BODY ONLY", and give any carry text main must land, verbatim.
- No Claude footers, Co-Authored-By trailers or session links anywhere.
