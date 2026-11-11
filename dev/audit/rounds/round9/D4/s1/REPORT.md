# Round 9 — D4-s1 (UI/UX, the card) — finder report

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), export `/home/claude/audit-r9-baseline`, box B10
(4-core Linux container, Node v22.22.2, Playwright 1.56.1, Chromium 141.0.7390.37). Cells: D4.M1, D4.M2, D4.M3 on
`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` (the only file `www/**` resolves to).

Exposure: none. No `docs/`, no GitHub, nothing under `tools/audit/round3..8` was read. `tests/card_browser.mjs` and
`tests/card_drift.mjs` were read as the brief's reuse list; their comments cite earlier finding ids (context only).

## Method

- `sweep.mjs` + `measure.js`: every `tests/card_drift.mjs --list` state (39 DOM states; `editor_schema` is not DOM and is
  covered by `editor.mjs`) re-driven against the real DOM in Chromium, plus `x_*` states STATES never reaches
  (status-text outcomes via real clicks, the slot menu opened near the right edge, the live default view with the
  measured indoor sensor present). Grid: 375x812, 768x1024, 1280x800 x HA default light/dark tokens x en/sv-SE x
  normal / coarse pointer (in-page matchMedia stub, the card's own predicate) / reduced motion; frozen clock
  (plan_view.py payload, first DHW step + 6 h). Card tile = viewport - 16 px. Per cell: text overflow beyond the nearest
  clipping ancestor less its scroll reach, text-box overlap, WCAG AA contrast of every visible text run (composited over
  ancestor backgrounds and preceding SVG fills), hit targets (24 px / 44 px coarse, with the 2.5.8 spacing exception),
  pointer-only and nameless targets, listbox option truncation, pop-up containment, console errors; on light/en/normal
  cells a real-Tab keyboard walk (reachability, visible focus indicator) and a hover pass with Chromium's layout-shift API.
  Full grid: 1626 cells, `sweep_full.log` (state list at launch: 47; the `x_live_default*` states were added after).
- `editor.mjs`: the visual editor (`HeatpumpOptimizerCardEditor`) through its ha-form contract (D4.M2 for this file).
- `layout_kbd.mjs`: keyboard operability of the setup page's layout editor (real Tab / Enter / Delete / arrows).
- `hover_diag.mjs`: which elements move on hover (explains the layout-shift API's number).
- Font: Liberation Sans (no Roboto on the box). No Home Assistant frontend: `ha-card` is a stand-in with ha-card's
  background/border/colour; `ha-form` is not rendered, so editor rendering is inferred from schema and labels.

Canonical targeted command (all five sweep-backed numbers; ~90 s):

```
T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /home/claude/venv314/bin/python tests/plan_view.py >/dev/null && \
HPO_PLANDATA=$T/plandata.json NODE_PATH=/home/claude/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/root/.cache/pw-browsers \
  node tools/audit/round9/D4/s1/sweep.mjs --no-keys --modes normal \
  --states x_pin_ok,x_pin_fail,x_save_ok,x_save_fail,x_dhw_clamped,x_save_confirm,draft_dirty_menu_open,x_menu_right_edge,x_menu_right_edge_dhw,picker_open_filtered,x_live_default,x_live_default_expanded \
  [--perturb none|status_text_token|menu_clamp|picker_wrap|now_temp_below]
```

| RESULT (144 cells) | none | status_text_token | menu_clamp | picker_wrap | now_temp_below |
|---|---|---|---|---|---|
| contrast_instances | 90 | **12** | 90 | 90 | 90 |
| popup_out_cells | 6 | 6 | **0** | 6 | 6 |
| option_indistinct_pairs | 8 | 8 | 8 | **0** | 8 |
| now_marker_collisions | 24 | 24 | 24 | 24 | **0** |

Each perturbation moves its own metric and no other: the cross-arms are the specificity control.

## Findings

### D4-s1-01 — Status text coloured by HA's status tokens fails WCAG AA (medium, bug, P9)

Every result/warning line the what-if panel and today's-slots section print in `--success-color`, `--error-color` or
`--warning-color`, and the armed Save button (white on `--error-color`), is below 4.5:1 on HA's default light theme; the
error text is also below it on the dark theme. Ratios are token-determined, identical in every cell:

| site | light (#fff) | dark (#1c1c1c) |
|---|---|---|
| `.wi-hint.wi-warn` (DHW minimum silently lowered) | **1.96:1** (10.2 px at 375) | passes |
| `.cheaper` (pinned / saved result) | 3.30:1 | passes |
| `.dearer` (cost delta, apply/save errors) | 4.29:1 | 3.97:1 |
| `.wi-save.confirm` (white on error red) | 4.29:1 | 4.29:1 |

Canonical command: `contrast_instances=90` (72 cells) -> 12 under `status_text_token` (text rules on
`--primary-text-color`; the 12 left are the confirm button's filled background, a second seam of the same property).
Property: every text run whose colour or backing fill resolves from a status token clears 4.5:1 against the card on HA's
default light and dark themes. Seams: `grep -nE "(color|background): var\(--(error|success|warning)-color" <card>` (8).
For the fixer: the card's own comments establish no single constant clears 4.5:1 on both #fff and #1c1c1c.

### D4-s1-02 — The lane slot menu is not kept inside its chart; Swedish labels are cut at the dialog edge (medium, bug, P2)

`LaneEditor.openMenu` places the menu at the raw tap / right-click / keyboard point (`menu.style.left = clientX - rect.left`)
with no clamp, while its sibling pop-up, the hover tooltip, clamps (`tt.style.left = min(max(0, place), rightLimit)`).
Opened at 97 % of the window: 375 px sv - the DHW menu runs 44.2 px past its chart and 9.7 px past the viewport,
label shown as "Lägg till ett varmvattenpa..."; 375 px en - the same menu is squeezed into a 64 px column (147 px when
opened mid-chart). `popup_out_cells=6` -> 0 under `menu_clamp` (one line after `host.appendChild(menu)`).
Null control: 1280 px en and every mid-chart opening, 0.

### D4-s1-03 — The setup picker's two identically named sensors are indistinguishable below 1280 px (medium, bug, new)

`SetupPage.pickerModel` labels every option "friendly - entity_id" precisely so colliding auto-names can be told apart,
but the `<select size=8>` sits in a pop-up capped at `max-width: 90%`, and a Chromium listbox neither wraps nor scrolls
sideways. At 375 px (box 190 px) both vedpanna options show "Vedpanna temperatur - sensor.v"; at 768 px (322 px)
"... - sensor.vedpanna_temperatur_te"; the `_2` that separates them is never visible. `option_indistinct_pairs=8`
(375/768 x light/dark x en/sv) -> 0 under `picker_wrap` (`.sp-select option { white-space: normal; overflow-wrap: anywhere }`).
Null control: 1280 px, 0. Assign writes the configuration and reloads the integration.

### D4-s1-04 — The layout editor's edits have no keyboard route (medium, bug, new)

In editing mode a pipe is removed only by `LayoutEditor.onClick` on a bare `<path data-edge>` (no tabindex, no name,
a 3.5-unit stroke: 6.6-38 px tall under a coarse pointer), and pipes are drawn and boxes moved only by pointer drags on
the canvas. `layout_kbd.mjs` (375/768/1280): `pipes=12`, `pipes_click=12` (control: the action exists),
`pipes_keyboard=0`, `boxes_keyboard=0` of 18; under `--perturb kbd` (tabindex on the pipe markup + a canvas keydown
forwarding Enter/Delete to `onClick`) `pipes_keyboard=12`. Keyboard users reach Save/Undo/Tidy only (WCAG 2.1.1;
removing a pipe is a discrete action, not path-dependent).

### D4-s1-05 — The now marker's label collides with the measured-now reading on every live default view (high, bug, P2)

`renderChart` draws `text.now-label` at (nx+3, plotT+font+1) and, since #1495, `text.now-temp` at (plotL+6, plotT+font)
with no shared placement; the default window starts at now, so nx ~ plotL and the two print over each other ("nnoww
21.1 °C", `evidence_now_collision_375.png`). The rig's `planStates` never carries the measured indoor sensor, so no
STATES default view renders it; `x_live_default*` add `withActuals`, which a real install has.
`now_marker_collisions=24` (inline + dialog, 3 viewports x 2 themes x 2 languages) -> 0 under `now_temp_below`.
Second seam of the same property in the full grid: the view controls' reset button over `now-label` (history_panned, 10 cells).
Seams: `grep -nE '<text class="now-|y="\$\{plotT \+ font|class="viewctl' <card>`.

## Non-findings (held)

- Keyboard: 132 walked cells, 3246 focusables, 0 unreached, 0 without a visible focus indicator (`sweep_full.log`).
- Hover: `hover_diag.mjs` `moved_non_overlay=0` over 48 hovers (`moved_overlay=194`); `--perturb shift` -> 343. The
  layout-shift API's 0.03-0.065 per expanded cell is the tooltip following the pointer.
- Reduced motion: `motion_elements_normal=9` -> `motion_elements_reduced=0`.
- Unreachable text: `overflow_instances=0`, `hscroll_cells=0` over 1626 cells; `ellipsized=0`; `console_error_cells=0`.
- Hit targets: every HTML control clears 24 px (44 px coarse); the sub-floor residue is lane slot targets (boxed in by
  design) and the layout pipes (D4-s1-04).
- i18n: en/sv dictionaries 286/286 keys; the only English runs in sv renders are data (fixture slot labels, entity ids,
  the narrative's own `language: en`) and "Plan" (identical in Swedish).
- Editor (`editor.mjs`): 17 fields (9 top-level), `labels_raw_en=0`, `labels_raw_sv=0`, `roundtrip_extra=0`,
  `roundtrip_throw=0` at every selector extreme; `helpers=0` (no help text; noted, not claimed); `--perturb helper` -> 17.
- Disproved lead (harness gap): axis unit titles vs top tick labels overlap by 2-5 px as glyph boxes (1300+ instances);
  the ink does not touch (screenshots; `tests/card_browser.mjs`'s ink test). The box metric over-reports stacked SVG text.

## Unfinished

- D4.M1: keyboard / screen-reader access to the chart's per-time values (the hover tooltip) not measured.
- D4.M3: headline-number alignment and a type-scale metric not built; observed only: dialog help text renders at
  9.1-10.2 px at 768/1280 beside 19.7 px axis ticks.
- D4.M2: install-to-first-plan step count is the config flow's (D4-s2's cells), not measured here.

## Harnesses

`sweep.mjs` (+ `measure.js`), `editor.mjs`, `layout_kbd.mjs`, `hover_diag.mjs`; `crop_now.mjs` makes the evidence PNG.
Screenshots in `shots/` (375 px all states/themes/languages, 1280 px light en), taken before the keyboard walk.
