Triage batch 181 rules queue line 279, 2026-11-11. It holds one ruling.

- **P600, ACCEPT: OWED-CAP-BLINDS-UNACTIONED, as the new not-started group R10-TICK-RESIDUE-P2 (after R10-TICK-RESIDUE).**
  - The tick's flagged cap line `OWED handoffs capped at 20 of 46` matches owed_unactioned's FAMILY, but no key pattern matches it. On the 09:45Z board the whole check exits rc 2 UNREADABLE.
  - On the same board with only that line removed, the check exits rc 1. It reads 85 keys and reports 2 UNACTIONED, one of them audit-r10-roster at 110.7 h.
  - 14 of the 20 capped OWED handoff lines are held `triage-s14-batch*` refs, which hide 26 more orphans.
  - It is a sibling rather than a carry because #3425 (R10-TICK-RESIDUE) holds a merge verdict.

The diff is one file against the merge base: `dev/programme/triage/s6-batch181.md`, the ruling. No product behaviour changes.

## Head

`49821e122b3ef0333a972756d365ea1943590542`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P600 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P600 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P601 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...49821e122b3ef0333a972756d365ea1943590542`: 1 file, 1 commit.
- The figures come from two `owed_unactioned.py --no-write` runs, on the live board and on the same board with the cap line filtered out, and from the `OWED handoff:` lines of that board. Each is cited beside its command in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
