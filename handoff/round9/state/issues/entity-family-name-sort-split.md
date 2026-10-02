# [R9-ENTITY-FAMILY-NAME-SORT-SPLIT] an entity family whose names do not lead with a shared token splits under the name sort

**Class `entity-family-name-sort-split`.** an entity family whose names do not lead with a shared token splits under the name sort. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 2 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D8-s3-01 | `custom_components/heatpump_optimizer/button.py` | low | Accuracy and Energy-dashboard meter families split in both English and Swedish name sort |
| sweep | `custom_components/heatpump_optimizer/sensor.py,button.py (accuracy family)` | (unrated) | SPLIT_UNEXPLAINED under both name orders |
| sweep | `custom_components/heatpump_optimizer/sensor.py (energy_meters family)` | (unrated) | SPLIT_UNEXPLAINED under both name orders and entity_id |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D8-s3-01: also `custom_components/heatpump_optimizer/strings.json`, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/*.py (tariff, learning, pv, card_headline families)` — guarded: 0 unexplained splits in every ordering

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D8-s3-01**: `PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m3_families.py  (SPLIT_UNEXPLAINED lines)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1; a lint rule needs a design decision on the canonical lead token per family.

## Fix

Fix: see round-9 fix plan.

