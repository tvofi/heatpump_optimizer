Fix review: merge c00082a9ae41447820af2a73c8fe4d1a2d661c8c

bus-nonce: 41dfaf10948eb8633b0941d53f4a84b3

## Scope

PR #2609, group R10-ARCH-DOCS-FIRST, fixer round 3 (code 7ae69419e, head c00082a9ae41447820af2a73c8fe4d1a2d661c8c). Reviewed adversarially from detached worktrees at the head, base origin/main 543c8087c57973ee58033a0c62520b5ec3a58621. I checked the head again just before writing this verdict: the branch and the PR still point at c00082a9a. `dev/governance/roles/` is identical between the merge base and origin/main, so the contract I followed is the current one.

## Findings

- pr-contract is red at this head, in both runs (jobs 119812987030 and 119813184314), and only because of the body. `tools/audit/carry_audit.py check` reads the `## Forward-carry` bullet `- Destinations: the orchestrator lands these in the named groups' roster carries (finding-propagation.md).` as a finding item with no destination. It prints `CARRY-AUDIT: 17 finding item(s): 16 routed, 1 unrouted`, rc 1. The body's `## Red checks` does not answer this red. Fix: rewrite that line as plain prose rather than a bullet, or end it with a `Carry:`. A body-only edit, so the head does not move. I reproduced the failure on the live body, and the same body with the line as prose prints `16 routed, 0 unrouted`, rc 0 (ev/carry-audit.txt). The code is unaffected. Owed before the merge train takes the PR. Carry: R10-ARCH-DOCS-FIRST
- The reason for the `dev/README.md` entry in `dev/governance/config/corpus_excluded.json` is written only in commit 7ae69419e's message and the PR body. In the file, the entry is a bare path. The file's `_comment` names the classes of excluded entries (finder reports, round baselines, the user-facing `docs/index.html`), and developer onboarding is not among them. A later reader of the file alone cannot tell why it is there. This is cosmetic: R10-ARCH-DOCS drops the entry once the `resolveCited` canon lookup lands. Carry: R10-ARCH-DOCS
- `docs/img/brand/coffee.svg` switches between light and dark token values on `prefers-color-scheme`. On GitHub and in HACS, an SVG loaded through `<img>` follows the OS or browser preference, not the host page's theme toggle. So the button can be drawn in light tokens on a dark-themed page. The values match docs.css's tokens, and the test compares them. The mismatch is about which renderer setting decides the theme, and it belongs to the existing V2 carry ("Confirm light and dark on both renderers"). Carry: R10-ARCH-DOCS

## Evidence

Merge: `git merge-tree --write-tree origin/main c00082a9a…` → tree 36f5fe3ed4c5, rc 0, no conflict (ev/merge-tree-and-scope.txt). No claim files changed, and `VERSION`, `RELEASE_NOTES.md` and the manifest are unchanged (three-dot diff, rc 0; ev/head-checks.txt).

1. The base-pinned lanes, reproduced. In three scratch worktrees at the head, I restored each job's pinned pathspec list as `.github/workflows/governance.yml` lists it, from 543c8087c, and committed it the way CI does:
   - policy-docs: restores `tests/layout.py` only. `RULES-SYNC ok`; codeowners_gap `RESULT uncovered_files=0`; `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 43 policy file(s)`, `FIXTURE ok: 92 error(s) hold 246 pins`; `FRAGMENTS ok`; `HOOKS ok` (ev/lane-policy-docs.txt).
   - env-matrix: restores `tests/layout.py`, with the head's driver as the step keeps it. `16 declared outcome(s) held, 0 did not, across 6 environment shape(s)`, rc 0, `ok pr / policy_lint rc=0 and every pin earned` (ev/lane-env-matrix.txt).
   - wave-script: restores `tests/entities.py` and `tests/layout.py`. `202 passed, 0 failed`; `agreement_py restore: 13 closure file(s), 13 covered …, 0 missing`; `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok` (ev/lane-wave-script.txt).
   - I attacked one path specifically: policy-docs and env-matrix restore the base's `tests/layout.py`, which has no `repo_path`, while keeping the head's `tests/entities.py`, which imports it. Neither lane imports entities.py, so both stay clean.
   - CI check-runs at this head (ev/check-runs.tsv): policy-docs, env-matrix, wave-script, instrument-self-tests, typing, browser, mutation, briefs, closure-scope, scope, arch-score ×2, budget-raise-gate ×2, hassfest, validate-hacs and delivery-status are all success.
   - Still in progress when I read them: fast (3.14), coverage, closures, CodeQL Analyze (python).
   - pr-contract is red twice; see Findings.
   - nightly-status is red with `NIGHTLY ABSENT: no scheduled run of the workflow was found at all`. The diff does not reach what it reads, it is not a required check, and it does not block.
2. Decision O-5.
   - (a) The path-token grammar is defined once. `grep -rnF '[\w.-]+(?:/[\w.-]+)+/?' tests tools` returns only `tests/layout.py:61` (`PATH_TOKEN`). `tests/entities.py` `_sp_path_literal` and `tests/doc_claims.py` predicate (a) both call `layout.repo_path`.
     - The head's agreement lane: `unregistered=0`, `AGREEMENT ok`.
     - Null control: I added `_PATH_TOKEN = re.compile(r"[\w.-]+(?:/[\w.-]+)+/?")` back to doc_claims.py. In the base-pinned lane this gives `UNREGISTERED … in tests/doc_claims.py, tests/entities.py`, `unregistered=1`, `AGREEMENT REFUSED`. At the head unpinned it gives `UNREGISTERED … in tests/doc_claims.py, tests/layout.py`, `unregistered=1`. I restored the file afterwards (ev/agreement-and-null.txt).
   - (b) `## Raise justification`. No `*_budgets.json` changes.
     - Payment 2, the policy_lint canon lookup, was tried and measured. I read the cited CI job 119791595301: `ERROR [named-docs] dev/README.md: is named by .claude/rules/ratchet-budgets.md but has no cap`, `FIXTURE ok … 246 pins`.
     - The base-pin reason holds. `tools/policy/policy_lint.mjs` is on every pinned list, so this PR cannot change its own checker.
     - I hunted for a payment the body missed. The error text's other route is bringing `dev/README.md` under `POLICY_GLOBS` with a cap. That would make developer onboarding policy and grow the corpus, which is worse, not sounder. Renaming `dev/README.md` is listed and rejected in the body's alternatives. I found no better payment.
     - `tools/audit/archscore/score.py --diff <merge base>` at the head: `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). I did not re-take the "before" (a0520623) end of the body's dS line. No production module is touched, so dS 0 is expected at both ends.
   - (c) No file under `tools/policy/` differs from origin/main (0 files). The Forward-carry's first item names the canon-lookup PR (commit 122381f55) and dropping the corpus entry afterwards: "Carry: R10-ARCH-DOCS. Land `policy_lint.mjs` `resolveCited` canon lookup + its pin as its own PR …, then drop `dev/README.md`'s `corpus_excluded.json` entry". I did not open the roster carry at a `handoff/audit-r<N>-roster` SHA. The body says the orchestrator lands these carries in the roster.
   - (d) The D9.md correction is a plain-text change of `harnesses/README.md` to `dev/audit/README.md`. `dev/audit/harnesses/README.md` does not exist. `dev/audit/README.md`'s "The harness contract" section is the header contract the sentence refers to ("A header comment stating what it measures …"). The correction is right.
3. Content.
   - `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 203 checks PASSED`. This covers `doc_wiring_findings` (predicates (a)–(e)) over docs/architecture.md, README.md and dev/README.md, with its red fixtures and null controls.
   - `tests/entities.py` at the head, a full run: `ALL 2388 ENTITY CHECKS PASSED`, rc 0. That includes `architecture.md's entity diagram counts match the census` and the opening, HA-boundary and HA-free counts. The body had measured this one on an earlier tree; my run at this head agrees with its figure.
   - Mermaid: `r10_mermaid_parse.mjs` with tools/site after `npm ci`: `mermaid 12.1.0 parse+render in Chromium: 8 block(s), 0 failure(s)`. Null control: a planted broken flowchart gives `1 failure(s)`, rc 1 (ev/mermaid.txt, ev/mermaid-null.txt).
   - Stale paths: predicate (a) is clean, and every relative markdown link in dev/README.md and docs/architecture.md resolves.
   - Markers: there are 30 `[target:]`/`[retired-by:]` markers, and every one names a roster group (predicate (b) passes).
   - I did not re-derive which non-done groups "change the shape". That is the design note's §2 judgement, and its procedure is followed.
4. The button.
   - Placements: README.md line 16, above the first `##`, `[![Buy me a coffee](docs/img/brand/coffee.svg)][coffee]` with `[coffee]: https://buymeacoffee.com/rpgshcwb2tp`; the `<footer>` of docs/index.html; the shared `footer.site` in tools/site/build_docs.mjs.
   - Theme: `.bmc` uses `var(--accent)`/`var(--accent-ink)` in both docs.css and index.html. The SVG's light and dark fills equal docs.css's `--accent` and `--accent-ink` (#026aa8/#ffffff and #4fb3f0/#0b1a28).
   - Off-origin: the SVG references only the `xmlns`, and none of the edited files adds an off-origin URL. A relative .svg is served by raw.githubusercontent.com as `image/svg+xml` (measured), so it renders through HACS's rewrite.
   - HACS: the entities.py HACS rewriter checks all pass at the head.
   - My own mutants, beyond the fixer's harness, each restored afterwards (ev/own-mutants.txt). Each goes red in doc_claims:
     - O1: README image hotlinked off-origin.
     - O2: an off-origin `<img>` in the index button.
     - O3: an off-origin `url()` on `.bmc` in docs.css.
     - O4: an off-origin `<script>` in build_docs.
     - O5: the button moved below the first section.
     - O6: the SVG's dark fg changed to an off-token value.
     - O7: the index `.bmc` rule hardcoding the accent hex.
5. Mutants. `python3 dev/audit/harnesses/r10_arch_docs_first_mutants.py <scratch worktree at head>` gives 21 rows (M0–M16, P1–P4) and 0 `CRASH` lines. M0 is rc 0 with 0 FAIL, and every other row is rc 1 with exactly the FAIL lines the body's table names. M2's three lines, M5, M6 and M16's renamed-path fixture all match (ev/mutants.txt). The worktree was clean after the run. The body's figure "17 + 4 rows, 0 CRASH" holds.
6. Other body figures I re-took at this head, all equal to the body:
   - `STRUCTURE RATCHET PASSED`
   - `layout self-test: ok`
   - `RULES-SYNC ok`
   - md_tables `doc_swallowed_prose_lines=0`, `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`
   - policy_lint `TOTAL: 0 error(s) across 43 policy file(s)` and `246 pins`
   - check-wave-script `202 passed, 0 failed`
   - env-matrix `16 declared outcome(s) held`

   I did not re-run `ci_predict.py`, `prepr.sh` or the closure `select`. The heavy gate is CI's.
7. Policy paths changed (three-dot, merge base…head), for the orchestrator to approve under mandate 6329234399:
   - `dev/governance/dimensions/D9.md`: one citation corrected.
   - `dev/governance/config/corpus_excluded.json`: one entry, `dev/README.md`.

   No other path under `dev/governance/`, `.claude/`, `.cursor/`, CLAUDE.md, AGENTS.md or the PR template changed. `dev/README.md` is new and excluded from the named-docs corpus by that entry.
8. ev/HEAD.txt holds the head reviewed. No `/Users/` or `/private/` path appears in this verdict or in ev/.
