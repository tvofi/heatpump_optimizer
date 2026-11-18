Part of #3616 (phase 3a of the owner's three; phase 3b, the loop-capacity limit, is its own group by the approved note)

R11-OUTSIDE-ROOMS-P3, built to the approved design `design/R11-OUTSIDE-ROOMS-P3` at `e36406c0f4` (`Design review: approve e36406c0f4c7ff73bdce5f7f3b5b7ec25a311ab7`, `design-verdict/R11-OUTSIDE-ROOMS-P3` `14ce168fb7`), on `origin/main` `5e2ef89b4e`, where R11-OUTSIDE-ROOMS-P1 and P2 have landed.

Room history and the identifiability report. Per half hour, whatever the entry's interval, each listed room's temperature, target and share of samples calling for heat, beside the house's outdoor and floor-return temperatures, measured power and share of cycles on space heating; 14 days deep (`room_history.HISTORY_LENGTH` rows). The report reads, per room, the first verdict that applies: `no_action`, `short_history`, `never_calling` / `always_calling`, `collinear` (naming the room), `no_response`, else `separable` with the fit dT/dt = a (outdoor - T) + b calling + c; and one house line for phase 3b (measured power against the calling fraction over space-heating periods). Published in diagnostics (`room_history`) and one sensor, Room Separability, both only where a room list is configured. Nothing in the plan reads it.

## What it does

- **`room_history.py`** (pure: `const`, `rooms`, numpy): the ring (`note`, `History`, `Period`), the store document (`stored`, `loaded`: one comma-joined centi-unit string per column) and the report (`identifiability_report`, `separable_count`).
- **`room_record.py`** (glue): one record per coordinator in a `WeakKeyDictionary` with its own `QuarantiningStore` (`duty_switch.py`'s pattern), loaded on the first cycle with a room list, saved with an awaited `async_save` every `SAVE_EVERY_ROWS` (12) closed rows, flushed in `async_unload_entry` before `coordinator.async_shutdown()` (verdict item v3a; unload runs at a Home Assistant stop, so no stop listener).
- **Coordinator**: one `_best_effort_cycle_step` after `_record_accuracy`, passing the house values as arguments (outdoor, floor return, measured kW, the executed step's space and hot-water kW). Paid for in the class span by deleting two comments in `_async_update_data` that narrated the call below them (`max_class_loc`, `class_excess_loc` unmoved).
- **Store**: `store.DOMAINS["room_history"]`, every column text with its `whole=` cost; `room_history.loaded` checks each cell against the column's own range (verdict item v3b): temperatures and targets `ROOM_AIR_RANGE_C`, outdoor `OUTDOOR_AIR_RANGE_C`, floor return `FLOOR_WATER_RANGE_C`, power `MEASURED_KW_RANGE`, shares 0..100 %. A bad room cell drops that room's ring whole; a bad house cell nulls the house columns and keeps the rooms; bad row times empty the ring.
- **Pairs** (verdict item v3c): successive non-null rows at most `PAIR_GAP_MIN` (120 min) apart, dT divided by the elapsed hours, so a 60-minute entry reads separable.
- **Factory reset keeps it** (the note's routed owner decision): no `_FACTORY_VOID` row, not in `_restored_stores`; `_FR_STORES` gains it as kept.
- **Docs**: the room list's row in `docs/configuration.md`; `docs/architecture.md`'s counts, module map and HA boundary list.

Departures from the note, each from a measurement:

1. **A row's temperature is the period's first reading, not its last.** With the last reading, a calling share averaged over the period is paired with the temperature change the next period's calling causes; on the 10-minute simulation the fitted gain read 0.50 K/h against the simulated 2.0. With the first reading, the period's calling acts on the change to the next row, at a 10- and a 60-minute interval alike (`independent calling reads separable, the calling gain within 20 % ...`). Mutant `first reading` below kills it.
2. **The glue is its own module, `room_record.py`.** In one module, `score.py --diff` read `layer_violations 13->14` (a module importing no `homeassistant` reaching it through `store`); split, the pure part reaches nothing and the glue imports `homeassistant.core` as `duty_switch` does. The ring length is `room_history`'s own (14 days of half hours) rather than an import of `accuracy.HISTORY_LENGTH`, which is the other path the same metric read.
3. **The `b > 0` test is the t-statistic's sign**: t carries b's sign, so `t < MIN_T` already refuses a non-positive gain; the separate comparison survived every mutant and was removed (`a room that cools while it calls reads no response ...` pins the behaviour).

The roster's carries to this group:

- Carry 0 (b92176a2, phase 3's store and sensor should it add an option): no option is added; the toggle-free design needs none.
- Carry 2 (fc1592bb, an options field moves `tests/golden/config_flow.json`, the D5 harness counts and `tests/entities.py`'s EG-B3 resolve table): no options field and no change to the `rooms.published` call text, so none of the three moves; the new sensor moves `tests/entities.py`'s room roster check (3 sensors, not 2), edited here.
- Carry 1 (e98789a8, the why-now row and narrative naming the room lift): not built here, a pending orchestrator ruling on where it is built; the precondition is under `## Forward-carry`. Carry: R11-OUTSIDE-ROOMS-P3 (item e98789a8)
- Carry 3 (e82913fe, this pull request's own body item for the same why-now row, landed on this group's roster by the orchestrator): the same disposition as Carry 1, and not built here; its precondition and control are under `## Forward-carry`. Carry: R11-OUTSIDE-ROOMS-P3 (item e98789a8)

The note's items for the fixer: p3a1 (cites re-anchored at this base), p3a2 (one step line, paid), p3a3 (the new modules recorded in measured closures, `tests/derive_closures.sh --scripts-from` on Linux), p3a4 (the first cycle awaits the load before it notes anything, so no row closes before it: `the first cycle loads the stored ring before it notes anything ...`).

## Head

`885f82e12b8b1bbadb575ada7f643cfec4efdb54`

prepr: passed rc=0 at 885f82e12b8b1bbadb575ada7f643cfec4efdb54

Repair round on the fix review's block `Fix review: blocked 478e2ab92c36b309c73e8cc29903671434f73375 mutation-vacuous` (`verdict/3711`), built on `478e2ab92c` (which merges the authored code head `3f9fa5f4f6` and the bot's pins `8518497c1a`). No main merge: `git merge-tree --write-tree origin/main HEAD` reports no conflict.

1. **Checks that drive the code the block named** (`tests/features.py`, the room-history block, 40 -> 47 checks):
   - `a production coordinator's cycle hands the room history this cycle's outdoor reading ...`: a `HeatPumpOptimizerCoordinator` runs `_async_update_data` four times with a room list (`rooms.readings_of` returns one climate reading for that coordinator); the House each cycle hands `room_record.async_note_cycle` is captured and the real call runs on the test's clock. Asserted: every cycle's outdoor, floor return, metered kW, the plan's space and hot-water kW, and the closed row's house columns (outdoor, return, the period's power mean, a space share with one hot-water cycle). The plan's two kW are set where the cycle sets them (a wrapper on `_apply_action`), so their values are the test's.
   - `unloading the entry saves the rows the last save missed ...`: an entry set up and unloaded through `harness.ha_setup_entry` / `ha_unload_entry`, i.e. through `async_unload_entry`.
   - `one period: a reading with a problem and one reporting no action are not calling samples ...` (problem guard, `calling is not None`, last target, power mean, hot-water exclusion), `a pair needs the first row's calling share ...`, `stored row times off the half-hour grid empty the ring ...`, `the house line reads only periods spent mostly on space heating ...`, `a full ring's report is re-read when a row replaces its oldest ...`.
2. **A defect the coordinator check found, fixed** (`coordinator.py`, the room-history cycle step): the step read `ctx._current_state.outdoor_temperature`, where `ctx` is the context `_async_update_data` captured on entry; `_update_current_state` publishes a new context during the cycle (`CoordinatorContext.publish` rebinds `coord._ctx`), so the ring stored the previous cycle's outdoor reading beside this cycle's room temperatures, and the first cycle after setup the 5.0 default. Measured before the fix with the outdoor sensor at -3.0, -4.0, -5.0, -6.0 over four cycles: the House read `5.0, -3.0, -4.0, -5.0`; after it, `-3.0, -4.0, -5.0, -6.0`. The step now reads `_ctx_of(self)._current_state.outdoor_temperature`. Floor return and metered power are attributes the same read sets and were current already. The other two `ctx.` reads in `_async_update_data` (`_opt_config.max_temp`, `_config.optimization_interval`) are configuration, not the state `_update_current_state` publishes, and are not changed here.

## Mutation proof

The reviewer's own driver (`verdict/3711` `evidence/mut_driver.py`), re-run at this head with two edits: the outdoor mutant's anchor follows the new read, and one mutant is added that restores the cycle-start `ctx`. The block command is `env PYTHONPATH=tests/hastub PYTHONDONTWRITEBYTECODE=1 python3 tools/audit/seat/features_block.py --prelude "exec(open(P).read())" 'R11-OUTSIDE-ROOMS-P3 (#3616, phase 3a)'`, where P is written at this head by `features_block.py --emit-prelude P 'R11-OUTSIDE-ROOMS-P3 (#3616, phase 3a)'`; the new checks read names earlier blocks bind (`_SrcHass`, `_seed_prices`, `_LC_DATA`), which the review's two hand-written preludes do not bind. Each mutant is applied alone, `__pycache__` is cleared, the block is run and the tree is restored.

Result: 23 mutants, 23 `KILLED`, 0 `SURVIVED`. Among them are the 13 the review read as survivors: `coord step deleted`, `coord outdoor->return`, `coord swaps space/dhw kw`, `unload flush deleted`, `call share counts problem rows`, `space ignores dhw`, `target first not last`, `power mean -> last`, `pairs keep null call` (killed by `numpy.linalg.LinAlgError: SVD did not converge`), `times off-grid accepted`, `house line drops space filter` and `report cache key len only`. Also killed: the added `coord outdoor from the cycle-start ctx`, and the 10 the review's null control already read killed. The review's evidence holds the per-mutant lines for those 10.

The failing tests come first: the coordinator check failed at `478e2ab92c`'s production code with `seen=[(5.0, 28.0, 1.0, 2.5, 0.0), (-3.0, 28.0, 2.0, 2.5, 1.5), (-4.0, ...), (-5.0, ...)]` before the one-line fix. The block's null control is its baseline at this head, `ALL 47 FEATURES BLOCK PASSED`, rc 0.

The 4 sites `python3 tools/pr/ci_predict.py --base origin/main` lists as `ADDED UNPINNED` at this head were each applied in a detached worktree at this head and run against the same block command: `room_history.py:182 CMP_BOUND` was killed by `three 10-minute cycles make one 30-minute row ...`, `:276 CLAMP_DROP` by `an exact fit ... keeps finite t-statistics`, `:302 RETURN_DEL` by a `TypeError` in the report and `:334 CMP_BOUND` by `a calling gain exactly MIN_T standard errors clear of zero ...`.

## Null control

- No room list: `async_note_cycle` with an empty list makes no record and no store key, `report_of` reads None and the diagnostics key is absent (`no room list: no record, no store file and no row (invariant i) ...`); `tests/entities.py`'s default roster holds no room sensor, the configured list adds exactly three.
- Each new check carries its own control in its text: the shares held, the grid times, every period on space heating, a report read twice with no new row, the store empty before the unload, and each coordinator value distinct from the one it could be swapped for.
- Golden drift was not re-run in this round. The production change is one argument of the room-history call, which no plan, golden fixture or claim file reads. The previous round's `NO UNCLAIMED DRIFT: 56 scenario(s)` at `478e2ab92c`'s tree stands.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=7c2f4c30cab5610cf8f5b040c326836ab544d27d head=885f82e12b8b1bbadb575ada7f643cfec4efdb54 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->
- Scope of this round's delta: `python3 tests/closure.py select --diff 478e2ab92c36b309c73e8cc29903671434f73375 --workdir "$D"` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out` (the coordinator is in most closures). These were run here, with `PYTHONPATH=tests/hastub`, at this head: `tests/features.py` `ALL 5947 FEATURE CHECKS PASSED`, rc 0; `tests/entities.py` `ALL 2731 ENTITY CHECKS PASSED`, rc 0; `tests/guard_pins.py` `ALL 91 GUARD PIN CHECKS PASSED`; `tests/typing_ruler.py` `ALL 12 typing-ruler source checks PASSED`; `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`. CI runs the other 17: the changed argument feeds only `room_record.House`, which none of them reads.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at this head.
- `python3 tools/pr/ci_predict.py --base origin/main` at this head: `no closures, fast, governance or instrument red predicted against 7c2f4c30cab5`, and 4 added unpinned sites (under `## Mutation proof` and `## Unpinned sites`).
- Finder's harness: none. #3616 is an outside report and the design note names none.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` at this head: `Architecture score: dS -0.0120 WORSENS (inadmissible: coord_footprint 2505->2526)`, the same 21-point footprint the original handoff read (2502 -> 2523 at `5e2ef89b4e`; main's base moved by 3). This round's production change replaces one name with a call to `_ctx_of`, the coordinator's own typed context accessor, and adds no line.

- `coord_footprint`: the one cycle step in the coordinator class, the two diagnostics lines that publish only where a record exists, and `room_record`'s five functions handed the coordinator (`_record_for`, `async_note_cycle`, `async_flush`, `record_of`, `report_of`). This is the side-table pattern the note prescribes, so the coordinator gains no attribute (`coordinator_attrs` sits at its budget).

## Unpinned sites

The 94 sites `python3 tools/pr/ci_predict.py --base origin/main` listed as `ADDED UNPINNED` at the original handoff, and the original handoff's `SURVIVED` lines, with their dispositions as before. At this head the predictor lists 4 (`room_history.py` 182 CMP_BOUND, 276 CLAMP_DROP, 302 RETURN_DEL and 334 CMP_BOUND); each is killed by the block (`## Mutation proof`) and left for mutation-autofix's pin run.

- custom_components/heatpump_optimizer/diagnostics.py:360 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:29 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:35 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:50 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:54 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:55 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:57 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:59 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:61 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:63 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:103 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:103 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:105 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:115 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:117 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:119 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:119 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:122 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:124 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:126 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:128 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:128 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:137 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:155 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:156 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:164 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:165 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:182 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:182 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:185 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:185 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:185 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:190 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:201 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:208 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:208 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:208 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:210 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:228 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:228 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:230 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:238 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:241 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:249 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:264 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:266 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:272 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:273 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:273 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:276 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:276 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:281 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:286 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:295 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:298 CMP_BOUND*3: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:302 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:310 BOOLOP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:310 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:310 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:317 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:320 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:320 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:322 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:323 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:323 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:325 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:325 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:327 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:334 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:334 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:346 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:350 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:352 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:353 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:353 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:357 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:357 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:360 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:380 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:382 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:29 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:32 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:51 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:56 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:59 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:82 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:85 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:89 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:89 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:96 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:103 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:106 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_record.py:108 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/sensor.py:779 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/room_history.py:59 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); no simulated room lands a t-statistic between 3 and 6
- custom_components/heatpump_optimizer/room_history.py:272 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); a fit with one degree of freedom is never reached past MIN_PAIRS
- custom_components/heatpump_optimizer/room_history.py:276 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: the floor only guards a zero variance
- custom_components/heatpump_optimizer/room_history.py:292 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: numpy reads any negative size as inferred
- custom_components/heatpump_optimizer/room_history.py:293 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: numpy reads any negative size as inferred
- custom_components/heatpump_optimizer/room_history.py:295 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: only pairs with under 3 common rows differ, and the mask drops them
- custom_components/heatpump_optimizer/room_history.py:308 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: any fill under 0 loses to a real |r|
- custom_components/heatpump_optimizer/room_history.py:309 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: a room is always its own row, so the row is never empty
- custom_components/heatpump_optimizer/room_history.py:310 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`); an |r| of exactly 0.9 is not constructed
- custom_components/heatpump_optimizer/room_history.py:334 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`); a t-statistic of exactly 3 is not constructed
- custom_components/heatpump_optimizer/room_history.py:348 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: every cell of the no-room stack is NaN
- custom_components/heatpump_optimizer/room_history.py:350 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: 0/0 reads NaN either way
- custom_components/heatpump_optimizer/room_history.py:356 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); the two-valued fixtures share their first quartile
- custom_components/heatpump_optimizer/room_history.py:360 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`); unreachable: past the IQR and row-count guards the house fit has full rank; kept for the type
- custom_components/heatpump_optimizer/room_history.py:361 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/room_record.py:29 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); a new store's first version
- custom_components/heatpump_optimizer/room_record.py:76 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/room_record.py:105 CONST_SWAP: pinned by mutation-autofix (its lane mutates `custom_components/`); equivalent: either row time moves with every closed row
- custom_components/heatpump_optimizer/room_record.py:25 STMT_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/room_record.py:27 STMT_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/room_record.py:39 STMT_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/room_record.py:67 STMT_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`); see the line's own statement: no behaviour the block reads
- custom_components/heatpump_optimizer/__init__.py:429 STMT_DEL (the unload flush), custom_components/heatpump_optimizer/coordinator.py:6123 STMT_DEL and :6124 CONST_SWAP (the cycle step and its executed-step power default): pinned by mutation-autofix (its lane mutates `custom_components/`). Each is now killed by the block: the unload flush by `unloading the entry saves the rows the last save missed ...` and the cycle step by `a production coordinator's cycle hands the room history ...` (`## Mutation proof`). This corrects the previous body, which called them "wiring the features block does not drive" while listing them as pinned.

## Red checks

- `tests / mutation` (at 1fe21304 and 9597676033): `MUTATION TABLE REFUSED` on the diff's added unpinned sites. The bot's and the orchestrator's pin commits (`8518497c1a`, `3f9fa5f4f6`) pinned all but 4, and those 4 are killed by the block (`## Mutation proof`), left for mutation-autofix. The cheaper detector is `tools/pr/ci_predict.py` (`prepr.sh` step 6d), which predicts which sites are unpinned, not which survive; the review's hand mutants are not the ratchet's operators, and no instrument in the tree generates them.
- `governance / wave-script` (at 9597676033): answered in the previous round's body (the DIRTY state's red, repaired by that round's main merge); inherited at `478e2ab92c`, where `python3 tools/audit/seat/merge_train.py classify 478e2ab92c36b309c73e8cc29903671434f73375 --pr 3711` reads `WAIT ... pending: gate red: none`. Cheaper detector: none that runs before main moves; the merge was the repair.
- `pr-contract / pr-contract` (at 9597676033): answered in the previous round's body (a bot push moved the head under the body); this body's figure block is refreshed at its own head.
- `gate` (at 1fe21304 and 9597676033): the aggregate of the runs above; no cause of its own.

## Forward-carry

- The why-now comfort-floor row and the daily narrative still do not name the room lift (P2 body item e98789a8). Not built here: the approved P3 note is phase 3a only and keeps `optimizer.py` out, and the precondition is a per-step lift on the solve's result beside `comfort_floors`, read by `slot_drivers` and `narrative.py`, with card text in three languages; its control is a solve with the toggle off whose row must not change. The roster sent it here and the approved note's routed orchestrator decision makes P3 phase 3a only, so where it is built is that decision's to place. Carry: R11-OUTSIDE-ROOMS-P3 (item e98789a8)
- The note's two routed owner decisions are built as designed and await the owner at this pull request's review: factory reset keeps room history (the alternative voids it whole, a `_FACTORY_VOID` row and a coordinator edit), and a crash loses up to 6 h of it (saving every row writes the store each half hour). Carry: R11-OUTSIDE-ROOMS-P3 | dismissed: owner decisions answered at this review

## Friction

none
