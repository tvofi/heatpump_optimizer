R10-USER-TEXT-VERIFY-STRINGS (production, user-facing text; the owner's ruling of 2026-11-13, "Do 1 in round 10"): every user-visible string the integration ships outside the dashboard card and outside the config flow (`config`, `options`, `selector` are R10-CONFIG-FLOW-TEXT-VERIFY's), judged against the code that decides it, never a comment; each false string corrected in en, sv and de; each mechanically checkable claim pinned in `tests/entities.py`. The tracked record is `dev/audit/rounds/round10/user-text/RECORD.md`, one row per string in `verdicts.json` beside it.

**What was false and is corrected** (code evidence per row in RECORD.md):
- `exceptions.factory_reset_not_applied`: "nothing was changed" -- `async_factory_reset` saves the undo snapshot before the unload it is refused; now says settings and learned state are unchanged and only that snapshot was saved.
- `services.run_optimization`: "will fetch the latest electricity prices and weather forecast" -- `async_run_optimization` solves from the prices and forecast already loaded; it fetches nothing.
- `entity.sensor.plan_narrative.state.dhw_window` / `dhw_preheat`, and the same two sentences of `narrative.TEMPLATES` (en, sv, de): "needed now" / "while electricity is cheap" -- `classify_dhw_steps` tags any step inside a hot water window, and any other non-ready, non-legionella run, with no read of the clock or the price; the sensor publishes the first non-idle reason of the plan, not the current step's.
- `entity.sensor.heat_pump_action.state.pre_heat`: "Pre-heating" -- the 70-90 % normalised-power band beside eco/normal/boost, no pre-heat decision; now "High output".
- `entity.sensor.buffer_tank_temperature_model.name`: "(Model)" -- the value is the configured probe's reading and the entity is unavailable without one; now "Buffer Tank Temperature" (translation key unchanged, so an existing install keeps its entity ID; a new install's generated ID drops `_model`). README's two rows follow, and round 4's D6 claims harness is re-run over them.
- `issues.quiet_silent_not_enforced` and the `quiet_silent_windows` field of set_thermal_parameters, simulate_plan and apply_schedule: the cap applies only where a control can hold the rows (a switch as the capacity-limited entity, or a pump night schedule `silent_unenforceable` accepts), at a measured silent-mode ceiling where one exists.
- `silent_mode_power_fraction` (three services): a fraction below 0.6 is raised to `CAPACITY_FLOOR_FRACTION`, a measured ceiling takes its place, and simulate_plan / apply_schedule never fold or store an explicit 1.0 (`_quiet_schedule_fields`, `quiet_windows.overridden_config`), so there 1.0 cannot undo a stored fraction; set_thermal_parameters stores it and keeps "1.0 caps nothing".
- `simulate_plan` / `apply_schedule` `dhw_windows`: an empty string falls back to windows learned from use, or the whole day with the schedule off (`_effective_dhw_windows`), not "no demand windows" / "only its idle minimum".
- `apply_topology` `dhw` / `wood`: they switch hot water and the wood tank on or off (`CONF_DHW_ENABLED`, `CONF_WOOD_FURNACE_ENABLED`), not only the picture.
- `set_thermal_parameters` `slab_heat_transfer` ("Radiators sit far higher than a slab": the presets give radiators a fifth of a slab's value per m²) and `rain_heat_loss_multiplier` (full only at 2 mm/h or more, scaled below, none at 0.1 mm/h or less).
- `issues.dhw_legionella_above_setpoint` ("one hot day a week": every `{interval_days}` days), `issues.dhw_legionella_unverified` (quoted the field label wrongly, in de in English), `issues.grid_fee_magnitude` / `grid_fee_sign` ("DSO fee options": the page is "Transfer fees and contract").
- `services.yaml` `simulate_plan.wood_price_sek_m3` selector min 0 -> 1: `_wood_override_fuel` refuses a price <= 0, so the slider's floor computed nothing.

None of these misleads a user about what is written to the pump; the one string in this corpus about pump writes, `issues.pump_write_ignored`, is true and its "every five minutes" is pinned to `pump_arbiter.RETRY_MINUTES`.

**Pinned** (`tests/entities.py`, Services section, each with a planted null control): services.yaml names exactly the services `async_register_services` registers, each with exactly its registered schema's fields, every number selector's min and max pass the field's own validator, and the schema refuses an unnamed key (the probe the field-set read does not name); every field description stating its unit states the selector's unit; the wood price floor through `_wood_override_fuel`; and 27 numbers quoted in user text against the constant the code decides each with (`_UT_NUMBER_CLAIMS`: disinfection lost timer, refit settled days and band, snapshot cadence, the 24 h horizon in three entity names and two service texts, manual-plan window, economy widening and floor, pump write retry, legionella retry, cooling-rate references, silent capacity floor, the presets' radiator/slab ratio). A reworded phrase fails its row, so a rewrite re-reads the constant. Translations stay key-complete under the existing `entities.py` catalogue checks (`all_keys`, `en_value_drift`).
**Prose-only**: every other claim row in `verdicts.json` -- behaviour no constant names (what a repair means and clears on, what a service writes), the narrative template wording, the "four price steps" (an inline `len(prices) < 4` at two coordinator sites, no name to read), the rain thresholds (inline literals in `effective_heat_loss_coefficient`), the buffer sensor's name.

Python-built text, found by search: `enumerate.py`'s `PY_RE` (WARNING-or-above log calls, `persistent_notification`, `async_create_issue(`, `translation_placeholders`, `translation_key=`) and its template walk (module-level dicts keyed `"en"` -> string dicts; only `narrative.TEMPLATES`). There is no persistent notification or notify call in the package, `diagnostics.py` carries no label text, and `notifier.py` fires data-only events.

## Head

`ea298df445835b20bb2f7d3e85dd1036f26b8ab1`, measured against `origin/main` at `e23124ff6e45bac1d48b4a775dad555a37965355` (`2026-11-13T19:20Z`).

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Mutation proof

`python3 tools/audit/seat/mutant_run.py --spec <spec> --in-place --cmd <tests/entities.py, its FAIL lines kept>` (in place: a `git archive` copy kills the null mutant on the #363 `recorded_at` check). The null mutant SURVIVED in both runs; the planted controls `a3`-`a13`/`hb` that print FAIL on every run, the null included, are left out below.

- `wood-selector-min-back-to-0` (services.yaml `simulate_plan.wood_price_sek_m3` min 1 -> 0): KILLED -- `FAIL simulate_plan's wood price selector minimum is a price the what-if computes with [min 0]`.
- `slab-text-back-to-merge-base` (strings.json `slab_heat_transfer` back to "Radiators sit far higher than a slab."): KILLED -- `FAIL en.json equals strings.json leaf for leaf ...`, `FAIL each of the 27 numbers quoted in user text equals the constant the code decides it with [... the phrase "a fifth of a floor slab's" is gone ...]`, and its null control.
- `capacity-floor-moved` (const.py `CAPACITY_FLOOR_FRACTION: Final = 0.6` -> 0.5): KILLED -- `FAIL each of the 27 numbers quoted in user text ... [... says 'raised to 0.6' (0.6) but const.CAPACITY_FLOOR_FRACTION is 0.5 ...]` and its null control.
- `buffer-name-back-to-model` (strings.json name back to "Buffer Tank Temperature (Model)"): KILLED -- `FAIL every sensor the platform builds has a row in the README, and every row is a sensor it builds [documented not built: ['Buffer Tank Temperature']; built not documented: ['Buffer Tank Temperature (Model)']]` and the en.json drift check.

Prose-only corrections (each in RECORD.md) have no killing check by construction: reverting the narrative templates, the `heat_pump_action` label, the repair, exception and service prose leaves every check green; the null control for those is the method control below.

## Null control

- Method: a fresh judge seat, brief unchanged, given eight `issues`/`services` rows with one planted false (`dhw_disinfection_switch_lost`, "half an hour" -> "six hours"), returned exactly that row `false`, against `const.DHW_DISINFECTION_LOST_MINUTES`, and the seven others `true`. Disclosed miss rate the other way: the judge seats returned two false strings `true` (`heat_pump_action.pre_heat`, `buffer_tank_temperature_model`), which the fixer's re-read caught and overrode (`judged_by` in `verdicts.json`); the method is a seat's reading, and its record names who judged each row.
- Pins at the merge base: the pin block run over a `git archive` of the merge base fails three checks -- the wood price minimum (`min 0`), the numbers row whose phrases only the corrected text carries ("raised to 0.6", "a fifth of a floor slab's"), and therefore its null control -- and passes the unit, field-set and probe checks, which pin claims already true there.
- Each pin's own null control is in the block: a planted out-of-range selector and a planted unknown field are two findings; a planted `kW/°C` in the `kWh/°C` field is one; "six hours" in the disinfection repair is one, and a constant moved off its stated value is one; the wood price 0 is refused.

## Figures

- Corpus: `python3 -I dev/audit/rounds/round10/user-text/enumerate.py` at the merge base prints the per-source counts (strings.json `exceptions`/`issues`/`entity`/`services`, services.yaml per service, `python`, `templates`) and the translation key gaps.
- Verdict counts: `python3 -c 'import json,collections; print(collections.Counter((r["source"], r["verdict"]) for r in json.load(open("dev/audit/rounds/round10/user-text/verdicts.json"))))'`; the false rows, all with `fixed` true: `python3 -c 'import json; print([r["key"] for r in json.load(open("dev/audit/rounds/round10/user-text/verdicts.json")) if r["verdict"]=="false" and not r["fixed"]])'` prints `[]`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`; every script `scope.run` names run with `PYTHONPATH=tests/hastub` at the head, `GOLDEN_MODE=drift` for `tests/golden.py`, each exit 0.
- `python3 tests/structure.py` at the head: exit 0. `tools/audit/archscore/score.py --diff`: `Architecture score: dS +0.0000 NULL` (`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`).
- `tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD`: one mutant drawn (`narrative.py` `TEMPLATES` STMT_DEL, the dict whose sentences this diff edits), KILLED by `tests/entities.py` (`AttributeError: module 'heatpump_optimizer.narrative' has no attribute 'TEMPLATES'`); no SURVIVED line.
- Instrument self-tests: this diff touches no file an `instrument-self-tests` step names (no `tools/` file).
- `git merge-tree --write-tree origin/main HEAD` prints one tree; `refs/heads/handoff/r10-config-flow-text-verify`, `r10-hotfix-flow-setpoint-stuck` and `r10-hotfix-boost-flow-ceiling`: `r10-config-flow-text-verify` and `r10-hotfix-flow-setpoint-stuck` each print one tree (`tests/closures.json` resolved by the ledger driver as a set); `r10-hotfix-boost-flow-ceiling` does not exist (`git ls-remote` prints nothing).

## Red checks

none

## Forward-carry

- The dashboard card repeats the two false narrative labels (`www/heatpump-optimizer-card.js` `reasons.dhw_window` "Hot water needed now", `reasons.dhw_preheat` "Charging the tank while electricity is cheap", and their sv/de); `classify_dhw_steps` reads neither the clock nor the price. Carry: R11-INTAKE-R10-RESIDUE
- apply_schedule cannot set `silent_mode_power_fraction` back to 1.0: `_quiet_schedule_fields` drops an explicit 1.0 as "the default", so a stored lower fraction survives the call; the text now says so, the behaviour is a code decision for its owner. Carry: R11-INTAKE-R10-RESIDUE
- simulate_plan's `min_temp`, `max_temp`, `comfort_weight`, `comfort_temp_night` and `dhw_min_temperature` selectors bound nothing the schema enforces, and disagree with the config flow's ranges for the same settings (RECORD.md, Unverifiable). Carry: R11-INTAKE-R10-RESIDUE
- apply_manual_plan's services.yaml examples are 2024 datetimes: sent verbatim, `expires_at` is refused as not in the future and the slots overlap nothing; any absolute example ages the same way. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
