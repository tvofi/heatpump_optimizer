Fix review: merge 413b7ae146265c75d875f151a9db1c9ad692376b

bus-nonce: 99698f0bb3611f15ab48672d78025bbd

Measured at a detached worktree at 413b7ae146265c75d875f151a9db1c9ad692376b.
- Files changed vs merge base aab94eea: only docs/delivery/{1838,1842,1843,1844,1849,1853}.md. Five rows rewritten one line each, plus the new 1853 row.
- Per row (gh pr view N --json state,mergeCommit; git merge-base --is-ancestor <sha> origin/main; line equals base line with the merged <8-hex> swapped back to open): 1838 2b6c5b87, 1842 7c94526f, 1843 af7660c7, 1844 b6fc4321, 1849 aab94eea. All MERGED, prefix matches, reachable from origin/main, rest of line unchanged. Output in real.txt.
- Null control: corrupting 1842's sha to deadbeef in a scratch copy turns the check to FAIL=1 (MISMATCH, reach=no), null.txt. My first null attempt used BSD sed with a GNU-only address, changed nothing and passed vacuously; I discarded it and redid it with perl.
- Body figures: 5 files read open at aab94eea (git grep), 0 at the head. Current origin/main lists 6 because #1845 merged since; out of scope as instructed. Merged 5, closed-unmerged 0, still-open 0 confirmed.
- Mutation proof, null control and forward-carry n/a: record-only, no production or check code.
- Head CI (check-runs): no red. Success: pr-contract, delivery-status, budget-raise-gate, closure-scope, policy-docs, briefs, env-matrix, wave-script, instrument-self-tests, hassfest, validate-hacs, nightly-status. Two cancelled entries (pr-contract, budget-raise-gate) have a success sibling on the same head. Still in progress when read: fast (3.14), typing, mutation, coverage, closures, browser, Analyze (python). Merge is conditional on those finishing green; none can be moved by a docs/delivery-only diff.
