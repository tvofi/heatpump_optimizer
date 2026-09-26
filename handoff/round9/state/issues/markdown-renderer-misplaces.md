# [R9-MARKDOWN-RENDERER-MISPLACES] markdown the renderer misplaces

**Class `markdown-renderer-misplaces`.** markdown the renderer misplaces. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 2 sweep-confirmed instances).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D5-s1-04 | `docs/configuration.md` | low | configuration.md has 9 lines a GFM renderer misplaces: 3 table rows as pipe text, 6 prose lines as rows |
| sweep | `docs/configuration.md:181-187` | (unrated) | anti-legionella rows orphaned |
| sweep | `docs/configuration.md:633-638` | (unrated) | fuel-price prose swallowed into table |

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `README.md; docs/{architecture,automations,dashboard-card,ecl110,how-it-works,setup}.md; rest of configuration.md` — guarded: files_checked=8, misrendered_lines=9 -- nothing else misrenders

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D5-s1-04**: `T=$(mktemp -d); npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1; NODE_PATH=$T/node_modules node tools/audit/round9/D5/s1/md_tables.mjs`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

Add md_tables.mjs's misrendered_lines==0 check as a CI gate on doc changes.

## Fix

Fix: see round-9 fix plan.

