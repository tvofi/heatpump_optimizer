# [R9-STRUCTURE-METRIC-BLIND-TO-SHAPE] structure metric blind to a code shape

**Class `structure-metric-blind-to-shape`.** structure metric blind to a code shape. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 6 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D7-s1-01 | `tests/structure.py` | low | Structural ratchet does not price coordinator state reached via module-level _helper(self, ...) |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_republish_handover_ages)` | (unrated) | cut_delta=12 |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_fold_flow_lift)` | (unrated) | cut_delta=8, the finding's headline cell |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_diagnose_payload)` | (unrated) | cut_delta=5 |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_power_windows, _watch_lift)` | (unrated) | cut_delta=3 each |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_cop_fold_blocked, _freq_fold_blocked)` | (unrated) | cut_delta=2 each |
| sweep | `custom_components/heatpump_optimizer/coordinator.py (_store_diagnosis)` | (unrated) | cut_delta=1 |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D7-s1-01: also `custom_components/heatpump_optimizer/wood_fuel.py`, `custom_components/heatpump_optimizer/coordinator.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/coordinator.py (_space_pump_to_drive, _warm_seeded)` — guarded: cut_delta=0, references cross no missed seam
- `custom_components/heatpump_optimizer/wood_fuel.py (wood_fuel_from_coordinator)` — not applicable: outside the coordinator-inlining transform's 10-cell grid

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D7-s1-01**: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/s1/helper_escape.py  (prints every module-level function called with self and its uncounted refs; --all runs the leave-one-out)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

Extend tests/structure.py to resolve a module-level function's first self-like parameter to its class and count state refs/internal calls against that class's metrics.

## Fix

Fix: see round-9 fix plan.

