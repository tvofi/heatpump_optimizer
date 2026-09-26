# D8 verify-v1 (round 9, lens V1 reproduce)

Tree: /home/claude/wt/D8, evidence tree 6f51db2c over baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Box: G2-V1 cloud container, 4 CPU, shared with up to two other verifier seats. All numbers below are counts (contention-immune). Every run had thread_factor 1.000 and swapins 0; load1 is quoted per run. No production file was edited. All perturbations ran in memory.

Votes: 8 verify, 1 weaken (D8-s2-01 high -> medium), 0 refute, 0 unresolved.

## D8-s1-01 — Current Electricity Price uses an earlier quarter's price (high) — verify
- Re-run `s1/price15.py`: wrong_quarters=95 of 96, worst 0.3000 (finder: 95, 0.30). `--cycle`: 0.0800 (finder: 0.08). load1 0.56.
- Perturbation `--fix`: 95 -> 0. Null control `--hourly`: 0.
- Own measure (`verify-v1/own.py`), per minute over 1440 minutes, reading `_current_spot_price()`: 1425 wrong (only 00:00-00:14 is right). Null arms: an hourly list gives 0 and a flat 15-min list gives 0. `--fix-price` gives 0.
- Leave-one-out: not applicable (one day, one topology).
- Reachability: `price_model.py:577` queries `priceInfo(resolution: QUARTER_HOURLY)`, so 15-min lists reach the coordinator in real HA.
- The 0.30 magnitude is set by the harness's synthetic intra-hour ramp. Settlement also reads `_get_current_price` (finder's statement, not measured here), which could raise the consequence to wrong money. That is left for V3 and the judge.
- Metric: of 1440 minutes, minutes where `_current_spot_price()` differs from the entry covering [start, next start).

## D8-s1-02 — DHW Heating Schedule counts steps as periods (low) — verify
- Re-ran the full `s1/matrix.py` (90 cells x 2 cycles, 30m47s wall, load1 1.35 at end): dhw_periods_vs_slots=92, power_while_off=2, every other class 0 except available_unknown=156. All match the finder.
- Perturbation `--only +dhw --perturb-dhw-runs`: 12 -> 0. The same subset without the perturbation gives 12.
- Leave-one-out: 46 cells at 2 each (min = max = 2). Dropping one cell gives 90.
- Own measure: synthetic schedules with 2 runs of k steps. The sensor and `_plan_slots` agree at k=1 (2 = 2). They disagree at k=2, 3, 4 (sensor 4/6/8 vs slots 2), so 3 of 4 schedules mismatch.
- Horizon attack: the perturbation reads the same `dhw_schedule` and reaches 0, so the gap is not a horizon difference.
- Metric: count of schedules where DHWScheduleSensor's leading integer differs from `len(_plan_slots)`.

## D8-s1-03 — Recommended Power published while Heat Pump Action is off (low) — verify
- Re-run `s1/minpower.py`: 4 at min_power 1.0 and 0 at 0.2, 0.6 and 1.5. Worst 0.41 kW. load1 3.62. All match.
- Perturbation `--perturb`: 4 -> 0. Null control (the 0.2 arm): 0.
- Leave-one-out: per-cell range 0..4, and dropping the largest cell gives 0. The whole aggregate rests on one of five cells (coord_all_features) and one of four min_power arms. The full matrix adds 2 of 180 real cycles, both also on coord_all_features (+valve, +grid_fee).
- Own measure: 10 space powers from 0.05 to 0.50 kW at min_power 1.0, through `get_current_action` and `_build_data_dict`: 9 of 10 publish power while the action is 'off'. `--gate-power` gives 0. So the mechanism does not depend on any one cell.
- Extra observation: at power exactly equal to the on-threshold (0.5), `heat_pump_on` uses `>` while `space_on` uses `>=`. The step reads 'off' and publishes 0.5 kW.
- Severity low stands. Whether the plan's cost books the sub-threshold kW belongs to D0/D2 and was not measured.
- Metric: count of powers where Recommended Power > 0.05 kW and Heat Pump Action == 'off'.

## D8-s2-01 — Climate unavailable without an indoor thermometer (high) — weaken to medium
- Re-run `s2/matrix.py`: climate_unavailable_with_payload=5 of 10, climate_attrs_hidden=112. load1 4.95. Matches the finder.
- Perturbation `--perturb-available`: both go to 0.
- Null control: the 5 thermometer cells read 0.
- Own measure: after a real `_update_current_state` and `_build_data_dict`, available is 0 without an indoor entity and 1 with one.
- Leave-one-out: each cell is a yes/no result. Dropping one cell gives 4.
- Reachability: `config_flow.py:1264` makes the indoor entity `vol.Optional`, so this install can be set up in real HA.
- Why weaken: the lost control has workarounds, and COMMON defines "a defect with a workaround" as medium.
  - Mode: the Optimizer Active switch and the `set_mode` service.
  - Setpoint: the options-flow `target_temperature` field (`config_flow.py:1566`).
- The unavailable gate is the recorded A3(e) decision, pinned at `tests/entities.py:3344-3383`, so the fix needs tvofi's decision.
- Metric: `climate.available` after one input read, with vs without an indoor entity.

## D8-s2-02 — hvac_action says off while a boost runs the pump (high) — verify
- Re-run: hvac_action_vs_plan=14. The per-step oracle hvac_action_steps_vs_plan=0 of 96. Matches the finder.
- Perturbation `--perturb-hvac-action`: 14 -> 0. Null control: the mode-auto arms give 0.
- Own measure: `boost.overlay` per channel with live and payload mode set to off gives 2 of 2 arms with hvac_action=off while heat_pump_on is True. At mode auto: 0 of 2.
- Method attack on the value: 7 of the 14 arms are no-thermometer cells where the climate is unavailable (D8-s2-01). Real HA publishes 'unavailable' there, not hvac_action=off. The published count is 7. The phenomenon is unaffected.
- Reachability: the coordinator runs `boost.apply` then `_apply_action` in every mode including off (`coordinator.py:4650-4651`), and the overlay sets `heat_pump_on=True` (`boost.py:110-125`).
- Metric: arms where the action has heat_pump_on True and `climate.hvac_action` is OFF or IDLE.

## D8-s2-03 — A mode action's state write mixes live and payload mode (medium) — verify
- Re-run: mode_split_after_action=2. Perturbation `--perturb-live-mode`: 2 -> 0.
- Own measure, with live mode off and payload mode auto:
  - climate: hvac_mode off, hvac_action heating
  - switch: is_on False, attribute mode auto
  - That gives 2 splits in 2 writes.
- Own null: before the live mode moves, both entities agree.
- The "30-70 s" window is the text of the `entity.py:147` docstring and was not measured, by the finder or by me. The state is transient and heals after the refresh, so medium is right.
- Metric: the 2 entity writes (climate, switch), counted when the live-mode field disagrees with the payload-mode field.

## D8-s3-01 — Accuracy and energy-meter families split in name sort (low, hygiene) — verify
- Re-run `m3_families.py`: unexplained splits name_en=2, name_sv=2, entity_id=1. `--perturb` gives 1 and 1. load1 3.17. Matches.
- Null control: ecl110, tariff, learning and card_headline are one run each in every ordering.
- Leave-one-out: 8 families. Dropping either split family gives 1, so no single family carries the count.
- Own measure: in the casefolded sort of the 74 names read from `translations/*.json`, the diagnose button sits 35 places (en) and 40 places (sv) from Prediction Accuracy.
- Reachability: DiagnoseIntervalButton has `entity_category None`, so the HA device page shows it under Controls and the sensor under Sensors. The split shows in the name-sorted Settings > Entities table.
- Metric: how many places apart the diagnose button and Prediction Accuracy sit in that name sort.

## D8-s3-02 — Swedish Sensor-Gap Advisor name (low, hygiene) — verify
- Re-run: concept_mismatch=1, key_set_differences=0, names_checked=74. `--perturb`: 1 -> 0.
- Null control: other tokens give 0 mismatches.
- Own measure: `translations/sv.json:1873` reads "Sensorlucka i valutan" and `en.json:1873` reads "Sensor-Gap Advisor".
- Metric: direct read of the two name strings.

## D8-s3-03 — Upper Floor Temperature duplicates Indoor Temperature and is enabled by default (low, hygiene) — verify
- Re-run: duplicate_enabled_pairs=1 over 5 topologies. `--perturb`: 1 -> 0.
- Null control: duplicate_pairs_any_default stays 1 under `--perturb`. Matches the finder.
- Own measure: both classes are enabled by default and share `_reading_key` "upper_floor_temperature".
- Leave-one-out: 1 in each of 5 topologies.
- The docstring at `sensor.py:920-942` records the decision to keep the entity. That decision is about removing it, not about its enabled default, and the proposed fix orphans nothing.
- Metric: the two classes' enabled-by-default flag and reading-key equality.

## Harnesses written
- `tools/audit/round9/D8/verify-v1/own.py`
  - Command: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v1/own.py`, with optional `--fix-price` and `--gate-power`.
  - No solve; each re-measure drives the production property named in its header.

## Not finished
- None. The full s1 matrix was re-run once, with no second quiet-window run; its counts are contention-immune.
