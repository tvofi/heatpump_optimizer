Item 1 of the brief (the cap line reading as UNREADABLE) was already landed by #3425: `CAP_NOTICE` in `tools/audit/seat/owed_unactioned.py` skips the cap line. This PR only widens that pattern for the new held count. Item 2 sorts held `triage-*batch*`/`record-*batch*` stranded refs after every other ref before the 20-line cap and prints their count in the cap line. Carry 1 (CI-PULSE-ONE-JOB-BASELINE, the brief's "Carry 0") adds a "CI waits on 1 job" pulse line to `Train.wait_ci`, with a same-name baseline from the already-fetched check-runs listing (no extra API call).

Repair round for the blocked verdict (mutation-vacuous: M4, M5, M8). The duplicated `HELD_TOPIC` and sort/held lines had no caller beyond the first copy and are removed, so M8 now mutates the single sort line. Checks added first: `wait_ci` is driven end to end and must log the pulse after each beat (M4); the baseline history's oldest run is a 9000 s outlier outside the BASELINE_JOBS window, so removing or shortening the window moves the printed max and p50 (M5, M5b); a `record-*batch*` ref is in the held set, so narrowing the regex to triage alone fails (M10).

## Head

1131843cf418a2bc0bb81c28bac1be45ea7d1def, measured at origin/main 0e28afd38b353ca8e66269d9ae4be8614fcf5cfb, 2026-11-11T15:22:00Z.

## Mutation proof

Driver: `tools/audit/seat/mutant_run.py --spec <spec> --cmd '<self-test>'`, run on the committed tree; every spec printed `SURVIVED NULL` first (the unedited tree passes), then one line per mutant. Every mutant below is KILLED; no survivor.

- `merge_train.py --self-test`: M4 `self.log(pulse)` in `wait_ci` replaced by `pass`; M5 `done[-BASELINE_JOBS:]` replaced by `done`; M5b window shortened by one; M1 `durs = []`; M6 `over max` comparison flipped; M7 single-unfinished guard `!= 1` to `< 1`.
- `orchestrator_tick.py --self-test`: M8 the `stranded.sort(...)` line replaced by `pass`; M9 `held = 0`; M10 `HELD_TOPIC` narrowed to `triage` only.
- `owed_unactioned.py --self-test`: M11 the optional held-count group removed from `CAP_NOTICE`.

## Null control

- `orchestrator_tick.py --self-test`: 11 live refs and no held ones print in bus order with no cap line.
- `merge_train.py --self-test`: two unfinished jobs print no pulse line, and none unfinished prints none either.
- `owed_unactioned.py --self-test`: a board holding only a cap line has no key and is not Unreadable.
- `mutant_run.py`'s own NULL mutant (no edit) SURVIVED in all three specs.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 315 checks, 0 failed.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`: 614 checks, 0 failed.
- `python3 tools/audit/seat/owed_unactioned.py --self-test`: run by `prepr.sh`/CI scope.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED.

## Red checks

none

## Forward-carry

none

## Friction

none
