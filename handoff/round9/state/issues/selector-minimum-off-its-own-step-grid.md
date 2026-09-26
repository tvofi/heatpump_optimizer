# [R9-SELECTOR-MINIMUM-OFF-ITS-OWN-STEP-GRID] selector minimum off its own step grid

**Class `selector-minimum-off-its-own-step-grid`.** selector minimum off its own step grid. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s2-05 | `custom_components/heatpump_optimizer/config_flow.py` | low | 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5 |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s2-05: also `custom_components/heatpump_optimizer/config_flow.py (8 box-mode NumberSelector fields at defaults)`, `custom_components/heatpump_optimizer/config_flow.py (4 more once derived values are stored)`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/config_flow.py (42 slider-mode fields)` — not applicable: sliders render no <input type=number>, stepMismatch cannot apply

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s2-05**: `tools/audit/round9/D4/s2/step_grid.py (enumerates every rendered NumberSelector of both flows, defaults and derived arm)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): config_flow._number sets step='any' for box fields, or move each RANGE_* minimum onto its step grid

## Fix

Fix: see round-9 fix plan.

