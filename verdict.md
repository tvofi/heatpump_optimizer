Design review: approve abc575172ca1e6758c58ca8d1f265a2dc7c4fa23

Round 2 of 3. Reviewed `design.md` at abc575172c from a detached worktree, against the tree at dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd, where the predecessor is merged (pull request 3405, merge b421442efe). Nothing was rerun. The ref still pointed at abc575172c when this was written.

## The nine points of the previous verdict

1. Owner of episodes, estimate and store (`design.md:23`): answered. A new module with its own `QuarantiningStore`; `ArbiterState` gains no field; `_persist` (`pump_arbiter.py:1699`) saves `{"written": ...}` only, confirmed.
2. One owner of "the compressor runs" (`design.md:25`): answered. `wear.py` (no Home Assistant import, confirmed) gains the classifier and the edge tracker; signal order frequency over a named floor, else power at `on_threshold_kw`; both existing readers stay, each with its reason, and the start counter's move is part D.
3. Listener home (`design.md:27`): answered. The new module registers it; the arbiter attaches from `_listen` (`pump_arbiter.py:1667`), which today listens only on its own control entities, not on power or frequency. `coordinator.py` gains nothing, so `coordinator_attrs` and `coordinator_private_reach` cannot move.
4. Planner price (`design.md:52-54`): deferred to part C with a direction and no commitment, as the split asked.
5. Evidence by file (`design.md:79-91`): answered. Seven tests in `tests/features.py`, two null controls as tests, restart test, "no golden moves; neither claim file is touched". `tests/golden/flat_prices.json` exists.
6. Cost (`design.md:17-19`): the split is adopted; this group is A.
7. Sibling sites (`design.md:63-77`): answered and re-run here. The note's command prints `pump_arbiter.py:1324`, `:1486`, `:1658` and one comment in `pump_mode.py:85`. My own grep of `heat_pump_mode_entity` over the package at dbd1ab5b07 finds the entity bound to a write slot only at `pump_arbiter.py:398`; the other `services.async_call` sites (`coordinator.py:4526`, `:7035`, `:10862`, `heat_curve.py:205`, `:222`, `inputs.py:611`, `pump_arbiter.py:1534`) do not take the mode slot. Every mode write lands at `pump_arbiter.py:1359` in `_write`, so observing there covers the class.
8. Relearn invariant (`design.md:46`): answered. p does not move with age, only n falls; on at n >= 5, two days, p >= 0.5; off at n < 2.5 or p < 0.3; the latch is stored.
9. Base and lines (`design.md:3`): answered. All 58 cited lines hold at 068074f0f2. At dbd1ab5b07 every `pump_arbiter.py`, `store.py`, `dhw_learning.py`, `wear.py` and `power_guard.py` line is unchanged; the others moved: `optimizer.py` 1546 to 1614, 4707 to 4783, 4246 to 4321, 4622 to 4697, 4230 to 4305, 3200 to 3268, 2027 to 2095, 2070 to 2138; `coordinator.py` 10729 to 10738, 10446 to 10454, 9976 to 9984, 10432 to 10440, 3731 to 3742, 10707 to 10716; `thermal_model.py` 1785 to 1876; `sensor.py` 2776 to 2780.

## Contract checks

- Seam: one owner per concern; no new write path into state another module owns. The arbiter calls four functions and holds no learned state.
- Shape: A changes no plan and no write. What it adds (a listener, a store, attributes on one sensor) the finding names.
- Sibling designs: all 30 other `design/*` refs were read for `pump_arbiter.py`, `wear.py`, `sensor.py`, `store.py`, `freq_control.py`, `tests/features.py` and `tests/closures.json`. The ones touching `pump_arbiter.py` or `freq_control.py` are merged (R10-WATER-SETPOINT-FEEDBACK 3405, R10-GENERIC-HEAT-CURVE and -PERSISTENT 3402, R10-COP-GATE 3371, R10-WHY-NOW-WIDGET 3346, r10-ceiling-probe 3050, r10-livestate 2675). Unmerged with an overlap: R10-COMBI-TANK-PR-B (`sensor.py`, the hot-water energy and cost sensors, another class than `CompressorStartsSensor`) and R10-ADVISOR-STEADY-START (`tests/features.py` only). No two designs claim one seam. `D7.md` states no rule this note meets or breaks beyond "name one owner".
- Cost: one new module, three production files, the suite. Fits L.

## Decisions routed

- decision: orchestrator. `design.md:95` hot files are short by what a new store costs in this tree: a schema entry in `store.py` (the map holding `pump_duty` at `:481`), `LOADERS` in `tests/finite_boundary.py:470`, `_FR_STORES` in `tests/features.py:14768` (which fails on an undispositioned store), and the module's entry in `docs/architecture.md` that `tests/entities.py` reads. Add them to the group's hot files when it gets its roster entry; the previous verdict's point that the group has none still stands.
- decision: orchestrator. Pull request 3420 now carries parts A and B together and a supply minimum-run hold that is none of A to E (see the last section). Whether the build starts from that head by cutting it down, or from an empty branch using it as reference, and where the supply hold goes, is yours; B still waits on the owner's product call routed in round 1.

## Notes for the fixer

- `design.md:42` against `design.md:83`: the heated gate (inlet minus set-point at least 2 K) is written for both directions, but for space to hot water the inlet is never 2 K over a set-point, so the table's three "kept" rows would count nothing and test 1 could not pass as written. State the gate per direction (the source-leg minimum for space to hot water is the reading the table supports) and pin it with those three rows. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n10)
- `design.md:46`: n has no ceiling, so after weeks of daily episodes it takes several half-lives of avoidance to fall under 2.5 (from 40, about 56 days) before a firmware change is re-tested. Harmless in A; B's and C's designs must bound n or shorten the path. Also "at least two fresh episodes" is three from just under 2.5. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n11)
- `design.md:48`: `wear.py:101` returns an empty counter only for a non-dict top level; a bad `lifetime` becomes 0 and bad month rows are skipped. The note's own rule (empty on any invalid shape or bound) is the one to build, not the cited behaviour. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n12)
- `design.md:23`: "pure learner, no Home Assistant import" and "registers the listener, holds the store" are in one module. Keep the learner class importable and testable with no Home Assistant object, as `dhw_learning.py` separates its profile from its store. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n13)
- `design.md:50`: `CompressorStartsSensor.extra_state_attributes` (`sensor.py:2780` at dbd1ab5b07) reads the coordinator payload through `entity.py:290` today; the learner read is a second source in one property. Keep it one call returning a finished dict, and check no entity snapshot under `tests/golden/` records that sensor's attributes before adding keys. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n14)
- `_write` (`pump_arbiter.py:1332`) and `_arbitrate` (`:1466`) each gain a call; check `functions_cc_over_15` and `methods_over_150` before and after, since a guard around the report line is a decision point. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n15)
- `_write` returns before the service call when the recorded value does not differ (`pump_arbiter.py:1337`), so a `hold` re-send of the same option reaches the learner only if reported ahead of that return; the void rule at `design.md:42` needs it. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n16)
- Items n1 to n7 and n9 of the note stand as written. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n17)

## Pull request 3420 at e05c6b1ccc against this design (non-blocking)

Read as data: the diff against dbd1ab5b07 (17 files, 1003 insertions), both new modules in full, and the note's "Implementation deviations" section. Not run.

Agrees with the design:
- The learner is its own module of the same name with its own `QuarantiningStore`, version 1, keyed per config entry; `store.py`, `_FR_STORES` and `tests/finite_boundary.py` register it.
- Its own state-change listener on the frequency sensor, else the power entity, outside `_listen`; the listener only records the edge, the arbiter's next pass confirms it after a named 30 s, the edge keeps the listener's time, no timer is armed. This is the design's edge tracker.
- Signal order frequency, else power at `on_threshold_kw`. Constants 2 K, 1 min, 3 min, 14 days, 5, 0.5 as named constants.
- Episode opens on a single-duty mode change while running, with demand and the plan held; stopped inside the window, kept at expiry, void on defrost, boost, disinfection, supply off, a foreign mode write and loss of signal; off time censored by a later write. Select transport only.
- Deviation "3a not implemented": agrees, it is part C.
- No file under `tests/golden/` changed; `coordinator.py` gains no attribute.

Conflicts with the design:
- Scope. `_share` reads the estimate through a split hook and can serve space first or give the whole step to the first duty: that is part B, with rule (c) that the owner has not ruled on. A must read nothing. `supply_hold.py` (10 min minimum run and pause on supply writes, a held write retried by `supply_tick`, `cycle_supply`, ten changed lines in `coordinator.py`, the constants of `early_cutoff.py` moved) is a behaviour change no part of the design names and no finding in the note measures; it also reads the learner's running-since. Both must leave an A build.
- Seam. Learned state sits on `ArbiterState` (a new field, plus the order latch); the design keeps `ArbiterState` unchanged with a registry in the new module. The module imports `pump_arbiter.py` and the arbiter reaches back through a hook registry; the design forbids the import and has the arbiter pass a reader and a context.
- Running signal. Classified inside the learner module as frequency above 0.0; the design puts the classifier and edge tracker in `wear.py` with a named floor (note item n9).
- Estimate. Recomputed from up to 200 retained episode rows with timestamps, the cap shared by both directions and applied on close only, not on load; the design stores two decayed counts per direction and a 32-entry off list. There is no on/off hysteresis and no stored latch, so round 1's point 8 is open in the implementation.
- Load. Invalid rows are dropped one by one and the rest kept; the design returns an empty learner on any invalid shape. A failed load is marked loaded and not retried.
- Heated gate reads the return entity only, not `_flow_inlet_c`.
- Void list. Adds fault, backup-heater and booster flags, a mode outside auto and economy and a person's change, all compatible; lacks the set-point-below-base rule for 3405's loop (item n5) and the same-option re-send.
- Publication. In the diagnostics download under one key with p, n, off minutes and a flag; the design publishes counts and durations on the compressor-starts sensor. Either avoids the coordinator payload; the designer or the owner picks one, the design as approved says the sensor.
- Tests. Present: stop with off time, kept control, defrost void, reload, the gate thresholds, supply-hold cases. Absent against `design.md:83-89`: the table replay with the 14 s and censored rows, each void cause in turn, the `unavailable` and one-frame-zero tracker cases, the malformed payload, the off-list cap, the flat-price and no-stop null controls over plan and written commands, and the attribute-key test. The split-order tests belong to B.

Usable as the start for A: the episode and void logic, the listener with pass-confirmed debounce, the store registration in the three census sites, and the stop, kept, defrost and reload tests, once moved behind the design's seam.

## Security, as for every outside contribution

The design ref holds one markdown file; nothing in it or in pull request 3420 was executed. The three build conditions of round 1 are in the note as items n1, n3 and `design.md:50`. In the implementation the stored list is bounded only on close, which is the n3 condition unmet on load.

## Not checked

- The cadence of `_record_accuracy` and the contributor's count of 5 against 12 starts; no bundle is on either ref.
- `pump_arbiter.py` at e05c6b1ccc was read as a diff only; `tests/closures.json` and `dev/audit/rounds/round4/D6/` of that pull request were not read.
- Merge status of sibling designs is by merge-commit name, not by pull-request contents.

Seat tokens: subagents 42872, 73178 and 70157; the harness reports no figure for the main loop.
