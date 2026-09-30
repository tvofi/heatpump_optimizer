<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

R9-UI-2, lane UI, part of #201 and #1791. Before: the README opens on a title and plain badges, the License badge's relative link puts the badge image inside the HACS rewriter's span, and "How it works" has no figure. After: a dusk banner above the title, fjord badges (License in ember) with an absolute License link, an "At a glance" 3x2 table whose cells restate claims the README already makes, and a figure under "How it works" (mermaid blocks stay). Design of record: handoff/round9/state/alt/design at 7bca8ab3. Only README.md, tests/layout.json and docs/img/readme/ change; no Python module, so every golden and both claim files are untouched.

The social preview is not tracked: tvofi uploads it under the repository settings from the generator's untracked output (social-preview.png; `HPO_SOCIAL_OUT` names where it lands).

## Head

0723471d0e5554d7c938ab5b7fb90398c3eb224b

## Mutation proof

n/a: the diff adds no production line; `python3 tests/mutation_table.py --scope changed --base origin/main` draws no mutant for a docs-only diff (its own docstring). The one check this change leans on is `tests/layout.py`'s dead-category arm, shown in Null control.

## Null control

- HACS rewriter, License badge line, base vs head: `python3 rw.py` (the `_HACS_LINK` regex of tests/entities.py applied to that line) finds 1 span at base (`[![License: MIT](https://img.shields.io/...)](LICENSE)`, so the rewrite takes the image src) and 0 at head.
- Generator: regenerating banner.svg, how-it-works.svg and how-it-works-dark.svg with make_readme_figures.py is byte-identical to the design of record's (`cmp` rc 0 on each).
- `python3 tests/layout.py` before the folder's glob and files: dead-category findings 27; after: 27 (the new glob matches tracked files). With the glob added and the files still untracked it read 28, naming `docs/img/readme/*`, which is the arm that would have refused a glob without files.

## Figures

- `python3 tests/entities.py`: ALL 1994 ENTITY CHECKS PASSED (base main 59c2543b: same command, run before the change, also passed)
- `python3 tests/doc_claims.py`: ALL 84 checks PASSED
- `node tests/md_tables.mjs`: doc_orphaned_table_rows=0, doc_misrendered_lines=0
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (no raise, no re-record)
- `python3 tests/layout.py`: before/after in Null control
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, names entities, doc_claims, layout, md_tables

## Red checks

none

## Forward-carry

none: R9-UI-4 regenerates docs/img/card-plan-chart.png and R9-RO-3 moves it, both already in their briefs; this PR leaves the pinned hero line untouched.

## Friction

none

## Approval

tests/layout.json is code-owned: tvofi's approving review is owed.
