# D8-s1 REPORT (audit round 11, dimension D8, seat D8-s1, steps M1 and M2)

I found three defects, all on the Monthly Savings and Sensor Gap Advisor sensors. Everything else in my cells held, and both steps are covered in full except three translation cells outside D8's files. Baseline is `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, measured in `~/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline`. Exposure: none.

## Method

**The matrix.** `rig.py` builds 18 cells: golden's five coordinator topologies, each with indoor, outdoor, pump-power and house-power sensors added, plus one overlay per feature toggle the brief lists:
- two-zone with probes, DHW with a probe
- valve storage, two-tank, wood, coil
- ECL110, PV, capacity tariff
- Tuya mode select, away, minimum modulation, slab

**One cycle** is the production `HeatPumpOptimizerCoordinator._async_update_data`. Only the three network fetchers are replaced by no-ops; prices and forecasts are injected the way `_capture_coordinator` does it, and the clock is frozen. Cycle B moves the clock 15 minutes and changes every input (indoor, outdoor, power, prices, forecast).

**Entities** come from the real `async_setup_entry` of sensor, binary_sensor, button, climate and switch: 81 per cell.

**Trap I hit, and a lead:** the solve runs in the process worker (`coordinator._run_in_process`), so an in-memory edit to `optimizer.py` changes nothing. `extras.py` runs that call inline in both arms, and only then did its perturbation move. `dev/audit/README.md` does not list this trap.

## Coverage

- **D8.M1.** Enumerator `python3 tools/audit/enumerate.py d8-cells`: universe 396, examined 393. Not reached: the three `datetime.away_return name` lines (de, en, sv), because `datetime.py` is outside D8's files. Evidence: `cells.py -v`.
- **D8.M2.** Enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/matrix.py --list`: universe 1458 (cell, entity) pairs, examined 1458, not reached none.
- **C1, examined.**
  - **Static values:** `follows.py` substitutes a tracing mapping for the published dict and resolves every sensor whose state stayed the same between the two cycles against the payload leaves its own `native_value` read. There are 298 such pairs here; the 54 last round counted came from a different rig.
    - 203 had sources that did not change.
    - 95 are category or count states whose inputs moved without changing the published category or count.
    - None is stale.
  - **Monthly Savings available but None:** now measured, and it is finding D8-s1-03.

Unfinished: none.

## Findings

**D8-s1-01** (medium, bug, class guess P2, step M2). The Sensor Gap Advisor prices a hot-water tank thermometer as its top gap on installs with no hot water.
- **Number:** in 12 of 22 cell-cycles whose payload says `dhw_enabled` is False, `SensorGapAdvisorSensor` publishes `dhw_temp_entity` as top slot and state. Example: 59.32 per month on `coord_minimal`.
- **Cause:** `sensor._gap_probe_terms` prices `DEFAULT_DHW_TANK_VOLUME`, and `topology.rank_sensor_gaps` has no DHW-enabled check.
- **Perturbation:** with `--fix` (zero the DHW term when DHW is disabled) the count goes 12 to 0. Null control: DHW-enabled cells with no probe stay at 4 of 6 in both arms.
- **Harness:** `gapdhw.py`.

**D8-s1-02** (high, bug, class guess new, step M2). Plan Monthly Savings publishes the open month as one settled 15-minute interval multiplied up.
- **Number:** the first numeric state of February is that interval's saving times 2688; in the install month the factor is 2976.
- **Effect:** within the first hour the state reads -1728.39, -1232.94, -1398.17, then 18.44.
- **Cause:** `ledger.coverage_factor` divides the month's hours by the settled hours with no floor, and the sensor publishes as soon as any row exists.
- **Perturbation:** `--min-hours 24` moves first_scale from 2688 to 0. Null control: `--gate-waiting` (D8-s1-03's fix) leaves it at 2688 and the swing at 1728.39.
- **Harness:** `monthly.py`.

**D8-s1-03** (low, bug, class guess P2, step M2; this is C1). Plan Monthly Savings is available with state unknown at the month rollover.
- **Number:** at 2026-02-01T00:00 it is available and publishes None while the settled January row exists; 1 of 17 cycles.
- **Cause:** `_waiting_for` is satisfied by any row, but `native_value` needs the open month's estimated row with a numeric saving. The second seam, a withheld row (`old_basis` / `below_meter_floor`), I read from code and did not measure.
- **Perturbation:** `--gate-waiting` takes the count from 1 to 0.
- **Harness:** `monthly.py`.

## Non-findings

- **`matrix.py`, all at 0 over 1458 pairs and 2 cycles:** properties raising, non-number under a unit or state class, bad timestamp, enum value outside options, wrong unit, non-JSON values, state over 255 characters, recorded attributes over 16 KB, available-but-None while the named payload key has a value. This harness has a gap: I ran no perturbation for these checks.
- **`stale`=18 in `matrix.py`:** these are ScheduleSensor's "96 steps", a count that legitimately stays put. `follows.py` resolves them.
- **`opstate.py`:** 114 cycles over 19 cells, including 6 cycles with space heating blocked by the Tuya DHW-only select and the minimum-modulation cell. No disagreement between any operating-state entity and the plan's draw (`current_action` power + dhw_power, and heat_pump_on). `--perturb` moves `hvac_action` from 0 to 5.
- **`extras.py`, heat-loss scale above 1.1:** at scale 1.3 under a flat forecast, no step gets a preheat_weather reason (scale 1.0 also 0). `--unscaled-divisor` moves it to 10.
- **`extras.py`, merged slots:** average power on a non-modulating pump with a minimum power matches the plan's own step draws in 15 of 15 slots. `--slot-halve` moves the mismatch count to 15.
- **`cells.py`:**
  - option_gap=0.
  - missing=3: the climate preset_mode attribute name, which Home Assistant core translates.
  - same_as_en=1: the German word "Auto".
  - unreached=29 informational: states no cell published.

## Harnesses

All under `dev/audit/rounds/round11/D8/s1/`: `rig.py` (shared builder), `matrix.py`, `cells.py`, `follows.py`, `opstate.py`, `monthly.py`, `gapdhw.py`, `extras.py`. Findings are in `findings/D8-s1-0{1,2,3}.json` and the report is in `REPORT.json`. The python I had has no `jsonschema`, so I checked REPORT.json against the schema's required fields and length limits by script only.

Every number is a count or ratio from a deterministic run. load1 was 160 to 275 throughout, and thread_factor 1.000 on the re-takes.

## Leads

- **unknown**, `dev/audit/README.md`, traps table: the process-worker trap above is not listed.
- **unknown**, `ledger.py`, `coverage_factor` / `savings_months`: the other readers of the open month (`notifier.py` reads `savings_months`) may get the same unbounded multiplier.
- **unknown**, `topology.py`, `rank_sensor_gaps`: the plan sensors' `_sensor_advisor_attribute` path was not checked for the same DHW gap.

## Housekeeping

- Early on I wrote `/tmp/x_d8cells.txt` by mistake. A safety check blocked my removal, so it is still there for you to delete.
- Working files are under `dev/audit/rounds/round11/D8/s1/scratch/`.
- `matrix.py --dump` wrote `$TMPDIR/d8s1-matrix-2_c95n3b`.