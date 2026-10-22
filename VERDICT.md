Fix review: merge b3a99a2af82516d26a0621ccf5dab4e3af64159a

bus-nonce: 1a91e335efe20296efbb7e934cd96e1c

Round: second review observed by this seat (previous verdict blocked carry-scope at 4649c7d53). Head measured: b3a99a2af82516d26a0621ccf5dab4e3af64159a, still the PR head when read. origin/main is c409c9b18.

## Findings

- The README-top placement is a carry only: README.md has no button at c409c9b18, and none is owed by this PR. R10-ARCH-DOCS-FIRST must land all three placements, and the carry on R10-ARCH-DOCS verifies and wire-tests them. Carry: R10-ARCH-DOCS-FIRST

## Evidence

- Roster diff against origin/main: dev/programme/delivery/2603.md (new row) and dev/programme/rosters/wave-r10-groups.json, 6 insertions and 2 deletions over the two files. Exactly three append-carry ops and nothing else: 838178f8a on R10-ARCH-DOCS-FIRST (the owner's carry), 9bd3c4d57 on R10-ARCH-DOCS-FIRST (names both footers), 33138bc2f on R10-ARCH-DOCS (verify and wire-test all three). Carries: R10-ARCH-DOCS-FIRST 3 to 5, R10-ARCH-DOCS 1 to 2. 148 groups on main, 148 at head. See ev/roster.diff.
- Previous block cleared. The owner asked for the top of the README and the bottom of the web page. Carry 2 of 5 on R10-ARCH-DOCS-FIRST now names docs/index.html's own hand-written footer (docs/index.html:407) and the shared footer built by tools/site/build_docs.mjs:221. Both line numbers are right at c409c9b18: line 407 is the footer opening, line 221 is the footer.site template. It adds docs/index.html to the group's reach for this change only, as O-1 did for build_docs.mjs, and it says doc_claims.py's site arms are updated in the same PR. tests/doc_claims.py reads docs/index.html as SITE_PAGE (line 2251), so that claim is real. The R10-ARCH-DOCS carry names all three placements. The link target https://buymeacoffee.com/rpgshcwb2tp, the in-tree SVG/CSS rule and the external-origin rule for <a href> match the tree.
- Liveness: R10-ARCH-DOCS-FIRST is queued and R10-ARCH-DOCS is not-started. Both are live on main's roster. docs/index.html is in R10-I5-DOCS (stage done), not in either live group's files, so the carry stating the reach is what makes the overlap visible.
- node tools/policy/brief_lint.mjs at head: TOTAL: 0 error(s) across 47 file(s). carry_audit.py check --body: 0 finding item(s), 0 unrouted, 0 bad destination(s). The Carry in this verdict names R10-ARCH-DOCS-FIRST, a live group.
- git merge-tree --write-tree origin/main b3a99a2af82516d26a0621ccf5dab4e3af64159a: clean, rc 0, tree 6021a7e0c9fad2676fd73b7303e3cd6e801e3ad1.
- Mutation proof: n/a, roster state only, no production or test code. VERSION, manifest version and the notes heading are untouched (diff touches two files).
- Check-runs at this head (see ev/check-runs.txt), read when I looked: pr-contract, briefs, policy-docs, budget-raise-gate, arch-score, hassfest, mutation, delivery-status, closure-scope and scope are success. fast (3.14), instrument-self-tests and closures were still in_progress, so their green state is not read and not claimed. nightly-status is failure; it grades main and is not a required check and does not block. No other red check, so no root-cause answer is owed.
- Forward-carry: the body says none, and the owner's request is carried on the roster at the body's SHA with its control stated as a precondition (the same PR updates the README-head and site-footer checks).
- Figures: the body's 148/148 groups, changed R10-ARCH-DOCS and R10-ARCH-DOCS-FIRST, and "carries 3 to 4, 4 to 5, 1 to 2" were re-derived from the roster JSON (the main side is 3, 1; the head side is 5, 2). The body's 5 insertions and 2 deletions refer to the roster file alone at 33138bc2f; I measured 6 and 2 over both files at the merge head, the extra line being the delivery row. The body's null-control claim that the roster on main equals the merge base was not re-run.
- The fix-review contract on main is unchanged since the merge base (empty diff of dev/governance/roles/).
