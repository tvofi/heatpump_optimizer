# D2-s2 — round 11, D2.M2 (COP and derates), baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692

Seat D2-s2, box B5. Cells: `{"files":["**"],"steps":["M2"]}`: 95 production files (from
`check_scopes.py --seat D2-s2`, run against the git checkout at the baseline SHA because the
export has no `.git`) and the 39 M2 identity cells of `enumerate.py d2-identities --cells`.
Exposure: none (I read no docs/, no GitHub, no earlier-round records).

## Method

The work started with redispatch item C1 (the capacity envelope and the Carnot band).

| harness | cells | production symbols driven |
|---|---|---|
| `m2_cop_laws.py [--perturb=lift\|defrost]` | cop-monotone, carnot-band, derate-unit-interval × 5 climates | `ThermalModel.compute_cop`, `compute_cop_dhw`, `flow_lift_factor`, `_batch_cop`, `partload_factor`, `DefrostDerate.factor`, `defrost.derate_from_duty` |
| `m2_capacity_envelope.py [--perturb] [--delivered=0.6]` | capacity-envelope × 15 (climate × compressor_modulation), C1 | `coordinator._fold_capacity_envelope`, `_capacity_caps`, `HeatPumpOptimizer.optimize` (power_caps_extra, `power_cap_breach_c`) |
| `m2_priced_surface.py [--perturb]` | priced-inputs-surface × 9 (space_setpoint_unit × compressor_modulation) | `thermal_model.declared_modulation`, `OptimizationConfig.from_mapping`, `HeatPumpOptimizer.optimize` |
| `m2_file_census.py` | the 95-file axis | coverage record: it hooks no symbol |

Climates are the `tests/profiles.py` weather profiles (winter_cold, winter_mild, summer_warm,
summer_cool, shoulder). Each perturbation is a one-line edit applied to a private copy of the
package under a tempfile root, or an in-memory constant swap for the envelope floor.

## Findings

- **D2-s2-01 (critical, P2?)**: the scalar `flow_lift_factor` is inverted. It returns
  `carnot_ref/carnot_flow`, which is greater than 1 above 35 °C, so COP rises with flow and tank
  temperature: 31330 rising pairs per climate, 156650 in total, and lift up to 2.02×. Hot water
  at 55 °C is priced at 1.34–1.61× the space COP; corrected, it is 0.62–0.75×. The Carnot
  fraction goes above 1 at 21320 points. The batch twin uses `carnot_flow/carnot_ref`, so scalar
  and batch differ by up to 8.01 COP units. With `--perturb=lift`, every one of these counts
  drops to 0.
- **D2-s2-02 (high, new)**: `defrost.derate_from_duty` computes `1 + duty·1.5` and then clamps
  the result to 1.0. The documented law is `1 − duty·1.5`. The function disagrees with it at 60
  of 61 duty points. A fully trusted 20 % duty therefore leaves frost-band COP at 1.0× when it
  should be 0.70×; this holds on winter_mild (73 frost steps) and shoulder (41). With
  `--perturb=defrost` the count goes to 0 and the ratio to 0.70.
- **D2-s2-03 (high, new)**: `declared_modulation` maps `on_off` to True, which means
  modulating. A declared on/off pump is therefore never clamped: 3 of 9 cells mismatch, and the
  solve plans 32 of 96 steps in (0, p_min). On the same surface, `auto` clamps and plans 0 such
  steps. With `--perturb` both counts go to 0.

The full blocks are in `findings/D2-s2-0{1,2,3}.json`.

## Priced-formula inputs and where each comes from (priced-inputs-surface)

| input | source | mark |
|---|---|---|
| cop_nominal, max/min electrical power | config (nameplate) | documented constant (user) |
| cop_reference_temp 7 °C, slope 0.025/K, factor floor 0.3 and cap 1.5, resistive floor 1.0 | code | documented constant |
| cop_flow_reference_temp 35 °C (W35) | code | documented constant |
| cop_scale | learned from measured power | modelled term |
| defrost derate | learned; the measured estimator reads the pump's own defrost flag | modelled term (D2-s2-02) |
| humidity | forecast or ambient | modelled input |
| flow temperature | valve: the tank state; direct plant: the weather curve when `flow_curve_cop_enabled` is set, otherwise unpriced | modelled term, not taken from the written flow set-point (lead 3) |
| part-load derate | config, default 0 | documented constant (user) |
| level law (clamp to {0} ∪ [p_min, p_max]) | the declared `compressor_modulation`, otherwise the install probe | surface-derived (D2-s2-03) |
| space_setpoint_unit | feeds only the arbiter (`flow_setpoint_driven`), not the priced COP | out of scope for the price |

## Non-findings

- COP never falls as outdoor temperature rises, in every model and every climate (0).
- Every derate stays in [0, 1], and the defrost factor is continuous at every bucket edge and
  both frost-band edges (0 violations, 0 jumps).
- C1, Carnot band: the tree states no band; a grep of `*.py`, `*.md` and `*.json` found none.
  Against the physical bound (0, 1], the only violations are D2-s2-01's. With the lift
  corrected, the fraction spans 0.016–0.335.
- C1, capacity envelope: in all 15 cells, `unexplained` is 0. Steps where the cap's heat falls
  below steady demand number 69 at 0.8 delivered and 141 at 0.6; in each case the plan
  pre-heats, and `power_cap_breach_c` is published whenever caps are in force. With
  `--perturb` (floor fraction 1.0), below_steps goes to 0.
- The COP law has a single source: only `thermal_model.py` carries the slope and the Carnot
  offset (1 of 95 files).

## Unfinished

None. The universe is 134 lines (95 files and 39 cells), and all 134 were examined.

All numbers are counts or ratios: contention-immune, thread_factor 1.0, load1 0.3–1.6.
