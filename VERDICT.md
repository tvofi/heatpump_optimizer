Fix review: merge e7fc65845c2609b5e2ce7096362460aa53e85b32

bus-nonce: a8b610eb401decafd6b9d6635d46924f

Delta re-review only (e62be31d -> e7fc65845c2609b5e2ce7096362460aa53e85b32), PREPR_SKIP_CLOSURES=1.

## Findings

None.

## Evidence

- Item 1: relay() keeps #2580's hold check (`HELD #$pr $hs; continue`, ahead of the failed-update ledger) and then this PR's single launch (`"${upd[@]}" ... &`, `PR_REAP_LEAD=$!; wait`); a held PR continues before the launch. The three-dot diff of cloud_relay.sh against origin/main shows only the PR's own hunks plus the union `local ... held_prs upd` line.
- Item 2: `cloud_relay.sh --self-test`: 192 checks, 0 failed, including the #2580 hold arms. Launch-mutant harness CR rows on the merged tree: CR-FG killed (the foreground mutant hangs the stop arm, no summary line), CR-FG-BOUND killed (4 failed), CR-LEADNAME killed (2 failed), CR-PRODPATH killed (1 failed).
- Item 3: `git merge-tree --write-tree origin/main HEAD` exits 0. The Red checks section names the one red, nightly-status, with its answer; the check-runs API at this head shows nightly-status as the only red. The checks coverage, fast, browser, closures, instrument-self-tests and Analyze (python) were still in progress when read, so their final result is not part of this verdict; this is not a finding. The stale 5f6a432cc paragraph is gone from the handoff body. `carry_audit check --body` reports 2 routed, 0 unrouted, 0 bad.
- Not re-derived: the body's `## Head` text describes a0cb0cdd7, one main merge behind this head (e7fc65845). That merge is clean.
- Heavy gate and mutation runs not repeated; CI is cited.
