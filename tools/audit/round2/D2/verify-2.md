# D2 round 2 — verifier seat 2 of 3

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` 3.13.1, `PYTHONPATH=tests/hastub`,
run from the export root, five BLAS thread variables pinned to 1 before any
numpy import. Apple M1, shared box; `load1` 1.47–4.56 and `thread_factor`
1.000–1.003 across every run. **No RESULT below is a wall, CPU or RSS number**,
so none needs the quiet window. Scratch under `/tmp/verify-D2-2/`; my own
harnesses live there (`v2_d201_plan.py`, `v2_d201_causal.py`, `v2_d203_dst_sek.py`,
`v2_d203_step0.py`, `v2_d202_d204_d205.py`, `v2_addenda.py`).

My assigned angle is **consequence to the user and to the shipped plan** — what
each finding costs, not that it exists.

## Harness re-runs (all nine, once each)

Every finder harness reproduces its headline number. Deltas: none outside
tolerance. One documentation mismatch worth the judge's eye:

| Harness | Headline | Mine | Verdict |
|---|---|---|---|
| `parity_substeps.py` | golden 0; single stiff 2.5e74; solve 108.50/103.81 vs 54.62/30.08; L1 82.35 | identical to the digit | reproduces |
| `cop_monotone.py` | 7/7 flow cells non-monotone; peaks 17/14.5/13/12/11/10; ratio 0.887–0.999 | identical | reproduces |
| `dst_grid.py` | 84 misaligned on all 6 days; 92 instants; 23 h; 6.0 kWh phantom; 75 min gap | identical | reproduces |
| `model_sanity.py` | `wood_share_max_jump` | **1.0000** | reproduces the REPORT body; the harness *header* still says "Expected … = 0.5". Stale header, not a stale number |
| `sysid_bias.py` | 0.107 @30 min, 0.250 @15 min; drift adopts at 0.304/0.341 | identical | reproduces |
| `conservation.py` | 3.979e-13 / 3.695e-13 / 2.203e-13 kWh | identical | reproduces |
| `fixture_identities.py` | cost 1.311e-4; deferred 0.982 committed / 3.449e-5 fresh | identical | reproduces |
| `tariff_arith.py` | every identity 0, every boolean 1 | identical | reproduces |
| `learner_clamps.py` | 0 violations, 4 nan leaks | identical | reproduces |

---

## D2-01 — batched single-zone simulation ignores the Euler sub-step

**Vote: `verify` (high).** Deciding number: **+69.85 SEK/day, a 3.26× overspend,
on a configuration built entirely from values the config flow's own selectors
offer** — and a three-line revert makes the gap exactly 0.0000 SEK.

**My metric** (differs from the finder's, which reported trajectory divergence
plus one solve): on a single-zone configuration every field of which is a value
the selector itself offers, the difference between the plan
`HeatPumpOptimizer.optimize` returns with the batched jacobian (production
default) and with `_bounds_supported_by_batch` forced False, measured as
predicted cost (SEK/day), objective under the *same* scalar scoring, schedule L1
(kWh/day), and comfort violation ∫max(0, `min_temp` − T_room) dt (K·h/day).

**Consequence, executed** (`v2_d201_plan.py`, winter_typical, single-zone, no DHW,
`min_temp` 17.0 °C):

| cell (all values selector-offered) | n_sub | cost batch / scalar | Δcost | L1 | comfort batch / scalar |
|---|---|---|---|---|---|
| A: slab mass **0.1** (field *minimum*), transfer **0.8** (field *default*) | 2 | 100.79 / 30.94 SEK | **+69.85** | 76.78 kWh | 0.000 / 0.314 K·h |
| B: slab mass 0.6 (step grid), transfer **5.0** (field max) | 2 | 103.77 / 29.60 SEK | +74.18 | 84.01 kWh | 0.000 / 0.310 K·h |
| C: house mass **0.5** (field min), transfer 5.0 | 2 | 98.18 / 46.08 SEK | +52.10 | 55.02 kWh | 0.000 / 0.342 K·h |
| NULL: default house | 1 | 23.28 / 23.28 SEK | **+0.0000** | **0.0000 kWh** | 0 / 0 |

Objective gaps under the one scalar objective the optimizer publishes: +49.06 /
+54.03 / +42.41. Energy on cell A: 62.66 kWh against 40.77 kWh, +54 %.

**Comfort direction is the opposite of the intuition and I want it on the
record**: the *broken* plan is the one that never breaches (0 K·h, room floor
19.69 °C); the correct plan takes a 0.31 K·h excursion the objective prices and
still wins by 49 objective units. So the user is not made cold — the user is
made to pay 3.26× for comfort the objective did not ask for. Nothing is
misreported: both `objective_batch` call sites (`optimizer.py:2784`, `:4629`) are
gradient-only; the published plan is scored by the scalar path.

### Attacks

1. **"It's a generic supplied-jac-vs-estimated-jac effect, not the sub-step
   lines."** Refuted (`v2_d201_causal.py`). I rebuilt
   `simulate_trajectory_batch` from its own source with three edits —
   `thermal_model.py:2605` `if i == 0:` → `if i == 0 and _sub == 0:`, `:2636` and
   `:2637` `* dt_hours` → `* dt` — and rebound it. Bitwise parity is restored
   (3.788e+01 → **0.000e+00**; 3.736e+07 → 0; 1.331e+24 → 0) and the plan becomes
   **bitwise identical to the scalar-jac plan**: Δcost **+0.0000 SEK** and L1
   **0.0000 kWh** on all three stiff cells and on the null cell. Those lines are
   the whole cause.
2. **Flat-price null control.** The gap survives but shrinks hard: cell A
   +69.85 SEK at winter_typical against **+10.03 SEK at `flat`**. So ~86 % of the
   headline SEK is forgone arbitrage — exactly the signature of a gradient that
   cannot see price structure — and it is not a price artefact.
3. **n_sub = 1 null control.** Exactly 0.0000 SEK and 0.0000 kWh at both price
   profiles. Clean.
4. **Reachable in real HA, or only in the stub?** Real: the expert page writes
   `slab_thermal_mass` (`config_flow.py:1178`, `:2186`) and
   `ThermalParameters.clamp` floors it at `THERMAL_MASS_FLOOR = 0.1`, exactly the
   field minimum. `FakeHass` is not on this path at all.
5. **Is the severity earned by population reach?** This is the one place the
   finding is softer than it reads, and I put the number on the record rather
   than leaving it to inference. **0 of 1320** buildings the guided
   questionnaire can derive (4 structures × 5 eras × 3 foundations × 11 areas
   20–1000 m² × 2 emitters, through `presets.derive`) fire n_sub ≥ 2: the worst
   stiffness ratio any derivable building reaches is **0.2500** against the
   `EULER_STABILITY_MAX_RATIO = 1.5` threshold — a factor of six of headroom, and
   structural (`derive` sets radiator loop mass ≈ radiator transfer, so the ratio
   pins near 1.0 h⁻¹). Across the selector's own grid, **2805 of 18513** points
   (15.2 %) fire. Firing needs a manual expert-page entry with slab mass at or
   near its 0.1 minimum (at the default transfer 0.8 the boundary is slab mass
   < 0.133, so the field minimum itself is the only firing value on that grid).
6. **Test gap.** Confirmed with the file and the line.
   `tests/features.py::_grad_parity`'s only n_sub ≥ 2 cell is
   `features.py:1951-1957`, and it passes `two_zone=True`. Every single-zone cell
   uses `profiles.house` (imported as `_grad_house`, `features.py:1646`), whose
   defaults give n_sub = 1 — my NULL cell measures that directly. The killing
   mutation is not hypothetical: the production lines
   `custom_components/heatpump_optimizer/thermal_model.py:2636-2637` are
   *already* wrong and the suite is green, and my three-line fix leaves it green
   too. The suite is blind in both directions, and all 49 golden fixtures have
   n_sub = 1.

I keep **high**: when it fires the user overspends 3.3× silently, and the fix is
three characters. The judge should weigh attack 5 — a panel that scores severity
by population reach has a defensible case for medium.

---

## D2-02 — COP falls as outdoor temperature rises above ~10–17 °C with a valve

**Vote: `weaken(low)`.** Deciding number: **0.0000 SEK and 0.0000 kWh** plan
difference in all nine cells built from the shipped weather profiles.

**The physics is wrong, and unambiguously so.** At a *fixed* flow temperature the
ideal Carnot COP `T_F/(T_F − T_out)` is strictly increasing in `T_out`: at 60 °C
flow it rises from **6.663 at 10 °C to 8.329 at 20 °C, a ratio of 1.2500**.
Production gives a ratio of **0.9244** — the wrong sign, 32 points off. A real
air-to-water unit at a fixed 60 °C flow does *better* at 20 °C than at 10 °C:
less lift, higher evaporating pressure and suction density, and above roughly
7 °C no defrost cycle at all. The measured peaks (flow 40/45/50/55/60/65/70 →
21.0/17.0/14.75/13.0/11.75/10.75/10.0 °C outdoor) confirm the turnover.

**My metric**: solve the same scenario with the production `compute_cop` and with
a **monotone variant** — a running max, identical below each flow temperature's
COP peak and flat above it, so *only* the unphysical falling limb is removed
(turning `cop_flow_carnot` off, the finder's perturbation, also moves the COP
*level* everywhere and would confound level with shape). Report predicted cost,
schedule L1, energy.

**Consequence, executed** (`v2_d202_d204_d205.py`, `valve_storage`,
`valve_storage_low_target`, `wood_two_tank`):

| weather | frac. of horizon above the peak | max \|Δcost\| | max L1 |
|---|---|---|---|
| `winter_cold` | 0.000 | **0.0000 SEK** | 0.0000 kWh |
| `shoulder` (max 11.0 °C) | 0.000 | **0.0000 SEK** | 0.0000 kWh |
| `summer_warm` | 1.000 | **0.0000 SEK** | 0.0000 kWh (plan is 0.000 kWh — nothing to schedule) |
| synthetic const 14/16/18/20 °C | 1.000 | **1.1704 SEK** (const 18 °C, `valve_storage`) | 2.6313 kWh |

Of 21 cells, 15 sit above the peak and only **8** both sit above the peak and
have any heating to schedule. The worst cell moves 1.17 SEK on a **2.39 SEK/day**
bill, and the sign is mixed across cells (−0.14, +0.01, −0.57, +0.80, +1.17) —
this is not a systematic overspend, it is churn in a near-degenerate corner.

### Attacks

1. **Did I give it its best shot?** Yes — I added synthetic constant-outdoor days
   at 14/16/18/20 °C precisely because no shipped profile puts the falling limb
   and real demand in the same horizon (`shoulder` tops out at 11.0 °C, just
   below the 11.75 °C peak at 60 °C flow). Those synthetic days are the only
   cells that move at all.
2. **Is "0 in the fixtures" the same as "0 in the world"?** No, and I will not
   claim it. Real Swedish shoulder days do reach 14–18 °C with residual night
   heating for a storage install; the const-18 °C cell is a plausible real day,
   not an impossible one. That is why my vote is `weaken(low)` and not `refute` —
   the consequence is small, not absent.
3. **Downstream store pricing.** The finder's `marginal_cop(·, "buffer",
   store_temp=60)` figures (2.034 at 10 °C, 1.880 at 20 °C, −7.6 %) reproduce
   exactly on my re-run. They are real, and they price `_terminal_cost` and
   `_deferred_energy_cost` — but the executed end-to-end plan delta is still 0 on
   every shipped profile.

Medium is not earned by a defect whose plan consequence is exactly zero across
every shipped scenario and at most ~1 SEK on a synthetic warm day. **Low.**

---

## D2-03 — the planning grid steps wall-clock time on DST days

**Vote: `weaken(low)`.** Deciding numbers: **0 of 48 solves mispriced at step 0
on the spring day; 2 of 48 on the autumn day** (one real hour per year), and
**0.0000 K·h of comfort breached on both days**.

**My metric**: with a realistic Swedish hourly curve (night 0.35, day 1.10,
morning 1.80, evening peak 2.60 SEK/kWh) published as Tibber publishes it — one
entry per *real* hour, each carrying its own offset — settle a real plan through
the **production** `HeatPumpOptimizer.get_current_action` at every real 15-minute
instant, and compare against what the integration reported.

**Consequence, executed** (`v2_d203_dst_sek.py`, `v2_d203_step0.py`):

| | plain (null) | spring 2026-03-29 | autumn 2026-10-25 |
|---|---|---|---|
| real span of the wall grid's 96 labels | 24.00 h | 23.00 h | 25.00 h |
| **reported day cost error** | +0.0002 SEK | **+2.1002 SEK** | **−2.0998 SEK** |
| … as a share of the 11.78 SEK/day bill | 1.5e-5 | **+17.8 %** | **−17.8 %** |
| booked kWh vs delivered kWh | −0.001 | **−6.001 kWh** | **+5.999 kWh** |
| **comfort breached** | 0.0000 K·h | **0.0000 K·h** | **0.0000 K·h** |
| room floor (min_temp 17.0 °C) | 20.63 °C | 19.76 °C | 20.71 °C |
| step-0 mispriced, of 48 half-hourly solves | **0** | **0** | **2** |

**The dispatched step is almost never wrong, and that is the finding's real
ceiling.** I expected the whole post-transition day to be mispriced and measured
the opposite: `step_offset` is computed as `(now − midnight)` on two datetimes
that carry the *same* `tzinfo` object, and Python subtracts those by **wall
clock**, not by instant — so the offset and the wall-clock label arithmetic
cancel exactly. Step 0 always carries the price in force now. The misalignment
lives entirely in the horizon *tail*, which the 30-minute re-solve
(`DEFAULT_OPTIMIZATION_INTERVAL = 30`) replaces before it is ever dispatched. The
one exception is the autumn fold, where the repeated 02:00 hour makes step 0
carry the *first* pass's price for **2 of 48 solves — one hour per year**.

What does survive: on each transition day the plan books 33.65 kWh and the real
clock delivers 27.65 (spring, one hour of the plan's own night power never
happens) or 39.65 (autumn, the repeated hour is dispatched twice), and the cost
the integration *reports* for the day is off by ±2.10 SEK. Bounding the money:
the spring 6.00 kWh shortfall is cheap night heat the house must make up later —
at worst the whole 6 kWh at the evening peak, 6 × (2.60 − 0.35) = **13.50 SEK**;
the autumn 6.00 kWh is surplus night heat at 0.35 SEK/kWh ≈ 2.10 SEK. Twice a
year. Order **5–30 SEK/year** against a bill in the thousands, with **no comfort
consequence at all** (2.8–3.7 K of margin above the floor on both days).

### Attacks

1. **Null control.** Plain day: reported error 1.8e-4 SEK, delivered−booked
   −0.001 kWh, step-0 mispriced 0/48. Clean.
2. **Does the 30-minute re-solve rescue it?** Measured, not assumed — see the
   step-0 row. Yes, everywhere except the autumn fold.
3. **A clean wall-grid-vs-UTC-grid loss number could not be built, and I am
   flagging that rather than reporting a confounded one.** Both the finder's
   `--perturb` and my first attempt patch `_price_series` only; `_Horizon.timestamps`
   (`optimizer.py:981`) still steps wall-clock, so the counterfactual plan
   dispatches through the same bug. My first cut produced a *negative* "loss"
   (−7.42 SEK spring, −2.48 SEK autumn) purely because the two plans delivered
   different amounts of heat (27.65 vs 36.00 kWh spring; 39.65 vs 21.87 kWh
   autumn). I discarded it. A judge re-taking this should patch `timestamps` and
   `step_hours` too.
4. **Six transition days.** The finder's 84/84/84 across 2025–2027 reproduces
   exactly; the mechanism is date-independent, so I measured consequence on one
   pair and did not re-derive the census.

Medium is not earned by two days a year, no comfort breach, one hour of
mispriced dispatch, and ~±2 SEK of reporting error. **Low** — though I note the
reporting error is user-visible and the fix (step in UTC, in `_price_series`,
`_weather_series`, `_forecast_arrays`, `_Horizon.timestamps` and `step_hours`) is
cheap.

---

## D2-04 — sysid confidence cannot reach its 0.3 adoption gate

**Vote: `weaken(low)`.** Deciding numbers: the feature is **off by default**
(`DEFAULT_SYSID_ENABLED = False`) and **1 of the 23 selectable optimization
intervals** lets a noise-free experiment through the gate; an adopted biased fit
moves the plan by **0.0000 SEK**.

**Is it opt-in?** Doubly, and then some. `DEFAULT_SYSID_ENABLED = False`
(`const.py:437`); a config switch must be turned on ("Allow a one-off measurement
experiment", `strings.json:661`); `RunSystemIdentificationButton`
(`button.py:106-115`) must then be pressed to *arm* it; and the experiment only
starts at a mild (−5…10 °C), cheap (bottom 30 %), night (23:00–05:00) window,
with `min_days_between_runs = 30`. There is no service — the button is the only
entry point.

**Consequence, executed** (`v2_d202_d204_d205.py`, `v2_addenda.py`). Confidence a
**noise-free** experiment with exact parameter recovery scores, by the
optimization interval the slider offers (10–120 min, step 5; gate 0.3):

| interval | 10 | 15 | 20 | 25 | **30 (default)** | 35 | 40 | 45 | ≥50 |
|---|---|---|---|---|---|---|---|---|---|
| confidence | **0.370** | 0.251 | 0.168 | 0.144 | **0.107** | 0.075 | 0.077 | 0.086 | 0.000 / incomplete |
| adopted | **yes** | no | no | no | **no** | no | no | no | no |

This *strengthens* the finder: only the slider's **minimum** value adopts a
perfect experiment. So the feature's single success path is a user who turns on
the option, presses the button, *and* has independently set the optimization
interval to 10 minutes.

**What a user who never gets an adopted fit loses**: only the experiment. The
passive heat-loss learner runs unchanged, and the result is published in the
coordinator data (`coordinator.py:6773`, `"system_identification":
self._sysid.as_dict()`), so the 0.107 confidence is visible to anyone who looks.
The cost is a silent no-op button and one 2 h step + 2 h relax with up to 0.8 K
of drift on a cheap night — the option's own copy promises a measurement
"instead of waiting weeks", and at the shipped default it cannot deliver.

**What an adopted *biased* fit costs**: much less than the raw bias suggests,
because `_adopt_system_identification` (`coordinator.py:10607`) **blends** rather
than overwrites — `blended = (1 − conf)·current + conf·scale`. The finder's
−12.2 % / −23.7 % UA bias becomes a **−3.70 % / −8.07 %** error in
`house_heat_loss_scale`. Executed on the default single-zone house at
winter_typical, with the override confirmed to reach the model (U 0.1500 →
0.1444 → 0.1379 kW/K):

| scale | model U | Δcost | L1 | room floor |
|---|---|---|---|---|
| 1.0000 (ref) | 0.1500 | — | — | 17.065 °C |
| 0.9630 | 0.1444 | **+0.0000 SEK** | **0.0000 kWh** | 17.339 °C |
| 0.9193 | 0.1379 | **+0.0000 SEK** | **0.0000 kWh** | 17.666 °C |
| 0.8000 | 0.1200 | +0.0000 SEK | 0.0000 kWh | 18.583 °C |
| 1.4000 | 0.2100 | +26.5671 SEK | 24.9489 kWh | 16.537 °C |

The plan is insensitive to *under*estimating heat loss out to −40 % on this
scenario and moves sharply only when the model over-estimates — and drift biases
UA the other way. The bias the finding identifies points in the direction that
costs this plan nothing.

### Attacks

1. **Did the override reach the model?** Verified explicitly (the model U column)
   rather than inferred from a zero.
2. **One scenario is one scenario.** The 0.0000 SEK is the default single-zone
   house at winter_typical; I did not sweep. A judge wanting a stronger claim
   should sweep, but the direction argument (drift under-estimates UA; this plan
   is insensitive to under-estimates) is structural, not scenario-specific.
3. **Is "off by default" a get-out?** No — an opt-in feature that cannot work is
   still a defect, and the copy promises something it cannot deliver. It is a
   reason the *consequence* is small, not a reason the bug is not one.

Medium is not earned by an off-by-default, button-armed, 30-day-cadence feature
whose failure mode is a silent no-op and whose success mode moves a plan by
0.0000 SEK. **Low.**

---

## D2-05 — `wood_share` is discontinuous at the flow curve

**Vote: `verify` (low).** Deciding number: **0 of 102,144** `wood_share` calls
made by real solves land within 1 K of the cliff while `hp_temp` is inside the
switch margin; closest approach **1.328 K**.

**My metric**: hook `thermal_model.wood_share` and record every
`(wood_temp, hp_temp, flow_set)` triple a real `optimize` of all three wood
golden scenarios (`wood_two_tank`, `wood_two_tank_smart_write`, `wood_coil`)
actually asks for; count the calls in the cliff's own band and the jump a 1e-6 K
move of `wood_temp` would make at a triple the solve genuinely visited.

**Consequence, executed** (`v2_d202_d204_d205.py`, `v2_addenda.py`):

| | value |
|---|---|
| `wood_share` calls in real solves | 102,144 |
| `hp_temp` inside the 2 K switch margin below the curve | 2,891 (2.83 %) |
| … **and** `wood_temp` within 1 K of the curve — the cliff | **0** |
| … within 2 K / 5 K | 18 / 29 |
| closest approach to the cliff, among in-band calls | **1.3279 K** (median 7.4383 K) |
| sign changes of (`wood_temp` − `flow_set`) across the call sequence | 2,621 |
| `hp_temp` − `flow_set` observed range | −14.68 … **+48.85 °C** |

The wood tank crosses the curve constantly (2,621 sign changes) and the buffer
does spend 2.8 % of calls just under it — but never both at once. Physically that
tracks: the pump charges the buffer *hot* (up to 48.8 K above the curve), so the
buffer sitting 0–2 K below the curve is a brief transient, and it does not
coincide with the wood tank's crossing in any of these solves.

The law itself is genuinely discontinuous and its docstring is genuinely wrong.
My `model_sanity.py` re-run gives `wood_share_max_jump=1.0000` at
`hp_temp == flow_set` — 13.44 kW of a 13.44 kW draw moving between tanks across a
1e-6 K change — against a docstring promising "continuous in w·Q_draw across
every boundary", and `_wood_share_vec` reproduces it bitwise (parity 0.000e+00),
so the batched gradient inherits the same cliff.

### Attacks

1. **Is the counterfactual jump a constant?** No — I evaluate it only at triples
   the solve actually visited, and separately report the distance from those
   triples to the cliff. The 0.9995 "worst reachable jump" sits at
   `wood = 17.604, hp = 27.715, flow_set = 27.716`: the buffer is 1 mK below the
   curve, but the wood tank is **10 K** away from it. That is a hypothetical, and
   I label it as one.
2. **Plausible install rather than fixture?** The joint condition — wood tank
   crossing the curve while the buffer sits 0–2 K below it — is describable, but
   0 hits in 102 k calls across every wood topology the fixtures carry, with a
   1.33 K closest approach, is the strongest evidence available without a
   long-horizon rolling run.

Low is the right severity and it already carries it. I verify rather than weaken
because a law whose docstring promises continuity and does not deliver it is a
real defect that the batched gradient shares, even where no plan touches it.

---

## Summary

| finding | finder | my vote | deciding number |
|---|---|---|---|
| D2-01 | high | **verify (high)** | +69.85 SEK/day (3.26×) on selector-offered values; three-line revert → Δ 0.0000 SEK, L1 0.0000 kWh. Reachability: 0 of 1320 derivable buildings |
| D2-02 | medium | **weaken(low)** | 0.0000 SEK plan delta in all 9 shipped-profile cells; 1.17 SEK on a 2.39 SEK synthetic 18 °C day. Physics ratio 0.9244 vs Carnot 1.2500 |
| D2-03 | medium | **weaken(low)** | step 0 mispriced 0/48 spring, 2/48 autumn; ±2.10 SEK reported-cost error; **0.0000 K·h comfort**; 2 days a year |
| D2-04 | medium | **weaken(low)** | off by default; 1 of 23 intervals adopts a perfect fit; adopted biased fit → **0.0000 SEK** plan change |
| D2-05 | low | **verify (low)** | 0 of 102,144 calls within 1 K of the cliff; closest approach 1.328 K |
