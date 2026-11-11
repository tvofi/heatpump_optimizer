Item 1 of the brief (the cap line reading as UNREADABLE) was already landed by #3425: `CAP_NOTICE` in `tools/audit/seat/owed_unactioned.py` skips the cap line. This PR only widens that pattern for the new held count. Item 2 sorts held `triage-*batch*`/`record-*batch*` stranded refs after every other ref before the 20-line cap and prints their count in the cap line. Carry 1 (CI-PULSE-ONE-JOB-BASELINE, the brief's "Carry 0") adds a "CI waits on 1 job" pulse line to `Train.wait_ci`, with a same-name baseline from the already-fetched check-runs listing (no extra API call).

## Head

cfc7185fc716f68829f6941e5b700ffebcb9cacc, measured at origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0, 2026-11-11T11:57:40Z.

## Mutation proof

- Pulse baseline: replacing the `durs` computation in `one_job_pulse` with `durs = []` turned the two checks "a one-unfinished listing prints the job, elapsed and its same-name p50/max baseline" and "elapsed past the max reads over max" red in `merge_train.py --self-test`. Restored after.
- Held-last sort: replacing the `stranded.sort(...)` line in `Tick.orphans` with `pass` turned "OWED handoffs held-last: 25 stranded with 14 held..." red in `orchestrator_tick.py --self-test`. Restored after.
- Cap-line key (item 1): not mutated here, because the pattern was not written in this PR; the existing "cap notice" checks in `owed_unactioned.py --self-test` plus a new check for the line with its held count cover the widened pattern.

## Null control

- `orchestrator_tick.py --self-test`: 11 live refs and no held ones print in bus order with no cap line.
- `merge_train.py --self-test`: two unfinished jobs print no pulse line, and none unfinished prints none either.
- `owed_unactioned.py --self-test`: a board holding only a cap line has no key and is not Unreadable.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 315 checks, 0 failed.
- `python3 tools/audit/seat/merge_train.py --self-test`: 613 checks before my additions, 0 failed.
- `python3 tools/audit/seat/owed_unactioned.py --self-test`: 60 checks, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED.

## Red checks

none

## Forward-carry

none

## Friction

none
