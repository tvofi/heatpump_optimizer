Fix reviewer for PR #2545 at head 2124bc75b245215b2742e2cd30089cf0cb71a895. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW. The earlier verdict (review/2545) was: Fix review: blocked 6e12aeb5bd976a7520361dd05bf9300cb6c77a04 harness: class-open relay_owed keys the probe-ref, handoff-update, approve-held-runs and dispatch OWED rows on the kind token as well, and the record names only handoff-no-pr and carries no class search (root-cause.md 1 and 3). Its three blocks: (1) the named cause stopped at one kind while relay_owed keys five OWED kinds (probe-ref, handoff-update, approve-held-runs, dispatch, handoff-no-pr) on f[2], so the class search was absent; (2) the cost test called 5.13 seat-hours measured when the R9 RCA says it was not verified; (3) two carries pointed at the done group R10-ROSTER-OPS. Verify each is cleared at this head, replaying relay_owed over a hand-written log yourself (the finding had no committed harness) and running carry_audit against the roster ref.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main 2124bc75b245215b2742e2cd30089cf0cb71a895 (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: b351261712df38a8c9eb2843fd1a12b5 in VERDICT.md.
