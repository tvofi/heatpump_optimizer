Triage batch 143 rules queue lines 232 and 233, both of which arrived after batch 142. It holds two rulings, P548 and P549, both ACCEPT.

- **P548, ACCEPT on the class-barrier route: S14-ROSTER-SYNC-DUP-CARRIES.** `roster_sync.py` appends a body item the queue had already appended, without the item id, and `roster_edit` refuses only exact repeats. 39 of the 312 open carries (12.5 %), across ten groups, repeat an earlier carry of their group. The fix is one carry to R10-TICK-RESIDUE: the sync skips a body item whose id or normalised text the destination already holds.
- **P549, ACCEPT as a repair of an observed wrong behaviour: S14-CLOUD-CLASSIFY-PAGINATE.** In a cloud seat, `merge_train.py classify` exits 2: its `gh api --paginate` follows a Link header that the proxy answers 403. The reads move to explicit page numbers through `gh_read.py`. The fix is one carry to R10-GH-READ-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch143.md`, the ruling. No product behaviour changes.

## Head

`6e5082b12b4ae381e787c9e31bbf0315174bca7b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P548 and P549 pass `triage_refusal`.
- With P548's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P550 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...6e5082b12b4ae381e787c9e31bbf0315174bca7b`: 1 file.
- The duplicate census reads the roster JSON at `39a92af760`. Every other figure is printed by the read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
