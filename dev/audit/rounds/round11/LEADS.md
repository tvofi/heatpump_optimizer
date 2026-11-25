# Round 11 leads (box B8, leads seat)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, measured in a private copy of the planted finder export (`audit-r11-leads-px`, prepared and stripped; not diffed against git), PYTHONPATH=tests/hastub. Owner seats' reports were read from `handoff/audit-r11-find-B1..B13`; a lead an owner (or another seat) already measured is closed by that entry, and every cited finding id was checked against the union of those reports (249 ids, 0 missing). Owner seats for 'unknown' leads were assigned from `check_scopes.py --seat` cell lists. This run resumes a predecessor leads seat's work in the same copy: its four harnesses were re-run (numbers below are this run's), its closures re-checked, and two further leads converted. A second resume (box B8, 2026-11-17 13:40Z) found 40 leads in the dispatch that the earlier runs had not seen (raised by the later B2/B3 seats: D0-s2, D3-s2, D5-s2, D5-s3, D6-s2, D6-s3, D9-s2, D9-s3, D10-s2, D10-s3), disposed of each against the B1..B13 reports fetched at this resume, and re-ran all six harnesses with and without --perturb: every value and perturbation reproduced exactly (load1 158-161).

Totals: 231 leads, 6 converted, 225 closed.

## Findings

### D1-s2-51 (high, bug): InputReader.read accepts any temperature above its plausible window: 15 of 15 keys deliver max+1

For every key of INPUT_PLAUSIBLE_RANGE_C, InputReader.read of a reading 1 degC above the key's window delivers it as a measurement, while 1 degC below the window is withheld.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/plausible_upper.py` (value 15 keys accepted above max (of 15); load1 161.41)
- Instrumented symbol: `heatpump_optimizer.inputs:plausible_c (via inputs:InputReader.read)`
- Perturbation: --perturb: plausible_c checks window[0] <= value <= window[1] in memory -> 0
- Null control: same run, below-min arm = 0 ((window min - 1) degC is withheld on all 15 keys: the lower bound is enforced)
- Metric: Keys of INPUT_PLAUSIBLE_RANGE_C whose InputReader.read of (window max + 1) degC returns reading.value not None.
- Property: Every plausibility window the reader applies is two-sided: a reading outside [low, high] of its key is withheld as implausible.
- Seam rule: `grep -n 'plausible_c(\|INPUT_PLAUSIBLE_RANGE_C' custom_components/heatpump_optimizer/*.py`

### D1-s2-52 (medium, bug): Indoor-humidity read ignores the entry's staleness settings: watchdog-off and scale 3.0 still drop the reading

HeatPumpOptimizerCoordinator._indoor_humidity_value builds InputReader(self.hass, {}) with the default enabled/scale, so with the staleness watchdog switched off or the age scale at 3.0 a 540-min-old humidity reading is withheld (mold floor disarmed) while a reader built from the entry's settings delivers it: 2 of 2 configuration arms disagree.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/humidity_reader_settings.py` (value 2 configuration arms where production withholds what the configured reader delivers (of 2); load1 159.3)
- Instrumented symbol: `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._indoor_humidity_value`
- Perturbation: --perturb: coordinator.InputReader replaced in memory by one taking the entry's staleness_watchdog_enabled / staleness_max_age_scale (the one-line fix at coordinator.py:9175) -> 0
- Null control: same run, default arm (watchdog on, scale 1.0) at the same age, and a fresh reading in every arm = 0 (null_disagree=0 and fresh_disagree=0: both readers agree where the settings do not matter)
- Metric: Arms (watchdog off; scale 3.0) where _indoor_humidity_value returns None for a reading aged 1.5x its scale-1 limit while an entry-configured InputReader returns the value.
- Property: Every InputReader the integration builds for a configured sensor takes the entry's staleness_watchdog_enabled and staleness_max_age_scale.
- Seam rule: `grep -n 'InputReader(' custom_components/heatpump_optimizer/*.py`

### D2-s1-51 (high, bug): Building preset 'low energy' derives 1.55x the heat loss of 'post 2005' in 36 of 36 cells

presets.derive's house_heat_loss_coefficient is not monotone in construction era: low_energy (0.85 W/m2K) exceeds post_2005 (0.55) and 1980_2005 (0.80), so a questionnaire low-energy house is modelled 1.545x leakier than a post-2005 one in every structure/foundation/area cell.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/leads/era_loss_order.py` (value 36 cells inverted (of 36); load1 159.3)
- Instrumented symbol: `heatpump_optimizer.presets:derive (reading presets:_ERA_LOSS_W_PER_M2K)`
- Perturbation: --perturb: _ERA_LOSS_W_PER_M2K['low_energy'] = 0.35 in memory -> 0
- Null control: same run, first four eras only = 0 (pre_1960 > 1960_1980 > 1980_2005 > post_2005 holds in all 36 cells)
- Metric: Cells (structure x foundation x area 80/140/250, single zone) where derive()'s house_heat_loss_coefficient is not strictly decreasing along presets.ERAS.
- Property: A newer or better-insulated era never derives a larger heat-loss coefficient than an older one, at any structure, foundation and area.
- Seam rule: `grep -n '_ERA_LOSS_W_PER_M2K' custom_components/heatpump_optimizer/presets.py`

### D1-s1-51 (low, bug): A tied slot reason publishes 'cheap' or 'preheat' by PYTHONHASHSEED: the same plan reads differently after a restart

plan_slots picks a slot's reason with max(set(codes), key=codes.count); on a tie the winner follows set iteration order, so one fixed 2:2 plan publishes two different reasons across PYTHONHASHSEED=1..12.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py` (value 2 distinct published reasons over 12 hash seeds; load1 158.95)
- Instrumented symbol: `heatpump_optimizer.plan_slots:plan_slots`
- Perturbation: --perturb: the module's set replaced by insertion-ordered dict.fromkeys -> 1
- Null control: same run, 3:1 plan = 1 (a plan with a strict majority publishes one reason under every seed)
- Metric: Distinct slot['reason'] values plan_slots returns for the 2:2 tied plan across child interpreters with PYTHONHASHSEED=1..12.
- Property: A published slot attribute is a function of the plan alone, not of interpreter hash randomisation.
- Seam rule: `grep -rn 'max(set(' custom_components/heatpump_optimizer/`

### D4-s2-51 (low, hygiene): Setup's first page passes a Tibber token hint ({tibber_info}) that no language renders

async_step_user passes description_placeholders {'tibber_info': ...} and none of en, de or sv references {tibber_info} under config.step.user, so the token hint is never shown.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D4/leads/dead_placeholder.py` (value 3 (language, placeholder) pairs unrendered; load1 158.32)
- Instrumented symbol: `heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow.async_step_user`
- Perturbation: --perturb: append ' {tibber_info}' to each loaded config.step.user.description -> 0
- Null control: same run, reverse direction = 0 (no user-step string references a placeholder the step does not pass)
- Metric: (language, key) pairs where a description_placeholders key the user step returns is referenced by no config.step.user string of that translation.
- Property: Every description placeholder a step passes is rendered by that step's text in every shipped language, and vice versa.
- Seam rule: `grep -n 'description_placeholders' custom_components/heatpump_optimizer/config_flow.py`

### D17-s3-51 (medium, bug): Published dhw_in_demand_window ignores a day-selector schedule: 18 of 336 week half-hours wrong

With dhw_windows 'weekdays 06:00-08:30, weekend 08:00-09:30' and no solved plan, _dhw_in_demand_window tests the flat union of every day's windows, so it reads True on Saturday 07:00 (next window 0.0 h) and on weekdays 08:30-09:30: 18 of 336 half-hour cells differ from the window in force that weekday.

- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py` (value 18 half-hour cells of the week where the published flag differs from the weekday's window (of 336); load1 158.32)
- Instrumented symbol: `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._dhw_in_demand_window (via _dhw_effective_windows)`
- Perturbation: --perturb: _dhw_effective_windows resolves today's weekday through dhw_schedule.windows_for_day in memory -> 0
- Null control: same run, flat spec '06:00-08:30' = 0 (with no day names the union is the schedule: 0 cells wrong)
- Metric: Half-hour cells over one week where _dhw_in_demand_window() != hour_in_windows(hour, windows_for_day(weekly, weekday, flat)).
- Property: Every published hot-water window attribute (in-window flag, hours to next window, windows text) resolves the same weekday's windows the plan uses.
- Seam rule: `grep -n '_dhw_effective_windows\|dhw_demand_windows' custom_components/heatpump_optimizer/coordinator.py`

## Non-findings

- The planted export copy carries no macOS AppleDouble ._* files, so every AppleDouble lead is an artefact of the earlier shared export, not the baseline: `find . -name '._*' | wc -l (export root)` -> 0
- Every finding id a closure cites exists in an owner seat's REPORT.json on the box evidence branches: `git show origin/handoff/audit-r11-find-B<1..13>:dev/audit/rounds/round11/*/*/REPORT.json; cited ids checked against the union` -> 249 ids indexed, 0 cited ids missing
- Null control of D1-s2-51: the lower plausibility bound is enforced on every key: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/plausible_upper.py` -> below_min_accepted=0 of 15
- Null control of D1-s2-52: with default staleness settings, and for a fresh reading, the humidity read agrees with an entry-configured reader: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/humidity_reader_settings.py` -> null_disagree=0, fresh_disagree=0
- Null control of D17-s3-51: a flat (no day names) hot-water spec publishes the in-window flag correctly in every half-hour of the week: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py` -> null_cells_wrong=0 of 336
- Null control of D2-s1-51: the four older eras derive strictly decreasing heat loss: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/leads/era_loss_order.py` -> null_cells_inverted=0 of 36

## Converted

| raised by | owner | file | symbol | finding |
|---|---|---|---|---|
| D5-s4 | D1-s1 | `custom_components/heatpump_optimizer/plan_slots.py` | plan_slots.plan_slots (slot['reason'] = max(set(codes), key=codes.count)) | D1-s1-51 |
| D7-s1 | D1-s2 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator (line 9175) | D1-s2-52 |
| D7-s1 | D1-s2 | `custom_components/heatpump_optimizer/inputs.py` | InputReader.read / plausible_c | D1-s2-51 |
| D4-s3 | D4-s2 | `custom_components/heatpump_optimizer/config_flow.py` | HeatPumpOptimizerConfigFlow.async_step_user description_placeholders['tibber_info'] | D4-s2-51 |
| D12-s2 | D2-s1 | `custom_components/heatpump_optimizer/presets.py` | _ERA_LOSS_W_PER_M2K | D2-s1-51 |
| D17-s2 | D17-s3 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._dhw_in_demand_window / _dhw_effective_windows | D17-s3-51 |

## Closed

| raised by | owner | file | symbol | why |
|---|---|---|---|---|
| D0-s1 | D0-s2 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._solve_space | not measured by this leads seat (no executed number); a closed-loop MPC run of the two-zone DHW plan against the seeds challenger is D0.M6 work; D0-s1-01 carries the open-loop gap; handed to D0-s2's next dispatch as not_reached. |
| D0-s1 | D0-s3 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._optimize_space_only | not measured by this leads seat (no executed number); the flat-price basin non-convexity needs a multi-start census; D0-s3's D0.M6 row already carries 9 not_reached items, this joins them. |
| D15-s3 | D0-s3 | `dev/governance/dimensions/D0.md` | step 8, same-information oracle | a method question for the brief, not a measurable code lead; goes to D0.md by finding-propagation, not to a finding. |
| D1-s1 | D1-s1 | `tools/audit/enumerate.py` | pkg_files | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. |
| D1-s1 | D1-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._async_update_data | not measured by this leads seat (no executed number); owner by check_scopes: D1-s1 (coordinator.py, M1+M4). D1-s1-03 measures the debounced in-flight write; the concurrent non-debounced second cycle and its double booking are handed to D1-s1's M4 as not_reached. |
| D1-s3 | D3-s3 | `tests/entities.py` | module level, line 9634 (_NOMINAL[_key]) | consequence of the two_zone_mode 'auto' -> on mechanism already found (D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01): the options page hides house_heat_loss_coefficient, so the check aborts/fails on it. |
| D2-s1 | D7-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalParameters.from_config (two_zone_mode) | already found: D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01. |
| D2-s1 | D2-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _propagated_slab / _replay_step | not measured by this leads seat (no executed number); owner D2-s1 (coordinator.py M1); its M1 identities exercised _propagated_slab but not behind a valve; handed to D2-s1's next dispatch. |
| D2-s2 | D8-s1 | `custom_components/heatpump_optimizer/sensor.py` | predictive_info['power_cap_breach_c'] | not measured by this leads seat (no executed number); a user-visibility question (D8.M2 sensor surface); D2-s2's non-finding records the plan publishes the figure. |
| D2-s2 | D3-s3 | `tests/features.py` | declared_modulation check near line 74196; derate_from_duty / flow_lift_factor checks | the checks run and fail on the planted export (features.py 131 FAIL, D7-s1 lead), so they are asserting; the production defects are D12-s3-01/D2-s2-03, D2-s2-02 and D2-s2-01. |
| D2-s2 | D2-s2 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _flow_target / FLOW_HEAT_C vs ThermalModel.compute_cop | the raiser records it as a modelled term by design ('not shown to be wrong'); no defect claim to measure. |
| D4-s3 | D4-s2 | `custom_components/heatpump_optimizer/topology.py` | setup_topology slots[].label / sensor_advisor candidates[].label | not measured by this leads seat (no executed number); backend label language not driven; handed to D4-s2's next dispatch. |
| D5-s1 | D6-s1 | `README.md` | Quick start 'Your first week' (L522) | held on the full install: 82 live entities measured by D14-s1's name-sort non-finding and D9-s1's 82-entity attribute run; D10-s2's disabled-by-default non-finding examined the README list. |
| D5-s1 | D5-s1 | `docs/configuration.md` | Wood tank top sensor row (L993) | same mechanism as D5-s1-01 (the two-tank activation rule the docs state does not match ThermalParameters.topology_layout/from_config). |
| D5-s1 | D5-s1 | `docs/CONTRIBUTING.md` | page as a whole | not measured by this leads seat (no executed number); a structure judgement with no executed number; D5-s2-02 (CONTRIBUTING linked from nowhere) and D6-s7-01 already hold the page. |
| D5-s4 | D6-s1 | `custom_components/heatpump_optimizer/*` | 3165 comment claim units | a ledger hand-off, not a defect; D6 seats row behavioural units not_reached in their coverage (D6-s1 M2 lists them), which carries them to the next dispatch. |
| D5-s5 | D6-s5 | `tools/policy/fixtures/figures/good.md, tools/policy/fixtures/policy-rot/prepr/red-answered.md` | tools/audit/prepr.sh | same phenomenon as D5-s5-02 (references to the pre-move tools/audit/prepr.sh); fixtures are lint inputs whose path text is data. |
| D5-s8 | D5-s8 | `tools/policy/agreement_py.py` | the sys.path list (line ~55) | not measured by this leads seat (no executed number); a dead sys.path entry with no behaviour reached; hygiene under D5-s8-01's moved-path phenomenon. |
| D5-s8 | D5-s8 | `tools/policy/policy_lint.mjs` | CORPUS_EXCLUDED pair near line 979 | already found: D5-s8-01 (policy_lint.mjs pre-move paths incl. corpus_excluded data). |
| D5-s9 | D5-s9 | `tests/entities.py` | string at line 1869 ('tools/audit/w5-partition/coverage_tree.sh and ratcheted per pull ...') | same moved-path phenomenon as D5-s9-01 and D5-s8-03 (coverage_tree.sh named at its pre-move path). |
| D6-s1 | D6-s1 | `tests/doc_claims.py` | DOCS glob / plan_view arm | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. The plan_view energy mismatch was read on a different tree; not measured here. |
| D6-s4 | D6-s4 | `tests/card.mjs` | R10-I18N-DE parity arm | already found: D6-s4-01 (sv stale-plan tooltip renders {minuter}). |
| D6-s5 | D6-s1 | `docs/ (options pages, manual-plan hours, weekly snapshots, +-12 %, external links)` | C1, C4 | D6-s1 examined C1 (non-findings: 20 h expiry holds, +-12 % holds) and rows C4 not_reached in its coverage, which carries it. |
| D6-s5 | D7-s1 | `custom_components/heatpump_optimizer/._*.py (export only)` | tests/structure.py:module_trees | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. |
| D6-s6 | D6-s3 | `custom_components/heatpump_optimizer/._const.py` | AppleDouble files | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. |
| D7-s1 | D7-s3 | `custom_components/heatpump_optimizer/power_guard.py` | project_window_mean | already found: D7-s3-02 and D17-s1-05. |
| D7-s1 | D8-s3 | `custom_components/heatpump_optimizer/sensor.py` | SpaceEnergySensor / DHWEnergySensor / TotalEnergySensor | already found: D10-s2-02 and D8-s3-01. |
| D7-s1 | D10-s1 | `custom_components/heatpump_optimizer/config_flow.py` | options-flow save (two-zone presence inference) | consequence of the two_zone_mode 'auto' -> on mechanism already found (D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01): the options page hides house_heat_loss_coefficient, so the check aborts/fails on it. |
| D7-s1 | D6-s1 | `custom_components/heatpump_optimizer/legionella.py` | the overdue anti-legionella cycle's placement | same mechanism as D6-s1-01/D5-s2-08: DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS is 10.0 (const.py:1600), so manual_plan.py's 200 h case is not due (240 h) and plans no cycle. |
| D7-s1 | D1-s2 | `custom_components/heatpump_optimizer/plan_step.py` | plan_step_start (and the DST seams around it) | not measured by this leads seat (no executed number); owner D1-s2 (M3 DST); plan_step.py is not among the export's edited files, and a tz-environment cause was not separated; handed to D1-s2's next dispatch. |
| D7-s1 | D15-s3 | `custom_components/heatpump_optimizer/debugger.py` | the debug bundle's inline / capped download | not measured by this leads seat (no executed number); D15-s1-04 and D15-s3-01 hold debugger defects; the inline/capped arms are handed to D15-s3's M8 not_reached. |
| D7-s1 | D3-s3 | `tests/features.py` | the suite's largest script, run on the tree itself | the suite going red on the planted export is the gate catching the export's planted production edits; each named line maps to an existing finding (flow_lift_factor D2-s1-01/D2-s2-01, _exact_topk_sum D7-s3-07, emitter_delivery D7-s3-08, declared_modulation D12-s3-01, two_zone auto D7-s3-09, inputs window D1-s2-51, legionella interval D6-s1-01) or is unmeasured here; a red suite is not itself a defect. |
| D7-s1 | D3-s3 | `tests/guard_pins.py` | #1913 GCHV hold; tests/block_duty.py start-hysteresis; tests/config_flow_steps.py; tests/finite_boundary.py | the suite going red on the planted export is the gate catching the export's planted production edits; each named line maps to an existing finding (flow_lift_factor D2-s1-01/D2-s2-01, _exact_topk_sum D7-s3-07, emitter_delivery D7-s3-08, declared_modulation D12-s3-01, two_zone auto D7-s3-09, inputs window D1-s2-51, legionella interval D6-s1-01) or is unmeasured here; a red suite is not itself a defect. golden strict CHANGED was not separated from BLAS drift (contention-provisional). |
| D7-s2 | D7-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalParameters.from_config (two_zone_mode) | already found: D7-s3-09 (and D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01). |
| D7-s3 | D1-s3 | `custom_components/heatpump_optimizer/boost.py` | persist (and six sibling save wrappers: m8_enum.py --show A014, A028) | not measured by this leads seat (no executed number); owner D1-s3 (M5); D1-s3-05 holds the persist handlers' logging; the save-before-load race is handed to its next dispatch. |
| D7-s3 | D7-s3 | `custom_components/heatpump_optimizer/config_flow.py` | HeatPumpOptimizerOptionsFlow._disinfection_errors | hygiene with no behaviour difference while both vocabularies spell 'control'; no executed number can move. |
| D7-s3 | D7-s3 | `custom_components/heatpump_optimizer/www/` | C2: card collaborators | not measured by this leads seat (no executed number); JavaScript collaborators outside D7-s3's Python cells; handed as not_reached. |
| D8-s1 | D11-s3 | `dev/audit/README.md` | What to reuse, and what will trip you | a toolkit documentation gap (the _run_in_process trap), not a defect with a number; goes to dev/audit/README.md by finding-propagation. |
| D8-s1 | D8-s1 | `custom_components/heatpump_optimizer/ledger.py` | coverage_factor / MonthlyLedger.savings_months | same mechanism as D8-s1-02 (open-month extrapolation in coverage_factor); its readers are that finding's seams. |
| D8-s1 | D8-s1 | `custom_components/heatpump_optimizer/topology.py` | rank_sensor_gaps | same mechanism as D8-s1-01 (dhw_temp_entity priced without the DHW gate). |
| D8-s2 | D8-s2 | `dev/audit/config/scopes.json` | D8-s2 cells (D8.M3) | a scopes configuration gap the raiser already measured through (datetime.py driven); for the round's evaluation, not a product finding. |
| D8-s2 | D4-s2 | `custom_components/heatpump_optimizer/services.py` | run_optimization (raises run_optimization_no_prices with {entry_ids}) | already found: D4-s2-02 measures the services raise site of the same key (with D8-s2-01, D10-s2-03 on the button). |
| D8-s3 | D6-s1 | `README.md` | Entities section, 'Twenty entities ... are disabled by default' | not measured by this leads seat (no executed number); a D6 claim check handed to D6-s1's not_reached; D10-s2's disabled-by-default non-finding read the DHW install. |
| D9-s1 | D9-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator.async_diagnose_interval | same mechanism as D9-s1-01 (a diagnose press runs a full cycle); the double-pairing consequence is that finding's seam. |
| D10-s1 | D7-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalParameters.from_config (two_zone_enabled) | already found: D12-s2-01, D17-s2-01, D7-s3-09. |
| D10-s1 | D6-s2 | `custom_components/heatpump_optimizer/const.py` | COMBI_TANK_PRESETS['external_station'] | already found: D6-s2-01 and D6-s6-01 (potable_volume_l 150 against its own 0 l). |
| D10-s1 | D1-s1 | `custom_components/heatpump_optimizer/pump_arbiter.py` | note_supply / _listen | not measured by this leads seat (no executed number); owner D1-s1 (M1 lifecycle); handed to its next dispatch. |
| D10-s1 | D3-s3 | `tools/coverage/coverage_tree.sh` | DERIVED (header comment on run_always scripts) | not measured by this leads seat (no executed number); comment vs run.sh; handed to D3-s3 (no D3-s3 report was on any box branch). |
| D12-s1 | D12-s1 | `custom_components/heatpump_optimizer/ (17 modules), www/heatpump-optimizer-card.js, translations/de.json` | the export tree | by design: the export under audit is the planted finder export (the task names it and forbids diffing it against git); the provisioning question is the orchestrator's, not a finding. |
| D12-s1 | D12-s1 | `tools/audit/enumerate.py` | tracked | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. |
| D12-s2 | D12-s2 | `custom_components/heatpump_optimizer/translations/._de.json` | tests/harness.py:SHIPPED_LANGS; tools/audit/enumerate.py:d12 | export artefact: macOS AppleDouble ._* files were in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0 lines), and they are not in the baseline tree. Not a baseline defect. |
| D13-s2 | D13-s2 | `tools/policy/check-wave-script.mjs` | taughtWords (the 'teaches block class' check) | already found: D13-s2-01 names this as its mechanism half. |
| D13-s3 | D13-s3 | `.github/workflows/tests.yml` | nightly-status | not measured by this leads seat (no executed number); a CI-history census for D13-s3's next dispatch. |
| D14-s1 | D14-s1 | `custom_components/heatpump_optimizer/sensor.py` | entity_category of family members (learning, optimization, dhw, cost, indoor, prediction, wood) | informational by the raiser; Home Assistant splitting cards by entity_category is its design, and D10-s2's entity-category non-finding holds the categories. |
| D14-s2 | D14-s2 | `dev/audit/config/bugclasses.json` | N-orphaned-handoff.status | a brief/ledger vocabulary note for D14.md, routed by finding-propagation; no product number. |
| D15-s1 | D15-s1 | `dev/audit/harnesses/r10_scores_envelope.py` | --bundle arm | a round-10 carry to run, not a defect; stays with D15's carries. |
| D16-s1 | D12-s3 | `custom_components/heatpump_optimizer/pump_arbiter.py` | desired (idle row) without heat_pump_switch_entity | not measured by this leads seat (no executed number); a D12 configuration level; handed to D12-s3's next dispatch. |
| D16-s1 | D16-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._apply_action (stale branch) | already found: D16-s1-04 (stale plan on an idle step leaves the supply off). |
| D16-s2 | D16-s2 | `custom_components/heatpump_optimizer/dhw_planner.py` | start mask (dhw_start_below_c) | not measured by this leads seat (no executed number); handed to D16-s2's next dispatch. |
| D17-s1 | D17-s1 | `tools/audit/enumerate.py` | d17 | already found: D17-s1-01 (156 section-nested option fields outside the enumerator). |
| D17-s2 | D6-s2 | `custom_components/heatpump_optimizer/strings.json` | config.step.temperature.data_description.target_temperature | not measured by this leads seat (no executed number); a D6 sentence for D6-s2's next dispatch. |
| D17-s2 | D6-s2 | `custom_components/heatpump_optimizer/strings.json` | config.step.device_prefill.data_description.dhw_windows | not measured by this leads seat (no executed number); a D6 sentence for D6-s2's next dispatch. |
| D17-s3 | D0-s1 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer objective under economy band | not measured by this leads seat (no executed number); a D0 band-use question; no null control run here. |
| D17-s3 | D16-s2 | `custom_components/heatpump_optimizer/coordinator.py` | _build_data_dict / boost.adopt_plan | not measured by this leads seat (no executed number); handed to D16-s2. |
| D17-s3 | D1-s3 | `custom_components/heatpump_optimizer/snapshots.py` | SnapshotRing persisted day stamps / drift.stored_instant | not measured by this leads seat (no executed number); pairs with the store._bound_instants lead (D1-s3); handed to its next dispatch. |
| D1-s2 | D1-s3 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._spawn | the instance is D1-s2-06 (boost restore raises in its task every restart); D1-s3's M5 examined its handler universe (C1, C2 examined). |
| D1-s2 | D1-s3 | `custom_components/heatpump_optimizer/store.py` | _bound_instants | not measured by this leads seat (no executed number); D1-s3's report has no entry; handed to its M5 not_reached. |
| D16-s3 | D1-s3 | `custom_components/heatpump_optimizer/coordinator.py` | _await_optimize (WORKER_FALLBACK_CAP, _bump_worker_fallback) | not measured by this leads seat (no executed number); D1-s1-01 holds the worker-fallback repair; the cap's non-retry arm is handed to D1-s3's M5. |
| D1-s3 | D1-s2 | `custom_components/heatpump_optimizer/coordinator.py` | _plausible_forecast_rows / _fetch_weather_forecast | same seam as D1-s2-03 (_fetch_weather accepts any plausible reply as fresh; staleness never judged from the rows' own stamps). |
| D1-s3 | D1-s2 | `custom_components/heatpump_optimizer/accuracy.py` | AccuracyTracker.from_dict / MeasuredCop.from_dict / CurveLearner.from_dict / ComfortLearner.from_dict | D1-s2's M2 row examined the store universe (C1 examined; D1-s2-01 the NaN leaf); the silent per-field resets are within that examined universe. |
| D2-s1 | D2-s2 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalModel.flow_lift_factor / compute_cop_dhw | already found: D2-s2-01 (and D2-s1-01). |
| D12-s2 | D2-s2 | `custom_components/heatpump_optimizer/thermal_model.py` | flow-temperature COP factor (return max(0.25, carnot_ref / carnot_flow)) | already found: D2-s2-01. |
| D2-s1 | D2-s3 | `tests/golden/` | tests/golden.py:capture vs committed fixtures | D2-s3's M3 examined C1/C4 and ran the predicted_cost identity on the goldens (non-finding; one mismatch is D2-s3-01). |
| D4-s3 | D4-s1 | `tests/card_browser.mjs` | p9Grid / instrument().drive 'hover' and 'hoverShared' | not measured by this leads seat (no executed number); an instrument coverage gap; handed to D4-s1's not_reached. |
| D4-s3 | D4-s1 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | dialog tabs (.dlg-tab) focus on open | not measured by this leads seat (no executed number); handed to D4-s1. |
| D4-s3 | D4-s1 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | dialog legend at 375 px | not measured by this leads seat (no executed number); handed to D4-s1. |
| D12-s1 | D4-s1 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | expanded house-temperature chart | consequence of D12-s1-01 (published zone columns on single-zone plants); the card draws what the payload carries. |
| D5-s4 | D5-s1 | `docs/*.md` | reader paths: two-tank storage, ECL110, capacity tariff | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s5 | D5-s1 | `docs/**, README.md` | feature reader paths (two-tank storage, ECL110, capacity tariff) | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s6 | D5-s1 | `docs/ecl110.md, docs/configuration.md, docs/how-it-works.md` | M1 feature reader paths | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s7 | D5-s1 | `docs/{configuration,ecl110,how-it-works}.md` | feature reader paths (two-tank storage, ECL110, capacity tariff) | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s8 | D5-s1 | `docs/configuration.md` | reader path: feature user (two-tank, ECL110, capacity tariff) | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s9 | D5-s1 | `docs/configuration.md` | feature reader paths (two-tank storage, ECL110, capacity tariff) | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s10 | D5-s1 | `docs/**` | M1 feature reader paths | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s4 | D5-s2 | `docs/how-it-works.md, docs/configuration.md, README.md` | mechanism paragraphs (M3); README/docs M4 cell | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s5 | D5-s2 | `docs/how-it-works.md, docs/configuration.md` | mechanism paragraphs | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s6 | D5-s2 | `docs/how-it-works.md, docs/configuration.md` | M3 mechanism paragraphs | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s7 | D5-s2 | `docs/how-it-works.md, docs/configuration.md` | mechanism paragraphs | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s7 | D5-s2 | `README.md, docs/*.md` | D5.M4 cell | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s8 | D5-s2 | `docs/how-it-works.md` | mechanism paragraphs (M3) | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s9 | D5-s2 | `docs/how-it-works.md` | mechanism paragraphs (also docs/configuration.md) | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s10 | D5-s2 | `docs/how-it-works.md, docs/configuration.md, README.md` | M3 mechanism paragraphs; M4 README/docs cell | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11), M4 C5 examined. |
| D5-s5 | D5-s4 | `custom_components/heatpump_optimizer/www/*.js` | comments | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s6 | D5-s4 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | comments | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s7 | D5-s4 | `custom_components/heatpump_optimizer/www/*.js` | comment units | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s8 | D5-s4 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | comment units | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s9 | D5-s4 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | comments | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s10 | D5-s4 | `custom_components/heatpump_optimizer/www/*.js` | M4 comment symbol scan | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s6 | D5-s8 | `tools/policy/policy_lint.mjs` | RECORD_CLASS_RES | same phenomenon as D5-s6-01 (the copied record-class list counted as three regexes over six). |
| D13-s1 | D5-s8 | `tools/policy/policy_lint.mjs` | prClass (comment) | not measured by this leads seat (no executed number); handed to D5-s8. |
| D5-s8 | D5-s6 | `tools/audit/text_ledger.py` | scan_c_like | already found: D5-s8-07 and D5-s4-03. |
| D5-s10 | D11-s1 | `tools/audit/seat/moved_paths.py` | main (tracked = git ls-files) | not measured by this leads seat (no executed number); the raiser's 557 vs 45 is a seat-session number; handed to D11-s1's next dispatch. |
| D11-s2 | D11-s1 | `tools/audit/seat/merge_train.py` | platform_gate | already found: D11-s2-01. |
| D11-s3 | D11-s1 | `tools/policy/policy_lint_mutants.mjs` | CORPUS_CHECK_NAMES / LOOP_CHECK_NAMES enumeration | the consequence is D11-s3-03; an inventory note for D11-s1's M1 row. |
| D13-s3 | D11-s1 | `dev/governance/config/cfr_exclusions.json` | excluded_jobs.record.reason | D13-s3-01 holds the record exclusion; the reason text is not measured further. |
| D13-s3 | D11-s1 | `tools/audit/round4/D11/d11lib.py` | merged_prs / api(paginate=True) | an environment limit of a REST-only session, not a defect of the baseline. |
| D15-s2 | D11-s1 | `dev/governance/dimensions/D15.md` | Method step 6 | a brief correction (no Cusum feeds accuracy_drift); goes to D15.md by finding-propagation. |
| D6-s1 | D2-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._house_heat_loss_scale (driven by tests/rolling.py:run_rolling) | already found: D6-s1-02 (closed-loop learner sentence false: learner diverges, claims.py learner_converges_35pct). |
| D12-s1 | D2-s1 | `custom_components/heatpump_optimizer/thermal_model.py` | flow COP Carnot ratio (line ~3391 of the export) | already found: D2-s1-01 and D2-s2-01. |
| D15-s3 | D2-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _record_accuracy (predicted_power_kw vs actual_power_kw) | not measured by this leads seat (no executed number); live-bundle evidence, not on this tree; handed to D2-s1. |
| D6-s1 | D1-s1 | `custom_components/heatpump_optimizer/pump_arbiter.py` | hold | already found: D6-s1-01 (60 s echo grace not applied, instrumented pump_arbiter:hold). |
| D6-s4 | D6-s3 | `custom_components/heatpump_optimizer/translations/en.json` | options.step.heat_curve.data_description.heat_curve_persistent_writes_per_day | same phenomenon as D6-s4-02 (heat_curve._write_persistent_target keeps no write; the budget text in every language); one finding per mechanism. |
| D6-s4 | D6-s3 | `custom_components/heatpump_optimizer/heat_curve.py` | module docstring (I2) / _write_persistent_target | same phenomenon as D6-s4-02. |
| D6-s6 | D6-s3 | `custom_components/heatpump_optimizer/const.py` | COMBI_TANK_PRESETS['external_station'] | already found: D6-s2-01 and D6-s6-01. |
| D6-s6 | D6-s3 | `custom_components/heatpump_optimizer/wood_fuel.py` | WOOD_KWH_M3['birch'] | already found: D6-s3-02. |
| D6-s6 | D6-s3 | `custom_components/heatpump_optimizer/translations/en.json` | options.step.building.sections.combi/wood data_description | already found: D6-s3-02 (wood en.json) and D6-s2-01 (strings.json, byte-identical to en.json). |
| D6-s7 | D6-s3 | `custom_components/heatpump_optimizer/config_flow.py, const.py` | options flow step count; manual-plan expiry constant | the 20 h expiry holds (D6-s1 non-finding); the '23 options pages' sentence is not in the tree (D6-s7's lead). |
| D6-s4 | D6-s2 | `custom_components/heatpump_optimizer/strings.json` | options.step.heat_curve.data_description.heat_curve_persistent_writes_per_day | same phenomenon as D6-s4-02. |
| D6-s6 | D6-s2 | `custom_components/heatpump_optimizer/strings.json` | options.step.building.sections.combi/wood data_description | already found: D6-s2-01. |
| D17-s3 | D6-s2 | `blueprints/automation/notify_on_manual_plan.yaml` | blueprint description | not measured by this leads seat (no executed number); handed to D6-s2. |
| D6-s4 | D6-s6 | `custom_components/heatpump_optimizer/translations/de.json` | options.step.heat_curve.data_description.heat_curve_persistent_writes_per_day | same phenomenon as D6-s4-02. |
| D6-s4 | D6-s1 | `docs/how-it-works.md, docs/architecture.md, docs/dashboard-card.md, docs/ecl110.md, docs/setup.md, docs/automations.md` | prose claims | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2); remaining behavioural rows are its not_reached. |
| D6-s5 | D6-s1 | `docs/how-it-works.md, docs/architecture.md, docs/dashboard-card.md, docs/ecl110.md, docs/setup.md, docs/automations.md` | prose claims (C2, C3) | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2); remaining behavioural rows are its not_reached. |
| D6-s6 | D6-s1 | `docs/how-it-works.md` | prose claims (C3) | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2); remaining behavioural rows are its not_reached. |
| D6-s7 | D6-s1 | `README.md` | lines 102, 800 ('up to 20 hours'), 922 ('within ±12 %') | measured by D6-s1's non-findings (20 h expiry clamps; +-12 % holds at plant_error 1.0). |
| D6-s7 | D6-s1 | `docs/how-it-works.md, docs/architecture.md, docs/dashboard-card.md, docs/ecl110.md, docs/setup.md, docs/automations.md` | behavioural prose ('the optimizer will ...') | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2); remaining behavioural rows are its not_reached. |
| D6-s7 | D6-s1 | `README.md, docs/index.html` | external links; behavioural claims | D6-s1's coverage rows C4 not_reached, which carries it to the next dispatch. |
| D17-s3 | D6-s1 | `README.md; docs/configuration.md` | Services table / run_optimization paragraph; climate entity paragraph | the behaviour is D17-s3-01; the text fixes ride with it. The comfort-weight sentence is not measured here. |
| D6-s6 | D6-s4 | `custom_components/heatpump_optimizer/translations/sv.json` | combi_potable_volume_l, wood_packing descriptions; quoted labels | D6-s4's non-findings: sv numbers agree key-for-key with en.json, so the two numbers are D6-s2-01/D6-s3-02's mechanism; label quoting not measured. |
| D6-s7 | D11-s2 | `.claude/workflows/web-fix-wave.js` | mergeGroup / mergeChain | already found: D6-s7-02 (driven by wave_red.mjs, merges_after_red=1). |
| D11-s1 | D11-s2 | `dev/governance/decisions/0008-a-seat-identity-distinct-from-the-owner.md` | step 3(d) | not measured by this leads seat (no executed number); a stale-record line for D11-s2's M3 next dispatch. |
| D11-s1 | D11-s2 | `dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md` | What a pin does not reach | not measured by this leads seat (no executed number); a stale-record line for D11-s2's M3 next dispatch. |
| D11-s1 | D11-s2 | `.github/workflows/tests.yml` | coverage-ratchet job comment | the unowned meter is D11-s1-05; the comment is its seam. |
| D11-s3 | D11-s2 | `tools/policy/fixtures/required-contexts.json` | ruleset_objects.23698884.bypass_actors (live ruleset main-protect-checks) | D11-s2-02 holds the provability question (0 of 52 merges carry the owner's approval). |
| D13-s3 | D11-s2 | `tools/ci/selftest_scope.py` | check | already found: D13-s3-02. |
| D7-s1 | D7-s3 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _planned_room / _step_index (and early_cutoff._planned_room) | already found: D7-s3-03. |
| D7-s1 | D7-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalModel._simulate_step_single / _simulate_step_two_zone / simulate_trajectory_batch | already found: D7-s3-08 (behind a valve the scalar model and its batch twin diverge) with D2-s1-02. |
| D7-s1 | D7-s3 | `custom_components/heatpump_optimizer/tariff.py` | _smooth_topk_sum / _smooth_topk_sum_batch / peak_cost_batch | already found: D7-s3-07 and D2-s3-06. |
| D7-s1 | D7-s2 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._apply_comfort_weight | already found: D7-s2-03 (two in-place _opt_config writers). |
| D7-s3 | D3-s3 | `tests/entities.py` | line 9634 `_low, _high = _NOMINAL[_key]` | consequence of the two_zone_mode 'auto' -> on mechanism already found (D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01): the options page hides house_heat_loss_coefficient, so the check aborts/fails on it. |
| D7-s3 | D3-s3 | `tests/` | the behaviour scripts' own verdicts in this tree | the suite going red on the planted export is the gate catching the export's planted production edits; each named line maps to an existing finding (flow_lift_factor D2-s1-01/D2-s2-01, _exact_topk_sum D7-s3-07, emitter_delivery D7-s3-08, declared_modulation D12-s3-01, two_zone auto D7-s3-09, inputs window D1-s2-51, legionella interval D6-s1-01) or is unmeasured here; a red suite is not itself a defect. |
| D7-s3 | D3-s3 | `tests/features.py` | the project_window_mean block (about line 19066) | no suite gap: the raiser reports the 45 and 60 minute neighbours detect the dropped term, and features.py is red on it; the defect is D7-s3-02. |
| D7-s3 | D3-s3 | `tests/env_drift.py` | C2: drift gate, scoped gate (tests/closure.py), stress budgets (tests/stress.py, tests/stress_budgets.json) | not measured by this leads seat (no executed number); round-10 carry C2 for D3-s3; no D3-s3 report was on any box branch. |
| D10-s1 | D3-s3 | `tests/entities.py` | module level, line ~9634 (_NOMINAL[_key]) | consequence of the two_zone_mode 'auto' -> on mechanism already found (D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01): the options page hides house_heat_loss_coefficient, so the check aborts/fails on it. |
| D14-s3 | D3-s3 | `tests/replay.py` | COST_BUDGETS / class_budget (cycle_cost) | contention-provisional (load1 5-12); needs the quiet-window re-take, not a leads-seat number. |
| D8-s3 | D8-s1 | `custom_components/heatpump_optimizer/sensor.py` | _AccumulatingSensor | already found: D8-s3-01 and D10-s2-02. |
| D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._accuracy (process RSS) | measured by D9-s2's non-findings (C4 examined: _accuracy plateaus at 672; ru_maxrss under 128 MB). |
| D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/sensor.py` | every entity's extra_state_attributes | measured by D9-s2's non-finding (B6 payload holds). |
| D9-s1 | D9-s3 | `tests/stress.py` | sweep / per-scenario budgets | already found: D9-s3-02 (stress gate runs no coordinator cycle). |
| D10-s1 | D10-s2 | `custom_components/heatpump_optimizer/quality_scale.yaml` | Gold rows docs-data-update, docs-examples, docs-known-limitations, docs-supported-devices, docs-supported-functions, docs-troubleshooting, docs-use-cases, entity-category, entity-device-class, entity-disabled-by-default | measured by D10-s2's non-findings (Gold docs rules, entity-category, entity-disabled-by-default hold). |
| D10-s1 | D10-s2 | `custom_components/heatpump_optimizer/button.py` | SystemIdentificationButton | the press doing nothing is D10-s1-02; D10-s2's entity-disabled-by-default non-finding examined the shipped defaults. |
| D11-s1 | D11-s3 | `dev/audit/harnesses/` | r10_carry_parser_mutants.py, mutant_run_diff_shards.py, r10_gh_read_retry_mutants.py | not measured by this leads seat (no executed number); inside D11-s3's M4 row (163 not_reached). |
| D11-s1 | D11-s3 | `dev/audit/harnesses/` | mutant drivers editing production in place | not measured by this leads seat (no executed number); handed to D11-s3. |
| D11-s2 | D11-s3 | `dev/governance/decisions/0006-policy-merge-grant-regranted-to-the-local-session.md` | front matter status/superseded-by | not measured by this leads seat (no executed number); a mechanisation candidate for D11-s3's M5. |
| D11-s2 | D11-s3 | `tools/policy/policy_lint.mjs` | cmdStats friction rule id keys | D13-s2-02 holds the friction-entry rule-id defect. |
| D11-s2 | D13-s1 | `dev/audit/rounds/round11/D11/s2/api/conformance_table.txt` | verdict coverage by class | D13-s1-01 holds the verdict-population mismatch; its non-finding reads the window's Fix review lines. |
| D13-s2 | D13-s1 | `tools/policy/policy_lint.mjs` | fetchWindow | measured by D13-s1's non-finding (the single page of 100 truncates no window PR); latent. |
| D12-s1 | D12-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | compressor modulation (line ~1473 of the export) | already found: D12-s3-01. |
| D12-s2 | D12-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | declared_modulation | already found: D12-s3-01 (and D2-s2-03, D17-s1-04). |
| D14-s2 | D14-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._replay_interval (P10) | D14-s1 examined C1 (P10 non-finding: no CPU kernel on the loop in 5 replay arms). |
| D14-s2 | D14-s1 | `dev/audit/config/bugclasses.json` | P8 (currency precedence) | already found: D14-s1-03 (and D14-s3-01). |
| D14-s2 | D14-s1 | `dev/audit/config/bugclasses.json` | N-name-sort, N-step-grid, N-reap-lock | D14-s1 examined C6: N-step-grid D14-s1-01, N-name-sort non-finding; N-reap-lock is D14-s3-02. |
| D15-s1 | D15-s3 | `custom_components/heatpump_optimizer/debugger.py` | DebugCollector.observe | same mechanism as D15-s3-01 (a restart's first publish is a not-run row). |
| D15-s2 | D15-s3 | `custom_components/heatpump_optimizer/debugger.py` | DebugCollector.record / async_close (SAVE_EVERY) | not measured by this leads seat (no executed number); within D15-s3's M8 not_reached (7). |
| D15-s2 | D15-s3 | `custom_components/heatpump_optimizer/sensor.py` | Heat Pump Action power_kw (tests/replay.py:inv_agreement) | synthetic-only by the raiser; the verdict hiding it is D15-s2-05. |
| D15-s1 | D15-s2 | `tools/replay/debug_replay.py` | main --bundle | D15-s2's M5 ran on this bundle (C1, C2 examined). |
| D15-s1 | D15-s2 | `custom_components/heatpump_optimizer/snapshots.py` | SnapshotRing.from_dict | D15-s2's M6 lists C3 examined (drift latch read). |
| D15-s3 | D15-s2 | `tools/replay/debug_replay.py` | run_seeded | already found: D15-s2-02. |
| D15-s2 | D15-s1 | `custom_components/heatpump_optimizer/debugger.py` | the bundle's stores section (privacy gate, D15.M2) | the unmasked-store mechanism is D15-s2-01/D15-s3-03; the privacy ruling goes to the owner directly, never to origin. |
| D15-s2 | D15-s1 | `tools/replay/export.py` | violations (replay_doc rules) as D15's 'Privacy' bar | already found: D15-s1-02. |
| D15-s3 | D15-s1 | `dev/audit/harnesses/d15_restart_gaps.py` | GAP_INTERVALS rule | pairs with D15-s3-01 (not-run first publish); not measured further. |
| D15-s3 | D15-s1 | `custom_components/heatpump_optimizer/store.py` | DOMAINS['off_restore'], DOMAINS['snapshots'], DOMAINS['thermal_learning'] | already found: D15-s1-04 (store.DOMAINS declares less than writers write) and D15-s1-05. |
| D15-s3 | D9-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _maybe_refresh_price_tile | already found: D9-s1-02 (background what-if and price-tile solves stack on the main solve). |
| D16-s1 | D16-s3 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._command_frequency | already found: D16-s3-02 (frequency has no restore owner) and D16-s2-01 (frequency holds the cycle step). |
| D16-s2 | D16-s3 | `custom_components/heatpump_optimizer/pump_arbiter.py` | release / off_restore on unload | measured by D16-s3's non-finding (each written entity returned once at the unload). |
| D16-s1 | D16-s2 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _lead_mode / write_supply | measured by D16-s2's non-finding (cell 3530: partial from idle writes the mode before the switch-on). |
| D16-s3 | D16-s2 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _dhw_target via desired(..., None, ...) | already found: D16-s3-03. |
| D16-s2 | D16-s1 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer.get_current_action | not measured by this leads seat (no executed number); pairs with D16-s1-04; handed to D16-s1. |
| D16-s3 | D16-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._apply_action/_write_supply, _command_frequency, _command_valve_target, _async_drive_pumps, async_publish_current_action (heat_curve.publish) | D16-s3-02 holds the unowned writers; whether they belong to the duty mode is D16-s1's M2 grading, not measured here. |
| D16-s3 | D16-s1 | `tools/audit/enumerate.py` | d16 (hold lines) | not measured by this leads seat (no executed number); an enumerator scope note for D16-s1's next dispatch. |
| D17-s2 | D17-s1 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalParameters.from_config (two_zone_mode) | already found: D17-s2-01. |
| D17-s2 | D17-s1 | `custom_components/heatpump_optimizer/silent_mode.py` | compose / DEFAULT_SILENT_MODE_FRACTION | already found: D17-s2-04 (same mechanism on the options axis). |
| D17-s2 | D17-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _external_heat_config (ExternalHeatConfig enabled) | not measured by this leads seat (no executed number); handed to D17-s1. |
| D17-s2 | D17-s1 | `custom_components/heatpump_optimizer/config_flow.py` | space_setpoint_unit / mixing_valve_write_target_kind | not measured by this leads seat (no executed number); the return-unit write is D6-s2-01's _as_target seam; the rest handed to D17-s1. |
| D17-s3 | D17-s1 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalParameters (from-config two_zone_mode branch, ~line 1121) | already found: D17-s2-01 and D7-s3-09. |
| D0-s2 | D0-s3 | `custom_components/heatpump_optimizer/optimizer.py` | _wood_covered_share (space-only seed scaling) | already found: D0-s2-01 (the charged-wood seed collapse; the raiser's own flat-price arm, 1.678 units, shows it is not a price effect). The census over summer/shoulder/flat is that finding's extent, handed to D0-s3's next dispatch as not_reached. |
| D0-s2 | D0-s3 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalState.wood_tank_temperature | a cell-builder caveat for D0-s3's wood cells, not a defect claim: the plant follows the reading by design. Goes to D0.md (finding-propagation) as a method note; nothing to measure. |
| D0-s3 | D0-s2 | `custom_components/heatpump_optimizer/optimizer.py` | _multi_start_minimize start set (_solve_space) | not measured by this leads seat (no executed number); owner by check_scopes: optimizer.py is a D0 cell; the raiser rules it a comfort-objective seed basin outside D0's price lens. Same start-set mechanism as D0-s2-01 (seeds collapse to an under-heating plan) and D0-s3-02 (no all-off start); handed to D0-s2's next dispatch. |
| D3-s2 | D3-s3 | `tests/closure.py` | select | already found: D3-s2-01 (import-level closures select 9 scripts for a function-body edit none of them executes); the line-level reach is that finding's fix scope. |
| D6-s2 | D3-s3 | `tests/doc_claims.py` | DOCS (module level) | export artefact: the AppleDouble docs/._configuration.md was in the earlier shared export only; the planted export this seat measured holds none (find . -name '._*' prints 0), and it is not in the baseline tree. |
| D6-s3 | D6-s3 | `custom_components/heatpump_optimizer/wood_fuel.py` | export provenance | the dispatch names the planted finder export as the tree under audit and rules it is not diffed against git; the export's differing production files are its planted content, not a baseline defect. Each planted hunk a seat measured is its own finding (e.g. D6-s3-02 birch row). |
| D6-s3 | D5-s6 | `tools/audit/text_ledger.py` | seat_files / units_of over a glob | export artefact: it needs an AppleDouble ._x.py in the tree; the planted export holds none (find . -name '._*' prints 0), and the baseline tree holds none. |
| D9-s2 | D6-s2 | `dev/governance/dimensions/criteria/D9-criteria.md` | B4 retained growth | a criteria method question (warm-up shorter than the bounded structures' fill), not a code defect; D9-s2 already reads B4 with its late-window arm (retained.py --late-from). Goes to D9-criteria.md by finding-propagation. |
| D10-s2 | D6-s1 | `README.md` | Entities / Energy, power and efficiency table | same phenomenon as D10-s2-02 and D8-s3-01 (lifetime energy sensors publish state class measurement): the README sentence describes the intended class and becomes true with that fix. |
| D10-s2 | D10-s2 | `custom_components/heatpump_optimizer/sensor.py` | ThermalBatterySensor / SensorGapAdvisorSensor | not measured by this leads seat (no executed number); the entities.py run dies on the KeyError the two_zone_mode 'auto' mechanism causes (D7-s3-09, D10-s1-04, D12-s2-01, D17-s2-01); the gap advisor's ordering is D8-s1-01's seam. The thermal-battery naming line is handed to D10-s2's next dispatch. |
| D5-s2 | D5-s4 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | comment units | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s3 | D5-s4 | `custom_components/heatpump_optimizer/www/*.js` | C7 (round-10 carry) | D5-s4's D5.M4 row lists C7 examined over 3367 units including www/*.js (findings D5-s4-01, D5-s4-03). |
| D5-s2 | D5-s8 | `tests/card_drift.mjs` | header comment (lines 20-33) | not measured by this leads seat (no executed number); a comment-truth check against closure.is_inert in D5-s8's cells; D5-s8-03 holds closure.py's own stale comments. Handed to D5-s8's next dispatch. |
| D5-s2 | D6-s1 | `README.md` | line 927-962 page table vs docs/configuration.md 337-365 | already found: D5-s2-01 (options-page table twice, 14/24 rows drifted); the three rows' truth is that finding's fix (one home per fact) and D6-s1-01's configuration.md rows. |
| D5-s2 | D6-s1 | `README.md` | 'How it works' prose, line ~880 | not measured by this leads seat (no executed number); an omission (the price-sensor source) rather than a false sentence; handed to D6-s1's not_reached C3 rows. |
| D5-s2 | D6-s1 | `docs/how-it-works.md` | lines 622, 1004, 827-831, 303-305 | already found: D5-s2-08 (legionella 7 vs 10 days, input age 60 vs 360 min, echo grace 60 vs 20 s), D5-s2-09 (smooth start term), D5-s2-10 (DHW presence rule), D5-s2-11 (setup.md menu order); D6-s1-01/02 carry the configuration.md and README truth. |
| D6-s2 | D6-s1 | `docs/how-it-works.md` | prose claims (C3; C1's '23 options pages', '8 weekly snapshots', '+-12 %') | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2; non-findings: 20 h expiry holds, +-12 % holds); remaining behavioural rows are its not_reached. |
| D6-s3 | D6-s1 | `README.md` | README Options / snapshot / ECL110 sections | D6-s1's coverage lists C1 examined (non-findings: 20 h expiry holds, +-12 % holds); the two unlocated sentences are its not_reached. |
| D6-s3 | D6-s1 | `docs/how-it-works.md` | prose claims in how-it-works.md, architecture.md, dashboard-card.md, ecl110.md, setup.md, automations.md | D6-s1's coverage lists C1, C2 and C3 examined (D6.M1/M2); remaining behavioural rows are its not_reached. |
| D5-s2 | D5-s1 | `docs/CONTRIBUTING.md` | inbound links | already found: D5-s2-02 (docs/CONTRIBUTING.md is linked from no other document). |
| D5-s3 | D5-s1 | `docs/how-it-works.md, docs/configuration.md, docs/ecl110.md` | C2 (round-10 carry) | D5-s1's D5.M1 row lists C2 examined over its 27 cells (D5-s1-01 two-tank path; capacity-tariff non-finding). |
| D5-s2 | D5-s6 | `tools/audit/text_ledger.py` | run_check --plant | already found: D5-s2-07 (check --plant always fails for D5-s2); the .md self-test arm is that finding's fix scope. |
| D5-s3 | D5-s6 | `tools/audit/text_ledger.py` | py_units | not measured by this leads seat (no executed number); an instrument unit-split defect in D5-s6's cells, same family as D5-s4-03/D5-s8-07 (text_ledger line drift); a tracked tooling fix is frozen mid-round, so it goes to D5-s6's next dispatch and the round-end proposal. |
| D5-s3 | D5-s2 | `docs/how-it-works.md, docs/configuration.md` | C3 (round-10 carry) | D5-s2's coverage lists C3 examined (M2) and its M3 universe of 3265 README/docs units examined (D5-s2-08..11). |
| D5-s3 | D5-s2 | `README.md, docs/*.md` | C7 (round-10 carry) | D5-s2's coverage lists its README/docs M4 cell examined (C5, D5-s2-05/06). |
| D5-s3 | D6-s3 | `custom_components/heatpump_optimizer/grid_fee.py` | IMPLAUSIBLE_FEE_SEK_PER_KWH comment | not measured by this leads seat (no executed number); a claim about real-world tariffs in every Tibber currency; no tree behaviour decides it, and D14-s1-03/D14-s3-01 already hold the fee bound's currency handling. |
| D6-s2 | D2-s1 | `custom_components/heatpump_optimizer/wood_fuel.py` | WOOD_KWH_M3['birch'] | already found: D6-s3-02 and D6-s2-01 (probes.py --probe wood_packing_ratio perturbs the production row: loose/packed 1.667 -> 0.600). |
| D6-s2 | D2-s1 | `custom_components/heatpump_optimizer/const.py` | COMBI_TANK_PRESETS['external_station'] | already found: D6-s2-01 (probes.py --probe station_potable perturbs the production preset) and D6-s6-01. |
| D6-s2 | D1-s1 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _arbitrate | already found: D6-s2-01, whose perturbation is the production edit in _arbitrate ('if mode != DUTY_CONTROL or _pump_off: return'; probes.py --probe observe_writes: one _command, one _adopt and one night-schedule write per observe pass). D16-s1's writer-gating lead names the same seam. |
| D6-s2 | D1-s1 | `custom_components/heatpump_optimizer/pump_arbiter.py` | _as_target | already found: D6-s2-01, whose perturbation is the production edit in _as_target ('supply_c - RETURN_SUPPLY_OFFSET_K'; probes.py --probe return_gate: gate 30 degC, W35 hold 40). |
| D6-s2 | D8-s1 | `custom_components/heatpump_optimizer/const.py` | FLOW_UNIT_TO_KG_S['L/min'] | already found: D6-s2-01, whose perturbation is the production row ('L/min': WATER_KG_PER_L/60.0; probes.py --probe flow_unit_lmin: 10 L/min x 5 K reads 0.058 kW, physical 3.48). |
| D9-s3 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._async_update_data | D9-s2's coverage measured retained_bytes over 1,100 real _async_update_data cycles (_drive.py, per-file tracemalloc slope after warm-up) with no coordinator finding; the 5-9 kB/cycle over cycles 2-4 is pre-warm-up fill. |
| D9-s2 | D9-s1 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer.optimize (GIL yields) | D9-s1's non-findings carry the quiet-window re-take (cycle.process.longest_gil_hold_ms_median 5.82 at load1 1.9; in-process 11.4/7.3 ms) and the _gil_yield arm (inert). |
| D9-s2 | D9-s1 | `custom_components/heatpump_optimizer/coordinator.py` | shadow/what-if solve (~line 11148), async_diagnose_interval | already found: D9-s1-01 (diagnose press re-solves), D9-s1-02 (background what-ifs stack on the main solve), D9-s1-03 (user what-ifs queue 3 solves). |
| D9-s2 | D9-s1 | `custom_components/heatpump_optimizer/dhw_planner.py` | DHW planning loops | D9-s1's non-finding C3: the DHW planner makes 0 model calls; the _co_optimize/_commit_runs re-solves gradient at <=97 rows. |
| D9-s2 | D9-s1 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | HistorySource.overlays | not measured by this leads seat (no executed number); the CPU face of D9-s2-01 (HistorySource never trims); its fix (trim past HISTORY_SPAN_MS) bounds the overlay rebuild too. Handed to D9-s1's next dispatch. |
| D10-s2 | D10-s1 | `custom_components/heatpump_optimizer/config_flow.py` | HeatPumpOptimizerConfigFlow.async_step_reauth_confirm | not measured by this leads seat (no executed number); the reauth face of D10-s2-01 (entry.options shadows entry.data after an Options save); same mechanism and fix seam, handed to D10-s1's next dispatch. |
| D10-s2 | D10-s1 | `custom_components/heatpump_optimizer/config_flow.py` | HeatPumpOptimizerOptionsFlow._save_or_menu / _omit_unstored_defaults | consequence of the two_zone_mode 'auto' -> on mechanism already found (D7-s3-09, D10-s1-04, D12-s1-02, D12-s2-01, D17-s2-01): an untouched save reads the forced two-zone state. |
| D10-s3 | D10-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator | already found: D10-s3-02 (coordinator has no config_entry annotation); the runtime-data row's done is that finding's other register row. |
| D10-s3 | D10-s1 | `custom_components/heatpump_optimizer/` | mypy --strict (D10.M3) | D10-s1's coverage lists M3 examined: mypy_strict.py ran mypy --strict over the whole package by code, ruler and hastub arms. |

## Exposure

Read the owner seats' REPORT.json files on the box evidence branches (as the task directs); read no GitHub issue or PR. `docs/` was not read for measurement.
