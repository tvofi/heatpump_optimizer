R10-CONFIGFLOW-PAGES (Product UX, L), arm A plus arm A3', the first of the group's pull requests in the approved design's order (`design/R10-CONFIGFLOW-PAGES` `32892dc67`, `dev/programme/designs/R10-CONFIGFLOW-PAGES.md`; approve verdict `design-verdict/R10-CONFIGFLOW-PAGES` `3af84d776`). Findings D7-s2-56 (fixed here) of #2238. Arms B (D7-s2-55), C/C2 (ARCH2-s5-F1) and D (the carried tripwires) follow as their own pull requests, so this one closes nothing.

**The bug (D7-s2-56).** Nine options pages validate their submit, and each wrote its own copy of the page skeleton. When a submit was refused, five of them re-rendered the form over `{**current, **user_input}`. A stored entity the user had cleared is absent from `user_input`, so the re-rendered form showed it again as the stored entity, and the next submit silently kept the entity the user had removed. Driven through the production steps at the merge base, 27 of the 30 cleared `_STORED` rows re-render as stored (entities 9, entities_metering 9, building 7, comfort 1, hot_water 1). hot_water_tank (re-renders over `merged`) and grid_fees (pops its one slot by hand) were already right.

**The fix (arm A, the finder's patch 08).** `HeatPumpOptimizerOptionsFlow._page` is now the one page sequence: flatten the sections, `merged = {**current, **flat}`, `cleaned = _clear_absent(flat, step, merged)` when `clear`, `errors = await check(cleaned, current)`, then either `_save_or_menu(finish(cleaned, merged) or cleaned)` or a re-render over `{**current, **cleaned}`, so a cleared slot shows empty. The nine pages fold into it. Their predicates move out unchanged as `_entities_errors`, `_metering_errors`, `_comfort_errors`, `_hot_water_errors`, `_disinfection_errors`, `_plumbing_errors`, `_peak_tariff_errors`, `_silent_window_errors` and `_grid_fee_errors`. Their save shaping moves out as `_warn_legionella_ceiling`, `_peak_window_as_int`, `_apply_dso_catalog` and `_building_wood_flag`, and the two duplicated placeholder dicts become `_fee_placeholders`. grid_fees' hand-written `current.pop(CONF_GRID_FEE_ENTITY)` goes: the template does that for every slot. One line differs from the patch: `_metering_errors` keeps its guard on one line, as `async_step_entities_metering` had it, because the mutation inventory generates `GUARD_OFF` only for a one-line `if`, and the wrapped form would have dropped the pinned site instead of moving it.

**`_clear_absent` is judged over `merged` on every page, which at the base only building did.** The two bases differ only for a row whose `when` gate a field on the same page opens. `grep -n 'when=' custom_components/heatpump_optimizer/config_flow.py` returns 15 lines: 13 rows on building (the wood block), 1 row on hot_water (the per-day windows, default `''`, not `_STORED`, so `_clear_absent` never nulls it) and 1 docstring. So building, which already used `merged`, is the only page where the basis can change a save, and no save moves. The mutant that judges the clear over `current` survived the suite at first. The check `turning the wood block off keeps its hidden entities instead of nulling them` now kills it.

**Arm A3', the price-entity clear (a deliberate behaviour change, user-visible).** The entities page judged `price_entity_required` over `user_input.get(CONF_PRICE_ENTITY) or current.get(CONF_PRICE_ENTITY)`. A cleared price entity is absent from the submit, so the stored entity satisfied the check, and then `_clear_absent` saved `price_entity: None`, an entity price source with no price sensor. `_entities_errors(cleaned, current)` now judges the source and the entity over `view = {**current, **cleaned}`, the rule `_disinfection_errors` (formerly `async_step_hot_water_tank`) already applies. **Behaviour change:** a submit whose resolved source is `entity` and whose price entity is cleared was accepted and saved `price_entity: None`; it is now refused with the existing `price_entity_required` error on the price-entity field, and the stored entity is kept. The translation key already exists in `strings.json` and every translation, so no string moves. The Tibber branch keeps `submit.get(CONF_TIBBER_TOKEN) or current.get(...)` unchanged: the token row's default is `''`, not `_STORED`, so `_clear_absent` never nulls it. One existing check pinned the defect: `a stored price sensor satisfies the entity source without being re-submitted` asserted the `menu` result and `price_entity is None`. It now submits the stored entity as the untouched picker does (its suggested value) and asserts that it is kept: `an untouched stored price sensor satisfies the entity source and is kept`. The cleared case is the new refusal check.

**Design invariants.** An accepted submit saves the same options at the base and at the head, with exactly one exception, named `A3-exception: price_entity_cleared_under_entity_source`. Every error key and placeholder is unchanged. Only a rejected form's cleared `_STORED` slots render differently. The harness's `--accepted` arm drives 12 accepted submits, one or more per page, and prints each saved options dict as canonical JSON with its sha1. The exception case prints on its own line, outside the digest, and `exceptions` must read 1, so the exception cannot grow silently.

**Design carries discharged here.** `a3p-test`: the A3' test, its two controls, the two mutants, the `--clear-required` arm and the A3 exception. `overlay-08`: dismissed as designed, because the overlay equals patch 08, which this diff applies. `grid-connection-flatten`: grid_connection's `{CONF_SILENT_MODE_WINDOWS: "", **user_input}` default still runs before `_page` flattens, and no grid_connection row carries a `group`, so no section can hold the window. The check `a cleared silent-mode window saves as no window, on an ungrouped page` asserts that the stored window becomes `""` and that no grid_connection row is grouped, so it fails the day a group is added and the default would sit outside it.

## Head

`cc0510ee2a25444363251df640509b3034bca4f6` merges origin/main `eab04d0eb` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2912.md`.

`f80503805fc6cf6218cb0949ae8243cf5c9707d6` merges origin/main `f844df1fe` into the authored code head `9d043f7814dfa3c4beea035a3de95bf6788fbcaa` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`9d043f7814dfa3c4beea035a3de95bf6788fbcaa`, branch `handoff/r10-configflow-a`, merge base `6d86acc909f7fc465e5736771daf8fa45c1373a4` (origin/main tip at 2026-10-28T10:06Z). Everything under `## Mutation proof`, `## Null control` and `## Figures` was measured on this branch over that base, three-dot, with the seat interpreter (Python 3.14.7, `~/.local/state/hpo/venv-ci`, first on `PATH`), which is CI's interpreter class. This head is `1eaa4e140` plus one commit that renames the test helper `_stored_rows` to `_page_stored_entities` (prepr's no-copies check read it as a copy of `price_model._stored_rows`). `config_flow.py` is byte-identical between the two, so the mutation and harness figures taken at earlier commits of this branch hold.

## Mutation proof

The tests came first. With `tests/config_flow_steps.py` at this head and `config_flow.py` at the merge base, the suite read `6 of 530 checks FAILED`: `a rejected entities submit re-renders each cleared stored entity empty` (still_stored 9 rows), the same for entities_metering (9), comfort (1), hot_water (1) and building (7), and `clearing the stored price entity under an entity source is price_entity_required` (`type=menu errors=None stored=None`). The hot_water_tank and grid_fees arms of the first check passed at the base, which is the positive control.

Each mutant below edits one line of `config_flow.py` in a fresh `git archive HEAD` copy, then runs `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`. Mutants 1-5 and the two A3' mutants ran at `8bdab62ce` (530 checks), and mutant 6 at `d1dc4a480` (531 checks). Neither commit's `config_flow.py` differs from this head's. 8 of 8 are red:

- M1, `_page`'s re-render merge `{**current, **cleaned}` -> `{**current, **flat}`: `7 of 530 checks FAILED`, the `a rejected <page> submit re-renders each cleared stored entity empty` check on entities, entities_metering, comfort, hot_water, hot_water_tank, building and grid_fees.
- M2, `check(cleaned, current)` -> `check(flat, current)` (the pre-clear view, the design's first A3' mutant, on the template): `3 of 530 checks FAILED`: `clearing the switch under a stored control mode is refused (#1067)`, the hot_water_tank re-render check, and `clearing the stored price entity under an entity source is price_entity_required`.
- M3, `_page`'s `if not errors:` -> `if True:`: `38 of 523 checks FAILED`, among them `a changed but refused token re-shows the entities page as invalid_tibber_token`, `'flow' without the two-zone model is refused, not saved (#398)`, `an inverted comfort band re-shows the page with min_above_target`.
- M4, the `finish` application dropped (`cleaned` saved as is): `4 of 530 checks FAILED`: `a valid hot-water page saves and warns about the legionella pair`, `an uncoercible peak window falls back to the default, not the string`, `a coercible peak window is converted to int, not defaulted`, `a catalog DSO product writes its own rules and mode over the page`.
- M5, `description_placeholders=placeholders` -> `None`: `4 of 530 checks FAILED`, `a rejected <page> form keeps its description placeholders` for grid, grid_fees, hot_water and grid_connection.
- M6, `_clear_absent(flat, step_id, merged)` -> `(..., current)`: survived at `8bdab62ce` (`ALL 530 checks PASSED`). The check `turning the wood block off keeps its hidden entities instead of nulling them` was added in `d1dc4a480`, and there the mutant reads `1 of 531 checks FAILED` (`options={'wood_furnace_enabled': False, ..., 'wood_tank_top_entity': None, ...}`).
- A3'-M1, `_entities_errors` judging the pre-clear view (`{**current, **{k: v for k, v in submit.items() if v is not None}}`): `1 of 530 checks FAILED`, `clearing the stored price entity under an entity source is price_entity_required`.
- A3'-M2, the restored `if not (submit.get(CONF_PRICE_ENTITY) or current.get(CONF_PRICE_ENTITY)):`: `1 of 530 checks FAILED`, the same check.

The mutation ledger: `tests/mutation_ledger/killed_by/config_flow.py/` held 8 rows keyed on symbols this diff empties. Six follow their guard: `async_step_entities` `980b44df` -> `_page` `980b44df`, `b9ebe2fa` -> `_entities_errors` `30631ec6` (the A3' guard), `c680d852` -> `_entities_errors` `2a9c0142`, `async_step_entities_metering` `c8d82db8` -> `_metering_errors` `bdb67645`, `async_step_hot_water` `02e99d97` -> `_hot_water_errors` `355fc9b4` and `07c72f5d` -> `8cd5759a`. Each re-keyed row's kill was re-measured with its own mutant, `python3 tests/mutation_table.py --anchor '<new anchor>' --scripts tests/config_flow_steps.py --jobs 1` at `71938ca71` (whose `config_flow.py` is this head's): all six print `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified` and `killed by tests/config_flow_steps.py`, each beside a baseline `rc=0 failed=0` and the comment-only null control `NULL_COMMENT survived tests/config_flow_steps.py`. Two rows retire: `async_step_comfort` and `async_step_hot_water_tank` `GUARD_OFF b75e92ec` (`if user_input is not None:`) fold into `_page`'s own pinned site, `HeatPumpOptimizerOptionsFlow._page GUARD_OFF b75e92ec`. The design's other seven ledger rows (`_options_suggested_numeric`, `_suggested_entity` and the wizard's five) belong to arms B and C, whose symbols this diff does not touch. `mutation_table.py --anchor` printed `the ledger agrees with the deterministic inventory` at this head.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` lists 24 sites the diff adds without a disposition, all in `custom_components/heatpump_optimizer/config_flow.py`. Each is left to `mutation-autofix` (`--pin-killed`; its lane mutates `custom_components/`). M3 and M5 above already show the suite kills the template's guard and pass-through.

- custom_components/heatpump_optimizer/config_flow.py:1896 RETURN_DEL: mutation-autofix (`return submit`)
- custom_components/heatpump_optimizer/config_flow.py:1907 RETURN_DEL: mutation-autofix (`return cleaned`)
- custom_components/heatpump_optimizer/config_flow.py:1914 RETURN_DEL: mutation-autofix (`return cleaned`)
- custom_components/heatpump_optimizer/config_flow.py:1919 RETURN_DEL: mutation-autofix (`return {"currency": currency, "fee_bound": f"{grid_fee.fee_b`)
- custom_components/heatpump_optimizer/config_flow.py:3282 GUARD_OFF: mutation-autofix (`if check is not None:`)
- custom_components/heatpump_optimizer/config_flow.py:3487 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3488 GUARD_OFF: mutation-autofix (`if not (submit.get(CONF_TIBBER_TOKEN) or current.get(CONF_TI`)
- custom_components/heatpump_optimizer/config_flow.py:3490 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3498 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3513 BOOLOP: mutation-autofix (`if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL a`)
- custom_components/heatpump_optimizer/config_flow.py:3515 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3527 RETURN_DEL: mutation-autofix (`return await self._page("comfort", user_input, clear=True, c`)
- custom_components/heatpump_optimizer/config_flow.py:3562 BOOLOP: mutation-autofix (`if not errors and _dhw_min_too_close(submit, current):`)
- custom_components/heatpump_optimizer/config_flow.py:3562 GUARD_OFF: mutation-autofix (`if not errors and _dhw_min_too_close(submit, current):`)
- custom_components/heatpump_optimizer/config_flow.py:3564 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3586 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3639 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3650 RETURN_DEL: mutation-autofix (`return cleaned`)
- custom_components/heatpump_optimizer/config_flow.py:3734 GUARD_OFF: mutation-autofix (`if not _valid_months_spec(submit.get(CONF_PEAK_TARIFF_MONTHS`)
- custom_components/heatpump_optimizer/config_flow.py:3736 GUARD_OFF: mutation-autofix (`if not is_valid_spec(submit.get(CONF_PEAK_TARIFF_HOURS, ""))`)
- custom_components/heatpump_optimizer/config_flow.py:3738 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3758 GUARD_OFF: mutation-autofix (`if problem is not None:`)
- custom_components/heatpump_optimizer/config_flow.py:3764 RETURN_DEL: mutation-autofix (`return errors`)
- custom_components/heatpump_optimizer/config_flow.py:3788 RETURN_DEL: mutation-autofix (`return errors`)

## Null control` and `## Figures` was measured on this branch over that base, three-dot, with the seat interpreter (Python 3.14.7, `~/.local/state/hpo/venv-ci`, first on `PATH`), which is CI's interpreter class. This head is `1eaa4e140` plus one commit that renames the test helper `_stored_rows` to `_page_stored_entities` (prepr's no-copies check read it as a copy of `price_model._stored_rows`). `config_flow.py` is byte-identical between the two, so the mutation and harness figures taken at earlier commits of this branch hold.

## Mutation proof

The tests came first. With `tests/config_flow_steps.py` at this head and `config_flow.py` at the merge base, the suite read `6 of 530 checks FAILED`: `a rejected entities submit re-renders each cleared stored entity empty` (still_stored 9 rows), the same for entities_metering (9), comfort (1), hot_water (1) and building (7), and `clearing the stored price entity under an entity source is price_entity_required` (`type=menu errors=None stored=None`). The hot_water_tank and grid_fees arms of the first check passed at the base, which is the positive control.

Each mutant below edits one line of `config_flow.py` in a fresh `git archive HEAD` copy, then runs `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`. Mutants 1-5 and the two A3' mutants ran at `8bdab62ce` (530 checks), and mutant 6 at `d1dc4a480` (531 checks). Neither commit's `config_flow.py` differs from this head's. 8 of 8 are red:

- M1, `_page`'s re-render merge `{**current, **cleaned}` -> `{**current, **flat}`: `7 of 530 checks FAILED`, the `a rejected <page> submit re-renders each cleared stored entity empty` check on entities, entities_metering, comfort, hot_water, hot_water_tank, building and grid_fees.
- M2, `check(cleaned, current)` -> `check(flat, current)` (the pre-clear view, the design's first A3' mutant, on the template): `3 of 530 checks FAILED`: `clearing the switch under a stored control mode is refused (#1067)`, the hot_water_tank re-render check, and `clearing the stored price entity under an entity source is price_entity_required`.
- M3, `_page`'s `if not errors:` -> `if True:`: `38 of 523 checks FAILED`, among them `a changed but refused token re-shows the entities page as invalid_tibber_token`, `'flow' without the two-zone model is refused, not saved (#398)`, `an inverted comfort band re-shows the page with min_above_target`.
- M4, the `finish` application dropped (`cleaned` saved as is): `4 of 530 checks FAILED`: `a valid hot-water page saves and warns about the legionella pair`, `an uncoercible peak window falls back to the default, not the string`, `a coercible peak window is converted to int, not defaulted`, `a catalog DSO product writes its own rules and mode over the page`.
- M5, `description_placeholders=placeholders` -> `None`: `4 of 530 checks FAILED`, `a rejected <page> form keeps its description placeholders` for grid, grid_fees, hot_water and grid_connection.
- M6, `_clear_absent(flat, step_id, merged)` -> `(..., current)`: survived at `8bdab62ce` (`ALL 530 checks PASSED`). The check `turning the wood block off keeps its hidden entities instead of nulling them` was added in `d1dc4a480`, and there the mutant reads `1 of 531 checks FAILED` (`options={'wood_furnace_enabled': False, ..., 'wood_tank_top_entity': None, ...}`).
- A3'-M1, `_entities_errors` judging the pre-clear view (`{**current, **{k: v for k, v in submit.items() if v is not None}}`): `1 of 530 checks FAILED`, `clearing the stored price entity under an entity source is price_entity_required`.
- A3'-M2, the restored `if not (submit.get(CONF_PRICE_ENTITY) or current.get(CONF_PRICE_ENTITY)):`: `1 of 530 checks FAILED`, the same check.

The mutation ledger: `tests/mutation_ledger/killed_by/config_flow.py/` held 8 rows keyed on symbols this diff empties. Six follow their guard: `async_step_entities` `980b44df` -> `_page` `980b44df`, `b9ebe2fa` -> `_entities_errors` `30631ec6` (the A3' guard), `c680d852` -> `_entities_errors` `2a9c0142`, `async_step_entities_metering` `c8d82db8` -> `_metering_errors` `bdb67645`, `async_step_hot_water` `02e99d97` -> `_hot_water_errors` `355fc9b4` and `07c72f5d` -> `8cd5759a`. Each re-keyed row's kill was re-measured with its own mutant, `python3 tests/mutation_table.py --anchor '<new anchor>' --scripts tests/config_flow_steps.py --jobs 1` at `71938ca71` (whose `config_flow.py` is this head's): all six print `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified` and `killed by tests/config_flow_steps.py`, each beside a baseline `rc=0 failed=0` and the comment-only null control `NULL_COMMENT survived tests/config_flow_steps.py`. Two rows retire: `async_step_comfort` and `async_step_hot_water_tank` `GUARD_OFF b75e92ec` (`if user_input is not None:`) fold into `_page`'s own pinned site, `HeatPumpOptimizerOptionsFlow._page GUARD_OFF b75e92ec`. The design's other seven ledger rows (`_options_suggested_numeric`, `_suggested_entity` and the wizard's five) belong to arms B and C, whose symbols this diff does not touch. `mutation_table.py --anchor` printed `the ledger agrees with the deterministic inventory` at this head.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` lists 24 sites the diff adds without a disposition, all in `custom_components/heatpump_optimizer/config_flow.py`. Each is left to `mutation-autofix` (`--pin-killed`; its lane mutates `custom_components/`). M3 and M5 above already show the suite kills the template's guard and pass-through:

- `config_flow.py:1896 RETURN_DEL` `return submit`: mutation-autofix
- `config_flow.py:1907 RETURN_DEL` `return cleaned`: mutation-autofix
- `config_flow.py:1914 RETURN_DEL` `return cleaned`: mutation-autofix
- `config_flow.py:1919 RETURN_DEL` `return {"currency": currency, "fee_bound": f"{grid_fee.fee_b`: mutation-autofix
- `config_flow.py:3282 GUARD_OFF` `if check is not None:`: mutation-autofix
- `config_flow.py:3487 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3488 GUARD_OFF` `if not (submit.get(CONF_TIBBER_TOKEN) or current.get(CONF_TI`: mutation-autofix
- `config_flow.py:3490 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3498 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3513 BOOLOP` `if submit.get(CONF_FREQ_CONTROL_MODE) == FREQ_MODE_CONTROL a`: mutation-autofix
- `config_flow.py:3515 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3527 RETURN_DEL` `return await self._page("comfort", user_input, clear=True, c`: mutation-autofix
- `config_flow.py:3562 BOOLOP` `if not errors and _dhw_min_too_close(submit, current):`: mutation-autofix
- `config_flow.py:3562 GUARD_OFF` `if not errors and _dhw_min_too_close(submit, current):`: mutation-autofix
- `config_flow.py:3564 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3586 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3639 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3650 RETURN_DEL` `return cleaned`: mutation-autofix
- `config_flow.py:3734 GUARD_OFF` `if not _valid_months_spec(submit.get(CONF_PEAK_TARIFF_MONTHS`: mutation-autofix
- `config_flow.py:3736 GUARD_OFF` `if not is_valid_spec(submit.get(CONF_PEAK_TARIFF_HOURS, ""))`: mutation-autofix
- `config_flow.py:3738 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3758 GUARD_OFF` `if problem is not None:`: mutation-autofix
- `config_flow.py:3764 RETURN_DEL` `return errors`: mutation-autofix
- `config_flow.py:3788 RETURN_DEL` `return errors`: mutation-autofix

## Null control

- Rejected forms with nothing cleared: `r10_configflow_pages.py --null` reads `rejected=7 stored_rows=30 shown_stored=19` at the base and at this head. Every stored entity on a rejected page re-renders as stored on both trees. (entities_metering and hot_water_tank accept that submit, because a stored entity satisfies them, and show no form.) The suite's own null, `a rejected <page> submit that cleared nothing re-renders every stored entity`, passes on both trees.
- Replacing the price entity: `--clear-required --null` reads `type=menu errors=None stored_price_entity='sensor.other'` on both trees, and so does the suite's `replacing the stored price entity saves the new one`.
- Switching to Tibber with a token: `switching to Tibber with a token saves it and nulls the cleared price entity` passes on both trees. The absent price entity is still nulled by `_clear_absent`, as at the base.
- Accepted submits: `--accepted` reads `cases=11 exceptions=1 digest=071e7ad04eb0` at the base and at this head. The 11 saved-option digests outside the exception are equal.
- Goldens: `wizard_widgets.py` reads `golden_equal=1` on both trees (`golden.capture_config_flow()` equals `tests/golden/config_flow.json`). `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to the base, so nothing is claimed.

## Figures

All at this head unless marked, seat interpreter:

- `tests/config_flow_steps.py`: `ALL 531 checks PASSED`, rc 0: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`. At the base (this head's tests over the base's `config_flow.py`): `6 of 530 checks FAILED`, rc 1, the six named under `## Mutation proof`.
- the defect, ported harness `dev/audit/harnesses/r10_configflow_pages.py` (new here): `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_configflow_pages.py`. Base: `RESULT pages=9 rejected=9 stored_rows=30 stale_slots=27`. Head: `RESULT pages=9 rejected=9 stored_rows=30 stale_slots=0`. The rule: for each of the nine validating pages, store an entity in every `_STORED` row its `_page_rows` returns with the `when` gates open, submit with all of them cleared plus one rejecting field, and count the cleared rows whose re-rendered `suggested_value` is the stored entity.
- A3', the same harness `--clear-required`: base `RESULT type=menu errors=None stored_price_entity=None`. Head `RESULT type=form errors=price_entity_required stored_price_entity='sensor.price'`.
- A3, `--accepted`: base and head `RESULT cases=11 exceptions=1 digest=071e7ad04eb0`. The exception line at the base reads `{"errors": null, "options": {"price_entity": null, "price_source": "entity"}, "type": "menu"}`, and at the head `{"errors": {"price_entity": "price_entity_required"}, "options": {"price_entity": "sensor.price", "price_source": "entity"}, "type": "form"}`.
- the finder's harness at the finder's base `554e2ecfa`, from a standalone clone at `01d9d0be2`: `bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 04_suggested 08_page`. `08_page` reads `RESULT delta_S=+1.1717`, `duplication_copies=68->62`, `perturbed_delta_S=+0.0000`, `perturbed_vector_equals_baseline=1`, which is #2238's figure for D7-s2-56. `04_suggested` (arm B's) reads `+0.1880`, `68->67`.
- the finder's widget harness `wizard_widgets.py` from `3930b421a` (`$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`, sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`), copied into a `git archive` of each tree: base and head both read `wizard_fields=46 in_registry=44 spelled_twice=44 disagree=0 golden_equal=1`. `--all` reads `other_spelled_twice=20` on both, and `--bump heat_pump_cop_nominal` reads `disagree=2` on both. Arm A leaves the wizard alone (arms C and C2 move it), so this harness reads flat by design. Its use here is `golden_equal=1` on both trees.
- architecture score, `Architecture score: dS +2.3483 IMPROVES`, `duplication_copies 35 -> 29 +2.3483`: `python3 tools/audit/archscore/score.py --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4`. This is the design's arm-A row (+2.3483). A3' moves no scored metric.
- structural ratchet: `class_excess_loc` 18038 -> 17992 re-recorded (`python3 tests/structure.py --record`; the reason is in commit `e7a8a3fc3`'s message). After it, `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- scoped gate, `MODE: SCOPED -- 13 script(s) run, 20 scoped out`: `python3 tests/closure.py select --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4 --workdir <dir>`. The 13 are `arch_score_head`, `config_flow_steps`, `deployment_shape`, `doc_claims`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`, `harness_headers`, `manual_plan`, `structure` and `typing_ruler`. Run here: `config_flow_steps`, `structure` and `golden`. `GOLDEN_MODE=drift python3 tests/golden.py`, taken at `8bdab62ce` (whose `config_flow.py` is this head's), exits 0 and prints `ok config_flow is byte-identical to origin/main here`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. The rest are CI's.
- the gate, at the previous commit `1eaa4e140`: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` printed `PRE-PR: 1eaa4e140db22b567e80090832a90693af79419a 000000000000000000000110001011`. Its four refusals were this body's `## Unpinned sites` spelling, `## Red checks` and `## Forward-carry`, all three rewritten since, and `no-copies` (`COPY-CLAIMED: tests/config_flow_steps.py defines '_stored_rows', which is production's price_model._stored_rows`), which this head's rename answers. At this head `bash tools/pr/prepr.sh --body-check <this body>` prints `PR-BODY: 0 error(s)` and `CARRY-AUDIT: 1 finding item(s): 1 routed`. `open_pr.sh` re-runs the full prepr on this head.
- three-dot diffstat: 20 files changed, 750 insertions(+), 305 deletions(-): `git diff --stat 6d86acc909f7fc465e5736771daf8fa45c1373a4...HEAD`. Production: `config_flow.py` +251/-251 (`git diff --numstat`).
- the branch touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`: `git diff --name-only 6d86acc90...HEAD -- <those five> | wc -l` prints 0.

**#2238's findings, each dispositioned** (this pull request writes no closing keyword; the group's last pull request carries #2238's):

- D10-s1-51: fixed by #2290 (R10-SERVICES-GUARD, merged `d8c13ac5b`).
- D2-s2-01: fixed by #2365 and #2368 (R10-PUMP-MODEL, merged `413944b67`, `499f952b0`).
- D7-s2-01: fixed by #2527 (R10-FREQ-DEFROST, merged `4b36dc730`).
- D7-s2-51 (weakened), D7-s2-52, D7-s2-53, D7-s2-54: fixed by #2379 (R10-SENSOR-PAYLOAD, merged `5756f2b15`).
- D7-s2-55: this group, arm B (the next pull request).
- D7-s2-56: fixed here.
- D7-s2-57: fixed by #2819 (R10-ARCH-SHAPES, merged `4f3c73020`).
- D7-s2-59: fixed by #2282 (R10-TARIFF, merged `4c01a3dc2`).
- D8-s1-01: fixed by #2819 (R10-ARCH-SHAPES; #2379's roster note hands it there).

The issue's 17 beyond-finding sweep instances are not findings in its table; the issue body records them as folded into `dev/audit/config/bugclasses.json` by `fold_ledger.py`. They are named so the group's closing pull request can disposition them.

## Red checks

No check has run on this head yet. Two reds are predicted, and both are answered before the push:

- `tests / mutation`: `ci_predict.py --base origin/main` predicts the 24 unpinned sites above. `mutation-autofix` pins the killed ones on the pull request (`ci-autofix.md`), so no seat commit duplicates it. The cheaper detector is `ci_predict.py` itself, which already runs in `body_push.sh` before every handoff at seconds of cost, and it named all 24 here.
- `tests / closures`: `ci_predict.py` predicted one `INERT READS` red, because the new harness is an inert read of `tests/harness_headers.py`. It was repaired before the push by `ci_predict.py --apply-inert` (commit `1eaa4e140`), after which the predictor prints `no closures, fast, wave-script or instrument red predicted`.

## Forward-carry

- The group's remaining arms (B, C/C2, D) and the design's carries not discharged here: `ledger-rekey` for arm B (the two `_options_suggested_numeric`/`_suggested_entity` rows; arm C's five wizard rows keep their anchors), `c19-dr`, `literal-clones`, `dr1-b-c2-conflict`, `close-2238` and `dr1-close-2238-disposition`. They stay on the group, whose next pull requests (`handoff/r10-configflow-b`, `handoff/r10-configflow-c`, then arm D) discharge them. It lands in `dev/programme/rosters/wave-r10-groups.json`, group R10-CONFIGFLOW-PAGES. Carry: R10-CONFIGFLOW-PAGES

## Friction

none

