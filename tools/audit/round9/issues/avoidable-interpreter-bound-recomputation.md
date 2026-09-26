# [R9-AVOIDABLE-INTERPRETER-BOUND-RECOMPUTATION] avoidable interpreter-bound recomputation in the solve

**Class `avoidable-interpreter-bound-recomputation`.** avoidable interpreter-bound recomputation in the solve. The mechanism the sweep confirms across 5 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 5 (4 judge-verified findings + 1 sweep-confirmed instance).

RCA: owed.

> Note: the judge's class table (`CLASSES-DRAFT.json`) recorded n=4, rca=True for this class; the class sweep (`S5.json`), run after the judge and enumerating every sibling seam, found N=5, rca=True. The sweep count is the one this issue uses, being the later, complete enumeration.

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D9-s1-01 | `custom_components/heatpump_optimizer/optimizer.py` | medium | Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here |
| D9-s1-02 | `custom_components/heatpump_optimizer/optimizer.py` | medium | L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve |
| D9-s1-04 | `custom_components/heatpump_optimizer/optimizer.py` | low | DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve |
| D9-s1-71 | `custom_components/heatpump_optimizer/thermal_model.py` | low | Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU |
| sweep | `thermal_model.py: ThermalParameters.{topology_layout,two_tank_modelled}` | (unrated) | new, low severity: cheap O(1) boolean derivations recomputed 100x/solve; negligible CPU despite meeting the class's literal shape |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D9-s1-01: also `optimizer.py:1889,1915 HeatPumpOptimizer._comfort_terms_batch`, `optimizer.py:819 cycling_penalty_batch`
- D9-s1-02: also `optimizer.py:_scoped_minimize scalar objective calls`
- D9-s1-04: also `optimizer.py:5584 HeatPumpOptimizer._clamp_dhw_to_capacity / DHW min-run repair`
- D9-s1-71: also `thermal_model.py: ThermalParameters.{dhw_tank_heat_loss_coefficient,dhw_inlet_reference,effective_dhw_draw_pattern}`, `thermal_model.py: ThermalParameters.{lower_floor_heat_loss_learned,buffer_tank_thermal_mass,buffer_tank_heat_loss_coefficient,dhw_tank_thermal_mass,dhw_hard_max_temp,dhw_windows_active}`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `34 other statically-reachable loops/properties` — not applicable: called O(1) times in the profiled solve: setup, bounded repair rounds, or post-solve reporting

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D9-s1-01**: `grep -n 'for b in range(n_rows)' custom_components/heatpump_optimizer/optimizer.py`
- **D9-s1-02**: `grep -n '_scoped_minimize(' custom_components/heatpump_optimizer/optimizer.py`
- **D9-s1-04**: `grep -n 'extend_dhw_temps(' custom_components/heatpump_optimizer/optimizer.py`
- **D9-s1-71**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_dhw_helpers.py  (seams = ThermalParameters properties/methods called from simulate_dhw_step and the DHW planners; count calls per solve)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S5.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

nightly ratchet: enumerate.py's dynamic call-count profiling asserting recompute_instances may only fall

## Fix

Fix: see round-9 fix plan.

