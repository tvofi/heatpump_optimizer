# D12-s1 — generalization, steps M1 and M6 (baseline 17f1c55fad1b)

Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D12/s1/cells.py [--shrink dhw|pv|zone] [--perturb-reading-ok]`

## Method
- M1 (inventory): the plant is derived from the 23 option pages (`HeatPumpOptimizerOptionsFlow._MENU_LABELS`)
  by the same seeded fixed-point walk as `tests/golden.py:capture_config_flow`:
  43 optional entity slots, 42 boolean toggles; crossed with 5 `coordinator_scenarios` and 50 golden `SCENARIOS`.
  Cells = reference + 43 mapped slots + 42x2 toggle states + all-seeded = 129, on the richest plant
  (`coord_all_features` + `coord_two_zone`).
- Each cell drives `golden.capture_coordinator` (real `_forecast_arrays`, `_build_data_dict`, sensor advisor,
  sensor `async_setup_entry`, no-NaN invariant) and separately counts reading sensors (`_reading_key`)
  that are available with a value although FakeHass holds no state (fabricated thermometer).
- M6 (perturbation): plant shrunk by dropping DHW, PV, or the second zone; plus an in-memory production
  perturbation `sensor._reading_ok -> True` to prove the fabrication count can move.

## Results
| arm | cells | fail_cells | fabricated_reading_cells |
|---|---|---|---|
| reference (all features, two zone) | 129 | 0 | 0 |
| --shrink dhw | 129 | 0 | 0 |
| --shrink pv | 129 | 0 | 0 |
| --shrink zone | 129 | 0 | 0 |
| --perturb-reading-ok | 129 | 0 | 129 |

## Findings
None.

## Non-findings
- No cell crashes coordinator assembly or sensor setup in any shrink arm (0/129 x4).
- No-DHW / single-zone plants: `dhw_temperature` (55.0), `upper_floor_temp`, `lower_floor_temp` carry
  defaults in `native_value` but are `available=False` via `sensor:_reading_ok` — the brief's trap
  (correctly unknown) applies; the perturbation proves the gate is what holds it (0 -> 129).

## Limits / unfinished
- The fail-count does not move under plant shrink (it is 0 in every arm); only the fabrication metric is
  shown to move, and only under a production perturbation. The harness does not run a solve per cell,
  so "a plan is published" (M4) is not measured here — that belongs to the M2-M5 seats.
- Wall/CPU not used; load1 on B4 was 24-31 during runs.

## Exposure
None (no docs/ or GitHub read).
