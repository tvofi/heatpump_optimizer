# Design of record: identity, card visual system, plan chart, README graphics (lane UI)

Commissioned by tvofi on 2026-09-29 ("propose professional looking graphic design elements for the integration, the card
and the readme"; brand direction: a new identity). Decided by tvofi on 2026-09-30. Measured against origin/main
`48786f65` (v6.7.12). This folder is the design of record the rev-4 roster's lane UI (R9-UI-1..4) cites. Nothing here is
production code: the scripts render and measure the proposal, and a fixer re-implements it in the card and re-measures
at its own merge base.

The proposal as tvofi saw it: https://claude.ai/artifact/1b27QyporrvqKN6Zjm5NEg (private showcase page) and the Figma file
https://www.figma.com/design/qczGAP3b0RCXHuYJwPsKUL (pages "Brand & tokens", "Card", "README"; colour variables in
`hpo / color / light`, `hpo / color / dark`, `hpo / dimension`).

## 1. Decisions (tvofi, 2026-09-30)

| # | question | answer, in tvofi's words where given | where it lands |
|---|---|---|---|
| D1 | primary mark | "dusk" | R9-UI-1 (brand), R9-UI-3 (card header) |
| D2 | plan chart layout | "A, make sure the plan editor and what-if-simulator still works" | R9-UI-4 |
| D2b | stat tiles | "include a forth, indoor temperature, stat tile" | R9-UI-3 |
| D3 | series palette | "adopt" | R9-UI-4 |
| D4 | colour-vision gate | "agreed": extend the card test from deuteranopia to protanopia and tritanopia | R9-UI-4 |
| D5 | lock a manual plan for the full horizon | asked, then withdrawn: "didn't know 20h was already locked. If slots can not automatically be changed during that window, no change is needed" | no group; see section 6 |

## 2. Identity (D1)

- **Mark "dusk":** a price line that steps down through the cheap hours, with the heat pooled in the lowest step. It sits
  on a 48-unit lattice. Line path `M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42`, stroke 3.6, round caps and joins; pool
  `M20 22 V26 H27 V35 H36 V22 Z`. Masters in `assets/svg/` (mark, app tile, inline and stacked lockups, light and dark).
- **Colours:** fjord `#026aa8` (5.79:1 on white) is the line on light, glacier `#4fb3f0` (7.34:1 on `#1c1c1c`) the line on
  dark, and ember `#d2601f` the heat (a graphic colour: 3.87:1 on white, 4.41:1 on `#1c1c1c`, above the 3:1 rule for
  marks). Ember as small text is `#b4501a` on light (5.12:1) and `#f08a3c` on dark ink (6.48:1). Ink `#0f2233`, frost
  `#f3f8fc`, slate `#5b6b7a`, mist `#9fb3c4`.
- **Wordmark:** Outfit (OFL), outlined to paths by `brand.py`, so nothing needs installing.
- **Home Assistant brand set** (`assets/brand/`): `icon.png` 256², `icon@2x.png` 512², `dark_icon.png`, `dark_icon@2x.png`,
  `logo.png` 558×130, `logo@2x.png` 1116×259, `dark_logo.png`, `dark_logo@2x.png`. All are transparent and trimmed; the
  logo's shortest side is inside the 128–256 range. They replace
  `custom_components/heatpump_optimizer/brand/icon.png` and `logo.png` (today one 256 px square on an opaque grey
  ground). `custom_components/heatpump_optimizer/icon.png` becomes the 512 px icon, and the root `icon.png` stays
  byte-identical to it, because R9-RO-4 deletes the root copy on exactly that premise.

## 3. Card visual system (R9-UI-3)

Renders: `assets/card/before-*.png` and `after-*.png` (light and dark, 900 px and 375 px), made from the real card with
the repository's plan fixture (`tests/plan_view.py`, saved as `plandata.json`) and Home Assistant's default theme variables. `overlay.js` is the
proposal applied on top of the unmodified card; `render_card.mjs` drives it.

- **Tokens.** Custom properties named with an `--hpo-` prefix, defined inside `cardStyleBlock(darkMode)` (no media
  queries), one `var()` level deep with a literal fallback, as the card tests require. The overlay's set: accent, heat,
  surface-2, text; space 4/8/12/16/24; radius 6/12/pill; text 12/13/15/18. They absorb the card's hex literals (about 40
  distinct values, about 130 uses, mostly `var()` fallbacks today).
- **Header:** the mark at 28 px before the title, and a status pill after it. States: heating now, idle, stale plan,
  fallback, and "manual plan until HH:MM" while the plan's manual override is active (the card already knows it through
  its manual-override reader).
- **Four stat tiles, one style:** price now (accent), planned heat (kWh), plan cost, and indoor temperature (D2b). The
  indoor value is the integration's indoor-temperature sensor, which the card already resolves for the chart's
  now-temperature label. It is not part of the card's render signature today, so the tile must join the headline
  signature or it never refreshes. On a phone the tiles form a 2×2 grid. The existing savings and score tiles stay:
  CLAUDE.md forbids deleting working functionality merely to fit.
- **Legend:** compact chips (28 px tall, 24 px hit target kept); one horizontally scrolling row on a phone instead of
  five wrapped rows. The dashed-line sentence becomes a footnote under the legend.
- **Fills:** price and solar area fills drop to 16% and 10% opacity so the heating bars are the loudest mark.

Component contrast (`contrast_components.json`, all pass):

| element | light | dark | needs |
|---|---|---|---|
| status pill text | `#1c7350` on `#e8f1ed`, 5.04 | `#1fad6b` on `#1c3027`, 4.83 | 4.5 |
| stat accent value | `#026aa8` on `#f7f9fb`, 5.48 | `#4fb3f0` on `#242a30`, 6.24 | 4.5 |
| stat label | `#727272` on `#f7f9fb`, 4.56 | `#9b9b9b` on `#242a30`, 5.21 | 4.5 |
| stat value | `#212121` on `#f7f9fb`, 15.26 | `#e1e1e1` on `#242a30`, 11.08 | 4.5 |
| mark line / heat (graphic) | 5.79 / 3.87 on white | 7.34 / 4.41 on `#1c1c1c` | 3 |

## 4. Plan chart, concept A (R9-UI-4; D2, D3, D4)

Renders: `assets/concept/A-panels-{light,dark}-{900,375}.png` and `.svg`, drawn by `concept_chart.py` from the same
fixture. (Concept B, one chart with four axes, is kept in `assets/concept/B-single-*` for the record; it was not chosen.)

**Layout.** Three panels share one time axis: Price (SEK/kWh, with solar as a relative dashed area), Heating power (kW:
space and hot-water bars, actioned power), Temperatures (°C: hot-water tank with its error band, house, outdoor). Each
panel has its own y-axis, gridlines, unit and inline legend; the now line crosses all three.

**The rule that keeps the plan editor and the what-if simulator working.** Draw the three panels **inside the one chart
SVG each copy already has**, with the one shared x-scale, and keep the lane strip under the bottom panel. Today every
consumer of the chart's geometry except the y-axes uses only x: the lane editor's hit-test maps clientX through the
chart's plot left, plot width and view window; pan and wheel do the same; the inline copy and the dialog copy are
indexed 0 and 1. Keeping one SVG per copy and the geometry object's x fields leaves all of them valid, and confines the
change to the y-scales, the axes, the gridlines, the series-to-panel assignment, the crosshair's vertical extent and the
lane placement.

**Must keep working (a review blocker for R9-UI-4):**
- plan editor: drag, resize and add a slot, remove, the keyboard menu, edge auto-pan, the 24/44 px slot targets;
- the manual-plan service calls and their payloads unchanged: apply with space and hot-water slot lists, clear;
- the what-if panel: simulate and save-schedule calls and payloads unchanged, and the draft wood slots in the wood lane;
- hover: crosshair across all three panels, tooltip rows for every series at the hovered time;
- pan, wheel zoom and the view window; the expanded dialog copy;
- the drift states that drive a drag and a hover, re-claimed in the card drift claim file.

**Palette of record (D3), per panel.** `check_palette.py` runs the repository's gates (ported in `color.py` from
`tests/card.mjs`: 3:1 on `#ffffff` and `#1c1c1c`, deuteranope ΔE ≥ 10, dash where ΔE < 20) and the dataviz skill's
validator (OKLab; protan, deutan and tritan; every pair). Output: `PALETTE-CHECKS.txt`, which ends `RESULT: every panel passes both`.

| panel | series | light | on #fff | dark | on #1c1c1c | today |
|---|---|---|---|---|---|---|
| price | electricity price | `#4a3aa7` | 8.56 | `#9085e9` | 5.45 | `#a86b00` |
| price | solar (dashed area) | `#d4561f` | 4.08 | `#d95926` | 4.39 | `#ed6900` |
| power | space heating | `#2a78d6` | 4.42 | `#3987e5` | 4.68 | `#4a90e2` |
| power | hot-water heating | `#d2403f` | 4.62 | `#e66767` | 5.28 | `#e0544e` |
| power | actioned power (outline) | `#008a70` | see checks | `#22a383` | see checks | `#00838f` |
| temps | hot-water tank | `#c2477a` | 4.69 | `#d55181` | 4.32 | `#c264d0` |
| temps | house | `#008300` | 4.95 | `#1f9d1f` | 4.79 | `#1a7a52` |
| temps | outdoor (dashed) | `#3b7dd8` | 4.11 | `#4b95e8` | 5.49 | `#7d8794` |

A correction against the proposal page: it showed outdoor as slate grey and said every panel passed the validator. Re-run
on 2026-09-30, the temperatures panel failed with grey outdoor (chroma floor; protan ΔE 2.3 against the tank colour), so
outdoor is now a cold blue and keeps its dash. Actioned power, which the concepts did not draw, now has a colour that
passes inside the power panel.

**Today's palette fails the extended gate (D4).** The eight series on one plot, light, every pair
(`PALETTE-CHECKS.txt`, first block): chroma floor fails for `#00838f` and `#7d8794`; protan ΔE 0.4 between house
`#1a7a52` and hot-water heating `#e0544e`; tritan 3.4; normal-vision ΔE 8.0 between solar and hot-water heating. The
repository test only simulates deuteranopia, so it passes today. R9-UI-4 writes the protan and tritan cases first, sees
them fail on the current series definitions, then lands the palette.

**Other files that move with the chart:** the card figure generator under `docs/img/` hard-codes the single plot (the
900×380 frame, the plot-box match, the now line's y, the "four units on four axes" subtitle); the dashboard-card doc's
chart text; the README hero `docs/img/card-plan-chart.png`, regenerated by the browser test's hero mode at its current
path (R9-RO-3 moves it later); the drift claims.

## 5. README (R9-UI-2)

Assets in `assets/readme/`: banner 1280×320, social preview 1280×640, "how it works" figure (light, and a dark variant
for the docs), each with its own background. `readme_assets.py` draws them; `readme_assets.py --live` writes SVGs with
live text. `README.proposal.diff` is the proposed README change, and `CHECKS.txt` records the repository's README rules
run on a scratch worktree with it applied: `tests/entities.py` 1988/1988 (baseline f88e6af8 also 1988/1988),
`doc_claims.py` 84/84, `md_tables.mjs` clean.

- the banner is one inline image line above the title; the pinned hero line is untouched;
- badges recoloured to fjord, License in ember, and the License link made absolute: its relative target breaks the badge
  image under HACS today;
- an "At a glance" 3×2 table, each cell restating a claim the README already makes;
- the figure under "How it works"; the mermaid diagrams stay in their details blocks;
- the social preview is uploaded by tvofi under the repository settings; it is not a tracked file.

The new image folders are `docs/img/brand/` (SVG masters) and `docs/img/readme/` (README graphics and their generator).
Both are final paths under R9-RO's target tree, so R9-RO-3 need not move them.

## 6. D5: the manual plan is already fixed for its window

Verified in the code at `48786f65` (`manual_plan.py`, `optimizer.py`, `coordinator.py`):
- an applied manual plan lasts up to 20 hours (the manual-plan window constant; `build_override` clamps the expiry and
  refuses slots that start later);
- the solver still runs every cycle, but the pins bound it: a pinned-off step is clamped to zero and a pinned-on step
  gets a raised lower bound, so the slot timing does not change;
- the exceptions: the power level inside an on-slot stays the solver's choice; the safety release frees an off-pin that
  would breach the comfort floor or the hot-water minimum, legionella included, and reports it on the card; a channel
  the editor did not send stays automatic (the card sends both whenever both have a forecast); the last hours of the
  24-hour horizon beyond the window stay automatic;
- the plan ends when its window passes or on "Back to automatic"; a mode change does not end it.

tvofi: "If slots can not automatically be changed during that window, no change is needed." No group is added.

## 7. Files

| path | what |
|---|---|
| `PHILOSOPHY.md` | "Valley Geometry", the design philosophy behind the mark and the graphics |
| `color.py` | the repository's colour gates ported from `tests/card.mjs` |
| `check_palette.py`, `PALETTE-CHECKS.txt` | the palette of record and its measurement |
| `contrast_components.json` | component contrast |
| `brand.py`, `marks.py` | the mark, lockups and Home Assistant brand PNGs; `marks.py` holds the rejected alternates |
| `overlay.js`, `render_card.mjs`, `render.mjs`, `plandata.json` | the card before/after renders |
| `concept_chart.py` | chart concepts A and B |
| `readme_assets.py` | banner, social preview, figure |
| `assets/` | every rendered file: `svg/`, `brand/`, `card/`, `concept/`, `readme/` (the scripts write to `out/` and `renders/`; `assets/` is the copy taken on 2026-09-30) |

To re-render: Node with Playwright and the pre-installed Chromium, Python with Pillow and fontTools. The `.mjs` scripts
need no `package.json`; do not add one above a repository worktree (a `"type": "module"` there made 33 of
`tests/entities.py`'s checks fail falsely during this work).
