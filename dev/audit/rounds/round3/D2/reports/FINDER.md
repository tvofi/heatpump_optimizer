# D2 — mathematical and physical sanity — round 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`.
Machine: 8-core Apple M1, 8 GB, python 3.11.5, numpy 2.4.6, scipy 1.17.1 on
OpenBLAS. The box carried eleven other agent sessions throughout; `load1` ran
from 12.4 to 156 and is quoted on every RESULT block. **No number in this
report is a wall, CPU or RSS number.** Every metric here is a residual, a count
or a ratio of pure arithmetic — contention cannot move any of them, and each
harness re-runs to the same value under any load.

## Method

Six harnesses under `tools/audit/round3/D2/`, each runnable by the single
command in its own header, each hooking a named production symbol and each
carrying its own live control (an arm in which the metric MUST move, so a green
result cannot be a harness that measures nothing). Nothing here reads a
committed golden fixture: `cost_identity.py` re-solves all 49 scenarios live, so
the five `may-drift` fixtures are irrelevant to every number below.

| harness | what it executes |
|---|---|
| `cop_monotonicity.py` | COP monotone in outdoor temperature at fixed flow |
| `dst_window_factors.py` | capacity-tariff mask vs the plan's own step clock |
| `sysid_bias.py` | `sysid.identify` bias under white / quantised / drifting noise |
| `cost_identity.py` | `predicted_cost`, savings, %, DHW split on 49 scenarios |
| `batch_parity.py` | scalar `simulate_trajectory` vs `simulate_trajectory_batch` |
| `thermal_identities.py` | energy conservation, dt-invariance, monotonicity, derate range |

`d2lib.py` is shared plumbing (thread pin before numpy, `sys.path`, RESULT
printer, `thread_factor`/`load1`/`swapins`/concurrent-process footer). It is not
a harness and prints nothing on its own.

---

## Findings

### D2-01 — COP falls as the weather warms, whenever a mixing valve throttles

`thermal_model.py:ThermalModel.compute_cop` multiplies the nameplate curve by a
Carnot *ratio* `carnot_flow / carnot_ref` whose value strictly decreases in
outdoor temperature, while the nameplate factor `1 + 0.025·Δ` is capped at 1.5
(reached at outdoor 27 °C). The product is therefore not monotone: for every
flow temperature above `cop_flow_reference_temp` (35 °C) there is an outdoor
temperature above which COP **falls** as it gets warmer. A heat pump's COP at a
fixed flow temperature cannot fall as the lift shrinks; this is a violated
physical bound, not a modelling preference.

Executed (`cop_monotonicity.py`): 7 of 7 flow temperatures violate over
−20 … +35 °C; **5 of 7 violate inside the heating-relevant −20 … +20 °C band**.
At 45 °C flow the curve peaks at outdoor 17 °C; at 65 °C flow it peaks at 11 °C
and has lost 0.181 COP by 20 °C. Worst single 0.5 K step inside the band:
0.02093 COP. Over the full sweep the loss from peak to 35 °C reaches 63 % of
peak COP (40 °C flow).

Control: the same sweep with `cop_flow_carnot = False` — the default, and what
`ThermalParameters.from_config` sets whenever no valve throttles — gives
`violating_flow_temps_carnot_off = 0_of_7`. So the nameplate curve is fine and
the Carnot block is the mechanism.

Leave-one-out over the seven flow cells: range 0.483 COP, worst single-step drop
0.254 COP with the most favourable cell dropped.

Reach: `cop_flow_carnot` is on exactly when `mixing_valve.is_throttling` is true,
i.e. every `manual` / `smart_read` / `smart_write` valve install — the whole
buffer-storage feature. The same expression is inlined in
`simulate_trajectory_batch` (verified here to be bit-identical to the scalar
one), and `marginal_cop(store="buffer")` prices every stored kWh through it, so
the inversion reaches the settlement terms as well as the simulation.

I did **not** measure a money consequence. A cost claim would need the
flat-price null control and I could not build one inside the budget; the finding
is the violated bound and its size, and severity is set to `medium` accordingly.

### D2-02 — the capacity-tariff billing mask walks the wall clock; the plan walks UTC

`tariff.py:window_factors` builds its window instants as
`_window_slot(start) + timedelta(minutes=window*i)`. On an aware datetime that
is wall-clock arithmetic: it emits the repeated autumn hour once and the
non-existent spring hour once. The plan's own step clock,
`optimizer.py:_utc_step_starts`, walks UTC — that function exists (#243) for
precisely this reason — and `PeakTracker.observe` keys a live window off the
real instant. So after a DST transition every window in the horizon is labelled
with the hour before or after the one it really falls in, and the plan's cost
term and the live meter *do* disagree about which hour a window bills under —
the property `window_factors`'s own docstring says can never happen.

Executed (`dst_window_factors.py`), over a 48-hour horizon starting at local
midnight:

* **12 of 12 cells mismatch** — {autumn 2026-10-25, spring 2026-03-29} ×
  {60, 30, 15}-minute windows × {`peak_hours`, `weekdays_only`} masks.
* Through the production symbol `HeatPumpOptimizer._peak_window_factors`:
  4 of 48 windows wrong on each transition day; **2 of them are hours the plan
  scores at factor 0.0 (free) that the meter bills at factor 1.0**.
* Money arm: a plan that parks 9 kW in the first such hour — which is exactly
  what a masked tariff's objective is built to do — is charged **0** by the
  objective and **180** currency units by the meter, at a 60/kW tariff over
  3 averaged peaks (`peak_cost` marginal price 20/kW, threshold 0).
* **NULL CONTROL**: the same masks on 2026-10-18, an ordinary Sunday, give
  `null_control_non_dst_day_mismatches = 0` and `unpriced = +0.0000`. The
  second control, no mask configured, returns `None` and the term is inert.

The existing DST coverage does not see this: `tests/dst_checks.py`'s
`window_factors` check starts the horizon at **13:30**, after the 03:00
transition, so it never crosses the fold.

### D2-03 — a drifting room sensor lands in the identified heat-loss coefficient once any noise exists

`sysid.identify`'s fourth regression column is there to keep a linearly drifting
room sensor out of UA, and it does so on noiseless data. The executed result is
that **it stops working at 0.02 °C of white noise** — below the quantisation step
of an ordinary 0.1 °C-resolution room sensor. The estimate collapses to ≈ 0.000
whatever the true drift, and the ramp goes where the docstring says it must:
into UA.

Executed (`sysid_bias.py`), plant `C dT/dt = Q + G − UA(T−T_out)` with
UA = 0.22 kW/K, C = 9.0 kWh/K, G = 0.35 kW, integrated finely and sampled at the
30-minute cadence over the real settle/step/relax phases; 60 seeds per cell;
`bias_UA` = median relative error of `heat_loss_kw_per_c`. The adoption gate is
the coordinator's own (`_adopt_system_identification`: `completed` and
`confidence >= 0.3`).

Median bias of the UA the coordinator would **adopt**, with (adopted / fits)
beside it:

| drift °C/h | σ = 0 (NULL) | σ = 0.02 | σ = 0.05 | σ = 0.10 |
|---|---|---|---|---|
| 0.00 | −0.00 % (60/60) | −2.1 % (59/59) | −5.8 % (28/51) | −18.2 % (3/21) |
| 0.02 | −0.00 % (60/60) | −6.6 % (59/59) | −9.8 % (27/51) | −21.5 % (3/16) |
| 0.05 | −0.02 % (60/60) | **−13.4 %** (59/59) | −16.6 % (26/43) | −38.1 % (1/11) |
| 0.10 | −0.06 % (60/60) | **−24.5 %** (57/57) | −27.5 % (21/33) | none adopted (0/6) |
| 0.20 | −0.25 % (60/60) | **−47.6 %** (27/46) | −42.9 % (2/9) | none adopted (0/1) |

The right-hand columns rest on few adopted runs and are quoted, not leaned on;
the finding rests on the σ = 0.02 column, where the confidence gate adopts
**every** run.

`median_drift_hat` recovers the true drift exactly at σ = 0 (0.0200, 0.0500,
0.1001, 0.2005) and collapses to ≈ 0.000 at every σ ≥ 0.02. The bias is
one-signed (UA always **under**-estimated) and scales monotonically with the
drift at fixed σ.

Null control: the σ = 0 column. Every cell there is within 0.25 % — so this is
the interaction of drift with noise, not the drift alone and not the noise
alone (the d = 0 row at σ = 0.02 is −2.1 %). Leave-one-out over the 20 cells:
range 0.585; the worst cell the harness names is d = 0.20, σ = 0.10 at −58.5 %,
which is a raw median over a single fit and zero adoptions — dropping it leaves
−47.6 % (d = 0.20, σ = 0.02), which is 27 adopted runs and is the honest worst.

Two candidate fixes were executed and do **not** work, recorded so a fixer does
not re-try them. Widening `sensor_drift_prior_c_per_h` from 0.02 to 1.0
(`--wide-drift-prior`) moves the bias by 0.002 and leaves `median_drift_hat`
near −0.024 whatever the true drift, so the ridge is not the binding
constraint — the column is simply not identifiable against sensor noise at this
experiment's excursion. A 5-minute cadence (60 rows instead of 10) gives
−0.2408 against −0.2446 at d = 0.10, σ = 0.02, and nothing is adopted at all.
(`max_excursion_c` gates the state machine's abort logic, not `identify`, and
moves nothing.)

The perturbation the judge should run is the injected drift itself, along the
σ = 0.02 row: −2.1 %, −6.6 %, −13.4 %, −24.5 %, −47.6 % for d = 0.00, 0.02,
0.05, 0.10, 0.20 °C/h — monotone in magnitude and one-signed. It is executed by
the default invocation.

A house modelled as losing 13–25 % less heat than it does is planned with too
little heat, so the consequence is a silently missed comfort band. Two
mitigations keep this at `high` rather than `critical`: `SysIdConfig.enabled`
defaults to `False`, and the result is blended by confidence rather than
adopted whole.

---

## Non-findings — checked, held, with the number

**N1. `predicted_cost == Σ price·power·dt` and the three money identities, on
every golden scenario.** `cost_identity.py`, all 49 scenarios re-solved live:
`max_resid_A = 1.42e-14`, `B = 3.55e-15`, `C = 6.66e-14`, `D = 1.42e-14`
currency units against a 1e-9 tolerance; `violations = 0`. A = the energy cost
re-derived independently from `_energy_cost_fn`'s documented piecewise-PV
contract; B = savings vs baseline − predicted − deferred; C = the clipped
percentage; D = the DHW/space split summing exactly to the total. Null control:
`flat_prices` and `valve_storage_flat_prices` are both ≤ 1.42e-14. Live control:
`--perturb` (prices × 1.01) takes `max_resid_A` to 3.06e-01, seven orders above
tolerance.

**N2. Scalar/batch bitwise parity.** `batch_parity.py`, 22 cells spanning
single-zone, two-zone, manual and smart-write valve, `valve_upper_direct_slab`,
two-tank wood, external heat, per-step valve targets, the defrost derate with a
NaN humidity step, a learned internal-gains profile, weather, and both Euler
sub-step branches: `cells_not_bit_identical = 0`, `max_ulp_all_cells = 0`,
`max_abs_kelvin = 0.0`, `max_abs_refused = 0.0 kW`. Live control:
`--scramble` adds 1e-9 kW to one step of the batch input only and every one of
the 22 cells leaves zero (`max_ulp_all_cells = 1.23e+06`).

**N3. Energy conservation, per store and whole-system.**
`thermal_identities.py`: E1 (marginal enthalpy per extra kW equals `cop·ΔP·dt`
summed over every store) `4.83e-14 kWh`; E2 (Σ C·ΔT equals net flux × dt, with
the buffer cap's refused-heat ledger booked as an outflow) `2.44e-14 kWh`. Both
against a 1e-12 kWh tolerance, over 4 topologies × 5 outdoor × 4 buffer × 5
power points. Live control: `--break-e2` drops the buffer standby loss from the
right-hand side and E2 rises to `5.95e-02 kWh` on every valve cell.

**N4. dt-invariance and integrator order.** E3: one hour taken as 1/2/4/8/16
steps against a 512-step reference. The deviation halves as dt halves, order
→ 1.037 (single), 1.039 (two-zone), 1.060 (valve), 1.035 (wood two-tank), all
inside [0.85, 1.15]. That is exactly first order, which is what explicit Euler
must give; nothing is losing an order at a sub-step seam.

**N5. More power never cools a store.** E4: worst `dT/dP` over the whole grid is
`−9.47e-15 K/kW` — float noise, three orders inside the `−1e-12` tolerance —
across room, slab, upper, lower and buffer in all four topologies.

**N6. Defrost derate stays in [0, 1].** E5: after 4 000 adversarial `observe` /
`observe_duty` calls with out-of-range ratios and duties, `factor` over a
121 × 6 (temperature × humidity, NaN included) grid stays in
`[0.550000, 0.700000]` ⊂ `[DERATE_MIN, DERATE_MAX] = [0.55, 1.0]`.

**N7. The capacity tariff charges the monthly peak once, at the marginal
price.** `peak_cost`'s docstring algebra (`full_price × mean(top-k)` =
`(full_price/k) × sum(top-k)`) checks out: `coordinator.py:4844` feeds
`peak_price_per_kw` from `CapacityTariff.marginal_price_per_kw`, which is
`price_per_kw / peaks_averaged`. No factor-of-k over-charge.

**N8. The smooth/hard top-k seam is continuous enough to optimise across.**
Sweeping a tied plateau through the `n_at_peak > k` switch, the largest jump in
`peak_cost` is 9.3e-03 on a 210 currency-unit term (4e-5 relative), and
`_smooth_topk_sum` reproduces the hard sum to 1.6e-06 for 4–24 tied windows.

**N9. Disproved lead, harness gap named.** `result.pv_surplus` is
`_pv_surplus_list`'s 3-decimal rounding of the array the objective actually
prices. Re-deriving identity A from that published copy manufactures a residual
of 5.09e-04 on `shoulder` and 2.47e-05 on `summer_dhw_only` — a false finding I
came within one step of filing. `cost_identity.py` now rebuilds the array from
`golden.pv_surplus_for` and the header says so, so the next auditor does not pay
for it again.

## What I could not finish

* **The solver's gradient versus a central finite difference.**
  `_batch_fd_gradient` is a faithful replica of scipy's own 2-point
  `approx_derivative` (I read the bound-adjustment and zero-step rules against
  scipy's and they match, including the deliberate `0.0`-at-a-fixed-variable
  departure). What I did not get to is the accuracy question underneath: a
  forward difference with `eps = 1e-4` against a central difference at random
  feasible points, and where the relative error is worst — the objective has
  `max(0, ·)` comfort kinks and a soft-top-k plateau, both places a one-sided
  step can be badly wrong. Reaching the live objective needs a
  `mock.patch.object` wrapper on `_multi_start_minimize` to capture
  `(objective, batch_objective, bounds, x0)`; the wrapper is straightforward and
  is the first thing a round-4 D2 should write.
* **A money figure for D2-01.** Needs the flat-price null control and a
  valve-storage arm; deliberately left unmeasured rather than asserted.
* **Grid-fee day/night and weekday windows, currency conversion, and the PV
  export price applied piecewise** were not swept. The PV piecewise form is
  checked indirectly and exactly by N1 on the two PV scenarios.

## exposure

Read: `tools/audit/briefs/COMMON.md`, `tools/audit/briefs/D2.md`,
`tools/audit/README.md`, the out-of-tree `SEAT-BLOCK.md`, `CLAUDE.md`, and
production/test sources under `custom_components/heatpump_optimizer/` and
`tests/`. No `gh`, no GitHub, no `docs/audit-*.md` (absent from this export), no
`docs/backlog.md`, no `RELEASE_NOTES.md`, no earlier-round findings. Two
`D<k>-nn` identifiers appear in production comments I read
(`optimizer.py:_batch_fd_gradient` cites `D9-01`, `sysid.py:identify` cites
`D2-07`); both were treated as context and neither steered a harness. Nothing
outside `tools/audit/round3/D2/` was created or modified; no production or test
file was edited. `tests/stress.py` was not run, no full `tests/run.sh` was run,
and the gate lock was never taken.
