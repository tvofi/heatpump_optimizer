# [R9-LIVE-INPUT-NO-PLAUSIBILITY-BOUND] live input with no physical-plausibility bound

**Class `live-input-no-plausibility-bound`.** live input with no physical-plausibility bound. The mechanism the sweep confirms across 2 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 2 (2 judge-verified findings + 2 sweep-confirmed instances).

RCA: not triggered (N=2).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s1-03 | `custom_components/heatpump_optimizer/dhw_learning.py` | medium | One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90 |
| D1-s2-02 | `custom_components/heatpump_optimizer/coordinator.py` | medium | Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve |
| sweep | `custom_components/heatpump_optimizer/dhw_learning.py:389-390` | (unrated) | max(0.0,...) floor only, no ceiling/finite check |
| sweep | `custom_components/heatpump_optimizer/coordinator.py+thermal_model.py (weather/ECL110 parsers)` | (unrated) | poisoned_series=8/200 at baseline |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s2-02: also `custom_components/heatpump_optimizer/thermal_model.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/coordinator.py:8245` — guarded: bound-checked: 0.0 < value <= 100.0, isfinite
- `custom_components/heatpump_optimizer/coordinator.py:8957` — guarded: bound-checked: isfinite + max(0.0, converted)

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s1-03**: `grep -n "temp_drop\|energy_kwh" custom_components/heatpump_optimizer/dhw_learning.py`
- **D1-s2-02**: `tools/audit/round9/D1/s2/parsers.py --n 200 (weather.poisoned_series counts the series the solve receives out of range: 8 of 200)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

Require every function parsing a live entity's .state to float, or folding two such parses, to be followed by an isfinite/range check before storage or use by a learner.

## Fix

Fix: see round-9 fix plan.

