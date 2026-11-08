# Design: R10-ADVISOR-WHATIF — the steady-start what-if estimator (#2257)

Base: 2a3c05644d85b7ee5c2c314fde5aca950e4aba91 (origin/main; no predecessor, `After: none`); every line below is cited at it.
Round 3: answers the one revise point of the round-2 verdict on b50afa686 (§1 held start, §1 buffer, §5 checks and mutant) and folds its five
fixer carries into §5. Round 1's points (one step-0 target, no feedback, fallback streak), the seam, sibling sites, consistency and cost are kept.
Toolchain: `tools/audit/seat/cloud-setup.sh --check` OK at the base. `brief_lint.mjs` (note wrapped as one roster group): clean but for the
two new helper names this note proposes (`_reference_held_start(...)`, `_stash_initial_buffer(state)`), absent from the tree by design.

## 0. Measured (round 1, base c3a279e32)
`r10_advisor_residue.py whatif`: `rows 24 plan_moves_by_start 24 held_moves_by_start 0`; caps `plan 18/36 settled 1/36` reading a saving
(the brief's 19/36 and 3/36 were a stale venv). Spike (never merges; rebuilt as a harness arm, §5), each plan solved from a held start at its own
schedule's step-0 target:

| figure | moves by start | degree sign wrong | cap rows saving (< -1) |
|---|---|---|---|
| steady, plan spend only | 0/24 | 3/12 | 30/36 |
| **steady, settled** (spend + each side's `deferred_energy_cost`) | **0/24** (spread 0.00) | **0/12** | **0/36** |
| held (control) | 0/24 | 0/12 | n/a |

The spike ran on fixtures with no throttling valve, so the round-3 tank rule (§1) does not change those rows; the fixer's arm re-measures at the base.

## 1. Owning seam
`HeatPumpOptimizerCoordinator.async_simulate` (`tests/seam_map.json`: `core`; coordinator.py:11239-11466) owns the change. It calls:
- `optimizer.py`: `SolveInputs` (optimizer.py:2351-2359, frozen, kw_only) gains `held_start: bool = False`; `optimize` (def 3551) resolves it.
  **One helper, two callers (revise point 1).** A new method `_reference_held_start(self, state, weather, comfort_targets)`, returning a `ThermalState`,
  returns `_sharing_wood_side(_thermostat_held_state(self.model, state, weather, _baseline_target(comfort_targets, 0, self.config.target_temp)), state)`,
  the expression `_start_gap_cost` builds inline today (optimizer.py:5634-5637). `_start_gap_cost` (5614-5645) calls the helper in place of
  those lines; `optimize`'s held_start branch calls it to rebind `initial_state`, right after `_build_comfort_bounds` returns `comfort_targets`
  (3683-3688) and before the `_solve` closure puts `initial_state` into `_Horizon` (3724-3728). The weather is a `WeatherSeries` over the
  truncated arrays (`weather_or_calm` 3602-3604, truncation 3613-3618). No caller derives a target; one expression, so the two cannot drift.
  **The tanks, behind a throttling valve.** `_thermostat_held_state` (558-602) holds the zones and slab at the target and, when
  `mixing_valve.is_throttling`, sets `buffer_tank_temperature = valve_hold_temperature(...)` if the held need is positive (594-597) and,
  on a two-tank layout, `wood_tank_temperature = _NO_WOOD_TANK_C` (0.0, 536-537; 598-601). `_sharing_wood_side` (540-542) puts the
  measured wood side back. So the steady plan starts with **the buffer held** (valve hold, or as measured when the need is 0) and **the wood
  tank as measured**: the stored wood heat "wood on both" relies on is kept. Held is what keeps the start gap zero: re-applying the helper to
  its own output returns it unchanged (zones and slab come from target and weather step 0; the valve hold reads the held zones through
  `_valve_draw_circuits`, thermal_model.py:1900-1922; the wood side comes back from the rebound state, which is the measured one). §5 checks
  this on a valve-plus-two-tank fixture rather than trusting the argument.
  **`_initial_buffer_temp`.** `_stash_price_horizon` (3619-3621, def 3955-3998) writes it from the measured buffer (3977-3982), before the
  comfort bounds exist; its only read floors the buffer settlement cap (`_settlement_caps`, 5314-5319). Chosen: **re-stash from the rebound
  state.** The six-line write is extracted to `_stash_initial_buffer(state)`, called by `_stash_price_horizon` and again by the held_start
  branch after the rebind, so the cap is floored from the start the solve uses. Building the comfort bounds before the stash lost: it reorders
  the price stash and the bounds on every solve, held or not, to serve one flag (§4). `_compute_baseline_power` (5474, its call 5532) keeps its
  own bare `_thermostat_held_state`; it already re-holds whatever `initial_state` it gets. Default False: byte-identical.
- `price_tiles.py`: `monthly_deltas` (94-109) gains `steady: tuple[live, sim] | None`, adding `monthly_steady_cost_delta` (per_month of sim
  spend + sim deferred + wood - live spend - live deferred). Pure.
One owner: the optimizer gains an input flag over a quantity it already owns. No second owner.

## 2. Shape
`async_simulate(overrides, *, limited=True, base=None, steady=False)`. With `steady=True`, after the measured shadow solve (11350-11407)
returns, it runs the live configuration and the scratch one, each with `SolveInputs(held_start=True)`: same horizon, `solve_at`, mode block;
quiet windows without the overrides on the live side, with them on the scratch side; mold floor at each side's `target_temp`; wood on both.
Inputs come from one extracted `_simulate_inputs(state, config, caps, quiet, wood_kw, held_start)`, called three times (pays the line growth).

**Which optimizer.** `SolveRecord.optimizer()` returns a fresh `HeatPumpOptimizer` per call (coordinator.py:2386-2387). The live steady solve runs on a **fresh scratch** `HeatPumpOptimizer(ThermalModel(copy.deepcopy(params)),
copy.deepcopy(config))` from async_simulate's own `config, params, state` (11289-11294: `_solve_hubs`, 6240-6304, or `base.*`), copied before any
override; never through `SolveRecord.optimizer`, nor `_warm_seeded` (coordinator.py:2344-2364), which seeds the optimizer it is given with the live plan. Its result and the steady cache only feed the payload: never assigned to
`_optimization_result` (one writer, 6496), never a warm seed, never a `SolveRecord`.
**Fallback streak.** One what-if makes one `_await_optimize` call (2299-2341; bump 2330, clear 2339). The steady pair runs through
`_await_off_loop` (2132-2154; executor on `ProcessWorkerUnavailable`, streak untouched) only after the shadow solve returned; past #783's cap
that solve raises `UpdateFailed`, caught at 11408-11410 into an error answer, so no steady solve runs. #783 is unchanged; no `decision: orchestrator` owed.
`_await_off_loop` re-raises `ProcessWorkerTimeout` with no executor rerun (2147-2149): the steady pair's own `except` catches it (and any
`Exception`) and drops the steady key (no money line), never the answer.

Payload: no what-if TypedDict exists; none is added. `monthly_cost_delta` keeps its meaning; `monthly_steady_cost_delta` is present only on a
`steady=True` answer whose two steady solves succeeded.

| caller | steady | figure it reads, after | reason |
|---|---|---|---|
| card (`services.handle_simulate_plan`, services.py:767) | True | `monthly_steady_cost_delta` | the owner's ruling |
| cap tile (`_maybe_refresh_price_tile`, call coordinator.py:10777) | `"power_cap_kw" in overrides` | `price_tiles.monthly_figure` (140-143) -> steady key | measured-start settled still saves 1/36 |
| degree tiles (same call) | False | `monthly_held_cost_delta`, unchanged | spread 0.00, sign right; +2 solves buys nothing |
| fuse advisor (`async_simulate` call coordinator.py:9048; reads at 9080) | True | steady key, read **directly** at 9080 | it bypasses `monthly_figure` |
| debugger `_solver_smoke` (debugger.py:323) | False | `cost_delta`, unchanged | it times one solve |

Card: the what-if `summary()` (heatpump-optimizer-card.js, around 9295-9309) reads `result.monthly_steady_cost_delta`; absent, no money line.
en/sv `whatif.cheaper_per_month` / `dearer_per_month` / `same_cost` say "steady-state monthly estimate". `docs/dashboard-card.md`'s "Try in
what-if" sentence: the panel prices the plan from a house already held at each schedule, settled, so a change's one-off coast or heat-up is excluded.
Invariants kept: `limited=False` neither reads nor writes the limiter or card cache; the slot is spent when the first solve starts (#1448);
overrides reach only scratch copies (#240); an error answer carries no figure.

## 3. Cost (Raspberry-Pi-class)
Round 1, this box: shadow solve mean 623 ms; steady pair mean 1201 ms, max 1838 ms. Card what-if 1 solve -> 3. Bound: at most 3 solves per
user what-if, one start per `SIMULATE_MIN_INTERVAL_SECONDS`. The live steady solve is cached on (the plan object, `solve_at`): the entry holds
the object `self._optimization_result` refers to **when read inside async_simulate** (main stores a copy, `replace(result, solve_band=...)`,
6496, so a solve's own return value never matches) and hits only on `is`; background callers key on `base`. Cap tile +2 solves every third
interval, fuse +2/week. The fixer re-measures solve count (wrapping both `_await_optimize` and `_await_off_loop`) and wall per what-if, before/after.

## 4. Alternatives (lost)
- **Steady, unsettled**: 3/12 degree signs wrong, 30/36 cap rows save.
- **Panel reads the held figure**: prices a thermostat, and is 0 for every cap, fuse and hot-water what-if.
- **Steady-solve the live plan every interval**: doubles every cycle's solves with no what-if asked.
- **Held start rebuilt in `optimize` beside `_start_gap_cost`'s copy**: two expressions of one reference; round 2 drifted exactly so.
- **Bounds before the stash**: moves an ordering every solve depends on to serve one flag; the re-stash touches only the held_start path.
- **Disclosure only**: ruled out by the owner, 2026-11-01.

## 5. Evidence plan
- Sibling sites: `grep -rn "async_simulate(" custom_components/` (four callers, §2) and `grep -rn "monthly_cost_delta\|monthly_settled_cost_delta"
  custom_components/ tests/` (card summary, cap tile, fuse at 9080; `PriceTile`'s key, price_tiles.py:188, is another payload and stays).
- Failing test first (`tests/features.py`): `monthly_steady_cost_delta` from `async_simulate(..., steady=True)` spreads 0 over the harness's three
  starts; red at the base (key absent; `monthly_cost_delta` moves 24/24). Sign test: degree -1 < 0 < +1, cap >= -1; `tests/card.mjs`: no steady key, no money.
- Start-settlement-zero check (`tests/features.py`): `held_start=True` solve, `_start_gap_cost` wrapped to record its return, reads 0 (1e-9) at
  three starts, incl. a weekday-override config; **and on a throttling-valve, two-tank fixture** (from `_grad_parity(True, wood=True,
  valve="manual")`, features.py:6814, with `model.params.two_tank_modelled` and `buffer_is_store` **asserted True as a precondition**; set
  `topology_layout_override` or a two-zone wood probe if the fixture does not reach it): the gap reads 0, the solve's start
  `wood_tank_temperature` equals the measured state's, its buffer equals `valve_hold_temperature`'s, and `_initial_buffer_temp` equals that buffer.
- No-feedback check: after a `steady=True` what-if, `coord._optimization_result` is the same object with an unchanged `power_schedule`; wrap
  `_await_off_loop`, capture each optimizer it receives, and assert it `is not` any instance `SolveRecord.optimizer()` or `_warm_seeded`
  returned in that test (a "no new write on the record's optimizer" assertion is vacuous: each call is fresh); with `_await_process` raising
  `ProcessWorkerUnavailable`, one what-if bumps the streak by exactly 1; with it raising `ProcessWorkerTimeout` on the steady pair only, the
  answer carries `monthly_cost_delta` and no steady key.
- Tile and fuse: one rotation of `_maybe_refresh_price_tile` passes `steady=True` only on the cap spec (count steady solves: 2 on the cap
  rotation, 0 on degree ones); the fuse advisor's `cost_delta_sek_month` equals the answer's steady key.
- Finder harness: `dev/audit/harnesses/r10_advisor_residue.py` gains a `steady` column in `arm_whatif`, solving with `SolveInputs(held_start=True)`
  and reading `price_tiles.monthly_deltas` (no re-implemented formula); verdict: steady spread 0, 0 cap saves.
- Null control: held spread 0.00 on every row; null series reads one steady figure at all starts; empty panel renders nothing; the valve-two-tank
  fixture's precondition assert is its own null (a fixture with no wood tank passes the wood check vacuously, so it must fail the precondition).
- Mutants: live side from the measured state (spread moves); drop `deferred_energy_cost` from the steady key (cap saves 30/36); card falls back to
  `monthly_cost_delta`; `+ 0.5` on the helper's `_baseline_target` (start-zero red); **drop `_sharing_wood_side` from `_reference_held_start(...)`'s
  rebind** (valve-two-tank check red: wood reads 0.0); **skip the re-stash** (`_initial_buffer_temp` check red where valve hold != measured);
  live steady side on `_warm_seeded(self, record.optimizer())` (identity check red); steady pair through `_await_optimize` (streak reads 3);
  `steady=True` on every tile spec (degree rotation counts 2); fuse reading `monthly_settled_cost_delta` (fuse check red).
- Goldens: the cap tile's and fuse figures move; `GOLDEN_MODE=drift`, claim per `claim-files.md` only what moves.

## 6. Hot files, position, carries
Hot: `coordinator.py`, `optimizer.py`, `price_tiles.py`, `services.py`, `www/heatpump-optimizer-card.js`, `docs/dashboard-card.md`,
`tests/features.py`, `tests/card.mjs`. After: none; serial position free. P141 is on main (86e9f8d53, `plan_slots.py`).

## Notes for the fixer
Carry: R10-ADVISOR-WHATIF (item 2257)
Carry: dismissed: landed on main at 86e9f8d53, verify ancestry only (item P141)
Carry: R10-ADVISOR-WHATIF (item 2257-cache-key) - never key the steady cache on `id(...)`; hold the object and compare with `is` (§3).
Carry: R10-ADVISOR-WHATIF (item 2257-cache-copy) - key on the object `self._optimization_result` holds when read inside async_simulate, never on a solve's return value: 6496 stores a `replace(...)` copy (§3).
Carry: R10-ADVISOR-WHATIF (item 2257-record-optimizer) - `SolveRecord.optimizer()` returns a fresh `HeatPumpOptimizer` per call (coordinator.py:2386-2387); assert identity on the instance passed to `_await_off_loop` (§5).
Carry: R10-ADVISOR-WHATIF (item 2257-fuse-key) - the fuse advisor reads its key directly (coordinator.py:9080); re-point that line, changing `monthly_figure` alone does not move it (§2, §5).
Carry: R10-ADVISOR-WHATIF (item 2257-tile-callsite) - the three tiles share one call (coordinator.py:10777); pass `steady` per spec, `"power_cap_kw" in overrides` (§2, §5).
Carry: R10-ADVISOR-WHATIF (item 2257-timeout) - `_await_off_loop` re-raises `ProcessWorkerTimeout` (2147-2149); the steady pair's own except drops the steady key, pinned by a test (§2, §5).
Carry: R10-ADVISOR-WHATIF (item 2257-stubs) - tests/debug_collect.py:567 and dev/audit/harnesses/r9_dbg2_selftest_price.py:78 mimic the async_simulate signature; add `steady=False` if a caller they stand in for passes it.
Carry: R10-ADVISOR-WHATIF (item 2257-doubles) - doubles replacing `_await_optimize` (tests/config_flow_steps.py:5414, 5588, 5630) miss the steady pair; a solve counter wraps both seams; `tests/deployment_shape.py:130` `WORKER_SEAMS` already lists `_await_off_loop` (fn at 1).
- If `tests/structure.py` refuses `coordinator.py` or `optimizer.py` growth, `_simulate_inputs`, `_reference_held_start(...)` (which shortens `_start_gap_cost`) and `_stash_initial_buffer(state)` are the payment; never a quiet raise.
