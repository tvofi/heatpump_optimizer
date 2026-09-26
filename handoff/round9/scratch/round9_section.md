## Round 9 — intake, baseline `1936d5ca`, 2026-09-26

Intake for round 9, batch 1, done by hand from `.claude/workflows/audit-find.js`'s intake step. Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. This section is the **intake register**: findings as reported by their finder and lead seats, validated against `tools/audit/finding.schema.json` and registered one row per finding. It does **not** merge, cluster, dedupe or verify — that is the judge's first step, which follows. `status` is `reported` for every row here; nothing has been judged yet.

Inputs: 122 finder findings from 40 seats (`accepted.json`), 25 findings the leads seats converted (`lead_findings.json`, `from_lead: true`), and D3-s2's catch-up batch of 2 findings from `origin/handoff/audit-r9-find-B2:tools/audit/round9/reports-B2.json` (box B2). `rejected.json` and `lead_rejected.json` were both empty at hand-off; the rejections below are this intake's own schema check.

### Dimension status — round 9 intake

| # | Dimension | Seats reported | Findings accepted | Rejected at intake |
|---|-----------|-----------------|--------------------|----------------------|
| 0 | Price optimality | 3 | 3 | 0 |
| 1 | Robustness and stability | 5 | 29 | 3 |
| 2 | Mathematical and physical sanity | 4 | 10 | 2 |
| 3 | Test-suite gaps | 2 (D3-s2 catch-up); D3-s3 deferred (catch-up) | 3 | 0 |
| 4 | UI/UX | 2 | 15 | 0 |
| 5 | Docs structure, flow and content; code comments | 2 | 8 | 2 |
| 6 | README and documentation claim verification | 2 | 10 | 0 |
| 7 | Architecture and maintainability | 3 | 5 | 4 |
| 8 | Sensor verification and ordering | 3 | 7 | 3 |
| 9 | CPU and memory efficiency, Raspberry-Pi-class target | 2 | 7 | 2 |
| 10 | Home Assistant integration quality scale | 2 | 4 | 0 |
| 11 | Governance mechanisms and policy | 2 | 10 | 0 |
| 12 | Generalization | 3 | 3 | 4 |
| 13 | Process yield and cost | 1 | 3 | 0 |
| 14 | Recurring bug classes | 5 | 12 | 0 |
| | **Total** | **41** | **129** | **20** |

Seats reported counts distinct finder seats in `reports.json` plus D3-s2 (reported on `origin/handoff/audit-r9-find-B2`, not in `reports.json`). D3-s3 has not reported and is listed separately; it is not counted in D3's seats-reported figure. Findings accepted and rejected at intake include both finder findings and the leads seats' converted findings, keyed by each finding's `scope`.

### Rejected at intake

20 findings failed validation against `tools/audit/finding.schema.json` (`#/definitions/finding`) and are rejected at intake, with the validator's message:

| id | seat | source | validator message |
|---|---|---|---|
| D2-s3-01 | D2-s3 | accepted | metric_definition: 'Per profile, the count of the 96 quarters (clock frozen 7 minutes into each) where _current_spot_price() differs from the price of the entry whose [start, start+15 min) contains now; keyed on the value the seam returns.' is too long; perturbation/expected_direction: "The quarter-entry arms fall to 0 mismatches and the hourly-entries null control rises from 0 to 273. The span is the mechanism; an honest fix takes each entry's end from the next entry's start, as _known_prices_for does, and must read 0 on all three arms." is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D2-s3-02 | D2-s3 | accepted | metric_definition: "Per (price profile, export price) cell, the count of the 96 steps where the production cost closure's price of a 3 kW single-step draw differs by more than 1e-9 from export·min(P,s)+import·max(P−s,0)·dt with a clear-sky 6 kWp surplus; keyed on the closure's returned value." is too long; perturbation/expected_direction: "Breach steps fall to 0 in every cell, the solve's predicted_cost − identity goes from −0.609 to 0.000, and surplus kWh in negative-price steps goes from 5.07 to 2.27." is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D5-s1-03 | D5-s1 | accepted | title: 'dashboard-card.md upgrade troubleshooting says the card version lags the integration; the stamp makes them equal on every release' is too long |
| D5-s1-04 | D5-s1 | accepted | title: 'configuration.md has 9 lines that a GFM renderer puts in the wrong block: 3 table rows as raw-pipe text, 6 prose lines as table rows' is too long |
| D7-s1-01 | D7-s1 | accepted | title: 'Structural ratchet does not price coordinator state reached via module-level _helper(self, ...), rewarding the refused move' is too long |
| D7-s2-01 | D7-s2 | accepted | title: 'sysid two-state fit rolls the candidate with one Euler step per 30-min sample: UA 17-25% low on an exact continuous plant, 0/3 presets adopt' is too long |
| D7-s2-02 | D7-s2 | accepted | title: 'Defrost derate fallback folds meter ratios that _cop_fold_blocked refuses to the COP learner (immersion, backup heater, capacity cap)' is too long |
| D7-s3-02 | D7-s3 | accepted | title: 'structure.py dead_methods reads 0 while 9 members are dead: properties are skipped and bare-name loads count as references' is too long |
| D8-s2-01 | D8-s2 | accepted | perturbation/expected_direction: 'climate_unavailable_with_payload 5 -> 0 and climate_attrs_hidden 112 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip']; title: 'Climate entity is permanently unavailable on an install without an indoor thermometer, taking the thermostat control with it' is too long |
| D8-s2-02 | D8-s2 | accepted | perturbation/expected_direction: 'hvac_action_vs_plan 14 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D8-s2-03 | D8-s2 | accepted | metric_definition: 'Number of immediate state writes made by climate.async_set_hvac_mode or OptimizerEnableSwitch.async_turn_off in which the live-mode field (hvac_mode or is_on) disagrees with a payload-mode field in the same write (hvac_action OFF-ness or the switch attribute mode).' is too long; perturbation/expected_direction: 'mode_split_after_action 2 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D9-s2-01 | D9-s2 | accepted | title: 'sensor_advisor ranking re-simulated on the event loop at every plan-sensor state write: 1152 simulate steps, ~32% of loop CPU per cycle' is too long |
| D9-s2-02 | D9-s2 | accepted | title: "No budgeted check can see a 2x of the coordinator's loop-thread work; nightly replay needs ~x5, stress.py reaches none of it" is too long |
| D12-s2-01 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts and ratios)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.38' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; metric_definition: "withheld_frac = planned space+DHW kWh in steps whose production heat_pump_on_schedule is False, divided by the plan's total planned kWh; a cell fails above 0.10; e2e counts switch.turn_off calls from _apply_action on steps with planned power > 0.1 kW" is too long; perturbation/expected_direction: 'down: onoff_failing_cells 4 -> 0, e2e turn_off-with-planned-heat 30 -> 0 (both measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s2-02 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.14' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; metric_definition: "misrouted_mode_writes = mode-slot service calls from pump_arbiter.apply whose service domain differs from the target entity's domain, over 9 ticks 7 min apart on a space/space/DHW/space plan, with HA entity-service routing modelled explicitly (select.select_option acts only on select.*, input_select.select_option only on input_select.*, and there is no sensor.select_option)" is too long; perturbation/expected_direction: 'down: input_select misrouted 5 -> 0, ticks_mode_wrong 9 -> 0, repair 1 -> 0 (measured). The sensor cell keeps 9 wrong ticks, which is the read-only half of the property.' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s2-03 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.30' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; perturbation/expected_direction: 'down: onoff_full_power_mislabelled 149 -> 0 and power_normalized minimum -60 -> -5 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s3-01 | D12-s3 | accepted | metric_definition: "Initial-flow completion paths (DFS over menus, forms untouched, quick-setup plant answers 'no') whose entry's first _async_update_data publishes dhw_enabled with a dhw_plan tank trajectory, or two_zone_enabled, with no affirming answer." is too long |
| D1-s2-54 | D1-s2 | lead_findings | title: 'apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps, the invariant it states is unenforced' is too long |
| D1-s5-51 | D1-s5 | lead_findings | title: 'A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable while HA holds its valid reading' is too long |
| D1-s5-52 | D1-s5 | lead_findings | title: 'InputReader has no plausibility window: -127 and 85 degC sensor sentinels are delivered as ok on 6 of 6 temperature inputs' is too long |

### Findings register — round 9 (intake, unjudged)

One table per dimension. Columns: id, scope, step, severity, class_guess, title, status, provisional. `status` is `reported` for every row: this is the intake register, before clustering, dedup or judge verification. No finding is provisional under the driver's rule, except D9-s1-71 and D9-s2-71 (both lead findings), marked provisional because their CPU ratios were taken on a shared box.

#### D0 — Price optimality

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D0-s1-01 | D0-s1 | D0.M2 | low | P4 | The two-zone 0.20x deep anchor is built only in _optimize_space_only; the DHW path's _solve_space never gets it | reported |  |
| D0-s2-01 | D0-s2 | D0.M2 | low | P4 | L-BFGS-B ftol=1e-6 stops the solve and its in-loop restart short of their own fixed point | reported |  |
| D0-s2-02 | D0-s2 | D0.M2 | low | P4 | Multi-start seed set misses lower basins on shoulder prices, above the flat-price null | reported |  |

#### D1 — Robustness and stability

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D1-s1-01 | D1-s1 | D1.M2 | medium | P1 | A tz-naive persisted timestamp raises on every cycle at three sibling loader seams (snapshots, curve, comfort) | reported |  |
| D1-s1-02 | D1-s1 | D1.M2 | medium | P1 | A non-numeric snapshot temperature_bias makes best_restore raise and suppresses the accuracy_drift issue for good | reported |  |
| D1-s1-03 | D1-s1 | D1.M6 | medium | new | One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90 | reported |  |
| D1-s1-04 | D1-s1 | D1.M3 | low | new | A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error | reported |  |
| D1-s1-51 | D1-s1 | D1.M2 | low | P11 | hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file *[from lead (L1)]* | reported |  |
| D1-s1-52 | D1-s1 | D1.M3 | low | P11 | hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted *[from lead (L1)]* | reported |  |
| D1-s2-01 | D1-s2 | D1.M6 | high | new | A malformed weather-forecast response wedges every later cycle until restart | reported |  |
| D1-s2-02 | D1-s2 | D1.M6 | medium | new | Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve | reported |  |
| D1-s2-03 | D1-s2 | D1.M2 | medium | P1 | A sample count past 2**64 in the thermal-learning store fails every cycle, across restarts | reported |  |
| D1-s2-04 | D1-s2 | D1.M5 | medium | new | Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation | reported |  |
| D1-s2-05 | D1-s2 | D1.M1 | medium | new | Home Assistant stop waits out an in-flight solve before reaping the solve worker | reported |  |
| D1-s2-51 | D1-s2 | D1.M5 | medium | new | A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves *[from lead (L1)]* | reported |  |
| D1-s2-52 | D1-s2 | D1.M1 | medium | new | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state *[from lead (L1)]* | reported |  |
| D1-s2-53 | D1-s2 | D1.M1 | medium | new | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) *[from lead (L1)]* | reported |  |
| D1-s2-55 | D1-s2 | D1.M5 | medium | new | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice *[from lead (L1)]* | reported |  |
| D1-s2-71 | D1-s2 | D1.M1 | low | P11 | hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells *[from lead (L3)]* | reported |  |
| D1-s3-01 | D1-s3 | D1.M6 | high | P2 | A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError | reported |  |
| D1-s3-02 | D1-s3 | D1.M1 | high | new | Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump | reported |  |
| D1-s3-03 | D1-s3 | D1.M2 | medium | P1 | pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply | reported |  |
| D1-s3-04 | D1-s3 | D1.M4 | medium | new | Climate entity publishes the away setback as the user's target while the solve is in the executor | reported |  |
| D1-s3-05 | D1-s3 | D1.M3 | medium | new | Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound | reported |  |
| D1-s3-06 | D1-s3 | D1.M2 | medium | P1 | FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days | reported |  |
| D1-s4-01 | D1-s4 | D1.M2 | medium | P1 | DefrostDerate.from_dict admits non-finite/out-of-range duty; the bucket pins at DERATE_MIN and never recovers | reported |  |
| D1-s4-02 | D1-s4 | D1.M5 | medium | P2 | A failed solve is returned as a plan with status 'failed (...)', so the coordinator counts it a success | reported |  |
| D1-s4-03 | D1-s4 | D1.M2 | low | P1 | One unreadable cell in a v2 defrost store voids all 12 measured buckets and is labelled a pre-v5.3.0 upgrade | reported |  |
| D1-s5-01 | D1-s5 | D1.M3 | medium | P2 | inputs.age_of ignores last_reported and accepts future stamps, diverging from InputReader's freshness rule | reported |  |
| D1-s5-02 | D1-s5 | D1.M2 | medium | P1 | Learner-store loaders check finiteness but not the domain their own update path enforces (price shape, peak tracker) | reported |  |
| D1-s5-03 | D1-s5 | D1.M6 | low | P2 | One huge JSON integer drops a whole price fetch (entity and Tibber) or Open-Meteo refresh instead of one row | reported |  |
| D1-s5-04 | D1-s5 | D1.M6 | low | new | One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon | reported |  |

#### D2 — Mathematical and physical sanity

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D2-s1-01 | D2-s1 | D2.M1 | medium | new | Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge | reported |  |
| D2-s1-02 | D2-s1 | D2.M1 | low | new | DHW refill coil debits the wood tank the full coil heat but spares the DHW tank only its scaled share | reported |  |
| D2-s1-51 | D2-s1 | D2.M2 | low | P6 | DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped *[from lead (L1)]* | reported |  |
| D2-s2-01 | D2-s2 | D2.M3 | high | P2 | Settlement caps (slab_settlement_cap, hold_demand_kw) ignore the learned house_heat_loss_scale the dynamics apply | reported |  |
| D2-s2-02 | D2-s2 | D2.M2 | medium | new | #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37% | reported |  |
| D2-s2-03 | D2-s2 | D2.M3 | low | P2 | DHW-path savings settle-up replays space schedule without the DHW coil: end state differs from published trajectory | reported |  |
| D2-s2-81 | D2-s2 | D2.M3 | medium | P3 | Two-zone comfort penalty halves each zone's floor price; shipped plans sit up to 0.46 K below min_temp *[from lead (L4)]* | reported |  |
| D2-s4-01 | D2-s4 | D2.M5 | medium | P5 | sysid adoption interval misses the true UA on 14 of 22 fits it admits; admitted fits biased high | reported |  |
| D2-s4-02 | D2-s4 | D2.M5 | medium | new | sysid step sized to exactly the abort bound: sensor noise aborts 100 of 294 experiments, light_new 81 of 96 | reported |  |
| D2-s4-81 | D2-s4 | D2.M5 | medium | P5 | sysid cannot adopt its own exact noise-free fit on 43 of 80 preset houses, yet arms on all 80 *[from lead (L4)]* | reported |  |

#### D3 — Test-suite gaps

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D3-s1-01 | D3-s1 | D3.M2 | low | I1 | No closure script fails when _dhw_inlet_c's lower plausibility bound moves (-5.0 <= value -> -5.0 < value) | reported |  |
| D3-s2-01 | D3-s2 | D3.M2 | medium | I1 | Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices *[catch-up batch]* | reported |  |
| D3-s2-02 | D3-s2 | D3.M2 | low | I1 | PriceShapeModel residual_var restore can discard every stored variance with the gate green *[catch-up batch]* | reported |  |

#### D4 — UI/UX

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D4-s1-01 | D4-s1 | D4.M3 | medium | P9 | Status text coloured by HA's --success/--error/--warning-color fails WCAG AA on the default themes | reported |  |
| D4-s1-02 | D4-s1 | D4.M1 | medium | P2 | Lane slot menu is placed at the tap point unclamped; near the right edge it spills past its chart and the viewport | reported |  |
| D4-s1-03 | D4-s1 | D4.M1 | medium | new | Setup picker: two identically named sensors render as identical options at 375 and 768 px | reported |  |
| D4-s1-04 | D4-s1 | D4.M1 | medium | new | Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route | reported |  |
| D4-s1-05 | D4-s1 | D4.M1 | high | P2 | Now-marker label prints over the measured-now reading on the live default view | reported |  |
| D4-s2-01 | D4-s2 | D4.M2 | medium | P6 | Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error | reported |  |
| D4-s2-02 | D4-s2 | D4.M2 | medium | P8 | Wood price field shows 'SEK/m³' to a non-SEK install while its sibling money fields follow the instance currency | reported |  |
| D4-s2-03 | D4-s2 | D4.M3 | medium | new | The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv) | reported |  |
| D4-s2-04 | D4-s2 | D4.M2 | high | P2 | Expert setup: the zones page says 'leave defaults if you don't need two-zone' and leaving them turns two-zone on | reported |  |
| D4-s2-05 | D4-s2 | D4.M1 | low | new | 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5 | reported |  |
| D4-s2-06 | D4-s2 | D4.M2 | low | P2 | The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields | reported |  |
| D4-s2-07 | D4-s2 | D4.M2 | low | new | After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again | reported |  |
| D4-s2-08 | D4-s2 | D4.M3 | low | new | None of the 12 registered services has an icon in icons.json | reported |  |
| D4-s2-09 | D4-s2 | D4.M3 | low | new | 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m² | reported |  |
| D4-s2-81 | D4-s2 | D4.M2 | medium | new | Setup overview page and setup diagram publish English slot text on a Swedish install *[from lead (L4)]* | reported |  |

#### D5 — Docs structure, flow and content; code comments

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D5-s1-01 | D5-s1 | D5.M1 | medium | I5 | configuration.md 'Initial setup' documents the pre-v6.6.5 flow: no finish menu, Tibber token required, 74 entities | reported |  |
| D5-s1-02 | D5-s1 | D5.M3 | medium | I5 | setup.md Quick setup promises buffer storage and two-tank physics that the quick-setup answers cannot produce | reported |  |
| D5-s1-05 | D5-s1 | D5.M1 | low | I5 | Docs name 5 option fields by labels the options forms do not show | reported |  |
| D5-s1-06 | D5-s1 | D5.M1 | low | I5 | simulate_plan accepts 5 wood fields that no doc names; configuration.md's table says 16 fields and its prose lists 11 | reported |  |
| D5-s2-01 | D5-s2 | D5.M4 | low | I5 | Card comments cite 12 private members the card no longer has (17 mentions) | reported |  |
| D5-s2-02 | D5-s2 | D5.M4 | low | I5 | Three comments cite a number the code beside them does not deliver | reported |  |
| D5-s2-03 | D5-s2 | D5.M4 | low | I5 | DHW_COLD_WATER_TEMP comment claims the draw model heats from it; the draw reads the configured inlet | reported |  |
| D5-s2-51 | D5-s2 | D5.M4 | low | I5 | Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash) *[from lead (L1)]* | reported |  |

#### D6 — README and documentation claim verification

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D6-s1-01 | D6-s1 | D6.M2 | low | I5 | README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes | reported |  |
| D6-s1-02 | D6-s1 | D6.M2 | low | I5 | README puts the two-zone split and the orientation factor on the wrong options pages | reported |  |
| D6-s1-03 | D6-s1 | D6.M2 | low | I5 | README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables | reported |  |
| D6-s1-04 | D6-s1 | D6.M2 | low | I5 | README says apply_manual_plan pins 'up to 20 hours'; an explicit expires_at pins the whole horizon | reported |  |
| D6-s1-81 | D6-s1 | D6.M1 | low | P11 | README's SEK currency fallback is unreachable under Home Assistant core, which defaults Config.currency to EUR *[from lead (L4)]* | reported |  |
| D6-s2-01 | D6-s2 | D6.M2 | low | I5 | configuration.md says 'All 74 entities'; the six platforms create 75 | reported |  |
| D6-s2-02 | D6-s2 | D6.M2 | low | I5 | configuration.md: the weather page does not create the entry; the setup flowchart omits the menu and overview | reported |  |
| D6-s2-03 | D6-s2 | D6.M2 | low | I5 | Curve-bias 'at most 0.5 K per week' is false: 0.6 K in a 7-day window | reported |  |
| D6-s2-04 | D6-s2 | D6.M2 | low | I5 | how-it-works.md: space solve 'from two starting points'; it runs four, each refined and polished | reported |  |
| D6-s2-05 | D6-s2 | D6.M2 | low | I5 | configuration.md simulate_plan field list omits the five wood fields | reported |  |

#### D7 — Architecture and maintainability

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D7-s1-02 | D7-s1 | D7.M5 | medium | I1 | Drift-gate comparison and stress per-scenario budget verdict are deletable with every runnable check green | reported |  |
| D7-s1-71 | D7-s1 | D7.M1 | low | new | Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves *[from lead (L3)]* | reported |  |
| D7-s3-01 | D7-s3 | D7.M6 | low | new | 10 class members are reached by no production code; 9 are kept only by tests that pin them | reported |  |
| D7-s3-51 | D7-s3 | D7.M6 | low | new | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed *[from lead (L1)]* | reported |  |
| D7-s3-72 | D7-s3 | D7.M6 | low | new | 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer *[from lead (L3)]* | reported |  |

#### D8 — Sensor verification and ordering

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D8-s1-01 | D8-s1 | D8.M2 | high | P2 | Current Electricity Price publishes an earlier quarter's price when prices are quarter-hourly | reported |  |
| D8-s1-02 | D8-s1 | D8.M2 | low | P2 | DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count | reported |  |
| D8-s1-03 | D8-s1 | D8.M2 | low | P2 | Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off' | reported |  |
| D8-s3-01 | D8-s3 | D8.M3 | low | new | Accuracy and Energy-dashboard meter families split in both English and Swedish name sort | reported |  |
| D8-s3-02 | D8-s3 | D8.M3 | low | I5 | Swedish name of Sensor-Gap Advisor reads 'sensor gap in the currency' and drops the advisor role | reported |  |
| D8-s3-03 | D8-s3 | D8.M4 | low | new | Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install | reported |  |
| D8-s3-61 | D8-s3 | D8.M4 | low | P2 | Valve Target Recommendation ships disabled where a mixing valve is set, and available-but-unknown where none is *[from lead (L2)]* | reported |  |

#### D9 — CPU and memory efficiency, Raspberry-Pi-class target

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D9-s1-01 | D9-s1 | D9.M1 | medium | new | Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here | reported |  |
| D9-s1-02 | D9-s1 | D9.M1 | medium | new | L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve | reported |  |
| D9-s1-03 | D9-s1 | D9.M1 | low | P10 | The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve) | reported |  |
| D9-s1-04 | D9-s1 | D9.M1 | low | new | DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve | reported |  |
| D9-s1-71 | D9-s1 | D9.M1 | low | new | Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU *[from lead (L3)]* | reported | yes |
| D9-s2-03 | D9-s2 | D9.M2 | medium | new | stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams | reported |  |
| D9-s2-71 | D9-s2 | D9.M2 | medium | I1 | stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees *[from lead (L3)]* | reported | yes |

#### D10 — Home Assistant integration quality scale

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D10-s1-01 | D10-s1 | D10.M1 | medium | P2 | Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice | reported |  |
| D10-s1-02 | D10-s1 | D10.M1 | medium | P2 | Optimize-now button press returns normally when the solve did not run; the run_optimization action raises | reported |  |
| D10-s1-03 | D10-s1 | D10.M1 | low | P11 | Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed | reported |  |
| D10-s2-01 | D10-s2 | D10.M1 | medium | I5 | Climate presets auto and economy are non-standard and have no translation or icon in any language | reported |  |

#### D11 — Governance mechanisms and policy

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D11-s1-01 | D11-s1 | D11.M1 | high | I3 | A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false) | reported |  |
| D11-s1-02 | D11-s1 | D11.M4 | high | I3 | A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator | reported |  |
| D11-s1-03 | D11-s1 | D11.M2 | medium | I3 | Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write | reported |  |
| D11-s1-04 | D11-s1 | D11.M2 | medium | new | Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record | reported |  |
| D11-s1-71 | D11-s1 | D11.M3 | low | I4 | Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint) *[from lead (L3)]* | reported |  |
| D11-s1-72 | D11-s1 | D11.M3 | low | I4 | entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes *[from lead (L3)]* | reported |  |
| D11-s2-01 | D11-s2 | D11.M3 | medium | I3 | Per-file policy caps count lines, so a capped rule file grows in prose with its per-file budget check green | reported |  |
| D11-s2-02 | D11-s2 | D11.M1 | medium | I3 | policy_lint --hooks never reads a hook's matcher: a PreToolUse matcher naming no edit tool passes as wired | reported |  |
| D11-s2-03 | D11-s2 | D11.M2 | medium | new | The owner-approval predicate keys on the tvofi account, and 6 of 6 sampled owner approvals at head were seat-given | reported |  |
| D11-s2-04 | D11-s2 | D11.M3 | low | I5 | CLAUDE.md rule 1 quotes a mode line the gate does not print, and says FULL prints a zero it does not | reported |  |

#### D12 — Generalization

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D12-s1-01 | D12-s1 | D12.M2 | high | P6 | Hot water without a tank probe: every solve starts from the 55 C ThermalState default, never advanced | reported |  |
| D12-s1-02 | D12-s1 | D12.M2 | high | P2 | Untouched Hot water / Hot water tank options page turns hot-water planning on for an install with no tank | reported |  |
| D12-s3-81 | D12-s3 | D12.M4 | medium | P8 | Grid-fee bounds are SEK numbers: a 0.05 EUR/kWh fee is unenterable in HUF, ISK, JPY and KRW *[from lead (L4)]* | reported |  |

#### D13 — Process yield and cost

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D13-s1-01 | D13-s1 | D13.M1 | medium | I4 | --stats API-mode enumerator silently drops 52 of 253 window merges whose /commits/<sha>/pulls answers [] | reported |  |
| D13-s1-02 | D13-s1 | D13.M1 | high | new | 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits | reported |  |
| D13-s1-03 | D13-s1 | D13.M3 | high | new | Body-answer blocks (8) exceed every engineering block class (max 1); record-and-body 12 vs engineering 7 | reported |  |

#### D14 — Recurring bug classes

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D14-s1-01 | D14-s1 | D14.M3 | medium | P1 | P1: a malformed store leaf raises out of a loader or consumer; a naive legionella timestamp wedges every refresh | reported |  |
| D14-s1-02 | D14-s1 | D14.M3 | low | P6 | P6: horizon_hours read from coordinator.data but never written; boost probes a field only a test double defines | reported |  |
| D14-s2-01 | D14-s2 | D14.M4 | medium | P2 | P2: the two-zone and wood-furnace facts are re-derived from a proxy key at three seams beside their canonical predicate | reported |  |
| D14-s2-02 | D14-s2 | D14.M4 | medium | P8 | P8: a money figure's currency comes from the label source, never from the price feed that denominates it | reported |  |
| D14-s2-03 | D14-s2 | D14.M4 | low | I4 | I4: class roster and finding grammar have disagreeing readers (P11 on no D14 seat; intake admits schema-refused ids) | reported |  |
| D14-s3-01 | D14-s3 | D14.M4 | low | P3 | P3: 22 quantities are read through a positive floor at one seam and raw at a sibling; no check enumerates them | reported |  |
| D14-s3-02 | D14-s3 | D14.M4 | low | P4 | P4: both multi-start seams stop at non-stationary points; 12 of 30 seam calls ship >0.1 % above reachable | reported |  |
| D14-s3-03 | D14-s3 | D14.M4 | medium | P5 | P5: sysid adoption gate keys on the UA half-width, which barely moves while unmodelled free heat biases UA to -21 % | reported |  |
| D14-s4-01 | D14-s4 | D14.M4 | high | P7 | Eight production seams still do wall-clock datetime arithmetic across DST; the forecast grid lands 60 min off | reported |  |
| D14-s4-02 | D14-s4 | D14.M3 | medium | P7 | The replay lane freezes a fixed-offset clock, so a DST-day replay reports zero P7 seams | reported |  |
| D14-s5-01 | D14-s5 | D14.M3 | medium | I2 | Python closures miss every file a spawned child process reads; select() skips the script on a change to it | reported |  |
| D14-s5-02 | D14-s5 | D14.M3 | medium | I1 | Mutation ratchet inventory cannot see 528 of 2313 production guard seams; a new guard of those shapes raises it by 0 | reported |  |

**D3 findings rest on the seats' pre-screen evidence.** D3's method (`tools/audit/briefs/D3.md`) turns a pre-screened survivor into a finding only after the quiet-window `GATE_SCOPE=full GOLDEN_MODE=drift` gate confirms it; that quiet window was **not run** this round, by tvofi's rule of 2026-09-26 (no heavy D3 re-runs). D3-s1's and D3-s2's findings above are registered as reported on the strength of the pre-screen closures alone, and the judge inherits that gap rather than a re-measured one.

### Leads — round 9

What the finder seats noticed outside their own cells, routed to the four leads seats (L1-L4). A lead is **converted** into a finding only with an executed number (rows above, marked *from lead*), or **closed** with a reason. Taken from `leads_result.json`, `leads_result_L2.json`, `leads_result_L3.json` and `leads_result_L4.json`.

| raised by | owner seat | file | symbol | converted to / closed because |
|---|---|---|---|---|
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator.async_run_optimization (:5096 _record_quiet_comfort_period) | converted to D1-s2-51 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | _async_save_ledger / _async_save_thermal_learning / _async_save_price_model / _async_save_energy_totals | converted to D1-s2-52 |
| D1-s3 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._apply_action | converted to D1-s2-51 |
| D6-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/services.py | handle_apply_manual_plan | converted to D1-s2-54 |
| D14-s4 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | _run_in_process / _ensure_worker | converted to D1-s2-55 |
| D1-s1 | D1-s5 (L1) | custom_components/heatpump_optimizer/inputs.py | input reader (problem codes) | converted to D1-s5-52 |
| D8-s1 | D2-s1 (L1) | custom_components/heatpump_optimizer/coordinator.py | _dhw_setpoint_sweep | converted to D2-s1-51 |
| D7-s2 | D5-s2 (L1) | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.buffer_temp_trajectory | converted to D5-s2-51 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/ | set_thermal_parameters | converted to D1-s2-53 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/ | async_reset_comfort_weight and the cycle-end save | converted to D1-s2-52 |
| orchestrator (#110) | D1-s5 (L1) | custom_components/heatpump_optimizer/inputs.py | INPUT_MAX_AGE_MINUTES age gate (Indoor Temperature unavailable after 60 min) | converted to D1-s5-51 |
| D1-s1 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s2 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s4 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s3 | D1-s1 (L1) | tests/hastub/homeassistant/util/dt.py | now | converted to D1-s1-52 (outside L1's own dimension) |
| D14-s1 | D1-s1 (L1) | tests/hastub/homeassistant/util/dt.py | now | converted to D1-s1-52 (outside L1's own dimension) |
| D7-s3 | D7-s3 (L1) | tests/nightly_ha.py | line 1274 (return inside finally, A4 recovery block) | converted to D7-s3-51 (outside L1's own dimension) |
| D0-s3 | D5-s2 (L1) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | converted to D5-s2-51 (outside L1's own dimension) |
| D0-s1 | (L1, closed) | tests/optimality.py | score_plan / pin_result | closed: owner deferred to catch-up batch; re-route then (owner D3-s3) |
| D0-s1 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._solve_space / _co_optimize | closed: closed by D0-s3 non-finding (M6/M7 measured by the owner: step 0 moves 1.197->1.200 kW in the largest cell, none in the other two); D0-s1 non-finding (horizon not reachable) |
| D0-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize | closed: closed by D0-s3 non-finding M6/M7 (receding-horizon realisation measured by the owner) and D0-s2-01/02, which carry the step-0 change |
| D0-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | closed: closed by D0-s3 non-finding M7 (terminal-credit share at 6 h measured by the owner) |
| D0-s3 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / HeatPumpOptimizer._solve_space seed set | closed: closed by D0-s1 non-finding: two-zone winter grid gap within 0.54 %, step 0 unchanged |
| D0-s3 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize seed set | closed: closed by D0-s2-02 (same seed-set gap on shoulder/summer_negative cells) |
| D1-s1 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _async_update_data (:4677 _async_watch_learning_drift guard); _async_load_accuracy (:7270-7283) | closed: closed by D1-s2 non-finding M2 (owner measured the from_dict chain: no sibling store lost at this baseline); the DEBUG heartbeat log is the documented guard level |
| D1-s3 | (L1, closed) | custom_components/heatpump_optimizer/services.py | SERVICE_SCHEMA_SET_AWAY | closed: closed by D1-s3-01 (tz-less return_time reaching the coordinator is that finding's mechanism) |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | thermal-learning load of internal_gains_profile (~3018-3023) and _learn_internal_gains (~8550) | closed: non-finding by measurement: gains_nan_probe.py nonfinite=0/4 (QuarantiningStore._sanitize scrubs "nan"/"inf" strings before float()); --raw bypass control 4/4 |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _shutdown_process_pool / _run_in_process | closed: closed by D1-s2-05 (shutdown waits on _PROCESS_LOCK held across the solve) |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _forecast_arrays | closed: non-finding by measurement: forecast_nonfinite.py failed_arms=0/7 at the coordinator boundary; positive control -1e308 fails (finite-absurd class is D1-s4-owned) |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator (price_sensor attributes at ~6992, peak_threshold_kw) | closed: closed by D1-s5-02 (negative threshold from a corrupt peak store is that finding's producer; publishing is its downstream) |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | solar_radiation horizon build from OpenMeteoSolar.irradiance_for | closed: closed by D1-s5-04: all-None irradiance falls back to the weather entity, else 0.0 (coordinator.py:6159), logged at DEBUG |
| D4-s2 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | dhw_legionella_above_setpoint repair (config_flow._dhw_legionella_warning judgement) | closed: non-finding: the shipped 55/60 default pair is excluded as "stock" in legionella.py, so a fresh default install raises no repair |
| D8-s1 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _get_current_price / _current_spot_price | closed: closed by D2-s3-01 (hour-window pricing under quarter-hour prices) |
| D1-s1 | (L1, closed) | custom_components/heatpump_optimizer/dhw_draws.py | DrawStats.fold / from_dict | closed: closed by D1-s1-03 (unbounded DrawStats energy is that finding) |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._stability_substeps | closed: closed by D1-s2-02 (runaway wind-driven substeps) |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | closed: closed by D1-s2-02 (non-physical finite forecast accepted); owner-side D1-s4 guard scope |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._stash_price_horizon | closed: inf sigma unreachable: QuarantiningStore._sanitize scrubs non-finite residual_var before from_dict; finite-absurd variance is D1-s5-02; price_risk_lambda defaults to 0 |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/store.py | QuarantiningStore._sanitize | closed: closed by D1-s2-03 (>= 2**64 counts through the loader int()) |
| D2-s1 | (L1, closed) | custom_components/heatpump_optimizer/sysid.py | identify / heat-loss learner (house_heat_loss_scale) | closed: closed as seam of D2-s1-01: the learned scale enters the same diagonal the substep count already includes |
| D2-s4 | (L1, closed) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.simulate_step | closed: closed by D2-s1 non-finding (dt invariance measured by the owner) |
| D8-s1 | (L1, closed) | custom_components/heatpump_optimizer/battery.py | VirtualBattery / label_measured | closed: closed by D12-s1-01 (unmodelled constant tank default) and the #282 disclosure decision |
| D6-s2 | (L1, closed) | docs/configuration.md | lines 181-187 (setup hot-water table) | closed: closed by D5-s1-02 (configuration.md table split) |
| orchestrator (#110, D4 framing) | (L1, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | IndoorTempSensor source-id attribute / card _entityIds indoor derivation | closed: D4 (card): route to D4 owner. The D4 side stands structurally: IndoorTempSensor publishes no source-entity attribute (sensor.py:636-661 defines no extra_state_attributes) and the card derives its indoor trace only from *_indoor_temperature_optimizer (card.js:4749-4775), so it cannot draw the raw thermometer through the stale gap; not measured by L1 |
| D1-s2 | (L1, closed) | tests/harness.py | ha_unload_entry | closed: non-finding by measurement: unload_coroutines.py dropped=1, raised_when_run=0 (the dropped async_shutdown coroutine has no effect the harness can observe) |
| D8-s1 | D8-s3 (L2) | custom_components/heatpump_optimizer/sensor.py | ValveTargetRecommendationSensor | converted to D8-s3-61 |
| D1-s3 | (L2, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | away-strip data-away-return change handler | closed: Same phenomenon as D1-s3-01, which names the card's datetime-local value as a seam (tz-less return_time; every later cycle raises until away is switched off). Card side (owner D4-s1 by check_scopes) is a seam of that finding, not a second one. |
| D4-s1 | (L2, closed) | custom_components/heatpump_optimizer (plan narrative sensor) | plan_narrative attributes.language | closed: Owner D8-s1 by check_scopes (sensor.py, D8.M2 attributes). Measured, holds: narrative_language_mismatch=0 of 4 hass.config.language arms (l2_d8_leads.py --only E; perturbation -> 2). The backend follows HA's configured language; a single-state sensor cannot follow each viewer's UI language. |
| D8-s3 | (L2, closed) | README.md | Entities > temperatures table, Upper Floor Temperature row | closed: Owner D6-s1 (README.md). Seam of D8-s3-03, which measured Upper Floor Temperature = Indoor Temperature on all 5 topologies including single-zone installs with no upper floor; README:503's 'The radiator zone' is true only under the two-zone convention the sensor docstring states. The README row is carried with that finding's fix. |
| D10-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | SolarIrradianceSensor.extra_state_attributes / open_meteo.OpenMeteoSolar.diagnostics | closed: Owner D8-s1 by check_scopes (sensor.py attributes). Measured: 5 dp recorded vs diagnostics' 1 dp (l2_d8_leads.py --only F). Not a defect: the value is hass.config's own home coordinate inside the instance; diagnostics coarsens because that file leaves it. |
| D10-s2 | (L2, closed) | custom_components/heatpump_optimizer/icons.json | services section | closed: Owner D4-s2 by check_scopes (icons.json); measured by D4-s2-08 (12 of 12 services without an icon). |
| D11-s1 | (L2, closed) | docs/decisions/0011-app-authored-identity.md | Context: 'about eleven of its merged pull requests now return 404' | closed: No seat owns it: check_scopes --seat for every D11/D5/D6 seat lists no docs/decisions/** cell (D11's universe is .github/.claude/.cursor/tools/CLAUDE.md/AGENTS.md; D5/D6 name specific docs files), although D11.md M3 names 'status lines in docs/decisions/'. Scope gap for the orchestrator to route; the executed 52-of-253 count is D11-s1's (its exposure line). Not measured here: it needs GitHub API reads. |
| D11-s1 | (L2, closed) | docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md | step 3(d) dismiss_stale_reviews_on_push: true | closed: Measured by D11-s1-01, whose claim names decisions 0008 3(d) and 0009 step 6 against live ruleset 23698884 (dismiss_stale_reviews_on_push=false). |
| D4-s2 | (L2, closed) | custom_components/heatpump_optimizer/wood_fuel.py | wood_fuel_ready / cheaper_hour_count (CONF_WOOD_PRICE_SEK_M3) | closed: Owner D12-s1. Measured (l2_wood_currency.py): the comparison is currency-agnostic, factors_changing_count=0 of 6. The harm is D4-s2-02's form label: a EUR install typing the price in SEK as the unit asks gets 0 cheaper steps vs 60. Seam evidence for D4-s2-02; the SEK-named keys price_sek_m3/sek_per_kwh belong to the same fix. |
| D5-s1 | (L2, closed) | custom_components/heatpump_optimizer/translations/en.json | config.step.quick_setup.data_description.buffer_tank / wood_buffer_tank | closed: Seam of D5-s1-02 (same mechanism: quick_setup.derive never sets a throttling mixing valve, so buffer_is_store and two_tank_modelled stay off). The form text at translations/en.json:312/:315 (strings.json same keys) is a second place the claim shows; carry it to that finding's seams. |
| D6-s2 | (L2, closed) | custom_components/heatpump_optimizer/strings.json | options ... data_description.curve_learning_enabled (line 1333) | closed: Seam of D6-s2-03 (curve bias moves 0.6 K in 7 days against 'at most 0.5 K per week'); strings.json/en.json:1333 carries the same figure as 'at most half a degree per week'. |
| D12-s1 | (L2, closed) | custom_components/heatpump_optimizer/config_flow.py | HeatPumpOptimizerConfigFlow.async_step_dhw | closed: Seam of D12-s1-02 (an untouched hot-water page stores dhw_windows/dhw_tank_volume and turns DHW planning on); its harness phantom_dhw.py already drives the wizard_dhw_step seam (HeatPumpOptimizerConfigFlow.async_step_dhw). The missing 'no tank' answer is that finding's fix surface. |
| D5-s1 | (L2, closed) | README.md | Entities: 'Nineteen entities (eighteen sensors and the wood binary sensor) are disabled by default' | closed: Owner D6-s1 measured it: D6-s1-03 (26 disabled on a no-hot-water install, six DHW sensors unlisted) and NF C08/C09 (19 on a hot-water install, list matches); D8-s3's NF agrees (19 + 7 DHW-gated). |
| D6-s2 | (L2, closed) | README.md | line 44 | closed: Owner D6-s1 measured it as a non-finding (claims.py C27-C48, 'curve 0.5 K/week' equal to the constant). That check reads the constant; D6-s2-03 measures the behaviour at 0.6 K in 7 days. The judge reconciles the two; README:44 is a seam of D6-s2-03's phenomenon. |
| D5-s1 | (L2, closed) | docs/setup.md | 'the original eleven-page wizard'; 'Quick setup arrived in v6.6.5' | closed: Owner D6-s2; measured here, holds: 10 screens at v6.6.4 on either building route (8 forms + 2 menus), 11 with the opt-in device pre-fill page; #1251 under the v6.6.5 heading (l2_wizard_pages.py; --with-offer -> 11). |
| D5-s1 | (L2, closed) | docs/ecl110.md | ## Sensors: 'on an install whose topics were configured at setup they are enabled' | closed: Owner D6-s2. Stale wording, not a false instruction: no initial-flow page offers an ECL110 topic (D6-s1 NF C49/C50), and ecl110.md:113-114 prescribes the only reachable route (topics added in Options, enable from the device page); 'configured at setup' describes only pre-v4.1.0 entries, which the same doc states at :88. README:549-550 is the same wording. |
| D5-s1 | (L2, closed) | docs/configuration.md | Services table: simulate_plan '16 optional comfort and wood fields' | closed: Owner D6-s2 measured it as D6-s2-05 (the paragraph lists 11 of the schema's 16 fields); D5-s1-06 carries the structure half. |
| D8-s1 | (L2, closed) | custom_components/heatpump_optimizer/entity.py | commanded_power_kw (climate recommended_power_kw) | closed: Seam of D8-s1-03: climate.py:232 publishes recommended_power_kw from entity.commanded_power_kw, the symbol D8-s1-03 instruments (whose docstring lists the climate among its four readers). |
| D8-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | IndoorTempSensor.available | closed: Owner D8-s1; measured, holds: non_measured_hidden=0 over 5 topologies; the 20 hidden entities are the thermometer's own and the thermal-battery 'store sensed' gate (l2_d8_leads.py --only B; perturbation gate -> 5). |
| D8-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | Heat Pump Action / operating-state sensors | closed: Owner D8-s1; measured, holds: boost_off_mismatch=0 of 7 mode-off boost arms, control 0; Heat Pump Action reads the actuated action's mode (boost / hot_water) (l2_d8_leads.py --only A; perturbation label -> 7). |
| D8-s3 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | DHWHeavyDaySensor | closed: Owner D8-s1; measured, holds: heavy_day_on_no_dhw=0 of 3 no-DHW topologies, and tests/entities.py _DHW_GATE_EXCEPTIONS names it with its reason (l2_d8_leads.py --only C). |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/config_flow.py | config-flow-test-coverage / test-coverage rows | closed: Owner D10-s2 measured D10.M3 as a non-finding: every module above 95 % statement coverage (min 95.12 %), which decides both coverage rows. |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/strings.json | exceptions section | closed: Owner D10-s2 NF exception-translations: raise_without_key=0 at baseline. The keys owed by fixes of D10-s1-02/-03 are a constraint on those fixers, not a baseline defect. |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/quality_scale.yaml | manifest quality_scale: platinum | closed: Not a separate mechanism: the declared tier stands or falls with D10-s1's Bronze/Silver findings; D10-s2's gold/platinum rows are non-findings except D10-s2-01. |
| D14-s4 | (L2, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | slot-hit rect (TARGET_MIN_PX_COARSE) | closed: Owner D4-s1 NF: every HTML control clears 24 px (44 px coarse); lane slot targets are recorded there as the boxed-in residue by design. |
| D5-s2 | D1-s2 (L3) | tests/hastub/homeassistant/helpers/update_coordinator.py | DataUpdateCoordinator.__init__ | converted to D1-s2-71 |
| D5-s2 | D7-s1 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalParameters.dhw_inlet_temp | converted to D7-s1-71 |
| D7-s2 | D7-s3 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._step_dhw_refused/_step_dhw_floor_injected/_step_dhw_draw_kw/_step_wood_refused | converted to D7-s3-72 |
| D9-s2 | D9-s1 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.effective_dhw_draw_pattern / dhw_tank_heat_loss_coefficient / dhw_inlet_reference | converted to D9-s1-71 |
| D12-s1 | D9-s2 (L3) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | converted to D9-s2-71 |
| D11-s2 | D11-s1 (L3) | .claude/workflows/rules_sync.mjs | parse | converted to D11-s1-71 |
| D13-s1 | D11-s1 (L3) | tools/audit/round4/D11/governance_cost.py | GOV | converted to D11-s1-72 |
| D1-s1 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | closed: done by L1: D1-s1-51 |
| D1-s2 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_load | closed: done by L1: D1-s1-51 |
| D1-s2 | (L3, closed) | tests/harness.py | ha_unload_entry | closed: done by L1: non-finding (unload_coroutines.py dropped=1, raised_when_run=0) |
| D1-s3 | (L3, closed) | tests/hastub/homeassistant/util/dt.py | now | closed: done by L1: D1-s1-52 |
| D1-s4 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | closed: done by L1: D1-s1-51 |
| D3-s1 | (L3, closed) | tests/golden/coord_dhw.json | data.dhw_advisor | closed: closed by D3-s1's own M2 prescreen entry: dhw_advisor is produced in coordinator.py (D3-s1's cells, check_scopes --seat D3-s1), and mutant C0086 (_dhw_setpoint_sweep) was KILLED by features.py, so the gate is not blind to the advisor's cover/ranking logic; the golden's degeneracy is redundancy, not a gap. Not re-run (tvofi 2026-09-26: no heavy D3 scripts). |
| D3-s1 | (L3, closed) | tools/audit/round3..round8 | (tracked files) | closed: by design, measured: r9-strip-rounds.sh (prepare_baseline strip_earlier_rounds) run on this seat's export printed RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 -- the same 498; it keeps every tools/audit/round* file named in tests/closures.json or by a literal path in tests/*.py\|*.mjs\|*.sh, so no file the gate reads is removed. Export-only; the tracked tree is untouched. |
| D4-s1 | (L3, closed) | tests/card_rig.mjs | planStates | closed: closed by D4-s1-05 (now-marker label over the measured-now reading on the live default view): that the card lanes' default-view states come from planStates() without withActuals is why the gate missed it -- the failing lane test that finding's fix owes (fixer.md step 1) and the escape's process cause under defect-root-cause.md, not a second mechanism. Owner D4-s1 (www/**; tests/*.mjs sit in no seat's cells, check_scopes). |
| D4-s1 | (L3, closed) | tests/card_browser.mjs | contrastOf / REQUIRED | closed: closed by D4-s1-01 (status-token text below WCAG AA): the contrast lane measuring four fixed sites on fixtures with no status outcome is why the gate missed it -- the failing lane test that fix owes and its root-cause seat's process cause, not a second mechanism. Owner D4-s1. |
| D6-s2 | (L3, closed) | tests/entities.py | README count pins (~lines 566-886) | closed: closed by D6-s2-01 (configuration.md 'All 74 entities' vs 75): the missing pin is the failing test that finding's fix owes under fixer.md step 1, not a second mechanism. D6-s2's cells hold docs/configuration.md (check_scopes --seat D6-s2). |
| D7-s3 | (L3, closed) | tests/nightly_ha.py | line 1274 (return inside finally, A4 recovery block) | closed: done by L1: D7-s3-51 |
| D11-s1 | (L3, closed) | tests/delivery_status.py | collect | closed: same phenomenon and seam as D11-s1-02 (single-parent direct pushes to main reported by no enumerator); its proposed_fix_scope already names delivery_status.collect. The docstring is that seam's prose; no separate mechanism. |
| D12-s1 | (L3, closed) | tools/audit/round9/D12/s1/ | REPORT.md | closed: not a defect of the baseline: a report-rendering matter for the orchestrator (the seat's JSON is its report). Nothing to measure. |
| D12-s3 | (L3, closed) | tests/entities.py | _walk_flow_untouched / check 'and turns hot water on anyway, with the 200 L tank the page pre-fills' | closed: owner deferred to catch-up batch; re-route then (a test-suite gap on config_flow.py is a D3 cell; check_scopes --seat D3-s3 lists config_flow.py) |
| D14-s1 | (L3, closed) | tests/hastub/homeassistant/util/dt.py | now | closed: done by L1: D1-s1-52 |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._run_system_identification | closed: closed by D9-s1-03, one finding per mechanism: its claim already names the synchronous call of SystemIdentification.step in coordinator._async_update_data; the call-site fix is that finding's fix scope. |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _maybe_run_fuse_advisor / _await_optimize | closed: closed by D9-s2's non-finding 'A coordinator cycle runs exactly one full solve by default': solves_per_cycle_mean=1.0000 (main 48/48), 2.0000 with price tiles, fuse advisor 0 solves/day (weekly rate limit). |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _solve_snapshot | closed: closed by D9-s2's non-finding on the default cycle's loop-thread work: loop_update_cpu_ms=9.03 per cycle (0.617 reference solves including the entity read), which bounds everything _async_update_data runs on the loop, _solve_snapshot included. |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _await_optimize (in-process fallback) | closed: closed by D9-s1's non-finding (in-process fallback starvation share 0.91-0.94, documented degraded path capped by WORKER_FALLBACK_CAP with a repair issue); what remains is a design choice about N, not a falsifiable defect. |
| D9-s2 | (L3, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._build_dhw_requirements / _apply_dhw_min_run / _plan_dhw_min_cost | closed: closed by D9-s1-04 and D9-s1's DHW-planner non-finding: _build_dhw_requirements is the parent of every DHW planner (optimizer.py:4712; it calls _plan_dhw_min_cost, _plan_dhw_cheapest_first, _apply_dhw_min_run, _clamp_dhw_to_capacity, _repair_dhw_floor), D9-s1 decomposed that parent (0.526 of the single-zone DHW solve, 0.287 of it _apply_dhw_min_run = D9-s1-04; each other planner 0.001-0.124). The replay's 58 % is the same parent under cProfile. |
| D11-s2 | (L3, closed) | .github (ruleset on main) | pull_request rule: require_last_push_approval / dismiss_stale_reviews_on_push | closed: closed by D11-s1-01 (ruleset dismiss_stale_reviews_on_push=false, require_last_push_approval=false; #1621 and #1623 merged on a stale owner approval). |
| D11-s2 | (L3, closed) | .claude/workflows/policy_lint.mjs | cmdHooks | closed: closed by D11-s2-02 (cmdHooks never reads a hook's matcher, 4 of 4 wrong matchers pass): the missing policy-rot/hooks fixture is the failing test that fix owes, not a second mechanism. |
| D11-s2 | (L3, closed) | .claude/workflows/budget_raise_gate.py | approval | closed: closed by D11-s1-04 (budget_raise_gate.py:approval accepts orchestrator-given approvals as the owner's, 27/27) and D11-s2-03; the lead names a fix constraint, not a defect. |
| D13-s1 | (L3, closed) | .github/workflows/governance.yml | instrument-self-tests | closed: not measured by this seat: the lead needs GitHub Actions run history and logs for governance.yml's instrument-self-tests on main, and this seat's GitHub API read was refused by the permission system (no gh, per brief). D13-s1's count (18 of 201 main merges, one 11.69 h episode) stands unconverted; re-route to a seat with GitHub read (D11-s1's d11lib cache) in the catch-up batch. |
| D13-s1 | (L3, closed) | .claude/workflows/web-fix-wave.js | verdict poster identity | closed: same phenomenon as D11-s1-04 (seat actions are recorded under the owner account, so the record cannot show the owner's own act); D13-s1's count 166 of 239 'Fix review:' lines under tvofi is a further seam of it, carried here for that finding's fix. No GitHub read from this seat. |
| D0-s1 | D2-s2 (L4) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | converted to D2-s2-81 |
| D4-s1 | D4-s2 (L4) | custom_components/heatpump_optimizer/topology.py | describe_setup slots / rank_sensor_advisor labels | converted to D4-s2-81 |
| D14-s3 | D2-s4 (L4) | custom_components/heatpump_optimizer/sysid.py | SystemIdentification (light_new preset) | converted to D2-s4-81 |
| D14-s2 | D12-s3 (L4) | custom_components/heatpump_optimizer/grid_fee.py | grid_fee:IMPLAUSIBLE_FEE_SEK_PER_KWH | converted to D12-s3-81 |
| D14-s2 | D6-s1 (L4) | custom_components/heatpump_optimizer/currency.py | currency:FALLBACK_CURRENCY | converted to D6-s1-81 |
| D0-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | closed: owner D2-s2 (objective shape, D2.M3). Measured, non-finding: the constant costs nothing -- polish gap 0.0000 % in 12 summer_warm cells (see non_findings). |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | closed: owner D2-s2 already measured the terminal credit's sign and magnitude against a re-simulated continuation: ratio 0.997-1.123 over 6 cells including shoulder, 0 sign disagreements (D2-s2 non-finding, terminal_continuation.py). |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | closed: done by L1: D5-s2-51 |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.predicted_cost | closed: owner D2-s2 measured predicted_cost == sum(price*(P_space+P_dhw)*dt) on all 50 golden scenarios (cost_err 0, D2-s2 non-finding); README.md:488 claims only 'Cost of the optimized 24 h plan', which that identity verifies, not the executed day. The 23.28 vs 38.61 SEK day gap is receding-horizon realisation (D0-s3's own M6 non-finding: the loop buys 0.6-1.0 K of warmth the objective values). |
| D1-s2 | (L4, closed) | custom_components/heatpump_optimizer/coordinator.py | async_diagnose_interval / _diagnose_payload | closed: owner D5-s2 (comment accuracy). Measured, non-finding: the worker does get copies on the production transport, leaked_writes=0 (see non_findings). |
| D2-s1 | (L4, closed) | custom_components/heatpump_optimizer/external_heat.py | ExternalHeatDetector.forecast_free_heat / optimizer.py HeatPumpOptimizer.optimize (np.clip of external_heat_kw) | closed: owner D1-s5 (external-input parsers). Measured, non-finding: nonfinite_forecast_cells=0 of 27; InputReader delivers no non-finite value (D1-s5 non-finding) (see non_findings). |
| D8-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | Optimizer._idle_action | closed: owner D8-s2 (climate recommended_power_kw via entity.commanded_power_kw). Covered by D8-s1-03: its property ('No entity attributes a power draw to the pump at a step the same action declares off') and fix scope (commanded_power_kw gates on heat_pump_on, shared with the climate attribute) include the idle action's power=min_electrical_power with heat_pump_on False; the fixer should add this seam to that finding's enumeration. |
| D9-s2 | (L4, closed) | custom_components/heatpump_optimizer/entity.py | HeatPumpOptimizerSensorBase.__init_subclass__ scrub (_finite) | closed: owner D9-s2, who bounds it already: its non-findings put loop-thread work outside the advisor at entity_read 5.89 ms per read and 0.617 reference solves per cycle, and the retained series the scrub walks are bounded (accuracy deque maxlen 672); the scrub is a subset of that bounded read, so no cost finding exists above the owner's bound. |
| D12-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.get_current_action | closed: owner D12-s2. Covered by D12-s2-03: its property ('power_normalized stay in [0,1] ... on every compressor kind') and fix scope (clamp to [0,1]) include the modulating -0.2, which its own null arm measured (minimum -0.2). |
| D12-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._idle_action | closed: owner D1-s2 (coordinator consumers). Not converted: the idle branch is reachable in production only when the wall clock steps back more than one step between _solve_anchor (now floored to the forecast grid) and get_current_action's only caller (coordinator.py:5074, right after the solve); the entity side of the same fact is D8-s1-03's property. Not measured here. |
| D12-s3 | (L4, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._build_data_dict | closed: owner D1-s2. Not converted: every published surface of these three keys gates on reading_ok (the dhw/buffer/slab sensors' _reading_key, climate._measured, battery.label_measured #282), reading_ok is published in the same data dict, and the card reads entity states only; the lead names no reader that shows them unflagged. Not measured here. |
| D14-s2 | (L4, closed) | custom_components/heatpump_optimizer/quick_setup.py | quick_setup:stored_answers | closed: owner D4-s2. Measured, non-finding: derive/stored_answers round-trip mismatch 0 of 32 (see non_findings). |
| D14-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / _lbfgsb_restart | closed: owner D0-s1. Not a production claim: the ABNORMAL terminations are a challenger's at ftol 1e-12; production runs ftol 1e-6, whose stop-rule residue is D0-s2-01's finding and D0-s1's stoprule_ab non-finding (not price-attributable in aggregate). |

### Judge flags

Verbatim, `judge_flags.txt`:

```
Round-9 exposure flags for the judge (orchestrator, 2026-09-26).
(1) Driver Prepare step 1 copied tools/audit/round3..round8 into every finder tree. The boxes ran handoff/round9/r9-strip-rounds.sh (498 removed, 235 gate-read kept). Seats that ran partly BEFORE the strip: B1 D0-s1 and D3-s1; B8 D14-s1..s3; B10 D4-s1; the B4 seats (strip about 12 min into the fan-out); the B6 seats.
(2) B8 D14-s3 read docs/audit-2026-09.md rows (rounds 1, 2, 4, 6, 7) to locate fixes, and recorded it under exposure.
(3) B9 D14-s4 read, but did not cite, the docstrings of round3/D2/dst_window_factors.py, round5/D1/seat-b/h5_dst_age_seams.py and 80 lines of harnesses/j5_gil.py before the strip. This bears on D14-s4-01 and D14-s4-02.
(4) B3 D13-s1 imports the brief-named instruments tools/audit/round4/D11/{dora_keys,governance_cost}.py (gate-read, kept by the strip). It read their headers only.
(5) B2 D0-s2 listed round8/ directory names before the strip and opened no file. B3 D11-s1 ran ls on round8/D11 once.
(6) Several REPORT.md files were rendered by the box host from the seat's JSON. reports-Bn.json is authoritative.
(7) D3 quiet window NOT run, by tvofi's rule of 2026-09-26: no heavy D3 re-runs. D3 findings rest on the seats' pre-screen evidence.
(8) Catch-up batch: D3-s2 is in (registered with the lead findings); D3-s3 is still to come.
```
