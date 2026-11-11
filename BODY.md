Triage batch 164 rules queue line 260. It holds one ruling.

- **P578, ACCEPT: DESIGN-REVIEW-OWED-NO-BOARD-LINE.**
  - The gap: the tick prints `DESIGN OWED:` only when no `design/<g>` ref exists, and `DESIGN-BUILD:` only on an approve at the tip. A revised design tip that no design reviewer has been dispatched at fits neither line. Nothing prints, and `owed_unactioned.py` cannot track it.
  - The fix: a `DESIGN-REVIEW OWED:` line in the owed family, git only, keyed on the group and the design tip.
  - Replayed at 05:06Z, the rule prints the three named cases. At 05:20Z it prints 0: 25 designs have a verdict at the tip, and 4 stale ones belong to `done` groups.
  - Measured over every design verdict in the round: 15 of 33 reviews waited more than 2 h for a reviewer dispatch after the design tip, 420.9 h in total (commit-time upper bounds).
  - The carry goes to R10-TICK-RESIDUE PART 2.

The diff is one file against the merge base: `dev/programme/triage/s6-batch164.md`, the ruling. No product behaviour changes.

## Head

`ac2bff21004dfd31011d9d12e17b7ca4ba7e6f02`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P578 passes `triage_refusal`.
- With P578's verdict flipped to REJECT, the same citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P579 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...ac2bff21004dfd31011d9d12e17b7ca4ba7e6f02`: 1 file, 1 commit.
- The design, verdict and dispatch refs are from `git ls-remote` and fetch at 05:20Z, with times from `git log`.
- No API calls.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
