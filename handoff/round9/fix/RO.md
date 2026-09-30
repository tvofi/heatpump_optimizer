# Repository reorganisation: docs, images, instruments and agent config (lane RO)

Requested by tvofi on 2026-09-30 (thread "Repo reorganisation", root message 14:59Z; the CI-barrier addition at 15:01Z).
tvofi answered D1-D4 at 16:20Z.
Measured against origin/main 754d2319 (v6.7.12) and roster rev 3.2 (handoff/audit-r9-fixplan at d13d6726).

Status: the decisions are answered, and nothing has moved yet. The nine roster entries, R9-RO-1 to R9-RO-9, are on `handoff/repo-reorg-plan` (on top of handoff/audit-r9-fixplan), and the Mac merge seat applies them.

The companion data is in `handoff/round9/fix/RO/` on the same branch, and in /mnt/project-files/audit-r9/repo-reorg/:

- `inventory.tsv` has one row per tracked non-code file (2,326 rows), with its path, action, new path, category and reason.
- `references.tsv` has one row per moved unit, with its live and historical reference counts and the files that hold the live references.
- `references-detail.tsv` has one row per reference (file and line), marked live or historical.

Every count below is a snapshot, and the seat re-derives it at its own merge base.

## 1. Decisions (tvofi, 2026-09-30T16:20Z)

| # | Question | Answer | What it changes |
|---|---|---|---|
| D1 | Where the canonical rules live | **lift** | `dev/governance/rules/` is the source. `rules_sync` generates both `.claude/rules/` and `.cursor/rules/`, and the policy lint treats the generated `.claude` copy as it treats `.cursor`. |
| D2 | Rewrite paths inside historical records | **no** | RELEASE_NOTES, delivery rows, round evidence logs, archived files and ADR bodies keep their old paths. Each is true at its own commit. |
| D3 | Top-level shape | **nested, and adjust the harnesses** | `governance/`, `programme/`, `audit/` and `archive/` sit under one `dev/`. That puts the round evidence one path segment deeper. So a new group, **RO-7**, first replaces every depth-computed repository root in the harnesses with a root finder, in place, and proves byte-identical output. Only then does RO-8 move them. |
| D4 | `.abacus.donotdelete` | **delete** | Deleted in RO-4, together with the root `icon.png`. |

The following are decided without asking, because they are reversible:

- The user docs keep their URLs (`docs/*.md`), because users and HACS links point at them.
- The lane runs last, after every code group (section 6).
- The root `icon.png` is deleted. It is byte-identical to the integration's own icon.

## 2. Target tree

```
/                              README.md LICENSE NOTICE DISCLAIMER.md SECURITY.md RELEASE_NOTES.md VERSION hacs.json
                               CLAUDE.md AGENTS.md          harness entry points; loaded only from the root
custom_components/             unchanged
blueprints/automation/         unchanged (each source_url pins raw.githubusercontent .../main/blueprints/...)
tests/                         unchanged (code), plus tests/layout.py and tests/layout.json from RO-1

docs/                          PRODUCT DOCUMENTATION: user guides and feature design
  setup.md configuration.md automations.md dashboard-card.md ecl110.md how-it-works.md architecture.md
  img/
    card/                      card-*.png, chart-*.svg, options-hot-water-by-day.png, make_card_figures.mjs
    model/                     dhw-*.svg, hydronic-*.svg, marginal-cop.svg, make_model_figures.py
    setup/                     01..08 screenshots (was docs/setup/)
  design/
    <yyyy-mm-dd-feature>/      design.md + plan.md side by side (was docs/superpowers/{specs,plans})

dev/                           THE DEVELOPMENT RECORD: everything an agent or maintainer reads, nothing a user needs
  governance/                  POLICY: agent-agnostic, code-owned
    rules/                     canonical rule sources (D1); .claude/rules and .cursor/rules are generated from here
    roles/                     orchestrator, fixer, fix-review, root-cause, judge, verifier, COMMON (the finder)
    dimensions/                D0..D14 audit dimension briefs
    decisions/                 ADRs 0001..0013 (was docs/decisions/)
    config/                    policy_budgets, policy_known_bad, corpus_excluded, cfr_exclusions
  programme/                   THE FIX PROGRAMME RECORD
    HANDOVER.md                the one living handover
    plan-2026-09-open-issues.md  the plan of record
    delivery/<N>.md            delivery rows
    carries/carry-<N>.json     live carries (destination issue still open)
    rosters/                   live wave rosters (empty on main today; the r9 roster lives on its handoff branch)
    register/                  audit-2026-09.md, the evidence register
  audit/                       AUDIT PROCESS AND EVIDENCE
    README.md                  how a round runs (merged from tools/audit/README.md and harnesses/README.md)
    config/                    bugclasses.json, finding.schema.json, rotation.json, scopes.json
    rounds/round3..round9/     round evidence (one segment deeper than today; roots found, not counted: RO-7)
    rounds/round5-fix/ ...     fix-round evidence beside its round
    rca/                       RCA documents (tools/audit/rca and v6612-root-cause.md)
    harnesses/                 cross-round harnesses, and ci-version-edit/
    waves/w5-g5-195-coverage/  wave-5 coverage evidence
  archive/                     OBSOLETE BUT STILL REFERENCED: read-only, never linted as live
    README.md                  one line per item: what it was, and what superseded it
    plans/                     plan-open-issues, plan-v4.0.0-program, plan-card-decomposition, plan-1067-rotenso-inputs
    audits/                    audit-2026-08.md
    backlog.md                 the self-declared archive of reasoning (v3.14.0)
    rosters/                   finished rosters: wave-3l, 4, 5, d11, r8, ux
    carries/                   carries whose destination issue is closed
    handoff/                   transport leftovers of merged fixes (r9-f2-solver-4/5, r9-frictions)
    experiments/ledger-layout/ the mutation-ledger layout demo

tools/                         EXECUTABLE INSTRUMENTS ONLY (same depth as today: ROOT=../.. holds)
  policy/                      brief_lint, policy_lint (+envmatrix, mutants), rules_sync, fragments_sync, counts,
                               field_coverage, figure_lint, figure_census, render_md, check-wave-script,
                               friction_issues, budget_raise_gate.py, record-predicate/, fixtures/, vendor/
  pr/                          app_push.sh, app_approve.sh, app_comment.sh, approve_held_runs.sh, push.sh, prepr.sh,
                               preflight.sh, gh_comment.py, contract_rerun.py  (prepr.sh stays beside app_push.sh)
  seat/                        ci-watch, codeql-triage-poll, handoff_push, merge_pr, remerge_main, worktree_gc
  audit/                       judge_batch.py, check_scopes.py, prepare_baseline.sh, merge_throughput.py
  coverage/                    coverage_tree.sh, partition.py (was tools/audit/w5-partition/)
  devices/                     gen_device_fixtures.py, measure_prefill_corpus.py
  release/ merge/ replay/      unchanged

.claude/                       CLAUDE-CODE-SPECIFIC ONLY
  settings.json hooks/ skills/steward/
  rules/                       GENERATED from dev/governance/rules (D1)
  workflows/                   Workflow-tool scripts only: audit-*.js, web-*.js, and web-fragments.md (the fragments_sync canon)
.cursor/rules/                 GENERATED (unchanged mechanism)
.github/                       unchanged (GitHub reads it only here)
```

Each category answers the question "who reads this, and when":

- `docs/` is read by users.
- `dev/` is read by maintainers and agents. Within it:
  - `governance/` binds every seat.
  - `programme/` is the current work.
  - `audit/` is how findings are produced, together with their evidence.
  - `archive/` is what nobody should act on.
- `tools/` holds anything you execute.

A tool-specific file stays where its tool looks for it.

## 3. Inventory

The per-file map is `inventory.tsv`, and section 3.3 has a per-unit summary table. Totals by action:

| action | files |
|---|---:|
| keep | 67 |
| move | 2,143 |
| archive | 113 |
| delete | 2 (`icon.png`, `.abacus.donotdelete`) |
| merge | 1 unit |

### 3.1 Supersede and duplicate calls, with evidence

| file | call | evidence |
|---|---|---|
| docs/plan-open-issues.md | archive | Its own banner says "Superseded and complete … kept as the record". It is cited from README.md:926. |
| docs/plan-v4.0.0-program.md | archive | README.md:920 says the program "is complete". |
| docs/plan-card-decomposition.md | archive | The program is finished. Still cited in comments at heatpump-optimizer-card.js:11020 and :11062, and those citations are rewritten. |
| docs/plan-1067-rotenso-inputs.md | archive | Wave 1067 is closed (issue #1067 is closed). It is cited by carry-1067.json (also archived) and HANDOVER.md. |
| docs/audit-2026-08.md | archive | Superseded by audit-2026-09.md (README.md:922-924). |
| docs/backlog.md | archive | Its own header: "An archive of reasoning, not a worklist … every item, 1–33, is delivered". Cited by coordinator.py:4339 and the README docs table. |
| wave-{3l,4,5,d11,r8,ux}-groups.json | archive | Every group is at `resume.stage: done`. The r9 roster is on its own branch. |
| carry-N.json for closed issues | archive | The destination issue is closed, so nothing dispatches or lints them. Twenty-one files today (#681, 752, 932, 962, 1067, 1295, 1300, 1308, 1320, 1330, 1336, 1395, 1398, 1412, 1454, 1459, 1463, 1617, 1648, 1659, 1668). Re-derive at the merge base: more will close by then. |
| tools/audit/handoff/** | archive | Transport directories of fixes that merged as #1782 and earlier, and nothing live reads them. The exception is `v6612-root-cause.md`, which is an RCA and moves to dev/audit/rca/. |
| tools/audit/ledger-layout/ | archive | A layout demo, cited only by closed carries 1412 and 1617 and by comments. |
| icon.png (root) | delete | Byte-identical to custom_components/heatpump_optimizer/icon.png (same blob). Referenced only by closure.py's INERT list. |
| byte-identical round9/D4 screenshots, and base==head logs | keep | They are evidence *of* identity, so deduplicating them would destroy the measurement. |
| .cursor/rules/*.mdc | keep (generated) | These are Cursor's copy, generated by rules_sync. They are not a duplicate to remove. |

### 3.2 Merge candidates, judged by RO-4 (opus)

1. tools/audit/README.md (228 lines) and tools/audit/harnesses/README.md (46 lines) become **dev/audit/README.md**. The PR-instrument half of the first moves to a short **tools/pr/README.md**. Both are code-owned policy files.
2. tools/audit/rca/, tools/audit/round9/rca/ and handoff/v6612-root-cause.md become **dev/audit/rca/**. round9/rca/ holds executable enumerators cited by live briefs (p2/owners_lint.py). If a seat judges it evidence rather than an RCA document, it stays under rounds/round9/.
3. The ADRs are not merged: an ADR is append-only. Their **superseded-by metadata** is corrected instead. 0001, 0006 and 0007 (session merge grants) and 0005 (no CODEOWNERS; CODEOWNERS exists now) all read `superseded-by: []` against 0009, 0011 and 0013. The seat confirms each supersession from the text before writing it. This is a policy edit.
4. The README "history" paragraph (README.md:918-939) and the docs-table row for backlog.md become one line pointing at dev/archive/README.md.
5. Each docs/superpowers spec and plan pair goes into one folder per feature.

Deliberate duplicates stay:

- AGENTS.md restates CLAUDE.md's load rules. The file says why.
- CLAUDE.md and orchestrator.md §8 both carry "fix it first". This is the owner's call.
- The web-fragments block is mirrored into five web-*.js files, and fragments_sync enforces the mirror.

### 3.3 Per-unit inventory

| current path | files | action | new path | category | why |
|---|---:|---|---|---|---|
| `.abacus.donotdelete` | 1 | delete | — | root | opaque encrypted blob from 2026-04 (Abacus agent state), read by nothing in the tree; tvofi D4: delete |
| `.claude/hooks/` | 4 | keep | `.claude/hooks/` | agent-config | Claude Code loads only here |
| `.claude/rules/` | 10 | move | `dev/governance/rules/` | policy | canonical source lifted out; .claude/rules/ becomes generated by rules_sync like .cursor/rules/ (decision D1) |
| `.claude/settings.json` | 1 | keep | `.claude/settings.json` | agent-config | Claude Code loads only here |
| `.claude/skills/steward/SKILL.md` | 1 | keep | `.claude/skills/steward/SKILL.md` | agent-config | Claude Code loads only here |
| `.claude/workflows/audit-find.js` | 1 | keep | `.claude/workflows/audit-find.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/audit-fix.js` | 1 | keep | `.claude/workflows/audit-fix.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/audit-verify.js` | 1 | keep | `.claude/workflows/audit-verify.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/audit-wave.js` | 1 | keep | `.claude/workflows/audit-wave.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/brief_lint.mjs` | 1 | move | `tools/policy/brief_lint.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/budget_raise_gate.py` | 1 | move | `tools/policy/budget_raise_gate.py` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/carry-1067.json` | 1 | archive | `dev/archive/carries/carry-1067.json` | programme | destination issue #1067 is closed; nothing dispatches it |
| `.claude/workflows/carry-1295.json` | 1 | archive | `dev/archive/carries/carry-1295.json` | programme | destination issue #1295 is closed; nothing dispatches it |
| `.claude/workflows/carry-1300.json` | 1 | archive | `dev/archive/carries/carry-1300.json` | programme | destination issue #1300 is closed; nothing dispatches it |
| `.claude/workflows/carry-1308.json` | 1 | archive | `dev/archive/carries/carry-1308.json` | programme | destination issue #1308 is closed; nothing dispatches it |
| `.claude/workflows/carry-1320.json` | 1 | archive | `dev/archive/carries/carry-1320.json` | programme | destination issue #1320 is closed; nothing dispatches it |
| `.claude/workflows/carry-1330.json` | 1 | archive | `dev/archive/carries/carry-1330.json` | programme | destination issue #1330 is closed; nothing dispatches it |
| `.claude/workflows/carry-1336.json` | 1 | archive | `dev/archive/carries/carry-1336.json` | programme | destination issue #1336 is closed; nothing dispatches it |
| `.claude/workflows/carry-1395.json` | 1 | archive | `dev/archive/carries/carry-1395.json` | programme | destination issue #1395 is closed; nothing dispatches it |
| `.claude/workflows/carry-1398.json` | 1 | archive | `dev/archive/carries/carry-1398.json` | programme | destination issue #1398 is closed; nothing dispatches it |
| `.claude/workflows/carry-1412.json` | 1 | archive | `dev/archive/carries/carry-1412.json` | programme | destination issue #1412 is closed; nothing dispatches it |
| `.claude/workflows/carry-1454.json` | 1 | archive | `dev/archive/carries/carry-1454.json` | programme | destination issue #1454 is closed; nothing dispatches it |
| `.claude/workflows/carry-1459.json` | 1 | archive | `dev/archive/carries/carry-1459.json` | programme | destination issue #1459 is closed; nothing dispatches it |
| `.claude/workflows/carry-1463.json` | 1 | archive | `dev/archive/carries/carry-1463.json` | programme | destination issue #1463 is closed; nothing dispatches it |
| `.claude/workflows/carry-1617.json` | 1 | archive | `dev/archive/carries/carry-1617.json` | programme | destination issue #1617 is closed; nothing dispatches it |
| `.claude/workflows/carry-1644.json` | 1 | move | `dev/programme/carries/carry-1644.json` | programme | live carry, issue #1644 open |
| `.claude/workflows/carry-1645.json` | 1 | move | `dev/programme/carries/carry-1645.json` | programme | live carry, issue #1645 open |
| `.claude/workflows/carry-1646.json` | 1 | move | `dev/programme/carries/carry-1646.json` | programme | live carry, issue #1646 open |
| `.claude/workflows/carry-1647.json` | 1 | move | `dev/programme/carries/carry-1647.json` | programme | live carry, issue #1647 open |
| `.claude/workflows/carry-1648.json` | 1 | archive | `dev/archive/carries/carry-1648.json` | programme | destination issue #1648 is closed; nothing dispatches it |
| `.claude/workflows/carry-1649.json` | 1 | move | `dev/programme/carries/carry-1649.json` | programme | live carry, issue #1649 open |
| `.claude/workflows/carry-1651.json` | 1 | move | `dev/programme/carries/carry-1651.json` | programme | live carry, issue #1651 open |
| `.claude/workflows/carry-1652.json` | 1 | move | `dev/programme/carries/carry-1652.json` | programme | live carry, issue #1652 open |
| `.claude/workflows/carry-1653.json` | 1 | move | `dev/programme/carries/carry-1653.json` | programme | live carry, issue #1653 open |
| `.claude/workflows/carry-1654.json` | 1 | move | `dev/programme/carries/carry-1654.json` | programme | live carry, issue #1654 open |
| `.claude/workflows/carry-1655.json` | 1 | move | `dev/programme/carries/carry-1655.json` | programme | live carry, issue #1655 open |
| `.claude/workflows/carry-1659.json` | 1 | archive | `dev/archive/carries/carry-1659.json` | programme | destination issue #1659 is closed; nothing dispatches it |
| `.claude/workflows/carry-1660.json` | 1 | move | `dev/programme/carries/carry-1660.json` | programme | live carry, issue #1660 open |
| `.claude/workflows/carry-1668.json` | 1 | archive | `dev/archive/carries/carry-1668.json` | programme | destination issue #1668 is closed; nothing dispatches it |
| `.claude/workflows/carry-1686.json` | 1 | move | `dev/programme/carries/carry-1686.json` | programme | live carry, issue #1686 open |
| `.claude/workflows/carry-201.json` | 1 | move | `dev/programme/carries/carry-201.json` | programme | live carry, issue #201 open |
| `.claude/workflows/carry-681.json` | 1 | archive | `dev/archive/carries/carry-681.json` | programme | destination issue #681 is closed; nothing dispatches it |
| `.claude/workflows/carry-752.json` | 1 | archive | `dev/archive/carries/carry-752.json` | programme | destination issue #752 is closed; nothing dispatches it |
| `.claude/workflows/carry-932.json` | 1 | archive | `dev/archive/carries/carry-932.json` | programme | destination issue #932 is closed; nothing dispatches it |
| `.claude/workflows/carry-962.json` | 1 | archive | `dev/archive/carries/carry-962.json` | programme | destination issue #962 is closed; nothing dispatches it |
| `.claude/workflows/cfr_exclusions.json` | 1 | move | `dev/governance/config/cfr_exclusions.json` | policy | policy-lint data, agent-agnostic |
| `.claude/workflows/check-wave-script.mjs` | 1 | move | `tools/policy/check-wave-script.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/contract_rerun.py` | 1 | move | `tools/pr/contract_rerun.py` | instrument | PR/comment instrument, agent-agnostic |
| `.claude/workflows/corpus_excluded.json` | 1 | move | `dev/governance/config/corpus_excluded.json` | policy | policy-lint data, agent-agnostic |
| `.claude/workflows/counts.mjs` | 1 | move | `tools/policy/counts.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/field_coverage.mjs` | 1 | move | `tools/policy/field_coverage.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/figure_census.mjs` | 1 | move | `tools/policy/figure_census.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/figure_lint.mjs` | 1 | move | `tools/policy/figure_lint.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/fixtures/` | 72 | move | `tools/policy/fixtures/` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/fragments_sync.mjs` | 1 | move | `tools/policy/fragments_sync.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/friction_issues.mjs` | 1 | move | `tools/policy/friction_issues.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/gh_comment.py` | 1 | move | `tools/pr/gh_comment.py` | instrument | PR/comment instrument, agent-agnostic |
| `.claude/workflows/policy_budgets.json` | 1 | move | `dev/governance/config/policy_budgets.json` | policy | policy-lint data, agent-agnostic |
| `.claude/workflows/policy_known_bad.json` | 1 | move | `dev/governance/config/policy_known_bad.json` | policy | policy-lint data, agent-agnostic |
| `.claude/workflows/policy_lint.mjs` | 1 | move | `tools/policy/policy_lint.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/policy_lint_envmatrix.mjs` | 1 | move | `tools/policy/policy_lint_envmatrix.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/policy_lint_mutants.mjs` | 1 | move | `tools/policy/policy_lint_mutants.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/render_md.mjs` | 1 | move | `tools/policy/render_md.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/rules_sync.mjs` | 1 | move | `tools/policy/rules_sync.mjs` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/vendor/` | 2 | move | `tools/policy/vendor/` | instrument | policy/record instrument, agent-agnostic; depth 3 keeps ROOT=../.. |
| `.claude/workflows/wave-3l-groups.json` | 1 | archive | `dev/archive/rosters/wave-3l-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/wave-4-groups.json` | 1 | archive | `dev/archive/rosters/wave-4-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/wave-5-groups.json` | 1 | archive | `dev/archive/rosters/wave-5-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/wave-d11-groups.json` | 1 | archive | `dev/archive/rosters/wave-d11-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/wave-r8-groups.json` | 1 | archive | `dev/archive/rosters/wave-r8-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/wave-ux-groups.json` | 1 | archive | `dev/archive/rosters/wave-ux-groups.json` | programme | finished roster (every group done); off brief_lint input |
| `.claude/workflows/web-decomp-stage.js` | 1 | keep | `.claude/workflows/web-decomp-stage.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/web-fix-wave.js` | 1 | keep | `.claude/workflows/web-fix-wave.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/web-fragments.md` | 1 | keep | `.claude/workflows/web-fragments.md` | agent-config | MCP mapping for Claude web seats; fragments_sync canon beside the web-*.js it syncs |
| `.claude/workflows/web-stamp.js` | 1 | keep | `.claude/workflows/web-stamp.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.claude/workflows/web-triage.js` | 1 | keep | `.claude/workflows/web-triage.js` | agent-config | Claude Code Workflow-tool script (exports meta); tool-specific |
| `.cursor/rules/` | 10 | keep | `.cursor/rules/` | agent-config | Cursor loads only here; stays generated |
| `.gitattributes` | 1 | keep | `.gitattributes` | root | GitHub/HACS/stamp convention; stays at the root |
| `.github/CODEOWNERS` | 1 | keep | `.github/CODEOWNERS` | ci | GitHub reads it only here |
| `.github/PULL_REQUEST_TEMPLATE.md` | 1 | keep | `.github/PULL_REQUEST_TEMPLATE.md` | ci | GitHub reads it only here |
| `.github/workflows/` | 10 | keep | `.github/workflows/` | ci | GitHub reads it only here |
| `.gitignore` | 1 | keep | `.gitignore` | root | GitHub/HACS/stamp convention; stays at the root |
| `AGENTS.md` | 1 | keep | `AGENTS.md` | root | harness entry point, loaded only from the root |
| `CLAUDE.md` | 1 | keep | `CLAUDE.md` | root | harness entry point, loaded only from the root |
| `DISCLAIMER.md` | 1 | keep | `DISCLAIMER.md` | root | GitHub/HACS/stamp convention; stays at the root |
| `LICENSE` | 1 | keep | `LICENSE` | root | GitHub/HACS/stamp convention; stays at the root |
| `NOTICE` | 1 | keep | `NOTICE` | root | GitHub/HACS/stamp convention; stays at the root |
| `README.md` | 1 | keep | `README.md` | root | GitHub/HACS/stamp convention; stays at the root |
| `RELEASE_NOTES.md` | 1 | keep | `RELEASE_NOTES.md` | root | GitHub/HACS/stamp convention; stays at the root |
| `SECURITY.md` | 1 | keep | `SECURITY.md` | root | GitHub/HACS/stamp convention; stays at the root |
| `VERSION` | 1 | keep | `VERSION` | root | GitHub/HACS/stamp convention; stays at the root |
| `blueprints/` | 3 | keep | `blueprints/automation/` | product | raw.githubusercontent main URLs are pinned in each blueprint source_url |
| `docs/HANDOVER.md` | 1 | move | `dev/programme/HANDOVER.md` | programme | the one living handover |
| `docs/architecture.md` | 1 | keep | `docs/architecture.md` | product | user doc; URL stays stable for users and HACS |
| `docs/audit-2026-08.md` | 1 | archive | `dev/archive/audits/audit-2026-08.md` | archive | superseded by audit-2026-09, cited from README |
| `docs/audit-2026-09.md` | 1 | move | `dev/programme/register/audit-2026-09.md` | programme | evidence register the plan delivers against |
| `docs/automations.md` | 1 | keep | `docs/automations.md` | product | user doc; URL stays stable for users and HACS |
| `docs/backlog.md` | 1 | archive | `dev/archive/backlog.md` | archive | self-declared archive of reasoning (v3.14.0), cited from README and coordinator.py |
| `docs/configuration.md` | 1 | keep | `docs/configuration.md` | product | user doc; URL stays stable for users and HACS |
| `docs/dashboard-card.md` | 1 | keep | `docs/dashboard-card.md` | product | user doc; URL stays stable for users and HACS |
| `docs/decisions/` | 13 | move | `dev/governance/decisions/` | policy | ADR; code-owned, policy |
| `docs/delivery/` | 309 | move | `dev/programme/delivery/` | programme | delivery row |
| `docs/ecl110.md` | 1 | keep | `docs/ecl110.md` | product | user doc; URL stays stable for users and HACS |
| `docs/how-it-works.md` | 1 | keep | `docs/how-it-works.md` | product | user doc; URL stays stable for users and HACS |
| `docs/img/` | 14 | move | `docs/img/card/, docs/img/model/` | product | figures grouped by subject; page links edited in the same PR |
| `docs/plan-1067-rotenso-inputs.md` | 1 | archive | `dev/archive/plans/plan-1067-rotenso-inputs.md` | archive | finished programme plan, still cited (README, card.js, carry-1067) |
| `docs/plan-2026-09-open-issues.md` | 1 | move | `dev/programme/plan-2026-09-open-issues.md` | programme | plan of record, live |
| `docs/plan-card-decomposition.md` | 1 | archive | `dev/archive/plans/plan-card-decomposition.md` | archive | finished programme plan, still cited (README, card.js, carry-1067) |
| `docs/plan-open-issues.md` | 1 | archive | `dev/archive/plans/plan-open-issues.md` | archive | finished programme plan, still cited (README, card.js, carry-1067) |
| `docs/plan-v4.0.0-program.md` | 1 | archive | `dev/archive/plans/plan-v4.0.0-program.md` | archive | finished programme plan, still cited (README, card.js, carry-1067) |
| `docs/setup.md` | 1 | keep | `docs/setup.md` | product | user doc; URL stays stable for users and HACS |
| `docs/setup/` | 8 | move | `docs/img/setup/` | product | screenshots join docs/img |
| `docs/superpowers/` | 6 | move | `docs/design/<feature>/{design,plan}.md` | design | feature design and its plan side by side; plugin-specific folder name dropped |
| `hacs.json` | 1 | keep | `hacs.json` | root | GitHub/HACS/stamp convention; stays at the root |
| `icon.png` | 1 | delete | — | root | byte-identical to custom_components/heatpump_optimizer/icon.png; only reference is closure.py INERT |
| `tools/audit/README.md` | 1 | merge | `dev/audit/README.md + tools/pr/README.md` | policy | split: how a round runs (audit/) vs the PR instruments (tools/pr/); code-owned |
| `tools/audit/app_approve.sh` | 1 | move | `tools/pr/app_approve.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/app_comment.sh` | 1 | move | `tools/pr/app_comment.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/app_push.sh` | 1 | move | `tools/pr/app_push.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/approve_held_runs.sh` | 1 | move | `tools/pr/approve_held_runs.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/briefs/COMMON.md` | 1 | move | `dev/governance/roles/COMMON.md` | policy | role contract |
| `tools/audit/briefs/D0..D14.md` | 15 | move | `dev/governance/dimensions/` | policy | dimension brief |
| `tools/audit/briefs/fix-review.md` | 1 | move | `dev/governance/roles/fix-review.md` | policy | role contract |
| `tools/audit/briefs/fixer.md` | 1 | move | `dev/governance/roles/fixer.md` | policy | role contract |
| `tools/audit/briefs/judge.md` | 1 | move | `dev/governance/roles/judge.md` | policy | role contract |
| `tools/audit/briefs/orchestrator.md` | 1 | move | `dev/governance/roles/orchestrator.md` | policy | role contract |
| `tools/audit/briefs/root-cause.md` | 1 | move | `dev/governance/roles/root-cause.md` | policy | role contract |
| `tools/audit/briefs/verifier.md` | 1 | move | `dev/governance/roles/verifier.md` | policy | role contract |
| `tools/audit/bugclasses.json` | 1 | move | `dev/audit/config/bugclasses.json` | evidence | audit-round configuration and register |
| `tools/audit/check_scopes.py` | 1 | keep | `tools/audit/check_scopes.py` | instrument | audit-round instrument |
| `tools/audit/ci-version-edit/` | 2 | move | `dev/audit/harnesses/ci-version-edit/` | evidence | finder harnesses for pr-contract shapes |
| `tools/audit/finding.schema.json` | 1 | move | `dev/audit/config/finding.schema.json` | evidence | audit-round configuration and register |
| `tools/audit/handoff/` | 79 | archive | `dev/archive/handoff/` | archive | transport leftovers of merged fixes (r9-f2-solver-4/5, frictions, v6612 RCA) |
| `tools/audit/handoff/` | 1 | move | `dev/audit/rca/` | evidence | an RCA document; joins the other RCAs |
| `tools/audit/harnesses/` | 7 | move | `dev/audit/harnesses/` | evidence | cross-round harnesses (depth changes: recompute ROOT in d907/k1725) |
| `tools/audit/judge_batch.py` | 1 | keep | `tools/audit/judge_batch.py` | instrument | audit-round instrument |
| `tools/audit/ledger-layout/` | 1 | archive | `dev/archive/experiments/ledger-layout/` | archive | design demo for the mutation-ledger layout; cited by carries 1412/1617 (closed) |
| `tools/audit/merge_throughput.py` | 1 | keep | `tools/audit/merge_throughput.py` | instrument | audit-round instrument |
| `tools/audit/preflight.sh` | 1 | move | `tools/pr/preflight.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/prepare_baseline.sh` | 1 | keep | `tools/audit/prepare_baseline.sh` | instrument | audit-round instrument |
| `tools/audit/prepr.sh` | 1 | move | `tools/pr/prepr.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/push.sh` | 1 | move | `tools/pr/push.sh` | instrument | PR authoring/approval instrument; prepr.sh stays beside app_push.sh |
| `tools/audit/rca/` | 19 | move | `dev/audit/rca/` | evidence | root-cause documents |
| `tools/audit/record-predicate/` | 2 | move | `tools/policy/record-predicate/` | instrument | live: restored by governance/tests/pr-contract jobs |
| `tools/audit/rotation.json` | 1 | move | `dev/audit/config/rotation.json` | evidence | audit-round configuration and register |
| `tools/audit/round3/` | 120 | move | `dev/audit/rounds/round3/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round4/` | 325 | move | `dev/audit/rounds/round4/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round5-fix/` | 3 | move | `dev/audit/rounds/round5-fix/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round5/` | 63 | move | `dev/audit/rounds/round5/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round6/` | 57 | move | `dev/audit/rounds/round6/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round7-fix/` | 2 | move | `dev/audit/rounds/round7-fix/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round7/` | 43 | move | `dev/audit/rounds/round7/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round8-fix/` | 2 | move | `dev/audit/rounds/round8-fix/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round8/` | 249 | move | `dev/audit/rounds/round8/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/round9/` | 717 | move | `dev/audit/rounds/round9/` | evidence | audit evidence; one segment deeper under dev/, so the depth-computed roots are replaced by a root finder first (D3) |
| `tools/audit/scopes.json` | 1 | move | `dev/audit/config/scopes.json` | evidence | audit-round configuration and register |
| `tools/audit/seat/` | 5 | move | `tools/seat/` | instrument | seat helpers |
| `tools/audit/w5-g5-195-coverage/` | 18 | move | `dev/audit/waves/w5-g5-195-coverage/` | evidence | wave-5 coverage evidence, excluded corpus |
| `tools/audit/w5-partition/` | 2 | move | `tools/coverage/` | instrument | live: tests.yml runs coverage_tree.sh |
| `tools/audit/worktree_gc.sh` | 1 | move | `tools/seat/worktree_gc.sh` | instrument | audit-round instrument |
| `tools/gen_device_fixtures.py` | 1 | move | `tools/devices/gen_device_fixtures.py` | instrument | device-fixture instruments grouped |
| `tools/measure_prefill_corpus.py` | 1 | move | `tools/devices/measure_prefill_corpus.py` | instrument | device-fixture instruments grouped |
| `tools/merge/` | 1 | keep | `tools/merge/` | instrument | already categorised |
| `tools/release/` | 1 | keep | `tools/release/` | instrument | already categorised |
| `tools/replay/` | 2 | keep | `tools/replay/` | instrument | already categorised |

## 4. References

### 4.1 Counts

There are 1,471 **live** references, meaning exact-path mentions in files that stay live. There are 7,219 **historical** references, in RELEASE_NOTES, delivery rows, round evidence, archived plans and rosters, and closures.json (which is regenerated rather than edited). D2 leaves the historical ones alone.

The ten heaviest units by live references:

| unit | live refs |
|---|---:|
| .claude/workflows/policy_lint.mjs | 117 |
| docs/HANDOVER.md | 94 |
| tools/audit/round9/** | 42 |
| tools/audit/briefs/D*.md | 40 |
| tools/audit/briefs/fixer.md | 38 |
| tools/audit/round6/** | 35 |
| docs/plan-2026-09-open-issues.md | 31 |
| tools/audit/README.md | 30 |
| tools/audit/round4/** | 27 |
| .claude/rules/gate-scoping.md | 27 |

`references.tsv` has all 128 units, and `references-detail.tsv` has every file:line.

**Basename citations are not caught.** brief_lint's `lookupPath` falls back to a unique basename (brief_lint.mjs:127-132), so prose like `fixer.md` or `HANDOVER.md` keeps "resolving" after a move. A stale directory prefix in prose is caught by nothing today. RO-1's check adds a retired-path arm for exactly this (section 7).

**Out-of-tree references.** The r9 roster (handoff branch), /mnt/project-files/audit-r9/* and #201 cite the current paths. By the time this lane runs, every r9 group before it is done. The lane rewrites only groups that are still live, and every RO brief cites its paths with a SHA.

### 4.2 Incorrect paths already in the tree (fixed by RO-9)

| where | what | fix |
|---|---|---|
| docs/HANDOVER.md:22 | cites `.claude/workflows/wave-r9-groups.json`, which is not on main (it is on handoff/audit-r9-fixplan) | name the branch |
| docs/decisions/0005-…:5 | cites `docs/plan-2026-09-governance-audit.md`, which was never in the tree at any commit (`git log --all` is empty) | status note, since the ADR body is immutable |
| docs/decisions/0010-…:153 | cites `.claude/workflows/audit-merge.js`, deleted by 93ae8de4 | status note |
| .claude/workflows/carry-1398.json:19 | `tools/audit/round6/D8/matrix.py` is not in the tree and has no SHA | archived with the carry; the archive README notes it |
| .claude/workflows/carry-1653.json:17, carry-1668.json:19 | round9/D14/sweep/… is on the sweep commits (51a2e98a, 1152a743), not on main | add the SHA on move |
| .claude/workflows/wave-r8-groups.json:105, 196, 358 | round8/D3/s1_*.py and round8/D8/s1_finite_boundary.py were never on main | archived; noted |
| custom_components/…/quality_scale.yaml:4, 180; tests/config_flow_steps.py:376, 442; .claude/workflows/web-decomp-stage.js:148; tools/audit/harnesses/README.md:5, 16 | `tools/audit/round1|round2/…` exists only at tag audit-round2-evidence | cite the tag |
| docs/configuration.md:427-428, modbus_prefill.py:6, tests/features.py:45139, tests/config_flow_steps.py:5689 | tvofi/tuya_heat_pump paths written as if local | write full GitHub URLs |
| .claude/workflows/policy_lint.mjs:169 | the grep exclude `:!tools/audit/round2` is dead | drop it |
| .claude/workflows/audit-wave.js:14 | `.claude/workflows/lib/audit-prompts.js` | hypothetical in prose; leave |

The script's other hits are fixture strings inside self-tests (`docs/a.md`, `tests/x.py`, `…/pull/N`) or deliberate examples (`docs/handovers/` in writing-for-agents.md). They are correct as written.

## 5. Mechanical barriers: what breaks when a path moves

Two independent sweeps were run: one over tests/, and one over .claude/workflows, tools/ and .github/.

### 5.1 Four facts decide the sequencing

1. **A pure `git mv` is scoped only by its destination** (closure.py:1909 `git diff --name-only`, renames on). A file a test reads, moved to an INERT destination, gives `MODE: SCOPED -- 0 script(s) run`: a green branch and a red main, the #354 shape. The move PRs are safe only because each also edits closure.py or closures.json, which are GATE_FILES and force FULL. The layout check in RO-1 is `run_always` for the same reason.
2. **The graders are restored from the base.** Six jobs run `git checkout "$PINNED" -- '.claude/workflows/*.mjs' '.claude/workflows/*.py' '.claude/workflows/vendor' 'tools/audit/*.sh' 'tools/audit/record-predicate' 'tools/audit/round6/D11/fix/codeowners_gap.py'`: governance.yml:121-130, 376-385, 426-435; tests.yml:447-456; pr-contract.yml:81-90; budget-raise-gate.yml:54-57. So a PR that moves a grader is graded by the base's copy with the old path constants, and a pathspec for the new directory fails with "did not match" under `set -e`. The instruments must first learn both locations (RO-2), then move, and only then drop the old ones (RO-9).
3. **entities.py runs the whole policy lint** (entities.py:24118-24129, rc must be 0). A moved policy file that POLICY_GLOBS misses, a stale key in policy_budgets.json, or a stale backticked citation turns entities.py red. Because node-child reads sit outside its closure, this shows on main only.
4. **Silent vacuity is the main trap.** These checks pass on nothing after a move:
   - harness_headers.py:107 and 160 `round*/D*/*.py` globs come back empty, so "every live-header harness is executed" passes vacuously.
   - harness_headers.py:128 `REGISTER_DIRS`: `git status -- <missing>` returns rc 0 and empty output.
   - rules_sync.mjs:32-33: if SRC and OUT both move, `--check` passes on 0 files.
   - delivery_status.py:480 `ROW_DIR`: the delivery-status job reads every merge as rowless.
   - prepare_baseline.sh:49 `rm -f docs/audit-*.md docs/backlog.md`: the finder wall opens silently.
   - codeowners_gap.py:138 EXEC only recognises `(tests|tools|.claude|.github)/`: instruments under a new top-level directory leave the enforcement surface.
   - policy_lint POLICY_DIRS:297-304: moved policy escapes the coverage check.

   Every RO brief names the vacuity arms it must re-point, and each re-point is proved by a planted case that fails.

### 5.2 Barriers that must change together with each move

| barrier (file:line on main) | breaks on move | moves with |
|---|---|---|
| tests/closure.py:217-359 INERT (docs/ 228, tools/audit/ 250, .claude/ 270, .cursor/ 273), 423-437 HANDOVER_DIR, 470-583 INERT_EXCEPT, 587-614 `_is_header_corpus` (`len(parts)==5` becomes 6 under dev/), 2462-2467 selftest pin (run_always) | orphan "these force the FULL suite when touched" (entities.py:13710); #357 INERT-and-recorded refusal; the selftest fails on every branch | every RO move PR |
| tests/closures.json (249 paths under moved dirs) | PHANTOM (closure.py:1568), then UNDER-SCOPED (1645) | `closure.py prune` plus Linux `derive_closures.sh --single` for entities, harness_headers, doc_claims, md_tables, card_drift, never a full re-derive (gate-scoping.md) |
| tests/entities.py module-scope reads 17063, 22373, 22485 (plus 786, 826, 1012 for user docs) | the whole run aborts | RO-3, RO-6, RO-8 |
| tests/entities.py handover block 13729-13768; the `docs/` INERT probe 16291/16336; `_493_FILES` 17875; the tools/ non-audit check 18852-18857; node calls to .claude/workflows/*.mjs (≈15 sites 21855-24121); workflow-text pins 21797-21821, 22566-22850, 24157-24168; the CFR/dora/judge_batch checks 23637-23822, 26876-26928 | named checks fail | RO-5, RO-6, RO-8 |
| tests/harness_headers.py:99-103, 107, 128, 160 (the glob gains a segment); tools/audit/round4/D6/claims.py:173-174, 240-244, 307; tests/env_drift.py:1839-1840; tools/release/stamp.py:131-133 (REGISTER_DIR, **no release can be stamped if wrong**) | vacuous passes; stale register | RO-8 (all four agree; regenerate claims.json and claims.md) |
| tests/delivery_status.py:121-124, 480; tools/release/stamp.py:1503-1506 RECORD_CLASS_RES; .claude/workflows/policy_lint.mjs:1907, 1915, 2275-2278, 5795-5800 | rowless merges and OVERDUE; the record-class carve-out fails closed | RO-5, all copies in one PR (policy_lint refuses drift between them) |
| .claude/workflows/policy_lint.mjs:237-271 POLICY_GLOBS, 297-304 POLICY_DIRS, 451-566 CORPUS_EXCLUDED, 592/1485/3161 data paths, 625, 947, 1032, 2393, 2533; policy_budgets.json files/files_tokens/roles.opens; policy_known_bad.json keys; corpus_excluded.json (≈70 entries) | orphan caps, FIXTURE VACUOUS, unlisted known-bad; **re-keying roles.opens reads as a raise in budget_raise_gate.py:194-203** | RO-5 (owner review, budget-raise-gate) |
| .claude/workflows/brief_lint.mjs:194, 200 (`:!.claude`), 830, 934, 1262-1264 roster directories; check-wave-script.mjs siblings and tools/audit/* data (579-938); counts.mjs:60-71; rules_sync.mjs:32-33; fragments_sync.mjs:31, 104-127; field_coverage.mjs DECLARED 329-343 | lint runs on nothing; ENOENT; registry refusal | RO-5 and RO-6 |
| depth-relative ROOT: policy_lint:90, brief_lint:62, counts:22, rules_sync:30, fragments_sync:29, figure_lint:94, field_coverage:53, check-wave-script ×5 (all `..','..'`); the round harnesses (72 files at 754d2319 use `parents[N]`, `.parent.parent` or `../../..`, including option_doc_coverage.py:116, dora_cfr.py:54, codeowners_gap.py:128 and claims.py); judge_batch.py:73; d907/k1725; make_*_figures | wrong root: a harness reads or writes the wrong tree, or crashes | tools/policy stays at the depth of .claude/workflows, so the instruments are unchanged. The round harnesses go one segment deeper (D3 nested), so **RO-7** replaces every depth-computed root with a root finder (walk up to the directory holding custom_components/heatpump_optimizer/manifest.json) in place, before anything moves, and proves byte-identical output. judge_batch and the harnesses/ scripts are recomputed in the same group |
| .github/CODEOWNERS (17 moved patterns, including the COMMON.md un-own line) | **moved policy becomes unowned: a governance hole** | the same PR as each move |
| .github/workflows restore pathspecs and invocations (governance.yml 121-598, tests.yml 447-594, pr-contract.yml 81-252, budget-raise-gate*.yml 54-70) | see 5.1.2 | RO-2 (both paths), RO-6 (new), RO-9 (old dropped) |
| .claude/hooks/stop-selfcheck.sh:28, 51-56, 195 POLICY_PREFIXES | a policy edit at a new path skips the lint silently | RO-5 |
| tools/audit/prepr.sh, push.sh, preflight.sh, app_comment.sh:52, app_push.sh:142 (prepr beside it), seat/*.sh, prepare_baseline.sh:49-52, tools/audit/scopes.json:328-623 universes, finding.schema.json:38, 55 | local gate, self-tests, the finder wall, audit cells | RO-6 and RO-8 |
| README.md and docs/*.md relative image and page links; tests/md_tables.mjs:33, 38; tests/doc_claims.py:66, 175, 204; entities.py:1395 hero | broken main links and failing figure checks | RO-3 |
| .gitignore:43 `.claude/workflows/.*.mutant-*.mjs` | leftover mutants become untracked | RO-6 |

Not affected: structure.py and the structure budgets (they measure custom_components/ only), mutation_table.py and the ledger layout, workflow `on: paths:` (there are none), HACS README rendering on old releases (HACS resolves relative links against the release tag).

## 6. Placement in the endgame register

**The default stands: this lane runs last.** Every move touches tests/closure.py, tests/closures.json and tests/entities.py, and so does every code branch through the closures autofix. Every live r9 brief also cites tools/audit/briefs/fixer.md, tools/audit/app_push.sh, CLAUDE.md, .claude/rules and round9 evidence paths. Moving them mid-programme would re-brief every open seat.

**One piece comes forward.** RO-1 is the layout manifest and its check in report-only mode. It adds only new files plus one run.sh line, so it can land now that the decisions are answered, off the critical path. From then on it measures the distance to the target, and every later RO PR shows its step on that meter.

```
RO-1 (report-only layout check; can land now, off the critical path)
R9-EG-A4, R9-F10.7, R9-F11.7, R9-EG-R1, R9-SW-3, R9-SW-4, R9-F11.5, R9-F6.4, RO-1
   └─> RO-2 dual-path instruments ─> RO-3 product docs ─> RO-4 archive + merge
       ─> RO-5 governance + programme lift ─> RO-6 instruments ─> RO-7 harness root finder
       ─> RO-8 audit evidence ─> RO-9 drop fallbacks, reference sweep, enforce the check
```

The chain is serial because all nine groups edit closure.py, closures.json and entities.py. Each group is sized as one PR: one category per PR, and main stays green after each merge.

| group | model (fixer / reviewer) | what | owner gate |
|---|---|---|---|
| RO-1 | opus / opus | tests/layout.py and tests/layout.json in report-only mode, with a self-test and null controls (section 7) | yes: new test script wired into run.sh and derive_closures.sh; a CODEOWNERS line for the manifest |
| RO-2 | opus / opus | Every grader that a workflow restores from the base resolves its data and sibling paths new-first, then old. The restore pathspecs list both globs and tolerate absence. | yes: .github/workflows, budget_raise_gate.py, contract_rerun.py, stamp.py |
| RO-3 | sonnet / opus | docs/img/{card,model,setup} and docs/design/<feature>/; README and page links; doc_claims, md_tables and the entities hero pin; closure INERT_EXCEPT; regenerate the D6 register | yes: closure.py and the entities checks are code-owned |
| RO-4 | opus / opus | dev/archive/ with its README, holding the superseded plans, rosters, closed carries, handoff leftovers and ledger-layout. Delete `icon.png` and `.abacus.donotdelete` (D4). Apply the merge candidates in 3.2 and the ADR superseded-by corrections. Re-point the code comments. | yes: the ADRs, policy_budgets roles.record.opens (it names wave-4-groups.json), tools/audit/README.md |
| RO-5 | opus / opus | Lift dev/governance/ and dev/programme/. The rules source moves (D1) and .claude/rules becomes generated. Roles, dimensions, decisions, policy config, HANDOVER, plan, delivery/, live carries and the register move with it. Re-account policy_lint and re-key the budgets; re-record known-bad; update CODEOWNERS, CLAUDE.md, AGENTS.md, SKILL.md, the PR template and the rule texts. | yes: policy plus budget (budget-raise-gate) |
| RO-6 | sonnet / opus | tools/policy, tools/pr, tools/seat, tools/coverage and tools/devices; the workflow invocations and new restore pathspecs; the hook prefixes; .gitignore | yes: .github/workflows, hooks, CODEOWNERS |
| RO-7 | sonnet / opus | **In place, before any evidence moves:** replace every depth-computed repository root in the round harnesses, harnesses/, ci-version-edit/, the wave-5 coverage scripts and judge_batch with one root finder. harness_headers' executed list and every committed output must be byte-identical. | yes: the codeowners_gap harness is restored by the governance jobs |
| RO-8 | opus / opus | Move dev/audit/ (rounds, rca, harnesses, config, waves). Update harness_headers globs (+1 segment) and the `_is_header_corpus` depth. claims.py, env_drift and stamp REGISTER_DIR must agree. Re-point the entities module-scope reads, corpus_excluded, the scopes universes and the finder wall; widen codeowners_gap EXEC to dev/. | yes: stamp.py, env_drift.py, closure.py, codeowners_gap |
| RO-9 | sonnet / opus | Drop RO-2's old-path fallbacks and old pathspecs. Rewrite the remaining live references (4.1) and the incorrect paths (4.2). Flip tests/layout.py to enforcing. | yes: workflows, policy text, required contexts |

tvofi reviews nine PRs. Only RO-1 comes before the programme ends, so RO-2 to RO-9 can be batched into one review session. GitHub shows most of those diffs as renames.

## 7. The layout barrier (tvofi, 15:01Z)

**Manifest**: tests/layout.json, code-owned. It holds:

- `categories`: an ordered list of `{name, globs, why}`. The categories are root, product (custom_components, blueprints), docs, tests, dev/governance, dev/programme, dev/audit, dev/archive (no other folder under dev/), tools (only the subfolders in section 2), agent-config (.claude allowlist, .cursor/rules, root harness files), ci (.github).
- `retired`: one entry per moved prefix, `{old, new, since}`, generated from inventory.tsv by each RO PR for the units it moves.
- `historical`: the prefixes the reference arm skips: dev/archive/, dev/audit/rounds/, dev/programme/delivery/, RELEASE_NOTES.md, tests/golden/, tests/mutation_ledger/, tests/closures.json.

**Checker**: tests/layout.py. It is `run_always`, because a pure rename is scoped only by its destination (5.1.1). Four arms:

1. **Category**: every `git ls-files` path matches exactly one category glob, or it is refused with "outside the allowed categories: <path>". Matching none or two is refused. `.claude/` admits only its allowlist (settings.json, hooks/*.sh, skills/*/SKILL.md, rules/*.md as generated, workflows/{audit,web}-*.js, workflows/web-fragments.md).
2. **Retired path, file**: no tracked path starts with a `retired.old`. Otherwise: "reintroduces moved path <old>; it lives at <new> since <PR>".
3. **Retired path, reference**: no live text file (every tracked text file outside `historical`) mentions a `retired.old` path as a path token. Otherwise: "<file>:<line> cites retired path <old>; use <new>". This closes the basename-fallback gap in brief_lint (4.1).
4. **No dead categories**: every category glob and every `retired` entry matches at least one file or reference target. A glob that matches nothing is a check that measures nothing.

**Null controls**: `--self-test`, run in the same job. It builds a throwaway repo from the real manifest and plants one case per arm, and each case must go red:

- `docs/notes/x.md` (outside every category)
- `tools/audit/briefs/fixer.md` re-added (a retired file)
- a line citing `.claude/workflows/policy_lint.mjs` in `docs/setup.md` (a retired reference)
- a category glob `nothere/**` (a dead category)

Each negative control must stay green:

- the same citation under `dev/archive/`
- the retired path inside a delivery row

The real tree must be green. The self-test also requires that the checker enumerated at least as many files as `git ls-files | wc -l` prints. That is the vacuity guard, since the file count is derived and never carried.

**Rollout**: RO-1 lands the manifest as the **target** layout, with `retired` listing every planned move and `--report` exiting 0. It prints per-arm counts, and those counts are the lane's progress meter. Each RO PR adds its `retired` entries as it moves. RO-9 makes the check enforcing (exit 1), wires it into `fast`, and lists it in the required contexts, as R9-EG-A4 does for the architecture score. Adding a category later is a manifest edit, so it gets owner review.

## 8. Risks

- The **Workflow tool lookup** of `.claude/workflows/*.js` is assumed from its `meta` export, not confirmed. If the tool does not need that directory, the scripts could move to tools/. They stay until confirmed.
- **HACS and external links**: user doc URLs are kept (D-default). Only README's own image moves, and old releases resolve against their tag.
- **Linux-only closure re-derivation**: cloud seats have Linux. The Mac must not run the full derive_closures.sh (gate-scoping.md).
- **Policy corpus accounting (RO-5)**: moving prose must leave `corpus_tokens` and the role caps flat. The drop in `always_loaded_tokens` is a reclassification, and it is recorded as one (ratchet-budgets.md).

## 9. Verification of this proposal

- `node .claude/workflows/brief_lint.mjs .claude/workflows/wave-r9-groups.json` on handoff/repo-reorg-plan reports the same three errors as its base d13d6726, and none of them is in an R9-RO entry. The three are R9-F1.7's carry-1655 path (reported twice) and R9-EG-B3's sensor.py:1511 anchor, which has drifted to line 1481. They belong to their own groups, and the Mac seat corrects them.
- `node .claude/workflows/check-wave-script.mjs` fails the same two roster-shape checks at the base and at this head. The r9 roster uses `not-started`, `fixing` and `rca-done` stages, which the wave script does not branch on. The nine new groups use `not-started`, like every other r9 group.
- Every `after` edge names a group in the same file.
