Fix reviewer for PR #2578 at head 36ca386d6a830a90096df6821b85abfad0c6a1f9. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW at a moved head. Earlier verdict: Fix review: merge 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20. The head has moved since (main absorbs and body re-takes); re-establish the verdict, do not inherit it. Group R10-FLOW-BODY-PATCH: body_patch.sh and the read-back retry; check retry exhaustion cannot print OK for a body never read back.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main 36ca386d6a830a90096df6821b85abfad0c6a1f9 (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: bab79752a47f364a206d67b2cbfa49bc in VERDICT.md.
