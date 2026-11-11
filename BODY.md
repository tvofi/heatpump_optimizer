Triage batch 152 rules queue line 246, which arrived after batch 151. It holds one ruling: P563, ACCEPT.

- **P563, ACCEPT, a repair of an observed wrong behaviour: S14-LANDED-PR-NEEDS-ROSTER-PR.**
  - `bus.sh carry_landed` passes only `--pr "#N"` to `carry_audit.py landed`, and `own_group` skips every `#` source. So a fresh PR whose body holds a status line on its own group's carries is refused at its first reviewer dispatch. PR 3424 was refused, 3 missing.
  - The same body with the PR's head ref as `--topic` passes at the round ref: 0 missing.
  - The source's cause, a missing `resume.pr`, is not read by `carry_audit` at all, so its `roster_sync` remedy is rejected.
  - The fix: `carry_landed` passes the head ref it can read in its existing API call.
  - It is one carry to R10-PREPR-RESIDUE, as PART 2, beside P557, which changes the same call.

The diff is one file against the merge base: `dev/programme/triage/s6-batch152.md`, the ruling. No product behaviour changes.

## Head

`bacfe934d3a9072cfe81d2671ab6368100c4683e`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P563 passes `triage_refusal`.
- With P563's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P564 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 63bcdcaad8...bacfe934d3a9072cfe81d2671ab6368100c4683e`: 1 file.
- The six `landed` runs over PR 3424's body are in the ruling's table.
- The line numbers come from origin/main `63bcdcaad8`.

## Red checks

`none`. The merge base is main `63bcdcaad8`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
