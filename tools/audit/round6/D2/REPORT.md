# D2 — Mathematical and physical sanity, audit round 6

- **Baseline**: `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), export at
  `/Users/timmalmstrom/audit-r6-baseline`.
- **Machine**: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy 2.4.6, scipy 1.17.1,
  interpreter `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`.
- **Harness**: `tools/audit/round6/D2/sanity.py` — one command, run from the
  export root:

      PYTHONPATH=tests/hastub python3 tools/audit/round6/D2/sanity.py

- **Contention**: the box was shared for the whole round (`load1` 12.6–17.5
  over the three recorded runs). Every number below is an **identity residual, a
  count, or a COP value** — contention-immune, so none of them is marked
  provisional. The harness emits no wall/CPU/RSS RESULT, so nothing here needs
  a quiet-window re-take. `thread_factor` was 0.757, 0.867 and 0.862 across
  the three runs (no deliberate second thread; all well under 1.05).

## Method

The harness drives, and nothing else:

| symbol | what it is used for |
|---|---|
| `thermal_model:ThermalModel.compute_cop` | the COP every price in the plan runs through |
| `thermal_model:ThermalModel.simulate_step` | per-step conservation, monotonicity |
| `thermal_model:ThermalModel._simulate_step_single` / `_simulate_step_two_zone` | the same step on the sub-step grid `simulate_step` actually integrates |
| `thermal_model:ThermalModel.simulate_trajectory` / `simulate_trajectory_batch` | scalar/batch/replay parity |
| `thermal_model:ThermalModel.simulate_dhw_step` (`_step_dhw_floor_injected`) | the DHW floor clamp |
| `defrost:DefrostDerate.factor` | the learned derate behind the COP step |
| `optimizer:_batch_fd_gradient` | the solver's batched gradient vs scipy's own |
| `optimizer:HeatPumpOptimizer._energy_cost_fn` | the cost identity, via the golden fixtures |

Specially absent from the instrumented set, deliberately: any number derived
from `const` or from reading the code. Every finding below moves under a
one-line perturbation the judge can run.

## Findings

### D2-01 — the learned defrost derate is a step function of continuous inputs, so the COP every price runs through is discontinuous

**Severity** high · **stop-rule class** bug · **files**
`custom_components/heatpump_optimizer/defrost.py` (`TEMP_EDGES`,
`HUMIDITY_EDGES`, `_bucket`, `factor`),
`custom_components/heatpump_optimizer/thermal_model.py` (`_cop_law`, the
`derate.factor(outdoor_temp, humidity)` product),
`custom_components/heatpump_optimizer/coordinator.py` (`in_frost_band` gate at
the fold sites).

**Metric definition (one line)**: `band_step_cop_<edge>` is
`|COP(t+1e-9) - COP(t-1e-9)|` through `ThermalModel.compute_cop`, in COP units,
with a fully-earned measured duty folded into the bucket on one side of the
edge.

Two of the model's *forecast* inputs — outdoor temperature and relative
humidity — are continuous physical quantities, and `DefrostDerate.factor`
answers from a hard-edged lookup table. So the COP the whole plan is priced
against is a step function of both. Measured, at the shipped defaults, with a
duty of 0.30 folded into the adjacent bucket (`DERATE_MAX` clamps the derate to
`1 - 0.30*1.5 = 0.55`):

| edge (1e-9 across) | COP below | COP above | step |
|---|---|---|---|
| -5.000000 C | 2.45000 | 1.34750 | **1.10250** |
| 0.000000 C | 2.88750 | 1.58813 | **1.29937** |
| 2.000000 C | 3.06250 | 1.68438 | **1.37812** |
| 5.000000 C | 1.82875 | 3.32500 | **1.49625** |
| 8.000000 C | 1.97313 | 3.58750 | **1.61437** |
| 70.000000 % RH (at 2 C) | 3.06250 | 1.68438 | **1.37812** |
| 70.000000 % RH (at -1 C) | 2.80000 | 1.54000 | **1.26000** |

Leave-one-out over the eight cells: min 0.649687, max 1.61437, and dropping the
single most favourable cell (the largest step, 8 C) leaves **1.49625 COP**.
The step at 5.000000 C is *upward*: the model's price of heat more than
**doubles** (1.82875 -> 3.32500) as the forecast crosses five degrees upward,
because bucket `[5,8)` was never learned and bucket `[2,5)` was. Humidity
matters identically — 69.999999 % and 70.000001 % RH are the same weather and
differ by 81.8 % of the modelled COP.

**Perturbation** (what the judge runs): fold a duty of 0 instead of 0.30 (or set
`params.defrost_derate = DefrostDerate()`), leaving the edges untouched. The
number must go **to zero**; it does —
`band_step_cop_null_no_duty = 1.75e-10 COP` and
`band_step_cop_null_rh_no_duty = 0 COP`. And the step scales linearly with the
learned duty, which is the mechanism confirming itself: at duty 0.15 the 0 C
step is `0.649687` = exactly half of `1.29937`.

**Why this is a defect and not the frost physics.** A real pump's COP does dip
in the frosting band, and the derate is *supposed* to make the model
non-monotone there. What is not physics is the *edge*: the model asserts that
frost costs 45 % of COP at +0.000000001 C and nothing at -0.000000001 C, and
that a 70 % relative humidity forecast is a different physical regime from
69.999999 %. `in_frost_band` (0.0 <= t < 5.0) is the right boundary for
**attribution** — which learner gets to see a shortfall, and the module argues
that case — but it is also, through the bucket table, the boundary the *model*
steps on, and no honest attribution rule requires the modelled COP itself to
jump. The consequence is a plan whose cost of heat is a step function of two
continuous forecasts: a horizon straddling 0 C (or a humidity forecast
hovering at 70 %) prices its steps at two different physics, the multi-start
solver's basin selection moves with them, and a re-solve on a forecast that
crossed the edge by a rounding amount can re-plan.

**Proposed fix scope**: make `factor()` vary continuously across bucket edges —
either by interpolating between the two adjacent buckets' learned values on a
declared cell grid, or by applying the derate through a taper that reaches 1.0
at the band edges the way `flow_lift_factor` already tapers its own band. Either
leaves the attribution gate alone. Expected golden drift: every frost-band
fixture would move; `precip_snow`, `winter_*` and `valve_storage*` are the
candidates to claim.

### D2-02 — the DHW tank's inlet floor is a heat source with no source, reachable from the shipped config surface

**Severity** medium · **stop-rule class** bug · **files**
`custom_components/heatpump_optimizer/thermal_model.py` (`simulate_dhw_step`,
the `floor` block and `_step_dhw_floor_injected`),
`custom_components/heatpump_optimizer/const.py`
(`DHW_COOLING_REFERENCE_AMBIENT_TEMP = 20.0`).

**Metric definition (one line)**: `dhw_free_kwh_day_inlet_<x>` is the sum of
`simulate_dhw_step`'s `_step_dhw_floor_injected * dt` over 96 quarter-hour steps
started at the inlet reference, commanded power 0 throughout, in kWh.

`simulate_dhw_step` forbids the tank from ever falling below
`dhw_inlet_reference` and books the heat that takes on
`_step_dhw_floor_injected`. The tank's surroundings are fixed at
`DHW_AMBIENT_TEMP = 20.0`. So whenever the configured or sensor-supplied inlet
reference sits **above 20 C**, the clamp is not a safety bound: it holds the
tank at a temperature its own standby loss is trying to pull it below, and the
difference is manufactured. The tank is pinned at the floor, permanently:

| inlet reference | end temperature after 24 h unheated | heat injected |
|---|---|---|
| 10 C (default) | 11.70 C | 0.00000 kWh |
| 19 C | 19.16 C | 0.00000 kWh |
| 20 C | 20.00 C | 0.00000 kWh |
| 21 C | **21.00 C, pinned** | 0.10022 kWh |
| 22 C | **22.00 C, pinned** | 0.20045 kWh |
| 25 C | **25.00 C, pinned** | 0.50112 kWh |
| 33 C | **33.00 C, pinned** | 1.30291 kWh |

Leave-one-out over the seven cells: min 0.0, max 1.30291, dropping the single
most favourable (largest) cell leaves 0.50112 kWh/day.

**Reachability from the shipped surface**: `config_flow.py:1598` offers
`CONF_DHW_INLET_TEMP` with `_number(2, 25, 0.5)` and
`CONF_DHW_INLET_SEASONAL_AMPLITUDE` with `_number(0, 8, 0.5)`, and a live inlet
entity supersedes both. So 25 C by configuration and 33 C by
inlet-plus-amplitude are both inside the shipped form — and
`dhw_free_kwh_day_inlet_33_config_max` confirms 1.30291 kWh/day at that setting.
The rate is exactly `UA_dhw * (inlet - 20)`:
`dhw_free_kw_inlet_25 = 0.02088 kW` against
`UA = 0.004176 kW/K * 5 K = 0.02088 kW`.

**Perturbation**: set the inlet reference at or below the 20 C tank ambient
(the shipped default, 10 C) — the number must go **to zero**, and it does
(`dhw_free_kwh_day_inlet_10 = 0`, `..._inlet_19 = 0`, `..._inlet_20 = 0`). The
tank's own temperature moves the same number in the same direction, which is
the null control the other way: a tank started hot never reaches the floor
(`dhw_free_kwh_day_hot_tank_control = 0 kWh`).

**Consequence, honestly bounded.** The energy identity *does* close — this is
not deleted heat, it is booked heat — so the defect is not a broken balance.
It is that the model contains a source term with no physical origin, and the
plan is priced against it: the tank holds a temperature its standby loss would
never hold it at, for free. The magnitude is bounded and small (0.1-1.3 kWh/day
of heat, i.e. a few ore of electricity a day at any real COP), which is why the
severity is `medium` and not higher. A second, sharper symptom appears at the
same setting: with the tank pinned at the floor, `T - inlet = 0` zeroes the
draw scaling entirely, so the whole day's hot-water service is booked at
`_step_dhw_draw_kw = 0.0000 kWh`. That half *is* defensible — a 22 C tank
genuinely cannot deliver 40 C mixed water — but it means a tank pinned at a
>20 C inlet reads as a tank serving the house for nothing.

**Proposed fix scope**: the floor should not be a source. Either clamp the
tank at `min(inlet_reference, DHW_AMBIENT_TEMP)` — the physical floor of a tank
standing in a 20 C room — or keep the inlet floor but inject no heat, letting
the tank sit below the inlet and letting the draw scaling (already
inlet-referenced) carry the consequence. The second is a one-line change and is
inert everywhere the inlet reference is at or below ambient, i.e. every
default. Expected golden drift: none — no golden scenario configures an inlet
above 20 C, which is also why six rounds of fixtures never showed this.

## Non-findings — what was checked and held, with the number

Every one of these is an executed number from the same harness; together they
are the reason the two findings above are the ones worth carrying.

| claim that held | RESULT | value | tolerance |
|---|---|---|---|
| Per-step energy conservation, single- and two-zone, valved, wood two-tank, direct-curve and slab-direct layouts — stores' enthalpy change = injected - losses - the refusal ledgers | `conserve_resid_kwh` | **1.78e-13 kWh** worst over 280 cells (136 of them on the sub-step grid `simulate_step` integrates) | < 1e-9 kWh |
| More commanded power never cools a store | `mono_violations` | **0** over 21 (config, dt) cells x 121 power points x 5 stores; `mono_worst_drop_c = 0` | 0 |
| Scalar `simulate_trajectory` = `simulate_trajectory_batch` = repeated `simulate_step`, bit for bit, on room/slab/upper/lower/buffer/wood and on the refused ledger | `parity_mismatches` | **0** over 7 configs (incl. two-tank wood, valve targets, smart_write, slab-direct, curve) | exact |
| The solver's batched forward-difference gradient is scipy's own estimator, to the last bit — including one-sided, unbounded and near-degenerate bound shapes | `gradient_mismatches` | **0** of 300 bound classes; `gradient_worst_abs_diff = 0` | exact |
| `predicted_cost` = sum(price*power*dt), piecewise in the PV surplus, on every golden fixture | `cost_identity_worst_sek` | **2.71e-06 SEK** (`valve_storage_small_tank`, 6-dp recording) over 50 fixtures | recording precision |
| COP is monotone in outdoor temperature and in flow temperature when no derate is learned | scratch sweep | 0 negative first differences over 2001 outdoor points x 8 configs; `flow_lift_factor` non-increasing in flow over 1401 points | 0 |
| The savings identity `savings = baseline - predicted - deferred` and its percentage | fixture sweep | worst residual 4.3e-05 SEK on `negative_prices` (recorded to 6 dp) over 50 fixtures | recording precision |
| No store crosses a physical bound in any golden scenario (buffer cap, DHW rating, 95 C wood ceiling) | fixture sweep | 0 violations over 50 scenarios | 1e-9 |
| `derate_from_duty` stays inside `[DERATE_MIN, DERATE_MAX]` | `band_*` | min 0.55, max 1.0 over 2001 duties | inclusive |
| The smooth peak surrogate never charges meaningfully more than the exact billed top-k | scratch sweep | worst over-charge **9.96e-07** relative over 4000 random excess vectors | the pin allows 1e-6 |

### A harness gap found the hard way (recorded so the next auditor does not pay it)

The first version of `probe_conservation` evaluated the loss terms once, at the
step's initial state. On cells where `simulate_step` subdivides
(`_stability_substeps`, 101 sub-steps for the 10 L tank at dt=1.0) the store
temperatures move tens of kelvin inside one step, so the initial-state loss
over-states the losses and the probe reported a **5.04 kWh** hole in a step
that conserves to 2e-14. The number was the harness's own discretisation error.
The probe now marches `_stability_substeps` sub-steps through the same two step
bodies `simulate_step` dispatches to, and emits `conserve_substep_cells` so a
reader can see how many cells depend on that. **Any conservation sweep on this
model must integrate the loss terms on the production sub-step grid.**

## Exposure

Nothing outside the export was read: no `gh`, no GitHub, no earlier round's
audit records (the export has no `docs/audit-*.md`, no `docs/backlog.md`, no
`tools/audit/round3/4/5`). Two sources inside the tree carry earlier audit
findings, and were read as context for what is already known:

- code comments citing earlier ids (`D2-01`, `D2-03`, `D2-07`, `R3-D2-03`,
  `R5-D2-01`, `D9-01`, `#961`) — used only to avoid re-reporting a fixed
  defect, never as evidence;
- `RELEASE_NOTES.md`, to see which areas the round-5 wave had just hardened
  (`#1370` the valved buffer's monotone bound, `#1375` sysid adoption), so that
  the probes aim where the code is least recently inspected.

## What I could not finish

- `sysid` bias under white, quantised and drifting noise (D2 brief item 5). The
  round-5 wave landed `#1375` on exactly this surface (drift-biased UA and the
  gap fallback) and the brief's `identify` path is 400 lines of ridge,
  errors-in-variables and drift-column algebra; I ran out of budget before
  building the noise sweep, and I did not want to report a number from a
  partially read fit. **Uncovered.**
- The terminal credit versus a re-simulated continuation (D2 brief item 3). I
  read `_terminal_cost` and its batch twin and confirmed the two share one
  per-row body, but did not execute a re-simulation comparison.
- Grid-fee day/night and weekday windows and the 23/25-hour DST days: covered
  heavily by `tests/dst_checks.py` and `tools/audit/round3/D2/window_size_sweep.py`
  (cited in `tariff.py`), so I spent the budget on the uncovered surfaces
  instead. Not independently re-measured this round.
- The defrost derate's *convergence* behaviour (the EWMA seeded at 0 and the
  measured/inferred selection step at 12 samples) — read, not measured.
