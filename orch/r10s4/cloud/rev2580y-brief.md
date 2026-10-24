Fix reviewer for PR #2580 at head f44296a61f42250b23c0f557a54c6295ab991dac. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW at a moved head (relay applied update 929ee160). Earlier verdict at a54aed8b: merge. Re-establish the verdict at this head. Group R10-FLOW-RELAY-HOLD; check what changed since a54aed8b (git diff a54aed8b...head) and that the earlier mutation proof still holds.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main f44296a61f42250b23c0f557a54c6295ab991dac (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: 0ed27b8ec8d7a80dd5c06d6dda5b6b33 in VERDICT.md.
