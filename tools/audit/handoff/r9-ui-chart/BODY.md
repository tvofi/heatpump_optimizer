<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Fixes #1791 (lane UI, the last of R9-UI-1..4). Part of #201.

Before: the plan chart drew all seven series on one plot with four value axes (temperature and power on the left, price and an inner solar W/m² axis on the right), the plan editor's lanes sat over the bottom of that plot, and the series palette failed protanope and tritanope separation (house temperature against hot-water heating, hot-water heating against solar).

After: the chart is tvofi's concept A (D2): price, heating power and temperatures stacked as three panels inside the one chart svg each copy already had, on the one shared x-scale, each panel with its own y-scale, gridlines and unit; solar is a relative dashed curve in the price panel; the actioned band and the shared-step hatch sit in the power panel; the lanes sit under the bottom panel. The series colours are the palette of record (D3), light and dark, and the card test's colour-vision gate covers protanopia and tritanopia as well as deuteranopia, every pair of series in one panel, each theme's own colours (D4).

How: `chartPanels` cuts the plot height between the panels that have a visible series (`CHART_PANELS`); `renderChart`'s `scaleY` maps each value scale into its panel and `baseOf` gives areas and bars their panel's floor; everything that reads x (`scaleX`, `plotL`, `plotW`, `plotR`, the view window, the geometry's lane fields) is computed as before, so the lane editor's hit-test, pan, wheel and the inline and dialog copies are untouched. Series paint is `var(--hpo-series-<key>, <light>)`, the tokens declared by `tokenDeclarations` from `SERIES_DEFS`' `color`/`colorDark`; each panel is filled with `--hpo-plot` from the same darkMode switch, and the in-panel text uses `--hpo-ink`, so a theme that reports darkMode false on a dark card (Home Assistant does for any theme without `modes.dark`) still paints every series and label on the surface it was measured against (R9-UI-3's review lesson).

Design choices a check encodes (`fixer.md` step 11):
- the colour-vision pairs are the series drawn in one panel; series in different panels are not compared;
- protanopia by Viénot 1999 (the same reduced model the deuteranope arm uses), tritanopia by Machado 2009 at severity 1, because the reduced model has no tritan plane and the one-plane tritan shortcut collapses the dark temperature panel's green and blue (house `#1f9d1f` against outdoor `#4b95e8`) that Machado and the design's OKLab validator keep apart;
- the dash-where-close arm stays deuteranope-only, as before, now per panel and per theme;
- the C4 browser arm passes `darkMode: true` with HA's dark theme (what Home Assistant reports) and measures in-chart objects against their panel's painted fill; the mismatched pairings are measured by the new themeMismatch arm.

Deviations from `DESIGN.md` section 4, by the brief's "change only" list: no inline legend inside the svg (the legend chips already name every series and toggle it); the unit is written above each panel on the left rather than at the right end of a title row; the lane colours are unchanged (lanes are not in the brief's list).

Must keep working (review blocker), each pinned by a check that runs green at the head:

| item | pinned by |
|---|---|
| editor drag, resize, add, remove | `tests/card.mjs`: "dragging a slot moves it", "dragging an edge resizes the slot", "choosing add creates a slot", "choosing remove deletes it" |
| keyboard menu | `tests/card.mjs`: "Enter on a slot opens the slot menu" |
| edge auto-pan | `tests/card.mjs`: "a drag parks its handlers on window and arms the edge auto-pan" |
| 24 and 44 px targets | `tests/card_browser.mjs`: "every lane and slot target in the dialog clears 24 px on both sides", "every HTML control in the dialog clears 44 px under a coarse pointer" |
| apply_manual_plan and clear_manual_plan payloads | `tests/card.mjs`: "applying calls the manual plan service", "it sends both channels", "going back to automatic clears the override" |
| what-if simulate_plan and apply_schedule; draft wood slots in the wood lane | `tests/card.mjs`: "the simulator sends the dragged temperature", "the second press calls apply_schedule", "a 20:00-24:00 household reaches simulate_plan", "Wood lane renders one detected slot", "what-if wood editor when show_whatif" |
| hover crosshair across all panels, a tooltip row per series | `tests/card.mjs`: "the crosshair spans all three panels" (new), "the tooltip carries one row per drawn trace, all distinctly labelled" |
| pan, wheel zoom, view window, dialog copy | `tests/card.mjs`: "zooming in narrows the window", "panning backwards stops at the start of the plan", "zooming out stops at the extent of the plan", "two chart copies, two geometries" |
| 8 px font floor on a phone | `tests/card.mjs`: "a phone-width tile boosts the chart font to the floor"; `tests/card_browser.mjs`: "a phone-width tile renders axis text at or above the 8 px floor", "the expanded dialog holds the 8 px floor on a phone too" |

`card_drift.mjs` renders the payloads of `draft_mid_drag` and `tooltip_hover` (the drag and hover states) and both are claimed moved; the manual-plan and what-if payload checks above compare the service-call bodies, not markup.

Screenshots (illustrations, no figure derives from them), at the merge base and at the code head, Home Assistant's default themes, the tile at 900 and 375 px:

| | before (merge base 661d56f4) | after (code head 6277884f) |
|---|---|---|
| light, 900 px | ![before light 900](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/before-light-900.png) | ![after light 900](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/after-light-900.png) |
| light, 375 px | ![before light 375](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/before-light-375.png) | ![after light 375](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/after-light-375.png) |
| dark, 900 px | ![before dark 900](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/before-dark-900.png) | ![after dark 900](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/after-dark-900.png) |
| dark, 375 px | ![before dark 375](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/before-dark-375.png) | ![after dark 375](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/after-dark-375.png) |

Editor drag in the dialog at the code head (a hot-water slot dragged right; the lanes sit under the temperature panel):

![editor drag](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/3f6d4cae457aae6fea7fdf8486973222abc5fca3/tools/audit/handoff/r9-ui-chart/editor-drag.gif)

## Head

Code head `b7ab9278bf36c7df7b378a7722f3a55c9a8a78df` (the last commit that changes merged files; round 2 adds `b7ab9278` on round 1's `6277884f`, tests only). Above it sit transport commits only, under `tools/audit/handoff/r9-ui-chart/`: the screenshots and drag recording, and the commit that carries this body. None is in the code head's ancestry. Round 2 is on `handoff/r9-ui-chart-n6t27u-v2`, because round 1's branch carries its transport commits above `6277884f` and a fixer does not force-push.

## Mutation proof

Each mutant applied alone to the card at the code head in a scratch worktree, the named lane run, then restored.

| mutant | change | lane | checks that went red |
|---|---|---|---|
| M1 one panel | `chartPanels` returns a single panel spanning the plot | `node tests/card.mjs` | 6: the two "writes each panel's unit above its own frame" checks, "the crosshair spans all three panels", and three top-strip row checks |
| M2 lanes over the panel | the panels run to the plot bottom instead of `laneTop - laneInset` | `node tests/card.mjs` | "the lane strip sits under the bottom panel, on the tile and in the dialog" |
| M3 solar full height | `SOLAR_PANEL_SHARE` 1 | `node tests/card.mjs` | "solar is drawn in the price panel, topping out at its share of it" |
| M4 dark series = light | the dark series tokens take `color` | `node tests/card.mjs`; `node tests/card_browser.mjs` | card: "every series token carries its own theme's colour"; browser: "C4 every .series[data-key] clears 3:1 (HA dark theme)" and "R9-UI-4 chart series clear 3:1 and in-panel text 4.5:1 on their panel with light theme variables, darkMode true" |
| M5 panel on theme surface | the panel fill is `--card-background-color` instead of `--hpo-plot` | `node tests/card_browser.mjs` | both mismatched-theme "R9-UI-4 chart series clear 3:1 and in-panel text 4.5:1 on their panel" checks (the card lane cannot see paint, so it stays green on M5) |

Round 2 (`b7ab9278`), after the round-1 review found nothing pinned a mark to its panel: `panelEscapes()` in `tests/card.mjs` measures every series path and dot, the actioned band, the shared-step hatch, each estimated wash and each vertical grid rule against its panel's top..bottom, in three scenarios (estimated prices, shared steps, actioned slots), and refuses an empty sweep; a second check pins that an emptied panel is dropped. The reviewer's mutants, each applied alone, then `node tests/card.mjs`:

| mutant | change | checks that went red |
|---|---|---|
| MA | `baseOf` returns `plotB` | the three "stays inside its own panel" checks |
| MB | actioned band based at `plotB` | "stays inside its own panel (actioned slots, R9-UI-4)" |
| MC | shared-step hatch spans `plotT..plotB` | "stays inside its own panel" (estimated prices; shared steps) |
| MD | dark outdoor colour = dark house colour | the deuteranope, protanope and tritanope arms and the dash arm |
| ME | estimated wash in the first panel only | "stays inside its own panel (estimated prices, R9-UI-4)" |
| MF | now-temp label in the top strip | "no two of the three top-strip labels share a row" |
| MG | one full-height vertical grid rule | the three "stays inside its own panel" checks |
| MH | an emptied panel keeps its height | "an emptied panel is dropped and the others take its height" |

The colour-vision arms are the failing-first commit `65a40f4e` on the merge base's `SERIES_DEFS`: `node tests/card.mjs` at that commit prints `FAIL no two series in one panel are the same colour to a protanope (D4, #1791)` and `FAIL ... to a tritanope (D4, #1791)`, and the deuteranope arm passes.

## Null control

At the code head with no mutant: `node tests/card.mjs` ends `ALL CARD CHECKS PASSED`, `node tests/card_browser.mjs` ends `ALL BROWSER CHECKS PASSED`, and `node tests/card_drift.mjs 661d56f4950bba6c43907da6e0d8a9e503b54151` ends `39 state(s) moved and claimed, 1 identical`. At the failing-first commit the two new arms are red on today's palette while the deuteranope arm, which that palette was tuned against, is green, so the new arms are not vacuous.

## Figures

- "39 state(s) moved and claimed, 1 identical": `node tests/card_drift.mjs 661d56f4950bba6c43907da6e0d8a9e503b54151` at the code head.
- protanope dE 1.6 (hot-water heating against house temperature, light) and tritanope dE 5.2 (hot-water heating against solar, light) on the merge base's palette: `git checkout 65a40f4e && node tests/card.mjs`, the two FAIL detail lines.
- the MA..MH red checks: the reviewer's mutant script (each `str.replace` on the card file at the code head, then `node tests/card.mjs`, counting FAIL lines).
- "6 checks red" for M1 and the other mutant counts: the mutant applied by hand to `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` at the code head, then the lane named in the table, counting its FAIL lines.
- "MODE: SCOPED -- 11 script(s) run, 17 scoped out" and "13 TEST SCRIPT(S) PASSED": `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` at the code head.

## Red checks

none. Not run in this seat: the real-HA `ha_contract` (this container has no pinned Home Assistant; the diff touches no Python), `typing_ruler --mypy` (no Python 3.14.2 here; no Python module changed), and the 17 scripts the scoped gate placed outside this diff's closures.

## Forward-carry

none: no finding changes how a later stage must work. R9-RO-3 moves `docs/img/card-plan-chart.png` later; this PR regenerates it at its current path with the browser test's hero mode, as its brief says.

## Friction

none
