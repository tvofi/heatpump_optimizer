R10-ARCH-DOCS-FIRST: the architecture, CI shape and development shape at programme end, in words and mermaid figures, and the owner's Buy Me a Coffee button. Part of #2395 and #201 (R10-ARCH-DOCS, the round's last stage, verifies, adjusts and wiring-tests what this lands, and closes the issue).

This is the docs delivery the owner (tvofi, 2026-10-22) asked to have stamped right after it merges.

Built to the approved design note `dev/programme/designs/R10-ARCH-DOCS-FIRST.md` at f122a1cb5d6aea08bb57840721e646c87f3c51fd (revision 2, ref `design/r10-arch-docs-first`). Design verdicts: `handoff-body/design-verdict-r10-arch-docs-first` (`Design review: revise 16954f0c8 architecture-unsound`, revision 1) and `handoff-body/design-verdict-r10-arch-docs-first-r2` (`Design review: approve f122a1cb5d6aea08bb57840721e646c87f3c51fd`).

What it writes:
- `docs/architecture.md`: every `##` section on main is kept. "How the pieces fit" takes seed 4305cd109's four-region diagram (outside, the Home Assistant boundary, the pure core, the learners) and its legend, re-derived at the merge base. The counts stay the tree's own, and `tests/entities.py` and `tests/doc_claims.py` still check them. "Where the architecture is measured" comes from the seed and now names `tools/audit/archscore/` and the wiring check. New: "The shape at programme end", one marked line per code group that changes the shape. No non-done group's `files` names an absent package path, so the page has no Planned-modules list (Figures).
- `dev/README.md` (new): the developer onboarding, from seed 0edd7fa66 with its literal counts replaced by commands. It covers the `dev/` layout, the governing documents, and the work in order: audit → [design → design review, L/XL] → fix → fix review → train → merge → record → stamp. Then the requirements before a push and the CI shape: the job graph at programme end, the workflows today, and the refusal order folded in from `0edd7fa66:dev/CI-GATE.md`. Then the orchestration machinery: its components (carry a), one handoff's path as a `sequenceDiagram` naming the ledger kind each step opens or closes (carry b), and who decides (carry c). Last, a command-generated index of `dev/audit/harnesses/` (the O9 fold).
- `README.md`: one developer paragraph pointing to `dev/README.md`, and the button at the top.
- The button: https://buymeacoffee.com/rpgshcwb2tp from three places:
  - the top of `README.md`, as an in-tree SVG, `docs/img/brand/coffee.svg`;
  - `docs/index.html`'s own hand-written `<footer>`;
  - the shared footer that `tools/site/build_docs.mjs` renders on every markdown page.

  On the site the button is an inline SVG icon plus a `.bmc` rule in `var(--accent)`/`var(--accent-ink)`, so it follows the theme toggle. The README's SVG cannot read CSS variables, so it carries docs.css's light and dark token values under `prefers-color-scheme`, and the test compares those values with `docs/site/docs.css`. No image, script, stylesheet or CSS `url()` comes from another origin.
- `tests/doc_claims.py`:
  - `doc_wiring_findings` checks predicates (a)–(e) of the note's §6 over the three marked documents, and (e) over the note's sibling-site list.
  - `coffee_button_findings` checks the three placements and the SVG's tokens.
  - Red fixtures, the state-tolerance control and the null controls are inline. The fixtures' roster is an inline stub (T2).
- Classification: the `dev` category in `tests/layout.json`. `tests/closure.py` moves the roster and the SVG to `INERT_EXCEPT`, because doc_claims opens them. `tests/closures.json` is re-recorded with `--single`, plus two harness inert reads.
- Round 2, the `named-docs` refusal of `dev/README.md`, cleared by removing its cause (section "Policy edits under mandate 6329234399" below): `tools/policy/policy_lint.mjs` resolves a citation spelt at a moved file's new path by its canon spelling, pinned in its acceptance; and `dev/governance/dimensions/D9.md`'s stale `harnesses/README.md` citation now names `dev/audit/README.md`.

### Policy edits under mandate 6329234399

Decision O-2 (orchestrator, 2026-10-22, under mandate 6329234399, scope all) approved payment 2: correct the stale citations so that no `README.md` the round adds trips the basename fallback. It is a citation correction, not a new rule, so it is outside moratorium 0012. Measured in this round, the round-1 diagnosis was inverted, so payment 2 as briefed does not clear the refusal (Figures, "payment 2 as briefed"):
- `policy_lint.mjs` lists tracked files by their canon spelling (`counts.mjs` `canon`, from `tests/layout.json`'s `retired` moves), and `tools/audit/README.md` is the canon spelling of `dev/audit/README.md` (move `since: 1995`). So the `tools/audit/README.md` entry in `ratchet-budgets.md`'s `paths:` resolves exactly. The citation that falls to the basename is the correct one, `dev/audit/README.md`: `resolveCited` looked the token up as written, missed the canon'd listing, and resolved the basename `README.md` to every tracked `README.md`. Four policy files cite it (`ratchet-budgets.md`, `.claude/skills/steward/SKILL.md`, `CLAUDE.md`, `dev/governance/roles/COMMON.md`), all correctly.
- The one genuinely stale citation is `harnesses/README.md` in `dev/governance/dimensions/D9.md`, a file archived in 72826387f.

What this PR does instead, the same payment's intent (remove the cause, correct the stale citation to the file the sentence means):
1. `tools/policy/policy_lint.mjs` `resolveCited`: a token missing the listing is looked up again by `canon(token)` before the basename fallback. One line, plus one acceptance pin: a synthetic listing spelt at the first `.md` move's old path, with a second file sharing its basename, must resolve a citation at the new path to the old path alone. The fixture count goes from 246 to 247 pins. Not code-owned (`.github/CODEOWNERS` names `counts.mjs` and `policy_lint_envmatrix.mjs` in `tools/policy/`, not `policy_lint.mjs`).
2. `dev/governance/dimensions/D9.md` (a dimension brief, policy, in the owner's words): `see \`harnesses/README.md\`` becomes `see \`dev/audit/README.md\``, the harness contract the sentence points a finder to (`dev/audit/README.md` names itself "the harness contract"). A citation correction only; the brief's method is unchanged.

The `.claude/rules/` and `.cursor/rules/*.mdc` copies needed no change: `ratchet-budgets.md` is left as it is (both its `paths:` entries are correct, and removing either was measured to add a refusal), and `rules_sync.mjs --check` is ok. The orchestrator approves the D9.md correction under the mandate as O-2's citation correction; the `policy_lint.mjs` line departs from O-2's letter, because its premise measured false, and the review should confirm it. Payment 1 (a `corpus_excluded.json` line) was not taken: an architecture-improving payment existed, so CLAUDE.md rule 2's bar for it was not met. No budget file changes, so there is no `## Raise justification`.

Visual language (note §4): meaning is in shape. A seat is a stadium, a script or detached job is a rectangle, a person's or agent's decision is a rhombus, a ref or store is a cylinder, and a planned edge is dashed. No block carries a hex value or an `%%{init}`, and (e) refuses either. Colour comes from the renderer.

Design choices the checks encode, stated so they are not read as bugs:
- (a) checks a backticked token as a repository path only when it contains `/` and its first segment is a top-level tracked name. A span with a placeholder (`<`, `>`, `*`, `{`, `$`) is skipped, so `handoff/<topic>` passes as prose.
- A marker inside an inline-code span is the grammar being quoted and is not read as a marker. The clean fixture carries one.
- The marker's unit is a list item, a table row, a paragraph, or a heading that covers its section (note §3).
- (d) skips `|…|` and quoted edge labels, and a subgraph id counts as declared.
- `resolveCited` prefers the canon spelling over the basename: a citation at a moved file's new path names that file only. A citation whose canon spelling is untracked still falls to the basename, as before.

Beyond the roster's `files` (`docs/architecture.md`, `README.md`), this PR writes the following, for train hot-file accounting (the orchestrator owns the roster, item F2):
- `tools/site/build_docs.mjs` (O-1, and the owner's footer carry);
- `docs/index.html` (owner's carry, this change only);
- `docs/site/docs.css` (the `.bmc` rule the built pages link);
- `docs/img/brand/coffee.svg`;
- `dev/README.md`;
- `tests/doc_claims.py`, `tests/layout.json`, `tests/closure.py`, `tests/closures.json`;
- `tools/policy/agreement.mjs`: one `SHARED_GRAMMARS` entry. The path-token grammar of predicate (a) is the one `tests/entities.py`'s `_sp_path_literal` uses, for the same concept, and discovery refused it unregistered. It is a hot file shared with R10-MERGE-SUBJECT-HARDEN;
- `tools/policy/policy_lint.mjs` (round 2: `resolveCited` canon lookup and its pin; a hot file);
- `dev/governance/dimensions/D9.md` (round 2: policy, one citation corrected under mandate 6329234399);
- `dev/audit/harnesses/r10_mermaid_parse.mjs`, `dev/audit/harnesses/r10_arch_docs_first_mutants.py`.

Alternatives, and why each lost:
- An inline README link `[![…](svg)](https://…)`: HACS's README image rewriter (pinned by `tests/entities.py`) leaves a relative image unrewritten when `://` follows it on the line. That would break the image on HACS, so the link is by reference and the image stays inline.
- A hotlinked buymeacoffee badge: refused by the owner's carry and by doc_claims' site rules.
- A `<picture>` pair of SVGs in README: raw HTML that `build_docs.mjs` does not rewrite, so the site's readme page would point at `docs/img/...` from the site root, a dead path. One SVG with internal `prefers-color-scheme` renders on both.
- Payment 2 as briefed (rewrite `tools/audit/README.md` to `dev/audit/README.md`): measured to leave `named-docs` and add `rule-binding` (Figures).
- Payment 1 (exclude `dev/README.md` from the corpus): a raise-bar entry, not approvable while the canon fix exists (CLAUDE.md rule 2), and it would leave the trap for the next `README.md`.
- Renaming `dev/README.md`: a departure from the approved note's file list, and it leaves the trap.
- The rest are as the note lists (SVG figures, onboarding inside README, a separate CI-GATE file, planned modules in the module map).

🤖 Generated with [Claude Code](https://claude.com/claude-code) (attribution placed here, not at the end, because `## Friction` must be the last section and every line in it must parse)

https://claude.ai/code/session_019uBtZfqMPgdCvWq52YBP3X

## Head

122381f55daa95b7a8264c1202f8b2ef11bb5429 (merge base cd4aaed44b9000057aeff01ee3df9f80dbec8aad, `origin/main` at 2026-10-22T10:19:08Z, measured 2026-10-22T10:46Z; roster ref `handoff/audit-r10-roster` at aa38bdd5f65ce4327c6def865107d17864bf7926). The head is round 1's 4ee045168, a merge of `origin/main` (035b760db), and one commit, 122381f55.

## Mutation proof

Docs arms. Instrument: `python3 dev/audit/harnesses/r10_arch_docs_first_mutants.py <scratch worktree at 122381f55>`. It applies each mutant in place, runs `tests/doc_claims.py`, lists the FAIL lines, and restores the file. Every row targets the predicate, not a tail line.

| mutant | rc | checks that go red |
|---|---|---|
| M0 null (no mutation) | 0 | none (null control) |
| M1 (a) path resolution never fires | 1 | red fixture: a renamed path is a finding |
| M2 (a) marker exemption dropped | 1 | every path resolves or is marked, every marker names a roster group, every block is well formed; the clean fixture yields no finding and no note (null control); state tolerance: a marker naming a done group, and an absent retired-by path, yield only notes |
| M3 (b) unknown group passes | 1 | red fixture: a marker naming no roster group is a finding |
| M4 (b) malformed marker passes | 1 | red fixture: a malformed marker is a finding |
| M5 (c) refuses a done group | 1 | state tolerance: a marker naming a done group, and an absent retired-by path, yield only notes |
| M6 N1 roster read unconditionally | 1 | no marker: no roster is read, and none needs to exist (null control, N1) |
| M7 (d) declared-node rule off | 1 | red fixture: a bare node id used once is a finding |
| M8 (d) diagram type unchecked | 1 | red fixture: a block of an unknown diagram type is a finding |
| M9 (d) sequence participants unchecked | 1 | red fixture: an undeclared sequence participant is a finding |
| M10 (e) hex colour unchecked | 1 | red fixture: a hex fill is a finding |
| M11 (e) init unchecked | 1 | red fixture: an init directive is a finding |
| M12 button: README arm off | 1 | red case: the button removed from README.md is a finding there |
| M13 button: index footer arm off | 1 | red case: the button removed from docs/index.html is a finding there |
| M14 button: built footer arm off | 1 | red case: the button removed from architecture.html is a finding there |
| M15 button: SVG token compare off | 1 | red case: an SVG colour that is not the docs.css token is a finding |
| P1 production: button gone from build_docs.mjs footer | 1 | README top, the product page footer and every built page's footer link the button, from in-tree tokens |
| P2 production: button gone from docs/index.html footer | 1 | README top, the product page footer and every built page's footer link the button, from in-tree tokens |
| P3 production: button gone from README top | 1 | README top, the product page footer and every built page's footer link the button, from in-tree tokens |
| P4 production: a marker dropped from dev/README.md | 1 | every path resolves or is marked, every marker names a roster group, every block is well formed |

Every mutant is killed by the check named for its arm, and the driver prints `CRASH` for a mutant that dies with no FAIL line (none did).

Round-2 linter line. Mutant: delete `if (listing.set.has(canon(token))) return [canon(token)]` from `resolveCited` and run `node tools/policy/policy_lint.mjs`: rc 1, with `FIXTURE VACUOUS: a citation of the moved file \`dev/programme/HANDOVER.md\` resolved to ["docs/HANDOVER.md","elsewhere/HANDOVER.md"], not to its canon spelling \`docs/HANDOVER.md\` alone`, and on the tree `ERROR [named-docs] dev/README.md: is named by .claude/rules/ratchet-budgets.md` (`TOTAL: 1 error(s)`). Restored: rc 0. `node tools/policy/policy_lint_mutants.mjs` at the head: `MUTANTS ok`, `namedDocsOverTree` and `citationPresenceOverTree` among the checks that turn the acceptance red when emptied.

## Null control

- M0 above: the unmutated head, 0 FAIL lines, rc 0.
- The checker's own controls, run by `tests/doc_claims.py` at the head:
  - The clean fixture yields no finding and no note.
  - The state-tolerance control: a marker naming a stub-`done` group, and a `retired-by` path absent from the stub tree, yield two notes and no finding (R1, R2).
  - With no marker, no roster is read, and none needs to exist (N1). The roster is a callable that records a call, and the check asserts it was never called.
  - A marker with no roster file is a finding.
- Each button red case removes the button from one place only, and the finding names that place.
- Failing test first: commit 02dc9baa1 adds the arms before the docs. At that commit `tests/doc_claims.py` is red on the real tree: `3 of 202 checks FAILED` (dev/README.md absent, no marker, no button in any of the three places).
- The mermaid parse: a planted broken block (`A[unclosed --> B`) makes the same driver exit 1, `1 block(s), 1 failure(s)`, with a parse error.
- The stale-citation null (the brief's): re-adding `harnesses/README.md` to D9.md at the head, `node tools/policy/policy_lint.mjs` exits 1 with `ERROR [named-docs] dev/README.md: is named by tools/audit/briefs/D9.md` (D9.md's canon spelling), `TOTAL: 1 error(s)`. Restored: `TOTAL: 0`.
- The linter fix alone, with D9.md still stale, was the first measurement: `TOTAL: 1 error(s)`, the D9.md named-docs error. Each half is needed.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at 122381f55: `ALL 203 checks PASSED`, with `(8 mermaid block(s), 28 marker(s), 0 note(s))`. The block count is every ```` ```mermaid ```` fence in the three marked documents, and the marker count is `_MARKER.findall` over the same three. Null: at 02dc9baa1 the same arm printed `4 block(s), 0 marker(s)`.
- `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs <tools/site copy after npm ci> docs/architecture.md dev/README.md README.md` (T1a): `mermaid 12.1.0 parse+render in Chromium: 8 block(s), 0 failure(s)`, rc 0. `npm ci` ran in a scratch copy of `tools/site/package.json` and `tools/site/package-lock.json` (the pinned 12.1.0). Null: the planted broken block gives rc 1.
- `node tools/policy/policy_lint.mjs` at 122381f55: `TOTAL: 0 error(s) across 43 policy file(s)`, rc 0, `FIXTURE ok: 92 error(s) hold 247 pins`, with `dev/README.md` present. Null: at 4ee045168 merged with main (035b760db), `TOTAL: 1 error(s)`, the `named-docs` error, with `246 pins`.
- Payment 2 as briefed, measured at 035b760db and reverted: rewriting the `paths:` entry `tools/audit/README.md` to `dev/audit/README.md` in `dev/governance/rules/ratchet-budgets.md`, then `node tools/policy/rules_sync.mjs` and `node tools/policy/policy_lint.mjs`: `TOTAL: 2 error(s)`, `named-docs` on dev/README.md (still named by `.claude/rules/ratchet-budgets.md`) and `rule-binding` on `tools/audit/README.md`. Dropping the `dev/audit/README.md` entry instead moved the `named-docs` source to `.claude/skills/steward/SKILL.md`, `TOTAL: 1 error(s)`: the correct citations are what fall to the basename.
- The four policy files citing `dev/audit/README.md`: `git ls-files` over the policy globs piped to `grep -n 'audit/README'` returns `.claude/rules/ratchet-budgets.md`, `.claude/skills/steward/SKILL.md`, `CLAUDE.md`, `dev/governance/roles/COMMON.md` (plus the canonical `dev/governance/rules/ratchet-budgets.md` and `dev/audit/README.md` itself), and `.claude/workflows/*.js`, which no glob measures.
- `node tools/policy/policy_lint_mutants.mjs`: `MUTANTS ok: every check this clone could drive turns the acceptance red when it is emptied`.
- Closure growth: `tests/closures.json`'s `tests/doc_claims.py` entry against `git show cd4aaed44:tests/closures.json`, by a `python3 -c` set difference: 168 to 171 files, adding `dev/README.md`, `dev/programme/rosters/wave-r10-groups.json` and `docs/img/brand/coffee.svg`, dropping none.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against cd4aaed44b90`.
- Planned modules: the non-done groups on the roster ref (aa38bdd5f) name 0 absent `custom_components/` paths, by `jq -r '.groups[]|select(.resume.stage!="done")|(.files//[])[]|select(startswith("custom_components/"))'` and a `[ -e ]` test per path. Null: the same loop with a planted `custom_components/heatpump_optimizer/no_such_module.py` counts 1.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/entities.py` at 122381f55: `ALL 2388 ENTITY CHECKS PASSED`, the D11-05 template arm (which runs the whole `node tools/policy/policy_lint.mjs`) and the HACS README image rule included. Null: round 1's run at 31f7726f1 gave `1 of 2388 ENTITY CHECKS FAILED`, that arm, on the `named-docs` refusal.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: always-loaded ~3497 against cap 3349 + band 500, corpus ~62857 against 62892 + 500, role fixer ~6176 against 5852 + 500, role record ~7320 against 7405 + 500, role policy ~9904 against 9958 + 500. D9.md's correction is token-neutral at the corpus figure. No budget file changes.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/layout.py`: rc 0. `node tests/md_tables.mjs`: `doc_swallowed_prose_lines=0`, `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`.
- Scope, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: FULL`, reason `tests/closure.py changes the gate itself, so every closure is suspect`. CI runs the full suite. Locally: doc_claims, entities, layout, md_tables, structure, the policy lint, its mutants and the parse driver. The rest is left to CI (fixer.md step 5).
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` at 122381f55: every lane ok or skip (`closures` skipped by the variable; `push order` and `ancestry reds` skipped, no remote branch yet). `policy_lint` and `mutants` ok, `agreement lane` `AGREEMENT ok`, `claim files` byte-identical to origin/main. Null: its first run on this body, without `## Approval`, refused `pr-body` (`no \`## Approval\` section, and this diff touches \`tools/audit/briefs/D9.md\``).
- Contrast of the button, by the WCAG 2 relative-luminance formula over `docs/site/docs.css`'s `--accent`/`--accent-ink`: white on `#026aa8` (light) is 5.79:1, and `#0b1a28` on `#4fb3f0` (dark) is 7.58:1, both over 4.5:1. The command is a `python3 -c` over that formula. Null: `#4fb3f0` on white is 2.32:1.
- Claims and version: `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md` exits 0. The branch claims nothing.

## Architecture score

`python3 tools/audit/archscore/score.py --diff cd4aaed44b9000057aeff01ee3df9f80dbec8aad`: `Architecture score: dS +0.0000 NULL`. No production module is touched.

## Unpinned sites

none: the diff adds no production code. The `policy_lint.mjs` line is pinned by its own acceptance (Mutation proof).

## Red checks

- No check has run on this branch yet: no pull request is open. Round 1's local reds, all before any push:
  - `policy-docs` (`node tools/policy/policy_lint.mjs`), and through it `tests/entities.py`'s D11-05 template arm, refused `dev/README.md` with `named-docs`. Cleared in round 2 by the canon lookup and the D9.md correction above. Cause: `resolveCited` did not canon a token before falling to the basename, so a correct citation of a moved file named every file sharing its basename. Process state: the acceptance pinned exact, unique-basename, ambiguous and folded resolution against synthetic listings, none of them canon'd, so the canon route had no witness; the pin added here is that witness. Cheaper detector: `node tools/policy/policy_lint.mjs` itself is a seconds-long run; `tools/pr/ci_predict.py` (which `body_push.sh` runs) does not model the named-docs arm. Carry: dismissed: with the canon fix, the trap that made the detector worth building is gone, and the lint run already catches a genuinely stale citation in seconds.
  - The first full `tests/entities.py` run went red on the HACS README image rule (the inline button link). Commit fd5382d5b repairs it. Cheaper detector: none is missing; the gate's own `tests/entities.py` caught it before any push.
  - `tools/site/node_modules` was committed locally by `git add -A` after the parse's `npm ci`, caught by `ci_predict.py`'s UNCLASSIFIED arm and recut before any push. The parse now installs into a scratch copy.

## Forward-carry

- Carry: R10-ARCH-DOCS (item R1). Own the end-of-round predicate "no target or retired-by marker names a done group". Here (c) is report-only: it prints a `note:` line and is never a finding (§3).
- Carry: R10-ARCH-DOCS (item T1). Wire a real `mermaid.parse` into a check. `dev/audit/harnesses/r10_mermaid_parse.mjs` is the driver T1a used, and it needs a DOM (Chromium).
- Carry: R10-ARCH-DOCS (item V1). Add the docs.css token map in `tools/site/build_docs.mjs` to mermaid's `themeVariables`. This PR uses only O-1's reach for the footer, not for the token map.
- Carry: R10-ARCH-DOCS (item V2). Confirm light and dark on both renderers. `dev/README.md`'s figures get GitHub's themes only.
- Carry: R10-ARCH-DOCS (item S1). Widen (e) tree-wide if it chooses. Today it covers `MERMAID_STYLE_DOCS`.
- Carry: R10-ARCH-DOCS (item D1). Check the machinery figure against R10-ORCH-MACHINERY's job and event-kind tables at its own merge base. The figure draws the final shape with markers.
- Carry: R10-ARCH-DOCS (item F1). Fold P40 there: compare the `docs/img/card/*.png` figures to the card. This group commits no figure.
- The owner's button carry already routes the verification of both placements and the link target to R10-ARCH-DOCS. Nothing new is owed there.
- Carry: R10-PLAN-ARTIFACT (item D2). One plan model, marked `[target: R10-PLAN-ARTIFACT]`. R10-ORCH-MACHINERY confirms that its part (3) builder extends that model.
- Carry: R10-ROUND-PLAYBOOK (item D3). Its path-resolving control is `doc_wiring_findings`: extend it to `dev/audit/README.md` rather than building a second checker.
- Carry: R10-CI-LAYOUT-P2 (item D4). The ruleset node is drawn `[target: R10-CI-LAYOUT-P2; owner step]`. `.github/workflows/pr-contract-rerun.yml` and `.github/workflows/budget-raise-gate-rerun.yml` are `[retired-by: R10-CI-LAYOUT-P2]`, and P2's gate-sweep workflow is marked `[target: R10-CI-LAYOUT-P2]`.
- decision: orchestrator. Carry: R10-FLOW-BOARD (item D5). The same notice goes to R10-REPLAY-SCOPED. The doc names the two units' jobs `<file stem> / <job>` either way.
- Round 1's carry about the named-docs basename trap (any `README.md` the round adds trips it): Carry: dismissed: payment 2's intent was taken, and the canon lookup removes the trap; a genuinely stale citation still falls to the basename, which is the check working.
- Destinations: these carries are the design note's, and the orchestrator lands them in the named groups' roster carries (finding-propagation.md). This PR adds no new finding beyond the design's.

## Approval

Owner approval is owed for one policy file, `dev/governance/dimensions/D9.md` (one citation corrected). Approved by the orchestrator under mandate 6329234399 (scope all), decision O-2 (2026-10-22): correct the stale `README.md` citation to the file the sentence means. A citation correction, not a new rule, so outside moratorium 0012. `tools/policy/policy_lint.mjs` is not code-owned; its line departs from O-2's letter (see "Policy edits under mandate 6329234399") and the review confirms it. No budget file changes.

## Friction

- environment: stale: the payload says the venv is on PATH, but `python3` here was the system interpreter, without voluptuous. Every run used `PATH=/opt/hpo/venv-ci/bin:$PATH`. Carry: dismissed: environment, not repository
- fixer.md#18: cost: the T1a parse needs Chromium plus mermaid's DOM. `mermaid.parse` under plain node fails (`DOMPurify.addHook is not a function`), so T1's gate wiring will need a browser lane. Carry: R10-ARCH-DOCS
- fixer.md#7: unclear: the roster lists #2395 under `fixes` for both this group and R10-ARCH-DOCS. This body says "Part of #2395" so the issue stays open until ARCH-DOCS verifies. Carry: dismissed: orchestrator decides the closing keyword
- fixer.md#3: contradiction: decision O-2 prescribed rewriting `tools/audit/README.md` to `dev/audit/README.md`, on round 1's diagnosis, but `policy_lint.mjs` lists tracked files by canon spelling, so the rewrite was measured to add a refusal; the round took the decision's intent instead. Carry: dismissed: resolved in this PR, the review confirms the departure
