# Round 11 D4 verify (seat D4-v1, box V6)

All 12 findings come from planted scopes (D4-s1, D4-s2, D4-s3), so every number below was taken in a private copy of the planted export (../audit-r11-px-D4) with PYTHONPATH=tests/hastub.
Browser numbers come from this box's preinstalled Chromium and playwright (/opt/node-tools), not the finder's Chromium 158; every count still matched exactly.
V2 harnesses: v2_text.py and v2_card_static.py, in this report directory. The verdict columns, other verifiers' reports and GitHub were not read.

## D4-s1-01: **verify** (medium; class P9 (unfloored hit target): confirmed)

- metric: pipe targets in layout_editing_dragged/tidy whose elementFromPoint band, normal to the pipe at its midpoint, is under 24 px (fine) or 44 px (coarse)
- V1 reproduced: 576 of 576; max 5.75 px; port median 30.5 px; perturbed 296
- V2 independent: stroke-width 3.5 user units is the whole hit target, with no wider hit path in the source
- attacks:
  - perturbation PERTURB=1 (stroke-width 60): 576 -> 296 (down, as stated)
  - null control: port_hit_median_px 30.5 px, so the scan reads a sized target as sized
  - max band 5.75 px at 1280 px; min 0 (pipes under dragged boxes)
  - V2: the only editing rule is `.setup-svg.editing .setup-pipe { stroke-width: 3.5; cursor: pointer }`; no transparent hit path exists (no pipe-hit class)
  - keyboard alternative: pipes are focusable (data-edge refocus, card.js:14779-14788). D4-criteria F1 has no equivalent-control exception, so it does not void the finding; it does bound the consequence for keyboard users
- V3 reach: yes: card layout editor in a real browser; no HA stub involved
- seam_rule enumerates: yes: m1_browser.mjs strict_small covers every interactive element class in the grid; m1_pipes covers the SVG pipes it cannot box-measure

## D4-s1-03: **verify** (low; class P9: confirmed)

- metric: interactive targets under 44 px under a coarse pointer (24 px fine) in the score_open state
- V1 reproduced: 72 (renders 72); perturbed 0
- V2 independent: min-height 32px; .hl-fold-head absent from the coarse 44 px list
- attacks:
  - perturbation HPO_PERTURB adds .hl-fold-head to the floor list: 72 -> 0 (to_zero, as stated)
  - null: the 36 fine renders count 0 (72 renders, 72 targets, all coarse)
  - V2: `.hl-fold-head { min-height: 32px }`; the `.sp-filter, .sp-select` coarse floor list omits it
- V3 reach: yes: card on a touch device; no stub
- seam_rule enumerates: yes: strict_small over every interactive element

## D4-s2-01: **verify** (low; class P2 (sibling seam options.modbus_prefill carries the placeholder, config.device_prefill does not); corrected from new)

- metric: (shipped translation language, window field) pairs whose config.error string reads {min_window_minutes} while the device_prefill form result carries no such placeholder; strings.json (the en source, not shipped to users) excluded
- V1 reproduced: 8
- V2 independent: device_prefill is the one window-error step whose placeholder expression lacks _WINDOW_PLACEHOLDERS; 3 shipped languages x 2 errors = 6
- attacks:
  - perturbation --perturb: 8 -> 0 as stated
  - null/control cells (modbus_prefill x2, config.dhw, options.hot_water, grid_fees x3): 0 unfilled
  - finder's 8 counts strings.json as a 4th 'language file'; only de/en/sv ship: 6 user-visible pairs
  - V2: L2720 device_prefill placeholders = {**disclaimer(), **notes} without _WINDOW_PLACEHOLDERS; dhw (L3155) and modbus_prefill (L3996) carry it
- V3 reach: yes: production form result; HA frontend formats step errors with the step's description_placeholders, no stub divergence involved; requires the pre-fill offer switched on and a resolving device
- seam_rule enumerates: partial: flow_errors.py drives a hand-listed 9 cells; V2's AST scan over every show_form site finds no further window step without the placeholder

## D4-s2-02: **verify** (low; class P6 (a reader names a key the producer never writes); corrected from new)

- metric: translation leaves whose {placeholder} set differs from strings.json's for the same key
- V1 reproduced: 1
- V2 independent: 1
- attacks:
  - perturbation --perturb-fix-de: 1 -> 0 (both parity and exception_placeholders_unsupplied)
  - in-file control: en and sv of the same key read {entry_ids}
  - V2: 4533 leaves compared, 1 mismatch (de exceptions.run_optimization_no_prices.message {entry_id} vs {entry_ids})
- V3 reach: yes for a German-language Home Assistant: services.py raises HomeAssistantError(translation_key=run_optimization_no_prices, translation_placeholders={entry_ids}); the de template names {entry_id}, which is never supplied. Exact rendering (raw braces or a fallback to the key) depends on HA's formatter, not measured here
- seam_rule enumerates: yes: PLACEHOLDER_PARITY covers every leaf string and EXC_PLACEHOLDER every services.py raise

## D4-s3-01: **verify** (medium; class new)

- metric: sv/de cells in pin_fail/save_fail whose failure line contains an en exceptions.*.message prefix
- V1 reproduced: 24 of 24; perturbed 0; null 0
- V2 independent: 10 err.message print sites, 0 translation_key reads
- attacks:
  - perturbation err_localize: 24 -> 0
  - null --err=plain: 0
  - V2: 10 sites print err.message (card.js lines 11038, 11082, 11091, 11641, 11660, 13332, 13437, 13937, 14173, 15098); 0 read translation_key
  - --err=ha is the harness's model of the websocket rejection; in HA core, async_get_exception_message formats in en, so err.message is English. This was not executed against real HA
- V3 reach: yes, provided HA's websocket error message is the en-formatted text (HA core behaviour, stated, not executed)
- seam_rule enumerates: yes: the grep lists every err.message site, matching V2's 10

## D4-s3-02: **verify** (low; class new)

- metric: headline rows whose numbers differ in first-line bottom or font-size by >0.5 px
- V1 reproduced: 12 of 108 cells' rows; perturbed 0
- V2 independent: full 900-cell grid: 12, all inside the six states
- attacks:
  - perturbation tile_nowrap: 12 -> 0
  - full grid: 12 misaligned rows, so no other state, viewport or language carries the defect (confined as claimed)
- V3 reach: yes: card at 375 px in German
- seam_rule enumerates: yes: the selector grep lists every tile/hl label and value rule

## D4-s3-03: **verify** (medium; class P9 (unfloored): confirmed)

- metric: cells with any visible HTML text run whose computed font-size < 12 px
- V1 reproduced: 78 cells (7 elements); perturbed 54; full grid 78
- V2 independent: 4 rules with a bare em font-size under the 12 px floor
- attacks:
  - perturbation tooltip_floor: 78 -> 54 (down)
  - null: the full 900-cell grid also gives 78, so 0 cells outside the six states
  - leave-one-out: with the tooltip floored, 54 cells remain from .sp-note and .layout-verdict alone, so the count is not one element's artefact
  - V2: .tooltip 0.78em, .tt-shared 0.85em, .sp-note 0.8em, .layout-verdict 0.85em, all without the max(12px, ...) wrapper the card uses elsewhere
- V3 reach: yes: card in a browser
- seam_rule enumerates: yes: the grep lists every bare em font-size

## D4-s3-04: **weaken** (cosmetic; class new (not P9: no token is missing and nothing is clipped or unfloored))

- metric: (theme, status role) pairs whose rendered colour set has more than one member
- V1 reproduced: 5; perturbed 3
- V2 independent: 6 contrast-documented *_READABLE constants separate from the --hpo-crit/ok/warn tokens, by design
- attacks:
  - perturbation one_error_colour: 5 -> 3 (down)
  - full grid: 5
  - V2: the second shade is a deliberate, separately named text tone. ERROR_READABLE #ca4c46 is commented 4.53:1 on #fff, SUCCESS_READABLE #24845d 4.63:1, and the _DARK variants carry their own ratios. These are text-on-surface tones; the pill and stripe colours are fills. Two of the 5 splits (warning #ffa600) are a non-text stripe against pill text
  - no reader-facing defect: every shade carries the same role and meets contrast, so this is a palette-consolidation preference
- V3 reach: yes: card in a browser
- seam_rule enumerates: yes: the grep lists every *_READABLE constant and status colour var

## D4-s3-05: **verify** (low; class new)

- metric: distinct computed font-sizes of visible HTML text off {12,13,15,18} px over the full grid (subset of 10 states: 14); distinct off-scale spacings: 45
- V1 reproduced: 14 (subset), 17 (full grid), spacing 45; perturbed 10
- V2 independent: 23 of 27 font-size expressions bypass the --hpo-text tokens
- attacks:
  - perturbation type_tokens: 14 -> 10 (down)
  - full grid: 17 sizes and 45 spacings, both exactly as claimed
  - null: the token-reading elements land on the scale
  - V2: 27 distinct font-size expressions in card.js; 23 are literal em/px/rem or max(12px, em), and only 4 are var(--hpo-text-*)
- V3 reach: yes: card in a browser
- seam_rule enumerates: yes: the grep lists every literal size and spacing declaration

## D4-s3-06: **verify** (low; class new (copy consistency))

- metric: en config/options step titles with a capitalised non-first word that is not all-caps and not a proper name
- V1 reproduced: en 6 of 41, sv 3 of 41
- V2 independent: en 6 of 41, sv 3 of 41, identical titles
- attacks:
  - perturbation sentence_titles: en 6 -> 0, sv 3 -> 0
  - null: 35 of 41 en titles uncounted
  - V2: the same 6 en titles (user, temperature, thermal, zones, dhw, weather_sensitivity) and 3 sv (user, thermal, zones)
- V3 reach: yes: the config flow's first-run pages
- seam_rule enumerates: yes: every config and options title in en and sv

## D4-s3-07: **weaken** (low; class new (copy consistency))

- metric: straight-quoted spans in de.json that quote prose (a UI label, an issue or button name, a word), excluding spans that quote a literal value the user types or a placeholder value
- V1 reproduced: de straight 27, typographic 95; en degree-without-sign 2
- V2 independent: de.json 25 straight (7 prose, 18 literal or placeholder values), 82 typographic; 2 bare-C in one blueprint
- attacks:
  - perturbation de_quotes: 27 -> 2 as stated
  - null: degree count 0 in de and sv
  - V2: 25 straight spans in de.json (finder 25), 82 typographic (finder 95 including card STRINGS)
  - 18 of the 25 quote literal input values or placeholder values ('06:00-08:30, 17:00-22:00', '22:00-06:00', 'Nov-Mar', '{entry_id}', '{windows}'), where straight quotes delimit a value the user types; only 7 quote prose labels
  - blueprint economy_mode_on_price_peak.yaml: '1.5 C' and '15 C' confirmed
- V3 reach: yes: rendered strings and the blueprint description
- seam_rule enumerates: yes: all de strings and the card's STRINGS

## D4-s2-51: **verify** (low; class new (inverse of P6: the producer writes a key no reader reads))

- metric: shipped languages whose config.step.user strings never reference a placeholder that async_step_user passes
- V1 reproduced: passed=1 unrendered=3 unpassed=0
- V2 independent: 0 text references of {tibber_info}, 1 code pass
- attacks:
  - perturbation --perturb: unrendered 3 -> 0
  - null control unpassed=0
  - V2: 0 JSON files reference {tibber_info}; config_flow.py passes it once (async_step_user)
- V3 reach: yes: every first-run setup page; HA ignores an unused placeholder silently, so the Tibber token hint never appears
- seam_rule enumerates: no: the harness checks async_step_user only, not every step's description_placeholders
