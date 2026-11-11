# D4 round 4 — verify-0-2 (verifier 2 of 3)

- tree: worktree `../audit-r4-verify-D4-2`, detached at `ae2a60b`
  (`claude/13-dimension-audit-920935`). Diff to the finder's baseline
  `7dd68dd`: **one line**, `CARD_VERSION = "6.4.2"` → `"6.4.3"` — no
  behavioural change, so the finder's committed grid outputs are directly
  comparable.
- box: 8-core Apple M1, macOS 25.6.0, Chromium 131.0.6778.33 (chromium-1148),
  node v20.10.0, Playwright 1.49.0 from `/private/tmp/hpo-pw/node_modules`.
- private plan payload: `HPO_PLANDATA=/private/tmp/hpo-d4-v2own/plandata.json`
  (own temp root; written by `tests/plan_view.py` with `PYTHONPATH=tests/hastub`).
- Every number below is a count, a CSS-pixel length or a colour ratio.
  `load1` at the runs: 3.35–6.90 (box shared with other panels); quoted,
  not gated, per the harness contract — no timing, CPU or RSS number is
  claimed anywhere in this report.
- Read first and followed: `tools/audit/briefs/verifier.md`,
  `tools/audit/README.md`. Other verifiers' outputs were not read. The
  scratch files of an earlier session found under `/private/tmp/hpo-d4-v02/`
  were likewise not read; this report's artifacts live under
  `/private/tmp/hpo-d4-v2own/` and `out/v2_*`.

## Harness re-runs (finder's instruments, exact commands from their headers)

| harness | result vs finder |
|---|---|
| `contrast_pixels.mjs` (9 probes) | every probe exact to 3 decimals (1.014 Wood, 1.794/2.393, 1.891/2.547, 1.797, 2.783 wi-save dark, 5.786 light), `load1=4.71` |
| `target_size.mjs` (2 arms × 3 vp × 34 states) | exact: fine 2907 targets / 1548 undersized / 364 failing, dominant sig `button.vc-out 20.22x20.22 (nearest centre 22.22px: button.vc-in)` 93×; coarse 4 / 2; `load1=3.96` |
| `card_grid.mjs` wall clock (1224 cells) | summary identical to committed `out/summary.json` on every line (drive_failures=72, low_contrast_instances=4729, low_contrast_cells=1080, tiny_text_instances=1884 …), `load1=3.35`; per-signature comparison of my re-run vs the committed `cells.json`: **identical sets and counts** (`text.lane-label` 3309, `text.lane-more` 1150, `button.wi-save` 270; tiny `6.4`×1128, `6.6`×756) |
| `card_grid.mjs` frozen (`D4_FREEZE=1`) | summary identical to committed `summary_frozen.json` (see below) |

The finder's instruments reproduce exactly on this box. Where a number below
disagrees with the finder, the disagreement is about **which theme table the
pixels were fed**, not about the instrument's arithmetic.

## My own harness

`tools/audit/round4/D4/v2_own.mjs` (untracked), results in `out/v2_own.json`.
It uses the finder's `lib/states.js` state drivers only — none of
`lib/measure.js` — and its own metric implementations (definitions in the
header and below). One honest bug on the way, recorded because it matters to
anyone re-running this: my first version passed `[pointer === "coarse"]` to
`page.evaluate` **without destructuring**, so `matches` was the truthy array
`[false]` and `_coarsePointer()` turned the coarse floor on in both arms
(every arm then measured 24 px — exactly the failure mode a stub can hide).
Fixed; the finder's harness destructures correctly.

## D4-01 — lane strip 6.4 px at ~1:1 — **verify (high)**

Finder's numbers all reproduce; my own instrument agrees, and my contrast
method returns numbers **worse** than the finder's.

Mine (`v2_own.mjs`, plan_inline, frozen clock, stock HA themes):

| viewport | lane-label px (mine = finder) | my worst band cluster, light | dark |
|---|---|---|---|
| 375×812 | **6.40** | 1.045:1 vs rgb(144,111,76) | 1.137:1 vs rgb(172,139,104) |
| 768×1024 | 6.60 | 1.045:1 | 1.137:1 |
| 1280×800 tile | 11.15 | 1.045:1 | 1.137:1 |

- My metric (1): `font-size` attribute × svg rect / viewBox width. At 375 the
  label runs 16.504 units on a 349 px svg = 6.40 px while the axis floor
  holds the axis text at 8.0 px — the 0.8 factor is measured, not inferred.
  Perturbation arithmetic: removing the `* 0.8` at `heatpump-optimizer-card.js:6653`
  gives exactly 8.0 px at every width where the floor binds; the number moves
  as the claim requires.
- My metric (2): one screenshot at deviceScaleFactor 4, histogram of the
  label's bounding-box band, contrast of the **specified fill** against every
  colour cluster covering ≥ 1 % of the band. Every ≥ 1 % cluster at 375 lies
  between 1.045 and 1.42:1 (light) — red "dearer" slot blocks, the brown
  wood block, the grey track all sit inside the band. This is a different
  definition than the finder's glyph-core worst-pixel (1.014–2.55) and it
  lands in the same class: both are catastrophically under 4.5:1, in both
  themes, at every viewport. My screenshot
  (`out/v2_lane-strip-375-light.png`, regenerated) shows the three labels
  barely distinguishable from the slot colours behind them.
- Source confirmations: labels emitted at `font * 0.8` with
  `fill="var(--secondary-text-color,#888)"` and no plate (`:6651`, `:6788`);
  `--secondary-text-color` values in both theme tables are HA's real ones
  (`ha-style.ts` / `darkStyles`); the axis floor `MIN_AXIS_FONT_PX = 8`
  applies to `font`, and `tests/card_browser.mjs:416,453` filters `lane-*`
  out of the floor check by name (comment: labels "are drawn at 0.8x
  deliberately and are D4-06's subject").
- Attacks run: (a) colours not an artefact of the harness theme table —
  checked, all stock; (b) size an artefact of the ha-card stub's chrome —
  no: when the floor binds, the label is 0.8 × 8 = 6.4 px regardless of the
  svg's exact width (measured 349 px; with the card's own padding the svg is
  narrower and the label is still 6.4); (c) "drag-to-edit surface" — lanes
  are `tabindex`/`role=button` drop targets per `:6640-6644`; (d) severity —
  the naming strip is illegible on phones (size) and low-contrast at every
  size including the 15.96 px dialog (my cluster numbers are
  viewport-independent). High stands for a UI/UX dimension.

## D4-02 — wi-save 2.78:1 "in Home Assistant's dark theme" — **refute as filed (residual low)**

The arithmetic is real; the premise about Home Assistant is false. This is
the KEY ATTACK, executed against HA's own frontend source at the versions
this card supports (hacs.json `homeassistant: 2025.2.0`; today 2026.9):

- `src/resources/ha-style.ts` at 2025.2 (`20250205.0`), the html-level block:
  `--text-primary-color: #ffffff;`. Dark mode adds `darkStyles`
  (`src/resources/styles-data.ts`) via `apply_themes_on_element.ts` — and
  **`darkStyles` does not define `text-primary-color` at all**, so the
  html-level `#ffffff` survives in dark mode. Same structure at 2025.8
  (`20250806.0`, after the refactor into
  `src/resources/theme/color/color.globals.ts`), at 2026.7 (`20260729.0`,
  `darkColorStyles` — no `text-primary-color`) and at current `dev`.
  Stock HA dark theme therefore hands the card **`#ffffff`**, not `#212121`.
- The finder's harness table (`contrast_pixels.mjs` THEMES.dark) asserts
  `--text-primary-color: #212121` for dark — a value stock HA never produces
  in any supported version. The repo's own witness disagrees with the
  finder's table: `tests/card_browser.mjs:882` (`HA_DARK`) sets
  `--text-primary-color:#fff` — matching HA source.
- My executed numbers (`v2_own.mjs`, real Chromium, computed layers):

| theme table | fg | bg | ratio |
|---|---|---|---|
| stock HA dark (source-derived) | rgb(255,255,255) | rgb(2,106,168) | **5.786 — passes AA** |
| stock HA light | rgb(255,255,255) | rgb(2,106,168) | 5.786 |
| custom-primary variant (`#212121`) | rgb(33,33,33) | rgb(2,106,168) | 2.783 |
| finder's dark table (reproduction) | rgb(33,33,33) | rgb(2,106,168) | 2.783 ✓ |

- Where `#212121` really comes from: `apply_themes_on_element.ts` sets
  `text-primary-color = rgbContrast(primaryColor, [33,33,33]) < 6 ? "#fff" :
  "#212121"` **only when the user has picked a custom primary colour**
  (Settings → Themes), and in **both** modes — the default blue #03a9f4
  measures 6.12 vs #212121, so it picks `#212121`. My measurement confirms
  the failure is then mode-independent (`custom_primary_light` is also
  2.783), i.e. not a dark-theme bug even in that variant. A hand-written
  custom theme that sets the variable is the other path.
- So: the finding's headline claim — "Home Assistant's default **dark**
  theme sets `--text-primary-color: #212121`, so … 2.78:1" — is false at
  every HA version the card supports; the "grid corroboration" (270
  `button.wi-save` dark instances below AA, 15 states) is the same table
  artefact and disappears under the stock table. What survives is a
  narrower, lower-severity fragility (a hard-coded fill paired with a theme
  variable the card does not control breaks under a **user-chosen** primary
  colour or custom theme, 2.783:1 in both modes) — different claim, lower
  prevalence, arguably low. The mechanism narrative (the card's own comment
  at `tests/card_browser.mjs:825` records that no fixed colour clears 4.5:1
  against both surfaces) is accurate as far as it goes, but the comment's
  sibling assertion "white on #026aa8" is in fact what stock HA dark shows —
  the card's assumption holds in the stock case it was written for.
- The folded-in second instance **survives the attack untouched**:
  `.delta.dearer` uses `var(--error-color)` and `#db4437` IS HA's stock
  `--error-color` in both modes (`ha-style.ts`); my arithmetic reproduces
  4.291:1 on `#ffffff` and 3.972:1 on `#1c1c1c` exactly. It is separate code
  from `.wi-save` and was explicitly not a finding of its own.

Vote: **refute** the finding as filed (medium, default-dark premise). If the
judge wants the residual re-filed, it is a low.

## D4-03 — zoom pair 20.22 px / 22.22 px under a mouse — **verify (low)**

Finder's `target_size.mjs` reproduced exactly. My own implementation
(`v2_own.mjs` part 4) differs in two ways and still convicts:

- Metric: SC 2.5.8 with the spacing exception applied per the standard's
  exact wording — the 24 px centre circle of an undersized target must not
  intersect a sized target's **box** (circle-rect test) or another
  undersized target's **circle** — instead of the finder's
  nearest-centre-distance approximation for all neighbours.
- Fine arm: 1548 undersized / **386 failing** under my "adjacent" reading
  (finder: 364), 539 under a strict reading that also counts containers.
  The dominant signature is unchanged and fails via the circle-circle
  clause: `button.vc-in 20.22x20.22 circle-circle -> button.vc-out d=22.22`
  (80×; with the 17.33/19.33 variant 30×, the 18.63/20.63 variant 15×).
  Explicit geometry across all states: 93 cells at 20.22×20.22 with 22.22 px
  centre gap, 32 cells at 17.33×17.33 with 19.33 px (the 375 tile) —
  exactly the finder's numbers.
- Coarse arm: buttons 24×24 (floor holds; 141 cells), 4 undersized targets
  total — the coarse arm is clean as claimed.
- Source confirmations: the 24 px floor lives only in `coarseHtmlTargets`
  (`:2769`), emitted only inside `@media (pointer: coarse)` (`:3495`) and
  the `_coarsePointer()` duplicate (`:3497`); the base rule is
  `.viewctl button { width: 1.7em; height: 1.7em; ... font-size: 0.85em }`
  (`:2961`) = 20.21875 px at the 14 px page font — measured live at
  20.21875. The buttons are real mouse targets (`.viewctl` fades in on
  hover; opacity does not remove hit-testing).
- Attacks run: (a) a naive box-only reading of the spacing exception would
  marginally spare the pair (circle radius 12.00 vs neighbour box edge at
  12.11 — 0.11 px), but the exception's circle-circle clause for two
  undersized targets fails them (22.22 < 24), so the finder's conclusion
  holds under the exact wording; (b) the "Equivalent" exception (wheel/pinch
  zoom exists) is arguable but a gesture is not another control on the page;
  (c) my own first-run bug (matchMedia stub arg not destructured) shows how
  the fine arm could be silently measured with the floor on — the finder's
  stub is correct and their 20.22 is the true fine-pointer size; (d)
  severity: low is right — two 2 px-apart 20 px buttons under a mouse.

## Votes

| id | vote | severity | one line |
|---|---|---|---|
| D4-01 | verify | high | 6.40 px / 1.05–2.55:1 reproduced by my own instrument; floor exclusion confirmed in source |
| D4-02 | refute | low (residual) | stock HA dark keeps `--text-primary-color:#ffffff` at every supported version (frontend source, 2025.2/2025.8/2026.7/dev): measured 5.786:1, passes; 2.783:1 needs a user custom primary colour (then in both modes) or a custom theme |
| D4-03 | verify | low | 20.22×20.22 at 22.22 px under fine pointer confirmed by my exact-wording implementation; coarse arm clean at 24 |

## Artifacts (all untracked)

- `tools/audit/round4/D4/v2_own.mjs` — my harness; `out/v2_own.json` results.
- `out/v2_lane-strip-375-light.png`, `out/v2_wi-save-dark-stock.png`,
  `out/v2_wi-save-dark-asserted.png` — regenerated screenshots
  (blobs-not-landed; left untracked per instructions).
- `/private/tmp/hpo-d4-v2own/` — plan payload, grid logs, backup of the
  committed `out/*.json` (restored after the re-runs).
- HA frontend sources fetched to `/tmp/ha_*.ts` (2025.2 = tag `20250205.0`,
  2025.8 = `20250806.0`, 2026.7 = `20260729.0`, plus `dev`).
