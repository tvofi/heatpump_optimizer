Triage batch 144 rules queue lines 234 and 235, both of which arrived after batch 143. It holds two rulings, P550 and P551, both ACCEPT, narrowed.

- **P550, ACCEPT narrowed, an amendment to P506: S14-LIVENESS-STALE-PATTERNS.** The session-local liveness hook and its proof hard-code a session path and demand a standalone `cloud_relay.sh pass` process. `tick_loop.sh` runs the relay once per pass instead. The tracked `hooks/liveness.py` already reads its loop list from `beatd.py status`, so P550 constrains the arms P506 adds rather than adding one:
  - the restart arm relaunches only `beatd`;
  - the relay is judged live by its log age;
  - no session path is named.
  The fix is one carry to R10-STANDING-CONTRACTS-P2.
- **P551, ACCEPT narrowed, a repair of an observed wrong behaviour: S14-BRIEF-OVER-FIVE.** Four fixers were published with more than five carries and no part named, and one of them stopped (25 %). The orchestrator's answer was a mechanical split, index-ordered fives. `dispatch_group` will refuse a fixer with more than five pending carries unless it gets `--part k`; the refusal prints that split, and `--part` renders the part line. The fix is one carry to R10-REVIEW-DISPATCH-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch144.md`, the ruling. No product behaviour changes.

## Head

`01f299b9c5f0f4695c772d3c8cba1c069ce07e6c`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P550 and P551 pass `triage_refusal`.
- With P551's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P552 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...01f299b9c5f0f4695c772d3c8cba1c069ce07e6c`: 1 file.
- The pending-carry census reads the roster JSON at `38db9e1130` through `roster_lib.pending_carries`.
- The dispatch times are the commit times of the `dispatch/fixer-*` tips. Every other figure is printed by the read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
