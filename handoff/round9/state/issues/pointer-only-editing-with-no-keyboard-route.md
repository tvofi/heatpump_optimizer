# [R9-POINTER-ONLY-EDITING-WITH-NO-KEYBOARD-ROUTE] pointer-only editing with no keyboard route

**Class `pointer-only-editing-with-no-keyboard-route`.** pointer-only editing with no keyboard route. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D4-s1-04 | `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | medium | Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D4-s1-04: also `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:10266-10270 (setup layout editor)`

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:5572 (chart pan gesture)` — guarded: equivalent zoom in/out/reset buttons, keyboard-operable natively
- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:8502-8507 (dialog drag surface)` — guarded: own keydown handler at :8507
- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:9660-9698 (picker surface)` — guarded: own keydown handler at :9698

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D4-s1-04**: `grep -nE 'canvas.addEventListener\("(pointerdown|click)"|data-edge="\$\{edge\}"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): lint for pointerdown with no keydown AND no adjacent button-wired equivalent (needs the equivalent-control relation taught by hand)

## Fix

Fix: see round-9 fix plan.

