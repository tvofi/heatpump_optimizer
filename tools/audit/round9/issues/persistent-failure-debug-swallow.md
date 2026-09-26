# [R9-PERSISTENT-FAILURE-DEBUG-SWALLOW] persistent failure swallowed at DEBUG

**Class `persistent-failure-debug-swallow`.** persistent failure swallowed at DEBUG. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s2-04 | `custom_components/heatpump_optimizer/coordinator.py` | medium | Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:4662,4667,4682,5087,5094` | (unrated) | silent_sites=5 of 5 on 3 cycles each |

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/coordinator.py:2444,4525` — guarded: explicitly best-effort, one-shot setup, not per-cycle
- `custom_components/heatpump_optimizer/coordinator.py:2849,3128,4287,4463,7168,7192,7199,7259,7266,7321,7327,7366,7395,7423,8898,8911` — guarded: storage I/O, explicitly 'never block setup on storage'
- `custom_components/heatpump_optimizer/coordinator.py:10120` — guarded: nested inside the already-counted :5094 guard

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s2-04**: `grep -n -A2 'except Exception' custom_components/heatpump_optimizer/coordinator.py | grep _LOGGER.debug (24 guards); harness tools/audit/round9/D1/s2/guards.py drives the 5 on the cycle path`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None class-wide; a targeted check on the 5 cycle-path guards specifically (log at WARNING or raise a repair issue after N consecutive failures).

## Fix

Fix: see round-9 fix plan.

