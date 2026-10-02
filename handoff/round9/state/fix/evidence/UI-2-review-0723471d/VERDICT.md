merge 9b7eddb5f511ea1fb0aedc514efb1a4d6fe53a35 (round 2, PR #1801)

PR head 9b7eddb5 = code head 91a4813d (parent 0723471d, which adds only the D6 claims pair, byte-equal to d6_claims_regen_2bdd974a.patch) merged with 2bdd974a (adds only docs/delivery/1801.md). No handoff/ file anywhere in the range 59c2543b..9b7eddb5.
RESULT D6 harness at 91a4813d: claims.py leaves the tree clean (git status 0 lines), claims_false=0.
RESULT CI at 9b7eddb5: every check on the head passed or was skipped, including fast (3.14), pr-contract (both runs), mutation, typing, coverage, closures, policy-docs, delivery-status, nightly-status, validate-hacs and hassfest; nothing red.
Red checks in the range: fast (3.14) and pr-contract were red at 0723471d and 2bdd974a. The body answers fast (3.14) under Red checks (cheaper detector: tests/harness_headers.py run locally, required by the docs-lane brief); pr-contract's red was that missing answer, and it is now green.
mutation: docs-only diff, so no mutant is drawn.
merge-tree against origin/main 59c2543b: rc 0.
Round 1's findings below all hold at this head.

--- earlier rounds ---
blocked 2bdd974abb2bd899edffd6fe5cfa5d5073f24fc9 harness: tools/audit/round4/D6 claims output not regenerated (round 1, PR #1801)

CI fast (3.14) at code head 0723471d is red (job 110125296480): tests/harness_headers.py "FAIL the executed harnesses leave their committed output byte-identical [ M tools/audit/round4/D6/claims.json; M tools/audit/round4/D6/claims.md]".
Reproduced at 2bdd974a: PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py rewrites both files (C108 relative links 90->92, C110 images 20->22, C111 external links 14->15; verdicts unchanged, claims_false=0). At base 59c2543b the same run leaves the tree clean.
Fix: commit the regenerated pair (d6_claims_regen_2bdd974a.patch here), and name fast (3.14) under Red checks with its answer: the cheaper detector is tests/harness_headers.py run locally, which the docs-lane brief already requires (state b), standing cost about 2 minutes.
Everything below stays true of the code head and carries to the fixed head once CI is green.
Row commit 2bdd974a adds only docs/delivery/1801.md (checked by diff), a step-12 carry of the code head.

--- round-1 review of the code head ---
merge 0723471d0e5554d7c938ab5b7fb90398c3eb224b (round 1, pending the PR head's CI)

R9-UI-2, lane UI, #1791. Base 59c2543b (= origin/main at review time). Reviewed from a detached worktree at 0723471d.

RESULT generator: make_readme_figures.py at the head, run with the OFL fonts, rewrites banner.svg, how-it-works.svg, how-it-works-dark.svg and all three PNGs byte-identical to the tracked files (git status empty); social-preview.svg identical to the design of record's.
RESULT design: all six tracked assets are blob-identical to 7bca8ab3 handoff/round9/state/alt/design/assets/readme; the README's +/- lines equal README.proposal.diff except the two image paths, moved to docs/img/readme as DESIGN.md section 5 requires.
RESULT D1: mark paths LINE and POOL, stroke 3.6, glacier line and ember heat match DESIGN.md section 2 dark colours; badges fjord 026aa8, License ember d2601f.
RESULT D3: the series palette is R9-UI-4's (chart); this diff draws no chart series, nothing to check.
RESULT D4 (applied to the README graphics, own Machado harness): banner line/heat protan 88.7 deutan 100.0 tritan 110.2; figure flow/action light 87.0/102.1/97.0; dashed feedback vs flow lowest tritan 17.5 (light), all above 10.
RESULT HACS class (hacs_class.py, own harness applying the _HACS_LINK regex of tests/entities.py to the whole README): spans whose first '(' is an absolute URL, base 1 (the License badge), head 0.
RESULT cheap checks at head: layout.py dead 27 (body says 27); md_tables orphaned 0, misrendered 0; structure.py PASSED; closure select MODE: SCOPED, 4 scripts; merge-tree vs origin/main rc 0. entities.py and doc_claims.py need homeassistant, not installed here: cite CI.

Mutation proof: n/a, docs-only diff, no production line.
VERSION, manifest, notes heading: untouched.
Claim files: untouched.

Non-blocking notes:
1. how-it-works-dark.svg/png is tracked but nothing references it (DESIGN.md: "a dark variant for the docs"). Either use it via a <picture> source or leave it for a later docs page.
2. tests/entities.py's HACS image check skips an absolute image src, so the fixed badge shape (absolute image inside a relative link) has no detector; this PR closes the only instance.
3. "Pin exact run slots from the card editor": in Home Assistant "card editor" usually means the card's config UI; "plan editor" would be exact. Wording is the approved design's.

Structure: no ratchet raised or re-recorded; the generator lives under docs/img (INERT prefix, precedent make_model_figures.py). No concern.
Approval: tests/layout.json is code-owned; the orchestrator approves under the mandate.
