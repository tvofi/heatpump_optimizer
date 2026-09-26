# Round 9, seat D4-s2 (D4)

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Rendered by the B9 box thread from this seat's report.json, which is the authoritative record: the seat's own file tool refused to write a .md report.

## Exposure
none: no docs/, no GitHub, no earlier-round evidence read (tools/audit/round3..round8 not opened; only tools/audit/round9/BASELINE.md for the Chromium path)

## Coverage
- D4.M1: spot. My cells hold no card file (the card is D4-s1's). The browser part that applies to them was run: Chromium 1194 headless via tests/pwlane's lock measured native number-input validity for all 92 rendered NumberSelectors (step_grid.py). Viewports, themes, tab order and contrast apply to the card only and were not measured by this seat.
- D4.M2: deep. All 14 initial-flow and 25 options-flow pages rendered through the real steps (flow_rubric.py): field counts, sections, label/help coverage en+sv, placeholders, three first-run paths walked to create_entry; error keys cross-checked per flow namespace (prefill_config_strings.py, escaped_text.py); defaults/ranges/steps (step_grid.py); the expert path's stored result (zones_default.py); pre-fill page (prefill_*.py); menus (quick_menu.py). Config-flow rendering is inferred from schema and strings: there is no Home Assistant frontend locally.
- D4.M3: deep. Unit/currency consistency across rendered fields (currency_units.py, unit_typography.py), text encoding of every translation leaf (escaped_text.py), icon coverage of services vs entities (service_icons.py), warning placement across sibling pages (preset_warning.py).

## Findings

### D4-s2-01 (medium, D4.M2, class P6): Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error

On the config flow's device_prefill page, a name-matched pump yields 3 rendered fields (compressor_freq_sensor, dhw_min_temperature, dhw_legionella_temperature) with no label or help in config.step.device_prefill, and the page's own refusal key prefill_device_unreadable has no text in config.error, in both en and sv; the options twin page resolves all of them.

Mechanism: async_step_device_prefill renders modbus_prefill.infer keys through _prefill_schema/_prefill_row (the options registry) and returns {'base':'prefill_device_unreadable'}, but only the options namespace (options.step.modbus_prefill, options.error) carries the texts; config.step.device_prefill.data has 8 keys, the options twin 19. name_match.ROLE_FILTERS reaches compressor_freq_sensor, r405 and r406 by name, which the config page never labelled. The same reuse renders the options-only after_save control on the wizard page, where both of its choices lead to the same finish_setup menu and the choice is stored into the created entry (prefill_after_save.py: config_distinct_destinations=1, after_save_leaks_into_entry=1; options null control 2).

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/prefill_config_strings.py` gives 3 unlabelled + 1 untranslated error per language (en, sv) (count); harness tools/audit/round9/D4/s2/prefill_config_strings.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_device_prefill
- Perturbation: --perturb: copy options.step.modbus_prefill data/data_description and options.error texts into config.step.device_prefill / config.error (the translation fix), in memory (expected to_zero, observed 0 unlabelled, 0 no-help, 0 untranslated errors in en and sv)
- Metric: Rendered field keys of the config device_prefill preview without config.step.device_prefill.data label, plus returned error keys without config.error text, per language file.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/prefill_config_strings.py` gives options_twin_unlabelled=0, options_twin_untranslated_errors=0. the same keys resolve in the options namespace the options flow reads
- Property: Every field key the config flow's device_prefill step renders, and every error key it returns, resolves in the config namespace (config.step.device_prefill.data/data_description, config.error) of every shipped language, and every control on it acts in the config flow.
- Seam rule: tools/audit/round9/D4/s2/prefill_config_strings.py (enumerates the rendered/returned keys of the page) together with tools/audit/round9/D4/s2/prefill_after_save.py; the key universe is modbus_prefill.infer's output keys (options.step.modbus_prefill.data less the page's own controls)
- Proposed fix scope: strings.json + translations/en.json, sv.json: add the modbus_prefill-reachable keys (at least compressor_freq_sensor, dhw_min_temperature, dhw_legionella_temperature, and every key infer can return) and prefill_device_unreadable (and the _prefill_errors keys flow_target_needs_two_zone, silent_mode_window_too_short, dhw_windows_day_selector if reachable) to the config namespace; drop CONF_AFTER_SAVE from the config-flow preview schema; add a test that walks the config preview with a name-matched device and resolves every rendered key in config.*

### D4-s2-02 (medium, D4.M2, class P8): Wood price field shows 'SEK/m³' to a non-SEK install while its sibling money fields follow the instance currency

With Home Assistant's currency set to EUR, 1 of the 4 money fields the options flow renders (building.wood_price_sek_m3) displays the unit SEK/m³, while compressor_replacement_cost, grid_fee_fixed and contract_fixed_price display EUR.

Mechanism: The wood-price row is built at import with the literal _number(0, 10000, 10, 'SEK/m³'), whereas its siblings are _ByHass(lambda hass: _number(..., resolve_currency(hass))). wood_fuel compares the entered figure against the electricity price in the instance currency, so the label asks for a different currency than the arithmetic uses. The static services.yaml selector unit (simulate_plan.wood_price_sek_m3: SEK/m³) and the service field's description ('in SEK') carry the same fixed currency (static_fixed_currency_texts=2).

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/currency_units.py` gives 1 of 4 money fields (count); harness tools/audit/round9/D4/s2/currency_units.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_building (row _OPTION_FIELDS[wood_price_sek_m3]) against currency:resolve_currency
- Perturbation: --perturb: the wood-price row's widget becomes _ByHass(lambda hass: _number(0, 10000, 10, f'{resolve_currency(hass)}/m³')) in memory (expected to_zero, observed 0)
- Metric: Rendered options-flow NumberSelectors whose unit_of_measurement names a currency code other than resolve_currency(hass), hass currency EUR.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/currency_units.py --currency SEK` gives 0. at the currency the literal happens to fit, the count vanishes
- Property: Every money unit the flows and service descriptions show is the instance currency from resolve_currency(hass), or names no currency at all.
- Seam rule: tools/audit/round9/D4/s2/currency_units.py (enumerates every rendered money unit across all option pages, plus the static services.yaml/translation texts naming a currency code)
- Proposed fix scope: config_flow.py wood-price row via _ByHass/resolve_currency; services.yaml unit and the simulate_plan field description without a fixed currency

### D4-s2-03 (medium, D4.M3, class new): The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv)

The dhw_min_too_close error both flows return is stored double-escaped, so after JSON parsing the shown text contains 1 literal '\u00b0' sequence in en and 9 literal '\u00XX' sequences in sv, in config.error and options.error alike (4 texts reached, 6 leaves across strings.json/en.json/sv.json).

Mechanism: strings.json and translations/*.json hold "\\u00b0C" (an escaped backslash) instead of the character; json.loads yields a backslash-u sequence, and the frontend's ICU MessageFormat does not treat a backslash as an escape, so it is printed verbatim (inference: no HA frontend here).

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/escaped_text.py` gives 4 error texts reached (config+options x en+sv); 1 garbled char en, 9 sv (count); harness tools/audit/round9/D4/s2/escaped_text.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_dhw and HeatPumpOptimizerOptionsFlow.async_step_hot_water (errors returned for min 53 / setpoint 55)
- Perturbation: --perturb: decode the literal escapes in the loaded translation texts (write the characters), in memory (expected to_zero, observed 0)
- Metric: Error texts the flows return for the DHW minimum/setpoint pair whose displayed string (after json.loads) matches \\u[0-9a-fA-F]{4}, per flow and language.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/escaped_text.py` gives escaped_other_error_texts=0. every other error text of both flows is clean
- Property: No shipped translation leaf contains a literal backslash-u escape after JSON parsing.
- Seam rule: tools/audit/round9/D4/s2/escaped_text.py (RESULT escaped_texts_all_files enumerates every leaf of strings.json and translations/*.json)
- Proposed fix scope: strings.json, translations/en.json, translations/sv.json: the two dhw_min_too_close leaves each; a lint in the translation checks for \\u sequences

### D4-s2-04 (high, D4.M2, class P2): Expert setup: the zones page says 'leave defaults if you don't need two-zone' and leaving them turns two-zone on

Walking the initial flow's 'Enter thermal values directly' path and submitting every page as pre-filled creates an entry that ThermalParameters.from_config reads as two_zone_enabled=True (1), while the describe path at the same defaults reads False (0).

Mechanism: async_step_zones declares the zone fields vol.Optional(..., default=DEFAULT_...), so the frontend posts them and voluptuous refills them even when cleared; the step stores them with self._data.update(user_input). ThermalParameters.from_config's 'auto' two_zone_mode infers two-zone from the presence of any of those keys, and the initial flow never writes two_zone_mode. quick_setup.derive guards the same fact explicitly (writes two_zone_mode on/off, its comment: adding zone keys 'is what silently flips a house to 2-zone'); the zones page, its sibling seam, does not. The page description promises the opposite. The overview then says 'House: two zones' for a single-zone house; the only way back is the options flow's two_zone_mode, which the page never mentions.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/zones_default.py` gives 1 (count (two_zone_enabled of the created entry)); harness tools/audit/round9/D4/s2/zones_default.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_zones, read through thermal_model:ThermalParameters.from_config
- Perturbation: --perturb: in async_step_zones, store only zone values that differ from the page's own defaults (one-line edit applied to the module source in memory) (expected to_zero, observed 0)
- Metric: two_zone_enabled (0/1) of the entry created when every page of the expert path is submitted exactly as pre-filled.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/zones_default.py` gives two_zone_describe_defaults=0. the path without the zones page stays single-zone at the same defaults
- Property: No first-run path turns the two-zone model on unless the user answers that the house has two zones; submitting any page unchanged leaves a single-zone install single-zone.
- Seam rule: tools/audit/round9/D4/s2/zones_default.py (walks each first-run path at its pre-filled answers and reads the delivered two_zone_enabled; extend its path list for new branches)
- Proposed fix scope: config_flow.async_step_zones: ask whether the house has two zones (or write two_zone_mode explicitly as quick_setup does) and make the zone fields suggested rather than defaulted; correct the zones description in strings/translations

### D4-s2-05 (low, D4.M1, class new): 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5

Chromium reports validity.stepMismatch for 8 number fields at their shipped defaults (e.g. slab_thermal_mass 5 with min 0.1 step 0.5 -> spinner gives 5.1; upper_floor_heat_loss 0.08 with min 0.001 step 0.01 -> 0.081) and for 4 more once the questionnaire's derived values are stored; slider fields show 0.

Mechanism: _number passes min/max/step through; HTML number inputs take min as the step base, and these ranges put min off the grid the step implies (RANGE_* minima 0.1, 0.02, 0.25, 0.001, POSITIVE_PARAM_FLOOR 0.01) or store derived values of arbitrary precision. Inference boundary: that HA's box-mode number selector forwards min/max/step to a native number input is not measured here.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/step_grid.py` gives 8 defaults + 4 derived (count); harness tools/audit/round9/D4/s2/step_grid.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:_number (as rendered by async_step_thermal, async_step_zones, options async_step_thermal_model, async_step_building_preset)
- Perturbation: --perturb: in _number, '"step": step,' -> '"step": step if slider else "any",' applied to the module source in memory (expected to_zero, observed 0 and 0)
- Metric: Distinct rendered NumberSelector fields whose rendered value Chromium's <input type=number min max step> reports as stepMismatch.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/step_grid.py` gives off_grid_slider_fields=0. the 42 slider fields, whose minimum is on their grid, report none
- Property: Every value a number field renders (default, suggested or stored) lies on that field's step grid as the browser computes it, or the field declares step 'any'.
- Seam rule: tools/audit/round9/D4/s2/step_grid.py (enumerates every rendered NumberSelector of both flows, defaults and derived arm)
- Proposed fix scope: config_flow._number and the RANGE_* constants (step 'any' for box fields, or minima on the step grid)

### D4-s2-06 (low, D4.M2, class P2): The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields

With the building questionnaire armed on a two-zone install, 6 of the 10 derived fields the options flow renders sit on thermal_model_zones, whose en and sv descriptions do not contain {preset_warning}, so the warning the step returns is never shown there; thermal_model shows it for its 4.

Mechanism: async_step_thermal_model_zones passes description_placeholders={'preset_warning': ...} but options.step.thermal_model_zones.description is 'Zone split, inter-floor transfer and solar orientation.' An edit there silently turns the derivation off (_disarm_preset_on_derived_edit), and the warning that explains it lives only on the sibling page, where it still says the two-zone values are 'below'.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/preset_warning.py` gives 6 unwarned derived fields per language (count); harness tools/audit/round9/D4/s2/preset_warning.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_thermal_model_zones
- Perturbation: --perturb: append '\n\n{preset_warning}' to options.step.thermal_model_zones.description in en and sv, in memory (expected to_zero, observed 0)
- Metric: DERIVED_THERMAL_KEYS fields rendered on an options page whose displayed description (placeholders substituted) lacks PRESET_WARNING[lang], preset armed.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/preset_warning.py --disarmed` gives warned_derived_fields=0. disarmed, the warning is empty everywhere
- Property: Every page that renders a questionnaire-derived field shows the overwrite warning while the derivation is armed.
- Seam rule: tools/audit/round9/D4/s2/preset_warning.py (every options page rendering a DERIVED_THERMAL_KEYS field; add a page to its step tuple when a derived key moves)
- Proposed fix scope: strings.json/translations: add {preset_warning} to thermal_model_zones' description; reword PRESET_WARNING's 'below'

### D4-s2-07 (low, D4.M2, class new): After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again

After quick_setup and the device pre-fill, async_step_finish_setup returns a menu option-for-option identical to the one the user chose from (menu_identical_after_quick=1), with 'Quick setup (recommended)' still first, and a description that still says the user can 'start with shipped defaults'.

Mechanism: async_step_finish_setup builds a fixed three-option menu with no reference to what _data already holds; quick_setup and device_prefill both hand back to it. The quick path takes 7 screens to an entry against 4 for finish_now, and its last decision is a repeat of its first.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/quick_menu.py` gives 1 (count); harness tools/audit/round9/D4/s2/quick_menu.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_finish_setup
- Perturbation: --perturb: the quick_setup entry is offered only while CONF_BUILDING_STRUCTURE is absent from self._data (one-line edit on the module source, in memory) (expected to_zero, observed 0 and 0)
- Metric: Options on the menu reached after the quick path that re-offer the completed quick_setup path.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/quick_menu.py` gives null_repeated_options=0. the first menu, before any path, re-offers nothing completed
- Property: A menu reached after a path completes offers neither that path again as the recommended next step nor text that describes the pre-path state.
- Seam rule: tools/audit/round9/D4/s2/quick_menu.py (every hand-back to finish_setup; flow_rubric.py prints each first-run path's screen sequence)
- Proposed fix scope: config_flow.async_step_finish_setup (state-aware options or a quick-path-specific finish), strings description

### D4-s2-08 (low, D4.M3, class new): None of the 12 registered services has an icon in icons.json

Of the 12 services services.async_register_services registers, 12 have no entry under icons.json 'services', while every entity translation key has an icon (0 missing).

Mechanism: icons.json carries only an 'entity' block; Home Assistant reads service-action icons from icons.json 'services', so the action picker shows the generic icon for all 12.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/service_icons.py` gives 12 of 12 (count); harness tools/audit/round9/D4/s2/service_icons.py
- Instrumented symbol: custom_components/heatpump_optimizer/services.py:async_register_services (registered names) against icons.json
- Perturbation: --perturb: an in-memory icons.json 'services' block with one mdi icon per registered service (expected to_zero, observed 0)
- Metric: Registered domain services with no icons.json services.<name> entry.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/service_icons.py` gives entity_keys_without_icon=0. the same file's entity section is complete
- Property: Every registered service has an icon in icons.json.
- Seam rule: tools/audit/round9/D4/s2/service_icons.py (enumerates the services the production registration delivers)
- Proposed fix scope: icons.json: add a services block

### D4-s2-09 (low, D4.M3, class new): 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m²

8 rendered field help texts per language (en and sv) write temperatures as '<n> C' or areas as 'm2' (dhw_min_temperature, dhw_legionella_temperature, dhw_cooling_rate, solar_radiation_entity, on config and options pages), while the flows' 31 temperature selectors use '°C' and none uses a bare 'C'.

Mechanism: Hand-typed unit spellings in strings.json/translations drifted from the house style the selectors set.

- Evidence: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/unit_typography.py` gives 8 per language (count); harness tools/audit/round9/D4/s2/unit_typography.py
- Instrumented symbol: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_dhw / async_step_user_sensors and options async_step_hot_water / async_step_hot_water_tank / async_step_entities_metering (rendered field keys)
- Perturbation: --perturb: '<n> C' -> '<n> °C' and 'm2' -> 'm²' in the loaded translations, in memory (expected to_zero, observed 0)
- Metric: Rendered fields whose data_description matches (\d) C\b or \bm2\b, per language.
- Null control: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/unit_typography.py` gives selector_units_bareC=0. the selectors themselves never use the bare spelling
- Property: Help texts spell units as the selectors do (°C, m²).
- Seam rule: tools/audit/round9/D4/s2/unit_typography.py (every rendered field's help text in both flows)
- Proposed fix scope: strings.json and translations/*.json text edits

## Non-findings
- Every field the 39 pages render at defaults (initial and options flows, wood block on) has an en label and help text: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/flow_rubric.py` gives missing_label_total=0, missing_help_total=0
- No sv field label on any rendered page is left identical to en: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/flow_rubric.py` gives sv_labels_identical_to_en=0
- No rendered step's title, description, section or help text references a placeholder the step does not supply (en, sv): `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/flow_rubric.py` gives unsupplied_placeholders=0
- Every rendered number value lies inside its selector's [min, max]: `NODE_PATH=<pw>/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/step_grid.py` gives out_of_range_values=0
- Every registered service and all 67 of its schema fields are named in en and sv: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/service_icons.py` gives service_fields_checked=134, service_names_or_fields_untranslated=0
- Every error text of both flows other than dhw_min_too_close is free of literal escapes: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/escaped_text.py` gives escaped_other_error_texts=0
- The grid-fee and compressor money fields follow the instance currency: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/currency_units.py` gives 3 of 4 money fields show EUR under a EUR instance
- Steps from install to a created entry, each page submitted as pre-filled: finish_now 4 screens, quick 7, expert 10. Largest page: options.building, 24 fields in 4 sections. Flat pages over 10 fields: 5 (config quick_setup 13, zones 11, dhw 11; options quick_setup 14, entities_pump 11).: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/s2/flow_rubric.py` gives screens 4/7/10; max_fields_on_a_page=24; flat_pages_over_10_fields=5

## Unfinished
- D4.M1: For this seat's cells only the native number-input check applies; whether HA's ha-textfield forwards min/step and shows the invalid state was not measured (no HA frontend). The card-state/viewport/theme matrix is D4-s1's.
- D4.M2: A written per-page rubric score beyond the counts in flow_rubric.py (one theme per page, jargon) was judged by reading, not scored numerically; the config 'zones' page mixes two-zone, buffer-tank and solar fields (11 flat fields) -- recorded, not made a finding.

## Leads
- to D1-s2: custom_components/heatpump_optimizer/coordinator.py dhw_legionella_above_setpoint repair (config_flow._dhw_legionella_warning judgement). The shipped defaults (DEFAULT_DHW_LEGIONELLA_TEMP 60 > DEFAULT_DHW_SETPOINT 55, legionella on) trip the legionella-above-setpoint judgement on every default submit of the dhw page (config_flow logs it in every expert-path walk here); config_flow's comment says the coordinator turns it into the repair notice the user reads -- check whether a fresh default install raises a repair nobody caused.
- to D12-s1: custom_components/heatpump_optimizer/wood_fuel.py wood_fuel_ready / cheaper_hour_count (CONF_WOOD_PRICE_SEK_M3). The wood price is compared against the electricity price in the instance currency while its key, form unit and service text say SEK; check the wood-vs-pump sensors' published units and values for a non-SEK install (form side is D4-s2-02).

## Harnesses
- tools/audit/round9/D4/s2/prefill_config_strings.py
- tools/audit/round9/D4/s2/prefill_after_save.py
- tools/audit/round9/D4/s2/currency_units.py
- tools/audit/round9/D4/s2/escaped_text.py
- tools/audit/round9/D4/s2/zones_default.py
- tools/audit/round9/D4/s2/step_grid.py
- tools/audit/round9/D4/s2/step_grid.mjs
- tools/audit/round9/D4/s2/preset_warning.py
- tools/audit/round9/D4/s2/quick_menu.py
- tools/audit/round9/D4/s2/service_icons.py
- tools/audit/round9/D4/s2/unit_typography.py
- tools/audit/round9/D4/s2/flow_rubric.py
