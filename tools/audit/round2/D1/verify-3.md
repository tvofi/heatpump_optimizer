# D1 round-2 — verifier seat 3 (perturbation, determinism and scope)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D1-3`, scratch
`/private/tmp/claude-501/audit-scratch/D1-3`. Box: Apple M1 8-core 8 GB,
CPython 3.13.1, the shared `.venv`. **Every number below is a count or a
fraction; no timing number is claimed as evidence.** `load1` ran 16–93
through the session (eleven agents on the box); it is recorded per run and is
irrelevant to counts. `thread_factor` is meaningless for the executor
harnesses (their CPU is on worker threads) and 1.000–1.006 for the rest.

The full-gate lock `/tmp/hpo-gate.lock` was held by another agent from 16:07
for the entire session, so **no full `tests/run.sh` was run** and I did not
`rmdir` a lock I did not create. In its place every proposed fix was measured
against the gate's four behaviour scripts (`features.py`, `entities.py`,
`validate.py`, `edge.py`); the table is at the end.

---

## 0. Re-runs of the five harnesses, exactly as their headers say

All five were copied into the worktree at `tools/audit/round2/D1/` and run
from the worktree root with the header's command and thread pins.

| harness | result | load1 |
|---|---|---|
| `lifecycle_realloop.py` | every RESULT reproduced; two deviations noted below | 30.22 |
| `staleness.py` | **byte-identical** to `staleness.out` bar `load1`/`thread_factor` | 51.83 |
| `executor_race.py` | **byte-identical** to `executor_race.out` bar `load1`/`thread_factor` | 55.48 |
| `guards.py` | **byte-identical** to `guards.out` bar `load1`/`thread_factor` | 54.00 |
| `store_fuzz.py` | **byte-identical** to `store_fuzz.out` bar `load1` | 78.20 |

Two deviations in `lifecycle_realloop.py`, both cosmetic, both recorded
because REPORT.md asserts otherwise. Over **7 runs** of the harness:

* `sched_zombie_service_calls_detail` reads
  `switch.turn_off+mqtt.publish+mqtt.publish` in 7/7; REPORT.md says
  `switch.turn_on`. The count (3) is what the finding rests on and it
  reproduced.
* REPORT.md says "Both eager and lazy task start are run; the numbers are
  identical." They are not here: the lazy arm's `sched_zombie_service_calls`
  was 3, 3, 6, 6, 6, 3, 3 across 7 runs while the eager arm was 3 in 7/7.
  `sched_zombie_actuations=1` and `sched_zombie_saves=2` were identical in
  **7/7** for both arms, so the headline numbers are stable; a judge
  re-taking the service-call count should expect 3 **or** 6.

---

## D1-01 — ConfigEntryNotReady leaks the coordinator's listeners and MQTT subscription per retry

**Re-run.** `notready_leaked_listeners=10`, `notready_leaked_mqtt_subs=5`,
`notready_zombie_coordinators=5`, `notready_zombie_handler_runs=5`,
`notready_leaked_listeners_guards_off=0`, `total_escaped_exceptions=0`;
exact, eager and lazy, and identical in 7/7 repeats. `load1=30.22`.

**My own number.** `my_d103`-independent harness `my_d101.py`.
*Metric: after K setups of the real `heatpump_optimizer.async_setup_entry`
that each raise ConfigEntryNotReady, plus one that succeeds, the number of
coordinator instances from the failed setups still alive after
`gc.collect()`, and the bus registrations and MQTT subscriptions bound to one
of them.* It shares no code with the finder's harness: it drives the real
`async_setup_entry` directly and models only three real-HA facts —
`async_config_entry_first_refresh` runs `_async_update_data` and raises;
NotReady runs `async_on_unload` and cancels entry tasks but never calls
`async_unload_entry`; `hass.async_create_task` really schedules — plus a
recording `mqtt.async_subscribe`, which the hastub throws away.

> `zombie_coordinators=5, leaked_listeners=10, leaked_mqtt_subs=5,
> zombie_handler_runs=5, live_listeners=2`

Identical to the finder's, from a different harness.

**Source confirmation.** `coordinator.py:676–691` spawns the three
registrations from `__init__`, before `__init__.py:411` awaits the first
refresh. `_async_first_refresh_light` (4476–4491) does call
`_fetch_tibber_prices`, and `_tibber_fetch_failed` (5443–5455) raises
`UpdateFailed`, so the NotReady path is reachable exactly as claimed.

**Perturbation.** Stated: the guards-off config → to_zero. Observed **0** in
both harnesses. The number moves; nothing here is computed from constants.

**Scope — 5 configurations, my harness, 5 retries each.**

| configuration | zombies | listeners | mqtt subs | handler runs |
|---|---|---|---|---|
| peak guard on + defrost entity + default MQTT topic | 5 | 10 | 5 | 5 |
| **stock install** — peak guard off *by default* (`DEFAULT_PEAK_GUARD_ENABLED = False`), no defrost entity, default ECL110 topic, MQTT reachable | **5** | 0 | **5** | 0 |
| guards off **and** `ecl110_state_topic=""` (the finding's null control) | 0 | 0 | 0 | 0 |
| no DHW (`dhw_tank_volume=0`) | 5 | 10 | 5 | 5 |
| two-zone | 5 | 10 | 5 | 5 |

Holds in **4 of 5**; the one it fails is the finding's own null control.
Tibber unreachable at boot is the trigger, not a scope variable. The stock
row is the one worth reading twice: with both guards at their defaults the
coordinator still leaks — through the MQTT subscription — *provided the MQTT
integration is present*. Without MQTT, `mqtt.async_subscribe` raises, the
bare `except` at `coordinator.py:1280` swallows it, and a stock install
leaks nothing.

**The proposed fix, applied as a real source edit and measured.** I took the
third of the finding's three alternatives, in `__init__.py`:
`try: await coordinator.async_config_entry_first_refresh()` /
`except: await coordinator.async_shutdown(); raise`.

| harness / arm | before | after |
|---|---|---|
| my harness (base and stock_mqtt) | 5/10/5/5 | **0/0/0/0**, `live_listeners` still 2, setup ok |
| finder's harness, **eager** start | 10/5/5/5 | **0/0/0/0** |
| finder's harness, **lazy** start | 10/5/5/5 | **10/5/5/5 — unchanged** |

That last row is a defect in the proposed fix, not in the finding. Under
lazy task start the `_spawn`ed registration coroutines have not run when the
first refresh fails, so `async_shutdown` finds `_unsub_peak_guard`,
`_unsub_defrost` and `_unsub_ecl110_state` all `None` and unsubscribes
nothing; the tasks then run and register on a coordinator that is already
dead. Lazy start is HA 2024.1–2024.2 and **`hacs.json` declares
`"homeassistant": "2024.1.0"`** — the repo's own declared support floor. The
other two alternatives the finding lists (register through
`entry.async_on_unload`, or register only after the first refresh succeeds)
do not have this hole. **A fixer must not take the `async_shutdown` form.**

**Attacks run.** Contention: counts only, immune. Wrong gate mode: not a
suite-gap claim. Grid artefact: no grid. Null control: present and 0 in both
harnesses. Real-HA reachability: the point of my harness — the registrations
run from `hass.async_create_task` (a hass-level task in real HA) and HA does
not call `async_unload_entry` after a NotReady setup. Severity by
consequence: every dead coordinator's `_on_power_event` runs on **every**
meter event for the life of the process (5 dead handlers fired for a single
synthetic event, measured), and an outage at ~80 s backoff accumulates tens
of them, each holding a thermal model and its arrays on an 8 GB Pi. Medium
is earned.

**Vote: `verify` (medium).** Decisive: an independent harness sharing no
code with the finder's gives `zombie_coordinators=5 / leaked_listeners=10 /
leaked_mqtt_subs=5` after 5 NotReady retries, and 0/0/0 under the stated
perturbation.

---

## D1-02 — reload during a scheduled solve lets the torn-down coordinator actuate

My seat was told to settle this one, because `FakeHass.async_add_executor_job`
runs inline and a synchronous stub can manufacture exactly this shape.

**Is it a stub artefact? No.** `lifecycle_realloop.py:369/398` builds a real
`ThreadPoolExecutor(max_workers=4)` and awaits `loop.run_in_executor` on a
real loop; `FakeHass.async_add_executor_job` is overridden, never used. I
then reproduced it in a harness of my own that does the same, independently.

**Re-run.** `sched_midsolve_zombie_actuations=1`,
`sched_midsolve_zombie_saves=2`, `sched_zombie_service_calls=3`,
`sched_shutdown_returned_before_release=1`, `sched_newest_first_cycle_ok=1`,
`sched_escaped_exceptions=0`, and the two null controls
(`old_post_shutdown_actuations=0`, `old_post_shutdown_saves=0`,
`old_instance_alive_after_gc=0`). Exact; 1 and 2 in 7/7 repeats.

**My own number.** `my_d102.py`. *Metric: the number of `switch.*`/`mqtt.*`
service calls and `Store.async_save` writes that happen strictly after
`await coordinator.async_shutdown()` returned, in a trial where a scheduled
`_async_update_data()` was in flight when the shutdown was issued; a trial
"hits" when that number is > 0.* Real loop, real `ThreadPoolExecutor(4)`,
`_shutdown_requested` set by a modelled base-class shutdown (HA core 2024.x)
and nothing else modelled. **The solve is never blocked, gated or slowed:
there is no harness sleep inside `optimize`.** The window is the solve's own
natural duration.

### Determinism — the question my seat was set. 20 trials per arm.

| arm — how the shutdown is timed | trials | hits | hit rate | after shutdown, per trial |
|---|---|---|---|---|
| `entered` — shut down the instant `optimize` is *observed* in the executor (nothing injected; the solve then runs its own duration) | 20 | 20 | **1.000** | 3 calls + 1 save |
| `d1ms` — 1 ms after the refresh task is created; **no synchronisation with the solve thread at all** | 20 | 20 | **1.000** | 3 + 1 |
| `d50ms` — same, blind, 50 ms | 20 | 20 | **1.000** | 3 + 1 |
| `d500ms` — same, blind, 500 ms | 20 | 20 | **1.000** | 3 + 1 |
| `between` — no refresh in flight (null control) | 20 | 0 | **0.000** | 0 |

`calls_after_per_trial` is the literal vector `[3]×20` in each hitting arm,
not an average over a lucky cell. Escaped exceptions 0 everywhere.

**This is not a race that fires once in twenty, and it is not a harness that
fires only because it inserted a sleep.** It is a deterministic window whose
width is the whole solve. The three blind fixed-delay arms are decisive:
they never touch the solve thread and still hit 60/60.

The window's width does not matter either. Forcing `horizon_hours` to 6 h
versus 36 h moves the median real solve from **0.043 s to 1.961 s** — a 45×
spread — and the hit rate is 1.000 in both. A 43-millisecond solve is
already long enough.

### Scope — 10 trials each, `entered` arm

| configuration | hits/trials |
|---|---|
| base (DHW on, single zone) | 20/20 |
| no DHW (`dhw_tank_volume=0`) | 10/10 |
| two-zone | 10/10 |
| ECL110 / MQTT enabled | 10/10 |
| fast solve (6 h horizon, median 0.043 s) | 10/10 |
| slow solve (36 h horizon, median 1.961 s) | 10/10 |
| **Tibber unreachable** (`_fetch_tibber_prices` raises `UpdateFailed`) | **0/10** |
| reload **between** solves instead of during one | 0/20 |

Holds in **7 of 8**, 90/90 trials across them. The Tibber-down row is not a
counterexample to the mechanism: the cycle raises before it reaches the
solve, so there is nothing in the executor for the shutdown to overtake. A
reachable fetch is a precondition of the window, not something the finding
got wrong.

**Real-HA semantics, checked against the source.**

* Production contains **zero** references to `_shutdown_requested` (`grep`
  over `coordinator.py` and `__init__.py`): nothing after the executor await
  guards against a shutdown. That is the whole mechanism.
* `async_unload_entry` (`__init__.py:980`) awaits
  `coordinator.async_shutdown()`; the override (`coordinator.py:4989–5025`)
  awaits only `self._background_tasks`, and a scheduled refresh is not one.
* `super().__init__` (`coordinator.py:651–660`) passes **no `config_entry=`**,
  so no HA version can attach the scheduled refresh to the entry: it is a
  hass-level task on every version, and entry unload cancels only entry
  tasks. The finder's modelled semantics are right, and right for newer HA
  too.

**The proposed fix, applied as a real source edit and measured.**
`if getattr(self, "_shutdown_requested", False): return` after the executor
await in `async_run_optimization`, and `... return self.data` before
`await self._apply_action()` in `_async_update_data` — 5 added lines.

| measurement | before | after |
|---|---|---|
| my harness, `entered`, 20 trials | 20/20 hits, 60 calls, 20 saves | **0/20 hits, 0 calls, 0 saves** |
| finder's `sched_zombie_actuations` | 1 | **0** |
| finder's `sched_zombie_saves` | 2 | **0** |
| finder's `sched_zombie_service_calls` | 3 | **0** |
| finder's `sched_newest_first_cycle_ok` | 1 | 1 (unbroken) |
| finder's D1-01 numbers | 10/5/5/5 | 10/5/5/5 (the two findings are independent) |

Not algebraically the shipping code. **Gate exposure: none by
construction.** `_shutdown_requested` is set only by real HA's
`DataUpdateCoordinator.async_shutdown`; neither production nor
`tests/hastub/homeassistant/helpers/update_coordinator.py` ever sets it, so
under the suite `getattr(..., False)` is always `False` and both new branches
are dead code. Measured anyway — see the gate table.

**Attacks run.** Contention: counts. Wrong gate mode: not a suite-gap claim.
Grid artefact: none; per-trial vectors, not aggregates. Null controls: two,
both 0 (reload between solves; reload during the *first* solve, an entry
background task HA cancels). Stub reachability: the decisive attack,
answered with a real thread pool and blind timing. Severity: one actuation
from the pre-reload configuration lands during the new instance's setup and
the old instance's saves race the new one's loads; the new first cycle
supersedes within one cycle. Bounded — medium, as filed.

**Vote: `verify` (medium).** Decisive: **60/60 hits across the three blind
fixed-delay arms** of my own real-loop, real-thread-pool harness with no
sleep inside the solve, against **0/20** in the between-solves null control.

---

## D1-03 — store loaders crash on corrupt payloads; three stores never reset

**Re-run.** Byte-identical to `store_fuzz.out`: `total_loader_raised=152`,
`repeat_on_restart` 64 (dhw_profile) + 9 (thermal_learning) + 1 (dhw_draws)
= 74, `cycle1_failed = cycle2_failed = 0` in 2000/2000,
`identity_failures=0` × 10. `load1=78.20`.

**My own number.** `my_d103.py`. *Metric: for each store, the number of
hand-written corruptions whose loader task ends with an unhandled exception
when the coordinator is constructed on a real loop, and the subset that
raises again on a fresh coordinator built on the disk left behind — with no
update cycle in between, so this measures the loader alone.* The mutation
set is **exhaustive and seedless**: two whole-document shapes (`[doc]`,
`"corrupt"`) plus five damage shapes (`null`, `str`, `inf`, `nan`,
`[value]`) applied to **every** top-level key of each store's own healthy
payload — 220 mutants. No RNG, so no seed can be cherry-picked.

> `total_raised=16/220`, `total_repeat=16`, `identity_raised=0`

| store | raised | repeat | kinds |
|---|---|---|---|
| thermal_learning | 6/117 | 6 | `inf@buffer_cooling_samples`, `inf@cop_samples`, `inf@house_heat_loss_samples`, `inf@lower_floor_loss_samples` → OverflowError; `top_str`, `top_wrapped_list` → AttributeError |
| dhw_profile, price_model, ledger, accuracy, energy_totals | 2/12 each | 2 each | `top_str`, `top_wrapped_list` → AttributeError |
| snapshots, dhw_legionella, dhw_draws, manual_plan | 0 | 0 | — |

My sweep is shallower than the finder's (top-level keys only; its 64
dhw_profile failures come from mutations *inside* the 24-element hourly
list, e.g. `none@hourly_profile/1`), so my rate is lower — but it agrees on
every mechanism and lands on the same exception kinds at the same sites.
Where we differ is instructive: **my `repeat` equals my `raised` for every
store**, including `price_model`/`ledger`/`accuracy`/`energy_totals`, because
I run no cycles between the two loads. The finder's `repeat_on_restart`
column is therefore the *conservative* one — it credits the cycle for
rewriting those four — and its claim that only three stores are permanently
lost is the weaker, and correct, statement.

**Source confirmation of the two specific mechanisms.**
`_async_load_thermal_learning` (1843–1880) guards each block with
`except (TypeError, ValueError)`; `int(float("inf"))` raises `OverflowError`,
which escapes *after* `_apply_buffer_cooling_rate` has already run — exactly
the "half-applied" claim, and exactly what `inf@buffer_cooling_samples`
reproduces. `_async_load_dhw_profile` (1409–1415) checks
`isinstance(profile, list) and len(profile) == 24` and then hands the
elements to `np.clip` unchecked.

**Perturbation.** Stated: wrap each loader body after `async_load()` in
`try/except Exception` that logs one WARNING and saves `{}`. Applied to all
ten loaders: `total_raised` **16 → 0**, `total_repeat` **16 → 0**,
`identity_raised` still 0. The number moves.

**Scope.** DHW disabled (`dhw_tank_volume=0`, `dhw_enabled=False`, no DHW
entity): `total_raised=16/220`, `total_repeat=16` — **identical**. The DHW
loaders run regardless of the DHW config, so the finding holds in 2/2 DHW
configurations. Zone count and Tibber reachability do not touch the load
path: it runs at construction, before any fetch.

**Attacks run.** Contention: counts. Null control: present and passing in
both harnesses. Grid artefact: the finder reports leave-one-out (drop the
biggest cell → 88/1800); my exhaustive sweep is an independent
re-aggregation and it agrees. Reachability: the loaders run at `__init__`
through `hass.async_create_task`, which really schedules in HA; the
exception is logged once by the loop handler and nothing is quarantined —
confirmed by `repeat_on_restart`. One honest reach caveat the report does
not state: a `.storage` file damaged by an SD-card fault usually fails
**JSON parsing**, and that path *is* guarded (`try/except` around
`async_load`). Every failure here is structurally-wrong-but-valid JSON —
a version skew, a downgrade, or a hand edit. That narrows the trigger; it
does not change the number, and the permanence (`repeat_on_restart`) is what
earns the severity.

**Vote: `verify` (medium).** Decisive: a seedless exhaustive sweep gives
16/220 loader crashes with 16/16 repeating on the next load, and **0/220**
under the finding's own proposed guard.

---

## D1-04 — a stale price list is planned and actuated on a flat 0.5 while the cycle stays green

**Re-run.** Byte-identical to `staleness.out`: `stuck_prices_known_steps=0`,
`stuck_prices_fallback_steps=96`, `stuck_prices_solved=1`,
`stuck_prices_update_success=1`, `stuck_prices_switch_calls=1`,
`stuck_prices_savings_pct=13.4`, against the `covering` arm's
96 / 0 / 1 / 1 / 1 / 27.92. `load1=51.83`.

**My own number.** `my_d104.py`. *Metric: with the published price list's
last entry starting N hours before `now`, the fraction of horizon steps
whose planning price is not backed by a published entry
(`price_known == False`), together with whether the cycle solved, actuated
`switch.*`, and published a `savings_percentage`.* I count the **mask**, not
`price == 0.5`, for the reason under Scope.

| list ends | unknown steps | at fallback 0.5 | price span | solved | actuated | published savings |
|---|---|---|---|---|---|---|
| 24 h in the future | 0/96 | 0 | 0.600–1.058 | 1 | 1 | 30.18 % |
| 1 h in the future | 88/96 | 0 | 1.017–1.058 | 1 | 1 | 15.61 % |
| at `now` | 92/96 | 0 | 1.058 | 1 | 1 | 15.68 % |
| **1 h ago** | **96/96** | **96** | **0.500** | 1 | 1 | **13.40 %** |
| 6 / 12 / 24 / 48 h ago | 96/96 | 96 | 0.500 | 1 | 1 | 13.40 % |

The cliff is sharp and it is **one hour**, not "a clock more than a day off"
as the report's Reach paragraph says. The moment no entry covers *any* step,
`extend_price_series`'s `known_count == 0` branch replaces the learned prior
with a bare constant. Partial coverage (88 or 92 unknown steps) is the
normal, documented, prior-filled path and is untouched.

**Source confirmation.** `_price_series` (5711–5765) returns `None` only for
`if not self._prices`, while its own docstring says inventing a flat curve
"used to let the optimizer run and report a savings figure that no price
data supported, so the caller skips the run instead".
`price_model.py:380–381` is `if known_count == 0: return np.full(n_steps,
fallback)`. The stated intent and the guard do not line up.

**Perturbation.** Stated: shift the list to cover `now` → `fallback_steps`
to_zero. Observed **0** (my −24 h row; the finder's `covering` arm). The
number moves.

**Scope — 4 configurations.** Holds in **4 of 4** (base, no DHW, two-zone,
DSO grid fee): each reaches 96/96 unknown steps, solves and actuates. But
the grid-fee row breaks the **finder's metric**: with
`grid_fee_mode="rules", grid_fee_fixed=0.35` the fee is added *after* the
fallback, so every step prices at 0.850 and `stuck_prices_fallback_steps`
(which counts `price == 0.5`) reads **0** while the finding fully holds. A
judge re-taking the finder's number on a grid-fee install would be told the
finding is gone. My mask-based metric is not fooled. That is a metric
fragility, not a refutation — but the metric should be restated in terms of
`price_known` before it enters the register.

**The disclosure claim, measured — and this is what moves my vote.** The
report says "The only disclosure is `price_known_steps=0` in the payload and
the per-slot `price_known` flags; no sensor or the card reads
`price_known_steps`." Literally true, materially misleading. The card reads
the **per-slot** flag: `heatpump-optimizer-card.js:3594`
(`estimatedPricesFrom()`) feeds `:4243`, which shades the estimated stretch
and prints `plan.estimated_prices`. I rendered the shipped card through
`tests/card_rig.mjs` on a real `plan_view.py` payload (`my_d104_card.mjs`;
*metric: `class="estimated"` rects and label hits in the card's markup, with
every slot's `price_known` set true, then false*):

| arm | `class="estimated"` rects | label hits | rect geometry |
|---|---|---|---|
| every slot `price_known: true` | 0 | 0 | none |
| every slot `price_known: false` — the D1-04 condition | **2** | 5 | `x=92 width=700` — the **entire** plot width |

So on the card the user sees the whole horizon shaded and labelled
"estimated prices". The fabricated flat price is not silent. What remains
undisclosed is the `savings_percentage` (13.40 %), which carries no such
mark, and the actuation, which happens either way.

**The proposed fix, applied and measured.** `if not known: return None`
after `_known_prices_for` in `_price_series`: `solved` 1 → **0**,
`switch_calls` 1 → **0**, `savings_pct` 13.40 → **None**, while the cycle
still completes (`update_ok=1`) and the partial-coverage rows (88 and 92
unknown) are untouched. Not algebraically the shipping code, and it passes
all four gate scripts (see the table).

**Attacks run.** Contention: counts and published scalars. Null control: the
`covering` arm, 0. Grid artefact: my eight-offset sweep is a re-aggregation
that locates the cliff more precisely than the finder's two arms.
Reachability: this needs a fetch that **succeeds** and returns content
covering nothing — a failed fetch raises `UpdateFailed`
(`_tibber_fetch_failed`, 5443–5455) and goes red, honestly. The real path is
a badly wrong local clock (a Pi with no RTC before NTP sync) or a
stale-but-200 API. Severity by consequence: the plan degenerates to
comfort-only control — no worse, and no more expensive, than an unoptimised
thermostat — it recovers automatically on the next covering fetch, and the
card marks the whole horizon estimated. The one genuine harm is a published
savings number with no price data behind it.

**Vote: `weaken(low)`.** The finding reproduces and its fix works, so it is
not refuted; medium is not earned once the card's disclosure is measured.
Decisive: `disclosure_visible_when_all_unknown=1` with a full-plot-width
`class="estimated"` rect (`x=92 width=700`) against
`disclosure_visible_when_all_known=0`.

---

## D1-05 — the what-if solve shares learner containers with the loop by reference

**Re-run.** Byte-identical to `executor_race.out`: `whatif_torn_fields=10`,
`whatif_torn_defrost_learner=9`, `whatif_torn_gains_profile=7`,
`whatif_torn_dhw_windows=9`, `whatif_torn_draw_pattern=0`,
`whatif_scalar_torn_fields=0`, `whatif_control_changed=10`,
`live_torn_fields=0` with `live_control_changed=26`,
`whatif_repeat_identical=1`, `live_repeat_identical=1`. `load1=55.48`.

**My own number.** `my_d105.py`, two metrics.
*Structural: mutable fields of the thermal parameter object for which
`replace(params)` — what `async_simulate` uses — yields the identical object
the live coordinator holds.*
*Behavioural: whether one in-place write on one of those containers,
performed on the event loop while the what-if solve is inside a real
`ThreadPoolExecutor`, changes the what-if payload.*

> `shared_containers=3` — `dhw_windows`, `defrost_derate`,
> `dhw_hourly_draw_pattern` — against **0** under `copy.deepcopy` on a fresh
> coordinator. (After a cycle, `deepcopy` "shares" two internal caches,
> `_layout_cache` and `_buffer_ua_cache`; neither is a learner container.)

A single in-place `del windows[1:]` on the shared `dhw_windows` list
mid-solve gives `torn_answer=1`, `torn_fields=7` (`compressor_starts`,
`cost_delta`, `dhw_slots`, `min_dhw_temperature`, `min_room_temperature`,
`monthly_cost_delta`, `simulated_cost`).

**Determinism.** Nothing to report: `whatif_repeat_identical=1` and
`live_repeat_identical=1` in the finder's harness, both reproduced, and my
own runs were repeatable. This is structural aliasing, not a timing race —
a write at any point during the solve exposes it.

**Scope.** `shared_under_replace=3` and `shared_under_deepcopy=0` in **3 of
3** configurations (base, no DHW, two-zone) — the same three containers each
time. `whatif_scalar_torn_fields=0` (scalars are copied by `replace`) and
`live_torn_fields=0` over 26 loop-side writers (`_solve_snapshot`
deep-copies), so the finding is correctly confined to the what-if path.

**Perturbation.** Stated: `copy.deepcopy(self._thermal_params)` in
`async_simulate`. Applied as a real source edit:
`whatif_torn_fields` **10 → 0**, `whatif_torn_defrost_learner` 9 → 0,
`whatif_torn_gains_profile` 7 → 0, `whatif_torn_dhw_windows` 9 → 0, with
`whatif_control_changed` still **10** (the comparison keeps its power) and
every `live_*` number untouched. My own `torn_answer` **1 → 0**. Not
algebraically the shipping code; passes all four gate scripts.

**Reach, checked at the source — and the finder is right.** Every production
write to `dhw_windows`, `internal_gains_profile` and
`dhw_hourly_draw_pattern` is a *reassignment* (`coordinator.py:1412, 4306,
4652, 4949, 8697`), which cannot reach a `replace()` copy taken earlier. The
only in-place writer of a shared object is `self._defrost.observe` /
`observe_duty` (9171, 9177) in `_record_accuracy`, and
`_thermal_params.defrost_derate` *is* `self._defrost` (1129, 7248, 8746). So
the real trigger is one EWMA step at a cycle's tail landing inside a
card-driven what-if solve — rare, and the what-if never actuates.

Said plainly so the judge does not over-read my number: **my own mutation
(`dhw_windows` in place) is not something production does.** It proves the
aliasing is load-bearing, not that production exercises it.

**Vote: `verify` (low).** Severity low is right, for the reach reason above.
Decisive: `shared_containers=3` under `replace()` versus 0 under
`copy.deepcopy`, and `torn_answer` 1 → 0 when the deepcopy is applied.

---

## Gate exposure of the proposed fixes

The full-gate lock was held all session, so this is the gate's four
behaviour scripts, not `tests/run.sh`. `entities.py` is the one the toolkit
README singles out as the trap several round-2 proposals fall into; all four
fixes clear it.

| arm | features.py | entities.py | validate.py | edge.py |
|---|---|---|---|---|
| baseline | rc=0 (101 s) | rc=0 (7 s) | rc=0 (42 s) | rc=0 (49 s) |
| D1-05 fix — `copy.deepcopy` in `async_simulate` | rc=0 (70 s) | rc=0 (7 s) | rc=0 (31 s) | rc=0 (47 s) |
| D1-04 fix — `if not known: return None` in `_price_series` | rc=0 (88 s) | rc=0 (8 s) | rc=0 (32 s) | rc=0 (49 s) |
| D1-01 fix — shutdown on NotReady in `async_setup_entry` | rc=0 (77 s) | rc=0 (11 s) | rc=0 (44 s) | rc=0 (39 s) |
| D1-02 fix — `_shutdown_requested` guard after the executor await | rc=0 (74 s) | rc=0 (5 s) | rc=0 (27 s) | rc=0 (47 s) |

**Every proposed fix I could apply as a source edit clears all four,
including `entities.py`.** Each was reverted with `git checkout` immediately
after its arm; the worktree ends with no production change
(`git status --porcelain` → only the untracked `tools/audit/` copy).

D1-02's fix is byte-inert to the suite by construction: nothing in
production or in `tests/hastub` ever sets `_shutdown_requested`, so both new
branches are unreachable under the gate. D1-01's fix in the form I applied
is likewise inert under the stub (`async_config_entry_first_refresh` never
raises there) — its problem is the lazy-start hole measured above, not the
gate. D1-03's fix is a ten-loader change I measured only in my own harness.

## Harnesses I wrote

All in `/private/tmp/claude-501/audit-scratch/D1-3/`: `my_d101.py`,
`my_d102.py`, `my_d103.py`, `my_d104.py`, `my_d104_card.mjs`, `my_d105.py`,
with their logs (`d102_determinism.log`, `d102_scope.log`, `d103_own*.log`,
`d104_scope.log`, `lifecycle_repeat.log`, `gate_*.log`) and the three fix
patches (`d101_fix.patch`, `d102_fix.patch`, `d105_fix.patch`). Every fix
was reverted with `git checkout`; the worktree carries no production change,
only the untracked copy of the finder's harnesses under `tools/audit/`.

## Votes

| finding | vote | the number that decides it |
|---|---|---|
| D1-01 | `verify` (medium) | independent harness: 5 zombie coordinators / 10 leaked listeners / 5 leaked MQTT subs after 5 NotReady retries; 0/0/0 under the stated perturbation |
| D1-02 | `verify` (medium) | 60/60 hits across three **blind** fixed-delay arms on a real loop and real thread pool with no sleep inside the solve, against 0/20 between solves |
| D1-03 | `verify` (medium) | seedless exhaustive sweep: 16/220 loader crashes, 16/16 repeating on the next load, 0/220 under the proposed guard |
| D1-04 | `weaken(low)` | the shipped card renders a full-plot-width `class="estimated"` rect (`x=92 width=700`) whenever every slot is `price_known:false`, and none when they are known |
| D1-05 | `verify` (low) | `replace()` shares 3 mutable learner containers that `deepcopy` shares 0 of, in 3/3 configurations; `torn_answer` 1 → 0 under the deepcopy fix |

**Nothing voided.** Every finding's stated perturbation moved its number in
the stated direction, so no harness in this dimension is computing a
constant.

Two things a fixer must carry forward regardless of the votes:

1. **D1-01's `async_shutdown` fix is incomplete** on HA 2024.1–2024.2, which
   `hacs.json` declares as supported. Measured: 10/5/5/5 unchanged on the
   lazy-start arm. Use `entry.async_on_unload`, or register after the first
   refresh.
2. **D1-04's metric must be restated** as `price_known == False` steps rather
   than `price == 0.5`, or a grid-fee install reports the finding as absent.
