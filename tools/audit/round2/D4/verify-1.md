# D4 — verifier seat 1 (stance: OWN-HARNESS)

Worktree `v-D4-1` at the baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`
(VERSION 6.2.14). Apple M1, macOS Darwin 25.6.0, Node 20.10.0, Playwright
1.49.0 / Chromium 1148 from `~/.cache/pw-browsers`. Every number below is a
count or a rendered pixel size produced by Chromium's layout/raster engine, so
none of it depends on load; `load1` during my runs ran 6–59 and the finder's
re-run still reproduced to the unit (the two places it did not are traced
below, and neither is a contention effect).

Nothing was written into the worktree. The finder's harnesses were run from a
symlink farm at `$SCR/repo` whose `tools/audit/round2/D4/` holds copies of them,
so `path.resolve(here,"../../../..")` still lands on the baseline tree. My own
harnesses are in `$SCR/mine/`:

| file | what it measures |
|---|---|
| `own_geom.mjs` | axis font through the live screen CTM; lane/slot client rects; coarse-pointer targets with my own interactivity test |
| `own_contrast.mjs` | WCAG contrast read out of **rendered PNG pixels** (element screenshots at `deviceScaleFactor: 4`, decoded on a canvas) |
| `own_ink.mjs` | whether two axis labels' **ink** collides (isolated-glyph raster bounding boxes), and how far the empty state's ink leaves the card |
| `own_rotate.mjs` | the axis font after a resize from the floored state |

`$SCR` = `/private/tmp/claude-501/audit-scratch/D4-1`.

## 0. Re-run of the finder's `card_geometry.mjs` (all twelve rest on it)

```
HPO_PLANDATA=$SCR/plandata.json NODE_PATH=$PW/node_modules \
PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
node tools/audit/round2/D4/card_geometry.mjs
```

| RESULT | finder | my re-run (baseline) | my run on `origin/main` |
|---|---|---|---|
| `renders` | 390 | 390 | 390 |
| `coarse_emulated` | 1 | 1 | 1 |
| `text_overlap_pairs` | 1039 | **1079** | **1079** |
| `text_overflow` | 792 | 792 | 792 |
| `contrast_fail` | 1209 | 1209 | 1209 |
| `contrast_fail_light` / `_dark` | 891 / 318 | 891 / 318 | 891 / 318 |
| `contrast_fail_inactive` | 105 | 105 | 105 |
| `hit_small_24` | 4224 | 4221 | 4224 |
| `hit_small_24_nospacing` | 1883 | 1880 | 1883 |
| `hit_small_44_coarse` | 548 | 548 | 548 |
| `tab_unreached` / `focus_no_indicator` | 330 / 0 | 330 / 0 | 330 / 0 |
| `console_errors` / `hover_shift` | 0 / 0 | 0 / 0 | 0 / 0 |
| `min_text_px` | 2.96 | 2.96 | 2.96 |

`thread_factor` 1.00, `swapins` 0 in all three; `load1` 3.24 (finder), 58.83
(mine), 9.92 (main). The by-element breakdowns are **byte-identical** in all
three runs (`rect.slot=1344; button.chip=952; rect.lane=476; …` and
`tspan=300; tspan.setup-value=300; text=153; button.wi-save=150; …`).

**The one mismatch outside tolerance, traced.** `text_overlap_pairs` 1039 →
1079. I diffed the 390 per-state rows: exactly ten cells differ, each by +4,
and all ten are inline (non-dialog) phone states on the two arms
`phone-light-en` and `phone-dark-sv` — which are precisely the two arms the
finder's `--shots` run screenshots. The same states on `phone-light-sv` and
`phone-dark-en` show ov=4 in *both* runs, with identical chart geometry
(`{w:333, fontUnits:10, fontPx:3.7, laneH:5.5}`). So the finder's own
screenshot pass suppressed 40 overlaps in its headline number: **1039 is an
undercount of 1079, not an inflation.** The finder's harness header claims
"exact for counts"; it is not exact under `--shots`.

The `hit_small_24` −3 is a 0.07 % flake in my baseline run (main and the
finder both give 4224 from an identical tree for these elements); it changes
nothing.

## 1. Does the code still look the same on `origin/main`?

`origin/main` = `dd506890de58e085b10eb5bca6988f7f79cd45d1`, VERSION 6.3.2. The
card diff against the baseline is 95 changed lines, all of it issues #138/#141:
`host.geom` → `host.geomAt(index)` / `_geoms[]` so each chart copy hit-tests
and redraws its lanes in its own geometry, and a per-render pattern-id
sequence. Plus `CARD_VERSION` 5.4.17 → 5.4.19.

**Not one line of the code any of the twelve findings rests on changed.**
Verified byte-for-byte at the same line numbers: `FONT_BASE` 10, `FONT_EXPANDED`
15, `MIN_AXIS_FONT_PX` 8, `MAX_COMPACT_FONT` 28, `compactFontUnits`,
`_measuredCardWidth` (still the host, not the chart), the `ResizeObserver`
callback (still `this._cacheRect()` only, under a `_measuredCardWidth` doc
comment that still claims "the ResizeObserver re-renders on size change" — it
does not), `LANE_H` 15, `LANE_GAP` 3, `LANE_EDGE_GRAB_COARSE` 16,
`.setup-slot.empty { opacity: 0.75 }`, `.chip.off { opacity: 0.4 }`,
`.whatif .wi-pin/.wi-apply/.wi-save/.wi-viewreset`, `.layout-verdict.match`,
`.empty` (still no `overflow-wrap`), `SERIES_DEFS`, `stats.delta_detail`.
`config_flow.py` did change (182 lines) but `config_flow_ux.py` returns the
**same 26 RESULT lines** on main as on the baseline.

Executed proof rather than inspection: `card_geometry.mjs` on a `git archive
origin/main` tree gives the table above; `first_paint_font.mjs`,
`series_contrast.mjs`, `card_version.mjs`, `delta_wording.mjs` and
`config_flow_ux.py` on main all reproduce the baseline numbers exactly
(`card_version` now reads 5.4.19 vs 6.3.2 — still `card_version_matches=0`).

**No finding is fixed by the refactor.**

---

## D4-01 — chart text 3.7 px at first paint — VERIFY (high)

**Re-run.** `first_paint_font.mjs`: `font_px_lovelace=3.7`,
`lane_px_lovelace=5.55`, `renders_lovelace=1`, `font_px_resize=3.04`,
`renders_resize=0`, `font_px_refresh=7.31`, `font_px_attached=7.42`,
`floor_px=8`. Identical on main.

**My metric (different from the finder's).** The finder multiplies the
`font-size` attribute by `svg width / 900`. I read the scale the rasteriser
actually applies: `text.getScreenCTM().a`, times the attribute — plus, as a
second independent reading, the rendered `getBoundingClientRect().height` of
one axis text node, and the same figure in **device** pixels at
`deviceScaleFactor: 3` (a real phone).

| sequence (359 px tile, 375×812) | units | CTM `a` | **CSS px** | glyph box | device px @DPR3 | renders |
|---|---|---|---|---|---|---|
| Lovelace (setConfig→hass→append→hass) | 10 | 0.3700 | **3.70** | 5.00 | 11.10 | 1 |
| then narrowed to 300 px | 10 | 0.3044 | **3.04** | 3.18 | 9.13 | **0** |
| then a plan refresh | 20.056 | 0.3700 | 7.42 | 9.00 | 22.26 | 1 |
| attached (append→setConfig→hass) | 20.056 | 0.3700 | **7.42** | 9.00 | 22.26 | 1 |
| expanded dialog on the phone | 15 | 0.3733 | **5.60** | 6.00 | 16.80 | — |

Smallest chart text on the phone tile: **2.96 CSS px** (the 0.8× lane label);
in the phone dialog **4.48 px**.

**What a person actually sees.** 3.70 CSS px on a 375-CSS-px viewport spanning
a ~2.6 in phone screen is ~144 CSS px/inch, so the em box is 0.65 mm and a
digit's cap height ~0.47 mm — roughly a fifth of newspaper body type. At DPR 3
the digit stems are one device pixel wide. The finder's own
`shots/phone-light-en--plan_inline.png`, upscaled 4×, shows the time axis as a
row of grey smears and the value axes as single-pixel smudges: I cropped and
looked at it. This is not "small", it is not text.

**Attacks.**
- *The mount order is a model of `hui-card` I cannot check offline.* It does
  not matter. My `own_rotate.mjs` mounts in the **attached** (best-case) order
  so the floor applies, then resizes: 359 px → 7.42, 812 → 17.52, back to
  359 → 7.42, 300 → **6.11**, 250 → **4.99**, with no re-render at any step.
  The declared 8 px floor is never reached in any order, and any narrowing
  (rotation, sidebar, masonry reflow) walks further below it until the next
  plan refresh.
- *Is the floor arithmetic just a constant?* No: it hooks `_measuredCardWidth`.
  `compactFontUnits` gets 359 (the host) while the svg it sizes is 333 px
  (ha-card's 1 px border + padding), so 8 × 900/359 × 333/900 = 7.42.
- *Is `MAX_COMPACT_FONT` doing the damage?* No, 20.06 < 28.

**Perturbations, both run.**
- ResizeObserver callback also calls `this.render()`:
  `axis_font_css_px_lovelace_phone` 3.70 → **7.42** (up), `renders_on_resize`
  0 → **1** (up), resize-to-300 3.04 → 7.31.
- `_measuredCardWidth` measures `.chartwrap` instead of the host:
  `axis_font_css_px_after_refresh` 7.42 → **8.00** exactly (up) — the finder's
  diagnosis of the 7.42 is right to the second decimal. The Lovelace first
  paint stays 3.70 (no chartwrap exists yet), so both edits are needed.
- Dialog unchanged at 5.60 under both, confirming "the expanded dialog has no
  floor at all".

**On main.** Byte-identical code, identical numbers.

**Vote: verify, high.** Decisive number: **3.70 CSS px / 11.1 device px on a
phone tile, 0 re-renders on resize, and 7.42 px — never 8.00 — when the floor
does apply.** The chart is the card's entire content on the device most
dashboards are read on.

---

## D4-02 — schedule-editor slots 1.3–22 px wide, lanes 5.6 px tall — VERIFY (high)

**Re-run.** `hit_small_44_coarse=548`, `hit_small_24_nospacing=1880` (finder
1883), by-element `rect.slot=1344; rect.lane=476` identical. Smallest per
element across all 390 renders, identical in finder / mine / main:
`rect.slot` **1.3 × 5.5 px** (`phone-light-en`, `custom_title_currency`, the
48-hour window), `rect.lane` 259 × **5.5 px**.

**My metric.** `min(width,height)` of every `rect.lane` / `rect.slot`
`getBoundingClientRect()`, taken directly in the scope (dialog when open,
`ha-card` otherwise), on a phone viewport.

| scene | lanes | lane height | slots | slot width min → max | under 24 px | under 44 px |
|---|---|---|---|---|---|---|
| phone inline tile (359) | 2 | **5.55** | 6 | 2.70 → 21.58 | 8/8 | 8/8 |
| phone expanded dialog | 2 | **5.60** | 6 | **2.72 → 21.78** | 8/8 | 8/8 |
| dialog at tile 372 / 400 / 1200 | 2 | 5.60 | 6 | 2.72 → 21.78 | 8/8 | 8/8 |

The dialog is `96vw`, so its lanes are 5.60 px on a 375 px viewport whatever
the tile behind it is. I reproduce the finder's "a 15-minute DHW slot is 2.7 px
in the dialog" to 0.02 px. I did not hit 1.3 px in the states I drove myself;
the finder's `results.json` locates it in `custom_title_currency` (`hours: 48`)
and my re-run and the main run both find the identical 1.3 × 5.5 rect there.

**A correction the finder should carry.** The inline lane is 5.55 px only
while the D4-01 first paint is in force. Once the font floor applies, the lane
scales with it (`marginScale = font/FONT_EXPANDED`) and becomes 7.42 px
(`first_paint_font.mjs`, `attached order → laneH 7.42`). The dialog lane is
5.60 px unconditionally. Either way, four to eight times below the 24 px AA
minimum.

**Attacks.**
- *Are these real controls or drawing?* They are controls. Every `rect.lane`
  carries `tabindex="0" role="button" aria-label=…` and every unlocked
  `rect.slot` the same (`laneGroupInner`, lines 5753 and 5821). They are
  keyboard stops with "press Enter" affordances, not decoration.
- *Does the coarse-pointer adaptation rescue it?* `LANE_EDGE_GRAB_COARSE = 16`
  viewBox units = **6.0 px** on the phone. It widens the resize grab only; the
  lane's 5.6 px height and the slot's 2.7 px width are unchanged.
- *Is the spacing exception (2.5.8) available?* No — 1711 of the small targets
  fail it, and the lanes are stacked 3 units apart.
- *Is the size essential (WCAG's exception for content-determined size)?* The
  lane height is a free constant, `LANE_H`. The slot width is time-determined
  and therefore arguably essential — which is exactly why the height matters.

**Perturbation.** `LANE_H` 15 → 40: `lane_height_phone_dialog_px` 5.60 →
**14.93** (up, as claimed). Slot widths unchanged (time-driven), so the
finding's own "a px floor on the lane height" is the fix that actually moves
`rect.lane` out of the count.

**On main.** `laneGroupInner`, `LANE_H`, `LANE_GAP` byte-identical; the #138
per-copy geometry refactor changes which geometry each copy draws with, not the
sizes: main's `card_geometry` run gives the same `rect.lane=476`,
`rect.slot=1344`, same 1.3 × 5.5 minimum.

**Vote: verify, high.** Decisive number: **lane 5.60 px tall and slots
2.72–21.78 px wide in the phone dialog, every one a `role="button"` target,
against a 44 px touch minimum and a 24 px AA minimum.**

---

## D4-03 — axis labels collide at the plot corners — WEAKEN (low)

**Re-run.** `text_overlap_pairs` 1039 → **1079** (see §0: the finder's own
`--shots` pass suppressed 40). Pair families in my `results.json` match the
report: `'60'~'°C'`, `'400'~'W/m²'`, `'6'~'kW'`, `'3'~'SEK/kWh'`, and the
`'06:00 AM'~'-20'` family.

**My metric, and it is the one that decides this.** The finder intersects
*layout* boxes. I intersected **ink**: I isolate one glyph run at a time
(`visibility:hidden` on every other text and on every rect/path/line in the
svg), screenshot at `deviceScaleFactor: 4`, take the tightest box around device
pixels differing from the region's modal background by >8/255, and intersect
those two boxes.

| scene | pair | layout overlap (w × h) | **ink overlap (w × h)** |
|---|---|---|---|
| phone tile | `'60'~'°C'` | 4.11 × 2.29 | 3.75 × **0.25** |
| phone tile | `'6'~'kW'` | 2.06 × 2.29 | 2.00 × **0.00** |
| phone tile | `'3'~'SEK/kWh'` | 2.06 × 2.29 | 2.00 × **0.25** |
| phone tile | `'400'~'W/m²'` | 6.17 × 2.29 | 6.25 × **0.00** |
| desktop dialog | `'60'~'°C'` | 22.19 × 8.37 | 21.00 × **0.00** |
| desktop dialog | `'6'~'kW'` | 11.09 × 8.37 | 9.75 × **−0.50** |
| desktop dialog | `'400'~'W/m²'` | 33.28 × 8.37 | 32.00 × **−0.50** |
| desktop dialog | `'06:00 AM'~'-20'` | 28.83 × 4.38 | 27.50 × **−3.50** |
| desktop dialog | `'06:00 AM'~'0'` | 11.09 × 4.38 | 10.00 × **−3.50** |

`RESULT axis_pairs_layout_overlap=9`, `RESULT axis_pairs_ink_overlap=2` — and
those two overlap by 0.25 px, one device pixel at DPR 4.

**The glyphs do not collide.** The unit label is stacked directly on the top
tick with zero separation, and the time-label family the report cites
(`'06:00 AM'~'-20'`, 141 of the 1039 pairs) has a **3.5 px clear gap**: those
are SVG text bounding-box artefacts, not anything a reader sees. I confirmed
by eye on `shots/tablet-light-en--expanded_plan.png`: "°C" sits immediately
above "60", touching, legible.

**What is real.** The unit label overruns the svg's top edge by 1.3 px on
every render (744 of the 792 `text_overflow`), and at the leftmost axis the
unit label and its top tick are clipped by the svg's left edge — in the tablet
screenshot the "kW" and "6" of the outermost axis are cut in half, so a reader
cannot tell what unit that axis carries. That is a defect, and it is worth
fixing; it is not 1039 collisions.

**Perturbation.** `uy = plotT - 4*(size/FONT_BASE)` → `- 10*(…)`:
layout-overlapping pairs 9 → **2**, ink-overlapping pairs 2 → **0**. The
number moves, so the harness is not measuring a constant.

**On main.** `valueAxis`, `timeAxis`, `MARGIN` byte-identical;
`text_overlap_pairs=1079` on main too.

**Vote: weaken(low).** Decisive number: **the ink overlap of the pairs the
finding names is 0.00–0.25 px, and −3.50 px (a visible gap) for the
time-label family.** Real defect (crowding and a clipped unit label), wrong
name and one severity too high.

---

## D4-04 — the empty state's entity ids overflow the card — VERIFY (medium)

**Re-run.** `card_geometry.mjs` state `no_plan`: the `overflow` rows
`code@scope x` / `div.empty@scope x` reproduce; `text_overflow=792` identical
on baseline and main.

**My metric.** The distance the `<code>`'s **ink** (raster, DPR 4) lies to the
right of `<ha-card>`'s painted right edge, in CSS px, alongside the layout
figure.

| tile | card width | layout spill right | **ink spill right** |
|---|---|---|---|
| 359 (phone) | 359 | 44.06 | **47.00** |
| 372 (tablet column) | 372 | 31.06 | **34.00** |
| 400 (sections column) | 400 | 3.06 | **6.00** |
| 1200 (panel) | 1200 | −522.53 | fits |

44.06 px reproduces the finder's 44.1 to 0.04 px, and the ink confirms that
pixels really are painted 47 px outside the card box — nothing clips them,
because `.empty` has no `overflow-wrap` and no clipping ancestor. On a real
masonry dashboard that text either lands on the neighbouring card or is cut by
the column.

**Attacks.** *Is `no_plan` reachable?* It is the state of every fresh install
until the first plan is published, and the sentence it spills is the one that
tells the user which entity id to look for — the one thing they need to read.
*Is it a modelling artefact of my 359 px tile?* No: it still spills 6 px of ink
at 400 px, the widest single-column tile HA's sections view gives.

**Perturbation.** `.empty code { overflow-wrap: anywhere; }`: ink spill
47.00 → **0.00** at 359, 372 and 400 (to_zero, as claimed).

**On main.** `.empty` CSS and `_noPlanHtml` byte-identical; no `overflow-wrap`
anywhere in the file.

**Vote: verify, medium.** Decisive number: **47.0 px of ink painted outside
the card box on a 359 px tile, in the first state every install shows.**

---

## D4-05 — primary-colour text and buttons at 2.63:1 — VERIFY (medium)

Threshold: **WCAG 2.1 SC 1.4.3 Contrast (Minimum), level AA, 4.5:1** for text
below 18.66 px bold / 24 px. Every element here is 12 px.

**Re-run.** `contrast_fail_light=891`, by element `button.wi-save=150;
button.wi-pin=90; button.wi-apply=90; button.wi-viewreset=18;
span.layout-verdict.match=9` — identical on baseline and main.

**My metric.** Contrast computed from **rendered pixels only**: an element
screenshot at `deviceScaleFactor: 4`, decoded on a canvas; background = the
modal pixel colour of the element's own raster; foreground = the pixel whose
relative luminance is furthest from it. No declared colour, no opacity chain —
the compositor has already done the blending.

| element | light | dark | need | verdict |
|---|---|---|---|---|
| `button.wi-pin` "Apply this plan" | **2.63** (bg 255,255,255 / fg 3,169,244) | 6.48 | 4.5 | fails light |
| `button.wi-apply` "Simulate these slots" | **2.63** | 6.48 | 4.5 | fails light |
| `button.wi-save` "Save as my schedule" | **2.63** (bg 3,169,244 / fg 255,255,255) | **2.63** | 4.5 | fails **both** |

**The attack that could have killed this, and did not.** The whole finding
rests on `--primary-color: #03a9f4` being Home Assistant's default, which the
finder had to model because there is no HA frontend on this box. So I removed
the theme entirely and rendered against the **card's own authored fallbacks**
(`var(--primary-color, #03a9f4)`): `.wi-pin` 2.63, `.wi-apply` 2.63,
`.wi-save` 2.63, `.wi-viewreset` 3.54. The finding does not depend on the
theme model at all — the card's own declared colours fail AA.

**One correction to the finding.** My isolated-pixel read of `.wi-viewreset`
under HA tokens comes out 4.81 (light) / 6.48 (dark), not 2.63 — but that is my
method's fault, not the finder's: the button is inline inside a
`--secondary-text-color` sentence and my extremum picks the neighbouring grey.
Its computed colour is `rgb(3,169,244)`, so 2.63 stands for the button's own
glyphs; the 18 failures the finder counts are right.

**Perturbation.** `.wi-pin/.wi-apply/.wi-viewreset { color:
var(--primary-text-color) }` and `.wi-save { background:
var(--dark-primary-color,#01579b) }`: 2.63 → **16.10** for the three text
buttons and 2.63 → **7.40** for Save in both themes; my scene fail count
21 → 16. Moves as claimed.

**On main.** All five CSS rules byte-identical; `contrast_fail_light=891`.

**Vote: verify, medium.** Decisive number: **2.63:1 against a 4.5:1 AA
threshold for the card's three main actions, measured from pixels, and
unchanged when every Home Assistant theme token is removed.**

---

## D4-06 — opacity-faded text below AA — VERIFY (medium)

Threshold: **SC 1.4.3, AA, 4.5:1** (12 px / 11.5 px text, not large).

**Re-run.** `tspan=300; tspan.setup-value=300; button.chip.off=45` in the
by-element breakdown, `contrast_fail_inactive=105` counted apart — identical on
baseline and main.

**My metric.** Same rendered-pixel method as D4-05, which composites the
`opacity` for me rather than multiplying it into a declared colour.

| element | light | dark | need |
|---|---|---|---|
| `text.setup-slot.empty` "… not configured" | **3.00** (fg 149,149,149 on 255) | **4.03** (fg 123 on 28) | 4.5 |
| `tspan.setup-value` "not configured" | **3.00** | **4.03** | 4.5 |
| `button.chip.off` "Electricity price" | **2.43** (fg 166 on 255) | **3.20** (fg 107 on 28) | 4.5 |
| `tspan.setup-value` "47.5 °C" (configured) | 16.10 | 13.03 | passes |

Finder: 2.99 / 4.04 / 2.43 / 3.19. I match to ±0.01 by a completely different
route — pixels rather than the opacity chain.

**Theme-independence check.** With no HA tokens at all, on the card's own
fallbacks (`var(--secondary-text-color, #888)` × 0.75): `.setup-slot.empty`
**2.43**, `.chip.off` **2.43**. Worse, not better.

**Attacks.** *Is `.chip.off` an inactive control that AA exempts?* No — a
switched-off legend chip is still operable (clicking it turns the series back
on), and its label is what tells you which series you are turning on. The
finder already exempted `.nodata`/`[disabled]`/`.locked` separately (105
boxes). *Is `.setup-slot.empty` decorative?* It is the row that names the
sensor the user has not configured — the setup page's entire purpose.

**Perturbation.** `.setup-slot.empty { opacity: 1 }` and `.chip.off { opacity:
0.7 }`: setup rows 3.00 → **4.81** light / 4.03 → **6.13** dark (both now
pass), chips 2.43 → **6.01** / 3.20 → **7.00**; my scene fail count 21 → 9.

**On main.** Both CSS rules byte-identical at lines 2560 and 2804.

**Vote: verify, medium.** Decisive number: **3.00:1 (light) and 4.03:1 (dark)
for the rows that say what is missing, against 4.5:1 AA — and 2.43:1 on the
card's own fallback palette.**

---

## D4-07 — 548 targets under 44 px with a coarse pointer — VERIFY (medium)

**Re-run.** `hit_small_44_coarse=548`, `coarse_emulated=1` on baseline and
main.

**My metric, and my own count.** The finder's `TARGETS` selector is a hand-list
that includes class names (`.chip, .setup-hit, .slot, .lane, .dlg-tab,
.hl-score, .layout-port-hit`), so the obvious refutation is that the 548 is
padded with decoration. I counted differently: I walk **every element** in the
scope on a touch-emulated phone (`hasTouch/isMobile`, Chromium reporting both
`(pointer: coarse)` and `(hover: none)`) and keep one if it is natively
focusable (`button/input/select/textarea/a[href]`), or carries `role="button"`,
or has `tabindex ≥ 0`, or has `cursor: pointer`; then I de-nest — an element
that only has `cursor: pointer` is dropped when a genuinely interactive element
sits above or below it in the tree (so a legend chip's colour dot and the
`div.header` wrapper both go).

Three scenes (inline tile, expanded dialog, setup page):

```
RESULT coarse_targets_under_44=58 count (3 scenes)
RESULT coarse_targets_under_44_strict=57 count
total targets = 58        under 44 px = 58        i.e. 100 %
by kind:  native 35 | role=button 22 | cursor:pointer-only 1
by element: button.chip=14; rect.slot=12; rect.setup-hit=6; rect.lane=4;
  button.vc-out/vc-in=4; button.dlg-tab(.active)=4; button.close=2;
  button.expand=1; button.wi-pin/-revert/-add/-apply/-save/-reset=6;
  input.wi-day-start/-day-end/-temp/-dhw-min=4; span.title=1
```

**Answering the question directly: how many are actually interactive controls
rather than decoration?** **57 of my 58 (98 %)** are unambiguous controls —
35 native form controls/buttons and 22 elements carrying `role="button"` plus
`tabindex="0"` (`rect.slot`, `rect.lane`, `rect.setup-hit`, which the card
itself exposes to assistive technology as buttons and gives "press Enter"
labels). The single soft one is `span.title`, a `cursor: pointer` heading.
The finder's list is not padded. Its only genuinely questionable member,
`.layout-port-hit`, is a 32-unit drag port and did not appear in my scenes.

Not one target reaches 44 px anywhere: the largest is `button.close` at 31.5,
then `button.expand` at 26.0. The card's only coarse-pointer adaptation in the
whole file is `LANE_EDGE_GRAB_COARSE` (6 px on a phone).

**Attack on the threshold, which earns a discount but not a refutation.**
44 × 44 is **SC 2.5.5 Target Size (Enhanced), level AAA** (and Apple/Material
platform guidance); the AA requirement is **SC 2.5.8 Target Size (Minimum),
24 × 24**. The finder frames 548 against 44 without saying it is an AAA line.
But the AA line is failed too: 186 of the coarse-arm targets are under 24 px
with no spacing rescue, and 1880 across all fine-pointer arms.

**Perturbation.** `@media (pointer: coarse) { … { min-height: 44px } }`:
58 → **23** in my scenes (−60 %). The 23 that survive are exactly the SVG
`rect.slot` / `rect.lane` / `rect.setup-hit` targets that a CSS `min-height`
cannot reach — the same geometry D4-02 names, which is the right conclusion
for a fixer to take away.

**On main.** `_coarsePointer`, `cardStyleBlock`, `Legend.html`,
`ExpandedDialog.html`, `SetupPage.pickerHtml` byte-identical;
`hit_small_44_coarse=548`.

**Vote: verify, medium.** Decisive number: **58 of 58 interactive targets
under 44 px on a touch phone, 57 of them natively focusable or `role="button"`
— nothing on the card grows for a finger.**

---

## D4-08 — three of seven series colours below 3:1 on white — VERIFY (low)

Threshold: **SC 1.4.11 Non-text Contrast, AA, 3:1.**

**Re-run.** `series_below_3_light=3`, `series_below_3_dark=0`; price #f5a623
2.03, solar #f2c94c 1.59, house temperature #2fae7a 2.82 on #ffffff. Identical
on main.

**My own reading.** Independently computed from `SERIES_DEFS` with my own
sRGB→luminance implementation in `own_contrast.mjs`'s `lum`/`ratio`: 2.03,
1.59, 2.82 — same three, same values.

**Attack.** The chart draws each series as a stroked line plus a legend dot,
and the dot is the only identification. The line's colour is therefore
"required to understand the content", which is exactly 1.4.11's scope, so the
claim is correctly scoped. It is genuinely low: the legend labels the series in
words as well, so nothing is unreachable — the colour is a convenience.

**Perturbation.** solar `#f2c94c` → `#b8860b`: `series_below_3_light` 3 → **2**
(down by 1, as claimed).

**Vote: verify, low.** Decisive number: **1.59:1 for solar on the light card
background, against 3:1.**

---

## D4-09 — form length and grouping — VERIFY (low)

**Re-run.** `config_flow_ux.py` reproduces all 26 RESULT lines exactly, on the
baseline **and on `origin/main`** (whose `config_flow.py` differs by 182 lines):
`initial_screens=7`, `initial_fields=46`, `user_page_fields=17`,
`user_page_pickers=13`, `options_pages=13`, `options_fields=158`,
`options_max_fields=23 (hot_water)`, `pages_over_15=5 ['entities','hot_water',
'thermal_model','grid','learning']`, `off_theme_fields=1`.

**My own reading.** I confirmed `space_circulation_pump_entity` is
`CONF_SPACE_PUMP_ENTITY` (`const.py:632`), that the only schema that carries it
is the hot-water page (`config_flow.py:1982`), and that its own string is
"Heating circulation pump switch" — a space-heating control on the hot-water
page. That is one line, verified by reading the production schema, not by the
harness's prefix heuristic.

**Attack.** The "off-theme" count is a key-prefix heuristic and could have been
noise; it is not — the single hit is the one real case, and the heuristic finds
no false positives across 158 option fields.

**Perturbation.** Removing the pump picker from `async_step_hot_water`'s
schema: `off_theme_fields` 1 → **0** and `options_max_fields` 23 → **22**
(now `entities`), exactly the two movements the finding predicts.

**Vote: verify, low.** Decisive number: **17 fields (13 entity pickers) on the
first screen and one off-theme field, reproduced unchanged on main.**

---

## D4-10 — a default install logs a WARNING about its own defaults — VERIFY (low)

**Re-run.** `default_submit_warnings=1` on the baseline and **on main**.

**My own reading.** I read both sides of the asymmetry in production:
`coordinator.py:3857` computes `stock = legionella == DEFAULT_DHW_LEGIONELLA_TEMP
and setpoint == DEFAULT_DHW_SETPOINT` and suppresses the repair notice with
`and not stock`, under a comment explaining that a Repairs card on a fresh
install "is not what a Repairs card is for". `config_flow.py:1283` calls
`_dhw_legionella_warning` with no such exemption. Same judgement, two places,
one of them missing it.

**Attack.** *Is a log line a user-visible defect?* Barely — it is a WARNING in
the HA log on a fresh install, which is noise rather than harm. `low` is the
right severity and the finder gave it.

**Perturbation.** Adding the coordinator's stock-pair test to the config-flow
call site: `default_submit_warnings` 1 → **0** (to_zero).

**Vote: verify, low.** Decisive number: **1 WARNING record on the untouched
default path, 0 with the coordinator's own exemption applied.**

---

## D4-11 — the card announces v5.4.17 in a 6.2.14 release — VERIFY (low)

**Re-run.** `card_version_matches=0`; `CARD_VERSION=5.4.17`, `VERSION=6.2.14`,
`manifest=6.2.14`.

**My own reading.** On `origin/main` the constant has moved to **5.4.19** while
VERSION and the manifest are **6.3.2** — so the refactor touched the number and
still did not reconcile it, and `tools/release/stamp.py` on main contains no
reference to `CARD_VERSION`. The duplicate-resource guard
(`customElements.get(CARD_TAG).cardVersion !== CARD_VERSION`) therefore still
cannot distinguish two 6.x copies unless the hand-maintained constant happens
to differ.

**Perturbation.** `CARD_VERSION = "6.2.14"`: `card_version_matches` 0 → **1**
(up).

**Vote: verify, low.** Decisive number: **5.4.19 vs 6.3.2 on origin/main —
still `card_version_matches=0` after the refactor.**

---

## D4-12 — "the same than the saved plan" — VERIFY (low)

**Re-run.** `ungrammatical_en=1`, `ungrammatical_sv=0`; the composed string is
`the same than the saved plan (31.97 → 31.97 SEK, estimated)`. Identical on
main (the English template at line 230 is unchanged).

**My own reading.** The composition is `L("stats.delta_detail", {verdict:
L(cheaper|dearer|the_same)})` with the English template `"{verdict} than the
saved plan"`; Swedish uses `"jämfört med"`, which composes correctly with all
three verdicts. One of three English verdicts is ungrammatical, and it is the
one a cost-neutral edit produces — which is the common case when a user nudges
a slot within the same price hour.

**Perturbation.** English template → `"{verdict} compared with the saved
plan"`: `ungrammatical_en` 1 → **0** (to_zero), and the other two verdicts
still read correctly ("cheaper compared with the saved plan").

**Vote: verify, low.** Decisive number: **1 of 3 English verdicts composes an
ungrammatical sentence; 0 of 3 in Swedish.**

---

## Non-findings I checked

- `console_errors=0` and `hover_shift=0` reproduce on baseline and main across
  390 renders. Confirmed.
- `focus_no_indicator=0` reproduces. Confirmed.
- The `tab_unreached=330` caveat is honest: the finder's own limits section
  says it is the walk's start point, and my re-run gives the same 330 with the
  same per-state pattern (1 unreached per dialog state).
- The Swedish and help-text coverage numbers (`sv_missing=0`, `help_missing=0`,
  `error_keys_missing=0`, `defaults_out_of_range=0`, `duplicate_keys=0`)
  reproduce on both trees.

## What I could not do

- There is still no Home Assistant frontend on this box, so the tile widths
  (359/372/400/1200) and the `<ha-card>` `:host` rules are the finder's model.
  I removed the theme-token half of that dependency for D4-05/06 by measuring
  the card's own fallbacks; the tile-width half remains, and D4-01/02's numbers
  scale with it (a wider real tile makes the font larger and the lanes taller
  in proportion — but the dialog is `96vw` and its 5.60 px lane and 5.60 px
  font do not depend on the tile at all).
- The exact mount order `hui-card` uses is a model. D4-01 survives without it
  (`own_rotate.mjs`).
- `card_geometry.mjs` was re-run without `--shots`; the 182 PNGs are
  regenerable and I read two of the finder's committed ones directly.
