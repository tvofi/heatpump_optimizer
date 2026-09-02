# D2 verifier seat 1 of 3 — round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` 3.13.1, numpy 2.5.2, scipy 1.18.1,
five BLAS thread variables pinned to 1 before any numpy import in every harness.
Apple M1, 8 GB, shared (load1 1.47–5.66 during these runs; `thread_factor`
1.000–1.002 in every run). **No RESULT below is a wall, CPU or RSS number** —
every one is a count, an exact parity, a residual, a ratio or a SEK/kWh figure —
so none needs the quiet window. I did not run `tests/run.sh` and did not take
`/tmp/hpo-gate.lock`.

My own harnesses live under `/tmp/verify-D2-1/`:
`d201_substep_identity.py`, `d201_consequence.py`, `d201_nonfinite.py`,
`d201_fix_probe.py` (+ the patched tree at `/tmp/verify-D2-1/patched/`),
`d202_cop_physics.py`, `d202b_plan.py`, `d202c_plan.py`,
`d203_grid_dt.py`, `d204_sysid_gate.py`, `d204b_signs.py`,
`d205_wood_reach.py`, `d205b_cross.py`.

Verdict summary: **D2-01 verify (high)** · **D2-02 verify (medium), fix scope
wrong** · **D2-03 verify (medium)** · **D2-04 weaken (low) — headline refuted**
· **D2-05 verify (low)**.

---

## D2-01 — batched single-zone simulation ignores the Euler sub-step

**Vote: verify (high).** Deciding number: the two-line production fix takes the
stiff single-zone parity from **2.54e74 °C to 0.0 exactly** while leaving all 49
golden configurations at **0.0** — the divergence is exactly this bug and the fix
is invisible to every committed fixture.

### Finder's harness, re-run

`PYTHONPATH=tests/hastub python tools/audit/round2/D2/parity_substeps.py`, all
five BLAS vars = 1, from the export root. Every number reproduced exactly:

```
parity_max_diff_golden        = 0.000e+00   (49 cells)
parity_max_diff_single_nsub1  = 0.000e+00
parity_max_diff_single_stiff  = 2.536e+74   min 5.283e+00, 1 non-finite cell
parity_max_diff_two_zone_stiff= 0.000e+00
solve_objective_gap           = 53.8845     cost 103.8091 vs 30.0832 SEK
grad_batch_vs_scipy_maxabs_stiff = 1.614e+83
thread_factor = 1.000   load1 = 3.25
```

### My metric (`d201_substep_identity.py`)

One line: *a bit-exact attribution identity* — I wrote two single-zone
integrators from the equations in `_simulate_step_single`, using the production
flux helpers (`compute_cop`, `effective_heat_loss_coefficient`,
`compute_solar_gain`) so the residual is attributable to the **integration
scheme alone**: `ref_correct` takes `n_sub` sub-steps of `dt_hours/n_sub`;
`ref_naive` takes `n_sub` sub-steps of `dt_hours` and re-seeds `T_room` from the
initial state on every sub-step of step 0 (the literal shape of
`thermal_model.py:2605-2606, 2636-2637`).

```
d201_batch_vs_naive_maxabs        = 0.000e+00 degC   (every cell, n_sub 1..3)
d201_batch_vs_correct_maxabs      = 2.599e+74 degC
d201_scalar_vs_correct_maxabs     = 0.000e+00 degC
d201_batch_effective_stability_ratio_max = 12.500  (constant is 1.500)
```

The batch is **bitwise my wrong integrator** and the scalar is **bitwise the
right one**. That kills the "different but legitimate discretisation" reading.
A third reference (`naive_noreseed`, wrong `dt` but no step-0 re-seed) differs
from the batch by 0.646 °C on the minimal cell, so the `T_room` re-seed is a
second, independent defect and not cosmetic.

Physical framing: the batch integrates at an effective ratio
`worst_coupling · n_sub · dt_hours` of up to **12.5**, against
`EULER_STABILITY_MAX_RATIO = 1.5` and the divergence threshold of 2 that
`thermal_model.py:136` names. The guard exists precisely to keep this below 1.5,
and the batch defeats it.

### Attacks

**1. Is `n_sub ≥ 2` reachable inside the config flow's own ranges?** Yes, with
**one field**. `config_flow.py:414-417`: `RANGE_SLAB_THERMAL_MASS = (0.1, 60.0)`,
`RANGE_SLAB_HEAT_TRANSFER = (0.02, 5.0)`; `THERMAL_MASS_FLOOR = 0.1`, so the
range minimum survives `ThermalParameters.clamp` untouched, and the hastub
`NumberSelector` (which mirrors HA's own `vol.Coerce(float)` + range check)
accepts it.

```
d201_nsub_one_field_off_default   = 2      (slab_thermal_mass = 0.1, everything else default)
d201_selector_grid_cells          = 6000
d201_selector_grid_nsub_ge2       = 58     (0.97 % of the two fields' own lattice)
```

**2. Does the questionnaire reach it?** No — and this is the one real narrowing.
Swept all 1320 `presets.BuildingPreset` combinations (structures × eras ×
foundations × emitters × 11 areas from 20 to 1000 m²):

```
d201_preset_configs   = 1320
d201_preset_max_nsub  = 1
```

`derive` gives a radiator house `slab_transfer/slab_mass ≤ 1.0` and a floor
house `≈ 0.010/(slow+0.045) ≪ 6`, so the guided path never subdivides. The live
path is the **expert page**, where a user typing the slab-mass field's own
documented minimum ("the radiator loop of a small house") lands in the bug.

**3. Any golden fixture with `n_sub ≥ 2`?** No.

```
d201_golden_scenarios = 49   d201_golden_single_zone = 35   d201_golden_max_nsub = 1
```

**4. Is the consequence earned at a *reachable* cell, not just the finder's
corner?** Yes — `d201_consequence.py`. My metric: both plans re-scored on the
**scalar (correct) model of record**, so the number is real SEK, not two
objectives from two models. `res.objective_value` is already the scalar
objective of the returned schedule, so it too is a same-model comparison.

| cell | objective batch/scalar jac | true cost (SEK/day) | energy (kWh) |
|---|---|---|---|
| null: default house | 60.1043 / 60.1043 | 23.2800 / 23.2800, Δ **0.0000** | 36.00 / 36.00, L1 **0.0000** |
| **slab_mass 0.1 only** | 104.2048 / 55.1476 | 100.7914 / 30.9385, Δ **+69.8529** | 62.66 / 40.77, L1 76.78 |
| finder's 0.5 / 5.0 | 108.5030 / 54.6186 | 103.8091 / 30.0832, Δ +73.7259 | 62.04 / 40.10, L1 82.35 |

At the minimally reachable cell the batched-jacobian plan costs **3.26×** what
scipy's own scalar FD plan costs on the same model, and burns 54 % more
electricity. The null control is 0.0000 on every column.

**5. Does it fail loudly?** No — worse. At `slab 0.1 / k 5.0` (`n_sub = 9`,
parity `inf`) the solve still returns `status=optimal`, objective 109.19,
cost 105.11 SEK against 55.09 / 31.11 on the scalar path. Silent.

**6. Is the batched jac actually used?** `_bounds_supported_by_batch` rejects
only zero-range bounds; every ordinary solve takes the batched path
(`optimizer.py:314-325`), and its docstring claims bit-identity with scipy.

**7. The test gap, with the killing production mutation named.** The single
killing edit is in a **production** file:
`custom_components/heatpump_optimizer/thermal_model.py:2636-2637`, `* dt_hours`
→ `* dt` (plus `if i == 0` → `if i == 0 and _sub == 0` at :2605). Applied to a
copied tree (`/tmp/verify-D2-1/patched/`) and re-measured (`d201_fix_probe.py`):

```
                       baseline                       patched
slab0.1_k0.8 (n_sub 2) 37.87966429250174        ->    0.0
slab0.2_k1.5 (n_sub 2) 5.283487676097124        ->    0.0
slab0.5_k5.0 (n_sub 2) 1.2698194086957931e+20   ->    0.0
slab0.3_k5.0 (n_sub 3) 2.535594550527266e+74    ->    0.0
golden_max (49 configs) 0.0                     ->    0.0
```

`tests/features.py:1947-1978` confirms why: the only `_grad_parity` cell labelled
`"stability substeps"` is `two_zone=True`, every single-zone cell runs default
masses, and `tests/features.py:11430-11436` asserts the opposite ("no sane
configuration ever subdivides a step") for the defaults only.

Severity: reachable with one in-range field, silent, 3.3× cost, can go
non-finite, no fixture covers it, and it defeats a guard written for exactly
this. **high is earned.**

---

## D2-02 — with a valve, COP falls as outdoor temperature rises

**Vote: verify (medium)** — with two corrections the judge should carry:
the finder's stated fix is a **no-op**, and 4 of 9 plan cells show **zero**
movement when the turnover is isolated.

### Finder's harness, re-run

`cop_monotone.py` reproduced exactly: `cop_flow_cells_nonmonotone = 7/7`,
`cop_ratio_20_over_peak_min = 0.8874`, `carnot_fraction 0.165–0.328`,
`marginal_cop_buffer60` 1.8210 / 1.9608 / **2.0339 (10 °C)** / 2.0181 /
**1.8802 (20 °C)**, sign changes 1, DHW violations 0. `thread_factor 1.000`.

### My metric (`d202_cop_physics.py`)

One line: *the worst `dCOP/dT_out` at a fixed flow temperature, and the fraction
of the (flow, outdoor) grid where it is negative* — a heat pump at a fixed flow
delivers into a shrinking lift as outdoor rises, so this derivative cannot be
negative.

```
d202_min_dcop_dtout        = -0.26025 per_K     (flow 40 °C)
d202_negative_slope_cells  = 510 of 1540        (7 flows x [-25, 30] °C at 0.25 K)
d202_negative_slope_fraction = 0.3312
peaks: 21.00 / 17.00 / 14.75 / 13.00 / 11.75 / 10.75 / 10.00 °C for F = 40..70
d202_cop_flow_carnot_from_config = 1   d202_throttling_modes_of_four = 3
```

**Physically wrong, not a modelling choice.** Carnot COP at a fixed flow is
monotonically increasing in `T_out`; every real air-to-water unit at a fixed
60 °C flow does better at 20 °C than at 10 °C. The artefact comes from
normalising by `carnot_ref` at a 35 °C reference: as `T_out → T_ref`, `T_ref −
T_out` collapses, so the base curve's implied η falls ≈ 2.3 %/K locally
(η(10) = 0.305 → η(20) = 0.226) while the flow Carnot gains only ≈ 2.0 %/K.
Reachable by configuration alone: `thermal_model.py:868` sets
`cop_flow_carnot = True` for **3 of the 4** valve modes.

### Attacks

**1. The finder's proposed fix does not fix it.** The report suggests
"η = COP_ref·(T_ref−T_out)/T_ref at the reference, then COP(F) = η·T_F/(T_F−T_out)".
Algebraically that is `COP_ref · carnot_flow/carnot_ref` — the current code.
Executed as a control column in my harness: identical COP values and identical
worst slopes at flows 40/45/50 (`cop10` 3.1863 / 2.7747 / 2.4660;
`min_slope` −0.26025 / −0.23696 / −0.20391 in both columns), differing at
55–70 only because production's `max(0.25, …)` clamp binds there —
`d202_negative_slope_cells_eta_consistent = 559`, i.e. **worse**, not fixed.
The fix has to change the base curve or bound the ratio; re-deriving the same
ratio cannot.

**2. Does the turnover change a plan?** I isolated it: `compute_cop` replaced by
its **monotone hull in outdoor temperature** (bit-identical below each flow's
peak, differs only above it), so any plan move is attributable to the turnover
alone — unlike the finder's `cop_flow_carnot=False`, which moves the COP
everywhere. Valve + 750 L buffer + `buffer_max 70`, tank at 55 °C:

| cell | schedule L1 (kWh) | cost delta (SEK) |
|---|---|---|
| winter_cold | 0.0000 | 0.0000 |
| shoulder (out_max 11 °C) | 0.0000 | 0.0000 |
| summer_warm (out_max 25 °C, plan is 0 kWh) | 0.0000 | 0.0000 |
| summer_cool, winter_typical prices | 0.0000 | 0.0000 |
| summer_cool, **flat prices** (null control) | **2.8364** | **+3.4036** |
| summer_cool, winter_extreme prices | 2.8364 | +3.4036 |
| summer_cool, summer_negative prices | 0.1321 | +0.0396 |
| summer_cool, extreme + valve target 21 | 4.4231 | −1.0083 |

The flat-price cell is the honest one: with nothing to arbitrage, removing the
turnover still moves the plan by 2.84 kWh L1 and 3.40 SEK on a 7.49 kWh day
(production buys **61 % more** electricity for the same task), so the movement
is COP-driven, not price-driven. But the direction is not systematic (the
valve-target cell reverses sign) and the whole effect lives above ~11 °C
outdoor, where space heating barely runs.

**3. A metric of mine that I am voiding.** I first measured "electricity per kWh
stored in the buffer" through `simulate_trajectory` at 10 vs 20 °C
(`d202_elec_per_stored_ratio_20_over_10 = 0.6276`). It is confounded — at 10 °C
the house draws more heat out of the tank than at 20 °C, so the ratio measures
demand, not COP. It does not support the finding and I am not counting it.

Severity: the defect is real, on by default for any valve user, and propagates
into `marginal_cop`, which prices storage in `_terminal_cost` and
`_deferred_energy_cost`. Against that, half my plan cells do not move and the
band is a shoulder/summer edge. **medium, at the low end of medium.**

---

## D2-03 — the planning grid steps wall-clock time on DST days

**Vote: verify (medium).** Deciding number: on all six transition days the grid
is internally contradictory — `span_error = ±1.0000 h` and one step whose real
duration is **1.25 h** (autumn) or **−0.75 h** (spring), against the `dt = 0.25 h`
every consumer integrates with. Plain day: 0.

### Finder's harness, re-run

`dst_grid.py` reproduced exactly: six transition cells all
`steps_misaligned = 84`, spring `distinct_instants = 92`, `span 23.00 h`,
`plan_phantom_kwh = 6.000` of `total 29.960`; autumn `span 25.00 h`,
`max_gap 75 min` at 6.000 kW; `dst_null_control_plain = 0`. `thread_factor 1.000`.

### My metric (`d203_grid_dt.py`)

One line: *the number of steps whose real elapsed duration is not the 0.25 h the
simulation integrates with, and the horizon's real span minus 24 h* — a
contradiction inside the production grid that needs no choice of time
convention. `step_starts` is captured from the real `_price_series` call by
wrapping `_known_prices_for`; the price array is the one `_forecast_arrays`
returns.

```
                    dt_mismatch  min_dur   max_dur   span_err   price_shift
plain_null (2026-08-26)   0      0.2500 h  0.2500 h  +0.0000 h      0
spring 2025/2026/2027     1     -0.7500 h  0.2500 h  -1.0000 h     84
autumn 2025/2026/2027     1      0.2500 h  1.2500 h  +1.0000 h     84
d203_transition_cells = 6, price_shift min = max = drop-most-favourable = 84
d203_energy_error_kwh = 1.2483 (span error x the 29.96 kWh/day the solver books)
```

On spring days the grid is **not monotone in real time**: one step starts
45 real minutes *before* its predecessor. No convention makes that right.

My price recount is independent of the finder's construction — a direct linear
interval scan over the seeded Tibber entries, compared against the array
`_forecast_arrays` actually returns — and lands on the same **84** on all six
days, from a different method.

### Attacks

**1. Why does `tests/dst_checks.py` pass?** Read in full. It checks two things
and neither is this one: (a) the quarter snap and step-0 price **through the
coordinator on a plain day** (`FROZEN = 2026-08-26 12:07:33`, one assertion,
`result.prices[0] == 12.0`); (b) `_window_slot`, `PeakTracker` and
`window_factors` — the **tariff metering** path — on both transitions, minute by
minute, with a genuine UTC walk. `_price_series`, `_weather_series`,
`_forecast_arrays` and `_Horizon.timestamps` are never exercised on a DST day.
The suite is right about what it tests; the plan grid is not in it.

**2. Is it a stub artefact?** No. `dt_util.now()` returns aware local time in
real HA; `now.replace(hour=0, …)` gives local midnight with the same `ZoneInfo`;
`+ timedelta` is wall arithmetic by Python's own definition. Live for every
install in a DST zone, twice a year. I also confirmed
`_Horizon.timestamps`/`step_datetimes` build labels identically
(`horizon_labels_identical = True` on all seven days), so this is one grid with
one defect, not two.

**3. Is 84 a grid artefact of the anchor?** Drop-most-favourable over the six
cells is 84; the plain-day null is 0 on every column.

Severity: real, live, silent, but bounded — two days a year, ~1 h of
misalignment, and the plan is re-solved every 30 minutes. **medium is fair.**

---

## D2-04 — sysid confidence cannot reach its 0.3 gate; a drifting sensor passes biased

**Vote: weaken (low).** Both headline claims fail on my numbers. Deciding
number: at the default 30-minute interval, with the production row count of 7,
an outdoor temperature drifting 1 K/h gives **confidence 0.3500, adopted in
60/60 seeds, with UA bias +0.0000** — the gate is reachable, and where it is
reached the fit is correct.

### Finder's harness, re-run

`sysid_bias.py` was re-run; I do not dispute its clean-data figure, which my own
route reproduces in shape (see below).

### My metric (`d204_sysid_gate.py`, `d204b_signs.py`)

One line: *`identify().confidence` and the UA/τ bias against an exact
first-order room I integrate myself, plus the confidence ceiling derived from
the production row count rather than assumed*. Two routes: (A) build the STEP
and RELAX `SysIdSample` records from `C dT/dt = Q + G − UA(T − T_out)` with
C = 8 kWh/K, UA = 0.20 kW/K, G = 0.30 kW and the production phase durations;
(B) drive the real `SystemIdentification.step` state machine end to end.

**The row count.** Route B (the production state machine) yields
`d204_routeB_p3_rows = 7` at 30 min — the finder's 7, confirmed by driving the
real object rather than assuming it. `min(1, 7/20) = 0.35`.

**The ceiling, and where the finder's arithmetic goes wrong.** The code is
`confidence = clip(r²,0,1) · min(1, rows/20) · clip(excursion/2, 0.3, 1.0)` with
`deltas = -a[:,0] = T_room − T_out`. The 0.8 K comfort abort bounds the **room**
excursion at 1.6 K; it does **not** bound `T_room − T_out`, because the outdoor
temperature is free to drift over the 5-hour experiment. So:

```
d204_ceiling_room_only_30min = 0.2800   (finder's number — correct only if T_out is constant)
d204_ceiling_exc_ge_2K_30min = 0.3500   >= the 0.30 gate
```

**Measured, not just argued** (`d204b_signs.py`, production row count 7,
60 seeds per cell):

| cell (30 min) | confidence | excursion | adopted | UA bias |
|---|---|---|---|---|
| clean, q = 1.6 kW | 0.1050 | 1.29 K | 0.000 | −0.0000 |
| clean, q = 0.8 kW | 0.1880 | 1.28 K | 0.000 | −0.0000 |
| clean, q = 3.2 kW | 0.1050 | — | 0.000 | +0.0000 |
| **outdoor drift −1.0 K/h** | **0.3500** | 2.28 K | **1.000** | **+0.0000** |
| **outdoor drift +1.0 K/h** | **0.3500** | 4.46 K | **1.000** | **−0.0000** |
| outdoor drift −0.5 K/h | 0.1050 | 0.60 K | 0.000 | +0.0000 |
| sensor drift +0.10 K/h | 0.1050 | 0.74 K | **0.000** | +0.1432 |
| sensor drift −0.10 / −0.15 / −0.25 K/h | 0.0000 | — | **0.000** | fit rejected |
| sensor drift −0.15, q = 3.2 kW | 0.0000 | — | **0.000** | fit rejected |

1. **"Cannot reach the 0.3 gate at the default interval" — refuted.** 0.3500,
   adopted 60/60, at an outdoor drift of 1 K/h, which is an ordinary clear
   night. The ceiling is 0.35, not 0.28.
2. **"A drifting sensor passes it biased" — not reproduced.** Across 11 cells ×
   60 seeds, no sensor-drift cell cleared the gate: +0.10 K/h scores 0.1050
   (biased UA +14.3 %, but **never adopted**), and negative drift makes
   `identify` reject the fit outright. Every cell that *was* adopted carried
   UA bias 0.0000. The finder's 0.304 / 0.341 depends on their step size and
   drift sign; I could not obtain it with the production row count.

**What survives.** The row normalisation is genuinely mis-scaled: the formula
divides by 20 rows, and the default 30-minute interval with `step_hours = 2` +
`relax_hours = 2` can only ever produce 7. Clean, noise-free data at the default
interval scores 0.105–0.188 and is discarded (`d204_routeB_p3_confidence =
0.1359` end-to-end through the real state machine). That is a real design
defect, but it *withholds* a good result rather than adopting a bad one — it
cannot produce a wrong plan. **low.**

**One extra fact, unclaimed by the finder and worth a lead:** driven end to end
on my room inside the gate's own outdoor band, the experiment **aborts on the
comfort bound before completing** at the default 6 kW nameplate
(`d204_routeB_p6_phase_is_done = 0`, `rows = 3`,
reason `'room temperature drifted beyond the allowed excursion'`) and at 12 kW
(`rows = 2`). The step is `0.6 × max_power_kw` and is not sized against
`max_excursion_c`. Not a D2-04 number; a separate lead.

---

## D2-05 — `wood_share` is discontinuous at the flow curve

**Vote: verify (low).** Deciding number: on the committed `wood_two_tank`
config in an ordinary end-of-burn state, a **1e-6 K** change in the wood tank
temperature changes the wood tank after one 15-minute step by **3.671163 °C** —
but the trajectories reconverge to **5.5e-05 °C** after 96 steps, and in the
fixtures' own solves the state never comes within **1.33 K** of the cliff.

### Finder's harness, re-run

`model_sanity.py` reproduced exactly: `wood_share_max_jump = 1.0000`,
`jump_cells = 21`, `drop_most_favourable = 0.9500`,
`wood_share_times_drawn_jump = 13.4400 kW`, `wood_share_vec_parity = 0.000e+00`.

Reading confirms the shape: region 3 → region 1 at `wood_temp = flow_set` for
`hp_temp ∈ (flow_set − margin, flow_set]`, jump `1 − (flow_set − hp)/margin`,
`WOOD_TANK_MIN_MARGIN = 2.0`. The other two boundaries (1↔2 and 2↔3) I checked
algebraically and they are continuous, so the docstring's "continuous in
`w·Q_draw` across every boundary" is false at exactly one of the three.

### My metric (`d205_wood_reach.py`, `d205b_cross.py`)

One line: *reachability from the solver's own call arguments* — `wood_share` and
`_wood_share_vec` wrapped (module-attribute swap, `try/finally`) so every
`(wood_temp, hp_temp, flow_set)` triple a real `optimize()` passes is recorded,
then classified against the discontinuous band.

```
                      calls      in_band   near cliff (<=0.5 K)   min dist to cliff
wood_two_tank         847,680     31,816            0                4.5472 K
wood_two_tank_smart_write 1,968,096 57,914          0                1.3279 K
wood_coil             2,004,960    40,841           0                4.5472 K
max jump at a real call: 0.9955 / 0.9995 / 0.9896
real 96-step trajectories: in_band 49 of 96 steps, crossings_in_band = 0
```

So in the fixtures the hp band is entered constantly (2–3.8 % of 4.8 M calls)
but the wood tank never approaches the cliff. **Reachability then tested
directly** with an ordinary state on the same production config (wood tank at
the curve, HP tank 0–2 K below it — the end of a burn):

| initial hp | crossings in horizon | theoretical jump | wood tank after 1 step | after 96 steps |
|---|---|---|---|---|
| flow_set | 0 | 1.0000 | **3.671163 K** | 0.000055 K |
| flow_set − 0.5 | 0 | 0.7500 | 2.753374 K | 0.000039 K |
| flow_set − 1.0 | 0 | 0.5000 | 1.835583 K | 0.000008 K |
| flow_set − 1.5 | **2** | 0.2500 | 0.917792 K | 0.000012 K |
| flow_set − 1.9 | **2** | 0.0500 | 0.183560 K | 0.000060 K |

The cliff is reachable with a production configuration and an ordinary state,
and real crossings occur inside a 24-hour horizon. But the consequence is a
transient reallocation *between* the tanks: the emitters receive the same heat
whenever both tanks have availability, and the trajectories reconverge to 1e-5 °C
by the end of the horizon. **low is right.**

---

## Method notes and what I did not do

- Every number above came from a run I executed on this box today; nothing is
  quoted from the finder without re-running it.
- No `tests/run.sh`, no `/tmp/hpo-gate.lock`, no `env_drift.py`, no `docs/`
  read, no other verifier's output read.
- The only file I wrote inside the export is this one.
- Not settled, and worth the judge's attention: whether D2-02's turnover matters
  once a *correct* base curve is in place (my monotone hull is a probe, not a
  fix), and whether D2-04's sensor-drift half reproduces under the finder's own
  room and step size — my sweep says no, but the disagreement is in the setup,
  not in the arithmetic, so it is worth one re-take.
