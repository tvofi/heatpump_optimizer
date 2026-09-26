# [R9-TEXT-PRODUCER-TAKES-NO-LANGUAGE-PARAMETER] text producer takes no language parameter

**Class `text-producer-takes-no-language-parameter`.** text producer takes no language parameter. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s2-81 | `custom_components/heatpump_optimizer/topology.py` | medium | Setup overview page and setup diagram publish English slot text on a Swedish install |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s2-81: also `custom_components/heatpump_optimizer/topology.py:117 (_SLOTS catalog)`, `custom_components/heatpump_optimizer/topology.py:389 (describe_setup)`, `custom_components/heatpump_optimizer/topology.py:538 (render_text_summary)`, `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js (setup overview/diagram)`, `custom_components/heatpump_optimizer/config_flow.py`, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s2-81**: `grep -n "describe_setup\|render_text_summary\|rank_sensor_advisor" custom_components/heatpump_optimizer/*.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): route _SLOTS labels through strings.json/translations/, thread a language argument through both functions

## Fix

Fix: see round-9 fix plan.

