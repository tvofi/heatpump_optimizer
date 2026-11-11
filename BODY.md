Triage batch 161 rules queue line 256. It holds one ruling: P574, ACCEPT.

- **P574, ACCEPT, a repair of an observed wrong behaviour: OWED-CHECK-UNKEYABLE-CAP-LINE.**
  - When more than 20 handoffs are owed, the tick's cap summary (`orchestrator_tick.py` line 2427) opens with `OWED`. That puts it in `owed_unactioned.py`'s family (line 56), which cannot key it, so the whole owed check goes UNREADABLE (line 120).
  - Reproduced read-only at 04:36Z on the live tick: rc 2. With only that line removed, rc 1 and 2 unactioned items, so the cap line hides them.
  - The fix: the writer moves the summary out of the family. A pin in the tick's `--self-test` drives the orphan section past the cap and feeds every emitted family line through the reader's key.
  - The reader-side skip of the exact literal is REJECTED.
  - One carry goes to R10-TICK-RESIDUE (PART 2, PR 3425).

The diff is one file against the merge base: `dev/programme/triage/s6-batch161.md`, the ruling. No product behaviour changes.

## Head

`a0d1be33149f79a89b9cfed3056f61cfb67f0139`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P574 passes `triage_refusal`.
- With P574's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P575 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...a0d1be33149f79a89b9cfed3056f61cfb67f0139`: 1 file, 1 commit.
- The reproduction uses local files only (`r10s6/tick.txt` and `owed-unactioned.json`, copied at 04:36Z). No API calls.
- The line numbers come from origin/main `dbd1ab5b07`.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
