# Round 9, batch 1 — leads seat L1

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, machine B10 cloud container. L1 set: the 34 leads of `leads_L1.json` (D0, D1, D2, D3, D5 owners and two orchestrator-carried D1-s1 leads) plus the carried INPUT_MAX_AGE lead (#110). Leads outside L1 that were measured before the orchestrator split are listed separately and marked.

## Method

Each lead was checked against its owner's round-9 report first; a lead the owner already measured is closed by that entry. A lead is converted only on an executed number under `tools/audit/briefs/COMMON.md`: a harness under `tools/audit/round9/<dim>/leads/`, the instrumented symbol, an in-memory perturbation, a stated count key, a null control, and the `thread_factor`/`load1`/`swapins` tail. Owners D3-s2, D3-s3 and D7-s1 are deferred to the catch-up batch. No heavy D3 script was re-run (tvofi's rule of 2026-09-26). Every harness runs as `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python <harness>`; the shared rig is `D1/leads/_rig.py`.

## Findings

| id | severity | class | title | value | harness |
|---|---|---|---|---|---|
| D1-s1-51 | low | P11 | hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file | 6 | `tools/audit/round9/D1/leads/stub_store_codec.py` |
| D1-s1-52 | low | P11 | hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted | 6 | `tools/audit/round9/D1/leads/stub_naive_clock.py` |
| D1-s2-51 | medium | new | A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves | quiet_solve_failed=3/3 (plan published 3/3); arbiter_cycles_failed=3/3, arbiter_skipped_steps=15/15 | `tools/audit/round9/D1/leads/cycle_fence.py` |
| D1-s2-52 | medium | new | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state | 5 | `tools/audit/round9/D1/leads/startup_clobber.py` |
| D1-s2-53 | medium | new | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) | 24 | `tools/audit/round9/D1/leads/runtime_params_restart.py` |
| D1-s2-54 | low | new | apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps, the invariant it states is unenforced | free_at_apply=0, free_at_23h=0 | `tools/audit/round9/D1/leads/manual_plan_expiry.py` |
| D1-s2-55 | medium | new | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice | planned=0/3, fallback_notice=0 | `tools/audit/round9/D1/leads/worker_spawn.py` |
| D1-s5-51 | medium | new | A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable while HA holds its valid reading | 4 of 7 | `tools/audit/round9/D1/leads/indoor_silence.py` |
| D1-s5-52 | medium | new | InputReader has no plausibility window: -127 and 85 degC sensor sentinels are delivered as ok on 6 of 6 temperature inputs | 12 | `tools/audit/round9/D1/leads/sentinel_temps.py` |
| D2-s1-51 | low | P6 | DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped | 14 | `tools/audit/round9/D2/leads/dhw_sweep_outdoor.py` |
| D5-s2-51 | low | I5 | Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash) | handed_offset_steps=0 vs elapsed_steps=2; model_sequence_writes=0 | `tools/audit/round9/D5/leads/dataflow_comments.py` |
| D7-s3-51 | low | new | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed | swallowed=2 of 2; syntax_warnings=1 | `tools/audit/round9/D7/leads/nightly_finally_return.py` |

### INPUT_MAX_AGE (#110): is the 60-minute guard too eager?

D1 side, measured (`D1/leads/indoor_silence.py`): with the thermometer state valid in Home Assistant, Indoor Temperature is unavailable in 4 of 7 silence cells, which are every silence of 61 minutes or more (61/90/240/480 min). A thermometer that re-writes an unchanged value, so that only `last_reported` moves, stays available (`rereport_unavailable=0 of 1`). The guard is therefore too eager for thermometers that report only on change, which contradicts the intent stated in `const.py` that a healthy sensor never trips it. Setting `--scale 8` or `--no-watchdog` brings it to 0. How often real devices go more than 60 minutes between reports could not be measured here, because there is no corpus of device report intervals. The field evidence is the reported gaps in the stable hours. This is a different mechanism from D1-s5-01. The D4 side (the card cannot draw the raw thermometer through the gap, because the sensor publishes no source-entity attribute) is recorded as a closed lead routed to the D4 owner.

## Non-findings

- D1-s4 gains NaN (L1 #11): nonfinite=0/4 (control: --raw 4/4) — `tools/audit/round9/D1/leads/gains_nan_probe.py`
- D1-s4 forecast non-finite (L1 #13): failed_arms=0/7 (control: -1e308 positive control fails) — `tools/audit/round9/D1/leads/forecast_nonfinite.py`
- harness ha_unload_entry dropped coroutine (L3 #2): dropped=1, raised_when_run=0 (control: n/a) — `tools/audit/round9/D1/leads/unload_coroutines.py`
- legionella default repair (L1 #16): stock pair excluded in legionella.py (control: reasoned from code)

## Converted — L1 set

| raised_by | file | symbol | finding |
|---|---|---|---|
| D1-s1 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator.async_run_optimization (:5096 _record_quiet_comfort_period) | D1-s2-51 |
| D1-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _async_save_ledger / _async_save_thermal_learning / _async_save_price_model / _async_save_energy_totals | D1-s2-52 |
| D1-s3 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator._apply_action | D1-s2-51 |
| D6-s1 | `custom_components/heatpump_optimizer/services.py` | handle_apply_manual_plan | D1-s2-54 |
| D14-s4 | `custom_components/heatpump_optimizer/coordinator.py` | _run_in_process / _ensure_worker | D1-s2-55 |
| D1-s1 | `custom_components/heatpump_optimizer/inputs.py` | input reader (problem codes) | D1-s5-52 |
| D8-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _dhw_setpoint_sweep | D2-s1-51 |
| D7-s2 | `custom_components/heatpump_optimizer/optimizer.py` | OptimizationResult.buffer_temp_trajectory | D5-s2-51 |
| D1-s1 | `custom_components/heatpump_optimizer/` | set_thermal_parameters | D1-s2-53 |
| D1-s1 | `custom_components/heatpump_optimizer/` | async_reset_comfort_weight and the cycle-end save | D1-s2-52 |
| orchestrator (#110) | `custom_components/heatpump_optimizer/inputs.py` | INPUT_MAX_AGE_MINUTES age gate (Indoor Temperature unavailable after 60 min) | D1-s5-51 |

## Closed — L1 set

| raised_by | file | symbol | why |
|---|---|---|---|
| D0-s1 | `tests/optimality.py` | score_plan / pin_result | owner deferred to catch-up batch; re-route then (owner D3-s3) |
| D0-s1 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._solve_space / _co_optimize | closed by D0-s3 non-finding (M6/M7 measured by the owner: step 0 moves 1.197->1.200 kW in the largest cell, none in the other two); D0-s1 non-finding (horizon not reachable) |
| D0-s2 | `custom_components/heatpump_optimizer/optimizer.py` | _multi_start_minimize | closed by D0-s3 non-finding M6/M7 (receding-horizon realisation measured by the owner) and D0-s2-01/02, which carry the step-0 change |
| D0-s2 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._terminal_cost | closed by D0-s3 non-finding M7 (terminal-credit share at 6 h measured by the owner) |
| D0-s3 | `custom_components/heatpump_optimizer/optimizer.py` | _multi_start_minimize / HeatPumpOptimizer._solve_space seed set | closed by D0-s1 non-finding: two-zone winter grid gap within 0.54 %, step 0 unchanged |
| D0-s3 | `custom_components/heatpump_optimizer/optimizer.py` | _multi_start_minimize seed set | closed by D0-s2-02 (same seed-set gap on shoulder/summer_negative cells) |
| D1-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _async_update_data (:4677 _async_watch_learning_drift guard); _async_load_accuracy (:7270-7283) | closed by D1-s2 non-finding M2 (owner measured the from_dict chain: no sibling store lost at this baseline); the DEBUG heartbeat log is the documented guard level |
| D1-s3 | `custom_components/heatpump_optimizer/services.py` | SERVICE_SCHEMA_SET_AWAY | closed by D1-s3-01 (tz-less return_time reaching the coordinator is that finding's mechanism) |
| D1-s4 | `custom_components/heatpump_optimizer/coordinator.py` | thermal-learning load of internal_gains_profile (~3018-3023) and _learn_internal_gains (~8550) | non-finding by measurement: gains_nan_probe.py nonfinite=0/4 (QuarantiningStore._sanitize scrubs "nan"/"inf" strings before float()); --raw bypass control 4/4 |
| D1-s4 | `custom_components/heatpump_optimizer/coordinator.py` | _shutdown_process_pool / _run_in_process | closed by D1-s2-05 (shutdown waits on _PROCESS_LOCK held across the solve) |
| D1-s4 | `custom_components/heatpump_optimizer/coordinator.py` | _forecast_arrays | non-finding by measurement: forecast_nonfinite.py failed_arms=0/7 at the coordinator boundary; positive control -1e308 fails (finite-absurd class is D1-s4-owned) |
| D1-s5 | `custom_components/heatpump_optimizer/coordinator.py` | HeatPumpOptimizerCoordinator (price_sensor attributes at ~6992, peak_threshold_kw) | closed by D1-s5-02 (negative threshold from a corrupt peak store is that finding's producer; publishing is its downstream) |
| D1-s5 | `custom_components/heatpump_optimizer/coordinator.py` | solar_radiation horizon build from OpenMeteoSolar.irradiance_for | closed by D1-s5-04: all-None irradiance falls back to the weather entity, else 0.0 (coordinator.py:6159), logged at DEBUG |
| D4-s2 | `custom_components/heatpump_optimizer/coordinator.py` | dhw_legionella_above_setpoint repair (config_flow._dhw_legionella_warning judgement) | non-finding: the shipped 55/60 default pair is excluded as "stock" in legionella.py, so a fresh default install raises no repair |
| D8-s1 | `custom_components/heatpump_optimizer/coordinator.py` | _get_current_price / _current_spot_price | closed by D2-s3-01 (hour-window pricing under quarter-hour prices) |
| D1-s1 | `custom_components/heatpump_optimizer/dhw_draws.py` | DrawStats.fold / from_dict | closed by D1-s1-03 (unbounded DrawStats energy is that finding) |
| D1-s2 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalModel._stability_substeps | closed by D1-s2-02 (runaway wind-driven substeps) |
| D1-s2 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer.optimize | closed by D1-s2-02 (non-physical finite forecast accepted); owner-side D1-s4 guard scope |
| D1-s5 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._stash_price_horizon | inf sigma unreachable: QuarantiningStore._sanitize scrubs non-finite residual_var before from_dict; finite-absurd variance is D1-s5-02; price_risk_lambda defaults to 0 |
| D1-s2 | `custom_components/heatpump_optimizer/store.py` | QuarantiningStore._sanitize | closed by D1-s2-03 (>= 2**64 counts through the loader int()) |
| D2-s1 | `custom_components/heatpump_optimizer/sysid.py` | identify / heat-loss learner (house_heat_loss_scale) | closed as seam of D2-s1-01: the learned scale enters the same diagonal the substep count already includes |
| D2-s4 | `custom_components/heatpump_optimizer/thermal_model.py` | ThermalModel.simulate_step | closed by D2-s1 non-finding (dt invariance measured by the owner) |
| D8-s1 | `custom_components/heatpump_optimizer/battery.py` | VirtualBattery / label_measured | closed by D12-s1-01 (unmodelled constant tank default) and the #282 disclosure decision |
| D6-s2 | `docs/configuration.md` | lines 181-187 (setup hot-water table) | closed by D5-s1-02 (configuration.md table split) |
| orchestrator (#110, D4 framing) | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | IndoorTempSensor source-id attribute / card _entityIds indoor derivation | D4 (card): route to D4 owner. The D4 side stands structurally: IndoorTempSensor publishes no source-entity attribute (sensor.py:636-661 defines no extra_state_attributes) and the card derives its indoor trace only from *_indoor_temperature_optimizer (card.js:4749-4775), so it cannot draw the raw thermometer through the stale gap; not measured by L1 |

## Outside L1, measured before the split

| raised_by | file | symbol | finding / why |
|---|---|---|---|
| D1-s1 | `tests/hastub/homeassistant/helpers/storage.py` | Store.async_save/async_load | D1-s1-51 |
| D1-s2 | `tests/hastub/homeassistant/helpers/storage.py` | Store.async_load | D1-s1-51 |
| D1-s4 | `tests/hastub/homeassistant/helpers/storage.py` | Store.async_save/async_load | D1-s1-51 |
| D1-s3 | `tests/hastub/homeassistant/util/dt.py` | now | D1-s1-52 |
| D14-s1 | `tests/hastub/homeassistant/util/dt.py` | now | D1-s1-52 |
| D7-s3 | `tests/nightly_ha.py` | line 1274 (return inside finally, A4 recovery block) | D7-s3-51 |
| D0-s3 | `custom_components/heatpump_optimizer/optimizer.py` | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | D5-s2-51 |
| D1-s2 | `tests/harness.py` | ha_unload_entry | non-finding by measurement: unload_coroutines.py dropped=1, raised_when_run=0 (the dropped async_shutdown coroutine has no effect the harness can observe) |

## Harnesses

- `tools/audit/round9/D1/leads/_rig.py`
- `tools/audit/round9/D1/leads/cycle_fence.py`
- `tools/audit/round9/D1/leads/forecast_nonfinite.py`
- `tools/audit/round9/D1/leads/gains_nan_probe.py`
- `tools/audit/round9/D1/leads/indoor_silence.py`
- `tools/audit/round9/D1/leads/manual_plan_expiry.py`
- `tools/audit/round9/D1/leads/runtime_params_restart.py`
- `tools/audit/round9/D1/leads/sentinel_temps.py`
- `tools/audit/round9/D1/leads/startup_clobber.py`
- `tools/audit/round9/D1/leads/stub_naive_clock.py`
- `tools/audit/round9/D1/leads/stub_store_codec.py`
- `tools/audit/round9/D1/leads/unload_coroutines.py`
- `tools/audit/round9/D1/leads/worker_spawn.py`
- `tools/audit/round9/D2/leads/dhw_sweep_outdoor.py`
- `tools/audit/round9/D5/leads/dataflow_comments.py`
- `tools/audit/round9/D7/leads/nightly_finally_return.py`
