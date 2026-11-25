# D3-s1, box D3-g09 -- full gate for 16 u1 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Report path `dev/audit/rounds/round11/D3/s1/wave/D3-g09/REPORT.md`. Seat D3-s1, step D3.M3 (+ D3.M4 answers by probe).

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1126       13458          12        1800       14961
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.77
Sun Nov 22 21:39:10 UTC 2026
--- re-fire 2026-11-25 (successor seat, after predecessor stall) ---
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         730       14079          12        1549       15356
Swap:              0           0           0
Model name:                              Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.60
```

Null control (`fullgate.py null`, a comment-only marker): gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], summary ['3 TEST SCRIPT(S) FAILED'], wall 3868.5 s, load1 0.67 -> 1.02 (provisional). Record `dev/audit/rounds/round11/D3/s1/wave/D3-g09/gates/null.json`. Read as artefact-only (the same three scripts and fail-line counts as box D3-rem's null; none reads a production file): `dev/audit/rounds/round11/D3/s1/wave/D3-g09/gates/null-note.txt`. A key is KILLED only on a script beyond the null or more FAIL lines in one.

Procedure: `gate_wave.sh run` (dispatch ref) applies each key's one-line mutant with `fullgate.py run --src complete --key <key>`: commit, gate_lock lease, `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh`, record, reset; one gate at a time, 4 h cap. Wall, CPU and load numbers are provisional; verdicts and probe values are counts.

## Seat continuity

Seat continuity: gates for 9cdf54d2309cfcc8..002980a15ae8b9a9 and every probe were taken by the first seat of this box (2026-11-22/23); it stalled during 1785780ac9dd1b18 and a successor seat resumed on 2026-11-25 from the checkpoint on handoff-wip/finder-r11-D3-g09 @ ae720a2b, re-gating 1785780ac9dd1b18 and the 9 keys after it with the same gate_wave.sh run and the same null. Two gates were cut by container restarts and re-run from scratch (no record written): d8101520588009d9 (2026-11-23 ~00:28Z) and 1785780ac9dd1b18 (2026-11-25 ~01:15Z); partial logs in gates/interrupted/. Out-of-tree workaround: gate_wave.sh expects $HOME/venv-ci, which the re-fired container provides at /opt/hpo/venv-ci; a symlink $HOME/venv-ci -> /opt/hpo/venv-ci was made, nothing tracked changed.

## Tally

- gated: 16 of 16
- KILLED: 0
- SURVIVED: 0
- RED-AS-NULL: 16
- TIMEOUT: 0
- candidates: 12
- equivalent-candidates: 4

| key | site | patch | verdict | killed_by | gate wall s | class |
|---|---|---|---|---|---|---|
| 9cdf54d2309cfcc8 | custom_components/heatpump_optimizer/coordinator.py:9038 CMP_BOUND | `and utc_elapsed_seconds(self._outage_recovery_until, now) > 0 -> and utc_elapsed_seconds(self._outage_recovery_until, now) >= 0` | RED-AS-NULL | - | 3587.7 | candidate |
| d8101520588009d9 | custom_components/heatpump_optimizer/coordinator.py:8900 CMP_BOUND | `elif tariff.enabled and tariff.sample_factor(dt_util.now()) > 0.0: -> elif tariff.enabled and tariff.sample_factor(dt_util.now()) >= 0.0:` | RED-AS-NULL | - | 3323.9 | candidate |
| 33d708ab867fe5e7 | custom_components/heatpump_optimizer/coordinator.py:10262 CLAMP_DROP | `/ max(ctx._opt_config.time_step_minutes, 1.0) -> / (ctx._opt_config.time_step_minutes)` | RED-AS-NULL | - | 3303.4 | equivalent-candidate |
| 3dcdfbdd2542f33e | custom_components/heatpump_optimizer/coordinator.py:10267 CLAMP_DROP | `idx = min(steps, len(trajectory) - 1) -> idx = (steps)` | RED-AS-NULL | - | 3323.3 | equivalent-candidate |
| 3d83c32f185cf411 | custom_components/heatpump_optimizer/coordinator.py:9819 CMP_BOUND | `if not config.enabled or config.peak_kw <= 0: -> if not config.enabled or config.peak_kw < 0:` | RED-AS-NULL | - | 3284.8 | candidate |
| 002980a15ae8b9a9 | custom_components/heatpump_optimizer/coordinator.py:9827 GUARD_OFF | `if self._pv_production is not None and len(production): -> if False:` | RED-AS-NULL | - | 3386.2 | candidate |
| 1785780ac9dd1b18 | custom_components/heatpump_optimizer/coordinator.py:9836 GUARD_OFF | `if self._pv_production is not None: -> if False:` | RED-AS-NULL | - | 3181.1 | candidate |
| 326b26f53972df61 | custom_components/heatpump_optimizer/coordinator.py:9810 GUARD_OFF | `if not entity_id: -> if False:` | RED-AS-NULL | - | 3223.7 | candidate |
| 104db258fed59c2d | custom_components/heatpump_optimizer/coordinator.py:11000 CMP_BOUND | `if mean_price <= 1e-6: -> if mean_price < 1e-6:` | RED-AS-NULL | - | 3112.2 | candidate |
| 8daaf4fcaf8cd897 | custom_components/heatpump_optimizer/coordinator.py:11002 CMP_BOUND | `if float(np.max(prices) - np.min(prices)) / mean_price < 0.15: -> if float(np.max(prices) - np.min(prices)) / mean_price <= 0.15:` | RED-AS-NULL | - | 3075.8 | candidate |
| 3cfe39778305daba | custom_components/heatpump_optimizer/coordinator.py:11008 CMP_BOUND | `if heating_kwh < 1.0: -> if heating_kwh <= 1.0:` | RED-AS-NULL | - | 3118.6 | candidate |
| 146d687b30889301 | custom_components/heatpump_optimizer/coordinator.py:10504 GUARD_OFF | `if closed: -> if False:` | RED-AS-NULL | - | 3266.3 | equivalent-candidate |
| 425a9196b86265d0 | custom_components/heatpump_optimizer/coordinator.py:11057 GUARD_OFF | `if not self._sysid.active: -> if False:` | RED-AS-NULL | - | 3224.4 | candidate |
| 84797ff91697f6a7 | custom_components/heatpump_optimizer/coordinator.py:11091 CLAMP_DROP | `override / max(ctx._thermal_params.max_electrical_power, 0.1) -> override / (ctx._thermal_params.max_electrical_power)` | RED-AS-NULL | - | 3404.1 | equivalent-candidate |
| 0c99189b7639f1bd | custom_components/heatpump_optimizer/coordinator.py:9980 CMP_BOUND | `if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s: -> if 0.25 * interval_s <= window.seconds < 3.0 * interval_s:` | RED-AS-NULL | - | 3458.8 | candidate |
| df697cc04154fbdd | custom_components/heatpump_optimizer/coordinator.py:9980 CMP_BOUND | `if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s: -> if 0.25 * interval_s < window.seconds <= 3.0 * interval_s:` | RED-AS-NULL | - | 3331.7 | candidate |

## Survivors: step-4 answers with probe numbers

### 9cdf54d2309cfcc8 -- custom_components/heatpump_optimizer/coordinator.py:9038 CMP_BOUND (candidate, severity claimed low, class guess I1)

`and utc_elapsed_seconds(self._outage_recovery_until, now) > 0 -> and utc_elapsed_seconds(self._outage_recovery_until, now) >= 0` in `HeatPumpOptimizerCoordinator._outage_recovery_active`; gate RED-AS-NULL (gate_rc 1).
**Outage recovery's end instant is unpinned: `> 0` -> `>= 0` keeps recovery active at its deadline and the gate passes.** HeatPumpOptimizerCoordinator._outage_recovery_active (coordinator.py:9038) may be weakened from `> 0` to `>= 0` and the full gate still passes; at now == _outage_recovery_until the baseline answers inactive and the mutant active (probe: 0 vs 1), so one extra interval of staggered recovery (DHW queued behind space) at the boundary is invisible to the suite.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_9cdf54d2309cfcc8.py`: RESULT active_at_tie_{baseline,mutant}: _outage_recovery_active(now) as 0/1 at now == _outage_recovery_until. Baseline **active_at_tie=0**; mutant **active_at_tie=1**. Null: before_end and after_end cells: both arms 1 and 0. Inputs tried: now == until (tie); now = until - 1 s; now = until + 1 s. load1 1.07, thread_factor 1.0.
Should have failed: tests/features.py, the #22 block (~19496) 'a three-hour silence reads as an outage and opens recovery': it asserts active inside the window and inactive after it, but no arm evaluates now == _outage_recovery_until, where the recovery window must already be closed.

### d8101520588009d9 -- custom_components/heatpump_optimizer/coordinator.py:8900 CMP_BOUND (candidate, severity claimed high, class guess I1)

`elif tariff.enabled and tariff.sample_factor(dt_util.now()) > 0.0: -> elif tariff.enabled and tariff.sample_factor(dt_util.now()) >= 0.0:` in `HeatPumpOptimizerCoordinator._power_headroom`; gate RED-AS-NULL (gate_rc 1).
**Power headroom publishes 0 kW all off-season under a `> 0.0` -> `>= 0.0` mutant, and no check notices.** HeatPumpOptimizerCoordinator._power_headroom (coordinator.py:8900) may be weakened from `sample_factor(now) > 0.0` to `>= 0.0` and the full gate passes; sample_factor is clamped to [0, 1], so the mutant takes the capacity branch whenever the tariff is enabled: for a fuse-less install with a Nov-Mar capacity tariff, in July the baseline publishes unavailable while the mutant publishes 0.0 kW headroom (probe), which a charger automation reads as 'draw nothing'.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_d8101520588009d9.py`: RESULT available_offseason_{baseline,mutant}: _power_headroom()['available'] (0/1), capacity tariff Nov-Mar, no fuse, no peak, at 2026-07-15 12:00 UTC. Baseline **available_offseason=0 (unavailable)**; mutant **available_offseason=1, limit_kw=0.0, limit_source='capacity tariff with no peak reference yet'**. Null: in-season cell: both arms available with limit 0.0 kW. Inputs tried: off-season month (sample_factor 0.0); in-season month (sample_factor 1.0). load1 1.07, thread_factor 1.0.
Should have failed: tests/features.py, the #5 power-headroom block (~19481) 'with no limit configured the sensor says unavailable, not zero': it checks only a coordinator with no tariff; no arm enables a capacity tariff at a moment it does not bill (a month outside peak_tariff_months, or an off-peak hour at factor 0), where the sensor must stay unavailable.

### 33d708ab867fe5e7 -- custom_components/heatpump_optimizer/coordinator.py:10262 CLAMP_DROP (equivalent-candidate)

`/ max(ctx._opt_config.time_step_minutes, 1.0) -> / (ctx._opt_config.time_step_minutes)` in `HeatPumpOptimizerCoordinator._predicted_next_room_temp`; gate RED-AS-NULL (gate_rc 1).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_33d708ab867fe5e7.py`: RESULT differing_cells_reachable: arms that disagree on _predicted_next_room_temp() at time_step_minutes >= 1. Baseline **differing_cells_reachable=0 (25 cells)**; mutant **differing_cells_subminute_step=9 (time_step 0.5: other point; 0.0: ZeroDivisionError)**. Null: time_step 15.0 cells, clamp inactive. Inputs tried: optimization_interval 10/15/30/60/120 x time_step_minutes 15/5/1/0.5/0.0 on a 97-point ramp. load1 0.99, thread_factor 1.0.
Should have failed: none distinguishes on a reachable input: OptimizationConfig.time_step_minutes is the dataclass default 15.0 (optimizer.py:2667) and no config path writes it (grep `time_step_minutes=` finds no writer); the clamp is defensive.

### 3dcdfbdd2542f33e -- custom_components/heatpump_optimizer/coordinator.py:10267 CLAMP_DROP (equivalent-candidate)

`idx = min(steps, len(trajectory) - 1) -> idx = (steps)` in `HeatPumpOptimizerCoordinator._predicted_next_room_temp`; gate RED-AS-NULL (gate_rc 1).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3dcdfbdd2542f33e.py`: RESULT differing_cells_at_production_len: arms that disagree on _predicted_next_room_temp() at trajectory length n_steps+1 = 97. Baseline **differing_cells_at_production_len=0 (23 intervals)**; mutant **differing_cells_short_trajectory=100 (IndexError where len(trajectory) <= steps <= 8)**. Null: production-length cells. Inputs tried: optimization_interval 10..120 by 5 x trajectory length 1..12 and 97. load1 0.99, thread_factor 1.0.
Should have failed: none on a produced plan: the one OptimizationResult constructor (optimizer.py:3848) emits n_steps+1 points with the forecasts held flat to opt_config.n_steps (coordinator.py:7475); a trajectory of <= 8 points would separate the arms (IndexError) but no solve produces one.

### 3d83c32f185cf411 -- custom_components/heatpump_optimizer/coordinator.py:9819 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if not config.enabled or config.peak_kw <= 0: -> if not config.enabled or config.peak_kw < 0:` in `HeatPumpOptimizerCoordinator._pv_forecast`; gate RED-AS-NULL (gate_rc 1).
**A 0 kWp enabled PV array is unpinned: `peak_kw <= 0` -> `< 0` publishes an all-zero PV summary.** HeatPumpOptimizerCoordinator._pv_forecast (coordinator.py:9819) may be weakened from `peak_kw <= 0` to `< 0` and the gate passes; with pv_enabled and pv_peak_kw 0 (accepted by the options flow) the baseline treats PV as off (summary {}) while the mutant publishes a five-key all-zero PV summary (probe). The surplus is 0 in both, so the plan is unchanged; only the published PV block differs.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3d83c32f185cf411.py`: RESULT summary_keys_peak0_{baseline,mutant}: len(_pv_forecast(solar, 8)[1]) with pv_enabled and pv_peak_kw 0. Baseline **summary_keys_peak0=0 ({})**; mutant **summary_keys_peak0=5 (forecast_production_kwh 0.0, ..., export_price 0.0)**. Null: peak 6 and peak -1 cells: equal arms. Inputs tried: pv_peak_kw 0 (the flow's minimum, config_flow.py:1933); pv_peak_kw 6; pv_peak_kw -1. load1 0.99, thread_factor 1.0.
Should have failed: tests/solar_alignment.py / tests/features.py PV checks: none configures pv_enabled with pv_peak_kw 0 and asserts the disabled-PV answer (empty summary, zero surplus, _pv_production None).

### 002980a15ae8b9a9 -- custom_components/heatpump_optimizer/coordinator.py:9827 GUARD_OFF (candidate, severity claimed medium, class guess I1)

`if self._pv_production is not None and len(production): -> if False:` in `HeatPumpOptimizerCoordinator._pv_forecast`; gate RED-AS-NULL (gate_rc 1).
**The inverter meter's step-0 override of the PV forecast can be switched off and the gate passes.** HeatPumpOptimizerCoordinator._pv_forecast (coordinator.py:9827) may lose its measured-production override (`if ...:` -> `if False:`) and the full gate passes; with a production meter reading 3.0 kW under a dark irradiance step the baseline plans 2.6 kW of step-0 surplus and the mutant 0.0 (probe), so the step being acted on ignores the meter.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_002980a15ae8b9a9.py`: RESULT surplus0_meter_{baseline,mutant}: _pv_forecast(solar, 8)[0][0] kW, 6 kWp, dark step 0, production meter 3.0 kW. Baseline **surplus0_meter=2.6 kW (surplus_sum 11.32)**; mutant **surplus0_meter=0.0 kW (surplus_sum 8.72)**. Null: no-meter cell: both 0.0. Inputs tried: meter 3.0 kW; meter 9.0 kW (over peak: min(meter, peak) = 6); no meter. load1 0.9, thread_factor 1.0.
Should have failed: tests/config_flow_steps.py and the env_drift.py coordinator fixtures execute line 9827 but no scenario configures pv_production_entity with a reading that differs from the irradiance model and asserts surplus[0] (or the plan's step-0 PV) equals min(meter, peak_kw) less the baseline load.

### 1785780ac9dd1b18 -- custom_components/heatpump_optimizer/coordinator.py:9836 GUARD_OFF (candidate, severity claimed medium, class guess I1)

`if self._pv_production is not None: -> if False:` in `HeatPumpOptimizerCoordinator._pv_forecast`; gate RED-AS-NULL (gate_rc 1).
**The PV summary's measured_production_kw can vanish and the gate passes.** HeatPumpOptimizerCoordinator._pv_forecast (coordinator.py:9836) may drop the measured_production_kw key (`if ...:` -> `if False:`) and the full gate passes; with a 3.0 kW production meter the baseline publishes measured_production_kw 3.0 and the mutant publishes no key (probe).
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_1785780ac9dd1b18.py`: RESULT measured_production_kw_meter_{baseline,mutant}: _pv_forecast(...)[1].get('measured_production_kw') with a 3.0 kW production meter. Baseline **measured_production_kw=3.0**; mutant **measured_production_kw=None (key absent from _pv_summary)**. Null: no-meter cell: both None. Inputs tried: meter 3.0 kW; no meter. load1 0.9, thread_factor 1.0.
Should have failed: tests/config_flow_steps.py and env_drift.py fixtures execute line 9836 but no check reads the PV summary's measured_production_kw with a production meter configured.

### 326b26f53972df61 -- custom_components/heatpump_optimizer/coordinator.py:9810 GUARD_OFF (candidate, severity claimed high, class guess P11)

`if not entity_id: -> if False:` in `HeatPumpOptimizerCoordinator._pv_measured_production`; gate RED-AS-NULL (gate_rc 1).
**The no-entity guard of _pv_measured_production is untestable on FakeStates: without it every un-metered PV install raises under Home Assistant.** HeatPumpOptimizerCoordinator._pv_measured_production (coordinator.py:9810) may lose its `if not entity_id: return None` guard and the full gate passes, because the suite's FakeStates.get tolerates None; under Home Assistant's own StateMachine.get (entity_id.lower()) the mutant raises AttributeError in _pv_forecast for every PV install without a production meter (the default, pv_production_entity None), while the baseline answers (probe). The slice box's M4 answer read this key as equivalent on the stub.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_326b26f53972df61.py`: RESULT ha_none_{baseline,mutant}: outcome of _pv_forecast(solar, 8), PV enabled 6 kWp, no production entity, under Home Assistant's StateMachine.get (transcribed from homeassistant 2025.1.0 core.py:2151-2158). Baseline **ha_none: surplus_sum=8.72**; mutant **ha_none: raised AttributeError ('NoneType' object has no attribute 'lower')**. Null: FakeStates arms (equal: why the suite cannot fail) and the metered arm (guard not taken). Inputs tried: FakeStates + entity None; FakeStates + entity '' (resolves to None); HA get + None; HA get + ''; HA get + meter 3.0 kW. load1 0.99, thread_factor 1.0.
Should have failed: tests/config_flow_steps.py, env_drift.py and features.py execute line 9810, but every one runs on tests/harness.py:FakeStates.get, a plain dict.get that answers None for entity_id None where Home Assistant's StateMachine.get calls entity_id.lower() and raises; no check runs _pv_measured_production with no entity against a state machine that rejects None (or asserts states.get is never called with a falsy id).

### 104db258fed59c2d -- custom_components/heatpump_optimizer/coordinator.py:11000 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if mean_price <= 1e-6: -> if mean_price < 1e-6:` in `HeatPumpOptimizerCoordinator._record_quiet_comfort_period`; gate RED-AS-NULL (gate_rc 1).
**The near-zero mean-price guard of the quiet-comfort recorder is unpinned at its boundary (`<= 1e-6` -> `< 1e-6`).** HeatPumpOptimizerCoordinator._record_quiet_comfort_period (coordinator.py:11000) may be weakened from `mean_price <= 1e-6` to `< 1e-6` and the gate passes; at a float64 mean of exactly 1e-6 the mutant records a quiet period (evidence -0.0073) the baseline skips (probe). Boundary-only.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_104db258fed59c2d.py`: RESULT calls_tie_{baseline,mutant}: record_quiet_period calls from one _record_quiet_comfort_period on a flat plan, prices [5e-07, 1.5e-06] (float64 mean exactly 1e-6), 1.5 kWh heating. Baseline **calls_tie=0 (evidence 0.0)**; mutant **calls_tie=1 (evidence -0.007292)**. Null: ordinary and zero cells: equal arms. Inputs tried: mean exactly 1e-6 (tie); ordinary 0.5/1.0/1.5; all-zero prices. load1 0.9, thread_factor 1.086.
Should have failed: tests/features.py, the quiet-period block (~51783-51882): it covers swinging prices, flat prices and no plan, but no arm sits at mean_price == 1e-6, the near-zero-price guard's boundary.

### 8daaf4fcaf8cd897 -- custom_components/heatpump_optimizer/coordinator.py:11002 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if float(np.max(prices) - np.min(prices)) / mean_price < 0.15: -> if float(np.max(prices) - np.min(prices)) / mean_price <= 0.15:` in `HeatPumpOptimizerCoordinator._record_quiet_comfort_period`; gate RED-AS-NULL (gate_rc 1).
**The 15 % price-spread threshold of the quiet-comfort recorder is unpinned at its boundary (`< 0.15` -> `<= 0.15`).** HeatPumpOptimizerCoordinator._record_quiet_comfort_period (coordinator.py:11002) may be tightened from `< 0.15` to `<= 0.15` and the gate passes; at a spread of exactly 15 % of the mean the baseline records the quiet period and the mutant does not (probe). Boundary-only.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_8daaf4fcaf8cd897.py`: RESULT calls_tie_{baseline,mutant}: record_quiet_period calls from one _record_quiet_comfort_period, prices [0.6, 0.6972972972972973] ((max-min)/mean exactly 0.15), 1.5 kWh heating. Baseline **calls_tie=1 (evidence -0.007292)**; mutant **calls_tie=0 (evidence 0.0)**. Null: 0.10 and 0.30 cells: equal arms. Inputs tried: spread exactly 0.15 (ulp walk); spread ~0.10; spread 0.30. load1 1.07, thread_factor 1.0.
Should have failed: tests/features.py quiet-period block (~51783) and config_flow_steps.py: no arm puts the price spread at exactly 15 % of the mean.

### 3cfe39778305daba -- custom_components/heatpump_optimizer/coordinator.py:11008 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if heating_kwh < 1.0: -> if heating_kwh <= 1.0:` in `HeatPumpOptimizerCoordinator._record_quiet_comfort_period`; gate RED-AS-NULL (gate_rc 1).
**The 1 kWh heating threshold of the quiet-comfort recorder is unpinned at its boundary (`< 1.0` -> `<= 1.0`).** HeatPumpOptimizerCoordinator._record_quiet_comfort_period (coordinator.py:11008) may be tightened from `heating_kwh < 1.0` to `<= 1.0` and the gate passes; at exactly 1.0 kWh the baseline records the quiet period and the mutant does not (probe). Boundary-only.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3cfe39778305daba.py`: RESULT calls_tie_{baseline,mutant}: record_quiet_period calls from one _record_quiet_comfort_period at exactly 1.0 kWh planned heating (4 kW x 0.25 h). Baseline **calls_tie=1**; mutant **calls_tie=0**. Null: 0.75 and 1.5 kWh cells: equal arms. Inputs tried: 1.0 kWh as one step; 1.0 kWh as two steps; 0.75 kWh; 1.5 kWh. load1 0.99, thread_factor 1.095.
Should have failed: tests/features.py quiet-period block (~51783): no arm plans exactly 1.0 kWh, the heating threshold's boundary.

### 146d687b30889301 -- custom_components/heatpump_optimizer/coordinator.py:10504 GUARD_OFF (equivalent-candidate)

`if closed: -> if False:` in `HeatPumpOptimizerCoordinator._roll_month`; gate RED-AS-NULL (gate_rc 1).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_146d687b30889301.py`: RESULT settle_saves_* and receipt_frozen_at_last_save: ledger saves per _accumulate_energy settlement crossing into February (the only caller of _roll_month, coordinator.py:10306), and whether the frozen receipt precedes the last save. Baseline **direct _roll_month: saves_close=1; settlement: 2 saves, receipt frozen at last save 1**; mutant **direct: saves_close=0; settlement: 1 save, receipt frozen at last save 1 (same stored state)**. Null: the within-January cell. Inputs tried: direct _roll_month across Jan->Feb; direct within January; settlement energy 2 kW; settlement energy 0; settlement with an injected fault after the roll. load1 1.06, thread_factor 1.0.
Should have failed: none on a reachable path: the settlement saves the ledger unconditionally after the roll (coordinator.py:10332 for energy <= 0, 10401 otherwise), so the receipt is persisted by the same settlement; only a settlement that raises after the roll separates the arms (fault arm: 1 save vs 0).

### 425a9196b86265d0 -- custom_components/heatpump_optimizer/coordinator.py:11057 GUARD_OFF (candidate, severity claimed low, class guess I1)

`if not self._sysid.active: -> if False:` in `HeatPumpOptimizerCoordinator._run_system_identification`; gate RED-AS-NULL (gate_rc 1).
**An idle system-identification experiment can ship a process-worker job every cycle and the gate passes.** HeatPumpOptimizerCoordinator._run_system_identification (coordinator.py:11057) may lose its `if not self._sysid.active: return` guard and the full gate passes; behaviour is unchanged (SystemIdentification.step returns None and stand_down/abort return at once when inactive), but on an install with indoor and outdoor sensors every cycle then dispatches one off-loop step_detached job (probe: 0 -> 1 per cycle), a pickled experiment round trip to the process worker that the Raspberry-Pi-class host pays for nothing.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_425a9196b86265d0.py`: RESULT offloop_jobs_rooms_{idle,done,aborted}_{baseline,mutant}: off-loop sysid jobs (coordinator._await_off_loop: a process-worker round trip) per _run_system_identification with no active experiment, indoor and outdoor entities configured; behaviour_differs_* compares the adopted action and the experiment state. Baseline **offloop_jobs (idle/done/aborted) = 0; behaviour_differs = 0**; mutant **offloop_jobs (idle/done/aborted) = 1 each; behaviour_differs = 0**. Null: phase ARMED (the guard not taken): 1 job in both arms; default config: 0 jobs in both arms. Inputs tried: phases IDLE, DONE, ABORTED, ARMED x configs default (hold_reason stands down) and indoor+outdoor entities. load1 1.07, thread_factor 1.0.
Should have failed: tests/features.py ~24718 drives _run_system_identification on the executor route but never counts the off-loop dispatches of an inactive experiment; tests/deployment_shape.py checks where step_detached runs, not how often. No check asserts that an idle experiment ships nothing to the worker.

### 84797ff91697f6a7 -- custom_components/heatpump_optimizer/coordinator.py:11091 CLAMP_DROP (equivalent-candidate)

`override / max(ctx._thermal_params.max_electrical_power, 0.1) -> override / (ctx._thermal_params.max_electrical_power)` in `HeatPumpOptimizerCoordinator._run_system_identification`; gate RED-AS-NULL (gate_rc 1).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_84797ff91697f6a7.py`: RESULT differing_cells_flow_reachable: arms that disagree on the adopted action's power_normalized (override 0.5 kW) at a resolved max_electrical_power >= 1.0 (the options flow minimum). Baseline **differing_cells_flow_reachable=0 (5.0: 0.1/0.1, 1.0: 0.5/0.5, 0.5: 1.0/1.0)**; mutant **differing_cells_below_flow_minimum=2 (0.05: 5.0 vs 10.0; 0.0: ZeroDivisionError)**. Null: the 5.0 and 1.0 cells. Inputs tried: heat_pump_max_power 5.0, 1.0, 0.5, 0.05, 0.0 through the coordinator's config path. load1 1.07, thread_factor 1.0.
Should have failed: none on a flow-validated entry: config_flow.py:1851 bounds heat_pump_max_power to [1, 20] kW, so the 0.1 floor never binds; a hand-edited entry below 0.1 kW would separate the arms (the coordinator passes it through unclamped).

### 0c99189b7639f1bd -- custom_components/heatpump_optimizer/coordinator.py:9980 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s: -> if 0.25 * interval_s <= window.seconds < 3.0 * interval_s:` in `HeatPumpOptimizerCoordinator._settle_defrost`; gate RED-AS-NULL (gate_rc 1).
**The measured-defrost window filter's upper bound is unpinned (`<= 3.0 * interval` -> `<`).** HeatPumpOptimizerCoordinator._settle_defrost (coordinator.py:9980) may make its upper window bound strict and the gate passes; a measured-duty window exactly three intervals long is folded by the baseline and dropped by the mutant (probe, at intervals 10, 30 and 120 min). Boundary-only.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_0c99189b7639f1bd.py`: RESULT calls_tie_i{10,30,120}_{baseline,mutant}: observe_duty calls from one _settle_defrost on a measured-duty window exactly 3 x the optimization interval long. Baseline **calls_tie=1 at intervals 10/30/120**; mutant **calls_tie=0 at intervals 10/30/120**. Null: the inside and outside cells: equal arms. Inputs tried: window = 3x interval (tie); 3x interval - 1 s; 3x interval + 1 s; at intervals 10, 30, 120 min. load1 0.9, thread_factor 1.0.
Should have failed: tests/features.py, the `_settle_defrost` block (~56686-56710): it folds measured-duty windows of ordinary length but no arm sits at window.seconds == 3.0 * interval_s, the restart filter's upper boundary.

### df697cc04154fbdd -- custom_components/heatpump_optimizer/coordinator.py:9980 CMP_BOUND (candidate, severity claimed low, class guess I1)

`if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s: -> if 0.25 * interval_s < window.seconds <= 3.0 * interval_s:` in `HeatPumpOptimizerCoordinator._settle_defrost`; gate RED-AS-NULL (gate_rc 1).
**The measured-defrost window filter's lower bound is unpinned (`0.25 * interval <=` -> `<`).** HeatPumpOptimizerCoordinator._settle_defrost (coordinator.py:9980) may make its lower window bound strict and the gate passes; a measured-duty window exactly a quarter interval long is folded by the baseline and dropped by the mutant (probe, at intervals 10, 30 and 120 min). Boundary-only.
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_df697cc04154fbdd.py`: RESULT calls_tie_i{10,30,120}_{baseline,mutant}: observe_duty calls from one _settle_defrost on a measured-duty window exactly 0.25 x the optimization interval long. Baseline **calls_tie=1 at intervals 10/30/120**; mutant **calls_tie=0 at intervals 10/30/120**. Null: the inside and outside cells: equal arms. Inputs tried: window = 0.25x interval (tie); 0.25x interval + 1 s; 0.25x interval - 1 s; at intervals 10, 30, 120 min. load1 1.07, thread_factor 1.0.
Should have failed: tests/features.py, the `_settle_defrost` block (~56686-56710): no arm sits at window.seconds == 0.25 * interval_s, the filter's lower boundary.

## Leads

- tests/harness.py `FakeStates.get`: FakeStates.get is a plain dict.get and answers None for entity_id None; Home Assistant's StateMachine.get (core.py, 2025.1.0: `self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())`) raises AttributeError. Every coordinator read that could pass a falsy id to hass.states.get is untestable on the stub; a sweep of `hass.states.get(` call sites whose argument can be None is outside this box's cells
- custom_components/heatpump_optimizer/coordinator.py `HeatPumpOptimizerCoordinator._run_system_identification`: D9 (CPU on a Pi-class host): the inactive-experiment early return is the only thing keeping an idle sysid off the process worker each cycle; no budget or count pins it (probe_425a9196b86265d0.py: 0 vs 1 off-loop job per idle cycle)

## Unfinished

- SURVIVORS.tsv (the D3.M3 enumerator's input) is not in this box's tree; universe 742 is taken from the brief and re-derived as the union of the 47 dispatch refs' keys.tsv (742 distinct keys)

## Exposure

No docs/ or GitHub issue/PR text read; no register, J/ or verifier report read. Read from git refs: the 47 dispatch/finder-r11-D3-g<NN> tips' keys.tsv (key lists only), to name the other boxes' keys in not_reached. Downloaded homeassistant==2025.1.0's wheel to a scratch dir to read StateMachine.get (core.py:2151-2158), transcribed in probes/_pv_common.py:HAStates for key 326b26f53972df61.
