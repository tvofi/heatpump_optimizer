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

The note's items for the fixer: p3a1 (cites re-anchored at this base), p3a2 (one step line, paid), p3a3 (the new modules recorded in measured closures, `tests/derive_closures.sh --scripts-from` on Linux), p3a4 (the first cycle awaits the load before it notes anything, so no row closes before it: `the first cycle loads the stored ring before it notes anything ...`).

## Head

`8fedab0deeba340e6c83e5674feb6ec31f21aea9`

## Mutation proof

`python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --path custom_components/heatpump_optimizer/room_history.py --path custom_components/heatpump_optimizer/room_record.py --cmd CMD --max-mutants 400`, CMD `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from heatpump_optimizer import coordinator as _r9f13_cmod' --prelude 'import json as _fi_json' 'R11-OUTSIDE-ROOMS-P3 (#3616, phase 3a)'`, each mutant in a git-archive copy of the head. The first run printed 75 `SURVIVED` lines, the second (after boundary checks) 31, the head's 22; each of the 22 is listed under `## Unpinned sites` with its disposition. The coordinator's cycle step and the unload flush are wiring the block does not drive (`prepr.sh`'s own `MUTANT_CMD` step reads them as survivors); the diagnostics key is pinned on a production coordinator (`a production coordinator's diagnostics carry the room-history report ...`).

Hand mutants on the design's named targets, each run against the same block (`/tmp` driver, one edit, restore): period boundary (`start = now_min`), 14-day cut (`HISTORY_LENGTH - 1` to `HISTORY_LENGTH`), every report threshold (`MIN_PAIRS`, `CALLING_SHARE`, `NEVER_FRACTION`, `ALWAYS_FRACTION`, `COLLINEAR_R`, `MIN_T`, `FLAT_IQR`, `PAIR_GAP_MIN`), the code order (collinear skipped), the `whole=` drop, the save cadence, the empty-list early return, the first reading, the flush, the clock-back guard and the gain's sign: each KILLED, by the checks named in the block (`three 10-minute cycles make one 30-minute row ...`, `fifteen days of rows keep the ring's 14 days ...`, `100 pairs read short history ...`, `a room whose calling copies another's reads collinear ...`, `the store round-trips the ring unchanged ...`, `a save at exactly SAVE_EVERY_ROWS closed rows ...`, `no room list: no record, no store file and no row ...`, `after a reload, a sample at or before the ring's last row opens nothing ...`, `a calling fraction that moves, but by under FLAT_IQR ...`, `a room that cools while it calls reads no response ...`).

The failing test first: the block over `5e2ef89b4e`'s production code fails at its import (`room_history` absent).

## Null control

- No room list: `async_note_cycle` with an empty list makes no record and no store key, `report_of` reads None and the diagnostics key is absent (`no room list: no record, no store file and no row (invariant i) ...`); `tests/entities.py`'s default roster holds no room sensor, the configured list adds exactly three.
- The collinear verdict's control is the same room on its own schedule, which reads separable; the shuffled room's control is the room left in order, which reads separable in the same report.
- A healthy store document loads every room and round-trips byte-equal; each corruption costs only what it owns.
- Golden drift against the merge base, `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub python3 tests/golden.py`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 5e2ef89b4e7348b190aa917dc032da73ba04998e` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, rc 0; no claim file is touched.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=5e2ef89b4e7348b190aa917dc032da73ba04998e head=8fedab0deeba340e6c83e5674feb6ec31f21aea9 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- The block reads `MODE: FULL` because its registered instrument overlays `origin/main`'s `tests/closure.py` on the head's tree (`tools/pr/figure_registry.json`, `files`), and main's copy has moved past this branch's merge base (`git diff --quiet HEAD origin/main -- tests/closure.py || echo DIFFERS` prints `DIFFERS`), which `select` reads as a change to the gate itself. The head's own copy, the command above, prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the branch is not re-merged.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `tests/structure_budgets.json` is main's (`git diff --quiet $(git merge-base origin/main HEAD) HEAD -- tests/structure_budgets.json && echo IDENTICAL` prints `IDENTICAL`): a `name_kept_members` gain recorded mid-branch was incidental to a typing choice and was restored, not claimed.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py ... 'R11-OUTSIDE-ROOMS-P3 (#3616, phase 3a)'` (the CMD above): `ALL 33 FEATURES BLOCK PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`: `ALL 115 FINITE BOUNDARY CHECKS PASSED` (the new store seeded, loaded and saved in every arm; its version constant named apart from `duty_switch`'s, which `no two stores share a version constant` refused first).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2731 ENTITY CHECKS PASSED`, rc 0.
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py`: `ALL 9 typing-ruler checks PASSED` and `ALL 12 typing-ruler source checks PASSED` (mypy `--strict` over the package, no new error and no `type: ignore`).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 115 HARNESS HEADER CHECKS PASSED` (the D6 claims harness header moved to 98 modules and 34 module-level importers, its register re-run).
- `python3 -I tools/audit/regret_oracle.py --self-test`: `SELF-TEST passed (64 arms)`; it imports `tests/stress.py`, whose closing `sys.exit` the first cut of this diff had moved outside its main guard.
- Closures: `tests/derive_closures.sh --scripts-from F` on Linux for the 27 scripts whose closure reads the coordinator, the sensor platform or diagnostics, `tests/entities.py` recorded and merged with `--partial --allow-failures` as on main (`rc 1` recorded there too); `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted`.
- The report at its largest, `tests/stress.py`'s new section: 32 rooms (`rooms.ROOMS_MAX`) by 672 rows, store under 0.5 MB at indent 2 and the ring under 8 MB held, the report's median of three under one reference solve (`timing_check`); on the fixer's 4-core container the store measured 331004 bytes and the held ring 1805558 bytes (`tracemalloc`), the report tens of milliseconds under concurrent load. `tests/stress_budgets.json` is untouched.
- Seam enumeration, every store: `git grep -n "QuarantiningStore(" -- custom_components/heatpump_optimizer` returns each store; the new one, in `room_record.py`, has its `_FR_STORES` row (`features.py`'s AST walk refuses one without) and its `DOMAINS` entry (`finite_boundary.py` arm 1). Every cycle step: `git grep -n "_best_effort_cycle_step(" -- custom_components/heatpump_optimizer/coordinator.py`; the new one sits after `_record_accuracy`.
- Finder's harness: none. #3616 is an outside report and the design note names none.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 5e2ef89b4e7348b190aa917dc032da73ba04998e`: `Architecture score: dS -0.0121 WORSENS (inadmissible: coord_footprint 2502->2523)`.

- `coord_footprint` 2502 -> 2523: the one cycle step in the coordinator class, the two diagnostics lines that publish only where a record exists, and `room_record`'s five functions handed the coordinator (`_record_for`, `async_note_cycle`, `async_flush`, `record_of`, `report_of`), the side-table pattern the note prescribes so the coordinator gains no attribute (`coordinator_attrs` sits at its budget). The ring, the store document and the report take a `History` and readings, not the coordinator. The first cut also read `duplication_copies 18->19` (a residual block shared with `sysid.identify`), `literal_clone_copies 114->116` (an `np.errstate` call shared with `_liquid_fraction`) and `layer_violations 13->14`; the fit now reads the residual sum of squares `lstsq` already returns, the correlations divide without an errstate, and the glue is split out: those three read flat at the head.

## Unpinned sites

The 94 sites `python3 tools/pr/ci_predict.py --base origin/main` lists as `ADDED UNPINNED` at the head, then the 22 `SURVIVED` lines of the `mutant_run.py` command under `## Mutation proof` at the head; each is under `custom_components/`.

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
- custom_components/heatpump_optimizer/__init__.py:429 STMT_DEL (the unload flush), custom_components/heatpump_optimizer/coordinator.py:6119 STMT_DEL and :6120 CONST_SWAP (the cycle step and its executed-step power default), the `SURVIVED` lines of `prepr.sh`'s own `MUTANT_CMD` step: pinned by mutation-autofix (its lane mutates `custom_components/`); wiring the features block does not drive, while `room_record.async_flush` and `async_note_cycle` themselves are pinned in it.

## Red checks

- `tests / mutation`: predicted red on the diff's `ADDED UNPINNED` sites (`python3 tools/pr/ci_predict.py --base origin/main`), each listed under `## Unpinned sites`; the `mutation-autofix` job pins them (ci-autofix.md). The cheaper detector is that predictor, run here before the handoff at no standing cost beyond `prepr.sh` step 6d; no cheaper one exists.

## Forward-carry

- The why-now comfort-floor row and the daily narrative still do not name the room lift (P2 body item e98789a8). Not built here: the approved P3 note is phase 3a only and keeps `optimizer.py` out, and the precondition is a per-step lift on the solve's result beside `comfort_floors`, read by `slot_drivers` and `narrative.py`, with card text in three languages; its control is a solve with the toggle off whose row must not change. The roster sent it here and the approved note's routed orchestrator decision makes P3 phase 3a only, so where it is built is that decision's to place. Carry: R11-OUTSIDE-ROOMS-P3 (item e98789a8)
- The note's two routed owner decisions are built as designed and await the owner at this pull request's review: factory reset keeps room history (the alternative voids it whole, a `_FACTORY_VOID` row and a coordinator edit), and a crash loses up to 6 h of it (saving every row writes the store each half hour). Carry: R11-OUTSIDE-ROOMS-P3 | dismissed: owner decisions answered at this review

## Friction

none
