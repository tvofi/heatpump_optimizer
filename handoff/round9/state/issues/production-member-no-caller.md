# [R9-PRODUCTION-MEMBER-NO-CALLER] production member reached by no production code

**Class `production-member-no-caller`.** production member reached by no production code. The mechanism the sweep confirms across 2 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 2 (2 judge-verified findings + 7 sweep-confirmed instances).

RCA: not triggered (N=2).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D7-s3-01 | `custom_components/heatpump_optimizer/coordinator.py` | low | 10 class members are reached by no production code; 9 are kept only by tests that pin them |
| D7-s3-72 | `custom_components/heatpump_optimizer/thermal_model.py` | low | 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:2422,2543,2414,2418` | (unrated) | 4 dead properties, static+dynamic |
| sweep | `custom_components/heatpump_optimizer/defrost.py:327` | (unrated) | DefrostDerate.measured dead |
| sweep | `custom_components/heatpump_optimizer/inputs.py:147` | (unrated) | InputHealth.healthy dead |
| sweep | `custom_components/heatpump_optimizer/open_meteo.py:108,273` | (unrated) | IrradianceSeries.start, OpenMeteoSolar.last_success dead |
| sweep | `custom_components/heatpump_optimizer/optimizer.py:1484` | (unrated) | _Horizon.weather dead |
| sweep | `custom_components/heatpump_optimizer/defrost.py (DefrostDerate.samples)` | (unrated) | invisible to static reach.py due to name collision with AccuracyTracker.samples |
| sweep | `custom_components/heatpump_optimizer/thermal_model.py (_step_dhw_refused, _step_dhw_floor_injected, _step_dhw_draw_kw, _step_wood_refused)` | (unrated) | write_only=True, zero consumer reads |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D7-s3-01: also `custom_components/heatpump_optimizer/inputs.py`, `custom_components/heatpump_optimizer/optimizer.py`, `custom_components/heatpump_optimizer/defrost.py`, `tests/features.py`, `tests/open_meteo.py`, `custom_components/heatpump_optimizer/open_meteo.py`
- D7-s3-72: also `tests/features.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/thermal_model.py (_step_buffer_refused)` — not applicable: write_only=False -- read by simulate_trajectory

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D7-s3-01**: `tools/audit/round9/D7/s3/reach.py --list (lists 9 of the 10; DefrostDerate.samples is kept alive in every name-based view by the AccuracyTracker.samples field collision, and only sentinel.py shows it dead)`
- **D7-s3-72**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py  (members = ThermalModel class attributes named _step_*; extend to any attribute with production stores and no production loads)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

Fold reach.py's static scan plus a dynamic sentinel smoke pass into tests/structure.py's dead-code metric, replacing the property-skipping method screen; add the write-only-scratch check as a second metric.

## Fix

Fix: see round-9 fix plan.

