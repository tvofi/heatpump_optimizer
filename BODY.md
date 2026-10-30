README graphics in the Home Assistant Marketplace (R10-README-GRAPHICS, owner request tvofi 2026-10-30). Architect note: handoff-body/r10-readme-graphics 2e536d1396486ba55eb798039bc0412086b26b2f (approved: handoff-body/r10-readme-graphics-drev 9e3073142).

The Marketplace's markdown worker (marked, then js-xss) blanks every `src`/`href` that is not absolute, `#`, `/`, `./` or `../`, before its URL rewriter runs, and has no mermaid. So the banner, the coffee button, the card chart, the how-it-works figure and all 28 document links were broken, and the three mermaid fences showed as raw code. The fix: every repository-relative README target gains `./`; `docs/img/readme/how-it-works.png` becomes a `<picture>` with its existing `-dark.png` (orchestrator ruling under mandate 6329234399); each mermaid block gets a `<picture>` of committed 2x PNGs (light `<img>`, dark `<source media="(prefers-color-scheme: dark)">`) directly above its now-closed `<details>`; a `tests/doc_claims.py` arm keeps both true. Dark mode is in scope by tvofi's ruling of 2026-10-30 ("dark mode should absolutely not be scoped out"), relayed by the orchestrator, who also relayed the approval of the code-owned tools/site/ head under mandate 6329234399. Only a stamped tag shows the fix, and only to users who install or update to it: an installed v7.1.0 keeps the broken page, and any stamp after this merge carries it, not specifically v10.0.0.

Landed from the note's carries here, not carried: P1/P4 (the harness and the product-page check, both in the diff), P5 (the manifest records both hashes per figure and the arm refuses a mismatch of either; regenerate-then-green shown under Mutation proof), P6 (the generator header states the install: `npm ci --prefix tools/site`, `npm ci --prefix tests/pwlane` with `playwright install chromium`, `NODE_PATH`, `MERMAID_JS`, `HPO_CHROMIUM`), the `<picture>` dark sources (by tvofi's ruling). Other readers of README relative targets adjusted in the diff: tests/entities.py's hero-image regexp (now `./docs/img/card/card-plan-chart.png`), tests/doc_claims.py's coffee-button tracked-file check (strips `./`) and the two Documentation-row sets (normalised).

Closes: none (owner request; roster group R10-README-GRAPHICS, no issue).

## Head

17ee47eef93a682ba9c08489c03048441a6c58bf

## Mutation proof

Production line mutated, `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`, restored after each:
- README.md at the merge base (`git show cc930cdd1:README.md`): FAIL `README.md has no bare-relative target and each mermaid block has its current figure above a closed <details>` (17 distinct bare targets named), plus the four red-case checks whose planted edit no longer differs. 5 of 219 FAILED.
- One link `(./docs/ecl110.md)` to `(docs/ecl110.md)`: FAIL on the same check, naming `docs/ecl110.md`. 1 of 219.
- `flowchart LR` to `flowchart RL` in the first block, nothing regenerated: FAIL on the same check, `mermaid block 1: its text differs`. 1 of 219.
- tools/site/build_docs.mjs, `path.posix.normalize(m[1])` back to `m[1]`: FAIL `every README Documentation row is a built page` and `product page: a docs card for a built document linked to GitHub is refused`. 2 of 219.
- A `<source>` removed from one picture (light-only): FAIL the same check, `no <picture> of ./...setup-flow.png with the dark source ...`, plus the built-page check and two red-case checks. 4 of 228.
- Dark srcset `./` removed: FAIL the same check naming `docs/img/readme/mermaid-one-interval-dark.png` as bare-relative. 1 of 228.
- A dark PNG replaced by the light one: FAIL `mermaid block 3: ...-dark.png differs from the PNG the manifest recorded`. 1 of 228.
- tools/site/build_docs.mjs, `return rawImages(tokens[idx].content)` back to `return tokens[idx].content`: FAIL `the built readme page resolves every <picture> srcset and src to its docs/-relative image, none left ./-prefixed`. 1 of 228.
- The how-it-works source removed (light-only): FAIL the same check, `no <picture> of ./docs/img/readme/how-it-works.png with the dark source ...`. 2 of 228 (the second is its own red-case check reading the mutated README). Planted-red controls added: the how-it-works figure light-only, and its dark PNG missing.
- Passes when fixed: the same block edit followed by `node docs/img/readme/render_mermaid.mjs` (mermaid 12.2.0, playwright 1.64.1): ALL 228 PASSED, then restored.
Planted-red controls in the arm itself (each a `red case:` check): a light-only figure, a dark source pointing at the light PNG, a bare-relative dark srcset, a manifest figure with no dark variant, a dark PNG hash differing, a dark PNG missing, block one-character edit, `./` removed from an image and from a link, a bare `<img src>`, a bare `<source srcset>`, a bare reference definition, the figure line deleted, an open `<details>`, a PNG hash differing, a PNG missing, a manifest entry with no block, no manifest. Green null: the unchanged tree.

## Null control

Finder's harness, a replica of the Marketplace pipeline (marked 15.0.4 + xss 1.0.15 under the worker's allow-list, rewrite rule of `rewrite-html-urls.ts`; not the shipped bundle): `HPO_PIPELINE_MODULES=<node_modules> node dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs --readme <file>`.
- Base (`git show cc930cdd1:README.md`): relative_images=4 resolved=0; relative_links=28 resolved=0; rc=1 (red).
- Head 17ee47eef93a682ba9c08489c03048441a6c58bf: relative_images=7 resolved=7; relative_links=28 resolved=28; picture_sources=4 resolved=4; rc=0 (green). The 7 are the 4 original images and the 3 light mermaid `<img>`s; the 4 sources are the three mermaid figures and how-it-works.
- Base: picture_sources=0 resolved=0. A README whose only source has a bare srcset (`docs/d.png`): picture_sources=1 resolved=0, rc=1.
- Picture handling in the replica (srcset survives only if every candidate passes xss's test, markdown-worker.ts:21-43; the rewriter resolves source[srcset], rewrite-html-urls.ts:29-56): `RESULT control srcset_bare=stripped srcset_dot=kept light_img=ok` at base and head. So in the Marketplace a `./` dark source is kept and resolves to the pinned ref's raw URL; a bare one is dropped while the light `<img>` of the same picture still renders. The browser picks the source by the OS/browser `prefers-color-scheme`, not by Home Assistant's own theme setting; so an HA in a theme that differs from the OS shows the OS-chosen PNG on the HA background (opaque PNGs, both read acceptably).
- GitHub keeps the picture: `gh api -X POST markdown` with `context=tvofi/heatpump_optimizer` on the README's exact `<picture>` form returns it wrapped in `<themed-picture>` with source and srcset unchanged (`./` paths), which is GitHub's own theme switch. Not a screenshot.
- Null control, an absolute-URL image, at both ends: absolute_images=5 resolved=5 on the base and on the head, and a one-line absolute-only README resolves 1 of 1, rc=0. The harness's own controls read `bare=blank dot=ok absolute=ok` at both ends, so it can go red.
- mermaid_fences=3 plain_code=3 at both ends: fences stay raw code in the Marketplace, which is why the PNGs exist.

## Figures

- Relative targets prefixed: `grep -o '](\./' README.md | wc -l` prints 35 at the head and 0 on the base (`git show cc930cdd1:README.md | grep -o '](\./' | wc -l`): 28 links, 4 images, 3 new figures; a bare target left: `grep -n -E '\]\(' README.md | grep -v -E '\]\((https?:|#|mailto|\./)'` prints nothing.
- Figure sizes: `file docs/img/readme/mermaid-*.png`: light and dark, each 2296x806, 2296x1434, 2296x5986 (the setup flow is tall; 1100 CSS px container at 2x, inside the Marketplace's ~1150 px).
- GitHub still renders: `gh api -X POST markdown` with `context=tvofi/heatpump_optimizer` on `![b](./docs/img/readme/banner.png)` and `[c](./docs/setup.md)` returns them with the `./` path unchanged; the browser resolves it against the README's URL exactly as it resolves the bare path. This is the API's rendering, not a screenshot of the repository page.
- Dark variant: mermaid `dark` theme on docs/site/docs.css's dark `--bg` (#0b1a28), opaque RGB, read back for the sequence diagram and the setup flow. PNG bytes are not reproducible across runs (the light setup-flow PNG re-rendered with different bytes in this session), which is why the arm compares source and file hashes recorded together, not a re-render.
- Product page: `tests/doc_claims.py` builds the docs through tools/site/build_docs.mjs; the build exits 0 with no FAIL line and every Documentation row is a built page. build_docs.mjs resolved `./` in links and images but read the Documentation table's row targets verbatim, so the `./` rows were not matched: one line, `src: path.posix.normalize(m[1])`. tools/site/ stays code-owned (`.github/CODEOWNERS`: `/tools/site/ @tvofi`, and `/tests/closure.py @tvofi`), so the head still merges only on tvofi's approving review; the orchestrator relayed the approval, which is not a review. The second change there is `rawImages` in the raw-HTML rules: the page is served from docs/, so a raw `<img src>`/`<source srcset>` naming `./docs/img/...` would break on the product page; it resolves each candidate as the image rule does (or errors, naming the file). Checked: the built readme page carries `srcset="img/readme/mermaid-...-dark.png"` three times and no `./docs/`. The `<picture>` there follows the OS color scheme, not the site's own theme toggle.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, reason `tests/closure.py changes the gate itself`. The brief requires the closure.py classification, so CI runs the full suite; I ran the doc_claims.py arm (228 checks pass) and `python3 tests/structure.py` (passes) locally.
- Closure record: `tests/derive_closures.sh --single tests/doc_claims.py` (Darwin, `--single` per gate-scoping.md): 175 files at the base to 183 at the head (manifest, three light and three dark mermaid PNGs, how-it-works-dark.png), plus `tools/pr/ci_predict.py --apply-inert` for harness_headers.py's INERT READS of the new harness.

## Red checks

The D6 claims register (`dev/audit/rounds/round4/D6/claims.json`, `claims.md`) is regenerated and committed: C108 84 to 83 links, C110 22 to 21 images, because the how-it-works figure is now a `<picture>` and no longer a markdown image. Regenerated by `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round4/D6/claims.py`; `tools/pr/prepr.sh` step 6g agrees.


none yet at this head (CI not run). Local only: `tests/harness_headers.py` rewrites `dev/audit/rounds/round4/D6/claims.json` and `claims.md` when run (the known churn, gate-scoping.md); restored, not committed.

## Unpinned sites

- tools/site/build_docs.mjs, `path.posix.normalize(m[1])`: tools/ site, outside mutation-autofix's `custom_components/` lane. Disposition: a value check. The mutation above (reverting it) turns `every README Documentation row is a built page` red.
- docs/img/readme/render_mermaid.mjs: a generator under docs/, executed only by a seat with a browser; its output is pinned by the arm (block hash and PNG hash), and the regenerate-then-green run above is its demonstration.

## Forward-carry

- Real HA 2026.11 instance (the note's P2): not reachable from this seat; the replica transcribes the pipeline and is not the bundle. Carry: R10-CATALOG-PR in `dev/programme/rosters/wave-r10-groups.json` (owner step: a screenshot of the Marketplace repository page at the first stamped tag after this merge).
- Figures compared to what they depict (P3): the manifest binds each PNG to its block's text hash; nothing compares the drawn picture to the diagram semantically. Carry: R10-ARCH-DOCS (the P40 check).
- Product page (P7): each README diagram appears as the static `<picture>` plus the live mermaid inside a closed `<details>` (summary ends `(diagram source)`); the build passes and I did not screenshot it. The picture follows the OS color scheme, not the site's own theme toggle. Carry: R10-ARCH-DOCS (verify the built page reads acceptably).
- Group ordering: add R10-README-GRAPHICS to the `after` lists of R10-ARCH-DOCS and R10-CATALOG-PR (the note's routed decision). Carry: R10-ARCH-DOCS.

## Friction

none.
