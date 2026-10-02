# [R9-MISSING-ICONS-JSON-SERVICES-BLOCK] missing icons.json services block

**Class `missing-icons-json-services-block`.** missing icons.json services block. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s2-08 | `custom_components/heatpump_optimizer/icons.json` | low | None of the 12 registered services has an icon in icons.json |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s2-08: also `custom_components/heatpump_optimizer/services.py (12 registered services)`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s2-08**: `tools/audit/round9/D4/s2/service_icons.py (enumerates the services the production registration delivers)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): tests/ check asserting every registered service has a matching icons.json["services"] key

## Fix

Fix: see round-9 fix plan.

