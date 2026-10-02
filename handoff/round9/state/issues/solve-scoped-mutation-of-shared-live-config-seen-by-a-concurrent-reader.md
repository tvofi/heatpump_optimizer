# [R9-SOLVE-SCOPED-MUTATION-OF-SHARED-LIVE-CONFIG-SEEN-BY-A-CONCURRENT-READER] solve-scoped mutation of shared live config seen by a concurrent reader

**Class `solve-scoped-mutation-of-shared-live-config-seen-by-a-concurrent-reader`.** solve-scoped mutation of shared live config seen by a concurrent reader. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s3-04 | `custom_components/heatpump_optimizer/climate.py` | low | Climate entity publishes the away setback as the user's target while the solve is in the executor |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s3-04: also `custom_components/heatpump_optimizer/climate.py:157 / coordinator.py:2495-2498 (target_temperature)`, `custom_components/heatpump_optimizer/away.py`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s3-04**: `rg -n "_opt_config\.|target_temperature" custom_components/heatpump_optimizer/{climate,sensor,binary_sensor,entity}.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): publish target_temperature from the same per-cycle coordinator.data snapshot every other entity reads

## Fix

Fix: see round-9 fix plan.

