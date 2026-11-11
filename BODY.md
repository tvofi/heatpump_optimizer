Triage batch 166 rules queue line 262. It holds one ruling.

- **P580, ACCEPT (arm 3, corrected): CARRY-FOLD-ARM-REJUDGES-EVERY-PASS.**
  - The arm's read loop (ls-remote, then a fetch and a `BLOCKED.md` show per wip topic) costs 27-33 s a pass. That was measured on 46 topics, 15 of them blocked.
  - The larger cost: a fold whose `body_push.sh` failed after `carry_fold.py` succeeded is never recorded, so it re-runs on every pass. Two topics do this today, about 181 s a pass.
  - Together the arm is about 211 s, roughly 36% of a 588-605 s relay pass. A memo keyed on (topic, wip sha, body sha), with a 3600 s retry for failures after the fold, saves about 30%.
  - The memo must re-emit each stored OWED level line, because `level_set` replaces the whole carry-fold level every pass.
  - The carry goes to R10-REVIEW-DISPATCH-RESIDUE.
  - Arms (1) and (2), widening `dispose` to `handoff-wip/`: REJECT. They add a hand step per ref and save nothing once (3) lands.

The diff is one file against the merge base: `dev/programme/triage/s6-batch166.md`, the ruling. No product behaviour changes.

## Head

`44106d026f1054572072c8d9e03561c517519d38`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P580 as ACCEPT, and a citation of P580 passes (`None`).
- With P580's verdict flipped to REJECT, the same citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P581 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".
- In the measurement, the 11-10 relay passes (median 563-590 s) bound the rest of the relay. With no failed fold, the saving falls to the read loop alone, about 5%.

## Figures

- `git diff --stat a7628041dc...44106d026f1054572072c8d9e03561c517519d38`: 1 file, 1 commit.
- The relay pass lengths come from tick-loop.log's `TICK-RELAY` lines. The fold timings come from the state dir's fold-file mtimes in the 05:48-05:51Z pass. The read loop was timed from a seat worktree at 06:00Z.
- No API calls.

## Red checks

`none`. The merge base is main `a7628041dc`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
