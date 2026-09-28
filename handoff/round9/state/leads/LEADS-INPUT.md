# Round 9 leads seat: what it is working on

Batch 1. 109 leads raised by 39 finder seats outside their own cells, plus 1 carried from the card-history fix (#1643): 110 in all. The leads seat reads each owner seat's report first. A lead the owner already measured is closed. Any other lead becomes a finding only with an executed number from a harness. Leads owned by the three deferred seats (D3-s2, D3-s3, D7-s1) wait for the catch-up batch.

Status as of 11:50Z: the seat has built a digest of all reports and started its first harnesses (D1 cycle fence). Per-lead outcomes will be listed here when it returns.

| Owner area | Leads |
|---|---|
| D0 | 5 |
| D1 | 20 |
| D2 | 4 |
| D3 | 1 |
| D4 | 4 |
| D5 | 2 |
| D6 | 5 |
| D7 | 2 |
| D8 | 5 |
| D9 | 7 |
| D10 | 3 |
| D11 | 7 |
| D12 | 1 |
| unknown | 43 |
| carried (#1643) | 1 |

## D0 (5)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D0-s3 | D0-s1 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._solve_space / _co_optimize | M6: does MPC re-planning mask finding D0-s1-01? Step-0 power moves only 1.197 -> 1.200 kW in the largest cell and not at all in the other two. M7: the co-optimisation re-solve is handed a single warm-start candidate. |
| 2 | D0-s3 | D0-s2 | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize | D0-s2-01 and D0-s2-02 change step 0 in some cells (two\|nodhw\|shoulder\|winter_cold 1.52->0.89 kW; 48 h two\|dhw\|summer_typical\|winter_cold 0.99->0.93 kW); M6 receding-horizon realisation unmeasured. |
| 3 | D0-s3 | D0-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | At 6 h horizon 36 of 64 cells plan 0 kWh space heating; the terminal credit alone decides the plan (M7). |
| 4 | D0-s1 | D0-s3 | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / HeatPumpOptimizer._solve_space seed set | Two-zone winter cells: the race challenger finds 0.3-0.45 % lower objective (e.g. two\|1\|winter_moderate\|winter_cold 0.447 %, two\|0\|winter_typical\|winter_cold 0.350 %) from bang-bang seeds at 0.5x/0.75x/1.5x energy or a tight-ftol warm restart, usually with step 0 unchanged. race.py output in t |
| 5 | D0-s2 | D0-s3 | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize seed set | shoulder/summer_negative single-zone cells: gaps of 0.9-2.8 % (shoulder) and up to 16 % relative (summer_negative, absolute 0.05 units on a near-zero bill); the winning seeds are 0.1-1.25x bang-bang. Most spend more money than production. out/race_one.log |

## D1 (20)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D1-s2 | D1-s1 | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator.async_run_optimization (:5096 _record_quiet_comfort_period) | The learner feed is unguarded inside the solve's except-Exception: any learner raise is logged as 'Optimization failed', bumps _solve_failures (towards the solve_failures repair issue) and skips _command_valve_target. |
| 2 | D1-s2 | D1-s1 | custom_components/heatpump_optimizer/coordinator.py | _async_update_data (:4677 _async_watch_learning_drift guard); _async_load_accuracy (:7270-7283) | The heartbeat guard logs a permanent failure at DEBUG on every cycle. _async_load_accuracy runs its from_dict calls outside the try, so one raising parser aborts the rest of that store's load (dhw_accuracy, defrost, peaks, mode, comfort) in a fire-and-forget task. |
| 3 | D1-s2 | D1-s1 | custom_components/heatpump_optimizer/coordinator.py | _async_save_ledger / _async_save_thermal_learning / _async_save_price_model / _async_save_energy_totals | Only the accuracy store's writer awaits QuarantiningStore.async_wait_for_read (:5153). The other stores' writers do not, although the loads are spawned fire-and-forget in __init__ (write-before-read clobber class, R6). |
| 4 | D1-s2 | D1-s3 | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._apply_action | pump_arbiter.apply is awaited unfenced, while _command_frequency, _async_drive_pumps and the drift watch are fenced. Any arbiter exception (see D1-s3-01/03) fails the whole _async_update_data with an ERROR traceback on every poll and skips frequency, pumps, accuracy and energy saves. |
| 5 | D1-s2 | D1-s3 | custom_components/heatpump_optimizer/services.py | SERVICE_SCHEMA_SET_AWAY | return_time is vol.Any(None, cv.string) with no datetime or awareness validation, so the card's tz-less datetime-local value reaches the coordinator unchecked (D1-s3-01). |
| 6 | D1-s2 | D1-s4 | custom_components/heatpump_optimizer/coordinator.py | thermal-learning load of internal_gains_profile (~3018-3023) and _learn_internal_gains (~8550) | [float(g) for g in raw_gains] admits the strings 'nan'/'inf'; np.clip keeps NaN, so it never washes out. Handed to ThermalModel.internal_gains_at (unguarded float()), a NaN profile makes every optimizer start non-finite: a scratch probe gave status 'failed (no usable starting point)' with non-finite |
| 7 | D1-s2 | D1-s4 | custom_components/heatpump_optimizer/coordinator.py | _shutdown_process_pool / _run_in_process | _run_in_process holds _PROCESS_LOCK for the whole solve and pickle.load has no timeout; _shutdown_process_pool takes the same lock before it can terminate the worker, so HA stop waits out an in-flight (or hung) solve on the executor. |
| 8 | D1-s2 | D1-s4 | custom_components/heatpump_optimizer/coordinator.py | _forecast_arrays | The optimizer has no input guard: one nan/inf step in prices, outdoor, solar (and -inf wind) yields a 'failed' plan, nan/inf wind raises ValueError/OverflowError at an int() cast (solve_guard.py second section: 9 failed, 2 raised of 15). Worth confirming every non-finite forecast value is neutralise |
| 9 | D1-s2 | D1-s5 | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator (price_sensor attributes at ~6992, peak_threshold_kw) | Publishes peak_threshold_kw as round(threshold_kw, 2) with no sign check. A negative threshold loaded from a corrupt peak store (D1-s5-02) is published as-is. |
| 10 | D1-s2 | D1-s5 | custom_components/heatpump_optimizer/coordinator.py | solar_radiation horizon build from OpenMeteoSolar.irradiance_for | Not measured: what the plan uses when irradiance_for returns None for every step (D1-s5-04) — zero solar, the weather entity, or something else — and whether that is logged. |
| 11 | D1-s2 | D4-s2 | custom_components/heatpump_optimizer/coordinator.py | dhw_legionella_above_setpoint repair (config_flow._dhw_legionella_warning judgement) | The shipped defaults (DEFAULT_DHW_LEGIONELLA_TEMP 60 > DEFAULT_DHW_SETPOINT 55, legionella on) trip the legionella-above-setpoint judgement on every default submit of the dhw page (config_flow logs it in every expert-path walk here); config_flow's comment says the coordinator turns it into the repai |
| 12 | D1-s2 | D6-s1 | custom_components/heatpump_optimizer/services.py | handle_apply_manual_plan | expires_at is accepted unbounded, which breaks the invariant stated at const.py:MANUAL_PLAN_WINDOW_HOURS (the override must be shorter than the 24 h horizon, or re-applying switches the optimizer off while appearing to leave it on). With space_slots=[] and expires_at=now+48h, all 96 steps are pinned |
| 13 | D1-s2 | D8-s1 | custom_components/heatpump_optimizer/coordinator.py | _get_current_price / _current_spot_price | The same 1 h window prices the settlement's pending dict and the comfort learner's relative price. With quarter-hour prices, booked costs (lifetime cost accumulators, ledger) would use a quarter up to 45 min old. |
| 14 | D1-s2 | D14-s4 | custom_components/heatpump_optimizer/coordinator.py | _run_in_process / _ensure_worker | _ensure_worker() (subprocess.Popen) is called outside _run_in_process's try, so a spawn OSError escapes as OSError, not ProcessWorkerUnavailable; _await_optimize catches only the latter, so a worker that cannot START gets neither the in-process fallback nor the solve_worker_fallback repair notice (s |
| 15 | D1-s3 | D1-s1 | custom_components/heatpump_optimizer/dhw_draws.py | DrawStats.fold / from_dict | No physical bound on the energy of one occurrence: it accepts 231757 kWh (see D1-s1-03's harness). |
| 16 | D1-s5 | D1-s1 | custom_components/heatpump_optimizer/inputs.py | input reader (problem codes) | No plausibility range for temperature readings, so the DS18B20 sentinel values -127 and 85 pass as ok readings to every learner. |
| 17 | D1-s4 | D1-s2 | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._stability_substeps | Substep count grows without bound with the wind-driven heat loss: one forecast step at wind 1e12 m/s makes a solve run past 60 s (1e6 finishes in 0.9 s). A cap on n_sub (or on the wind it is computed from) would bound a runaway solve whatever the coordinator passes (see D1-s2-02). |
| 18 | D1-s4 | D1-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | A single outdoor-temperature step at -1e308 yields status 'failed (no usable starting point)' rather than a clamped or refused input; the optimizer accepts non-physical but finite forecast series. |
| 19 | D1-s4 | D1-s5 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._stash_price_horizon | Clips sigma at 0 from below but not from above or for inf. price_model.from_dict turns an inf residual_var into inf through max(0.0, v), so sigma is inf and with price_risk_lambda > 0 the unpublished prices become inf. Not hit by this seat's fuzz sample; unmeasured. |
| 20 | D1-s1 | D1-s2 | custom_components/heatpump_optimizer/store.py | QuarantiningStore._sanitize | Scrubs non-finite leaves but passes finite values that become unrepresentable after the loader's int() (>= 2**64 floats); the store boundary could refuse counts beyond int64 for every store at once (see D1-s2-03). |

## D2 (4)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D2-s4 | D2-s1 | custom_components/heatpump_optimizer/sysid.py | identify / heat-loss learner (house_heat_loss_scale) | Check whether learned masses or house_heat_loss_scale can move a configuration into the D2-s1-01 divergence region (a diagonal ratio near 1.5/h on two coupled stores). |
| 2 | D2-s1 | D2-s4 | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.simulate_step | dt-dependence on light_new: peak room rise of the same 2 h heat pulse is 1.5271 K at dt 0.5 h, 1.5104 at 0.25, 1.4991 at 0.05 (1.9 %); enough to push a sysid step sized at 0.25 h over the 0.8 K abort bound when the plant runs at the 0.5 h cadence. |
| 3 | D2-s1 | D8-s1 | custom_components/heatpump_optimizer/coordinator.py | _dhw_setpoint_sweep | It prices candidate setpoints at ctx._current_state.outdoor_temperature, which is the 5.0 C ThermalState default without an outdoor thermometer. _effective_outdoor / forecast_outdoor_now exist for exactly this case. |
| 4 | D2-s1 | D8-s1 | custom_components/heatpump_optimizer/battery.py | VirtualBattery / label_measured | On a DHW install without a tank probe, Thermal Battery charge/energy include the dhw_tank at the constant 55.0 C constructor default across cycles. It is disclosed as 'modelled' but not modelled. |

## D3 (1)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D3-s3 | D0-s1 | tests/optimality.py | score_plan / pin_result | The pin 'the plan holds the comfort floor' reads the room series even for two-zone houses, but the objective's floor is on the upper and lower zones. On two-zone DHW-on winter_typical/winter_cold the shipped upper zone reaches 16.53 C (1.34 degree-steps below 17) while room stays at or above 17.57,  |

## D4 (4)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D4-s2 | D5-s1 | custom_components/heatpump_optimizer/translations/en.json | config.step.quick_setup.data_description.buffer_tank / wood_buffer_tank | The Quick setup form itself promises 'On stores cheap heat' and two-tank physics once a probe is assigned. quick_setup.derive never sets a throttling mixing valve, so neither buffer_is_store nor two_tank_modelled comes on (see D5-s1-02's harness). |
| 2 | D4-s2 | D6-s2 | custom_components/heatpump_optimizer/strings.json | options ... data_description.curve_learning_enabled (line 1333) | 'at most half a degree per week' -- same figure as D6-s2-03 |
| 3 | D4-s2 | D12-s1 | custom_components/heatpump_optimizer/config_flow.py | HeatPumpOptimizerConfigFlow.async_step_dhw | The full wizard's DHW page offers only defaulted optional fields and no 'no tank' answer. 'Continue setup' therefore always stores dhw_tank_volume and dhw_windows and turns hot-water planning on (phantom_dhw.py wizard_dhw_step seam: 9 DHW steps, 3.16 kWh planned). |
| 4 | D4-s1 | D14-s4 | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | slot-hit rect (TARGET_MIN_PX_COARSE) | Under the card's own coarse-pointer floor (44 px) a dialog slot target measures 31.3 x 44.5 px at 359 px; the code documents this as the boxed-in exception (>=24 px), but whether 44 px is meant to bind slot widths on touch is D4's call. |

## D5 (2)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D5-s1 | D6-s2 | docs/configuration.md | lines 181-187 (setup hot-water table) | A paragraph splits the table; the three anti-legionella rows follow it with no header and render as literal pipe text |
| 2 | D5-s2 | D7-s2 | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.buffer_temp_trajectory | Comment says 'the model stashes the series on itself for the terminal-cost term'; no such stash exists at this baseline (_terminal_cost takes buffer_temps as an argument). |

## D6 (5)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D6-s1 | D5-s1 | README.md | Entities: 'Nineteen entities (eighteen sensors and the wood binary sensor) are disabled by default' | README:600 says DHW Boost is also disabled by default without hot water. The disabled-by-default list sits under Sensors but names a binary sensor. Verify the 19 against registry_default. |
| 2 | D6-s1 | D6-s2 | README.md | line 44 | Carries the same 'at most 0.5 K per week' curve-bias claim D6-s2-03 measured false (0.6 K in 7 days) |
| 3 | D6-s2 | D5-s1 | docs/setup.md | 'the original eleven-page wizard'; 'Quick setup arrived in v6.6.5' | Page count and release version are unverified against config_flow steps and RELEASE_NOTES.md. |
| 4 | D6-s2 | D5-s1 | docs/ecl110.md | ## Sensors: 'on an install whose topics were configured at setup they are enabled' | Setup has not offered the ECL110 topics since v4.1.0 (the same doc says so). The enable condition as written can only describe legacy entries. README:549-550 carries the same wording (D6-s1). |
| 5 | D6-s2 | D5-s1 | docs/configuration.md | Services table: simulate_plan '16 optional comfort and wood fields' | The count is right, but the paragraph lists 11. The claim-level half of D5-s1-06. |

## D7 (2)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D7-s2 | D5-s2 | custom_components/heatpump_optimizer/thermal_model.py | ThermalParameters.dhw_inlet_temp | Default is a bare literal 10.0 (thermal_model.py:469) beside const.DEFAULT_DHW_INLET_TEMP=10.0 and const.DHW_COLD_WATER_TEMP=10.0: three copies of the cold-water default, one of them (DHW_COLD_WATER_TEMP) now only a default argument of dhw_coil_draw_reduction. |
| 2 | D7-s3 | D7-s2 | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._step_dhw_refused/_step_dhw_floor_injected/_step_dhw_draw_kw/_step_wood_refused | Per-step scratch written by production step functions and read only by tests/features.py; no production reader (only _step_buffer_refused is read, by simulate_trajectory). |

## D8 (5)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D8-s2 | D8-s1 | custom_components/heatpump_optimizer/entity.py | commanded_power_kw (climate recommended_power_kw) | The climate entity's recommended_power_kw shares commanded_power_kw, which ignores heat_pump_on (D8-s1-03). It likely publishes a power at steps its hvac_action calls off. |
| 2 | D8-s3 | D8-s1 | custom_components/heatpump_optimizer/sensor.py | ValveTargetRecommendationSensor | Static enabled_default False even when a mixing valve is configured. Without a valve it is available and permanently unknown instead of unavailable. |
| 3 | D8-s1 | D8-s2 | custom_components/heatpump_optimizer/sensor.py | IndoorTempSensor.available | It gates on reading_ok['upper_floor_temperature'] like the climate, for the same A3(e) reason. Check whether any sensor carrying a non-measured value (plan or money) is hidden along with the measurement, as D8-s2-01 found on the climate. |
| 4 | D8-s1 | D8-s2 | custom_components/heatpump_optimizer/sensor.py | Heat Pump Action / operating-state sensors | Run the D8-s2-02 arm on the sensor side: mode off with a live space or DHW boost, where boost.apply still actuates the pump. Check whether sensors publishing an operating state or pump power read the mode label or the actuated action. |
| 5 | D8-s1 | D8-s3 | custom_components/heatpump_optimizer/sensor.py | DHWHeavyDaySensor | A hot-water-subject sensor (dhw_ key, DHW name) outside DHWEntityMixin; check its availability/default gate on a no-DHW install against the mixin's, or that tests/entities.py names it as an exception. |

## D9 (7)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D9-s2 | D9-s1 | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._run_system_identification | Call site of D9-s1-03: sysid.step (and so the identify_slab fit) is called synchronously in _async_update_data on the event loop; the fit's cost is measured in tools/audit/round9/D9/s1/sysid_loop.py, the call-site fix is yours. |
| 2 | D9-s2 | D9-s1 | custom_components/heatpump_optimizer/coordinator.py | _maybe_run_fuse_advisor / _await_optimize | Full solves per coordinator cycle by path (main, fuse-advisor what-if at coordinator.py ~10731, any shadow/diagnose) were not counted here: my cells stop at optimize(). The what-if is another full solve through the worker. |
| 3 | D9-s2 | D9-s1 | custom_components/heatpump_optimizer/coordinator.py | _solve_snapshot | Loop-thread cost of the per-cycle optimizer/state snapshot taken before every solve was not measured (coordinator is outside my cells). |
| 4 | D9-s2 | D9-s1 | custom_components/heatpump_optimizer/coordinator.py | _await_optimize (in-process fallback) | The in-process fallback solve starves the loop (starvation share 0.91-0.94, see non-findings, tools/audit/round9/D9/s1/gil_hold.py); whether WORKER_FALLBACK_CAP=N consecutive fallbacks is the right bound is a coordinator decision. |
| 5 | D9-s1 | D9-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._build_dhw_requirements / _apply_dhw_min_run / _plan_dhw_min_cost | DHW planning loops dominate the DHW-only replay's solve. Under cProfile over 48 real cycles, _build_dhw_requirements was 9.64 s of 16.5 s solve time (58 %), with thermal_model.extend_dhw_temps called 1383 times and simulate_dhw_step 106,595 times (~2,220 per solve). A candidate for the brief's DHW p |
| 6 | D9-s1 | D9-s2 | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.effective_dhw_draw_pattern / dhw_tank_heat_loss_coefficient / dhw_inlet_reference | Per-step helpers called ~100k-320k times per day of solves: effective_dhw_draw_pattern 4,704 calls driving dhw_schedule.overlap_fraction 114,360 times (24 per call) for a window set that is constant within a solve; dhw_inlet_reference 321,602 calls; dhw_tank_heat_loss_coefficient 107,572 calls. Thes |
| 7 | D9-s1 | D12-s1 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | One two-zone solve with a throttling valve (manual/smart_read; single_tank_valve, valve_upper_direct_slab, two_tank_4way) took 50-145 s of wall time per cycle on B6 at load1 ~5-6, against 1-7 s single-zone and 13-17 s two-zone without a valve (matrix.py per-cell wall_s, provisional, not evidence). |

## D10 (3)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D10-s2 | D10-s1 | custom_components/heatpump_optimizer/config_flow.py | config-flow-test-coverage / test-coverage rows | s1 carried both coverage-bearing Bronze/Silver rows as done without measuring them. The per-module coverage number is D10.M3 and decides both rows. |
| 2 | D10-s2 | D10-s1 | custom_components/heatpump_optimizer/strings.json | exceptions section | exception-translations (gold): the fixes for D10-s1-02 (button raise) and D10-s1-03 (ConfigEntryAuthFailed) add raise sites, and each needs a translation_key in strings.json/en/sv. |
| 3 | D10-s2 | D10-s1 | custom_components/heatpump_optimizer/quality_scale.yaml | manifest quality_scale: platinum | The manifest tier is derived from the in-tree register, which marks unique-config-entry, test-before-setup and action-exceptions done. The s1 draft marks them todo, so the declared tier depends on the gold/platinum rows only through s1's Bronze/Silver outcome. |

## D11 (7)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D11-s1 | D11-s2 | .github (ruleset on main) | pull_request rule: require_last_push_approval / dismiss_stale_reviews_on_push | PR #1621 merged at head 99fcc3f2 with its only approving review (tvofi) on ecb7af8e and no approval at the merged head; read the ruleset with both arms to see whether an approval on an earlier commit satisfies the required review |
| 2 | D11-s1 | D11-s2 | .claude/workflows/policy_lint.mjs | cmdHooks | D11-s2-02's fix lands in this file; also no fixture under fixtures/policy-rot/hooks/ carries a wrong matcher |
| 3 | D11-s1 | D11-s2 | .claude/workflows/rules_sync.mjs | parse | paths extraction regex requires `"..."\s*$`, rulePaths in policy_lint uses `-\s*"([^"]+)"` inside a block: a paths entry with a trailing YAML comment is kept by policy_lint and dropped from the generated .mdc globs (two parsers of one frontmatter, class I4); not measured |
| 4 | D11-s1 | D11-s2 | .claude/workflows/budget_raise_gate.py | approval | D11-s2-03 hooks it; any identity-hardening fix (distinct App for seat approvals) touches this predicate and main-protect-checks |
| 5 | D11-s1 | D13-s1 | .github/workflows/governance.yml | instrument-self-tests | fails at 18 of 201 main merge commits (one 11.69 h red episode, 2026-09-25) while succeeding or absent at every PR head; a merge-surface-only red the PR gate never sees |
| 6 | D11-s1 | D13-s1 | .claude/workflows/web-fix-wave.js | verdict poster identity | 166 of 239 `Fix review:` lines in window posted under the owner account tvofi, 73 by hpo-approver[bot]; decision 0011 says hpo-approver posts verdicts |
| 7 | D11-s1 | D13-s1 | tools/audit/round4/D11/governance_cost.py | GOV | misses rerun-stale-verdict (budget-raise-gate-rerun.yml); tests/entities.py pins GOV only against governance.yml jobs, so a governance job in another file escapes (64 s in window) |

## D12 (1)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | D12-s1 | D4-s2 | custom_components/heatpump_optimizer/wood_fuel.py | wood_fuel_ready / cheaper_hour_count (CONF_WOOD_PRICE_SEK_M3) | The wood price is compared against the electricity price in the instance currency while its key, form unit and service text say SEK; check the wood-vs-pump sensors' published units and values for a non-SEK install (form side is D4-s2-02). |

## unknown (43)

| # | Owner seat | Raised by | File | Symbol | What |
|---|---|---|---|---|---|
| 1 | unknown | D0-s1 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | D2 scope: on the default two-zone winter day, shipped two-zone plans breach the upper-zone floor by 1.34 degree-steps, a trade the soft penalty accepts. Whether that is intended belongs to the objective's owner. |
| 2 | unknown | D0-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | Under summer_warm weather objective_value is a plan-independent overshoot constant (6435 single-zone, 10598 two-zone) from warmth no heater can remove; dominates objective_value (D2 objective shape). |
| 3 | unknown | D0-s3 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | Magnitude of the terminal credit (D2): the 24 h plan's tail buys 0.50-0.69x of a 48 h plan's energy in cold weather but 1.5-7.9x in shoulder weather (end slab +3.17 K above the 48 h plan, DHW on). The same at flat prices, so it is valuation, not price. out/term_one.log |
| 4 | unknown | D0-s3 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | The docstring says the handed plan is 'the same problem one step later', but coordinator._warm_seeded passes the previous power_schedule unshifted (misaligned by the elapsed re-plan steps). Measured effect on the plan is noise (non-finding), so this is a comment-accuracy lead (D5). |
| 5 | unknown | D0-s3 | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.predicted_cost | With a perfect model, the day-1 plan's energy (23.28 SEK, winter_typical single-zone) is not what the 30-min loop spends that day (38.61 SEK); the published per-plan predicted cost does not describe the executed day (D2/D6 reporting question). out/mpc4.log |
| 6 | unknown | D1-s1 | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | The stub codec is stdlib json: it decodes 10**400 as an exact int and 1e400 as inf, and it writes NaN tokens. Real HA's orjson refuses or converts these, so store-fuzz results over-report loader raises (19 of 250 accuracy mutants were stub-only). |
| 7 | unknown | D1-s1 | custom_components/heatpump_optimizer/ | set_thermal_parameters | [carried by the orchestrator from RC2] the runtime fields it sets are not persisted and are lost at restart (user state that does not survive a restart; class of v2.4.1, v3.13.0, #1249, bug 5) |
| 8 | unknown | D1-s1 | custom_components/heatpump_optimizer/ | async_reset_comfort_weight and the cycle-end save | [carried by the orchestrator from R6 round 2] a save during startup, before the store's first read completes, can overwrite persisted learner state with defaults (the startup-clobber R6 fixed only in async_set_mode via async_wait_for_read) |
| 9 | unknown | D1-s2 | tests/hastub/homeassistant/helpers/storage.py | Store.async_load | Parses with stdlib json, which accepts NaN/Infinity tokens and >64-bit integers that Home Assistant's orjson-based Store refuses (whole file quarantined). Fuzz results through the stub include failures that cannot occur in HA; energy 10**400 and defrost duty 10**400 were two. |
| 10 | unknown | D1-s2 | tests/harness.py | ha_unload_entry | Calls each async_on_unload callback synchronously and drops a returned coroutine (RuntimeWarning: coroutine 'HeatPumpOptimizerCoordinator.async_shutdown' was never awaited, registered by the stub DataUpdateCoordinator); Home Assistant awaits coroutine unload callbacks. |
| 11 | unknown | D1-s2 | custom_components/heatpump_optimizer/coordinator.py | async_diagnose_interval / _diagnose_payload | Docstring says the worker 'gets copies, never this object (#1529)', but _diagnose_payload passes coord._last_interval_record by reference (only thermal params are deep-copied). Harmless today (the record is only rebound), but the comment is inaccurate - a D5 comment-accuracy lead. |
| 12 | unknown | D1-s3 | tests/hastub/homeassistant/util/dt.py | now | The stub's now() is naive unless HASTUB_TZ is set, while real HA is always aware. This hides every naive-vs-aware TypeError: store_fuzz.py --naive-clock loses all the naive_dt failures, and tests/finite_boundary.py seeds a naive datetime into the pump_duty record it fuzzes. Possible instrument findi |
| 13 | unknown | D1-s3 | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | away-strip data-away-return change handler | Sends the datetime-local value (tz-less) as set_away return_time; the card could send an offset-bearing ISO string (new Date(value).toISOString()). |
| 14 | unknown | D1-s4 | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | The stub round-trips through stdlib json, which writes and reads NaN; Home Assistant's Store serialises with orjson, which writes NaN as null. A NaN learner cell therefore survives a save/load in the stub but becomes null in production (for DefrostDerate that voids the whole duty grid on the next lo |
| 15 | unknown | D2-s1 | custom_components/heatpump_optimizer/external_heat.py | ExternalHeatDetector.forecast_free_heat / optimizer.py HeatPumpOptimizer.optimize (np.clip of external_heat_kw) | A NaN free_heat_kw passes `rate <= 0.0` and np.clip. The scalar step then drops it (max(0.0, nan) == 0.0), but simulate_trajectory_batch's np.maximum propagates NaN into the finite-difference gradient. The batch docstring's parity claim is scoped to finite values. Whether NaN can reach free_heat_kw  |
| 16 | unknown | D3-s1 | tests/golden/coord_dhw.json | data.dhw_advisor | Both coordinator goldens carrying dhw_advisor (coord_dhw, coord_all_features) sit in the degenerate regime where every candidate has meets_heaviest_window=false and the recommendation is the last candidate (60). As a result, env_drift --all cannot observe the advisor's cover and ranking logic: mutan |
| 17 | unknown | D3-s1 | tools/audit/round3..round8 | (tracked files) | During this session (directory mtimes around 09:15 UTC), 498 tracked files under tools/audit/round3-8 were deleted from the D3-s1 worktree. No D3-s1 harness writes outside mkdtemp roots or round9/D3/s1. This is probably the orchestrator's pruning, but it should be confirmed that the gate does not re |
| 18 | unknown | D4-s1 | tests/card_rig.mjs | planStates | The default-view plan states omit the integration's own measured sensors (withActuals), so card_drift/card_browser never render the live default view; D4-s1-05's collision passed every lane for that reason. |
| 19 | unknown | D4-s1 | tests/card_browser.mjs | contrastOf / REQUIRED | The contrast lane measures four fixed sites on fixtures that never produce a status outcome (.cheaper/.dearer/.wi-warn/.confirm), so D4-s1-01 is outside every gate. |
| 20 | unknown | D4-s1 | custom_components/heatpump_optimizer/topology.py | describe_setup slots / rank_sensor_advisor labels | Slot and advisor labels reach the card as published strings; whether the backend localizes them for a Swedish UI was not checked (the fixture's are English). |
| 21 | unknown | D4-s1 | custom_components/heatpump_optimizer (plan narrative sensor) | plan_narrative attributes.language | The card prints narrative lines in the language the sensor published, regardless of hass.language; whether the backend follows the UI language was not checked. |
| 22 | unknown | D5-s2 | tests/hastub/homeassistant/helpers/update_coordinator.py | DataUpdateCoordinator.__init__ | The stub accepts update_interval and drops it (no attribute), so no harness or test can read the cadence a coordinator was built with; comment_numbers.py had to spy on the base __init__. Upstream stores self.update_interval. |
| 23 | unknown | D6-s2 | tests/entities.py | README count pins (~lines 566-886) | Entity/page counts are pinned against README.md only; docs/configuration.md's own count (D6-s2-01) has no pin |
| 24 | unknown | D7-s3 | tests/nightly_ha.py | line 1274 (return inside finally, A4 recovery block) | A `return` inside a `finally` block (SyntaxWarning on Python 3.14) swallows any exception still in flight from the try, including CancelledError, whenever the recovery refresh raises. The nightly A4 check can then end without re-raising a failure. |
| 25 | unknown | D8-s2 | custom_components/heatpump_optimizer/optimizer.py | Optimizer._idle_action | The idle fallback action publishes power=min_electrical_power with heat_pump_on=False and no dhw_power. commanded_power_kw therefore reports a non-zero recommended power (climate recommended_power_kw, Recommended Power) while the pump is commanded off. |
| 26 | unknown | D8-s3 | README.md | Entities > temperatures table, Upper Floor Temperature row | README describes Upper Floor Temperature as 'The radiator zone' while it publishes the indoor reading on every install (UpperFloorTempSensor docstring). |
| 27 | unknown | D9-s2 | custom_components/heatpump_optimizer/entity.py | HeatPumpOptimizerSensorBase.__init_subclass__ scrub (_finite) | The non-finite scrub walks every attribute of every entity at every write, including the unrecorded bulk series: 233,594 recursive _finite calls per 48 entity reads (~4.9k per read). Its CPU share of the 5.9 ms entity read was not isolated. A loop-thread cost that grows with payload size. |
| 28 | unknown | D10-s2 | custom_components/heatpump_optimizer/sensor.py | SolarIrradianceSensor.extra_state_attributes / open_meteo.OpenMeteoSolar.diagnostics | Publishes latitude/longitude rounded to 5 decimals (~1 m) as recorded state attributes, while diagnostics.py coarsens the same coordinates to 1 dp as a privacy control. |
| 29 | unknown | D10-s2 | custom_components/heatpump_optimizer/icons.json | services section | No service icons for the 12 services in services.yaml (hassfest requires them for core integrations only; not a quality-scale rule for a custom one). |
| 30 | unknown | D11-s1 | docs/decisions/0011-app-authored-identity.md | Context: 'about eleven of its merged pull requests now return 404' | Measured 52 of 253 first-parent PR merges since 2026-09-17 answer 404 (61 of merged PRs >= #1000; 53 whose head commit is by tvofi-seat-author); the record undercounts the purge and conformance over those merges is unmeasurable from GitHub. |
| 31 | unknown | D11-s1 | docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md | step 3(d) dismiss_stale_reviews_on_push: true | Status reads as enforced by GitHub; live ruleset 23698884 has false (see D11-s1-01). 0009 step 6 inherits the claim. |
| 32 | unknown | D11-s1 | tests/delivery_status.py | collect | Docstring: 'nothing else reaches main with two parents under the ruleset' - false under the DeployKey bypass; single-parent direct pushes are skipped silently (same class as D11-s1-02). |
| 33 | unknown | D12-s1 | tools/audit/round9/D12/s1/ | REPORT.md | The seat harness refused to write REPORT.md (a policy against subagent report files), so this JSON is the whole report. The orchestrator may need to render REPORT.md from it. |
| 34 | unknown | D12-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.get_current_action | On every install (modulating 1/6 kW), idle and sub-floor steps publish power_normalized = -min/range = -0.2 on the Heat Pump Action sensor attribute and the climate attribute: 585 of 864 steps in onoff_label.py's modulating arm. A wrong published value outside [0,1] (D2/D8). |
| 35 | unknown | D12-s2 | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._idle_action | The empty-plan and pre-horizon action carries power=min_electrical_power with heat_pump_on=False, so coordinator._commanded_power reports min kW commanded while the pump is off. The external-heat, COP and frequency consumers read it (D1/D2). |
| 36 | unknown | D12-s3 | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._build_data_dict | On an install with no tank, buffer or slab sensor, the data dict publishes dhw_temperature 55.0, buffer_tank_temperature 40.0 and slab_temperature 22.0, which are the ThermalState constructor defaults. The entities stay unavailable, but any card or diagnostics reader of coordinator.data would show f |
| 37 | unknown | D12-s3 | tests/entities.py | _walk_flow_untouched / check 'and turns hot water on anyway, with the 200 L tank the page pre-fills' | The suite pins the untouched full wizard enabling DHW as a passing check, so the gate defends the DHW half of D12-s3-01 instead of catching it (D3). |
| 38 | unknown | D14-s1 | tests/hastub/homeassistant/util/dt.py | now | The stub returns a naive datetime.now() when no clock is frozen, while Home Assistant's dt_util.now() is always aware. Tests on the default clock therefore never compare an aware stored timestamp with an aware now, and never meet the naive-stored case that production meets (class P11, which no round |
| 39 | unknown | D14-s2 | custom_components/heatpump_optimizer/grid_fee.py | grid_fee:IMPLAUSIBLE_FEE_SEK_PER_KWH | The 10-per-kWh fee plausibility bound (config-flow refusal and repair notice) is one number for every currency; a high-denomination currency (HUF, JPY) fee would be refused as implausible. Not measured. |
| 40 | unknown | D14-s2 | custom_components/heatpump_optimizer/currency.py | currency:FALLBACK_CURRENCY | Real Home Assistant always sets hass.config.currency (core default EUR), so the SEK fallback the module and README describe fires only under stubs; an unconfigured instance labels in EUR, not SEK. Not measured against HA core. |
| 41 | unknown | D14-s2 | custom_components/heatpump_optimizer/quick_setup.py | quick_setup:stored_answers | The buffer-tank answer is read back as volume >= BUFFER_STORE_MIN_VOLUME while ThermalParameters.buffer_is_store also requires a throttling valve; read here as an answer read-back (not applicable to P2), left for a D12/D8 seat to judge. |
| 42 | unknown | D14-s3 | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / _lbfgsb_restart | L-BFGS-B exits with ABNORMAL line-search terminations at ftol 1e-12 on two\|nodhw\|winter_typical: FD-gradient (eps 1e-4) noise on a piecewise objective, relevant to any D0 convergence work |
| 43 | unknown | D14-s3 | custom_components/heatpump_optimizer/sysid.py | SystemIdentification (light_new preset) | light_new: every completed experiment is refused at hw 0.1446 even with no bias, and any gains/drift/cap mismatch aborts on excursion, so the experiment can never adopt on this preset at MAX_KW 3.5 |

## Carried

| 1 | unknown | orchestrator (from #1643) | inputs.py / const.py | INPUT_MAX_AGE_MINUTES, age_of | The integration's indoor-temperature sensor goes unavailable after an hour without a source report, leaving history gaps (about 16:30-20:45 and 03:30-06:15 on tvofi's install). Check against D1-s5-01 first. |
