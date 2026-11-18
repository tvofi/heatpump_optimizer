R11-SEAM-config (round 11, size L), on the approved design at 069bff452c24cb5b98e5fc7c5d361a3978f9c2f2 (`design.md`). Findings: D17-s1-02, D10-s2-01, D10-s1-03, D17-s2-05, D17-s2-04, D4-s2-01, D6-s3-01 (merged in); classes I4, N-dead-input, N-entry-data-placement, P2. None is filed: `ISSUES.json` at `plan/r11` 50a932de3b2a carries `"number": null` for all four class rows, so there is no issue to close.

What changed, by owner:
- `entry_config.py` owns where a key is stored: `DATA_ONLY` (the first-screen keys no options page edits; at this head `{"name"}`) and `placed(effective)`. Setup (`_create_setup_entry`, `data=` and `options=`), reconfigure (`_async_save_reconfigure`), reauth (`async_step_reauth_confirm`), the reset (`factory_settings`) and its undo (`undone_settings`) write placed pairs; the reader `{**data, **options}` is unchanged. Reconfigure prefills the mapping in force.
- `__init__.py`: entry version 7.2 (`MINOR_VERSION` on the flow, `CONFIG_ENTRY_MINOR_VERSION` in `const.py`). `async_migrate_entry` places any entry below 7 or below minor 2; placing moves keys only and keeps the options value where a key is on both sides.
- `config_flow.py`: `_omit_unstored_computed` judges a computed default over the save (`saving`), not the stored configuration. One page builder, `_prefill_page`, serves both pre-fill pages (the two methods delegate to it), carrying `_WINDOW_PLACEHOLDERS`, the empty disclaimer and the notes. The setup page keeps `(keys, notes)` like the options page, so a refusal re-renders the preview's notes. `_prefill_fields` is split from the options page's after-save field, so the setup page posts no `after_save`. `_PREFILL_PAIRED` shows the power fraction beside a shown night-mode schedule, and `_uncapped_schedule_errors` refuses a kept schedule whose fraction in force is `>= 1.0` (new key `silent_mode_fraction_uncapped`, all language files).
- `tests/hastub`: `ConfigEntry.minor_version = 1`, `ConfigFlow.VERSION`/`MINOR_VERSION = 1` (upstream's `FlowHandler` and `ConfigEntry` defaults); `harness.FakeEntry.minor_version = 1`.

Alternatives lost, as the design ruled them (§4): writing first-screen keys back to data from the options flow (four option writers in `services.py`/`coordinator.py` would each need the rule); major version 8 (the previous release's migrate returns False above 7, so a downgrade stops loading); capping a 1.0 schedule in `silent_mode` (changes the plan of every install that saved one on the grid page, which no finding names); re-placing at every setup (the brief requires a versioned migration).

Release notes (T18, owed first in the stamped section's `### Action needed`): "Settings now live in one place in each config entry (entry version 7.2). Downgrading to an earlier release still loads with the same settings, but a reconfigure or re-authentication saved under that earlier release is shadowed by the options until the next save under this one."

The design's four fixer notes (stub minor version, token redaction, the two-zone comment, the undo record) are built here — the stub extension above, the token now in options under `diagnostics.py`'s redaction over both sides (`tests/entities.py`'s and `tests/features.py`'s redaction checks pass), the comment reworded in `const.py` and its twin in `thermal_model.py`, and the undo record's placement tested in `tests/entities.py`.

## Head

5cc4bd2c44e80fb521ee2d6e159a1e6a4f3dfbb4, measured against merge base 8751943e17ef4d3ec699e7859ae829b4528d8ce7 (= `origin/main` at measurement).

## Mutation proof

Each mutant applied to a detached copy of the head, the named suite run, the source restored (`mutate.py` in the seat scratch; the mutant text is quoted).
- `entry_config.placed`: data side `if k in DATA_ONLY` deleted (everything to data) -> `tests/config_flow_steps.py` red on 7: "the created entry stores DATA_ONLY in data and every setting in options, the effective mapping unchanged"; "reconfigure after options save: ..."; "reconfigure with no options save: ..."; "a new token is written through, the entry reloads, reauth_successful"; "re-submitting this entry's own identity reconfigures it instead of aborting"; "a rotated token is written through and the entry keeps its other settings"; "a slot the user cleared is dropped, not silently kept".
- `async_migrate_entry`: `or minor < CONFIG_ENTRY_MINOR_VERSION` deleted -> `tests/entities.py` red on "a 7.1 entry migrates to 7.2: data holds DATA_ONLY alone, the effective mapping is unchanged and a key in both sides keeps the options value in force".
- `_omit_unstored_computed`: `row.default.of(saving, hass)` -> `row.default.of(current, hass)` -> `tests/config_flow_steps.py` red on 2: "a computed value kept while its source changes is stored; kept with its source unchanged it stays unstored"; "a valid per-day save stores the two specs, not seven keys, and reads per-day on from them".
- `_prefill_page`: `**_WINDOW_PLACEHOLDERS` deleted -> red on "a too-short window refusal on the setup pre-fill page renders its placeholders". The first run of this mutant survived (the uncapped-schedule refusal reads no window placeholder); the check was added and the mutant re-run red.
- `_uncapped_schedule_errors`: `>= 1.0` -> `> 1.0` -> red on 3: "a kept schedule at fraction 1.0 is refused on the fraction, ..."; "a too-short window refusal ..."; "the schedule kept with a fraction below 1.0 is stored with it".

## Unpinned sites

`tools/pr/ci_predict.py` at the head lists the added unpinned sites; each, with its disposition:
- custom_components/heatpump_optimizer/__init__.py:222 CMP_BOUND*2 if entry.version < CONFIG_ENTRY_VERSION or minor < CONFIG_EN: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/__init__.py:222 GUARD_OFF if entry.version < CONFIG_ENTRY_VERSION or minor < CONFIG_EN: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:588 RETURN_DEL return {**entry.data, **entry.options}: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:613 GUARD_OFF if unique_id == entry_identity(_in_force(entry)): pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2247 BOOLOP if key in values or (key not in keys and key in in_force): pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2259 RETURN_DEL return _options_schema(_prefill_fields(keys, values, current: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2443 GUARD_OFF if not saved.get(CONF_SILENT_MODE_WINDOWS): pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2446 CMP_BOUND if float(fraction) >= 1.0: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2446 GUARD_OFF if float(fraction) >= 1.0: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2448 RETURN_DEL return {}: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2474 GUARD_OFF if CONF_SILENT_MODE_WINDOWS not in errors: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2824 RETURN_DEL return _prefill_page(self, "device_prefill", schema, notes,: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:3458 RETURN_DEL return _in_force(self._entry): pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:4098 RETURN_DEL return _prefill_page(self, "modbus_prefill", schema, notes,: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:4171 RETURN_DEL return self._prefill_form(_prefill_schema(suggested, suggest: pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/entry_config.py:414 RETURN_DEL return placed({**data_side, **options_side}): pinned by `mutation-autofix` (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/entry_config.py:430 RETURN_DEL return placed({**data_side, **options_side}): pinned by `mutation-autofix` (its lane mutates `custom_components/`)

Five pins this diff stales are deleted by hand, as the predictor's STALE PIN lines require (`_current`, `async_step_modbus_prefill`, `identity_update`, `factory_settings`, `undone_settings`).

## Null control

- Finder harnesses: each null arm reads the same at both ends (table below): `null_kept_value_lost` 0/0, `shadowed_null` 0/0, `finish_now_settings_in_data` 0/0, `options_refusal_missing` 0/0.
- New checks: the reconfigure check runs a no-options-save arm beside the options-save arm; the computed-default check re-submits the source unchanged and the value stays unstored; the migration check's 7.2 entry is not rewritten (`config_entries.updated` unchanged); the uncapped refusal does not fire for fraction 0.6 nor for fraction 1.0 without a schedule (companion harness arms).
- Downgrade (T18): the previous release's `async_migrate_entry` (`__init__.py` identical at v10.1.0 and the merge base, `git diff --quiet v10.1.0 8751943e17ef -- custom_components/heatpump_optimizer/__init__.py`) on an entry stamped 7.2 returns True with no update and both sides unchanged; its refusal arm (major 8) is the existing "a downgrade is refused rather than mangled" check.

## Figures

Finder harnesses from `plan/r11` 50a932de3b2a, exported and run from the tree root with `PYTHONPATH=tests/hastub:. python3 $EXPORT/dev/audit/rounds/round11/<path>`, base 8751943e17ef -> head 5cc4bd2c44e8:
- `$EXPORT/dev/audit/rounds/round11/D17/s1/h_computed.py` (sha1 b104763742264dc09f2df9e65302376cbee9548a): `computed_kept_value_lost` 8 -> 0; `null_kept_value_lost` 0 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D10/s2/reconfig_shadow.py` (sha1 2fa91d8ffe2a3e798cc51b3e37a29330ce9bacbc): `shadowed_options_saved` 2 -> 0; `prefill_shows_running_indoor` 0 -> 1; `shadowed_null` 0 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D10/s1/cfg_data_options.py` (sha1 f82ebb7f5889bfa8f9fee1b03c631d59d7f21e7d): `continue_settings_in_data` 41 -> 0; `finish_now_settings_in_data` 0 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D17/s2/after_save_stray.py` (sha1 dd4cdaa6428e307bab5f27fe595353e3e19b404c): `entries_with_after_save` 2 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D4/s2/flow_errors.py` (sha1 c50ebfa82360840517a1d38d0ae327e15d134e3e): `unfilled_placeholders_total` 8 -> 0 over its 9 cells, all fired at both ends.
- `$EXPORT/dev/audit/rounds/round11/D6/s3/prefill_placeholders.py` (sha1 05cd85c0c5cae6fc8225c01769126141fa07b262): `config_refusal_missing` 2 -> 0; `config_refusal_changed_vs_preview` 3 -> 0; `options_refusal_missing` 0 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D17/s2/silent_prefill.py` (sha1 42b79596d65fa2b024a301c2b667713d4656ba93) reads flat at the head (`kept_schedule_cap_delta_kW` 0.000 -> 0.000, `with_fraction_cap_delta_kW` -2.000 -> 0.000): it reads the created entry's `data` alone, which now holds `DATA_ONLY`, and posts a schedule with no fraction, which the fix refuses, so its walk ends without the schedule. Companion applying the pages' own rule to the same inputs, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_seam_config_silent_prefill.py` (sha1 ff021f0bfe3d5ce833d8adbd7079b16eb893b493): `fraction_shown_beside_windows` 0 -> 1; `uncapped_schedule_accepted` 1 -> 0; nulls `capped_schedule_refused` 0 -> 0, `no_schedule_refused` 0 -> 0. The cap a kept fraction buys is the finder's own `with_fraction_cap_delta_kW` -2.000 at the base.

Class enumeration (fixer step 8). Entry writes passing `data=`: an AST walk of `custom_components/heatpump_optimizer/**/*.py` for calls to `async_update_entry`/`async_create_entry` with a `data` keyword returns 7 sites at the head: `__init__.py::async_migrate_entry`, `config_flow.py::HeatPumpOptimizerConfigFlow._async_save_reconfigure`, `::_create_setup_entry`, `::async_step_reauth_confirm`, `coordinator.py::_async_rewrite_entry` (closed in this diff: each writes a pair from `placed`); `config_flow.py::HeatPumpOptimizerOptionsFlow._save` (dispositioned: an options flow's result data is the entry's options); `repairs.py::DhwSetpointRepairFlow.async_step_confirm` (dispositioned: a repair flow's result, not an entry write). The rule is landed as the P2 registry entry `entry_key_placement` in `tests/entities.py`, whose check fails on an eighth site with neither an owner nor a disposition. Pre-fill renders: both page methods call `_prefill_page`. Computed defaults: every `_Computed` row passes through `_omit_unstored_computed`.

Gate: `python3 tests/closure.py select --diff 8751943e17ef` printed `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran them: `tests/doc_claims.py` (the fraction field had no row in `docs/configuration.md`) and `tests/typing_ruler.py` (an unused `type: ignore`) went red and were repaired at the head, each re-run green (`ALL 411 checks PASSED`, `ALL 12 typing-ruler source checks PASSED`); every other script passed. No golden moved; neither claim file is touched.

Structure: `python3 tests/structure.py` passes; `class_excess_loc` 17382 -> 17370 is re-recorded (reason in the commit). `_prefill_errors` rose from CC 14 to 17 on its first cut, over the `functions_cc_over_15` budget; it was paid by moving the refusal into `_uncapped_schedule_errors` (CC back to 15). Architecture score: `python3 tools/audit/archscore/score.py --diff 8751943e17ef` printed `Architecture score: dS +0.0000 NULL`.

<!-- figure-block: scope-line mb=8751943e17ef4d3ec699e7859ae829b4528d8ce7 head=5cc4bd2c44e80fb521ee2d6e159a1e6a4f3dfbb4 -->
~~~text
MODE: SCOPED -- 32 script(s) run, 1 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / mutation` (predicted by `tools/pr/ci_predict.py`; no CI run exists yet): the unpinned sites listed above, each a site this diff adds, until `mutation-autofix` pins them (`ci-autofix.md`). Cheaper detector: `ci_predict.py`, which `prepr.sh` already runs before every handoff at a standing cost of its own run time; it named every site here before the push, so no further detector is owed.

## Forward-carry

none

## Friction

none
