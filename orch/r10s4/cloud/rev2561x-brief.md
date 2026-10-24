Fix reviewer for PR #2561 at head de47b55ccebe0a90aa4a50543658f7616cb4ff2e. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW at a moved head. Earlier verdict: Fix review: merge 2aea7f088607c1b86e0f42499d84c8b3aea1c9b0. Re-establish the verdict at this head. R10-RCA-HARNESS-FRICTION: the RCA record for friction keys harness, class-open, mutation-vacuous; check the named cause, process state, cost test and countermeasure-or-refusal against root-cause.md.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main de47b55ccebe0a90aa4a50543658f7616cb4ff2e (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: f50558aec80d928a1e4afcbd7f535055 in VERDICT.md.
