R9-UI-3 (lane UI, #1791 D1 and D2b): the dashboard card's visual system, the
design of record's section 3 (`handoff/round9/state/alt/design/DESIGN.md`).
One `--hpo-` token layer, the dusk mark and a status pill in the header, four
stat tiles, compact legend chips with the dashed-line sentence as a footnote,
and lighter price and solar fills. It changes what the card draws on every
state but the editor schema; it changes no plan, no service call and no
backend file. Part of #1791; UI-4 carries concept A, the palette and the
protan/tritan work (D2, D3, D4), and D5 (no plan-lock change) is honoured by
touching no lock path.

_Requested by **tvofi**_

### What changed

- **Token layer.** `CARD_TOKENS` and `CARD_SCALE_TOKENS` are declared once on
  `:host` inside `cardStyleBlock(darkMode)`. A token that stands for a Home
  Assistant variable is declared as `var(<ha-var>, <literal>)`, one var() level
  deep, so a theme still wins; the rest are literals. The stylesheet's hex
  literals now resolve through the tokens, which folds the three divider
  greys and two text greys the literals had drifted to into one value per role.
  Light and dark are picked from `hass.themes.darkMode`, as the D4-s1-01
  colours already are; `themeFallbacks()` swaps each use site's light fallback
  for the dark literal. Left as they were: `--error-color`,
  `--secondary-background-color` and the slot hit-rect's `#fff`, whose values
  carry their own measured contrast rules.
  The tiles, the headline stats and the idle pill sit on `--hpo-surface-2`,
  a literal switched by `darkMode`, so their text comes from `--hpo-ink` and
  `--hpo-ink-2`, literals switched by the same flag, and never from the HA
  theme's own text colour. Home Assistant reports `darkMode` false for any
  theme without a dark mode, so a community dark theme would otherwise paint
  its light text on the light surface (round 1 measured 1.24:1).
- **Header.** The dusk mark (one inline SVG, `aria-hidden`) before the title,
  and a status pill after it: *Manual plan until HH:MM*, *Fallback: pump's own
  curve*, *Plan stale*, *Heating now*, *Idle*, in that precedence. No plan
  sensor at all draws no pill.
- **Stat tiles.** Price now, planned heating, plan cost and indoor
  temperature, in a grid of four that folds to two by two under 600 px. The
  savings and score items keep their row and their sensors and are restyled as
  tiles; the narrative line is unchanged.
- **Legend.** Compact pill chips that keep the 24 px target (44 px on a
  coarse pointer), wrapped in a `legend-chips` span, one scrolling row on a
  phone; the dashed-line sentence is a footnote under them.
- **Fills.** The price area at 16% and the solar area at 10%; every other
  filled series keeps 18%.
- **U5.** `tests/card_browser.mjs` gains a page-screenshot mode,
  `HPO_PAGES_OUT=docs/img/card`, that writes the tile and the Plan, Setup,
  Savings and Advisor pages in light and dark; `docs/dashboard-card.md`
  describes the header, the pill states, the tiles and the legend with them,
  and the Plan and Savings sections carry their page. The README hero
  `docs/img/card-plan-chart.png` is re-taken because the tile row changes it.

### Design decisions a reviewer should check

1. **"Planned heating", not "Planned heat".** The tile sums the plan
   sensors' `total_energy_kwh`, which is the electricity the heat pump draws
   (`total_cost` is that energy times the price), not delivered heat. The
   label says heating and the tile's hover text says it is electricity.
2. **Stale mirrors the coordinator's rule.** `_plan_is_stale` calls a plan
   stale past `max(3 x interval, 90 min)`. The card reads the age from the
   `last_optimization` sensor and the interval from `next_optimization`'s
   state minus its `last_changed` (the coordinator sets it to now + interval
   on every cycle), falling back to the 30 min default outside (0, 1440] min.
3. **Fallback is "no plan" on every available plan sensor.** That is the
   state the plan sensors publish when no plan exists, and the case in which
   the integration actuates nothing. One sensor still planning is not
   fallback.
4. **The pill joins the re-render signature with its key and text**, so a
   plan crossing the stale limit redraws with no sensor changing; the indoor
   sensor's state and `last_updated` join `headlineSignature`, so the indoor
   tile refreshes on its own.
5. **`<span class="legend-chips">`, not a `<div>`.** `tests/card.mjs`'s
   legend helpers slice from `<div class="legend">` to the first `</div>`; a
   span keeps every existing legend check measuring the chips it always did.
6. **No host member added.** Every new piece is a module-level pure function
   (`tilesHtml`, `statusPill`, `planAge`, `priceNow`, `planTotal`,
   `indoorState`), so `HOST_MEMBER_CEILING` (26) stands.

### Screenshots

Taken by `tools/audit/handoff/r9-ui-card/shots.mjs` from the shipped card at
the merge base (before) and the head (after), at 900 and 375 px, against the
solved plan the card tests use. In the tree:
`tools/audit/handoff/r9-ui-card/{before,after}-{light,dark}-{900,375}.png`.

| | light | dark |
|---|---|---|
| before, 900 px | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/before-light-900.png?raw=true) | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/before-dark-900.png?raw=true) |
| after, 900 px | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/after-light-900.png?raw=true) | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/after-dark-900.png?raw=true) |
| before, 375 px | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/before-light-375.png?raw=true) | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/before-dark-375.png?raw=true) |
| after, 375 px | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/after-light-375.png?raw=true) | ![](https://github.com/tvofi/heatpump_optimizer/blob/531006792f4df9c1e1a65416a5936128dba9ece2/tools/audit/handoff/r9-ui-card/after-dark-375.png?raw=true) |

The page screenshots are in `docs/img/card/`.

### Round 2 (review of a0fe0243 blocked on theme-contrast)

The reviewer measured the tile value and the headline value at 1.24:1, and
the tile labels, units, headline label and idle pill at 2.63:1, under a dark
theme with no dark mode (`darkMode` false). The fix re-points `--hpo-text`
and `--hpo-text-2` at the ink literals inside `.tile` and `.hl-stat`, and
gives the idle pill `--hpo-ink-2`. `tests/card_browser.mjs` gains
`themeMismatch`, which renders the card with dark theme variables and
`darkMode` false, and with light variables and `darkMode` true, and measures
every text run on a tile, a headline stat and the pill against what it is
painted on. Run with this head's test file against the a0fe0243 card, both
checks fail (dark mismatch: idle pill, tile labels and units 2.63:1, tile
value 1.24:1; light mismatch: 3.01:1 and 1.11:1). At this head both pass,
and so does the rest of the browser lane. `card_drift` still reports 39
moved and claimed, 1 identical. The code head is a0fe0243 plus this one
commit; a merge commit carries it under the transport tip, so no
transport file is in the code head's ancestry.

### Checks run, and what was not

Run at the code head, all green: `node tests/card.mjs`;
`HPO_BROWSER_SCOPE=full node tests/card_browser.mjs` (the P9 grid, 306
cells, with three new pill cells: idle with the indoor tile, stale and
fallback); `node tests/card_drift.mjs origin/main`; `python3
tests/structure.py`; `python3 tests/entities.py` (with `tests/hastub` on `PYTHONPATH`, as `run.sh` sets it); `python3 tests/doc_claims.py`; `node .claude/workflows/brief_lint.mjs`; `tools/audit/prepr.sh` on this body.

The browser lane's D4-04 empty-state check now clips each element by its
scrolling ancestors before it measures spill: the phone legend is one
scrolling row, so a chip scrolled past the edge is inside its scroller and
paints nothing outside the card. The card box itself is never treated as a
clipper, so the check still measures what it was written for.

Not run: `typing_ruler` and the real-HA `ha_contract` (this cloud seat has no
Python 3.14 with the pins; no Python changed, so neither has a site here);
`tests/stress.py` and the full gate are left to CI.

## Head

dfe4d53cb355f3637449ab61d52bcf7928bd32e0 (code head). Everything below was measured there; the
transport commit above it adds only `tools/audit/handoff/r9-ui-card/`.

## Mutation proof

`tests/mutation_table.py --scope changed --base f67f598a --pin-killed`
prints `no production code line added or modified against the base` and
`PIN KILLED: nothing to pin`: it measures Python sites, and this diff changes
no Python. The card's JS is proven by hand instead:
`python3 tools/audit/handoff/r9-ui-card/js_mutants.py` breaks one seam per
mutant and runs `tests/card.mjs`.

| mutant | result | first check that goes red |
|---|---|---|
| headline drops indoor | killed (1 red) | UI-3 tiles: an indoor sensor change alone re-renders the indoor tile |
| _signature drops statusSignature | killed (1 red) | UI-3 pill: crossing the stale limit redraws with no sensor changing |
| stale floor 90->60 | killed (1 red) | UI-3 pill: a plan solved 80 min ago is inside the 90 min floor, not stale |
| stale intervals 3->1 | killed (1 red) | UI-3 pill: the stale limit scales with the published solve interval |
| interval estimate ignored | killed (1 red) | UI-3 pill: the stale limit scales with the published solve interval |
| stale > to < | killed (4 red) | UI-3 pill: a plan last solved 4 h ago, past max(3 x 30 min, 90 min), reads stale |
| fallback every->some | killed (1 red) | UI-3 pill: one plan sensor still planning is not fallback |
| fallback after stale | killed (1 red) | UI-3 pill: no plan on either sensor reads fallback, ahead of stale |
| heating some->every | killed (1 red) | UI-3 pill: a plan step active now reads heating |
| manual ignored | killed (1 red) | UI-3 pill: a manual plan reads 'Manual plan until |
| themeFallbacks identity | killed (1 red) | UI-3 tokens: no use site in dark mode keeps a light text or surface fallback |
| dark surface literal | killed (3 red) | UI-3 tokens (dark): pill, tile and text pairs clear 4.5:1 on the literals |
| indoorValue null | killed (5 red) | a live indoor reading shows the corner now temperature, without a second 'now' |
| cost tile reads energy | killed (1 red) | UI-3 tiles: plan cost sums both plans' cost |
| show_stats ignored | killed (1 red) | UI-3 tiles: show_stats: false draws no tile row |
| price area 0.16->0.18 | killed (1 red) | UI-3 fills: the price area is drawn at 16% and the solar area at 10% |
| solar area 0.1->0.18 | killed (1 red) | UI-3 fills: the price area is drawn at 16% and the solar area at 10% |
| tile order swap | killed (1 red) | UI-3 tiles: price now, planned heating, plan cost and indoor, in that order |

The first test set let four of these survive (the pill dropped from
`_signature`, the 90 min floor at 60, fallback on `some` instead of `every`,
both fill opacities); each has a check now that kills it.

Failing tests first: the 25 new `UI-3` checks in `tests/card.mjs`, run
against the merge base's card (`f67f598a`), fail 20 and pass 5. The 5 are
absence checks that the base passes for want of the thing they inspect: no
pill without a plan sensor, no tile row with `show_stats: false`, and three
token-shape checks with no tokens on the base to inspect.

## Null control

`node tests/card_drift.mjs origin/main` on the unmodified tree prints every
state identical; on the head it prints `39 state(s) moved and claimed, 1
identical` (`editor_schema`), and every moved state is claimed in
`tests/golden/card_claimed_drift.txt` for this diff, replacing the F6.4
claims the branch inherited from main. `tests/golden/claimed_drift.txt` is
untouched.

## Figures

- 39 moved and claimed card states, 1 identical: `node tests/card_drift.mjs origin/main`
- 20 of the 25 new card checks red at the merge base: `tests/card.mjs` from the head, run in a worktree at `f67f598a`
- 2 of 2 theme-mismatch checks red at a0fe0243 and green at this head: `HPO_BROWSER_SCOPE=full node tests/card_browser.mjs`
- 18 of 18 card mutants killed: stated without a command, because its driver is evidence and not code. It rests on the table under ## Mutation proof, printed by the driver `js_mutants.py` that transport commit 53100679 adds under tools/audit/handoff/r9-ui-card/, run from the repository root of a tree at the code head.

## Red checks

none

## Forward-carry

none

## Friction

none
