# D4 round 9: verifier V2 (independent lens), box G2-V2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` plus round-9 evidence (worktree `/home/claude/evid`, head `6f51db2c`).

Machine: 4-core Linux 6.18 container shared with other seats. CPython 3.14.0rc2 (`/home/claude/venv`), Node v22.22.2, Playwright 1.56.1 with its bundled Chromium, Liberation Sans.

Differences from the finders' boxes: venv, NODE_PATH and browser paths substituted as the brief says. Every number is a count, pixel or ratio, so none depends on load. thread_factor was 1.00 or 1.000 on every run.

Harnesses:
- `tools/audit/round9/D4/verify-v2/card_v2.mjs` (`--check contrast|menu|picker|layout|now`) uses its own mount, real Playwright input and its own metrics.
- `tools/audit/round9/D4/verify-v2/flow_v2.py` (`--check prefill|currency|escaped|zones|stepgrid|preset|quickmenu|icons|units`) uses independent enumerators.

Each check has its own in-memory one-line `--perturb`. Limits: no Home Assistant frontend, a stand-in `ha-card`, and HA's default light/dark theme tokens.

## Finder-harness re-runs

| harness | numbers | load1 |
|---|---|---|
| `s1/sweep.mjs` (targeted 12 states) | cells=144, contrast_instances=90, popup_out_cells=6, max_popup_viewport_out_px=9.7, option_indistinct_pairs=8, now_marker_collisions=24 | 2.56 |
| `sweep.mjs --perturb` | status_text_token → contrast 12; menu_clamp → popup 0; picker_wrap → options 0; now_temp_below → now 0 | 1.61–2.22 |
| `s1/layout_kbd.mjs` | pipes=12, pipes_click=12, pipes_keyboard=0, boxes_keyboard=0; `--perturb kbd` → 12 | 3.71 |
| `s2/*.py` | prefill 3/3/1/1 (twin 0), after_save 1/1/1 (null 2), currency 1 (static 2), escaped 4/1/9 (all files 6), zones 1/0, step_grid 8+4 (sliders 0), preset 6/4 per lang, quick_menu 1/1 (null 0), service_icons 12/12 (entities 0), unit_typography 8/8 | 0.67–1.40 |
| `s2/*.py --perturb` | every headline → 0 | ≤1.40 |

All reproduce the finders' numbers exactly.

## D4-s1-01: status text contrast. **Vote: verify, medium**
- **Metric:** (element, theme) pairs of the four status classes, reached by real Save clicks (arm, confirm ok, confirm fail) and a state update lowering the DHW ceiling. A pair fails when its WCAG ratio, from my own formula over the composited background, is below 4.5.
- **Result:** 6 of 8 below AA; min 1.96 (load1 5.3–5.8).

  | theme | failing runs | passing runs |
  |---|---|---|
  | light | warning 1.96, success 3.30, error 4.29, white on confirm 4.29 | none |
  | dark | error 3.97, confirm 4.29 | success 5.16, warning 8.69 |

- **Perturbation:** own fix (readable text token, `#b3261e` confirm fill) → 0 of 8.
- **Attacks:** dropping any single run leaves at least 5 failing. The states come from real clicks. Token values are HA's defaults. Severity is by consequence: the text is still legible.

## D4-s1-02: slot menu not clamped. **Vote: verify, medium**
- **Metric:** cells whose `.slot-menu`, opened by a real mouse down/up, ends more than 0.5 px beyond min(viewport, `.chartwrap` right).
- **Result:** 36 of 36 menus opened; 4 cells spill; max 54.3 px past the chart and 19.8 px past the viewport (375 px, sv, hot water, "Ta bort det här varmvattenpasset"). Null (mid-lane) 0 of 12. Own clamp → 0.
- **Reach attack:** at default zoom the last 25% of the lane is `rect.lane-past`; real taps there open no menu. The finder's 97% case came from calling `openMenu` directly.
  - The spill is reachable after two clicks on the zoom-in control (`.vc-in`).
  - At the last editable pixel at 375 px the menu is squeezed to 113 px and the button wraps (37.6–51.6 px tall).
- **Constraint on the fixer:** test with a real tap after zooming in.

## D4-s1-03: duplicate names in the picker. **Vote: verify, medium**
- **Metric:** option pairs with different text whose screenshot row crops differ in fewer than 8 pixels at the best ±1 px shift.
- **Result:** the two Vedpanna rows are identical (0 px differ) at 375 and 768 px, en and sv (4 cells). At 1280 px they differ by 43 px, which matches the finder's null control.
- **Perturbations:**
  - The finder's CSS wrap makes each option 43 px tall and the rows distinct (0 identical), so the finder's metric moves because the pixels move.
  - My own markup fix (entity id first) leaves 2, at 375 px only, because the id itself is cut there.
- **Severity:** filtering by the id suffix is a workaround.

## D4-s1-04: layout editor has no keyboard route. **Vote: verify, medium**
- **Metric:** Tab through every stop (15 per viewport). At each, press Delete, Backspace, Enter, Space, then separately ArrowRight, ArrowDown. Count stops after which the `[data-edge]` count fell or a `rect.setup-box` x,y attribute changed.
- **Result:** keyboard 0 of 12 pipes and 0 of 18 boxes; mouse 10 of 12 pipe midpoints remove a pipe. The 6 in-canvas Tab stops per viewport are all sensor-picker hit areas (`rect.setup-hit`).
- **Perturbation:** own tabindex plus Delete handler → 12.
- **Self-correction:** my first draft measured screen rects and read page scroll as box movement (4 false moves). It was rewritten on the SVG's own x,y and now reads 0.

## D4-s1-05: now label over the measured-now reading. **Vote: weaken, high → medium**
- **Metric:** pixels inked by both `text.now-label` and `text.now-temp`, each shown alone against a blank.
- **Result:** 24 of 24 live default-view cells overlap, up to 88 px. Null control (no measured sensor) 0. Own shift of now-temp → 0.
- **Why weakened:** both runs start with "now", about 1 px apart. The ink merges into a smeared "now" while "21.1 °C" stays legible, so no value is lost.
- **Not measured:** the second seam (view controls over the now label when panned).

## D4-s2-01: wizard pre-fill page labels. **Vote: verify, medium**
- **Metric:** keys `modbus_prefill.infer` returns when every role it reads is present, filtered by `_prefill_fits`, that have no `config.step.device_prefill.data` label.
- **Result:** 13 keys; 7 unlabelled in en, sv and strings.json alike:
  - compressor_freq_sensor
  - dhw_legionella_temperature
  - dhw_windows
  - heat_pump_max_power
  - mixing_valve_write_target_kind
  - silent_mode_windows
  - space_setpoint_unit
- **Refusal:** the real step returns `prefill_device_unreadable` for an unresolvable device, and it has no `config.error` text.
- **Controls:** options twin 0. `--perturb` → 0.
- **Reach:** Quick setup always leads to this page.
- **Constraint on the fixer:** cover all 7 keys, not the finder's 3.

## D4-s2-02: wood price shown in SEK. **Vote: verify, medium**
- **Metric:** field rows whose widget shows a currency code other than `resolve_currency(hass)`.
- **Result:** 1 of 4 money rows at NOK and at EUR; 0 at SEK (null). `--perturb` → 0.
- **Consequence:** `wood_fuel.py` uses the raw value against the electricity price in the instance currency, with no conversion. A SEK amount entered at a EUR install makes wood look about 11 times dearer.

## D4-s2-03: escaped characters in the DHW error. **Vote: verify, medium**
- **Metric:** text entries of `strings.json` and `translations/*.json` still containing a literal `\uXXXX` after JSON parsing.
- **Result:** 6 entries, 22 sequences, all `dhw_min_too_close`. A real config-flow DHW submit (min 53, setpoint 55) returns that key; the en text has 1 sequence and the sv text 9. `--perturb` → 0.
- **Inference:** the HA frontend is not local; its message formatter is inferred to print the backslash as ordinary text.

## D4-s2-04: zones page turns two-zone on. **Vote: verify, high**
- **Metric:** `ThermalParameters.from_config(flow._data).two_zone_enabled` after the real `async_step_zones` is submitted with its schema applied to `{}`.
- **Result:** 0 → 1. An empty or cleared submit stores 11 zone keys because the fields carry defaults.
- **Reach:** the expert path always passes through this page (`async_step_thermal` hands over to it), and nothing writes `two_zone_mode`.
- **Perturbation:** own fix (write two_zone_mode off) → 0.
- **Severity:** a single-zone house is planned with the two-zone model, against what the page says. High kept; the overview does say "two zones", so it is not fully silent.

## D4-s2-05: number fields off their step grid. **Vote: verify, low**
- **Metric:** box-mode fields whose shown value gives a non-integer (value − min) / step, in Decimal arithmetic.
- **Result:** 9 of 54 (config 8, matching the finder's 8 field for field; options 1, building_preset window_area). Step "any" → 0.
- **Not re-measured:** the finder's derived arm (4).
- **Inference:** that Home Assistant passes min and step to a native number input is not measured.

## D4-s2-06: overwrite warning missing on the zones page. **Vote: verify, low**
- **Result:** 6 of 10 derived fields per language sit on `thermal_model_zones`. The step passes the warning but the page text has no `{preset_warning}` placeholder. `thermal_model` shows it for its 4. `--perturb` → 0.

## D4-s2-07: quick setup offered again after quick setup. **Vote: verify, low**
- **Result:** the menu after quick setup plus an empty device pick lists `quick_setup`, and lists it first (1, 1). Own flag fix → 0.
- **Reach:** the second device_prefill submit also returns to finish_setup, so a real device does not change this.

## D4-s2-08: services without icons. **Vote: verify, low**
- **Result:** 12 of 12 services the real `async_register_services` registers have no icons.json entry; the 12 `services.yaml` keys agree. `--perturb` → 0.

## D4-s2-09: bare units in help text. **Vote: verify, low**
- **Result:** 9 help texts per language across the whole file, all field help texts, against the finder's 8 rendered. My extra is `user_sensors` `solar_radiation_entity`, which appears both top-level and inside `sections.solar`. `--perturb` → 0.

## Commands
```
T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/claude/venv/bin/python tests/plan_view.py >/dev/null
HPO_PLANDATA=$T/plandata.json NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tools/audit/round9/D4/verify-v2/card_v2.mjs --check <contrast|menu|picker|layout|now> [--perturb] [--perturb-css-wrap]
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D4/verify-v2/flow_v2.py --check <name> [--perturb] [--currency X]
```
