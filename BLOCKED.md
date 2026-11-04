# BLOCKED: r10-hotfix-ci-critpath-5, step 1 (re-measure at a45cf7f5) cannot be read

Measured 2026-11-04 (about 23:10 UTC) at base a45cf7f509477596e8024ad2293073f83f04d3e3.

- ci.yml push run 41930400278 (run 4365) for a45cf7f5 is `queued`. Its `tests / ci-ratchet` job has not started, so no `critical_path_minutes` line exists for this head.
- The metric is derived from the newest push-run window fetched from the Actions API with CI's token (tests/ci_ratchet.py). It cannot be reproduced offline, and this seat has no such token.
- The prior main run, 41924930946 (af941ad4, run 4331), was also still queued or in progress, with `tests / closures`, `fast`, `coverage` and `mutation` queued. CI is backlogged, so there is no concluded ratchet verdict for #3201's change.
- The stored budget is `critical_path_minutes: 21.983`, band 1.3 (tests/ci_budgets.json).

Question for the orchestrator: wait for run 4365's `ci-ratchet` conclusion and re-dispatch if it is red. If it is green, this group needs no change. No budget is touched, because re-recording an unmeasured value would be a guess.
