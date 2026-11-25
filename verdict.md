Design review: approve 869c3441a36bd9028dd5a43bb31c06a348a906f9

Second review of design/R11-OUTSIDE-START-APPROACH at 869c3441a3 (ref unmoved at review start), delta-first against 65d571d655, base 0e1eba2b4a. Revise point 1 of 4c0c286d03 (`class-open`, axis "readers that compare the plan's shipped draw against the meter") is answered.

## Revise point 1: answered

- The axis is now enumerated by a rule: four `git grep` roads (R1 `_commanded_power()`/`_commanded_split()`, R2 the settled interval's copy, R3 `plan_promise(`/`power_schedule`, R4 the direct `action.get("power"`/`get("dhw_power"` reads). Each disposition is E (reads the expected draw), G (gated while the step is inside the profile), or a residue category with its reason (F, T, W, A, P, Record, ruled).
- I re-ran the four commands at 0e1eba2b4a. Every R1 line (963, 970, 1002, 1096, 1137, 1175, 3552, 4971, 4993, 5182, 5256, 5292, 8630, 9056, 9270, 10055, 10056, 10751, 10800, 10839) has a disposition. So do the R2 lines (accuracy.py's `predicted_power_kw` readers 383 and 646-650, coordinator 9964/9965, 10000 and 10008, `ledger.py:368`), and the R3 lines and their continuations (2364, 3121/3124, 3176, 4504/4505, 4809/4816, 8900-8903, 10173/10174, 10554/10559, 10947). Lines the note names but no command returns (10261, 8887, 11021, 10603, 5582, 1262) are covered too.
- The predecessor's three named readers: the defrost derate (`delivered_ratio` via `predicted_power_kw` from `coordinator.py:10055`), `power_ratio` (`accuracy.py:383`) and the cost error (`coordinator.py:10008`) are E, through the pending prediction's power. The plan-promise cost curve is E: `note_promise` (`accuracy.py:229`) is `plan_promise`'s only caller, fed from `coordinator.py:10173`, which the shape files from the received space schedule. `ledger.py:368`'s `meter_calibration` is E as well.
- The predecessor's example was measured, not assumed (spike s2): `REASON_ASK_IGNORED` is not the gate, and the derate moves to 0.930/0.947 against 1.000 at the floor. The failing case and its null are under Evidence 7, with three mutations. The null control moves under the finding's perturbation (the pending power reverted to `_commanded_power()` gives today's 0.947).
- The delta's other changes: `accuracy.py` leaves the hot list, with its readers moving through the sample. One accessor joins `coordinator.py` beside `_commanded_power`, a caller of the `runs.py` function, so `runs.py` still owns the received draw and there is no new write path. There are seven production files, and the p1/p2 split stays ruled. The seam, shape, sibling and cost items under "Checked, no point" in 4c0c286d03 carry: the delta changes none of them beyond what is stated here.

## Routed (no revise point)

- Stated in the note and kept: `_power_headroom` (`coordinator.py:8900`) offers up to 0.72 kW the pump is already drawing on an entry step. The note names it for owner decision under the shipped-total ruling. decision: owner.
- The group is on the roster on handoff/audit-r11-roster only. decision: orchestrator, as the note states.

## Notes for the fixer

- Item s8 makes any R4 line with no named disposition a stop, and at 0e1eba2b4a R4 returns four lines the note does not name. `coordinator.py:4944`/`:4945` are `_commanded_split`'s own body, the same category as `:4971`. `coordinator.py:10059`/`:10060` write the pending `space_power`/`dhw_power`, whose one reader is `_planned_split` (`coordinator.py:1260-1262`). `_planned_split` feeds W (`_settle_interval_diag` at `:1283`, the energy settlement's attribution at `:10283`) and F (`planned_total`, the fallback at `:10261`). These are dispositions, not a stop: they stay on the shipped split. Carry: R11-OUTSIDE-START-APPROACH (item v2-1)
- `meter_calibration` (`ledger.py:368`) will divide metered by expected kWh, so stored savings stop scaling by the entry excess. Case 7 should pin this beside `power_ratio`. Carry: R11-OUTSIDE-START-APPROACH (item v2-2)

Seat tokens: the harness reports none for this seat.
