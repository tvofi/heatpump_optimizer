Fix review: merge 06d9220eb710f9fb2d4452c106776ddad9f588fd
bus-nonce: e9136e87c852d9149fd3f93e3d92813a

Round 2, a delta of the `merge` proposed on review/3818 (a625c2ee9a) at c5795f202c761b4fb2367bcb723985137e52dddd, whose seat ended before confirmation; no verdict/3818 existed.

- Delta: 06d9220eb7 is one merge of origin/main 9d65fe80b0 with no resolution. `review_carry.py c5795f20 06d9220e` prints CARRY; the PR's own three-dot diff at both heads is identical except one `tests/closures.json` hunk header offset (-5088 to -5090). The round-1 measurements (box accounting of all 321 files, the log trims, privacy, no budget, claim or version file) therefore stand unchanged; no production path in the delta.
- Live checks: `merge_train.py classify --pr 3818` reads GREEN, pending none, red none; `review_packet.py` digest green, refusals none, carry_audit 0 items, figure_lint 0.
- `git merge-tree --write-tree origin/main` (main 698eeeb2ab) exits 0; `ref_privacy.py guard` over the head's commits exits 0; roles contract unchanged since the merge base.
- The body's `## Head` names 06d9220eb7 and its lineage to the authored head 00b7d10d9c.
