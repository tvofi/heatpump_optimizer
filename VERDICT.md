Fix review: merge bb64701112e98415646ea8c019a93addb2296789
bus-nonce: 080f34e71888388a06bd0babd83e026a

Delta review from the prior merge verdict at 9bc1e9b9927a2a73c13d8dcc66a3288e48c03177 (later-rounds-review-delta-only). review_carry.py printed FRESH-REVIEW because tests/structure_budgets.json differs from the merged reviewed head.
- Branch-own patches (merge-base...head) at 9bc1e9b9 and bb647011: same 14 files, 269+/49-. Outside hunk offsets, the only change is the structure_budgets.json row: class_excess_loc 17218 -> 17216 and recorded_at e84856520d.
- tests/structure.py at the head measures class_excess_loc = 17216, so 17216 <= 17216 passes (STRUCTURE RATCHET PASSED). The row went down, nothing was raised, and the commit message names the row that moved.
- VERSION, the manifest version and the RELEASE_NOTES heading are unchanged against main.
- Live check-runs at the head: every owed-reds check succeeded, including tests / mutation, tests / fast shards and gate. The only reds are nightly-ha (stable, 2025.2.0) and nightly-status, which are not owed.
- The body names bb64701112 as its head. Its Red checks section answers fast 2/4, instrument-self-tests, gate and mutation.
- The prior verdict's points still hold: the branch's code, tests and harness hunks match those at 9bc1e9b9.
