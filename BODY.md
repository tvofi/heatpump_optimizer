Triage batch 142 rules queue lines 230 and 231, both of which arrived after batch 141. It holds two rulings, P546 and P547.

- **P546, ACCEPT on the class-barrier route: S14-DISPOSE-WIP-GAP.** `cloud_relay.sh` `dispose()` refuses `handoff-wip/` refs, and neither the carry-fold arm nor `bus.sh orphans` reads a disposition. Dead blocked-stop lines therefore stay owed. There are 9 instances: 2 from queue line 208 and 7 from line 230, standing owed for 9 to 34 h. That overturns batch 141's P529, which rejected the class on 2. The fix is one carry to R10-REVIEW-DISPATCH-RESIDUE.
- **P547, REJECT: S14-OVERLAY-KEYS.** `sweep_render.py` refuses overlay keys its placeholder table does not declare. That is one instance per session-start render, worked around with a filtered copy, and under 1 % on every measure.

The diff is one file against the merge base: `dev/programme/triage/s6-batch142.md`, the ruling. No product behaviour changes.

## Head

`8f8f44d50ac529809df2df9d1716f488571c20d5`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads ACCEPT for P546, and its citation passes `triage_refusal`.
- With P546's verdict flipped to REJECT, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P547 is refused as "not an ACCEPT ruling (REJECT)".
- P548 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...8f8f44d50ac529809df2df9d1716f488571c20d5`: 1 file.
- Every ruling figure is printed by the command or read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
