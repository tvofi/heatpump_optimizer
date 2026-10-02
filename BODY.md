_Requested by **tvofi**_

Part of #1798

Before: the reader documents are readable only as markdown on GitHub, and the product page's documentation cards link there. After: `tools/site/build_docs.mjs` renders the README and every row of the README Documentation table (less its EXCLUDE list, today `docs/backlog.md`) into one page each, in the product page's design, over the markdown-it 14.1.0 the repository vendors at `.claude/workflows/vendor/` (the path `render_md.mjs` requires; no parser added). It keeps GitHub's heading slugs, turns a link to a published document into its page and a link to another tracked file into a GitHub link, renders badges and any third-party image as their words, and writes only into the directory it is given: nothing it makes is tracked (S7). The stylesheet is `docs/site/docs.css`, beside the fonts. `tools/site/package.json` and `package-lock.json` pin mermaid 12.1.0 for the deploy only; tests never install it. The product page's documentation cards, its card and setup links, its Reference link and its footer now point at the sub-pages; the archive row keeps its GitHub link and the product-page card keeps `#top`.

`tests/doc_claims.py` gains four things: the build arm (`check_docs_subpages`: the build runs over the working tree into a temporary directory with `git ls-files`, and every `FAIL` line fails the arm; zero pages built is red, and so is a build that dies without a FAIL line); the sub-page rule on the page arm (a link to a page the build does not produce is refused, and a docs card for a built document must link its page); the third-party rule R9-WEB-1's review carried here (a `<link rel=icon>`, a `<link rel=preload>` and an `<iframe>` from another origin are refused on the product page, and every request kind on every built page); and the mermaid pin check (one exact version that the lockfile resolves). Each rule has a planted control inside the arm. Classification: `tools/site/**` is one glob in the tools category of `tests/layout.json`; `tests/closures.json` carries the build, `package.json` and the lock in `doc_claims.py`'s closure and the lock in `entities.py`'s (Mac recordings, additive; CI's Linux recording supersedes them). `.github/CODEOWNERS` gains `/tools/site/ @tvofi`, so R9-WEB-2's workflow, which executes the generator, need not edit it. No `custom_components` file, golden, `VERSION`, version literal or `tests/README.md` line is touched; no docs defect was found (the build is green over the reader docs at the merge base).

## Head

a9440930d4e5da7703190c616083341a06f3a062

## Mutation proof

`tests/mutation_table.py --scope changed` draws nothing (no `custom_components` line changed), so the sites this change adds were mutated by hand on in-memory copies at the head, each run against the planted controls.
- `tools/site/build_docs.mjs`: all 10 `errors.push(` sites, each turned into `void (`, then the 12 planted-tree controls run. 8 of 10 are killed (a control prints `MISS`). Two survive, triaged: the duplicate-page-name site (the same collision also fails 14 dead anchors, because one page overwrites the other's heading set, so the build stays red without that message), and the `zero pages built` site (unreachable by construction: the README is always a document, and a missing README throws before it; the live anchor is the arm's, red in the first-run table below).
- `tests/doc_claims.py`: the 31 added predicate and append lines, each neutralised (`if False:`, `pass`, an emptied list), run against the arm's in-tree controls and two planted trees through `docs_build`. 30 of 31 are killed. The survivor is `if kind == "third-party":` in the control loop itself: a mutant of the test, not of a predicate (its built-page branch is also exercised by the script and image plants, which are killed). A first pass left 16 survivors on the same sites; the controls added since are what killed them.

## Null control

Failing test first at `1998fc5686a2ee7ad62c1b54d01b0d9423cf7a38` (the arm alone, no generator): `FAIL the build exists and built at least one page (anchor)  [tools/site/build_docs.mjs does not exist]`, `FAIL every README Documentation row but the archive is a built page`, 4 of 126 checks FAILED (output in `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/red-before-generator.txt`).

At the head, the design's `docs_controls.py` cases, ported to the repository paths and run against the tracked tree (`/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/docs_controls.py`), baseline `exit 0, 0 FAIL line(s)`:

| planted error | build result |
|---|---|
| cross-page anchor to a missing heading | RED, `anchor #no-such-heading is not a heading of configuration.html` |
| same-page anchor to a missing heading | RED, `... of setup.html` |
| image not in the tree | RED, `image setup/01-first-screens.png does not resolve under docs/` |
| relative link to an untracked file | RED, `link to ../tools/nope.py ... which is not tracked` |
| README row for a file that does not exist | RED, `README Documentation row docs/new-page.md names a file that does not exist` |
| EXCLUDE entry the README no longer lists (renamed file exists) | RED, `EXCLUDE names docs/backlog.md, which the README Documentation table no longer lists` |
| heading renamed under an inbound link | RED, `anchor #services is not a heading of configuration.html` |
| README without its Documentation table | RED, `ANCHOR: no rows found in the README Documentation table` |
| raw HTML third-party image | RED, `raw HTML requests a third-party resource` |
| two documents with one page name | RED, `two documents would be built to one page name` |
| stylesheet not tracked | RED, `docs/site/docs.css is not tracked` |
| README row naming a missing product-page file | RED, `link to docs/gone.html ... which is not tracked` |

Inside the arm (`check_site_request_controls`, `check_docs_build_controls`, the pin controls): a third-party icon, preload font and iframe are each refused on the product page and on a built page; a third-party script and image on a built page; a link to `tuning.html`; a docs card linked to GitHub; a minimal tree with a dead anchor; a tree with no README (a build exit with no FAIL line); a tree outside git; a missing build script; a mermaid range and a lockfile that disagrees. Each is a green check because the rule fired; the unplanted baselines and a same-origin icon (the rule is not over-broad) are green the other way.

## Figures

Rules: counts are what the named instrument prints at the head `a9440930d4e5da7703190c616083341a06f3a062` (merged with `origin/main` tip `1abfef56d081146d7a38828047d790a23ffcac27`, `2026-10-02T20:33Z`), in the Python 3.14.7 venv `/Users/timmalmstrom/hpo-seats/R9-F11.4-venv` (numpy, scipy), `PYTHONPATH=tests/hastub` as the lesson says.
- `node tools/site/build_docs.mjs --root . --tree <(git ls-files) --out DIR`: `pages 9, pageLinks 51, anchors 39, githubLinks 19, images 21, badges 4, external 17, mermaid 8`, `RESULT: PASS`. Pages: readme, how-it-works, configuration, setup, dashboard-card, automations, architecture, ecl110, disclaimer; excluded `docs/backlog.md`. `pages` 9, `pageLinks` 51, `anchors` 39 and `mermaid` 8 equal the design's measure at `aac8fb77`; `githubLinks` 19 (design 20) and `images` 21 (design 20) differ because the docs changed since.
- `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/docs_controls.py .` (sha1 prefix `211e96e0f9cc`): `baseline: exit 0, 0 FAIL line(s)`, 12 lines starting `RED`, `RESULT: every control red, baseline green`; a control that measured nothing prints `MISS`.
- `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/mutate_build.py .` (sha1 prefix `5cf926785c5e`): `10 errors.push sites`, 8 lines `KILLED`, 2 `SURVIVED`. `/Users/timmalmstrom/hpo-seats/R9-WEB-3/scratch/mutate_arm.py .` (sha1 prefix `ed23ecb1fa2d`, which calls `arm_driver.py`, `3da12e5b7ed3`): `31 mutable lines among 245 added lines`, `SURVIVORS: 3` on the pass before the last commit and `SURVIVORS: 1` after the two mermaid-pin survivors were killed by the range control (re-run singly: both `in_tree_failures=1`).
- `PYTHONPATH=tests/hastub:tests:custom_components python tests/doc_claims.py`: `ALL 147 checks PASSED` (`ALL 121 checks PASSED` for the same script at the merge base's `origin/main`, run from a `git archive` of it).
- `python tests/entities.py`: `ALL 2074 ENTITY CHECKS PASSED`; `python tests/harness_headers.py`: `ALL 94 HARNESS HEADER CHECKS PASSED`; `python tests/deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `python tests/layout.py`: `layout self-test: ok`; `node tests/md_tables.mjs`: `doc_swallowed_prose_lines=0`, `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no metric measures `tools/site` or `docs/`; no budget touched); `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 3 script(s) run, 25 scoped out`, running `tests/doc_claims.py`, `tests/entities.py`, `tests/layout.py`; all three are the runs above. An earlier select printed `MODE: FULL` because `tools/site/package.json` and the lock were unmeasured; the lock is now in `entities.py`'s and `doc_claims.py`'s closures and `package.json` in `doc_claims.py`'s.
- Rendering on the generator as first built (the later commits only added controls, a lockfile entry and removed one redundant check), in a browser served from a staging of the built pages beside `docs/` with the lockfile's `mermaid.min.js` at `site/mermaid/`: readme 3 of 3 diagrams drawn, how-it-works 2 of 2, architecture 1 of 1, configuration 2 of 2, setup 0 of 0 (8 of 8 in all, equal to the build's `mermaid 8`), every image loading once scrolled into view (they are `loading="lazy"`), no horizontal overflow on any of the five pages measured.
- `./tests/derive_closures.sh --single tests/doc_claims.py` (venv, Darwin): `tests/doc_claims.py 136 files`, additive only (`tools/site/build_docs.mjs`, `package.json`, `package-lock.json`). The same for `tests/entities.py` proposed to drop `tests/golden/card_claimed_drift.txt`, the `inert_reads` entry for `LICENSE` and to flip `rc` to 1 (the tree had an unclassified `package-lock.json` while recording), so only its one added line was kept by hand, and CI's Linux recording is the check. Left to CI: `closures`, `stress.py`, the mutation autofix, `features.py`, `optimality.py`.
- `git diff --stat origin/main...HEAD` (three-dot): 9 files, `tests/closure.py` not among them.

## Red checks

none yet at this head; before the push, local only: `tests/entities.py` read `these force the FULL suite when touched: tools/site/build_docs.mjs` until the closure recorded it, then `narrowing INERT leaves every non-audit tools/ file in the must-classify set` when I first made `tools/site/package.json` INERT on the `tests/pwlane/package.json` precedent. Cause: entities.py had not been run after the classification choice. Cheaper detector: that command, already in the lesson list; the answer was the arm reading `package.json` (the exact-pin check) instead of an INERT entry.

## Forward-carry

R9-WEB-2 (the Pages workflow): it must run `npm ci` in `tools/site/`, run `node tools/site/build_docs.mjs --root . --tree <(git ls-files) --out _site/` (the pages and the product page land together; `site/docs.css`, `site/fonts/` and the staged images already sit beside `docs/index.html`), and copy the installed mermaid package's minified UMD file from its dist directory to `_site/site/mermaid/`; pages load it from that path and only on the four pages that draw a diagram. `/tools/site/` is already owned in `.github/CODEOWNERS`, so that PR need not edit it. Destination: the R9-WEB-2 group's brief in the round-9 roster on the audit-r9-fixplan handoff branch, which already names these steps in the design's "Hosting change" and which only the orchestrator can edit; this PR needs no roster change, and I name the destination rather than a path because the roster is not in this tree.

## Friction

gate-scoping: contradiction: the brief says to classify with one `tests/layout.json` glob and let the autofix record the closure, but `tests/entities.py` refuses an unclassified `tools/` file (and refuses `INERT` for one outside `tools/audit/`) before CI can record, so a seat must hand-record `doc_claims.py` and `entities.py` first or run FULL.
gate-scoping: unenforced: `derive_closures.sh --single tests/entities.py` on Darwin proposes dropping a closure file and an `inert_reads` entry and flips `rc`; nothing refuses a lossy Darwin record except reading its "would drop" line.

## Approval

tvofi's approving review is owed: `tests/layout.json`, `tests/closures.json` and `.github/CODEOWNERS` are code-owned. No budget is raised.
