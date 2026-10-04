# Round-9 plan table — regenerated 2026-10-04T11:16Z at main `cc442e3e`, roster `929ea1d5`

Groups: 133 — done 101, not-started 30, rca-done 1, building 1

### Wave 1

| group | live state | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|
| R9-EG-B1 | round-2 hand-off at 13b1b8f0b; PR head moving now; CI then round-2 review | **#1736** | any structure-budget raise needs tvofi's confirmation before the push (CLAUDE.md | opus/opus |
| R9-F10.16 | queued (row batch: 5 rows owed) | — | tests/run.sh, tests/derive_closures.sh, tests.yml and tests/mutation_table.py ar | sonnet/opus |
| R9-FR-1 | done (8eab7dfd) | #1807 #1825 #1826 #1855 #1860 #1881 | — | opus/— |
| R9-FR-2 | PR #1891 open; reviewer measuring | #1860 | — | opus/opus |
| R9-FR-3 | PR #1892 open; reviewer measuring | #1825 | — | sonnet/sonnet |
| R9-FR-4 | hand-off 523fd84a; PR opening (raise 1428->1469 + policy clause; manual mandate path, not the train) | — | tests/closure.py is @tvofi code-owned; ci-autofix.md is policy — both merge on t | opus/opus |
| R9-RO-2b | in flight (opus fixer) | — | code-owned: .github/workflows, budget_raise_gate.py, contract_rerun.py, tools/re | opus/opus |
| R9-WEB-5 | hand-off 5dbd3726; PR opening | — | — | sonnet/opus |

### Wave 2

| group | live state | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|
| R9-DIAG-1F | folded, after EG-B1 — dispatches at its merge | — | — | opus/opus |
| R9-EG-A3 | not-started | **#1776** | — | sonnet/opus |
| R9-EG-B6 | not-started | **#1739** | — | sonnet/opus |
| R9-FR-5 | in flight (sonnet fixer; prepr recorder interpreter policy) | — | — | sonnet/sonnet |
| R9-RO-3 | not-started | — | tests/closure.py is code-owned; merges on tvofi's approving review at the head | sonnet/opus |
| R9-RO-4 | not-started | — | policy: the ADR superseded-by corrections, tools/audit/README.md and tools/audit | opus/opus |
| R9-RO-5 | not-started | — | policy and budget: CLAUDE.md, AGENTS.md, .claude/rules, tools/audit/briefs, docs | opus/opus |
| R9-RO-6 | not-started | — | code-owned: .github/workflows, .claude/hooks, CODEOWNERS, budget_raise_gate.py,  | sonnet/opus |
| R9-RO-7 | not-started | — | the codeowners_gap harness is restored by the governance jobs and is code-owned  | sonnet/opus |
| R9-SW-1 | not-started | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only  | opus/opus |

### Wave 3

| group | live state | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|
| R9-DIAG-2S | folded, after 1F | — | — | opus/opus |
| R9-EG-B11 | not-started | **#1745** | — | opus/opus |
| R9-EG-B7 | not-started | **#1744** | a classes_over_300 increase, unless R9-F10.4 re-defined it, needs tvofi's confir | opus/opus |
| R9-RO-8 | not-started | — | code-owned: tests/closure.py, tests/env_drift.py, tools/release/stamp.py, the co | opus/opus |
| R9-SW-2 | not-started | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only  | opus/opus |
| R9-SW-3 | not-started | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only  | sonnet/opus |
| R9-SW-4 | not-started | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only  | sonnet/opus |
| R9-SW-5 | not-started | — | a structure-budget raise, if any, is asked first and merges only on tvofi's appr | opus/opus |
| R9-UX-5 | not-started | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4 | opus/opus |

### Wave 4

| group | live state | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|
| R9-EG-A4 | not-started | **#1774** | — | sonnet/opus |
| R9-UX-6 | not-started | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4 | opus/opus |
| R9-UX-7 | not-started | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4 | opus/opus |

### Wave 5

| group | live state | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|
| R9-RO-9 | not-started | — | policy and code-owned: .github/workflows and the required-context list (a reposi | sonnet/opus |

## Merged 2026-10-04 (this session)

| PR | sha | group |
|---|---|---|
| #1889 | `fb11a017` | handover record |
| #1885 | `c2e84dfa` | R9-F10.13 |
| #1890 | `9a51f6d7` | R9-F10.15 |
| #1886 | `cc442e3e` | R9-RO-2 |

Stamps: v6.7.15 `ac255c20`; **v6.7.16** (rows deferral: 5 ride R9-F10.16). Red ledger deployment: fix #1878 merged; validation runs in flight, ETA ~12:30-13:30Z.

## Process instruments adopted this session

- `tools/audit/seat/merge_train.py` — verdicted-PR queue: recarry, CI wait, carry check, policy filter, labelled approve, merge; policy PRs excluded (FR-4 manual).
- `open_pr.sh` / `update_pr.sh` / `handoff_push.sh` — the purpose-built PR openers/updaters (adopting for the remaining openings).
- `bus.sh` (verdict refs), `wt_sync.sh` (15-min crash safety), `merge_pr.sh` (UNSTABLE-aware), `remerge_main.sh`, `codeql-triage-poll.sh`, `tmp_paths.py` (disk-fill detector), `seat_venv.sh`.

Critical path: EG-B1 → EG-B6 ∥ EG-A3 ∥ SW-1 → SW-5, UX-5 → UX-6/7 → RO-2b → RO-3..RO-8 → RO-9 → EG-A4 → v7.0.0. ETA 2026-10-08..10.

For tvofi: #1793 scoping; hpo-ledger bypass ratify-or-clear; EG-A4 required-context; ci-autofix Darwin clause (rostered R9-FR-4); prepr recorder policy (rostered R9-FR-5).
