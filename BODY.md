The beat's `opener` job (`beat_jobs.py opener`) hands `open_driver.py` the tick board (the overlay's `tick_log`), where every owed level line is rendered flagged, `-> OWED: OWED <utc> handoff-no-pr refs/heads/handoff/<topic> <sha> ...` (`orchestrator_tick.py`: `"-> "` + `f"OWED: {row}"`). `open_driver.BOARD_RE` was anchored at a bare `^OWED`, so `parse_board` read zero topics from the live board: the open arm opened nothing and its state stayed `{}` while seven handoffs, a critical-path one among them, sat with no pull request (2026-11-09). Its self-test fixture wrote bare lines only, the shape no producer writes to that board, so it passed. Process state: the reader's fixture was written from the reader's own grammar, not from the writer's output. Fix: `BOARD_RE` accepts the board's `-> OWED: ` flag in front of the bare line; the self-test now carries the flagged form, and a null that an unflagged line is not owed. Alternative rejected: pointing the beat at the relay's `cloud-relay.log.level` instead, which would drop the ledger-derived `handoff-no-pr` lines the tick folds into the board.

## Head

7d6540509c884772cfbf0739ed876a6a619f9669

## Mutation proof

Reverting `BOARD_RE` to the bare `^OWED` anchor turns `python3 -I tools/audit/seat/open_driver.py --self-test` red: "FAIL parse_board: the tick board's flagged -> OWED: line is read", 91 checks, 1 failed (this was the failing check written first, run against origin/main's regex).

## Null control

At origin/main the existing 89 checks pass and the new flagged-line check fails; the unflagged-line null (`   OWED: ...` is not owed) passes at both ends, and a flagged `handoff-update` line is ignored at both ends.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test`: head 91 checks, 0 failed.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: head 185 checks, 0 failed.

## Red checks

none

## Forward-carry

none

## Friction

none
