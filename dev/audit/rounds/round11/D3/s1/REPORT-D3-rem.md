# D3-s1, box D3-rem: D3.M3 remainder and its D3.M4 answers

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. box D3-rem: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box. Walls provisional; counts exact.

## T1 full gate

| mutant | site | survived | killed_by | wall s | load1 | carried-or-gated |
|---|---|---|---|---|---|---|
| c2:95779f9d6d71c50d | grid_fee.py:355 | True (SURVIVED) | - | 3486.5 | 0.23..0.0 | carried from cloud box D3-top6 (wip 917689bd) |
| c2:a0b3b28854fa500c | flow_lift.py:188 | True (SURVIVED) | - | 3451.2 | 0.07..0.01 | carried from cloud box D3-top6 (wip 917689bd) |
| c2:c38d53ab787ddbfa | price_model.py:252 | True (RED-AS-NULL) | - | 3123.6 | 0.43..0.93 | gated on box D3-rem |
| c3c6:5cc84148fa68bda1 | grid_fee.py:383 | True (RED-AS-NULL) | - | 3122.9 | 0.86..0.92 | gated on box D3-rem |
| c3c6:a4b00ac3ca662eec | thermal_model.py:835 | True (RED-AS-NULL) | - | 3133.2 | 0.72..0.86 | gated on box D3-rem |

Null control on this box: gate_rc=1 on artefact checks only (state/gates/null-D3-rem-note.txt); RED-AS-NULL = no script fails more checks than the null.

## T2 probes

| mutant | site | probe command | baseline value | mutant value | null delta | finding-or-non-finding |
|---|---|---|---|---|---|---|
| 0c3e91a6a349409a | flow_lift.py:47 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_0c3e91a6.py` | bias=3.638040 K | bias=4.689280 K | 0.0 K | D3-s1-65 |
| 3885e472b8297a90 | flow_lift.py:183 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_3885e472.py` | bias=2.0 K samples=3 | bias=nan K samples=4 | 0.0 K | non-finding (unreachable through production) |
| a0b3b28854fa500c | flow_lift.py:188 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_a0b3b288.py` | bias=3.000000 K | bias=3.666667 K | 0.0 K | D3-s1-66 |
| 050fdc4a20eba212 | thermal_model.py:169 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_050fdc4a.py` | holiday windows (option absent/''/None)=None | [] for all 3 unset forms | 0 count | D3-s1-67 |
| 22b5ec8775d5bd50 | thermal_model.py:2593 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_22b5ec87.py` | delivered=0.278400 kW | delivered=2.800000 kW | 0.0 kW | D3-s1-68 |
| a4b00ac3ca662eec | thermal_model.py:835 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_a4b00ac3.py` | seasonal inlet at swing=0 equals dhw_inlet_temp | identical | 0.0 C (swing 3 and negative) | non-finding (equivalent mutant) |
| 121362d48b408236 | grid_fee.py:173 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_121362d4.py` | rules=-1 (GridFeeError), verdict invalid_grid_fee_rules | rules=1 parsed, verdict None | 0 count | D3-s1-62 |
| 95779f9d6d71c50d | grid_fee.py:355 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_95779f9d.py` | max_abs_component source label=fixed | label=rules | 0 count (rule-rule tie and untied) | D3-s1-63 |
| 2719aef4cbb8b464 | price_model.py:337 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_2719aef4.py` | expected_daily_min(level=0)=None | 0.0 | 0.0 | non-finding (unreachable through production) |
| 460217277822d5bd | sysid.py:610 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_46021727.py` | slab_mode_tau_fast=0.0 h on degenerate inputs | 1.33e10 h (k_s tiny), ZeroDivisionError (k_s=0), -2.0 h (c_r<0) | 0.0 h | non-finding (unreachable through production) |
| 65f121eb047174ad | optimizer.py:773 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_65f121eb.py` | _holiday_flags_for(empty)=None | [False]*n | 0 count | non-finding (equivalent at the observable output) |
| 0911281eca895664 | dhw_planner.py:1559 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_0911281e.py` | dhw_kwh=2.5056 kWh | dhw_kwh=1.9948 kWh | 0.000000 kWh | D3-s1-69 |
| 5e8d48eff7e4fa8d | coordinator.py:8806 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_5e8d48ef.py` | (5.0,10.0) suppressing=False in both cases | enabled,factor0: (0.0,3.0); disabled,factor1: (5.0,3.0) suppressing=True | 0 count | D3-s1-70 |
| 5cc84148fa68bda1 | grid_fee.py:383 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_5cc84148.py` | min_component label=fixed | label=rules | 0 count | D3-s1-64 |
| c38d53ab787ddbfa | price_model.py:252 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/probe_c38d53ab.py` | accepted=0 | accepted=1 | 0 count | D3-s1-71 |

## D3.M4 answers (production line, file, the check that should have failed)

- 0c3e91a6a349409a flow_lift.py:47: flow_lift:FLOW_BIAS_ALPHA read in FlowCurveBias.observe (lines 194-195). Should have failed: tests/doc_claims.py:1949-1956 reads the constant instead of pinning 0.1; tests/features.py exercises the symbol
- 3885e472b8297a90 flow_lift.py:183: flow_lift:FlowCurveBias.observe line 183 non-finite guard. Should have failed: none through production; only a direct unit call separates
- a0b3b28854fa500c flow_lift.py:188: flow_lift:FlowCurveBias.observe line 188 warm-up boundary. Should have failed: tests/doc_claims.py:1949-1956 loops FLOW_BIAS_MIN_SAMPLES samples but never folds one past the boundary
- 050fdc4a20eba212 thermal_model.py:169: thermal_model:_holiday_dhw_windows line 169, reached via ThermalParameters.from_config (thermal_model.py:1157); dhw_planner.py:964 reads it. Should have failed: tests/features.py (dhw_holiday_windows) / tests/config_flow_steps.py do not pin None for the unset option
- 22b5ec8775d5bd50 thermal_model.py:2593: thermal_model:_valve_two_zone_delivery single-tank branch line 2593, via simulate_step -> _simulate_step_two_zone (thermal_model.py:3963). Should have failed: no tank-energy bound check in tests/edge.py or tests/block_duty.py (both drive mixing_valve_mode) pins the delivered-heat cap
- a4b00ac3ca662eec thermal_model.py:835: thermal_model:ThermalParameters.seasonal_inlet_temp line 835. Should have failed: none: at swing==0 the fall-through returns dhw_inlet_temp - 0.0*cos(phase) == dhw_inlet_temp; max_abs_delta_swing0=0.0 over days 1..366, means 4/10/15 C
- 121362d48b408236 grid_fee.py:173: grid_fee:_parse_rule line 173 (missing '=' guard). Should have failed: tests/features.py bad-rule cases (~17831-17847) never feed a rule with no '='
- 95779f9d6d71c50d grid_fee.py:355: grid_fee:GridFeeSchedule.max_abs_component line 355. Should have failed: tests/features.py has no fixed/rule tie case for max_abs_component
- 2719aef4cbb8b464 price_model.py:337: price_model:expected_daily_min line 337. Should have failed: none through production; a direct unit call at level==0 separates
- 460217277822d5bd sysid.py:610: sysid:slab_mode_tau_fast line 610. Should have failed: none through production; tests/features.py:53975 pins (0,1,1)->0.0 which the mutant also returns
- 65f121eb047174ad optimizer.py:773: optimizer:_holiday_flags_for line 773. Should have failed: none: no observable output moves
- 0911281eca895664 dhw_planner.py:1559: dhw_planner:DhwPlanner._plan_dhw_min_cost line 1559 (call site dhw_planner.py:1235). Should have failed: tests/features.py _plan_dhw_min_cost cases (~63150, 63611, 63732) never use a spread large enough to make the shortfall penalty bind
- 5e8d48eff7e4fa8d coordinator.py:8806: coordinator:HeatPumpOptimizerCoordinator._on_power_event line 8806. Should have failed: tests/features.py, tests/dst_checks.py, tests/entities.py reference _on_power_event but cover neither case
- 5cc84148fa68bda1 grid_fee.py:383: grid_fee:GridFeeSchedule.min_component line 383. Should have failed: tests/features.py ~17746-17766 has no tie case
- c38d53ab787ddbfa price_model.py:252: price_model:PriceShapeModel.observe_day_quarters line 252 (via fold, price_model.py:452). Should have failed: tests/features.py ~18732-18792 has no zero-mean boundary case

## Findings

- D3-s1-62: No check feeds a grid-fee rule without '=' to _parse_rule; dropping the guard is unseen
- D3-s1-63: No check pins max_abs_component's source label on a fixed/rule |rate| tie
- D3-s1-64: No check pins min_component's source label on a fixed/rule rate tie
- D3-s1-65: No check pins FLOW_BIAS_ALPHA's value; doubling the flow-bias EWMA weight is unseen
- D3-s1-66: No check folds the sample one past FLOW_BIAS_MIN_SAMPLES; the warm-up boundary is unpinned
- D3-s1-67: No check pins that an unset holiday-DHW-windows option parses to None, not []
- D3-s1-68: No check bounds single-tank valve delivery by the tank energy over dt; max->min is unseen
- D3-s1-69: No check makes the DHW shortfall penalty bind; its max->min price base is unseen
- D3-s1-70: No check covers _on_power_event with the tariff disabled or its factor 0; and->or is unseen
- D3-s1-71: No check feeds observe_day_quarters a day whose mean is exactly 1e-6
