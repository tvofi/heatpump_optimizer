Fix review: merge 1a18fa6fe7c1beeb424895fb718087e533ab9cb2

Round 1 at this head (the earlier block was at a different head).

## Diff scope
Three-dot diff against the merge base: two files, tools/site/package.json (mermaid 12.1.0 -> 12.2.0) and tools/site/package-lock.json. One commit, authored by dependabot[bot]; no seat merge or delivery-row commits on the branch. VERSION, manifest version and RELEASE_NOTES heading untouched.
Lockfile transitive moves beyond mermaid: katex 0.16.47 -> 0.18.10, its nested commander 8.3.0 -> 15.0.0 (engines node >=22.12.0). Both are only reachable through mermaid's own dependency (katex ^0.18.0); the commander bump is katex's CLI dependency, not loaded by the mermaid UMD bundle. pages.yml pins node-version "22" (resolves to a current 22.x), so the engines floor is met. Integrity hashes are present for every changed entry.

## Usage in tools/site
Only two touch points: pages.yml copies node_modules/mermaid/dist/mermaid.min.js into _site/site/mermaid/, and build_docs.mjs emits pre.mermaid blocks plus a script calling mermaid.initialize({startOnLoad:false,theme,fontFamily}) and mermaid.run({nodes}). Release notes for mermaid@12.2.0 (GitHub releases API): one opt-in minor feature (mindmap.colorBy: depth) and layout/rendering patch fixes (circle node sizing, ELK edge straightening, mindmap labels, swimlane/bpmn fixes). No breaking change, no change to initialize/run API. A local npm ci from the head's lockfile succeeds and installs mermaid 12.2.0 with dist/mermaid.min.js present (5.5 MB), the exact file the workflow copies. (Local Node was 20.10, only an engines warning; CI uses 22.) Not verified: rendered output of the repository's own diagrams at 12.2.0; the circle-node sizing patch could change appearance slightly, which is cosmetic.

## Check-runs at the head (commit check-runs API, paginated, every run listed)
All completed; no failure, cancelled or timed-out run. success: gate (both runs), pr-contract / pr-contract (both runs, the later at 12:16:23Z started after the last red-capable workflow concluded), budget-raise-gate, arch-score, tests/fast, coverage, typing, browser, closures, closure-scope, mutation, mutation lane, briefs, lane-proofs, graders-head-copy, coverage-ratchet, arch-instrument, nightly-status, governance/{delivery-status,env-matrix,policy-docs,instrument-self-tests,wave-script}, codeql Analyze x3, CodeQL, hassfest, validate-hacs. skipped (path-scoped or not applicable): remaining governance/tests jobs, kernel-points, autofix jobs. No red, so no root-cause answer owed.

## Earlier blocked verdict 558fcd6a (pr-contract-refused)
Does not apply at this head. That verdict concerned head 558fcd6aea84bc99894fbb713c7846481ef53345, which carried the seat's merge and delivery-row commits on the Dependabot branch. The branch was recreated (@dependabot recreate comment) and the head is now the single Dependabot commit 1a18fa6fe7c1beeb424895fb718087e533ab9cb2; pr-contract is green here under the dependency-bump contract.

## Other
git merge-tree --write-tree origin/main 1a18fa6fe7c1beeb424895fb718087e533ab9cb2 exits 0 (no conflict). Head confirmed as 1a18fa6fe7c1beeb424895fb718087e533ab9cb2 via the pulls API immediately before writing. Code-owned path /tools/site/: needs the owner's approving review (or the mandate path) to merge; this verdict does not substitute for it.
