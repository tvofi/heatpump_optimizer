# D2-s1, round 11: D2.M1 (thermal model)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B4. Exposure: none. Full JSON: REPORT.json.

## Method
Universe `python3 tools/audit/enumerate.py d2-identities --cells | grep '^M1 '` = 227 cells (batch-parity x7,
buffer-cap-rate x5, energy-conservation/dt-invariance/power-monotone/store-bounds x50 golden each,
switch-back-slab x15). File bound: check_scopes.py --seat D2-s1 = 95 files x M1. All 227 executed.

- batch_parity.py: simulate_trajectory per row vs simulate_trajectory_batch, 26 arms (1z/2z).
- buffer_cap_rate.py: every layout, scalar + batch, 0.25/1 h, tank above and crossing the cap; DHW store_step.
- golden_identities.py: the published simulate_trajectory(_with_dhw) call of every golden.capture (50/50),
  replayed under wrappers of _simulate_step_single/_two_zone, simulate_dhw_step, apply_dhw_coil,
  mixing_valve.emitter_delivery, flow_lift_factor. Logs in runs/.
- switch_back_slab.py: coordinator _update_current_state -> _propagated_slab (features.py rig copied).
Single-zone arms pin two_zone_mode="off" (the default resolves to two-zone at this baseline; lead).

C1 (redispatched, examined): store bounds on every golden trajectory in fixture, fresh capture and replay:
0 samples out of bound. measured_heat_kw has no batch input; conservation (4.8e-14 kWh) and +1 kW
monotonicity (0 violations) of simulate_step with it were executed on every golden step instead.

## Findings
- D2-s1-01 (critical): ThermalModel.flow_lift_factor returns carnot_ref/carnot_flow, so a hotter flow
  raises COP (1.586 at 60 C); the batch twin uses carnot_flow/carnot_ref. 14 897 parity mismatches;
  1268 lift>1 calls on golden plans; DHW COP 2.89 at 35 C vs 4.26 at 55 C. --fix-lift -> 0 on those arms.
- D2-s1-02 (high): mixing_valve.emitter_delivery lacks its documented max(0,.); a tank colder than a zone
  cools the zones in the scalar two-zone valve step. 3674 parity mismatches after 01 is corrected;
  496 reverse deliveries / 87.52 kWh over 9 valved golden plans (LOO 30.2 kWh). --fix-emitter -> 0.

## Non-findings
Conservation <= 4.2e-14 kWh; store bounds 0; cap-as-rate 0/44; dt-invariance convergent (5 valve/wood
blocks with weakened local order, ratio <= 1.94; harness gap named: lone 1 h vs 15 min reads cancellation);
power-monotone holds except the wood tank under the documented 4-way blend law (physical, worst 0.0049 K);
switch-back slab 0/15 (9 tank-buffered cells cannot separate: slab fed from tank's opening temperature).

## Leads
D2-s2 COP increasing in flow temp; unknown two_zone_mode 'auto' forces two-zone; D2-s3 fresh goldens vs
fixtures diverge; unknown _propagated_slab inert behind a valve.

## Unfinished
None. Wall times provisional (full golden run ~12 min at load1 ~3.5).
