R10-ARCH-DOCS-FIRST: the architecture, CI shape and development shape at programme end, in words and mermaid figures, and the owner's Buy Me a Coffee button. Part of #2395 and #201 (R10-ARCH-DOCS, the round's last stage, verifies, adjusts and wiring-tests what this lands, and closes the issue).

**Blocked on one owner decision**: `policy-docs` refuses `dev/README.md` (`named-docs`). Clearing it takes an entry that its own code puts at a cap raise's bar, so it waits for the owner's confirmation. See Red checks, option 1.

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

Visual language (note §4): meaning is in shape. A seat is a stadium, a script or detached job is a rectangle, a person's or agent's decision is a rhombus, a ref or store is a cylinder, and a planned edge is dashed. No block carries a hex value or an `%%{init}`, and (e) refuses either. Colour comes from the renderer.

Design choices the checks encode, stated so they are not read as bugs:
- (a) checks a backticked token as a repository path only when it contains `/` and its first segment is a top-level tracked name. A span with a placeholder (`<`, `>`, `*`, `{`, `$`) is skipped, so `handoff/<topic>` passes as prose.
- A marker inside an inline-code span is the grammar being quoted and is not read as a marker. The clean fixture carries one.
- The marker's unit is a list item, a table row, a paragraph, or a heading that covers its section (note §3).
- (d) skips `|…|` and quoted edge labels, and a subgraph id counts as declared.

Beyond the roster's `files` (`docs/architecture.md`, `README.md`), this PR writes the following, for train hot-file accounting (the orchestrator owns the roster, item F2):
- `tools/site/build_docs.mjs` (O-1, and the owner's footer carry);
- `docs/index.html` (owner's carry, this change only);
- `docs/site/docs.css` (the `.bmc` rule the built pages link);
- `docs/img/brand/coffee.svg`;
- `dev/README.md`;
- `tests/doc_claims.py`, `tests/layout.json`, `tests/closure.py`, `tests/closures.json`;
- `tools/policy/agreement.mjs`: one `SHARED_GRAMMARS` entry. The path-token grammar of predicate (a) is the one `tests/entities.py`'s `_sp_path_literal` uses, for the same concept, and discovery refused it unregistered. It is a hot file shared with R10-MERGE-SUBJECT-HARDEN;
- `dev/audit/harnesses/r10_mermaid_parse.mjs`, `dev/audit/harnesses/r10_arch_docs_first_mutants.py`.

Alternatives, and why each lost:
- An inline README link `[![…](svg)](https://…)`: HACS's README image rewriter (pinned by `tests/entities.py`) leaves a relative image unrewritten when `://` follows it on the line. That would break the image on HACS, so the link is by reference and the image stays inline.
- A hotlinked buymeacoffee badge: refused by the owner's carry and by doc_claims' site rules.
- A `<picture>` pair of SVGs in README: raw HTML that `build_docs.mjs` does not rewrite, so the site's readme page would point at `docs/img/...` from the site root, a dead path. One SVG with internal `prefers-color-scheme` renders on both.
- The rest are as the note lists (SVG figures, onboarding inside README, a separate CI-GATE file, planned modules in the module map).

🤖 Generated with [Claude Code](https://claude.com/claude-code) (attribution placed here, not at the end, because `## Friction` must be the last section and every line in it must parse)

https://claude.ai/code/session_01HTcKYp1ZHt1cQntacAVYtG

## Head

4ee04516855d2f6e49590e7d213d4c117ef82f31 (merge base c409c9b18a9fa42531004008d0ee03128def4729, `origin/main` at 2026-10-22T09:57:55Z; roster ref `handoff/audit-r10-roster` at 33138bc2f49b85f4f94c9edfad422789ef00eee3)

## Mutation proof

Instrument: `python3 dev/audit/harnesses/r10_arch_docs_first_mutants.py <scratch worktree>`, run at 62f1a9aae. The head adds one commit, 4ee045168, a `SHARED_GRAMMARS` entry in `tools/policy/agreement.mjs` that `tests/doc_claims.py` does not read. `tests/doc_claims.py` was re-run at the head (Figures). It applies each mutant in place, runs `tests/doc_claims.py`, lists the FAIL lines, and restores the file. Every row targets the predicate, not a tail line.

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

Every mutant is killed by the check named for its arm. M3 and M12 were first written to disable a guard, and the next line then crashed (KeyError, AttributeError): the mutant died by a crash, not by its check. Both now remove the finding itself, and the driver prints `CRASH` for a mutant that dies with no FAIL line.

## Null control

- M0 above: the unmutated head, 0 FAIL lines, rc 0.
- The checker's own controls, run by `tests/doc_claims.py` at the head:
  - The clean fixture yields no finding and no note.
  - The state-tolerance control: a marker naming a stub-`done` group, and a `retired-by` path absent from the stub tree, yield two notes and no finding (R1, R2).
  - With no marker, no roster is read, and none needs to exist (N1). The roster is a callable that records a call, and the check asserts it was never called.
  - A marker with no roster file is a finding.
- Each button red case removes the button from one place only, and the finding names that place.
- Failing test first: commit 02dc9baa1 adds the arms before the docs. At that commit `tests/doc_claims.py` is red on the real tree: `3 of 202 checks FAILED` (dev/README.md absent, no marker, no button in any of the three places).
- The mermaid parse has a null control: a planted broken block (`A[unclosed --> B`) makes the same driver exit 1 with a parse error.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`: `ALL 203 checks PASSED` at the head 4ee045168, with `(8 mermaid block(s), 28 marker(s), 0 note(s))`. The block count is every ```` ```mermaid ```` fence in the three marked documents, and the marker count is `_MARKER.findall` over the same three. Null: at 02dc9baa1 the same arm printed `4 block(s), 0 marker(s)`.
- `NODE_PATH=$(npm root -g) node dev/audit/harnesses/r10_mermaid_parse.mjs <tools/site copy after npm ci> docs/architecture.md dev/README.md README.md` (T1a): `mermaid 12.1.0 parse+render in Chromium: 8 block(s), 0 failure(s)`, rc 0. `npm ci` ran in a scratch copy of `tools/site/package.json` and `tools/site/package-lock.json` (the pinned 12.1.0), because `mermaid.parse` needs a DOM. Null: the planted broken block gives rc 1.
- Closure growth, `./tests/derive_closures.sh --single tests/doc_claims.py` on Linux: tests/doc_claims.py goes from 168 to 171 files. The added files are `dev/README.md`, `dev/programme/rosters/wave-r10-groups.json` and `docs/img/brand/coffee.svg`, and none was dropped. The command that diffed them is `python3 -c` over `git show <base>:tests/closures.json` against the head's file. Re-recorded on the clean tree, closures.json was unchanged. No workflow file entered the closure: (a) resolves paths through `git ls-files`, and no arm opens a workflow, so the note's "workflows read" growth does not arise.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted`. Its two inert-read predictions are applied in the diff.
- Planned modules: the non-done groups on the roster ref (33138bc2f) name 0 absent `custom_components/` paths, by `jq -r '.groups[]|select(.resume.stage!="done")|(.files//[])[]|select(startswith("custom_components/"))'` and a `[ -e ]` test per path. Null: the same loop with a planted `custom_components/heatpump_optimizer/no_such_module.py` counts 1.
- HACS image rule: the `_img_offences` block of `tests/entities.py`, run over the head's README, gives `[]`. Over the inline-link form it gives `[('docs/img/brand/coffee.svg', "a later '://' on the line fails the rewriter's lookahead")]`, the finding the first full `tests/entities.py` run raised on this branch.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/entities.py` at 31f7726f1 (the head less one harness line, M12's mutant in `dev/audit/harnesses/r10_arch_docs_first_mutants.py`, which no gate script reads): `1 of 2388 ENTITY CHECKS FAILED`. The one failure is the D11-05 template arm, which runs the whole `node tools/policy/policy_lint.mjs`. That run exits 1 on this branch with `[named-docs] dev/README.md` (see Red checks: it is the blocker). Every other entities check passes, including the module map, the HA boundary and the counts in `docs/architecture.md`, the orphan classification, and the HACS README image rule.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 1 error(s) across 43 policy file(s)` at the head, the `named-docs` error below. Null: `TOTAL: 0 error(s)` at `origin/main` c409c9b18.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` at 4ee045168: rc 1, with two REFUSE lanes, `policy_lint` and `mutants`. Both are the `named-docs` blocker: `mutants` refuses because the policy-lint entry point exits 1 on the corpus. Every other lane is ok or skip, and `agreement lane` reads `unregistered=0` after the entry above.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No code metric moved.
- `node tools/policy/policy_lint.mjs --budgets`: rc 0. always-loaded ~3497 against cap 3349 + band 500, and corpus ~62857 against 62892 + 500, the same values the design review measured at 8a4c438e7. No file this PR writes matches `POLICY_GLOBS`, and no CLAUDE.md row was added. No budget raise.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/layout.py`: rc 0. `node tests/md_tables.mjs`: `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`.
- Scope, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: FULL`, reason `tests/closure.py changes the gate itself`. That is a gate file, so CI runs the full suite. Locally: doc_claims, entities, layout, md_tables, structure, the policy lint and the parse driver. The rest is left to CI (fixer.md step 5).
- Contrast of the button, by the WCAG 2 relative-luminance formula: white on `#026aa8` (light `--accent`), and `#0b1a28` on `#4fb3f0` (dark). Light is 5.79:1 and dark is 7.58:1, both over 4.5:1. The command is a `python3 -c` over that formula, and its null control is a pair below 4.5:1: `#4fb3f0` on white is 2.32:1.

## Architecture score

`python3 tools/audit/archscore/score.py --diff c409c9b18a9fa42531004008d0ee03128def4729`: `Architecture score: dS +0.0000 NULL`. No production module is touched.

## Unpinned sites

none: the diff adds no production code.

## Red checks

**BLOCKER, owner decision needed (CLAUDE.md rule 2's bar; I stopped rather than push the payment).** `node tools/policy/policy_lint.mjs` (the `policy-docs` context, and through it `tests/entities.py`'s D11-05 template arm) refuses the new file:

```text
ERROR   [named-docs] dev/README.md: is named by .claude/rules/ratchet-budgets.md but has no cap in dev/governance/config/policy_budgets.json [...] Bring it under a POLICY_GLOBS pattern so a cap on it is actually compared, or add it to CORPUS_EXCLUDED with a reason.
```

- Cause: `ratchet-budgets.md` (its `paths:` and its prose) and three other policy files cite `tools/audit/README.md`. That path is untracked since 72826387f, so `resolveCited` falls back to the basename and resolves it to every tracked `README.md`. All the others are capped or excluded, and any new `README.md` anywhere in the tree trips this. The design note's §5 budget reading ("no file this group writes matches `POLICY_GLOBS`") is true, but it did not see this basename route.
- Measured: removing the stale `paths:` entry alone does not clear it. It leaves the prose citation, and it adds a `rule-binding` error for `tools/audit/README.md`.
- The payments available, none taken:
  1. Add `dev/README.md` to `dev/governance/config/corpus_excluded.json` `excluded`, with the reason "onboarding, not policy; it defers to CLAUDE.md". This is one line, on the same ground as `dev/archive/README.md`'s entry. `policy_lint.mjs`'s own comment on `CORPUS_EXCLUDED` says "adding to this list is ... the same bar as raising a cap", so it needs the owner's confirmation before the push. **Recommended**: the page states it is not policy, and the design rules out a cap on it, which would mean a corpus raise.
  2. Correct the stale `tools/audit/README.md` citations in the four policy files to `dev/audit/README.md`. That is a code-owned policy edit with owner review, and it is wider than this group.
  3. Rename the file away from `README.md`. That is a departure from the approved note's file list, so it is raised here, not made.
- On the owner's word for option 1, the change is one line in that JSON plus one sentence in the body. No other figure moves, because `policy_lint` is the only reader and doc_claims does not read the file.
- Cheaper detector: `tools/pr/ci_predict.py` (which `body_push.sh` runs) does not model `policy_lint`'s named-docs arm. `node tools/policy/policy_lint.mjs` itself is a seconds-long run that would have caught it before the full entities run. Root-cause owes a cost test of folding a named-docs prediction into `ci_predict.py`. Carry: R10-ARCH-DOCS (item named-docs basename): the same trap fires for any `README.md` the round adds.

Other reds, all local and before any push:
- No check has run on this branch yet: the handoff is its first push. Locally, the first full `tests/entities.py` run went red on the HACS README image rule (the inline button link). The finding is in the Figures above, and commit fd5382d5b repairs it.
  - Cheaper detector: none is missing. `tools/pr/ci_predict.py` does not model that rule, and the gate's own `tests/entities.py` caught it before any push.
- I also committed `tools/site/node_modules` locally by `git add -A` after the parse's `npm ci`, and caught it with `ci_predict.py`'s UNCLASSIFIED arm. I recut the two unpushed commits without it; nothing was pushed. The parse now installs into a scratch copy.

## Forward-carry

- Carry: R10-ARCH-DOCS (item R1). Own the end-of-round predicate "no target or retired-by marker names a done group". Here (c) is report-only: it prints a `note:` line and is never a finding (§3).
- Carry: R10-ARCH-DOCS (item T1). Wire a real `mermaid.parse` into a check. `dev/audit/harnesses/r10_mermaid_parse.mjs` is the driver T1a used, and it needs a DOM (Chromium).
- Carry: R10-ARCH-DOCS (item V1). Add the docs.css token map in `tools/site/build_docs.mjs` to mermaid's `themeVariables`. This PR uses only O-1's reach for the footer, not for the token map.
- Carry: R10-ARCH-DOCS (item V2). Confirm light and dark on both renderers. `dev/README.md`'s figures get GitHub's themes only.
- Carry: R10-ARCH-DOCS (item S1). Widen (e) tree-wide if it chooses. Today it covers `MERMAID_STYLE_DOCS`.
- Carry: R10-ARCH-DOCS (item D1). Check the machinery figure against R10-ORCH-MACHINERY's job and event-kind tables at its own merge base. The figure draws the final shape with markers.
- Carry: R10-ARCH-DOCS (item F1). Fold P40 there: compare the `docs/img/card/*.png` figures to the card. This group commits no figure.
- The owner's button carry already routes the verification of both placements and the link target to R10-ARCH-DOCS (roster ref 33138bc2f). Nothing new is owed there.
- Carry: R10-PLAN-ARTIFACT (item D2). One plan model, marked `[target: R10-PLAN-ARTIFACT]`. R10-ORCH-MACHINERY confirms that its part (3) builder extends that model.
- Carry: R10-ROUND-PLAYBOOK (item D3). Its path-resolving control is `doc_wiring_findings`: extend it to `dev/audit/README.md` rather than building a second checker.
- Carry: R10-CI-LAYOUT-P2 (item D4). The ruleset node is drawn `[target: R10-CI-LAYOUT-P2; owner step]`. `.github/workflows/pr-contract-rerun.yml` and `.github/workflows/budget-raise-gate-rerun.yml` are `[retired-by: R10-CI-LAYOUT-P2]`, and P2's gate-sweep workflow is marked `[target: R10-CI-LAYOUT-P2]`.
- decision: orchestrator. Carry: R10-FLOW-BOARD (item D5). The same notice goes to R10-REPLAY-SCOPED. The doc names the two units' jobs `<file stem> / <job>` either way.
- Destinations: these carries are the design note's, and the orchestrator lands them in the named groups' roster carries (finding-propagation.md). This PR adds no new finding beyond the design's.

## Friction

- environment: stale: the payload says the venv is on PATH, but `python3` here was the system interpreter, without voluptuous. Every run used `PATH=/opt/hpo/venv-ci/bin:$PATH`. Carry: dismissed: environment, not repository
- fixer.md#18: cost: the T1a parse needs Chromium plus mermaid's DOM. `mermaid.parse` under plain node fails (`DOMPurify.addHook is not a function`), so T1's gate wiring will need a browser lane. Carry: R10-ARCH-DOCS
- fixer.md#7: unclear: the roster lists #2395 under `fixes` for both this group and R10-ARCH-DOCS. This body says "Part of #2395" so the issue stays open until ARCH-DOCS verifies. Carry: dismissed: orchestrator decides the closing keyword
