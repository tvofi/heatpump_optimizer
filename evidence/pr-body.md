Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`. Each stored key it declares has one default and one coercion. Readers in the migrated modules take the field. A mapping handed to a price reader is parsed at that boundary; an `EntryConfig` is returned unchanged. Whole-mapping parsers (thermal parameters, grid fee, topology, wood, the options form, service data, the quiet-window what-if) still take the mapping; `tests/entities.py` names each of those modules and why.

Main was merged in three times (3910026e, 38c03d94, e0f0b6fb). Each resolution keeps main's change and reads the configuration through the parsed object. `EntryConfig` declares `heat_pump_capacity_limited_entity`, `quiet_silent_windows` and `quiet_off_windows` (`""` where none is stored) for R9-SW-1/4/5. `coordinator.model_restart_advice` (#1936) reads the parsed interval; the auto-merge used names this branch had removed from the import.

### Round 1 of the review (#2025, blocked at a390f589)

- **Quiet windows apply live, as on main** (orchestrator ruling under the owner's mandate). `set_thermal_parameters` folds its quiet keys into a copy of the frozen configuration, through main's own `quiet_windows.apply_config_keys`. It then swaps the new parse onto the coordinator's context (`_with_quiet_keys`, `replace(_ctx_of(self), _config=...)`). The options write that follows equals that parse, so the update listener skips the reload. `apply_config_keys`, its `features.py` check, SW-1's live-config check and both `apply_config_keys` killed_by pins are main's again, byte for byte.
- **typing**: `mypy --strict` errors 9 to 0. Coordinator reads that went through the untyped `getattr(self, "_ctx", self)` now read the typed `effective_config` property. `ThermalParameters.from_config`, wood_fuel's readers and `_one_of` take a `Mapping`/`Container`; none of them mutates its argument. binary_sensor annotates its margin.
- **closures**: every closure CI's closures job found under-scoped at a390f589 now lists the files it named. That is `entry_config.py` everywhere, plus `freq_control.py` and `inputs.py` for the five scripts that reach `entry_config` through `optimizer.py`.
- **fast**: `tests/manual_plan.py`'s quiet-window stand-in returned `{}` from `effective_config`; the plan sensor now reads the parsed fraction there and raised `AttributeError`. The stand-in returns an `EntryConfig`, as the real coordinator does.
- **survivors**: `entities.py` now kills a stored NaN or infinity reaching a number field, and a stored tank volume of 0.

## Head

`bfaf5486a66f2f10a835b9d668d30999521a9364` merges the authored code head `d81907ad872378051cab14f0145487eb1cdd47a4` and then merges origin/main `2d8cab3f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e14ca26229ff184c9939a0653e1155313b65f71c` merges the authored code head `d81907ad872378051cab14f0145487eb1cdd47a4` and then merges origin/main `143e2d0a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`70fff51d70ffc729db5a10f03a7b31481b3d092c` merges the authored code head `d81907ad872378051cab14f0145487eb1cdd47a4` and then merges origin/main `143e2d0a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0d45191fe0243cf48c711a7f46d1cac82b634ca1` merges the authored code head `d81907ad872378051cab14f0145487eb1cdd47a4` and then merges origin/main `f637d24a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

d81907ad872378051cab14f0145487eb1cdd47a4

Delta since d15fc0ae (the previous handoff head), four commits: the merge and three follow-ups. The first merges `origin/main` 8d7903e6 (after #1987 R9-DBG-1 and R9-SW-1's quiet-window refactor). Six files conflicted:
- `coordinator.py`, imports: kept this branch's removal of the `CONF_*` names (main's five, `CONF_TIBBER_TOKEN`, `CONF_SILENT_MODE_FRACTION`, `CONF_PRICE_ENTITY`, `CONF_PRICE_SOURCE`, `DEFAULT_PRICE_SOURCE`, have no other use in the file here; the parsed object reads them).
- `coordinator.py`, `configured_quiet_windows`: took main's one-line `quiet_windows.configured_specs(...)` over this branch's inline copy of the same logic (main moved it into `quiet_windows.py`).
- `diagnostics.py`: both imports kept (`debugger` from main, `CONF_COP_SCALE` from this branch).
- `docs/architecture.md`, `tests/deployment_shape.py`, `dev/audit/rounds/round4/D6/claims.py`: the module count is 73 (72 on each parent), HA module-level importers 27 (`debugger.py`), package files 91. The `deployment_shape.py` pair figures were recomputed from the merged `tests/closures.json` with the file's own definition (Jaccard >= 0.80 over package files): 120 of 528 pairs, 406 comparable, 18 at exactly 1.00; the 1.00 pairs' shared-file counts are the merged ones.
- `claims.md` and `claims.json` regenerated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`; against main they differ only in the two module-count results (72 -> 73).

Two things the merge itself needed. `python3 tools/pr/ci_predict.py` (from `origin/fix/r9-ro-11-pr`, run from a scratch copy) predicted `closures UNDER-SCOPED`: `tests/debug_collect.py` (main's, new) reaches `entry_config.py` through the coordinator and its closure omitted it; added, and the predictor then printed no closures red. `tests/structure.py` failed `max_class_loc` 8823 > 8821, because the two parents' budget cuts are additive and main's added coordinator lines are not; the fix is code, not a raise: the `dhw_schedule_enabled` assignment and the `async_set_cooling_rate` call are one line each (-4 lines in the class). A first attempt that collapsed `configured_quiet_windows`'s `return out` was reverted: `entities.py`'s mutation-ledger check refused it, because main's `RETURN_DEL` pin names that exact line. The class now measures 8819 and the budget is recorded 8821 -> 8819 (down only; no raise).

`tests/entities.py` also needed one disposition: main's `debugger.py` reads `entry.options.get(CONF_DEBUG_COLLECT, ...)`, an options-only flag `EntryConfig` does not declare, so it is listed in `_EC_RESIDUAL` with the reason (`UNCLASSIFIED ['debugger.py']` before).

## Mutation proof

Applied in place to the committed head tree, `PYTHONPATH=tests/hastub python3 tests/entities.py` run, then `git checkout -- custom_components` (tree clean after each). The baseline at 057028f3 failed 1 check: the deployment-shape selection-cost note. That commit fixes it; the mutants ran before it.

- M1, `_number` keeps a non-finite value (`return result`): 2 of 2210 failed. The added one is "a stored NaN or infinity reads the declared default, and a stored tank volume of 0 reads the default volume; null control: 7.5 and 150 pass through", with `non-finite=[nan, inf, -inf]`.
- M7, `_nonzero_number` keeps 0 (`return _number(value, default)`): 2 of 2210 failed. The added one is the same check, with `tank=0.0`.
- RETURN_DEL on `IndoorTempSensor.extra_state_attributes` (`pass`): 5 of 2210 failed, among them "the indoor sensor publishes its thermometer's id, None without one" and "IndoorTempSensor publishes exactly its pinned attribute keys (#373)".

The live quiet apply is pinned by `entities.py`'s check "a stored None quiet spec reads unset, and a quiet window set by the service applies live through a new parse that equals the saved entry (no reload), the old parse untouched". The two restored `apply_config_keys` pins name it as killed by `tests/features.py` on main's measurement.

Disposition of the mutation lane:
- **Unmeasured added sites.** CI's mutation job at a390f589 (job 112880877079) started none of the 55 sites this diff added: "55 not started for --budget-minutes". This round adds a few more. They are left to CI's chain: `mutation-autofix` pins what it kills once the lane measures, and no site is pinned or triaged locally (fixer.md step 2).
- **Seven deleted killed_by pins.** Each was keyed to the text of a line this diff rewrote from a mapping read to a parsed-field read, so its anchor names a line that no longer exists:
  - `HeatPumpOptimizerCoordinator._pv_export_price` RETURN_DEL: the return now reads `self.effective_config.pv_export_price`.
  - `HeatPumpOptimizerCoordinator._solve_record` GUARD_OFF: the guard now reads `ctx._config.fuse_guard_enabled`.
  - `HeatPumpOptimizerCoordinator.target_temperature` RETURN_DEL: the return now reads `EntryConfig.from_mapping(...).target_temperature`.
  - `_grid_fee_entity_value` RETURN_DEL: the return now reads `.grid_fee_entity`.
  - `_price_feed` RETURN_DEL: the return now reads `cfg.price_entity`.
  - `pump_arbiter.duty_mode` RETURN_DEL: the return now reads `.pump_duty_mode`; the clamp to `PUMP_DUTY_MODES` moved into `EntryConfig`'s `_one_of`.
  - `IndoorTempSensor.extra_state_attributes` RETURN_DEL: re-earned locally above (5 checks), and left to `mutation-autofix` to pin.

  The other six are each the same mutation on the rewritten line, killed on main by `tests/features.py`. That script is CI's under the owner's 2026-10-07 rule, so their re-pins are CI's chain's.

## Null control

- The reviewer's `quiet_reload_driver.py` (round 1 evidence) at 057028f3, real call: `live_spec='09:00-09:30' live_off_steps=2 live_fraction=0.8`, `reloaded=0`. The empty call: `reloaded=0`, no spec. These are main's figures in the reviewer's run. The reviewer's run at a390f589 read `live_spec=''` and `reloaded=1`.
- `closure.py check --partial` was run against stand-in recordings: one per script CI named, each listing a390f589's committed closure plus the files CI said it really reads. Against this head's `tests/closures.json`: rc=0, "committed closures cover every file this run touched". Against a390f589's: rc=1, 21 `UNDER-SCOPED` lines.
- The M1/M7 check carries its own null arm: 7.5 and 150 pass through unchanged.

## Figures

Merge base `09ba95d08157e40950104d28a34c94dc899d4be1` (= `origin/main` at measurement, 2026-10-07). Interpreter `venv-ci` python3 3.14.7, one script at a time with `PYTHONPATH=tests/hastub`.

Taken at the previous head d15fc0ae (before this merge; the three lines under it that name a count are stale): `tests/entities.py` `ALL 2210 ENTITY CHECKS PASSED`; `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/typing_ruler.py` under `HPO_TYPING_PYTHON` (mypy included) `ALL 12 typing-ruler source checks PASSED`; `tests/manual_plan.py` `ALL 128`; `tests/config_flow_steps.py` `ALL 496`; `tests/closure.py selftest` `ALL 33 closure shrink pins PASSED`.

The figures below were taken before that merge, at 057028f3 unless noted.

- `HPO_TYPING_PYTHON=<the pinned typing venv> python3 tests/typing_ruler.py`: `ALL 12 typing-ruler source checks PASSED`, mypy included. The same mypy invocation at a390f589 printed the 9 errors CI's typing job did.
- `python3 tests/entities.py`: `ALL 2210 ENTITY CHECKS PASSED`.
- `python3 tests/manual_plan.py` at 2f987a6d: `ALL 128 manual plan checks PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `max_class_loc` 8880 -> 8877 and `seam_cut_total` 765 -> 760 are recorded in de811106 with the reason. No budget was raised.
- At eaaa6c2f: `tests/config_flow_steps.py` `ALL 496`, `tests/doc_claims.py` `ALL 160`, `tests/guard_pins.py` `ALL 47`, `tests/deployment_shape.py` passed, `tests/closure.py selftest` `ALL 32`.
- `python3 tests/closure.py select --files custom_components/heatpump_optimizer/entry_config.py`: `MODE: SCOPED -- 26 script(s) run, 6 scoped out`. `entities.py`, `features.py`, `typing_ruler.py` and `structure.py` are among those it runs.

Heavy scripts (`features.py`, `golden.py`, `stress.py`, `boost_drift_replay.py`, `arch_score`, mutation) are CI's under the owner's 2026-10-07 rule and are not run locally for this head.

## Red checks

Every non-green check-run at a390f589, read through the commit's check-runs API:

- `typing` (job 112880876862): this PR's. mypy grew 0 -> 9 and is 0 again here. The cheaper detector exists and costs nothing new: `typing_ruler.py` under `HPO_TYPING_PYTHON`, run locally. The first body ran the ruler without mypy, which measured nothing.
- `closures` (job 112881062368) and `closures-autofix` (job 112897209809): this PR's. `entry_config.py` was hand-added to 5 of the 20 closures that import it; the rest are added here. The autofix skipped because it read a recording as failed. The cheaper detector is `closure.py check --partial` against stand-in recordings, seconds, shown under Null control.
- `fast (3.14)` (job 112880876855): this PR's. `tests/manual_plan.py` raised on the stand-in fixed above. The cheaper detector is that script itself (about 40 s). It was in this branch's scope, but the local gate run that would have reached it was stopped under the owner's heavy-script rule before it did.
- `mutation` (job 112880877079) and `mutation-autofix` (job 112884087373): the lane measured nothing ("55 not started for --budget-minutes"), and the autofix reported skip-no-measurement. Disposition under Mutation proof. No cheaper detector exists for an unmeasured lane; the local kills above cover the two survivors the reviewer found and one re-earned pin.
- `mutation-nightly` (job 112857793518), and `closures` (job 112857717705), both in the `tests.yml` run I dispatched at 5947316c (run 37640455476): this PR's. The nightly mutation drive's baseline raised in `tests/manual_plan.py` on the same `{}` stand-in fixed above (`'dict' object has no attribute 'silent_mode_power_fraction'`). That closures red is the same under-scope as job 112881062368. The cheaper detectors are the ones named for `fast` and `closures`.
- `delivery-status` (job 112880304107): not this PR's. #2003 and #2001 are overdue on main, and this diff only adds the row for 2025.
- `nightly-status` (job 112880876632): not this PR's. It reports main's nightly, which this diff does not reach.
- `pr-contract` (job 112901458904): the previous body named none of the reds above. This body names each.
- `budget-raise-gate` (job 112880302977): cancelled, not failed. This diff raises no budget leaf.

Locally only: `tests/features.py` R9-F2.1 P3 (two-zone) prints shipped 110.4366 and seeded 110.1297 on this machine for the branch and for the base package alike. CI's Linux lane decides it.

## Unpinned sites

The mutation lane measures nothing at this head (the `mutation` red above, awaiting R9-CI-1), so no site below was killed or survived on a measurement. Each is a line this diff adds, in `entry_config.py` or a migrated reader that now reads the parsed object. Disposition for all 56, from `python3 tools/pr/ci_predict.py` at this head: unpinned; `mutation-autofix` owns pinning (`ci-autofix.md`) once R9-CI-1 lets the lane measure, and no survivor is triaged by hand here.

- custom_components/heatpump_optimizer/__init__.py:179 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/binary_sensor.py:174 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:822 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:1764 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:1801 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:2327 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:3167 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:3275 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:4141 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:4187 BOOLOP: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:5051 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:5462 BOOLOP: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:5483 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6466 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6836 BOOLOP: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6836 CMP_BOUND: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6836 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6871 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:6930 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:7120 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8126 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8156 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8294 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8630 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8725 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8785 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8816 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8871 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8903 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8936 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:8967 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:9019 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:9421 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:9811 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10146 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10533 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10606 BOOLOP: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10606 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10778 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10793 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/coordinator.py:10826 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/disinfection.py:116 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/disinfection.py:121 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:37 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:43 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:52 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:55 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:75 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:80 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:97 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:255 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:260 BOOLOP: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/entry_config.py:262 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/legionella.py:194 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/sensor.py:704 RETURN_DEL: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)
- custom_components/heatpump_optimizer/silent_mode.py:104 GUARD_OFF: unpinned; pinned by mutation-autofix once the lane measures (R9-CI-1)

## Forward-carry

none. The modules that still read a mapping are named, with why, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none.

## After the merge (this head, local cheap scripts, one at a time, `PYTHONPATH=tests/hastub`, venv-ci python)

- `tests/entities.py`: `ALL 2214 ENTITY CHECKS PASSED`.
- `tests/manual_plan.py`: `ALL 129 manual plan checks PASSED` (taken at the head before the last three commits; they touch `coordinator.py` lines no stand-in reaches, and `entities.py` after it).
- `tests/structure.py`: the `max_class_loc` row measured 8819 against a recorded 8820 before the final record commit, then recorded; no row raised.
- `tools/pr/ci_predict.py` (from `origin/fix/r9-ro-11-pr`): `no closures or fast red predicted`. It still lists 56 unpinned mutation sites this diff adds (`entry_config.py`, the migrated readers); those are `mutation`'s, which is still red and answered above (awaiting R9-CI-1: the lane measures nothing until it lands). `typing` is CI's at this head.

