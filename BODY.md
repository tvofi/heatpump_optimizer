Triage batch 145 rules queue lines 236 and 237, both of which arrived after batch 144. It holds two rulings, P552 and P553, both ACCEPT, narrowed.

- **P552, ACCEPT narrowed on the class-barrier route: S14-TICK-STALE-SILENT.** `tick_loop.sh` restarts itself only from a detached head. On a branch-backed checkout it skips the relay and sweep arms every pass, and says so only in its own log. Three episodes, 9, 17 and 1 passes, kept the relay dark for about 4 h. The restart learns to run from a clean branch-backed checkout with no commit outside origin/main. A stale state lasting a second pass puts one OWED line on the board. The liveness-hook arm is dropped as covered by P550. The fix is one carry to R10-TICK-RESIDUE.
- **P553, ACCEPT narrowed, a repair of an observed wrong behaviour: S14-TRAIN-SUPERSEDED-DEFERRAL.** A deferring gate suite's red stands under A5 after its referent concluded success, so PR 3383 sat skipped for about 13 h until a hand re-run. The train re-runs such a suite's failed jobs once, when a later gate suite at the head is green. `failure_logs.sh` breaks a `started_at` tie by `completed_at`. The fix is one carry to R10-TRAIN-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch145.md`, the ruling. No product behaviour changes.

## Head

`4f0c1d7045dbc10466822f06b3ff04ef4a4ba5d2`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P552 and P553 pass `triage_refusal`.
- With P552's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P554 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...4f0c1d7045dbc10466822f06b3ff04ef4a4ba5d2`: 1 file.
- The episodes come from `grep '^TICK-STALE'` over the tick loop's log, grouped by code and cause.
- The gate check-runs were read at each PR's head with `check_name=gate`.
- The SKIP census comes from the merge train's logs. Every other figure is printed by the read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
