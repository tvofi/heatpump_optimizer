Triage batch 146 rules queue lines 238 and 239, both of which arrived after batch 145. It holds two rulings, P554 (ACCEPT, narrowed) and P555 (ACCEPT).

- **P554, ACCEPT narrowed: S14-PULSE-VERDICT-WHILE-TRAIN-LIVE.** `pulse.py`'s verdict arm counts verdicts the live train holds as STOPPED.
  - Of the 13 STOPPED verdicts in the snapshot, the train's `queue.pending.json` held five. Six were in no train queue and were real owed work; one of them, #3392, was CLEAN for 24.1 h.
  - So a verdict counts as held only when it is in `queue.pending.json` and the train pid is alive, never merely in `queue.seen.json`, which keeps PRs the train already skipped.
  - The fix is one carry to R10-STANDING-CONTRACTS-P2, which owns `pulse.py`.
- **P555, ACCEPT, a repair of an observed wrong behaviour: S14-DRAIN-REFUSAL-NOT-DURABLE.** The beat's roster drain marks a refused op done, like an applied one, and its only report is a job file the next pass overwrites. The queue file's 261 `#refused` marks show how often refusals happen. Each refusal now appends one line to `digest/events.txt` and goes to a separate refused-state memory. The fix is one carry to R10-TICK-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch146.md`, the ruling. No product behaviour changes.

## Head

`819ca4896a43090d2dada47ecbe02562c6150b38`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P554 and P555 pass `triage_refusal`.
- With P555's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P556 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...819ca4896a43090d2dada47ecbe02562c6150b38`: 1 file.
- The verdict snapshot is `beatd/pulse.txt`, read against the merge train's `queue.pending.json` and `queue.seen.json` and `gh pr view` states.
- The refusal counts are `grep -c` over the roster queue file. Every other figure is printed by the read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
