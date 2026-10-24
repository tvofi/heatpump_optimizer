Fix reviewer for PR #2579 at head eb9f7e89d0b258ca66a8d9757df0156a776b7332. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

RE-REVIEW after a block. Earlier verdict (origin/review/2579) opened: Fix review: blocked 816b1e20fdfd0a4b99bcc2b81361b70bd3007acb mutation-survivor: three one-line mutants of review_strength.py pass all 24 self-test checks yet move body figures (L>=600 size cut, guardrail last-N slice, as_of --first-parent). Group R10-FLOW-YIELD-PROBE. Verify the three named mutants of review_strength.py (the L>=600 size cut, the guardrail last-N slice, as_of --first-parent) are now each killed by the self-test, and that every other body figure holds at this head.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main eb9f7e89d0b258ca66a8d9757df0156a776b7332 (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: 0e359fb8bd15567e4ab97a86c4e27758 in VERDICT.md.
