Fix review: merge a8dff54818f8749246fffb9e18344dbbb1318735
bus-nonce: 323f54d89da09c7d5fc06c606ac00579

Delta re-review, git diff d92bb3a7 a8dff548 (branch-side commits are main merges only). All three earlier blocks are resolved:
- tests/deployment_shape.py: the "184 of the 561" merge-chain figure is gone. The note carries no counts and names tests/entities.py's #1218 block as their source.
- tests/entities.py #1218: the figures are derived and printed. A carried count in the note is refused, and a planted-corpus null control backs the refusal. At head CI prints 126 files and 192 of 561 pairs at >= 0.80.
- claims.py: the header reads config_ranges_compared=104. harness_headers at head reports "ok ... config_ranges_compared matches header".
Notes (non-blocking): local runs were blocked by the seat venv (overlay tried, see ev/delta.txt), so the authority is CI fast shards 1-4 green at head. The nightly-ha reds are not required checks.
