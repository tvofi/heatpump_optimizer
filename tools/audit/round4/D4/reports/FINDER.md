# D4 — UI/UX — round 4

- dimension: D4, the card and the config flow
- baseline: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- tree: `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline` (export, no `.git`)
- box: 8-core Apple M1, 8 GB, macOS 25.6.0; node v20.10.0; Playwright 1.49.0
  from `/private/tmp/hpo-pw/node_modules`; Chromium `chromium-1148`
  (HeadlessChrome 131.0.6778.33) from `$HOME/.cache/pw-browsers`
- python: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub`, run from the export root
- private plan payload: `HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json`
  (written by `tests/plan_view.py`; never the shared default path)
- `exposure`: none. No `docs/`, no GitHub, no earlier round's material was
  read. `tools/audit/round3/` is absent from this tree.

Every number below is a count, a pixel distance, a CSS-pixel size or a
contrast ratio. None is a wall, CPU or RSS figure, so none is affected by the
two other finders sharing the box. `load1` at the time of each run is printed
by each harness (3.7–6.8 across the session) and is quoted, not gated.

## Method

### The card, in a real browser

`tests/card_rig.mjs`'s DOM stub returns a constant 900×400 rectangle and has
no geometry at all, so nothing built on it can answer a layout question. Every
geometric and colour number here comes from real Chromium, driven the way
`tests/card_browser.mjs` drives it: the card source injected with
`addScriptTag`, a stub `<ha-card>` carrying the Home Assistant frontend's own
`:host` rule set, and the Lovelace mount order (`setConfig` and `hass` before
the element is attached, so the first paint has no width).

The 34 states are **derived** from `tests/card_drift.mjs` at run time — the
harness re-reads that file and refuses to run if the list is not 34 — and
re-expressed against real DOM in `lib/states.js`: real elements, real
`dispatchEvent`, coordinates taken from real rects. The grid is

| axis | values |
|---|---|
| state | the 34 in `tests/card_drift.mjs`'s `STATES` (`--list`) |
| viewport | 375×812 (tile 359 px), 768×1024 (tile 736 px), 1280×800 (tile 500 px) |
| theme | Home Assistant `default_light` and `default_dark` variable sets |
| language | `en`, `sv-SE` |
| media | fine pointer, coarse pointer (CDP `Emulation.setEmulatedMedia` **and** a `matchMedia` stub, because the card reads the query in JS as well as in CSS), reduced motion |

= **1224 cells**, 105 612 measured text nodes, **0 uncaught page errors and 0
console errors** across the whole grid.

The grid is run **twice**: once on the real wall clock, and once with
`D4_FREEZE=1`, which stands the clock six hours into the captured day the way
`tests/card_browser.mjs` does. That second run matters and is not a
formality: on the real clock the recorded payload's day (2026-01-15) is
entirely in the past, every slot is locked, no `rect.slot-hit` is drawn at
all, and two states (`draft_dirty_menu_open`, `draft_mid_drag`) never drive —
72 of 1224 cells — so every measurement of the editable surface is taken over
an empty set, which reads as a pass. Frozen, **`drive_failures=0`** and all
34 states drive. Both runs are reported; `out/cells.json` /
`out/summary.json` are the wall-clock run and `out/cells_frozen.json` /
`out/summary_frozen.json` the frozen one.

| | wall clock | frozen |
|---|---|---|
| cells | 1224 | 1224 |
| drive failures | 72 | **0** |
| page + console errors | 0 | 0 |
| text nodes measured | 105 612 | 104 040 |
| text clipped by its own box | 0 | 0 |
| svg text escaping its svg | 0 | 0 |
| sub-8 px text instances | 1884 | 1884 |
| cells with text below AA | 1080 | 1080 |

Per cell the harness records, from `getBoundingClientRect` /
`getComputedStyle` / `getBBox`: every visible text run with its composited
foreground and background, overlapping text boxes, text clipped by its own
box, SVG text escaping its own `<svg>`, every interactive target's on-screen
size, the focusable list, and on-screen font size (an SVG `font-size`
attribute is in viewBox units, so it is multiplied by the svg's own
rect/viewBox scale).

**Two measurement traps were hit and fixed before anything was claimed**, and
both are recorded here because a verifier will meet them:

1. *`fill` is not the background.* The card paints its lane and series blocks
   at `fill-opacity` 0.07–0.85. Reading `fill` alone reports a saturated
   series colour as the background and invents contrast failures that no
   pixel on screen has. `lib/measure.js` now composites every covering layer
   in paint order at its effective alpha (`fill-opacity` × the `opacity` of
   itself and every ancestor group) over the HTML background beneath the svg,
   sampled at five points across each text box, worst point reported.
2. *A bounding box is not ink.* Rect-overlap over text boxes reported 27 266
   "overlaps" in the grid. Nearly all are an axis tick's em-box brushing a
   unit label's em-box with no glyph collision, or an element box brushing a
   scrolled/sticky neighbour. Every overlap claim would need rasterisation,
   which `tests/card_browser.mjs` already does for the axis-unit pairs (and
   reports 0 colliding pairs). **No overlap is claimed here.** See
   non-findings.

Because the analytic compositing still depends on which shapes' *bounding
boxes* cover a text run — and an area `path`'s bbox reaches far below its
filled region — every contrast claim below is re-measured by
`contrast_pixels.mjs`, which never asks what is nominally behind the text: it
rasterises the same frame twice at `deviceScaleFactor` 4, once with the run's
glyphs painted and once with them made transparent (`color`/`fill:
transparent`, **not** `visibility: hidden`, which would take a button's own
background away with its label and report a coloured button as
white-on-white), and reads the background off the second raster at the
glyph pixels of the first.

### The config flow

Driven through the real handlers with the Home Assistant stub the way
`tests/entities.py`'s options loop does (`FakeEntry`, `FakeHass`,
`async_step_*(None)`), then scored against the written rubric below.

**Limit, stated as the brief requires: there is no Home Assistant frontend on
this box, so nothing here renders a config-flow page.** Field order and
grouping, section nesting, defaults, selector ranges, error keys and
translation coverage are read off the real schema objects and the real
strings files; anything about spacing, wrapping or control size on a rendered
config-flow page is *not* measured and is not claimed.

#### The rubric

| id | rule | how it is scored |
|---|---|---|
| R1 | one theme per page | judged, not scored: every page's fields share a subject; no counter-example found, so no number is reported |
| R2 | related fields adjacent | fields sharing a `_`-prefix are contiguous in the presented order |
| R3 | sensible defaults | every non-entity field carries a default, so an untouched page submits |
| R4 | errors say what to change | every error/abort key a handler raises is translated in `en.json` and `sv.json` |
| R5 | no jargon without help text | every field has a `data_description` in `strings.json` |
| R6 | field count | ≤ 8 fields at a page's top level (section contents excluded) |
| R7 | both languages complete | every label and help text in `en.json` exists in `sv.json` |
| R8 | numeric ranges bounded | every `NumberSelector` carries a `min` and a `max` |

## Findings

The ids below are this round's, in the format `tools/audit/finding.schema.json`
requires (`^D4-[0-9]{2}$`). Same-numbered ids appear in comments in the card
source from an earlier round; per `COMMON.md` those are context, not a
register, and nothing here is keyed to them.


### D4-01 — the plan's lane strip is unreadable: 6.4 px type at 1.01:1 (high)

- instrumented symbol: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:LaneEditor.laneGroupInner` (the `<text class="lane-label">` emitted at `:6651` and `:6788`)

**Claim.** The lane strip under the chart — the band that names which lane is
*Heating*, which is *Hot water*, which is *Wood*, and which is also the
drag-to-edit surface — draws its labels at `font * 0.8` in
`--secondary-text-color` directly over the slot blocks, with no minimum font
size and no background plate. Measured in real Chromium, those labels land at
**6.4 CSS px on a 375×812 phone tile** and at **1.01–2.55:1 contrast** against
the pixels actually behind them, where WCAG 2.1 AA requires 4.5:1. A user on a
phone cannot read which lane is which, and the card's own 8 px axis font floor
does not reach these labels.

**Numbers.**

- Contrast, pixel-verified (`contrast_pixels.mjs`, specified fill over the
  background read off a real raster at `deviceScaleFactor` 4):

  | state | theme | run | ratio | AA bar |
  |---|---|---|---|---|
  | `wood_lane` | light | "Wood" | **1.014** | 4.5 |
  | `plan_inline` | light | "Heating" | 1.794 | 4.5 |
  | `plan_inline` | light | "Hot water" | 2.393 | 4.5 |
  | `plan_inline` | dark | "Heating" | 1.891 | 4.5 |
  | `plan_inline` | dark | "Hot water" | 2.547 | 4.5 |
  | `expanded_plan` | light | "Heating" | 1.797 | 4.5 |
  | `expanded_plan` | dark | "Heating" | 1.891 | 4.5 |
  | `plan_inline` @375 | light | "Heating" | 1.794 | 4.5 |

- On-screen font size (`card_grid.mjs`, SVG `font-size` × svg rect / viewBox):
  **6.4 px** at 375×812, **6.6 px** at 768×1024, 11.15 px (tile) and 15.96 px
  (dialog) at 1280×800. The card floors axis text at 8 px
  (`tests/card_browser.mjs`, D4-01/#256/#257); that lane's own check
  explicitly excludes `lane-*` (`.filter((t) => !/lane-/.test(...))`), so the
  floor has never applied here. 1884 sub-8 px text instances in the grid,
  **all of them `text.lane-label`**.
- Spread across the grid: **1080 of 1224 cells**, **30 of 34 states**, 4459
  instances, in *both* themes, *both* languages and all three media arms.

**What a user cannot do.** Tell the heating lane from the hot-water lane on a
phone, which is what the strip exists to say; and the same strip is the
surface the what-if editor asks them to drag slots on.

**Screenshots.** `shots/FINDING_lane-strip-375-light.png`,
`shots/FINDING_lane-strip-375-dark.png`,
`shots/FINDING_lane-strip-500-light.png`,
`shots/plan_inline__375x812__light.png`.

### D4-02 — "Save as my schedule" is 2.78:1 in Home Assistant's dark theme (medium)

- instrumented symbols: `heatpump-optimizer-card.js:cardStyleBlock` (the `.whatif .wi-save` rule at `:3485`) and `heatpump-optimizer-card.js:WhatIfPanel.html` (the button at `:7458`)

**Claim.** `.whatif .wi-save` hard-codes its background to the card's
`ACCENT_READABLE` constant (`#026aa8`) while taking its label colour from
`var(--text-primary-color, #fff)`. Home Assistant's default **dark** theme
sets `--text-primary-color: #212121`, so the one pairing the card fixed on one
side breaks on the other: **#212121 on #026aa8 = 2.78:1**, against a 4.5:1 AA
bar. In light theme the same rule is #ffffff on #026aa8 = **5.79:1** and
passes. This is the primary confirming action of the what-if editor — the
control that writes a schedule to the user's heat pump.

**Numbers.** `contrast_pixels.mjs`, state `expanded_plan`, selector
`.wi-save`, 9 724 glyph pixels measured:

| theme | specified label | measured button pixels | ratio | AA bar |
|---|---|---|---|---|
| dark | `rgb(33,33,33)` | `rgb(2,106,168)` | **2.783** | 4.5 |
| light | `rgb(255,255,255)` | `rgb(2,106,168)` | 5.786 | 4.5 |

Grid corroboration: `button.wi-save` is the **only** non-lane text signature
below AA anywhere in 1224 cells, and it appears in 15 states, dark theme only.

**Mechanism, and why this is one finding and not a colour nit.** The card
already reasoned this through once, for the "now" marker: its own comment
records that `#026aa8` "measures 2.946:1 against a `#1c1c1c` one", that "no
fixed colour can clear 4.5:1 against both `#ffffff` and `#1c1c1c`", and that
the marker therefore needs a theme token rather than a constant. That
conclusion was applied to the marker and not to the filled buttons that pair
the same constant with `--text-primary-color`. `.sp-save.confirm` and
`.wi-save.confirm` are the same shape (a hard-coded fill with a
`--text-primary-color` label); **they were not measured** — reaching them
needs an armed confirm state — so they are named as siblings of the
mechanism, not claimed.

**A second instance of the same phenomenon, weaker and reported here rather
than as a fourth finding.** `.whatif .delta.dearer` — the "+0.51 SEK" figure
that tells a user their what-if edit costs *more* — takes
`var(--error-color, #e0544e)`. With Home Assistant's own `--error-color`
(`#db4437`) that is **4.291:1** on the light card and **3.972:1** on the dark
card, both under 4.5:1. It appears in 72 instances across 2 states of the
frozen grid, both themes. It needed no rasterisation to establish: both
layers are opaque and named (`#db4437` over `dialog.expanded`'s
`--card-background-color`), so the ratio is arithmetic, and the harness's
number and an independent recomputation agree to three decimals. It is
grouped here because it is the same failure to check a chosen colour against
the surface it lands on; it is *not* the same code, and a fix for one does
not fix the other.

**Screenshots.** `shots/FINDING_wi-save-dark.png`,
`shots/FINDING_wi-save-light.png`.

### D4-03 — the zoom −/+ pair fails WCAG 2.2 SC 2.5.8 under a mouse (low)

- instrumented symbols: `heatpump-optimizer-card.js:ViewWindow.controlsHtml` (the `.vc-in` / `.vc-out` buttons at `:4664`) and `heatpump-optimizer-card.js:cardStyleBlock` (`coarseHtmlTargets` at `:2769`, applied only inside `@media (pointer: coarse)` at `:3495`)

**Claim.** The card's 24 px target floor is applied only inside
`@media (pointer: coarse)` (and its `_coarsePointer()` duplicate). Under a
fine pointer the two view-zoom buttons render at **20.22 × 20.22 CSS px with
22.22 px between their centres** — undersized *and* too close together, so
SC 2.5.8's spacing exception does not rescue them. At the smallest tile they
fall to **17.33 × 17.33 px at 19.33 px centre spacing**.

**Numbers.** `target_size.mjs`, which applies the standard's spacing exception
(a 24 px-diameter circle centred on each undersized target must not intersect
another target's circle) rather than counting every small box:

| pointer arm | cells | targets | under 24 px | spared by the spacing exception | **failing SC 2.5.8** |
|---|---|---|---|---|---|
| fine | 102 | 2907 | 1548 | 1184 | **364** |
| coarse | 102 | 2907 | **4** | 2 | **2** |

Dominant failing signature, in **93 of 102** (state × viewport) cells:
`button.vc-out 20.22×20.22 (nearest centre 22.22 px: button.vc-in)` and its
mirror. The coarse arm is effectively clean — the card's own floor holds
there — which is why the claim is about the fine-pointer arm only.

**What a user cannot do.** Hit zoom-out without hitting zoom-in on the first
try with a mouse or a trackpad; the two controls are 2 px apart.

**Screenshot.** `shots/FINDING_zoom-buttons-fine.png`.

## Non-findings

Each with the command and the number that showed it.

| claim that held | command | number |
|---|---|---|
| No uncaught page error or console error in any state, viewport, theme, language or media arm | `node tools/audit/round4/D4/card_grid.mjs` | `page_errors=0` over 1224 cells |
| No HTML text is clipped by its own box (no inherited-nowrap / ellipsis truncation) | same | `clipped_instances=0`, `clipped_cells=0` |
| No SVG text escapes its own `<svg>` at any viewport | same | `svg_escape_instances=0` |
| **Text overlap is not established.** 27 266 rect-overlap candidates, all bounding-box artefacts | same | `overlap_instances=27266`; the two dominant signatures are `button.chip ~ span.title` (2624) and `p.legend-note ~ button.chip` (1668), both a full-width block's box brushing an inline control's box with no glyph collision, and the SVG ones are tick-vs-unit em-boxes that `tests/card_browser.mjs`'s ink lane already measures at 0 colliding pairs. **Harness gap, named: an ink claim needs rasterisation and this grid does rects.** |
| The expanded dialog is a real modal: keyboard focus never leaves it while it is open | `node tools/audit/round4/D4/keyboard_tab.mjs` | `escaped_dialog=0` in all four dialog cases; the card uses `<dialog>` + `showModal()` |
| Every focusable has an accessible name | same | `unnamed=0` in all five cases |
| Every keyboard-focused control changes something on screen (WCAG 2.4.7) | same | `PIXEL_invisible_focus=0` in four of five cases; the single exception is a `rect.setup-hit` sitting behind an open picker popup. Weakest real ring 284 changed pixels. A computed-style read said otherwise (`css_no_ring` up to 8) and was **wrong in both directions** — `.setup-hit:focus-visible` rings itself with a `stroke`+`fill` rather than an `outline`, and native inputs take the UA ring, which reports `outline-style: auto` with no usable width. The pixel test is the instrument; the CSS read is not. |
| Coarse-pointer targets meet the card's own 24 px floor | `node tools/audit/round4/D4/target_size.mjs` | 4 undersized of 2907 targets over 102 cells; 2 failing SC 2.5.8, both a 16.72 px-wide 15-minute `rect.slot-hit` |
| Swedish translation of both flows is complete | `python3 tools/audit/round4/D4/config_flow_rubric.py` | `sv_translation_gaps=0` over every `title`, `description`, `data` and `data_description` key in `config` and `options` |
| Every error and abort key a flow handler raises is translated in both languages (R4) | same | `error_keys_raised=9`, `error_keys_untranslated_en=0`, `error_keys_untranslated_sv=0` |
| Every `NumberSelector` in both flows is bounded (R8) | same | `R8_failing_pages=0` over 31 form pages and 258 fields |
| Every field on every page has a label and help text (R5) | same | `R5_failing_pages=1` — and that one, `config.reauth`, is **not a page**: `async_step_reauth` immediately returns `async_step_reauth_confirm()`, so the harness scored the redirect's inherited schema. `reauth_confirm` itself has both. Disproved lead, harness gap named. |
| Top-level field count is ≤ 8 on 26 of 31 form pages (R6) | same | five over: `config.dhw` 11, `config.zones` 11, `config.thermal` 10, `options.grid` 9, `options.heat_curve` 9. Pages with far more fields (`options.comfort` 19, `options.entities` 16) sit under the bar because they use sections — the grouping the brief asks about is present and working. Not claimed as a finding: no user-facing failure was measured, only a count over a bar this report chose. |
| Defaults survive their own page (R3) | same | `R3_failing_pages=4`; two are the `reauth` redirect pair, and `options.thermal_model` / `thermal_model_zones` are `_SUGGESTED` **by design** — the handler's own docstring records that a `vol.Optional` default there would silently flip a legacy single-zone entry to two-zone. Disproved lead. |
| Field adjacency (R2) | same | `R2_failing_pages=3`: `config.user` (`price_source`, `tibber_token`, `price_entity` — the token sits between the source and the entity, and only one of the latter two ever applies), `config.zones`, `options.away`. Cosmetic ordering; no measured consequence, so recorded here rather than filed. |
| Steps from install to the first plan | same | 5 screens on the questionnaire path (`user` 5 fields → `user_sensors` 14 → `finish_setup` menu → `finish_now` → `setup_overview`), 19 fields; the expert path adds `temperature`/`building`/`building_describe`/`building_extras`/`thermal`/`zones`/`dhw`/`weather_sensitivity` |

## What I could not finish

1. **The editable-slot surface is measured only in the frozen arm.** Both
   grid runs are complete and reported above, so this is a stated boundary
   rather than unfinished work: any claim about `rect.slot-hit` or the lane
   editor rests on `out/cells_frozen.json` and `target_size.mjs` (which
   always freezes), never on the wall-clock run. Nothing in the three
   findings depends on either arm alone — the lane-label and `wi-save`
   signatures are identical in both.
2. **`.wi-save.confirm` and `.sp-save.confirm` were not measured** (see
   D4-02). They are the same mechanism with `--error-color` as the fill;
   reaching them needs an armed confirm state that the ported drivers do not
   enter.
3. **No ink-level overlap measurement.** Stated as a harness gap in the
   non-findings rather than left as a silent pass.
4. **`editor_schema` has no geometry.** The card editor renders `ha-form`,
   which does not exist outside the Home Assistant frontend; the state mounts
   and is measured, but what it measures is the host element, not a rendered
   options form. Recorded, not claimed.
5. **Config-flow rendering is inferred, never rendered** — the brief's own
   limit, repeated here because it bounds everything in the rubric section.

## Harnesses

All under `tools/audit/round4/D4/`, each runnable by the single command in its
own header, each writing only under its own directory and a private temp root.

| file | what it produces |
|---|---|
| `card_grid.mjs` | the 1224-cell grid: contrast, overlaps, clipping, escapes, target sizes, focusables, on-screen font sizes, page errors → `out/cells.json`, `out/summary.json`, `out/page_errors.json` (and the `D4_FREEZE=1` arm's `out/*_frozen.*`). The two per-cell files are ~15 MB each and are stored gzipped (`out/cells.json.gz`, `out/cells_frozen.json.gz`); `gunzip -k` them, or re-run the harness, which writes them uncompressed. |
| `contrast_pixels.mjs` | pixel-truth contrast for a named selector in a named state, from two rasterisations of one frame → `out/contrast_pixels.json` |
| `target_size.mjs` | WCAG 2.2 SC 2.5.8 with the spacing exception applied, fine and coarse arms, frozen clock → `out/target_size.json` |
| `keyboard_tab.mjs` | the real Tab order, modal containment, accessible names, and focus visibility measured in changed pixels → `out/keyboard_tab.json` |
| `config_flow_rubric.py` | both flows driven through the real handlers and scored against the rubric above → `out/config_flow.json` |
| `lib/measure.js` | browser-side: composited backgrounds, contrast, overlaps, clipping, targets, focusables (loaded with `addScriptTag`) |
| `lib/states.js` | `tests/card_drift.mjs`'s 34 states re-expressed against real DOM; every driver returns `{ok, note}` so a vacuous cell is visible |

Prerequisite for every Node harness:

```
PYTHONPATH=tests/hastub HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
  /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tests/plan_view.py
export NODE_PATH=/private/tmp/hpo-pw/node_modules
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers
export HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json
```
