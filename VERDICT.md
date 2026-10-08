Fix review: merge 28c1f2bee9d208a78c984a4d3ae050b0a6e9db0e
bus-nonce: 89b385b19998182024e5703902803a61

Round 1, head 28c1f2bee9d208a78c984a4d3ae050b0a6e9db0e.
(a) Three-dot diff vs merge base 816547ef is exactly the one inert_reads line (sorted between eg_b7_seam_hubs.py and h8_single_scenario.py) plus dev/programme/delivery/2055.md.
(b) Main's closures red at 470bbd60 (job 113210470058) and 816547ef (job 113224039800) names exactly tests/harness_headers.py: dev/audit/harnesses/git_auto_maintenance_race.sh, nothing else.
(c) closures at the head is success (job 113246938034, "Fail if tests/closures.json under-approximates" success). Other non-green: delivery-status and nightly-status (not required, nightly-status reads mutation-ledger/mutation-nightly/record-autofix from 2026-10-07, diff reaches neither: not this PR's per fix-review.md step 11); budget-raise-gate cancelled run 113246365669 has success twin 113246374402. coverage settled success.
(d) #2051 head afbaaf73 closures job 113198518531: SCOPE_CASE scoped, "Scoped re-derive", zero mentions of harness_headers; supports the body's cause. Process answer given in the body as a recorded candidate.
Evidence: /Users/timmalmstrom/hpo-seats/review-2055/wt/ev
