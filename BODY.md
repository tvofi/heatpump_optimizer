Triage batch 101 rules one routing amendment that the orchestrator s9 sent by message on 2026-11-01. The train parked #3080, batch 98's record pull request, because a finding there is routed to a group that is done. This is the rolling batch after batch 100, which was pushed first and left at its head.

- **P357: ACCEPT.** It moves two triage carries off groups that are done. Each carry keeps the ask and controls it was ruled with.
  - **P353** (batch 98, the remerge_main.sh push log) goes to R10-TRAIN-OVERLAP-GRADE instead of reopening R10-FLY-ABORT-OWN-MERGE. That group is live: `carries-open` on the roster branch and `in-review` on origin/main. It already carries remerge_main.sh, and it owns the train's recarry path. Its part 2, #3063, has merged, and nothing of it is in flight.
  - **P354(a)** (batch 99, `posted_verdict` keyed on the tree) already landed as carry 5 of R10-FLY-TRAIN-DEFAULTS, which is done. It moves to R10-TRAIN-MERGE-LOOP. That group is where the s9 carry-routing pass sent P331's carry, the verdict and approval reading that P354's Binding chose its group for.
  - **What it cannot clear.** The verdict comment on #3080 (6553573489) still names R10-FLY-ABORT-OWN-MERGE, and `carry_audit` keeps every marker's destinations. A body marker adds a live one but does not drop the done one, so the ruling leaves that marker to the orchestrator.

Roster ops are queued `#held` in the session's roster queue: a `drop-carry` on R10-FLY-TRAIN-DEFAULTS together with an `append-carry` on R10-TRAIN-MERGE-LOOP, and an `append-carry` on R10-TRAIN-OVERLAP-GRADE released once batch 98 is also on main. Batch 98's `set-stage` and `append-carry` lines are marked `#superseded`. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`3a7d7a712f232cfa1df1c2e122c2e807cdccf2d8`; the file is the whole diff against `c3b7c964f`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P357 as `ACCEPT`, and `triage_refusal` passes both carries.
- With the verdict flipped to `REJECT`, the carry is refused: `dev/programme/triage/s6-batch101.md#P357 is not an ACCEPT ruling (REJECT)`.
- On roster branch `3f6dc470f`, the three ops apply. R10-FLY-TRAIN-DEFAULTS goes from 6 carries to 5, R10-TRAIN-MERGE-LOOP from 4 to 5, and R10-TRAIN-OVERLAP-GRADE from 20 to 21. A second `drop-carry` is refused: `no carry entry matches`.

## Null control

- With the file absent, a carry citing it is refused, because the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch101.md is not on the roster branch or origin/main`.

## Figures

- `python3 -I tools/audit/carry_audit.py pr 3080` prints `BAD-DEST #3080 review 6553573489 item bd9082e1: R10-FLY-ABORT-OWN-MERGE: R10-FLY-ABORT-OWN-MERGE is done (resume.stage done)` and `0 routed, 0 unrouted, 1 bad destination(s)`.
- `carry_audit.py check` with #3080's body plus `Carry: R10-TRAIN-OVERLAP-GRADE (item bd9082e1)` still prints `1 bad destination(s)`: the marker routes the item, and the done destination stays.
- `gh pr view 3063`: MERGED (R10-TRAIN-OVERLAP-GRADE part 4).
- `node tools/policy/brief_lint.mjs` on the roster before and after the ops: `TOTAL: 0 error(s)` both times.
- No capped file is touched.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
