Fix review: blocked 42b228ec7e13ac30e49739d738dad374aa729da2 figure-wrong: the body's Figures count of README ](./ targets is 35, it is 31 at this head

bus-nonce: c1ba19cb6925a39b0a5f7de7334fd59c

Round 1. Reviewed from a detached worktree at 42b228ec7e13ac30e49739d738dad374aa729da2 (live head re-read before writing: unchanged). Contract dev/governance/roles/fix-review.md at origin/main; `git diff <merge-base>...origin/main -- dev/governance/roles/` touches only standing-merge.md, so fix-review.md is current.

## Block

The PR body's `## Figures` states: "`grep -o '](\./' README.md | wc -l` prints 35 at the head ... 28 links, 4 images, 3 new figures". At 42b228ec7 (and at the code head 17ee47eef and at 08d1b3d5c) the same command prints **31**: 28 links plus 3 markdown images (banner, coffee, card chart). The how-it-works figure and the three mermaid figures are now `<picture>` HTML, so they carry `src="./`/`srcset="./` (8 attributes) and no `](./`. 35 is the count of the pre-dark-mode revision, when the how-it-works figure and the three mermaid PNGs were markdown images; the body was not re-taken after the `<picture>` conversion. The base figure (0) and the "no bare target left" grep (prints nothing) re-derive correctly.

Repair is body-only and does not move the head: re-take that figure (and its breakdown) at the head. While editing, the `## Red checks` line "none yet at this head (CI not run)" is stale: CI has now concluded green at this head with no red check. Everything else below was verified and survives an unchanged head.

## Findings

- The D6 claims register's C108/C110 counts (83 links, 21 images) no longer include `<picture>` images: the how-it-works light/dark pair and the six mermaid PNGs are outside C110's "every image the documentation embeds exists". Their existence is held instead by the new doc_claims arm (my mutants deleting mermaid-one-interval-dark.png and how-it-works-dark.png both turn it red). Carry: dismissed: existence is pinned by the tests/doc_claims.py arm, shown by two killed mutants; the register regenerates byte-identical at the head.
- render_mermaid.mjs is not executed in CI and has no self-test of its own; its output is pinned by the manifest's block and PNG hashes, and the body shows regenerate-then-green. Carry: dismissed: the approved design note 2e536d13 (roster entry) defines the CI wiring as the tests/closure.py classification of the manifest and PNGs as doc_claims.py reads, not a CI run of the generator.
- tools/site/build_docs.mjs and tests/closure.py are code-owned (`/tools/site/ @tvofi`, `/tests/closure.py @tvofi`); the orchestrator's relayed approval is not a review, so this head merges only on tvofi's approving review. Flagged per the brief, not blocked on. Carry: dismissed: enforced at merge by main-protect-checks' code-owner rule.

## Evidence

- CI: `merge_train.py classify 42b228ec7...` -> `GREEN ... pending: none red: none`, exit 0 (ev/ci_classify.txt). Review packet: gate digest green, refusals none, CARRY-AUDIT 4 routed / 0 unrouted (ev/review-packet.md). No red check at this head, so no root-cause trigger to answer.
- Merge: `git merge-tree --write-tree origin/main(5d4e0bcfb) 42b228ec7` exit 0, tree d36663cfd; `LEDGER-MERGE: resolved tests/closures.json` (inert_reads set merge). No conflict (ev/merge_tree.txt).
- Finder's harness (dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs, marked 15.0.4 + xss 1.0.15 installed by me), ev/harness.txt:
  - RESULT base 437f1ba9b: relative_images=4 resolved=0; relative_links=28 resolved=0; picture_sources=0; absolute_images=5 resolved=5; rc=1 (red).
  - RESULT head: relative_images=7 resolved=7; relative_links=28 resolved=28; picture_sources=4 resolved=4; absolute_images=5 resolved=5; rc=0 (green).
  - RESULT null control (one absolute-URL image README): absolute_images=1 resolved=1, rc=0; controls `bare=blank dot=ok absolute=ok`, `srcset_bare=stripped srcset_dot=kept light_img=ok` at both ends.
  - RESULT my perturbation (head with one dark srcset made bare): picture_sources=4 resolved=3, rc=1, so the harness moves under its own perturbation.
  - mermaid_fences=3 plain_code=3 at both ends, as the body states.
- tests/doc_claims.py at the head: ALL 228 checks PASSED (ev/doc_claims_head.txt).
- Mutation proof, 13 mutants, each restored after (ev/mutations.txt), all killed: one link `./` removed (1 FAIL); setup-flow light-only (4); how-it-works light-only (2); mermaid-one-interval-dark.png deleted (1); how-it-works-dark.png deleted (2); dark PNG replaced by the light one (1); first block `flowchart LR`->`RL` without regenerating (1); dark srcset made bare (1); dark source media changed to `prefers-color-scheme: light` (1, mine); how-it-works dark source pointed at the light PNG (2, mine); build_docs.mjs `path.posix.normalize(m[1])`->`m[1]` (2); build_docs.mjs `rawImages(...)` reverted (1); hero image `./` removed (1, mine). The "passes when fixed" regenerate run is covered in-tree by the arm's own check "regenerating the manifest after the planted block edit is green again"; I did not re-render PNGs.
- Dark mode: each of the four figures is a `<picture>` with a light `<img>` and a `(prefers-color-scheme: dark)` `<source>`; the how-it-works figure is included and uses the pre-existing how-it-works-dark.png (differs from the light PNG). Held to the brief's owner ruling, which supersedes the note's scoping-out of `<picture>`.
- Figures re-derived at the head: base count 0; no bare target left; PNG sizes 2296x806, 2296x1434, 2296x5986, light and dark, RGB (opaque); every PNG sha256 equals mermaid_figures.json's; doc_claims.py closure 175 -> 183 entries in tests/closures.json; D6 register regenerated with `claims.py` at the head: no diff against the committed claims.json/claims.md (C108 83, C110 21) (ev/claims_regen.txt). The 35 figure is the block above (ev/figure_35.txt).
- Not re-derived: the GitHub markdown API `<themed-picture>` rendering. This seat's proxy refuses `POST /markdown` (sessions are bound to repository-scoped endpoints). Unverified by me, not refuted.
- Closure classification: the eight new or newly-read docs/img/readme files are on INERT_EXCEPT and in doc_claims.py's recorded closure (the coffee.svg route the note prescribes); render_mermaid.mjs stays under the INERT docs/ prefix; the harness is in harness_headers.py's inert_reads; tests/entities.py hero regexp updated to `./` (green in CI).
- build_docs.mjs: row targets normalised with path.posix.normalize; raw `<img src>`/`<source srcset>` resolved to docs/-relative or refused; both mutants above prove each line is pinned.
- Forward-carry read back on handoff/audit-r10-roster at ce4dac44e: R10-CATALOG-PR carry index 0 (real HA 2026.11 Marketplace page at the first stamped tag with #3014, light and dark, absolute-URL image as control) and R10-ARCH-DOCS carry index 8 (figures vs what they depict; product page in both site themes under both OS schemes). R10-README-GRAPHICS is in both groups' `after` lists. Both state their control as a precondition.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched by the three-dot diff. No golden or claim file moved.
