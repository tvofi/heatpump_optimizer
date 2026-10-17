# Round-9 plan table — regenerated 2026-10-04T09:56Z at main `cc442e3e`, roster `ac6fa330`

Groups: 129 — done 100, not-started 27, rca-done 1, building 1

## Wave lanes (open groups in dependency order)

### Wave 1

| group | stage | PR | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|---|
| R9-DIAG-1 | **in flight (opus study seat; boost vs the model-drift warning + restart feasibility)** | — | — | — | opus/— |
| R9-EG-B1 | **in review-pending (round 2 code+body on handoff/r9-eg-solve-inputs @ cf3bada3; PR #1887 head updates at hand-off)** | 6b68bca0 | **#1736** | any structure-budget raise needs tvofi's confirmation before the push (CLAUDE.md rule 2) (decisions given under the 2026-09-29 mandate; the approving review at the head remains a GitHub requirement) | opus/opus |
| R9-F10.16 | **queued (row batch: 3 owed from 2026-10-03 + #1885/#1890 deferral)** | — | — | tests/run.sh, tests/derive_closures.sh, tests.yml and tests/mutation_table.py are @tvofi code-owned gate files (force FULL); merges on tvofi approval at head under mandate 5951564627 | sonnet/opus |
| R9-FR-1 | **done** (pre-study 8eab7dfd) | — | #1807 #1825 #1826 #1855 #1860 #1881 | — | opus/— |
| R9-FR-2 | **in flight (opus fixer)** | — | #1860 | — | opus/opus |
| R9-FR-3 | **in flight (sonnet fixer)** | — | #1825 | — | sonnet/sonnet |
| R9-RO-2b | **in flight (opus fixer)** | — | — | code-owned: .github/workflows, budget_raise_gate.py, contract_rerun.py, tools/release/stamp.py; merges on tvofi's approving review at the head | opus/opus |
| R9-WEB-5 | **in flight (sonnet fixer)** | — | — | — | sonnet/opus |

### Wave 2

| group | stage | PR | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|---|
| R9-EG-A3 | not-started | — | **#1776** | — | sonnet/opus |
| R9-EG-B6 | not-started | — | **#1739** | — | sonnet/opus |
| R9-RO-3 | not-started | — | — | tests/closure.py is code-owned; merges on tvofi's approving review at the head | sonnet/opus |
| R9-RO-4 | not-started | — | — | policy: the ADR superseded-by corrections, tools/audit/README.md and tools/audit/harnesses/README.md, and policy_budgets.json roles.record.opens (it names a roster being archived; budget-raise-gate); merges on tvofi's approving review at the head | opus/opus |
| R9-RO-5 | not-started | — | — | policy and budget: CLAUDE.md, AGENTS.md, .claude/rules, tools/audit/briefs, docs/decisions, the steward skill, the PR template, policy_budgets.json and policy_known_bad.json re-keyed (budget-raise-gate reads a re-keyed roles.opens as a raise); confirm before the push and merge on tvofi's approving review at the head | opus/opus |
| R9-RO-6 | not-started | — | — | code-owned: .github/workflows, .claude/hooks, CODEOWNERS, budget_raise_gate.py, contract_rerun.py; merges on tvofi's approving review at the head | sonnet/opus |
| R9-RO-7 | not-started | — | — | the codeowners_gap harness is restored by the governance jobs and is code-owned through them; merges on tvofi's approving review at the head | sonnet/opus |
| R9-SW-1 | not-started | — | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only on tvofi's approving review at the head | opus/opus |

### Wave 3

| group | stage | PR | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|---|
| R9-EG-B11 | not-started | — | **#1745** | — | opus/opus |
| R9-EG-B7 | not-started | — | **#1744** | a classes_over_300 increase, unless R9-F10.4 re-defined it, needs tvofi's confirmation before the push (decisions given under the 2026-09-29 mandate; the approving review at the head remains a GitHub requirement) | opus/opus |
| R9-RO-8 | not-started | — | — | code-owned: tests/closure.py, tests/env_drift.py, tools/release/stamp.py, the codeowners_gap harness; merges on tvofi's approving review at the head | opus/opus |
| R9-SW-2 | not-started | — | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only on tvofi's approving review at the head | opus/opus |
| R9-SW-3 | not-started | — | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only on tvofi's approving review at the head | sonnet/opus |
| R9-SW-4 | not-started | — | — | a structure-budget raise is confirmed by tvofi (D3, 2026-09-30) and merges only on tvofi's approving review at the head | sonnet/opus |
| R9-SW-5 | not-started | — | — | a structure-budget raise, if any, is asked first and merges only on tvofi's approving review at the head | opus/opus |
| R9-UX-5 | not-started | — | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi's approving review at the head | opus/opus |

### Wave 4

| group | stage | PR | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|---|
| R9-EG-A4 | not-started | — | **#1774** | — | sonnet/opus |
| R9-UX-6 | not-started | — | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi's approving review at the head | opus/opus |
| R9-UX-7 | not-started | — | #1795 | tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi's approving review at the head | opus/opus |

### Wave 5

| group | stage | PR | issues (Fixes **bold**) | owner gate | model |
|---|---|---|---|---|---|
| R9-RO-9 | not-started | — | — | policy and code-owned: .github/workflows and the required-context list (a repository-settings change only tvofi applies; the orchestrator requests and records it on #201); merges on tvofi's approving review at the head | sonnet/opus |

## Recently merged (this session, 2026-10-04)

| PR | sha | group |
|---|---|---|
| #1889 | `fb11a017` | handover record |
| #1885 | `c2e84dfa` | R9-F10.13 |
| #1890 | `9a51f6d7` | R9-F10.15 |
| #1886 | `cc442e3e` | R9-RO-2 |

Stamps: v6.7.15 `ac255c20` (site published), **v6.7.16** (1913f0dd-line; publishes #1883 site fixes, ships #1882 card; `--allow-rowless` deferral: #1885/#1890 rows ride the next row batch with the three owed from 2026-10-03 — R9-F10.16).

## Open PRs

| PR | what | state |
|---|---|---|
| #1887 | R9-EG-B1 round 2 (record-shares-no-object; main absorbed) | fixer finishing body re-take; CI starts at hand-off push |
| (next) | R9-WEB-5 README product-page links | fixer in flight |
| (next) | R9-FR-2 prepr ancestry red-check arm; R9-FR-3 stats family folding; R9-RO-2b CI restore listed form | fixers in flight |

Studies: R9-DIAG-1 (boost vs the model-drift warning + restart-recommendation feasibility) in flight; R9-FR-1 landed — folded R9-FR-2/R9-FR-3, refused 4 with flip-numbers, closed #1881.

Critical path: EG-B1 (#1887) → EG-B6 ∥ EG-A3 ∥ SW-1 → SW-5, UX-5 → UX-6/UX-7 → RO-2b → RO-3..RO-8 → RO-9 → EG-A4 (programme's last PR) → stamp v7.0.0 close-out.

For tvofi's hands: #1793 scoping call; hpo-ledger bypass ratify-or-clear (5902383542); F10.5 writer identity; EG-A4 required-context setting; ci-autofix.md Darwin-inert_reads clause (policy, one clause).


_Stage cells in **bold** are the orchestrator's live overlay (seats dispatched/in flight today); the roster's resume fields catch up at each hand-off and merge. The claude.ai artifact 7Mdnn5vX belongs to the previous session's conversation and cannot be edited from here — this file (mirrored to handoff/audit-r9-plan) is the current table._
