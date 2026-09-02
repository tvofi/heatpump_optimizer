# D4 — verifier seat 2 (consequence and reachability)

Worktree `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D4-2` at the
baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`. Scratch
`/private/tmp/claude-501/audit-scratch/D4-2`. Node 20.10.0, Playwright 1.49.0,
Chromium 1148, `PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers`. Python
3.11.5 + numpy 2.4.6 (`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`
— the shell `python` on this box has no numpy, so `tests/plan_view.py` fails
under it). Fan-out conditions: `load1` 8.7–56.6 during the runs. Every number
below is a count, a pixel size or a ratio, so none of them depends on load;
`thread_factor` was 1.00 throughout and no timing number is claimed.

## 0. The one thing this seat was asked first: is any of it already fixed on `origin/main`?

**No. Not one of the twelve.**

`origin/main` is `dd50689`. The card there is **not** a decomposed rewrite: it
is the same single file, `366 896` bytes against the baseline's `365 489`,
touched by exactly two commits since the baseline —

```
e403f75  Each chart copy keeps its own lane geometry (#138) (#164)
f945d44  Shared-band pattern ids are the card's own, and start over every render (#141) (#163)
```

— 59 insertions and 36 deletions in total. (The `#136` decomposition into
`ViewWindow` / `ManualPlan` / `LaneEditor` / `WhatIfPanel` / `SetupPage` /
`LayoutEditor` is *already in the baseline*; it is not post-baseline work.)
Those two commits replace `host.geom` with `host.geomAt(i)` and make the
shared-band `<pattern>` id sequence per-render. Neither touches a font, a lane
height, a colour, a hit size, an overflow rule, a config-flow schema or a
string.

Measured rather than argued. I extracted the whole `origin/main` tree with
`git archive origin/main | tar -x` (no checkout, no fetch, no worktree add)
into `$SCR/main-tree` and re-ran the finder's own harnesses there:

| RESULT (`card_geometry.mjs`, 26 states × 15 arms = 390 renders) | baseline (my re-run) | `origin/main` | finder |
|---|---|---|---|
| `text_overlap_pairs` | 1079 | **1079** | 1039 |
| `text_overflow` | 792 | **792** | 792 |
| `contrast_fail` | 1209 | **1209** | 1209 |
| `contrast_fail_light` / `_dark` | 891 / 318 | **891 / 318** | 891 / 318 |
| `hit_small_24` | 4221 | **4221** | 4224 |
| `hit_small_24_nospacing` | 1880 | **1880** | 1883 |
| `hit_small_44_coarse` | 548 | **548** | 548 |
| `slot_handles_small` | 2880 | **2880** | 2880 |
| `min_text_px` | 2.96 | **2.96** | 2.96 |
| `console_errors` / `hover_shift` / `focus_no_indicator` | 0 / 0 / 0 | **0 / 0 / 0** | 0 / 0 / 0 |

and `config_flow_ux.py` on the `main` tree reproduces **every** RESULT line
bit-for-bit (`user_page_fields=17`, `options_max_fields=23 (hot_water)`,
`pages_over_15=5`, `default_submit_warnings=1`, `off_theme_fields=1`, …),
despite `config_flow.py` having been rewritten twice on main (audit B3, B4).

My own harness (§below) confirms it element by element: `baseline` and `main`
are identical on axis font, lane height, slot width, target counts, what-if
contrast and empty-state overflow, at every tile width I tried.

The only two findings whose *text* changes on main are D4-11 (`CARD_VERSION`
5.4.17 → 5.4.19, manifest 6.2.14 → 6.3.2 — still mismatched) and D4-01's
version banner. Both findings survive.

**Discrepancies in my re-runs, stated up front:** `text_overlap_pairs` came out
1079 against the finder's 1039 (+3.8 %), and `hit_small_24` 4221 against 4224
(−3). Both deltas move *against* the direction that would help a refutation.
The finder ran with `--shots`; I did not, which changes screenshot timing on
the hover states. Everything else reproduced exactly.

## 1. My own harnesses and metric definitions

Three, all in `$SCR` and all written by me:

- **`consequence.mjs`** — mounts the card in the *Lovelace order* (`setConfig`
  → `hass` → append → `hass`), against N card sources × M tile widths, and
  reports:
  - `axis_font_css_px` — the font-size the **engine** resolved for the chart's
    first numeric axis label, `parseFloat(getComputedStyle(t).fontSize)`. The
    finder computed *attribute × width / 900*; I read what the engine used, so
    a CSS override or transform would show up here and not there.
  - `digit_box_px` — the client-rect **width × height of that rendered text
    node**: the physical size of the drawn glyphs, which is what an eye gets.
  - `lane_h_px` / `slot_min_px` — min client-rect height of `rect.lane`, min
    of `min(w,h)` over `rect.slot`, in the expanded dialog.
  - `small24` / `small44` — interactive targets in the expanded dialog whose
    smaller side is under 24 / 44 px.
  - `no_plan spill / offscreen / doc_hscroll` — px by which the empty state's
    text passes the `<ha-card>` border box, px by which it passes the
    **viewport**, and the horizontal scroll the document gains.
  - `wi_contrast` — WCAG 2.x ratio of the what-if buttons from my own sRGB
    relative-luminance function, compositing the button's own background.
  - `renders_during_resize` — `_render` calls (hooked on the prototype) while
    the tile narrows with no new plan.
- **`contrast_focus.mjs`** — per-class worst contrast and count below 4.5:1 for
  `.setup-slot.empty` / `tspan.setup-value` (dialog → Setup tab) and
  `.chip.off` (price series toggled off), light and dark, my own luminance code.
- **`overlap_probe.mjs`** — vertical/horizontal intersection in px between each
  value-axis **unit caption** (`°C`, `kW`, `W/m²`, `SEK/kWh`) and every other
  chart text, in the expanded dialog at 1280×800.
- **`lanes_inline.mjs`** — what the schedule editor's targets are in the
  **compact tile with no dialog open and stock config**: count, min side,
  `tabindex`, `aria-label`, and whether `Enter` opens the slot menu.

## 2. The tile width, and whether it is a real Home Assistant column

The finder models a phone tile as **359 px** = 375 − 16. That is what Home
Assistant's masonry view produces at one column (view padding 4 px each side +
`#columns` margin 4 px each side). I could not verify the frontend source on
this box — there is no HA frontend here — so instead of arguing I measured the
**sensitivity**, running my harness at 359 / 367 / 377 / 393 / 400 px (375 px
iPhone-SE viewport, 383 px, 393 px iPhone-14-Pro-class, 409 px, and the 400 px
desktop sections column):

| tile px | axis glyph box at first paint | dialog lane | min slot | `no_plan` spill past the card |
|---|---|---|---|---|
| 359 | 5.34 × 5.00 px | 5.60 px | 2.44 px | 47.95 px |
| 367 | 5.47 × 5.00 | 5.73 | 2.52 | 39.95 |
| 377 | 5.63 × 5.00 | 5.89 | 2.62 | 29.95 |
| 393 | 5.89 × 5.00 | 6.14 | 2.79 | 13.95 |
| 400 | 6.00 × 5.00 | 6.26 | 2.86 | 6.95 |

Nothing turns on the exact column. Over the whole plausible range the axis
label `-20` is drawn in a box 5.3–6.0 px wide — **three characters in six
pixels** — the editor lanes stay between 5.6 and 6.3 px, and the empty state
still spills. The one finding whose *magnitude* is width-sensitive is D4-04
(48 px at 359, 7 px at 400); its direction is not.

## 3. Reachability of the 26 states

Classified from `card_geometry.mjs`'s `STATES` and the card's `DEFAULTS`
(`what_if: true`, `show_stats: true`, entity ids derived from the default
device name, with attribute auto-discovery as a fallback):

- **Default, no config, no interaction** — `no_plan`, `plan_inline`,
  `plan_inline_sv` (Swedish HA), `shared_steps`, `reduced_motion` (an OS
  setting): these carry D4-01's 3.70 px chart and D4-02's inline lanes.
- **Default config, one tap** — `expanded_plan`, `no_plan_expanded`,
  `score_open`, `expanded_zoomed`, `draft_dirty_menu_open`, `whatif_edited`,
  `tooltip_hover`, `shared_steps_hover`: these carry D4-02's dialog lanes,
  D4-03's axis collisions and D4-05's what-if buttons. `what_if: true` is the
  **default**, so the schedule editor needs no configuration at all.
- **Default config, two taps** — `setup_single_buffer` / `setup_two_tank` /
  `setup_coil` (dialog → Setup tab): D4-06's "not configured" rows.
- **Needs card YAML** — `plan_short_window` (`hours`), `custom_title_currency`,
  `hidden_series` (`series:`), `what_if_off`.
- **Needs integration state** — `whatif_weekly` (a weekly DHW window),
  `override_active` (a manual override in force).
- **Needs a deliberate sequence** — `layout_editing_dragged` (layout editor
  toggled on), `picker_open_filtered` (entity picker opened), `editor_schema`
  (the visual card editor).
- **`coarse_pointer`** is not an exotic arm: it is the Home Assistant
  companion app, which is how most people read a dashboard.

No finding rests only on a state behind an unusual dashboard layout. The one
arm that is unusual is `panel` (a 1200 px single-card panel view), and it is
never the sole carrier of a finding.

---

## D4-01 — the chart's text at first paint

**Re-run** (`first_paint_font.mjs`, exact command from its header):
`font_px_lovelace=3.7`, `lane_px_lovelace=5.55`, `renders_lovelace=1`,
`font_px_resize=3.04`, `renders_resize=0`, `font_px_refresh=7.31`,
`font_px_attached=7.42`, `floor_px=8`. `thread_factor=1.00`, `load1=20.38`.
**Every number is the finder's, to the stated tolerance.**

**My number, my definition** — *the client-rect of the rendered axis label at
first paint, in the order `hui-card` uses*: the label `-20` occupies
**5.34 × 5.00 CSS px**, i.e. **1.78 px per character**. On a 359 px tile the
engine-resolved font attribute is 10 user units on a 333 px svg. Identical on
`origin/main` (`main_digit_box_h_px_first_paint=5`).

**Reachability, which is what decides the severity.** The state is the default
one: stock config, no interaction. The re-render that would apply the 8 px
floor is gated by `_signature()`, which is built only from the plan sensors'
`last_updated`/`state`, the config, the language, the currency and the headline
sensors. The `ResizeObserver` installed in `connectedCallback` calls
`this._cacheRect()` and nothing else — I measured
`renders_during_resize=0` on baseline **and** on main — even though
`_measuredCardWidth`'s own docstring says *"the ResizeObserver re-renders on
size change, so a rotated phone picks the boosted font up on the next frame."*
The code does not do what the comment says. So the wait is one coordinator
cycle: `DEFAULT_OPTIMIZATION_INTERVAL = 30` minutes (`const.py:1070`).
**Every fresh creation of the card — every dashboard open, every navigation,
every frontend reload — shows a 3.7 px chart for up to 30 minutes** unless the
user touches something that forces a render (a legend chip, tap-to-expand: the
`hidden_series` and `score_open` states in the geometry run show 7.42 px for
exactly this reason). That is the honest bound: not permanent, but recurring
and default.

**Perturbations, both of them, run by me.**
- P1 — `ResizeObserver` callback also calls `this.render()`: first-paint glyph
  box **5.34 × 5.00 → 10.73 × 9.00 px**, `renders` 1 → 2,
  `renders_during_resize` **0 → 1**. Up, as stated.
- P2 — `_measuredCardWidth` measures `.chartwrap svg` instead of the host:
  the floored font goes **20.0557 → 21.6216 units = 8.00 px exactly**. The
  finder's "7.42 → 8.00" is exact: the floor divides by the host width (359)
  while the svg it sizes is 333 px, so it lands at 8 × 333/359 = 7.42.

The expanded dialog's `FONT_EXPANDED = 15` has no floor at all: dialog svg
336 px → 15 × 336/900 = **5.60 px**, which is also `lane_h_px` in my run.

**Attacks.** Not a stub artefact — real Chromium, real layout. Not contention —
counts and pixels. Not a grid artefact — it is the same number on every inline
state of every tile arm (`chart=333x140.6@3.7px` throughout the geometry log).
Not fixed on main. The only softening fact is that a single user interaction
repairs it for that card instance, and I have said so.

**Vote: `verify` (high).** Decisive number: three characters rendered in
5.34 px on the default phone tile, with `renders_during_resize=0` on both
baseline and main.

## D4-02 — the schedule editor's targets

**Re-run**: `hit_small_24=4221` (`rect.slot` 1344, `rect.lane` 476),
`hit_small_24_nospacing=1880` (`rect.slot` 1344, `rect.lane` 367),
`hit_small_44_coarse=548`, `slot_handles_small=2880`. The per-element
breakdown from `summarise.py` on my own `results.json` matches the report's
numbers element for element.

**My number, my definition** — *min client-rect height of `rect.lane` and min
`min(w,h)` of `rect.slot`, in the states a stock install reaches*:

- expanded dialog, 359 px phone: **lane 5.60 px, smallest slot 2.44 px**,
  and 58 of the dialog's 74 interactive targets under 24 px.
- **compact tile, no dialog, stock config** (`lanes_inline.mjs`): **2 lanes at
  5.55 px and 6 slots at 2.70 px, every one of them `tabindex="0"`**, with
  `aria-label` "Hot water lane. Press Enter to add a slot." and "Hot water
  06:45 AM–07:00 AM. Press Enter for actions, Delete". 8 of the default inline
  card's focus stops are these sub-6-px rectangles.

**A correction that strengthens the finding.** The report says the inline lanes
are focusable "where … editing is not enabled". It is enabled: I focused the
first inline slot and dispatched `keydown Enter` — `menuAfterEnter=true`, the
slot menu opens in the compact tile. So the card's editing surface *is* live on
a default phone dashboard at 2.70 px wide.

**Perturbation.** `LANE_H` 15 → 40 units: `lane_h_px` **5.60 → 14.93 px**
(down, as stated) — but still under 24, so the finding's second proposal (a
px floor like the font's) is the one that reaches the bar. Identical on main.

**Attacks.** WCAG 2.2 SC 2.5.8 is the right bar and the spacing exception does
not rescue these: 1344 + 367 of the 1880 no-rescue failures are exactly slots
and lanes. There is a form-based fallback in the what-if panel (`Day from` /
`to` time inputs, `+ Add window`), so *schedules* can be edited without
dragging — but individual space-heating slots cannot, and on a touch device
there is no Tab to reach a slot at all. Not fixed on main.

**Vote: `verify` (high).** Decisive number: 2.70 px slots and 5.55 px lanes,
`tabindex=0`, editable by Enter, in the **default compact tile** with no
configuration and no interaction.

## D4-03 — axis labels collide at the plot corners

**Re-run**: `text_overlap_pairs=1079` (finder 1039). Families reproduce:
`'60'~'°C'` 270 (finder 260), `'400'~'W/m²'` 255 (245), `'6'~'kW'` 240 (232),
`'3'~'SEK/kWh'` 61 (53), `'06:00 AM'~'-20'` 50 (50). Worst intersection 8.4 px,
on the `panel` arm (the report attributes it to the desktop dialog).

**My number, my definition** — *intersection in px between a value-axis unit
caption and every other chart text, expanded dialog at 1280×800*
(`overlap_probe.mjs`): **3 overlapping pairs**, and the overlap is not a graze:

```
°C   over "60"    22.19 px wide × 8.37 px tall
kW   over "6"     11.09 px × 8.37 px
W/m² over "400"   33.28 px × 8.37 px
```

The caption covers the whole top tick number horizontally and its full glyph
height vertically. A reader of the expanded dialog cannot read the maximum of
the temperature, power or solar axis, and cannot read the unit either.
Identical on `origin/main` (3 pairs, same pixels).

**Perturbation, mine.** Lift the unit caption from 4 to 13 units above the plot
top (`const uy = plotT - 13 * (size / FONT_BASE)`): **3 → 0**. `to_zero`, as
stated.

**Attacks.** Reachable in one tap from the default card. Not theme-dependent —
both texts are drawn by the card's own SVG. Not a grid artefact (leave-one-out
in the report: min 38, max 82, total 1039 over 15 arms; my totals are 3.8 %
higher across the board). The severity is arguable in the other direction: on
the default phone tile the whole axis is 3.7 px anyway, so this is only legible
as a defect where D4-01 is not the dominant one — but that is exactly the
expanded dialog, which is one tap away.

**Vote: `verify` (medium).** Decisive number: the `°C` caption covers 22.19 px
of the 22-px-wide string `60` in the desktop dialog; my perturbation takes it
to zero.

## D4-04 — the empty state's entity ids overflow

**Re-run**: `text_overflow=792`, of which `code@scope x` 24 and
`div.empty@scope x` 24 across the arms — the report's 48.

**My number, my definition** — *px by which the empty state's text passes the
`<ha-card>` border box, and by which it passes the **viewport***, state
`no_plan`, tile 359 px in a 375 px viewport:

```
spill past the card    47.95 px
past the 375 px viewport 39.95 px
document horizontal scroll gained 40 px
worst line: ". Check the entity id in Developer Tools > States and set"
```

Confirmed visually in the finder's `shots/phone-light-en--no_plan.png`: the
string `sensor.heat_pump_optimizer_space_heating_plan.` runs out of both sides
of the card.

**Reachability — better than the report claims.** The card's own comment at the
`window.customCards` registration says: *"The preview renders from
getStubConfig; with no plan sensors in the dashboard picker's context it shows
the card's own diagnostic empty state."* So **the empty state is what the card
picker shows every user the first time they add the card**, in a narrow dialog
column; and `PlanSource.diagnose` also returns it whenever a plan sensor is
missing, `unknown`, `unavailable` or has no forecast — after a restart, during
a Tibber outage, and whenever the entity was renamed. The consequence is exact:
**the sentence that tells the user which entity id to fix is the sentence that
runs off the right edge of the phone screen.**

**Perturbation.** `.empty code { overflow-wrap: anywhere }` (plus the same on
`.empty`): spill **47.95 → 0**, offscreen **39.95 → 0**, document h-scroll
**40 → 0**. `to_zero`. Identical on main (`main_no_plan_spill_px=47.95`).

**Vote: `verify` (medium).** Decisive number: 39.95 px of the diagnostic
sentence lies outside a 375 px viewport, on the state the card picker shows
first.

## D4-05 — primary-colour text and buttons at 2.63:1

**Re-run**: `contrast_fail_light=891`; per element `button.wi-save` 150,
`button.wi-pin` 90, `button.wi-apply` 90, `button.wi-viewreset` 18,
`span.layout-verdict.match` 9, `text` 153 + `text.lane-more` 54 = 207. Every
count in the report, exactly.

**My number, my definition** — *WCAG ratio from my own sRGB luminance function,
compositing the element's opacity chain over its own painted background*:
`wi-pin` **2.63**, `wi-apply` **2.63**, `wi-save` text **2.63** and its fill
against the card **2.63**, all at `font-size: 12px`. Identical on main.
Visible without instruments in `shots/desktop-light-en--expanded_plan.png` and
`shots/phone-light-en--expanded_plan.png`.

**Perturbation, and a problem with the proposed fix.** I applied the report's
own proposal — `.wi-pin, .wi-apply { color: var(--primary-text-color) }` and
`.wi-save { background: var(--dark-primary-color, #0288d1) }`:

```
wi-pin   2.63 -> 16.10   pass
wi-apply 2.63 -> 16.10   pass
wi-save  2.63 ->  3.86   STILL FAILS AA (12 px needs 4.5:1)
```

Direction confirmed (down by far more than 200 across the arms), but **the
Save button's proposed colour does not reach AA**; `#0288d1` under white gives
3.86:1. The fixer needs a darker fill (roughly `#0277bd` or below) or larger
text.

**Attacks.** Not a token-model artefact: `--primary-color: #03a9f4` is Home
Assistant's stock default and the card names it directly. The buttons are also
bordered and labelled, so this is legibility, not discoverability. One tap from
the default card. Not fixed on main.

**Vote: `verify` (medium)**, with the note that the proposed `.wi-save` fix is
insufficient. Decisive number: 2.63:1 at 12 px for the three headline actions,
from my own luminance code.

## D4-06 — opacity-faded text below AA

**Re-run**: `contrast_fail` 1209, of which `tspan` 300 + `tspan.setup-value`
300 = **600**, and `button.chip.off` 45.

**My number, my definition** — *worst ratio and count below 4.5:1 per class, on
the Setup tab of the expanded dialog and on the inline card with the price
series toggled off* (`contrast_focus.mjs`, my luminance code):

| | light | dark |
|---|---|---|
| `.setup-slot.empty` ("… not configured") | **2.99:1**, 9 of 12 rows fail | **4.04:1**, 9 of 12 fail |
| `.chip.off` ("Electricity price") | **2.43:1** | **3.19:1** |

at `font-size: 12px` and `11.48px`. Identical on `origin/main`.

**Perturbations, both, mine.**
- `.setup-slot.empty { opacity: 1 }`: **2.99 → 4.81** light, **4.04 → 6.13**
  dark; failures **9 → 0**. `to_zero`, as stated.
- `.chip.off { opacity: 0.7 }`: **2.43 → 5.95** light, **3.19 → 6.99** dark;
  failures **1 → 0**.

**Attacks.** The `.chip.off` half is the weaker one: the user turned that series
off themselves, and `text-decoration: line-through` carries the state
redundantly, so no information depends on the contrast. The `.setup-slot.empty`
half is the opposite — those rows exist *only* to say which sensor is missing,
they are 600 of the 1209 failures, they are two taps from the default card,
and the fix is one CSS declaration.

**Vote: `verify` (medium).** Decisive number: 2.99:1 at 12 px for the setup
page's "not configured" rows, my own luminance code, `to_zero` under
`opacity: 1`.

## D4-07 — 548 coarse-pointer targets under 44 px

**Re-run**: `hit_small_44_coarse=548` exactly, `coarse_emulated=1`.

**My decomposition of that 548, from the coarse arm of my own `results.json`:**

```
548  targets under 44 px          <- the finding's number
342  of them under 24 px          <- the WCAG 2.2 AA bar
167  of those also fail the 24 px spacing exception (SC 2.5.8 genuinely failed)
130  of those 167 are rect.slot (96) + rect.lane (34)  -- i.e. D4-02 again
 37  independent residue: rect.setup-hit 12, zoom buttons vc-out/vc-in/vc-reset 24,
     input.sp-filter 1
```

**44 px is not an AA requirement.** WCAG 2.2 AA is SC 2.5.8 at 24 px; 44 px is
SC 2.5.5 (AAA) and the platform HIGs. Measured against the bar the project can
be held to, this finding's independent content is **37 targets**, of which the
substantive ones are the chart's zoom buttons at 17.3 px and 12 setup-diagram
hit areas at 11.7 px — and 411 of the 548 are chips, tabs and form controls
that pass AA because the spacing exception rescues them.

**Perturbation, mine.** The report's proposed
`@media (pointer: coarse) { … min-height: 44px }` rule, in a touch context on
the expanded dialog: targets under 44 px **74 → 44**, under 24 px **58 → 42**.
It moves, and by more than the claimed direction; but note what it cannot
touch — the 44 that remain are `rect.slot`, `rect.lane` and `rect.slot-handle`,
which is D4-02's geometry and needs a viewBox change, not a CSS rule.

**Confirmed:** exactly one coarse-pointer adaptation exists in the card
(`LANE_EDGE_GRAB_COARSE`, used at one call site); there is no
`@media (pointer: coarse)` CSS block at all, on baseline or on main.

**Vote: `weaken(low)`.** Decisive number: of the 548, only 167 fail the AA
24 px bar without a spacing rescue, and 130 of those 167 are already D4-02's
slots and lanes. The finding is real but its headline count is inflated by an
AAA threshold and by double-counting D4-02; what remains that D4-02 does not
already carry is 37 targets.

## D4-08 — three of seven series colours below 3:1 on light

**Re-run** (`series_contrast.mjs`): `series_below_3_light=3`
(price `#f5a623` 2.03, solar `#f2c94c` 1.59, house temp `#2fae7a` 2.82),
`series_below_3_dark=0`. Exactly the report.

**On main**: `SERIES_DEFS` colours are byte-identical
(`git show origin/main:…` lines 865/875/885/895/905/944/966). Not fixed.

**Perturbation, mine**: solar `#f2c94c → #b8860b` gives 3.25:1 and
`series_below_3_light` **3 → 2**. Down by 1, as stated.

**Attacks.** WCAG 1.4.11 applies to graphical objects *needed to understand the
content*. Each series also carries a labelled legend chip and occupies a
distinct axis and vertical band, so colour is not the sole identifier — which
is why this is hygiene and not a bug. It is nonetheless a real number and a
one-line fix.

**Vote: `verify` (low).** Decisive number: solar `#f2c94c` at 1.59:1 on
`#ffffff`, unchanged on main.

## D4-09 — form length and grouping

**Re-run** (`config_flow_ux.py`, exact command): `initial_screens=7`,
`initial_fields=46`, `initial_required=13`, `initial_must_know=2`,
`user_page_fields=17`, `user_page_pickers=13`, `options_pages=13`,
`options_fields=158`, `options_max_fields=23 (hot_water)`,
`pages_over_15=5 ['entities','hot_water','thermal_model','grid','learning']`,
`off_theme_fields=1 ['hot_water.space_circulation_pump_entity']`. Every number
exact, and **exactly the same on `origin/main`**.

**My own check of the off-theme field.** `translations/en.json` labels it
"Heating circulation pump switch (optional)" and its help text is entirely
about space heating ("the pump is paused only in slots that are provably idle
and warm…"). It is the last field on the Hot water page, immediately after
`vvc_pump_entity` / `vvc_lead_minutes` — filed by the word "circulation pump"
rather than by what it controls. A user configuring heating will not look for
it under Hot water.

**Perturbation**: dropping `space_circulation_pump_entity` from
`async_step_hot_water` takes `off_theme_fields` **1 → 0** and
`options_max_fields` 23 → 22.

**Attacks on severity.** The first screen's 17 fields are only 3 required and
13 optional entity pickers a user may skip entirely; `initial_must_know=2`
(a Tibber token and a weather entity) is a genuinely short list, and the
non-findings show `help_missing=0` over 172 fields, `defaults_out_of_range=0`
and `untouched_submit_fail=0`. So the flow is long but not obstructive. One
misfiled optional picker is a hygiene item, which is what the finding claims.

**Vote: `verify` (low).** Decisive number: `off_theme_fields=1`, identical on
main; `initial_must_know=2` is what keeps it at low.

## D4-10 — a default install logs a WARNING about its own defaults

The seat was asked specifically to check the "default install" claim. **It is
true, and it is once per install, not once per cycle.**

**Re-run**: `default_submit_warnings=1`, message *"Hot water: the
anti-legionella cycle at 60 °C is above the 55 °C charge limit, so the tank is
taken above that limit every 7 days"*. Identical on `origin/main`.

**Reachability, checked rather than assumed.** The `dhw` step is on the
**recommended install path** — the harness's screen list is
`user → temperature → building(menu) → building_describe → building_extras →
dhw → weather_sensitivity → create_entry`. `DEFAULT_DHW_SETPOINT = 55.0`
(`const.py:873`) and `DEFAULT_DHW_LEGIONELLA_TEMP = 60.0` (`const.py:1026`),
and `_dhw_legionella_warning` returns non-`None` for any pair with
`legionella > setpoint`, with no exemption. So **every user who clicks through
with the defaults writes one WARNING to `home-assistant.log`**, visible in
Settings → System → Logs.

**How often.** Not per cycle. It fires at `config_flow.py:1283`
(`async_step_dhw`) and, on main, also at line 1902 (the hot_water options
page). The periodic path is the coordinator's, and the coordinator
*deliberately exempts* this exact pair (`coordinator.py:3857`, `stock = …`)
from the `dhw_legionella_above_setpoint` repair notice. So: **once per install,
plus once per hot-water save; never on the update cycle, and never in the UI.**
The consequence is a single confusing log line contradicting the coordinator's
own considered decision — small, and I will not inflate it.

**Perturbation, mine.** Adding the coordinator's `stock` exemption to
`_dhw_legionella_warning` gives `default_submit_warnings` **1 → 0**. `to_zero`.

**Vote: `verify` (low).** Decisive number: `default_submit_warnings=1` on the
untouched recommended path, on baseline and on main; the fix is the exemption
the coordinator already has.

## D4-11 — the card announces 5.4.17 in a 6.2.14 release

**Re-run** (`card_version.mjs`): `card_version_matches=0`,
`version_delta=1.-2.-3`, banner ` heatpump-optimizer-card  v5.4.17 `.
**On main**: `CARD_VERSION = "5.4.19"` against `VERSION`/manifest `6.3.2` —
still mismatched, and `tools/release/stamp.py` still does not touch the
constant (it writes `VERSION`, the manifest, the notes and the two claim files
only). Not fixed.

**Perturbation, mine**: setting `CARD_VERSION` to `"6.2.14"` gives
`card_version_matches=1`, `version_delta=0.0.0`. Up, as stated.

**Attack on the finding's second half, with numbers — it is overstated.** The
report says the duplicate-copy guard is defeated because *"two copies from any
two 6.x releases carry the same 5.4.17 and stay silent."* I mapped every
release's `VERSION` to its `CARD_VERSION`:

```
6.2.13 -> 5.4.12    6.2.16 -> 5.4.19
6.2.14 -> 5.4.14    6.2.17 -> 5.4.19
6.2.15 -> 5.4.19    6.3.0/6.3.1/6.3.2 -> 5.4.19
```

Six releases do share 5.4.19 — **because the card file is byte-identical across
them**. `CARD_VERSION` is an independent, monotonically bumped *card-file*
version: 18 of the last 22 commits that touched the card bumped it. So
`previous.cardVersion !== CARD_VERSION` fires almost exactly when the two
copies actually differ, and stays silent when a duplicate is harmless. The
guard is not defeated the way the finding says.

What *does* survive: the banner a user quotes in a bug report names a card
revision, not the release they installed; and 4 recent commits changed the card
without bumping the constant ("The card reads at phone width…", "The
optimization score explains…", "Explain a mode-paused channel…", "Extract the
card's two clean seams…"), which are genuine silent-duplicate windows.

**Vote: `verify` (low)**, with the guard rationale corrected. Decisive number:
`card_version_matches=0` on both baseline and main (5.4.19 vs 6.3.2); the
duplicate-guard argument is refuted by the release→card-version map above.

## D4-12 — "the same than the saved plan"

**Re-run** (`delta_wording.mjs`): `ungrammatical_en=1`, `ungrammatical_sv=0`.
The composed English string is *"the same than the saved plan (31.97 → 31.97
SEK, estimated)"*; Swedish composes correctly via "jämfört med".

**On main**: `stats.the_same` and `stats.delta_detail` are unchanged
(lines 229–231 of the main card). Not fixed.

**My own check**: visible in the finder's
`shots/desktop-light-en--expanded_plan.png`, in the TODAY'S SLOTS row, without
any instrument — "the same than the saved plan".

**Perturbation, mine**: `"{verdict} compared with the saved plan …"` gives
`ungrammatical_en=0`. `to_zero`.

**Consequence, stated plainly and not inflated:** one ungrammatical English
sentence, shown only for a cost-neutral edit, in a panel the user has already
opened and is already reading. Nothing is unreadable and nothing is blocked. It
is a one-string fix and it belongs at `low`.

**Vote: `verify` (low).** Decisive number: 1 of 3 English verdicts composes
ungrammatically, 0 of 3 in Swedish, unchanged on main.

---

## Summary

| id | vote | the number that decides it |
|---|---|---|
| D4-01 | verify (high) | axis label `-20` drawn in a 5.34 × 5.00 px box at first paint; `renders_during_resize=0` on baseline **and** main; up to 30 min per card creation |
| D4-02 | verify (high) | 2.70 px slots / 5.55 px lanes, `tabindex=0`, `Enter` opens the menu, in the **default compact tile** |
| D4-03 | verify (medium) | the `°C` caption covers 22.19 px of the 22-px string `60`; my probe 3 → 0 under the fix |
| D4-04 | verify (medium) | 39.95 px of the diagnostic sentence off a 375 px viewport, 40 px h-scroll; `to_zero` |
| D4-05 | verify (medium) | 2.63:1 at 12 px for the three headline actions; the proposed `.wi-save` fix only reaches 3.86:1 |
| D4-06 | verify (medium) | `.setup-slot.empty` 2.99:1 light / 4.04:1 dark, 600 of 1209 failures, `to_zero` at `opacity: 1` |
| D4-07 | **weaken(low)** | of 548 under 44 px, only 167 fail the AA 24 px bar without spacing rescue, and 130 of those are D4-02's slots and lanes |
| D4-08 | verify (low) | solar `#f2c94c` 1.59:1 on white, unchanged on main |
| D4-09 | verify (low) | `off_theme_fields=1`, every config-flow count identical on main, `initial_must_know=2` |
| D4-10 | verify (low) | `default_submit_warnings=1` on the untouched recommended path — once per install, never per cycle |
| D4-11 | verify (low) | `card_version_matches=0` (5.4.19 vs 6.3.2); the duplicate-guard half is overstated |
| D4-12 | verify (low) | 1 of 3 English verdicts ungrammatical, 0 of 3 Swedish |

Nothing voided: every perturbation I ran moved its number in the stated
direction, so no harness here is measuring a constant.

**The panel-level fact**: `origin/main` reproduces all 19 geometry RESULTs and
all 27 config-flow RESULTs identically. The post-baseline card work (#163,
#164) fixed **none** of the twelve.

## Files

- `$SCR/consequence.mjs`, `$SCR/contrast_focus.mjs`, `$SCR/overlap_probe.mjs`,
  `$SCR/lanes_inline.mjs` — my harnesses.
- `$SCR/pert/p1…p9` — perturbed card sources; `$SCR/base-tree`,
  `$SCR/main-tree` — `git archive` extractions used for the Python
  perturbation and the main-tree re-runs.
- `$SCR/card_geometry.rerun.out`, `$SCR/card_geometry.main.out`,
  `$SCR/consequence.out` — the runs.
- `$SCR = /private/tmp/claude-501/audit-scratch/D4-2`.
