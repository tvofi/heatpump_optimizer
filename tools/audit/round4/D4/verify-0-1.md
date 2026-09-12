# D4 — round 4 — verifier report, seat 0-1 (verifier 1 of 3)

- worktree: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D4-1`
  (detached at `0855277`, branch `claude/13-dimension-audit-920935`)
- payload: `HPO_PLANDATA=/private/tmp/hpo-d4-verify1/plandata.json` (written by
  `tests/plan_view.py` from this tree, private temp root)
- Playwright 1.49.0 from `/private/tmp/hpo-pw/node_modules` via `NODE_PATH`,
  Chromium `chromium-1148` from `$HOME/.cache/pw-browsers`, node v20.10.0
- stance: refute-first; every number below was executed by me in this worktree.
  `load1` across my runs: 4.90–12.73 (other agents fan-out out on the box).
  None of these findings rests on a wall/CPU/RSS figure — every number is a
  count, a pixel distance, a CSS-pixel size or a contrast ratio — so the
  contention rule does not touch them. No timing-based refutes below.

## Harnesses re-run (finder's, exactly per header)

| harness | RESULT (mine) | finder said | verdict |
|---|---|---|---|
| `contrast_pixels.mjs` | all 8 lane rows to 3 decimals: wood_lane/light "Wood" spec=1.014; plan_inline/light 1.794 / 2.393; plan_inline/dark 1.891 / 2.547; expanded_plan/light 1.797; expanded_plan/dark 1.891; plan_inline@375/light 1.794. `.wi-save` dark 2.783 / light 5.786 | same | reproduce, ±0 |
| `target_size.mjs` | fine: 102 cells, 2907 targets, 1548 undersized, 1184 spared, **364 failing**; coarse: 4 undersized, **2 failing**; dominant signature `button.vc-out 20.22x20.22 (nearest centre 22.22px: button.vc-in)` ×93 (+mirror ×93) | same | reproduce, ±0 |
| `card_grid.mjs` wall clock | cells=1224, drive_failures=72, page_errors=0, text_nodes=105612, clipped=0, svg_escape=0, tiny_text=**1884** (all `text.lane-label`, 30 states), low_contrast_cells=**1080**, overlap=27266 | same | reproduce, ±0 |
| `card_grid.mjs` frozen (`D4_FREEZE=1`) | cells=1224, drive_failures=**0**, page_errors=0, text_nodes=104040, tiny_text=1884, low_contrast_cells=1080; frozen low-contrast split: lane-label 3151, wi-save 270, delta.dearer 72, lane-more 30 | same | reproduce, ±0 |

Lane-signature instance count: wall-clock lane-label+lane-more = 3309+1150 =
**4459** — the finder's "4459 instances" exactly. The D4 screenshots that
matter were in fact landed (`shots/FINDING_*.png` exist; `blobs-not-landed.md`
keeps exactly the six the findings cite); the `cells*.json` dumps I regenerated
myself rather than trusting anything absent.

## My own harnesses (beside the finder's, `d4_own_<id>.mjs`)

### `d4_own_D4-01.mjs` — lane strip size + contrast, my own definitions

- **(a) on-screen font**: font-size attribute × svg rect/viewBox (finder's
  definition, re-derived independently) = **6.4 px** at 375×812 and **11.15 px**
  at the 1280×800 / 500 px tile — the finder's numbers exactly. My *own*
  additional metric, rendered ink extent `getBBox().height × scale`, gives
  **7 px** (375) and **14 px** (500 tile) for the label runs — larger because
  ink includes descenders, but still under the 18.66 px "large text" bar in
  every case, so the 4.5:1 AA bar applies to all of them.
- **(b) contrast, my own method**: one frame rasterised twice at
  deviceScaleFactor **2** (finder: 4); glyphs removed by **emptying
  `textContent`** (finder: inline `color`/`fill: transparent`); glyph core =
  top **35 %** of changed pixels at channel-delta > **20** (finder: 20 % at
  > 12). Metric = **median** measured-fg/measured-bg ratio over core pixels,
  plus specified-fill vs worst core backdrop pixel (`specWorst`).
  - 375×812 light: median 2.648 / 2.838, specWorst 2.493–2.988, backdrop
    rgb(232,199,165)
  - 375×812 dark: median 3.056 / 3.133, specWorst 3.554, backdrop rgb(92,59,25)
  - 1280×800 light (inline + expanded): median 2.88, specWorst 3.011
  - 1280×800 dark (expanded): median 3.175, specWorst 3.608
  - **every number is under 4.5:1 in both themes at every viewport.** My
    definitions are milder than the finder's worst-point metric, and the
    finding still fails them by a wide margin; both definitions are recorded
    for the judge.
- **(c) floor**: the re-run grid answers it — of 105 612 text nodes over 1224
  cells the only sub-8 px signature is `text.lane-label` (1884 instances);
  every other chart text clears 8 px, i.e. the card's floor reaches everything
  except the lane strip. Source confirms why:
  `tests/card_browser.mjs:416` and `:453` explicitly `.filter((t) =>
  !/lane-/.test(t.getAttribute("class") || ""))` out of the 8 px floor check,
  under the comment "The lane strip's own labels are drawn at 0.8x
  deliberately and are D4-06's subject, not this floor's."
- production source confirmed: `heatpump-optimizer-card.js:6651` and `:6788`
  emit `<text class="lane-label" ... font-size="${font * 0.8}"
  fill="var(--secondary-text-color,#888)">` with no floor and no plate; the
  lane row it names is the interactive editor surface (the `<rect class="lane">`
  at `:6649` carries `tabindex="0" role="button"` and the drag handlers).

**Attacks run on D4-01**

1. *Flattered background?* The finder's analytic compositing was the risk; the
   pixel-truth harness and my own one-raster-diff both read real Chromium
   pixels. Both fail the bar. Not an artefact.
2. *Grid artefact?* 1080 of 1224 cells, 30 of 34 states, both themes, both
   languages, all media arms — and my independent 5-cell run shows the same
   failure. Not a single-cell effect.
3. *Wrong clock arm?* Signature identical in wall-clock and frozen runs.
4. *Is the strip even drawn on a phone?* Yes — measured at 375×812, the phone
   tile; `drive_failures=0` frozen.
5. *Severity inflation?* The strip names the lanes and is the drag-to-edit
   surface of the what-if editor; 6.4 px type at ~2–3:1 is unreadable on a
   phone. High is earned for a UI dimension.

**Vote D4-01: verify, severity high (as filed).** Executed numbers: 6.4 px at
375×812 (mine = finder's), 11.15 px at the 500 px tile, contrast 1.01–2.55:1
(finder, reproduced) / 2.49–3.61:1 (mine, milder definition) — all under the
4.5:1 AA bar that applies (no label reaches large-text size).

### `d4_own_D4-02.mjs` — the wi-save pairing and the premise it rests on

- Arithmetic (my own luminance implementation): `#212121` on `#026aa8` =
  **2.783:1**; `#ffffff` on `#026aa8` = **5.786:1**. Rendered control (bare
  divs, no card, DSF 3, measured pixels): background measured rgb(2,106,168),
  ratios **2.783 / 5.786** from pixels. The finder's arithmetic is correct and
  reproduces exactly.
- **The premise does not survive contact with Home Assistant.** The finding
  says "Home Assistant default **dark** sets `--text-primary-color: #212121`".
  I fetched HA's own frontend theme source at run time (the file HA's docs
  name as the reference) and at three points in history by hand:

  | source | `--text-primary-color` |
  |---|---|
  | `color.globals.ts` @ `dev` (fetched live by my harness) | assigned **0 times** in `darkColorStyles`, once in the base set: **`#ffffff`** |
  | `color.globals.ts` @ tag `20260826.7` | same: base `#ffffff` (line 10), no dark assignment |
  | `styles-data.ts` @ tag `20240103.0` (`darkStyles`) | no `text-primary-color` key at all; base `ha-style.ts` sets `#ffffff` |

  `apply_themes_on_element.ts` (dark path) applies
  `{...darkSemanticVariables, ...darkColorVariables}` **only** — the variable
  is never touched in dark mode. The card requires HA ≥ 2025.2 (`hacs.json`),
  so every version it supports ships `--text-primary-color: #ffffff` in dark
  mode. The repo's own witness agrees (`tests/card_browser.mjs:875,882` sets
  `--text-primary-color:#fff` in both its themes, and its comment at :849
  records `.wi-save` as "white on #026aa8").

  RESULT lines from my harness:
  `ha_dark_block_assignments_of_text_primary_color=0`,
  `ha_base_assignment=#ffffff`, `ha_dark_rules_source=darkColorVariables only`.

  The finder's dark theme table hand-sets `--text-primary-color: #212121`
  (`contrast_pixels.mjs` THEMES dict) — a value stock HA never produces. It is
  plausibly a confusion with HA's real `--text-light-primary-color: #212121`
  (`color.globals.ts:11`), which is a light-mode variable for text on light
  surfaces, not a dark-mode value.

- **Consequence:** in Home Assistant's default dark theme `.wi-save` renders
  `#ffffff` on `#026aa8` = **5.786:1** — passes 4.5:1. The 2.78:1 pairing
  exists only inside the harness's invented theme. HA's own on-accent
  algorithm would also pick white here (`apply_themes_on_element.ts` chooses
  `#fff` unless the accent contrasts ≥ 6:1 with `#212121`; `#026aa8` is 2.78).

- Residues, stated so the judge can weigh them:
  - a **custom** theme that sets `--text-primary-color` dark in dark mode
    would reproduce 2.78:1 — but every filled `ha-button` in HA core shares
    `--mdc-theme-on-primary: var(--text-primary-color)`, so that exposure is
    HA's design surface, not this card's defect;
  - the second instance grouped into D4-02, `.whatif .delta.dearer` at
    HA's own `--error-color` `#db4437`, **does** reproduce arithmetically
    (I recomputed by hand: 4.291:1 on `#ffffff`, 3.970:1 on `#1c1c1c`; the
    frozen grid shows 72 instances) and is genuinely sub-AA — but the finder
    itself says it "is *not* the same code, and a fix for one does not fix
    the other", and 4.29 vs 4.5 on a cost-delta annotation is a low at most.

**Vote D4-02: refute.** The executed number the finding leads with
(2.783:1 "in Home Assistant's dark theme") cannot occur in the environment it
names: HA's default dark theme leaves `--text-primary-color` at `#ffffff`
(verified from HA's own source at run time and at tags 20240103.0 /
20260826.7 / dev), and the real pairing is 5.786:1, a pass. The arithmetic is
right and the harness reproduces — the *theme premise* is wrong, which is the
whole finding. If the judge salvages anything, it is a low-severity finding on
the `delta.dearer` residue, not this claim.

### `d4_own_D4-03.mjs` — zoom pair target size, my own geometry

- Fine pointer, **default environment** (no CDP emulation, no matchMedia stub —
  the honest desktop default), frozen clock, base plan state:

  | viewport/tile | `.vc-out` | `.vc-in` | centre distance |
  |---|---|---|---|
  | 375×812 / 359 | 20.22×20.22 | 20.22×20.22 | **22.22 px** |
  | 768×1024 / 736 | 20.22×20.22 | 20.22×20.22 | 22.22 px |
  | 1280×800 / 500 | 20.22×20.22 | 20.22×20.22 | 22.22 px |

- SC 2.5.8 applied with **my own** geometry (circle–rect intersection of the
  24 px circle with every other target's box, plus circle–circle for other
  undersized targets — the finder used centre distance only): the zoom pair
  **fails** in all three fine-pointer viewports (2 failing targets each);
  coarse control arm lifts them to **24.00×24.00 at 26.00 px**, **0 failing**
  — the floor works where it is applied, exactly the finding's framing.
- The smaller 17.33×17.33 at 19.33 px variant in the finder's claim reproduces
  in my re-run of `target_size.mjs`: 32 cells, all expanded-dialog states
  (away_*, draft_*, …) at the phone/tablet tiles, where the dialog's inset
  shrinks the em-based buttons.
- Source confirmed: `coarseHtmlTargets` (`:2769`, includes `.viewctl button`
  min 24) is emitted only inside `@media (pointer: coarse)` (`:3495`) and the
  `_coarsePointer()` JS duplicate (`:3497`); the base rule (`.viewctl button
  { width: 1.7em; height: 1.7em; font-size: 0.85em }`, `:2961`) yields
  1.7 × 0.85 × 14 = 20.23 px under a fine pointer — measured 20.22.

**Attacks run on D4-03**

1. *Is the finder's spacing test the standard's?* Their centre-distance test
   is close to but not exactly the SC's circle test; my circle–rect version
   agrees the pair fails (both undersized, circles intersect), so the
   conclusion is not an artefact of their simplification.
2. *opacity:0 until hover* — under a fine pointer the controls fade in on
   `.chartwrap:hover`; the finder's walker counted them regardless of opacity.
   The user can only click them in the visible state, which is the state
   measured (20.22 px, 2 px apart); counting the invisible state too does not
   change the verdict.
3. *Does anything rescue them?* The card's own comment (`:4655`) notes wheel
   and drag cover a trackpad — true, and it caps severity at low, which is
   what the finder filed.
4. *Grid artefact?* 93 of 102 (state × viewport) fine cells carry the dominant
   signature; my independent default-environment run reproduces it at all
   three tiles.

**Vote D4-03: verify, severity low (as filed).** Executed numbers: 20.22×20.22
px at 22.22 px centre spacing under a fine pointer (mine = finder's, ±0.01),
17.33 px variant in dialog states, coarse arm clean at 24.00/26.00.

## Summary of votes

| id | vote | severity |
|---|---|---|
| D4-01 | **verify** | high (as filed) |
| D4-02 | **refute** | — (premise false; residue, if any, is a low on different code) |
| D4-03 | **verify** | low (as filed) |

Artifacts from this verification: `d4_own_D4-01.mjs`, `d4_own_D4-02.mjs`,
`d4_own_D4-03.mjs` beside the finder's harnesses; outputs in
`out/d4_own_D4-0{1,2,3}.json`, regenerated `out/{summary,summary_frozen,
cells,cells_frozen,target_size,contrast_pixels}.json`, and the regenerated
`shots/<state>__<vp>__<theme>.png` frames from the grid re-run.
