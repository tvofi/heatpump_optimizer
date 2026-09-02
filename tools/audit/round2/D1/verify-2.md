# D1 — verifier seat 2 (consequence and reachability)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D1-2` (clean, at the
baseline SHA). My harnesses are in
`/private/tmp/claude-501/audit-scratch/D1-2/`. Box: Apple M1 8-core 8 GB,
CPython 3.13.1, ten other auditors running.

**Every number below is a count, a byte-allocation count, or a repriced energy
schedule — contention-immune by the README's rule.** `load1` ran 16–88 for the
whole session, so no wall, CPU or RSS number is claimed anywhere in this report;
the one memory figure is `tracemalloc` allocation accounting, not RSS.

## Re-runs of the finder's five harnesses

All five reproduce **exactly**, every RESULT line, no tolerance consumed.

| harness | headline | `thread_factor` | `load1` |
|---|---|---|---|
| `staleness.py` | `stuck_prices_known_steps=0`, `fallback_steps=96`, `solved=1`, `update_success=1`, `savings_pct=13.4`, `switch_calls=1` | 1.000 | 29.68 |
| `executor_race.py` | `whatif_torn_fields=10`, `live_torn_fields=0`, `live_control_changed=26`, `whatif_torn_defrost_learner=9` | 251.652 (meaningless: executor threads) | 54.31 |
| `store_fuzz.py` | `total_loader_raised=152/2000`; dhw_profile 64/64, thermal_learning 9/9, dhw_draws 1/1, price_model 57/0; every `identity_failures=0` | 1.000 | 87.79 |
| `lifecycle_realloop.py` | `notready_leaked_listeners=10`, `mqtt_subs=5`, `zombie_coordinators=5`, `zombie_handler_runs=5`, guards-off arm 0/0/0; `sched_zombie_actuations=1`, `sched_zombie_saves=2`, `sched_zombie_service_calls=3`, `total_escaped_exceptions=0` | 37.313 (executor threads) | 56.81 |
| `guards.py` | 79 RESULT lines, all matching the non-findings table | 1.000 | 68.69 |

One prose slip, not a number: REPORT.md gives D1-02's three calls as
`switch.turn_on + mqtt.publish + mqtt.publish`; the harness itself prints
`sched_zombie_service_calls_detail=switch.turn_off+mqtt.publish+mqtt.publish`.
The count (3) is right; the direction in the prose is not.

---

## D1-01 — NotReady leaks listeners and the MQTT subscription per retry

**Vote: `verify` (medium).**

**Re-run.** `notready_eager` 10 / 5 / 5 / 5, lazy arm identical, guards-off null
control 0 / 0 / 0. Exact.

**My own number.** `notready_scale.py` — metric: *bytes of allocation retained
per additional coordinator constructed exactly as `async_setup_entry`
constructs it and then abandoned while its bus registrations hold it alive
(tracemalloc snapshot diff over N=20, loaders drained), together with the
listener count per setup attempt and Home Assistant's own retry cadence.*

```
RESULT listeners_per_retry=2                 (matches the finder's 10/5)
RESULT bytes_per_leaked_coordinator=33962    (33.2 KB, N=20)
RESULT alive_after_gc=20                     (all 20 unreachable-but-alive)
RESULT gc_reclaims_after_unsubscribe=1       (perturbation: to_zero)
RESULT retries_per_hour_ha=45.0
RESULT leaked_coordinators_12h=543   leaked_listeners_12h=1086   leaked_mb_12h=17.6
RESULT leaked_coordinators_24h=1083  leaked_listeners_24h=2166   leaked_mb_24h=35.1
RESULT zombie_handler_calls_per_event_12h=543
```

**Attacks.**

- *Stub artefact?* No. `FakeHass.async_add_executor_job` is not on this path at
  all — the leak is `async_track_state_change_event` registrations made in
  `__init__`, on the stub's real `state_listeners` registry
  (`tests/hastub/homeassistant/helpers/event.py` keeps and returns a real
  unsub). The `@callback`-decorated `_on_power_event` never touches the
  executor. Real HA's registry behaves the same way, and real HA does *less*
  cleanup, not more: on `ConfigEntryNotReady` it runs only
  `entry.async_on_unload` callbacks, and these three registrations are not
  registered through it. Nothing here rests on a stub property.
- *Perturbation.* `gc_reclaims_after_unsubscribe=1` — drop the registrations and
  the coordinator is collected. The number moves; the harness is not measuring a
  constant.
- *Severity by consequence — the finder under-counts by two orders of
  magnitude.* The report frames the cost as "5 retries". Home Assistant does not
  stop at five: the backoff caps at ~80 s and continues for the length of the
  outage, so a Pi that boots before its router (the finder's own stated path)
  leaks **45 coordinators per hour**. One overnight 12 h outage: **543
  coordinators, 1086 dead state-change listeners, ~17.6 MB, and 543 dead
  `_on_power_event` handlers invoked on every single meter state change** — a
  power meter reporting every 10 s means ~54 dead-handler calls per second, for
  the life of the process. This is the finding's real cost, and it is
  per-hour-of-outage, not per-retry.
- *Where my extrapolation is soft.* The 80 s cap is HA-core behaviour that
  neither the finder nor I re-read from source (the finder flags the same). It
  is the only assumption in the number. Even at a tenfold slower cadence the
  12 h outage still leaks 54 coordinators and 108 listeners — an order of
  magnitude above the reported 5.

**Decisive number.** `leaked_listeners_12h=1086` at `bytes_per_leaked_coordinator=33962`,
against a reported 10. Medium is earned and, on frequency, conservatively so:
there is no wrong actuation (the zombies hold no plan) and a restart clears it.

---

## D1-02 — Reload during a scheduled solve lets the dead coordinator actuate

**Vote: `weaken(low)`.**

**Re-run.** `sched_shutdown_returned_before_release=1`,
`sched_midsolve_zombie_actuations=1`, `sched_zombie_service_calls=3`,
`sched_midsolve_zombie_saves=2`, `sched_newest_first_cycle_ok=1`,
`escaped_exceptions=0`. Exact. The null control (reload during the *first*
solve, an entry background task) is clean: 0 / 0 / 0.

**My own number.** `price_reach.py` supplies the piece that decides severity —
what supersedes the zombie's actuation and how fast. From
`custom_components/heatpump_optimizer/__init__.py:923–936`, the new setup
schedules `coordinator.async_request_refresh()` as an entry **background task**
immediately after the platforms are forwarded, and my re-run confirms
`sched_newest_first_cycle_ok=1`. So the correcting solve is not the next
30-minute cycle: it is a background solve that starts within the same setup.

**Attacks.**

- *Stub artefact?* Partly, and in the finder's favour — but it survives. The
  window is created by `async_add_executor_job`, and `FakeHass` runs that
  inline, which would make the race impossible; `lifecycle_realloop.py` replaces
  it with a real loop and a real `ThreadPoolExecutor` and gates
  `HeatPumpOptimizer.optimize` on a `threading.Event`, so the "in-flight" point
  is deterministic rather than a stub ordering. The claim that survives a real
  event loop is the code one: nothing after the executor await in
  `async_run_optimization` or `_async_update_data` reads `_shutdown_requested`.
  That is true by inspection of `coordinator.py:4733–4760` and holds regardless
  of stub or loop.
- *Reachability.* Real, and ordinary in kind — an options save reloads the entry
  — but rare in rate. Exposure per save is (solve duration)/(1800 s); at tens of
  seconds on a Pi that is a low single-digit percent, and a household saves
  options a handful of times a year. Expected events per install per year is
  well under one.
- *Severity by consequence.* The zombie's three calls are
  `switch.turn_off + mqtt.publish + mqtt.publish` from the *pre-reload* plan,
  landing while the new instance is still doing a cold setup — so the zombie
  almost always lands first and the new instance's background solve corrects it
  within one solve duration, not one cycle. The two post-shutdown store writes
  carry at most one cycle of accounting and are overwritten by the new
  instance's own saves. No money, no actuation that outlives a solve.

**Decisive number.** `sched_midsolve_zombie_actuations=1`, corrected by a
background first solve (`sched_newest_first_cycle_ok=1`) rather than by the next
cycle, at an exposure of solve/1800 per options save. One transient
`switch.turn_off` per rare coincidence is a low, not a medium.

---

## D1-03 — Store loaders crash; "three stores are never reset so the loss repeats"

**Vote: `weaken(low)`.**

**Re-run.** `store_fuzz.py` reproduces to the mutant: `total_loader_raised=152`,
dhw_profile 64 / `repeat_on_restart=64`, thermal_learning 9 / 9, dhw_draws 1 / 1,
price_model 57 / 0, `cycle1_failed=cycle2_failed=0` in 2000/2000, every
`identity_failures=0`.

**My own number.** `store_recovery.py` — metric: *for each never-reset store,
loaded with the concrete mutant the report names, the number of production
30-minute `_async_update_data` cycles before the store's file on disk is
rewritten by the production saver, driven on a tank that cools and is drawn
from; whether a fresh coordinator on that disk still raises; and the learned
quantities lost, converted to calendar days through the production learner
constants.*

```
RESULT dhw_profile_loader_raised=1        (TypeError, the finder's none@hourly_profile/1)
RESULT dhw_profile_cycles_to_rewrite=2    RESULT dhw_profile_hours_to_rewrite=1.0
RESULT dhw_profile_still_raises_after_rewrite=0
RESULT thermal_learning_loader_raised=1   (OverflowError, inf@buffer_cooling_samples)
RESULT thermal_learning_cycles_to_rewrite=-1   (never, in 48 cycles = one full day)
RESULT thermal_learning_still_raises_after_rewrite=1
RESULT identity_loader_raised=0   RESULT identity_lost_count=0     (null control)
```

**The report's central claim does not survive.** REPORT.md: *"the corrupt file
is never rewritten, so a restart raises again — the learned state is lost for
good"*, and counts `repeat_on_restart=74`. The finder measured that over **two**
cycles on a coordinator whose `sensor.dhw` never moves, so no DHW learning event
can fire and no saver can run. Give the tank a household's temperature
trajectory and `_async_learn_dhw_cooling` fires on cycle 2 and calls
`_async_save_dhw_profile()`: the file is rewritten after **1.0 hour** of normal
operation and a fresh coordinator then loads it cleanly. The same holds for
`dhw_draws` (2 cycles). Of the 74 claimed permanent cases, **65 are one-hour
conditions**; only `thermal_learning`'s **9/200** is genuinely permanent, because
its saver is gated on `_house_heat_loss_samples % 10 == 0` and my measured
cadence is 1 house-loss sample per day.

**How much history, in days** (all from the production constants, imported not
retyped: `DHW_PROFILE_EWMA_ALPHA=0.12`, `HOUSE_LOSS_ALPHA=0.02`,
`COP_LEARNING_ALPHA=0.03`, `DHW_DAYTYPE_BLEND_K=14.0`):

```
RESULT dhw_profile_lost_quantities=_dhw_daytype_samples+_dhw_cooling_samples+_dhw_hourly_profile_peak
RESULT weekday_trust_lost=0.741   weekday_calendar_days_lost=56
RESULT weekend_trust_lost=0.611   weekend_calendar_days_lost=77
RESULT weekend_days_to_w50=49     weekend_days_to_w80=197
RESULT days_to_regain_dhw_profile_95pct=24
RESULT thermal_learning_lost_quantities=_house_heat_loss_samples+_house_heat_loss_scale+_buffer_cooling_samples+_cop_scale
RESULT days_to_regain_cop_scale_95pct=2.06
```

So a crashed `dhw_profile` load costs **8 weeks of weekday and 11 weeks of
weekend day-type history (56 and 77 calendar days)** — the day-type counter
counts *distinct days*, so that is a hard calendar bound no cadence can
shorten — plus **24 days** to re-converge the hourly shape at α=0.12. A crashed
`thermal_learning` load costs the house heat-loss scale's 210 samples and the
COP scale, permanently, with a traceback on every boot until the user deletes
the file.

**Attacks.**

- *Stub artefact?* No. The loaders are fire-and-forget `hass.async_create_task`
  coroutines; `store_fuzz.py` runs them on a real loop and my harness does too.
  The executor is not on this path.
- *Reachability — the corruption is not self-inflicted.*
  `_normalize_dhw_profile` (coordinator.py:1385) clips every element to
  `[DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY]` and falls back to the
  default pattern on a wrong length, so no production path can write the
  crashing shapes. The corruption has to arrive from outside the integration —
  SD-card damage on a Pi, a hand-edited `.storage`, or a version rollback. That
  is not a Tuesday.
- *Grid artefact / leave-one-out.* Confirmed and it matters: dropping the
  `dhw_profile` cell takes the "permanent" total from 74 to 10; dropping
  `dhw_profile` and `dhw_draws` — the two my harness shows self-heal in an
  hour — leaves 9.
- *The repo already owns the fix idiom.* The snapshot **restore** path
  (coordinator.py:8703–8715) validates `isinstance(arr, list) and len(arr) == 24`
  and wraps `int()` in `try/except (TypeError, ValueError)`; the **load** path
  for the same data does neither. That is a real inconsistency and supports the
  bug class — it does not raise the consequence.

**Decisive number.** `dhw_profile_cycles_to_rewrite=2` (1.0 h) with
`still_raises_after_rewrite=0`, which removes 65 of the 74 permanent cases the
severity was argued from. What remains is 9/2000 mutants in one store, reachable
only through external file damage, costing the heat-loss and COP scales. Low.

---

## D1-04 — A price list not covering the horizon is planned and actuated on flat 0.5

**Vote: `weaken(low)`.**

**Re-run.** Exact: `stuck_prices_known_steps=0`, `fallback_steps=96`,
`solved=1`, `update_success=1`, `switch_calls=1`, `savings_pct=13.4`,
`forecast_min_max=0.500/0.500`; `covering` arm 96 / 0 / 27.92.

### The money, with a validated zero floor

`price_cliff_money.py` — metric: *each arm's own `power_schedule +
dhw_power_schedule` repriced at the **true** published price vector (SEK over a
24 h, 96-step horizon), where the arms differ only in how much of the price list
covers the horizon.* `cover1` is the same code path one known step later — the
learned prior fills the rest — so `cover0 − cover1` is what the
`known_count == 0` short-circuit actually throws away.

| true profile | cost cover96 | cost cover1 | cost cover0 | penalty (SEK/24 h) | penalty % | kWh cover0 | min room cover0 | published savings cover0 |
|---|---|---|---|---|---|---|---|---|
| winter_typical | 50.23 | 50.23 | 103.43 | **+53.19** | **+105.9 %** | 76.35 | 19.92 | 7.53 % |
| winter_extreme | 87.44 | 87.44 | 199.87 | **+112.43** | **+128.6 %** | 76.35 | 19.92 | 7.53 % |
| shoulder | 50.86 | 50.86 | 67.24 | +16.38 | +32.2 % | 76.35 | 19.92 | 7.53 % |
| **flat (null control)** | 84.96 | 84.96 | 91.62 | +6.66 | +7.8 % | 76.35 | 19.92 | 7.53 % |

Two things fall out of that table on their own. The `cover0` columns are
**identical across all four profiles** — 76.349 kWh, 19.924 °C, 7.53 % — because
the plan never sees the prices at all; it is literally the same plan whatever
electricity costs. And the flat-price null control is **not** zero (6.66 SEK,
7.8 %): with no shape to exploit, that residue is a pure *level* artefact — the
0.5 constant underprices a 1.20 SEK/kWh day, so the plan over-buys comfort
(19.92 °C against 19.01 °C, 76.3 kWh against 70.8 kWh). Subtracting it leaves
~46.5 SEK of genuine lost price shape on winter_typical.

Because a non-zero null control would normally void the money metric, I measured
the floor separately (`price_reach.py`): with the true prices flat at *exactly*
the 0.5 fallback, `cover0` and `cover96` see identical inputs and

```
RESULT zero_floor_fallback_steps=96
RESULT zero_floor_penalty=0.0
```

The metric's floor is exactly 0.000 SEK. The 6.66 SEK at flat-1.20 is the level
effect, not noise.

### The reachability, which is where this finding loses a severity band

`price_reach.py` — metric: *which real Home Assistant entry point reaches the
flat-0.5 solve when `_prices` has stopped covering the horizon, with the **real**
`_fetch_tibber_prices` on the path.* The finder's harness monkeypatches
`_fetch_tibber_prices = _noop`, which is what produces
`stuck_prices_update_success=1`. Restore the real fetch:

```
RESULT scheduled_cycle_update_success=0     RESULT scheduled_cycle_exc=UpdateFailed
RESULT scheduled_cycle_solved=0             RESULT scheduled_cycle_switch_calls=0
RESULT scheduled_cycle_prices_retained=96   (the stale list IS retained)
RESULT button_solved=0                      RESULT button_switch_calls=0
RESULT service_known_steps=0   service_fallback_steps=96
RESULT service_solved=1        service_switch_calls=1
RESULT service_published_savings=10.03      service_published_cost=26.47
```

- The **scheduled 30-minute cycle** cannot reach it. `_fetch_tibber_prices`
  raises `UpdateFailed` (coordinator.py:5455) before `async_run_optimization` is
  ever called, so during the outage the coordinator is **red**, not green, and
  no solve runs. The finding's title — *"while the cycle stays green"* — is a
  `_noop` artefact.
- The **dashboard "Optimize Now" button** cannot reach it either:
  `async_force_optimization` goes through `async_request_refresh` →
  `_async_update_data` → the same failing fetch. `button_solved=0`.
- The **`heatpump_optimizer.run_optimization` service** can, and does.
  `__init__.py:428–433` calls `coord.async_run_optimization()` directly with no
  fetch on the path. It solves on 96 fabricated steps, actuates the switch, and
  publishes a savings figure of 10.03 % that no price data supports. This entry
  point is not named anywhere in the finding's Mechanism or Reach section.

**How a real install gets there, and for how long.** `_prices` is never cleared
on a failed fetch (`prices_retained=96`), and Tibber's list holds today plus
tomorrow once tomorrow is published (~13:00 local). So the retained list stops
covering `now` **11–24 h** into an outage that began before tomorrow was
published, or **24–35 h** into one that began after. The state then persists for
the rest of the outage. So: an internet or Tibber outage of at least ~11 hours
*and* something calling `run_optimization` during it — realistically a user
automation on a timer, since the human is looking at a red integration.

**Attacks.**

- *Stub artefact?* The mechanism is not — `extend_price_series`
  (`price_model.py:380–381`) returns `np.full(n_steps, 0.5)` at
  `known_count == 0` before the learned prior is ever consulted, and
  `_price_series` returns `None` only when `self._prices` is empty. Pure code.
  The *"stays green"* half is entirely a stub artefact, refuted above at 0.
- *Perturbation.* `covering` arm → `fallback_steps=0`, `zero_floor_penalty=0.0`.
  The number moves in both directions.
- *Null control.* Flat prices give +7.8 %, which I decomposed to a level effect
  and floored at exactly 0.000. Not a missing control.

**Decisive number.** `scheduled_cycle_update_success=0` and `button_solved=0`:
both automatic paths are closed, and the only door is an explicit service call
during a ≥11 h price outage. The money behind that door is real and large
(+105.9 % of a winter day's bill, floor validated at 0.000), which is why this is
a weaken rather than a refute. If the judge counts a timer automation calling
`run_optimization` as ordinary equipment, medium is defensible; on the evidence I
executed, low.

---

## D1-05 — The what-if shares learner containers with the loop by reference

**Vote: `verify` (low, as filed), with the magnitude cut ~5×.**

**Re-run.** Exact: `whatif_torn_fields=10`, `whatif_control_changed=10`,
`whatif_repeat_identical=1`, `whatif_scalar_torn_fields=0`,
`live_torn_fields=0` against `live_control_changed=26`,
`whatif_torn_defrost_learner=9`, `gains_profile=7`, `dhw_windows=9`,
`draw_pattern=0`.

**My own number.** `whatif_write.py`, two metrics.

*Can a user-triggered what-if corrupt live learner state?* Metric: *live mutable
containers (`_defrost`'s factors/counts/duty/duty_counts and `to_dict`,
`internal_gains_profile`, `dhw_windows`, `dhw_weekly_windows`,
`dhw_hourly_draw_pattern`, and the scalars the overrides touch) whose json
fingerprint differs before vs after `async_simulate`.*

```
RESULT whatif_live_learner_writes=0                    (target_temp override)
RESULT whatif_live_learner_writes_windows_override=0   (the dhw_windows path)
RESULT whatif_live_learner_writes_all_overrides=0      (all 12 override keys)
RESULT write_metric_control_changed=3                  (the metric has power)
```

**Zero, in every direction.** The sharing is read-only in practice, and the code
says why: `async_simulate` *reassigns* `scratch_params.dhw_windows`,
`.comfort_ceiling`, `.dhw_setpoint`, `.dhw_min_temp` on the shallow copy rather
than mutating them, and every consumer of the shared containers in
`thermal_model.py` reads — `derate.factor(...)` resolves through
`DefrostDerate._decide`, which is pure; `internal_gains_profile` is indexed;
`dhw_hourly_draw_pattern` is `list()`-copied at `thermal_model.py:680`. A card
drag cannot damage the learner.

*What does one production-shaped write actually do to the answer?* Metric:
*what-if payload fields differing when exactly the write `_settle_defrost` makes
per cycle lands mid-solve.* `_settle_defrost` (coordinator.py:9171–9177) makes
**one** call — `observe_duty` on a flagged install, otherwise `observe` — into
one bucket, once per 30-minute cycle. The finder's arm applies **240** `observe`
calls at `delivered_ratio=0.35`, clamped to `DERATE_MIN`.

```
RESULT prod_one_observe_torn_fields=2        (min_dhw_temperature, monthly_cost_delta)
RESULT prod_one_observe_cost_delta_shift=0.0
RESULT prod_one_observe_duty_torn_fields=0
RESULT n240_observe_torn_fields=8            (the finder's amplitude)
RESULT n240_observe_cost_delta_shift=1.2
RESULT whatif_repeat_identical=1             (no noise floor)
```

**Attacks.**

- *Stub artefact?* No, and this is the one finding where a real loop is
  load-bearing and the finder built it: the tear needs the what-if to be
  *inside* `async_add_executor_job` while the loop runs `_record_accuracy`.
  `FakeHass` runs the executor inline and would show 0 by construction;
  `executor_race.py` uses a real loop, a real `ThreadPoolExecutor` and a gated
  `HeatPumpOptimizer.optimize`. On a real loop the overlap is genuine — the
  what-if awaits the executor and releases the loop, so a cycle's
  `_record_accuracy` can land inside it.
- *Attribution artefact.* `prod_inplace_writer_containers=1` of
  `finder_attributed_containers=4`. Three of the four attributed arms mutate
  containers with **no production in-place writer** — `only_gains` does
  `prof[:] = [3.0]*24`, `only_draw_pattern` scales in place, `only_windows` calls
  `.clear()`; production *reassigns* all three, as REPORT.md itself concedes. So
  16 of the 25 attributed tears (gains 7 + windows 9) come from mutations
  production never performs.
- *Severity by consequence.* At the production writer and amplitude the tear is
  2 display fields, and the number the card actually shows — `cost_delta` —
  moves by **0.000**; `savings_percentage` and `simulated_cost` do not move at
  all. The flagged-install writer (`observe_duty`) tears **nothing**. Overlap
  requires a what-if solve to straddle the one moment per 30-minute cycle when
  `_record_accuracy` runs. The what-if never actuates.

**Decisive number.** `prod_one_observe_torn_fields=2` with
`prod_one_observe_cost_delta_shift=0.0`, against the reported 10 and a 1.2 shift
at 240× the production amplitude — and `whatif_live_learner_writes=0`, which
answers the corruption direction outright. The mechanism is real and the
perturbation moves, so this is not void; the filed severity of **low** is
correct and, if anything, generous.

---

## Summary

| id | vote | the number that decides it |
|---|---|---|
| D1-01 | `verify` (medium) | `leaked_listeners_12h=1086` at 33.2 KB each and 543 dead handlers per meter event — the finder's 10 is one hour's worth of a routine overnight outage |
| D1-02 | `weaken(low)` | one `switch.turn_off` per (options save × solve/1800), corrected by the new instance's background first solve, not the next cycle |
| D1-03 | `weaken(low)` | `dhw_profile_cycles_to_rewrite=2` (1.0 h), `still_raises_after_rewrite=0` — 65 of the 74 "permanent" cases self-heal within an hour; 9/2000 remain, reachable only via external file damage |
| D1-04 | `weaken(low)` | `scheduled_cycle_update_success=0`, `button_solved=0`, `service_solved=1` — both automatic paths closed; +105.9 % of a winter day's bill behind the one remaining door, floor validated at 0.000 SEK |
| D1-05 | `verify` (low) | `whatif_live_learner_writes=0` (control 3) and `prod_one_observe_torn_fields=2` with `cost_delta_shift=0.0`, against a reported 10 at 240× the production amplitude |

Nothing voided: every finding's perturbation moved its number.

## My harnesses

- `/private/tmp/claude-501/audit-scratch/D1-2/notready_scale.py` (D1-01)
- `/private/tmp/claude-501/audit-scratch/D1-2/store_recovery.py` (D1-03)
- `/private/tmp/claude-501/audit-scratch/D1-2/price_cliff_money.py` (D1-04, money)
- `/private/tmp/claude-501/audit-scratch/D1-2/price_reach.py` (D1-04, reachability + zero floor; D1-02 supersession)
- `/private/tmp/claude-501/audit-scratch/D1-2/whatif_write.py` (D1-05)

Logs sit beside each as `<name>.log`; the five finder re-runs as
`<name>.rerun.log`.

## Exposure

No `verify-*.md`, no `docs/audit-*.md`, no round-1 register, no GitHub issue,
no `gh`. Read only SEAT_COMMON.md, `briefs/verifier.md`, `briefs/D1.md`,
`README.md`, `round2/D1/REPORT.md` and the five harnesses, plus production
source in my own worktree.
