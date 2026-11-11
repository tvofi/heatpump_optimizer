Triage batch 151 rules queue line 245, which arrived after batch 150. It holds one ruling: P562, ACCEPT narrowed.

- **P562, ACCEPT narrowed, a repair of an observed wrong behaviour: S14-TRAIN-BOT-PR-VOIDS-PROOF.**
  - What happened: a green 44-minute proof was voided when record PR 3422 merged in P191's refusal arm, right after #3405's first merge attempt was refused.
  - The sweep runs before the refusal is classified. Of 59 attempt-1 base-policy refusals in the train log, 21 cleared with no record merge.
  - The arm merged a record PR right after an attempt-1 refusal 4 times, each forcing a recarry or a re-prove.
  - The fix: the sweep runs only after the refusal reads as stuck (not a wait, not a carriable approval), at attempt 2 or later.
  - The proposal's own remedy, bot PRs only after the batch's merges, is rejected: it would bring back P191's s44 deadlock.
  - It is one carry to R10-TRAIN-RESIDUE, as PART 2.

The diff is one file against the merge base: `dev/programme/triage/s6-batch151.md`, the ruling. No product behaviour changes.

## Head

`11aa8c596541388600810247ae6b01985eeb01a7`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P562 passes `triage_refusal`.
- With P562's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P563 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 63bcdcaad8...11aa8c596541388600810247ae6b01985eeb01a7`: 1 file.
- The proof wait, the refusal counts and the sweep instances come from the live train's `train.log`.
- The line numbers come from origin/main `63bcdcaad8`.

## Red checks

`none`. The merge base is main `63bcdcaad8`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
