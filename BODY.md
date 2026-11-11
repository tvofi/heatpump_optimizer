Triage batch 147 amends batch 146's P554 on the orchestrator's measured correction, and rules queue line 240 as P556. Both are ACCEPT, narrowed.

- **P554 amendment: S14-PULSE-VERDICT-WHILE-TRAIN-LIVE.** The train also holds its spool, `queue-add.jsonl`. At 01:10Z it held 3389-3392, so 9 of the 13 STOPPED verdicts were held and only #3379 and #3419 were in no queue; batch 146 said six.
  - `pulse.py` reads the holdings through merge_train's own `already_held`. Only its "spooled" and "still to run" answers count as held. A PR skipped at its current verdict stays STOPPED, because the train will not retry it.
  - Batch 146's carry was voided in the queue before it drained. This one replaces it in R10-STANDING-CONTRACTS-P2.
- **P556, a repair of an observed wrong behaviour: S14-CARRY-FOLD-WRONG-CHECKOUT.** The relay's carry fold ran `body_push` from a worktree at main's tip: 18 times for one topic on 11-10, and once at 01:06Z. The source's proposed fix, a throwaway worktree at the handoff tip, has been on main since 2026-11-08. Run sequentially, its two steps land the right head.
  - The carry is reproduce-first: fetch into a private ref instead of `FETCH_HEAD`, and assert that the worktree head equals the `ls-remote` tip before `body_push`.
  - The fix is one carry to R10-REVIEW-DISPATCH-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch147.md`, the ruling. No product behaviour changes.

## Head

`e6d28754d98f22885b68870f583404c646e5927a`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P554 and P556 pass `triage_refusal`.
- With P556's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P557 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...e6d28754d98f22885b68870f583404c646e5927a`: 1 file.
- The 01:10Z spool contents are the orchestrator's measurement. The relay refusals come from `tick.txt.relay.log` and `tick-loop.log`. Every other figure is printed by the read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
