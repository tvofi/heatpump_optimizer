Fix review: blocked 4649c7d531330970aa31b76afea523ae23d66b70 carry-scope: the carry does not reach docs/index.html, the product page whose hand-written footer is the site's front

bus-nonce: 5fd97fcc866baaa0a0cd219c646ceb88

Round: first review observed by this seat. Head measured: 4649c7d531330970aa31b76afea523ae23d66b70 (the head named in the dispatch). origin/main at review time is c409c9b18 (the brief and body say c1e1967bc; main has since taken #2602).

## Block

The roster diff is exactly what the brief requires, but the carry's text does not ask for the owner's full placement.

- The owner: "at the bottom of the web page". The site has two kinds of page. The markdown-rendered pages (readme.html and the others) share one footer, built at tools/site/build_docs.mjs:221. The product page docs/index.html is not rendered from markdown: build_docs.mjs:45 and :98 treat it as the site's front, and it carries its own hand-written `<footer>` (docs/index.html:407), separate from the shared one.
- The carry scopes the footer as "the docs web page (the site built by tools/site/build_docs.mjs from docs/; every page's footer if the footer is shared)". The condition is not met for index.html, so a fixer following the carry literally edits build_docs.mjs and README.md and leaves the landing page, the page most likely meant by "the web page", with no button.
- docs/index.html is in no live group's files. It is in R10-I5-DOCS (stage done), not in R10-ARCH-DOCS-FIRST or R10-ARCH-DOCS. A fixer who edits it as well, to comply with the owner's wording, is outside the group's files and the roster's overlap checks cannot see it. The carry should name docs/index.html and its footer, say that it is added to the group's reach (as O-1 did for build_docs.mjs), and say which of the two footers carries the button, or both.
- Fix: append one further carry, or reword this one, naming docs/index.html's own footer (and the tests that read it: tests/doc_claims.py's site arms), with the same in-tree-asset rule. Everything else below passes.

## Findings

- The carry leaves R10-ARCH-DOCS's verification of "both placements" with a gap on the product page: its brief verifies docs/architecture.md and the developer onboarding, and the carry adds the button placements and the link target to it. If the product-page footer is added to the placements, R10-ARCH-DOCS's carry must name it as well. Carry: R10-ARCH-DOCS-FIRST

## Evidence

- Roster diff against origin/main (three-dot and two-dot agree): dev/programme/delivery/2603.md (new, one row) and dev/programme/rosters/wave-r10-groups.json, 3 insertions and 1 deletion. Exactly one group changed (R10-ARCH-DOCS-FIRST), only its `carry` field, 3 to 4 entries, the first three unchanged. Re-measured: 148 groups on main, 148 at head, none removed, none new, 1 changed.
- The carry quotes the owner verbatim and matches the PR body's quotation. It names https://buymeacoffee.com/rpgshcwb2tp, README.md top, the footer, docs.css tokens in light and dark, and R10-ARCH-DOCS as verifier. It does not contradict the owner. The link is written `https://buymeacoffee.com/...` where the owner wrote the bare host; that is a fix of the form, not a change of the target. (The em dash is stored as a JSON escape; the file parses.)
- Routing: R10-ARCH-DOCS-FIRST (files docs/architecture.md, README.md) is the only live group whose files include README.md; tools/site/build_docs.mjs is in its reach by the O-1 carry on the same group. R10-ARCH-DOCS (not-started) lists README.md and its carry reads as consistent with its rescoped brief (verify, adjust, wiring-test).
- Shared footer produced at tools/site/build_docs.mjs:221 (within O-1's reach). Site rules in tests/doc_claims.py (_site_external, _site_requests, subpage_findings): external script, stylesheet, icon, preload, iframe, img and CSS url() are refused; an `<a href>` to another origin is allowed, as the existing GitHub link shows. So the carry's in-tree-asset requirement agrees with the tree's rules and is stricter only for the third-party badge image. No CSP exists in docs/index.html or build_docs.mjs output.
- node tools/policy/brief_lint.mjs at head: TOTAL: 0 error(s) across 47 file(s), equal to main. On the roster alone: 0 error(s) across 1 file(s). carry_audit.py check over the body: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s). Every Carry in this verdict names R10-ARCH-DOCS-FIRST, a live group on main's roster.
- git merge-tree --write-tree origin/main 4649c7d531330970aa31b76afea523ae23d66b70: clean, rc 0, tree 0ef30e5de28195189a60c0a9f1d09beb811bd791.
- Mutation proof: n/a, roster state only, no production line. VERSION, manifest version and the notes heading are untouched (diff touches two files).
- Check-runs at this head (36 listed): everything concluded is success, skipped or neutral except nightly-status, failure. nightly-status grades main and is not a required check and does not block. At the time of reading, "fast (3.14)" and "instrument-self-tests" were still in_progress and "closures" had finished; the green state of those two is not read and is not claimed. mutation, pr-contract, briefs, policy-docs, budget-raise-gate, arch-score and hassfest are success. No red check, so no root-cause answer is owed.
- Forward-carry: the body says none, and the owner's request lands as a carry on the roster at the body's SHA. Stated control precondition: the carry says the same PR updates the README-head and site-footer checks.
- Figures: the body's 148/148/1 groups and "3 to 4 carries" were re-derived with my own script. The body's c1e1967bc merge-base claim for #2601 is not re-derived (main has moved to c409c9b18).
