# Proposal triage, session s7, batch 59 (P273)

The rolling batch (V182) after batch 58 (#2934, merge-verdicted at
`56e61dc9edbb61c293b22254928ad8e1548b1bb6`). Facts were read at origin/main
`b0b2d7697f8c5baaef2c082d9bf3242b57249e68`.

## P273: card docs may still show the pre-R10-CARD-VOICE setup drawing

Verdict: REJECT. The measurement the proposal asks for comes first, and this seat took it. It
finds no drift, so the size-S docs fly-in would have nothing to change.

Source: `proposals.md` V185 (orchestrator, 2026-10-28T22:00Z). It cites item 4 of "Decisions for
the owner" in the card-symbols pre-study, `docs/design/card-symbols/NOTES.md` on
`probe/card-symbols-design` `2cc4d5ebc89657e4103c09447fc2d0e4c7adfe40`: "the docs/figure drift in
`docs/dashboard-card.md` and `docs/img/model/` (they still show the coil spring and the line-art
silhouettes)".

Instances:
- **The premise predates the fix.** The pre-study commit is dated 2026-10-20T15:17:11+02:00 and
  does not contain #2841 (`git merge-base --is-ancestor 75ac45353 2cc4d5ebc` is false). #2841
  merged on 2026-10-26 as `75ac453534e10c0a6ef88533ad5ff375cd6ca333`, and its own diff rewrites
  `docs/dashboard-card.md` (44 lines) and all three `docs/img/model/hydronic-*.svg`
  (`git show --stat 75ac45353`).
- **The spring is the shipped design, not a leftover.** In the card at main, the wood tank's type
  disc "is the coil's spring while a coil is configured in it, dimmed while that coil is not
  modelled" (`heatpump-optimizer-card.js:4002-4008`, glyph `SETUP_BADGE_GLYPH.coil`). The pipe
  of a configured but unmodelled coil is drawn dashed (`:3796`). So the four `spring` hits that
  V185 counts (`docs/dashboard-card.md:737-772`) describe what ships: the spring, its dimming,
  and the dashed pipe.
- **The silhouettes are gone from the figures.** The only `silhouette` match in each
  `hydronic-*.svg` is the card's own inlined comment saying the hand-drawn silhouettes were
  replaced (`heatpump-optimizer-card.js:4719`). No silhouette is drawn.
- **The figures equal the shipped card's render.** `tests/setup_qa_render.mjs` was run on a
  `git archive` of origin/main, with `HPO_QA_OUTDIR`/`HPO_QA_PREFIX=hydronic-`. All three outputs
  are byte-identical (`cmp`) to the committed `docs/img/model/hydronic-{coil,single-buffer,two-tank}.svg`.
  They were last regenerated in `c62c56cb5` ("regenerate the setup figures"). Three card commits
  landed after it, none in the setup drawing: `99367cbc3` (a receipt string), `c89e5b5db` (house
  grade), `59c744f4c` (a pop-up CSS comment).
- **Control.** The comparison can fail. In the archived copy, the coil glyph's arc
  `c1.3-2.9 2.6-2.9 3.9 0` was changed to `c1.3-2.0 2.6-2.0 3.9 0` and the figures were
  re-rendered. `hydronic-coil.svg` then differs (2 lines) while the two figures without a coil
  stay identical, which is exactly where the spring is drawn.

Cost: none further. A fly-in would cost a fixer seat and a review seat to land an empty diff.

Binding: the measurement refutes the premise. There is nothing to fix.

Residual, not a proposal: `docs/` is INERT in `tests/closure.py`, so a future change to the setup
drawing selects nothing that re-renders these figures. `tests/card_drift.mjs`'s header already
names that gap (#558 C2/C3), and `tests/setup_qa_render.mjs` names the hand-drawn case (#558 B9). This ruling takes no position on it.
