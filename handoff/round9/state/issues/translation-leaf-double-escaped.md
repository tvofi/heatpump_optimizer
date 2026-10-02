# [R9-TRANSLATION-LEAF-DOUBLE-ESCAPED] translation leaf double-escaped

**Class `translation-leaf-double-escaped`.** translation leaf double-escaped. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s2-03 | `custom_components/heatpump_optimizer/strings.json` | medium | The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv) |
| sweep | `custom_components/heatpump_optimizer/strings.json,translations/en.json,sv.json (config.error.dhw_min_too_close, options.error.dhw_min_too_close)` | (unrated) | escaped_error_texts_reached=4, garbled_chars_en=1, garbled_chars_sv=9, escaped_texts_all_files=6 |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s2-03: also `custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `every other error text of both flows, both languages` — guarded: escaped_other_error_texts=0

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s2-03**: `tools/audit/round9/D4/s2/escaped_text.py (RESULT escaped_texts_all_files enumerates every leaf of strings.json and translations/*.json)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

CI regex check: no translation leaf's string value (after json.loads) may match a literal backslash-u escape.

## Fix

Fix: see round-9 fix plan.

