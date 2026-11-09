Fix review: merge 07ad9ae34ab5903bb2c103a2828fc71910b30a7e

bus-nonce: a7da0eea72898859480f41210d92d972

Round 1. Head measured: 07ad9ae34ab5903bb2c103a2828fc71910b30a7e (ev/HEAD.txt).

## Evidence
- RESULT mutation de.json: deleting the flow_min_lift_k label line fails harness_headers.py with 3 of 112 checks (claims_true header 123 vs printed 122, claims_false header 0 vs printed 1, harnesses byte-identical), matching the body. Restored.
- RESULT mutation card: dropping the two de savings.* lines fails tests/card.mjs on key-for-key parity (de missing savings.below_meter_floor, savings.meter_floor_note) and on the null-control check, matching the body. Restored.
- RESULT at head: claims.py prints claims_true=123 claims_false=0; harness_headers.py ALL 112 PASSED; card.mjs ALL CARD CHECKS PASSED; card_drift identical in all 45 states; structure.py STRUCTURE RATCHET PASSED. (First card.mjs run needed tests/plan_view.py run first; environment only.) I did not re-run tests/entities.py to completion; its figure in the body is not re-derived by me.
- Diff is 3 files (de.json, card.js, delivery/3378.md); VERSION, manifest and RELEASE_NOTES untouched; no claim file, budget or closure moved.
- git merge-tree --write-tree origin/main head: exit 0, clean (ev/merge-tree.txt).
- CI: merge_train.py classify at this head exits 0: GREEN, pending none, red none. The packet's earlier gate and pr-contract failures were stale at render; classify is the live state.
- Class rule: the body names the two key-parity checks (C112 and card.mjs key-for-key) as the enumeration; both pass at the head, so the class is one seam per language set.
- Forward-carry: none named in the body; none required.
- carry_audit: 0 findings.

## Findings
none
