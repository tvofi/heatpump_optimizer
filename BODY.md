<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

R9-UX-2, lane UX (#1795, design of record `handoff/round9/state/alt/design/ux/DESIGN-UX.md` at 1a90e4cb, section UX-2). Part of #1795 and #201; the lane issue stays open for UX-3..7.

Before: the Advisor tab drew only the sensor ranking (`sensor_advisor`), so the money the other advisors publish, a missing sensor's monthly cost and a cheaper hot-water setpoint, never reached the card.

After: the Advisor tab opens with a "Worth doing" inbox ranked by monthly value, read from the three advisor sensors that are on by default (sensor gap, hot-water setpoint, valve target) and from the score sensor's `price_tiles` (price of a degree). Each row has at most one action, through a lane the card already owns: "Assign sensor" opens the Setup picker for the gap's top slot; "Open schedule" goes to the Plan tab's schedule editor; "Apply" on the valve target calls `assign_entity` with `entity_id: ""` and a manual setpoint (only when the valve is in manual mode); "Try in what-if" seeds the what-if comfort slider with the cooler tile's target and runs `simulate_plan`. A "More advice, once turned on" section offers wood-stove timing, fuse size and compressor frequency, and the price of a degree while its tiles are off, with "Open settings"; it never reads the disabled advisors. The empty, waiting (an `unknown` advisor's own `waiting_for`) and error ("This advice is unavailable right now") states are drawn. Today's sensor ranking and its assign flow follow, unchanged.

How. Module-level functions beside `advisorPageHtml` (`advisorRows`, `priceTiles`, `dhwCostPerDay`, `advisorInboxHtml`, `attachAdvisorInbox`, `advisorSignature`), no new host member. The advisor sensors join the render signature through `ADVISOR_SUFFIXES`; the score sensor, which carries the tiles, is already in `HEADLINE_SUFFIXES` and the `entities.py` reads list, so no new read is added. The hot-water monthly value is `(cost_per_day at the running setpoint − cost_per_day at the recommendation) × 30`, with `cost_per_day` interpolated linearly between the swept candidates (48..60 step 2) because the default setpoint, 55, is off the grid. The degree row's value is the cooler tile's saving (null when a cooler target costs more); the warmer tile's cost is in the detail. Valve rows carry no money and follow every priced row. Home Assistant hides extra attributes while an entity is `unavailable`, so that state reads only the state and draws the generic error; `unknown` keeps its attributes, which is where `waiting_for` lives. Strings are in `en` and `sv`. Only the card, its tests, its docs and fixtures change: no Python, no structure metric moves, no budget is touched.

Round 1 review fixed: (1) price of a degree is delivered from `price_tiles` (the first draft wrongly claimed no producer exists; `sensor.py` publishes it on the score sensor behind `price_tiles_enabled`, default off, so on a default install the row shows as "enable to see"); (2) the hot-water row is priced at an off-grid setpoint; (3) the ranking test uses an unordered fixture (build order gap, hot water, valve, degree; value order degree 90 > hot water 55 > gap 40 > valve); (4) the UX-5 carry is written into `carry-1795.json`; the survivors on gap value, already-at-recommendation and valve rounding are killed; waiting and error states no longer read attributes HA hides.

Departures from the brief, each deliberate:
- **"Open schedule" opens the Plan tab**, where the schedule editor is; it does not seed a value, since the editor holds the hot-water minimum, not the setpoint. UX-5 makes it an "Apply" (carried).
- **An opt-in row is offered even when that advisor is already on.** Telling the two apart needs a read of the sensor, which `tests/entities.py` refuses for a disabled-by-default one.
- **An unavailable advisor shows no reason.** HA drops the attributes there, so the card cannot know it; the earlier design read one that is never present.

Documentation (U5): `docs/dashboard-card.md` "The advisor page" is rewritten around the inbox and embeds the regenerated `advisor-light.png` and `advisor-dark.png` (`HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs`), replacing the hand-drawn figure. The page fixture in `tests/card_browser.mjs` gains the three advisor sensors and the score sensor's price tiles. The advisor pictures were regenerated again for the degree row. The other pages re-rendered with raster noise only and are left as they were. The product page's gallery is not on main (no `docs` gallery slot exists), so no slot is owed.

`tests/card_browser.mjs` is code-owned: this merges on tvofi's approving review at the head.

## Head

9cd195065146fcf457bf86d1d9d4d5cbcf4eabe8 (code head; `origin/main` 3bd6f122 merged in at e335ad27)

## Mutation proof

The card is not in `tests/mutation_table.py`'s production set, so no site is pinned. Hand mutants instead, each a one-line replace in the working tree at the code head, then `node tests/card.mjs` (`/tmp/ux2/mut.py`; rc 0 on the unmutated head). All 22 are killed, each by at least one named check:
- rank ascending; 7 days a month; valve threshold 5; Apply without the manual-mode guard; signature drops advisors; Apply payload `entity_id: "x"`; wood advisor added to `ADVISOR_SUFFIXES`; waiting branch removed; opt-in rows removed; assign opens the wrong key (the first ten, killed as in the first handoff).
- Round 1 additions, each killed by one named check: gap `>= 0` (`a sensor gap worth nothing is no row`); `to === from` guard removed (`a hot-water setpoint already at the recommendation is no row`); valve rounding to whole degrees (`the valve target rounds to the nearest half degree`); clamp 40 (`the valve target is clamped to 30 °C`); no interpolation (`the hot water at the off-grid default 55 is priced by interpolation`); degree saving sign flipped (ranking and `price of a degree`); warmer detail read from the cooler tile (`price of a degree`); unavailable no longer an error (`an unavailable advisor says so without reading any attribute`); degree seeds 21 not the tile target and degree does not run the simulation (both `Try in what-if seeds the what-if slider...`); degree opt-in always shown (`without price tiles the degree row is offered as enable-to-see`).
- The ranking mutant `rank ascending` is red on the unordered fixture, which the first fixture, already in descending build order, did not give.

Failing test first for the original work: commit 9bc74be9 (tests only) against main's card.

## Null control

- The unmutated head: `node tests/card.mjs` rc 0, `ALL CARD CHECKS PASSED`, which is what the M-list is read against.
- `tests/card_drift.mjs` at the merge base: 39 states moved and claimed, 1 identical (`editor_schema`). Every moved state moves through the one stylesheet; `advisor_page` also moves in markup. A scan of the diff lines of the other 38 for anything that is not an `adv-` rule found none; the claims in `tests/golden/card_claimed_drift.txt` say which is which.
- Ranking null: the three-row fixture has a 180, a 45 and an unpriced row; M1 reverses it and the check goes red, so the ranking check is not satisfied by any order.

## Figures

- `node tests/card.mjs`: ALL CARD CHECKS PASSED at 9cd19506. `node tests/card_drift.mjs`: "39 state(s) moved and claimed, 1 identical". `node tests/card_browser.mjs` (page screenshots to a scratch directory, advisor pictures copied): ALL BROWSER CHECKS PASSED, 71 ok.
- Scoped gate selection: "MODE: SCOPED -- 11 script(s) run, 17 scoped out", at 9cd19506 with `GOLDEN_MODE=drift`: all eleven pass (`entities`, `features`, `harness_headers` re-run on their own after a first pass was missing `yaml` in the seat's venv; rc 0). `tests/stress.py` is not in the selection. `structure.py` passes; `brief_lint.mjs` exits 0.
- Hot-water figure: cost(55) interpolated 10.85, cost(48) 9.00, 1.85 × 30 ≈ 55 a month; the degree row is the fixture's own -90 tile, so 90. Both are fixture figures, shown with "≈".

## Red checks

Two local reds, neither on a pushed commit's CI:
- `card_browser.mjs` "P9 grid: every visible text run clears WCAG AA": the new button's accent colour, 2.09:1 against 4.5. Cheaper detector: none; the rendered pixel contrast is only measurable in the browser, which is the gate that found it. Fixed before the push that carried the stylesheet.
- `harness_headers.py` "the executed harnesses leave their committed output byte-identical": the D6 link and image counts moved with the embed. The detector is already seconds-cheap; the fix is the regenerated `tools/audit/round4/D6/` in the same commit.

## Forward-carry

`.claude/workflows/carry-1795.json`, stage R9-UX-5 (hot-water row becomes an apply action): the file now carries it (second entry, effect `removes`): the hot-water row's `open_schedule` becomes a service call writing the recommended setpoint and the Plan-page fallback goes; `node .claude/workflows/brief_lint.mjs` accepts the file. Price of a degree is delivered here, so no later stage owes it. The roster's R9-UX-5 brief on handoff/audit-r9-fixplan should carry the same text; sent to the coordinator.

## Friction

- fixer.md-2: unclear: `mutation_table.py --scope changed` has no JavaScript sites, so a card-only PR's mutation proof is hand-run and nothing pins it; the M-list above is that proof.
- fixer.md-5: cost: this cloud seat has no Python 3.14 or Home Assistant, so typing and real-HA `ha_contract` are unrun; no Python changed and CI is their authority.
