# [R9-FIT-INTEGRATOR-DIFFERS-FROM-PLANT] fit integrator differs from the simulated plant

**Class `fit-integrator-differs-from-plant`.** fit integrator differs from the simulated plant. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D7-s2-01 | `custom_components/heatpump_optimizer/sysid.py` | medium | sysid two-state fit rolls the candidate one Euler step per sample: UA 17-25% low, 0/3 presets adopt |
| sweep | `custom_components/heatpump_optimizer/sysid.py:576-800` | (unrated) | one Euler step per 30-min sample, coarser than the optimizer's own 0.25h step |

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/sysid.py:1475 identify (one-state control)` — not applicable: closed-form comparator, not a production fit path

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D7-s2-01**: `grep -n "_valve_drive(\|simulate_step(" custom_components/heatpump_optimizer/sysid.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1.

## Fix

Fix: see round-9 fix plan.

