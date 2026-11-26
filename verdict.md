Fix review: merge 98c1e9dff262a71ce3c5285c790b4b6173dd16a9

bus-nonce: e7845a5dc73f589d0052a894981c4c6b

## Scope

Delta round over eead33b0ac600ce4f6ef250ba47166fefe8e0402..98c1e9dff262a71ce3c5285c790b4b6173dd16a9. The delta is the one bot commit `ci: re-record closures` (github-actions[bot]), touching only tests/closures.json. No production (custom_components/) code changed, so the scope is not widened (fix-review.md step 12).

## Evidence

- The previous verdict blocked at eead33b0 on a stale closure: tests/entities.py could not reach tools/ci/shards.py. At 98c1e9df, `closures.tests/entities.py` gains `tools/ci/shards.py`, which settles that block.
- `closures.tests/config_flow_steps.py` gains `custom_components/heatpump_optimizer/services.yaml`. This is a measured addition only: it widens what runs and removes nothing.
- `recorded` seconds change for block_duty.py (8.3 -> 19.8), entities.py (1338.1 -> 2691.9) and harness_headers.py (159.7 -> 320.0). These are timing records only.
- A structural diff of the two closures.json files shows no closure losing an entry and no key added or removed (ev/delta.diff).
- `git merge-tree --write-tree origin/main 98c1e9df` merges cleanly; the LEDGER-MERGE driver resolved closures.json as sets (ev/merge-tree.txt).
- CI at this head: `GREEN 98c1e9dff262a71ce3c5285c790b4b6173dd16a9 pending: none red: none`, classify rc 0 at 14:18:39 UTC (ev/classify.log).
- `tests / nightly-status` reads failure in the packet digest. It is not in `merge_train.py owed-reds`, so it is neither answered nor a block.
- Review packet: refusals none, advisories none, carry_audit 2 items routed, 0 unrouted (ev/review-packet.md).
