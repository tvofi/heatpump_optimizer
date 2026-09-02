# D2 — Mathematical and physical sanity (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` 3.13.1, numpy 2.5.2, scipy 1.18.1,
OpenBLAS pinned to one thread by every harness. Apple M1, 8 GB, shared with ten
other auditors (load1 22–72 while these ran; `thread_factor` 1.000 in every run).
Every number below is a count, a ratio, a residual or an exact parity: none is a
timing, so none needs the quiet window. Exposure: none (no `docs/` read).

## Method

One harness per mechanism under `tools/audit/round2/D2/`, each hooking a named
production symbol and printing `RESULT` lines; the golden `SCENARIOS` (49) are the
configuration sweep wherever a sweep is called for. Identities were checked at the
kernel level (per `_simulate_step_*` call), at the trajectory level (every
`simulate_trajectory*` entry point), on the committed fixtures, and on fresh
captures where a fixture is in the repository's own may-drift set.

## Findings

### D2-01 (high, bug) — batched single-zone simulation ignores the Euler sub-step

`simulate_trajectory_batch` is the solver's gradient twin and must be bitwise equal
to `simulate_trajectory`. It is, on all 49 golden configurations and on three stiff
two-zone cells (`parity_max_diff_golden = 0`, `parity_max_diff_two_zone_stiff = 0`).
In the single-zone branch it is not: `thermal_model.py:2401-2402` sets
`dt = dt_hours / n_sub` for the sub-step loop, but the single-zone twin integrates
with `dt_hours` per sub-step (`:2636-2637`) and re-seeds `T_room` from the initial
state on every sub-step of step 0 (`:2606`). For any single-zone configuration with
`_stability_substeps ≥ 2` the batch diverges: 5.3 °C (slab mass 0.2, transfer 1.5),
37.9 °C (slab mass 0.1 with the default transfer 0.8), 1.3e20 °C (slab 0.5,
transfer 5.0), inf (slab 0.1, transfer 5.0). All of these are inside the config
flow's own ranges (`RANGE_SLAB_THERMAL_MASS=(0.1, 60)`, `RANGE_SLAB_HEAT_TRANSFER=
(0.02, 5.0)`), and `tests/features.py::_grad_parity`'s only sub-step cell is two-zone.

Consequence, executed: `HeatPumpOptimizer.optimize` on the `slab 0.5 / transfer 5.0`
house (winter_typical, no DHW) with the batched jacobian returns status `optimal`
with objective 108.50 and cost 103.81 SEK; with `_bounds_supported_by_batch`
forced False (scipy's own scalar FD) the same inputs give objective 54.62 and cost
30.08 SEK. The batched jacobian is 1.6e83 away from scipy's estimate there
(`grad_batch_vs_scipy_maxabs_stiff`), and 0.0 on the default house.

- harness: `parity_substeps.py`; metric: max |T_batch − T_scalar| over 48 steps per
  configuration cell, and the scalar-evaluated objective of the plan the solver
  returns with vs without the batched jac.
- instrumented: `thermal_model:ThermalModel.simulate_trajectory_batch` vs
  `simulate_trajectory`, `ThermalModel._stability_substeps`,
  `optimizer:_bounds_supported_by_batch`, `optimizer:_batch_fd_gradient`.
- perturbation: `--perturb` sets `slab_heat_transfer` 5.0 → 0.8 (n_sub 2 → 1):
  parity diff 0 exactly, objective gap −0.0000, schedule L1 0.0024 kWh (to_zero).
- null control: the three n_sub = 1 cells and all 49 golden configs: 0 exactly.
- leave-one-out over the 6 stiff single-zone cells (5 finite): min 5.28 °C,
  max 2.5e74 °C, drop-most-favourable 1.3e24 °C; one cell non-finite.
- fix scope: single-zone branch of `simulate_trajectory_batch` — use `dt` and hoist
  the `T_room` seed out of the sub-step loop; add a single-zone stiff cell to
  `_grad_parity`. No golden drift expected (every fixture has n_sub = 1).

### D2-02 (medium, bug) — with a valve, COP falls as outdoor temperature rises above ~10–17 °C

`ThermalParameters.from_config` sets `cop_flow_carnot = True` for every throttling
valve (`thermal_model.py:868`). `compute_cop(T_out, flow_temp=F)` then multiplies
the linear base curve by `Carnot(F, T_out) / Carnot(35 °C, T_out)`
(`thermal_model.py:1328-1338`). The base curve's implied Carnot fraction falls from
0.33 at −20 °C to 0.17 at +25 °C (`carnot_fraction_min/max`), and the ratio's
derivative in `T_out` has the sign of `(T_ref − T_F) < 0`, so the product turns
over: for F = 45/50/55/60/65/70 °C the COP peaks at 17/14.5/13/12/11/10 °C outdoor
and at 20 °C outdoor is 0.989/0.966/0.943/0.922/0.903/0.887 of its peak. Seven of
seven flow cells are non-monotone; with `cop_flow_carnot = False` all seven are
monotone. Downstream (`valve_storage` config): `marginal_cop(T_out, "buffer",
store_temp=60)` is 2.034 at 10 °C and 1.880 at 20 °C (−7.6 %), and that COP prices
the tank in the simulation, in `_terminal_cost` and in `_deferred_energy_cost`. A
real air-to-water unit at a fixed 60 °C flow does better at 20 °C than at 10 °C.

- harness: `cop_monotone.py`; metric: sign changes of ΔCOP/ΔT_out on a 0.5 K grid
  over [−25, 30] °C per flow temperature, and COP(20 °C)/COP(peak).
- instrumented: `thermal_model:ThermalModel.compute_cop`, `marginal_cop`,
  `compute_cop_dhw`, `optimizer:HeatPumpOptimizer._buffer_charge_ceiling`.
- perturbation: `--perturb` sets `cop_flow_carnot=False`: non-monotone cells 7 → 0.
- null control: `flow_temp=None` (no valve) 0 sign changes; `compute_cop_dhw` 0
  violations in either variable.
- leave-one-out over 7 flow cells: ratio min 0.887, max 0.999,
  drop-most-favourable 0.903.
- fix scope: `compute_cop` — make the flow derate consistent with the base curve's
  own Carnot fraction (e.g. η = COP_ref·(T_ref−T_out)/T_ref at the reference, then
  COP(F) = η·T_F/(T_F−T_out) with a floor on lift) and re-record the valve/wood
  fixtures (`valve_storage*`, `wood_*`, `valve_upper_direct_slab`).

### D2-03 (medium, bug) — the planning grid steps wall-clock time on DST days

`_price_series`/`_weather_series`/`_forecast_arrays` (`coordinator.py:5728, 5849,
6035`) and `_Horizon.timestamps`/`step_datetimes` (`optimizer.py:981, 2033`) build
step instants as `aware_local_midnight + timedelta(15·i min)`. Python defines that
as wall-clock arithmetic, while Tibber entries carry real offsets and are bisected
by instant. On six DST transition days (2025-03-30, 2025-10-26, 2026-03-29,
2026-10-25, 2027-03-28, 2027-10-31) 84 of 96 steps carry a price that is not the
price in force at `t0 + i·15 min` real time (plain day: 0). Spring: the 96 labels
map to 92 distinct instants (02:00–02:45 do not exist), the horizon spans 23 real
hours, and the production optimizer anchored as the coordinator anchors it books
6.0 kWh of the day's 29.96 kWh in those four phantom steps (the night trough) —
heat the pump never delivers. Autumn: 25 real hours in 96 steps, with the step
labelled 02:45 CEST lasting 75 real minutes at 6.0 kW. `price_model._entries_by_day`
already drops DST days for learning and `tariff._window_slot` carries `fold`; the
plan grid does neither.

- harness: `dst_grid.py` (sets `HASTUB_TZ=Europe/Stockholm` itself); metric: number
  of the 96 steps whose assigned price ≠ the price in force at the real instant
  `t0 + i·15 min`, distinct instants, real span, longest step, phantom kWh.
- instrumented: `coordinator:HeatPumpOptimizerCoordinator._price_series`,
  `_forecast_arrays`, `optimizer:_Horizon.timestamps`.
- perturbation: `--perturb` replaces `_price_series`'s stepping by UTC stepping
  converted to local: misaligned 84 → 0 on all six days (to_zero).
- null control: plain day (2026-08-26) 0 misaligned, 96 instants, 24 h.
- leave-one-out over 6 transition cells: min 84, max 84, drop-most-favourable 84.
- fix scope: build `step_starts` and `timestamps` by stepping in UTC (as
  `tests/dst_checks.py`'s real walk does) and converting to local; the same for
  `step_hours`. No golden drift (fixtures use naive datetimes).

### D2-04 (medium, bug) — sysid confidence cannot reach its 0.3 adoption gate at the default interval; a drifting sensor passes it biased

`sysid.py:453-459`: `confidence = r² · min(1, rows/20) · clip(excursion/2, 0.3, 1)`.
`_run_system_identification` samples once per optimization cycle (default
`DEFAULT_OPTIMIZATION_INTERVAL = 30` min), so a 2 h step + 2 h relax yields 7 rows
(factor 0.35), and the 0.8 K comfort abort bounds the excursion factor at 0.8: the
ceiling is 0.28, below `_adopt_system_identification`'s 0.3 gate
(`coordinator.py:10610`). Executed on an exact first-order room (C 8 kWh/K,
UA 0.20 kW/K, G 0.30 kW): noise-free data scores 0.107 at 30-min sampling and 0.250
at 15-min sampling (UA recovered to 1e-15), never adopted; a 0.10 / 0.15 K/h linear
drift scores 0.304 / 0.341, is adopted, and carries UA −12 % / −24 % (τ +15 % /
+32 %). White noise up to 0.1 K and 0.1 K quantisation bias UA by ≤ 1.4 %; 0.5 K
quantisation gives UA −7 %, C +38 %.

- harness: `sysid_bias.py`; metric: `identify().confidence` and median relative
  error of UA/C/τ over 300 seeds per noise model, adoption fraction at the 0.3 gate.
- instrumented: `sysid:SystemIdentification.identify` (via `SysIdSample` records),
  the coordinator gate replicated as a filter.
- perturbation: sampling 30 → 15 min raises clean confidence 0.107 → 0.250 and the
  ceiling 0.28 → 0.60 (up); noise σ → 0 drives the UA bias to 0.
- leave-one-out over 9 noise cells: adopted fraction 0 in seven, 1.0 in the two
  drift cells ≥ 0.10 K/h.
- fix scope: size the confidence to the experiment the comfort bound allows (rows
  from the configured interval, excursion normalised by `max_excursion_c`) or lower
  the gate, and reject fits whose relax-phase residuals trend (drift).

### D2-05 (low, bug) — `wood_share` is discontinuous at the flow curve

`thermal_model.py:1108-1115`: region 1 (`wood ≥ flow_set`) returns 1.0; region 3
(both tanks at/below the curve) returns `(wood − hp)/margin`. With
`hp ∈ (flow_set − margin, flow_set]` the share jumps as `wood` crosses `flow_set`:
from `(wood − hp)/2` to 1.0 — a jump of 1.0 at `hp = flow_set` (13.44 kW of a
13.44 kW draw moving between tanks for a 1e-6 K change), 0.5 at `flow_set − 1 K`.
The docstring promises "continuous in w·Q_draw across every boundary".
`_wood_share_vec` reproduces the scalar law bitwise (parity 0), so the batched
gradient sees the same cliff.

- harness: `model_sanity.py`; metric: |w(flow_set) − w(flow_set − 1e-6)| over 21
  `hp_temp` cells in the switch margin.
- instrumented: `thermal_model:wood_share`, `_wood_share_vec`.
- perturbation: `--perturb` makes region 3 `max(wood − hp, wood − flow_set + margin)
  / margin` (meets region 1 at the curve): max jump 1.0 → 0.0 (to_zero).
- leave-one-out over 21 cells: min 0, max 1.0, drop-most-favourable 0.95.

## Non-findings (held)

| Claim | Harness / command | Value |
|---|---|---|
| Batched twin bitwise on all 49 golden configs and 3 stiff two-zone cells | `parity_substeps.py` | 0.000 °C |
| Batched jac == scipy 2-point on the default house; forward vs central FD | `parity_substeps.py` | 0.0; max rel 1.04e-6 at step 20 |
| Energy conservation per kernel call, all 49 configs × 3 schedules × 96 steps (space) | `conservation.py` | 4.0e-13 kWh |
| Same through `simulate_trajectory_with_dhw` incl. the DHW coil (39 DHW configs) | `conservation.py` | 3.7e-13 kWh |
| Same through `simulate_step` with n_sub = 3, and with a learned gains profile | `conservation.py` | 2.2e-13 / 9.3e-14 kWh |
| Wood ceiling deletes heat without booking it (documented) — only in a forced cell | `conservation.py` | 20.08 kWh of a 192 kWh burn; 0 in every golden scenario |
| `dhw_coil_draw_reduction`: reduced + coil == draw | `conservation.py` | 28 of 1426 cells off by ≤ 4.4e-16 kW (1 ulp) |
| Euler order: err(1 h)/err(15 min) after 6 h vs a 1/64 h reference | `model_sanity.py` | 4.29 (two-zone valve), 4.44 (single) |
| More power never cools a store (3 topologies × 5 states × 25 powers) | `model_sanity.py` | 0 of 2160 |
| Buffer cap clamps a rate: 75 °C read → 72.83 °C, refused 0; charging clamps at 70.000000 with 0.864 kW refused; DHW rating likewise | `model_sanity.py` | 1 / 1 |
| `dhw_coast_hours` closed form vs simulated coast | `model_sanity.py` | 0.011 h |
| Objective terms scale with `price_weight` (energy, cycling, capacity, terminal ×pw; comfort ×1) | `model_sanity.py` | residual 0.0 |
| `stored_heat_survival` ∈ [0,1]; `slab_settlement_cap` ≤ `buffer_max_temp` | `model_sanity.py` | 1 / 1 |
| `predicted_cost == Σ price·(space+dhw)·dt` (PV piecewise) on 49 fixtures | `fixture_identities.py` | 1.3e-4 SEK (6-dp rounding) |
| `dhw_heating_cost`, savings, savings % identities on 49 fixtures | `fixture_identities.py` | 1.5e-4 / 1e-6 / 4.3e-5 |
| `pv_self_consumed`, `peak_cost`, `projected_peak_kw`, `compressor_starts` re-derived | `fixture_identities.py` | 0 / 0 / 0 / 0 |
| `baseline_cost` re-derived on 10 space-only fixtures | `fixture_identities.py` | 3.4e-5 SEK |
| `deferred_energy_cost` re-derived: exact on fresh captures; five committed may-drift fixtures differ (their plans are not this box's) | `fixture_identities.py` | 3.4e-5 SEK fresh; ≤ 0.98 SEK on may-drift fixtures |
| Buffer ≤ cap, DHW ≤ rating, wood ≤ 95, power ≤ p_max/caps, savings ≤ 100 % in every fixture | `fixture_identities.py` | 0 violations |
| COP monotone (non-increasing) in flow temperature; DHW COP monotone in both variables | `cop_monotone.py` | 0 / 0 / 0 |
| Defrost derate bounded after 2000 random observations | `cop_monotone.py` | [0.55, 1.00] |
| Defrost derate jump at the 0 °C bucket edge with a learned 0.8 (bucketed by design) | `cop_monotone.py` | 0.20 (COP −20 % across 1e-9 K) |
| Base curve's implied Carnot fraction over −20..25 °C; COP at 70 °C flow peaks at 1.75 (docstring: real units 1.5–2.0) | `cop_monotone.py` | 0.165–0.328 |
| `metering_windows` conserves energy; offset grid gives 1+23+1 windows with exact head mean | `tariff_arith.py` | 5.7e-14 kW; 25 |
| `peak_cost` == marginal × Σ top-k excess for 1, 3, 5 windows above threshold; 0 below; 0 at inf threshold | `tariff_arith.py` | 0 |
| `PeakTracker` bills the month's peak once (3 spikes → billed 8.0, threshold 7.0), resets on month change, marginal 60/3 | `tariff_arith.py` | 1 / 1 / 20 |
| Grid fee rule `Nov-Mar Mon-Fri 06:00-22:00` at month, weekday and wrap boundaries | `tariff_arith.py` | 0 mismatches of 7 |
| `_known_prices_for`: hourly, quarter, mixed spacing, partial (last entry spans 1 h), stale list | `tariff_arith.py` | 0 mismatches; 96/96/96/48/0 |
| `blended_block_prices` == piecewise cost of a block; `import_margin` floors at 0 | `tariff_arith.py` | 0 / 1 |
| Learner clamps (COP scale, heat-loss scale, buffer cooling, zone split) hold at both edges | `learner_clamps.py` | 0 violations of 4 |
| sysid under white noise ≤ 0.1 K and 0.1 K quantisation | `sysid_bias.py` | median UA bias ≤ 1.4 %, 0.08 % |
| `_wood_share_vec` == `wood_share` bitwise on a 101×101 grid; range [0,1] | `model_sanity.py` | 0 / 1 |

Notes on leads that did not become findings: the four learner chokepoints
`np.clip` a NaN through to the live model (`clamp_nan_leaks = 4`); the storage
restore path (`coordinator.py:1913`) does `float()` but not `isfinite`. Reachability
of a NaN into those calls was not traced (it is the learners' input validation, not
the arithmetic), so this is a lead for D0/D3, not a D2 finding. Currency: there is no
conversion arithmetic to check (`currency.resolve_currency` is a label).

## Harnesses (all run from the export root with `PYTHONPATH=tests/hastub`)

- `tools/audit/round2/D2/parity_substeps.py` (`--perturb`)
- `tools/audit/round2/D2/cop_monotone.py` (`--perturb`)
- `tools/audit/round2/D2/dst_grid.py` (`--perturb`; sets HASTUB_TZ itself)
- `tools/audit/round2/D2/conservation.py`
- `tools/audit/round2/D2/fixture_identities.py`
- `tools/audit/round2/D2/sysid_bias.py`
- `tools/audit/round2/D2/model_sanity.py` (`--perturb`)
- `tools/audit/round2/D2/tariff_arith.py`
- `tools/audit/round2/D2/learner_clamps.py`

## Not finished

- The terminal credit's sign and magnitude against a re-simulated continuation
  (a thermostat run from each plan's end state through the next window): not built
  within the budget; `_terminal_cost` was checked only for its `price_weight` scaling.
- The learned capacity envelope vs demand-at-derate reason codes (coordinator T4b).
- Whether a NaN can reach the learner chokepoints (see note above).
- Nothing here needs a quiet-window re-take: no RESULT is a wall, CPU or RSS number.
