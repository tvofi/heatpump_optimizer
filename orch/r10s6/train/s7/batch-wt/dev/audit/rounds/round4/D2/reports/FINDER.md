# D2 — Mathematical and physical sanity — round 4

- **Baseline** `7dd68dd327fe3dbfb09f3bd0fe38910c58877697` (read-only export,
  no `.git`).
- **Machine** 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy
  2.4.6 on OpenBLAS. Interpreter
  `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, every run
  from the export root with `PYTHONPATH=tests/hastub` and the five-variable
  BLAS thread pin. `thread_factor` 0.9948–1.0038 on every committed run (contract: <= 1.05).
- **Contention** the box carried nine other finders. `load1` 4.2–14.3 across the session, 13.8–14.3 on the
  committed `.out` runs, and is quoted beside every RESULT. **Every number in this
  report is a count, a ratio or a closed-form float identity — none is a
  timing or a memory figure**, so none of them is provisional on the quiet
  window.
- **Exposure** none. I read no `docs/audit-*.md`, no `docs/backlog.md`, no
  `docs/plan-*.md`, ran no `gh`, opened no GitHub. Production comments in
  `thermal_model.py` and `sysid.py` cite earlier `D<k>-nn` ids; per
  `COMMON.md` I read those as context and did not chase them.
- **Concurrency** `concurrent_processes = 2` on every run (this harness
  plus its `grep`); no `tests/stress.py` and no `tests/run.sh` ran beside
  them, and I took no gate lock (nothing here selects `MODE: FULL` or
  `stress.py`).
- **Harnesses** `tools/audit/round4/D2/`. Each carries its metric
  definition, exact command, expected value ± tolerance, baseline SHA,
  machine, instrumented symbols, perturbation and null control in its own
  header, and each executes its perturbation in-process so the direction is
  measured rather than asserted. `_d2common.py` is shared RESULT/footer
  boilerplate, not a harness. `*.out` are the runs this report quotes.

## Method

I drove production symbols directly and checked identities, not code
readings: per-step energy conservation, monotonicity in power, COP
monotonicity and bounds, the explicit-Euler truncation at the production
step, the PV-piecewise cost closure, the metering-window box average, the
marginal capacity price, the DHW coil identity, the wood-share range and its
batched twin, and the derate clamps. Where an identity failed I swept the
operating envelope to find where it is worst, and built the null control that
makes the effect vanish.

I did not re-audit batch/scalar trajectory parity: `tests/features.py`
(`_grad_parity`, 13 cells) already pins it bitwise and adds the
`_batch_fd_gradient`-vs-`approx_derivative` contract. Re-measuring it would
have been re-running a gate.

## Findings

Ids are `D2-01` … `D2-05` because `tools/audit/finding.schema.json` requires
`^D<k>-[0-9]{2}$`. They are round-local and **collide by construction** with
the `D2-01` / `D2-07` ids that earlier rounds left in production comments;
cite them as *round 4* `D2-0n`.

### D2-01 — the capacity-tariff penalty charges up to 13× the bill it approximates (high)

`tariff._smooth_topk_sum` bisects a logistic threshold on the bracket
`[min(x)-1, max(x)+1]` with temperature `scale = 0.05*max(x)`. The root sits
at `peak + scale*ln((n-k)/k)`, so once `0.05*peak*ln((n-k)/k) > 1` it is
**outside** the bracket; the 64 bisection steps converge to the bracket end,
every window keeps weight ≈ `sigmoid(-1/scale)`, and the returned sum is far
above `k*peak`. The docstring's contract — "when many windows tie, each gets
weight k/n and the approximate sum stays k × tie_level" — does not hold.

The smooth branch is taken whenever more than `k` metering windows sit within
`_PEAK_TIE_BAND` (1e-3 kW) of the largest excess: a flat plan, which is what
a capacity tariff exists to produce, and what a solver saturated at `p_max`
through a cold spell produces on its own.

- `ratio_catalog_6kw = 1.102246261`, `ratio_catalog_9kw = 3.128723195`,
  `ratio_worst = 5.083811356` (96 fifteen-minute windows, k=3).
- `break_excess_kw_1pc = 5.841609 kW` — above that flat excess the term is
  overstated by more than 1 %. **All four shipped DSO catalog rows set
  `peak_tariff_window_minutes = 15`**, which is the worst case: at hourly
  metering (24 windows) the break point is ~10.3 kW.
- Grid sweep, 28 cells over (24, 48, 96, 192) windows × (2…15) kW excess:
  `cells_over_1pc = 16`, `cell_ratio_min = 0.99999973`,
  `cell_ratio_max = 13.35`, mean 2.902, **leave-one-out mean with the worst
  cell (192 windows, 15 kW) dropped = 2.515**.
- Money, through the Ellevio catalog row (81.25 SEK/kW, k=3, 15-min):
  charged 4956.72 SEK vs billed 975.00 SEK at 12 kW flat excess
  (`phantom_sek_12kw = 3981.72`); 2287.88 vs 731.25 at 9 kW; 537.35 vs
  487.50 at 6 kW.
- **Null controls.** `ratio_null_flat_5kw = 1.000000062` and
  `ratio_null_hourly_8kw = 0.99999973` — below the break point the
  approximation is exact. `ratio_null_spiky_12kw = 1.0` exactly — a plan with
  at most k windows at the peak never enters the smooth branch at all,
  whatever the excess. The effect is the bracket, not the top-k sum.
- **Perturbation, executed.** Widening the bracket to
  `peak + 1.0 + 40*scale` (and the symmetric low end):
  `perturbed_ratio_worst = 1.00000032`, `perturbed_cells_over_1pc = 0`.

Consequence: with a peak tariff enabled the objective's capacity term is
inflated by a factor that grows with the plan's own excess, so the plan is
far more peak-shy than the bill justifies — and because the term jumps when a
(k+1)-th window joins the peak plateau, the objective actively rewards a
spiky profile over the flat one the tariff is supposed to buy. It bites
hardest early in a month, when `PeakTracker.threshold_kw` is the lowest peak
seen rather than a realistic one, which is exactly when the excess is large.

Files: `custom_components/heatpump_optimizer/tariff.py`.
Harness: `peak_topk_bracket.py`.

### D2-02 — every shipped DSO catalog row writes two masks that provably change nothing (medium)

`grid_fee.apply_catalog` writes `peak_tariff_hours` and
`peak_tariff_weekdays_only` for all four rows and never writes
`peak_tariff_offpeak_factor`, whose default is 1.0.
`tariff.mask_active` states the gate in one line: an hours/weekday mask "can
change what a window counts at" only when `offpeak_factor < 1.0`. So the two
masks are inert as shipped. The month mask is not — it maps to factor 0.0 and
does bite, which is what makes this a gap in two of three masks and not a
dead feature.

Driven through the real builder
`coordinator.HeatPumpOptimizerCoordinator._capacity_tariff`:

| row | discounted windows | declared off-peak | offpeak_factor |
|---|---|---|---|
| ellevio_villa_effekt_2026 | 0 of 672 | 432 | 1.0 |
| vattenfall_eldistribution_effekt_2026 | 0 of 672 | 432 | 1.0 |
| eon_energidistribution_effekt_2026 | 0 of 672 | 412 | 1.0 |
| goteborg_energi_effekt_2026 | 0 of 672 | 432 | 1.0 |

- Money: a 4-hour 5 kW excess placed at 00:00 on the Saturday of that January
  week — inside both the night window and the weekend the Ellevio row
  declares off-peak — is charged `ellevio.phantom_peak_sek = 406.25 SEK`.
- **Null control.** `july_factor_unique = [0.]` for the three Nov–Mar rows
  and `[1.]` for the Jan–Dec row: the month mask, written by the same call,
  does move the factor. A harness that could not tell an inert mask from a
  live one would report the same for both.
- **Perturbation, executed.** Adding
  `CONF_PEAK_TARIFF_OFFPEAK_FACTOR: 0.0` to the dict `apply_catalog` returns
  (one line): `discounted_windows` rises 0 → 432/432/412/432 and
  `ellevio.phantom_peak_sek` falls 406.25 → 0.00.

Consequence: a user who selects their DSO from the catalog sees
"07:00–19:00, weekdays only" in the options and gets a plan that defends
night and weekend peaks at the full rate. I am claiming the internal
contradiction — a config that declares a mask the code proves inert — not a
reading of any DSO's published tariff, which I did not consult.

Files: `custom_components/heatpump_optimizer/grid_fee.py`,
`custom_components/heatpump_optimizer/tariff.py`.
Harness: `catalog_masks.py`.

### D2-03 — the 4-way valve law is discontinuous where its docstring says it is continuous (high)

`thermal_model.wood_share` documents "Three regions, continuous in
`w * Q_draw` across every boundary". At `hp_temp == flow_set` it is not.
Region 2 gives `f_w = (hp_temp - flow_set)/(hp_temp - wood_temp) → 0` from
above; region 3 gives `max(wood-hp, wood-flow+margin)/margin →
1 - (flow_set - wood_temp)/margin` from below, which is 0 only when the wood
tank is a full `WOOD_TANK_MIN_MARGIN` (2.0 °C) below the curve.

Measured at `flow_set = 26.6 °C` (the curve this configuration's own
`mixing_valve.flow_setpoint` produces at −5 °C outdoor), moving the
**heat-pump** tank by 2e-6 °C across the curve with the wood tank held fixed:

| wood tank below curve | share jump |
|---|---|
| 0.001 °C | 0.9985 |
| 0.25 °C | 0.8750 |
| 1.0 °C | 0.5000 |
| 1.999 °C | 0.0005 |
| 2.0 °C (= margin) | −3.2e-07 |

- In energy, through `ThermalModel.simulate_step` on the `two_tank_4way`
  topology: the wood tank's one-step (15 min) enthalpy change goes from
  −0.6470 kWh to −0.0053 kWh, `wood_energy_jump_kwh = −0.6417`, which is
  **99.2 % of the discharge**.
- Driven by the solver's own decision variable, through
  `ThermalModel.simulate_trajectory`: step-0 electrical power moves the HP
  tank across the curve, and **one float ulp** of that power
  (`traj_power_gap_kw = 2.78e-17`) changes the wood tank's step-1 enthalpy
  change from −1.1161 kWh to −0.0060 kWh, `traj_wood_jump_kwh = −1.1101`.
  The objective is therefore genuinely discontinuous in the variable
  L-BFGS-B differentiates, not merely in a diagnostic.
- The batched twin carries the identical jump
  (`share_jump_vec_at_0.25C = 0.8750`), so the finite-difference gradient
  sees it too.
- **Direction is backwards against the documented priority law.** The
  docstring's law is "wood-while-usable … *not* hotter-tank-first"; measured,
  the wood tank is abandoned precisely because the heat pump's own tank got
  hotter.
- **Null controls.** `share_jump_null_at_2C = −3.2e-07` (a full margin below
  the curve, region 3 already returns 0) and `share_jump_null_above = 0`
  exactly (wood at or above the curve is region 1 on both sides).
- **Perturbation, executed.** Fading region 3 out with
  `min(1, max(0, (flow_set - hp_temp)/margin))`:
  `perturbed_share_jump_worst = 0.000998` (the residue is the 2e-6 °C probe
  itself) and `perturbed_wood_energy_jump_kwh = 7.3e-07`.

Consequence: `wood_share` is, by its own docstring, shared verbatim with the
savings baseline, so the reported wood displacement jumps with it. The
topology is the `two_tank_4way` layout (`two_zone` + throttling valve + a
configured wood probe), and an HP tank crossing the curve temperature is the
ordinary charging cycle, not a corner.

Files: `custom_components/heatpump_optimizer/thermal_model.py`.
Harness: `wood_share_jump.py`.

### D2-04 — the modelled COP goes below 1.0, and inverts, over a reachable envelope (medium)

`compute_cop` floors the nameplate curve at `max(0.3, …)`, which keeps it at
`3.5 × 0.3 = 1.05` — deliberately above unity. It then multiplies by the
defrost derate and by the Carnot flow ratio, and `compute_cop_dhw`
multiplies the same base by `max(0.5, 1 - 0.008*(T_dhw - 35))`. The final
clamp is `max(cop, 0.5)`. The product crosses 1.0 and the clamp does not stop
it. `cop_flow_carnot` is not exotic: `ThermalParameters.from_config` sets it
to `mixing_valve.is_throttling(mode)`, so every valved install has it on, and
`compute_cop_dhw` has no gate at all.

- Space, over outdoor −25…+15 °C × flow 35…`buffer_max_temp` (70 °C), 328
  cells: `min_cop = 0.71954` at outdoor −21, flow 70;
  `cells_below_unity = 51`; **44 with the coldest outdoor column dropped**.
  Unity is crossed at outdoor −19.91 / −18.24 / −16.52 °C for flow
  45 / 55 / 65.
- DHW, over outdoor −25…+15 °C × tank 40…`dhw_hard_max_temp` (60 °C), 205
  cells: `min_cop = 0.84`; `cells_below_unity = 23` (19 leave-one-out);
  unity crossed at outdoor −19.39 °C at the 55 °C default setpoint.
- It reaches the money, not only the simulation:
  `marginal_cop(-25, "buffer", 70) = 0.73848` and
  `marginal_cop(-25, "dhw", 60) = 0.84` — the symbol `_terminal_cost` and the
  settlement price call.
- **Second consequence of the same mechanism: the COP inverts.** Below
  −21 °C the nameplate factor is pinned by its own floor while the Carnot
  ratio keeps falling as outdoor rises, so the product falls with rising
  outdoor temperature. Band `−40 … −21 °C` at every flow; the drop from
  −30 °C to −21 °C is 2.10 / 3.64 / 4.83 / 5.33 % at flow 45 / 55 / 65 / 70.
  The model says the pump gets worse as the weather warms.
- **Null controls.** With the Carnot term off (`mixing_valve_mode: none`) the
  same grid gives `min_cop = 1.05` and `cells_below_unity = 0`, and
  `worst_step_vs_outdoor = 0.0` — monotone. At the DHW penalty's own
  reference temperature (35 °C) `min_cop = 1.05`. The base curve alone never
  misbehaves; the metric is measuring the post-floor corrections.
- **Perturbation, executed.** Raising `cop_nominal` (CONF_HEAT_PUMP_COP_NOMINAL):
  `cells_below_unity` 51 → 28 → 11 → 2 → 0 at 3.5 / 4.0 / 4.5 / 4.8 / 5.0,
  and `min_cop` 0.71954 → 1.02792. The one-line production alternative is
  `max(cop, 0.5)` → `max(cop, 1.0)`.

A COP below 1 says the unit delivers less heat than the electricity it is
charged for — below a resistive element, and below the Carnot bound of any
vapour-compression cycle, whose `T_hot/(T_hot − T_cold)` is 3.98 at
−20 °C/65 °C. Consequence: in deep cold the plan under-values heating and
prices stored heat back at a COP no machine has.

Files: `custom_components/heatpump_optimizer/thermal_model.py`.
Harness: `cop_below_unity.py`.

### D2-05 — the grid-fee rate's decimal-comma support is unreachable (low)

`grid_fee._parse_rule` converts a decimal comma
(`rate_token.strip().replace(",", ".")`), but `parse_rules` has already split
the whole specification on that same comma, so the conversion can only ever
see a token with no comma in it. Every decimal-comma fee specification is
refused, in a module that deliberately spells "maj", "okt", "lör" and "sön".

- `specs_rejected = 6 of 6`; the same six with a decimal point all parse
  (`dotted_equivalents_ok = 6`, the **null control**).
  `spec_problem` returns `invalid_grid_fee_rules`.
- `_parse_rule("= 0,45")` on its own returns `rate = 0.45`
  (`unit_accepts_comma = 1`) — the dead code proven dead.
- The first fragment of a split comma rate parses to `rate = 0.0`, so the
  split is not merely a rejection: `"Nov-Mar 06:00-22:00 = 0,27"` would have
  become a silent zero fee had its second fragment parsed.
- `GridFeeSchedule.from_config` degrades a rejected spec to no rules at all:
  `schedule_rules_after_reject = 0`, `schedule_fee_after_reject = 0.0` with
  only a log line, so a hand-edited or migrated store carrying a comma
  prices the plan with zero grid fee.
- **Perturbation, executed.** Splitting on `;` and newlines only (one line
  in `parse_rules`): `specs_rejected` 6 → 0 and
  `schedule_fee_after_reject` 0.0 → 0.27 SEK/kWh.

Files: `custom_components/heatpump_optimizer/grid_fee.py`.
Harness: `grid_fee_decimal_comma.py`.

## Non-findings — identities that held

All from `identities.py` (one command, in the header). These are what lets a
later round call this area dry.

| claim | metric | value |
|---|---|---|
| Per-step energy conservation across every store | ΔE_stored − (Q_in − losses + gains)·dt + refused·dt | **−1.30e-13 kWh** worst of 1600 cases over 5 topologies (single/two-zone × valve/no-valve × two-tank) |
| More power never cools a store | worst ΔT from +0.25 kW | **−2.13e-14 °C** over 6240 comparisons |
| COP non-increasing in flow temperature | worst positive step | **0.0** |
| COP_dhw non-increasing in tank temperature | worst positive step | **0.0** |
| The production step is converged | \|T_end(24 h @ 0.25 h) − T_end(24 h @ 0.03125 h)\| | **0.0113 °C** (`time_step_minutes` is 15.0 and has no CONF_ key, so 0.25 h is the only step production integrates at) |
| Defrost derate stays in its clamp | min/max of `factor` over the whole learned grid after extreme duties | **0.55 / 0.55**, bounds [0.55, 1.0], in-bounds = 1 |
| `wood_share` stays a fraction | min/max over a 39×39 sweep | **0.0 / 1.0** |
| `_wood_share_vec` equals the scalar law | max abs diff | **0.0** (bitwise) |
| DHW wood-coil identity `reduced + coil == draw` | max abs error over 180 points | **5.55e-17 kW** |
| `predicted_cost == Σ price·power·dt` with no PV | abs error | **0.0** |
| The PV-piecewise cost equals `Σ price·P − margin·min(P,s)` | abs error | **2.13e-14 SEK** |
| `import_margin` never goes negative | min | **0.0** |
| `metering_windows` is the box average | max abs error | **0.0** |
| `marginal_price_per_kw == price/k` | abs error | **0.0** |
| Batched vs scalar trajectory parity | not re-measured: `tests/features.py:_grad_parity` pins it bitwise over 13 cells plus the `_batch_fd_gradient` vs `approx_derivative` contract | — |

## What I could not finish

- **`sysid.identify` bias (brief item 5).** Not measured. The estimator
  carries an errors-in-variables correction, a ridge toward a configured
  prior, a column equilibration and a noise-refusal gate; a bias harness
  under white, 0.1 °C-quantised and drifting noise with an honest null
  control is a half-day on its own and I chose depth on four executed
  defects over a shallow pass here. It is the largest unexamined surface in
  this dimension.
- **DST 23- and 25-hour days (brief item 4).** Not measured. `tests/dst_checks.py`
  exists and `tariff.window_factors` carries a long argument about which
  window lengths reconcile across a transition; I did not put a number on
  either. The catalog's 15-minute window divides the hour, which is the case
  that argument says is exact, so I judged the residual risk lower than the
  four things I did measure — that is a judgement, not a measurement.
- **The gradient vs a central finite difference at random points (brief
  item 3).** Not measured directly. D2-03 shows the objective is
  discontinuous in the decision variable on the two-tank topology, which is
  a stronger statement for that topology, but I did not sweep relative
  gradient error across operating points on the others.
- **Month boundaries and currency conversion (brief item 4).** Not
  measured. `PeakTracker.observe` resets on a `%Y-%m` change, which I read
  but did not drive across a boundary.
- **Whether D2-01 changes a real plan's kWh.** I measured the objective
  term, not a solve. Quantifying the plan shift needs
  `tests/optimality.py`-style arms with a flat-price null control, which the
  fan-out box cannot time honestly; I report the term's error, which is
  contention-immune, and leave the plan delta to a fix's own before/after.
- **`buffer_tank_thermal_mass < 0.01` and `dhw_tank_thermal_mass < 0.01`.**
  Two divisor inconsistencies I found by reading and did not pursue: the
  buffer's availability bound uses `C_buf` while `dT_buf` divides by
  `max(C_buf, 0.01)`, and `simulate_dhw_step` returns the tank temperature
  unchanged (charging electricity, no heat, no refused accounting) below
  that same floor. Both need a tank under ~8.6 L. I did not establish
  whether the config flow admits one, so neither is a finding.
