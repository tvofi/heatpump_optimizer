# D12-s2 (round 10) — generalization: installation axes (M2) under the usability bar (M4)

Baseline 17f1c55fad1b. Machine B5 (macOS arm64, shared; load1 56–145 during the runs).
Cells: D12-s2 = steps M2, M4 over `**`. Exposure: none.

## Method

`cells.py` (committed, here) builds a real `HeatPumpOptimizerCoordinator` per
installation cell on `FakeHass`, injects prices/weather/irradiance exactly as
`tests/golden.py:_capture_coordinator` does, runs one full
`_async_update_data` cycle (state read, solve, actuation, accuracy, learners),
then drives every platform's `async_setup_entry` (sensor, binary_sensor,
button, climate, switch, datetime) and reads each entity's `available`,
`native_value`/`is_on`, `extra_state_attributes`, `current_temperature`,
`hvac_mode`.

M4 bar, per cell (fails on the first of): cycle raises; no schedule and no
named refusal status; any setup or entity property raises; a plant-specific
entity (DHW / wood / PV / lower-zone regexes) is `available` with a value
while that plant is absent, or the plan carries `dhw_power` / `pv_surplus`
for an absent plant. Count key: what the production seam delivers (payload
and entity properties), never a config attribute.

Grid (M2): DHW × zones (1/2, with floor-return and lower thermometers) ×
wood (4-way two-tank probes + external heat) × PV × valve (none /
smart_read with buffer + valve-outlet probes) = 32 cells. Optional-entity
sweep (M2 "every optional entity both mapped and omitted"): the richest cell
with 16 further optional slots mapped, then each of the 24 mapped slots
omitted once = 25 runs.

## Results (executed)

| run | command | cells | failing |
|---|---|---|---|
| grid | `cells.py --verbose` | 32 | 0 (cycle 0, entity 0, invented 0) |
| sweep | `cells.py --sweep --verbose` (`sweep.out`) | 25 | 0; present_plant_entities_available=297 |
| detector control | `cells.py --only 'dhw=1,zones=1,wood=1,pv=1'` (`ctl.out`) | 2 | 0; present_plant_entities_available=24 |
| perturbation | `cells.py --only 'dhw=0,zones=0,wood=0,pv=0,valve=0' --perturb has_hot_water` (`perturb.out`) | 1 | **1** (invented 0 → 1) |
| perturbation twin | same, no `--perturb` (`unperturbed.out`) | 1 | 0 |

The detector is live: removing the one DHW gate (`entity.has_hot_water`
forced True) makes the no-DHW cell fail on `sensor.dhw_schedule` and
`sensor.dhw_heating_plan`. A `--perturb reading_ok` arm did NOT move
(0 → 0): the DHW temperature sensor is double-gated (`_reading_ok` and
`DHWEntityMixin.available`), so that arm is recorded as a harness gap, not a
control.

## Findings

None. Every installation cell in the 32-cell grid and every one-slot
omission of the 25-run sweep completes setup, publishes an `optimal` plan,
evaluates every entity without raising, and fabricates no absent plant.

## Non-findings

- All 32 DHW×zone×wood×PV×valve cells usable (M4): 0 failing.
- Omitting any one of 24 optional entity slots from the fully mapped plant
  leaves it usable: 0 failing of 25.
- No-DHW / one-zone / no-wood / no-PV cells publish their plant-specific
  entities unavailable (data dict still carries ThermalState defaults such as
  `dhw_temperature=55.0`, `buffer_tank_temperature=40.0`, but no entity
  publishes them: gated by `_reading_ok`, `DHWEntityMixin`,
  `ConfiguredInputMixin`).

## Not covered / unfinished

- M2: the two non-default stored layouts (`valve_upper_direct_slab`,
  explicit `topology_layout` overrides) and the mixing-valve `manual` /
  `smart_write` modes were not put on the grid; only `none` and
  `smart_read`. The entity count is constant (81) across cells, so entity
  creation never varies by plant — gating is by availability only.
- M4 timing numbers: none taken (all results are counts).
