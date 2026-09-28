# [R9-STATE-BLIND-MENU-RE-OFFERS-A-COMPLETED-PATH] state-blind menu re-offers a completed path

**Class `state-blind-menu-re-offers-a-completed-path`.** state-blind menu re-offers a completed path. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s2-07 | `custom_components/heatpump_optimizer/config_flow.py` | low | After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s2-07: also `custom_components/heatpump_optimizer/config_flow.py:2473-2493 (async_step_finish_setup)`, `custom_components/heatpump_optimizer/strings.json`, `custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/config_flow.py:~3123-3129 (options-flow 'missed quick setup' menu)` — guarded: conditioned on prior state per its own comment, different code path

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s2-07**: `tools/audit/round9/D4/s2/quick_menu.py (every hand-back to finish_setup; flow_rubric.py prints each first-run path's screen sequence)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): track whether quick setup already ran and drop that option from the menu

## Fix

Fix: see round-9 fix plan.

