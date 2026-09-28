# Intake normalisation log — round 9, 20 findings

Per finding, per field: the validator error, the before text/value and the after text/value. The full pre-normalisation text for every shortened field is preserved verbatim inside the finding itself (`claim` for `title`, `mechanism` for `metric_definition`, `perturbation.observed_value` for `expected_direction`) -- this log is the audit trail, not the only copy.

## D2-s3-01

- **metric_definition**
  - before: 'Per profile, the count of the 96 quarters (clock frozen 7 minutes into each) where _current_spot_price() differs from the price of the entry whose [start, start+15 min) contains now; keyed on the value the seam returns.'
  - after: 'Per profile, the count of 96 quarters where _current_spot_price() differs from the entry covering now.'
- **perturbation.expected_direction**
  - before: "The quarter-entry arms fall to 0 mismatches and the hourly-entries null control rises from 0 to 273. The span is the mechanism; an honest fix takes each entry's end from the next entry's start, as _known_prices_for does, and must read 0 on all three arms."
  - after: 'to_zero'

## D2-s3-02

- **metric_definition**
  - before: "Per (price profile, export price) cell, the count of the 96 steps where the production cost closure's price of a 3 kW single-step draw differs by more than 1e-9 from export·min(P,s)+import·max(P−s,0)·dt with a clear-sky 6 kWp surplus; keyed on the closure's returned value."
  - after: "Per (price profile, export price) cell, count of 96 steps where the production cost closure's price of a single-step draw differs from the export/import identity."
- **perturbation.expected_direction**
  - before: "Breach steps fall to 0 in every cell, the solve's predicted_cost − identity goes from −0.609 to 0.000, and surplus kWh in negative-price steps goes from 5.07 to 2.27."
  - after: 'to_zero'

## D5-s1-03

- **title**
  - before: 'dashboard-card.md upgrade troubleshooting says the card version lags the integration; the stamp makes them equal on every release'
  - after: 'dashboard-card.md says the card version lags the integration; the stamp keeps them equal every release'

## D5-s1-04

- **title**
  - before: 'configuration.md has 9 lines that a GFM renderer puts in the wrong block: 3 table rows as raw-pipe text, 6 prose lines as table rows'
  - after: 'configuration.md has 9 lines a GFM renderer misplaces: 3 table rows as pipe text, 6 prose lines as rows'

## D7-s1-01

- **title**
  - before: 'Structural ratchet does not price coordinator state reached via module-level _helper(self, ...), rewarding the refused move'
  - after: 'Structural ratchet does not price coordinator state reached via module-level _helper(self, ...)'

## D7-s2-01

- **title**
  - before: 'sysid two-state fit rolls the candidate with one Euler step per 30-min sample: UA 17-25% low on an exact continuous plant, 0/3 presets adopt'
  - after: 'sysid two-state fit rolls the candidate one Euler step per sample: UA 17-25% low, 0/3 presets adopt'

## D7-s2-02

- **title**
  - before: 'Defrost derate fallback folds meter ratios that _cop_fold_blocked refuses to the COP learner (immersion, backup heater, capacity cap)'
  - after: 'Defrost derate fallback folds meter ratios _cop_fold_blocked refuses to the COP learner'

## D7-s3-02

- **title**
  - before: 'structure.py dead_methods reads 0 while 9 members are dead: properties are skipped and bare-name loads count as references'
  - after: 'structure.py dead_methods reads 0 while 9 members are dead: properties skipped, bare-name loads count'

## D8-s2-01

- **title**
  - before: 'Climate entity is permanently unavailable on an install without an indoor thermometer, taking the thermostat control with it'
  - after: 'Climate entity is unavailable with no indoor thermometer, taking the thermostat control with it'
- **perturbation.expected_direction**
  - before: 'climate_unavailable_with_payload 5 -> 0 and climate_attrs_hidden 112 -> 0 (measured)'
  - after: 'to_zero'

## D8-s2-02

- **perturbation.expected_direction**
  - before: 'hvac_action_vs_plan 14 -> 0 (measured)'
  - after: 'to_zero'

## D8-s2-03

- **metric_definition**
  - before: 'Number of immediate state writes made by climate.async_set_hvac_mode or OptimizerEnableSwitch.async_turn_off in which the live-mode field (hvac_mode or is_on) disagrees with a payload-mode field in the same write (hvac_action OFF-ness or the switch attribute mode).'
  - after: 'Count of immediate state writes (climate.async_set_hvac_mode / OptimizerEnableSwitch.async_turn_off) where the live-mode field disagrees with a payload-mode field in the same write.'
- **perturbation.expected_direction**
  - before: 'mode_split_after_action 2 -> 0 (measured)'
  - after: 'to_zero'

## D9-s2-01

- **title**
  - before: 'sensor_advisor ranking re-simulated on the event loop at every plan-sensor state write: 1152 simulate steps, ~32% of loop CPU per cycle'
  - after: 'sensor_advisor ranking re-simulated on the event loop at every plan-sensor write: ~32% of loop CPU'

## D9-s2-02

- **title**
  - before: "No budgeted check can see a 2x of the coordinator's loop-thread work; nightly replay needs ~x5, stress.py reaches none of it"
  - after: "No budgeted check sees a 2x of the coordinator's loop-thread work; stress.py reaches none of it"

## D12-s2-01

- **metric_definition**
  - before: "withheld_frac = planned space+DHW kWh in steps whose production heat_pump_on_schedule is False, divided by the plan's total planned kWh; a cell fails above 0.10; e2e counts switch.turn_off calls from _apply_action on steps with planned power > 0.1 kW"
  - after: "withheld_frac = planned space+DHW kWh in steps whose production heat_pump_on_schedule is False, over the plan's total planned kWh; e2e counts switch.turn_off on planned-heat steps."
- **perturbation.expected_direction**
  - before: 'down: onoff_failing_cells 4 -> 0, e2e turn_off-with-planned-heat 30 -> 0 (both measured)'
  - after: 'down'
- **evidence.cpu_or_wall**
  - before: 'neither (counts and ratios)'
  - after: 'count'
- **evidence.load1**
  - before: '1.38'
  - after: 1.38
- **evidence.thread_factor**
  - before: '1.000'
  - after: 1.0

## D12-s2-02

- **metric_definition**
  - before: "misrouted_mode_writes = mode-slot service calls from pump_arbiter.apply whose service domain differs from the target entity's domain, over 9 ticks 7 min apart on a space/space/DHW/space plan, with HA entity-service routing modelled explicitly (select.select_option acts only on select.*, input_select.select_option only on input_select.*, and there is no sensor.select_option)"
  - after: "misrouted_mode_writes = mode-slot service calls from pump_arbiter.apply whose service domain differs from the target entity's own domain, over 9 ticks on a space/space/DHW/space plan."
- **perturbation.expected_direction**
  - before: 'down: input_select misrouted 5 -> 0, ticks_mode_wrong 9 -> 0, repair 1 -> 0 (measured). The sensor cell keeps 9 wrong ticks, which is the read-only half of the property.'
  - after: 'down'
- **evidence.cpu_or_wall**
  - before: 'neither (counts)'
  - after: 'count'
- **evidence.load1**
  - before: '1.14'
  - after: 1.14
- **evidence.thread_factor**
  - before: '1.000'
  - after: 1.0

## D12-s2-03

- **perturbation.expected_direction**
  - before: 'down: onoff_full_power_mislabelled 149 -> 0 and power_normalized minimum -60 -> -5 (measured)'
  - after: 'down'
- **evidence.cpu_or_wall**
  - before: 'neither (counts)'
  - after: 'count'
- **evidence.load1**
  - before: '1.30'
  - after: 1.3
- **evidence.thread_factor**
  - before: '1.000'
  - after: 1.0

## D12-s3-01

- **metric_definition**
  - before: "Initial-flow completion paths (DFS over menus, forms untouched, quick-setup plant answers 'no') whose entry's first _async_update_data publishes dhw_enabled with a dhw_plan tank trajectory, or two_zone_enabled, with no affirming answer."
  - after: "Initial-flow completion paths whose entry's first _async_update_data publishes dhw_enabled (with a dhw_plan tank trajectory) or two_zone_enabled, with no affirming answer."

## D1-s2-54

- **title**
  - before: 'apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps, the invariant it states is unenforced'
  - after: 'apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps unenforced'

## D1-s5-51

- **title**
  - before: 'A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable while HA holds its valid reading'
  - after: 'A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable'

## D1-s5-52

- **title**
  - before: 'InputReader has no plausibility window: -127 and 85 degC sensor sentinels are delivered as ok on 6 of 6 temperature inputs'
  - after: 'InputReader has no plausibility window: -127 and 85 degC sentinels deliver as ok readings'

