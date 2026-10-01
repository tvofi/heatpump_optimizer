<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the stat tiles and the savings/score tiles were four columns whenever the viewport was wider than the phone breakpoint. On a wide macOS Safari window with the card in a narrow dashboard column, each tile was a sliver and `overflow-wrap: anywhere` broke units and values mid-word ("SEK/k Wh", "45/10 0"). The expanded dialog's Plan page showed no tiles at all.

After: both rows are two tiles across at every width, as the round-9 mockup draws them (`handoff/round9/state/alt/design/assets/card/after-dark-375.png` on `handoff/audit-r9-alt`), and values wrap only between words (`overflow-wrap: break-word`). The Plan page opens with the same tile and headline rows above its chart; the score toggle is wired on both copies.

How: `cardStyleBlock` sets `repeat(2, …)` on `.tiles` and `.hl-stats` and drops the phone media rule's column override; `_render` builds the tile and headline markup once and places it on the card and at the top of the plan page body; the score wiring iterates `querySelectorAll`. `docs/dashboard-card.md` and its tile and plan pictures (regenerated with `HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs`) follow. The legend chips, which also wrap at that width for the same viewport-keyed reason, are out of scope here.

## Head

73028145f27d5460892ad1b975c837a562278973

## Mutation proof

Two new `tests/card.mjs` checks, each red on its own mutant and green on the head:

- `.tiles` back to `repeat(4, …)`: `FAIL  tiles: the tile and headline rows are two across outside any media rule`
- `${stats}` removed from the plan page body: `FAIL  tiles: the expanded Plan page shows the four tiles above its chart`

## Null control

On the merge base the expanded plan page renders no `data-tile`, and the card's `.tiles` rule reads `repeat(4, minmax(0, 1fr))`; the first new check fails there for the same reason as the first mutant.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
