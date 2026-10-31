Fix review: blocked 42b228ec7e13ac30e49739d738dad374aa729da2 carry-missing: not carried to R10-CATALOG-PR (Marketplace screenshot at the first stamped tag) or R10-ARCH-DOCS (README mermaid figures against their blocks; product-page OS-versus-site-theme)

bus-nonce: bf5542271dd07163e2a190e2f8747034

Round 1. Reviewed head 42b228ec7e13ac30e49739d738dad374aa729da2 (code head 17ee47eef93a682ba9c08489c03048441a6c58bf), from a detached worktree at that head. Merge base 437f1ba9b. Contract: fix-review.md at origin/main a6e4a5afe; the roles diff since the merge base touches only standing-merge.md. The head was still the live PR head when I wrote this.

## Block

fix-review.md step 10 and finding-propagation.md. The body's `## Forward-carry` routes three findings to later stages. None of them is written on the roster at origin/handoff/audit-r10-roster f686aee59 (2026-10-30T23:10+01:00). Evidence: `ev/roster_carries.txt`.
- **P2, to R10-CATALOG-PR.** Owed: a screenshot of the Marketplace repository page on a real Home Assistant 2026.11 instance, at the first stamped tag after this merge. R10-CATALOG-PR's `carry` is `[]`. The orchestrator did add R10-README-GRAPHICS to its `after` list, but that orders the stages. It does not carry the control.
- **P3, to R10-ARCH-DOCS.** Owed: compare the six mermaid PNGs with the blocks they depict. R10-ARCH-DOCS's carries mention none of `mermaid-*.png`. Its P40 text covers the card figures, and that arm has since moved to R10-ARCH-DOCS-WIRING (the L4 split carry). The README figures are named nowhere on the roster except in this group's own `files`.
- **P7, to R10-ARCH-DOCS.** Owed: confirm the built product page reads acceptably, with the static `<picture>` following the OS colour scheme rather than the site's theme toggle, and the live mermaid inside the closed `<details>`. No such carry exists. The only theme carry on R10-ARCH-DOCS is #2609's coffee.svg one.

carry_audit's packet line ("R10-CATALOG-PR resolved on origin/handoff/audit-r10-roster") resolves the destination group, not the carry text. That is how it passed.
Repair: a `roster_edit.py` op writing the three carries, each stating its control as a precondition. It moves no code head. The rest of this review stands and would carry to a re-verdict at this head.

## Findings

- The body's `## Figures` line says `grep -o '](\./' README.md | wc -l` prints 35 at the head ("28 links, 4 images, 3 new figures"). It prints 31 at 42b228ec and at 17ee47eef, and 32 at the first commit 3d8a848fd. That is 28 links plus 3 markdown images (banner, coffee, card chart). How-it-works and the three mermaid figures are `<img src="./...">` inside `<picture>`, so the pattern does not count them: 4 `<img src="./` and 4 `srcset="./`. The quoted figure is false at every head of this PR. The fix is to correct the body to 31 and count the 4 `<img>` and 4 `<source>` separately. Evidence: `ev/targets.txt`. Carry: R10-README-GRAPHICS

## Evidence

- RESULT harness, base 437f1ba9b: relative_images=4 resolved=0, relative_links=28 resolved=0, absolute_images=5 resolved=5, picture_sources=0, mermaid_fences=3 plain_code=3, controls `bare=blank dot=ok absolute=ok` and `srcset_bare=stripped srcset_dot=kept light_img=ok`, rc=1 (red).
- RESULT harness, head 42b228ec: relative_images=7 resolved=7, relative_links=28 resolved=28, absolute_images=5 resolved=5, picture_sources=4 resolved=4, the same controls, rc=0 (green).
- RESULT null control: a one-line README with only an absolute-URL image gives absolute_images=1 resolved=1, rc=0. The harness ran with marked@15.0.4 and xss@1.0.15 installed in my own scratch directory (`ev/harness.txt`). Every body figure in Null control matches.
- About the harness: dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs is the fixer's rebuild of the finder's out-of-tree replica, as the architect note's P1 directs ("Rebuild it under dev/audit/harnesses/"). The body names it as a replica and not the bundle. I read it: the srcset rule, the safeAttrValue rule and the rewrite rule match the note's citations.
- RESULT doc_claims at head: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed ALL 228 checks PASSED, rc=0 (`ev/doc_claims_head.txt`). The product-page build ran inside it ("the build exits 0 with no FAIL line").
- RESULT mutation proof, mine, each restored afterwards. All 11 mutants were killed (`ev/mutations.txt`):

  | mutant | failed checks |
  |---|---|
  | how-it-works light-only | 2 |
  | setup-flow dark srcset pointing at the light PNG | 3 |
  | how-it-works-dark.png deleted | 2 |
  | mermaid-one-interval-dark.png deleted | 1 |
  | dark PNG replaced by the light one (manifest hash) | 1 |
  | `flowchart LR` changed to `RL` with nothing regenerated | 1 |
  | build_docs `rawImages` reverted | 1, "the built readme page resolves every <picture> srcset ... [4 srcset(s)]" |
  | build_docs `path.posix.normalize` reverted | 2 |
  | one `./docs/configuration.md` link made bare | 1 |
  | the `media=` attribute removed from a dark `<source>` | 1 |
  | the first figure's `<details>` reopened | 1 |

- Dark mode (in scope by tvofi's ruling) is met. All four `<picture>`s carry a light `<img src="./...">` and a `<source media="(prefers-color-scheme: dark)" srcset="./...-dark.png">`, and how-it-works is included. All six mermaid PNGs and both how-it-works PNGs exist and are tracked, at the dimensions the body states (`ev/png_sizes.txt`). I viewed mermaid-how-the-pieces-fit-dark.png: an opaque dark background with legible light labels.
- GitHub rendering: the POST markdown endpoint is not reachable from this cloud seat, because the session is scoped to the repository (`ev/github_markdown_api.txt`). The repository-scoped `GET repos/tvofi/heatpump_optimizer/readme?ref=42b228ec` with the html media type returns 4 `<themed-picture>` elements, each keeping its dark `<source>` (`ev/github_readme_api.txt`). This confirms GitHub still renders `<themed-picture>`, by the API rather than a screenshot. The body's markdown-API command itself I could not re-run.
- D6 register: re-running `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round4/D6/claims.py` at the head leaves claims.json and claims.md byte-identical, so the committed C108 (84 to 83) and C110 (22 to 21) are reproduced (`ev/claims_regen.txt`). The body answers them under Red checks.
- Closure classification: closure.py's INERT_EXCEPT and closures.json's doc_claims.py closure both gain the manifest, the six mermaid PNGs and how-it-works-dark.png, the same route coffee.svg took. The harness joins harness_headers.py's reads. `tests / closures`, `tests / closure-scope` and `tests / fast (3.14)`, which runs entities.py under the forced FULL gate, are all green at this head.
- build_docs.mjs: the `normalize` change maps `./docs/x.md` rows to `docs/x.md`, and `rawImages` maps `./docs/img/...` to `img/...` relative to docs/, or refuses the target. Both are killed by the mutants above.
- The generator docs/img/readme/render_mermaid.mjs is not executed in CI. PNG bytes are not reproducible across machines, as the architect note's design records. CI pins its output through the doc_claims arm, which hashes both the block text and each PNG. The body's Unpinned sites gives that disposition. I did not re-run the generator, because this seat has no tools/site node_modules.
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched by the three-dot diff. No `*_budgets.json` moved.
- Merge with origin/main a6e4a5afe: `git merge-tree --write-tree` exits 0 with no conflict and no claim-driver line (`ev/merge_tree.txt`).
- Code ownership: tools/site/build_docs.mjs and tests/closure.py are code-owned by @tvofi, and the PR has tvofi as a requested reviewer. Per the brief, this is flagged, not blocked. The orchestrator's relay under mandate 6329234399 is not a GitHub review.
- CI at this head: `merge_train.py classify` printed `RED 42b228ec... pending: none red: gate` (`ev/ci_classify.txt`). The red `gate` job 124358330438 (run 41138088966) logged only `FAIL run(s) [41138089896] at this head are still being judged; their gate decides`. That is a sequencing wait on the second run, whose `pr-contract` was still queued, not a failing test. Every tests/governance/codeql/hassfest/validate job at this head concluded success: fast, closures, coverage, browser, typing, mutation, arch-instrument, instrument-self-tests and env-matrix. The step-11 red-check answer is not judgeable until run 41138089896 concludes and a later pr-contract checks the body. I return this verdict without judging it, because the carry block above stands either way.
