# [R9-STALENESS-LIMIT-SHORTER-THAN-QUIET-INTERVAL] staleness limit shorter than a report-on-change sensor's quiet interval

**Class `staleness-limit-shorter-than-quiet-interval`.** staleness limit shorter than a report-on-change sensor's quiet interval. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 2 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s5-51 | `custom_components/heatpump_optimizer/inputs.py` | medium | A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable |
| sweep | `custom_components/heatpump_optimizer/sensor.py:647,944 (IndoorTempSensor / upper_floor_temperature)` | (unrated) | unavailable=4 of 7 silence cells (61/90/240/480 min) |
| sweep | `custom_components/heatpump_optimizer/sensor.py:753,982,1015,1080,1118,2350 (slab/lower-floor/floor-return/buffer-tank/dhw temperatures)` | (unrated) | same _age_gate mechanism, same class of 60-min-limited temperature entity |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s5-51: also `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/const.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/const.py (CONF_HEAT_PUMP_ONLINE_ENTITY)` — guarded: explicitly documented as written every poll cycle, not report-on-change
- `custom_components/heatpump_optimizer/const.py (outdoor temp, solar, energy, mode/fault horizons)` — not applicable: each carries its own deliberate generous-horizon reasoning
- `custom_components/heatpump_optimizer/const.py (defrost, backup heater, dhw booster, capacity limited, supply/return temp, PV production, power entities)` — not applicable: documented as fast-moving signals, opposite regime from this class

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s5-51**: `grep -n 'INPUT_MAX_AGE_MINUTES' custom_components/heatpump_optimizer/const.py (every keyed limit) plus grep -n '_reading_key' custom_components/heatpump_optimizer/sensor.py (every entity whose availability follows one); harness: tools/audit/round9/D1/leads/indoor_silence.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1; fix is a design decision (honour last_reported for report-on-change sources).

## Fix

Fix: see round-9 fix plan.

