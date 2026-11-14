# R10-START-COUNTER-EDGES, part D of outside pull request 3420: the start counter fed from running-signal edges

Designer round 2, answering `Design review: revise 111d3c3f0882d643aeb8d36131f942df75233948 architecture-unsound` (design-verdict/R10-START-COUNTER-EDGES at 6fe6b093c4). Base and code read: origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439; round 1 read e23124ff6e. No predecessor handoff head (R10-DUTY-SWITCH-RESTART-LEARNING is merged). Sibling read at its tip, design/R11-OUTSIDE-HONEST-STARTS-RUNS 0c692c86d2. Part D is Bankaifan's (pull request 3420), with thanks. No finder harness: outside report, owner-routed; the fixer builds the synthetic traces under Evidence. Every line below was re-read at a77d71fb. Held from round 1 and confirmed by the review, unchanged: option (b) and its rejected alternative (a), the stored shape, the premise correction (`_effective_cycling_cost`, `coordinator.py:10474`, reads `_wear_price`, `coordinator.py:10467`, no count), section 3's start rule and the score expectations; they are restated only where this round changes them.

**Pull requests in flight.** 3569 changes one line in `Direction.decay` and one docstring line in `duty_switch.py`: every `duty_switch.py` cite below moves down by one line, no cited body changes. 3532 adds the both-step order (`_Record` gains a field, a new function after `starts_attributes`) and the duty-switch store to the coordinator's `_restored_stores` and `_FACTORY_VOID`: `duty_switch.py` cites move by +16 to +36 lines, `pump_arbiter.py` cites by +19 to +23, coordinator cites by +1; no cited body changes in either (checked `git diff origin/main...<head>` per file). Neither touches `wear.py`, `thermal_model.py` or the ledger restore.

## 1. Lifecycle: where the attach really is (revise point 1)

Facts. The ledger load is one of the loads `__init__` spawns and nothing awaits (the spawn loop, "self._spawn(load())" at `coordinator.py:3592`); `async_config_entry_first_refresh` (`__init__.py:318`) can run `_record_accuracy` before it lands. `load_mapping` swallows a read error and returns `None` (`store.py:683`), and `_async_load_ledger` then returns early (`coordinator.py:8308`), as on a fresh install; otherwise it replaces the counter, `self._start_counter = StartCounter.from_dict(...)` (`coordinator.py:8313`). Today a sample folded before that line is overwritten: a latent loss on the sampled path too.

**Attach: in `__init__`, synchronously, a hass registration like those it already makes there (`watch_away_inputs`, `InputReturnWatch`), placed before the loads are spawned.** Detach: in `_release_registrations` (`coordinator.py:3601`), which the entry's unload callbacks run on every unload including a failed setup (#236, registered at `coordinator.py:3572`) and `async_shutdown` runs again (idempotent). The module's detach drops the listener and cancels a pending confirm timer. An unload can therefore never precede the attach, and no listener outlives the entry; the review's load-after-unload case has nothing to detach.

**The counter before the load, and the restore.** `StartCounter` (pure, `wear.py:99`) gains an unrestored state: the default instance (`coordinator.py:3910`) folds no edge but queues it in order; the restore becomes an instance method replacing the assignment at `coordinator.py:8313`. It reads the stored payload exactly as `from_dict` does today, then replays the queue against the stored `running`, and returns the start times the replay counted. `_async_load_ledger` calls it in a `finally`, so every exit restores: the early return (no store, fresh install, unreadable store, all with no payload) and an exception after the read. The coordinator then books one wear line per replayed start, after the ledger restore at `coordinator.py:8310` so no line is overwritten, and schedules one save; both are skipped when `_entry_released` is set (a load landing after unload restores in memory and writes nothing). The queue lives in the counter, so `coordinator_attrs` and `coordinator_multiassigned_attrs` stay flat.

**What readers see before the load lands**: the default counter, zero lifetime and months, as today: the insight payload ("self._start_counter.lifetime", `coordinator.py:10751`) and the month report ("compressor_starts=self._start_counter.month_count", `coordinator.py:10539`) read it unchanged. The queue's starts appear at the restore; none is lost and none is counted twice.

```
__init__ ── attach(module, entity, reader, element callable) ──> listener + confirm timer
         ── spawn(_async_load_ledger) ............................................┐
HA state event ─> module: reader -> class -> EdgeTracker.note ─> edge ─> subscribers
                                                   ├─ coordinator callback: counter.fold(edge)  (queued while unrestored)
                                                   └─ duty_switch record (only while the arbiter listens)
refresh: _update_current_state -> _detect_immersion -> module.re-read (one line, every mode)
_async_load_ledger: ledger restore -> finally: counter.restore(stored or None) -> wear lines + save unless released
_release_registrations: module.detach (unsub + cancel timer)
```

## 2. Immersion: the sampled-path orders and the rule (revise point 2)

Per refresh today: `_update_current_state` (`coordinator.py:6070`) sets `_measured_power`, calls `_detect_immersion` (`coordinator.py:6712`), and later the cycle runs `_record_accuracy` (`coordinator.py:6124`), which folds the sample (`coordinator.py:10018`). The latch sets on the second over sample ("self._immersion_over_count >= 2", `coordinator.py:9117`), over meaning draw above nameplate times `IMMERSION_FACTOR` with power commanded (`coordinator.py:9110`).

| case | sampled path today | event path, latch only (round 1) | event path, this rule |
|---|---|---|---|
| S1 element cuts in, compressor off, over | streak 1, then latch at the next refresh freezes it (`wear.py:131`): 0 | edge at 30 s, latch one refresh later: **1, false** | 0 |
| S2 element cuts in, compressor running | no class change: 0 | 0 | 0 |
| S3 compressor stops under the latched element | frozen: stop unseen | `None`: void/censored | same |
| S4 element drops, two-refresh release lag | frozen two refreshes, then observes | `None` through the lag | same; a start under the element counts once at release, as today |
| S5 element over and back inside one refresh period | never sampled: 0 | 1, false | 0 |
| S6 element alone not over (nothing commanded, or under the factor) | counts a start | counts | counts (unchanged residual) |
| S7 meter reporting a value between the on-threshold and the over level for at least `EDGE_DEBOUNCE_S` before over | 0 if over arrives within two refreshes | 1 | 1 (residual) |

**Rule.** On the meter source the reader returns `None` when the latch is set **or the reading itself is over** (the instantaneous test `_detect_immersion` latches on). The over test is factored into one pure function in `thermal_model.py`, beside `on_threshold_kw` (`thermal_model.py:1939`), taking the reading, the thermal params and the commanded draw; `_detect_immersion` calls it, so the latch and the reader cannot disagree on what over means, and the carve-out's threshold ("* IMMERSION_FACTOR", `coordinator.py:10388`) reads the same level (one owner of the level, no value moves). The coordinator hands the module one element callable over the reading, built from the latch and that function: the module reads no coordinator private. The frequency source ignores it. Because the latch and the commanded draw change at a refresh and fire no meter event, the coordinator asks the module to re-read once per refresh, right after `_detect_immersion` (review carry r4).

**S6** is not a regression: both paths count it today and the classifier's commanded-power term is #11's rule. **S7** is a new false start only on a meter whose reports average over 30 s or more; closing it needs the start held until two refreshes pass without a latch, which puts the refresh clock back into the event path, two clocks for one signal. Carried as a decision, measured first (note n6).

**The check that pins it**: test 4, on a meter-only replay at the default interval (`DEFAULT_OPTIMIZATION_INTERVAL`), drives S1, S3, S4 and S5 through the module and the counter; expected starts 0, 0, 1 (a start under the element) and 0, with S3's open episode void. Mutants: drop the instantaneous term (S1 and S5 go to 1), drop the latch term (S3 with the element alone under the over level reads as running, so the episode is kept), scope the element term to both sources.

## 3. One owner of the settled value, and what R11-OUTSIDE-HONEST-STARTS-RUNS may rely on (revise point 3)

The sibling's coordinator reads "running now = duty_switch's settled class, else the executing step" and its carry n5 cites the tracker at `duty_switch.py:480` and the settled reading at `duty_switch.py:487`. This build moves that tracker out of the duty-switch record. **The single owner of the settled running class is the running-signal module (new, read-only HA glue beside `wear.py`, named in the build for the term, running-signal, hyphen to underscore).** It exposes one read for a coordinator, the running-now read (named likewise in the build):

- returns `True` when the settled class is running and no change is pending, `False` when it is stopped and none is pending, and `None` otherwise: before the first confirmed edge (at least `EDGE_DEBOUNCE_S` after the attach; `EdgeTracker.settled` starts `None`, `wear.py:76`), with neither a frequency sensor nor a meter configured, with the entity unavailable or non-numeric, on the meter source while the element rule above holds, and while a change is pending;
- is available in every duty mode, mode off included, from the coordinator's construction to its release; it never triggers a pass and writes nothing.

`duty_switch.note_mode_write` reads it as `is True`, which is exactly today's expression at `duty_switch.py:487`. The sibling reads it and keeps its executing-step fallback for `None`, which now covers the cases listed, not "no reader attached". **Merge order, `decision: orchestrator`**: this group first (L, round 10, no open predecessor), then the sibling (XL, after R10-ADVISOR-STEADY-START). If the sibling merges first, its one read goes through the duty-switch record as written, and this build re-points that line to the running-now read in the same pull request; `coordinator.py` is hot for both.

## 4. Evidence, by file (`tests/features.py` unless named)

Failing first at the base: (1) the perturbation: one stop and restart inside one refresh period counts one start (today 0); (2) the lifecycle: an edge confirmed before `_async_load_ledger` lands survives the restore, on a stored payload, on a fresh install (no store) and on a load landing after `_release_registrations` (no wear line, no save). Then: the count control (round 1's section 4, exclusion widened to two periods, carry r1); held 40 Hz confirmed by the timer in duty mode off; `unavailable`/`unknown`/non-numeric and the `None` continuity rules; test 4 above; part A's listener pins re-pointed, none deleted, and arbiter detach no longer resetting the settled class; a stored e23124ff6e-shape payload continuing. Mutants: the count condition, the `None` guard on the last class, the queue replay, the `finally`, the released guard, both element terms and the meter-only scope, timer arm and cancel, the per-refresh re-read, the stop-edge save. No golden moves; neither claim file is touched.

## Hot files, position, carries

After R10-DUTY-SWITCH-RESTART-LEARNING (merged). Production files: the new module, `wear.py`, `thermal_model.py`, `duty_switch.py`, `pump_arbiter.py`, `coordinator.py`, `const.py` (the comment at `const.py:1032`, as round 1 worded it); plus `tests/features.py`, `tests/closures.json`, `tests/seam_map.json`. Hot: `duty_switch.py` and `pump_arbiter.py` (3532, 3569), `coordinator.py` (3532, the sibling), `tests/features.py` (3561, 3562, 3532: carry 0's merge-tree check). Ships in round 10 only if merged when the closure stamp is ready, else round 11 (owner, 2026-11-13). No grader changes: no p1/p2 split.

## Notes for the fixer

- The roster says size M, three files, no architect note; this note makes it L with the file list above. Carry: R10-START-COUNTER-EDGES (item n1)
- Before deleting `START_HYSTERESIS_SAMPLES` (`const.py:1240`): `dev/audit/rounds/round10/D3/s3/mutants.py` (M04) and the `tests/mutation_ledger/killed_by/wear.py/` entries target the streak line by text, and claim C-RM-58 in `dev/audit/rounds/round3/D6/claims.py` cites the constant for the peak guard; re-point each. Carry: R10-START-COUNTER-EDGES (item n2)
- The compressor-starts sensor's availability reads `measured_power_available` (`sensor.py:2776`); a frequency-only install counts but publishes nothing, unchanged. Carry: R10-START-COUNTER-EDGES (item n3)
- Measure the default install's starts per day on the control trace before claiming any missed-start figure; the contributor's count is unverified. Carry: R10-START-COUNTER-EDGES (item n4)
- The bare test stub's hass must accept the constructor's new registration as it does `watch_away_inputs`; a stub that returns no unsubscribe must leave detach a no-op. Carry: R10-START-COUNTER-EDGES (item n5)
- S7 (section 2): measure on a 60 s averaged meter trace whether a held intermediate value precedes over; if it does, the owner decides between the residual and a refresh-held start. Carry: R10-START-COUNTER-EDGES (item n6)
- Folded from the review: the two-period exclusion (r1); the meter-to-frequency source change on an install with both, stated in the body with its test (r2); `tests/features.py:9018-9024` and the G8 corruption barrier at `tests/features.py:56025` re-pointed, none deleted (r3); the per-refresh re-read pinned against an unchanged meter (r4). Carry: R10-START-COUNTER-EDGES (item n7)
- For the sibling: the running class is the running-signal module's running-now read (section 3), not the duty-switch record's tracker; its `None` cases are listed there and its executing-step fallback stays for them. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n8)

## Figures

At a77d71fb, `python3 -m tools.audit.archscore.vector .`: coord_footprint 2503, coordinator_private_reach 2, private_cross_module 10, import_cycle_modules 0, layer_violations 13, dead_members 1. Expected after the build: coord_footprint down; the other five flat (the module imports `wear`, `freq_control`, `thermal_model` only; `duty_switch` imports it). Any rise is a design defect, not a raise.

## Size, and what the fixer proves first

**Size L, one pull request**: seven production files, part A's listener tests re-pointed; a split leaves two listeners and two owners between merges. **First proof**, before any production line: the two failing tests of section 4 at a77d71fb (or the merge base then), each red there for the stated reason, the perturbation at 0 starts and the pre-restore edge lost to `from_dict`; and, once the module exists, test 4's S1 case red under the latch-only mutant, so the instantaneous term is shown to bite.
