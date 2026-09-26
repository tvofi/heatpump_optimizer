# [R9-LEARNED-CORRECTION-CLAMP-SIZED-AGAINST-AN-ASSUMED-RANGE-NOT-THE-MODEL-S-CURVE] learned-correction clamp sized against an assumed range, not the model's curve

**Class `learned-correction-clamp-sized-against-an-assumed-range-not-the-model-s-curve`.** learned-correction clamp sized against an assumed range, not the model's curve. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D2-s2-02 | `custom_components/heatpump_optimizer/flow_lift.py` | medium | #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37% |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D2-s2-02: also `custom_components/heatpump_optimizer/flow_lift.py:64,179,221 (FLOW_BIAS_CLAMP_K)`, `custom_components/heatpump_optimizer/thermal_model.py`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D2-s2-02**: `grep -n "FLOW_BIAS_CLAMP_K\|curve_supply_temp(\|emitter_design_delta_t" custom_components/heatpump_optimizer/*.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): derive the clamp from curve_supply_temp's actual range for the configured emitter_design_delta_t

## Fix

Fix: see round-9 fix plan.

