# [R9-AN-APPROVAL-BOUND-TO-AN-EXACT-HEAD-IS-RE-BOUGHT-ON-A-DIFF-IDENTICAL-MOVE] an approval bound to an exact head is re-bought on a diff-identical move

**Class `an-approval-bound-to-an-exact-head-is-re-bought-on-a-diff-identical-move`.** an approval bound to an exact head is re-bought on a diff-identical move. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 0 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D13-s1-02 | `tools/audit/briefs/fix-review.md` | medium | 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits |

Findings touching more than one file (first file is the table's file:line; the rest share the same fact):

- D13-s1-02: also `tools/audit/briefs/fix-review.md (re-verification trigger on any head move)`, `.claude/workflows/web-fix-wave.js`, `tools/audit/app_approve.sh`

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D13-s1-02**: `HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D13/s1/yield_rounds.mjs  (reverify_* RESULTs)`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S7.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

none (N<3): rerun re-verification only when the diff against the last-reviewed head is non-empty; policy change needs owner approval

## Fix

Fix: see round-9 fix plan.

