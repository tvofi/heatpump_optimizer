# D4 — UI/UX (the card and the config flow), round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`,
VERSION 6.2.14. Apple M1 (8 GB), macOS Darwin 25.6.0, Node 20.10.0, Playwright
1.49.0 / Chromium 1148. Fan-out conditions: three other auditors on the box,
`load1` 2.8–8.5 during the runs. Every number below is a count or a pixel size
measured by a layout engine, so none depends on load.

## Limits, stated first

- **No Home Assistant frontend exists on this box.** The card was driven in
  real Chromium with the frontend's default theme tokens (`HA_TOKENS` in
  `card_geometry.mjs`: the light and dark values of `styles-data.ts`) and
  `<ha-card>` defined as the frontend defines it (`:host` rules of
  `ha-card.ts`). Tile widths are modelled: 359 px (phone, viewport minus the
  8 px gutters), 372 px (tablet, two masonry columns), 400 px (desktop
  sections column), 1200 px (panel). A real dashboard may give other widths;
  the dialog's geometry (`96vw`, `78vh`) does not depend on the tile.
- Config-flow **rendering** is inferred from schemas and `strings.json`;
  nothing was drawn. Field order, selectors, ranges, defaults, error keys,
  help text and menu structure are what the stub returns.
- The coarse-pointer arm uses Playwright's touch emulation
  (`hasTouch: true, isMobile: true` with a viewport meta); Chromium then
  reports both `(pointer: coarse)` and `(hover: none)` (`RESULT
  coarse_emulated=1`). On the other arms the `coarse_pointer` state answers
  the card's JS media query through a shim; its CSS `(hover: none)` rule is
  not exercised there.
- Contrast is computed against HTML backgrounds only. SVG fills under text
  (the lane labels drawn over the price area, visible in
  `shots/tablet-light-en--expanded_plan.png`) are not composited; that
  case is under-reported, not over-reported.
- Dialog screenshots were taken after the keyboard walk, so `.dlg-body`
  may be scrolled in them; the measurements were taken before the walk.
- `tab_unreached` (330) is a harness artifact: Chromium resumes sequential
  focus after the element that was focused when the state was built (the
  active tab, or the layout-edit toggle), and the walk ends when focus
  reaches the document. The only elements ever missed are the ones before
  that start point (`results.json`, `tabUnreached` per state). Keyboard
  reachability is therefore a non-finding, below.
- The plan payload is `tests/plan_view.py`'s single winter day (2 space
  slots, 9 DHW slots); slot widths in D4-02 are this plan's, other plans
  make other widths but the same lane height.

## Method

1. `card_geometry.mjs`: the 26 states of `tests/card_drift.mjs:STATES`,
   re-driven with real events (mouse drags for the slot and layout edits,
   real hover for the tooltips, `click()` for chips and the score stat) in
   Chromium, over 15 arms: {phone 375×812, tablet 768×1024, desktop
   1280×800} × {light, dark} × {en, sv}, a 1280×800 panel arm, a
   coarse-pointer arm and a reduced-motion arm (390 renders). Per render:
   text-box overlaps (text-node client rects and SVG text/tspan rects),
   text overflow past clipping ancestors or the scope, WCAG contrast of
   every visible text box, interactive-target sizes (24 px; 44 px on the
   coarse arm; WCAG 2.5.8's spacing exception computed), a Tab walk,
   console/page errors, hover-induced layout shift, and the chart's
   on-screen axis font and lane height. `results.json` holds every
   measurement; `summarise.py` cuts it; `shots/` holds 182 PNGs
   (light/en and dark/sv arms).
2. `first_paint_font.mjs`: the compact chart's font under the four
   sequences a dashboard produces (Lovelace order, attached order, resize,
   plan refresh), with `HeatpumpOptimizerCard.prototype._render` counted.
3. `config_flow_ux.py`: every page of both flows rendered through the
   stub; the initial path submitted with its own defaults until
   `create_entry`; counts of screens, fields, required fields, pickers,
   help coverage, error-key and select-option and menu-label translation
   coverage, defaults within selector range, untouched-submit validity,
   duplicate keys across pages, off-theme keys on the top-menu pages,
   Swedish coverage, and WARNING log records emitted by a default install.
4. `series_contrast.mjs`, `card_version.mjs`, `delta_wording.mjs`,
   `setup_scroll.mjs`: one number each, read out of the card's module scope
   through `tests/card_rig.mjs`'s vm context or measured in Chromium.

Commands (from the export root; `$SCR` is the session scratchpad,
`$PW` the Playwright prefix):

```
HPO_PLANDATA=$SCR/d4/plandata.json PYTHONPATH=tests/hastub python tests/plan_view.py
HPO_PLANDATA=$SCR/d4/plandata.json NODE_PATH=$PW/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers node tools/audit/round2/D4/card_geometry.mjs --shots
HPO_PLANDATA=$SCR/d4/plandata.json NODE_PATH=$PW/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers node tools/audit/round2/D4/first_paint_font.mjs
HPO_PLANDATA=$SCR/d4/plandata.json NODE_PATH=$PW/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers node tools/audit/round2/D4/setup_scroll.mjs
PYTHONPATH=tests/hastub python tools/audit/round2/D4/config_flow_ux.py
node tools/audit/round2/D4/series_contrast.mjs
node tools/audit/round2/D4/card_version.mjs
node tools/audit/round2/D4/delta_wording.mjs
python tools/audit/round2/D4/summarise.py [state-or-arm substring]
```

Outputs are beside each harness as `*.out`.

## Findings

### D4-01 (high, bug) — The chart's text is 3.7 px on a phone tile at first paint and 5.6 px in the phone dialog; the 8 px floor never holds

`first_paint_font.mjs`: in the order `hui-card` uses (setConfig → hass →
append → hass) the compact chart renders with `FONT_BASE` = 10 viewBox
units on a 333 px svg: **3.70 px** axis text, lanes 5.55 px, one render.
Narrowing the tile to 300 px re-renders **0** times (the ResizeObserver in
`connectedCallback` only calls `_cacheRect()`), so the text falls to
3.04 px. Only a hass update whose plan signature moves re-renders (7.31
px), and the attached order gives 7.42 px — not 8, because
`compactFontUnits(this._measuredCardWidth())` divides by the **host**
width (359) while the svg it sizes is 26 px narrower (ha-card's border and
padding). `card_geometry.mjs`: every inline state on every phone/tablet/
desktop tile arm shows the chart at 3.70 / 3.84 / 4.16 px (`chart` column
in `summarise.py`'s geometry table; `min_text_px` 2.96 px is the lane
label at 0.8×). The expanded dialog has no floor at all: `FONT_EXPANDED`
renders at **5.6 px** on a 375 px phone (dialog 360 px, chart 336×142 px),
11.75 px on a tablet, 19.95 px on a desktop; lane labels 4.5 px on the
phone (`shots/phone-light-en--expanded_plan.png`).

- Metric: on-screen axis font = `font-size` attribute × rendered svg width / 900.
- Instrumented: `HeatpumpOptimizerCard._render` / `_maybeRender` /
  `connectedCallback` / `_measuredCardWidth`, `compactFontUnits`, `renderChart`.
- Perturbation: have the ResizeObserver callback call `this.render()` (or
  put the measured width in `_signature`): `font_px_lovelace` 3.70 → ~7.4,
  `renders_resize` 0 → ≥1 (**up**). Measure the chartwrap instead of the
  host: `font_px_attached` 7.42 → 8.00. Floor the expanded font the same
  way: phone dialog 5.6 → 8.
- Why high: the card's whole content on the device most dashboards are
  read on, unreadable until the next plan refresh; the D4-01 fix that
  shipped for exactly this only applies to renders that happen attached.

### D4-02 (high, bug) — The schedule editor's targets are 1.3–22 px wide and 5.6 px tall on a phone; below 24 px at every viewport

`card_geometry.mjs`: `rect.lane` is 5.5 px tall in the phone tile, 5.6 px
in the phone dialog, 11.8 px on the tablet, 19.9 px in the desktop dialog
(`LANE_H` = 15 viewBox units, never floored). Slots in this plan are 1.3–
22 px wide on the phone (`worst small24` in `summarise.py`; a 15-minute
DHW slot is 2.7 px in the dialog). Across the 14 fine-pointer arms
**1,344** slot and **476** lane targets fall under 24 px, **1,711** of them
with no 24 px spacing rescue (`hit_small_24_nospacing` by element:
rect.slot 1344, rect.lane 367); on the coarse arm the smallest slot is
**1.3 px** and every lane 5.5 px against a 44 px touch target. The card
already anticipates touch (`LANE_EDGE_GRAB_COARSE` = 16 units = 6 px on the
phone; `touch-action: none` on the chart), but the geometry defeats it. The
lanes are also rendered — and tab-focusable, with "Press Enter for actions"
labels — in the compact tile, where they are 5.5 px tall and editing is not
enabled.

- Metric: min(width, height) of `rect.slot` / `rect.lane` client rects; count below 24 (44 coarse).
- Instrumented: `LaneEditor.laneGroupInner` (`LANE_H`, `LANE_GAP`), `renderChart`.
- Perturbation: `LANE_H` 15 → 40 units: phone dialog lane 5.6 → 15 px, `hit_small_24` **down**; a floor like the font's (lane px = max(24, …)) takes `rect.lane`/`rect.slot` out of `hit_small_24_nospacing` (**to_zero** for lanes).
- Leave-one-out (15 arms, `hit_small_24_nospacing`): min 104 (panel), max 186 (coarse), total 1,883, without the largest cell 1,697.
- Why high: the editor is the dialog's headline feature and cannot be operated by touch on a phone; the workaround is a desktop.

### D4-03 (medium, bug) — Axis labels collide at the plot corners at every viewport

`card_geometry.mjs`: **1,039** overlapping text pairs in 390 renders, all
but two of them SVG `text~text`. By pair: `'60' ~ '°C'` 260, `'400' ~
'W/m²'` 245, `'6' ~ 'kW'` 232, `'3' ~ 'SEK/kWh'` 53 (`'EUR/kWh'` 13): the
unit label drawn at the top of each value axis sits on the top tick label,
by 1.9 px on the phone and **8.4 px** in the desktop dialog (visible in
`shots/tablet-light-en--expanded_plan.png`, "°C 60", "kW 6"). And `'06:00
AM' ~ '-20'` 50, `'06:00' ~ '-20'` 46, `'06:00 AM' ~ '0'` 45: on tiles
≤ 400 px the first time label collides with the bottom tick of the left
axes. Every unit label also overruns the svg's top edge by 1.3 px
(`text_overflow` 744 of 792 are this).

- Metric: intersection of two text boxes ≥ 1.5 px on its narrower side, non-nested elements, overlays excluded.
- Instrumented: `valueAxis`, `timeAxis`, `renderChart` (`MARGIN.top` = 16).
- Perturbation: draw the unit label above the plot (`MARGIN.top` room, or offset the top tick) → the `'60' ~ '°C'` family **to_zero**; thin the first time label when it meets the bottom tick → the `'06:00' ~ '-20'` family to zero.
- Leave-one-out (15 arms, overlaps): min 38 (phone-light-en), max 82, total 1,039, without the largest cell 957.

### D4-04 (medium, bug) — The empty state's entity ids overflow the card on ≤ 400 px tiles

`card_geometry.mjs`, state `no_plan`: `<code>sensor.heat_pump_optimizer_space_heating_plan</code>`
and the sentence around it spill **31.1–44.1 px** past the card's box on
the phone arms (359 px), 26 px on the tablet (372 px) and 14 px at 400 px
(`overflow` rows `code@scope x`, `div.empty@scope x`, 48 across the
arms; `shots/phone-light-en--no_plan.png`). `.empty` is centred text with
no `overflow-wrap`; a 45-character monospace id does not fit a phone tile.
This is the first state every new install shows.

- Metric: text-box edge beyond the measured scope's box, px.
- Instrumented: `HeatpumpOptimizerCard._noPlanHtml`, `PlanSource.diagnose`, `.empty` in `cardStyleBlock`.
- Perturbation: `.empty code { overflow-wrap: anywhere; }` → `no_plan` overflow **to_zero**.

### D4-05 (medium, bug) — Primary-colour text and buttons render at 2.63:1 in the light theme

`card_geometry.mjs`: **891** light-theme contrast failures, of which the
what-if actions are 12 px text at **2.63:1**: `button.wi-pin` "Apply this
plan" (90), `button.wi-apply` "Simulate these slots" (90),
`button.wi-save` "Save as my schedule" — white on `#03a9f4`, 2.63:1 in
both themes (150), `button.wi-viewreset` (18), `span.layout-verdict.match`
(9), the `now` marker and the `»` lane marker (`text`, `text.lane-more`,
207). HA's default `--primary-color` is `#03a9f4`; the card uses it as
the text colour of its main actions and as the Save button's background.

- Metric: WCAG contrast of computed colour (opacity chain applied) over the first opaque ancestor background; fail < 4.5:1 (3:1 large).
- Instrumented: `cardStyleBlock` (`.wi-pin`, `.wi-apply`, `.wi-save`, `.wi-viewreset`, `.layout-verdict.match`), `renderChart` (now marker).
- Perturbation: `.wi-pin, .wi-apply, .wi-viewreset { color: var(--primary-text-color) }` and `.wi-save { background: var(--dark-primary-color, #0288d1) }` → `contrast_fail_light` **down** by ≥ 200.
- Leave-one-out (15 arms, contrast): min 53 (dark), max 99 (light), total 1,209, without the largest cell 1,110.

### D4-06 (medium, bug) — Opacity-faded text falls below AA: the setup page's "not configured" rows and switched-off chips

`card_geometry.mjs`: `.setup-slot.empty` (opacity 0.75 on
`--secondary-text-color`) renders the rows that say what is missing at
**2.99:1** in 9.3 px on the phone (light) and **4.04:1** (dark): 600 of the
1,209 failures (`tspan` 300, `tspan.setup-value` 300, every setup state on
every arm). `.chip.off` (opacity 0.4) renders an active toggle's label at
**2.43:1** light / 3.19:1 dark (45). Inactive controls (`.chip.nodata`,
disabled) were exempted and counted apart (`contrast_fail_inactive` 105).

- Metric: as D4-05.
- Instrumented: `cardStyleBlock` (`.setup-slot.empty`, `.chip.off`), `setupSvgHtml`.
- Perturbation: `.setup-slot.empty { opacity: 1 }` → the 600 tspan failures **to_zero**; `.chip.off { opacity: 0.7 }` → chip.off to zero.

### D4-07 (medium, bug) — With a coarse pointer no control grows: 548 targets under 44 px in the 26 states

`card_geometry.mjs`, coarse arm (`coarse_emulated=1`): **548** targets
below 44 px; smallest side per element: `rect.slot` 1.3, `rect.lane` 5.5,
`rect.setup-hit` 11.7, `button.wi-remove` 13.2, `.hl-score` 14, range
inputs 16, zoom buttons 17.3, layout-bar buttons 18.1, `select.wi-win-days`
19.2, chips 22, picker buttons 22, dialog tabs 23.7, what-if buttons 24.4,
time inputs 25.4, expand 26, close 31.5. The only coarse-pointer
adaptation in the card is the lane edge grab width. 186 of these are also
under 24 px with no spacing rescue.

- Metric: min side of every focusable/clickable target, coarse arm, threshold 44.
- Instrumented: `cardStyleBlock`, `_coarsePointer`, `Legend.html`, `ExpandedDialog.html`, `SetupPage`.
- Perturbation: `@media (pointer: coarse) { .chip, .dlg-tab, .viewctl button, .whatif button, .layout-bar button, .sp-actions button { min-height: 44px } }` → `hit_small_44_coarse` **down** by ≥ 250.

### D4-08 (low, hygiene) — Three of seven series colours are below 3:1 on the light card background

`series_contrast.mjs`: price `#f5a623` 2.03:1, solar `#f2c94c` 1.59:1,
house temperature `#2fae7a` 2.82:1 against `#ffffff`; all seven clear 3:1
on `#1c1c1c`. WCAG 1.4.11 asks 3:1 of graphical objects needed to read
the content; the legend dot and the line are the only identification of a
series.

- Metric: contrast of `SERIES_DEFS[i].color` vs the card background.
- Instrumented: `SERIES_DEFS`.
- Perturbation: solar `#b8860b` → `series_below_3_light` **down** by 1.

### D4-09 (low, hygiene) — Form length and grouping: 17 fields (13 entity pickers) on the first screen, 5 of 13 options pages over 15 fields, one hot-water field that is a heating pump

`config_flow_ux.py`: the initial path is 7 screens (6 forms, 1 menu), 46
fields, 13 required, 2 that a user must bring (Tibber token, weather
entity), and the entry is created (`initial_entry_created=1`). The `user`
screen carries 17 fields, 13 of them optional entity pickers spanning
sensors, pump telemetry, a solar-source select and a map. Options pages:
hot_water 23 fields, entities 22, learning 18, grid 18, thermal_model 16
(`pages_over_15=5` of 13; 158 fields in all). `hot_water` ends with
`space_circulation_pump_entity` ("Heating circulation pump switch"),
the one top-menu field off its page's theme (`off_theme_fields=1`, key-
prefix heuristic in the harness).

- Metric: fields per rendered schema; pickers = `EntitySelector` fields; off-theme = keys matching none of the page's prefixes.
- Instrumented: `HeatPumpOptimizerConfigFlow.async_step_user`, `HeatPumpOptimizerOptionsFlow.async_step_hot_water` and siblings.
- Perturbation: move `space_circulation_pump_entity` to the building page → `off_theme_fields` **to_zero**; move the pump-telemetry pickers off `user` → `user_page_pickers` down.

### D4-10 (low, hygiene) — A default install logs a WARNING the coordinator deliberately suppresses

`config_flow_ux.py`: submitting the DHW step untouched (setpoint 55,
anti-legionella 60, enabled) emits **1** WARNING ("the anti-legionella
cycle at 60 °C is above the 55 °C charge limit…"). `coordinator.py`
exempts exactly this stock pair from the `dhw_legionella_above_setpoint`
repair notice (`stock = legionella == DEFAULT … and setpoint == DEFAULT`);
`_dhw_legionella_warning` has no such exemption, so every fresh install
warns about its own defaults.

- Metric: WARNING records on `config_flow._LOGGER` during the default initial path.
- Instrumented: `config_flow._dhw_legionella_warning`, `async_step_dhw`.
- Perturbation: add the coordinator's `stock` exemption → `default_submit_warnings` **to_zero**.

### D4-11 (low, hygiene) — The card announces v5.4.17 in a 6.2.14 release, and its duplicate-copy guard keys on that number

`card_version.mjs`: `CARD_VERSION` = 5.4.17, VERSION = manifest = 6.2.14
(`card_version_matches=0`). The console banner is what a user quotes in a
bug report, and `customElements.get(CARD_TAG).cardVersion !== CARD_VERSION`
is the only thing that makes a duplicate resource report itself: two copies
from any two 6.x releases carry the same 5.4.17 and stay silent.
`tools/release/stamp.py` does not touch the constant.

- Metric: string equality of the three versions.
- Instrumented: `CARD_VERSION` (card module scope).
- Perturbation: set `CARD_VERSION` to VERSION (or stamp it) → **up** to 1.

### D4-12 (low, hygiene) — "the same than the saved plan"

`delta_wording.mjs`: the English `stats.delta_detail` template
"{verdict} than the saved plan" is composed with `stats.the_same` = "the
same" for a cost-neutral edit: **1** of 3 verdicts ungrammatical (Swedish
uses "jämfört med", 0 of 3). Visible in every dialog screenshot's
"TODAY'S SLOTS" row.

- Instrumented: `L` / `STRINGS` as `WhatIfPanel`'s delta row composes them.
- Perturbation: "{verdict} compared with the saved plan" → **to_zero**.

## Non-findings

| Claim | Command | Value |
|---|---|---|
| No console errors or uncaught exceptions in any of the 390 renders | `card_geometry.mjs` | `console_errors=0` |
| No layout shift on hovering chips, tabs, buttons or setup rows (14 hover targets per state) | `card_geometry.mjs` | `hover_shift=0` |
| Every keyboard focus stop shows a visible indicator (outline, box-shadow or SVG stroke) | `card_geometry.mjs` | `focus_no_indicator=0` over 390 walks |
| Every focusable in a dialog is reached by Tab (the misses are the walk's own start point, see Limits) | `card_geometry.mjs`, `results.json` `tabSeq` | e.g. `expanded_plan` 29 stops, 1 unreached = the pre-focused active tab |
| The setup diagram on a phone scrolls sideways and every assignment row can be brought into view | `setup_scroll.mjs` | `hits_reachable=6/6`, `canvas_scroll_px=230` |
| No text box overflows a `white-space: nowrap` / clipped HTML element (the tooltip's shipped defect stays fixed) | `card_geometry.mjs` | 0 `scrollWidth` overflows; all 792 overflows are the 1.3 px unit-label ascender and the empty-state ids (D4-03/04) |
| Swedish translation is complete: card and integration | `config_flow_ux.py`; card STRINGS via `card_rig` | 232/232 card keys, 686/686 leaves; `sv_identical=4` (all legitimately identical: "MQTT QoS", era digits, "open_meteo") |
| Every config-flow field has help text | `config_flow_ux.py` | `help_missing=0` (172 fields) |
| Every error key the code raises has a translation in its flow | `config_flow_ux.py` | `error_keys_missing=0` (10 keys) |
| Every select option and menu label is translated | `config_flow_ux.py` | `select_options_missing=0`, `menu_labels_missing=0` |
| Every NumberSelector default lies inside its own range; every page accepts its own defaults | `config_flow_ux.py` | `defaults_out_of_range=0`, `untouched_submit_fail=0` |
| No setting is reachable from two options pages; every saving page carries the after-save choice | `config_flow_ux.py` | `duplicate_keys=0`, `after_save_missing=0` |
| Install to entry: 7 screens, 2 fields the user must bring | `config_flow_ux.py` | `initial_screens=7`, `initial_must_know=2` |
| The two-level options menu partitions the 13 pages 6 + 7 with "Advanced settings" as the 7th top entry | `config_flow_ux.py` | `top_menu_entries=7`, `advanced_menu_entries=7` |
| Reduced motion: the only transition is the zoom-control fade and it is dropped | `card_geometry.mjs` reduce arm | identical counts to the phone-light-en arm (58/54/99/304) |
| Series colours all clear 3:1 on the dark background | `series_contrast.mjs` | `series_below_3_dark=0` |
| The setup page's assignment rows are ≥ 8 px and inside their svg (card_browser's own check) at every viewport | `card_geometry.mjs` | smallest `rect.setup-hit` 11.7 px (phone) |

## Harnesses

- `tools/audit/round2/D4/card_geometry.mjs` (+ `card_geometry.out`, `results.json`, `shots/`)
- `tools/audit/round2/D4/first_paint_font.mjs` (+ `.out`)
- `tools/audit/round2/D4/setup_scroll.mjs` (+ `.out`)
- `tools/audit/round2/D4/config_flow_ux.py` (+ `.out`)
- `tools/audit/round2/D4/series_contrast.mjs` (+ `.out`)
- `tools/audit/round2/D4/card_version.mjs` (+ `.out`)
- `tools/audit/round2/D4/delta_wording.mjs` (+ `.out`)
- `tools/audit/round2/D4/summarise.py`, `validate_report.py` (readers, not harnesses)

## Not finished

- Lane labels drawn over the price area (contrast against SVG fills) — seen
  in the screenshots, not measured.
- The editor element (`editor_schema`) renders `ha-form`, which does not
  exist here; only its schema count (7 entries) was taken.
- A run with real Home Assistant tile widths and theme (needs a frontend).

## Exposure

None: no `docs/` was read; the `D4-01`/`D4-06` ids in the card's comments
were seen while reading the source, as context.
