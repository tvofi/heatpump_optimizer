Triage batch 171 re-rules queue line 266, which batch 170 rejected as P586. P587 supersedes P586.

- **P587, ACCEPT: CARRY-SOURCE-BARE-NUMBER.**
  - Replayed against the round roster the fold read (`e60ea43333`, before `f63227bd43`): `landed --pr '#3425'` gives 1 missing, and `--pr 3425` gives 0.
  - The cause: `landed` counts an item as landed when a source token is a whole token of the group's text (`carry_audit.py:650`). R10-TICK-RESIDUE's carries say "handed off as PR 3425" and hold no `#3425`, so a bare number matches prose.
  - P586 missed it because its replay read one ref only (`--roster-ref`), not main plus the round roster.
  - The ruling adds a carry to R10-CARRY-AUDIT-P5: an all-digit `--pr` is normalised to `#<N>` in `landed` and `land_ops`.

The diff is one file against the merge base: `dev/programme/triage/s6-batch171.md`, the ruling. No product behaviour changes.

## Head

`c31b3da1424ad01ecf4ff20715e7a47c0ff4856b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P587 as ACCEPT, and a citation of P587 passes (`None`).
- A citation of the superseded P586 (batch 170, REJECT) is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P588 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat a7628041dc...c31b3da1424ad01ecf4ff20715e7a47c0ff4856b`: 1 file, 1 commit.
- The replay ran in a shared clone with `origin/main` at `a7628041dc` and the round roster at `e60ea43333`, on PR 3425's body as the fold read it.

## Red checks

`governance / instrument-self-tests` is red at the merge base `a7628041dc`. That red is main's own (P584), and this one-file record does not touch it.

## Forward-carry

none

## Friction

none
