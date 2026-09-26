# [R9-WHOLE-ENTITY-AVAILABILITY-GATED-ON-AN-OPTIONAL-INPUT] whole-entity availability gated on an optional input

**Class `whole-entity-availability-gated-on-an-optional-input`.** whole-entity availability gated on an optional input. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D8-s2-01 | `custom_components/heatpump_optimizer/climate.py` | medium | Climate entity is unavailable with no indoor thermometer, taking the thermostat control with it |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D8-s2-01: also `custom_components/heatpump_optimizer/climate.py:122-131 (available)`, `tests/entities.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/button.py:83 (available, optimization_running)` — not applicable: coordinator-state gate, not an optional-input gate
- `custom_components/heatpump_optimizer/button.py:112 (available, system_identification_active)` — not applicable: same, different mechanism

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D8-s2-01**: `grep -n "def available" -A8 custom_components/heatpump_optimizer/climate.py custom_components/heatpump_optimizer/switch.py custom_components/heatpump_optimizer/button.py | grep reading_ok`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): drop the whole-entity gate, let current_temperature alone go unknown

## Fix

Fix: see round-9 fix plan.

