Fix review: merge 0a3e8d3968d1a561c99fbda52913b1e3e4195783

Round 1. PR #1797 (R9-UI-1, dusk brand mark, part of #1791). Measured head 0a3e8d39 = code 1b029045 + merge of main aac8fb77 + its own delivery row; head equals live PR head at posting; merge base = origin/main = aac8fb77; fix-review.md at the head is current (diff against main empty).

RESULT assets: the 8 brand PNGs and the 8 docs/img/brand SVGs are blob-identical to design of record 7bca8ab3 assets/brand and assets/svg (blob_identity.txt).
RESULT icon-identity: HEAD:icon.png == HEAD:custom_components/heatpump_optimizer/icon.png == brand/icon@2x.png == dbed6dd4 (RO-4 premise holds).
RESULT pil: all RGBA, corner alpha 0; icons 256/512 square, logos 558x130 and 1116x259 (shortest side 130, inside 128-256), matching the body table.
RESULT layout: docs/img/brand/* added to tests/layout.json in eeee359b, the same commit as the eight SVGs; tests/layout.py rc=0 at head.
RESULT version: VERSION, manifest.json, RELEASE_NOTES.md untouched (0 diff lines against aac8fb77).
RESULT entities: ALL 1994 ENTITY CHECKS PASSED at head, including the three #1218 checks.
RESULT structure: STRUCTURE RATCHET PASSED; no budget file touched; budget-raise-gate green.
RESULT merge-tree: git merge-tree --write-tree origin/main HEAD rc=0.
RESULT template: all seven template headings present; pr-contract green.
RESULT ci: all 35 check runs at 0a3e8d39 success or skipped; none red, so no root-cause trigger is owed. fast, closures, coverage, mutation cited from CI, not re-run.

Out-of-brief changes, judged:
1. tests/closures.json re-record: necessary and correct. The six new PNGs are production files under custom_components; without them the closures leave them unmapped (the fixer's red state forced MODE: FULL with "no recorded closure mentions") and the #1218 entity check fails on the package count. The diff adds exactly the six paths to the three closures that already list brand/icon.png and brand/logo.png, plus timing noise. It forces MODE: FULL on this PR because closures.json is the gate's own input; CI ran it and the closures lane is green with closures-autofix skipped.
2. tests/deployment_shape.py cost note: necessary (the #1218 entities check pins it) and correct. Re-derived independently with _d308_pairs' rule (rederive_1218.py/.txt): at head 85 files, 67 of 378 pairs >= 0.80, 12 at exactly 1.00 with the shared counts the note states. The note on main at aac8fb77 was already stale (it claimed 15 pairs at 1.00 and three doc_claims pairs that are 0.92, and shared counts 65/46/11/75/47 against a recording of 67/50/14/77/51); this PR corrects those too, which is within the lines it had to touch.

Mutation limit: acceptable for this stage. The PR adds no production code line, so CI's mutation lane draws no mutant; the closures and docstring sites are pinned (FULL-mode fallback and the #1218 check). Dropping the docs/img/brand glob turns nothing red because tests/layout.py is report-only by R9-RO-1's design; the body records that rather than claiming a detector, which is what fixer.md asks. RO-1's later enforcing stage is where that becomes a failing check.

Non-blocking body inaccuracies (no verdict effect): the Head section says the commit above the code head touches only handoff/ paths, but it touches docs/delivery/1797.md; the null control is quoted at 48786f65 (1990 checks) rather than the merge base aac8fb77 (1994 at head).

Code-owned: tests/layout.json. Approval by the orchestrator under the mandate.
