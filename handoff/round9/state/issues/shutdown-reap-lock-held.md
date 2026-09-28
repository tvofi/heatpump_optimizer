# [R9-SHUTDOWN-REAP-LOCK-HELD] shutdown reap waits on the lock a solve holds

**Class `shutdown-reap-lock-held`.** shutdown reap waits on the lock a solve holds. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s2-05 | `custom_components/heatpump_optimizer/coordinator.py` | medium | Home Assistant stop waits out an in-flight solve before reaping the solve worker |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:968,1047,1094` | (unrated) | the package's only lock; shutdown reap waits behind a long-held solve |

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s2-05**: `grep -n '_PROCESS_LOCK' custom_components/heatpump_optimizer/coordinator.py (3 sites: definition, _shutdown_process_pool, _run_in_process)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1; the package's only lock.

## Fix

Fix: see round-9 fix plan.

