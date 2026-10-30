# R10-README-GRAPHICS: design review, round 2 of 3

Design review: approve 2e536d13

Seat: cloud probe, read-only. Contract: dev/governance/roles/design-review.md at origin/main.
Note: handoff-body/r10-readme-graphics at 2e536d1396486ba55eb798039bc0412086b26b2f. Tree: ca0a6cfbc2e5538e6e2220793831443719ff6e98.
No tracked file changed, no PR opened.

## Round-1 revise point: fixed

- `files` is now the real edit set: README.md, the new generator `docs/img/readme/render_mermaid.mjs`, the manifest `mermaid_figures.json`, the three PNGs, the harness `dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs`, `tests/doc_claims.py` and `tests/closure.py`. The unedited `render.mjs` is gone. The new paths are absent from origin/main, as new files should be.
- `hot_files` is now README.md, tests/doc_claims.py and tests/closure.py. This matches the note's section 4 and the overlap with R10-ARCH-DOCS and R10-MERGE-SUBJECT-CASEARM.
- brief_lint, re-run at origin/main on a scratch copy of origin/handoff/audit-r10-roster with the corrected entry appended: exit 0, 0 errors, 6 warnings. All 6 belong to pre-existing R10-FLY-* groups, none to this group.

## Round 2 diff

The 2e536d13 vs e995b815 diff changes only the roster entry and adds the carries P2 and P5-P9 for the fixer. No evidence or design section changed, so I did not re-litigate the points round 1 accepted.

## Carries for the fixer

The note records them: P2 (a real instance or screenshot), P5 (PNG sha256 in the manifest, regenerate -> green), P6, P7, P8 (only a stamped tag shows the fix) and P9. The orchestrator routing, to add this group to the `after` lists of R10-ARCH-DOCS and R10-CATALOG-PR, is still owed at dispatch.
