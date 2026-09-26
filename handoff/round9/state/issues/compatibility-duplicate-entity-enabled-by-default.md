# [R9-COMPATIBILITY-DUPLICATE-ENTITY-ENABLED-BY-DEFAULT] compatibility duplicate entity enabled by default

**Class `compatibility-duplicate-entity-enabled-by-default`.** compatibility duplicate entity enabled by default. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D8-s3-03 | `custom_components/heatpump_optimizer/sensor.py` | low | Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D8-s3-03: also `custom_components/heatpump_optimizer/sensor.py:918-958 (UpperFloorTempSensor)`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/sensor.py:2174 (ContractComparisonSensor)` — not applicable: distinct computed value, regex false positive
- `custom_components/heatpump_optimizer/sensor.py:2329 (MixedHotWaterSensor)` — not applicable: derived transform, not a byte-duplicate, regex false positive

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D8-s3-03**: `PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m4_duplicates.py  (DUPLICATE_ENABLED lines)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): lint flagging any sensor whose native_value reads exactly the same coordinator.data key as another entity, with a positive allowlist for intentional duplicates

## Fix

Fix: see round-9 fix plan.

