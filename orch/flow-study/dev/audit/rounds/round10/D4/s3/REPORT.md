# D4-s3 — round 10, D4.M3 (professional look)

Baseline 17f1c55fad1b. Box B10, macOS, Chromium 131 (ms-playwright chromium-1148) driven by playwright 1.56.1
from `tests/pwlane`'s lock (`npm ci --ignore-scripts` into a scratch prefix; executablePath to the 1148 build,
since 1.56.1's own 1194 build is not on this box). No Home Assistant frontend: `ha-card` is a stub element.

## Method
Mounted the real card source in Chromium, states: tile, expanded plan, no plan (`hass.states={}`), setup page;
viewports 375/768/1280 (and 1920/2560 for the dialog), light and dark (`hass.themes.darkMode` in lockstep).
Measured per text run the rendered font size (SVG: fontSize x getScreenCTM().a), font family, legend dot paint
against the series stroke/fill, and the empty state's content.

## Findings
- **D4-s3-01 (low, bug)** — the inline card renders all 8 legend chips (dashed, italic, focusable) in the no-plan
  empty state, above the "No plan data available yet" diagnosis; the expanded dialog gates its legend on `anyData`
  and shows 0. `RESULT empty_state_chips=8`, `empty_state_focusable_chips=8`, control `dialog_empty_chips=0`.
  Perturbation `--perturb=legend` (`savingsTile || !anyData`) → 0. Screenshot `empty_state_8_chips.png`.
- **D4-s3-02 (low, hygiene)** — in the expanded dialog the chart's SVG text (viewBox units, `FONT_EXPANDED`)
  and the setup diagram's text render larger than the dialog's own title: plan 1.104x at 1280, 1.112x at
  1920/2560; setup 1.190/1.198x. Perturbation `--perturb=font` (13 px ceiling on the expanded chart font) →
  0.884/0.889. Setup seam not perturbed by that edit (stays 1.19x), shown as the second seam.

Harness: `node dev/audit/rounds/round10/D4/s3/m3_look.mjs [--perturb=legend|font]` (header has env).

## Non-findings
- Legend dot colour equals its series' painted stroke/fill for all 7 drawn series, light and dark, at 375/768/1280
  (`explore.mjs`); the dashed solar series gets a dashed swatch in both themes.
- One font family (inherited) for all HTML and SVG text; only the diagnostic entity ids use monospace (intended `<code>`).
- Tile chart text floors at 8.0 px rendered at 375 (MIN_AXIS_FONT_PX holds).

## Unfinished
- Spacing-token consistency across states (rendered margins/gaps vs the --hpo-space scale) not measured.
- Headline-number alignment and error states (pin_fail/save_fail) not measured.
- sv language not driven in this seat.

## Leads
- `var(--hpo-text-sm, 14px)` fallback (3 uses) disagrees with the token's 13px declaration (CARD_SCALE_TOKENS);
  only matters if the :host declaration is absent. Within my cells but not measured.

exposure: none.
