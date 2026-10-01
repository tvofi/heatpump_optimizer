<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

R9-UX-1, lane UX (#1795, design of record `handoff/round9/state/alt/design/ux/DESIGN-UX.md` at 1a90e4cb, section UX-1). Part of #1795 and #201; the lane issue stays open for UX-2..7.

Before: the card's headline showed only the first line of the plan narrative, and hovering an idle step showed its values and no reason, because `reasonHtml` skips idle steps on purpose.

After: the headline lists every line the narrative sensor publishes, in its own order (by spend, then the idle hours). Hovering a step where a channel is not heating adds a block that says why the plan likely left it idle, under "Likely because", from the published per-step fields only: the step's price rank within the horizon (only when it is in the dearer half), the run it coasts on, that channel's next run, the tank against the published `dhw_min_temperature` (only when above it, and only when published), and the solar surplus ahead (`pv_surplus`). Nothing about the room floor or a fuse cap is said, as the design requires. Both channels idle at one step share one block and one price line.

How. `idleWhyHtml(rows, ctx)` is a module-level function beside `reasonHtml`, fed by `_onPointerMove` from `plan.forecastOf("space"|"dhw")`, `plan.attr("dhw_min_temperature", null)` and `plan.priceUnit()`; `tooltipHtml` takes it as a second argument. A step counts as running above 0.05 kW, the threshold `sharedTooltipHtml` already uses. The tooltip now flips left of the crosshair past mid-width by its own measured width (it flipped at 60 % by an assumed 160 px), and `fitWhy` keeps it inside the chart's height by dropping the explanation's last lines, then the block, never a value row. Strings are in `en` and `sv`.

Two departures from the design, both deliberate:
- No footer with the house and outdoor temperatures: they are already the tooltip's own rows (House temperature, Outdoor temperature), and repeating them made the box taller than a 400 px card's chart.
- The box is shortened rather than clipped on a small chart. A first cut capped it with `max-height` and `overflow: hidden`; `tests/card_browser.mjs`'s P9 check "no text is clipped where its ancestor cannot scroll to it" went red on the explanation's lines in the `tooltip_hover` cell, so the clip is refused by the tree's own barrier. The P9 pop-up check now also holds a tooltip inside its chart's height (it bounded it horizontally only), which is what the design's "stays inside the chart" means.

Documentation (U5): `docs/dashboard-card.md` gains "Why a step is idle" with the new idle-hover screenshot, and its headline and hover paragraphs say what the card now shows. The page-screenshot mode gains a `plan-why` view (the Plan page with the pointer on the fixture's dearest idle step) and checks that its tooltip explains the step and stays inside the chart. The page fixture's narrative lines are `narrative.render`'s English output for `plan_view.py`'s plan. Only the tile (narrative lines) and the two new `plan-why` pictures are committed; the plan, setup, savings and advisor pages re-rendered with raster noise only and are left as they were. The product page's gallery (R9-WEB-1) is not on main, so no gallery slot is owed.

`tests/card_browser.mjs` is code-owned: this merges on tvofi's approving review at the head.

## Head

8f30964f

## Mutation proof

The card is not in `tests/mutation_table.py`'s production set: `python tests/mutation_table.py --scope changed --base origin/main` prints "no production file in scope; nothing to mutate", so no site is added and no pin is owed. Hand mutants instead, each a one-line replace in a detached worktree at the head, then `HPO_PLANDATA=<plan_view.py payload> node tests/card.mjs`, failing check names read out of the output:

- M0 null (comment only): rc 0, failing 0
- M1 headline shows first line only: rc 1, failing 2
  - `headline shows every narrative line`
  - `headline keeps the narrative's order`
- M2 no idle explanation: rc 1, failing 11 (the first six shown)
  - `UX-1 an idle step is explained, as an inference`
  - `UX-1 the explanation names the step's own quarter hour`
  - `UX-1 a dear idle step gives its price rank within the horizon`
  - `UX-1 it names the run it coasts on and the next run`
  - `UX-1 it names the solar surplus ahead`
  - `UX-1 both channels idle share one block and one price line`
- M3 price line for every idle step: rc 1, failing 1
  - `UX-1 a step in the cheaper half claims no price reason`
- M4 tank line below the minimum too: rc 1, failing 1
  - `UX-1 no tank line when the tank is below the minimum`
- M5 hover does not pass the explanation: rc 1, failing 3
  - `UX-1 hovering the fixture's dearest idle step explains it`
  - `UX-1 hovering an idle hot-water step names its own coast and next run`
  - `UX-1 and compares the tank with the published minimum`
- M6 flip assumes a 160 px box: rc 1, failing 2
  - `UX-1 past mid-width the tooltip sits wholly left of the crosshair`
  - `UX-1 at 55 % of the width the tooltip already sits left of the crosshair`
- M7 fitWhy never shortens: rc 1, failing 2
  - `UX-1 on a short chart the explanation loses its last lines, not its value rows`
  - `UX-1 and is dropped whole when not even one line fits`
- M8 fitWhy keeps an empty block: rc 1, failing 1
  - `UX-1 and is dropped whole when not even one line fits`
- M10 hover does not fit the box: rc 0, failing 0
- M9 active steps explained too: rc 1, failing 1
  - `UX-1 a running step with no published reason is not explained`
- R2 hover reads `dhw_min_temp`: rc 1, failing 1
  - `UX-1 and compares the tank with the published minimum`
- R3 hover passes the space forecast as `dhw`: rc 1, failing 2
  - `UX-1 hovering an idle hot-water step names its own coast and next run`
  - `UX-1 and compares the tank with the published minimum`
- R6 flip at 60 % (main's threshold): rc 1, failing 1
  - `UX-1 at 55 % of the width the tooltip already sits left of the crosshair`
- R9 narrative lines reversed: rc 1, failing 1
  - `headline keeps the narrative's order`

R2, R3, R6 and R9 are the round-1 review's survivors at 57eeaa6d; the checks that kill them were added at 7fc5d3fa: a hover at 55 % of the width, a real hover on the fixture's warmest idle hot-water step past the first quarter with `dhw_min_temperature` published 5 °C below its tank, and an order check on the headline. R10 (tank line on the space channel) is equivalent: the space forecast carries no `dhw_temp`.

M10 (the hover does not call `fitWhy`) has no Node detector: the test DOM has no layout. Its detector is the browser: with M10 applied, `node tests/card_browser.mjs` fails "P9 grid: no pop-up leaves the viewport or its chart" (`div.tooltip` up to 72.7px outside, 10 findings), the vertical arm this PR adds; it is the only browser check that goes red.

Failing test first: the head's `tests/card.mjs` against main's card file stops with `ReferenceError: idleWhyHtml is not defined`; M1 is the headline pin red against the first-line-only rendering main ships.

## Null control

- M0, a comment appended to the `WHY_RUNNING_KW` line, leaves `tests/card.mjs` green (rc 0, no FAIL), so the mutant runs above are read against a harness that passes on an unbroken card.
- `tests/card_drift.mjs` at the merge base: 39 states moved and claimed, 1 identical. All 39 move through the one stylesheet every state carries; three also move in DOM (score_open's headline list, tooltip_hover's explanation, shared_steps_hover's tooltip left), each named in `tests/golden/card_claimed_drift.txt`.
- The P9 clip refusal and its control: the grid red with `overflow: hidden` on the tooltip (code commit f2e1311e's card), green with `fitWhy` at the head.

## Figures

- `node tests/card.mjs`: ALL CARD CHECKS PASSED at 8f30964f (7fc5d3fa merged with main d536fb4d, the v6.7.13 stamp; the claim file keeps main's header at `claims-for: 6.7.13` and restates this branch's claims).
- `node tests/card_drift.mjs $(git merge-base origin/main HEAD)` at 8f30964f (merge base d536fb4d): "39 state(s) moved and claimed, 1 identical".
- `NODE_PATH=<playwright> node tests/card_browser.mjs`: ALL BROWSER CHECKS PASSED at 8f30964f, P9 grid MODE: FULL, including "P9 grid: no pop-up leaves the viewport or its chart", "P9 grid: no text is clipped where its ancestor cannot scroll to it", "R9-UX-1 the idle-step hover explains the step and stays inside the chart" (light, dark) and the U5 page check (12 pictures).
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at 8f30964f: "MODE: SCOPED -- 11 script(s) run, 17 scoped out", "13 TEST SCRIPT(S) PASSED; 16 SCOPED OUT AND NOT RUN". Python 3.13 venv from `tests/requirements-ci.txt`, not the pinned 3.14.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (no Python changed; the card has no structure metric).
- `node .claude/workflows/brief_lint.mjs`: TOTAL: 0 error(s), `carry-1795.json` 0 errors.
- The idle-step example in the docs picture, from the repository fixture: 16:00, 2.85 SEK/kWh, among the dearest 17 % of the plan (cheapest 0.62), coasting on 00:00-05:00, next run 23:00 at 0.78; this is `idleWhyHtml` on `plan_view.py`'s plan, and the design's mockup predicted the same numbers.

## Red checks

none

## Forward-carry

`.claude/workflows/carry-1795.json`, stage R9-UX-5 (exact idle sub-codes go into the same tooltip): the tooltip may not clip text, it must stay inside its chart's height, and sub-codes replace the likely-because lines in `idleWhyHtml` with `fitWhy` omitting what does not fit. The roster's R9-UX-5 brief on handoff/audit-r9-fixplan should carry the same text; sent to the coordinator to add.

## Friction

- fixer.md-5: cost: this cloud seat has no Python 3.14 or Home Assistant, so typing (mypy) and real-HA `ha_contract` are unrun here; both are out of this diff's scope (no Python changed) and CI is their authority.
- fixer.md-2: unclear: `mutation_table.py --scope changed` has no JavaScript sites, so a card-only PR's mutation proof is hand-run and nothing pins it; the M-list above is that proof.
