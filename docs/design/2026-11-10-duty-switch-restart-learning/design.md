# R10-DUTY-SWITCH-RESTART-LEARNING, part A: observe, estimate, persist, publish

Revision 1, answering `Design review: revise edf2ceb333956fa6797d6bb30d7c5b72f440123e`. Base: origin/main d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a. Every line cited below is at the predecessor's head 068074f0f2c2dfdb57fc1821ed39f3510bc913ed (pull request 3405, R10-WATER-SETPOINT-FEEDBACK), which this group builds after. The finding, install description and reasoning are Bankaifan's, pull request 3420, with thanks; their note is this ref's parent commit edf2ceb333 and stays unchanged on 3420. No finder harness: outside report, owner-routed.

## Finding (Bankaifan, 2026-11-10, alpha innotec LWDV 91-1/3, Luxtronik 2.1, select transport, 15 min steps)

| Mode write | Direction | Source leg | Return at write / set-point | Compressor | Off time |
|---|---|---|---|---|---|
| 14:02:53 | hot water to space | 17 min | 44.2 / 32.0 °C | stopped after 19 s | 8.2 min |
| 14:18:53 | hot water to space | 3 min | 43.6 / 32.0 °C | stopped after 12 s | censored: HPO wrote the mode before the restart |
| 15:00:01 | hot water to space | 29 min | 51.0 / 32.0 °C | stopped after 12 s | 8.5 min |
| 03:32:32, 13:45:53, 14:15:53 | space to hot water | n/a | n/a | ran on | n/a |
| 13:29:53 | hot water to space, 14 s leg | 14 s | return not heated | ran on | n/a |

`cycling_penalty_batch` (`optimizer.py:1546`) prices the swing of the combined series (`optimizer.py:4707`), so this switch costs nothing in the plan, and nothing observes it.

## Scope (revise point 6)

The reviewer's split is adopted. This group is **A only**: the learner exists, records, estimates, persists and publishes; **nothing reads the estimate to change a plan or a write**. B (arbiter order latch and minimum share), C (planner price), D (start counter fed from edges) and E (mode write ahead of the supply switch-on) are the orchestrator's to place; B waits on the owner's product call the verdict routed.

## Owning seam (points 1, 2, 3)

**Owner of episodes, estimate and store: a new module, duty_switch.py, beside `wear.py`.** It holds a pure learner (no Home Assistant import, like `wear.py`), its own `QuarantiningStore` keyed per config entry (one entry is one pump) on the pattern of `dhw_learning.py:111`, and its per-entry registry on the pattern of `_STATES` (`pump_arbiter.py:374`). `ArbiterState` gains no field and `_persist` (`pump_arbiter.py:1699`) keeps saving only `written`.

**Owner of "the compressor runs" and its edges: `wear.py`**, which already owns the start counter. It gains a pure classifier and a debounced edge tracker. Signal order: the frequency from `freq_control.resolve_reading` (the existing owner of the Hz reading, used at `coordinator.py:10729`) above a named floor where one is configured and numeric; else metered power at or above `on_threshold_kw` (`thermal_model.py:1785`), the one threshold both existing readers already share; else no signal. Readers in this group: the new learner only. **Stays, start counter** (`coordinator.py:10446`, fed from `_record_accuracy` at `coordinator.py:9976`): moving it changes the counted starts that feed `_effective_cycling_cost` (`coordinator.py:10432`), a behaviour change this group's finding only reports; it is part D. **Stays, 3405's loop** (`_ran_kw`, `pump_arbiter.py:1204`, read at `:922` and `:1423`): it controls on the size of the draw error, so it needs kW and its own sample period, not an edge; it keeps the shared threshold.

**Owner of the listener: duty_switch.py.** It registers on the frequency sensor, else the power entity, and keeps its unsubscribe in its own registry. The arbiter attaches it from `_listen` (`pump_arbiter.py:1667`) and detaches it in `release_listeners` (`pump_arbiter.py:1661`). **`coordinator.py` gains zero lines and zero attributes**; `coordinator_attrs` and `coordinator_private_reach` do not move. The new module never imports `pump_arbiter.py` (`import_cycle_modules` is at zero): the arbiter hands it a reader callable at attach.

## Shape

```
listener event --> reader() --> wear classifier --> edge tracker --(edge: when, running)--> learner
_write, slot "mode" landed (pump_arbiter.py:1332) --(when, old option, new option, context)--> learner
_arbitrate, each pass (pump_arbiter.py:1466) --(when, context)--> learner: void checks, close window, save if changed
sensor.py:2776 extra_state_attributes <-- learner summary (counts, durations)
```

Calls the arbiter makes, all into duty_switch.py: attach(hass, entry id, entities, reader), detach, note-mode-write, note-pass. Read API for B and C, unused in A: per direction, usable (bool), stop probability, median off seconds.

Context (built by one arbiter helper from `ArbiterInputs`, `pump_arbiter.py:346`): supply on (`_pump_off`, `:1639`), defrosting, disinfecting, boost held, immersion active, inlet temperature (`_flow_inlet_c`, `:714`) and written space set-point, source-leg age (`dhw_since`, `:329`, or the mode record's age), target duty has demand (room under `_planned_room`, `:575`; tank under its set-point), plan keeps the target duty on, origin (share, lease, other).

**Episode.** Opens on a landed mode write between the two single duties while the tracker says running, and counts only if the circuit was heated (inlet minus set-point at least 2 K; with no inlet entity, source leg at least 1 min), the target has demand and the plan stays on. Within 3 min: **stopped** on a stop edge, **kept** at expiry, **void** on supply off, any other write (a re-send by `hold`, `:1275`, included), defrost, boost, disinfection, immersion, a set-point below the open-loop base (3405's loop), or loss of signal. Off time runs to the next start edge, censored by any HPO write in between. One open episode at most.

**Edge tracker.** An event whose class equals the settled class returns after one parse and compare. A changed class is confirmed after a named debounce, by the next event or by the arbiter's pass; the edge carries the first changed event's time. This replaces a time-spacing throttle (`power_guard.py:82`) deliberately: that throttle can drop the final event to zero, after which no event arrives and the stop is never seen. The listener never calls `apply` (`pump_arbiter.py:1449`).

**Estimate and its invariant (point 8).** Per direction, decayed counts k (stopped) and n (stopped plus kept), half-life 14 days. Decay scales both alike, so **p = k / n never moves with age; only n falls.** Usable switches **on** at n >= 5, evidence spanning two days, p >= 0.5; once on it stays on until n < 2.5 or p < 0.3. The latch is stored. One episode lifts n by at most 1, so a direction that fell under 2.5 cannot cross 5 on one episode: no toggle at the threshold. When B or C avoid a direction, n halves every 14 days, usable drops, the default runs and at least two fresh episodes re-test it: that bounded re-test is the relearn path, and its cost is those starts. Off time: median of a capped list (32, oldest dropped).

**Store.** Version 1: per direction k, n, last-decay instant, first and last episode day, latch, off-time list, void and censored counts. `from_dict` validates shape and bounds and returns an empty learner otherwise, as `wear.py:101` does. Loaded on the first pass; reports before load are dropped.

**Published** on the compressor-starts sensor's attributes, read from the learner in `sensor.py:2776`, never through the coordinator payload (`coordinator.py:10707`), which the goldens snapshot: per direction k, n, stopped, kept, void, censored, median off seconds, span days. Counts and durations only.

## Planner price (point 4): part C, not built here

Direction for C's own design round, not a commitment: the price belongs in the objective closure of `_solve_objectives` (`optimizer.py:4622`) beside `cycling(combined)`, because `_solve_space` (`:4230`) and `_co_optimize` (`:3200`) both score with it and both hold the hot-water and space series separately; the duty sequence comes from the rule `step_duty` (`pump_arbiter.py:466`) already uses; the off time enters as lost headroom at `optimizer.py:4246`; `OptimizationConfig` (`:2027`) gains the two learned values next to `cycling_cost` (`:2070`). An indicator of a duty change is not smooth, which is why C needs its round.

## Alternatives

- **Record on `ArbiterState`, saved by `_persist`** (the contributor's): the pump-duty store holds only the ownership record that `_load` (`:1710`) and `_writable` (`:1731`) filter; a second meaning there puts learned state in the arbiter.
- **Learner as a coordinator attribute**, like the hot-water learner (`coordinator.py:3731`): costs `coordinator_attrs`, which only moves down, and a line in the load list.
- **No listener, sample per arbiter pass**: it would see an 8 min stop, but a void cause and a stop inside one tick lose their order, so the void rule cannot be applied; and D needs edges.
- **Classifier in the new module**: D's reader, the start counter, would then import the switch learner for a signal `wear.py` already owns.

## Sibling sites (point 7)

`git grep -n -E "select_option|await _command\(" -- 'custom_components/heatpump_optimizer/*.py'` prints the only mode write (`pump_arbiter.py:1324`, through `_write`) and its two callers (`:1486`, `:1658`). Observing at `_write` covers every origin:

| Path into space | Site | In A |
|---|---|---|
| split inside a "both" step, hot water first | `_share`, `:1494`, `:1513` | covered, origin share |
| step change, re-solve, away return (arrives as a plan) | `_planned_duty`, `:1129`, `:1151` | covered, origin other |
| lease cap | `_leased`, `:1217` | covered, origin lease |
| re-send | `hold`, `:1275` | same option: opens nothing, voids an open episode |
| boost end | `_without_block`, `:1162`; `:1477` | void while held, covered after |
| disinfection | `:1094`, `:1502` | void while disinfecting; "both" to space is not a single-duty switch |
| supply tick, supply off | `supply_tick`, `:1607`; `:1483` | writes no mode; voids |
| unload | `release`, `:1651` | detach first, no episode |
| set-point gate transport | `desired`, `:1083` | out of scope: no single-duty mode write exists there |

## Evidence, by file (point 5)

All in `tests/features.py`, failing today because the module and the two `wear.py` symbols do not exist:

1. Observer replay of the table: three stopped, three kept, the 14 s row counts nothing, row 2 counts as stopped with no off sample; each void cause in turn turns a stopped episode void.
2. Edge tracker: `unavailable`, `unknown`, non-numeric give no signal and void; a one-frame zero is no edge; a final zero with no later event is confirmed by the pass.
3. Gates: below 5, or within two days, not usable; on at the thresholds; the 2.5 and 0.3 off conditions; decay leaves p unchanged; one episode after switch-off does not switch on.
4. Restart: dict round trip keeps counts and latch; a malformed or out-of-bounds payload loads empty; the off list never exceeds its cap.
5. **Null control, no stops**: an install whose every switch is kept, and
6. **null control, flat prices**: scenario `tests/golden/flat_prices.json`; in both, the plan, the split order and every written command are byte-identical between an empty learner and one saturated at p = 1. This is the stronger control and it holds by construction in A.
7. Attributes carry only the listed keys, all numeric.

**No golden moves; neither claim file is touched.** A moving golden is a defect in the build. The new file goes into a measured closure in `tests/closures.json`. Mutation targets: the count conditions, each void rule, the four latch comparisons, the debounce comparison, and the report line in `_write`. Field check on the contributor's install after B or C; not an acceptance test of A.

## Hot files, position, carries

After R10-WATER-SETPOINT-FEEDBACK. Hot: `pump_arbiter.py`, `wear.py`, `sensor.py`, `tests/features.py`, `tests/closures.json`, plus the new module. Not touched: `coordinator.py`, `optimizer.py`, `dhw_planner.py`, `const.py` (constants live in the new module; `const_modules_over_50` does not move).

## Notes for the fixer

- No signal is never "stopped"; it voids. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n1)
- Class-equality early return and debounce, not a time-spacing throttle; never trigger a pass. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n2)
- Off list capped at 32; counts are two floats per direction. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n3)
- `QuarantiningStore` (`store.py:673`) scrubs poisoned leaves to a default and does not reject, so the learner's own `from_dict` must return empty on any invalid shape. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n4)
- 3405's loop is on the void list by name. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n5)
- 2 K, 1 min, 3 min, 14 days, 5, 2.5, 0.5, 0.3 are named constants from one day on one install, not measured thresholds. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n6)
- Re-read every `pump_arbiter.py` anchor after 3405 merges. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n7)
- The reviewer's `optimizer.py` lines were at another tree; here they are `:4707` and `:4246`. Carry: dismissed: corrected in this note (item n8)
- The frequency floor: check what the sensor reports when stopped before fixing the constant. Carry: R10-DUTY-SWITCH-RESTART-LEARNING (item n9)

Seat tokens: subagents 75890, 49789 and 41294; the harness reports no figure for the main loop.

## Part A as built: where the code departs from this note

The text above is the approved design, unchanged. Part A (`duty_switch.py`) departs from it in the points below; parts B and C build on the code, so where the two disagree this section is the one to read.

- **No read API.** "Read API for B and C, unused in A" was not built: an unused module-level function is refused by `tests/structure.py`'s `dead_top_level_symbols`. `Direction.usable`, `Direction.p` and `Direction.median_off_s` hold the three values; the part that first reads them adds the module-level reader together with its first caller. Control: a reader added with no caller turns that metric red.
- **Stored record.** Version 1 stores, per direction, `k` and `kept_w` (the kept episodes' weight; n is their sum), the decay stamp, first and last day, the latch, the off list and the four integer tallies `stopped`, `kept`, `void`, `censored`. With k and n stored, `tests/finite_boundary.py`'s in-domain probe produced k over n. n has no ceiling but the load bound.
- **Publication is conditional.** A direction publishes its attributes only once it holds a stopped, kept or void episode, and the median only once an off time exists: five `coord_*` goldens snapshot the starts sensor's attributes. A reader of those keys treats an absent key as no observation, never as zero. Control: with the condition removed (the body's mutant `publish_only_observed`) the section's attribute check fails.
- **The feedback-loop void is wider.** An episode voids on any target the loop moved off the open-loop one (`FeedbackRun.sent_c` set), raised as well as lowered; it costs evidence only.
- **Origin** (share, lease, other) is not in `SwitchContext`: nothing in A reads it.
- **Source-leg age** is the age of the mode record the write replaced, not `dhw_since`, which `_leased` has reset by the pass that leaves hot water.
- **The heated gate's space set-point** is the command's, written right after the mode, not the written record, which at that instant is still the hot-water leg's.
- **The heated gate is decided per set-point unit.** The inlet is compared with the command's space set-point only where that set-point is a water temperature (`space_setpoint_unit` flow or return). On the default indoor unit it is the planned room temperature, which a running pump's return is always over, so there the gate is the source leg's age, as it is with no inlet reading. Control: the section's "an indoor set-point, a return 9 K over the room's, and a 30 s leg" row opens nothing, and the same return with a 60 s leg books.
- **The span ages with the evidence.** Once a direction's decayed n is under `SPAN_FLOOR_N` (0.5, one episode a half-life old; a named constant, not a measurement) its first and last day are forgotten, so "spanning two days" is judged on evidence that still weighs. Without it the first day never moved and one year-old episode made six stops on a single day usable. A reader of `span_days` treats 0 beside non-zero tallies as "nothing recent", not as "never observed".
- **The pass does not judge a lost signal.** `DutySwitchLearner.note_pass` takes no "signal known" argument: with an episode open the settled class is unknown only after a confirmed edge to unknown, which `edge` has already voided, and `detach` clears both, so no install could exercise it.
- **Factory reset keeps the store** (`_FR_STORES` in `tests/features.py`), where every other learned estimate is voided. The owner rules on this before any part reads the estimate.
- **The supply minimum-run hold** of pull request 3420 is removed and built nowhere.

## Part B, first pull request: the carries part A left to its first reader

Part B's own rule (the arbiter's split order) is a later pull request of the same group; this one settles what part A's review left to "the part that first reads" and changes no plan and no write.

- **`N_ON` is a decayed weight, not a count of episodes** (part A's body item ef5d3875). Each booking ages the earlier ones first, so five stops ten hours apart weigh under five and a sixth latches; the approved note's "n >= 5" already reads that way, and the code is unchanged. Pinned by the section's check "N_ON is a weight"; control, the check where a stop taking an undecayed n from 4 to 5 switches a direction on.
- **The publication moves with observations, not with age** (item c7d068a1). The starts sensor publishes `p` to two places, which decay does not move, and `n` as the whole episodes still weighing, rounded down; `k` is no longer published, being `p` times `n`. Age alone now moves only `n`, one step per whole episode lost. Pinned by the section's check "age alone moves no published attribute within a day"; its null control is the decayed weight read to two places, the old resolution, which moves within the same reads.
- **Still owed by part B's later pull request**, which first reads the estimate: the module-level reader added with its first caller (item 1b22f416); the owner's ruling on factory reset keeping this store, before that reader merges (item 3c666f5b); a reader taking an absent key as no observation and `span_days` 0 beside non-zero tallies as "nothing recent" (item 90bc5153); evidence accruing at different rates per set-point unit (item d088605d); and the ceiling on `n` the group's ruling sets, which also bounds how often the published `n` can step.

## Part B, second pull request: the arbiter's split reads the estimate

- **The reader and its first caller** (item 1b22f416). `duty_switch.both_step_duty` is the module-level reader, and `_share` in `pump_arbiter.py` is its caller, handing it the pump's record, the step and the plan's next step; the arbiter holds no learned state and computes no share past the two collapses it had. The decision (the duty served first, and whether it keeps the whole step) is made by `DutySwitchLearner.split` and latched on the pump's record per step start, so neither the tick nor a re-solve inside the step flips it. A record not yet loaded splits as before and latches nothing.
- **The rule** (the group's ruling on rule c). Space goes first only where hot water to space is the one usable direction. The first duty keeps the whole step only when the switch into the second is usable, the second share is shorter than `SPLIT_MIN_MINUTES` plus that direction's median off time, and the plan's next step serves the second duty (or both); otherwise the split is today's in the chosen order. With no usable direction the decision is hot water first, not whole: today's split, minute for minute.
- **What the reader reads** (items 90bc5153, d088605d). Only the latches and the median off time: never `n`, the tallies, `span_days` or a published key, so `span_days` 0 beside tallies and evidence accruing faster on one set-point unit move the split only through a latch.
- **`n` has a ceiling**, `N_CAP`, twice `N_ON`, held at each booking and on each pass's decay by scaling both counts alike (`p` does not move). With no further episode a latched direction is under `N_OFF` just past two half-lives, so the default split runs again and re-tests it; a record stored over the cap is held to it by the first pass.
- **Factory reset voids the store** (item 3c666f5b, the orchestrator's ruling under mandate 6715477401, 2026-11-12). The store joins `_restored_stores` and `_FACTORY_VOID` as voided whole, so the undo point carries it and the undo restores it like every other learner; the entry is set up again with a new coordinator, whose record loads the voided store empty. A reversal is the `("duty_switch", None)` row and its test.
