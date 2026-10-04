# Round-9 plan — swimlanes, critical path, ETA

Regenerated 2026-10-04T14:53Z | main `7865ba90` | roster `aa8e8dc7` | 138 groups: 104 done, 33 open across waves 1-4

## Swimlanes (lane rows x wave columns; multiple groups in a cell run in parallel)

| lane | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|
| EG | R9-EG-B1 | R9-EG-A3 + R9-EG-B6 | R9-EG-B11 + R9-EG-B7 | R9-EG-A4 |  |
| F10 | R9-F10.16 |  |  |  |  |
| FIX | R9-DBG-1 + R9-DBG-3 + R9-FR-3 + R9-FR-4 + R9-FR-5 + R9-FR-6 | R9-DBG-2 + R9-DIAG-1F | R9-DIAG-2S |  |  |
| RO | R9-RO-2b | R9-RO-3 + R9-RO-4 + R9-RO-5 + R9-RO-6 + R9-RO-7 | R9-RO-8 |  | R9-RO-9 |
| SW |  | R9-SW-1 | R9-SW-2 + R9-SW-3 + R9-SW-4 + R9-SW-5 |  |  |
| UX |  |  | R9-UX-5 | R9-UX-6 + R9-UX-7 |  |
| WEB | R9-WEB-5 |  |  |  |  |

**Critical path**: EG-B1 (r3) → EG-B6 ∥ EG-A3 ∥ SW-1 → SW-5 → UX-5 → UX-6/UX-7 → RO-2b → RO-3..RO-8 → RO-9 → EG-A4 → stamp v7.0.0. Tooling (FR-2/3/4/5/6) and studies (DIAG-1, DBG-0) run beside it; DBG-1/3 start immediately (their lane edges are all merged).

## Per-group detail (open groups by wave)

### Wave 1

**R9-DBG-1** — Pre-study R9-DBG-0 (doc tools/audit/round9/prestudy/debugger-prestudy.md on handoff/r9-dbg-0 @eae236  
  stage: not-started | issue: #1939 | model: opus/opus | gate: —

**R9-DBG-3** — Pre-study R9-DBG-0 sections 6 and 7: the repo-side debugger harness, confined to tools/replay (unown  
  stage: not-started | issue: #1941 | model: sonnet/sonnet | gate: —

**R9-EG-B1** — B1 (lane EG, architecture: per-solve immutable inputs)  
  stage: r3 in flight: pinning 21 sites locally (mutation-unpinned block); then re-review | issue: **#1736** | model: opus/opus | gate: any structure-budget raise needs tvofi's confirmation before

**R9-F10.16** — 16 (mutation driver hygiene), same origin as F10.15  
  stage: MERGED #1896 7865ba90 (rows for #1886/#1891/#1892) | issue: #1930 | model: sonnet/opus | gate: tests/run.sh, tests/derive_closures.sh, tests.yml and tests/

**R9-FR-3** — tvofi, 2026-10-04 (pre-study R9-FR-1): #1825 — the stats counter folds verdict-class sibling familie  
  stage: MERGED #1892 b3372838; closes #1825 (verified) | issue: #1825 | model: sonnet/sonnet | gate: —

**R9-FR-4** — Carry from R9-RO-2's round 2 (#1886, reviewer-verified): a Darwin `--single` recording of any script  
  stage: absorbed at 4b4c0f03; r2 merge verdict carries; merging | issue: #1934 | model: opus/opus | gate: tests/closure.py is @tvofi code-owned; ci-autofix.md is poli

**R9-FR-5** — tvofi, 2026-10-04 (small instrument fix, both FR-3 and WEB-5 hit it): prepr's closures recorder defa  
  stage: PR #1895 open at 81cc117b; reviewer verdict merge in hand; needs absorb at merge time | issue: #1937 | model: sonnet/sonnet | gate: —

**R9-FR-6** — head needs an automatic main absorb — three proven instances today (#1893, #1894, #1896 all stopped at recarry  
  stage: PR #1944 open at e9a86cc4; reviewer verdict merge in hand | issue: #1943 | model: sonnet/sonnet | gate: —

**R9-RO-2b** — Round-9 PR RO-2b, split from #1886 (R9-RO-2). Change the CI restore steps to the listed form (list o  
  stage: not-started | issue: #1931 | model: opus/opus | gate: code-owned: .github/workflows, budget_raise_gate.py, contrac

**R9-WEB-5** — Owner ask (tvofi, 2026-10-04, folded per the no-pre-study ruling): the README links the product page  
  stage: absorbed at d6c1f64d; r1 merge verdict carries; prepr repair done, pushing | issue: #1932 | model: sonnet/opus | gate: —

### Wave 2

**R9-DBG-2** — Pre-study R9-DBG-0 sections 4 and 7: the debugger module self-test orchestration (the priced self-te  
  stage: not-started | issue: #1940 | model: sonnet/opus | gate: —

**R9-DIAG-1F** — Pre-study R9-DIAG-1 (doc tools/audit/round9/prestudy/boost-drift-prestudy.md on handoff/r9-diag-1 @3  
  stage: folded; dispatches at EG-B1 merge | issue: #1935 | model: opus/opus | gate: —

**R9-EG-A3** — A3 (lane EG, parameter objects). Issue #1776 (Fixes)  
  stage: not-started | issue: **#1776** | model: sonnet/opus | gate: —

**R9-EG-B6** — B6 (lane EG, architecture: collaborator interfaces)  
  stage: not-started | issue: **#1739** | model: sonnet/opus | gate: —

**R9-RO-3** — , comments and delivery notes; the PR attribution line is _Requested by **tvofi**_  
  stage: not-started | issue: #1916 | model: sonnet/opus | gate: tests/closure.py is code-owned; merges on tvofi's approving 

**R9-RO-4** — , comments and delivery notes; the PR attribution line is _Requested by **tvofi**_  
  stage: not-started | issue: #1917 | model: opus/opus | gate: policy: the ADR superseded-by corrections, tools/audit/READM

**R9-RO-5** — 5 (lane RO, the governance and programme lift)  
  stage: not-started | issue: #1918 | model: opus/opus | gate: policy and budget: CLAUDE.md, AGENTS.md, .claude/rules, tool

**R9-RO-6** — , comments and delivery notes; the PR attribution line is _Requested by **tvofi**_  
  stage: not-started | issue: #1919 | model: sonnet/opus | gate: code-owned: .github/workflows, .claude/hooks, CODEOWNERS, bu

**R9-RO-7** — 7 (lane RO, harness roots found, not counted)  
  stage: not-started | issue: #1920 | model: sonnet/opus | gate: the codeowners_gap harness is restored by the governance job

**R9-SW-1** — 1 (lane SW, silent windows: model and plan)  
  stage: not-started | issue: #1910 | model: opus/opus | gate: a structure-budget raise is confirmed by tvofi (D3, 2026-09-

### Wave 3

**R9-DIAG-2S** — Feature per the R9-DIAG-1 feasibility verdict (doc section 4): at accuracy_drift warning time, batch  
  stage: folded; after 1F | issue: #1936 | model: opus/opus | gate: —

**R9-EG-B11** — B11 (lane EG, typed entry configuration)  
  stage: not-started | issue: **#1745** | model: opus/opus | gate: —

**R9-EG-B7** — B7 (lane EG, architecture: coordinator seams, conditional)  
  stage: not-started | issue: **#1744** | model: opus/opus | gate: a classes_over_300 increase, unless R9-F10.4 re-defined it, 

**R9-RO-8** — , comments and delivery notes; the PR attribution line is _Requested by **tvofi**_  
  stage: not-started | issue: #1921 | model: opus/opus | gate: code-owned: tests/closure.py, tests/env_drift.py, tools/rele

**R9-SW-2** — 2 (lane SW, silent windows: actuation). Models: fixer opus (write safety)  
  stage: not-started | issue: #1911 | model: opus/opus | gate: a structure-budget raise is confirmed by tvofi (D3, 2026-09-

**R9-SW-3** — 3 (lane SW, silent windows: card and docs)  
  stage: not-started | issue: #1912 | model: sonnet/opus | gate: a structure-budget raise is confirmed by tvofi (D3, 2026-09-

**R9-SW-4** — 4 (lane SW, silent windows on the GCHV Modbus package)  
  stage: not-started | issue: #1913 | model: sonnet/opus | gate: a structure-budget raise is confirmed by tvofi (D3, 2026-09-

**R9-SW-5** — line is _Requested by **tvofi**_. Scope: two switches (Block DHW, Block Space Heating  
  stage: not-started | issue: #1926 | model: opus/opus | gate: a structure-budget raise, if any, is asked first and merges 

**R9-UX-5** — 5 (lane UX, advisor actions and exact idle reasons)  
  stage: not-started | issue: #1795 | model: opus/opus | gate: tests/card_browser.mjs is code-owned; a budget raise, if any

### Wave 4

**R9-EG-A4** — A4 (lane EG, the architecture score becomes a required check)  
  stage: not-started | issue: **#1774** | model: sonnet/opus | gate: —

**R9-UX-6** — 6 (lane UX, money and memory). Models: fixer opus (ledger and accuracy stores, a receipt defect with its faili  
  stage: not-started | issue: #1795 | model: opus/opus | gate: tests/card_browser.mjs is code-owned; a budget raise, if any

**R9-UX-7** — 7 (lane UX, model status and diagnostics)  
  stage: not-started | issue: #1795 | model: opus/opus | gate: tests/card_browser.mjs is code-owned; a budget raise, if any

### Wave 5

**R9-RO-9** — , comments and delivery notes; the PR attribution line is _Requested by **tvofi**_  
  stage: not-started | issue: #1922 | model: sonnet/opus | gate: policy and code-owned: .github/workflows and the required-co

## Merged 2026-10-04 (11 PRs): #1885 #1886 #1889 #1890 #1891 #1892 #1893 #1894* #1895* #1896 + row batch; stamps v6.7.15, v6.7.16 (* = absorbed heads merging; #1895 landing after #1894)

## ETA

Waves 1-2 land today/tomorrow. W3's structural groups (EG-B7, EG-B11) plus SW/UX features: 1-1.5 days. W4-W5 (EG-A4 + RO close-out): 1-1.5 days. **Programme completion: 2026-10-08 to 2026-10-10**, on the base case inside the mandate window (2026-10-09T12:00Z). Risks: EG-B7's measured go/no-go, DIAG-1F follow-ups, review rounds on the structural groups, the mandate boundary for policy merges landing after 2026-10-09T12:00Z.

For tvofi: #1793 scoping; the coordinate-coarsening decision (DBG-0 doc 8.3, 1 dp proposed); hpo-ledger bypass ratify-or-clear (#201 comment 5902383542); EG-A4's required-context setting.
