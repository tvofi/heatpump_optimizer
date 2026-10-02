_Requested by **tvofi**_

Part of #1798

Before: the reader documents are readable only as markdown on GitHub. After: `tools/site/build_docs.mjs` renders the README and every README Documentation row (less `docs/backlog.md`) into one page each over the vendored markdown-it 14.1.0, writing only into the directory it is given; `tools/site/package.json` and its lockfile pin mermaid 12.1.0 for the deploy only; `docs/site/docs.css` is the stylesheet; the product page's documentation cards, card and setup links, Reference link and footer point at the sub-pages. `tests/doc_claims.py` gains the build arm (every `FAIL` line fails it; zero pages is red), the sub-page link rule, the third-party refusal R9-WEB-1's review carried here (icon, preload and iframe on the product page; every request kind, the linked stylesheet's `@import`, `url()` and `image-set()`, and `srcset` on every built page), and the exact mermaid pin check, each with planted controls. Classification: a `tests/layout.json` glob, `/tools/site/ @tvofi` in `.github/CODEOWNERS`, `docs/site/docs.css` on `INERT_EXCEPT` and in `doc_claims.py`'s closure (as `docs/index.html` is), the build, `package.json` and the lock in that closure, the lock in `entities.py`'s. `carry-1645.json`'s five `doc_claims.py` line citations moved by the arm's eight lines. No `custom_components` file, golden, `VERSION` or `tests/README.md` line is touched.

## Head

e83fc996f7737d43aeaa57a46d432e69c5abb2cc

## Mutation proof

`mutation_table.py --scope changed` draws nothing (no production line changed), so the added sites were mutated by hand at the head.
- `build_docs.mjs`: 10 `errors.push(` sites, 9 killed by the planted-tree controls; the survivor is `zero pages built`, unreachable because the README is always a document (the arm's own anchor is the live one, red in the first-run output below).
- `doc_claims.py`: 33 mutable added lines through the reviewer's harness (crashes are not kills, baseline first): 29 killed. Not killed: `if kind == "third-party":` in the control loop (a mutant of the test), `if not css.is_file():` (crashes on the planted tree), and `if readme:` and `if git:` in the test's own scaffold (crash).
- The reviewer's four mutants on the CSS patterns, from its round-3 verdict: `re.I` dropped, the `image-set` loop emptied, its `findall` dropped, the external filter forced false: each rc 1 with the matching planted control FAIL.

## Null control

Failing test first at `1998fc5686a2ee7ad62c1b54d01b0d9423cf7a38`: the arm printed `FAIL the build exists and built at least one page (anchor)  [tools/site/build_docs.mjs does not exist]`, 4 of 126 checks FAILED. At the head, `docs_controls.py` (ported to the repository paths) prints a green baseline and 13 `RED` lines: cross-page and same-page anchor to a missing heading, a missing image, a link to an untracked file, a README row for a missing file, a stale EXCLUDE entry, a heading renamed under an inbound link, a README without its table, a raw third-party image, two anchor-free documents with one page name, an untracked stylesheet, a README row naming a missing product-page file. Inside the arm: a third-party icon, preload and iframe (product page and built page), script, image, `srcset`, a stylesheet `@import`, an uppercase `URL()` font, an `image-set()` string and a `@font-face` src, a missing linked stylesheet, a link to `tuning.html`, a docs card linked to GitHub, a dead anchor, a build that dies without a FAIL line, no tracked-file list, a missing build script, a mermaid range and a lock that disagrees; a same-origin icon is not refused.

## Figures

Rules: counts are what the instrument prints at the head, in the venv `/Users/timmalmstrom/hpo-seats/R9-F11.4-venv`, `PYTHONPATH=tests/hastub`.
- `node tools/site/build_docs.mjs --root . --tree <(git ls-files) --out DIR`: `pages 9, pageLinks 51, anchors 39, githubLinks 19, images 21, badges 4, external 17, mermaid 8`.
- `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/docs_controls.py .`: `RESULT: every control red, baseline green`, 13 `RED` lines.
- `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/mutate_build.py .` and `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/mutate_arm_rev.py .`: the counts above (`33 mutable lines among 289 added lines`, `BASELINE in_tree_failures=0`, `SURVIVORS: 4`).
- `python tests/doc_claims.py`: `ALL 155 checks PASSED` (`ALL 121 checks PASSED` at the merge base).
- `python tests/entities.py`: `ALL 2081 ENTITY CHECKS PASSED`.
- `node .claude/workflows/brief_lint.mjs`: exit 0.
- `python3 tests/closure.py check --in-dir <closure-recordings of CI run 37072797978, doc_claims only> --partial`: `committed closures cover every file this run touched`.

## Red checks

- `briefs`: the arm's 8 added top lines moved `check_simulate_plan_fields` out of `carry-1645.json`'s window. Cheaper detector: `node .claude/workflows/brief_lint.mjs` run locally; I did not run it because my pre-push list did not name it.
- `closures`, two causes in order. First `INERT READS UNDER-APPROXIMATED`: the stylesheet scan opens `docs/site/docs.css`, which is INERT, and `inert_reads` had no `doc_claims.py` entry; closures-autofix printed `skip-not-under-scoped`. Then `UNDER-SCOPED`: with the inert entry in, the file also had to be in `doc_claims.py`'s closure list and on `INERT_EXCEPT`, as `docs/index.html` is; closures-autofix printed `skip-failed-recording`, so I hand-merged the Linux recording of CI run 37072797978 for that script alone. Cheaper detector for both: `./tests/derive_closures.sh --single tests/doc_claims.py --record-only --out-dir D` then `python3 tests/closure.py check --in-dir D --partial`, run after any change that adds a file open to the arm; I ran neither before the push.
- `nightly-status`: red on main, not reached by this diff.

## Forward-carry

R9-WEB-2 (the Pages workflow): `npm ci` in `tools/site/`, `node tools/site/build_docs.mjs --root . --tree <(git ls-files) --out _site/`, and the installed mermaid package's minified UMD file from its dist directory into `_site/site/mermaid/`. Destination: the R9-WEB-2 group's brief in the round-9 roster on the audit-r9-fixplan handoff branch, which only the orchestrator can edit; `/tools/site/` is already owned.

## Friction

gate-scoping: contradiction: `entities.py` refuses an unclassified `tools/` file, and `INERT` for one outside `tools/audit/`, before CI can record, so a seat must hand-record first.
gate-scoping: unenforced: closures-autofix printed `skip-not-under-scoped` and then `skip-failed-recording` for one file read; neither names the next step.

## Approval

tvofi's approving review is owed: `tests/layout.json`, `tests/closures.json`, `tests/closure.py` and `.github/CODEOWNERS` are code-owned. No budget is raised.
