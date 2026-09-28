# D4 — verifier seat 2 of 3

Stance per `tools/audit/briefs/verifier.md`: refute-first. Every number below
was executed on this box. Baseline `ae36eff`, 8-core Apple M1, Node v20.10.0,
python 3.11.5, **real Chromium 131.0.6778.33** via Playwright 1.49.0
(`LAUNCH_OK version=131.0.6778.33` printed by each of my three browser
harnesses). No headless-DOM substitution was used for any geometry or contrast
number in this report. `thread_factor` is 1.0 by construction in every harness
here — no BLAS is imported — and every figure is a pixel count, an element
count, a field count or an sRGB ratio.

Production tree untouched: `custom_components/` and `tests/` are byte-identical
to the source worktree (`diff -rq`, empty), and
`heatpump-optimizer-card.js` / `config_flow.py` md5 to
`794f004f10c11b5f5af2ce642917025d` / `bc44b4ad290ef2bd212da0ec8e075f3b` in both
trees. My instruments are under `tools/audit/round3/D4/verify-2/`; the finder's
six files are unmodified (mtimes still 07:50 / 08:00).

## 1. The finder's harnesses, re-run exactly as their headers say

| harness | load1 | thread_factor | outcome |
|---|---|---|---|
| `card_ux_defects.mjs` | 7.92 | 1.0 | every RESULT line reproduced exactly |
| `flow_ergonomics.py` | 8.01 | 1.0 | every RESULT line reproduced exactly |

Both reproduced at the stated tolerance with no deviation, including
`chip_nodata_contrast_light=1.90`, `chip_nodata_contrast_dark=2.36`,
`away_checkbox_min_px=13`, `config_sections_total=0`,
`options_sections_total=34`, `config_flat_fields=70`,
`config_flat_fields_grouped_in_options=55`.

### The 15.91 / 16.10 discrepancy — resolved against the instrument

`card_ux_defects.mjs:39-40` states `15.91` for the opacity:1 perturbation and
for the null arm. The code prints **16.10** for both, on my run and on the
finder's own (`REPORT.md:101,103` says 16.10 twice). **16.10 is right; the
header is stale**, and I confirmed it by a third, independent route: my
rasterised measurement of the same perturbation, which reads the pixels
Chromium painted rather than the finder's colour maths, also returns
**16.10** (`rastered_PERTURBATION_opacity1_light=16.10`,
`rastered_NULL_ARM_with_plan_light=16.10`).

Treated as evidence about the instrument, not the finding: the header was
written from an earlier run and not re-derived when the body was. It changes
nothing about D4-01 — 15.91 and 16.10 are both far past the 4.5 floor and the
perturbation's direction is the same — but it is the **second** of two
header-vs-code divergences I found in the same file, and the other one does
touch a number the report quotes:

**`coarse_ruleset_min_px=24 over 29 controls` is taken over six selectors, not
twelve.** `REPORT.md` says the floor holds "on twelve selectors" and lists all
twelve; `card_ux_defects.mjs`'s `ruled` array contains six
(`.close, .dlg-tab, .chip, .viewctl button, .layout-bar button, .whatif
button`). I re-measured over all twelve: **`styled_control_min_px=24` over 33
controls**, distribution `[24 x7, 25.4, 25.4, 26, 26.8 x5, 28 x3, 30.2 x7,
31.5, 36.4 x7]`. The control survives the correction and gets stronger; the
finder's "29" is an undercount of its own null arm.

## 2. Measured my own way — my metric definitions

Instruments: `verify-2/d4v2_card.mjs`, `verify-2/d4v2_attacks.mjs`,
`verify-2/d4v2_unstyled.mjs`, `verify-2/d4v2_flow.py`. Each carries its command
in its header.

### D4-01 — `rastered_nodata_chip_contrast`

> WCAG 2.x ratio between the 99.5th-percentile-ink pixel of a `.chip.nodata`
> label and the modal background pixel of the chip's own painted box, both
> sampled out of a real `deviceScaleFactor: 1` screenshot of that chip's
> bounding box, decoded by the browser's own PNG decoder into a canvas.

Deliberately different from the finder's: no opacity model, no CSS colour
parsing, no `bgOf` ancestor walk. If the finder's software compositing of
`opacity: 0.3` were wrong, this would disagree. It does not.

| cell | ratio |
|---|---|
| light, host 359 / 736 / 492 | **1.90 / 1.90 / 1.90** |
| dark, host 359 / 736 / 492 | **2.36 / 2.36 / 2.36** |
| perturbation `opacity: 1` | 16.10 |
| null arm, plan sensors present | 16.10, **0** nodata chips |

All seven chips return the identical ratio in every cell (per-chip values
printed in the harness output).

### D4-01 — two numbers the finder listed under "what I could not finish"

The finder measured **reachability** (`tabIndex >= 0`) and said the tab-order
*sequence* was not walked. I walked it, with real `page.keyboard.press("Tab")`
from `document.body`, piercing shadow roots:

* `tab_stops_total=7`
* `tab_stops_to_first_nodata_chip=1`
* `nodata_chips_in_tab_order=7`

**In the no-plan state the seven unreadable chips are the entire
keyboard-reachable surface of the card.** The first Tab lands on one; there is
no other tab stop. That is a stronger statement than "they are tabbable" and it
is the finder's own gap, closed.

Then keyboard activation, not a synthetic `MouseEvent`:
`keyboard_enter_writes_localstorage=1` (Enter on the Tab-focused chip writes
`{"price":true}`), and `hidden_pref_survives_plan_arrival=1` — a **fresh card**
constructed on the same origin after the plan sensors arrive renders
`chip[price]` with `aria-pressed=false`, `off=true`, `nodata=false`. The series
is hidden from a chart that now has data, exactly as claimed.

### D4-02 — `away_min_activation_px` + a finger hit test

> The smaller side, in CSS px, of the smallest element inside `.away-strip`
> that is a form control or a `<label>`, under an emulated coarse pointer;
> plus a 5x5 grid over a nominal 24x24 CSS-px finger target centred on the
> checkbox, where a sample point counts as a hit only if `elementFromPoint`
> returns the checkbox or the `<label>` that wraps it — an ancestor
> `.contains()` test would count the strip `<div>`, which activates nothing,
> and I rejected it after it inflated the first run from 11/25 to 17/25.

* `away_min_activation_px=13` — `<input type=checkbox>` 13x13; `<label>`
  "Away" 51.8x14; `<label>` "Return" 223.7x14; `<input type=datetime-local>`
  184.3x21.3.
* **`away_finger_hit_fraction=11/25`** — 14 of 25 sample points inside a
  finger-sized target do not activate the toggle. Under the perturbation:
  **25/25**.
* `away_strip_display=block`, `gap:normal`, inter-child gap `[0]`.
* Null control: `styled_control_min_px=24` over **33** controls (all twelve
  `coarseHtmlTargets` selectors). Fine-pointer arm:
  `styled_control_min_px_FINE=17.3` — the coarse rule set is what creates the
  24 px floor, and `.away-strip` is simply not in its selector list.

### D4-02 — precondition 1 resolved: the control really is live

The finder's stub `hass` has no `callService`, so `bindAwayStrip` returned at
its first line and the finder's harness never wired the control it describes.
I supplied a `hass` **with** `callService` and drove a real Playwright mouse
click at the checkbox's centre:

```
away_service_call_fires=1
calls=[{"domain":"heatpump_optimizer","service":"set_away","data":{"active":false}}]
```

**The service call does happen.** The control is fully wired in the
configuration real Home Assistant supplies, and `switch.py:110-111` ships
`switch.heat_pump_optimizer_away` with exactly the entity id the strip looks
for — so this is a real control on a real install, not a stub artefact.

### D4-03 — my counting rule, stated before the number

> A **section grouping** is one `section()` **instance** present in the
> `data_schema` a handler actually returns, counted once per
> (flow, step, section-name), recursing into nested sections. The same name on
> two pages is two groupings, because a user meets two collapsible headings.

Two rules I rejected, reported so the divergence is visible rather than
arguable — this project has had three agents count one census three ways:

| rule | config | options |
|---|---|---|
| **mine — `section()` instances per (flow, step, name)** | **0** | **34** |
| source `section(` call sites (whole file) | 2 | 2 |
| distinct section *names* per flow | 0 | 32 |

The call-site count measures the builder, not the UI, and it also carries the
strongest form of the finding: `section()` is constructed in exactly **one**
place in `config_flow.py` — `_page_schema` (line 1613), driven by the `group`
column of the options-only `_OPTION_FIELDS` registry. The other call site
(line 669, `_fit_stored_values`) only re-wraps a section that already exists.
**A config-flow section is therefore structurally impossible, not merely
absent at the state I walked** — which removes the "the walker did not supply
prior answers" objection entirely.

> **My denominator rule**: setup-reachable pages only, where reachable means
> reachable from `async_step_user` through the handlers' own
> `await self.async_step_X()` transitions and `async_show_menu` options
> (derived by AST from `HeatPumpOptimizerConfigFlow` alone). Either/or menu
> branches are reported as branches, never summed.

`config_steps_reachable_from_user=13`. Dropped as unreachable:
`reauth`, `reauth_confirm`, `reconfigure`.

| denominator | flat fields | of which the options flow groups |
|---|---|---|
| finder's union (all `strings.json` `config.step` keys) | 70 | 55 |
| **mine — setup-reachable union ceiling** | **69** | **54** |
| **the "Describe my building" path** | **48** | **40** |
| **the "Enter thermal values directly" path** | **60** | **48** |
| **the default path (Finish setup now)** | **19** | — |

`config.building` is an `async_show_menu` with two mutually exclusive
continuations (`building_describe -> building_extras` vs `thermal -> zones`);
no user is shown both, so the union over-states what anyone meets. And
`reauth_confirm` is entered only from `async_step_reauth`, which Repairs starts
when Tibber revokes a token — never during installation. **A union denominator
is not legitimate for a claim about "the initial config flow", and it inflates
this one by 1 field and by one whole branch.** The finding's direction is
unaffected: 40/48, 48/60 and 54/69 are all above 80%.

## 3. Attacks

### Contention

Both my card harness runs, one at `load1=5.85` and one under twelve spinners at
`load1=12.78`, returned **byte-identical** output on every line — contrast,
tab stops, pixel sizes, hit fractions, the 33-control distribution. Contention
immunity here is measured, not asserted. (This box ran 5.8–12.8 across the
session; the finder's 9.1–25.2 is in the same regime.)

### Grid artefact — does D4-01 rest on one chip or one theme?

No. Dropping cells and re-aggregating: **7 of 7 chips return the identical
ratio in each of 6 cells** (2 themes x 3 host widths). Light alone is 1.90;
dark alone is 2.36; either alone fails 4.5:1. The aggregate is not carrying a
single outlier.

### Grid artefact — does D4-02 rest on one viewport?

No. `13 px` checkbox at 375 / 768 / 1280 viewport, light and dark; labels 14 px
at the two narrow viewports and 15 px at 1280. `away_strip_on_inline_card=0`:
the strip is dialog-only, so it costs one tap to reach.

### Missing null control — what do the styled controls measure?

Present and passing, in both findings. D4-01: with the plan sensors,
**0** nodata chips and worst-chip contrast **16.10**. D4-02:
`styled_control_min_px=24` over 33 controls under coarse, `17.3` under fine.
14 px has something real to be small against.

### Reachable in real Home Assistant, or only through the stub?

Both reachable, and I strengthened one of them.

* **D4-01 is not only an install-time state.** With the plan sensors present
  but **no solar sensor configured**, `nodata_chips_plan_no_solar_sensor=1` —
  "Solar irradiance" stays `.nodata` at **1.90:1**, permanently, clickable,
  tabbable. The solar sensor lives on `config.user_sensors`, whose own title is
  "Optional sensors", so this is the steady state for every install without
  solar, not a transient. The finder framed D4-01 as the fresh-install arm; the
  permanent arm is the better one.
* **D4-02**: `away_service_call_fires=1` with a real click and a real
  `callService` (above), and `switch.py` ships the entity the strip binds to.

### Is the severity earned by consequence?

**D4-01 — yes, at `medium`, and I have to bound one claim of my own.** The
undo affordance is unreadable for exactly as long as the series has no data,
and no longer. Measured on both sides of that line:

* `off_chip_contrast_light=1.90` / `off_chip_contrast_dark=2.36` — a chip a
  user has hidden keeps `.nodata` (the class is recomputed from `hasData`, not
  from `hidden`), so while the series is still empty the *undo* affordance is
  exactly as unreadable as the thing that caused it: line-through at 1.90:1,
  opacity 0.3. In the solar-less arm that is indefinite —
  `permanent_nodata_chip_after_hide=1.9`, `.off=true .nodata=true`.
* `hidden_chip_once_sensor_added=off=true nodata=false opacity=1
  deco=line-through` — **the moment data arrives the chip is readable
  (16.10:1), plainly struck through, and one click restores it.**

So the finder's word "**permanently**" ("silently and permanently hides that
trace") is **not earned and should be struck**: the preference survives, but
the state is visibly marked and reversible in one click as soon as there is a
trace to restore. My own first framing — "no readable way to discover why" —
overstated it the same way and is corrected here to the bounded version above.

What is earned at `medium`: `tab_stops_total=7` (the chips are the *whole*
keyboard surface of the no-plan card), a `not-allowed` cursor that lies about
the control being inert, a label at 1.90:1, and a preference that outlives the
arrival of data — a user taps something they cannot read, on a control that
says it is disabled, and loses a trace until they notice a struck-through chip
later. Not `high`, because it is one click to undo once it matters.

**D4-02 — partly. The miss is inert.** I measured what the 14 missing sample
points land on: `{"dialog.expanded":5,"div.legend":4,"svg":4,"div.away-strip":1}`,
and a real click on the strip `<div>` produced `calls 0->0, dialog still
open=true`. So a mis-tap costs a retry; it does not close the dialog, toggle
the wrong control, or stop the heat pump. The finder's "what a user cannot do"
paragraph — *the control that stops the heat pump heating an empty house is a
13 px target* — is true about the target size and silent about the fact that
missing it does nothing. `medium` is defensible on the 11/25 hit fraction and
the WCAG 2.2 SC 2.5.8 failure; it is not earned by any destructive consequence.

### The claim I could not reproduce: "the only block with no CSS"

`FINDINGS.md`'s headline for D4-02 says `.away-strip` "is the only block with
no CSS". I enumerated every class token the card emits across the inline card,
the expanded dialog and every dialog tab, in both the full-data and no-data
states, and checked each against every `.`-selector in the card's own shadow
stylesheet:

```
emitted_class_tokens=71
styled_class_tokens_in_shadow_css=123
unstyled_emitted_classes=24   ["away-strip","band","crosshair","grid","grid-h",
  "grid-v","lane-label","lane-past","savings-empty","series","shared-band",
  "vc-in","vc-out","vc-reset","wi-actions","wi-comfort-value","wi-day-end",
  "wi-day-start","wi-dhw-min","wi-dhw-value","wi-reset","wi-revert","wi-slots",
  "wi-temp"]
away_strip_is_the_ONLY_unstyled=0
```

**24, not 1.** The headline as written is false. The report body's narrower
wording ("the card's style block ... carries none for `.away-strip`") is true.
And the claim that actually carries the finding survives, because I measured
it: of those 24, `.away-strip` is the **only** one that wraps a form control
whose activation area is undersized —

```
unstyled_blocks_wrapping_an_undersized_control=1   ["away-strip"]
```

Nine of the other 23 are SVG paint classes with no controls; `.wi-actions`
(26.8 px) and `.wi-slots` (24.7 px) have no class rule of their own but their
controls are caught by `coarseHtmlTargets`' `.whatif button` /
`.whatif input[type="time"]`; the rest are text spans. So the finding should be
restated as *the only unstyled block wrapping an undersized control*, which is
a measured 1 of 24, not an unmeasured 1 of 1.

### The claim I refuted: D4-03's stated consequence

The finder's D4-03 rests its severity on this sentence:

> `config.user_sensors` alone asks for [fourteen entities], **with no heading
> telling a first-time user which of them the integration cannot start
> without.**

Measured off the same schema the finder read, plus the shipped catalogue it
already loads:

* `config.user_sensors` markers: **0 `vol.Required`, 14 `vol.Optional`.**
* Its own title: **"Optional sensors"**.
* Its own description: **"Every sensor here is optional. Skip any you do not
  have — the optimizer still works, just with less accuracy."**
* **13 of 13** config steps carry a `description` (23 of 23 options steps do
  too).

The page names the answer in its title, states it in prose, and the schema
agrees: nothing on it is required. The finder's instrument reads `data` and
`data_description` per field and never reads the step's own `title` /
`description`, so it could not see the grouping mechanism the config flow
actually uses — page-level titles and prose across 13 small pages, rather than
in-page `section()` headings across 21 larger ones. The options flow's widest
pages are 19, 16, 13 and 12 fields because they are jump-to-page destinations;
the config flow's default first-run path is **19 fields over two forms**
before a "Finish setup now" menu (`finish_setup`'s own docstring: *"The first
two screens are the only required answers"*).

D4-03's missing control is exactly this: it measures the absence of one
grouping mechanism without a control for the alternative one. Its declared
null arm — the options flow's own pages — proves only that the walker can see
a `section()`, not that a `section()` is the right instrument for a wizard page.
What survives is narrow and true: `config.user_sensors` puts 14 flat entity
pickers on the mandatory path, and 10 of those same keys are grouped in options
under `indoor` / `plant`; `my_config_wide_ungrouped_pages=4`
(`dhw`, `thermal`, `user_sensors`, `zones`). Against which
`my_options_wide_ungrouped_pages=3` (`grid`, `heat_curve`, `thermal_model`) and
`my_options_pages_with_sections=10 of 21` — the options flow is not uniformly
grouped either, so "grouped there, flat here" is a tendency, not a rule.

### Instrument note on my own harness

My first unstyled-class pass printed `emitted_class_tokens=0` and would have
reported a confident "0 unstyled classes". The hand-rolled walker started at a
`shadowRoot` (`nodeType 11`) behind a `nodeType === 1` guard and returned
immediately. It was caught only because the companion figure
(`styled_class_tokens_in_shadow_css=123`) was non-zero. Fixed to
`shadowRoot.querySelectorAll("*")`; both figures printed side by side in the
harness for exactly that reason.

## 4. Verdicts

| id | vote | severity | my executed number |
|---|---|---|---|
| D4-01 | **verify** | **medium** | 1.90 light / 2.36 dark, rasterised over 6 cells; 7 of 7 tab stops; 1 chip permanently nodata without a solar sensor; hidden-chip undo 1.90 while nodata, 16.10 once data arrives |
| D4-02 | **verify** | **medium** | 13 px min activation; 11/25 finger-target hit; 24 px over 33 styled controls; 1 of 24 unstyled blocks wraps an undersized control |
| D4-03 | **weaken** | **low** | 0 vs 34 sections; 40 of 48 / 48 of 60 per-path, not 55 of 70; 0 of 14 required on `user_sensors`; 13 of 13 config steps carry a description |

**D4-01 verify, medium.** Reproduced exactly, then reproduced again by a
method that shares no code with the finder's. Survives every attack, and two
of my attacks strengthen it: the permanent no-solar arm and the unreadable
undo affordance. Stays at `medium` rather than `high` only because a second
click undoes it.

**D4-02 verify, medium.** The geometry is exact and contention-immune, the
null control holds and is 33 controls rather than 29, and the control is
provably live under a real `hass` — which the finder's own harness could not
show. Two corrections the judge should carry into any fix: the headline "only
block with no CSS" is false (24 unstyled classes; the true statement is 1 of
24 wrapping an undersized control), and a missed tap is inert, so the severity
rests on the target-size failure and the 11/25 hit rate, not on a destructive
outcome.

**D4-03 weaken to low, and reclassify from `bug` to a design inconsistency.**
The schema facts are exactly right and I reproduce them (0 config sections, 34
options sections — and structurally so, since the only section-constructing
call site is options-only). What does not survive is the size of the claim and
its stated consequence. The 70/55 denominator is a union across an either/or
menu branch and a reauth page no first-run user reaches; the honest per-user
numbers are 40 of 48 and 48 of 60, and the default first-run path is 19 fields
over two forms. The consequence sentence — no heading says what is required —
is false on the page it names: 0 of 14 markers are required, the title is
"Optional sensors", the description says so, and every one of the 13 config
steps carries a description. Nothing malfunctions, every field has a label and
a help line in all three catalogues (the finder's own non-finding), and the
residual is a real but narrow inconsistency: `config.user_sensors` presents 14
flat entity pickers whose keys the options flow splits into `indoor` / `plant`.
That is worth fixing; it is `low`, and it is not a bug.

No verdict here rests on a timing mismatch, so none is recorded as
`unresolved`.

## 5. Where I differ from seat 1

Opened only after the numbers above were fixed and this report was written, per
the contract, and read only for metric-definition divergence. Seat 1's votes and
severities are the same three as mine; we reached them from different
instruments, so the agreement is independent rather than copied. Three
definitions genuinely differ, and in one of them **seat 1's rule is the better
one**:

1. **The unstyled census (D4-02).** Seat 1's metric is *elements that zero
   parsed rules `Element.matches`* — 64 unstyled classed elements, 2 containing
   a control (`.away-strip`, `.wi-section`). Mine is *class tokens no selector
   mentions* — 24 tokens, 1 wrapping an undersized control. My rule is the more
   permissive of the two and it disagrees on the counterexample: my census
   does **not** list `wi-section`, because some selector mentions `.wi-section`
   even where no rule matches the rendered element. **Seat 1's `matches`-based
   rule is the correct instrument for "has no CSS applied"**, and mine
   under-counts by that much. Both rules land on the same corrected wording, by
   two different routes: seat 1 by 2-of-38 dialog controls under 24 px, mine by
   `unstyled_blocks_wrapping_an_undersized_control=1` of 24 — `.away-strip` is
   the only unstyled block whose controls fall below the card's own floor.
2. **The away-strip size metric (D4-02).** Seat 1 measures the **hit-test
   extent** (1 px-pitch `elementFromPoint` probe): 14 px away vs 28 px styled.
   I measure the **layout box** (13 px) plus a **finger-target coverage
   fraction** (11 of 25 sample points in a nominal 24x24 target activate the
   toggle; 25/25 under the perturbation). Different questions — seat 1's says
   how tall the hittable region is, mine says how much of a finger lands on it
   — and they agree on the conclusion. Seat 1's null control is 28 px over
   three named selectors; mine is 24 px over all 33 controls the card's twelve
   `coarseHtmlTargets` selectors match. Both refute the finder's 6-selector/29.
3. **The section census (D4-03).** Seat 1 ran three rules over three *sources*
   (catalogue `sections` keys, the `_OPTION_FIELDS` `group` column, rendered
   schema) and got 0/34 from all three. I ran one rule over the rendered schema
   and reported two rejected alternatives (2 source call sites, 32 distinct
   names). Seat 1's catalogue rule is a source mine does not touch, and it is a
   genuinely independent confirmation of 0/34; my call-site observation is one
   seat 1's Rule B reaches differently — that `section()` is constructed in
   exactly one options-only place, so a config-flow section is structurally
   impossible rather than merely absent.

We independently derived the same D4-03 branch decomposition (40 of 48, 48 of
60, and a default install path of 19 fields over two form pages) and
independently refuted the same consequence sentence with the same measurement
(`config.user_sensors` required=0, titled and described, all 14 labelled and
help-lined). Seat 1 additionally establishes two fix-scope facts I did not
measure — the W4-G11 recorded precondition that one-level schema walks silently
stop asserting on a grouped page, and that `_page_schema` emits
`collapsed: emitted_group` so adopting the options sections verbatim would
collapse every group after the first on a first-run page. Neither contradicts
anything I measured, and both strengthen the case for `low` rather than
`medium`.
