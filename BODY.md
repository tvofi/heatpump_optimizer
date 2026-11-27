R11-LATE-P1-OPTIONS (late class sweep P1, finder box SW7; report `dev/audit/rounds/round11/sweep/P1/REPORT.json`). A config-entry option stored as a non-number raised out of the readers that coerced it with a bare `float()`. The migration's repair (`entry_config.number_repairs`, D1-s2-05) runs only when it stamps the version, so a value written past it still reached them. Each reader now coerces through `finite_float`, the entry's own numeric parse, and reads a non-number as its default. A reader whose `or DEFAULT` fallback read 0 as unset keeps that fallback. `bool`, NaN and infinities now read as the default too.

**The claim and its set.** The set is every unguarded `float()`/`int()` coercion in `custom_components/heatpump_optimizer/` of a value read off a mapping. The rule is `dev/audit/harnesses/stored_option_coercions.py`, landed here: the `.get(...)` sits in the coerced expression, or in the assignment of a local name the coercion reads; a `try` catching `TypeError`/`ValueError`/`Exception` counts as guarded. The claim: no seam that rule prints at the head coerces a raw stored config-entry option. Each seam's disposition is under `## Figures`. The sweep's own `opt-float` rule (`p1_seams.py`) keys on the receiver's name, so it missed readers whose mapping is called `current`, `answers`, `stored` or `updates`. The wider rule returned the brief's four readers and ten more reader functions of a stored option. All fourteen are closed here (listed below); they are the 21 seams the rule prints at the base and not at the head.

**Readers closed** (production symbol, stored key):
- the brief's four: `config_flow._effective` (deleted: it was a copy of `comfort_band.effective`; its five callers now use that one reader), `topology.describe_setup` (`wood_tank_volume`), `topology._slot_extras` (`mixing_valve_target`), `quiet_windows.measured_ceiling_kw` (`compressor_freq_min_hz`, `compressor_freq_max_hz`);
- `comfort_band.effective` (every key the band rules and the options flow's cross-field rules read). D1-s2-05's judged site: it raised past the migration;
- `thermal_model.ThermalParameters.from_config` (`wood_tank_volume`, `mixing_valve_target`, `buffer_max_temperature`, `max_temperature`) and `thermal_model._flow_curve_values` (`target_temperature`). The first two keys are D1-s2-05's judged sites;
- `presets.preset_from_config` (`upper_floor_area_ratio`; `heated_area_m2`, which `presets.grade` passes the stored configuration as answers for);
- `modbus_prefill._plant` (`heat_pump_cop_nominal`);
- `quick_setup.derive` (`heated_area_m2`: the options page's quick-setup baseline copies each stored questionnaire key, so a bare post hands it the stored value) and `quick_setup.stored_answers` (`buffer_tank_volume`: a non-number gives no answer, as absent does);
- `config_flow._dhw_min_too_close` and `services.handle_apply_schedule` (`dhw_setpoint`, `dhw_min_temperature`) through the new `comfort_band.dhw_deadband`, and `config_flow._uncapped_schedule_errors` (`silent_mode_fraction`) through `comfort_band.effective`.

**Design.** `comfort_band.effective` is the one reader of "the value a save would leave in force": its parameters widen to `Mapping`, and the options flow's copy is deleted. `comfort_band.dhw_deadband` owns the hot-water pair and its ceiling. With both callers reading the pair through `effective`, `structure.py`'s `duplication_copies` read the options page and `apply_schedule` as one clone class (4 > 3). The shared function removes the copy, so no budget is raised. Alternatives that lost: (a) a `try/except` per reader, the finder's perturbation. It catches the raise but leaves the coercion rule spelled 17 ways and reads `True` as 1.0. (b) Coercing once at load into the stored mapping. That is D1-s2-05's migration, which already exists and cannot see a value written after it. (c) Reading every option through the parsed `EntryConfig`. That is the sound end state, but it moves each reader's input type across modules beyond this group's scope.

**A check that encoded the old design.** `tests/entities.py`'s migration check required the comfort band to raise on an unmigrated text hour, as its control. That raise is what this fix removes. The check now requires the unmigrated read clean and still requires the migration to repair what is stored.

## Head

`cf00b99f5a1bbc314b5cb44b9528371e7b177e7f`, merge base `d66452586467967848c7cd6012c43bc955f0f9dc` (`origin/main` at `fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5` when measured, 2026-11-26T23:00Z). The repair commits `e714df49fa` and `cf00b99f5a` sit on the bot head `1bed5619cd` (its `ci: merge main` and `ci: pin killed mutants`). Every figure below `## Mutation proof`'s repair row was measured at the first handoff `e1d91dee6065` against `dbdc71faea35`; the repair adds three checks (one in `tests/features.py`, two in `tests/config_flow_steps.py`) and no production line, so it re-takes only what those checks reach.

## Mutation proof

Each mutant restores one site's pre-fix expression at the head, runs the script named, and restores the file (`git status` clean after the last). 18 of 18 killed. Every check named is in `tests/config_flow_steps.py`'s `stored_options_of_the_wrong_type` or the `R11-LATE-P1-OPTIONS` block of `tests/entities.py`; each name starts `R11-LATE-P1-OPTIONS:`.

| mutant (pre-fix expression restored) | script | red |
|---|---|---|
| M01 `comfort_band.effective` | config_flow_steps | 8 of 728: `config_flow._power_errors on stored heat_pump_min_power` / `heat_pump_max_power`, `config_flow._partload_errors on stored heat_pump_min_power` / `heat_pump_max_power` / `heat_pump_cop_partload_derate`, `config_flow._dhw_min_too_close on stored dhw_setpoint` / `dhw_min_temperature`, `config_flow._uncapped_schedule_errors` |
| M02 `topology._slot_extras` | config_flow_steps | 1: `topology._slot_extras` |
| M03 `topology.describe_setup` | config_flow_steps | 1: `topology.describe_setup` |
| M04 `quiet_windows.measured_ceiling_kw` min Hz | config_flow_steps | 1: `quiet_windows.measured_ceiling_kw on stored compressor_freq_min_hz` |
| M05 same, max Hz | config_flow_steps | 1: `... on stored compressor_freq_max_hz` |
| M06 `from_config` wood-tank volume | config_flow_steps | 1: `thermal_model.ThermalParameters.from_config` |
| M07 `_flow_curve_values` | config_flow_steps | 1: `thermal_model._flow_curve_values` |
| M08 `from_config` mixing-valve target | config_flow_steps | 1: `... from_config on stored mixing_valve_target` |
| M09 `from_config` buffer ceiling | config_flow_steps | 1: `... from_config on stored buffer_max_temperature` |
| M10 `from_config` comfort ceiling | config_flow_steps | 1: `... from_config on stored max_temperature` |
| M11 `preset_from_config` upper-floor share | config_flow_steps | 1: `presets.preset_from_config` |
| M12 `preset_from_config` heated area | config_flow_steps | 1: `presets.preset_from_config on stored heated_area` |
| M13 `modbus_prefill._plant` | config_flow_steps | 1: `modbus_prefill._plant` |
| M14 `quick_setup.derive` | config_flow_steps | 1: `quick_setup.derive on stored heated_area` |
| M15 `quick_setup.stored_answers` | config_flow_steps | 1: `quick_setup.suggested_answers` |
| M16 `config_flow._uncapped_schedule_errors` | config_flow_steps | 1: `config_flow._uncapped_schedule_errors` |
| M17 `comfort_band.dhw_deadband` (both reads) | config_flow_steps | 2: `config_flow._dhw_min_too_close on stored dhw_setpoint` / `dhw_min_temperature` |
| M18 same mutant | entities | 2 of 2781: `apply_schedule reads a wrong-typed stored DHW setpoint or minimum as its default`, and the entry-reader census `no migrated module reads a key off a mapping outside a dispositioned site; ...`, which the mutant's raw `candidate.get` trips |

Repair row, at `e714df49fa`: M19 `quick_setup.stored_answers` bound `volume >= BUFFER_STORE_MIN_VOLUME` to `>` (the CI mutation table's `CMP_BOUND` at that line). `MUTANT_CMD` below exits 1, failing `a stored buffer volume at the store minimum reads yes, under it no  [stored=[(100.0, {'buffer_tank': False}), ('100.0', {'buffer_tank': False}), (99.0, {'buffer_tank': False})]]`; restored, it exits 0 (`ALL 1 FEATURES BLOCK PASSED`). The 99.0 arm is the control both bounds pass. `MUTANT_CMD`: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from heatpump_optimizer import quick_setup as _qs' --prelude '_qs_stored = _qs.stored_answers' "# The buffer question's bound is inclusive" 'R.section("P8 — a price or temperature entity'`.

Driver: `$SCRATCH/mutfinal.py` (out of tree; each row is the literal pair it swaps). The failing-test-first commit `6afdfa3f63` adds the brief's four readers' checks before their fix commit `ad25815a2c`. At the merge base those checks read 9 of 704 red; the vacuous pair `_power_errors` × derate was dropped before the fix.

## Null control

- Every reader's arm has a well-typed control: the stored value is read, not replaced by the default (e.g. `null -- a well-typed stored floor above the ceiling is still refused`, `null -- apply_schedule still refuses against a well-typed stored setpoint`). Every control passes at the head, and every mutant leaves its control green.
- The finder's probe (`dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_probes.py`, sha1 `c3329ae93e605d234a3199968163f02b4a2c7792`): its null arms read 0 at both ends. Its `--perturb config-effective` arm reads 0 at the base.
- `stored_option_coercions.py` refuses unless its planted module reads exactly one `direct` and one `via-name` seam and not the guarded call.

## Figures

All run with `PYTHONPATH=tests/hastub:.` at the merge base (B) and the head (H).

- `python3 dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_probes.py`: `config_effective_stored_wrong_type_raised` B 20, H 0; `opt_other topology.describe_setup` B 3, H 0; `opt_other topology._slot_extras` B 3, H 0; `opt_other quiet_windows.silent_cap_kw->measured_ceiling_kw` B 3, H 0; every `null` 0 at both.
- `python3 dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_seams.py` (sha1 `22c4de9babe2ff4b9ea7119da019435e4fc96f3c`), `RESULT opt-float`: B `seams=12 flagged=7`, H `seams=5 flagged=0`. The seven flagged at B were the brief's four plus `comfort_band.effective`, `ThermalParameters.from_config` and `_flow_curve_values`, all closed here. The five left are guarded by a `try`.
- `python3 dev/audit/harnesses/stored_option_coercions.py .` (`RESULT` lines): B `float_direct=58 float_via_name=46 int_direct=8 int_via_name=5 seams=117`; H `float_direct=41 float_via_name=42 int_direct=8 int_via_name=5 seams=96`. Keyed by (coercion, spelling, file, function) so line moves cancel, the B and H sets differ by 21 seams gone and 0 new. The gone seams fall in exactly the fourteen functions listed above, and no seam appears at H that B lacked. Disposition of the 96 at H by what the `.get` reads (traced to its assignment or the caller passing it):
  - **computed in-memory** (the integration's own plan, current action, pending prediction, simulation result, payload, diagnosis inputs, issue data, its own rows): `binary_sensor.py:199`; `climate.py:145`; `coordinator.py` 1259, 1260, 2493 ×2, 2494, 2499, 3269, 3270, 4940, 4941, 5578, 7663, 7694, 8806, 8876 ×2, 8959, 8964 ×2, 8965, 10048, 10049, 10233, 10590, 10882, 11008, 11018, 11019, 11022; `diagnosis.py` 58–64, 71, 72, 107; `duty_switch.py:582` ×2; `entity.py` 66, 99, 102; `ledger.py:368`; `pump_arbiter.py:874`; `repairs.py` 41, 51; `sensor.py` 1620, 1654, 2978, 3080, 3081, 3082, 3097; `topology.py` 739, 1214. `quiet_windows.py:194`: its `int()` reads an action code `step_actions` computes from the stored window spec; the spec itself is never coerced there;
  - **persisted store payload** (the store boundary's class, `tests/finite_boundary.py` arm 4; not this claim's set): `coordinator.py` 8276, 8361, 8403 ×2, 9296, 9300 ×2, 9421 ×2; `dhw_draws.py:126`; `flow_lift.py:243`; `heat_curve.py` 431, 582; `learner_progress.py:110`; `ledger.py` 188, 189, 431 ×2, 437 ×2, 454, 455, 473, 474; `wear.py` 192, 206;
  - **external feed or Home Assistant core**: `coordinator.py` 2428, 4342, 9463, 10885 (`p.get("total")` over the price rows `price_model` parses), 7125 ×2 (`hass.config` latitude/longitude, read by `getattr`; the rule matched the name, not a `.get`);
  - **service or form data a schema coerced first**: `services.py` 910, 922 (`vol.Coerce(float)`), `climate.py` 324, 334 (Home Assistant's `climate.set_temperature` schema; not in this tree, unverified here).
- Seams classified by reading each function; the classification is not a rule's output, and each line above is its record.
- `python3 tests/structure.py`: no violation at H. `module_excess_loc` and `class_excess_loc` re-recorded down (commits `90ba663b81` and `5f62ad4f2c`); `duplication_copies` stays at 3.
- `python3 tools/audit/archscore/score.py --diff dbdc71faea358a95a7b33840ed252b0d8a646a31`: `Architecture score: dS +0.0000 NULL`; `shape_copies 32 -> 30 (gate only)`.
- `python3 tests/closure.py select --diff dbdc71faea358a95a7b33840ed252b0d8a646a31 --workdir "$D"`: `MODE: SCOPED -- 28 script(s) run, 6 scoped out.`
- Every script `"$D"/scope.run` names, plus `tests/run.sh`'s `run_always` lines (`tests/env_drift.py --claims-only origin/main`, `tests/closure.py selftest`, `tests/layout.py`), exits 0 at H with no counted failure under `PYTHONPATH=tests/hastub`. `tests/stress.py` ran last and alone, after the mutation driver finished. An earlier stress run at an intermediate head, sharing the CPU with four other scripts, read one memory arm over its recorded budget; it is not reproduced at H.
- `GOLDEN_MODE=drift GOLDEN_REF=dbdc71faea358a95a7b33840ed252b0d8a646a31 python3 tests/env_drift.py --all dbdc71faea358a95a7b33840ed252b0d8a646a31`: `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`; no claim file is touched.

## Unpinned sites

`python3 tools/pr/ci_predict.py` at the head lists seven added unpinned sites, all under `custom_components/`, the lane `mutation-autofix` pins:
- `custom_components/heatpump_optimizer/comfort_band.py:96 RETURN_DEL` (`effective`): pinned by `mutation-autofix`; M01's eight reds show a value check kills it.
- `custom_components/heatpump_optimizer/comfort_band.py:111 RETURN_DEL` (`dhw_deadband`): pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/config_flow.py:1060 CMP_BOUND` (`_dhw_min_too_close`): pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/config_flow.py:1060 RETURN_DEL` (`_dhw_min_too_close`): pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/config_flow.py:2455 CMP_BOUND` (`_uncapped_schedule_errors`): pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/config_flow.py:2455 GUARD_OFF` (`_uncapped_schedule_errors`): pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/quick_setup.py:145 CMP_BOUND` (`stored_answers`): pinned by `mutation-autofix` once a driver kills it. At `1bed5619cd` none did: `mutation-autofix` pinned the other six (`1bed5619cd`'s six ledger files) and left this one, so `tests / mutation` stayed red. No check put a volume on the bound. The repair's `tests/features.py` check reads exactly `BUFFER_STORE_MIN_VOLUME` (float and text) as yes and one litre under as no, and kills it (M19).

Diff mutants (40 drawn, file order, over `d66452586467...HEAD`'s added production lines; `MUTANT_CMD` is `## Mutation proof`'s, without its `PYTHONPATH=tests/hastub` prefix, which is exported instead). `MUTANT_CMD` runs only the M19 block, so `prepr.sh` read `WARN     diff mutants           31 survivor(s) on the diff's added lines -- each owes a killing check or a line under ## Unpinned sites (fixer.md step 2)` at `e714df49fa` and again at `cf00b99f5a`. Each survivor was then re-run under the scripts the first handoff's mutation proof used:
- `mutant_run.py --diff d66452586467...e714df49fa --cmd "python3 tests/config_flow_steps.py" --max-mutants 40 --report-only`: rc 0, 4 `SURVIVED` lines (`config_flow.py:978 CMP_BOUND`, `quick_setup.py:145 CMP_BOUND`, `services.py:1104 STMT_DEL`, `topology.py:392 CONST_SWAP`). The other 36 are killed by `config_flow_steps.py`.
- `quick_setup.py:145 CMP_BOUND`: killed by M19's `tests/features.py` check.
- `services.py:1104 STMT_DEL` (`handle_apply_schedule`'s `dhw_deadband` read): killed by `tests/entities.py`, rc 1 (`NameError: name 'wanted' is not defined`); 2788 of 2788 pass at the head.
- `config_flow.py:978 CMP_BOUND` (`_power_errors`, `>` to `>=`) and `topology.py:392 CONST_SWAP` (`_slot_extras`, `or 0.0` to `or 1.0`): both survived `config_flow_steps.py` and `entities.py` at `e714df49fa`. Both predicates are base text the fix carried through its rewrite. `cf00b99f5a` adds `a stored floor equal to the ceiling is not refused` and `an unset mixing-valve target publishes a 0.0 setpoint` to `config_flow_steps.py`. Each mutant now exits 1 on its own check (`[{'manual_setpoint': 1.0}]` for the second); restored, the script reads `ALL 730 checks PASSED`. The strict bound is a design choice, recorded in the check's comment: a floor equal to the ceiling is a fixed-output pump.
- `quick_setup.py:186 STMT_DEL` (`derive`'s `heated_area` read, a `--path quick_setup.py` run of `MUTANT_CMD`): killed by `tests/config_flow_steps.py`, rc 1 (`NameError: name 'heated_area' is not defined`).

The six pins whose lines this diff rewrote (`config_flow.py` `_effective`, `_dhw_min_too_close` ×2, `_uncapped_schedule_errors` ×2; `comfort_band.py` `effective`) are deleted in `e1d91dee60`, as `ci_predict`'s ledger arm directs.

## Architecture score

`python3 tools/audit/archscore/score.py --diff dbdc71faea358a95a7b33840ed252b0d8a646a31` reads `dS +0.0000 NULL`: no gate rise. The structural gains are in `tests/structure.py` instead: the deleted `config_flow._effective` copy and the shared `comfort_band.dhw_deadband` lower `module_excess_loc` and `class_excess_loc`, and keep `duplication_copies` at its budget.

## Red checks

- `tests / mutation`: red at `1bed5619cd`, step `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3`: `ADDED UNPINNED custom_components/heatpump_optimizer/quick_setup.py:145 CMP_BOUND` / `MUTATION TABLE REFUSED -- 1818 unpinned site(s) against 1818 at the ratchet base ..., 1 of them added by this diff`. Null control: the same command at `origin/main` `fd93aa3e9b16` prints `MUTATION TABLE PASSED (empty scope)` (rc 0), and at `1bed5619cd` the same refusal (rc 1). Cause: the first handoff's `## Unpinned sites` read every added site as pinned by `mutation-autofix`, but that lane pins only a site a driver kills, and none killed this one. Cheaper detector: one exists, `prepr.sh`'s diff-mutant step (`mutant_run.py --diff` under `MUTANT_CMD`), which reports a `SURVIVED` line for a site no check kills. Its standing cost is that step's run per `prepr.sh`, already in the path when `MUTANT_CMD` is set. The first handoff's body quotes no `diff mutants` line, so whether that step ran is not on record, and the process state is left to the separate root-cause seat (`defect-root-cause.md`). Every handoff since the FG-3 trial brief (2026-11-26) must quote that line, which is the countermeasure already in force. This repair builds none.
- `gate`: red only because it reads `tests / mutation` (`FAIL tests / mutation: failure (this run)`). Its answer is the one above.
- `ci predict` (prepr refusal at the first handoff): `PREDICT governance / instrument-self-tests STEP REPLAY Show the verdict bus refusing its own fixtures: rc 1 at the head, 0 at the base`, on two consecutive `prepr.sh` runs. The diff cannot reach it: the step runs `bash tools/audit/seat/bus.sh --self-test`, and `git diff --stat dbdc71faea35...e1d91dee6065 -- tools/` prints nothing. With the committer date pinned to `2005-04-07T22:13:13 +0000`, `bus.sh --self-test` exits 1 at the head and at the base alike, so the replay's rc 1 follows from the environment, not the diff. `governance / instrument-self-tests` concluded `success` at `1bed5619cd`.

## Forward-carry

none

## Friction

none
