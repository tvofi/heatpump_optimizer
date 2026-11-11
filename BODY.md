Triage batch 172 rules queue lines 267 and 268, 2026-11-11. It holds two rulings.

- **P588, ACCEPT: GH-BUCKET-SPENDER-UNLOGGED.**
  - The `gh` shim is installed on no PATH, so `gh_calls.py --top` printed `(none)` with rc 0 through a core-bucket drain.
  - A 600 s process sample shows 563 core calls in 10 min. `orchestrator_tick.py` accounts for about 21% of the bucket, the orchestrator's out-of-tree `blind_spots.py` for about 7.5%, and the merge train for about 3.7%. About 50% is unattributed.
  - The ruling adds a PART 2 ITEM carry to R10-GH-READ-RESIDUE, reopening the half of P449 that PR 3427 dismissed: `gh_calls.py` refuses (rc 3) when no call is logged, and `tick_loop.sh` puts the seat bin dir on its children's PATH.
- **P589, ACCEPT, re-pointed: EVIDENCE-CARRY-WORD-NOT-MARKER.**
  - All 3 measured Evidence `[carry]` refusals were mentions of the word `Carry:`, not markers.
  - The ruling adds a carry to R10-CARRY-AUDIT-P5: in structural sections, `Carry:` counts as a marker only when a destination shape follows it.

The diff is one file against the merge base: `dev/programme/triage/s6-batch172.md`, the ruling. No product behaviour changes.

## Head

`223a1d27b7548cd0d75dfda98dca15f762615d86`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P588 and P589 as ACCEPT, and citations of both pass (`None`).
- A citation of a REJECT ruling (batch 170's P586) is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P590 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat a7628041dc...223a1d27b7548cd0d75dfda98dca15f762615d86`: 1 file, 1 commit.
- The figures come from the process sample with `rate_limit` at both ends, `ps eww` PATH reads, and grep counts over the relay and tick-loop logs. Each is cited beside its command in the ruling.

## Red checks

`governance / instrument-self-tests` is red at the merge base `a7628041dc`. That red is main's own (P584), and this one-file record does not touch it.

## Forward-carry

none

## Friction

none
