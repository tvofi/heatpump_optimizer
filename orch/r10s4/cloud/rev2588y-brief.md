Fix reviewer for PR #2588 at head 922640dcd6ca515040d18a12a0a4e74aaa5eb8fb. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

First review of this head. This is the roster PR (PR-B, the sole change is dev/programme/rosters/wave-r10-groups.json, plus carry files if any). The head carries roster tip 2ce05426. Check that EVERY group added since the last review passes brief_lint and validates against the roster schema: R10-FLY-BUDGET-LEAF, R10-FLY-STAMP-CHECK-NOTES, R10-FLY-MANDATE-REVOKE-GUARD, the R10-FLOW-JIDOKA sentence citing #2528, and the P22 carry on R10-FLOW-BODY-ONLY; then the earlier groups (23 R10-FLOW-*, the fly-ins, R10-ROUND-PLAYBOOK) and the body's group counts (re-count them with jq). Run brief_lint.mjs and the roster schema validator yourself and report their output; a group with a literal metric or a count the tree answers is an error. Every carry the body or roster adds must resolve to a live group.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main 922640dcd6ca515040d18a12a0a4e74aaa5eb8fb (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: e245625fcfc35a83b4c0685318d070df in VERDICT.md.
