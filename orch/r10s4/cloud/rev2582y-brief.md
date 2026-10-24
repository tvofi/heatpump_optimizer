Fix reviewer for PR #2582 at head c8b85d11564a9f429fafbe3353a4b8746e45b187. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW at a moved head (relay applied the returned body). Earlier verdict at 83d9662d: merge. Re-establish the verdict at this head. Group R10-FLOW-ANDON: heartbeat.sh --once from tick_loop.sh, force-push of heartbeat/orchestrator, no host path in the commit message, a failed push prints HEARTBEAT NOT PUSHED and the loop continues; check the --watch --max-age arm with a stale and a fresh null control.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main c8b85d11564a9f429fafbe3353a4b8746e45b187 (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: 4609f9ffca1b26db069b09122e427086 in VERDICT.md.
