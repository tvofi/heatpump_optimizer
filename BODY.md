Triage batch 205 rules P636 (queue line 313), 2026-11-11. It holds one ruling.

- **P636, ACCEPT, as a carry on R10-TICK-RESIDUE-P3: postmerge's stage write goes through the beat's roster drain queue.**
  - `roster_sync --apply` loses the push race to the drain. Its 3 tries each span the ~4 min lint window, which is the drain's own cadence.
  - train.log holds 6 lost stage writes, 2 of 2 on 2026-11-11 (#3425, #3447).
  - The fix appends the derived op to `roster-drain.queue`: atomic, newline-terminated and idempotent per merge sha.

The diff is one file against the merge base: `dev/programme/triage/s6-batch205.md`, the ruling. No product behaviour changes.

## Head

`065bd080b0e60b725b3f2f184355c031c087928c`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P636 as ACCEPT, and a citation of it passes (`None`).
- With its verdict text flipped, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P637 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat` over the merge base: 1 file, 1 commit.
- The figures come from:
  - `~/.local/state/hpo/merge_train/train.log` (`grep "OWED stage"`);
  - the roster tip at 14:50Z;
  - origin/main `0e28afd38b`.

## Red checks

none

## Forward-carry

none

## Friction

none
