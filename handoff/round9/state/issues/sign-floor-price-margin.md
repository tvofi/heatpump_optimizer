# [R9-SIGN-FLOOR-PRICE-MARGIN] a sign floor on a price margin breaks the stated piecewise identity

**Class `sign-floor-price-margin`.** a sign floor on a price margin breaks the stated piecewise identity. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 3 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D2-s3-02 | `custom_components/heatpump_optimizer/pv.py` | low | PV piecewise cost clipped by import_margin's zero floor wherever import price < export price |
| sweep | `custom_components/heatpump_optimizer/pv.py:92-101` | (unrated) | floors at 0 when export_price > import price |
| sweep | `custom_components/heatpump_optimizer/pv.py:123` | (unrated) | blended_block_prices consumes the floored margin |
| sweep | `custom_components/heatpump_optimizer/optimizer.py:2428` | (unrated) | production call site |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D2-s3-02: also `custom_components/heatpump_optimizer/optimizer.py`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/pv.py:68; optimizer.py:2465,2819,3160,3205,3350,5186,5187` — not applicable: non-negative physical/deficit quantities, not signed price margins

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D2-s3-02**: `grep -n "import_margin" custom_components/heatpump_optimizer/*.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1.

## Fix

Fix: see round-9 fix plan.

