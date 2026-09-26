# [R9-EXPLICIT-EULER-STABILITY-JUDGED-PER-STORE-INSTEAD-OF-ON-THE-COUPLED-STEP-MATRIX] explicit-Euler stability judged per store instead of on the coupled step matrix

**Class `explicit-euler-stability-judged-per-store-instead-of-on-the-coupled-step-matrix`.** explicit-Euler stability judged per store instead of on the coupled step matrix. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D2-s1-01 | `custom_components/heatpump_optimizer/thermal_model.py` | medium | Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D2-s1-01: also `custom_components/heatpump_optimizer/thermal_model.py:2419-2470 (_stability_substeps)`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D2-s1-01**: `PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D2/s1/m1_stability.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): judge the coupled step matrix, or at minimum the valve-throttled buffer<->zone pair

## Fix

Fix: see round-9 fix plan.

