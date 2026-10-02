# [R9-CPU-WORK-INLINE-ON-THE-EVENT-LOOP] CPU work inline on the event loop

**Class `cpu-work-inline-on-the-event-loop`.** CPU work inline on the event loop. The mechanism the sweep confirms across 2 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 2 (2 judge-verified findings + 0 sweep-confirmed instances).

RCA: not triggered (N=2).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D9-s1-03 | `custom_components/heatpump_optimizer/sysid.py` | low | The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve) |
| D9-s2-01 | `custom_components/heatpump_optimizer/sensor.py` | low | sensor_advisor ranking re-simulated on the event loop at every plan-sensor write: ~32% of loop CPU |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D9-s1-03: also `custom_components/heatpump_optimizer/coordinator.py:10478,10512`
- D9-s2-01: also `custom_components/heatpump_optimizer/sensor.py:111`, `custom_components/heatpump_optimizer/coordinator.py`, `custom_components/heatpump_optimizer/topology.py`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D9-s1-03**: `grep -n '_sysid\.\(step\|arm\|identify\)' custom_components/heatpump_optimizer/coordinator.py`
- **D9-s2-01**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py  (RESULT loop_simulate_steps_per_read must be 0; the hook counts every simulate_step on the loop thread during entity reads, whichever property makes it)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): finders' own scope is route both through hass.async_add_executor_job, or precompute sensor_advisor once per cycle

## Fix

Fix: see round-9 fix plan.

