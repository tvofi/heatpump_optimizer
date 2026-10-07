# D4 — round 4 — verifier 3 of 3 (verify-0-3)

- worktree: `../audit-r4-verify-D4-3` at `claude/13-dimension-audit-920935`
  (head `ae2a60b`), re-created clean for this run
- box: 8-core Apple M1, macOS 25.6.0; node v20.10.0; Playwright 1.49.0 from
  `/private/tmp/hpo-pw/node_modules`, Chromium chromium-1148
  (HeadlessChrome 131.0.6778.33) from `$HOME/.cache/pw-browsers`
- private plan payload: `HPO_PLANDATA=/private/tmp/hpo-d4-v3/plandata.json`
  (fresh `tests/plan_view.py` run under this worktree's temp root)
- `load1` across the session: 4.71–14.49 (other panels share the box).
  Every metric here is a count, a CSS-pixel size or a contrast ratio —
  no timing, CPU or RSS claim is made anywhere in this report, so nothing
  below is contention-sensitive.
- Not read, per the brief: `verify-0-1.md`, `d4_own_*.mjs` and the
  register. Only `FINDER.md`, the finder's harnesses and `lib/` (fixtures)
  were used from the round's material.

## My own harness

`tools/audit/round4/D4/verify3_own.mjs` (this worktree, uncommitted), output
`out/verify3_own.json`. It is written against the same state fixtures
(`lib/states.js`) but shares none of the finder's measurement code: its own
theme tables, its own two-raster contrast loop, its own SC 2.5.8 check.

Two bugs in it were caught and fixed before any number was kept, and are
recorded because a judge re-running the file in this worktree gets the fixed
version while the transcript shows the bad intermediate outputs: Playwright's
`page.evaluate(fn, [x])` passes the **array** as one argument, so my first
version passed `matches: [false]` (truthy) into the `matchMedia` stub — which
made `_coarsePointer()` true in every cell and put the coarse 24 px floor into
my fine arms — and the same array arg made both raster passes hide the glyphs
(`no glyph px`). Both were passing array-args without destructuring; fixed by
passing the boolean. The probe `/tmp/probe_vc.mjs` is what isolated the first
one (20.22 px standalone vs 24 px in-harness).

## D4-01 — lane strip labels: 6.4 px at ≤3.6:1 — **verify (high)**

Finder's harness re-run (`contrast_pixels.mjs`, wall clock, unmodified):
every number in the finding's table reproduces to the third decimal —
`wood_lane` light "Wood" **1.014**, `plan_inline` light "Heating" **1.794** /
"Hot water" **2.393**, dark **1.891**/**2.547**, `expanded_plan` light
**1.797**, dark **1.891**, 375×812 **1.794**.

My own numbers (`verify3_own.mjs`, frozen clock 6 h into the captured day —
the arm the finder's own method calls the realistic one, since on the wall
clock the payload day is entirely in the past and `lane-past` greys the whole
strip):

| cell | on-screen px | spec ratio (worst=median, uniform bg) |
|---|---|---|
| plan_inline 375×812 light | **6.4** | **3.011** over rgb(232,199,165) |
| plan_inline 375×812 dark | **6.4** | **3.607** over rgb(92,59,25) |
| plan_inline 768×1024 light | **6.6** | **3.011** |
| expanded_plan 1280×800 light | 11.15–15.96 | **3.011** |
| expanded_plan 1280×800 dark | 11.15–15.96 | **3.608** |
| wood_lane 1280×800 light | 11.15 | **3.011** |

Every cell is under the 4.5:1 AA bar in both themes; the frozen and
wall-clock arms give different backgrounds (active slot blocks vs the greyed
`lane-past` day) but fail the bar in both, which is the finding's mechanism:
the label has no plate, so its contrast is whatever the schedule happens to
paint under it. My size numbers match the finder's exactly (6.4 / 6.6 /
11.15 / 15.96), and in my cells the only sub-8 px svg text is
`text.lane-label` (`sub8_nonlane=0` everywhere) — corroborating "1884 sub-8 px
instances, all of them lane labels".

Corroboration by the finder's grid, spot-run by me
(`D4_ONLY=plan_inline,wood_lane,expanded_plan D4_VP=375x812`, wall clock,
6 cells): `tiny_text_instances=18`, all `text.lane-label` at 6.4 px —
including the **edit dialog on a phone** (`expanded_plan` at 375), which the
finding's table does not list separately; lane-label analytic contrast
1.08–3.83 across those cells, all under 4.5.

Source and test-gate checks:

- `heatpump-optimizer-card.js:6651` and `:6788` emit
  `<text class="lane-label" ... font-size="${font * 0.8}" fill="var(--secondary-text-color,#888)">`
  with no floor and no plate, over the lane track (fill-opacity 0.07), the
  `lane-past` overlays (0.12) and the slot blocks (0.85). Confirmed by read.
- `tests/card_browser.mjs:416` and `:453` exclude `lane-*` from the 8 px
  axis-font floor, with the comment "drawn at 0.8x deliberately and are
  D4-06's subject, not this floor's" — the exclusion the finding names is
  exactly there.
- Visual check: regenerated `shots/V3_lane-strip-375-light-frozen.png`
  (untracked) and had the strip region read back — the two lane labels are
  the least legible text in the crop, below the axis ticks on the same
  frame.
- The strip is the drag-to-edit surface in the expanded chart
  (`laneKbd` tabindex rect + `slot-hit` rects, `interactive = true`), and
  the drag lanes are named only by these labels.

Attacks run: wrong-background risk (the finder's `fill`-vs-composite trap) —
defused by the pixel method in both their harness and mine; clock-arm
dependence — measured both arms, both fail; "labels redundant with lane
colours" — no: the label is the only thing distinguishing the lanes;
"only the phone tile" — no: the contrast failure holds at 500 px tile and in
the dialog; the 6.4 px size failure additionally holds in the dialog at 375.
Severity high is earned: AA failure on the card's lane naming and edit
surface, both themes, all viewports, both clocks.

**Vote: verify, high.** Executed number: 6.4 px at 3.011:1 (frozen light,
mine) / 1.794:1 (wall light, finder's harness re-run); range across arms and
themes 1.014–3.608, all < 4.5.

## D4-02 — `.wi-save` in "Home Assistant's default dark theme" — **refute**

The finding's mechanism premise — "Home Assistant's default **dark** theme
sets `--text-primary-color: #212121`" — is false, and the false value comes
from the harness's hand-written dark table, exactly the attack this panel was
told to run.

Home Assistant frontend source (via the GitHub API, no checkout):

- **HA 2025.2 era** (the card's minimum, `hacs.json: "2025.2.0"`): tag
  `20250203.0` and `20250205.0`, `src/resources/ha-style.ts:24` —
  `--text-primary-color: #ffffff;` on `html`, and `:25`
  `--text-light-primary-color: #212121;` (a different, unused-here token).
  `src/resources/styles-data.ts:4-57` — `darkStyles`, the complete variable
  set dark mode applies (`apply_themes_on_element.ts`:
  `if (themeToApply && darkMode) themeRules = { ...darkStyles }`) — contains
  **no** `text-primary-color` key (verified by substring over the whole
  object on both tags).
- **Current dev** (Sept 2026): `src/resources/theme/color/color.globals.ts:10`
  `--text-primary-color: #ffffff;` in the base `colorStyles`; the dark block
  `darkColorStyles` (lines 340-401) sets backgrounds, primary/secondary text,
  dividers — **no** `text-primary-color` override (substring check false).
- The only stock code path that ever sets `--text-primary-color` to
  `#212121` is `apply_themes_on_element.ts`'s default-theme branch
  (identical at `20250205.0` and dev):

      themeRules["text-primary-color"] =
        rgbContrast(rgbPrimaryColor, [33, 33, 33]) < 6 ? "#fff" : "#212121";

  which runs **only** when the user has customised the default theme's
  primary colour in settings (`themeSettings.primaryColor`), and applies to
  light and dark alike — it is not a dark-mode behaviour. Otherwise only a
  hand-written custom theme could define the variable.

My own executed numbers (`verify3_own.mjs`, `expanded_plan`, `.wi-save`,
arithmetic from computed styles and the pixel method in agreement; the
button's fill is opaque `#026aa8` so arithmetic is exact):

| theme table | `--text-primary-color` | ratio | AA 4.5 |
|---|---|---|---|
| stock light (HA base) | #ffffff | **5.786** | pass |
| **stock dark (HA `darkStyles`)** | **#ffffff** | **5.786** | **pass** |
| customised-primary, light | #212121 | 2.783 | fail |
| customised-primary, dark | #212121 | 2.783 | fail |

Pixel runs agree with arithmetic in all four (glyph px 9724–9908). The
finder's 2.783 is real arithmetic for #212121-on-#026aa8 — I reproduce it —
but stock HA never puts #212121 there: in the default dark theme the label
resolves to #ffffff and the button passes at 5.786:1, the same as light. The
finder's grid corroboration ("only non-lane signature below AA … dark theme
only, 15 states") inherits the same wrong table and falls with it.

The card's own comment the finding cites (at `:4855`, about the *now marker*
on the card background) is about a different surface (text on
`--card-background-color`) and does not bear on a label sitting on the
button's own opaque fill.

Residuals, for the judge, not for the finding as filed: the hard-coded-fill
+ `var(--text-primary-color)` pairing is theme-dependent, and it does reach
2.783:1 under (a) the opt-in customised-primary-colour default theme — in
**both** modes, not dark — and (b) any custom theme that defines
`text-primary-color` with a dark value. That is a conditional, unmeasured
population, not "Home Assistant's default dark theme", which is what the
medium severity was premised on. The bundled second instance
(`.delta.dearer`, HA's own `--error-color` #db4437 at 4.291/3.972 on the
light/dark card) does not depend on the wrong table — it is arithmetic
against real HA values — but the finder explicitly filed it only as a rider
on this finding, not as its own.

**Vote: refute** (executed number: 5.786:1 in stock HA dark, vs the claimed
2.783:1; premise contradicted by HA's own frontend source at the minimum
supported version and at current dev). Residual exposure via customised
primary colour or custom themes is real but is not the claim as filed and is
not dark-specific.

## D4-03 — zoom −/+ pair under a mouse — **verify (low)**

Finder's harness re-run (`target_size.mjs`, unmodified, frozen clock):
`fine`: 102 cells, 2907 targets, 1548 under 24, 1184 spared, **364 failing
SC 2.5.8**; `coarse`: 4 under 24, **2 failing** (both a 16.72 px-wide
`rect.slot-hit`); dominant fine signature `button.vc-out 20.22x20.22
(nearest centre 22.22px: button.vc-in)` in 93 of 102 cells — every figure in
the finding's table reproduces exactly (±0).

My own numbers (`verify3_own.mjs`, same SC 2.5.8 definition written from the
standard: smaller side < 24 and a 24 px circle (r=12) centred on the box
intersecting another target's circle, i.e. centre distance < 24):

| arm | cell | size | nearest centre | fails |
|---|---|---|---|---|
| fine | plan_inline 1280×800 | 20.22×20.22 | 22.219 (`vc-in`) | yes |
| fine | plan_inline 768×1024 | 20.22×20.22 | 22.219 | yes |
| fine | plan_inline 375×812 | 20.22×20.22 | 22.219 | yes |
| fine | expanded_plan 375×812 (dialog) | **17.33×17.33** | **19.328** | yes |
| coarse | all cells | 24×24 | 26 | no — the floor holds |

Source: `.viewctl button { width: 1.7em; height: 1.7em; … font-size: 0.85em }`
(`:2961`) gives 14 × 0.85 × 1.7 = 20.23 px at HA's 14 px root font, gap
2 px (`:2943`); the 24 px floor (`TARGET_MIN_PX`, `:1205`) is emitted only
inside `@media (pointer: coarse)` (`:3495`) and its `_coarsePointer()` twin
(`:3497`, `:1219`) — confirmed by read, and by my coarse arm where the floor
measurably engages (24×24 at 26 px centres).

Attacks run: spacing exception mis-application — two r=12 circles 22.22
apart intersect, so the exception cannot rescue; conversely my
undersized-but-spared handling reproduces the finder's 1184 spared, so the
exception is being applied, not ignored. `vc-reset` disabled when not
zoomed — a disabled control is not an operable target, but `vc-in`/`vc-out`
fail as a pair on their own. `.viewctl` at `opacity: 0` until hover under a
mouse — the controls are revealed on hover and are then 20.22 px targets;
the reveal does not change the size, and the finding does not rest on the
pre-hover state. Consequence check: zoom is also reachable by wheel, drag,
pinch and keyboard (`controlsHtml`'s own docstring), so a mis-hit costs a
zoom step — low is the right severity.

**Vote: verify, low.** Executed number: 20.22 × 20.22 px at 22.219 px centre
spacing (fine, 500/736/359 px tiles), 17.33 × 17.33 at 19.328 px in the
phone dialog; coarse arm clean (24×24, floor holds).

## Instrument notes (not findings, for the judge's context)

- `contrast_pixels.mjs`'s header claims "the frame is frozen" but the
  harness does not freeze the clock; it is deterministic only because the
  payload day lies entirely in the past on any run date. Numbers taken with
  it are wall-clock numbers (greyed `lane-past` strip); my frozen numbers
  above are the mid-day state. Both fail AA for D4-01; the distinction
  matters only to which background colour is quoted.
- My first `verify3_own.mjs` outputs (24×24 fine-arm buttons, empty glyph
  sets) were the two `page.evaluate` array-arg bugs described above; the
  committed file is the fixed one and its `out/verify3_own.json` is from the
  fixed run.
- Untracked screenshots left in place, not committed:
  `shots/V3_lane-strip-375-light-frozen.png` plus the four
  `<state>__375x812__*.png` frames the spot grid regenerated.
