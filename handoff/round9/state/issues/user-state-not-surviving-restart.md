# [R9-USER-STATE-NOT-SURVIVING-RESTART] user state not surviving restart

**Class `user-state-not-surviving-restart`.** user state not surviving restart. The mechanism the sweep confirms across 2 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 2 (2 judge-verified findings + 0 sweep-confirmed instances).

RCA: owed.

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s2-52 | `custom_components/heatpump_optimizer/coordinator.py` | medium | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state |
| D1-s2-53 | `custom_components/heatpump_optimizer/coordinator.py` | medium | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s2-52: also `coordinator.py: 5 store writers (energy_totals, ledger, thermal_learning, price_model, accuracy)`, `custom_components/heatpump_optimizer/store.py`
- D1-s2-53: also `coordinator.py:async_update_thermal_params, 24 of 26 fields`, `custom_components/heatpump_optimizer/services.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `coordinator.py:async_set_mode` — guarded: the one writer that already awaits its store's read before writing

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s2-52**: `grep -nE 'async_save\(|_async_save_if_changed\(' custom_components/heatpump_optimizer/coordinator.py (every writer of a store whose loader is in the __init__ _spawn(load()) tuple, coordinator.py:1862-1876); harness: tools/audit/round9/D1/leads/startup_clobber.py`
- **D1-s2-53**: `grep -n '_THERMAL_PARAM_FIELDS\|async def async_update_thermal_params' custom_components/heatpump_optimizer/coordinator.py plus services.py SERVICE_SCHEMA_SET_THERMAL_PARAMS keys; harness: tools/audit/round9/D1/leads/runtime_params_restart.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S5.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

2 targeted fixes matching RC2's own pattern: await async_wait_for_read() at each of the 5 writer call sites (D1-s2-52); persist the 24 set_thermal_parameters fields through entry.options (D1-s2-53). Each barriered by its own enumerator asserting lost==0

## Fix

Fix: see round-9 fix plan.

