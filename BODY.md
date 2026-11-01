Triage batch 98 rules one instrument defect that the orchestrator s9 sent by message on 2026-11-01. The merge seat found it on #3052's recarry: `remerge_main.sh` printed a prepr refusal without naming the arms that failed. This is the rolling batch after batch 97, which was pushed first and left at its head.

- **P353: ACCEPT narrowed, as one carry on R10-FLY-ABORT-OWN-MERGE, reopened to `carries-open`.**
  - **The failing arms were not lost.** prepr's full log persists in `$TMPDIR` (`prepr.sh` line 3502). The refused run's log, `prepr-log.h6GW1PlY`, still names both failing arms on its line 19.
  - **What is lost is the pointer.** `remerge_main.sh` prints only `RECARRY|REFUSE|PUSHED` (line 39) and deletes its push log on every exit (line 19). So neither the FAIL lines nor the `full log:` path reach the merge seat or `merge_train.py`'s Stop message.
  - **The fix.** It prints both, and keeps the push log only when nothing was pushed, as `pr_args.sh`'s `pr_push_failed` already does. It comes with three self-test arms beside the existing `remerge_main` arms.
  - **The measured instance.** #3052's refused run took 2 h 19 min of wall time, about 22 min of it in a heavy slot. A `bash -x` re-run to recover the two lines has been in flight since 03:38Z.
  - **Why this group.** R10-FLY-ABORT-OWN-MERGE owns exactly `remerge_main.sh` and `pr_args.sh`, and has nothing in flight. The train groups each have a second part in flight, and the fix does not touch the train.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`112882355d2a00b7469f4add2b264c05a20ab9fa`; the file is the whole diff against `61b0076f4`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`. The gate was run against the roster at `5cfbe719e`.
- On the committed file, `ruling_verdict` reads P353 as `ACCEPT`.
- `op_set_stage` takes R10-FLY-ABORT-OWN-MERGE from `done` to `carries-open`, and `op_append_carry` accepts the carry.
- `triage_refusal` returns None.
- With P353's verdict changed to `REJECT`, the carry is refused: `dev/programme/triage/s6-batch98.md#P353 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it: `the triage ruling dev/programme/triage/s6-batch98.md is not on the roster branch or origin/main`.
- `brief_lint.mjs` reports 0 error lines on the roster both before and after the two ops.

## Figures

- `s9/seat-merge/rm3052.log`: the banner at `2026-10-31T23:13:32Z`, a modification time of 01:32:54Z, 5 lines, and no FAIL line.
- `$TMPDIR/prepr-log.h6GW1PlY`: line 18 `REFUSE   self-test   429 passed, 2 failed`; the heavy slot `slot=2`, expiring `2026-11-01T01:41:03Z`.
- `grep -rl 'RECARRY: prepr RUNS'` under the session state directory: 6 logs, of which 1 is a remerge refusal.
- No capped file is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
