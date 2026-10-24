Fix reviewer for PR #2591 at head 400e15d277c7fb7c9e27aa1c203de282e0c51c4f. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

First review of this head. Group R10-FLY-BUDGET-LEAF (roster brief names the finder harness). The body claims one shared helper body_refusal in tools/pr/prepr.sh used by step 7 and step 7c; re-measure its mutation proof (the old grep -m1 form as the mutant must fail exactly the two new self-test rows) and run a null control.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main 400e15d277c7fb7c9e27aa1c203de282e0c51c4f (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: 83814d80bae8f1eedb0ae013d6900cdd in VERDICT.md.
