Fix review: merge 5dbd37263519e3359a7c07348a3601154e4a3f7a

PR #1894, roster R9-WEB-5. Round 1. Live head at posting is still 5dbd3726
(PR headRefOid = measured); merge base is the stated 1913f0dd7.

The fix. README lines 16 and 1012 target
`https://tvofi.github.io/heatpump_optimizer/`. pages.yml stages
`docs/index.html` at the artifact root (`rel="${f#docs/}"` -> `_site/index.html`),
so the site root is the product page: the URL answers 200 with
`<title>Heat Pump Cost Optimizer</title>`; `.../docs/index.html` answers 404.
Tree-wide grep: no repo-relative docs/index.html link remains — only plain-text
mentions in RELEASE_NOTES.md and docs/delivery/1846.md, dispositioned in the
body. resolveHref keeps `^[a-z]+:` hrefs verbatim, so the absolute link is
correct on the site too.

The pin. At head: ALL 160 doc_claims checks PASSED. Head tree with only the
base README: `1 of 160 checks FAILED`, the readme-link check naming
'docs/index.html' twice (both links). Mutant killed by me: line 16 reverted in
place → 1 of 160 FAILED; restored → green. The pin also normalizes the
published form to the docs/index.html identity for the Documentation two-way
check, so it cannot pass vacuously.

Scope. Four files: README.md, tests/doc_claims.py, D6 claims.json/.md. No
production line; VERSION, manifest, RELEASE_NOTES and tests/golden/ show an
empty diff against base. D6 census re-derived under the harness's own rules:
relative 91, external 17 — matches the committed figures. harness_headers 105
green.

CI: 30 check-runs at head, only nightly-status red, answered in the body as the
standing expected-red. Body contract: `_Requested by **tvofi**_` first line,
headings, mutation and null with commands, no armed closing keyword.

Evidence: evidence/ in this branch, naming head 5dbd37263519e3359a7c07348a3601154e4a3f7a.

Evidence (absolute): /Users/timmalmstrom/hpo-orch/notes/rev1894/ — VERDICT.md and the reviewer's evidence naming measured head 5dbd37263519e3359a7c07348a3601154e4a3f7a (carried to d6c1f64de2965c04ffff07d5883043980da89ce3 by automatic main merges only).
