# D2 round-3 — verifier 1 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, run from the export root
with `PYTHONPATH=tests/hastub`. Machine: 8-core Apple M1, 8 GB, python 3.11.5,
numpy 2.4.6, scipy 1.17.1 on OpenBLAS. The five BLAS thread variables were
`export`ed to `"1"` (not `setdefault`) before every invocation; every harness
prints `blas_pin=1,1,1,1,1`.

`load1` across the session ran **23.2 – 99.7** (box ambient floor is ~1.9 with
zero audit workload, per the round-2 judge). Every number below is a count, an
exact float identity or a median over deterministic seeded arithmetic. **All
three finder harnesses re-ran to their recorded values digit-for-digit** at
`load1` 44.6–48.8 against recordings taken at `load1` 44.6–99.7, which is
itself the demonstration that contention cannot move them. No timing, CPU or
RSS number appears in this report. `tests/stress.py` was not run, no full
`tests/run.sh` was run, the gate lock was never taken, and nothing outside
`tools/audit/round3/D2/verify-1/` (plus this file) was created or modified.

My own instruments are under `tools/audit/round3/D2/verify-1/`:
`v1lib.py` (my own thread pin / sys.path / RESULT printer — deliberately not
`d2lib`, so a defect in the finder's shared module cannot propagate into my
numbers), `v1_cop_bound.py`, `v1_dst_clock.py`, `v1_sysid_plant.py`, plus the
raw outputs `out_v1_*.txt` and the finder re-runs `rerun_*.txt`.

---

## Step 1 — the finder's harnesses, re-run as their headers say

| harness | recorded | my re-run | verdict |
|---|---|---|---|
| `cop_monotonicity.py` | every RESULT in `out_cop_monotonicity.txt` | identical | reproduces |
| `dst_window_factors.py` | every RESULT in `out_dst_window_factors.txt` | identical | reproduces |
| `sysid_bias.py` | every RESULT in `out_sysid_bias.txt` | identical | reproduces |

**Method defect, two of three: the harness headers carry stale EXPECTED
values.** The audit README says the judge re-runs a harness *without reading the
finding*, from the header. Keyed on the header, two of these three read as
mismatches:

* `cop_monotonicity.py` header: `violating_flow_temps=6 of 7` and
  `worst_drop_kelvin_band_-20_20=0.15959` (tolerance 1e-4). Executed:
  `7_of_7` and `0.02093`.
* `dst_window_factors.py` header: `total_mismatched_cells=8 of 12`. Executed:
  `12_of_12`.
* `sysid_bias.py`'s header matches what it prints.

The report bodies carry the correct numbers, so this is a header-hygiene defect,
not a false claim — but it is the exact failure mode the harness contract exists
to prevent, and it is worth a fix before these instruments are handed on.

---

## D2-01 — COP falls as the weather warms under the Carnot flow correction

### My number

Harness: `v1_cop_bound.py`. Output: `out_v1_cop_bound.txt`, `out_v1_cop_eta.txt`.

**My metric (one line):** the maximum *relative* fall of
`ThermalModel.compute_cop(T_out, flow_temp)` with respect to rising outdoor
temperature, in %/K, by central difference at h=0.01 K on a 4001-point grid
(not adjacent 0.5 K pairs), together with the largest *inversion gap* —
max over pairs `T_cold < T_warm` inside the domain of `COP(T_cold) − COP(T_warm)`
— reported over four nested outdoor domains.

The finder's metric is a count of strictly-decreasing adjacent pairs on a 0.5 K
sweep and the largest such step. Both are hooked on the same symbol; mine is
grid-independent and scale-free, theirs is grid-dependent. They are comparable
in sign and in which flows violate.

```
RESULT domain_full_-20_35   violating_flows=7_of_7 max_rel_fall=45.5686pct_per_K max_inversion_gap=2.22562 COP
RESULT domain_heating_-20_20 violating_flows=6_of_7 max_rel_fall= 2.7755pct_per_K max_inversion_gap=0.19650 COP
RESULT domain_core_-20_15   violating_flows=5_of_7 max_rel_fall= 1.0962pct_per_K max_inversion_gap=0.04503 COP
RESULT domain_cold_-20_10   violating_flows=1_of_7 max_rel_fall= 0.0064pct_per_K max_inversion_gap=0.00000 COP
```

**Headline (mine): `V1_max_inversion_gap_heating_band = 0.19650 COP`
(flow 70 °C), `V1_max_rel_fall_heating_band = 2.7755 %/K`.**

### I derived the bound myself rather than accepting the finder's algebra

The code's construction is `COP = N(T_out) · carnot_flow/carnot_ref`. Because
`carnot_ref` depends only on `T_out`, the implied **second-law efficiency** of
the modelled machine,

    eta(T_out) = COP_model / (T_flow_K / (T_flow_K − T_out_K)),

is algebraically independent of flow. Executed:
`implied_eta_flow_independence_max_abs_spread_T<=20 = 1.110e-16` across the
seven-flow grid, and it equals the closed form `N(T_out)·(35 − T_out)/308.15`
to `4.718e-16`. So the model is exactly *"true Carnot at the real flow, times a
fitted efficiency that depends only on outdoor temperature"* — a physically
well-formed construction. What is wrong is the **shape** of that efficiency:

```
RESULT implied_eta_at_-10C=0.2939  0C=0.3280  5C=0.3237  10C=0.3052  15C=0.2726  20C=0.2257
RESULT implied_eta_peak_at_C=1.000   fall_peak_to_20C = 31.23 %
```

The implied second-law efficiency peaks at +1 °C and **collapses 31 % by
+20 °C**, on its way to zero at +35 °C, because the reference Carnot denominator
`(35 − T_out)` goes to zero while the nameplate curve `N` is linear and capped
at 1.5. A real vapour-compression machine's second-law efficiency does not
collapse as the lift shrinks.

My analytic crossover — solving `0.025/(1+0.025(T−7)) = 1/(35−T) − 1/(flow−T)`
by Brent, derived here from the code's own expressions — matches the numeric
argmax to **≤ 0.005 K on six of the seven flows** (the seventh, 40 °C, has its
crossover at 20.895 °C, outside my heating domain, so the numeric argmax sits on
the domain edge). The finder's algebra is independently confirmed.

**Is the fall genuinely impossible, or merely surprising?** Genuinely a violated
bound, with one honest caveat. At a fixed condensing (flow) temperature, cutting
the lift cannot cut steady-state COP; the two real mechanisms that *can* dent
measured COP as it warms — defrost and part-load cycling — are respectively
modelled separately (`defrost_derate`, disabled in both sweeps) and absent from
this model entirely. So the sign is wrong, not merely unusual. But the deeper
statement is the efficiency collapse, not the monotonicity: the model
under-states COP at mild outdoor temperatures at **every** flow above the
reference, including flows and temperatures where COP is still rising and the
finder's metric reads zero.

### Attacks run

* **Grid artefact — dropped cells and re-aggregated.** Yes, partly. The
  finder's headline `7_of_7` and `worst_drop_full_sweep = 0.5267` are dominated
  by outdoor temperatures of 27–35 °C, where no house has a space-heating load
  and where the `max(·, 1.0)` clamps inside the Carnot denominators distort the
  curve (36 °C flow "violates" only there, and its `worst_step = 0.5267` is a
  clamp artefact, not physics). Re-aggregating on nested domains: **6/7 at
  −20..20, 5/7 at −20..15, and 1/7 with a zero inversion gap at −20..10.**
  Below +10 °C outdoor the defect is effectively absent. The finder anticipated
  half of this with their own `-20..20` band row, to their credit.
* **Leave-one-out over flow cells.** `loo_range_inversion_gap = 0.19650`,
  `loo_max_inversion_gap_without_best_flow = 0.18146` — the headline does not
  rest on one cell.
* **Null control missing or failing?** Present and passing, and I added two the
  finder did not run: `cop_flow_carnot=False` → `0_of_7` and
  `max_rel_fall = 0.0`; `flow_temp = 35.0` (at the reference) → 0 falling
  points; `flow_temp = 30.0` (below it) → 0 falling points. My **live positive
  control** (a −0.02·T_out tilt injected into `compute_cop`) fires with 581
  falling points, so those zeros are real zeros and not a dead path.
* **Reachable in real Home Assistant?** Yes. `thermal_model.py:916` sets
  `cop_flow_carnot = mixing_valve.is_throttling(mixing_valve_mode)`, and
  `THROTTLING_MODES` is every mode but `none` — `manual`, `smart_read`,
  `smart_write`. `buffer_max_temp` defaults to 70 °C, so the whole flow grid is
  in range. I hooked the settlement entry point the finder did not:
  `marginal_cop(store="buffer", store_temp=…)` gives inversion gaps 0.03097 /
  0.12868 / 0.18145 COP at 45/55/65 °C over the heating band, while
  `marginal_cop(store="room")` — which never passes `flow_temp` — gives
  `0.000000`, a clean internal control.
* **Severity earned by consequence?** Partly. The decision-relevant number is
  small: comparing a 10 °C hour against a 15 °C hour at a fixed tank
  temperature, the model prefers the colder hour by 0.0158 COP at 60 °C flow and
  0.0332 at 65 °C, and prefers the warmer hour at 50 °C and below. Relative
  inversion over the heating band runs 1.07 % (45 °C flow) to 9.66 % (65 °C).
  The finder measured **no** money consequence and says so explicitly; on
  Raspberry-Pi-class hardware there is no resource cost, only a mis-priced
  storage decision in mild weather. `medium` is the right level — but it is
  earned by the *breadth* of the efficiency error (31 %, at every flow above
  reference, present where the monotonicity metric reads zero), not by the
  monotonicity headline, which is narrower than the report's `7_of_7` framing
  suggests.

**Vote: `verify`, severity `medium`** (same level as the finder, different
reason). Executed number: `V1_max_inversion_gap_heating_band = 0.19650 COP`,
`implied_eta_fall_peak_to_20C = 31.23 %`, control `0_of_7`.

---

## D2-02 — the capacity-tariff mask walks the wall clock, the plan walks UTC

### My number

Harness: `v1_dst_clock.py`. Output: `out_v1_dst_clock.txt`,
`out_v1_dst_labels.txt`.

**My metric (one line):** the number of horizon windows `i` where
`window_factors(mask, start, n, dt)[i]` differs from `mask.sample_factor(T_i)`,
where `T_i` is the real instant of plan step `i` built **here, by hand, from
UTC** (`start.astimezone(utc) + i·dt`) rather than by calling
`optimizer._utc_step_starts` — so my truth vector does not inherit the very
production function the finding argues about.

The finder's metric is the same comparison but takes `_utc_step_starts` as the
truth. The definitions coincide; mine removes the circularity.

```
RESULT V1_mismatch_autumn_60min_peak_hours=4_of_48   spring=4_of_48
RESULT V1_mismatch_autumn_30min_peak_hours=8_of_96   spring=8_of_96
RESULT V1_mismatch_autumn_15min_peak_hours=16_of_192 spring=16_of_192
RESULT V1_direction_autumn = mismatched=4_of_48 plan_free_meter_bills=2 plan_bills_meter_free=2
RESULT V1_direction_spring = mismatched=4_of_48 plan_free_meter_bills=2 plan_bills_meter_free=2
RESULT V1_direction_control= mismatched=0_of_48 plan_free_meter_bills=0 plan_bills_meter_free=0
```

**Headline (mine): 4 of 48 windows mis-billed on each transition day; 2 of them
hours the plan scores at 0.0 that the meter bills at 1.0.** Identical to the
finder's production-path arm.

The *label* claim is exactly true and I measured it separately:
`label_wrong_hours_autumn = 45_of_48` (first at step 3: produced `10-25 03:00`,
real `10-25 02:00`), `spring = 46_of_48`, `control = 0_of_48`. Every window from
the transition onward carries the wrong hour; only the four that cross a mask
boundary change the factor.

### The half the finder asserted but did not execute

Both `tariff.py:window_factors` and `optimizer.py:_peak_window_factors` claim in
their docstrings that "the plan's cost term and the realised tracker can never
disagree about which hour a window bills under". I drove the realised side —
`PeakTracker.observe` at the real instants — and read back the factor it
captured per window:

```
RESULT V1_live_meter_vs_plan_autumn = tracker factor differs from plan factor in 4_of_48 windows
RESULT V1_live_meter_vs_plan_control= 0_of_48
```

The docstring guarantee is falsified directly, against the tracker itself, not
against a proxy.

### Attacks run

* **Null control missing or failing?** Present and passing, and I added three
  the finder did not: ordinary Sunday `0_of_48`; the same two dates in
  `Asia/Tokyo`, a zone with no DST, `0_of_48` each; a tz-naive start
  `0_of_48`. My **live positive control** (rotating the produced factor vector
  by one window on the ordinary day) is caught, `4_of_48` — so the zeros are
  real.
* **Aggregate a grid artefact?** The finder's headline
  `total_mismatched_cells = 12_of_12` is a *saturating cell count*: a cell
  enters it on one bad window out of 48. The per-cell spread in their own
  output is 1 to 16 (`autumn_60min_weekdays_only = 1_of_48`). The number that
  carries information is the per-day 4-of-48, which the report body does state.
* **Money arm.** The finder's `180.0000` is not a solved-plan outcome — no
  optimizer was run — it is `9 kW × 20 currency/kW`, the marginal price times a
  power the harness parked by hand. I normalised it:
  `V1_unpriced_per_kw = +20.0000` at 1, 3 and 9 kW alike on both transition
  days, `+0.0000` on the control. The figure is definitional; the *mechanism*
  it prices is real, but "180 currency units" is a scenario, not a measurement.
* **Reachable?** Yes, and I measured how often. The production anchor is
  `coordinator._solve_anchor(now)` — `now` floored onto the 15-minute forecast
  grid — **not** local midnight; the finder's midnight start is the most
  favourable choice available. Sweeping every 30-minute solve start across six
  days around each transition: `172 of 576` starts produce a mismatch, first at
  `2026-10-23 08:00+02:00`, last at `2026-03-29 01:30+01:00`. Against
  `365×24×2 = 17 520` solves a year that is **0.98 % of a year's solves**, and
  only on installs that configured a `peak_hours` / `weekdays_only` / `months`
  mask (`mask_active` is false otherwise and `window_factors` returns `None` —
  `no_mask_returns_none = True`).
* **Severity earned by consequence?** Not at `high`. Three things bound it:
  (1) 0.98 % of solves, on two 48-hour stretches a year, mask-configured
  installs only; (2) 4 of 48 windows per affected horizon, half of them in the
  over-timid direction (plan bills, meter does not) which costs opportunity
  rather than money; (3) the executed step is always labelled from its **own**
  wall slot — `_window_slot(start)` at index 0 is correct — so the horizon is
  re-planned correctly as each wrong hour arrives, and the residual harm is a
  mis-shaped forward plan rather than a delivered burst. It is a genuine
  correctness defect that falsifies a stated invariant in two docstrings, and
  the existing coverage genuinely misses it (`tests/dst_checks.py:287` starts at
  13:30 on the autumn day, after the 03:00 fold, and never crosses it) — but
  the consequence is `medium`, not `high`.

**Vote: `weaken` to severity `medium`.** Executed number:
`V1_mismatch_autumn_60min_peak_hours = 4_of_48` (2 free-but-billed),
`V1_live_meter_vs_plan_autumn = 4_of_48`,
`V1_reachability_affected_solve_starts = 172_of_576` = 0.98 % of a year's
solves; all four null controls `0`.

---

## D2-03 — a drifting room sensor lands in the identified heat-loss coefficient

### My number

Harness: `v1_sysid_plant.py`. Outputs: `out_v1_sysid_plant.txt`,
`out_v1_sysid_consequence.txt`, `out_v1_finder_plant_excursion.txt`.

**My metric (one line):** median over 100 seeded nights of
`(heat_loss_kw_per_c − UA_true)/UA_true` among runs the coordinator would
**adopt** (`completed and confidence >= 0.3`), against a house integrated by
RK4 with parameters *different from the finder's* — UA = 0.20 kW/K, C = 12.0
kWh/K, G = 0.30 kW, T_out = 8 °C, room started in steady state — and, unlike
the finder's plant, at a step whose predicted excursion the production comfort
sizer **accepts**.

The finder's metric is the same statistic on their own plant (UA 0.22, C 9.0,
G 0.35, T_out 2 °C, forward Euler, room 19 K above its own steady state).

```
RESULT V1_perturbation_row_white0.02_q5.4
  d=0.00: +0.0240   d=0.02: -0.0704   d=0.05: -0.2087   d=0.10: -0.4397   d=0.20: nan (0 completed)
RESULT V1_perturbation_monotone_in_magnitude = True
   adopted: 95/100, 95/100, 95/100, 90/100
```

**Headline (mine): `bias_UA_adopted = −0.2087` at d = 0.05 °C/h, σ = 0.02 °C
with 95 of 100 adopted, and −0.4397 at d = 0.10 °C/h with 90 of 100 adopted.**
The finder's figures on their plant are −0.1340 and −0.2454. **Same sign, same
monotone direction, 1.6–1.8× larger on mine.** The finding survives a plant
generated differently — different parameters, different integrator, different
outdoor temperature, different initial condition.

### Attribution — three counterfactual fits I wrote, on the same rows

| arm | what it is | result |
|---|---|---|
| production `identify()` | the shipped estimator | d=0.10, σ=0: **−0.0002**; σ=0.02: **−0.4397** |
| `OLS3` | my OLS on `[-ΔT, Q, 1]`, no drift column at all | d=0.10, σ=0: −0.4043 |
| `OLS4` | my OLS on all four columns, **no ridge, no EIV, no scaling** | drift_hat = d + 0.0939 at *every* d |
| `ORACLE` | true ramp subtracted first | σ=0: −0.0000 |

Read together these attribute the bias:

* **The safeguard genuinely works on clean data.** At d = 0.10, σ = 0 the
  production fit returns bias −0.0002 with `drift_hat = +0.1000` exactly, while
  the same rows with no drift column give −0.4043. The column buys 0.40 of bias
  when it can see.
* **The ridge is not the binding constraint** — confirmed by a route the finder
  did not take. My `OLS4` has *no* shrinkage prior at all, and its drift
  estimate is `0.0939, 0.1139, 0.1439, 0.1939, 0.2939` for true
  `0.00, 0.02, 0.05, 0.10, 0.20`: unit sensitivity to the true drift, with a
  constant ~0.094 °C/h of noise-induced error. The column tracks the drift
  one-for-one but its error is the same order as the drift being estimated. So
  the failure is an **identifiability limit of this experiment at this
  excursion**, not a bad prior — which is the finder's `--wide-drift-prior`
  conclusion, reached independently.
* Note that plain OLS is not a usable alternative at σ = 0.02: my `ORACLE`
  (3-column OLS, true ramp removed) reads **+3.16** — the errors-in-variables
  blow-up the production EIV correction exists to remove, and does remove
  (+0.024 at d = 0). The shipped pipeline is doing a great deal of correct work;
  the drift leak is what is left.

### New, and stronger than the finder: a realistic sensor

An "ordinary 0.1 °C-resolution sensor" is **quantised**, not white — its
quantisation noise is 0.1/√12 = 0.0289 °C, above the finder's σ = 0.02. The
finder never crossed drift with quantisation. I did:

```
RESULT BYPASS_q5.4_quant0.1_d0.0 : bias -> +0.0378  adopted 100/100
RESULT BYPASS_q5.4_quant0.1_d0.1 : bias -> -0.4309  adopted 100/100
RESULT BYPASS_q5.4_quant0.1_white0.02_d0.05 : bias -> -0.2429  adopted 75/100
```

A plain 0.1 °C sensor with a 0.10 °C/h ramp gives **−43 % UA with 100 of 100
adopted**.

### New: is it reachable through the state machine?

The finder appended to `sid.samples` directly and never touched `arm()`,
`conditions_met()`, `_size_step_power()` or `_over_excursion()`. I drove the
production state machine in closed loop:

```
RESULT CLOSED_maxP1.2_white0.02_d0.05 : aborted 0/40, completed 32, adopted 20, bias -0.2130
RESULT CLOSED_maxP1.2_white0.02_d0.10 : aborted 0/40, completed 28, adopted 27, bias -0.4501
RESULT CLOSED_maxP1.8_white0.02_d0.10 : aborted 39/40 ("room temperature drifted beyond the allowed excursion")
RESULT CLOSED_maxP2.4_white0.02_d0.05 : aborted 40/40
```

So at a modest step the biased fit **is reachable and is adopted** — 20–27 of 40
nights, at the same bias the bypass arm reports. At a larger step the drift
inflates the apparent excursion past 0.8 °C and `_over_excursion` aborts. Both
halves matter: the comfort guard is a partial mitigation at large steps and no
mitigation at all at small ones.

### A defect in the finder's instrument — their operating point is one the code refuses

Replaying `sysid_bias.py:plant()` and measuring it against the production
comfort machinery:

```
RESULT finder_plant_room_monotone_cooling_throughout = True
RESULT finder_plant_dT_over_step_phase_C = -0.1208      (the 3.2 kW "step" never reverses dT/dt)
RESULT finder_plant_max_abs_excursion_from_baseline_C = 1.2624   (bound 0.8)
RESULT finder_plant_would_trip_over_excursion_guard = True, first breach at elapsed 4.0 h (relax)
RESULT predict_step_excursion_of_finder_step(peak,final) = 0.9608,0.9608   (bound 0.8)
RESULT finder_house_feasible_step_kW_thermal_range = 3.98..7.51
RESULT finder_house_size_step_power_returns = 2.5033 kW electrical  (= 7.51 kW thermal)
RESULT finder_house_step_the_harness_used = 3.2 kW thermal
```

Their room starts 19 K above its own steady state and **cools monotonically
through settle, step and relax**; the 3.2 kW step is *below* the production
sizer's feasible band (3.98–7.51 kW thermal), so it only slows the cooling. The
excursion reaches 1.2624 °C against `max_excursion_c = 0.8`, `_over_excursion`
fires at 4.0 h, and `_size_step_power` — which would have chosen 7.51 kW
thermal — would never have selected 3.2 in the first place. **`identify()` is
never called on those rows in a real install.** The finder's specific numbers
are therefore taken at an operating point the code refuses. The *finding*
survives only because it reproduces, larger, at a legal operating point — which
is what my harness supplies. This is why step 2 of the verifier contract exists.

### Consequence, measured

The coordinator does not adopt the UA whole; `_adopt_system_identification`
blends by confidence. I measured the number it actually writes:

```
RESULT adopted_d0.00 : n=95 median_conf=0.503 bias -> +0.0240  blended house_heat_loss_scale = 1.0119
RESULT adopted_d0.05 : n=95 median_conf=0.637 bias -> -0.2087  blended house_heat_loss_scale = 0.8690
RESULT adopted_d0.10 : n=90 median_conf=0.765 bias -> -0.4397  blended house_heat_loss_scale = 0.6627
```

A single adopted night with a 0.10 °C/h drifting sensor writes
`house_heat_loss_scale = 0.663` — **the house modelled as losing 34 % less heat
than it does** — and it persists immediately (`_async_save_thermal_learning`).
Worse, **the median adopted confidence rises with the drift** (0.503 → 0.637 →
0.765): the drift inflates the ΔT range the confidence credits as
identifiability, and the D2-07 de-inflation (`deltas -= drift_hat · a[:,3]`) is
inert precisely because `drift_hat ≈ 0`. The more the sensor drifts, the more
the coordinator trusts the answer.

### Attacks run

* **Grid artefact?** No. Bootstrap over the headline cell's 95 adopted runs
  (2000 resamples): median 95 % CI **[−0.2176, −0.2025]**. `mean = −0.2123` vs
  `median = −0.2087`. Dropping the most favourable decile:
  **−0.2064**. The number does not rest on the aggregation rule or on any
  subset of cells.
* **Null control missing or failing?** Present and passing on both sides:
  my `d = 0, no sensor error` arm gives `−0.0000` in every one of the four
  fits; the finder's σ = 0 column is within 0.25 %. My **live positive control**
  (+20 % on the recorded thermal power) moves the production bias to exactly
  `+0.2000`, so the null is a real null.
* **Perturbation.** Runs under its own perturbation: raising `d` along the
  σ = 0.02 row gives `+0.0240, −0.0704, −0.2087, −0.4397`, monotone in
  magnitude (`V1_perturbation_monotone_in_magnitude = True`) and one-signed for
  d > 0. Not void.
* **Is the drift magnitude fair?** Yes — the production code sets the bar
  itself: `SysIdResult.sensor_drift_c_per_h`'s docstring names "a sensor ageing
  at 0.10 °C/h" as the case the column exists for, and `SysIdConfig`'s comment
  claims the 0.02 °C/h prior "more than halv[es] the adopted UA error at every
  noise level". Measured, at σ = 0.02 it halves nothing.
* **Severity earned by consequence?** Yes, at `high`. Against it:
  `SysIdConfig.enabled` defaults `False`, the experiment runs at most once every
  30 days, and the result is blended. For it: the blended write is 0.663 — a
  third of the house's heat loss gone in one night — it persists across
  restarts, the adoption gate *rewards* the drift rather than catching it, my
  quantised-sensor arm adopts 100 of 100, and the direction of harm is a house
  planned with too little heat, i.e. a silently missed comfort band. On
  Raspberry-Pi-class hardware there is no resource dimension; the consequence is
  entirely a wrong parameter. `high` stands.

**Vote: `verify`, severity `high`.** Executed number:
`bias_UA_adopted = −0.2087` (d = 0.05 °C/h, σ = 0.02 °C, 95/100 adopted,
bootstrap CI [−0.2176, −0.2025]) and `−0.4397` (d = 0.10 °C/h, 90/100 adopted),
on my own plant, with the closed-loop arm confirming reachability at
`−0.2130` / `−0.4501` and the consequence arm giving a written
`house_heat_loss_scale = 0.6627`.

---

## Summary

| id | vote | severity | my executed number |
|---|---|---|---|
| D2-01 | verify | medium (= finder) | inversion gap 0.19650 COP in the heating band; implied second-law efficiency falls 31.23 % from peak to +20 °C; control 0_of_7 |
| D2-02 | weaken | medium (finder: high) | 4 of 48 windows mis-billed per transition day, 2 free-but-billed; tracker disagrees with the plan in 4 of 48; 172 of 576 solve starts affected = 0.98 % of a year |
| D2-03 | verify | high (= finder) | −0.2087 at d=0.05/σ=0.02 (95/100 adopted, CI [−0.2176, −0.2025]); −0.4397 at d=0.10; blended `house_heat_loss_scale` = 0.6627 |

Two instrument defects to carry forward regardless of the votes: the stale
EXPECTED headers on `cop_monotonicity.py` and `dst_window_factors.py`, and
`sysid_bias.py`'s plant, which the production comfort guard would abort.
