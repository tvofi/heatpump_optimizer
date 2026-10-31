# D4 — UI/UX, audit round 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Machine: 8-core Apple M1,
8 GB, Node v20.10.0, python 3.11.5, Chromium 1148 driven by Playwright 1.49.0
(`NODE_PATH=/private/tmp/hpo-pw/node_modules`,
`PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers`; both resolved, Chromium
launched, so nothing here falls back to the DOM stub).

**Every number in this report is a pixel count, an element count, a field count
or an sRGB contrast ratio.** None of them is a wall, CPU or RSS reading, so none
of them moves with the box's load. `load1` at the runs was 9.1–25.2 and
`thread_factor` is 1.0 by construction (no BLAS is imported by any harness
here). `tests/stress.py` was not run, `./tests/run.sh` was not run, and the gate
lock was neither taken nor stolen.

## Method

1. **Real geometry, every state.** `tools/audit/round3/D4/card_states_geometry.mjs`
   mounts the shipped card in real Chromium the way Lovelace does (`setConfig`
   and `hass` *before* the element is placed) and drives **33** states — the
   states `node tests/card_drift.mjs --list` enumerates (34) minus
   `editor_schema`, which is a JSON dump with no rendered tree. Each state is
   driven at three viewports (375x812 phone / host 359 px, 768x1024 tablet /
   host 736 px, 1280x800 desktop / host 492 px, HA's masonry column width),
   in HA's light and dark default theme token sets, and under both an emulated
   **coarse** pointer (CDP `Emulation.setEmulatedMedia` plus a `matchMedia`
   stub, because CDP alone does not re-evaluate shadow styles) and a fine
   pointer. 33 x 3 x 2 x 2 = **396 cells**.
   The DOM stub in `tests/card_rig.mjs` returns a constant 900x400 rectangle
   and was used for nothing in this report.
2. **The two card defects the sweep localised**, each with a perturbation that
   moves the number and an arm where it must vanish:
   `tools/audit/round3/D4/card_ux_defects.mjs`.
3. **The flows, page by page.** `tools/audit/round3/D4/flow_ergonomics.py`
   calls every `async_step_*(None)` on the real `HeatPumpOptimizerConfigFlow`
   and `HeatPumpOptimizerOptionsFlow` and reads the schema off the form each
   handler actually returns — 36 pages, 32 of them forms, **257 presented
   fields**.
4. **Screenshots** in `tools/audit/round3/D4/shots/`, written by
   `tools/audit/round3/D4/shots.mjs`.

### Limits, stated as the brief requires

* There is **no Home Assistant frontend on this box**, so nothing about how a
  config-flow page *looks* was observed. Every flow claim below is derived from
  the schema the handler returns and from `strings.json` / `en.json` /
  `sv.json` — field counts, section counts, key coverage. Where I say a page is
  "flat" I mean it declares no `section()`, which is a fact about the schema;
  how Home Assistant chooses to render that is **inferred**, not measured.
* The card harnesses stub `<ha-card>`. Home Assistant's real `<ha-card>`
  declares `color: var(--primary-text-color)`; `tests/card_browser.mjs`'s stub
  omits it, and with the omission every inherited-colour text run in the card
  measures against the page default instead of the theme. The harnesses here
  restore that declaration. (This is a gap in the existing lane's stub, not a
  card defect — the existing lane resolves its four required colours
  explicitly, so it never depended on the inherited value.)
* Tab-order *sequence* through every focusable was not walked; only
  reachability (`tabIndex >= 0`) was measured, on the chips. Hover layout-shift
  was not measured. Both are listed under "not finished".

---

## Findings

### D4-01 — the no-data legend chips are unreadable *and* still fully live

**severity: medium — bug**

On the state a fresh install shows (the plan sensors do not exist yet), and on
the state the dashboard card picker previews, all **7 of 7** legend chips carry
`.nodata`, whose only rule is `cursor: not-allowed; opacity: 0.3`
(`heatpump-optimizer-card.js:2908`). Composited over the card background that
is **1.90:1** on HA light and **2.36:1** on HA dark — against WCAG 1.4.3's
4.5:1 floor. See `shots/D4-01-no-plan-light.png`: the seven chip labels are a
pale wash while the empty-state paragraph beneath them is fully legible.

WCAG 1.4.3's "inactive user interface component" exemption does **not** apply,
because the chip is not inactive:

* `chip_nodata_is_disabled=0` — no `disabled`, no `aria-disabled`.
* `chip_nodata_tabbable=7` — every one is reachable by Tab.
* `chip_nodata_click_persists=1` — a click runs `Legend.onChipClick`, flips
  `aria-pressed` from `true` to `false`, and writes `{"price":true}` into
  `localStorage` under the card's own storage key. That preference **survives**
  the arrival of plan data, so a user who taps a chip they cannot read, on a
  control whose cursor says `not-allowed`, silently and permanently hides that
  trace from the chart they are waiting for.

The `not-allowed` cursor and the live click handler disagree about what the
control is; the 0.3 opacity makes the label unreadable in the one state where
the card has nothing else to say.

* **metric**: WCAG 2.x contrast ratio of a `.chip.nodata` label against the
  resolved card background, sRGB, with the element's computed opacity
  composited in.
* **instrumented symbol**:
  `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:Legend.onChipClick`
  (and the `.chip.nodata` rule the same file's style block emits). The harness
  reads `getComputedStyle` off the live element and dispatches a real click.
* **perturbation**: append `.chip.nodata { opacity: 1; }` to the card's shadow
  root -> `chip_nodata_contrast_light` **1.90 -> 16.10** (up, past 4.5).
* **arm where it must vanish (null control)**: the same card given the three
  plan sensors -> **0** `.nodata` chips and a worst chip contrast of **16.10**.
  The defect is a property of the no-data arm, not of the legend.
* **files**: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
* **fix scope**: either make the chip genuinely inactive (`disabled` +
  `aria-disabled="true"`, and skip it in `Legend.attach`'s wiring), which makes
  the exemption real and the trap impossible; or keep it live and raise the
  dimming to a contrast-safe treatment. Not both as they stand. A card-markup
  claim in `tests/golden/card_claimed_drift.txt` will be needed for `no_plan`
  and `no_plan_expanded`.

### D4-02 — the away strip is the one feature block with no CSS at all

**severity: medium — bug**

`AwayControls`' markup (`heatpump-optimizer-card.js:3875`) emits
`<div class="away-strip"><label><input type="checkbox">...</label>...`, and the
card's style block — which carries rules for **69** distinct class selectors —
carries **none** for `.away-strip`. Everything in that row is therefore browser
default, inside a dialog where every neighbour is styled. Measured in the
expanded dialog, under an emulated **coarse** pointer, at 375x812:

| what | measured | required / control |
|---|---|---|
| the Away checkbox | **13 x 13 px** | 24 px (WCAG 2.2 SC 2.5.8) |
| its wrapping `<label>` (the whole activation area, so "the label rescues it" does not hold) | **51.8 x 14** and **223.7 x 14 px** | 24 px |
| the Return `datetime-local` input | **184.3 x 21.3 px** | 24 px |
| gap between the strip's two children | **0 px** (`display:block`, `gap:normal`) | `.legend` on the same page: `display:flex`, `gap:6px` -> **6 px** |
| every control the card's own `coarseHtmlTargets` rule set names | **24 px minimum over 29 controls** | — |

That last row is the control that makes this a hole rather than a policy: the
card *does* enforce a 24 px coarse-pointer floor, on twelve selectors
(`.expand, .close, .viewctl button, .chip, .dlg-tab, .layout-bar button,
.whatif button, .whatif input[type="time"], .whatif .wi-win-days,
.whatif .wi-viewreset, .sp-actions button, .slot-menu button`), and every one
of the 29 controls those match clears 24 px on the same page in the same run.
`.away-strip` is simply not in the list.

The 0 px gap is visible in `shots/D4-02-away-strip-coarse.png`: the row reads
**"AwayReturn"** as one word (Swedish: "BortaHemkomst"), directly above a chart
whose every other control is a rounded, padded chip.

What a user cannot do: on a phone — the device on which "I am away" actually
gets toggled — the control that stops the heat pump heating an empty house is a
13 px target, and the label that would enlarge it is 14 px tall.

* **metric**: the smaller side, in CSS px, of the smallest activation area in
  the expanded dialog's `.away-strip`, under an emulated coarse pointer.
* **instrumented symbol**:
  `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:AwayControls`
  (the `.away-strip` markup) — the harness opens the real dialog and measures
  the rendered elements' `getBoundingClientRect`.
* **perturbation**: append, after the dialog render,
  `.away-strip input[type='checkbox']{width:24px;height:24px}` +
  `.away-strip label{min-height:24px;display:inline-flex;align-items:center}` +
  `.away-strip input[type='datetime-local']{min-height:24px}` ->
  checkbox **13 -> 24**, label **14 -> 28**, return input **21.3 -> 28** (all up).
  The style has to be appended *after* `_render()`: `_render()` replaces the
  shadow root's `innerHTML` and drops a style appended before it.
* **files**: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
* **fix scope**: give `.away-strip` a rule set (flex row, gap, padding) and add
  `.away-strip input, .away-strip label` to `coarseHtmlTargets`. `away_toggle`,
  `away_return` and `away_status` will drift in the card markup gate.

### D4-03 — the flow groups its fields on the revisit, not on the first run

**severity: medium — bug**

The options flow declares **34** `section()` groupings across 10 of its 21 form
pages. The initial config flow declares **0** across all 11 of its form pages
and **70** presented fields. The two flows present largely the same fields:

**55 of the 70 fields the initial flow presents flat are presented inside a
named `section()` by the options flow.** Per page:

| initial-flow page | fields | of which the options flow groups |
|---|---|---|
| `config.user_sensors` | 14, no sections | 10 (options: `indoor` / `plant`) |
| `config.dhw` | 11, no sections | **11 of 11** (options: `schedule` / `temperatures` / `legionella`) |
| `config.zones` | 11, no sections | **11 of 11** |
| `config.thermal` | 10, no sections | 3 |
| `config.temperature` | 7, no sections | **7 of 7** |
| `config.building_describe` | 6, no sections | **6 of 6** |
| `config.weather_sensitivity` | 2, no sections | 2 of 2 |

So the screen a user meets when they know least about the integration —
`user_sensors`, fourteen entity pickers in a flat list — is the ungrouped one,
and the screen they return to when they already know what everything means is
the grouped one. `config.user_sensors` alone asks for the indoor probe, the
outdoor probe, the pump switch, the solar sensor and its forecast source and
location, two floor probes, the DHW and buffer probes, and four heat-pump
diagnostic entities, with no heading telling a first-time user which of them
the integration cannot start without.

Three of the seven form pages with >= 8 fields and no sections are in the
options flow too (`options.grid` 9, `options.heat_curve` 9,
`options.thermal_model` 8), so the pattern is not purely a config/options
split; the config flow is where it is total.

* **metric**: the count of field keys the initial flow presents outside any
  `section()` that the options flow presents inside one, over the pages both
  flows' handlers really return.
* **instrumented symbol**:
  `heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow` and
  `heatpump_optimizer.config_flow:HeatPumpOptimizerOptionsFlow` — the harness
  calls each `async_step_*(None)` and reads `result["data_schema"]`; nothing is
  read off the source.
* **perturbation**: wrap `async_step_dhw`'s schema in the same three
  `section()` groups the options `hot_water`/`hot_water_tank` pages use ->
  `config_sections_total` **0 -> 3**, `ungrouped_pages_ge8_fields` **7 -> 6**,
  `config_flat_fields_grouped_in_options` **55 -> 44** (down).
* **arm where the effect must vanish**: the options flow's own pages, measured
  by the same code in the same run — 34 sections, 10 of 21 pages grouped. A
  metric that reported "no sections anywhere" would be measuring the walker,
  not the flow.
* **files**: `custom_components/heatpump_optimizer/config_flow.py`,
  `custom_components/heatpump_optimizer/strings.json`,
  `custom_components/heatpump_optimizer/translations/en.json`,
  `custom_components/heatpump_optimizer/translations/sv.json`
* **fix scope**: sections are a schema-and-strings change with no behaviour
  change (the submitted data is flattened by the frontend), so the four widest
  initial pages can adopt the section names the options flow already
  translates. `tests/golden/config_flow.json` fingerprints will move; the
  presented-field set must not.

---

## Non-findings — what was checked and held

| what held | command | number |
|---|---|---|
| No card state clips content out of reach at any viewport. 396 cells; overflow measured against the nearest ancestor that actually clips (`overflow-x: hidden/clip`), not against the card box. | `node tools/audit/round3/D4/card_states_geometry.mjs` | `clipped_overflow_cells=0` |
| No card state gives the document horizontal scroll. | same | `doc_hscroll_cells=0` |
| No HTML text box in any state clips its own content (`scrollWidth > clientWidth` on an overflow-hidden box). | same | `clipped_text_cells=0` |
| No state throws. 396 cells, `pageerror` and console-error listeners on every page. | same | `page_error_cells=0`, `render_failures=0` |
| Exactly **one** text site in the whole card fails WCAG AA across 396 cells, and it is D4-01. Disabled controls are excluded per WCAG 1.4.3's inactive-component exemption. | same | `low_contrast_sites=1` |
| Under a **coarse** pointer only 3 selectors fall under 24 px, against 31 under a fine pointer: the card's coarse rule set does its job everywhere it is applied. Two of the three are 0.8 px and 9 px shortfalls (`input.sp-filter` 23.2, `span.hl-score` 15.0); the third is D4-02. | same | `small_target_cells_coarse=24` vs `small_target_cells_fine=198` |
| The setup diagram's 230 px of phone-width overflow is **reachable**, not lost: `@media (max-width: 600px)` gives `.setup-canvas { overflow-x: auto }` with `min-width: 560px` on the svg, a deliberate choice recorded in the source. | same | `scrollable_overflow_cells=24`, all 24 in the six setup states at the phone viewport, 230.0 px each |
| **Disproved lead.** 372 of 396 cells report an SVG `<text>` box overlapping another `<text>` box — including axis unit titles over their top tick, by 8.9 x 2.2 px on the compact tile. It is **not** an ink collision: `getBoundingClientRect` on SVG text returns the font's em box, not the glyph outline. Rasterising every unit-title/tick pair at the chart's own viewBox resolution returns zero overlapping ink, on the inline chart (which `tests/card_browser.mjs`'s ink lane never reads — it takes the *last* `.chartwrap svg`, the dialog's) as well as the dialog's. Harness gap named; no finding. | `node tools/audit/round3/D4/card_ux_defects.mjs` | `axis_ink_overlap_pairs_inline=0`, `axis_ink_overlap_pairs_dialog=0` |
| Every one of the 257 presented flow fields has a translated **label** in all three catalogues. | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D4/flow_ergonomics.py` | `fields_without_label_*=0` (x3) |
| Only **one** of the 257 lacks a help line, in all three catalogues, and it is `config.reauth_confirm.tibber_token` — a single-field re-auth page whose title and description already say what to paste. | same | `fields_without_help_*=1` (x3) |
| The Swedish catalogue is at parity with English on labels and help lines: the same 0 and the same 1. | same | `fields_without_label_sv_json=0`, `fields_without_help_sv_json=1` |
| The options menus are shallow and ordered: 7 items on top (6 pages + Advanced), 15 behind Advanced, so no revisited page is more than two clicks from `init`. | same | `options_top_menu_items=7`, `options_advanced_menu_items=15` |
| The path from install to a first plan is five screens: `user -> user_sensors -> finish_setup (menu) -> finish_now -> setup_overview -> create_entry`; a user who skips the questionnaire never opens the 15-page advanced tree. | same (`pages_walked=36`, the two menus' `menu_options`) | 2 form pages + 1 menu + 1 overview before `create_entry` |
| The card's own `coarseHtmlTargets` floor is real: all 29 controls it matches in the open dialog clear exactly 24 px under an emulated coarse pointer. | `node tools/audit/round3/D4/card_ux_defects.mjs` | `coarse_ruleset_min_px=24` |

## What I could not finish

* **Tab-order sequence.** Reachability was measured (`tabIndex >= 0` on all
  seven `.nodata` chips); the *order* a Tab walk visits every focusable in the
  expanded dialog was not. That needs a keypress walk per state and would have
  doubled the sweep's runtime.
* **Layout shift on hover.** Not measured.
* **Config-flow rendering.** Not observable here (no HA frontend); see Limits.
* **`tests/setup_qa_render.mjs`** was deliberately not run: its header says it
  writes SVGs to `../setup-qa/`, outside the repository. The three setup
  topologies it renders were driven in-browser instead, through the same
  `qaTopologies()` payloads, inside this sweep.

## Harnesses

| path | what it produces |
|---|---|
| `tools/audit/round3/D4/card_states_geometry.mjs` | the 396-cell sweep; every RESULT above with a `*_cells` or `*_sites` name |
| `tools/audit/round3/D4/card_ux_defects.mjs` | D4-01 and D4-02's numbers, their perturbation arms, their null arms, and the rasterised ink control for the disproved lead |
| `tools/audit/round3/D4/flow_ergonomics.py` | D4-03's numbers and the flow non-findings |
| `tools/audit/round3/D4/shots.mjs` | the screenshots in `shots/` (not a measuring instrument) |

Each is runnable by the single command in its own header. All four need a plan
payload written first, to a private path:

```
export HPO_PLANDATA=$TMPDIR/plandata-d4.json
PYTHONPATH=tests/hastub python3 tests/plan_view.py
```

and the two browser harnesses need
`NODE_PATH=/private/tmp/hpo-pw/node_modules` and
`PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers`.

## Exposure

None. Nothing under `docs/` was read, `gh` was not run, GitHub was not read, and
no earlier audit finding was looked for. The `D4-01`...`D4-06` identifiers that
appear in `tests/card_browser.mjs`'s comments were read as part of reading that
file's checks; they were treated as context, and the ids in this report are
this round's own numbering.
