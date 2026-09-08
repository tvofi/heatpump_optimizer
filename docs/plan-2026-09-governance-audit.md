# Repository governance audit: execution plan

## Context

`tvofi/heatpump_optimizer` is developed almost entirely by LLM seats in multi-day sessions. Its governance corpus is about 31,000 lines across `CLAUDE.md`, five `.cursor/rules/*.mdc`, eighteen briefs under `tools/audit/briefs/`, `tests/README.md`, four workflows, `docs/HANDOVER.md`, the plan of record and 22 orchestration files under `.claude/workflows/`. It already has a strong mechanical substrate: a closure-scoped gate, a structural ratchet, claimed goldens, an orphan-file check, a single-handover check, a citation linter with a rot-pin fixture, and eleven release refusals. The owner's mandate is to audit whether the corpus prevents degradation over long agent-driven cycles and to redesign it so every rule is either mechanically enforced or explicitly labelled honor with a reason, every document is small enough to load and impossible to leave stale, and the policy set improves itself.

This session ran a read-only discovery over twelve governance surfaces (about 1,170 rules extracted, 366 load-bearing classifications adversarially re-verified), five cross-cut analyses, a public-standards benchmark, and a three-lens design panel with a judge. The measured baseline is in Appendix A. The headline: about 60 percent of rules are honor-system, the three files every seat opens first are 85 to 97 percent honor, `CLAUDE.md` is parsed by nothing, governance prose only grows (6.8 lines added per line deleted; 13 of 15 policy commits incident-born), 27 counts in policy text are wrong and all drifted the same way, thirteen terms have two definitions, three seats named by contracts are dispatched by nothing, and the programme's own record shows 55 percent of review verdicts blocked. The prose is uniformly stricter than the machinery that implements it, so every prose-versus-mechanism conflict resolves toward the permission.

Live state matters: GitHub main moved nine commits past this branch's base during the session (a 338-line orchestrator contract landed, `CLAUDE.md` grew 65 lines, the brief linter was found to have been linting nothing and was repaired, one PR merged without review, v6.3.18 was stamped). Seven PRs were open at last read, four of them policy PRs. The plan below is sequenced against that and re-measures at every phase boundary.

**Authority for this session.** The owner has granted this session complete and unconditional authority to merge policy changes and to perform GitHub-account actions where they are technically possible, scoped to this audit and to this session only. Consequences, applied throughout: the audit merges its own policy PRs after the repository's adversarial fix-review protocol, one at a time, with the main gate green after each; the owner-approval clause of `CLAUDE.md` "Changing any of it" is recorded as discharged by this grant in an ADR and in every policy PR's `## Approval` section; the audit attempts the GitHub-side controls itself and records the response rather than deferring them. The grant does not extend to release stamps, or to PRs authored outside the audit except where landing or superseding them is needed to unblock an audit rewrite of the same file. After this session, policy merges revert to owner approval, or to the mechanical form in section 4.9.

**What the container can actually reach (measured this session, read-only).** The proxied credential authenticates as the owner but carries `permissions: {admin: false, maintain: false, push: false}` on the repository object. Two Settings questions are now answered without the owner: `GET /repos/tvofi/heatpump_optimizer/rulesets?includes_parents=true` returns `[]` and `GET .../rules/branches/main` returns `[]`, so no repository ruleset and no inherited ruleset applies to main. That is the authoritative confirmation the earlier `protected: false` flag could not give. Blocked with 403: branch protection, code-scanning default setup and alerts, `actions/permissions`, `hooks`, `collaborators/<user>/permission`, and every org-level path ("sessions are bound to their configured repositories"). The GitHub MCP server exposes no rulesets, protection, code-scanning or settings tool at all. So ruleset creation is attempted once through REST and its status recorded; if it refuses, the ruleset specification is handed to the owner as a paste-ready block rather than left as an open question.

## 0. Operating rules for the audit session

- Policy is `CLAUDE.md`, `.cursor/rules/*.mdc`, `tools/audit/briefs/*`, plus the new `.claude/rules/*.md`, `.claude/settings.json` and `.claude/hooks/*` (`CLAUDE.md` "Changing any of it"). Under the session grant the audit merges its own policy PRs. Every such merge satisfies the repository's own preconditions first: a fix-review verdict `merge` posted from a detached worktree at the head SHA; every check green or skipped; the body names the measured head SHA; the three-dot diff on `VERSION`, the manifest and the notes heading is empty; `## Approval` cites the grant ADR. One merge at a time; the next merge waits for the unscoped main gate to go green on the previous one (`CLAUDE.md` rule 1: a push to main forces `full`).
- Every merge owes its record in the same session: a row in the plan of record's new "Governance programme" section, `docs/HANDOVER.md` `updated-for:` re-pointed when the handover changes, and one #201 comment per merge (`delivery-status-tracking.mdc`).
- The audit takes no release stamp. If a stamp falls due, the fact is posted on #201 for the owner; policy files are INERT, so no audit merge moves a fixture.
- The audit never pushes to another PR's branch and never moves a frozen head (`fixer.md` "The handoff freezes the branch"). An open policy PR that edits a file the audit must rewrite (#592 `fixer.md`, #603 `fix-review.md`, #605 `orchestrator.md`) is landed first when it already carries a `merge` verdict and green checks, or superseded: its intent is folded into the audit's rewrite, the PR is closed with a comment naming the superseding PR, and the fold is listed in that PR's body.
- Every new tracked file is classified before push: a measured closure, the `INERT` tuple in `tests/closure.py`, or `INERT_EXCEPT` on main. `tests/entities.py` refuses an orphan with "these force the FULL suite when touched".
- Every check lands with a fixture it refuses and a null control on a healthy tree. A check that cannot be shown failing does not merge (`defect-root-cause.mdc` "A detector must be shown to detect").
- Every number in a PR body is re-derived by the reviewer. `check && publish`, never `;`.
- Line anchors into files under review are quoted phrases or symbols, never bare numbers: #603, #592, #605 and #602 move them.
- Live state is re-measured at every phase boundary, never taken from memory or from this plan.
- Nothing in this plan touches `tests/golden/*claimed_drift.txt`, `tests/structure_budgets.json`, `VERSION`, or `.github/workflows/tests.yml` while #596 is open.

## 1. Sequence and dependencies

| step | needs | parallel with | waits for |
|---|---|---|---|
| P1.0 full-depth clone, pin `BASE` | this container | nothing | nothing |
| P1.1 GitHub Settings probe, by the audit | this container | P1.2 to P1.10 | nothing; each endpoint is recorded as answered or 403 |
| P1.2 to P1.10 execute, re-baseline, inventory, synergy, staleness, probe, budget, rework, freeze map | P1.0 | P1.1 | nothing |
| P1.12 grant ADR `docs/decisions/0001-session-policy-merge-grant.md` merged first | P1.0 | P1.2 to P1.10 | nothing (docs/ is INERT; scopes to zero scripts) |
| P2 decision table, check catalogue, ADR drafts, harness defects handed off | P1 tables | nothing | nothing |
| PR-P0 land or supersede #603, #592, #605 | P1.10 freeze map | PR-T1 | each PR's own review verdict and checks |
| PR-T1 `policy_lint.mjs`, `rules_sync.mjs`, `fragments_sync.mjs`, budgets, fixtures, `governance.yml` | P1.6 seed | PR-P0 | nothing (new files under INERT prefixes; one MODE: FULL run because `.github/workflows/` is a gate file) |
| PR-T2 `STAGES`, `web-fix-wave.js` branches, VERDICT grammar, root-cause dispatch, `check-wave-script.mjs` wired | PR-T1 merged | PR-T3 | nothing |
| PR-T3 `.claude/settings.json` hooks, `tools/audit/prepr.sh` | P1.7 probe result | PR-T2 | nothing |
| PR-T4 `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, two INERT entries | nothing | nothing | #591 (edits the INERT region of `tests/closure.py`); if #591 is not merged within the session, PR-T4 adds its entries beside #591's and merges first, and #591 rebases |
| PR-P1 `CLAUDE.md` index, `.claude/rules/*.md`, generated `.cursor/rules` | PR-T1 merged and green on main | nothing | PR-P0 |
| PR-P2 D-briefs, `COMMON.md`, `judge.md` repaired | PR-T1 merged | PR-P1 | nothing (D5 decided in section 7) |
| PR-P3 `fixer.md` | PR-P1 merged | PR-P4, PR-P5 | PR-P0 (#592) |
| PR-P4 `fix-review.md`, verdict grammar | PR-P1 merged | PR-P3 | PR-P0 (#603) |
| PR-P5 `orchestrator.md`, MCP mapping | PR-P1 merged | PR-P3 | PR-P0 (#605) |
| PR-D1 README and register cuts | PR-T1 merged | PR-P3 to P5 | #602 landed or superseded the same way as PR-P0 |
| PR-D2 tag then delete | PR-P1 merged | nothing | PR-P1 (the index no longer cites deleted files) |
| PR-L1 `--stats`, `--record`, `--sunset`, proposal path | PR-T1, PR-T2 merged | nothing | PR-P4 merged |
| Record PR after each merge, or folded into the next audit PR when the gate is still running | the merge | the next PR's build | nothing |
| GitHub ruleset attempt via REST, status recorded | PR-T1 and PR-L1 checks exist on main | nothing | `governance.yml` green once; the audit tries, then hands the owner a paste-ready spec if refused |

Main-gate cost: every merge to main runs the full suite (about forty minutes). Twelve to fourteen merges serialised is about nine hours of gate time. The audit builds the next PR while the previous gate runs and merges only after green; it never re-gates an unchanged head (`docs/HANDOVER.md` "Never re-gate an unchanged head").

## 2. Target architecture

One line per file: audience; loader; size cap; enforcing check.

```
CLAUDE.md                           every seat; Claude Code auto-load; <=200 lines; policy_lint --budgets; index section generated from rule frontmatter and diffed
.claude/rules/                      canonical rules, flat names <scope>-<topic>.md; Claude Code mechanical load, paths: scoped
  policy-change.md                  every seat; always loaded; <=60 lines; policy_lint format + budgets
  verify-before-claim.md            every seat; always loaded; <=60 lines; same
  gate-scoping.md                   fixer, reviewer; paths tests/**, custom_components/**; <=120; same
  claims-goldens.md                 fixer, reviewer; paths tests/golden/**; <=120; same
  ratchet-budgets.md                fixer, reviewer; paths tests/structure_budgets.json, custom_components/**; <=120; same
  release-stamp.md                  orchestrator; paths VERSION, RELEASE_NOTES.md, manifest.json; <=120; same
  ci-autofix.md                     fixer; paths tests/closures.json, tests/golden/*_drift.txt; <=120; same
  record-tracking.md                orchestrator; paths docs/**, .claude/workflows/*.json; <=120; same
  finding-propagation.md            fixer, reviewer; paths .claude/workflows/*.json, tools/audit/briefs/**; <=120; same
  root-cause.md                     root-cause seat; paths tools/audit/briefs/**, .claude/workflows/**; <=120; same
.cursor/rules/*.mdc                 Cursor seats; Cursor mechanical; GENERATED by rules_sync.mjs; --check byte-diff; PreToolUse hook refuses hand edits
tools/audit/briefs/<role>.md        one role each (orchestrator, fixer, fix-review, judge, verifier, root-cause, COMMON for finders); opened by role via the index; <=120 lines; frontmatter role, dispatched-by, reads, returns
tools/audit/briefs/D0..D10.md       finders; opened by dimension; <=70 lines; citations + worktree: key
tools/audit/prepr.sh                fixer, orchestrator, Stop hook; hand-run; INERT by prefix; self-test in governance.yml on 10 fixtures
tools/audit/preflight.sh            unchanged (on main); called by prepr.sh
.claude/settings.json               Claude Code seats; harness; 3 hooks; policy_lint --hooks asserts each command exists and self-tests
.claude/hooks/session-start.sh      prints shallow state, installs the merge driver, prints the role read set; --self-test
.claude/hooks/pre-edit.sh           PreToolUse on Edit|Write|MultiEdit; exit 2 on VERSION, manifest, notes heading off main, .cursor/rules/, budget files; --self-test
.claude/hooks/stop-selfcheck.sh     Stop; runs prepr.sh when the diff touches policy or workflow paths; stop_hook_active guard; --self-test
.claude/workflows/policy_lint.mjs   the refusal for everything above; shares resolvers with brief_lint.mjs (lintBrief, assertAcceptanceFixture)
.claude/workflows/rules_sync.mjs    generator for .cursor/rules; --check
.claude/workflows/fragments_sync.mjs  web-fragments.md into the five web-*.js between markers; --check
.claude/workflows/policy_budgets.json one-sided caps: lines per file class, tokens per role read set
.claude/workflows/fixtures/policy-rot/  one fixture per policy_lint rule class, one per prepr.sh refusal
.github/workflows/governance.yml    jobs policy-docs, pr-contract, wave-script, record; never scoped; pull_request types opened, edited, synchronize, reopened; push to main; weekly schedule
.github/CODEOWNERS                  owner on policy paths, budgets, VERSION, manifest, .github/; INERT entry
.github/PULL_REQUEST_TEMPLATE.md    the H2 set the pr-contract parser requires; INERT entry
docs/decisions/NNNN-<slug>.md       ADRs, superseded-not-deleted; INERT by docs/ prefix; policy_lint checks superseded-by targets exist
docs/HANDOVER.md                    unchanged role; its Decisions section becomes links into docs/decisions/
```

Naming: rule files `<scope>-<topic>.md`, scope in {policy, verify, gate, claims, ratchet, release, ci, record, finding, root}. Rule ids `<stem>.<n>`, never reused. A seat locates doctrine from the generated index in `CLAUDE.md` (`## Every seat`, `## By role`, `## By task`, `## Live state`, `## Optional`), never by listing directories. Nested rule directories are not used until P1.7 proves the harness loads them. Always-loaded set: `CLAUDE.md` plus the two no-paths rules, at most 320 lines and 6,000 tokens (baseline 796 lines, 11,349 tokens).

## 3. Conversion table: honor to mechanical

Columns: obligation (source), level now, target artefact and command, standing cost, decision.

| # | obligation | now | target | cost | decision |
|---|---|---|---|---|---|
| 1 | open every rule at session start (`CLAUDE.md` "list that directory and open every rule") | honor | `.claude/rules` mechanical load; `rules_sync.mjs --check` for Cursor | 0 | convert, PR-P1 |
| 2 | policy index complete both ways | honor | index generated from rule frontmatter; `policy_lint` diffs committed text | 0.1 s | convert, PR-P1 |
| 3 | always-loaded size | none | `policy_budgets.json` one-sided caps; `policy_lint --budgets` | 0.1 s | convert, PR-T1 |
| 4 | derive counts, never carry | honor | numerals >= 2 outside EXAMPLE, REFUSED BY and BORN refused in rule bodies; nine derivations checked in prose files | 0.5 s | convert; warning in PR-T1, error after PR-P1 |
| 5 | citations resolve in policy files | linter aimed at rosters only | `policy_lint` over CLAUDE.md, rules, briefs, READMEs, HANDOVER, web-fragments; backticked identifiers are symbol candidates; second rot fixture | 2 s per PR | convert, PR-T1 |
| 6 | no `gh` in seat-facing text | none | regex `\bgh (pr\|issue\|run\|api)\b` = 0 outside the `web-fragments.md` mapping table | 0.05 s | convert, PR-T1 |
| 7 | one statement per obligation | none | a 12-word shingle shared across two policy files refused outside `>` quotes | 0.2 s | convert; known set snapshotted, drained in PR-P1 to P5 |
| 8 | policy-document format | none | frontmatter keys, block keys, `EXAMPLE`, 12-line block cap | 0.1 s | convert, PR-T1 |
| 9 | roster `resume.stage` vocabulary | none | `STAGES` defined once; `check-wave-script.mjs` asserts each; `web-fix-wave.js` branches on all | 0.5 s | convert, PR-T2 |
| 10 | `blocked: <reason>` consumed | none | verdict grammar with class; VERDICT schema pattern; roster patch `stage: blocked` | 0 | convert, PR-T2, PR-P4 |
| 11 | PR body carries evidence sections | honor | `policy_lint --pr-body` in job `pr-contract`; required H2 set from the template; `n/a: <reason>` accepted per section | 1 s per event | convert, PR-T1 |
| 12 | body head SHA equals live head | honor | `pr-contract` compares `## Head` to `github.event.pull_request.head.sha` | 0 | convert |
| 13 | forward-carry destination exists | honor | `## Forward-carry` is `none` or a path in `git ls-files` at head | 0 | convert |
| 14 | red check answered | honor | `pr-contract` lists `failure` check-runs via REST; each must be named under `## Red checks` | 1 s | convert; the analysis stays honor |
| 15 | never touch VERSION, manifest, notes heading in a branch | honor | `pre-edit.sh` exit 2 off main; `pr-contract` requires an empty three-dot diff on those paths | 0 | convert, PR-T3 |
| 16 | owner approval before merging policy | honor | in this session: discharged by the grant, recorded in ADR 0001 and in every policy PR's `## Approval`; standing: `policy:` title prefix, `## Approval` section, `Policy-Approved-By:` trailer checked on push to main, and CODEOWNERS plus required code-owner review once O1 gives cloud seats a distinct identity | 0 | paper trail converted now; the GitHub half needs a second identity the container cannot create |
| 17 | budget raise needs owner confirmation (`structure.py` `record_budgets` accepts any string) | local-check | `pr-contract` requires `## Budget raise` naming the owner's comment URL when any budget at head exceeds base; CODEOWNERS on the budget file. The audit raises no budget; the grant covers policy, not the ratchet | 0 | convert the paper trail; provenance stays honor |
| 18 | merge driver installed per clone | honor | `session-start.sh` runs `env_drift.py --install-merge-driver` and reads back `merge.claimnotes.driver` | 0.3 s per session | convert, PR-T3 |
| 19 | shallow-clone fiction (HANDOVER trap 11) | honor | `session-start.sh` prints `is-shallow-repository`; `prepr.sh` refuses when `git merge-base origin/main HEAD` fails | 0 | convert |
| 20 | `stress.py` exclusivity by process | honor | `tests/run.sh` refuses to start `tests/stress.py` when `pgrep -f tests/stress.py` is non-empty | 10 ms | convert, small PR after #596 |
| 21 | root-cause seat dispatched | none | `web-fix-wave.js` dispatches `rootCausePrompt` when the verdict class is `root-cause-unanswered` or `## Red checks` is non-empty | one seat per red-check PR | convert, PR-T2 (D5) |
| 22 | judge on every fix PR (`judge.md`) | honor, never seated | rule amended to round >= 3 or disputed verdict | 0 | amend; build nothing |
| 23 | stamp per merge / merge queue (`docs/audit-2026-09.md` Merge queue row) | honor, contradicted | section marked superseded; ADR records merge queue as considered | 0 | delete; build nothing |
| 24 | INERT restated in prose (`tools/audit/README.md` "tools/ is INERT") | honor, wrong | prose deleted; `closure.py` is the only home | 0 | build nothing, delete |
| 25 | box spec and tool-path literals | honor | derive from `nproc` and env; literals deleted | 0 | build nothing, delete |
| 26 | `load1 > 1.5` rejection (`judge.md`) | honor, unattainable | one copy citing the quiet-window section; the shingle check keeps it single | 0 | fix text, PR-P2 |
| 27 | two orchestration generations | none | `RETIRED:` prefix on `meta.description` of `audit-fix.js`, `audit-wave.js`, `audit-merge.js`, `web-phase0.js`; `triage-quiet-judges.json` deleted | 0 | retire, PR-D2 (D4) |
| 28 | hooks exist and detect (`defect-root-cause.mdc` claims one was built) | none | `policy_lint --hooks`: every `command` in `settings.json` exists and its `--self-test` refuses its fixture | 0.2 s | convert, PR-T3 |
| 29 | required checks at the merge boundary (measured: `rules/branches/main` returns `[]`) | honor | ruleset with named required checks, attempted by the audit via `POST /repos/.../rulesets`; the spec handed to the owner if the call is refused | 0 | attempt, 4.9 |
| 30 | check names vs jobs vs ruleset | none | job `record` compares check-run names on the last five PRs with job ids and the ruleset list | 1 s weekly | convert, PR-L1 |
| 31 | every merged PR has a record row | honor | `policy_lint --record --since <tag>` with `stamp.py`'s `PR_RE` refuses a merged PR absent from plan and handover; on push to main | 1 s | convert, PR-L1 |
| 32 | contract seats are dispatched and verdicts consumed | none | `dispatched-by:` must grep in a workflow script or read `manual: <reason>`; `returns:` entries need a consumer | 0.2 s | convert, PR-T1; exposes rows 10, 21, 22 mechanically |
| 33 | fragment copies in sync (`web-fragments.md`) | honor by hand | `fragments_sync.mjs --check` | 1 s | convert, PR-T2 |
| 34 | verify before claiming; quantifiers | honor | reviewer; `preflight.sh` stays advisory | 0 | honor: judgement, no refusal possible |
| 35 | mutation proof and null control are true | honor | reviewer executes | 0 | honor: needs independent execution |
| 36 | approval obtained before push (timing) | honor | none | 0 | honor: timing cannot be mechanical |
| 37 | `finding.schema.json` executed | none | validated with `jsonschema` only if a round 3 is scheduled | 0 | build nothing this session (D6); the two omitted COMMON.md requirements are added to the schema text in PR-P2 so a later round inherits them |

## Phase 1: Baseline and discovery

- [ ] 1.0 Full-depth clone. `git fetch --unshallow origin && git fetch --tags origin`; `BASE=$(git rev-parse origin/main)` written once to the tracking issue; `python3 tests/env_drift.py --install-merge-driver`. Success: `git rev-parse --is-shallow-repository` prints `false`; `git merge-base origin/main HEAD` exits 0; `git tag -l 'v6.3.*' | wc -l` >= 18; `git config --get merge.claimnotes.driver` non-empty.
- [ ] 1.1 GitHub Settings probe, run by the audit with `curl -H "Authorization: Bearer $GITHUB_TOKEN"` against `api.github.com`, one row per endpoint with its status: `rulesets?includes_parents=true`, `rules/branches/main`, `branches/main/protection`, `code-scanning/default-setup`, `code-scanning/alerts`, `actions/permissions`, `hooks`, `collaborators/tvofi/permission`. Already measured this session: the first two return `200 []` (no ruleset applies to main, repository or inherited); the rest return 403, four of them refused by the agent proxy rather than by permissions. Output: the table on the tracking issue plus a one-line consequence per 403. Success: eight rows, each `answered` or `403 <reason>`; the two answered rows replace the `protected: false` inference in Appendix A finding 9. The owner is asked only for what stays 403: the CodeQL default-setup languages and query suite, and the installed-app list.
- [ ] 1.2 Execute what the read-only audit could not, at `BASE`: `node .claude/workflows/brief_lint.mjs`; `node .claude/workflows/check-wave-script.mjs`; `python3 tests/structure.py`; `python3 tests/closure.py select --diff BASE~1`; `python3 tools/release/stamp.py --self-test`; `git log -10 --format=%B | bash tools/audit/preflight.sh`. Output: rc and last line per tool on the issue. Success: six rows; `FIXTURE ok` present twice (931dffe and shape-defects).
- [ ] 1.3 Re-baseline the in-flight delta. For the 9 addressed and 10 partly addressed findings (Appendix A), re-run the deciding command at `BASE`; record `closed | open | worse`. Success: 19 of 19 re-measured; 0 findings filed from the discovery tree.
- [ ] 1.4 Asset inventory. Denominator: the 88-file governance set plus files added since `6ea0083` (`orchestrator.md`, `preflight.sh`, `wave-ux-groups.json`, `fixtures/shape-defects.json`). Per file: `wc -l`, bytes/4, `closure.is_inert`, membership in `tests/closures.json`, loader class (auto, mechanical, must-open-by-rule, linked-only, orphan), in-degree via `git grep -l <basename> | wc -l`. Success: rows = denominator; 0 unclassified; the 21 never-opened files opened or excluded with a reason; `.abacus.donotdelete` gets the documenting line D7 prescribes.
- [ ] 1.5 Test-suite synergy. Reuse the 1,173-rule extraction from the journals; re-verify only rules in files changed since `6ea0083`. Row: `id, file, quoted anchor, binds, enforcement in {hard-ci:<job>, local-check:<script:function>, hook, driver, honor}, refuser line`. A hard-ci claim without a refusing line is downgraded. Success: >= 1,170 rows; 0 rows `hard-ci` with an empty refuser; the "now" column of section 3 carries a file and symbol each.
- [ ] 1.6 Staleness and bloat. Prototype `policy_lint.mjs` (no CI yet) over the policy set; re-run the nine count derivations; union bloat ranges per file (the journals summed; one file came out at 102 percent). Output: the known-bad seed keyed by file plus token, never by line. Success: dead-citation count is a number with a command; bloat is a union; seed entry count N stated.
- [x] 1.7 Loader probe — **answered from the vendor documentation instead, which is stronger than a one-shot probe.** `.claude/rules/*.md` are loaded: a rule with no `paths` key loads at session start, and a `paths:`-scoped rule loads when Claude reads a file matching one of its globs. `paths:` is the key and its value is an array of glob strings; there is no `applyTo:`. Nested directories under `.claude/rules/` ARE supported — discovery is recursive — so D8's flat-vs-nested question is a naming preference, not a constraint. `@path` imports in `CLAUDE.md` expand eagerly at launch with a four-hop depth limit, which confirms the plan's decision to discard them. `.cursor/rules/*.mdc` have no effect on Claude Code at all. The 200-line CLAUDE.md figure is documented guidance, not an enforced cap, and the only hard limit is a 4 MiB skip — so section 2.1's "no vendor ships a size refusal; written here" stands. Hook events are `SessionStart`, `PreToolUse` (matcher `Edit|Write|MultiEdit|NotebookEdit`, exit 2 blocks the call and the agent sees the reason) and `Stop`, configured under `hooks` in `.claude/settings.json`.
- [ ] 1.8 Context budget. Recompute the per-role read sets at `BASE` (every-session floor, fixer, reviewer, orchestrator, finder, root-cause, maximal). Success: baseline values for section 5 stated against `BASE`.
- [ ] 1.9 Rework baseline. Verdict counts from `pull_request_read get_comments` over every PR merged since v6.3.9; add:delete over the eight prose paths; incident markers over policy commits; the blocked verdicts classified once by hand into the section 4.3 class grammar. Success: eight numbers, each with its command.
- [ ] 1.10 Freeze map. `pull_request_read get_files` for every open PR. Success: 0 audit branches touch a path in an open PR under review.
- [ ] 1.11 Tracking issue `[governance] audit 2026-09` (label `policy`). Dedupe first against #541, #581, #575, #582, #527, #583, #574, #560. Success: issue number recorded; 0 duplicate issues.
- [ ] 1.12 Grant ADR. `docs/decisions/0001-session-policy-merge-grant.md`: the grant's text, its scope (policy merges by this audit, this session), its exclusions (stamps, GitHub account and Settings actions, non-audit PRs except landing or superseding to unblock a rewrite), the session id, and the reversion rule after the session. Merged as the audit's first PR so every later `## Approval` can cite it. Success: the file is on main; `git log --format=%s -1 -- docs/decisions/` names it; the plan of record gains a "Governance programme" section with this row.

Phase 1 done: shallow = false; 19 of 19 re-measured; 0 unclassified files; 0 unbacked hard-ci rows; eight metric numbers; three probe answers; Settings pasted or recorded as unread; ADR 0001 on main.

## Phase 2: Golden-standard gap analysis

- [ ] 2.1 Decision table over the fetched standards, one row each on the issue:

| standard | verdict | artefact here | reason |
|---|---|---|---|
| CLAUDE.md <= 200 lines; llms.txt index shape | adopt | `policy_lint --budgets` | no vendor ships a size refusal; written here |
| `.claude/rules/*.md` with `paths:` | adopt as canonical, after 1.7 | mechanical load; `rules_sync` | Claude Code loads it; `.mdc` is loaded by nothing in the container |
| `@imports` in CLAUDE.md | discard; fallback only if 1.7 fails | none | re-inflates the always-loaded set |
| SessionStart, PreToolUse, Stop hooks | adopt three | `.claude/settings.json` | the only deterministic seat-side layer |
| Cursor `.mdc` globs | adapt: generated only | `rules_sync --check` | six behaviour-changing drift clusters were prose copies |
| Copilot 2-page cap; AGENTS.md nesting | discard | none | no Copilot; one package, one root |
| MADR superseded-not-deleted | adapt: lite frontmatter | `policy_lint` checks `superseded-by` targets | history leaves rule files, keeps rationale |
| CODEOWNERS plus required code-owner review | adopt the file now; the review requirement is attempted with the ruleset | ruleset | an author cannot approve their own PR under one identity, so the requirement is recorded even where it cannot bind |
| GitHub merge queue | discard; ADR records it | none | `tests.yml` keys scoping on `pull_request`; DIRTY claim-file PRs never get a merge commit; one collision in five days (#606) |
| Conventional Commits, release-please | discard; adopt the `policy:` prefix only | `pr-contract` | `stamp.py` rules 1 to 5 are this shape already |
| Betterer-style ratchet | present for code; one-sided cap for prose | `policy_budgets.json` | the measured defect is accretion; deletion must cost nothing |
| markdownlint, Vale, lychee, conftest, danger, pre-commit | discard as tools; danger's shape adopted | `policy_lint --pr-body` | the substrate exists; git hooks are not cloned |
| OpenSSF: branch protection, pinned actions (#412), read-only token | adopt protection; others tracked | ruleset | `tests.yml` already sets `contents: read` |

- [ ] 2.2 Check catalogue. `node .claude/workflows/policy_lint.mjs --list` prints every check with its fixture path and one-run time. Success: N checks, N fixtures, N timings; standing cost <= 3 s per PR event.
- [ ] 2.3 ADR drafts 0002 to 0007 as text on the issue, and merged with the PR they justify: baseline, loader model, format contract, deletions, merge queue refused, identity decision (0001 is the grant, merged in 1.12). Success: each has Context, Decision, Consequences, Evidence command.
- [ ] 2.4 Harness defects handed to ordinary fixer seats, not to governance: the self-satisfying autofix re-check in `closure.py apply_under_scoped_recordings`; `env_drift.three_dot_files` ignoring git's exit status; `run.sh` unguarded on an unresolvable `GOLDEN_REF`; `release.yml` gating nothing on the dispatch path; the `SLOW_GATED` assertion `closure.py` claims and `entities.py` lacks; `stamp.py PR_RE` over-collecting `scope(#N):` subjects. Success: six fix PRs or issues, none in the audit's write set.

Phase 2 done: 13 standard decisions plus the eleven D-decisions in section 7, 0 undecided; every adopted rule names an artefact or `honor <reason>`; 6 ADR drafts; catalogue printed.

## Phase 3: Agent-optimised refactoring

Each PR: one surface, cut from current main, `policy_lint` green, its rot fixture red, budgets stated in the body, reviewed once by an adversarial fix-review seat from a detached worktree at the head SHA, then merged by the audit under the grant and section 0's preconditions. Policy PRs carry the `policy:` title prefix and an `## Approval` section citing ADR 0001.

- [x] **PR-P0 is discharged with no action taken.** All four target pull requests merged on 2026-09-07 before the audit reached this step — #603 (`fix-review.md`), #592 (`fixer.md`), #605 (`orchestrator.md`) and #602 (`structure.py` counts) — along with #596, #591 and #569. Two pull requests remain open: #607, a record pull request holding `docs/HANDOVER.md`, `docs/plan-2026-09-open-issues.md` and `wave-4-groups.json`, so PR-D1 and PR-P1 wait on it; and #608, the audit's own PR-T1. No audit branch touches a path in a pull request under review. Recorded on #609. Superseded text: unblock the contract files. For each of #603 (`fix-review.md`), #592 (`fixer.md`), #605 (`orchestrator.md`) and #602 (`structure.py` counts): read the PR's review comments and checks; if a `merge` verdict stands and every check is green, merge it (squash, one at a time, main gate green between); otherwise fold its diff intent into the audit's rewrite of the same file, close it with a comment naming the superseding PR, and list the fold in that PR's body. #596 (DIRTY) and #591, #569, #567 are outside the audit's write set and are left to their owners. Success: 0 open PRs edit a file an audit rewrite touches; each disposition posted on #201.
- [ ] PR-T1 tooling. `policy_lint.mjs` (resolvers shared with `brief_lint.mjs`'s `lintBrief` and `assertAcceptanceFixture`), `rules_sync.mjs`, `fragments_sync.mjs`, `policy_budgets.json` recorded at today's values, `fixtures/policy-rot/`, `governance.yml` with jobs `policy-docs` and `pr-contract`. Known-bad citations from 1.6 pinned as a shrinking allowlist. Success: job green on the PR; `FIXTURE ok: N error(s)` with N >= 8; allowlist may only shrink; null control passes at `BASE` with an empty body.
- [ ] PR-T2 orchestration. `STAGES = {pending, fix, review, blocked, merge, done}` defined once; `web-fix-wave.js` branches on `blocked` (repair with `resume.comment`) and `pending` (fresh fixer); the Reconcile mismatch list gains both; VERDICT schema `pattern: ^(merge|blocked)$` plus `class`; `rootCausePrompt` dispatch; `fragments_sync` markers in the five `web-*.js`; `check-wave-script.mjs` gains cases and runs in job `wave-script`. Success: harness reports >= 12 passed; a roster with `in-review` refused; `fragments_sync --check` 0.
- [ ] PR-T3 hooks and prepr (policy; merged under the grant). `.claude/settings.json` with three hooks; `.claude/hooks/*.sh` each with `--self-test`; `tools/audit/prepr.sh`. Success: `policy_lint --hooks` 3 of 3; `prepr.sh` exits 2 on ten fixtures and 0 on the last five merged squash bodies; `pre-edit.sh` refuses a `.cursor/rules/` edit in a probe session.
- [ ] PR-T4 GitHub-side files (after #591, or beside it as section 1 states). `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, both added to `INERT` in `tests/closure.py`. Runs MODE: FULL once. Success: `tests/entities.py` reports 0 orphans; the template H2 set equals the parser's required set.
- [ ] PR-P1 root and rules (policy; merged under the grant). `.claude/rules/*.md` from the five `.mdc` bodies and CLAUDE.md's four-rules, root-cause, gate-lock, autofix and claim-file sections; CLAUDE.md rewritten as the index; the 26 HISTORY and 31 META lines moved to `docs/decisions/`; `.cursor/rules` regenerated. The fourteen cross-cut contradiction pairs resolved to one copy each. Success: CLAUDE.md <= 200 lines; always-loaded <= 6,000 tokens; 0 `#NNN` outside link lines; every block has IF, THEN, REFUSED BY and EXAMPLE; `rules_sync --check` 0; the `--single` scope and the `skip-failed-recording` remedy exist once each.
- [ ] PR-P2 briefs (policy; merged under the grant). Seven dead citations repaired (`evaluate`, `HeatpumpOptimizerSensorBase`, `last_buffer_trajectory`, `ALLOW_EXTRA`, `STATES (26)`, manifest tags, the two D9 facts); D7 items 1 and 2 replaced by "read `tests/structure_budgets.json`"; `worktree:` key in 11 of 11; `COMMON.md` no longer lists dimensions; `judge.md`'s per-fix-PR seat amended to round >= 3 or a disputed verdict (section 7, D5) and gains the load1 revocation. Success: 0 dead symbol citations in 11 briefs; `worktree:` 11 of 11.
- [ ] PR-P3 `fixer.md` (policy; merged under the grant; after PR-P0 disposes #592). Block format, ids, `reads:`; the never-rebase prohibition and `ps` exclusivity carried; the step-5 MODE: FULL contradiction resolved; the preflight step from section 4.1. Success: <= 120 lines; fixer read set <= 14,000 tokens.
- [ ] PR-P4 `fix-review.md` (policy; merged under the grant; after PR-P0 disposes #603). Verdict grammar; a step for `blocked: preflight-mismatch`; `gh pr checks` replaced by the MCP mapping. Success: <= 120 lines; every `returns:` entry names a consumer that contains the literal.
- [ ] PR-P5 `orchestrator.md` (policy; merged under the grant; after PR-P0 disposes #605). 338 lines to <= 120; incident stories to ADRs; `gh` replaced by the mapping extended with `gh pr checks`, `gh pr list`, `gh pr view --json closingIssuesReferences`. Success: 0 `gh` hits; `dispatched-by: manual: owner session`.
- [ ] PR-D1 READMEs and register (after PR-P0 disposes #602). `tests/README.md` to <= 150 lines (its per-script section duplicates the docstrings by its own admission); `tools/audit/README.md` to <= 100 with the INERT sentence corrected and the history sections moved to ADRs; `docs/audit-2026-09.md` Round 1 and the two-session protocol removed; `docs/HANDOVER.md` Decisions become links. Success: line counts met; `policy_lint` bans hold on the READMEs.
- [ ] PR-D2 archive and delete (decided in section 7, D4). Tag `archive-rosters-2026-09` and `audit-evidence-2026-09`, then delete: `docs/plan-open-issues.md`, `docs/audit-2026-08.md`, `docs/plan-v4.0.0-program.md`, `docs/backlog.md`, `docs/superpowers/plans/*`, done rosters (`wave-1b`, `wave-2`, `wave-3`; `wave-3l` once 3L-G6 is confirmed closed), `web-phase0.js`, `triage-quiet-judges.json`; `RETIRED:` prefix on `audit-fix.js`, `audit-wave.js`, `audit-merge.js`; `tools/audit/round1-3/` tagged then deleted with the three judge instruments moved to `tools/audit/harnesses/`; `w5-g5-195-coverage/` kept until Wave 5 closes. Success: `git ls-files | wc -l` down by >= 230; tracked bytes down by >= 5 MiB; every deleted path has in-degree 0 or a repointed citer listed in the body; `brief_lint` and `policy_lint` green.

Format contract for every future policy document (parsed by `policy_lint`):

```
---
description: one line, <=120 chars; rendered into the CLAUDE.md index
paths: ["tests/**"]                 # omitted = always loaded
binds: [fixer, fix-review, orchestrator]   # closed vocabulary
enforced-by: [job:governance.yml/pr-contract, hook:PreToolUse/pre-edit, tests/closure.py:select]
last-verified: <sha>                # must be an ancestor of HEAD
supersedes: []                      # rule ids or paths this retires
---
# <One question this file answers>

### gate.3 Scoped run keys on the mode line
IF the scoped gate prints a mode line THEN act on MODE, never on the script count.
REFUSED BY: honor (no script reads a reader; a parser costs more than the class)
BORN: incident #354   DETECTOR-DEMO: none (cost test in decisions/0007)   SUNSET: when run.sh prints one line for both modes
EXAMPLE BAD: "0 scripts ran, so nothing to do"   GOOD: "MODE: FULL, so run.sh unscoped before push"
```

`policy_lint` refuses: a block over 12 lines; a missing key; a `REFUSED BY` that does not resolve (a job in a workflow file, a script in `git ls-files`, a `path:function` via grep) unless it reads `honor (<reason>)`; `BORN: incident` without `DETECTOR-DEMO` or a decisions pointer; a numeral >= 2 outside EXAMPLE, REFUSED BY and BORN; a duplicate id; a 12-word shingle shared with another policy file; `#NNN`, ISO dates, "once", "used to", "incident" in the body outside BORN. Role contracts add `role:`, `dispatched-by:`, `reads:`, `returns:`; the body is `### O<n>` blocks of the same shape. Rationale and history go to `docs/decisions/`.

Phase 3 done: CLAUDE.md <= 200 lines; always-loaded <= 6,000 tokens; 7 of 7 contracts dispatch-resolved; 0 dead citations in policy files; shingle duplicates 0; honor share in the always-loaded set <= 50 percent with 100 percent reasons; `.cursor/rules` byte-equal to generated; >= 9,000 lines and >= 5 MiB removed; every policy PR merged with a `merge` verdict, green checks and an `## Approval` citing ADR 0001; main green on the full gate after the last merge; every merge has its plan row and #201 comment.

## Phase 4: Continuous-improvement loop

- [ ] 4.1 Pre-PR self-policing, `tools/audit/prepr.sh`. Run by the fixer before `create_pull_request`, by the Stop hook when the diff touches policy or workflow paths, and by the orchestrator over the squash body at merge. Steps, each refusing on non-zero: merge-base resolves; `python3 tests/closure.py select --diff <base>` prints the mode line; `policy_lint`; `rules_sync --check`; `fragments_sync --check`; `check-wave-script` after a `web-fix-wave.js` edit; `python3 tests/structure.py`; three-dot diff on VERSION, manifest and the notes heading is empty; claim files byte-identical to `origin/main` unless the body claims drift; `preflight.sh` over the body; `policy_lint --pr-body body.md --head $(git rev-parse HEAD)`. Prints `PRE-PR: <head> <digest of step rcs>`; the body carries that line; `pr-contract` re-executes the pure steps, so the line is a claim and the re-execution is the proof. Success: exits 2 on each of ten fixtures under `fixtures/policy-rot/prepr/`; exits 0 on the last five merged squash bodies.
- [ ] 4.2 `pr-contract` in CI on every body event. Required H2 set from the template: `## Head`, `## Mutation proof`, `## Null control`, `## Red checks`, `## Forward-carry`, `## Friction`, plus `## Approval` and `## Trigger` when the title starts `policy:`. Each section is content or `n/a: <reason>`. Success: required in the ruleset; a body without `## Head` blocks merge; a body edited without a push is caught by the `edited` trigger.
- [ ] 4.3 Verdict grammar and its consumer. First line of a review comment is exactly `Fix review: merge <sha>` or `Fix review: blocked <sha> <class>: <why>`, class in {mutation-vacuous, harness, null-control, claims, version, head-moved, carry-missing, root-cause-unanswered, preflight-mismatch, conflict, other}. `web-fix-wave.js` throws on a verdict that does not parse; the `blocked` path returns a roster patch `{stage:'blocked', pr, head_sha, class, comment}` applied in the record PR. Success: a `check-wave-script.mjs` case for an unparseable verdict fails red; the `audit-wave.js` success-list routing is retired.
- [ ] 4.4 Friction as a body section. `## Friction` is `none` or lines `<rule_id>: <event in {unclear, contradiction, unenforced, stale, cost}>: <evidence>`; `pr-contract` validates that each `rule_id` resolves to a block. Success: 100 percent of merged PRs carry the section; unknown ids refused.
- [ ] 4.5 Policy-evolution trigger (mechanical trigger, human decision). `policy_lint --stats --since <tag>` runs weekly in job `record` and at every stamp: a histogram of blocked classes and friction rule ids over merged PRs via REST. A class or rule id at >= 3 in seven days opens or updates issue `[policy] recurring friction: <key>` (label `policy-proposal`). The orchestrator answers with one `policy:` PR in the format above, `provenance:` naming the issue, `## Trigger` quoting the histogram line. Within this session the audit decides and merges such a PR under the grant; after the session the owner approves or declines. A decline is recorded as `REFUSED BY: honor (<reason>)` so the same friction never re-opens the same proposal. Success: over two waves, >= 1 proposal PR or a recorded "no friction"; `pr-contract` refuses a `policy:` PR without `## Trigger`.
- [ ] 4.6 Incident-to-rule pipeline. A qualifying defect (`defect-root-cause.mdc` trigger, or a third occurrence of a class) dispatches the root-cause seat; its product lands as a `policy:` PR whose block carries `BORN: incident #N`, `DETECTOR-DEMO` (the run or commit where the detector failed on the defect), and `SUNSET`. Success: `policy_lint` refuses the block without them; 100 percent of incident-born rules after PR-T1 carry `DETECTOR-DEMO` or a cost-test pointer.
- [ ] 4.7 Sunset. `policy_lint --sunset --since <tag>` lists: prose rules whose `REFUSED BY` names a detector (cut the prose, keep the detector); honor rules with zero friction and zero incident references over two stamps; rules past `SUNSET`. Run by the stamp seat at every second stamp. Never sunsets a detector on zero fires. Success: a `policy: sunset <date>` PR or a `decisions/` entry "none" every second stamp; `policy_lint` fails a rule past `SUNSET` with no decision entry.
- [ ] 4.8 Record derivation. `policy_lint --record --since <tag>` lists merged PRs from `git log --format=%s <tag>..origin/main` with `PR_RE` tightened to `\(#N\)$` and refuses when any number is absent from both `docs/plan-2026-09-open-issues.md` and `docs/HANDOVER.md`; open issues absent from the plan are refused via REST on the weekly run. Success: refuses on a synthetic missing PR; passes at `BASE` after the plan is truthed; check-name drift (row 30) reported in the same run.
- [ ] 4.9 GitHub side, attempted by the audit. `POST /repos/tvofi/heatpump_optimizer/rulesets` with ruleset `main-protect`, target `branch`, include `~DEFAULT_BRANCH`, enforcement `active`: `deletion`, `non_fast_forward`, and `required_status_checks` naming `fast (3.13)`, `fast (3.14)`, `browser`, `briefs`, `closure-scope`, `closures`, `hassfest`, `validate-hacs`, `policy-docs`, `pr-contract`; `typing` added once #596 lands; `strict_required_status_checks_policy` false, because "require branches up to date" collides with the freeze rule. `CodeQL` and the three `Analyze (…)` checks are added only after their default-setup configuration is readable, since a required check that no file defines cannot be reasoned about. Bypass: `repository_role` maintain, so the stamp's direct push to main still lands; `stamp.py` rules 1 and 3 are unchanged. A required-approval or code-owner rule is not requested while one identity authors and approves, which would make it honor with extra steps. Success: the POST returns 201 and `GET .../rules/branches/main` returns a non-empty list naming the checks. If the POST returns 403, record the status and the response body, and post the exact JSON payload on the tracking issue as a paste-ready block for the owner, with the CodeQL and code-owner decisions stated. Either outcome is a result; silence is not.
- [ ] 4.10 Re-measurement. At +2 and +4 stamps after 4.1 lands: `policy_lint --stats`, `--budgets`, `--report`, `--sunset`. Posted as one #201 comment and one `decisions/` entry. Success: the section 5 targets hold, or the rule set reopens when a target is missed twice.
- [ ] 4.11 What stays honor, written into blocks with the reason: approval obtained before push (timing); verify-before-claim beyond the parser's regexes; mutation-proof truth (needs independent execution); the harness loading `.claude/rules/` (observed, not refused); Cursor and other non-Claude seats for hooks (no hook surface); a seat killed mid-mutation.

Phase 4 done in-session: `prepr.sh` red on 10 fixtures; 3 hooks self-testing; 4.1 to 4.8 merged; `record` green on the first push to main after PR-L1; the ruleset either live with `policy-docs` and `pr-contract` required, or its refusal status and paste-ready payload on the issue. Phase 4 done after the session: `record` green two consecutive runs; the first sunset produced a PR or a recorded none; at +4 stamps the section 5 targets hold.

## 5. Metrics

| metric | baseline (`6ea0083` unless noted) | target | measurement command |
|---|---|---|---|
| CLAUDE.md lines | 399 (about 464 on main) | <= 200 | `wc -l CLAUDE.md` |
| always-loaded lines | 796 | <= 320 | `policy_lint --budgets` |
| always-loaded tokens (bytes/4) | 11,349 | <= 6,000 | same |
| fixer read set tokens | 26,787 | <= 14,000 | `policy_lint --budgets --role fixer` |
| orchestrator read set tokens (policy plus contract) | 36,597 | <= 16,000 | same, `--role orchestrator` |
| maximal compliant read set | 38,774 | <= 20,000 | same, `--role all` |
| non-resolving citations in policy files | 105 (10 dead, 27 counts, 5 moved among 69 re-checked) | 0 | `policy_lint` |
| obligations with 2+ copies | 263 (8 disagree) | 0 shared shingles | `policy_lint --duplicates` |
| honor share, always-loaded set | 85 to 97 percent | <= 50 percent | `policy_lint --report` |
| honor rules without a reason | unmeasured (most) | 0 | same |
| `resume.stage` values unrecognised | 17 of 56 groups | 0 | `check-wave-script.mjs` |
| `gh` in seat-facing text | 3 hits here, more on main | 0 outside the mapping table | `policy_lint --no-gh` |
| blocked-verdict share | 47 of 86 (55 percent) | <= 30 percent over the next 30 merged PRs | `policy_lint --stats --since <tag>` |
| review rounds per PR | mean 1.79, max 11 | mean <= 1.4, max <= 4 | same |
| first-pass merge rate | 25 of 48 (52 percent) | >= 70 percent | same |
| governance add:delete | 6.8 | <= 1.5 during Phase 3; <= 2.0 standing | `git log --numstat <a>..<b> -- <8 prose paths>` |
| incident-born policy share | 13 of 15 | <= 50 percent; 100 percent carry DETECTOR-DEMO | `git log --format=%B -- <policy paths>` |
| tracked governance bytes | 1.94 MB corpus plus 6.6 MB evidence | >= 5 MiB removed | `git ls-files -z \| xargs -0 wc -c` |
| hooks with a passing self-test | 0 | 3 | `policy_lint --hooks` |
| merged PRs without a record row | 10 of 10 recent | 0 | `policy_lint --record --since <tag>` |
| policy PRs merged without an owner-approval trailer | unmeasured | 0 | `policy_lint --merge-trail` on push to main |

## 6. What this plan deliberately does not do

- Does not merge outside the grant: no release stamp, no budget raise, no PR authored outside the audit except landing or superseding #603, #592, #605 and #602 to unblock a rewrite of the same file, and nothing after this session ends.
- Does not create a machine account, install or configure an App, change code-scanning setup, or touch org settings: every org-level and settings path returns 403 through the agent proxy, so those stay with the owner as measured facts rather than open questions.
- Does not require a check the repository cannot yet produce, and does not require `CodeQL` until its configuration is readable.
- Does not touch claim files, `tests/structure_budgets.json`, `VERSION`, or `tests.yml` while #596 is open.
- Does not skip the adversarial fix-review on any policy PR because the merge authority is its own; the review seat and the merge seat stay separate.
- Does not add a `tests/governance.py` gate lane or edit the `INERT` prefixes; the policy corpus stays INERT and is linted by a never-scoped job, following the `briefs` job precedent.
- Does not adopt a merge queue, a third autofix job, or a cross-job autofix loop guard.
- Does not build a two-sided ratchet on prose; caps are one-sided so deletion is free.
- Does not build a nightly citation sweep; every PR already lints.
- Does not port `audit-find.js` or `audit-verify.js` unless a round 3 is scheduled.
- Does not rename `tools/audit/briefs/` into subdirectories.
- Does not grep session transcripts in a Stop hook.
- Does not weaken `brief_lint.mjs`, the ratchet, or any existing refusal.
- Does not truth the Delivery-status rows itself beyond what `--record` refuses; that stays with the programme's record PRs.
- Does not measure time-to-ready as a standing metric; one cold-start timing at Phase 1 and Phase 4 close only.

## 7. Decisions taken under the grant, and what stays with the owner

Decided by the audit in this session (each recorded in its ADR or PR body, reversible by a later `policy:` PR):

- D3 Open policy PRs: PR-P0 lands #603, #592 and #605 when each carries a `merge` verdict and green checks, otherwise supersedes them; #602 the same; #596 (DIRTY), #591, #569 and #567 are left to their owners.
- D4 Deletions after the two archive tags exist: the four 100-percent-history docs, `docs/backlog.md`, `docs/plan-v4.0.0-program.md`, `docs/superpowers/plans`, done rosters, `web-phase0.js`, `triage-quiet-judges.json`, round-1/2/3 evidence; `audit-fix/wave/merge.js` retired by marker. Anything a live citer still points at is repointed first, never deleted under it.
- D5 `judge.md` amended to round >= 3 or a disputed verdict; the root-cause seat is dispatched automatically whenever a PR names a red check.
- D6 No finder round 3 in this session; `audit-find.js` and `audit-verify.js` are archived with the `RETIRED:` marker, not deleted, so a round 3 can restore them.
- D7 `.abacus.donotdelete`: kept, with one documenting comment beside its INERT entry stating that its producer is unknown and asking the owner to name it.
- D8 `.cursor/rules` kept as generated output with a byte-compare; deleted only if the owner later says Cursor seats are gone. Confirmed by 1.7: Claude Code ignores `.mdc` entirely, so the directory is Cursor-only and generation is the only thing that keeps it true. Nested rule directories are supported, so flat naming is a choice about discoverability rather than a limit.
- D9 First caps: CLAUDE.md 200 lines, always-loaded 6,000 tokens, fixer read set 14,000, orchestrator 16,000 with rosters and the plan counted as task data; tightened at +4 stamps.
- D10 `SEAT-BLOCK.md` treated as dead: `finding-propagation`'s two-destination clause collapses to the in-tree destination; the out-of-tree copy, if any session still uses one, is a convenience copy and never a carry target.
- D11 `.claude/settings.json` and `.claude/hooks` count as policy.

- D12 Ruleset: the audit attempts `main-protect` itself per 4.9 and records the status. Required approvals and code-owner review are not requested while one identity authors and approves.

Still with the owner, because the agent proxy refuses these paths with 403 and no MCP tool exposes them. Each is a measured blocker on the tracking issue, not an open question the plan waits on:

- O1 Identity. A GitHub identity for cloud seats distinct from the owner (machine account or App) is what would let CODEOWNERS review and required approvals bind. The audit cannot create one: every org and installation path is proxy-blocked. Until it exists, row 16's paper trail is the enforcement, and the audit says so in the ADR rather than pretending otherwise.
- O2 Code-scanning default setup and installed apps. `code-scanning/default-setup`, `code-scanning/alerts`, `hooks` and `actions/permissions` all return 403 here. The owner pastes the enabled languages, the query suite, and the app list; only then do the four fileless CodeQL checks join the required set.
- O3 After this session: whether policy merges revert to owner approval per PR or stand on the ruleset plus `pr-contract`. The audit's closing #201 comment asks this and lists every policy PR merged under the grant, with its review verdict and head SHA.

## 8. Verification

- After P1.0: `git rev-parse --is-shallow-repository` prints `false` and the six 1.2 commands print their rc on the tracking issue.
- After every merge: `mcp__github__pull_request_read get` shows `merged: true`; the Tests run on the new main head concludes `success` before the next merge (`actions_list` on `tests.yml`, branch main); the PR body's `## Approval` cites ADR 0001; the plan of record's "Governance programme" row and the #201 comment exist; `git diff <prev-main>...<new-main> -- VERSION custom_components/heatpump_optimizer/manifest.json` is empty.
- After PR-T1: on the PR, job `policy-docs` is green; deleting any single check function from `policy_lint.mjs` turns `FIXTURE ok` red (the rot pin); running `policy_lint` at `BASE` with an empty PR body exits 0 (null control).
- After PR-T2: `node .claude/workflows/check-wave-script.mjs` prints >= 12 passed; a roster fixture with `stage: in-review` is refused; the verdict `Fix review: nonsense` throws.
- After PR-T3: `.claude/hooks/pre-edit.sh --self-test` refuses its fixture edit to `VERSION`; `tools/audit/prepr.sh` exits 2 on each of the ten rot fixtures and 0 on the last five merged squash bodies; a fresh seat prints the merge-driver readback at session start.
- After PR-P1: `wc -l CLAUDE.md` <= 200; `policy_lint --budgets` passes; `rules_sync --check` 0; `grep -c '#[0-9]' CLAUDE.md` counts only link lines; a probe seat that edits a `tests/` file reports the `gate-scoping` rule text in context.
- After PR-P2 to P5: `policy_lint` reports 0 dead citations across `tools/audit/briefs/`; each contract's `dispatched-by:` greps in a workflow script or reads `manual:`.
- After PR-D2: `git ls-files | wc -l` down by >= 230 against `BASE`; `brief_lint.mjs` and `policy_lint.mjs` green; no citer points at a deleted path.
- At +2 and +4 stamps: `policy_lint --stats --since <tag>` prints the blocked-verdict share and review rounds; compare with section 5.
- Throughout: the scoped gate runs as today (`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`), and `python3 tests/entities.py` reports 0 orphans after every file addition.

---

## Appendix A: measured baseline from this session

Twelve read-only readers, each over one surface, extracted every imperative as a rule and classified its enforcement; 366 load-bearing classifications were then adversarially re-verified (240 amended, mostly "hard-ci" downgraded to "local-check" or "honor"). Full data: the workflow journals under the session directory (`wf_14f431bb-de1`, `wf_8dbfb5b9-c7d`, `wf_a3ec62c2-bb8`, `wf_8298cdd4-51d`, `wf_d5256c38-38d`) and the digests in the scratchpad (`laneA_digest.txt`, `laneB_digest.txt`, `laneC_digest.txt`, `crosscut_digest.txt`, `designs_digest.txt`, `judge_synthesis.md`).

Facts established directly, before any lane returned:

- `CLAUDE.md` is the only auto-loaded file; the five `.mdc` rules are reached only by an agent choosing to open the directory; `.cursor/` is on the INERT list in `tests/closure.py`.
- `tools/audit/briefs/orchestrator.md` was cited by `CLAUDE.md`'s role-contract table and never existed in this tree's history; PR #593 landed it on main today, after this branch's base.
- The `claimnotes` merge driver is not installed in this clone; nothing checks it at session start.
- This box has 4 CPUs; `node`, `strace` and `python3` are present; `gh` is absent, while `delivery-status-tracking.mdc`, `fix-review.md`, `orchestrator.md` and every `audit-*.js` seat prompt instruct the seat to run `gh`.
- `docs/HANDOVER.md` `updated-for: af47c96` is reachable from HEAD.
- `tests/structure_budgets.json` holds 24 metrics.
- The audit skills this session lists resolve from `.claude/workflows/*.js` `meta` blocks; there is no SKILL.md and no test for them.

| surface | lines | rules | honor | hard-ci | local-check | other | non-current |
|---|---|---|---|---|---|---|---|
| `CLAUDE.md` | 399 | 120 | 88 | 22 | 6 | 4 | 15 |
| `.cursor/rules/*.mdc` (5) | 397 | 124 | 80 | 32 | 0 | 12 | 18 |
| role contracts (6 files) | 563 | 178 | 130 | 11 | 31 | 6 | 20 |
| dimension briefs D0 to D10 | 550 | 156 | 152 | 3 | 1 | 0 | 21 |
| suite governance | ~6,900 | 142 | 31 | 89 | 17 | 5 | 18 |
| CI workflows (4 yml) | 998 | 74 | 7 | 58 | 5 | 4 | 19 |
| orchestration (22 files) | ~3,500 | 128 | 60 | 19 | 39 | 10 | 34 |
| docs governance | ~9,500 | 122 | 87 | 21 | 9 | 5 | 41 |
| release and evidence | 766 plus 6.6 MB evidence | 129 | 81 | 19 | 26 | 3 | 35 |

Headline ratios: about 1,170 rules; roughly 60 percent honor-system across the corpus, and 85 to 97 percent honor in the three files every seat is told to open first. The suite and CI are the mirror image: the mechanism exists, it is aimed at code and not at policy.

**Blocking findings, all verified with a control:**

1. `orchestrator.md` cited and absent (now landed on main, instructing `gh`).
2. The `blocked:` verdict vocabulary is consumed by no script; `audit-wave.js` returns a blocked PR in the success list; `fix-review.md` returns a bare verdict while `audit-merge.js` requires a PR comment beginning "Fix review: merge".
3. The root-cause seat is dispatched by nothing; `fixer.md` and `fix-review.md` both delegate the analysis to it. `judge.md` puts a judge on every fix PR; no fix pipeline seats one.
4. `web-fix-wave.js` recognises four `resume.stage` values; 17 of 56 roster groups use `pending`, `in-review` or `blocked`.
5. Both CI autofix jobs have never completed a repair in the visible history; #527 (open, sev:high) records why.
6. `closures-autofix`'s post-repair check is self-satisfying (`closure.py apply_under_scoped_recordings`), the exact shape `derive_closures.sh` and `tests.yml` name as a hazard.
7. The Delivery-status table was behind main by seven Wave-4 stages, two Wave-5 tranches and two releases; 23 of 30 open issues and 10 of 10 recent merges had no disposition (largely repaired by #531, then regenerating).
8. PR #596 had a red `typing` check while #201 said every open PR was green (since fixed at its head).
9. `main` has no protection at all. Confirmed authoritatively this session: `GET /repos/tvofi/heatpump_optimizer/rules/branches/main` and `GET .../rulesets?includes_parents=true` both return `200 []`, so no repository or inherited ruleset applies, which closes the "the legacy flag may not reflect a modern ruleset" caveat the discovery pass had to leave open. No CODEOWNERS, no PR template, no "Claude Approvals" check; four CodeQL checks are defined by no file and their configuration is unreadable from here (403).
10. Seven of eleven dimension briefs carry a citation that does not resolve; `brief_lint.mjs` is aimed only at `wave-*-groups.json`, and only at non-`done` groups.
11. `tools/audit/README.md` says `tools/` is INERT and no test reads it; INERT is `tools/audit/` and `tests/entities.py` imports and self-tests `stamp.py`. The same README contradicts itself on the judge's load1 bar; `judge.md` carries only the unattainable version.
12. `finding.schema.json` omits two of COMMON.md's eight requirements, and nothing executes the schema.
13. `docs/architecture.md`'s structural counts are all wrong and the register records them as a verified non-finding; `docs/HANDOVER.md` breaks its own "name the metric, never its number" rule once.
14. The git history reachable here is a shallow clone with two graft roots and a stale `origin/main`.

**Git forensics (98 real commits, 5 days):** governance prose is pure accretion (CLAUDE.md 134 to 399 lines in 11 commits, 0 decreases; `fixer.md` 31 to 211 in 9 commits); governance adds 6.8 lines per line deleted versus 1.42 for production; 13 of 15 prose-policy commits incident-born; `finding-propagation.mdc` 64 percent rewritten one day after landing; the forbidden `mkdir` lock rediscovered and fixed by three PRs across two days; 14 of 22 brief and rule files have zero real commits; of 15 budget commits, 3 raised a budget and only 1 recorded owner confirmation; governance rework 27 percent versus production 6 percent; #201's own measure: 47 of 86 verdicts blocked, 52 percent first-pass merge rate, 1.79 review rounds per PR, one PR at 11 rounds.

**Cross-cut:** 1,173 rules cluster into 868 obligations; 263 have copies in two or more files; 8 clusters disagree, 6 change what a seat must do; thirteen terms have two definitions; in eleven of fourteen prose-versus-mechanism conflicts the mechanism is the permissive side. 69 references re-checked: 10 dead, 5 moved to a tag, 27 count mismatches, every one in the direction "the artefact grew, the prose did not". `CLAUDE.md`, all six role contracts and four of five `.mdc` files contain zero `file:line` citations; the one GOOD example in `brief-citations.mdc` drifted 1,577 lines. 21 governance-shaped files were never opened by any surface; `RELEASE_NOTES.md` was sampled at 0.9 percent; no surface executed a test script. Read sets: every session about 11,300 tokens; a literally compliant seat about 38,800; `tests/README.md` alone outweighs CLAUDE.md plus all five rules. The container's hooks enforce no repository rule.

**Delta re-measured at the Phase 1 boundary (2026-09-07T20:45Z).** Seven pull requests merged on 2026-09-07 with no independent verdict at their final head — #591, #592, #596, #602, #603, #605 and #569 — plus #606 with no review at all, the stated cause being an account rate limit that exhausted the session's review capacity. `docs/HANDOVER.md` in #607 records it and names two that matter most: #603 is policy whose owner-approved form changed twice after approval, and #596 introduces a typing census of 518 that four Wave 5 tranches will be ratcheted against, unchecked by any reviewer. This sharpens rather than weakens the Phase 4 case: the repository has no required check and no code-owner rule, so nothing at the merge boundary noticed, which is exactly what `pr-contract` and the section 4.9 ruleset exist to make impossible.

**In-flight delta at first read (GitHub main past `5a62b96`):** of 77 blocking and major findings, 9 addressed, 10 partly, 58 untouched, 6 worse. #593 landed `orchestrator.md` (+338, instructs `gh`) and `preflight.sh`; #595 and #598 grew CLAUDE.md by 65 lines; #601 repaired `brief_lint.mjs`, which had been linting 0 of 6 rosters; #531 truthed the plan and roster rows; #606 merged without independent review; v6.3.18 stamped and the plan does not know. Seven PRs open at last read; #596 DIRTY; line-number anchors in the contracts and `structure.py` are about to move.

**Enforcement that exists and works (the substrate to build on):** the closure-scoped gate and `MODE:` line; the orphan-file classification; the structural ratchet including "improved and not yet recorded"; the claim-file rules and three-dot replay; the single-handover count and reachable `updated-for:`; the `.gitattributes` routing check; the majority-refute kill in `audit-verify.js`; `brief_lint.mjs`'s four citation classes with its rot-pin fixture; `stamp.py`'s eleven refusals with a hard-ci self-test; `check-wave-script.mjs`; `tools/audit/preflight.sh` on main.

**Public standards mapped onto the gaps:** Anthropic's CLAUDE.md guidance (under 200 lines; `.claude/rules/*.md` with `paths:`; `@imports`; SessionStart, PreToolUse and Stop hooks as the deterministic layer; a Stop hook that proposes updates); Copilot's 2-page cap and `applyTo`; AGENTS.md nesting; llms.txt's index shape; MADR's superseded-not-deleted; danger.js, conftest, lychee, markdownlint as refusal-with-exit-code substrates; CODEOWNERS plus required code-owner review; GitHub merge queue (recorded, not adopted); Conventional Commits and release-please. No public standard mechanically caps instruction-file size; that check is written here.

---

## Appendix B: the built queue, its merge order, and how each conflict resolves

Measured with `git merge-tree --write-tree` at 22:20Z, before any of it was
pushed, so the sequence is known rather than discovered one push at a time.

**The dependent chain**, in order, each built on the one above:

| branch | what it lands |
|---|---|
| `gov-stack` 9ead53c | pre-PR self-check, `--pr-body` contract, PR template, `pr-contract` job |
| `gov-stack` a3dab2e | the policy-glob coverage check |
| `gov-stack` 05c5b28 | the steward skill, its linter wiring, the index leading-dot fix |
| `build/rules` e46ed2c | five policies become `.claude/rules/*.md`; `rules_sync.mjs` generates the Cursor copies |
| `build/contracts` 513a4c1 | `gh` removed from the role contracts; the judge's unattainable load bar |
| `build/index` | `CLAUDE.md` split into path-scoped rules |

**Independent branches**, each cut from `main`, to be rebased onto the chain
head rather than cherry-picked:

| branch | conflicts against the chain | resolution |
|---|---|---|
| `build/briefs` | `policy_known_bad.json` | regenerate: `--record-known-bad` on the merged tree. The file is generated, so a textual merge of it is meaningless |
| `build/readmes` | `policy_known_bad.json` | same |
| `build/archive` | `web-phase0.js` modify/delete | take the deletion. The chain's edit added a tool to the MCP mapping in a file the archive removes; the edit is moot, the deletion is the intent |
| `build/loop` | `policy_known_bad.json`, `policy_lint.mjs`, `governance.yml` | the only real one. Rebase LAST. Both sides are additive: the chain adds `--pr-body`, coverage and the allowlist; loop adds `--record`, `--stats`, `--sunset` and the `record` job. Resolve by keeping both, then re-run the acceptance — `REQUIRED_ROT` gains entries from both sides and the count must be the union |

**Two things a resuming session must not rediscover the hard way:**

Tag creation is refused by the agent proxy on both routes (`git push` of a tag,
and `POST /git/refs`), so the archive pass cites the commit `d5d8c4a` rather
than a tag name. A citation to a tag that does not exist is the dead-citation
class this audit removes.

`policy_known_bad.json` conflicts on every parallel branch because every branch
that fixes a defect re-records it. It is generated output; never merge it
textually, always regenerate. Treating it as a source file wastes a cycle each
time.
