# D3-s1 box D3-g46-h (helper half of D3-g46): full gate for 6 D3.M3 survivors

Machine: 4 vCPU Intel Xeon @ 2.30GHz, 16 GB, load1 about 1 (see wave/D3-g46-h/MACHINE.txt); every wall/CPU/load figure provisional. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. This is the helper half of box D3-g46; the main box gates rows 1-9.

Null control (comment-only marker): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py']: artefact checks (untracked wave files and probes in the tree), the same scripts as D3-top6's null; not re-taken.

Tally: gated 6; RED-AS-NULL=6; candidates 2; equivalent-candidates 4; KILLED 0; TIMEOUT 0.

## a087d5efb15533ce — custom_components/heatpump_optimizer/thermal_model.py:2598 CMP_BOUND — RED-AS-NULL — candidate
`elif available <= 0.0: -> elif available < 0.0:`. Gate wall 2761.1 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_a087d5efb15533ce.py`: baseline delivered_kw=0.0; mutant delivered_kw=5.2333333333333325. Inputs: available == 0.0 exactly (tp=0, q_buf_loss=stored energy, T_buf 40, floor 21, dt 0.25); null: available strictly <0 and >0 (delta 0.0). Should fail: tests/features.py (and tests/validate.py): no check of _valve_two_zone_delivery's single-tank branch at available == 0 exactly asserts that a store with zero available energy delivers zero heat to the emitters.

## efd15cba428cdcf2 — custom_components/heatpump_optimizer/thermal_model.py:2939 CMP_BOUND — RED-AS-NULL — equivalent-candidate
`r2 = (~r1) & (hp_temp > flow_set) -> r2 = (~r1) & (hp_temp >= flow_set)`. Gate wall 2660.6 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_efd15cba428cdcf2.py`: baseline max_abs_diff=0.0; mutant max_abs_diff=0.0. Inputs: 1440 vectors: flow_set 30/35.5/45, floor 15/22/29, wood 40 values from 5 to flow-1e-9, margin 1e-6/1/default/10, hp_temp == flow_set exactly; both regions give 0.0 at the tie (hotter=0 because wood<hp, hp_deficiency=0 -> share 0; v2: f_w=0). Should fail: none: continuous at the tie.

## 968644425a4f97f8 — custom_components/heatpump_optimizer/thermal_model.py:2946 CLAMP_DROP — RED-AS-NULL — candidate
`span = np.maximum(flow_set - floor_temp, 1e-6) -> span = (flow_set - floor_temp)`. Gate wall 2692.8 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_968644425a4f97f8.py`: baseline share=0.0 (tie: floor_temp == flow_set); mutant share=nan. Inputs: wood 30, hp 40, flow_set 35, floor 35 -> mutant nan; floor 37 -> -0.0 (equal value); floor 30 (null) -> equal. Should fail: tests/features.py / tests/env_drift.py: no scalar-vs-vector identity check of wood_share vs _wood_share_vec at floor_temp == flow_set (span 0), nor a finiteness check of the vector share.

## c9a7d4d29d08c3b4 — custom_components/heatpump_optimizer/thermal_model.py:2952 CLAMP_DROP — RED-AS-NULL — equivalent-candidate
`m = max(margin, 1e-6) -> m = (margin)`. Gate wall 2735.9 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_c9a7d4d29d08c3b4.py`: baseline share=0.0 (margin 0); mutant share=nan (margin 0, direct call). Inputs: margin=0.0 direct call: wood==hp==30, flow 35, floor 20 -> baseline 0.0, mutant nan; default margin WOOD_TANK_MIN_MARGIN > 1e-6 (null delta 0.0). Sole production caller (thermal_model.py:4685) passes no margin, so the clamp is dead there. Should fail: none through production; a direct margin=0 unit check would kill it.

## ca6ae797caf18708 — custom_components/heatpump_optimizer/thermal_model.py:2827 CLAMP_DROP — RED-AS-NULL — equivalent-candidate
`ln = math.log(max(vapor_pressure_hpa, 1e-9) / 6.112) -> ln = math.log((vapor_pressure_hpa) / 6.112)`. Gate wall 2704.4 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_ca6ae797caf18708.py`: baseline dew point -136.435 C at 0.0 hPa; mutant ValueError at 0.0 / negative hPa (direct call). Inputs: direct 0.0, -1.0, 1e-12, 10 hPa; via mold_safe_room_floor rh 0, 1e-9, 1e-6: identical (-100.0, -100.0, -169.82), because the caller returns early at e <= 1e-9 (line 2854) and the argument is then >= 1e-9. Should fail: none through production; a direct dew_point_for_pressure(0.0) check would kill it.

## 449caa49315447b2 — custom_components/heatpump_optimizer/thermal_model.py:2998 GUARD_OFF — RED-AS-NULL — equivalent-candidate
`if draw_kw <= 0.0: -> if False:`. Gate wall 2703.8 s (provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_449caa49315447b2.py`: baseline (-1.5, 0.0) for draw -1.5, wood 60; mutant (-0.6667, -0.8333) for draw -1.5, wood 60 (direct call). Inputs: draw 0.0, -0.0, nan, 2.0 (null) at wood 60 and 10: identical; only a negative draw at hot wood differs. Callers pass non-negative draw rates (dhw_planner.py:926, thermal_model.py:5009); negative reachability not shown. Should fail: none shown through production; a direct negative-draw check would kill it.
