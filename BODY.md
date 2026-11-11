Triage batch 153 rules queue line 247, which arrived after batch 152. It holds one ruling: P564, ACCEPT narrowed.

- **P564, ACCEPT narrowed, a repair of an observed wrong behaviour: S14-ROSTER-LANDING-MOVING-TARGET.**
  - `review_packet.handoff_not_applied` requires the current tip of `handoff/<t>` in the head. The round roster branch took 97 commits since 00:00Z, with a median gap of 43 s and no gap over 600 s, so the roster landing PR (3377) can never pass while the programme runs.
  - Its head already contains the snapshot its body names, an ancestor of the tip.
  - The fix: for the round roster topic only, the packet accepts a head containing the body's named snapshot when that snapshot is an ancestor of the tip, with an advisory.
  - The drain-hold alternative is rejected: it would stop every roster op.
  - It is one carry to R10-REVIEW-DISPATCH-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch153.md`, the ruling. No product behaviour changes.

## Head

`66b389870aeac2d7a95e11d57dbefecebf3637a2`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P564 passes `triage_refusal`.
- With P564's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P565 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 63bcdcaad8...66b389870aeac2d7a95e11d57dbefecebf3637a2`: 1 file.
- The commit cadence comes from `git log --format=%ct` on the roster branch.
- The snapshot ancestry comes from `git merge-base --is-ancestor`.
- The line numbers come from origin/main `63bcdcaad8`.

## Red checks

`none`. The merge base is main `63bcdcaad8`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
