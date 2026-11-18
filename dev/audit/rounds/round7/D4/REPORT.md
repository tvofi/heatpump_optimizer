# D4 — UI/UX — round 7 finder report

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave merged).
Workspace: `~/audit-r7-baseline` (export; no `.git`). No GitHub
was read; `gh` was not run.

Interpreter / driver (always from the export root):

```
NODE_PATH=/tmp/pw-r5d4/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
  ~/.nvm/versions/node/v20.10.0/bin/node <harness> [args]
```

Chromium 1148 (Playwright 1.49.0), real headless browser, card loaded into a page
by `addScriptTag({content})`.

## What was measured

`tests/card_browser.mjs` is the published browser lane and it is green at
baseline, so the ordinary flows did not need re-deriving. This report adds three
seams that lane does not drive: (1) the **expanded dialog** at phone widths, (2)
the **Swedish** locale on the same surfaces, and (3) the **currency contract**
between the headline the sensor declares and the table the card renders.

Two harnesses were written, both under `tools/audit/round7/D4/`:

- **`dialog_clip.mjs`** — "pixels by which a text run's rendered ink extends past
  the right edge of the nearest clipping ancestor, MINUS what that ancestor (or
  the document) can scroll to reveal". It walks every text-bearing node, finds
  the nearest ancestor whose `overflow-x` is `hidden`/`clip` (zero reachable) or
  `auto`/`scroll` (reachable = `scrollWidth - clientWidth`), and compares a
  `Range.getBoundingClientRect()` ink box against `rect.right + reachable`. It
  is a deterministic layout measurement, not a timing one (`thread_factor=1` by
  construction; the `RESULT load1=` line is quoted, not gated).
- **`currency_units.mjs`** — "number of money-bearing surfaces the card renders
  for the SAME savings figures whose named currency differs from the currency
  the plan sensor declares its values in", read from the RENDERED TEXT (the
  `.hl-stat` headline and the `.savings-table thead th` cells), never from the
  config that produced it.

Both harnesses set `font-family:-apple-system,"Segoe UI",sans-serif` on the card
host, matching `tests/card_browser.mjs`. This is load-bearing: a table's
min-content width is font-dependent, and without the stack the savings table
fits and the first defect disappears. The harness header states it.

## Findings

### D4-01 — the savings table's `%` column is unreachable at phone widths (high)

Command (the number a judge reproduces):

```
node tools/audit/round7/D4/dialog_clip.mjs --seam savings --width 375 --lang en
RESULT dialog_clip.savings_unreachable=22.4 px
RESULT dialog_clip.savings_table_scroll_width=366 px
RESULT dialog_clip.body_client_width=336 px
```

The savings table is `width:100%` inside `.dlg-body`, whose min-content width is
larger than the body; `.dlg-body { overflow-x: hidden }`
(heatpump-optimizer-card.js:3332) forbids any scroll, so the last column's ink is
painted outside a box no gesture can widen. Because the numeric cells are
`text-align: right`, the hidden strip is exactly the digits: the unreachable runs
are `td.num "25%"` (and the month rows below). At 375 px the reachable loss is
22.4 px of ink in English and 41.1 px in Swedish (the longer month/column
labels); at 320 px it is 75.2 px (en) and 93.9 px (sv).

Leave-one-out over the 20-cell grid (5 widths x 2 languages x 2 pages):
`cells.n=20`, `cells.min=0`, `cells.max=93.9`, `cells.after_dropping_most_favourable=75.2 px`.

Null control (same command, wide body): at `--width 1280` the table's
`scrollWidth` equals the body's `clientWidth` (1197 = 1197) and
`dialog_clip.savings_unreachable=-1` for every seam — the defect is exactly the
condition "table min-content > body width".

Fix moves the number two independent ways:

```
--patch pad     (cell padding 0.35em 0.5em -> 0.35em 0.2em) -> savings_unreachable=-1
--patch scroll  (.dlg-body overflow-x: hidden -> auto)       -> savings_unreachable=-1
```

The same mechanism has a second seam on the Plan tab: the what-if value cells
(`span.wi-value`, a non-wrapping flex row) lose 21.8 px (`wi-comfort-value`) and
12.5 px (`wi-dhw-value`) at 320 px, and `--patch scroll` also returns them to
-1.

### D4-02 — the Swedish tab label "Rådgivare" is clipped by the dialog (medium)

```
node tools/audit/round7/D4/dialog_clip.mjs --seam tabs --width 360 --lang sv --page plan
RESULT dialog_clip.tabs_unreachable=7.5 px      (button.dlg-tab "Rådgivare", clip=expanded)
node tools/audit/round7/D4/dialog_clip.mjs --seam tabs --width 320 --lang sv --page plan
RESULT dialog_clip.tabs_unreachable=45.9 px
```

`.dlg-tabs { display: flex; gap: 0.3em; flex: 0 0 auto }` (line 3378) cannot wrap
or shrink, and its container `dialog.expanded { overflow: hidden }` (line 3326)
hides the overflow. English never overflows (`--lang en -> -1` at every width);
only the longer Swedish labels do. At 375 px the label is inside the box but the
pill still spills 6.9 px.

Fix:

```
--seam tabs --width 360 --lang sv --page plan --patch tabs
(.dlg-tabs flex: 0 0 auto -> 0 1 auto; flex-wrap: wrap; min-width: 0)
RESULT dialog_clip.tabs_unreachable=-1 px            (and likewise at 320)
```

Null control: `--width 1280` -> `-1` for every seam.

This shares a root-cause class with D4-01 (intrinsic content wider than a
clipping ancestor, hidden rather than wrapped/scrolled) but a different container
and a different fix; a judge who prefers one finding per class may merge them.

### D4-03 — the savings table names a currency that is not the value's currency (high)

```
node tools/audit/round7/D4/currency_units.mjs
RESULT currency.heads_contradicting_the_unit=0 count
headline: "Projected savings 300.25 SEK (25%)..."
heads   : ["Month","Baseline (SEK)","Actual (SEK)","Savings (SEK)","%"]

node tools/audit/round7/D4/currency_units.mjs --config EUR
RESULT currency.heads_contradicting_the_unit=3 count
headline: "Projected savings 300.25 SEK (25%)..."     <-- still SEK
heads   : ["Month","Baseline (EUR)","Actual (EUR)","Savings (EUR)","%"]

node tools/audit/round7/D4/currency_units.mjs --hass USD    (no card config)
RESULT currency.heads_contradicting_the_unit=3 count
heads   : ["Month","Baseline (USD)","Actual (USD)","Savings (USD)","%"]
```

One card, one screen, one quantity, two currencies. The headline savings item
takes the unit the *sensor* declares (`headlineHtml`, line 6665-6671:
`attributes.unit_of_measurement`) and says so in its own comment — *"nothing here
converts, so a card-config `currency:` must not relabel it."* The table takes
`this.plan.currency()` (line 11128, heads at 11160), whose chain is
`config.currency || attrRaw("currency") || hass.config.currency || "SEK"` (line
4445) — a different precedence, so the two surfaces disagree. Nothing converts,
so the heads relabel un-converted numbers.

Three reachable arms, weakest configuration first:

- `--hass USD`, no card config: HA's global currency differs from the savings
  sensor's `unit_of_measurement` -> 3 heads contradict the headline. This is the
  realistic non-Swedish install: the integration publishes its own currency while
  HA's global currency is the household's. Needs no card edit at all.
- `--config EUR`: the card's own documented `currency:` option relabels the
  sensor's numbers -> 3.
- `--sensor EUR`, nothing else: the card's hard-coded `SEK` fallback contradicts
  a sensor that declares EUR -> 3.

Controls (both `=0`): nothing set, sensor SEK (`currency_units.mjs`); and
`--config EUR --sensor EUR` (the config agrees with the sensor).

Fix scope: make `_savingsPageHtml` resolve its currency the way `headlineHtml`
does — prefer the plan sensor's declared `unit_of_measurement` and never let a
card-config `currency:` relabel a sensor-denominated figure — or convert.

## Non-findings (checked; held, with the executed number)

| claim | command | value |
|---|---|---|
| No coarse-pointer target under 44 px (or 24 px) on the compact card or any of the four dialog pages | coarse sweep over `button,a,input,select,[role=button],[tabindex]`, viewport 375, spoofed `(pointer:coarse)` | 0 under 44 px, 0 under 24 px |
| Reduced-motion preference is honoured (no animation runs) | page with `prefers-reduced-motion: reduce`, count of running animations | 0 |
| The expanded dialog is genuinely modal (native blocking, focus trapped) | `dialog.showModal()` returns; `document.activeElement` stays in the shadow root | modal |
| No document horizontal scroll on the compact card at 375/360/300 px, either language | `documentElement.scrollWidth - clientWidth` | 0 px |
| The setup SVG needs no horizontal scroll and its hit targets are adequate across three topologies | setup page, `rect.setup-hit` sizes, 375/768/1280 | smallest hit >= 24 px; canvas `overflow-x:auto` |
| Desktop widths are clean for every seam | `dialog_clip.mjs --seam all --width 768` / `--width 1280` | -1 px for every seam |
| The empty-rows savings table does not overflow | savings page with zero `savings_months`, 375 px | table `scrollWidth` 336 = body `clientWidth` |
| The setup slot picker fits at phone width | picker open at 375 px | 213.2 px wide |

## Harnesses

- `tools/audit/round7/D4/dialog_clip.mjs` — D4-01, D4-02. `--seam
  savings|tabs|whatif|other|all`, `--width N`, `--lang en|sv`, `--page
  savings|plan|setup|advisor`, `--patch none|pad|scroll|tabs`, `--cells`.
- `tools/audit/round7/D4/currency_units.mjs` — D4-03. `--config CUR`, `--hass
  CUR`, `--sensor CUR`.

Both self-suffice with `HPO_PLANDATA` (they spawn `tests/plan_view.py` under the
temp root if it is unset, as `plan_view.py` requires).

## Not finished / inferred

- **Config-flow rendering is inferred, not executed.** There is no Home Assistant
  frontend in this export, so the config-flow rubric in `D4.md` was applied to the
  schema and the strings only (`ha-form` card editor, `EDITOR_CURRENCIES`, the
  `currency` option at line 11503/11570), never to a rendered flow.
- **Dark theme** was exercised for layout only; contrast was not re-measured
  against a colours table.
- The what-if seam at 320 px is reported as part of D4-01 rather than as its own
  finding, because it is the same clipping declaration.
- No timing number is reported, so nothing here is provisional: every number
  above is a deterministic layout or text count, contention-immune.
