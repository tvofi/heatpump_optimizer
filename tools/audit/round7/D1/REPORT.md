# D1 - Robustness and stability, round 7

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave merged), export at
`/Users/timmalmstrom/audit-r7-baseline`. Machine: 8-core Apple M1, 8 GB, darwin 25.6.0,
Python 3.11.5, numpy 2.4.6. Everything below was run from the export root with
`PYTHONPATH=tests/hastub`.

`exposure`: none. I read no `docs/`, no GitHub, and no earlier round's findings; the only
earlier-round text I met was code comments citing `D1-nn` / `R5-D1-nn` ids, which
`COMMON.md` calls context, not a to-do.

## What the round found

Two guard-seam findings, both with an executed count that moves under a one-line
production edit. The dimension is otherwise **dry**: the three sweeps the brief mandates
(lifecycle, store corruption fuzzing, external parser inputs) all returned zero, with the
numbers recorded under Non-findings.

---

## D1-01 - the what-if rate limiter is skipped on every failing return

**Severity**: medium. **Stop-rule class**: bug.

`HeatPumpOptimizerCoordinator.async_simulate` sets `self._last_simulation = now` only on
the **success** return (coordinator.py:10751). Every other return - `{"error": str(err)}`
after the shadow solve raises (coordinator.py:10700), `{"error": "invalid_windows: ..."}`,
`{"error": wood_err}` - leaves the limiter slot empty, so the next call re-enters the full
solve. The docstring's contract is explicit: *"it is **rate-limited**, because a full solve
is seconds of CPU and dragging a slider would otherwise trigger one per pixel."* That
protection is absent on exactly the path where the solve is *also* failing.

The reachable case is not exotic: the #783 worker-fallback latch (`WORKER_FALLBACK_CAP`)
makes `_await_optimize` raise `UpdateFailed` on every solve once the process worker has
failed four times running - an install whose child interpreter cannot start. From that
moment each `heatpump_optimizer.simulate_plan` call from the dashboard card (one per slider
drag event) launches a fresh multi-second solve, in the process whose worker is already
unusable, instead of one per `SIMULATE_MIN_INTERVAL_SECONDS`.

`_maybe_run_fuse_advisor` and `_maybe_refresh_price_tile` borrow the same seam and are
**not** affected: both snapshot and restore `(_last_simulation, _simulation_cache)` around
the call and read `rate_limited`, so the defect is confined to the user-facing entry point.

**Harness**: `tools/audit/round7/D1/guards.py`, arm (a).
**Instrumented symbol**: `heatpump_optimizer.coordinator:_await_process`.
**Metric**: the number of shadow-solve submissions made across 5 consecutive
`async_simulate` calls, with the clock frozen and the rate-limit slot left alone.
**Perturbation** (one-line production edit, verified both ways): insert
`self._last_simulation = now` immediately before `return {"error": str(err), ...}` at
coordinator.py:10700 - the count falls 5 -> 1, and reverting restores 5.

## D1-02 - the stale-plan actuation gate covers the switch path but not the pump path

**Severity**: low. **Stop-rule class**: hygiene.

`_plan_is_stale` is the rule that stops the integration actuating a plan whose horizon has
slid out from under it: *"Stop actuating, exactly as when no plan exists: the pump's own
weather-compensated curve holds comfort until a solve succeeds."* It is consulted in
`_apply_action` (coordinator.py:6560) and nowhere else among the write paths that follow
each cycle. `_async_drive_pumps` (coordinator.py:2590) runs in the same tick, one call
later, with no staleness test: it derives `idx` from `now - result.timestamps[0]` and
clamps it inside `pump_schedule.plan_commands_heat`, so an expired plan is read at its
**last** step and the circulation pumps keep being commanded from a horizon that no longer
exists, while the plan is simultaneously declared unfit to actuate.

The failure direction is the safe one - `curve_driven` is read from the same expired
`_current_action`, which holds `heat_pump_on: True`, so `space_pump_should_run` returns
True on the "heat curve is being driven" rail and the pump runs rather than stops. That is
why this is `low`: the inconsistency is real and countable, the user-visible consequence on
this baseline is nil. It matters because the gate's authority is what the next write path
will be judged against.

**Harness**: `tools/audit/round7/D1/guards.py`, arm (b).
**Instrumented symbols**: `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._apply_action`,
`._async_drive_pumps`, `._plan_is_stale`.
**Metric**: of the actuating write paths driven with `_plan_is_stale()` True, how many still
call a `hass.services.async_call` / `_async_set_pump`.
**Perturbation** (one-line production edit, verified both ways): insert
`if self._mode in (MODE_AUTO, MODE_ECONOMY) and self._plan_is_stale(): return` at the top of
`_async_drive_pumps` - `stale_paths_detail` goes `{'space_pump': 2}` -> `{}` and
`actuating_paths_still_writing_when_stale` goes 1 -> 0.

---

## Non-findings - checked, and held

Each carries the command that showed it and the number it produced.

### Lifecycle: unload mid-solve leaks nothing

`tools/audit/round7/D1/_explore_lifecycle.py` subclasses `tests/harness.py:FakeHass` so
`async_add_executor_job` runs on a real `ThreadPoolExecutor` over a real asyncio loop and
`async_create_task` schedules instead of closing. It drives a light first refresh, then a
**full** cycle whose solve it interrupts by hooking `coordinator:_await_process`, then
`async_shutdown` mid-solve, then waits for the orphaned refresh task and counts what
survives.

    mid_solve=False -> escaped=None          live_tasks=1 holding_coord=0 saves_after_shutdown={} state_listeners=0 bg=0
    mid_solve=True  -> escaped=CancelledError live_tasks=1 holding_coord=0 saves_after_shutdown={} state_listeners=0 bg=0

`holding_coord=0` - no live task holds the torn-down coordinator; `saves_after_shutdown={}`
- no store is written after `async_shutdown` returns; `state_listeners=0` - the
peak-guard/defrost subscriptions are gone; `_background_tasks` is empty. The
`_entry_released` latch in `_async_update_data` and `async_run_optimization` holds.

### Store corruption: 0 escapes out of every real loader seam

`tools/audit/round7/D1/store_types.py` captures one healthy payload per store from the
production save seams (12 stores), then drives a seeded mutant per node of each payload -
type swaps to `{}`, `[]`, `"x"`, `0`, `-1`, `1e308`, `None`, `True`, `False`, `"NaN"`,
`"Infinity"`, plus whole-payload swaps - through the **real** loader, counting exceptions
that escape the loader seam.

    stores_driven=12  stores_missing=0
    RESULT raising_pairs=0 count
    RESULT mutant_pairs=626 count

This is the type-corruption half the round-6 finiteness work (`QuarantiningStore`,
`tests/finite_boundary.py`) does not claim: `_sanitize` scrubs non-finite leaves only, so
structural corruption is the loaders' own responsibility, and every one of them survives
it. `manual_plan` and `accuracy` reset explicitly; the rest fall through to the loader's own
absent-data default. (The `--mutants` default of 240 is clipped to the node count on the
three smallest stores, hence 22/53/49 there.)

### Every reader key has an age limit except the one documented as unbounded

AST-enumerated every `CONF_*` key passed to a real `InputReader` read (`read`, `read_state`,
`read_bool`, `read_power_kw`) across the package: 29 call sites, 27 distinct keys.
`const.INPUT_MAX_AGE_MINUTES` covers all but `CONF_DHW_DISINFECTION_SWITCH_ENTITY`, and that
one is read `max_age_minutes=UNBOUNDED` on purpose (const.py:833,
`disinfection.py:observe`). Zero keys are missing from the table by oversight - the trap
`const.py:1376` names ("A key missing from this table gets no age limit at all, which
silently disables the staleness watchdog for it") is empty.

### The existing D1-shaped checks are green at this baseline

    PYTHONPATH=tests/hastub python3 tests/finite_boundary.py    -> ALL 25 PASSED
                                                                  (loader_escape_total=0,
                                                                   model_poison_total=0,
                                                                   published_poison_total=0)
    PYTHONPATH=tests/hastub python3 tests/guard_pins.py         -> ALL 6 PASSED
    HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 tests/dst_checks.py -> ALL 51 PASSED
    PYTHONPATH=tests/hastub python3 tests/features.py           -> 1 of 3099 FAILED
                                                                   (process exit 0)

`tests/dst_checks.py` run **without** `HASTUB_TZ` reports 1 of 51 failed ("dt_util carries
the configured zone"). That is the file's own precondition check firing, not a defect: the
module docstring says it is run by `tests/features.py` in a subprocess with
`HASTUB_TZ=Europe/Stockholm` set.

`tests/features.py`'s single failure is
"and the path that proceeds still stamps a resolvable recorded_at (#363)
[recorded_at = 'unknown']". **Named as a harness gap of my export, not a baseline defect**:
`tests/structure.py:1194 recorded_at_sha()` returns the literal `"unknown"` (structure.py:1191)
when `git merge-base HEAD <origin/main|main>` cannot run, and this export has no `.git`. The
check asserts a 40-character SHA, so it cannot pass here in principle. A seat with a real
worktree (D3/D11) should confirm it is green there; I did not, and I am not claiming it.

### Disproved leads

- `_maybe_run_fuse_advisor` and `_maybe_refresh_price_tile` both borrow `async_simulate`'s
  cache; I expected cache poisoning between them and the card. They snapshot and restore
  `(_last_simulation, _simulation_cache)` in a `finally`, the fuse advisor additionally
  checks its own cap echoed back (`echoed != cap_kw`), the tile checks `rate_limited`, and
  the card renders `whatif.rate_limited` (`www/heatpump-optimizer-card.js:9041`). No seam.
- `async_simulate` not checking `_optimization_running`: both solve paths serialise on the
  module-global `_PROCESS_LOCK` inside `_run_in_process`, so concurrent entry costs wall
  clock, never torn state.
- `_command_valve_target` and `_command_frequency` are only reached from the tail of a
  *successful* `async_run_optimization`, and `_apply_action`'s early return is what
  suppresses the publish path - so the D1-02 class does not extend to them in a way a user
  can see.
- `pump_schedule.plan_commands_heat` bounds `idx` to `n-1`, so an expired plan cannot raise
  IndexError through `_async_drive_pumps`.

## What I could not finish

- The reload half of the lifecycle sequence (setup -> refresh -> **reload** mid-solve ->
  setup again, through `__init__._take_fresh_handover` / `_republish_handover_ages`). The
  unload half is measured; the reload half needs `ha_setup_entry`/`ha_unload_entry` driven
  twice against a real loop and I ran out of the round's budget. Every step of it reads as
  guarded, but that is an argument, not a number.
- `_detect_outage`'s response to a `last_tick` written by a clock that ran **backwards** is
  a fail-open by construction; I did not build the harness to show whether anything
  downstream depends on it.

## Harnesses

- `tools/audit/round7/D1/guards.py` - both findings. Header carries the metric, the command,
  the expected values and the perturbations.
- `tools/audit/round7/D1/store_types.py` - the 12-store type-corruption sweep.
- `tools/audit/round7/D1/_explore_lifecycle.py` - the real-loop lifecycle probe
  (exploratory; the finding-bearing instruments are the two above).
- `tools/audit/round7/D1/_explore_cycle.py` - the real-loop single-cycle probe used to
  establish that a full solve runs under the stub (1.3 s, status `optimal`).
