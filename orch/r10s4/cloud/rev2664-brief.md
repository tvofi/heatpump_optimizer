Fix reviewer for PR #2664, R10-FLY-RELAY-REVIEW-FF (lane F, size S, instrument), branch fix/r10-fly-relay-review-ff, head 1270ba9b92e16143ddabab30c8ad89138a4b4cc5. The code head is af21edb9e6e6; 1270ba9b adds only the delivery row. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Your ev/ MUST contain ev/HEAD.txt holding the full 40-hex head, or the relay refuses the verdict.

The PR adds a confirm arm to cloud_relay.sh `pass --confirm`. For each review/<pr> tip the relay pushed (bus-nonce matched to a probe the relay ledgered) that bus.sh has not posted (posted-signed `<pr> <tree>`), it runs `bus.sh confirm` with bounded retries. It prints POSTED on success, and OWED with the last stderr line on failure. Also: a non-fast-forward review/<N> re-apply, tick_loop relay_start passing --confirm, and probe_arm retrying transients.

Verify adversarially, with the finder's harness, not the fixer's:
(1) Three-dot diff `git diff $(git merge-base origin/main HEAD)...HEAD`: every file is in the group's file list or is a test or fixture for it, plus INSTRUMENTS.md and dev/programme/delivery/2664.md.
(2) Rebuild the P-O failure: a relayed probe whose confirm failed, then the next pass. On main it says 'already relayed' and posts nothing. At the head it retries and logs POSTED. Null controls: an already-posted review does nothing and makes no confirm call; an undispatched review logs OWED once and not every pass.
(3) The three causes the body claims to cover: a failed confirm, a stale script, and a relay with no --confirm. Show each one is covered, or block naming the one that is not.
(4) Mutants: drop the arm, drop the posted check, drop the retry bound. Each must turn a test red. Check that no gh call was added (grep the diff).
(5) The non-fast-forward path never force-pushes, and probe_arm's REFUSED logging writes no .refused for a transient error.
(6) Every figure in the body at this head. `git merge-tree --write-tree` against origin/main is clean. Read CI with one bulk check-runs call. The commits carry no footers. Record the scoped-gate MODE line.
ORCH-LEDGER (unmerged) and UPDATE-PR-SIGNALS also edit cloud_relay.sh. Note any hunk overlap as a Carry, not a block.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API; no Claude footers.
