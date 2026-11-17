R11-SERVICE-SCHEMA-P2: an explicit `silent_mode_power_fraction: 1.0` now resets a stored lower fraction, and `set_thermal_parameters` refuses a `dhw_legionella_temperature` above the 70 °C hard maximum. Carries 2 and 3 are built under rulings; carries 0 and 1 had already landed on main.

**Rulings.** The previous seat stopped on two questions (BLOCKED.md on `handoff-wip/r11-service-schema-p2` at b7b0010759). The orchestrator ruled on both under the owner's overnight autonomy mandate, taking the recommended option each time. Both rulings are reversible on owner review:
- (a) carry 56724b85: an explicit 1.0 is applied, not dropped;
- (b) carry bde9263f: the range narrows to `vol.Range(min=55, max=70)`.

**User-facing behaviour changes (for the release notes).**
1. `apply_schedule` with `silent_mode_power_fraction: 1.0` now stores 1.0 and replaces a stored lower fraction. Before, it kept the stored fraction. Leaving the field out still keeps the stored one. The same rule now applies in two more places, described under Carry 2: a `simulate_plan` what-if and `set_thermal_parameters`' live configuration. Card consequence: the quiet-window save posts the slider's value. The slider is pre-filled from the plan sensor, which publishes the fraction only while quiet rows exist. So on an install that stored a fraction below 1.0 and then removed every quiet row, the next save from that page stores the 1.0 the slider shows.
2. `set_thermal_parameters` now refuses a `dhw_legionella_temperature` of 71-75 °C. Before, it accepted those values, but no cycle wrote above the 70 °C hard maximum (`ThermalParameters.dhw_hard_max_temp`). The service selector and the config flow already stopped at 70. A 71-75 stored by an earlier release is not migrated: the guard still caps it at 70 and raises the unreachable notice, and `tests/guard_pins.py`'s range census keeps driving 55-75 for that reason.

**Carry 0 (5375ae6f) and carry 1 (7965f82b): already on main, built nothing.** Both are on main through #3677 (commit 6d369cd68f, an ancestor of this base). The previous seat measured them at this base, in BLOCKED.md b7b0010759:
- `SERVICE_SCHEMA_SIMULATE_PLAN` refuses each selector-bound probe, with `min_temp 20` accepted as the null control;
- no `apply_manual_plan` field in `services.yaml` carries an `example`.

**Carry 2 (56724b85): built.** `_quiet_schedule_fields` in `services.py` stores the fraction whenever the call names it. Step 8 enumerates the class as every site that folds a call's fraction (command in Figures). It finds three sites at the base, and all three dropped an explicit 1.0:
- `services._quiet_schedule_fields` (apply_schedule): the carried site, changed;
- `quiet_windows.overridden_config` (simulate_plan's what-if fold): changed, so a what-if prices the fraction the save would store;
- `quiet_windows.apply_config_keys` (set_thermal_parameters' live-config fold): changed, so the live configuration equals the options the same call persists. `_with_quiet_keys` documents that equality as what lets the update listener skip a reload.

Changing the two sibling folds goes beyond ruling (a)'s literal scope (apply_schedule). It is the same decision applied to the same field. Leaving them unchanged would make a simulate_plan preview of 1.0 disagree with what apply_schedule stores. That is disclosed here for the owner's review with the ruling.

Alternative considered: change only `_quiet_schedule_fields`. Rejected because the preview would then disagree with the save, as above.

**Carry 3 (bde9263f): built.** The schema's top is now 70, with a comment naming the cap. Field text changed:
- the `dhw_legionella_temperature` description in `strings.json`, `en`, `sv` and `de` now states 55 to 70 °C and the cap;
- `docs/configuration.md` says 55–70;
- `legionella.OffStepNotice`'s docstring now names a stored 71-75 from an earlier release, not a service-set one.

`tests/entities.py` registers the description's "55 to 70 °C" in `_UT_NUMBER_CLAIMS` against `ThermalParameters(dhw_setpoint=90.0).dhw_hard_max_temp`. That way the text and the cap cannot drift apart unnoticed.

The `apply_schedule` and `simulate_plan` fraction descriptions in all four catalogs no longer say "1.0 is the unset value: sending it changes nothing". They now say that 1.0 caps nothing and that leaving the field out keeps the stored fraction.

## Head

prepr: passed rc=0 at e84f984783d26a99141b4b9d9ea8b81a9db9da32 (`PREPR_SKIP_CLOSURES=1`, the scoped gate run above; `MUTANT_CMD` the block's `features_block.py` call, `MUTANT_IN_PLACE=1`: no survivor).

`e84f984783d26a99141b4b9d9ea8b81a9db9da32`, merge base `38bf516bdd73f926ee9639ffda7b9ca5163fd50e` (the base the brief gave). origin/main was at `38bf516bdd73f926ee9639ffda7b9ca5163fd50e` at 2026-11-17T01:40Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

Four mutants, each applied to its production line and run through `tools/audit/seat/features_block.py` over the new block (`--emit-prelude` derived; start `_et_quiet_hass = FakeHass()`, end `_et_quiet_set = _et_call(`). Each file was restored afterwards:
- M1 `services._quiet_schedule_fields`: `if CONF_SILENT_MODE_FRACTION in data:` → `if data.get(CONF_SILENT_MODE_FRACTION, 1.0) != 1.0:`. Fails `apply_schedule with an explicit 1.0 resets a stored 0.6 to 1.0`.
- M2 `SERVICE_SCHEMA_SET_THERMAL_PARAMS`: `vol.Range(min=55, max=70)` → `max=75`. Fails `set_thermal_parameters refuses a 71 °C disinfection temperature and accepts 70`.
- M3 `quiet_windows.overridden_config`: `if CONF_SILENT_MODE_FRACTION in overrides:` → `if overrides.get(CONF_SILENT_MODE_FRACTION, 1.0) != 1.0:`. Fails `the what-if and live-config folds apply an explicit 1.0 over a stored 0.6 and keep it when absent`.
- M4 `quiet_windows.apply_config_keys`: the same predicate swap on `params`. Fails the same check.

Each block exited 1 with only that check failing.

Ledger: the three fold predicates moved off `if fraction != DEFAULT_SILENT_MODE_FRACTION:`, so their `killed_by` pins GUARD_OFF 8780e9c7 named no site (`ci_predict.py`'s `STALE PIN`). Each is re-keyed under `tests/mutation_ledger/killed_by/` to its new line (`_quiet_schedule_fields` 1f9e8473, `overridden_config` b6bb9a79, `apply_config_keys` df339fe0). GUARD_OFF (`if False:`) on each line was driven through the same block:
- `services.py` failed the 0.7 acceptance check and both new fraction checks;
- each `quiet_windows.py` line failed the sibling-fold check.

The unmutated block passed.

`prepr.sh`'s diff mutants (`MUTANT_CMD` = that `features_block.py` call, `MUTANT_IN_PLACE=1`) left one survivor: `services.py` `CONST_SWAP` `vol.Range(min=56, max=70)`. It is now killed by `set_thermal_parameters accepts a 55 °C disinfection temperature and refuses 54`; under the mutant, 55 is refused.

Failing test first: the block at the unfixed tree failed `apply_schedule with an explicit 1.0 resets a stored 0.6 to 1.0` (`stored 0.6`) and `set_thermal_parameters refuses a 71 °C …` (`71 raised None`). The sibling-fold check, added before its fix, failed with all four readings at 0.6.

## Null control

- Absent field, same entry: `apply_schedule without the fraction keeps a stored 0.6`. It passes at both the unfixed and the fixed tree. The sibling-fold check's `absent` arms read 0.6 at both trees.
- 70 °C: accepted at both trees (the `70 raised None` arm of the legionella check). 71 and 75 move from ACCEPTED to REFUSED (probe in Figures).

## Figures

- Before/after probe, `PYTHONPATH=tests/hastub:custom_components python3 probe.py`. It is a scratch probe, sha1 `4477a48060b3437d811be5d6bbab646ba594d49b`, reading only the production symbols named below.
  - At 38bf516bdd: `_quiet_schedule_fields({fraction: 1.0})` dropped; `overridden_config` 0.6+1.0 → 0.6; `apply_config_keys` 0.6+1.0 → 0.6; schema 70/71/75 ACCEPTED/ACCEPTED/ACCEPTED.
  - At the head: 1.0; 1.0; 1.0; ACCEPTED/REFUSED/REFUSED.
  - The absent arm reads dropped at both ends.
- Class enumeration (step 8): `git grep -nE 'CONF_SILENT_MODE_FRACTION|"silent_mode_power_fraction"' <sha> -- 'custom_components/heatpump_optimizer/*.py'`, excluding imports and `const.py`.
  - At 38bf516bdd it returns fold sites `quiet_windows.py:556`, `quiet_windows.py:575` and `services.py:388`: all three changed in this diff.
  - Non-fold rows: `config_flow.py:1923` (option field, stores what the flow submits), `quiet_windows.py:420` (reads the configured fraction, no call input), `sensor.py:127` (publishes), and the three schema rows in `services.py`. None drops a call's value.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 38bf516bdd73f926ee9639ffda7b9ca5163fd50e` printed `Architecture score: dS +0.0000 NULL`.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scoped gate, run at c22c267e2f. Since then the head adds only the ledger re-key and the 55/54 check, and the block holding that check passed at the head (`ALL 7 FEATURES BLOCK PASSED`): `GATE_SCOPE=auto GATE_SCOPE_BASE=38bf516bdd GOLDEN_MODE=drift GOLDEN_REF=38bf516bdd bash tests/run.sh` at the head printed `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, rc 0.

<!-- figure-block: scope-line mb=38bf516bdd73f926ee9639ffda7b9ca5163fd50e head=e84f984783d26a99141b4b9d9ea8b81a9db9da32 -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
