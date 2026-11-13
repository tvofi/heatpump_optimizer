# R10-START-COUNTER-EDGES, part D of outside pull request 3420: the start counter fed from running-signal edges

Base and code read: origin/main e23124ff6e45bac1d48b4a775dad555a37965355 (part A, R10-DUTY-SWITCH-RESTART-LEARNING, is merged there; no predecessor handoff head exists). Answers the fixer's BLOCKED.md at handoff-wip/r10-start-counter-edges bf6e97cbab2c, accepted in full by the brief. Part D is Bankaifan's (pull request 3420), with thanks. No finder harness: outside report, owner-routed; the fixer builds the synthetic traces named under Evidence.

## Facts at e23124ff6e

- Today's counter: `_observe_compressor_start` (`coordinator.py:10487`) runs from `_record_accuracy` (`coordinator.py:10017`) once per refresh, `update_interval` = `optimization_interval` (`coordinator.py:3547`; `DEFAULT_OPTIMIZATION_INTERVAL`, `const.py:1648`), in every duty mode. It reads the meter (`_measured_power`, `coordinator.py:6706`, entity `CONF_POWER_ENTITY`) and confirms a class after `START_HYSTERESIS_SAMPLES` consecutive samples (`wear.py:139`). So a stop and restart between two refreshes counts nothing, and a run shorter than that many refreshes counts nothing either.
- Part A's listener: `duty_switch.attach` from `pump_arbiter._listen` (`pump_arbiter.py:2041`); `apply` returns before `_listen` in duty mode off (`pump_arbiter.py:1725`), and `release_listeners` detaches and resets the tracker (`duty_switch.py:474`). The pending edge is confirmed only by `note_pass` (`pump_arbiter.py:1754`), which also does not run while the optimizer mode is off (`pump_arbiter.py:1748`). The arbiter tick, `_TICK`, is one minute (`pump_arbiter.py:258`).
- Part A's void context reads heater and booster entities only (`electric_heat=_lit(...)` in `_switch_context`, `pump_arbiter.py:1571`), not the meter's immersion latch `_immersion_active` (`coordinator.py:9116`), which sets after two refreshes over nameplate times `IMMERSION_FACTOR` with power commanded.

## 1. Owner of the running signal and its confirm clock

**Decision: option (b), a new read-only HA-glue module beside `wear.py` (in prose here: the running-signal module; it does not exist yet).** It owns, per coordinator in a weak registry on the pattern of `duty_switch._RECORDS`: the listener on the frequency sensor else the meter, the reader (moved whole from `pump_arbiter._running_signal`, `pump_arbiter.py:2044`), one `wear.EdgeTracker`, and the confirm clock. Consumers subscribe a callback and read the settled and pending class; it writes nothing and never triggers a pass. `wear.py` stays pure and keeps the classifier, tracker and counter.

**Confirm clock**: a one-shot `async_call_later` of `wear.EDGE_DEBOUNCE_S`, armed when a change goes pending and cancelled when it clears. A frequency held at 40 Hz fires no later event; the timer confirms it at the debounce in every mode, with no polling and no second clock. `duty_switch.note_pass` stops calling `tracker.confirm` and reads the module's pending flag.

**Lifecycle**: the coordinator attaches it once in setup, after the ledger restore (`coordinator.py:8312`), so no edge reaches a counter that `from_dict` then replaces, and detaches it at shutdown beside `pump_arbiter.release` (`coordinator.py:6622`). The coordinator hands three things at attach: its entry config, a threshold callable over the live thermal params (`on_threshold_kw`), and an element-on callable over the immersion latch, so the module reads no coordinator private. The arbiter's `_listen` subscribes the duty-switch record and `release_listeners` unsubscribes it; mode off detaches nothing of the signal.

**Consumers**: the start counter, held where it is (`_start_counter`, persisted in the ledger store, `coordinator.py:8354`), fed by one short coordinator callback that replaces `_observe_compressor_start` (wear ledger line plus `_schedule_ledger_save`); and `duty_switch`, whose record loses `tracker`, `reader`, `unsub` and `note_signal`, and whose `note_mode_write` reads the module's settled class.

**`const.py:1032`'s comment must then say**: off (the default) makes the arbiter write nothing and read no pump entity; the compressor's running signal is observed in every mode for the start counter, by the running-signal module. That was already untrue of the integration as a whole today, since the meter is sampled for the counter in every mode; the sentence was about the arbiter and now says so.

**One owner per seam (decision 0013; `fixer.md` step 17)**: (b) gives the running signal one owner and two consumers that each own their state. (a), the duty-switch record attached from setup, makes the arbiter's switch learner the start counter's feed: either it reaches the coordinator's counter or it holds the counter in its own store, and it keeps listening in mode off, which the arbiter's own off rule refuses. Rejected for that coupling, not taste.

**Score** (instrument: `python3 -m tools.audit.archscore.vector .` at the base and at the head; baseline in Figures). Expected: `coord_footprint` down (the sampled method out, one attach and one callback in); `coordinator_private_reach`, `private_cross_module`, `import_cycle_modules` flat (the module imports `wear`, `freq_control`, `thermal_model`, never `duty_switch` or `pump_arbiter`; `duty_switch` imports it); `layer_violations` flat (`wear.py` keeps no Home Assistant import); `dead_members` flat only if `START_HYSTERESIS_SAMPLES` and the counter's `_streak` go with the sampled path. Budgets: `coordinator_attrs` and `coordinator_multiassigned_attrs` flat; `coordinator_loc` down. Any rise is a design defect, not a raise.

## 2. The immersion rule

The reader returns no signal (`None`) while the element-on callable is true **on the meter source only**; the frequency sensor does not see the element, so it reads through. This replaces `StartCounter.observe`'s freeze (`wear.py:131`).

Effect on part A, meter-only installs: a latched window settles `None`, so an open episode not yet stop-checked is **void**, and a checked stop awaiting its off time closes **stopped, off time censored** (`DutySwitchLearner.edge`). Today A books such an episode **kept**, because a compressor stop under element draw stays over the threshold: a masked stop counted as evidence against stopping, biasing `p` down. Voiding is right: the meter cannot see the stop. Frequency installs: unchanged. **Residual, not fixed**: the latch sets two refreshes after the element cuts in, so episodes inside that lag still read the combined draw; and an element alone with the compressor off is never latched and reads as a run, today and after. Both are the latch's own rule; duplicating it per event would make a second immersion owner.

## 3. What counts as a start; continuity

A start is a confirmed edge to `True` whose last non-`None` settled class was `False`. `None` never counts and never overwrites the last class, so running, unknown, running is no start; stopped, unknown, running is one (starts inside the gap are lost, as the freeze loses them today). The counter's method becomes an edge fold; `_streak` goes.

**Stored shape unchanged** (`lifetime`, `months`, `running`; `StartCounter.as_dict`): `running` keeps its meaning, the last confirmed class, so the first edge after the upgrade continues from the stored one and no migration exists. Stored `running: true` and a pump running at boot is no start; stored `false` and running at boot is one, as today. Neither path resets or double-counts. The callback also schedules a ledger save on a stop edge, so the stored class is current across a restart. The month key is the edge's first-changed time, not the confirming refresh: a start within one refresh of a month boundary can land in the earlier month, an intended correction.

## 4. Premise correction and the null control

`_effective_cycling_cost` (`coordinator.py:10473`) reads `_wear_price` (`coordinator.py:10466`): config replacement cost over rated starts, no count. The counts feed the `wear` ledger line (`coordinator.py:10512`, only at a nonzero price), `freeze_month_report(compressor_starts=...)` (`ledger.py:631`), and the insight payload's `compressor_starts` (`coordinator.py:10749`, the sensor's state). The plan is identical by construction, so it is pinned as a regression, not claimed as a control. **The control is on the counts**: a meter trace whose every on and off phase spans at least two refresh periods, no start within one period of a month boundary, gives identical lifetime, months, wear lines and month-report count through the old sampled path and the new event path. Perturbation: one stop and restart inside one period adds exactly one start on the new path and none on the old.

## 5. Build plan

Files: the new module; `wear.py`; `duty_switch.py`; `pump_arbiter.py`; `coordinator.py`; `const.py`; `tests/features.py`; `tests/closures.json` (the new module in a measured closure); `tests/seam_map.json` (the `_observe_compressor_start` entry follows its replacement). Tests first, failing today:

1. Count control and perturbation (section 4), on a replay of meter events at the default interval.
2. Held 40 Hz after a stop, no later event: one start, confirmed by the timer in duty mode off.
3. `unavailable`, `unknown`, non-numeric: no start; running, `None`, running: no start; stopped, `None`, running: one.
4. Meter source with the latch on reads `None`; frequency source ignores it; A's episode is void, and a checked stop is censored.
5. Continuity: a stored payload from e23124ff6e's `as_dict` loads and continues; restore before attach (an edge before the restore is not lost); `running` stored after a stop edge.
6. Part A's listener pins (the `duty_switch` checks in `tests/features.py`) re-pointed at the module, none deleted; mode off to observe keeps the settled class.

Mutants: the count condition, the `None` guard on the last class, the element term and its meter-only scope, timer arm and cancel, the attach-after-restore order, the stop-edge save. **Size: L, not M** (six production files, A's listener tests re-pointed). One pull request: a split leaves two listeners, two owners, between merges. No golden moves (the coordinator goldens carry no insight start count; their `compressor_starts` is the simulation's); neither claim file is touched.

## Hot files, position, carries

After R10-DUTY-SWITCH-RESTART-LEARNING (merged). Hot: `pump_arbiter.py`, `duty_switch.py`, `coordinator.py`, `tests/features.py` (pull requests 3561, 3562 and 3532 edit it: carry 0's merge-tree check). Ships in round 10 only if merged when the closure stamp is ready, else round 11.

## Notes for the fixer

- The roster still says size M, files three, no architect note; this note makes it L with the file list above. Carry: R10-START-COUNTER-EDGES (item n1)
- `dev/audit/rounds/round10/D3/s3/mutants.py` targets the streak line by text, and README claim C-RM-58 cites `START_HYSTERESIS_SAMPLES`: check both and README's start-counter wording before deleting the constant. Carry: R10-START-COUNTER-EDGES (item n2)
- The compressor-starts sensor stays available only with the meter (`sensor.py:2775`); a frequency-only install counts but publishes nothing, unchanged here. Carry: R10-START-COUNTER-EDGES (item n3)
- Measure the default install's starts per day on the item 1 trace before claiming any figure for missed starts; the contributor's count is unverified. Carry: R10-START-COUNTER-EDGES (item n4)
- `_running_signal`'s `CONF_POWER_ENTITY` and the counter's meter are the same key (`const.py:98`): one entity, so the meter-only null control compares like with like. Carry: dismissed: verified in this note (item n5)

## Figures

At e23124ff6e, `python3 -m tools.audit.archscore.vector .`: coord_footprint 2503, coordinator_private_reach 2, private_cross_module 10, import_cycle_modules 0, layer_violations 13, dead_members 1.
