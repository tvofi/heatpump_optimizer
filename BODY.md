Triage batch 195 rules P619 (queue line 297, the roster-repair seat's carry-match proposal), 2026-11-11. It holds one ruling.

- **P619, ACCEPT narrowed: new group R10-ROSTER-CARRY-EXACT-MATCH** (S, instrument, severity low, sonnet). `_carry_index` prefers a carry equal to the match text exactly, then falls back to today's substring rule.
  - A pending carry whose whole text sits inside a sibling cannot be named by any `--match`, and the queue refuses the index form, so the only route is a hand index write past the replay guard (R10-TRAIN-RESIDUE carry 11, `f65729f2da`).
  - At roster `f65729f2da`, 35 of 778 pending carries in 15 groups are in that shape. Matching each by its full text resolves 0 of 35 today and 35 of 35 under the exact rule; the 743 others resolve identically under every rule, with no wrong entry.
  - The unmarked-only filter is rejected: 25 of 35, and it changes what an existing substring names.

The diff is one file against the merge base: `dev/programme/triage/s6-batch195.md`, the ruling. No product behaviour changes.

## Head

`8d3c8f63da3c43934c43e939b0a2046a8c8195c5`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P619 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P619 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P620 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...8d3c8f63da3c43934c43e939b0a2046a8c8195c5`: 1 file, 70 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from the roster at `f65729f2da` and `329c996e8e`, read by the seat's carry-match harness, and from `roster_edit.py` and `roster_queue.py` at `ee64358be7`.

## Red checks

none

## Forward-carry

none

## Friction

none
