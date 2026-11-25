# Class sweep: N-dropped-refresh (round 11, D14 steps 3-4)

Finding: D1-s1-03 (verified, medium). Mechanism: `DataUpdateCoordinator.async_request_refresh`
goes through `Debouncer.async_call`, which aborts while a call is executing; the
coordinator does not override it, so a re-plan request made during a debounced
in-flight solve never reaches `async_run_optimization`'s #1754 latch
(`_optimization_rerun_requested`). `bugclasses.json` has no entry for this class yet
(`null`); the ledger row is owed with this sweep's fold.

## Detector

`python3 dev/audit/rounds/round11/D14/n_dropped_refresh.py [PKG]` -- AST walk listing every
load of `.async_request_refresh` (calls and the bound method handed to a listener) in the
package; a seam is GUARDED when `coordinator.py` overrides `async_request_refresh` with a
store to the latch, or the calling function stores the latch itself.

`--selftest` result at the register head:
`{"seams": 19, "open": 19, "positive_control": true, "null_on_guarded_fixture": 0, "perturbation_reintroduced": 19}`

- Positive control: every judged site of D1-s1-03 is listed OPEN.
- Null control: a copy of the package with the four-line override (latch when
  `_optimization_running`, then `super()`) yields 0 OPEN.
- Perturbation: deleting the single latch line in that fixture returns all 19 to OPEN.

The detector is static: it measures whether the guard exists, not a runtime race. The
runtime race is measured only for the judged rows, by `D1/s1/m4_race.py` (7 of 8 debounced,
0 of 8 direct, 0 under `--perturb-rerun`). The beyond-finding instances share that one
root and are disposed by the static probe plus the fact that each writes a solve input
before requesting the re-plan; a runtime probe for each one was not run in this sweep.

## Dispositions (19 seams)

| seam | disposition |
|---|---|
| coordinator.py:9921 `async_set_away` | instance, judged (D1-s1-03) |
| coordinator.py:6541 `async_set_mode` | instance, judged |
| coordinator.py:8583 `async_apply_manual_plan` | instance, judged |
| button.py:175 `ResetComfortWeightButton.async_press` | instance, judged |
| coordinator.py:3590 away/holiday listener (`watch_away_inputs`) | instance, judged (the `hass` calendar row) |
| boost.py:681 `set_channel` | instance, beyond finding |
| boost.py:696 `set_block` | instance, beyond finding |
| button.py:192 `ResetHeatLossButton.async_press` | instance, beyond finding |
| services.py:1194 `handle_reset_heat_loss` | instance, beyond finding |
| coordinator.py:1449 `async_adopt_heat_loss_refit` | instance, beyond finding |
| coordinator.py:3592 `InputReturnWatch` callback | instance, beyond finding |
| coordinator.py:6592 `async_update_thermal_params` | instance, beyond finding |
| coordinator.py:8609 `async_clear_manual_plan` | instance, beyond finding |
| coordinator.py:9760 `async_restore_learned_snapshot` | instance, beyond finding |
| coordinator.py:11049 `async_arm_system_identification` | instance, beyond finding |
| entity.py:339 `publish_then_refresh` | instance, beyond finding (every switch/select/number action) |
| __init__.py:355 `async_setup_entry` | not applicable: the first solve; no solve is in flight before it |
| button.py:110 `ForceOptimizationButton.async_press` | not applicable: writes no input; the in-flight solve already reads current inputs |
| coordinator.py:10686 `async_diagnose_interval` | not applicable: stores a diagnosis report, which no solve reads |

No seam is guarded. Instances beyond the finding: 11.

## Proposed barrier

One fix at the root: override `async_request_refresh` on `HeatPumpOptimizerCoordinator`
to set `_optimization_rerun_requested` while `_optimization_running`, then call `super()`.
Barrier: this detector as a `tests/` script (exit 1 on any OPEN seam), under a second of
gate time; not barriered today.
