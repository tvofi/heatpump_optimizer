Fix review: merge f29c16fac7d846ac098fb30eb466c6961c7f9038

bus-nonce: 94b53deb701abce10724f492b7087832

Round 1. Measured at head f29c16fac7d846ac098fb30eb466c6961c7f9038 (the PR head at read time).

## Evidence
- RESULT classify: GREEN f29c16fac7d846ac098fb30eb466c6961c7f9038 pending: none red: none (merge_train.py classify, rc 0).
- RESULT merge-tree origin/main vs head: clean, rc 0, no MERGE-CLAIM lines.
- RESULT self-tests at head: merge_train 579 checks 0 failed; proof_watch 47 0 failed; cloud_dispatch 131 0 failed (matches body).
- RESULT mutants I ran on merge_train.py at head, each restored: comparison dropped (mt<bt -> False): 3 failed (STALE, tie, line-order); same-nonce admission dropped: 1 failed (SAME null control); stale_verdict call removed from posted_verdict: 13 failed. A fourth (registry read-error -> non-empty) was stopped before its result and not counted.
- Checks not re-run by me: the body's harness figures (guard/stale arms over 705 verdict refs, PR 3232 registry) need the bus snapshot and host registry; the packet's figure_lint marks them unverified. Not re-derived.
- VERSION, manifest, RELEASE_NOTES, tests/golden: untouched in the three-dot diff. No claim files touched.
- Red check: governance / delivery-status is red on this head. The diff adds only its own row dev/programme/delivery/3364.md and no script, workflow or plan it reads, so by defect-root-cause.md it is main's, not this PR's. Body's "Red checks: none" is consistent with all other gate checks green. pr-contract success.
- carry_audit at head: 2 finding items routed, 0 unrouted. Both body carries are dismissed with reasons.
- Class enumeration: the body's rule (git grep parse_verdict/posted_verdict/VERDICT_MERGE) dispositions every seam; both admission paths share posted_verdict, where the guard sits. No open seam found.
- Architecture score dS +0.0000 NULL per body; no budget, closure or golden moved in the diff.
