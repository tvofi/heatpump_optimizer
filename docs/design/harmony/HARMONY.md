# HARMONY — the card's design voice, page by page

Pre-study for the owner's ask (tvofi, 2026-10-20): *review every card page
against the canonical design voice and propose and prototype any changes to
harmonize the card. No changes needed is also an acceptable answer.*

- **Seat:** local design pre-study, refs only. No live-card change, no test
  change, no issue, no pull request.
- **Ref:** `probe/card-harmony-design` (this directory lands at
  `docs/design/harmony/`).
- **Card under study:** `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
  at this branch's base (`76bb45628`, 2026-10-20). Line numbers are that file.
- **Method:** the card was mounted in real Chromium from
  `harness/harness.html` (frozen `Date` at the first forecast slot + 6 h, a
  fixed `hass.states` fixture in `harness/states.js`, light and dark via
  `hass.themes.darkMode`), at 375×900, 768×900 and 1280×900. Open it as
  `harness.html?page=plan` — `page` is `plan`, `setup`, `savings`, `advisor` or
  `health`, `tile` leaves the dialog closed, and `theme=dark` selects the dark
  tokens. Every size and contrast below is
  `getComputedStyle`/`getBoundingClientRect` in that browser, not a redrawing.
  The four prototype pages are **generated from the card's own rendered
  dialog markup and its own stylesheet** (`cardStyleBlock(darkMode)`), so the
  "before" panels are the shipped CSS, and the "after" panels differ only by
  the rules each proposal names.
- **What is not in this study:** the Lovelace config editor (`editor_schema`
  in the drift suite) is a separate surface, not a page of the card; the live
  diagnostics bundle view is not a card page.

---

## 1. The canonical design voice

The card declares its system in two token tables (`CARD_TOKENS` 3845-3879,
`CARD_SCALE_TOKENS` 3883-3889) and writes every rule against them, one
`var()` level deep with the light literal as the fallback (`themeFallbacks`,
3904-3909, swaps the fallbacks for the dark literals). That declaration is the
voice; the audit below is the distance from it. Twelve checkable statements:

**V1 — One base, 14 px, and the dialog never goes under it.** The card's text
inherits the host (Home Assistant's 14 px; measured 14 px on the card face).
`dialog.expanded` instead sets its own base from its width,
`clamp(12, width × 0.0105, 21)` (`DIALOG_FONT_RATIO/MIN/MAX` 2100-2102,
`scaleFont` 9627-9646). An *enlarged* view must not render the same role
smaller than the tile. **Check:** the dialog's computed base against 14.

**V2 — Type ramp 12 / 13 / 15 / 18.** `--hpo-text-xs/sm/md/lg`
(3887-3888) are the HTML steps; measured on the card face: labels 12, chips 13,
headline value 15, tile number and title 18. Headings 600; dialog chrome 500;
**no 700** (the Health headings are the one UA-700 inheritance, H3b).

**V3 — Captions are 0.76–0.85 em, and never below 12 px on an HTML surface.**
`.legend-note` 0.76 em (4260), `.sb-text` 0.78 em (4216), `.hl-caveat` 0.82 em
(4153), `.setup-hint/.setup-result/.adv-basis/.adv-note/.adv-sub/.health-mark/.whatif .wi-hint/.viewctl button`
0.85 em (4579, 4583, 4858, 4859, 4851, 4833, 4917, 4294). They are footnotes,
not a second ramp; but the ramp's smallest step is 12 (`--hpo-text-xs`), and a
surface that drives a caption under it has left the system. **Check:** every
HTML text node's computed size ≥ 12.

**V4 — A scaled drawing is not text.** The chart and the setup map draw in
viewBox units; their rendered size is a function of the drawing's width, not of
the HTML ramp. The chart *floors* its rendered axis text at 8 px
(`MIN_AXIS_FONT_PX = 8`, 1801, applied by `chartFontUnits`, 1831-1835; the
comment records the phone tile that rendered at ~3.2 px before the floor). The
setup map has no floor constant but a phone `min-width: 560px` inside a
sideways-scrolling canvas (5039-5041), which keeps its smallest label at 8.6 px
at 375. **Check:** every drawing's smallest rendered text ≥ 8 px.

**V5 — A surface and its ink switch together, from one source.** The tokens
say it outright: *"one pair, one switch"* (3851-3857). `--hpo-ink`/`--hpo-ink-2`
are the literals for `--hpo-surface-2`; a theme variable may be the *first*
choice but only where the ink is the theme's too (`--hpo-text` and
`--hpo-text-2` stand for `--primary-text-color`/`--secondary-text-color`). A
row that takes its surface from `--secondary-background-color` but its text
from `--hpo-text` breaks the pair (the Health/Advisor rows, H3a).

**V6 — Status is a dot and a word in a token pair.** ok/warn/crit each carry a
text colour and a background (`--hpo-ok/-bg`, `--hpo-warn/-bg`,
`--hpo-crit/-bg`, 3865-3872); the healthy/stale pill and the health marks use
them, never colour alone.

**V7 — Space 4 / 8 / 12 / 16 / 24** (`--hpo-space-1..5`, 3884-3885); the card's
own padding 12, the dialog 16 (12 at ≤600 px, 5032), a page 0.5 em × 0.25 em
(`.setup-page` 4498).

**V8 — Radii 6 / 12 / pill** (`--hpo-radius-s/m/pill`, 3886); the dialog's
chips use `1.3em` (4468), the map's boxes 10 drawing units (4518-4521), and
the drawn Configure control is styled as *"the same border, radius and label
size a legend chip wears"* (4562-4564) — a claim the audit measures (Setup).

**V9 — Strokes 1 / 1.5 / 2 / 3.5.** 1 for outlines, dividers and chip borders
(4520, 4526, 4565); 1.5 for icons, pipes and pipe dots (4531-4539); 2 for the
focus ring (4129); 3.5 for the editing pipes (4629). Colour by role, never by
weight.

**V10 — Targets 24 px every pointer, 44 px coarse** (`_targetMinPx()`;
`TARGET_MIN_PX`/`TARGET_MIN_PX_COARSE`), SVG targets converted with
`unitsPerPx` (3632-3640).

**V11 — One decorative motion**, the chart view-controls' 120 ms fade
(4284), off under `prefers-reduced-motion` (4280-4286).

**V12 — One empty state shape.** `.empty` — muted, centred, 28 px 12 px
(4312-4324) — is used by the no-plan state, the setup page (14195) and the
advisor page (9289). Savings is the exception (H3c).

### Where conventions disagree, which wins

- **Token px vs em chrome.** The px ramp wins for content; the em scale is the
  dialog's *chrome* mechanism. The dialog base therefore has to sit at or above
  the card base (V1) or the em roles fall out of the ramp.
- **Ramp floor vs drawing floor.** Inside a drawing, V4 wins: the 8 px floor is
  the legibility floor there, and the 12 px ramp does not apply. (The chart
  text is 8–22 px by width; the reader is not meant to read it as body text.)
- **The phone legend's `1rem` vs the dialog's `1em`.** At ≤600 px the legend is
  a touch row and the card raises it to 16 px (5033); above 600 px it is 1 em of
  the dialog base. The phone rule wins where it applies.
- **A theme variable vs the card literal.** The theme variable is the first
  choice only when the ink comes from the theme too (V5). Where the ink is the
  card's literal, the surface must be the literal's pair.

---

## 2. Every page and view: 23, and how the count is derived

**What counts.** A *view* is a root the card paints into — the card body or
the dialog body — or a state that *replaces* a root's body when its data is
absent. Overlays and hover/drag layers that paint into an already-counted root
are *panes*, counted separately. The Lovelace config editor is a separate
surface, not a card view. This rule is the card's own `_render` structure
(card body 13895-13905, dialog body 13914-13945, `activePage()` 9457-9462).

| # | view | trigger | code | drift state(s) |
|---|---|---|---|---|
| **Surfaces — 6** |||||
| 1 | Card face | dialog closed | `_render` body 13895-13905 (chart, or the no-plan body in row 7) | `plan_inline`, `plan_inline_sv`, `plan_short_window`, `custom_title_currency`, `hidden_series`, `score_open`, `away_*`, `wood_*` |
| 2 | Plan page | dialog, tab Plan | 13936-13944 | `expanded_plan`, `expanded_zoomed`, `what_if_off`, … |
| 3 | Setup page | dialog, tab Setup | `_setupPageHtml()` 14192 | `setup_single_buffer`, `setup_two_tank`, `setup_coil` |
| 4 | Savings page | dialog, tab Savings | `_savingsPageHtml()` 14100 | **none** |
| 5 | Advisor page | dialog, tab Advisor | `advisorPageHtml()` 9281 | `advisor_page` |
| 6 | Health page | dialog, tab Health | `healthPageHtml()` 9105 | **none** |
| **Page states — 4** |||||
| 7 | No plan (card face and Plan page) | no plan data | 5723, 13944 | `no_plan`, `no_plan_expanded` |
| 8 | Setup — topology not published | `setup_topology` absent | 14194-14197 | **none** |
| 9 | Savings — no settled months | `savings_months` empty | 14134-14136 | **none** |
| 10 | Advisor — no ranked candidates | `sensor_advisor.candidates` empty | 9287-9291 | **none** |
| **Panes — 10** |||||
| 11 | What-if panel | `what_if` config, Plan | 13943, `whatIf.html()` | `what_if_off`, `whatif_edited`, `whatif_weekly`, `override_active`, `shared_steps*`, `wood_whatif` |
| 12 | Chart tooltip / crosshair | pointer over plot | tooltip + crosshair | `tooltip_hover`, `shared_steps_hover` |
| 13 | Slot menu / draft lanes | drag or click a lane | `draft_dirty_menu_open`, `draft_mid_drag` | `draft_dirty_menu_open`, `draft_mid_drag` |
| 14 | Score breakdown | click the score | `_scoreOpen` 13979-13990 | `score_open` |
| 15 | Away strip | away entities present | `awayStripHtml()` | `away_toggle`, `away_return`, `away_status` |
| 16 | Wood alert | wood fuel on / tank state | `woodAlertHtml()` 5632 | `wood_alert`, `wood_lane` |
| 17 | Chart history panes | recorder data past the plan | `histSource` | `history_panned`, `history_deep_panned` |
| 18 | Setup layout editor | Setup, Edit layout | `layoutEditor` | `layout_editing_dragged`, `layout_editing_tidy` |
| 19 | Setup entity picker | click a slot | `pickerHtml()` 14212 | `picker_open_filtered` |
| 20 | Advisor inbox | rows or actions present | `advisorInboxHtml()` 9282 | rendered by `advisor_page` |
| **Chart data states — 3** |||||
| 21 | History unavailable | recorder refuses | `history_unavailable` | `history_unavailable` |
| 22 | History pending | first fetch in flight | `history_pending` | `history_pending` |
| 23 | History without power | no power entity history | `history_no_power` | `history_no_power` |

**The count: 6 surfaces + 4 page states + 10 panes + 3 chart data states = 23.**

**Cross-check against `tests/card_drift.mjs`.** Its `STATES` array holds 40
scenarios (`tests/card_drift.mjs:208`). They cover **18 of the 23 views** and
leave five unpinned:

- the **Savings page** (with data) — no drift state at all;
- the **Savings empty state** — none;
- the **Health page** — none;
- the **Setup not-published empty state** — none;
- the **Advisor empty state** — none (`advisor_page` carries candidates).

The suite's 40 states also include `editor_schema`, which is the Lovelace card
editor, outside the 23 (a separate surface). So "40 states" is not "40 pages":
it is 40 scenarios over 23 views, with two whole dialog pages and three empty
states unrepresented.

**Cross-check against `tests/card_rig.mjs`.** `planStates()` (161-183) returns
three entities — solar irradiance, the space plan, the DHW plan — and drives
only the card-face chart and the Plan page. The other four pages need
`setupSensorStates()`, `qaTopologies()`, `layoutCatalogTopo()`, `historyApi()`
and the file-local stat fixtures (card_drift imports them at 51-55). The
fixture's name is accurate; the pages are not all plan-shaped.

---

## 3. Page-by-page audit

Measured at 375×900, 768×900 and 1280×900, light and dark. "HTML below 12"
counts text-bearing HTML elements with computed font-size under 12 px; SVG
`<text>` is excluded and treated under V4 (its computed px is in user units,
its *rendered* size is `units × chart scale`).

| surface | HTML text nodes (768) | below 12 px @375 | below 12 px @768 | below 12 px @1280 | verdict |
|---|---|---|---|---|---|
| Card face | 65 (at 900) | 5 (legend 10.6, caveat 11.5, zoom ×3 11.9) | 5 | 5 | H1 (caption floor) touches it; otherwise no change |
| Plan | 68 | 21 | 22 | 22 | **H1** |
| Setup | 10 | 3 | 3 | 3 | **H1** (hint) + **H2** (bar) |
| Savings | 54 | 0 | 0 | 0 | **H4** (replay chart; not HTML) + **H3c** (empty) |
| Advisor | 33 | 4 | 4 | 4 | **H1** + **H3a** |
| Health | 50 | 13 | 13 | 13 | **H1** + **H3a** + **H3b** |

At 768 px that is **42 HTML nodes below the ramp's floor in the five dialog
pages + 5 on the card face = 47**; at 375 the dialog's count is 41 (the plan
loses its legend note to the phone `1rem` rule) for **46**. The dialog is not
uniformly bad: the token-px content (stats 12/15/18) is unchanged; it is the em
chrome and the captions that fall.

### 3.1 Card face

- **Voice as shipped:** title 18/600, tile numbers 18/600, headline value 15,
  chip 13 (`--hpo-text-sm`, 3992), labels/pill/units 12 (`--hpo-text-xs`),
  base 14. Measured.
- **Below 12:** `.legend-note` 10.6 (0.76 em of 14), `.hl-caveat` 11.5
  (0.82 em), `.viewctl button` 11.9 (0.85 em) — three of the same caption
  roles as the dialog's, one surface over. On the tile they are 0.1–1.4 px under
  the 12 px step, not the 2–3 px the dialog shows.
- **Deliberate:** the chart's axis text is floored at 8 rendered px (V4); at
  900 px the chart renders 832 px wide (scale 0.924) and its axis text at 13.9
  px; in a 375 px dialog the floor produces 8.0 px (measured).
- **Verdict:** no structural change. H1's caption floor is the only rule that
  touches it, and by 0.1–1.4 px.

### 3.2 Plan page

- **The inversion.** The dialog base is **12.0 px at 375 and 768, 12.9 px at
  1280** (the dialog is 360/737/1229 px wide; `width × 0.0105`). The card base
  is 14. The dialog is smaller than the tile until the dialog itself is
  ≥1333 px wide (0.0105 × 1333 = 14.0), which on a 1280-wide browser it is
  not. This is the core of H1.
- **Below 12 (21 at 375, 22 at 768/1280):** 3 zoom buttons 10.2, 2 `wi-add`
  10.8, 6 what-if group titles 10.8, 9 what-if hints 10.2, 1 `hl-caveat` 9.8,
  and above 600 px the legend note 9.1–9.8. **17 of the 21/22 are in the
  what-if panel** — the panel is the page's densest small type.
- **The phone legend is already rescued:** the ≤600 px rule sets
  `dialog.expanded .legend` to `1rem` (5033), so at 375 the legend chips are 16
  px and the note 12.16 px; the base's 12 does not reach it. On a phone the
  page's own hints, titles and zoom controls are what fall.
- **Chrome geometry:** the head is 1.4 em (16.8 px at 768); the tabs are 0.85
  em *of the head* (1.19 em = 14.28 px at 768, 15.35 at 1280) — the tabs are
  larger than the chips (12/12.9), which is coherent for chrome and needs no
  change.
- **Verdict:** H1. No other change.

### 3.3 Setup page

- **The declared "one rule, two surfaces" is broken in the dialog.** The shared
  rule names both: `.chip, .layout-bar button { … border-radius:14px;
  font-size:0.82em }` (4223-4230, comment at 4221-4223). The dialog then raises
  `.chip` to `font-size:1em; border-radius:1.3em` (4466-4469) and never names
  `.layout-bar button`. Measured in the same dialog: legend chip 12.0 px at
  375/768 and 12.9 at 1280; tank-bar/Edit buttons **9.8 / 9.8 / 10.6**. H2.
- **The map's type is a scaled drawing (V4).** Measured rendered sizes at
  375 / 768 / 1280: title **10.1 / 12.6 / 21.5** px, slot rows **9.3 / 11.7 /
  19.8**, Configure label **8.6 / 10.7 / 18.2**. The mechanism is deliberate —
  `min-width:560px` inside `.setup-canvas{overflow-x:auto}` below 600 px
  (5039-5041) keeps the smallest label above the chart's 8 px floor. But the
  stylesheet's own claim that the drawn Configure control wears *"the same
  border, radius and label size a legend chip wears"* (4562-4564) is false away
  from ~768: 8.6 px vs 12 at 375, 18.2 vs 12.9 at 1280. **No change proposed**
  (the drawing's scale is the page's working model); correction **C2** records
  the false claim.
- **Below 12 (HTML):** the two bar buttons (9.8) and `.setup-hint` (10.2);
  H1 + H2 cover them. The map's labels are drawing text, not counted here.
- **Verdict:** H2 (+ H1's hint), badges carry the owner's decision.

### 3.4 Savings page

- **With data: no HTML text under 12** (54 nodes at 768). The page is
  compliant.
- **The replay chart is the exception to V4.** It is a 600×330 drawing
  (`replayPanel` 9219-9231, `replayHtml` 9257-9260) with literal 11/12-unit
  labels. Measured rendered: **6.2–6.8 px at 375**, 12.9–14.1 at 768,
  **21.9–23.9 at 1280** — no floor, no cap, unlike both other charts. It is
  under the card's own 8 px floor on a phone. H4.
- **Latent:** `RECEIPT_CSS` (9132-9155) writes `var(--hpo-text-sm, 14px)` three
  times (9138, 9143, 9154) while the token is **13 px** (3887). The fallback
  never fires while the token is declared, so nothing renders wrong today; it
  is still a fallback that disagrees with the token. Correction C1.
- **Empty state:** `<p class="savings-empty" style="margin:1em 0">` (14135) —
  primary ink, left aligned, no panel — beside the other three empty states'
  `.empty` (H3c).
- **Verdict:** H4 + H3c; the data view needs no design change.

### 3.5 Advisor page

- **Surface/ink split (V5).** `.adv-inbox-row` takes
  `background: var(--secondary-background-color, #f5f5f5)` (4844-4850) while
  its text is `--hpo-text` (the card literal). Measured in dark with the theme
  variable absent: **#f5f5f5 on #e1e1e1 = 1.20:1**. The same pair on
  `--hpo-surface-2` is **11.08:1**. H3a. (Stock Home Assistant themes define
  `--secondary-background-color`; this is the arm the card's own literal pairs
  exist for — a theme without it, or a non-HA host.)
- **Below 12 (4):** `.adv-note` 10.2, `.setup-hint` on the page 10.2,
  `.adv-basis` 10.2, an unpriced `.adv-value` 10.2 (0.85 em, 4860-4864). H1.
- **Empty state** uses `.empty` (9289) — the model the savings page should
  follow.
- **Verdict:** H1 + H3a.

### 3.6 Health page

- **Same split (V5):** `.health-row` at 4808-4813 is the advisor row's twin;
  measured 1.20:1 dark with the variable absent. The support row is the same
  class. H3a.
- **The only 700 weight.** `.health-h` (4807) sets no weight, so the `<h3>`
  takes the UA's 700; every other heading in the card is 600 (`.whatif
  .wi-group-title` 4913, `.adv-unpriced-head` 4857) and the dialog head is 500
  (4463). Measured weight 700. H3b.
- **Below 12 (13):** 10 `.adv-sub` 10.2 and 3 `.health-mark` 10.2. H1. The
  mark is a fixed 1.4 em circle with a 0.85 em glyph (4833-4838); raising its
  font enlarges the circle from 14.3 to 19.6 px at a 14 px base — a visible but
  coherent change (the mark is a control-sized glyph).
- **No empty state** by design: the checklist is meaningful with every input
  missing (it is how the page says what is missing).
- **Verdict:** H1 + H3a + H3b.

---

## 4. Proposals

Each proposal is a self-contained page: the card's tokens, its captured
stylesheet and markup, light/dark and 375/768/1280 from the same controls.
The pages mirror the card's ≤600 px media query with a container query, because
a 375 px frame inside a wider window does not change the viewport those rules
key on.

### H1 — The dialog type floor
`harmony-1-type-floor.html`

**What.** (a) `DIALOG_FONT_PX_MIN` 12 → **14**: the dialog base becomes the
card's base at every width below the 1333 px crossover, and the em chrome
(legend, tabs, head, chips) stops shrinking relative to the tile. (b) The
caption roles get `font-size: max(12px, <their em>)` on both surfaces, so no
HTML role renders under the ramp's smallest step.

**Measured effect** (375 / 768 / 1280): dialog base 12/12/12.9 → **14/14/14**;
what-if hints 10.2/10.2/11.0 → **12**; group titles 10.8/10.8/11.6 →
**12.6/12.6/12.6**; legend note (≥600 px) 9.1/9.8 → **12**; on the card face
legend 10.6 → 12, caveat 11.5 → 12, zoom 11.9 → 12.

**Cost.** At 375 the dialog head grows 141.8 → 162.8 px (+21.0) and the tab row
71.9 → 83.2 px (+11.3), so the body loses 20.9 px; the tab strip still fits the
same number of rows and the phone legend is unchanged (it is already `1rem`).
The tile's footnotes grow 0.1–1.4 px. The 21 px cap stays unreachable (C3).

**Risk.** One new behaviour at 1280: the dialog title (1.4 em) goes from 18.06
to 19.6 px, slightly above the tile's 18 px title. That is the enlarged view
doing what it says.

### H2 — The setup page's controls, and the Badge
`harmony-2-setup-controls.html`

**What.** Carry the dialog's own chip rule to the control the shared rule
already names: `.layout-bar button { font-size: 1em; border-radius: 1.3em }`
inside `dialog.expanded` (the same two lines the chip gets at 4466-4469).
Carry the owner's chosen Badge (prototype 1) into the map: a disc on the outer
corner of every box, the wood tank's glyph the spring.

**Measured effect.** Bar buttons 9.8/9.8/10.6 → **12/12/12.9** (1 em), radius
14 → 15.6/15.6/16.8. Badge disc 18 units → **14.0 / 17.5 / 29.8 px** rendered;
glyph stroke 1.5 units (the card's icon/pipe tier), disc stroke 1 (the box
outline tier).

**What the Badge decision still owes the page** (reconciliation carried from
the design pre-study):

- The glyph stroke is **1.5** units — the card's icon and pipe tier — not 1.6,
  which is on no tier.
- The Configure control's page-name line is **11 units**, the same tier as its
  "Configure" label and the existing chip; not 10, which no drawing text uses.
- The coil-state wording stays on its 11-unit lines; the badge adds no colour
  outside accent, divider and text-2.
- The badge is supplementary: the box's accessible name already carries the
  type and the coil state, so the disc is `aria-hidden`.
- The disc scales with the map (14 px at 375, 30 px at 1280). It is a symbol,
  not type; the map's smallest text at 375 is 8.6 px and the disc is 14.

**Cost.** Two CSS lines and the badge geometry in `setupSvgHtml` (one `<g>`
per box, after the carrier rect). No layout change: the disc is drawn in the
corner the box already reserves. **Risk.** The disc overlaps the box's top-right
border by design (a notch); at 1280 it is 30 px and needs the box's corner
clear of the folded-block chevron (the glyph set keeps to a 10-unit box, scale
0.92 inside a 9-unit-radius disc).

### H3 — Sibling surfaces and states
`harmony-3-sibling-states.html`

**What.** (a) `.health-row` and `.adv-inbox-row` take
`background: var(--hpo-surface-2, <literal>)` — the pair's own surface — instead
of `--secondary-background-color`. (b) `.health-h { font-weight: 600 }`.
(c) The savings empty state becomes the same `.empty` the other three empty
states use.

**Measured effect.** Row pair in dark 1.20:1 → **11.08:1**; health heading 700 →
**600**; savings empty: left/primary/no panel → **centred/muted/28 px 12 px**,
the advisor and setup shape.

**Cost.** Three CSS lines (the row rule is shared by both selectors; one weight;
one markup line in `_savingsPageHtml` replacing a `<p class="savings-empty">`
with `<div class="empty">`). **Risk.** In stock Home Assistant dark themes the
row already reads correctly; the change is a no-op there and a repair in the
unthemed arm. The heading change is visible everywhere; it is the only weight
change in the proposal.

### H4 — The Savings replay chart's labels (cheap, take first if only one)
`harmony-4-savings-chart.html`

**What.** Below 600 px, give the replay panel the setup map's existing
treatment: `.replay { overflow-x: auto }` and `.replay > svg { min-width: 560px }`
(inside the ≤600 px media query).

**Measured effect.** Labels 6.2–6.8 px at 375 → **10.3–11.2 px**, inside the
panel's own sideways scroll and above the card's 8 px chart floor. 768 and 1280
are unchanged (12.9–14.1 and 21.9–23.9).

**Cost.** Two CSS lines, the same mechanism already shipped for the setup map.
**Risk.** A sideways scroll on the Savings page at phone width, the same
tradeoff the setup page already makes. The alternative — the measured-width
floor the main chart uses — needs the render pipeline to measure this svg, a
larger change; the prototype shows the cheap path so the owner can judge.

### Small corrections (no prototype; each is one line)

- **C1.** `RECEIPT_CSS` `var(--hpo-text-sm, 14px)` ×3 → `13px` (9138, 9143,
  9154; token at 3887). Latent, not a visual defect today.
- **C2.** The Setup chip comment's claim that the drawn control wears the same
  label size as a legend chip (4562-4564) is false by width: 8.6–18.2 px vs
  12–12.9. Either cap the map's scale or correct the comment; this study does
  not change the drawing.
- **C3.** `DIALOG_FONT_PX_MAX = 21` is unreachable: the dialog's width caps at
  1700 px (`min(96vw, 78vh × ratio, 1700px)`, 4406), so the largest base is
  1700 × 0.0105 = **17.85 px**. Either lower the constant to 18 or record that
  it is aspirational.

---

## 5. No change needed — the explicit list

Deliberate, working deviations this study leaves alone:

1. **The chart's 8 px axis floor and its viewBox units** (V4). 8.0 px at 375 is
   the card's declared answer to a drawing that cannot be reflowed; the labels
   are furniture, not body text.
2. **The setup map's scaled type and its 560 px phone min-width** (V4). The
   measured 8.6–21.5 px is the drawing's model; only the comment's parity claim
   is wrong (C2).
3. **The phone legend at `1rem`** (5033). At ≤600 px the legend is a touch
   control row and is deliberately larger than the dialog's 1 em.
4. **The tabs' 1.19 em** (0.85 of the 1.4 em head): 14.3–15.4 px, larger than
   the chips by design; they are chrome, and they wrap rather than overflow.
5. **The 0.0105 width ratio** and the 21 px cap (the cap's reachability is C3,
   the ratio is fine).
6. **The tile's 13 px chip, 18 px title, 12 px labels** — the token ramp at
   work.
7. **The 6 px legend-chip gap, the 14 px shared radius on the tile, the 999 px
   pill** — three radii with three jobs (V8).
8. **The map's 10-unit box radius and 1-unit outlines**; the 1.5-unit pipes;
   the 3.5-unit editing pipes (V9).
9. **The status pairs and the dot-and-word status carriers** (V6).
10. **The single 120 ms fade and its reduced-motion arm** (V11).
11. **The Health page's absence of an empty state** — the checklist is the
    page's way of explaining what is missing.
12. **The em-based dialog chrome itself.** The mechanism is right; it needs the
    base floored (H1), not replacing.

---

## 6. What this study does not settle

- **The theme arm.** The 1.20:1 row is the "theme variable absent" arm. Stock
  HA dark themes define `--secondary-background-color`; the card's own rule
  exists so a theme is not required to. If the owner considers the unthemed arm
  out of scope, H3a is a robustness change, not a visible one in stock HA.
- **The setup map's ceiling.** At 1280 the map's title is 21.5 px and its
  Configure label 18.2 px — larger than the dialog's body. This is the drawing
  enlarging with the dialog. Whether it should cap is a design decision this
  study records but does not prototype.
- **The savings chart's ceiling.** At 1280 the replay labels are 21.9–23.9 px.
  H4 fixes the floor; the ceiling is the same open question as the map's.
- **Font metrics.** All sizes are Chromium on this machine. The ratios are
  computed from the card's own numbers, so they hold; the absolute px would
  shift by a browser's font stack.
- **The fixture's state set.** The harness mounts the card with a frozen date
  and one state fixture. Pages whose content depends on recorder history
  (Health's model/learning sections, the Plan history panes) were measured in
  their rendered form, but other data shapes may expose other roles.
