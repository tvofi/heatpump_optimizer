Triage batch 162 rules queue lines 257 and 258. It holds two rulings, both ACCEPT.

- **P575, ACCEPT for one arm: DISPOSE-NEVER-CLEARS-BOARD.**
  - `ledger.py` `covered()` (line 393) returns False on an empty merge-base..tip diff. A handoff whose net change is nothing, here `handoff/r10-body-contract-p3-bootstrap` (0 files three-dot, 3 `+` in git cherry), therefore stands STRANDED for good.
  - The fix: an empty net diff lands as `empty`.
  - The disposition arms are already P546, which is R10-REVIEW-DISPATCH-RESIDUE carry 13.
  - The "head newer than BLOCKED" arm is REJECTED: measured, it clears 0 of the 3 named stops.
- **P576, ACCEPT: PENDING-CI-RED-DEADLOCK.**
  - The relay's pending-ci path (`cloud_relay.sh` lines 259-275) refuses a moved head outright, although line 405 already carries verdicts across a range `review_carry.py` answers CARRY.
  - The fix: ask review_carry before refusing, then classify the live head. RED still refuses.
- Both carries go to R10-REVIEW-DISPATCH-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch162.md`, the rulings. No product behaviour changes.

## Head

`153a6936eafc3749b20d4813198e92ef25134fc4`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P575 and P576 pass `triage_refusal`.
- With P576's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P577 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...153a6936eafc3749b20d4813198e92ef25134fc4`: 1 file, 1 commit.
- The ref times and diffs come from git at about 04:50Z. No API calls.
- The line numbers come from origin/main `dbd1ab5b07`.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
