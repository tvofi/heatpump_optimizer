Triage batch 178 rules queue line 276, 2026-11-11. It holds one ruling.

- **P597, ACCEPT, widened: TRAIN-SKIP-RELEASES-WORKTREE.**
  - `skip()` never releases the entry's recarry worktree `state/wt/<pr>`. It is released only when the train closes, so `update_pr.sh` answers BUSY on that branch for as long as the train lives.
  - The relay logs show 40 BUSY passes across 6 pull requests. Every one of those pull requests was skipped, at the recarry, carry or ci phase.
  - The ruling opens the new not-started group R10-TRAIN-RESIDUE-P2 (S, after R10-TRAIN-RESIDUE) to release a skipped entry's worktree at its SKIP line, at every phase. R10-TRAIN-RESIDUE is carries-open, and `carry_receivable` refuses it as a destination.

The diff is one file against the merge base, in two commits: `dev/programme/triage/s6-batch178.md`, the ruling, then its destination amended. No product behaviour changes.

## Head

`183a71c402b5ac3395a1f17ee3fd44c762fae120`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P597 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P597 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P598 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...183a71c402b5ac3395a1f17ee3fd44c762fae120`: 1 file, 2 commits.
- The figures come from `cloud-relay.daemon.log` and `tick-loop.log` (grep `BUSY.*merge_train/wt/`), from the train's `SKIP #<pr>` lines, and from `merge_train.py` at `cbd23f1c8b`. Each is cited beside its command in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
