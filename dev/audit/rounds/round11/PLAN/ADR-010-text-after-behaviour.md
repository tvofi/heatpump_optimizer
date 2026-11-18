# ADR-010: text is verified after the behaviour it states, and the comment criterion is cut by seam

Groups: `R11-SEAM-product-text`, `R11-SEAM-docs`, `R11-SEAM-governance-text`,
`R11-SEAM-comments-production`, `R11-SEAM-comments-tests`.

## Context

Fourteen groups change production behaviour, and several change a number a
string or a doc states (the Fahrenheit write, the capacity charge, the
two-zone default, restore on Off). Criterion C5 fails across production and
test comments with no detector (D5-s4-01, D5-s9-04); the rewrite touches every
hot file (tradeoff T22). The owner's rulings put verify groups after every
user-facing change and all comments in this round's scope.

## Decision

1. `R11-SEAM-product-text` runs after the behaviour groups whose strings it
   states; `R11-SEAM-docs` after those, the card and the product text.
2. The two comment groups run last on their files: after every production
   group, and after `R11-SEAM-tests`. Each first lands a sentence-length count
   as a ratchet, then pays it per file; a fixer may cut the XL group into
   parts by seam, one PR per part.
3. Comment-only PRs change no statement: `score.py --diff` reads NULL and the
   mutation ledger's pins are re-keyed, not re-triaged.
4. Policy files in `R11-SEAM-governance-text` merge serially on the owner's
   approving review.

## Alternatives

- Text beside each behaviour group: nine groups editing `strings.json` and
  the translations, and a doc verified against behaviour a later group moves.
- Comments early: every later behaviour group conflicts with a rewritten
  file.

## Consequences

- The comment groups end the critical chain; their XL size is the chain's
  largest uncertainty, and parts are the lever.
- Release notes for T7, T16 and T18 are written by the behaviour groups, not
  left to the docs group.

## Scenarios served

Usability and text truth, second and third scenarios (S21, S22, T21, T22).

## Move and fitness functions

Score-neutral. Acceptance: the text ledger's rows for the group's strings
verified; the D6 claims register re-run reads no false claim; a comment PR's
`score.py --diff` reads NULL and `tests/structure.py` is unchanged.
