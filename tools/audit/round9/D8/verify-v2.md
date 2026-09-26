# D8, round 9, verifier V2 (independent)

Box G2-V2, a cloud container with 4 CPU shared with the D4, D10 and D12 seats. Python is CPython 3.14.0rc2 at /home/claude/venv; the finders' venv314 and venv-r9 paths are substituted. Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus the round-9 evidence. My harnesses are under `tools/audit/round9/D8/verify-v2/`, and every RESULT line is logged in `RESULTS.txt` there. Every number is a count, so contention does not affect it, and thread_factor was 1.000 on every run.

The V2 lens adds one independent oracle: `v2_entities.py` checks entity states against the **supply-switch service call the production cycle makes** (`heat_pump_switch_entity`, read from FakeHass.services.calls), not against `current_action`. The finders read `current_action`.

## D8-s1-01: vote verify, severity high
- **Finder's harness re-run** (`price15.py`): wrong_quarters=95/96 and worst 0.30. `--hourly` gives 0, `--fix` gives 0, `--cycle` gives 0.0800 (load1 0.47, thread_factor 1.000).
- **My number** (`v2_price_minutes.py`): 1425 of 1440 minutes wrong, mean abs error 0.24757 SEK/kWh. Prices enter through the production `pull_prices`, using Tibber's QUARTER_HOURLY query from a fake session, with profiles winter_typical ±3% within the hour.
  - Metric: minutes where native_value differs from the entry covering [start, next start).
- **Attacks and outcomes:**
  - **Nulls:** hourly rows give 0; the perturbation gives 0.
  - **Flat quarters:** with all four quarters of an hour priced equal, 270/1440 minutes are still wrong. The sensor shows the previous hour's price for 45 min after each hourly change. The effect is a 45–60 min lag, not only a within-hour error.
  - **Reach:** `pull_prices` asks for QUARTER_HOURLY first, so this is the default Tibber path.
  - **Severity:** `_get_current_price` also sets the settlement record's `price` and `spot_price` (coordinator.py:9328-9332). High is not inflated.

## D8-s1-02: vote verify, severity low
- **Finder's harness re-run:**
  - `matrix.py` in full: dhw_periods_vs_slots=92, power_while_off=2 (load1 1.18).
  - `--only +dhw`: 12; with `--perturb-dhw-runs`: 0.
- **My number:** 18 of 18 cycles (3 DHW cells x 6 real cycles; load1 5.62).
  - Metric: the state's integer differs from the number of contiguous runs (>0.1 kW) in the same `dhw_schedule`.
  - Example: "17 heating periods" where there are 5 runs of lengths [1,1,1,2,12].
- **Attacks and outcomes:**
  - A horizon mismatch is ruled out: `dhw_schedule` and `dhw_plan` have the same horizon.
  - The null arm (every run one step long) did not occur, so it has no data.
- **Why low:** hygiene-level label disagreement.

## D8-s1-03: vote verify, severity low
- **Finder's harness re-run** (`minpower.py`): min1_0=4, range 0..4, drop_max_cell=0, worst 0.41 kW (load1 2.34). `--perturb` gives 0.
- **My number:** 1 of 120 real cycles at the default min_power of 1.0 kW (coord_two_zone at 11:05: Recommended Power 0.26 kW, supply switch turn_off; load1 3.30). The min_power 0.2 arm gives 0/120.
- **Attacks and outcomes:**
  - The actuator confirms the pump is switched off while the sensor publishes power.
  - 1.0 kW is `DEFAULT_HEAT_PUMP_MIN_POWER`, so default installs are exposed.
  - Leave-one-out: every hit is in one cell in both harnesses (drop_max_cell=0).
- **Why low:** rare, and the error is bounded below the on-threshold.

## D8-s2-01: vote weaken, from high to medium
- **Finder's harness re-run** (`s2/matrix.py`): climate_unavailable_with_payload=5, climate_attrs_hidden=112 (load1 3.02). `--perturb-available` gives 0 and 0.
- **My number:** the climate is unavailable with a fresh payload in 5/5 cells with no indoor entity, 5/5 with a configured thermometer in state `unavailable`, and 0/5 with a reading thermometer. `--perturb-s201` gives 0/5 in every arm, and current_temperature stays None in 5/5.
- **Attacks and outcomes:**
  - The gate is redundant for the A3(e) aim: current_temperature is already None without it.
  - Reach is wider than claimed: a configured thermometer that goes stale also takes the thermostat away.
  - I did not run real HA, so the entity_service_call skip is cited from the finder, not executed.
- **Why medium:** the owner recorded A3(e) as a deliberate decision (tests/entities.py:3345), and mode and target stay reachable through the Optimizer Active switch, the `set_mode` service and the options flow. That makes it a defect with a workaround.

## D8-s2-02: vote verify, severity high
- **Finder's harness re-run:** hvac_action_vs_plan=14. `--perturb-hvac-action` gives 0.
- **My number:** 7 of 7 arms at mode off, where the supply switch gets turn_on and hvac_action is off. At mode auto: 0/7. `--perturb-s202` gives 0/7 (load1 6.85 and 3.39).
- **Attacks and outcomes:** the actuator oracle confirms the pump is commanded on, and the null arm holds.
- **Why high:** the published operating state is wrong while the boost runs at maximum power.

## D8-s2-03: vote refute
- **Finder's harness re-run:** mode_split_after_action=2. `--perturb-live-mode` gives 0.
- **My number:** hvac_action disagrees with the actuator in 0 of 4 immediate writes. The finder's internal split reproduces (4/4), but at the write the supply switch is still on, because it was last commanded turn_on and the refresh has not yet actuated. hvac_action=heating is therefore true, and the payload `mode` names the actuation that is running.
- **The finder's proposed fix** (`--perturb-s203`, read `coordinator.mode`): split 0/4, but vs-actuator becomes 4/4. The fix would publish OFF while the pump runs, which is the D8-s2-02 defect class.
- **Window:** the refresh into mode off calls `async_run_optimization` 0 times. The "30 to 70 s on a Pi" window is solve time and does not apply to the two actions measured.
- **Why refute:** the metric counts disagreement between two sources, not a wrong value. Load1 6.26 and 3.36.

## D8-s3-01: vote weaken, severity low, scope narrowed to the energy meters
- **Finder's harness re-run** (`m3_families.py`): unexplained name_en=2, name_sv=2, entity_id=1. `--perturb` gives 1/1/1 (load1 3.71).
- **My number:**
  - Whole-roster sort: accuracy 2 runs (en and sv); meters 4 (en) and 5 (sv).
  - HA device-page sections, enabled-by-default entities only: meters 3 runs (en) and 4 runs (sv), all in the Sensors section. Accuracy 2 runs, across 2 sections.
- **Why the accuracy half fails:** DiagnoseIntervalButton is listed under Controls (a button with category None), and PredictionAccuracySensor is Diagnostic. With `--perturb-s301`, the whole-roster runs go from 2 to 1 but the section runs stay at 2. The rename the finder proposes changes nothing on the device page.
- **What stands:** the meter family is split. Load1 4.08 and 3.84.

## D8-s3-02: vote verify, severity low
- **Finder's harness re-run** (`m3_translation.py`): concept_mismatch=1, other tokens 0, key-set differences 0. `--perturb` gives 0.
- **My number:** 1 of 74. The rule is a sv name containing "valuta" with no currency or cost token in the en name, plus en "…Advisor" without "råd" in sv. Both rules hit only sensor_gap_advisor ('Sensor-Gap Advisor' / 'Sensorlucka i valutan').
- **Why low:** hygiene, one string.

## D8-s3-03: vote verify, severity low
- **Finder's harness re-run** (`m4_duplicates.py`): duplicate_enabled_pairs=1. `--perturb` gives 0, with any_default still 1.
- **My number:** 1 pair, indoor_temperature_optimizer == upper_floor_temperature. Both carry `_reading_key` "upper_floor_temperature", and they are equal in 4/4 configs, including two-zone with a real lower-floor probe. `--perturb-s303` gives 0.
- **Attacks and outcomes:**
  - `READING_SOURCES` maps upper_floor_temperature to `CONF_INDOOR_TEMP_ENTITY`, and there is no upper-floor configuration key.
  - The class docstring records a decision to keep the entity. A new-install default-off does not orphan existing registry entries, so that decision does not refute the finding.
- **Why low:** hygiene.
