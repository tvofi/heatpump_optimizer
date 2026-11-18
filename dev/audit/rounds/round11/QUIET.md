# Round 11 — D3 quiet-window confirmation

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, worktree `r11/audit-r11-quiet` (detached, HEAD = baseline, no mutant applied).

## Status: window not reached

There was no quiet window on 2026-11-17 at about 14:48 local time: load1 was 111 to 134 on 8 cores. The D3 seats' own prescreens were still running on the box:

- D3-s1 (`r11/audit-r11-D3-s1`): `prescreen.py run --workers 3`, `run --sub c2`, `run --sub c3c6`, `complete --workers 2`
- D3-s3: `prescreen.py --jobs 2 --out prescreen_local.json`

These are the inputs to this window, so they were not stopped. Only D3-s2's report has been published (`handoff/audit-r11-find-B2`). No `handoff/audit-r11-find-*` branch carries a D3-s1 or D3-s3 REPORT.md, so their survivors are not known yet.

No gate ran, and no `gate_lock.py` lease was taken. `tests/stress.py` is quiet-window-only (the D3 trap), so a full gate at this load could give false kills. Its verdicts would not be admissible.

## Mutants (D3-s2), most consequential first — all not reached

| mutant | finding id | survived | killed_by | load1 |
|---|---|---|---|---|
| accuracy.py:261 GUARD_OFF (NaN actual_temp guard in score_lead_predictions) | D3-s2-02 | not reached | — | 133.6 |
| inputs.py:590 setpoint_step `step > 0.0` -> `>= 0.0` (recorded gap) | — | not reached | — | 133.6 |
| ledger.py:739 roll_receipts retention -> `[:0]` (recorded gap) | — | not reached | — | 133.6 |
| store.py:123 _sanitize tuple arm off (recorded gap) | — | not reached | — | 133.6 |
| sensor.py:2879 _gap_energy_rate `<= 0.0` -> `< 0.0` (recorded gap) | — | not reached | — | 133.6 |
| accuracy.py:555 plan_promise `steps < 1` guard off (recorded gap) | — | not reached | — | 133.6 |
| accuracy.py:269 GUARD_OFF (third barrier; M4 says equivalent at every reachable input) | — | not reached | — | 133.6 |
| __init__.py:188 GUARD_OFF (M4 equivalent) | — | not reached | — | 133.6 |
| accuracy.py:111 GUARD_OFF (M4 equivalent) | — | not reached | — | 133.6 |
| accuracy.py:238 GUARD_OFF (M4 equivalent) | — | not reached | — | 133.6 |
| accuracy.py:379 GUARD_OFF (M4 equivalent) | — | not reached | — | 133.6 |
| sensor.py:404 RAISE_DEL (abstract stub, M4 equivalent) | — | not reached | — | 133.6 |
| D3-s1 survivors | — | not reached (report unpublished) | — | 133.6 |
| D3-s3 survivors | — | not reached (report unpublished) | — | 133.6 |

## Re-entry

The window can start once every D3 seat has published its report and no `prescreen.py` or `drive_resumable.py` process is left on the box. Then run `python3 tests/gate_lock.py take --label quiet-r11` and, for each mutant, apply it, commit, and run `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=92d38ecb640bd462f2e19c0814d0f0b7df1ee692 GATE_JOBS=1 ./tests/run.sh`. Each run takes about 1.5 h serial, judging by D3-s2's M5 table.
