Fix review: merge 42b228ec7e13ac30e49739d738dad374aa729da2

bus-nonce: aafb80a56fd11fd21772fa7bb5839125

## Verdict

Round 1. Group R10-README-GRAPHICS, PR #3014, reviewed at head 42b228ec7e13ac30e49739d738dad374aa729da2 (code head 17ee47eef93a682ba9c08489c03048441a6c58bf), merge base 437f1ba9b521199b360d84effe6a621573d34663, in a detached worktree. The head was unchanged when this verdict was written (`git ls-remote`, ev/head-at-post.txt). Contract: dev/governance/roles/fix-review.md at origin/main. Since the merge base, main changed only standing-merge.md under roles/, not fix-review.md.

## Findings

- The fix is verified only against a replica of the Marketplace pipeline, not against a real Home Assistant 2026.11 instance (design note P2). Still owed after the merge: a screenshot of the Marketplace repository page at the first stamped tag that contains #3014, in light and dark OS colour scheme, with an absolute-URL image as the control. The roster carry exists on origin/handoff/audit-r10-roster (1e9f14dd3) and states its control. Carry: R10-CATALOG-PR
- On the product page, `<picture>` follows the OS colour scheme, not the site's theme toggle. Nothing compares a drawn PNG semantically with its mermaid block (P3/P40). Both are owed by a later verification. The roster carry exists, states both checks, and keeps dark mode in scope. R10-README-GRAPHICS is in R10-ARCH-DOCS's `after` list. Carry: R10-ARCH-DOCS
- tools/site/build_docs.mjs and tests/closure.py are code-owned (`@tvofi`), so the merge still needs tvofi's approving review at this head. The orchestrator's relayed approval is not a review. Flagged as the brief asks, not blocking. Carry: dismissed: enforced at merge by main-protect-checks' code-owner rule, not by this PR

## Evidence

- RESULT ci: `merge_train.py classify 42b228ec7…` prints `GREEN … pending: none red: none`, twice, the second time just before writing (ev/ci-classify.txt). The packet's gate digest lists no refusal, and pr-contract, gate, mutation and closures all show success. So there is no red check, and step 11 has no trigger. The body's Red checks section says CI concluded green with no red, which is correct.
- RESULT merge: `git merge-tree --write-tree origin/main 42b228ec7` exits 0 with tree 90b2fd195. The `LEDGER-MERGE: resolved tests/closures.json` driver merged the set. No conflict, and no `MERGE-CLAIM` line.
- RESULT finder harness, dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs with marked@15.0.4 and xss@1.0.15 (ev/harness-base-head.txt):
  - Base README (437f1ba9b): relative_images=4 resolved=0, relative_links=28 resolved=0, picture_sources=0, rc=1 (red).
  - Head: relative_images=7/7, relative_links=28/28, picture_sources=4/4, absolute_images=5/5, rc=0 (green).
  - Null control, a README holding only an absolute-URL image: 1/1, rc=0.
  - Controls at both ends: `bare=blank dot=ok absolute=ok`, `srcset_bare=stripped srcset_dot=kept light_img=ok`. mermaid_fences=3 plain_code=3.
  - Every figure matches the body.
  - The harness was rebuilt in-tree from the finder's out-of-tree copy, as the design note required (P1). The body names it as the replica under P1 of the note's carries.
- RESULT mutation, `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: 228/228 pass at the head (ev/doc_claims-head.txt). Each mutant below was restored after its run (ev/mutants.txt).
  - Base README: 10 fail, naming 17 bare targets.
  - Setup-flow dark `<source>` removed (light-only figure): 4 fail.
  - how-it-works dark `<source>` removed: 2 fail.
  - My own mutant, how-it-works dark srcset pointed at the light PNG: 2 fail.
  - build_docs `rawImages` reverted: 1 fail, on the built-page check.
  - build_docs `path.posix.normalize` reverted: 2 fail.
  - Dark PNG replaced by the light one (planted drift): 1 fail, naming the manifest mismatch.
  - `<details open>`: 1 fail.
  - Mermaid block edited without regenerating: 1 fail.
  - One link made bare: 1 fail.
  - My own mutant, dark source `media` set to light: 1 fail.
  - how-it-works-dark.png deleted (missing dark PNG): 2 fail.
  - No mutant survived.
  - "Passes when fixed" is self-tested in the arm (manifest regenerated, then green). I did not re-run the generator, which needs Chromium and mermaid. The body's live regenerate-then-green run is cited, not re-taken.
- The generator docs/img/readme/render_mermaid.mjs is tracked, and its header states the install (P6). CI reaches it through the doc_claims arm, which tests.yml runs. Per the design note the closure classification is that wiring, and no workflow edit was designed. The generator itself does not execute in CI. The arm pins its output by block hash and PNG hash.
- Dark mode: every `<picture>` has a light `<img>` and a `prefers-color-scheme: dark` `<source>`. That includes the how-it-works figure, which uses the existing how-it-works-dark.png. I viewed two dark PNGs: they are genuine mermaid dark-theme renders on #0b1a28 and read well. PNG sizes match the body: 2296x806, 2296x1434, 2296x5986 (ev/png-sizes.txt).
- Not re-derived: the claim that GitHub's markdown API wraps `<picture>` in `<themed-picture>`. This session's GitHub API access is repository-scoped, and POST /markdown was refused (ev/github-markdown-api.txt). `<picture>` with prefers-color-scheme is GitHub's documented form, but I did not verify it.
- D6 register: `claims.py` re-run at the head leaves claims.json and claims.md byte-identical: C108 "83 links, broken=[]" and C110 "21 images, missing=[]" (ev/claims-gate-structure.txt). The body's explanation holds: how-it-works is now a `<picture>`, so it is no longer counted as a markdown image.
- Closure: `tests/closure.py select` prints `MODE: FULL`, reason `tests/closure.py changes the gate itself`. The 8 new files plus how-it-works-dark.png sit in INERT_EXCEPT and in doc_claims.py's recorded closure, and the harness is under harness_headers' INERT READS. Every closures.json movement traces to a file this change reads (step 14). The `seconds` bump comes from the measured run time. `tests/structure.py` prints STRUCTURE RATCHET PASSED.
- build_docs.mjs: `path.posix.normalize` removes the `./` from Documentation rows. `rawImages` resolves `./docs/img/...` to `img/...` and refuses any target outside docs/. The arm's built-page check confirms 3 mermaid srcsets and no leftover `./docs/`. That check counts only mermaid sources: the how-it-works light-only mutant did not trip it, but the README check caught that mutant.
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched at the merge base…head range.
- Dispatch note body repair: the Figures line reads 31, "28 links plus 3 markdown images". I re-took it: `grep -o '](\./' README.md | wc -l` gives 31 at the head and 0 at the base. The Red checks line ("CI concluded green … no red") matches classify. I could not diff the body against its previous revision (no edit history through this seat's tools), so "nothing else changed" is unverified. The rest of the body is consistent with the head as measured above.
- Class: the design note dismisses sibling documents (P9): the Marketplace fetches README.md only, and hacs.json has no render_readme. The class is one seam, README.md's relative targets and figures, and the arm enumerates every md, refdef and HTML src/href/srcset target in it.
