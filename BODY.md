R11-SEAM-dead-state (ADR-001 decision 4; D7-s3-05, D7-s1-03 of #3779; #3779 stays open for its other findings). This PR deletes state that production stores and no production code reads, in the module that holds it and at its callers. No behaviour changes. The sets come from the finding's own harnesses: `m6_inner.py`, `m6_dead.py` and `m1_ratchet_census.py` under `dev/audit/rounds/round11/D7/`. Each row they print at the base is listed under `## Figures` with its disposition.

No `BLOCKED.md` from a previous seat exists on any ref of this topic (`git ls-remote origin 'refs/heads/*r11-seam-dead-state*'` lists only the dispatch and comms refs), so there was no option to take. The gate is open: R11-SEAM-store (#3875) is on main at `dc2b2bab31`.

Deleted:
- the five package import bindings no importer loads: `DHW_PROFILE_STORE_VERSION`, `CONF_UPPER_FLOOR_THERMAL_MASS`, `MIN_RUNNING_DRAW_KW`, `channel_heating_steps` and `quantise_setpoint_c`. The other nine of D7-s1-03's fourteen had already left main. `tests/guard_pins.py` now imports `channel_heating_steps` and `CHANNEL_ACTIVE_KW` from their owner, `thermal_model`.
- four unused stdlib imports.
- eight unread parameters, each removed at every caller: `_observe_frequency(now)`, `record_miss(now)`, `_baseline_dhw_economics(initial_state)`, `_floor_demand_terms(outdoor_temp)`, `_solve_space(n_steps)`, `_power_to_setpoints(outdoor_temps)`, `slab_mode_identifiability(config)` and `window_factors(dt_hours)`. Dropping `config` from `slab_mode_identifiability` left `adoption_decision(config)` unread, so that goes too.
- seven unread locals.
- state that copies an input, a flag nothing in production sets, and fields no check reads:
  - `_last_manual_setpoint` (the deleted test message said the climate entity reads it back; nothing in production does).
  - `draws_dirty` (production only ever clears it).
  - `FlowCurveBias.last_return_c`, together with `observe_temps`' `return_temp`. `observe_water` still passes both temperatures to `read_heat_output_kw`.
  - `DhwPlan.external_heat_suppressed_steps` and the arithmetic that fed only it.
  - `PVConfig.export_price_entity`. `_pv_export_price` reads the entity from the entry config.

Left, by category:
- **Fixed by a uniform invoker (protocol).** The signature is set by a caller that invokes a family of functions alike: `entry_config`'s six helpers' `default` (`_key(default, helper)`), `_configured(cap)` (the `_FEEDBACK_CLASSES` probe slot) and `handle_run_optimization(call)` (the HA service handler).
- **Production reads it.** These four `CONF_*` constants are read by `getattr(const, f"CONF_{conf}")` (`tests/structure.py` `DYNAMIC_REFERENCES`, sentinel-proven in `tests/features.py`): `CONF_BUFFER_TANK_LOSS`, `CONF_SOLAR_UPPER_FRACTION`, `CONF_HOUSE_HEAT_LOSS_SCALE` and `CONF_LOWER_FLOOR_LOSS_RATIO`. The harness reads names only, so it counts them as test-only.
- **A computation's only observable, pinned by a check.** The value is a decision or ledger production computes, and deleting it deletes the check: `_slab_fit_used`, `_step_dhw_refused`, `_step_dhw_floor_injected`, `_step_dhw_draw_kw`, `manual_pins_active` (the attribute and the field), `DhwPlan.windows_learned`, `QuietCompose.silent_dropped` and `SysIdResult.sensor_drift_c_per_h`. The architect note says to delete test-read attributes and fields. This departs from it, and the departure is raised here for the reviewer rather than made silently: each of these is one row under `## Figures`, and the choice turns on CLAUDE.md's "never delete working functionality merely to fit".
- **A stored document carries it.** `OptimizationResult.wood_temp_trajectory` is serialised by `tests/golden.py` into the golden fixtures (ADR-001: "a field a stored document carries is left").
- `dev/audit/harnesses/r10_heat_meter.py` and `r10_thermal_power_option.py` keep their two-temperature `observe_temps` calls. They archive older SHAs and measure those trees, and both already exit 1 at the base (`TypeError: Gate._learning_frozen() got an unexpected keyword argument 'sample'`). `r10_cop_gate_vent.py`, which imports the working tree, now uses the new signature.
- `_power_to_setpoints(room_temps)` stays because it bounds the `zip`. The new set-point length check now pins that bound.

## Head

`d60a2319be2bbd77f67a0e1249e7a30800f57ecb` is this PR's head after review 007cfa62 (blocking: `harness-broken`, plus one `harness-drift` note). This PR dropped `config` from `adoption_decision` and `slab_mode_identifiability` and `return_temp` from `FlowCurveBias.observe_temps`, and five round-11 finder harnesses still called the old signatures. The fix edits only those call sites, one line in each of `dev/audit/rounds/round11/D2/s3/m5_sysid.py`, `D7/s2/m2_sysid_plant.py`, `D3/s1/probe_46021727.py`, `D3/s1/fl183_nonfinite.py` and `D3/s1/probe_3885e472.py`, with no production change. Readings with `PYTHONPATH=tests/hastub`, in order base `190ffb10` / head `aeb563a7` / new head: `m5_sysid.py` rc 0 / 1 (TypeError) / 0; `m2_sysid_plant.py` rc 0 / 1 (TypeError) / 0; `probe_46021727.py` rc 0 / 1 (TypeError) / 0; `fl183_nonfinite.py` rc 0 / 0 / 0; `probe_3885e472.py` rc 0 / 0 / 0. The `RESULT` lines of all five at the new head are identical to the base's (`diff` of the `RESULT` lines excluding `load1`, `swapins`, `wall` and `thread` prints nothing). The two `Carry: R11-SEAM-dead-state` items of that review (the three-harness TypeError and the two `observe_temps` calls whose second argument now bound to `heat_output_kw`) are both done in this PR. `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` exits 0 at this head. The figures and mutation proof below are of the earlier head `aeb563a7`; this commit changes only `dev/audit/rounds/round11/` files.

Previous head:

`aeb563a713aa0b9d3587604c51dc7fb64397ec6a` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`aeb563a713aa0b9d3587604c51dc7fb64397ec6a` (the `fix/r11-seam-dead-state` tip, the `mutation-autofix` commit `ci: pin killed mutants` on `57c2f6d3`); merge base `190ffb10c230b6beaf77593b2926d55682e37f47`; origin/main `ef797d794017c98f7fb2d8a168d7de63d435ef3b` at `date -u` 2026-11-27, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. The figures below were taken at `9326a14143f37226666b2dd5620f989300bef10f` against merge base `7194ff84c09dd9d54a99f8208c906136981fd9dc`. They still describe this head's diff: `diff <(git diff 7194ff84 9326a141 -- custom_components tests dev/audit ':!tests/mutation_ledger' | grep -vE '^(index |@@)') <(git diff 190ffb10 aeb563a7 -- custom_components tests dev/audit ':!tests/mutation_ledger' | grep -vE '^(index |@@)')` prints nothing. Its null control is the same command without the ledger exclusion, which differs at the stale pin's deletion.

## Mutation proof

Each line restores one deletion into a scratch worktree at the head, runs the named check, and is then reverted:
- Re-adding `MIN_RUNNING_DRAW_KW,` to `optimizer.py`'s `thermal_model` import: `python3 tests/structure.py` prints `FAIL unloaded_package_imports 1 > 0 (+1)` and `FAIL module_excess_loc 21627 > 21626 (+1)`, rc 1.
- Re-adding `self._last_manual_setpoint = float(requested)` to `record_setpoint_override`: `tests/structure.py` prints `FAIL coordinator_attrs 134 > 133 (+1)`, `FAIL class_excess_loc 17207 > 17206 (+1)` and `FAIL max_class_loc 7760 > 7759 (+1)`. `m6_inner.py` prints `ROW write_only attribute _last_manual_setpoint` and `RESULT write_only_attributes=1`.
- Re-adding `dt_hours: float = 0.25` to `window_factors`: `m6_inner.py` prints `ROW unread_param parameter tariff.py:655 window_factors(dt_hours)` and `RESULT unread_params=9`.

The four new checks in `tests/features.py`, each failing under its mutant and passing on the head:
- `observe_water` folds the supply reading: `temps[0]`→`temps[1]` gives `last_supply_c 40.0`.
- One set-point per power step: `room_temps[:-2]` gives 95 set-points for 96 steps.
- One accuracy record takes one frequency sample: deleting `self._observe_frequency()` gives 0 calls.
- The singular sysid solve refuses with "fit gave implausible signs": deleting the `lstsq` fallback statement changes the reason.

Diff mutants. MUTANT_CMD=`bash dev/audit/harnesses/r11_dead_state_mutants.sh`:
PREPR_SKIP_CODE=1 skips prepr's step, so this is `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --report-only` at this head, 20 mutants, verbatim:

    SURVIVED custom_components/heatpump_optimizer/coordinator.py:6617 CONST_SWAP  _, still_pending = await asyncio.wait(pending, timeout=10.0)

The one survivor is dispositioned under `## Unpinned sites`. Before the four checks and the driver landed, the same diff left 14 survivors under `tests/edge.py`, `manual_plan.py`, `guard_pins.py` and `dst_checks.py` alone.

## Unpinned sites

- `custom_components/heatpump_optimizer/optimizer.py:4271 RETURN_DEL` (`HeatPumpOptimizer._peak_window_factors`) on `return window_factors(mask, start_time, n_windows)`: pinned. This diff deleted the stale pin `...RETURN_DEL.0fdad595.json`, which was recorded against the four-argument line. `mutation-autofix` committed `tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._peak_window_factors.RETURN_DEL.d5bd2655.json` (`killed_by: tests/features.py`, rc=0 failed=0 to rc=1 failed=4) at `aeb563a7`. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main` run by this seat at `57c2f6d3` printed `pinned custom_components/heatpump_optimizer/optimizer.py:4271 RETURN_DEL -- killed by tests/features.py` and `PIN KILLED: 1 pinned, 0 left unpinned`, and the file it wrote is byte-identical to the bot's (`cmp` exit 0). Carry: dismissed: pinned in this diff
- `custom_components/heatpump_optimizer/coordinator.py:6617 CONST_SWAP` (`async_shutdown`): `asyncio.wait(pending, timeout=5.0)` 5.0→10.0. The line was `done, still_pending = ...`, and this diff renames only the unread `done`. Pinning the bound needs either a task that never finishes plus a 5 s wall-clock wait, or a patched `asyncio.wait`. Carry: dismissed: this diff leaves the timeout literal unchanged, and a wall-clock pin costs 5 s on every run.

## Null control

At the base, the same harnesses print the defect, and planting one more instance moves each count:
- `m6_inner.py` prints `unread_params=16`, `unread_locals=7`, `unread_fields=1`, `test_read_only_attributes=8` and `test_read_only_fields=7`.
- `m6_dead.py` prints `unused_import=4`.
- `m1_ratchet_census.py` prints `unused_package_imports=5`.
- `m6_inner.py --perturb` at the head prints `planted_delta=1`.
- `m1_ratchet_census.py --perturb unused-import` at the head prints `unused_package_imports=1` and `ratchet_unloaded_package_imports=1`. `--perturb use-import` prints 0.

## Figures

Harness sha1s, taken at the head: `m6_inner.py` d0f3edd8d4bd2191d14af9054b813fcac24fc47b, `m6_dead.py` 9ebf92d8b78c6631e41423607985eb50b2bde178, `m1_ratchet_census.py` e2f94c69129a1e2840e5b4b83e67dab96b576f7b.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_inner.py | grep '^RESULT'`: base unread_params=16, unread_locals=7, unread_fields=1, test_read_only_attributes=8, test_read_only_fields=7; head 8 (all protocol, listed above), 0, 0, 5, 5 (each listed above as left).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_dead.py | grep '^RESULT unused_import'`: base 4, head 0. Its 9 `test_only` rows are the four dynamic `CONF_*` constants and five migration or framework members (`OLD_REFERENCE_BASIS`, `migrate_ledger_v1`, the two `_async_migrate_func`, the config-flow class), which a stored document or the framework reads. These are outside D7-s3-05's state.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py | grep -E '^(UNUSED|RESULT unused_package_imports)'`: base 5 UNUSED rows, head 0.
- `python3 tests/structure.py --record`: rows moved down, recorded with the reason in the commit message.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0153 IMPROVES` (coord_footprint 2533 -> 2531, coordinator_multiassigned_attrs 101 -> 100).
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: `MODE: SCOPED -- 30 script(s) run, 4 scoped out`. Every script named passed after the two round-3 D2 harnesses `tests/harness_headers.py` executes were moved to `window_factors`' new signature. The `doc_claims.py` comment-ratchet red on one long docstring sentence in `flow_lift.py` was split before the head.
- `HASTUB_TZ=Europe/Stockholm python3 tests/dst_checks.py` passes. Without `HASTUB_TZ` it reports 8 of 137 failing at both the base and the head, because `tests/features.py` runs it only under that zone.

## Red checks

- `tests / mutation` (required, in `merge_train.py owed-reds`), red at `57c2f6d3`: `MUTATION TABLE REFUSED -- 1817 unpinned site(s) against 1818 at the ratchet base 190ffb10, 1 of them added by this diff`, and the site is `optimizer.py:4271 RETURN_DEL`. This diff edits the pinned `return window_factors(...)` line, which re-hashes its anchor and stales the pin. Repaired at `aeb563a7` by the `mutation-autofix` pin above. `tools/pr/ci_predict.py` is the cheaper detector, already a `prepr.sh` step, and it named the site before the first handoff. `mutation-autofix` is the designed repair (`ci-autofix.md`), so nothing new is built.
- `gate` is red only because it follows `tests / mutation`. `tests / nightly-status` (red at `b6740620`, `Process completed with exit code 1.`) reports main's scheduled nightly, not this diff, and is outside the owed set.

## Forward-carry

none

## Friction

none

