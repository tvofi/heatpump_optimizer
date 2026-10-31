Fix review: merge c41c4053900fcc62ea152a9b264bc89472f5b2a6

bus-nonce: 4ec3c2e3cd360c4e284dbe8e358db936

## Scope

Delta review of PR #3014 (R10-README-GRAPHICS), round as dispatched: the last merge verdict was at 42b228ec7e13ac30e49739d738dad374aa729da2; the only new commit is c41c40539, a merge of origin/main 4822c8f9b. review_carry.py printed FRESH-REVIEW; the brief scopes this review to its four checks, so the full-PR steps (mutation proof, finder's harness) stand on the verdict at 42b228ec. Head measured: c41c4053900fcc62ea152a9b264bc89472f5b2a6; it was still the PR head and origin/main was still 4822c8f9b when this verdict was written.

## Findings

None.

## Evidence

- (1) No resolution in the merge. `git merge-tree --write-tree 42b228ec 4822c8f9b` exits 0 with tree d63f8f9ef49526bacc9360e25299a1dee5d0762f, which equals c41c40539's own tree. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json` (set-merge of doc_claims.py closure and harness_headers.py inert_reads); that is the driver's automatic merge and the committed tree matches it byte for byte.
- (2) Same change. The +/- lines of `git diff 437f1ba9...42b228ec` and `git diff 4822c8f9...c41c4053` are byte-identical (cmp exit 0, 530 lines; ev/old.lines, ev/new.lines). Both diffs: 18 files, 456 insertions, 50 deletions. `git range-diff` shows all three branch commits as `=` with the same SHAs (ev/range-diff.txt). What review_carry saw differ (ev/fulldiff-delta.txt, ev/index-delta.txt): the `index` blob lines of tests/closure.py, tests/closures.json, tests/doc_claims.py and tests/entities.py, 16 hunk headers' offsets, and context lines only: in tests/closure.py the two lines after the branch's INERT_EXCEPT insertion are now main's R10-ARCH-DOCS-WIRING comment instead of DISCLAIMER.md/blueprint entries; in tests/doc_claims.py main() the two lines above the branch's added `check_readme_marketplace()` call are now main's `check_marker_census()`/`check_card_figures()` instead of `check_image_dimensions()`/`check_doc_wiring()`.
- (3) No interaction. Main's 437f1ba9..4822c8f9 delta touches 174 files; the overlap with the branch's 18 is tests/closure.py, tests/closures.json, tests/doc_claims.py, tests/entities.py (ev/overlap.txt, ev/main-overlap-diffs.txt). Main's changes there: INERT_EXCEPT entries for docs/img/card/* and tools/audit/seat/*.sh (closure.py, closures.json), the marker-groups rewrite of _units/doc_wiring_findings and new check_marker_census/check_card_figures (doc_claims.py), COP-gate and mutation null-control checks (entities.py). None touches docs/img/readme/, README.md, the sanitizer arm or tools/site/build_docs.mjs. In the merged doc_claims.py main() still calls every check, check_readme_marketplace() last (lines 3885-3896). `python3 tests/doc_claims.py` at c41c4053900fcc62ea152a9b264bc89472f5b2a6: ALL 255 checks PASSED, exit 0 (ev/doc_claims-head.txt).
- (4) CI. `merge_train.py classify c41c4053900fcc62ea152a9b264bc89472f5b2a6` exited 0: `GREEN c41c4053900fcc62ea152a9b264bc89472f5b2a6 pending: none red: none` (ev/ci-classify.txt, ev/ci-classify.log). No red check, so step 11 has nothing to answer.
- Mergeability: `git merge-tree --write-tree origin/main c41c4053900fcc62ea152a9b264bc89472f5b2a6` exits 0 at origin/main 4822c8f9b (ev/merge-tree-main.txt).
- Policy currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Review packet rendered here (ev/review-packet.md): refusals none, advisories none, CARRY-AUDIT 4 items 4 routed 0 unrouted.
