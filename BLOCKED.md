# BLOCKED: r10-disinfection-step-notice main-conflict repair

Question: prepr.sh's `closures` step refuses only because `tests/features.py` exits 1 at origin/main 50373173d4 itself, a check that reads the wall-clock date and fails every Saturday and Sunday (UTC). Should this head be handed off as it stands (the train re-proves it on a weekday), wait for prepr to be re-run on a weekday, or is the date-dependent test to be fixed, and by which seat? It is not this group's seam.

Merged head: a07c37b273744ade8cc2c48d07d4a79c58365196 = handed-off head 5c961851a2aa13501912dc5f959f8270ba7885c0 + merge of origin/main 50373173d486faf394b24637c177ab38b691b394 (conflicts resolved; see the commit message). Not pushed to handoff/r10-disinfection-step-notice; body not published.

## The refusal (prepr.sh run 2026-11-14 ~01:10Z on a07c37b273)
`REFUSE closures  failed while being recorded: tests/features.py (exit 1) -- fix the script first`.
Every other prepr step at this head is ok, skip, info or WARN (`unpinned sites` WARN, answered in the drafted body's `## Unpinned sites`, which the body check accepts).

## Cause, measured
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `1 of 5571 FEATURE CHECKS FAILED` at origin/main 50373173d4 (checkout /root/wtmain) and the same at a07c37b273. In both logs the one FAIL is `a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked`.
- Source read (origin/main): tests/features.py `_chg_seq` sets `start = dt_util.now().replace(hour=..., minute=..., second=0)` (date taken from the wall clock), and only shifts it to Saturday when `saturday=True`. The clause `_chg_partial[3] == [1, 0] and _chg_partial_sat[3] == [0, 1]` therefore expects a weekday day type from `_chg_partial`, which on a Saturday or Sunday run is `[0, 1]`. Today 2026-11-14 is a Saturday. The check came in on main's history of tests/features.py through fix/r10-outside-dhw-start-hysteresis (#3531's group): efe1ae593c, ac3e2559ad.
- Not run under a weekday clock (no faketime here); the weekday pass is inferred from reading, not measured.

## Merged-head evidence already taken
- tests/guard_pins.py ALL 79 PASSED; tests/block_duty.py ALL 153 PASSED; tests/structure.py PASSED (class_excess_loc 17502 <= 17502); archscore dS +0.0000 vs 50373173d4.
- Scoped gate (GATE_SCOPE=auto, MODE: SCOPED -- 23 script(s)): only tests/features.py failed, on the check above.
- prepr diff mutants: ok with MUTANT_CMD running guard_pins and block_duty.
