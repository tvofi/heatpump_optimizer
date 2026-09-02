# D1 — verifier seat 1 (OWN-HARNESS)

Worktree `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D1-1` at
`c398fc84eec25fc44b60d74aae05b9a2da205884` (clean; the one production edit made
for a perturbation was restored and `git status` is empty). Scratch
`/private/tmp/claude-501/audit-scratch/D1-1`. Box: Apple M1 8-core, CPython
3.13.1, numpy 2.5.2, `load1` between 28 and 87 for every run below — an
eleven-agent fan-out. **Every number in this report is a count**, so the load
is evidence rather than a caveat: nine of the finder's ten harness arms
reproduced digit-for-digit at 20× the load they were taken under.

The finder's five harnesses were copied to my scratch dir and run from my
worktree root, so that `store_fuzz.py`'s `store_fuzz_failures.json` write could
not overwrite the committed artefact.

## Re-runs of the finder's harnesses

| harness | verdict | differences |
|---|---|---|
| `staleness.py` | **exact** | only `thread_factor` 1.006→1.000, `load1` 4.10→68.14 |
| `guards.py` | **exact** | only `thread_factor`/`load1` |
| `store_fuzz.py` | **exact**, all 93 RESULT lines incl. every per-store cell | only `load1` 1.87→87.05 |
| `executor_race.py` | **exact**, all 19 RESULT lines | only `thread_factor`/`load1` |
| `lifecycle_realloop.py` | **4 lines moved** (below) | |

`lifecycle_realloop.py` diff (mine on the right):

```
midsolve_eager.sched_zombie_service_calls_detail  switch.turn_on+…  →  switch.turn_off+…
midsolve_lazy.old_post_shutdown_saves             0                 →  2
midsolve_lazy.sched_zombie_service_calls          6                 →  3
midsolve_lazy.sched_zombie_service_calls_detail   (two triples)     →  (one triple)
```

Two things follow. (a) The header's `EXPECTED … exact` is overstated: the lazy
arm is not deterministic across runs. (b) **D1-02's stated null control failed
in my run.** The report offers "the same reload during the *first* solve …
`old_post_shutdown_saves=0`" as the clean reference; in the lazy arm I measured
**2**. The headline counts (`notready_*` 10/5/5/5, guards-off 0,
`sched_midsolve_zombie_actuations=1`, `sched_midsolve_zombie_saves=2`) did
reproduce exactly in both arms.

---

## D1-01 — ConfigEntryNotReady leaks the coordinator

**Re-run.** `notready_leaked_listeners=10`, `notready_leaked_mqtt_subs=5`,
`notready_zombie_coordinators=5`, `notready_zombie_handler_runs=5`,
`notready_leaked_listeners_guards_off=0`. Identical, eager and lazy.
`load1=28.25`, `thread_factor=29.863` (meaningless for an executor harness; no
timing claimed).

**My harness.** `mine_notready_leak.py`.
**My metric, one line:** *`HeatPumpOptimizerCoordinator` instances still
gc-reachable after `gc.collect()` once N setups have raised
`ConfigEntryNotReady` and every local handle has been dropped — counted by
scanning `gc.get_objects()` for the class, not by any bookkeeping of mine.*

Real `asyncio.run` loop, a real `ThreadPoolExecutor` bound to
`async_add_executor_job`, `hass.async_create_task` really creating tasks (the
stub closes the coroutine), and `mqtt.async_subscribe` replaced by a recorder
returning a real unsubscribe callable (the stub returns `None`, so the stub
cannot express an MQTT leak at all). The real
`heatpump_optimizer:async_setup_entry` is driven; the failure comes out of
**production code** — `_fetch_tibber_prices` → `_tibber_fetch_failed` →
`UpdateFailed` → `_async_first_refresh_light` rewrap — with a token configured,
i.e. the router-down path, not a stub raise. Teardown is HA's SETUP_RETRY path
and nothing else: `entry.async_on_unload` callbacks plus cancellation of the
entry's background tasks.

| N retries | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| `v1_zombie_coordinators` | 1 | 2 | 3 | 5 | 8 |
| `v1_live_bus_listeners` | 2 | 4 | 6 | 10 | 16 |
| `v1_live_mqtt_subs` | 1 | 2 | 3 | 5 | 8 |
| `v1_live_optimizers` | 1 | 2 | 3 | 5 | 8 |
| `v1_live_stores` | 11 | 21 | 31 | 51 | 81 |
| `v1_zombie_handler_runs` (one meter event) | 1 | 2 | 3 | 5 | 8 |

`RESULT v1_slope_zombies_per_retry=1.0000 count/retry`.

**What leaks, named.** For every failed setup the holder string is identical:

```
bus:_on_power_event@sensor.house_power
 + bus:_on_defrost_event@binary_sensor.defrost
 + mqtt:ecl110/flow_temp_control/displace
```

Three strong references per retry, each a bound method of the dead
coordinator. Each zombie drags **one `HeatPumpOptimizer` and ten `Store`
instances** with it (11 → 81 across the sweep: exactly ten per coordinator).
Nothing releases them: `_unsub_peak_guard` / `_unsub_defrost` /
`_unsub_ecl110_state` are dropped only in `async_shutdown`, which is reached
only from `async_unload_entry`, which SETUP_RETRY never calls.

**Perturbation.** Guards-off arm (`peak_guard_enabled=False`, no defrost
entity, `ecl110_state_topic=""`), 5 retries:
`v1_guards_off_zombie_coordinators=0`, `v1_guards_off_live_bus_listeners=0`,
`v1_guards_off_live_mqtt_subs=0`. **The number moves to zero.**

**Attacks.**
- *Stub artefact?* No — this is the arm the stub cannot show. On `FakeHass` the
  MQTT sub is `None` and the created coroutines are closed; both had to be made
  real before the leak is even visible. Verified on a real loop.
- *Reachable through the state machine?* Yes: nothing here needs a lifecycle
  method called out of order. The registrations happen in `__init__`
  (coordinator.py 676–691), the refresh that fails is the one
  `async_setup_entry` awaits at line 408, and SETUP_RETRY is HA's own path.
- *Does the token make it unreachable?* `config_flow.py:973` has
  `vol.Required(CONF_TIBBER_TOKEN)` and validates it, so a token-less install
  is not reachable through the flow — I re-ran with a token so the failure goes
  through the network branch. Same numbers.
- *Severity by consequence.* Linear growth, bounded only by outage length;
  every dead handler runs on every meter event (`zombie_handler_runs` = N). No
  wrong money and a restart clears it. **Medium is earned, not inflated.** I
  did not take an RSS number: it would be worthless at `load1=60`.

**Vote: `verify` (medium).**
Decisive number: `v1_slope_zombies_per_retry=1.0000`, guards-off arm 0.

---

## D1-02 — Actuation after the coordinator's own shutdown

**Re-run.** `sched_shutdown_returned_before_release=1`,
`sched_midsolve_zombie_actuations=1`, `sched_zombie_service_calls=3`
(`switch.turn_off+mqtt.publish+mqtt.publish`; the finder recorded
`switch.turn_on` — the plan's direction, not the count),
`sched_midsolve_zombie_saves=2`, `sched_newest_first_cycle_ok=1`,
`sched_escaped_exceptions=0`. The stated **null control failed** in the lazy
arm: `old_post_shutdown_saves=2`, not 0.

**My harness.** `mine_midsolve.py`.
**My metric, one line:** *calls to `switch.*` / `mqtt.*` on the service
registry, and `Store.async_save` writes, issued strictly after the
coordinator's own `async_shutdown()` set `_shutdown_requested`, when a real
solve held in a real `ThreadPoolExecutor` is released after that point.*

Real loop, real pool, `HeatPumpOptimizer.optimize` gated by a
`threading.Event` (class-attribute swap in `try/finally`) so "inside the
executor" is a fact — `solve_in_executor=1` in every arm. The refresh driven is
`coord._async_update_data()`, not `async_run_optimization()` alone: the
actuation lives in `_apply_action`, which only the former reaches. Teardown
runs through the real `heatpump_optimizer:async_unload_entry`. Real HA's
`DataUpdateCoordinator.async_shutdown` sets `_shutdown_requested`; the stub
does not, so I modelled that one line and nothing else.

| arm | in executor | shutdown returned first | post-shutdown actuations | detail | saves |
|---|---|---|---|---|---|
| A `not_cancelled` (refresh survives the unload) | 1 | 1 | **3** | `switch.turn_on+mqtt.publish+mqtt.publish` | 4 |
| B `cancelled` (refresh cancelled at unload) | 1 | 1 | **0** | — | 0 |
| C `race_in_shutdown` (executor returns while `async_shutdown` awaits) | 1 | 1 | **0** | — | 0 |
| A + the proposed guard | 1 | 1 | **0** | — | 0 |

**Perturbation.** The finding's own one-liner —
`if getattr(self, "_shutdown_requested", False): return` after the executor
await in `async_run_optimization`, and the same test before `_apply_action` in
`_async_update_data` — applied to production in my worktree: **3 → 0**. Against
the repo's gate with the edit in place, `tests/entities.py` is
`ALL 538 ENTITY CHECKS PASSED`, exit 0 (the flag is absent in the suite, so the
guard is a no-op there). The file was restored afterwards. So the proposed fix
is neither algebraically the shipping code nor gate-breaking.

**Attacks.**
- *The decisive one.* Arm A and arm B are the **same production code, the same
  real loop, the same held solve**, and they differ only in who owns the
  scheduled refresh task. The count is 3 or 0 purely as a function of that one
  modelling choice. The finder's harness asserts "a scheduled refresh is a
  hass-level task … NOT an entry task" and the report's own *Not finished*
  section says the HA core semantics were "written from the core sources as
  remembered, not re-read". If HA 2024.x instead wraps the interval refresh in
  `config_entry.async_create_background_task`, the entry unload cancels it and
  the finding's consequence is 0 — which is exactly what the finder's own null
  control (the first solve, an entry background task) measures.
- *Can I settle it here?* **No.** No `homeassistant` package is installed in
  any venv on this box (`pip list`: aiohttp, numpy, scipy only), no HA source
  tree exists under the user's tree, and the audit contract puts GitHub out of
  bounds. `hacs.json` pins the floor at `2024.1.0` and nothing more. **This
  half of D1-02 is unresolvable on this box and I say so rather than voting on
  a recollection.**
- *Is there a window that survives arm B?* I built arm C to find one: release
  the executor while `async_shutdown` is still awaiting. **0.** With
  `_background_tasks` already drained, `async_shutdown` never reaches its
  `asyncio.wait`, so it returns long before a real solve does. There is no
  second path — the actuation lands if and only if the refresh task outlives
  the unload.
- *Null control.* Failed once in my re-run (`old_post_shutdown_saves=2`).

**What survives regardless of the model:** the code property. Nothing between
the executor await and `_apply_action` consults `_shutdown_requested`, and arm
A shows on a real loop what that costs if the task is not cancelled. That is a
genuine latent gap and the one-line guard closes it at no gate cost.
**What does not survive:** the claim that a user's pump is commanded after a
reload. It rests on an unverified core-semantics assumption whose more likely
reading gives 0.

**Vote: `weaken(low)`.**
Decisive number: same code, same real loop — `post_shutdown_actuations=3` when
the refresh task survives the unload, **`=0` when it is cancelled**, and 0 in
the only other window I could construct.

---

## D1-03 — Store loaders crash; three stores are never repaired

**Re-run.** All 93 RESULT lines identical, including every per-store cell:
`dhw_profile 64/64`, `thermal_learning 9/9`, `dhw_draws 1/1`,
`price_model 57/0`, `accuracy 11/0`, `ledger 3/0`, `energy_totals 7/0`,
`snapshots/legionella/manual_plan 0/0`, `total_loader_raised=152`,
`cycle1_failed=cycle2_failed=0` in 2000/2000, `identity_failures=0` ×10.
`load1=87.05` and it did not move a single count.

**My harness.** `mine_store_fuzz.py` — my own 12-operator grammar
(`type_swap, nonfinite, huge, negate, drop_key, truncate_list, extend_list,
rewrap, key_rename, top_replace, str_number, deep_nest`), my own seed (991 per
store name), 200 mutants per store, and — the part my seat was asked for —
**setup survival measured by driving the real
`heatpump_optimizer:async_setup_entry`** on a real loop rather than by running
two cycles on a hand-built coordinator.

**My metric, one line:** *of 200 own-grammar mutants of that store's payload,
how many make the store's real loader coroutine end with an unhandled
exception during a real `async_setup_entry`; how many of those 200 still leave
`async_setup_entry` returning True; and how many raise the same exception again
on a second fresh `async_setup_entry` over the bytes left on disk.*

| store | loader raised /200 | setup ok /200 | raises again at once | exception kinds |
|---|---|---|---|---|
| snapshots | **0** | 200 | 0 | — |
| dhw_profile | **74** | 200 | 74 | TypeError 56, UFuncTypeError 15, AttributeError 3 |
| dhw_legionella | **0** | 200 | 0 | — |
| dhw_draws | **0** | 200 | 0 | — |
| thermal_learning | **6** | 200 | 6 | AttributeError 4, KeyError 1, OverflowError 1 |
| price_model | **81** | 200 | 81 | TypeError 77, ValueError 3, AttributeError 1 |
| ledger | **7** | 200 | 7 | AttributeError 4, OverflowError 2, TypeError 1 |
| accuracy | **7** | 200 | 7 | AttributeError 3, OverflowError 3, TypeError 1 |
| energy_totals | **5** | 200 | 5 | TypeError 5 |
| manual_plan | **0** | 200 | 0 | — |
| **total** | **180 / 2000** | **2000 / 2000** | 180 | |

An independently written grammar lands on the same phenomenon at
**180/2000 vs the finder's 152/2000** (+18 %), with the same shape: the two
heavy stores are `dhw_profile` and `price_model`, and the three stores that
validate their payload (`snapshots`, `manual_plan`, `dhw_legionella`) are 0/200
in both. The exception families match (`TypeError` from `np.clip` over a
`None`/string leaf, `OverflowError` from `int(float("inf"))`, `AttributeError`
from `.get` on a list).

**Per store, what the loader does, and does setup survive.** The loaders guard
`store.async_load()` and then trust the shape, so the failure is always *after*
the read: `_normalize_dhw_profile` clips whatever the 24-element list holds;
`_async_load_thermal_learning` catches `(TypeError, ValueError)` but not
`OverflowError`/`KeyError`/`AttributeError`; `PriceShapeModel.from_dict` runs
`float(v)` unguarded. In every one of my 2000 trials **the loader task dies
alone and `async_setup_entry` returns True** — the install comes up, the
entities appear, only the learned state is gone. That is the honest ceiling on
this finding's severity and it holds at 2000/2000.

**Where I differ from the finder, and why it is not a contradiction.** My
`repeats` column is 180 (all of them) against the finder's 74. The metrics ask
different questions: mine restarts *immediately*, before any update cycle; the
finder's restarts *after two cycles*, which is what lets `price_model`,
`ledger`, `accuracy` and `energy_totals` rewrite themselves. Both are right.
Read together they say: at the instant of boot every corrupt load raises; four
of the ten stores heal themselves one cycle later (default 30 minutes,
at the cost of the history they held) and three never do. The finder's "three
stores are never repaired" is the correct framing and my re-run reproduced its
`repeat_on_restart` cells exactly.

**Perturbation / null control.** `v1_<store>_identity_raised=0` for all ten
stores (the unmodified healthy payload), and `manual_plan`/`snapshots` at 0/200
are the in-harness reference for what a validating loader looks like.

**Attacks.**
- *Grid artefact?* Leave-one-out over my ten cells: range 0–81; dropping the
  most favourable cell (`price_model`, 81) leaves **99/1800**, still an order
  of magnitude above the three validating stores. The finding does not rest on
  one cell.
- *Contention?* Counts; `load1` 87 vs the finder's 1.87 changed nothing.
- *Reach.* Narrower than the mutant space suggests: HA's `Store` writes
  atomically, so byte-level SD corruption fails at the JSON parse, which *is*
  guarded. What reaches these crashes is structurally-valid JSON with wrong
  types — a bad migration, a hand-edited `.storage` file, or a saver that ever
  emits a non-finite value. That narrows the entry points but does not touch
  the defect: once such a file exists, three stores keep it forever.
- *Severity.* No wrong money, the cycle never fails (`cycle1_failed=0` in
  2000/2000, re-run), setup survives 2000/2000, and the workaround is deleting
  one file. **Medium, not higher.**

**Vote: `verify` (medium).**
Decisive number: `v1_total_loader_raised=180/2000` with
`setup_ok=2000/2000` and `identity_raised=0` in every store, from my own
grammar and seed.

---

## D1-04 — A stale price list is planned and actuated on a flat 0.5

**Re-run.** `stuck_prices_known_steps=0`, `stuck_prices_fallback_steps=96`,
`stuck_prices_solved=1`, `stuck_prices_update_success=1`,
`stuck_prices_switch_calls=1`, `stuck_prices_savings_pct=13.4`. Exact.

**My harness.** `mine_price_and_whatif.py`.
**My metric, one line:** *horizon steps whose planning price is exactly
`extend_price_series`'s `fallback` constant, read out of the array the wrapped
production function actually returned during one real `_async_update_data`,
reported next to whether that cycle raised and how many `switch.*`/`mqtt.*`
calls it issued.* I instrument by wrapping
`heatpump_optimizer.price_model:extend_price_series` at the coordinator's
import site and recording `(known_count, n_steps, fallback, prices)` — not by
inspecting the payload, so the number cannot come from the bounds shape.

| | `covering` (list starts 6 h ago) | `stale48h` (list ended 3 days ago) |
|---|---|---|
| `known_steps` | 96 | **0** |
| `horizon_steps` | 96 | 96 |
| `fallback_steps` (price == 0.5 exactly) | **0** | **96** |
| `cycle_raised` | — | — |
| `update_success` | 1 | **1** |
| `actuations` | 3 | **3** |
| detail | `switch.turn_on+mqtt.publish+mqtt.publish` | `switch.turn_off+mqtt.publish+mqtt.publish` |
| published `savings_percentage` | 43.56 | **3.61** |

Every one of 96 steps is the invented constant, the cycle returns normally, the
integration stays green, the switch is commanded and two MQTT commands go out,
and a savings percentage computed against a fabricated price is published.

**Perturbation.** The `covering` arm is the finding's stated config
perturbation: `fallback_steps` **96 → 0**. The number moves.

**Attacks.**
- *Measuring a constant?* No. The same wrapper on the same code gives 0 and 96
  in the two arms, and `known_steps` moves 96 → 0 with it.
- *Is `_price_series`'s guard doing anything?* It returns `None` only for an
  empty `self._prices`. `extend_price_series` line 380 —
  `if known_count == 0: return np.full(n_steps, fallback)` — is reached with a
  non-empty but non-covering list, and note that it **discards the learned
  `PriceShapeModel` entirely**: even an install with weeks of learned diurnal
  shape gets a flat 0.5, not its own prior. The `_price_series` docstring says
  inventing a flat curve "used to let the optimizer run and report a savings
  figure that no price data supported"; that is precisely what I measured.
- *Reach.* Needs a *successful* fetch with stale content, or a clock far from
  the list. A failing fetch is handled honestly (`UpdateFailed`, red) — I
  confirmed that path exists at `_tibber_fetch_failed` while working on D1-01.
  The clock arm is not exotic on a Pi without an RTC: it boots with a stale
  clock and NTP has not synced yet.
- *Severity.* One or a few cycles of planning and actuating on a fabricated
  price, with a fabricated savings figure shown to the user, self-correcting
  once data covers. The published-wrong-value half argues for high; the
  narrow reach and self-correction argue for medium. **Medium.**

**Vote: `verify` (medium).**
Decisive number: `v1_stale48h_fallback_steps=96/96` with
`update_success=1` and 3 actuations, against `v1_covering_fallback_steps=0`.

---

## D1-05 — The what-if shares learner containers with the loop

**Re-run.** `whatif_torn_fields=10`, `whatif_torn_defrost_learner=9`,
`whatif_torn_gains_profile=7`, `whatif_torn_dhw_windows=9`,
`whatif_scalar_torn_fields=0`, `whatif_exceptions=0`, and the null control
`live_torn_fields=0` against `live_control_changed=26`. All 19 lines exact.

**My harness.** `mine_price_and_whatif.py`, second half.
**My metric, one line:** *fields of `ThermalParameters` for which
`async_simulate`'s `scratch_params = replace(self._thermal_params)` holds the
**same object** (`is`) as the live params, restricted to non-scalars — the
mechanism itself, measured by identity rather than by its downstream effect.*

`RESULT v1_whatif_shared_mutable_fields=3`
`RESULT v1_whatif_shared_names=dhw_windows,defrost_derate,dhw_hourly_draw_pattern`

On a bare `ThermalParameters()` the shared set is `dhw_windows,
dhw_hourly_draw_pattern` (73 fields; `defrost_derate` and
`internal_gains_profile` are `None` until learned, so they only join the set
once they hold an object — `internal_gains_profile` is `None` on my config,
which is why it is absent from my three and present in the finder's). The
mechanism is exactly as claimed: a shallow `replace()` hands the executor
thread the live learner objects.

**My tear number is 0, and I report it against the finding.** With the solve
gated inside a real `ThreadPoolExecutor` and 81 in-place
`defrost.observe(-3.0, 85.0, 0.35)` calls landing before it was released, none
of the what-if payload's 15 keys changed (`v1_whatif_shared_torn_fields=0`;
the payload has `simulated_cost`/`baseline_cost`, not `predicted_cost`). My
forecast is a flat −3 °C constant ("No weather forecast available — using
current conditions"), so the derate table has nothing to vary against. That is
a scenario in which the shared object does not matter, not a refutation of the
finder's 9 — whose harness ran a varied forecast and which I re-ran exactly.

**Perturbation.** The finder's stated one (`copy.deepcopy` in
`async_simulate`) is run in-harness as the live-solve control:
`_solve_snapshot` already deep-copies, and its `live_torn_fields=0` against
`live_control_changed=26` is the to-zero arm on the same mutation set. My own
deepcopy arm was mis-placed (it copied the params before the simulate rather
than at the seam inside it) and I discount it rather than report it as a
control.

**Attacks.**
- *Real-HA reach.* The only in-place production writer is
  `_defrost.observe`/`observe_duty` in `_record_accuracy`, once per cycle; the
  what-if never actuates; the answer is a card tooltip. My own 0-tear arm is
  further evidence that even when the write lands the effect is often nil.
- *Severity.* **Low is right and I would not raise it.**

**Vote: `verify` (low).**
Decisive number: `v1_whatif_shared_mutable_fields=3`
(`dhw_windows, defrost_derate, dhw_hourly_draw_pattern` shared by identity),
with the finder's `whatif_torn_fields=10` / `live_torn_fields=0` reproduced
exactly.

---

## Voided

None. Every finding's number moved under its stated perturbation:
D1-01 5→0 (guards off), D1-02 3→0 (the guard line, and 3→0 again on task
ownership), D1-03 180→0 (identity mutant; 0/200 on the validating stores),
D1-04 96→0 (covering list), D1-05 10→0 (the deep-copying live solve).

## Harnesses I wrote

`/private/tmp/claude-501/audit-scratch/D1-1/mine_notready_leak.py`,
`mine_midsolve.py`, `mine_store_fuzz.py`, `mine_price_and_whatif.py`.
All four use `asyncio.run` with a real `concurrent.futures.ThreadPoolExecutor`
bound to `hass.async_add_executor_job`, a `hass.async_create_task` that really
creates tasks, and — where MQTT matters — a subscribe that returns a real
unsubscribe callable. None of the four numbers above can be taken on
`tests/harness.py:FakeHass` as shipped.

## What I could not settle

Which object owns `DataUpdateCoordinator`'s scheduled interval refresh in the
HA versions this integration supports (`hacs.json`: ≥ 2024.1.0). No
`homeassistant` package is installed on this box and the audit contract puts
GitHub out of bounds. It is the single fact that decides whether D1-02's
consequence is 3 or 0, which is why my vote there is a weaken and not a verify
or a refute.
