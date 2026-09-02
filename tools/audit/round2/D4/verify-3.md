# D4 round 2 — verifier seat 3 (perturbation, grid artefacts, scope)

Worktree `v-D4-3` at the baseline `c398fc84`. Playwright 1.49.0 from
`~/.npm/_npx/bbb8a2c4738e2b0c/node_modules`, Chromium 1148 under
`PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers`, Node 20.10.0, Python 3.11.5
(`/usr/local/bin/python3`, the one with numpy). `load1` during my runs was
**6.6–59.0** against the finder's 3.2–8.5; every number below is a count or a
layout-engine pixel size, but see the drift note under D4-03 — two of the
finder's metrics turned out **not** to be load-independent.

My harnesses are in `/private/tmp/claude-501/audit-scratch/D4-3/`:
`v3_flow.py`, `v3_font.mjs`, `v3_axis.mjs`, `v3_ink.mjs`, `v3_decompose.py`,
`perturb.py`, `run_two.sh`. Perturbations were applied to private copies of the
tree (`basesrc` = `git archive HEAD`, `mainsrc` = `git archive origin/main`),
never to the worktree; the worktree is clean.

---

## 0. The structural check: did the refactor move the ground?

**It did not.** The seat prompt's premise — "the card was refactored on main
after this audit's baseline" — is false for `origin/main`. The #136
decomposition landed *before* the baseline (`2afc36f`, PR 9 of #136, is
`c398fc84`'s parent chain). Since the baseline `origin/main` has 18 commits, of
which exactly two touch the card:

```
git diff HEAD origin/main -- .../heatpump-optimizer-card.js
  1 file changed, 59 insertions(+), 36 deletions(-)
```

`f945d44` (#141, per-render pattern ids) and `e403f75` (#138, per-copy lane
geometry), plus `CARD_VERSION` 5.4.17 → 5.4.19.

Every symbol the twelve findings rest on is byte-identical on main:

| symbol | baseline | main |
|---|---|---|
| `LANE_H` / `LANE_GAP` | 15 / 3 (L1045-6) | 15 / 3 (L1045-6) |
| `FONT_BASE` / `FONT_EXPANDED` / `MIN_AXIS_FONT_PX` | 10 / 15 / 8 | same lines |
| `MARGIN` | `{top:16,right:62,bottom:34,left:92}` (L984) | same line |
| `compactFontUnits` | L1027 | L1027 |
| `_measuredCardWidth` | L8591 | L8616 (body unchanged) |
| `.chip.off`, `.setup-slot.empty`, `.empty code`, `.wi-*` CSS | unchanged | unchanged |

And I re-measured on main rather than arguing it:

- 2-arm `card_geometry.mjs` on `mainsrc`: **every RESULT identical** to the same
  run on `basesrc` (overlaps 116, overflow 108, contrast_light 198,
  hit_small_24 307, nospacing 146, hit_small_44_coarse 548, min_text_px 2.96).
- `first_paint_font.mjs` on main: `font_px_lovelace=3.7`, `renders_resize=0`,
  `font_px_attached=7.42` — identical.
- `config_flow_ux.py` on main: **all 26 RESULT lines identical**, despite
  `config_flow.py` changing by 182 lines (the change is entry identity and
  reauth, not the pages).
- `series_contrast.mjs`, `delta_wording.mjs` on main: identical.
  `card_version.mjs` on main: 5.4.19 vs 6.3.2, still `card_version_matches=0`.

**No finding needs re-measuring on main; none is withdrawn on that ground.**

---

## 1. The grid: how many cells does the 15-arm sweep actually have?

The brief's suspicion is correct and worse than suspected. I grouped the arms by
their *per-state count vector* (`v3_decompose.py`): two arms in the same group
produced byte-identical measurements on that metric, so the second one carries
no information.

| metric | distinct arm-vectors / 15 arms | what actually varies |
|---|---|---|
| contrast (D4-05, D4-06) | **2** | theme only |
| overflow (D4-04) | **3** | tile width only (≤372, 400, 1200) |
| overlaps (D4-03) | **5** | width and language; theme none |
| small targets (D4-02, D4-07) | **7** | width, language, coarse; theme none |

Theme never changes geometry. Language changes only text-width metrics.
`phone-light-en-reduce` is byte-identical to `phone-light-en` on every metric
(the report says so; I confirm it). So a "390-render, 15-arm" sweep is a 2- to
7-cell measurement multiplied by 2 to 7, and every headline count in D4-02 to
D4-07 is that multiplier times a small constant.

The per-metric arithmetic:

- `contrast_fail_light = 891 = 99 × 9 light arms` — **exactly 99 in every one of
  the nine light arms.** `contrast_fail_dark = 318 = 53 × 6`.
- D4-06's `600 = 40 × 15` — **exactly 40 in every one of the fifteen arms**,
  from only 5 of the 26 states.
- `hit_small_44_coarse = 548` is **one arm × 26 states** (see D4-07).
- `hit_small_24_nospacing` ranges 104–147 across the 14 fine arms; leave-one-out
  (drop `tablet-light-en`, the largest) 1871 → **1724**.
- `text_overlap_pairs` 58–82 per arm; leave-one-out 1079 → **997**.

---

## 2. Re-run of the finder's harnesses

`card_geometry.mjs`, full 15 arms, 390 renders (my run vs the committed `.out`):

| RESULT | finder | seat 3 | |
|---|---|---|---|
| text_overlap_pairs | 1039 | **1079** | +3.9 %, tolerance said "exact" |
| text_overflow | 792 | 792 | ✓ |
| contrast_fail / _light / _dark | 1209 / 891 / 318 | same | ✓ |
| hit_small_24 | 4224 | **4212** | −12 |
| hit_small_24_nospacing | 1883 | **1871** | −12, tolerance said "exact" |
| hit_small_44_coarse | 548 | 548 | ✓ |
| min_text_px | 2.96 | 2.96 | ✓ |
| console_errors / hover_shift / focus_no_indicator | 0 / 0 / 0 | 0 / 0 / 0 | ✓ |

`load1=27.64`, `thread_factor=1.00`. The other six harnesses reproduce exactly
(numbers under each finding).

---

## D4-01 (high, bug) — the 8 px floor never reaches a dashboard tile

- **Re-run:** `font_px_lovelace=3.7`, `lane_px_lovelace=5.55`,
  `renders_resize=0`, `font_px_refresh=7.31`, `font_px_attached=7.42`,
  `floor_px=8`. Exact, `load1=11.86`, `thread_factor=1.00`. Identical on main.
- **My own number** (`v3_font.mjs`; metric: *the tick label's rendered ink box
  height in CSS px, `getBoundingClientRect().height` on the first axis `<text>`,
  two animation frames after mount*): **5.00 px** in the Lovelace order versus
  **9.00 px** appended-first — a 1.8× difference decided by mount order alone.
  New: `dwell_renders_lovelace=0` — fifteen further deliveries of the *same*
  `hass` object produce no re-render, so the card does not recover on its own.
- **Perturbation (stated, up):** ResizeObserver callback calls `this.render()` →
  `font_px_lovelace` **3.70 → 7.42**, `renders_resize` **0 → 1**. Then measuring
  `.chartwrap` instead of the host → `font_px_attached` **7.42 → 8.00** and
  `font_px_lovelace` **→ 8.00**. Both directions exactly as stated; my own metric
  moves 5.00 → 9.00 px. No render loop (`renders_lovelace` 1 → 2, stable).
- **Attacks.** (a) The code contradicts its own docstring: L8587 says "the
  ResizeObserver re-renders on size change", L8185-8189 only calls
  `_cacheRect()`. (b) `_signature()` (L8244) contains no width term, so nothing
  but a plan/language/currency change can redraw. (c) The 390-render "3.70 px
  everywhere" in the second half of the finding is **not** independent evidence:
  `card_geometry.mjs` L248-253 mounts in the same Lovelace order, so those are
  one fact seen 390 times. The first-order fact stands on its own. (d) Running
  the fix through the geometry grid: `min_text_px` **2.96 → 6.40**, inline chart
  font 3.7 → 8.0, inline lane 5.55 → 8.0 — and the **expanded dialog is
  untouched** (5.6 px), so the finding's third proposal (floor the expanded font)
  is a genuinely separate change, correctly called out.
- **Vote: `verify`.** Decisive: `font_px_lovelace` 3.70 with `renders_resize=0`
  and `dwell_renders=0`, and `font_px_attached=7.42` — the floor fails in *both*
  mount orders, so this is not a first-paint-only race.

## D4-02 (high, bug) — schedule-editor targets

- **Re-run:** `hit_small_24_nospacing` **1871** (claimed 1883, tolerance
  "exact for this payload" — it is not); `hit_small_44_coarse` 548 exact.
- **My own numbers** (`v3_decompose.py`; metric: *distinct `(state, element-class)`
  pairs behind an aggregate, and the aggregate restricted to one grid cell*):
  the 1871 is **46 distinct (state, element) pairs** spread over 14 arms,
  104–147 per arm, 21 of 26 states. Leave-one-out **1724**.
- **Perturbation (stated: `LANE_H` 15 → 40, direction *down*): THE NUMBER DOES
  NOT MOVE.** `hit_small_24` 307 → **307**, `hit_small_24_nospacing` 146 → **146**,
  `hit_small_44_coarse` 548 → **548** (2-arm run, all three unchanged to the
  unit). The geometry *does* move — `rect.lane` 5.60 → **14.9 px**, exactly the
  "5.6 → 15 px" the finding predicts — but the counted aggregate cannot see it,
  because 14.9 px is still under 24 and a slot's small side is its **width**, not
  the lane height.
- I then found the threshold at which it does move, so the harness is not a
  constant: `LANE_H = 70` (lane 25.9 px) gives `hit_small_24_nospacing`
  146 → **109**, with `rect.lane` leaving the fine-arm count entirely (34 → 0)
  and `rect.slot` barely moving (96 → 93). The coarse arm stays at 548 even
  then. So the finding's own proposed value is **4.3× too small** to reach its
  own metric, and no lane-height change touches the majority (96 of 146) of the
  count.
- **Scope / coupling.** The compact-tile lane figure (5.55 px) is a *consequence
  of D4-01*, not an independent defect: applying D4-01's fix raises it to
  **8.00 px**. What survives independently is the dialog: `FONT_EXPANDED` has no
  floor, so the phone dialog lane is 5.6 px and the narrowest slot 2.70 px
  (1.3 px on the coarse arm). Theme changes nothing (light/dark arm vectors are
  identical); only width, language and coarse do.
- **Consequence claim.** "cannot be operated by touch on a phone" is overstated:
  the same dialog carries the slot menu (Enter / long-press) and the what-if time
  inputs at 25.4 px, both non-drag paths to the same edit.
- **Vote: `weaken(medium)`.** Decisive: the finding's stated perturbation moves
  `hit_small_24_nospacing` by **0** (146 → 146). The pixel facts are real and
  reproduce; the 1,883 headline is a 14-arm product of 46 distinct pairs, not
  exactly reproducible, and the proposed fix does not reach it.

## D4-03 (medium, bug) — "axis labels collide at the plot corners"

- **Re-run:** `text_overlap_pairs` **1079** (claimed 1039). 1078 of 1079 are
  `text~text`.
- **My own number** (`v3_axis.mjs` / `v3_ink.mjs`; metric: *the **ink** overlap of
  two labels — each label's ink box from canvas
  `TextMetrics.actualBoundingBoxAscent/Descent` at its own rendered px size,
  with the baseline taken from the SVG `y` attribute mapped through the
  viewBox*):

  | geometry | finder's box pairs | **ink pairs** | ink gap |
  |---|---|---|---|
  | phone tile (svg 333) | 3 | **0** | **+0.09 px** |
  | phone dialog (svg 336) | 3 | **0** | +0.07 px |
  | desktop dialog (svg 1197) | 5 | **0** | **+0.26 px** |

  Every counted pair has a *negative* ink intersection (−0.07 to −3.93 px).
  I rasterised the corner at `deviceScaleFactor: 4` and looked: "°C" sits
  cleanly **above** "60", stacked and legible, with visible clearance
  (`ink_desktop-dialog.png`, `ink_phone-tile.png` in my scratch dir). The
  report's description of the screenshot — "°C 60", "kW 6", as if run together —
  does not match what is drawn.
- **Second problem: the metric is not deterministic.** Ten cells flipped between
  the finder's run and mine at **identical chart geometry** — `plan_inline` on
  `phone-light-en` records `chart 333×140.6 @3.7 px, laneH 5.5` in both runs, yet
  the finder logged **0** overlaps and I logged **4**, with intersection heights
  of 2.3 px against a 1.5 px threshold. This also falsifies the report's
  "none depends on load" for this metric.
- **Perturbation:** unit label lifted 4 → 12 units: `text_overlap_pairs`
  116 → **0** (to_zero, as stated) — but `text_overflow` rises 108 → **148**,
  i.e. the fix simply moves the same ascender box past the svg's top edge. D4-01's
  fix moves it the other way: overlaps 116 → **126**, overflow 108 → **148**.
  The two aggregates are two views of one ascender-box geometry.
- **Vote: `refute`.** Decisive: **`ink_pairs = 0` in all three geometries**, ink
  gap +0.09 px / +0.26 px, confirmed by pixels. A low hygiene note survives
  (0.09 px of leading between unit label and top tick is too tight), but nothing
  collides and nothing is unreadable for this reason.

## D4-04 (medium, bug) — the empty state's entity ids overflow ≤400 px tiles

- **Re-run, per arm** (state `no_plan`; my own cut of `results.json`):

  | tile | `code` spill | `div.empty` spill | rows |
  |---|---|---|---|
  | 359 px (phone, incl. coarse and reduce) | **44.1 px** | **48.0 px** | 4 |
  | 372 px (tablet) | **31.1 px** | 35.0 px | 4 |
  | 400 px (desktop) | **3.1 px** | 7.0 px | 2 |
  | 1200 px (panel) | — | — | 0 |

  The report's "26 px on the tablet … and 14 px at 400 px" is wrong on both
  counts; the correct figures are 31.1 and 3.1. It also under-reports the worst
  spill (48.0 px on `div.empty`, not 44.1).
- **Scope:** 48 rows across **14 of 15 arms**, all in **one of 26 states**
  (`no_plan`). Three distinct arm vectors; theme and language contribute nothing.
  Note the finder's own caveat is right: 744 of the 792 `text_overflow` rows are
  the D4-03 unit-label ascender, so the *aggregate* is mostly artefact; the
  finding's own number is the pixel spill, which is not.
- **Perturbation (stated, to_zero):** `.empty code { overflow-wrap: anywhere }`
  (plus the same on `.empty`) → `text_overflow` 108 → **100** in the 2-arm run,
  i.e. exactly the 8 `no_plan` rows removed. **to_zero, confirmed.**
- **Vote: `verify`** at the stated severity. Decisive: 44.1 px of `code` past the
  card box on a 359 px tile, to_zero under a one-line fix, in the first state a
  new install renders. Correct the two quoted tablet/desktop figures in the
  register.

## D4-05 (medium, bug) — primary-colour text and buttons at 2.63:1

- **Re-run:** `contrast_fail_light` **891** exact.
- **My own numbers.** (a) Independent WCAG computation: `#03a9f4` on `#ffffff`
  **2.63**; white on `#03a9f4` **2.63** — the ratios are right. (b) Grid cut:
  **exactly 99 in each of the 9 light arms** — `891 = 99 × 9`, two distinct arm
  vectors over the whole 15-arm grid, so viewport, language, coarse and reduced
  motion contribute *zero* information. (c) Composition of the 99:

  | element | n / light arm | worst |
  |---|---|---|
  | `tspan` + `tspan.setup-value` | **40** | 2.99 — *this is D4-06* |
  | `text` (now marker) + `text.lane-more` | 23 | 2.63 at 3.7 px |
  | `wi-pin` / `wi-apply` / `wi-save` | 30 | 2.63 |
  | `wi-viewreset`, `chip.off`, `layout-verdict.match` | 6 | 2.43 |

  **360 of the 891 (40 per light arm) are D4-06's rows, counted again here.**
- **Perturbation (stated: down by ≥ 200):** the finding's own rule set gives
  `contrast_fail_light` 198 → **158** in the 2-arm run — 20 per light arm, i.e.
  **≈180 over 9 light arms, short of the claimed ≥ 200**. Worse, the proposed
  `.wi-save { background: var(--dark-primary-color, #0288d1) }` computes to
  **3.86:1** — still below AA for 12 px text — so the 150 `wi-save` rows survive
  the fix, and the 207 `now`/`»` marker rows are not addressed at all.
- **Vote: `weaken(low)`.** Decisive: 891 = 99 × 9, of which 40 per arm are
  D4-06's, and the proposed fix moves only ~20 of 99 while leaving the Save
  button at 3.86:1. The residual honest finding is "three what-if action buttons
  and the chart's now marker render at 2.63:1 in the light theme; 56 boxes per
  light render-set".

## D4-06 (medium, bug) — opacity-faded setup rows and switched-off chips

- **Re-run:** 600 exact (`tspan` 300 + `tspan.setup-value` 300).
- **My own number:** **exactly 40 per arm in all 15 arms** — `600 = 40 × 15`, a
  pure grid product with *no* cell-to-cell variation at all (both themes, every
  width, every language). Only **5 of 26 states** contribute (`setup_coil`,
  `setup_two_tank`, `setup_single_buffer`, `picker_open_filtered`,
  `layout_editing_dragged`); **10 distinct (state, element) pairs**.
  Independent WCAG: `#727272` at 0.75 over white ≈ **3.00**; at opacity 1,
  **4.81** (clears AA). Dark arm total 53 = 20+20+10+3, so the defect is
  theme-invariant, which is why the grid is flat.
- **Perturbation (stated, to_zero):** `.setup-slot.empty { opacity: 1 }` +
  `.chip.off { opacity: 0.7 }` → `contrast_fail_light` 198 → **112**, i.e. 43 per
  light arm removed = exactly `tspan` 20 + `setup-value` 20 + `chip.off` 3.
  **to_zero for the named elements, confirmed; the fix works.**
- **Vote: `weaken(low)`.** The defect and its fix are correct; the number is
  inflated 15×. The register should carry "40 low-contrast rows per render-set,
  worst 2.99:1 at 9.3 px, in the five setup states", not 600.

## D4-07 (medium, bug) — "548 targets under 44 px in the 26 states"

The brief's prime suspect. It is worse than "one page's control count times the
number of cells" — it is one page's control count times the number of *states*.

- **Re-run:** `hit_small_44_coarse` **548**, exact, and exactly the same in a
  2-arm run (`coarse_emulated=1`) — because it is **one arm**, `phone-light-en-coarse`,
  1 of the 15 grid cells, by construction.
- **My own numbers** (`v3_decompose.py`; metric: *distinct element classes and
  distinct per-state signatures behind the aggregate*):
  - **37 distinct element classes** fall under 44 px. That is the inventory.
  - **19 distinct per-state signatures** among the 26 states.
  - Per state: `whatif_edited` 42 (worst), `whatif_weekly` 38,
    `layout_editing_dragged` 36, the plain compact card (`plan_inline`) **18**,
    `no_plan` 7, `no_plan_expanded` 3, `editor_schema` 0.
  - The multiplication: `button.chip` is counted **123 times** (7 chips × ~18
    states), `rect.slot` 96, `rect.setup-hit` 35, `rect.lane` 34.
  - Under the *normative* WCAG 2.2 AA threshold (24 px, SC 2.5.8), only **342**
    are small and **167** survive the spacing exception (report says 186; my
    re-run 167 — see the drift note).

  **Said per distinct page:** a stock compact card on a touch phone has 18
  targets under 44 px (7 legend chips at 22 px, 2 zoom buttons at 17.3, expand at
  26, 2 lanes at 5.5, 6 slots at 1.3–22); the schedule editor at its busiest has
  42.
- **Perturbation (stated, down by ≥ 250):** a coarse `min-height: 44px` rule
  (mine slightly broader than the finding's: I added `.close`, `.expand`, what-if
  inputs and selects, and `min-width`) → `hit_small_44_coarse` 548 → **191**,
  **down 357**. Confirmed and exceeded. The 191 that remain are entirely SVG
  (`rect.slot` 96, `rect.setup-hit` 35, `rect.lane` 34, `circle.layout-port-hit`
  24) — CSS `min-height` cannot reach them; that residue is D4-02's.
- **Vote: `weaken(low)`.** Decisive: 548 = 37 distinct control classes × 26
  renders of one card in one arm; the largest single page is 42 and the default
  view is 18. The defect is real and the fix works, but the number as titled is
  a state-count multiplier, and most of the HTML controls clear the 24 px AA
  threshold that 2.5.8 actually requires.

## D4-08 (low, hygiene) — three series below 3:1 on the light card

- **Re-run:** `series_below_3_light=3`, `series_below_3_dark=0`; price 2.03,
  solar 1.59, house 2.82. Exact. Identical on main.
- **My own number:** independent sRGB→relative-luminance computation reproduces
  all seven ratios to 0.01, and the proposed `#b8860b` gives **3.25** on white
  and **5.24** on `#1c1c1c` — it clears 3:1 in *both* themes, which the finding
  does not claim but needs.
- **Perturbation (stated, down by 1):** solar `#f2c94c` → `#b8860b` gives
  `series_below_3_light` 3 → **2**. Confirmed.
- **Vote: `verify`** (low). No grid, no aggregate, a constant that is what it
  says it is.

## D4-09 (low, hygiene) — form length and grouping

- **Re-run:** all 26 RESULT lines exact — `user_page_fields=17`,
  `user_page_pickers=13`, `options_max_fields=23 (hot_water)`, `pages_over_15=5`,
  `options_fields=158`, `initial_screens=7`, `initial_must_know=2`,
  `off_theme_fields=1`. Identical on `origin/main`.
- **My own number** (`v3_flow.py`; metric: *fields per options page counted by
  driving each `async_step_*` with `None` through a `FakeHass` and reading the
  `vol.Schema` keys, `after_save*` dropped; plus "fields on `hot_water` whose key
  begins `space_`" — no prefix table*):
  `away:5, building:11, building_preset:11, comfort:10, entities:22, grid:18,
  heat_curve:8, hot_water:23, learning:18, setup_overview:0, solar_pv:6,
  thermal_model:16, tuning:10` → `pages_over_15=5`, and
  **`hw_space_keys=1 ['space_circulation_pump_entity']`**. Same conclusion
  without the finder's heuristic.
- **Perturbation (stated, to_zero):** removing the pump picker from
  `async_step_hot_water` → `off_theme_fields` 1 → **0**, `options_max_fields`
  23 → **22**. Confirmed.
- **Vote: `verify`** (low). Honest counts, no grid, reproduces on main.

## D4-10 (low, hygiene) — a default install logs a WARNING "the coordinator deliberately suppresses"

- **Re-run:** `default_submit_warnings=1`, exact, and identical on main.
- **My own number** (`v3_flow.py`; metric: *WARNING records on
  `config_flow._LOGGER` when `async_step_dhw` is submitted with exactly the
  eleven defaults its own schema offers, with no other step driven*): **1** —
  "Hot water: the anti-legionella cycle at 60 °C is above the 55 °C charge
  limit…". The number is real.
- **Perturbation (stated, to_zero):** adding the coordinator's `stock` exemption
  to `_dhw_legionella_warning` → **0**, on both my harness and the finder's.
  The number moves.
- **But the proposed fix fails the repo's own gate.** `tests/features.py:16327`:

  ```
  R.check(
      "the stock defaults are reported too — this is not an exotic pairing",
      _lgw({}, {}) is not None,
      "55 °C limit against a 60 °C cycle is what a fresh install ships with",
  )
  ```

  With the fix, `_lgw({}, {})` returns `None` — I ran both: **True** unpatched,
  **False** patched. And `coordinator.py:3849-3856` explains itself in the
  opposite direction to the finding: it exempts the stock pair from the
  *Repairs card* ("raising a WARNING-severity, non-fixable Repairs card on it put
  a permanent card on every fresh install") and says in the same comment
  "**The config flow logs the same fact at save time**". The coordinator does not
  suppress the log line; it delegates to it.
- **Vote: `refute`.** Decisive: `_lgw({}, {}) is not None` is a named, shipped
  gate assertion that the proposed fix turns False. The behaviour is deliberate
  and tested; the finding rests on a misreading of what the coordinator exempts.

## D4-11 (low, hygiene) — `CARD_VERSION` 5.4.17 in a 6.2.14 release

- **Re-run:** `card_version_matches=0`, `version_delta=1.-2.-3`. Exact.
  On main: 5.4.19 vs 6.3.2, still 0.
- **Perturbation (stated, up):** `CARD_VERSION = "6.2.14"` → **1**. Moves.
- **But the lag is the repo's stated, gate-enforced policy.**
  `tests/entities.py:4398-4406`:

  > "A card-only release bumps both files; an integration-only release leaves the
  > card behind, **which is legal**. Ahead of VERSION is not"

  and the gate asserts `_version_tuple(CARD_VERSION) <= _version_tuple(VERSION)`.
  The finding reports a policy as a defect.
- **My own number** for the second claim (the duplicate guard "keys on that
  number"): over `origin/main`, **58 of the 67 commits that touch the card also
  change the `CARD_VERSION` line — 87 %.** Two installed copies whose card
  content differs therefore almost always differ in `CARD_VERSION`, and the guard
  fires. Where they do *not* differ, the two copies are the same card generation
  and silence is the correct behaviour: the guard keys on the card's own
  generation, which is exactly the thing that decides whether a duplicate matters.
- **Vote: `refute`.** Decisive: `tests/entities.py:4401` names the lag as legal
  and gates it, and the guard's key is 87 % effective and semantically right.

## D4-12 (low, hygiene) — "the same than the saved plan"

- **Re-run:** `ungrammatical_en=1`, `ungrammatical_sv=0`. Exact; identical on
  main.
- **My own number** (metric: *the literal string rendered into `.wi-hint` by a
  real card in Chromium, un-driven*): I built the card, opened the dialog and
  made **no edit**, and read the DOM:

  ```
  ".delta"   → "0.00 SEK"
  ".wi-hint" → "the same than the saved plan (31.97 → 31.97 SEK, estimated)"
  ```

  Composition confirmed at L5452-5468: `delta` within ±0.005 selects
  `stats.the_same`. So the string is not reached only "for a cost-neutral edit" —
  it is the **default state of the schedule editor**, shown every time the dialog
  opens. Reachability is broader than the finding claims.
- **Perturbation (stated, to_zero):** English template →
  "{verdict} compared with the saved plan" → `ungrammatical_en` **1 → 0**, and all
  three verdicts read correctly. Confirmed.
- **Vote: `verify`** (low). Real, reachable on every dialog open, one-line fix.

---

## Voided harness claims

Nothing is voided outright — every harness moves under *some* perturbation, so
none is computing a pure constant. Three claims **about** the harnesses are
false and should not be carried into the register:

1. **"tolerance: exact for this payload"** on D4-02 and D4-03. My re-run on the
   same box, same baseline, same payload gave 1871 (vs 1883) and 1079 (vs 1039).
2. **"Every number below is a count or a pixel size measured by a layout engine,
   so none depends on load."** Two metrics do. `draft_dirty_menu_open`, a
   real-mouse-drag state, gave 17 targets in the finder's run and 14 in mine on
   four arms; and ten `text_overlap` cells flipped 0 ↔ 4 at *identical* recorded
   chart geometry, because the intersection (2.3 px) sits just above the
   harness's 1.5 px threshold.
3. **D4-02's stated perturbation is inert.** `LANE_H` 15 → 40 moves
   `hit_small_24`, `hit_small_24_nospacing` and `hit_small_44_coarse` by exactly
   zero. Recorded here rather than voided because a larger perturbation
   (`LANE_H = 70`) does move them.

## Double counting between findings

`contrast_fail_light = 891` (D4-05) and the 600 tspan rows (D4-06) overlap by
**360** (40 of the 99 per light arm). A register that adds D4-05's 891 to
D4-06's 600 counts those 360 boxes twice.
