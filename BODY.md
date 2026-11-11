Triage batch 149 rules queue line 243, which arrived after batch 148. The line makes two proposals, so the batch holds two rulings: P559, ACCEPT, and P560, REJECT.

- **P559, ACCEPT, a repair of an observed wrong behaviour: S14-BRIEF-CARRIES-MOVING-TARGET (brief-carries).**
  - `review_packet.py handoff` counts a group's carries on the live roster. R10-TICK-RESIDUE grew from 21 carries at its dispatch to 27, so a finished body was refused twice, two minutes apart, for carries its brief never held.
  - The check is also 1-based while the dispatch renders `Carry 0`. R10-WORKTREE-GC-LIVE's one-carry brief was refused for a `carry 1` that does not exist.
  - The fix counts the dispatched brief's carries, 0-based. It is one carry to R10-REVIEW-DISPATCH-RESIDUE.
- **P560, REJECT: the same line's carry_audit half.** The status-line grammar it asks for already exists: `Carry N: ... Carry: <own group>` prints `CARRY-STATUS` and lands nothing, and the tick body passed with it. finding-propagation.md's "not a carry" is about a destination `git grep` cannot find. A second grammar costs complexity for no gain.

The diff is one file against the merge base: `dev/programme/triage/s6-batch149.md`, the ruling. No product behaviour changes.

## Head

`85316aa1028aecbd7e60f722dcac8431f2dcdf69`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P559 passes `triage_refusal`.
- A citation of P560 is refused as "not an ACCEPT ruling (REJECT)".
- With P559's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P561 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...85316aa1028aecbd7e60f722dcac8431f2dcdf69`: 1 file.
- The carry counts come from R10-TICK-RESIDUE's `carry` length at each roster commit, `2cd3f772f4` to `2f484ff60e`.
- The refusal lines come from the bodies seat's `body_push` logs.
- The line numbers come from origin/main `d08ed31049`.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
