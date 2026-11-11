Triage batch 176 rules queue line 272, 2026-11-11. It holds one ruling.

- **P593, ACCEPT, re-scoped: BRIEF-CARRIES-PART-SCOPE.**
  - Three fixer handoffs left a refused body and no `handoff-body` ref on one day. All three trace to `review_packet.py handoff`'s `brief-carries` check. The check counts the group's carries at the roster tip, over the whole group, numbered from 1.
  - Split parts are assigned a 0-based subset at dispatch, and a carry appended after dispatch refuses every in-flight part. P592's own carry stranded p3 that way.
  - The ruling adds a carry to R10-REVIEW-DISPATCH-RESIDUE: count at the dispatch-time roster commit, and only the indexes the part's prompt assigns.

The diff is one file against the merge base: `dev/programme/triage/s6-batch176.md`, the ruling. No product behaviour changes.

## Head

`d0f847b4578096dd8aaeb4dd0e4837dfe3af9b52`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P593 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P594 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat f24d107bd7...d0f847b4578096dd8aaeb4dd0e4837dfe3af9b52`: 1 file, 1 commit.
- The refusal kinds come from each topic's `handoff-wip` `BLOCKED.md`, the relay's `cloud-fold.out`, and a diff of the refused body against the passing one. The carry counts come from the roster branch history. Each is cited beside its source in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
