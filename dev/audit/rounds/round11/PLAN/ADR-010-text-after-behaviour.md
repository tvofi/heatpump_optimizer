# ADR-010: text is verified after the behaviour it states; comment style follows by file, not by edge

Groups: `R11-SEAM-product-text`, `R11-SEAM-docs`, `R11-SEAM-governance-text`,
`R11-SEAM-comments-production`, `R11-SEAM-comments-tests`.

## Context

Fourteen groups change production behaviour, and several change a number a
string or a doc states (the Fahrenheit write, the capacity charge, the
two-zone default, restore on Off). Criterion C5 fails across production and
test comments with no detector (D5-s4-01, D5-s9-04); the rewrite touches every
hot file (tradeoff T22). The owner's rulings put verify groups after every
user-facing change and all comments in this round's scope.

The two kinds of text differ. A string or a doc sentence states behaviour, so
verifying it before the behaviour merges verifies the wrong thing: that is a
prerequisite. Splitting a long comment sentence states nothing new; a
behaviour group that merges later conflicts with the rewritten lines, and
nothing else. That is a file order.

## Decision

1. `R11-SEAM-product-text` runs after the behaviour groups whose strings it
   states; `R11-SEAM-docs` after those, the card and the product text. These
   are edges.
2. The two comment groups carry **no edge**. Each first lands a
   sentence-length count as a ratchet, then pays it per file, in parts by
   seam, one PR per part. The part for a file is released when the last group
   in that file's row of `PLAN.md`'s hot-file order has merged.
3. A file no other group names is released at the first dispatch: 25 of the
   95 package modules and 42 of the 49 test scripts at the fork
   (`projection.py` reads the lists from the roster). The card's script
   carries 155 of D5-s4-01's units and is released after `R11-SEAM-card` and
   `R11-SEAM-product-text`, the two groups that edit it.
4. D5-s3-02's false docstring (`comfort_band.py`) states behaviour no group of
   this round changes; it goes in the first part.
5. Comment-only PRs change no statement: `score.py --diff` reads NULL and the
   mutation ledger's pins are re-keyed, not re-triaged.
6. Policy files in `R11-SEAM-governance-text` merge serially on the owner's
   approving review.

## Alternatives

- Edges from every production group into the comment group (this plan's first
  draft): sixteen edges whose only reason is a shared file, which
  `architect-planner.md` step 4 calls an order, and which put an XL group at
  the end of the critical chain for no dependency.
- Text beside each behaviour group: nine groups editing `strings.json` and
  the translations, and a doc verified against behaviour a later group moves.
- Comments early on hot files: every later behaviour group conflicts with a
  rewritten file.

## Consequences

- The critical chain by edges no longer ends in a comment group. The comment
  groups' last parts still wait for the last behaviour merge on their files;
  `projection.py` states that as the ORDERED figure beside the published one.
- Release notes for T7, T16 and T18 are written by the behaviour groups, not
  left to the docs group.

## Scenarios served

Usability and text truth, second and third scenarios (S21, S22, T21, T22).

## Move and fitness functions

Score-neutral. Acceptance: the text ledger's rows for the group's strings
verified; the D6 claims register re-run reads no false claim; a comment PR's
`score.py --diff` reads NULL and `tests/structure.py` is unchanged; a comment
part's diff touches no file whose row in the hot-file order still has an open
group.
