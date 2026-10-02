_Requested by **tvofi**_

Part of #1798

Before: the project had a README and reader documents and no product page. After: `docs/index.html` is the page tvofi asked for on 2026-09-30 ("a full product web page, based on the user facing documentation in the repo, in the same design language as the showcase page"), ported from the design of record, and `tests/doc_claims.py` gains one arm that pins it to the master documentation (test-pinned and linked). Every sentence of fact on the page is quoted from the README or a reader doc and carries a source anchor; a test refuses drift; the README links the page (a Product page row in its Documentation table and one line under the badges, pointing at the file until R9-WEB-2 serves it). The page states no savings percentage (S3) and no version (rule 4). No Python module under `custom_components` is touched, so every value-bearing golden is byte-identical and `tests/golden/*claimed_drift.txt` is untouched.

What the port changed against the design page, because main moved after it was written:
- The hero is the README hero `docs/img/card-plan-chart.png` that R9-UI-4 regenerated (one `<img>`, the design's 375 px sources and design note are gone); the how-it-works figure is the pair R9-UI-2 landed under `docs/img/readme/`.
- The Advisor gallery slot now shows `docs/img/card/advisor-{light,dark}.png` and quotes the current "The advisor page" opening: R9-UX-2 rewrote that section, and the design's caption was no longer in it (the arm went red on exactly that, which is its job).
- The documentation cards, the card and setup links and the footer link to the sources on GitHub, not to `*.html` sub-pages. The sub-pages are R9-WEB-3 (rev 4.3) and do not exist at this point, so a sub-page link would be a dead link; WEB-3 switches them and adds the sub-page rule to this arm.
- A `docs/index.html` card was added to the page's docs section, because the arm requires the page's docs set to equal the README Documentation table.

## Head

a46a91c88f282b567bf78b4899e3dff92defe5aa

## Mutation proof

`PATH=<venv>:$PATH PYTHONPATH=tests/hastub python tests/mutation_table.py --scope changed --base origin/main --max 5` reports `scope changed: no production code line added or modified against the base` (the diff touches no `custom_components` file), so the table has nothing to draw. The arm is test code, so its predicates were mutated by hand: each of 21 predicate lines in `site_findings` replaced by `if False:` / an empty comprehension in an in-memory copy (the tree is untouched), then the planted-error controls below run against the mutant. Instrument: `bash mutate.sh` over `controls.py` (both in the seat scratch, sha1 `ea6a23f9509b` and `da92737b765e`; run from the worktree root). Result: 21 of 21 mutants make at least one control print MISS (the run prints `A CONTROL DID NOT MEASURE`), and the unmutated run prints `every control red, baseline green`. Mutated sites: the verbatim fragment test, the number test of a key-phrase claim, the key-phrase test, the digit-outside-a-claim test, the image `src` vs `data-repo` test, the image-in-tree test, the alt-text test, the third-party image test, both directions of the feature set difference, both directions of the docs-row set difference, the stamped-version test, the version-literal scan, the external-script test, the stylesheet test, the CSS absolute-URL branch, the CSS not-in-tree branch, the zero-claims/features/docs anchor, the repository-link heading test and the repository-link path test.

Two survivors in a first pass were real and are why the control table has what it has: the CSS absolute-URL branch and the image-in-tree test were each masked by a neighbouring branch reporting the same kind, so those controls now require the message of the branch under test, and a control was added for a page feature the README does not lead with and for a key phrase absent from its section.

## Null control

Failing test first, at `0e6b4391e09ad1c754004c3a0c84710657b25914` (arm only, no page): `PYTHONPATH=tests/hastub:tests:custom_components python tests/doc_claims.py` prints `FAIL docs/index.html exists with claims, features and docs rows (anchor)  [docs/index.html is absent]` with `claims 0, ... docs 0`. At the head the same line is `ok` with `claims 47, fragments 110, numbers 3, copy 14, features 9, docs 10, images 11, links 16`.

Planted errors at the head, `HPO_REPO unset, python controls.py` (baseline: 0 findings; 24 controls, every one RED):

| planted error | kind | red with |
|---|---|---|
| a wrong number in a tile (20 -> 48) | claim | number 48 is not stated in the section |
| a reworded quote ("up to 20 hours" -> 48) | claim | not in the section |
| a dead heading slug | claim | no heading with slug |
| a key phrase absent from its section | claim | key phrase not in section |
| a README sentence changed under an unchanged page (README says 12 hours) | claim | key phrase not in section |
| a dropped feature heading | feature | README lead missing from the page |
| a page feature the README does not lead with | feature | does not lead with |
| an extra docs card | docs | the Documentation table does not list it |
| the new Product page card removed | docs | README row missing from the page |
| a number outside any claim | number | a number outside any claim |
| a version literal (v6.7.12) | version | a version literal on the page |
| the stamped VERSION on the page | version | the page states the version |
| a data-repo image not in the tree (src and data-repo agreeing) | image | not in the tree |
| a src that is not the data-repo path under docs/ | image | not the path under docs/ |
| an image without alt text | image | image without alt text |
| a repository link to a missing file | link | not in the tree |
| a repository link to a missing heading | link | no such heading |
| an external script | third-party | external script |
| a third-party stylesheet | third-party | stylesheet |
| a font `url()` to a third party | third-party | third-party resource in CSS |
| a font `url()` to a file not in the tree | third-party | CSS resource not in the tree |
| a third-party image | third-party | third-party image |
| zero claims (every `data-src` renamed) | anchor | zero claims found |
| no page | anchor | docs/index.html is absent |

The doc-side control builds a root of symlinks to the real tree with only `README.md` replaced, so a red there proves the fact set is read from the working tree's documents and not carried in the arm.

## Figures

Rules: a count is what the named instrument prints at the head `a46a91c88f282b567bf78b4899e3dff92defe5aa` on a main-equivalent tree (`origin/main` was `2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d` at the merge base and at the head); the numeric arms of `doc_claims.py` and `entities.py` ran in a Python 3.14 venv with the CI pins' versions of numpy, scipy, aiohttp, pyyaml and voluptuous installed unhashed, because the Mac has no numpy of its own.
- `PYTHONPATH=tests/hastub python /Users/timmalmstrom/hpo-seats/R9-WEB-1-scratch/controls.py` (sha1 prefix `da92737b765e`, run from the worktree root): `baseline: 0 finding(s)`, 24 `RED` lines, `RESULT: every control red, baseline green`; the count is the lines starting `RED`, and a control that measured nothing prints `MISS` and turns the result line into `A CONTROL DID NOT MEASURE`.
- `bash /Users/timmalmstrom/hpo-seats/R9-WEB-1-scratch/mutate.sh` (sha1 prefix `ea6a23f9509b`): 21 `MUTANT` lines, 21 of them ending `A CONTROL DID NOT MEASURE`, 0 ending `every control red`; the unmutated control run above is its null.
- `PYTHONPATH=tests/hastub:tests:custom_components python tests/doc_claims.py`: the baseline at the merge base printed `ALL 112 checks PASSED`; at the head `ALL 121 checks PASSED` (the 9 new checks are the arm's anchor and its eight kinds).
- `PYTHONPATH=tests/hastub python tests/entities.py`: the baseline at the merge base printed `ALL 2060 ENTITY CHECKS PASSED`; at the head one check is red: `every tracked file is either measured or deliberately classified [these force the FULL suite when touched: docs/index.html]`. That is the `UNDER-SCOPED` state the brief predicts: `docs/index.html` is on `INERT_EXCEPT` and no recorded closure holds it yet. CI's closures-autofix records the `doc_claims.py` closure; it is not re-derived by hand (`gate-scoping.md`, no full `derive_closures.sh` off Linux). The other 2059 pass (the other red lines in that run are its own null-control self-tests, present at the baseline too).
- `node tests/md_tables.mjs`: three `RESULT ... =0 count` lines at the merge base and at the head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no metric measures `docs/` or `tests/`, no budget is touched. `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `python3 tests/layout.py`: report mode (R9-RO-9 flips it); `category` findings went from the 6 font files outside the allowed categories (with a brace-alternation glob, which `glob_re` escapes literally) to none for `docs/index.html` and `docs/site/**`; the `reference` arm now also lists the page's `data-repo` and link paths against the planned moves, which the RO lane must edit together with the pin (the pin requires each `src` to be its `data-repo` path under `docs/`).
- `python3 tests/harness_headers.py`: at the first head one check was red, `the executed harnesses leave their committed output byte-identical [uncommitted: tools/audit/round4/D6/claims.json, claims.md]`: `tools/audit/round4/D6/claims.py` counts relative links and the README gained two (91 to 93). The regenerated files are in the second commit (`fixer.md` step 10: run the generator); the rerun at the head prints `ALL 94 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL -- every test script runs, nothing is scoped out`, reason `tests/closure.py changes the gate itself`. It is the diff's own gate file (the brief requires the `INERT_EXCEPT` line), not an instruction to reproduce CI's full run; what ran here is the files that read what changed: `doc_claims.py`, `entities.py`, `md_tables.mjs`, `layout.py`, `harness_headers.py`, `structure.py`, `policy_lint.mjs`.
- The page loads in a browser: served from `docs/` over localhost, at 375 px wide `scrollWidth` equals `innerWidth` (no horizontal overflow), and all 9 `<img>` elements report `complete` with `naturalWidth` above 0 once lazy loading is forced; the four self-hosted font faces report `loaded` (68617 bytes of font files in all, no request leaves the host: the arm refuses one).
- `stress.py`, the mutation autofix and the closure re-record are left to CI. `features.py` and `optimality.py` were not run (no numeric surface touched; they need the Linux container, which is gone).

## Red checks

`tests/entities.py` "every tracked file is either measured or deliberately classified" (`UNDER-SCOPED` shape, named per `ci-autofix.md`): CI's closures-autofix records `doc_claims.py`'s closure with `docs/index.html`; this is answered by naming it.

## Forward-carry

none. The one constraint this puts on a later stage, that a move of `docs/img/**` or `docs/setup/**` must edit the page's `src` and `data-repo` together, is held by the new arm itself: a move that leaves either dangling turns `tests/doc_claims.py` red in that PR (the image-in-tree and `src`-is-the-`data-repo`-path controls above), so it needs no brief to be read first. R9-WEB-3 (rev 4.3) already carries the switch of the docs cards to sub-pages and the sub-page rule.

## Friction

gate-scoping: contradiction: the R9-WEB-1 roster brief says to put `docs/site/` on `INERT_EXCEPT`, but `closure.py`'s `is_inert` matches an exact path there (a trailing slash is not honoured) and the recorder traces `openat` only, so a file the arm merely stats (fonts, images) is not a read and listing it would create an orphan that forces the FULL suite; only `docs/index.html`, which the arm opens, went on the list.
gate-scoping: unclear: `tests/layout.py`'s `glob_re` escapes a `{a,b}` alternative literally, so `docs/{index.html,site/**}` matched only the first path; the brief's one category glob became two.

## Approval

tvofi's approving review is owed: `tests/closure.py` and `tests/layout.json` are code-owned.
