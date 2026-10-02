_Requested by **tvofi**_

Part of #1798

Before: no product page. After: `docs/index.html`, the page tvofi asked for on 2026-09-30, ported from the design of record, with its self-hosted fonts under `docs/site/fonts/`; a new arm in `tests/doc_claims.py` (`check_product_page`) pins every claim on it to the README or a reader doc (a `data-src` heading anchor, verbatim or key-phrase), refuses a stray digit, a version, a dead link or image and any third-party request, and holds both directions of the README's "What it does" leads and Documentation table; the README links the page (a Product page row and a line under the badges, pointing at the file until R9-WEB-2). No savings figure, no version, no `custom_components` file, no golden touched. Classification: `docs/index.html` and `DISCLAIMER.md` on `INERT_EXCEPT` (the arm opens both), `docs/site/**` and `docs/index.html` in the layout manifest's docs category, `tests/closures.json` carries the two-path closure of `doc_claims.py` and moves `DISCLAIMER.md` from `harness_headers.py`'s `inert_reads` into its closure.

Against the design page: the hero is the README hero `docs/img/card-plan-chart.png` as one image; the Advisor slot shows `docs/img/card/advisor-{light,dark}.png` and quotes the rewritten section; the documentation cards link to the sources on GitHub, since R9-WEB-3's sub-pages do not exist yet.

## Head

699c4996ee77eb30b614b9ea315e85081696da1f

## Mutation proof

`tests/mutation_table.py --scope changed` draws nothing (no production line changed), so the arm's predicates were mutated by hand: 21 predicate lines in `site_findings`, each turned into `if False:` or an empty comprehension in an in-memory copy, then the planted-error controls run on the mutant. 21 of 21 mutants make a control print MISS; the unmutated run prints `every control red, baseline green`.

## Null control

Failing test first at `0e6b4391e09ad1c754004c3a0c84710657b25914`: the arm printed `FAIL docs/index.html exists with claims, features and docs rows (anchor)  [docs/index.html is absent]`. At the head, 24 planted errors are RED with a 0-finding baseline: a wrong tile number, a reworded quote, a dead slug, a key phrase absent from its section, a README sentence changed under an unchanged page, a dropped feature, an extra feature, an extra docs card, the Product page card removed, a digit outside a claim, a version literal, the stamped VERSION, an image missing from the tree, a `src` that is not its `data-repo` path, missing alt text, a link to a missing file and to a missing heading, an external script, a third-party stylesheet, a third-party font `url()`, a CSS file not in the tree, a third-party image, zero claims, no page.

## Figures

Rules: counts are what the named instrument prints at the head `699c4996ee77eb30b614b9ea315e85081696da1f`, in a Python 3.14.7 venv at `/Users/timmalmstrom/hpo-seats/R9-WEB-1-scratch/v` (numpy 2.5.3, scipy 1.18.1, aiohttp 3.14.3, PyYAML 6.0.3, voluptuous 0.16.0, yarl 1.25.1; installs approved by tvofi).
- `PYTHONPATH=tests/hastub python /Users/timmalmstrom/hpo-seats/R9-WEB-1-scratch/controls.py` (sha1 prefix `da92737b765e`): `baseline: 0 finding(s)`, 24 lines starting `RED`, `RESULT: every control red, baseline green`; a control that measured nothing prints `MISS`.
- `bash /Users/timmalmstrom/hpo-seats/R9-WEB-1-scratch/mutate.sh` (sha1 prefix `ea6a23f9509b`): 21 `MUTANT` lines, 21 ending `A CONTROL DID NOT MEASURE`.
- `PYTHONPATH=tests/hastub:tests:custom_components python tests/doc_claims.py`: `ALL 121 checks PASSED` (112 at the merge base).
- `PYTHONPATH=tests/hastub python tests/entities.py`: `ALL 2060 ENTITY CHECKS PASSED`.
- `python tools/audit/merge_fastpath.py --self-test`: `33 checks, 0 failed`.
- `node .claude/workflows/brief_lint.mjs`: `TOTAL: 0 error(s) across 45 file(s)`.
- `./tests/derive_closures.sh --single tests/doc_claims.py` (same venv): `tests/doc_claims.py 132 files`, adding `DISCLAIMER.md` and `docs/index.html`. The same command for `tests/harness_headers.py` was run and discarded: Darwin recording does not see that script's child processes, and it would have dropped 132 listed files and the whole `inert_reads` entry, so its two-line change (the `DISCLAIMER.md` entry moves from `inert_reads` into the closure) is made by hand and CI's strace recording is the check.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `node .claude/workflows/policy_lint.mjs --pr-body` of this body: 0 errors. Left to CI: `closures`, `stress.py`, the mutation autofix, `features.py`, `optimality.py`.

## Red checks

Each check red at an earlier head of this PR, and what answers it:
- `briefs` (round 1): the arm sat above `check_simulate_plan_fields` and moved two `path:line` pins in `carry-1645.json`. Cause: `brief_lint.mjs` not run before the push; cheaper detector: that command. Fixed: the arm sits before `main()` and the five pins moved by the docstring's five lines.
- `closures` (round 1, `INERT READS UNDER-APPROXIMATED`): the arm opens `DISCLAIMER.md`, which was INERT; closures-autofix skips this shape. Fixed by `DISCLAIMER.md` on `INERT_EXCEPT` and the `doc_claims.py` re-derive.
- `closures` (round 2, `UNDER-SCOPED tests/harness_headers.py: DISCLAIMER.md`): the same reclassification turns the read `harness_headers.py` makes through `claims.py` into a closure read, and I re-derived only the script I had changed. Fixed by the two-line edit above. Cheaper detector: grep every reader of a file when it leaves INERT, and read the `closures` job's log, which names the script; no standing check is proposed.
- `instrument-self-tests` (round 3): `tools/audit/merge_fastpath.py`'s probes used `DISCLAIMER.md` as an inert file; they now name `SECURITY.md`. Its real-tree check now names `LICENSE`, which `harness_headers.py` still reads as INERT (`33 checks, 0 failed`). `tests/entities.py`'s docs-only example and `tests/run.sh`'s comment moved off `DISCLAIMER.md` the same way.
- Live ruleset drift against `required-contexts.json` (`policy_lint`, the template arm): not this diff; cleared by main's #1849.

## Forward-carry

none. A later move of `docs/img/**` or `docs/setup/**` must edit the page's `src` and `data-repo` together, and the arm turns red in that PR if it does not. R9-WEB-3 already carries the sub-page switch.

## Friction

gate-scoping: contradiction: the R9-WEB-1 roster brief says to put `docs/site/` on `INERT_EXCEPT`, but that list matches exact paths and the recorder traces `openat` only, so files the arm merely stats (fonts, images) stay INERT; only the two files it opens went on the list.
gate-scoping: unclear: `tests/layout.py`'s `glob_re` escapes a `{a,b}` alternative literally, so the brief's one category glob became two.
gate-scoping: unenforced: `derive_closures.sh --single` on Darwin cannot see a script's child processes, so for `tests/harness_headers.py` it proposes dropping 132 files and an `inert_reads` entry; nothing refuses a lossy Darwin record except the human reading its "would drop" line.

## Approval

tvofi's approving review is owed: `tests/closure.py`, `tests/layout.json` and `tests/entities.py` are code-owned.
