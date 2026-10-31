# D11-s2 — round 9, governance: the policy prose and its wiring

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, box B3 (4 CPUs, shared with D0-s3 and three light seats).
Cells (`check_scopes.py --seat D11-s2`): M1–M4 over `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`,
`.cursor/rules/*.mdc`, `.claude/settings.json`, `.claude/skills/steward/SKILL.md`. Every number below is
a count, contention-immune; `load1` is printed by each harness.

## Method

M1 inventory built from the tree (the refusals my files say a mechanism enforces), each driven with a
planted defect in a throwaway `git clone` of HEAD (`controls.py`, `hooks_matcher.py`). M2 by executed
checks on the tree and on GitHub's records (read-only); the standards' own text could not be fetched on
this host. M3: `policy_lint.mjs --budgets`, `--stats --since v6.7.0`, `policy_lint_mutants.mjs`, a
12-PR conformance sample (the first-parent merges before the baseline), staleness of quoted output and
cited symbols. M4: each finding carries a perturbation executed in memory or in a clone.

## Findings

| id | step | sev | claim | harness | value | perturbation → |
|---|---|---|---|---|---|---|
| D11-s2-01 | M3 | medium | per-file policy caps count lines: +600 bytes on an existing line of 7 zero-headroom files draws 0 budgets errors in 7/7; as 8 new lines, refused 7/7 | `caps_unit.py` | joined_unrefused=7 | byte cap beside the line cap → 0 |
| D11-s2-02 | M1 | medium | `policy_lint --hooks` never reads `matcher`: 4/4 matchers that miss every edit tool pass as wired | `hooks_matcher.py` | variants_refused=0 | matcher check in cmdHooks → 4 |
| D11-s2-03 | M2 | medium | `budget_raise_gate.approval` keys on the tvofi account; 6/6 owner approvals counted at head in the sample were seat-given by their own body; 0 human ones at head | `owner_review.py` + `reviews_snapshot.json` | 6 of 6 | seat approvals via own App → 0 |
| D11-s2-04 | M3 | low | CLAUDE.md rule 1 quotes `MODE: SCOPED — 0 script(s) run` (printer writes `--`) and says FULL prints zero (it prints no count): 0/2 hold | `mode_line.py` | 0 of 2 | em dash in print_plan → 1 |

D11-s2-03 is the owner's own delegation, not a breach: the point is that CLAUDE.md ("only `@tvofi`
reviews code-owned paths", "approval is the owner's approving GitHub review") names a human oversight
point GitHub's record cannot distinguish from a seat, and the delegation lives only in review bodies,
not in `docs/decisions/`.

## Mechanism inventory (my cells; rows derived from the tree)

| mechanism | refuses | runs | positive control | leaves uncovered |
|---|---|---|---|---|
| `rules_sync.mjs --check` | `.mdc` drift, orphan `.mdc` | PR (governance.yml policy-docs, base copy), prepr.sh | C1, C2 fired | parser differs from policy_lint's `rulePaths` (lead) |
| policy_lint `budgets` per-file | a capped file over its line cap | PR + main | C6 fired | prose growth on existing lines (D11-s2-01) |
| policy_lint `budgets` aggregates | always/corpus/role tokens over cap+band | PR + main | not driven here (band 500) | growth inside the band |
| policy_lint `counts` | a stated cap that disagrees | PR + main | C3 fired | — |
| policy_lint `rule-binding` | dead `paths:` glob, unbound capped file | PR + main | C4 fired | whether the RIGHT rule binds (stated in code) |
| policy_lint `index` | a policy file CLAUDE.md does not name | PR + main | C5 fired | — |
| policy_lint `--hooks` | hook not wired / missing / self-test failing | PR (governance.yml:172), prepr.sh | script renamed → refused | matcher (D11-s2-02) |
| `pre-edit.sh` (wired by settings.json) | VERSION/manifest/heading off main; `.cursor/rules/**` | edit time, Edit/Write/MultiEdit/NotebookEdit | self-test 16/16 | Bash-tool writes by construction of the matcher |
| `budget_raise_gate.approval` (decision 0013, CLAUDE.md rule 2) | a budget raise without owner approval at head | PR | its self-test | who is behind the owner account (D11-s2-03) |
| `policy_lint_mutants.mjs` | an emptied check class | PR | 22/22 pinned | — |

## Standards scorecard (executed check per row; standards text not fetched — unverified references)

| criterion | standard | executed check | result | gap |
|---|---|---|---|---|
| Code-Review | OpenSSF Scorecard | reviews of 12 merged PRs | 12/12 approved by a non-author identity; 11/12 at merged head | identities share one operator (D11-s2-03); #1621 approval off-head (lead) |
| Security-Policy | Scorecard / Best Practices | `cat SECURITY.md` | present, private advisory channel | — |
| accountability, reviewer ≠ author | NIST AI RMF GOVERN / AI 600-1 | author/approver logins | author hpo-author[bot] 12/12; approver App or tvofi | provable at App level, not at seat level |
| human oversight point | NIST AI RMF GOVERN | `owner_review.py` | 0 human owner approvals at head in the sample | D11-s2-03 |
| documented roles | NIST AI RMF GOVERN | CLAUDE.md role table vs `tools/audit/briefs/` (index class) | C5 fired; index clean | — |
| continual improvement | ISO/IEC 42001 §10 | `--stats --since v6.7.0` | decision-0013 friction at 5 PRs, issue #1640 open | root-cause seat beside it not checked |
| excessive agency / prompt injection | OWASP LLM Top 10 | read settings.json | `allow` = WebFetch, WebSearch, Read, Glob, Grep; no `deny`; untrusted-text rule is prose (COMMON.md, writing-for-agents.md) | no mechanical control; not measured |

Branch-Protection, Dangerous-Workflow, Token-Permissions, Pinned-Dependencies, CI-Tests, SAST,
Maintained, Signed-Releases and SLSA sit in `.github/` and `tools/` (D11-s1's cells).

## Conformance (sample: `git log --merges --first-parent -12 1936d5ca`, PRs 1638 1637 1639 1636 1635 1633 1634 1632 1631 1621 1617 1619)

| obligation (where stated) | fraction |
|---|---|
| authored by hpo-author (CLAUDE.md identity) | 12/12 |
| `docs/delivery/<N>.md` row (delivery-status-tracking.md) | 12/12 |
| an approving review at the merged head | 11/12 |
| owner approvals at head that are human-distinguishable | 0/6 |
| first pr-contract run green at head; red check answered | not sampled (unfinished) |

## Non-findings

Controls 6/6 (`controls.py`); rules_sync wired on every PR; policy_lint TOTAL 0 at baseline; mutants
22/22; hooks 3/3 self-tests; my cells' add:delete since v6.6.0 = 265:216; 12/12 cited symbols resolve.
Full list with commands in `report.json`.

## Ranked changes

1. D11-s2-03 — record the approval delegation as a decision and route seat approvals through a distinct App
   (NIST GOVERN, Scorecard Code-Review meaning); ~0 s per merge, ~10 lines of policy.
2. D11-s2-01 — byte/token per-file caps (ratchet integrity); one comparison per file, <1 ms per run, a
   re-recorded `files{}`.
3. D11-s2-02 — matcher check in `cmdHooks` + one fixture; <1 ms, ~5 lines.
4. D11-s2-04 — one-line CLAUDE.md correction.

## Unfinished

M2: standards text not fetched (WebFetch prompt unanswerable here); Scorecard tool not run. M3: the
pr-contract-first-run and red-check-answered fractions need per-head check-run listings.

## Exposure

GitHub read-only: closed PR list, reviews of the 12 sampled PRs, PR search for decision-0013, issue
search (#1640). `policy_lint --stats` read merged-PR verdicts for v6.7.0..origin/main. No earlier-round
evidence opened; `tools/audit/round3/D11/conformance_raw.json` and `tools/audit/round7/QUIET.md`
appeared only as `git grep -l` hits and were neither read nor cited.

## Harnesses

`_common.py` (helpers), `caps_unit.py`, `hooks_matcher.py`, `owner_review.py` (+ `reviews_snapshot.json`),
`mode_line.py`, `controls.py`: each runs from the export root with the command in its header, and
writes only under a `$TMPDIR` temp root (clones of HEAD).
