# [R9-CPU-GATE-BLIND] CPU gate blind to a regression outside its sampled work

**Class `cpu-gate-blind`.** CPU gate blind to a regression outside its sampled work. The mechanism the sweep confirms across 3 instances: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 3 (3 judge-verified findings + 0 sweep-confirmed instances).

RCA: owed.

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D9-s2-02 | `tests/replay.py` | medium | No budgeted check sees a 2x of the coordinator's loop-thread work; stress.py reaches none of it |
| D9-s2-03 | `tests/stress.py` | medium | stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams |
| D9-s2-71 | `tests/stress.py` | medium | stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D9-s2-02: also `tests/replay.py:cost_offenders / coordinator.py:_async_update_data loop-thread share`, `tests/stress.py`, `custom_components/heatpump_optimizer/coordinator.py`
- D9-s2-03: also `tests/stress.py rules vs non-kernel solve CPU (objective assembly, DHW planning python)`
- D9-s2-71: also `tests/stress.py:sweep_combinations() throttling-valve topologies`, `tests/stress_budgets.json`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D9-s2-02**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py  (loop2x.offenders must be >= 1; stress_cycle_functions names what the per-PR gate reaches)`
- **D9-s2-03**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py auto-lease --label d9s2 -- /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_nonkernel_2x.py --arms plain,solvecpu2x_set  (every victim must be caught; add victims with --victims)`
- **D9-s2-71**: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py  (topology axes = const TOPOLOGY_* and mixing_valve modes; count sweep cases per axis value)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S5.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

3 additive tests/stress.py & tests/replay.py channels: per-scenario non-kernel CPU vs same-machine baseline; loop-thread-only cost channel in cost_offenders; at least one throttling-valve scenario in sweep_combinations()

## Fix

Fix: see round-9 fix plan.

