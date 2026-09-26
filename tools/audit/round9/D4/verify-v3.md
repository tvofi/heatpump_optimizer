# D4, verifier V3 (reach and class), round 9, box G2-V3

Baseline 1936d5ca (evidence tree at 6f51db2c). Machine: 4-core Linux container shared with two other sub-seats. Every number below is a count or a ratio, so contention does not affect it; load1 is quoted anyway.

## Own harnesses (under `tools/audit/round9/D4/verify-v3/`)

**`realha_flows.py`**
- Runs under real `homeassistant` 2026.2.3 without `tests/hastub`; numpy and scipy borrowed from the gate venv.
- Real components: `core.HomeAssistant`, the loader's custom_components discovery, `ConfigEntries` and the flow/options managers (each posted input goes through real `data_schema(user_input)` validation), device/entity registries, `helpers.translation`, `helpers.icon`, and `voluptuous_serialize` with `cv.custom_serializer` (the frontend's wire format).
- The frontend's form pre-fill is emulated from HA frontend's `computeInitialHaFormData` rule.
- Stubbed: `async_process_deps_reqs` (would pip-install and set up `http`); `ConfigEntries.async_setup` (entry stored, coordinator not started); a `typing.ByteString` shim (mashumaro does not import on CPython 3.14).
- Output: `realha_flows.out.txt`, plus `realha_flows.perturb-zones.out.txt`.
- `thread_factor` 1.07 because real HA runs its I/O on executor threads. Every RESULT is a count.

**`card_probe.mjs`**
- Drives the card with real Playwright mouse and keyboard input (the finder's harness called `openMenu` and `_onCardClick` directly).
- Theme and status tokens are the real HA frontend bundle's. Own WCAG formula and geometry code.
- Output: `card_probe.out.txt`.

**`layout_focus.mjs`**
- Opens the layout editor with real clicks, presses Tab 80 times, counts focus stops on pipes, boxes and ports. `--perturb` makes the pipes focusable: 0 → 8.
- Output: `layout_focus*.out.txt`.

**`frontend_extracts.txt`** — extracts from `home-assistant-frontend==20260128.6`, the version core 2026.2.3 pins:
- `--error-color #db4437`, `--success-color #43a047`, `--warning-color #ffa600`: one definition each; dark mode does not override them.
- Card background `#ffffff` light, `#1c1c1c` dark.
- `ha-card :host` has no overflow clip, so the finder's stand-in `ha-card` is faithful.
- `ha-selector-number` renders `<ha-textfield type=number .min .max .step autoValidate>`, spinner shown in box mode.
- The frontend's icon cache has a `services` category.

**Step 1 (finder harnesses re-run)** — all 14 reproduce exactly.
- s1 sweep: `cells=144 contrast_instances=90 popup_out_cells=6 option_indistinct_pairs=8 now_marker_collisions=24`, load1 2.89, tf 1.00.
- `layout_kbd`: `pipes_keyboard=0 boxes_keyboard=0 pipes_click=12`, load1 2.68.
- The ten s2 harnesses reproduce every claimed RESULT, load1 0.38–0.79, tf 1.000. `step_grid` needed `PLAYWRIGHT_BROWSERS_PATH` pointed at this box's browsers.

**Attacks not repeated per finding:** contention — every value is a count; gate mode — no mutation claims; null controls — present in every record and re-observed in step 1.

---

### D4-s1-01 — status-token text below AA

- Step 1: 90 instances, 72 cells.
- Own metric (seam lines × real tokens): the seam rule prints 8 lines, 6 text-bearing. Below 4.5:1 on the light card 6 of 6; dark 4 of 6.
- Ratios (own formula): error 4.29 light / 3.97 dark; success 3.30 / 5.16; warning 1.96 / 8.69; white on the error fill 4.29.
- A real click on `.wi-save` arms the confirm button in 12 of 12 cells, computed `rgb(255,255,255)` on `rgb(219,68,55)` = 4.29.
- Grid attack: 90 instances come from 13 distinct text runs; 36 are one "+0.51 SEK" delta repeated. Dropping it leaves 54. The per-rule count (6 light, 4 dark) stands without the grid.
- Reach: real. Tokens verified in the real frontend bundle; the pin/save result texts read `response.response.applied`, the real `{context, response}` shape of `callService(..., returnResponse)` with `{"applied": ...}` from `services.py:919`.
- Severity: medium earned (AA failures on what-if result, error and destructive-confirm texts).
- Seam rule: 8 lines; enumerates all 11 `var(--error|success|warning-color` uses (the other 3 are a stroke and two borders, not text). It also catches `.wi-remove:hover` (`:3799`, error text 4.29/3.97), which the finder's sweep never counted. **All.**
- Class: P9 confirmed.
- **Vote: verify, medium.**

### D4-s1-02 — slot menu unclamped

- Step 1: 6 cells, 9.7 px past the viewport.
- Reach attack: the finder's anchor (97% of the default window) is reached only by calling `LaneEditor.openMenu` directly. A real tap there lands on `rect.lane-past`, which has no `data-channel`, so no menu opens; right-click has the same guard; the keyboard path anchors inside the editable span.
- Own metric over 36 real-tap openings:
  - Rightmost editable point, unzoomed: 0 spill past the chart; the menu is squeezed to the wrapper edge (`menu ..340.5 = wrap ..340.5`).
  - After three real zoom-in clicks, tap at 97%: 2 openings spill, both sv-SE at 375 px, 18.2 px past the chart, 0.0 px past the viewport. The English menu at the same tap is squeezed to a 64 px column.
  - The DHW lane is never editable at 97% after zoom, so the finder's cut DHW label ("Lägg till ett varmvattenpa", 9.7 px off the viewport) is not reproduced by real input.
- Reach: real (same JS); magnitude smaller than claimed; viewport overflow unreached in this fixture.
- Severity: weaken to low — menu stays operable; label overflows the chart but stays on screen.
- Seam rule: 4 lines; enumerates both pointer-anchored pop-ups (menu `:7993`, tooltip `:11487`); other absolutely positioned elements are CSS-anchored. **All.**
- Class: P2 confirmed (the tooltip clamps; its sibling menu does not).
- **Vote: weaken, low.**

### D4-s1-03 — identical options in the setup picker

- Step 1: 8 cells.
- Own metric (real click on the wood-tank box, real typing "vedpanna", canvas `measureText` against the select's content box): twin pairs in 8 of 10 cells; 375 and 768 px, both themes and languages show them; 1280 px shows 0 (null control holds).
- Reach: real. HA names a colliding object id `_2` and keeps the same friendly name.
- Severity: medium stands (wrong sensor assignable; the box then shows its live reading).
- Seam rule: 11 lines; covers both `<select>` in the card (`.sp-select`, `.wi-win-days`, the latter with short fixed labels). **All.**
- Class: correct "new" → P9 (distinguishing text clipped by its container box).
- **Vote: verify, medium.**

### D4-s1-04 — layout editor has no keyboard route

- Step 1: `pipes_keyboard=0`, `boxes_keyboard=0` (click 12).
- Own metric: editor opened by real clicks, 80 real Tab presses at 375 and 1280 px: 0 stops on any of 8 pipes or 12 boxes. Stops are the tabs, close, the toggle, tidy, a button and one entity-row `rect.setup-hit` (opens the picker; not a layout edit). `--perturb`: 8.
- Reach: real. Severity: medium stands (WCAG 2.1.1 on topology edits; only out-of-card route is the `apply_topology` service).
- Seam rule: **partial.** 5 lines: canvas `pointerdown`/`click` delegation (pipes, ports, boxes) and the pipe markup. It matches the lane editor's `slot-handle data-edge` (`:7848`) by accident and does not reach the other pointer-only affordances the same sweep counts (`pointerOnly_instances=204`).
- Class: new, confirmed — pointer-only editing affordance with no keyboard equivalent.
- **Vote: verify, medium.**

### D4-s1-05 — now label over the measured-now reading

- Step 1: 24. Own metric (real payload, inline default view): overlap in 12 of 12 cells.
- Reach: real. `sensor.py:304` sets `entity_id = sensor.heat_pump_optimizer_indoor_temperature_optimizer`, exactly what the card derives; published whenever an indoor entity is configured.
- Severity: the collision is the word "now" printed twice, offset 3 px by 1 px (`evidence_now_collision_375.png`); "21.1 °C" stays legible. Cosmetic, no reading lost. Weaken high to low.
- Seam rule: **partial.** 4 lines (`now-label`, `now-temp`, the estimated-prices label, `viewctl`); misses the axis-unit titles placed on the same edge by `plotT - 5.2*…` (`:6085`).
- Class: correct P2 → P9 (no guard predicate exists at either seam; a card-geometry overlap found by P9's geometry sweep).
- **Vote: weaken, low.**

### D4-s2-01 — device pre-fill page shows raw keys

- Step 1: 3 unlabelled fields and 1 untranslated error, en and sv.
- Real HA: `quick_path_reaches_device_prefill_real=1`, `prefill_unlabelled_real_en/sv=3`, `prefill_error_untranslated_real_en/sv=1` (real translation loader, `component.heatpump_optimizer.config.*`).
- Reach: stronger than claimed. The recommended "Quick setup" path enters `device_prefill` unconditionally on a fresh install (`config_flow.py:2537`); the finder used the opt-in route.
- Severity: medium stands.
- Seam rule: **partial.** It enumerates one fixture device: 3 of the 9 content keys the options twin carries and config lacks, and 1 of the 3 missing `config.error` keys. The other two missing error keys are `flow_target_needs_two_zone` and `silent_mode_window_too_short`, both returned by `_prefill_errors`. The universe the rule names is stated, not iterated.
- Class: P6 confirmed.
- **Vote: verify, medium.**

### D4-s2-02 — wood price shows SEK to a non-SEK install

- Step 1: 1 of 4 money fields; static fixed-currency texts 2.
- Real HA (`hass.config.currency=EUR`, real serializer): `options_money_fields_real=4`, `options_foreign_currency_units_real=1` (`building.wood_price_sek_m3: SEK/m³`).
- Reach: real. Severity: medium stands (a EUR user is asked for a SEK figure that `wood_fuel` compares against the EUR electricity price).
- Seam rule: **partial.** Covers rendered option units, `services.yaml` and en.json only; misses sv.json's `services.simulate_plan.fields.wood_price_sek_m3.description` ("…i SEK per debiterad kubikmeter").
- Class: P8 confirmed.
- **Vote: verify, medium.**

### D4-s2-03 — escaped `°` in the hot-water minimum error

- Step 1: 4 texts; 1 garbled character en, 9 sv.
- Real loader: `escaped_seq_{config,options}_en_real=1`, `_sv_real=9`; `escaped_leaves_all_real_loader=4` (only translations/ is loaded at runtime; the finder's 6 includes strings.json).
- The real frontend receives the backslash through websocket JSON. ICU MessageFormat does not treat a backslash as an escape, so the frontend display step remains an inference.
- Severity: validation-only text, en readable — weaken to low.
- Seam rule: walks every leaf; card JS and `services.yaml` hold no `\\uXXXX`. **All.**
- Class: new, confirmed — translation leaf double-escaped so parsing yields a literal escape.
- **Vote: weaken, low.**

### D4-s2-04 — expert zones page turns two-zone on

- Step 1: expert 1, describe 0.
- Real FlowManager, schema-validated posts: `two_zone_expert_real=1`; `two_zone_expert_cleared_fields_real=1` (clearing every zone field does not help: real voluptuous refills defaults); `two_zone_describe_real=0`, `two_zone_quick_setup_real=0`, `two_zone_finish_now_real=0`. `--perturb-zones`: all 0.
- Reach: real.
- Severity: high not earned by a measured consequence — no plan or cost effect was taken, the setup overview shows "House: two zones" before creation, and the path is the non-recommended branch. Weaken to medium.
- Seam rule: **partial.** Walks 2 of 4 first-run paths; my real-HA walk of the other two finds no further instance.
- Class: P2 confirmed (`quick_setup.derive` guards two-zone; the zones page does not).
- **Vote: weaken, medium.**

### D4-s2-05 — number fields off their own step grid

- Step 1: 8 defaults and 4 derived off-grid; 0 sliders.
- Real wire format: `wire_offgrid_defaults_box_mode=8` on the config-flow thermal and zones pages. The real `ha-selector-number` passes `.min/.max/.step` to `type=number autoValidate` with the spinner on, closing the finder's stated inference boundary: native `stepMismatch` and spinner steps apply in real HA.
- Severity: low stands (submission not blocked). Seam rule: **all.**
- Class: new, confirmed — selector minimum off its own step grid.
- **Vote: verify, low.**

### D4-s2-06 — overwrite warning missing on the zones page

- Step 1: 6 unwarned per language.
- Real options manager, armed two-zone entry: `thermal_model_zones` `derived_unwarned_..._real_en/sv=6` (placeholder returned, not shown); `thermal_model` warned 4. Real loader: `zones_desc_has_placeholder_real=0`.
- Seam rule: derived keys render only on those two option pages (`_F` rows at `:1657–1665`). **All.**
- Class: P2 confirmed.
- **Vote: verify, low.**

### D4-s2-07 — quick setup returns to the identical menu

- Step 1: 1. Real HA, accept hand-back (`:2444`): `menu_identical_after_quick_real=1`.
- Seam rule: **partial.** The harness walks the decline hand-back (`:2392`) and the first menu (`:2313`), not the accept hand-back (`:2444`), which my walk shows also yields the identical menu.
- Class: new, confirmed — a state-blind menu re-offers a completed path.
- **Vote: verify, low.**

### D4-s2-08 — no service icons

- Step 1: 12 of 12. Real `icon.async_get_icons(hass, "services")` returns None for the domain: `services_without_icon_real=12`; the entity block is present.
- Reach: real (the frontend requests service icons by category). Seam rule: **all.**
- Class: new, confirmed.
- **Vote: verify, low.**

### D4-s2-09 — "45 C" / "W/m2" in help texts

- Step 1: 8 per language. Real loader: `bare_unit_data_descriptions_real=9` per language; `user_sensors.solar_radiation_entity` exists both flat (reconfigure) and sectioned (fresh setup): 9 leaves, 8 distinct rendered fields.
- Seam rule: no other translation leaf, nothing in `services.yaml`, the card only in a comment. **All.**
- Class: new, confirmed.
- **Vote: verify, low.**

---

Counts: verify 10, weaken 4 (s1-02, s1-05, s2-03, s2-04), refute 0, unresolved 0. No production or test file edited; all perturbations in memory. The frontend wheel was downloaded into a scratch directory outside the tree.
