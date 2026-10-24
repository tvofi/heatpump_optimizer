Fix reviewer for PR #2589 at head e4b3e01abb48644841202e7d7b0ae93107258bd3. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at that head, and use the finder's harness the group brief names (roster: origin/handoff/audit-r10-roster, read with jq), never the fixer's. PREPR_SKIP_CLOSURES=1.

First review of this head. Group R10-FLY-GH-READ-RETRY PR 1 of 2: tools/pr/app_approve.sh gh_read retries only on failures a later read can ride out. Check the four reads (pull request twice, comments, CODEOWNERS, changed files) all go through gh_read, that a permanent failure (404/403 non-rate-limit) is not retried, and that backoff is bounded.

Required:
- Run the mutation proof, the finder's harness at both ends and a null control for every quantified claim yourself; CI cannot produce them.
- Re-measure every figure in the PR body at this head and report each as re-derived or not re-derivable.
- Standing rule 19: run carry_audit.py --roster-ref origin/handoff/audit-r10-roster check over the body and report 0 unrouted; every Carry in your own verdict must be routed too.
- ## Red checks: read the check-runs API per commit at this head. nightly-status grades main, not this PR unless the diff reaches what it reads; main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT.
- Merge-tree: judge the combined result with git merge-tree --write-tree origin/main e4b3e01abb48644841202e7d7b0ae93107258bd3 (clean required); do not ask for a main absorb on a clean head.
- Confirm roles/ on main is unchanged since the merge base, else re-read the contract.
- Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt). Include the line bus-nonce: dc353331c0736bde6c26e8e29ce6b633 in VERDICT.md.
