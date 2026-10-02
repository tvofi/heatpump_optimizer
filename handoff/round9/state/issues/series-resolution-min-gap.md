# [R9-SERIES-RESOLUTION-MIN-GAP] series resolution inferred from the minimum gap

**Class `series-resolution-min-gap`.** series resolution inferred from the minimum gap. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s5-04 | `custom_components/heatpump_optimizer/open_meteo.py` | low | One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon |
| sweep | `custom_components/heatpump_optimizer/open_meteo.py:231` | (unrated) | single spurious small gap collapses the inferred resolution |

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/config_flow.py:2394,3798; prefill_offer.py:100` — not applicable: device-identity conflict resolution, unrelated name collision

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s5-04**: `grep -n "resolution = \|min(gaps)" custom_components/heatpump_optimizer/open_meteo.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1.

## Fix

Fix: see round-9 fix plan.

