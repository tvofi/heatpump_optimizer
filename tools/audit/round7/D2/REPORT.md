# D2 - mathematical and physical sanity (round 7)

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648`, export at
`/Users/timmalmstrom/audit-r7-baseline`, python
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, every command
run from the export root with `PYTHONPATH=tests/hastub`. Machine: 8-core Apple
M1, 8 GB, darwin arm64, shared with the other round-7 finders (`load1` 7.5-8.6
throughout). No wall or CPU figure is offered as evidence; every number below
is a count, an identity residual or a ratio, so none of it is
contention-sensitive.

## Method

Fresh eyes against the pinned baseline, working down D2's own method list:
thermal-model conservation and dt-invariance, scalar/batch parity, monotonicity
and physical bounds, COP and derate laws, the objective identity, tariff and
price arithmetic, and the estimators' clamps. Each item is driven through the
production symbol it belongs to (never a re-derivation from constants) and, for
every identity that held, the number that showed it is in Non-findings below.
Two instruments carry the findings; the rest are the sweeps that came back
clean, kept so a later round can call this dimension dry without redoing them.

D2's traps were honoured: the five `may-drift` fixtures were not read for
last-ulp differences (nothing here compares recorded floats), and every identity
was swept rather than checked at one operating point.

## Findings

### D2-01 - the buffer step divides by a capacity the tank does not have

Severity low, class `bug`, reachable only outside the config flow.

`_simulate_step_two_zone` computes the tank's temperature rate as

    dT_buf = (thermal_power - q_rad - q_floor - q_buf_loss) / max(C_buf, 0.01)

while every other use of the same capacity in the same step - the availability
bound that decides how much the tank may *deliver* (`available` / `avail_hp`),
and `_stability_substeps`' stiffness count - uses the raw `C_buf`. Below
0.01 kWh/K the two differ, so the tank's stored energy becomes
`C_actual / 0.01` of the heat the step was given and the balance closes short by
exactly `(C_actual - max(C_actual, 0.01)) * dT_buf`.

Executed, `tools/audit/round7/D2/buffer_cap_conservation.py`, seven volumes, one
step each at `dt = 0.003 h` so `_stability_substeps == 1` and the sub-step
composition error cannot mask the result:

| buffer | C_buf (kWh/K) | net (kWh) | sum dE (kWh) | residual (kWh) |
|---|---|---|---|---|
| 5 L | 0.00580 | 0.006733 | 0.012189 | +5.456e-03 |
| 8 L | 0.00928 | 0.006728 | 0.007664 | +9.356e-04 |
| 8.62 L | 0.01000 | 0.006727 | 0.006728 | +1.040e-06 |
| 10 L | 0.01160 | 0.006725 | 0.006725 | +2.0e-15 |
| 35 L | 0.04060 | 0.006698 | 0.006698 | +2.0e-15 |
| 200 L | 0.23200 | 0.006592 | 0.006592 | +1.2e-15 |
| 750 L | 0.87000 | 0.006374 | 0.006374 | +1.5e-15 |

The mechanism is exact, not fitted: at 5 L, `dT_buf = -1.298983 K`,
`(0.00580 - 0.01000) * dT_buf = +5.456e-03 kWh`, and
`residual / predicted = 1.000000`. The same grid with the tank at 200 L closes
to 1.2e-15 kWh.

Reachability, measured: the config flow's own floor is `_number(10, 1500, 5,
'L')` for `buffer_tank_volume` (config_flow.py:1619), so
`C_actual >= 0.0116 > 0.01` and **no shipped UI path reaches the guard**. That
is why the severity is low and not higher - but the same three-way disagreement
is written at three more seams in the same file:

    grep -n "C_buf\|C_w\|C_dhw" custom_components/heatpump_optimizer/thermal_model.py

* `dT_buf` - `max(C_buf, 0.01)` vs the raw `C_buf` in `available`/`avail_hp`
  and in `_stability_substeps` (the finding above).
* `dT_wood` / `avail_wood` - `max(C_w, 0.01)` vs the raw `C_w`; the wood-tank
  volume floor is 50 L, so also unreachable.
* `simulate_dhw_step` returns the tank temperature UNCHANGED (no heat in, no
  draw, no loss) when `C_dhw < 0.01`; the DHW volume floor is 50 L, so also
  unreachable.
* `_stability_substeps` states in its own comment that it mirrors "the step's
  own `C_buf` fallback" and uses `0.04` for `c_buf < 1e-6`, which is a third
  value again: `0.04` there, `0.01` in `dT_buf`, and raw in `available`.

The property the fixer is held to: **one capacity per store, read once per
step, by every expression in that step that needs a store's capacity** - the
step's rate, its availability bound and its stability count. The seams this
finding demonstrated are the four rows above; the rule that enumerates them is
the grep.

Null control: the 200 L cell of the same harness - same step, same weather,
capacity above the guard - closes to 1.2e-15 kWh.

### D2-02 - one statement in the package cannot execute

Severity low, class `hygiene`.

`HeatPumpOptimizer._terminal_cost_batch` ends with two identical
`return cost_batch` lines; the second (`optimizer.py:2119`) is unreachable.
Executed, `tools/audit/round7/D2/dead_statements.py`, an AST walk of all 65
files in `custom_components/heatpump_optimizer`:

    RESULT unreachable_statements=1 count
    RESULT sites=optimizer.py:2119 in _terminal_cost_batch
    RESULT mutated_count=0 count

The second line is also the mutation proof for the check itself: deleting it by
text substitution drops the count 1 -> 0, so the instrument is drivable and the
count is not an artefact of the walk. Only one such statement exists in the
package, which is itself evidence that the structural budget's LOC cost lands
on exactly the kind of line a reader deletes on sight.

The property: **no statement follows an unconditional `return` in the same
block**, package-wide, with the AST walk as the rule.

## Non-findings - checked, held, with the number

| Claim | Command | Value |
|---|---|---|
| Per-step energy conservation of `simulate_step` (stores' enthalpy change = heat in - losses + gains, minus booked refused), randomised config x state x input grid, cells whose step does not subdivide | `tools/audit/round7/D2/energy_balance_sweep.py` | 453 cells, max 2.49e-14 kWh, p99 2.18e-14, tolerance 1e-9 |
| `simulate_trajectory_batch` is bitwise `simulate_trajectory`: single/two-zone x 4 valve modes x wood x 35/200/750 L x `slab_fed_direct` x `flow_curve_cop` x `cop_flow_carnot` x dt 0.25/0.5/1.0 x 4 state overrides | `tools/audit/round7/D2/batch_parity_sweep.py` | 64 configurations x 4 rows x 25 steps, 0 mismatching cells |
| More power never cools a store: all six stores, 81-step power sweep over 10 configurations, plus an 81 x 61 (outdoor, power) grid on the 35 L valved plant | `tools/audit/round7/D2/monotonicity_sweep.py` | 0 violations |
| COP monotone in outdoor, monotone non-increasing in flow temperature and in DHW tank temperature, never below the resistive floor of 1.0 | `tools/audit/round7/D2/cop_sweep.py` | 400 randomised parameter sets x 221 outdoor points x 4 humidities x 111 flow points x 4 DHW curves: 0 violations |
| No golden scenario's recorded trajectory crosses a plant bound (`buffer_max_temp`, `dhw_hard_max_temp`, `WOOD_TANK_MAX_TEMP`) - the checker in `tests/golden.py` bounds every series by a flat -40..120 C, so it would not catch one | `tools/audit/round7/D2/golden_bounds.py` | 50 scenarios, 0 crossings |
| `predicted_cost == sum(price * power * dt)` and `baseline_cost == sum(price * baseline_power * dt)` on the committed fixtures (PV scenarios excluded by design: their term is piecewise in surplus) | `tools/audit/round7/D2/objective_identity.py` | 48 fixtures, worst relative error 1.38e-07 (fixture rounding to 5 dp) |
| `sysid.identify`'s UA bias under a 0.1 C **quantised** room sensor - the brief's own arm, absent from the committed ensemble, which drives white Gaussian noise | `tools/audit/round7/D2/sysid_quantised_ensemble.py` | 0.1 C resolution over 40 seeds: median +0.0 %, abs(bias) p90 9.9 %, max 14.9 %, 17 of 40 refused for noise - no worse than the committed Gaussian arm (median +3.5 %, p90 12.2 %), because 0.1 C quantisation carries 0.029 C of error where the committed arm injects 0.10 |
| Defrost derate continuous in outdoor temperature and humidity and inside [DERATE_MIN, DERATE_MAX], on a deliberately non-uniform grid (R6-D2-01 is the interpolation) | `tools/audit/round7/D2/derate_sweep.py` | 40851 cells: factor range [0.600000, 1.000000] inside [0.55, 1.0], 0 cells outside; max jump 2.541e-08 per 1e-5 K, 2.376e-08 per 1e-5 RH |
| dt-invariance of `simulate_step`: 4 x 15 min vs 1 x 60 min differs by 4.5e-03 K (room, no power) to 8.9e-02 K (room, 6 kW), i.e. first-order explicit-Euler error in dt, the integrator's stated order | `tools/audit/round7/D2/monotonicity_sweep.py` (dt section of the probes run before it was renamed) | no zero-order residual |
| The stated objective in `optimizer.py`'s module docstring matches the implementation term for term: `grid_cost * price_weight`, comfort terms unscaled, `(cycling + capacity) * price_weight`, terminal cost carrying the weight through `refill_price` | read against `_cost_terms_batch` | consistent; no finding |
| `peak_cost`'s algebra (bill = full price x mean top-k = marginal price x sum of top-k excesses) and its `price_per_kw` argument being fed `marginal_price_per_kw` at every production call site (`_grid_report`, coordinator.py:4675, `topology.peak_miss_sek`) | grep + `tests/features.py` pins | consistent; the parameter's *name* is the hazard, not its value |
| The `max(C, 0.01)` guards are inert at every schema-reachable volume: buffer floor 10 L (0.0116), wood floor 50 L (0.058), DHW floor 50 L (0.058) | `grep -n "tank_volume" custom_components/heatpump_optimizer/config_flow.py` | all above 0.01 - see D2-01 for what happens below |

## What I could not finish

* The gradient behind `_batch_fd_gradient` measured against a **central**
  difference (D2's method item 3) - the suite pins it against scipy's own
  2-point estimate bit for bit, which is a different question from how far
  either is from the true derivative. Not run.
* `_smooth_topk_sum`'s documented bound (soft <= hard x (1 + 1e-6)) was read and
  reasoned about (the logistic weights are bounded in (0, 1) and the bisection
  drives their sum to k, so the bound is structural) but not swept
  independently of `tests/features.py`'s five rows.
* Tariff folding on a 23/25-hour DST day and the capacity tariff's month
  boundary: read only; `tests/dst_checks.py` drives 15 and 60 minutes across
  both Stockholm transitions and `window_factors`' docstring documents the
  off-grid trade with a round-3 sweep, so nothing new was measured.

## Exposure

None. This dimension needed no `docs/` file and no GitHub record; nothing in the
tree that carries an earlier round's findings was read. The only audit artefacts
consulted were `tools/audit/briefs/COMMON.md`, `D2.md` and
`tools/audit/README.md`.
