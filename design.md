# Design: R10-ADVISOR-WHATIF — the steady-start what-if estimator (#2257)

Base: c3a279e3252a8b57bb00b5a677318cd4fe20387f (origin/main; no predecessor, `After: none`).
Toolchain: refreshed by `tools/audit/seat/cloud-setup.sh`, `--check` OK, numpy 2.5.4 / scipy 1.18.1 = `tests/requirements-ci.txt`.

## 0. Measured at the base
`r10_advisor_residue.py whatif`: `rows 24 plan_moves_by_start 24 held_moves_by_start 0`; caps `plan 18/36 settled 1/36` reading a saving.
**The brief's 19/36 and 3/36 (at 92588d581) do not reproduce on the pinned toolchain**: they equal #2834's 18/36 and 1/36. The 2 extra settled rows
are this-box variance from the stale venv (numpy/scipy behind the locks), not drift. The 1/36 that remains is real: a measured-start settled cap row still saves.

Spike (never merges; the fixer rebuilds it as a harness arm, §5): each plan solved from `_thermostat_held_state` at its **own** schedule's step-0 comfort target
(`config.get_comfort_temp(start)`), the rest of `state` as measured, over the same 24 rows and three starts:

| figure | moves by start | degree sign wrong | cap rows saving (< -1) |
|---|---|---|---|
| steady, plan spend only | 0/24 | 3/12 (null 07:00/15:00 +1 read -18.8/-24.0; null 15:00 -1 reads +4.1) | 30/36 |
| **steady, settled** (spend + each side's `deferred_energy_cost`) | **0/24** (spread 0.00) | **0/12** | **0/36** |
| held (control) | 0/24 | 0/12 | n/a (0 by construction) |

So the estimator is **steady and settled**: from held starts the start side of the settlement is zero, and the end side buys back the heat a capped or
cooler plan leaves unstored. Varying 00:00 rows: `target_minus_1` -32.2, `target_plus_1` +28.8, `power_cap_75` +10.7, `fuse_cap_50` +46.0, identical at all starts.
Magnitude is about half the held figure (null 00:00: +25.2 against +51.5): the plan follows a moved schedule by less than the thermostat does (`docs/dashboard-card.md`, "The price of a degree").

## 1. Owning seam
`HeatPumpOptimizerCoordinator.async_simulate` (`tests/seam_map.json`: `core`) owns the change. It calls:
- `optimizer.py`: one new public method `HeatPumpOptimizer.steady_start(state, forecast, start_time) -> ThermalState`, a wrapper on the private
  `_thermostat_held_state` (already the thermostat baseline's primitive, #2255) with the step-0 target from `self.config.get_comfort_temp`. No solver change.
- `price_tiles.py`: `monthly_deltas` gains `steady: tuple[live, sim] | None`, which adds `monthly_steady_cost_delta` (per_month of sim spend + sim deferred + wood - live spend - live deferred). Pure.
One owner: the optimizer gains a read-only accessor, not a concern. No second owner.

## 2. Shape
`async_simulate(overrides, *, limited=True, base=None, steady=False)`. With `steady=True` it runs, after today's measured shadow solve:
the live configuration and the scratch one, each from `opt.steady_start(state, ...)` of its own optimizer, same horizon, same `solve_at`, same mode block,
quiet windows composed **without** the overrides on the live side and with them on the scratch side, mold floor at each side's own `target_temp`, wood on both.
The inputs are built by one extracted helper (`_simulate_inputs(state, config, caps, quiet, wood_kw)`) called three times, which also pays the line growth.

Payload: **no what-if TypedDict exists in `payload.py`** (async_simulate returns `dict[str, Any]`); none is added. `monthly_cost_delta` **keeps its meaning**
(the measured-start plan, one-off included); a new key `monthly_steady_cost_delta` is present only on a `steady=True` answer and only when both steady solves succeeded.

Per caller:
| caller | steady | figure it reads, after | reason |
|---|---|---|---|
| card (`services.handle_simulate_plan`) | True | `monthly_steady_cost_delta` | the owner's ruling |
| cap tile (`_maybe_refresh_price_tile`, `power_cap_kw`) | True | `price_tiles.monthly_figure` -> steady key | brief: a cap tile row never reads a saving; measured-start settled still saves 1/36 |
| degree tiles | False | `monthly_held_cost_delta`, unchanged | spread already 0.00, sign already right; +2 solves on 2 of 3 rotations buys nothing |
| fuse advisor (`cost_delta_sek_month`) | True | steady key | it reads the cap tile's figure (price_tiles docstring); +2 solves a week |
| debugger `_solver_smoke` | False | `cost_delta`, unchanged | it times one solve against the live plan; extra solves change what `wall_ms` measures |

Card: `summary()` (heatpump-optimizer-card.js, the what-if summary) reads `result.monthly_steady_cost_delta`; absent, it renders **no money line** (comfort
lines stay). The en and sv `whatif.cheaper_per_month` / `dearer_per_month` / `same_cost` strings say "steady-state monthly estimate". Docs: the
"Try in what-if" sentence in `docs/dashboard-card.md` becomes: the panel prices the plan from a house already held at each schedule, settled, so a change's
one-off coast or heat-up is excluded; it prices the plan, the tile a thermostat, so the two figures differ.

Invariants kept: `limited=False` neither reads nor writes the limiter or the card cache; the slot is spent when the first solve starts (#1448); every
override still reaches only scratch copies (#240); an error answer carries no figure, so a tile records nothing.

## 3. Cost (Raspberry-Pi-class)
This box, harness fixture: measured shadow solve mean 623 ms; the steady pair mean 1201 ms, max 1838 ms. Card what-if: 1 solve -> 3 (~1.8 s here).
**Bound**: at most 3 solves per user what-if, at most one what-if start per `SIMULATE_MIN_INTERVAL_SECONDS` (unchanged); the live steady solve is cached
on (`id(self._optimization_result)`, `solve_at`), so a drag within one quarter costs 2. Background: cap tile +2 solves every third interval
(<= +0.67/interval), fuse +2/week. The fixer re-measures solve count (a counting wrapper on `_await_optimize`) and wall per what-if before/after on
`tests/features.py`'s async_simulate fixtures and states it in the body; a Pi-class ratio it cannot bound is a finding, reported.

## 4. Alternatives (lost)
- **Steady, unsettled**: 3/12 degree signs wrong, 30/36 cap rows save (table above): an end-of-horizon coast reads as saving.
- **Panel reads the held figure**: it prices a thermostat, not the plan, and is 0 for every cap, fuse and hot-water what-if (the baseline ignores caps).
- **Steady-solve the live plan every interval**: doubles every scheduled cycle's solves with no what-if asked; the lazy cache costs nothing when unused.
- **Disclosure only**: ruled out by the owner, 2026-11-01.

## 5. Evidence plan
- Sibling sites: `grep -rn "async_simulate(" custom_components/` (four callers above) and `grep -rn "monthly_cost_delta\|monthly_settled_cost_delta" custom_components/ tests/` (card summary, cap tile, fuse, PriceTile is a different payload and stays).
- Failing test first (`tests/features.py`): the panel's figure (`monthly_steady_cost_delta` from `async_simulate(..., steady=True)`) at the harness's three starts spreads 0; red at the base (key absent; `monthly_cost_delta` moves 24/24). Sign test: degree tiles -1 < 0 < +1 and cap >= -1 on the harness rows; red at the base on the settled rows varying 00:00 (`target_minus_1` +24.6, `target_plus_1` -25.8). `tests/card.mjs`: no steady key renders no money and no caveat.
- Finder harness: `dev/audit/harnesses/r10_advisor_residue.py` gains a `steady` column in the whatif arm, calling `HeatPumpOptimizer.steady_start` and `price_tiles.monthly_deltas` (never a re-implemented formula); verdict requires steady spread 0 and 0 cap saves.
- Null control: held spread 0.00 on every row; null series reads the same steady figure at all starts before and after; empty panel renders nothing.
- Mutants: live side solved from the measured state (spread moves); drop `deferred_energy_cost` from the steady key (cap saves 30/36); card summary falling back to `monthly_cost_delta`.
- Goldens: the cap tile's and fuse advisor's figures move; run `GOLDEN_MODE=drift` and claim per `claim-files.md` only what moves.

## 6. Hot files, position, carries
Hot: `coordinator.py`, `optimizer.py`, `price_tiles.py`, `services.py`, `www/heatpump-optimizer-card.js`, `docs/dashboard-card.md`, `tests/features.py`, `tests/card.mjs`. After: none; serial position free.
Item (2), P141, is **already on main**: 86e9f8d53 moved the slot builder to `plan_slots.py` (a numpy dependency kept it out of `payload.py`, stated in its docstring).

## Notes for the fixer
Carry: R10-ADVISOR-WHATIF (item 2257)
Carry: dismissed: landed on main at 86e9f8d53, verify ancestry only (item P141)
- `_thermostat_held_state` takes a `WeatherSeries`; check `ForecastSeries` supplies its four arrays, or pass them.
- If `tests/structure.py` refuses `coordinator.py` growth, the `_simulate_inputs` extraction is the payment; never a quiet raise.
- `monthly_steady_cost_delta` must not reach the degree tiles: `monthly_figure` keys on `power_cap_kw` only.
