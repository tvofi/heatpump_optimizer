# D6-web: product page (docs/index.html, docs/site, live page)

Baseline 323fc7c48309cf2fc4ddec090ac6721006636cfc. Harness: web_claims.py (--live for network, --perturb-dims for the perturbation).

Claims: extracted 88, checked 88, false 1, stale 0, unverifiable 0.

## Finding
- D6-s9-01 (low, hygiene): img/card/plan-why-light.png is declared 1056x616, the file is 1056x792. Perturbation: declare 792, mismatch count 1 to 0.

## Non-findings
Live page is byte-identical to docs/index.html (HTTP 200); 9 sub-pages, images and GitHub links return 200; 9 anchors resolve; tiles (24 h, 30 min, 20 h, EN/SV), 8 snapshots, p90, five quick-setup toggles, menu labels, HA 2025.2.0, Python 3.13 hold; no version number on the page; no stale feature list (the page quotes README, pinned by tests/doc_claims.py).

## Not finished
README-quoted prose is left to the README D6 seats; weekday labels in card-dhw-band-weekly.png not machine-checked.

Exposure: none beyond docs/index.html, README.md, docs/dashboard-card.md.
