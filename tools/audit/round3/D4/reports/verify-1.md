# D4 panel — verifier seat 1 of 3

Stance per `tools/audit/briefs/verifier.md`: refute-first. Nothing below is
taken from the finder's report; every figure is one I executed.

Machine: 8-core Apple M1, macOS 25.6.0, Node v20.10.0, python 3.11.5,
Playwright 1.49.0, **Chromium 131.0.6778.33 launched for real**. Positive
control before any measurement, `verify-1/launch_control.mjs`:

```
LAUNCH_OK version=131.0.6778.33
GEOM 137x19
```

No headless-DOM substitute was used anywhere in this report. `thread_factor`
is 1.0 by construction throughout (no BLAS is imported by any instrument
here). `load1` is reported per run.

My instruments are under `tools/audit/round3/D4/verify-1/`. The production
tree was not modified: `config_flow.py` and `heatpump-optimizer-card.js` are
byte-for-byte as delivered, and every perturbation is injected at runtime.

---

## 0. The contention attack, run once for all three findings

The finder asserts its numbers are contention-immune. I did not take that on
the argument; I re-took them under deliberate load.

| run | `load1` | every RESULT line |
|---|---|---|
| finder's, as reported | 9.1 – 25.2 | baseline |
| mine, quiet | 5.83 – 6.17 | **identical** |
| mine, 12 `yes` spinners on 8 cores | **14.40 – 15.33** | **identical** |

Both card harnesses and the flow harness print byte-identical RESULT blocks
at load1 6 and at load1 15. The attack fails: these are layout-engine
pixel counts, sRGB ratios and schema counts, and none of them moves.
**No vote below rests on a timing mismatch**, so `unresolved` does not arise.

---

## D4-01 — the no-data legend chips

### 1. Re-run of the finder's harness

`HPO_PLANDATA=… node tools/audit/round3/D4/card_ux_defects.mjs`, load1 6.17 →
6.15, 3.68 s wall. Transcript: `verify-1/finder_card_ux_defects.rerun.txt`.

| RESULT | finder | mine | Δ |
|---|---|---|---|
| `chip_nodata_count` | 7 of 7 | **7 of 7** | 0 |
| `chip_nodata_contrast_light` | 1.90 | **1.90** | 0 |
| `chip_nodata_contrast_dark` | 2.36 | **2.36** | 0 |
| `chip_nodata_is_disabled` | 0 | **0** | 0 |
| `chip_nodata_tabbable` | 7 | **7** | 0 |
| `chip_nodata_click_persists` | 1 | **1** | 0 |
| `PERTURBATION opacity:1` | 16.10 | **16.10** | 0 |
| `NULL_ARM` with plan data | 16.10, 0 nodata chips | **16.10, 0** | 0 |

Exact, well inside the stated ±0.02. **One internal inconsistency in the
finder's own artifacts**, which I flag because a judge reading only the
harness header would take a different number: the header of
`card_ux_defects.mjs` says `PERTURBATION opacity:1 -> 15.91` and
`NULL ARM -> 15.91`, while the code prints and `REPORT.md` states `16.10`.
The header is stale by 0.19, ten times the tolerance it declares. The
direction and the conclusion are unaffected.

### 2. My own measurement, my own metric

The finder computed contrast **arithmetically** from `getComputedStyle`: it
parsed `color`, walked ancestors for a background, and composited `opacity`
itself. If that arithmetic is wrong nothing in that method would say so. I
never read `color`. `verify-1/chip_raster_and_reach.mjs` **screenshots each
chip and reads the pixels Chromium painted**.

> **My metric A1**: the WCAG 2.x sRGB contrast ratio between the pixel of
> maximum luminance distance from the backdrop inside a chip's label sub-rect
> of a real screenshot (the glyph core), and the **modal** pixel colour of
> that same sub-rect (the backdrop as painted). No computed style is read.
>
> **The finder's metric**: the WCAG 2.x ratio of the element's computed
> `color`, composited with its computed `opacity`, against the first ancestor
> background with alpha > 0.5. The two are comparable and agreed to 0.00.

7 chips × 2 themes × 3 viewports = **42 cells**:

```
RESULT raster_cells_total=42
RESULT raster_nodata_cells_below_4p5=42
RESULT raster_chip_nodata_contrast_light_min=1.90
RESULT raster_chip_nodata_contrast_light_max=1.90
RESULT raster_chip_nodata_contrast_dark_min=2.36
RESULT raster_chip_nodata_contrast_dark_max=2.36
RESULT raster_nodata_contrast_phone_worst=1.90     14 of 14 below 4.5
RESULT raster_nodata_contrast_tablet_worst=1.90    14 of 14 below 4.5
RESULT raster_nodata_contrast_desktop_worst=1.90   14 of 14 below 4.5
```

Painted pixels: light `fg=188,188,188 bg=255,255,255`; dark
`fg=87,87,87 bg=28,28,28`. Both equal the arithmetic composite of
`#212121`/`#e1e1e1` at 0.3 over the card token, so the renderer and the
finder's maths agree independently.

### 3. Attacks

**(a) Is the aggregate a grid artefact — one theme or one chip?** No, and
this is the attack I pushed hardest. `_max` is the honest cell to read: the
**best** chip in each theme is 1.90 / 2.36, so no cell carries the aggregate.
All 7 chips, both themes and all 3 viewports fail, and they fail at the same
number because every chip inherits the one `.chip.nodata` rule. Dropping any
cell and re-aggregating changes nothing.

**(b) Does the number depend on the `<ha-card>` stub?**
`verify-1/ha_card_stub_sensitivity.mjs`, three stubs:

```
RESULT stub[finder (color + background)] / light = 1.90   dark = 2.36
RESULT stub[bare (display:block only)]   / light = 1.90   dark = 1.08
RESULT stub[none (undefined element)]    / light = 1.90   dark = 1.08
```

The **light** number is entirely stub-independent — `.chip` sets
`color: var(--primary-text-color)` explicitly, so nothing is inherited. The
dark number needs a card background, which real `<ha-card>` does declare; and
the bare-stub dark arm is **worse** (1.08), not better, so there is no stub
choice that flatters the finding.

**(c) Tabbability — a property, or a walk?** The finder measured
`tabIndex >= 0`. I ran a **real keyboard walk** (`page.keyboard.press("Tab")`,
`activeElement` resolved through the shadow root):

```
RESULT chip_nodata_tab_reached=7   in 9 press(es)
first stops: button.chip.nodata -> ... x7 -> body -> button.chip.nodata
```

Seven presses from the body land on seven distinct `.nodata` chips: they are
the **first seven tab stops in the card**. Stronger than the finder's claim.

**(d) Click persistence — synthetic or hit-tested?** The finder dispatched
`new MouseEvent("click")`, which bypasses hit testing entirely; a
`pointer-events: none` or an overlay would have made that claim false. I used
a **real hit-tested `page.mouse.click`** at the chip centre:

```
RESULT chip_nodata_pointer_events=auto   cursor=not-allowed key=price
RESULT chip_nodata_real_click_persists=1
   stored={"heatpump-optimizer-card:sensor.heat_pump_optimizer_space_heating_plan:…
```

Verified. `cursor: not-allowed` does not block pointer events, so the CSS
affordance and the behaviour genuinely disagree.

**(e) Is the path reachable in real Home Assistant, or only in a stub?** No
`FakeHass` is involved — this is the shipped card JS in real Chromium. The
only stub is `<ha-card>`, attacked in (b). More importantly I found the
finder **understated** reachability. Their null arm supplies every sensor, so
it can only show the state is transient. I added the arm they did not run —
plan present, an **optional source absent**:

```
RESULT nodata_chips_no_sensors=7 of 7           [price, dhw_slots, space_slots, outdoor, dhw_temp, house_temp, solar]
RESULT nodata_chips_plan_but_no_solar=1 of 7    [solar]  — this arm does NOT go away with time
RESULT nodata_chips_all_sensors=0 of 7          the finder's null arm
```

A household with no solar sensor carries a **permanently** unreadable, live,
tabbable chip at 1.90:1. That is a standing state, not a first-boot window,
and it is the stronger case for the finding.

**(f) Is the severity earned by consequence?** Here the finder **overclaims,
and I can measure it**. `REPORT.md` says a click "silently and **permanently**
hides that trace from the chart they are waiting for". After the real click I
mounted a fresh card, same config, same origin, now with plan data:

```
RESULT hidden_series_survives_plan_arrival=1     aria-pressed=false
RESULT hidden_series_chip_marked_off=1           text-decoration=line-through, opacity=1
RESULT hidden_series_restore_chip_contrast=16.10
RESULT hidden_series_restorable_in_one_click=1
```

The preference does survive — that half is true. But once data exists the
chip renders at **opacity 1 with `line-through`** at **16.10:1**, and **one
click restores it**. "Permanently" is not earned: the state is visibly
marked and one-click reversible. Cut that word and the finding is intact.

The consequence that *is* earned, and that the finder did not measure, is the
feedback loop while the chip is still `.nodata`:

```
RESULT nodata_chip_after_click_opacity=0.3   .off=true .nodata=true decoration=line-through
RESULT nodata_click_feedback_is_dimmed=1
```

The only visual confirmation the click did anything is itself rendered at
1.90:1. A user who cannot read the chip also cannot read that they changed it.

### Vote — `verify`, severity `medium`

Every number reproduces exactly, twice, by two methods, under two load
regimes; all three sub-claims (contrast, tabbability, persistence) hold
independently and each survived a stronger instrument than the finder used.
Medium, not high: the consequence is a legibility failure and a
cursor/handler contradiction, and the trap it enables is one-click
reversible and visibly signposted once data arrives. The word "permanently"
should be struck from the report.

---

## D4-02 — the away strip

### 1. Re-run of the finder's harness

Same run as above, load1 6.17 → 6.15.

| RESULT | finder | mine | Δ |
|---|---|---|---|
| `away_checkbox_min_px` | 13 (13x13) | **13 (13x13)** | 0 |
| `away_label_min_px` | 14 (51.8x14, 223.7x14) | **14 (51.8x14, 223.7x14)** | 0 |
| `away_return_min_px` | 21.3 (184.3x21.3) | **21.3 (184.3x21.3)** | 0 |
| `away_strip_child_gap_px` | 0, `display:block`, `gap:normal` | **0, block, normal** | 0 |
| `legend_row_child_gap_px` | 6, `display:flex; gap:6px` | **6, flex, 6px** | 0 |
| `coarse_ruleset_min_px` | 24 over 29 controls | **24 over 29** | 0 |
| perturbation | 13→24, 14→28, 21.3→28 | **identical** | 0 |

### 2. My own measurement, my own metric

`verify-1/away_hittest_and_reach.mjs`.

> **My metric B1**: the vertical extent, in CSS px, of the set of viewport
> points whose hit test (`elementFromPoint`, resolved through the shadow
> root) lands on the element or a descendant — probe pitch 1 px, emulated
> coarse pointer, 375x812.
>
> **The finder's metric**: the smaller side of `getBoundingClientRect`.
>
> They answer different questions. A layout box can be laid out and covered;
> a hit-test probe cannot. I used it deliberately so that "the label rescues
> it" and "something overlays it" are both testable.

```
RESULT away_checkbox_hit_height_px=14      hit 14x14,  layout 13x13
RESULT away_label_1_hit_height_px=16       hit 51x16,  layout 51.8x14
RESULT away_return_input_hit_height_px=21  hit 185x21, layout 184.3x21.3
RESULT away_hit_height_min_px=14
RESULT away_strip_text="AwayReturn"
```

The hit areas are 1–2 px taller than the layout boxes (antialiased edges
still hit) and land in the same place: **14 px against a 24 px floor.** The
row really does read `AwayReturn` as one word.

### 3. Attacks

**(a) The null control — what does a block WITH css measure?** The task asks
for this explicitly, so I built my own rather than reuse the finder's. Same
page, same run, same probe:

```
RESULT styled_chip_hit_height_px=37      hit 156x37
RESULT styled_dlg_tab_hit_height_px=28   hit 57x28
RESULT styled_close_hit_height_px=32     hit 33x32
RESULT styled_control_hit_height_min_px=28   THE NULL CONTROL
RESULT away_strip_css={"display":"block","gap":"normal","padding":"0px","margin":"0px","font":"12px"}
RESULT legend_row_css={"display":"flex","gap":"6px"}
```

The control holds: styled controls on the same page measure **28 px minimum**
under my metric (24 under the finder's), the away strip measures 14.

Independently, over every control in the opened dialog
(`verify-1/dialog_controls_under_24px.mjs`):

```
controls in dialog: 38; under 24px: 2
   input.  13x13     min=13      <- away checkbox
   input.  184.3x21.3 min=21.3   <- away return
```

**2 of 38, and both are the away strip.** That is a cleaner statement of the
defect than the finder's own, and it is my number, not theirs.

**(b) The universal — "the only feature block with no CSS at all".** A
universal is refuted by one counterexample, and a source grep for
`.away-strip` proves the premise for one block, never the "only". A class
with no rule of its own can still be fully styled through a parent selector
(`.whatif button` styles `.wi-viewreset`), so a **name** census over-fires — I
ran one first and it returned 42 false positives. The right test is rule
matching. `verify-1/unstyled_block_census.mjs`:

> **My metric B3**: elements in the rendered shadow tree carrying a class
> attribute that **zero** rules in the card's own stylesheets match, counted
> with `Element.matches` against every selector the browser parsed.

```
RESULT stylesheet_selectors_parsed=207
RESULT classed_elements_rendered=198
RESULT away_strip_matching_rules=0
RESULT unstyled_classed_elements=64
RESULT unstyled_classed_elements_containing_a_control=2
    CTRL <div class="away-strip">  "AwayReturn"
    CTRL <div class="wi-section">  "Today's slots Drag a slot "
```

**The universal is false by one.** `.wi-section` also matches zero rules. But
the counterexample is harmless and I measured that too — its own controls are
covered by parent selectors and all clear the floor:

```
wi-section controls: wi-viewreset 117x24, wi-pin 96.4x26.8, wi-revert 109x26.8
```

The other 62 are SVG chart primitives (`.series`, `.grid`, `.lane-label`,
`.crosshair`, `.shared-band`) painted by presentation attributes, not CSS.

So: the finder's premise (`.away-strip` has no CSS) is exactly right, and the
sentence built on it ("the only feature block with no CSS at all") needs
re-wording to what is actually true and what I measured — **the only block
whose controls fall below the 24 px floor**.

**(c) Is the path reachable in real Home Assistant?** Two gaps in the
finder's own harness that I closed:

* `bindAwayStrip` returns early on `if (!hass || typeof hass.callService !==
  "function")`. **The finder's `hass` is `{ states }` with no `callService`,
  so their harness never wired the strip** — they measured geometry on an
  unwired control and then asserted it "stops the heat pump heating an empty
  house". I supplied a `callService` and measured:
  `RESULT away_toggle_calls_service=1` — one `heatpump_optimizer.set_away`
  invocation. The control is live. The claim is true; it just was not theirs.
* `switch.heat_pump_optimizer_away` is a shipped entity with a hard-coded
  `entity_id` (`custom_components/heatpump_optimizer/switch.py:111`), so the
  strip renders on any install with away mode on. No stub-only path.

**(d) Is the severity earned by consequence?** Yes. WCAG 2.2 SC 2.5.8 gives
24 px; the card sets the same floor itself for twelve other selectors; this
is a live service call on a phone at 14 px, with the two labels abutting at
0 px so the row reads as one word. The repository's own standard is the
control, which is what makes this a hole rather than a policy choice.

### Vote — `verify`, severity `medium`

Numbers exact on re-run and reproduced by a different metric. Medium rather
than high: the control is small and unlabelled-looking, not unreachable —
a 14 px checkbox is still hittable, and a mis-tap calls a reversible service.
The report's "only feature block with no CSS at all" should become "the only
block whose controls fall below the card's own 24 px floor", which is what
2-of-38 measures.

---

## D4-03 — the initial flow groups nothing

### 1. Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D4/flow_ergonomics.py`,
load1 5.83 → 5.83. Transcript: `verify-1/finder_flow_ergonomics.rerun.txt`.

| RESULT | finder | mine | Δ |
|---|---|---|---|
| `config_sections_total` | 0 | **0** | 0 |
| `options_sections_total` | 34 | **34** | 0 |
| `config_flat_fields` | 70 | **70** | 0 |
| `config_flat_fields_grouped_in_options` | 55 | **55** | 0 |
| `ungrouped_pages_ge8_fields` | 7 | **7** | 0 |
| `presented_fields_total` | 257 | **257** | 0 |

### 2. My own measurement — three counting rules, stated

Three agents on this project counted "the same" census three ways. So I ran
three rules over **three different data sources** and wrote each down:
`verify-1/flow_sections_census.py`.

> **Rule A (catalogue)**: a section is a key of `<flow>.step.<page>.sections`
> in `strings.json` / `en.json` / `sv.json` — what the frontend needs a
> heading for, so what a user can see.
>
> **Rule B (source registry)**: a section is a distinct `(step, group)` pair
> over `config_flow._OPTION_FIELDS` rows with `group is not None` — the
> column `_page_schema` turns into a `section()`. Plus literal `section(`
> calls inside the `HeatPumpOptimizerConfigFlow` class body.
>
> **Rule C (rendered schema)**: walk every `async_step_*(None)` and count
> values in the returned `data_schema` whose `.schema` is a `vol.Schema` —
> the finder's rule, re-derived.

```
RESULT A_config_sections_strings.json=0            A_options_sections_strings.json=34
RESULT A_config_sections_translations_en.json=0    A_options_..._en.json=34
RESULT A_config_sections_translations_sv.json=0    A_options_..._sv.json=34
RESULT B_options_sections=34   on 10 page(s)
RESULT B_config_literal_section_calls_in_configflow_class=0
RESULT C_config_sections=0     C_options_sections=34
```

**Three rules, three sources, the same 0 and the same 34.** The core claim is
not rule-sensitive.

The 55-of-70 figure: my first attempt at an independent rule (a config key
appears as an `_OPTION_FIELDS` row with a non-`None` group) returned **49**,
not 55, and the difference was all six fields of `config.building_describe`.
The cause is `_DYNAMIC` rows, whose `key` is a placeholder and whose real
field keys come out of `widget(current)` — a source-level rule cannot see
them. Re-derived off the **rendered** nesting instead
(`verify-1/grouped_in_options_nesting_walk.py`, a walker I wrote, not the
finder's):

```
RESULT my_config_flat_fields=70
RESULT my_config_flat_fields_grouped_in_options=55
   user_sensors 10/14 | dhw 11/11 | zones 11/11 | thermal 3/10 | temperature 7/7
   building_describe 6/6 | user 4/5 | building_extras 0/3 | weather_sensitivity 2/2
   reauth_confirm 1/1
```

**55 of 70, reproduced.** I record the 49 because it is the kind of number a
later seat would otherwise re-derive and disagree over: the source rule is
wrong, the schema rule is right, and the reason is `_DYNAMIC`.

### 3. Attacks

**(a) Is the aggregate a grid artefact? Yes — the denominator is a union over
mutually exclusive branches.** This is the attack that lands. `config.building`
is a **menu**, not a step: `building_describe`+`building_extras` **or**
`thermal`+`zones`. And `reauth_confirm` is a re-authentication page, not part
of setup at all. So no user is ever presented 70 fields. Dropping the
unreachable cells and re-aggregating:

```
RESULT branch[minimal, "Finish setup now"] = 14 of 19   over 2 form pages
RESULT branch[continue + Describe my building] = 40 of 48   over 7
RESULT branch[continue + Enter thermal values] = 48 of 60   over 7
RESULT branch[union — the finder's denominator] = 55 of 70   over 10
```

The worst single walk is **48 of 60**; the **default** install path — which
the finder's own non-finding correctly identifies as five screens,
`user → user_sensors → finish_setup → finish_now → setup_overview` — is
**14 of 55 over 19 fields on two pages**. "55 of 70" is real arithmetic over
a real union, but it is not an experience anyone has.

**(b) Is `section()` absence a defect, or does the initial flow deliberately
differ?** I looked for a recorded decision and found the opposite of one:

* Issue **#516** is titled *"config-flow **options** are ungrouped"*, closed
  by #653 (`docs/plan-2026-09-open-issues.md:361`). Its scope was the options
  flow. Nothing anywhere states the initial flow should stay flat.
* `section` is available at the declared floor: `hacs.json` declares
  `"homeassistant": "2025.2.0"`, and `tests/hastub/homeassistant/data_entry_flow.py`
  records that `section` exists since 2024.7.0 and that *"grouping was
  originally parked"* at an older 2024.6.0 floor. The version reason is void.
* Mechanically the asymmetry is architectural, not chosen: the options flow's
  sections fall out of the `_OPTION_FIELDS` registry's `group` column via
  `_page_schema`; the config flow has no registry and builds each
  `vol.Schema` by hand.

So: not deliberate, and not blocked. The absence is real.

**(c) Is the severity earned by consequence?** **No — and this is measured,
not argued.** The finder's stated harm is that `config.user_sensors` asks for
fourteen entities *"with no heading telling a first-time user which of them
the integration cannot start without"*. I measured that page
(`verify-1/config_page_required_and_help.py`):

```
config.user_sensors  fields=14  required=0
                     labelled=14/14  help_line=14/14  title=True description=True
config.user          fields= 5  required=2  ['name', 'weather_entity']
config.dhw           fields=11  required=0   labelled=11/11  help_line=11/11
config.zones         fields=11  required=0   labelled=11/11  help_line=11/11
```

**Every one of the 14 fields on that page is `vol.Optional`.** The
required/optional distinction the stated harm turns on does not exist on the
page the harm is stated about — the integration starts without all fourteen,
which is precisely why `finish_setup` offers "Finish setup now" on the very
next screen. And every field carries a translated label *and* a translated
help line, on a page that has its own title and description. What is missing
is grouping, not explanation.

**(d) Is the fix scope as stated?** No. The report says *"sections are a
schema-and-strings change with no behaviour change"*. There is a recorded,
measured precondition in the tree that contradicts that: the W4-G11 brief in
`.claude/workflows/wave-4-groups.json` states that one-level schema walks in
the assertion layer **do not fail on a grouped page, they silently stop
asserting**, that the count was 35 at `52c83d1`, and that *"before grouping
any page, teach the walks that assert on that page to recurse, in the same
PR"*. My own narrower AST rule (`verify-1/one_level_schema_walks.py`) finds
**14** — I state mine rather than carry theirs, the rules differ, and the
load-bearing point survives either count: grouping a config page owes
assertion work, and a fixer told "no behaviour change" will not do it.

A second cost the report does not name: `_page_schema` emits
`section(..., {"collapsed": emitted_group})`, so adopting the options flow's
sections verbatim would **collapse** every group after the first. On a setup
screen that means fields hidden behind a disclosure on the one page a
first-time user must complete.

### Vote — `weaken`, severity `low`

The measurement is solid and survives every attack I could build: 0 vs 34
holds under three counting rules over three data sources, and 55 of 70 holds
under a walker I wrote myself. The *finding* does not survive at medium.

* The denominator is a union over an either/or branch and a non-setup reauth
  page; the default install path is 19 fields over 2 pages, of which 14 are
  grouped in options.
* The stated consequence is measurably wrong: `config.user_sensors` has
  **0** required fields, so there is nothing for a heading to disclose about
  what the integration "cannot start without", and all 14 fields are labelled
  and help-lined on a titled, described page.
* Nothing malfunctions, nothing is unreachable, nothing is illegible. Class
  `bug` is not earned; this is a consistency and polish item — the same
  ground is grouped on the revisit and flat on the first run — and it is
  worth fixing, at `low`.

---

## Summary

| id | vote | severity | my executed number |
|---|---|---|---|
| D4-01 | `verify` | medium | 42 of 42 raster cells below 4.5 — 1.90 light / 2.36 dark, 7 chips x 2 themes x 3 viewports; 7 real Tab stops; real hit-tested click persists |
| D4-02 | `verify` | medium | away hit-height min **14 px** vs **28 px** for styled controls on the same page; **2 of 38** dialog controls under 24 px, both in the strip |
| D4-03 | `weaken` | low | 0 vs 34 sections under three rules; **14 of 19** fields on the default install path, not 55 of 70; `config.user_sensors` **required=0** |

Wording corrections the judge should carry into any fix brief: strike
"permanently" from D4-01; replace D4-02's "the only feature block with no CSS
at all" with "the only block whose controls fall below the card's own 24 px
floor" (`.wi-section` is a second zero-rule block, harmless); and strike
D4-03's "schema-and-strings change with no behaviour change", which the
W4-G11 recorded precondition contradicts.
