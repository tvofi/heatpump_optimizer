# Class sweep: N-orphan-doc (round 11, PLAN phase D)

Class status: `N-orphan-doc` has no entry in `dev/audit/config/bugclasses.json` at
`handoff/audit-r11-register` (28b864af6d); it is new this round, so it is neither
`detector` nor `barriered`.

## Enumerator

`python3 dev/audit/rounds/round11/D14/orphan_doc.py [root]` — the reader set is
`README.md`, `CONTRIBUTING.md` (if present) and `docs/*.md|html`; a page is an orphan
when no other reader page links it (relative link, or a `/blob/<ref>/` URL into the
repo). `README.md` is the entry point and never counts.

| control | input | result |
|---|---|---|
| positive | the tree, and a copy with inbound links to CONTRIBUTING.md stripped | lists `docs/CONTRIBUTING.md` (re-finds D5-s2-02) |
| null | temp fixture: README linking `docs/a.md` | `orphan_doc=0` |
| perturbation | same fixture plus one unlinked `docs/b.md` | `orphan_doc=1`, lists `docs/b.md` |

## Seams it returns at 28b864af6d

| seam | disposition | evidence |
|---|---|---|
| `docs/CONTRIBUTING.md` | instance (judged site D5-s2-02) | only inbound link is `.github/ISSUE_TEMPLATE/3-feature_design.yml`, outside the reader set; probe: the enumerator lists it |
| `docs/index.html` | not applicable | Pages site root published by `.github/workflows/pages.yml`; an entry point, not a navigated page |

Instances beyond the finding: 0. Proposed barrier: the enumerator as a `tests/`
check over the reader set, with `docs/index.html` allow-listed as an entry point.
