# [R9-SERVICE-INPUT-WITHOUT-AN-UPPER-BOUND-CLAMP] service input without an upper-bound clamp

**Class `service-input-without-an-upper-bound-clamp`.** service input without an upper-bound clamp. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s2-54 | `custom_components/heatpump_optimizer/services.py` | low | apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps unenforced |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D1-s2-54: also `custom_components/heatpump_optimizer/services.py:867 (handle_apply_manual_plan expires_at)`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/services.py:86-111 (SERVICE_SCHEMA_SIMULATE_PLAN, 6 unbounded fields)` — not applicable: read-only what-if simulator, no persisted/actuating effect
- `custom_components/heatpump_optimizer/services.py (SET_THERMAL_PARAMS, assign-entity range-bound fields)` — guarded: already vol.Range-clamped

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s2-54**: `grep -n 'expires_at' custom_components/heatpump_optimizer/services.py custom_components/heatpump_optimizer/manual_plan.py; harness: tools/audit/round9/D1/leads/manual_plan_expiry.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): clamp expires_at to now + MANUAL_PLAN_WINDOW_HOURS (or the plan horizon)

## Fix

Fix: see round-9 fix plan.

