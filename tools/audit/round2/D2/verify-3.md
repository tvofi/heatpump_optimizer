# D2 verifier seat 3 of 3 — perturbation and fix scope

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` 3.13.1, numpy 2.5.2, scipy 1.18.1,
`PYTHONPATH=tests/hastub`, run from the export root, five BLAS thread variables
pinned to 1 before any numpy import. Apple M1 8 GB, quiet box (load1 1.74–5.38
across the runs; `thread_factor = 1.000` in every run). **No RESULT below is a
wall, CPU or RSS number** — every one is a count, a ratio, a residual or an exact
parity — so the load1 ≤ 1.5 rule does not bind and nothing needs a quiet-window
re-take.

Working copies under `/tmp/verify-D2-3/` (`repo` = D2-01 fix, `repo_dst` = D2-03
fix, `repo_wood` = D2-05 fix, `repo_eps` = a sensitivity control). Nothing in the
export was modified except this file. `tests/run.sh` was not run and
`/tmp/hpo-gate.lock` was not taken.

Harnesses I wrote myself (the panel's own-metric obligation, and the fix-scope
instrument): `/tmp/verify-D2-3/golden_bits.py` (byte-identity of all 55 golden
captures), `cop_shape.py` (COP shape + the proposed replacement formula),
`sysid_interval.py` (confidence across the whole configurable interval range),
`wood_grid.py` (what the region-3 change moves on a 101×101 grid).

All nine finder harnesses were re-run once. The four that carry only non-findings
(`conservation.py`, `fixture_identities.py`, `tariff_arith.py`,
`learner_clamps.py`) reproduced every reported value exactly (space residual
3.979e-13 kWh, DHW 3.695e-13, sub-step 2.203e-13, wood cap 20.081 kWh, coil 28 of
1426 at 4.441e-16; cost identity 1.311e-04 SEK, deferred 9.820e-01 on the
may-drift fixtures and 3.449e-05 fresh, 0 bound violations; metering 5.684e-14 kW,
25 offset windows, 0 grid-fee mismatches; 4 clamp learners, 0 violations,
4 NaN leaks).

---

## D2-01 (high) — batched single-zone simulation ignores the Euler sub-step

**My number.** `parity_max_diff_single_stiff = 2.536e+74 °C`,
`parity_min_diff_single_stiff = 5.283 °C`, `parity_diff_slab0.5_k5.0 = 1.270e+20 °C`,
1 of 6 stiff cells non-finite, `parity_max_diff_golden = 0.000e+00`,
`parity_max_diff_two_zone_stiff = 0.000e+00`,
`solve_objective_gap_batch_minus_scalar = 53.8845` (batch-jac 108.5030 / 103.8091 SEK
vs scalar-jac 54.6186 / 30.0832 SEK), `grad_batch_vs_scipy_maxabs_stiff = 1.614e+83`,
`_default = 0.000e+00`. Identical to the finder's report in every digit.
`thread_factor=1.000`, `load1=2.50`.

**Metric definition.** max |T_batch − T_scalar| (°C) over a 48-step trajectory per
configuration cell, room/slab/upper/lower/buffer/wood; and
J_scalar(plan solved with the batched jac) − J_scalar(plan solved with scipy's FD jac).

**Perturbation outcome — moves, in the stated direction.**
`--perturb` (slab_heat_transfer 5.0 → 0.8 on the slab_thermal_mass 0.5 cell,
n_sub 2 → 1): `parity_diff_slab0.5_k5.0` 1.270e+20 → **0.000e+00**,
`solve_objective_gap_batch_minus_scalar` 53.8845 → **−0.0000**,
`solve_schedule_l1_distance` 82.3475 → 0.0024 kWh,
`grad_batch_vs_scipy_maxabs_stiff` 1.614e+83 → 0.000e+00. Not void.

**The fix, applied as a real production edit on the copy** (`/tmp/verify-D2-3/repo`,
`thermal_model.py`: `T_room = T_room + dT_room * dt` / `T_slab = ... * dt` in place of
`dt_hours` at the two sub-step updates, and the `if i == 0: T_room =
initial_state.room_temperature` seed deleted in favour of `T_room = room[:, 0].copy()`
hoisted beside `T_upper`/`T_lower`/`T_slab`/`T_buf`/`T_wood`):

- parity restored on **all six** stiff single-zone cells, exactly:
  `parity_max_diff_single_stiff = 0.000e+00`, `parity_min_diff_single_stiff = 0.000e+00`,
  `parity_single_stiff_nonfinite_cells` 1 → **0** (the n_sub = 9 cell that was `inf`);
- the solver consequence closes: batch-jac now returns objective **54.6186**, cost
  **30.0832** — bit-for-bit the scalar-jac answer — `solve_objective_gap = 0.0000`,
  `solve_schedule_l1_distance = 0.0000 kWh`, `grad_batch_vs_scipy_maxabs_stiff = 0.000e+00`;
- two-zone parity and the 49 golden configs unchanged at 0.

**Fix-shipability: it does not move a golden.** My own harness re-derives the JSON the
fixture recorder would write for all 49 plan `SCENARIOS` + 5 coordinator topologies +
`config_flow` and hashes each:

| tree | `golden_digest_all` |
|---|---|
| baseline export | `2c6bef383fed6ba83b70184c1e546dfd5a1627a7bab9b7bcab3477667040547d` |
| `/tmp/verify-D2-3/repo` (fixed) | `2c6bef383fed6ba83b70184c1e546dfd5a1627a7bab9b7bcab3477667040547d` |

`golden_captures=55`, **0 digest mismatches, 0 raw-byte mismatches**. Sensitivity
control for my own harness (it must be able to see this code path): a 1e-12 addend on
the same `T_room` update in `/tmp/verify-D2-3/repo_eps` moves `shoulder`'s digest
(`c3f42492bb205864` → `4ab3396435a9af72`) while three other single-zone fixtures hold —
so the identity above is a measured null, not blindness. Instrumented count: **48 of 49**
golden scenarios reach `simulate_trajectory_batch`, **34** reach the single-zone branch,
**2621** single-zone batch calls, and every one of them has **n_sub = 1** — which is why
the fix is inert on the fixtures. `tests/features.py` on the fixed copy:
**ALL 1557 FEATURE CHECKS PASSED** (exit 0), including all eleven
`batched simulation is bitwise-identical` / `batched jac == scipy 2-point` cells.

**Scope completeness — the listed files clear it; the test gap is WIDER than stated.**
`simulate_trajectory_batch` is the *only* batch twin in the package
(`grep -n "def .*batch"` over `custom_components/heatpump_optimizer/*.py`): both
`objective_batch` sites (`optimizer.py:2776`, `:4619`) route through it, and the
DHW-path scalar objective (`optimizer.py:4563`) calls the same
`simulate_trajectory` the space-only one does — so the scalar/batch divergence class
has exactly one home and the one-branch fix closes it. But the finder understates
`_grad_parity`: I measured `n_sub` for all eleven of its cells and **every one is
n_sub = 1**, including the cell *labelled* `"stability substeps"` — its
`room_thermal_mass: 0.3` override is not a config key at all (`from_config` maps the
room mass from `CONF_HOUSE_THERMAL_MASS = "house_thermal_mass"`), and even with the
three mass overrides that do land, the two-zone stability ratio is **0.746 × dt**
against `EULER_STABILITY_MAX_RATIO = 1.5` → n_sub = 1. So the batch/scalar parity
contract has **zero** coverage in the sub-step regime, single-zone *and* two-zone, and
the fix should add a cell whose n_sub is asserted > 1 rather than merely named so.
Killing single-line production mutation the suite fails to notice: the shipped
`dt_hours` at `thermal_model.py:2636-2637` itself — a production file, so the gap stands.

**Vote: `verify` (high).** Deciding numbers: 2.536e+74 °C → **0.000e+00** and objective
gap 53.8845 → **0.0000** under the fix, with the golden digest **byte-identical across
all 55 captures** and features.py green — the fix ships without touching a fixture.

---

## D2-02 (medium) — with a valve, COP falls as outdoor temperature rises

**My number.** Finder's metric reproduced exactly: `cop_flow_cells_nonmonotone = 7 of 7`,
`cop_ratio_20_over_peak_min = 0.8874` (flow 70), `_flow55 = 0.9427`, peaks at
17/14.5/13/12/11/10 °C for flow 45…70, `marginal_cop_buffer60_out10 = 2.0339` vs
`_out20 = 1.8802` (−7.6 %), `marginal_cop_buffer60_sign_changes = 1`,
`carnot_fraction 0.165–0.328`, DHW COP 0 violations in either variable.
`thread_factor=1.000`, `load1=2.46`.

**My own metric** (`cop_shape.py`, independent of the sign-change count):
`monotone_violation(F) = max over T1 < T2 on the grid of COP(T1) − COP(T2)` — the
kelvin-ordered COP drop, zero iff non-decreasing. Result:
`cop_monotone_violation_cells_ship = 6 of 6` flows above the 35 °C reference,
`cop_max_drop_ship = 1.1405` COP units, `cop_monotone_violation_flowNone = 0`.
Same phenomenon, different definition; the two agree.

**Perturbation outcome — moves, in the stated direction.**
`--perturb` (`cop_flow_carnot = False`): `cop_flow_cells_nonmonotone` 7 → **0**,
`marginal_cop_buffer60_sign_changes` 1 → **0**, marginal COP monotone
2.8875 → 3.3250 → 3.7625 → 4.2000 → 4.6375 over 0…20 °C. Not void.

**The proposed replacement formula is a no-op — this is the deciding scope number.**
Implemented literally as the finding states it
(`η = COP_base·(T_ref,K − T_out,K)/T_ref,K`, then `COP(F) = η·T_F,K/max(T_F,K − T_out,K, 1)`)
and measured against the shipping `compute_cop`:

- it is **algebraically the shipping code**: `COP_base · (T_ref−T_out)/T_ref · T_F/(T_F−T_out)`
  *is* `COP_base · carnot_flow/carnot_ref`. Every cell keeps the identical peak location
  (+17/+14.5/+13/+12/+11/+10 °C) and the identical `ratio20/peak`
  (0.9893/0.9661/0.9427/0.9217/0.9034/0.8874);
- `cop_monotone_violation_cells_proposed = 6 of 6` — **the turnover is not removed**;
  `cop_max_drop_proposed = 1.1405`, unchanged;
- the only divergence is the shipping `max(0.25, ratio)` clamp, which the literal
  proposal drops: `cop_ship_vs_proposed_maxabs_full_domain = 4.767` but it first appears
  at T_out ≥ 32/29/27.5/25 °C for flow 45/55/60/70. Over the domain the nine fixtures the
  finder lists as `expected_golden_drift` actually visit (T_out −16…−8 °C, flow 36…75 °C),
  `cop_ship_vs_proposed_maxabs_over_fixture_domain = **6.661e-16**` — one ulp. **The
  proposed change would not move any of those nine fixtures**; the
  `expected_golden_drift` list is wrong in the same breath as the formula.

The root cause the proposal misses: the ratio is fine, the *base curve* is not — its
implied Carnot fraction falls 0.328 → 0.165 across −20…+25 °C (the finder measured this
itself), and a derate made "consistent with the base curve's own Carnot fraction" is by
construction the identity. A real fix has to change the base curve's shape or make the
derate depend on lift rather than on T_out.

**Physical sanity at the extremes** (my assignment). Both formulas stay under the Carnot
bound everywhere (`cop_ship_minus_carnot_max = cop_proposed_minus_carnot_max = −2.3560`).
At very low outdoor with flow at the emitter maximum they are identical and both
unphysical in the same way: `cop_ship_at_-25C_flow70 = cop_proposed_at_-25C_flow70 =
**0.7385**` against a Carnot bound of 3.612 and a base curve of 1.0500 — a COP below 1.0,
i.e. the model says a resistive heater beats the pump; at flow 45 / −30 °C both give
0.9395, also sub-unity. Neither the shipping code nor the proposal has a floor at the
resistive-heat line (only the absolute `max(cop, 0.5)`). At the high end the proposal is
strictly worse than shipping: dropping the 0.25 clamp collapses COP to the 0.5 floor at
T_out ≥ ~40 °C, and shipping's clamp instead creates a flat plateau (1.3125 for flow 70
from ~+27 °C up) with a discontinuous jump to 5.8463 once the 1 K lift floor engages —
both outside the physical domain, both artefacts.

**Reachability / severity.** All nine valve and wood golden scenarios run at outdoor
−16…−8 °C: `d2_02_valve_steps_in_declining_cop_region = **0 of 864**`. The defect is
never exercised by a shipped fixture, so no fixture can notice it or a regression in it.
The consequence is a permanent −7.6 % mis-pricing of stored heat at 10 → 20 °C outdoor
on throttling-valve installs, with no executed plan-level delta on either side.

**Vote: `verify` (medium)** — the defect and every number in the claim reproduce
exactly, and the perturbation isolates the mechanism cleanly (7 → 0). But the finding is
**not actionable as written**: the deciding scope number is
`cop_monotone_violation_cells_proposed = 6 of 6` (the proposed formula leaves the
turnover exactly where it is) together with `6.661e-16` over the fixture domain (so its
listed nine-fixture golden drift would not happen either). A fixer must be sent back for
a formula; I would not let this one through fix-review.

---

## D2-03 (medium) — the planning grid steps wall-clock time on DST days

**My number.** `dst_transition_steps_misaligned` = **84** on all six transition days
(min = max = drop-most-favourable = 84), `dst_null_control_plain = 0`;
spring `distinct_instants = 92`, `span_hours = 23.00`, `phantom_steps = 4`,
`plan_phantom_kwh = 6.000` of `plan_total_kwh = 29.960`; autumn `distinct_instants = 96`,
`span_hours = 25.00`, `max_gap_min = 75`, `plan_gap_step_power = 6.000 kW`.
Identical to the report. `thread_factor=1.000`, `load1=1.74`.

**Metric definition.** Number of the 96 coordinator steps whose assigned price ≠ the
price in force at the real instant `t0 + i·15 min`, on a solve anchored at local midnight
with `HASTUB_TZ=Europe/Stockholm`.

**Perturbation outcome — moves to zero on all six, and does not move the non-DST day.**
`--perturb` (the one-line `_price_series` UTC stepping): misaligned **84 → 0** on
2025-03-30, 2025-10-26, 2026-03-29, 2026-10-25, 2027-03-28, 2027-10-31;
`dst_null_control_plain` stays **0 → 0** and the plain day keeps 96 distinct instants,
24.00 h, 15-min gaps, 0 phantom kWh. Not void.

One honest caveat on the perturbation's reach: it patches `_price_series` only, so the
geometry half of the claim is untouched by it — under `--perturb` the spring plan still
books `plan_phantom_kwh = 6.000` and the autumn plan still holds a 75-minute step at
6.000 kW, because those come from `_Horizon.timestamps`. The headline number does move,
so the harness is not void; the fix simply has to be wider than the perturbation.

**Fix-shipability — I built the wider fix and it ships clean.** On
`/tmp/verify-D2-3/repo_dst` I added a naive-safe `_real_step` helper to both files
(aware datetimes step in UTC and convert back; naive datetimes keep the old arithmetic)
and routed through it: `coordinator.py` `_price_series`, `_weather_series`,
`_apply_open_meteo`, `_forecast_arrays`, `_horizon_step_starts`; `optimizer.py`
`_Horizon.timestamps` and `optimize`'s `step_datetimes`. Result:

- misaligned **0** on all six transition days, plain day **0**;
- `plan_phantom_kwh` **6.000 → 0.000** on all three spring days;
- autumn `plan_max_gap_min` **75 → 15** and `timestamps_distinct` **96** on every day
  (spring 92 → 96);
- **golden digest identical**: `2c6bef38…40547d` on the fixed tree, 0 of 55 captures moved;
- `tests/features.py` on the fixed tree: **ALL 1557 FEATURE CHECKS PASSED**, including the
  subprocess block `ALL 19 DST / QUARTER-GRID CHECKS PASSED`.

The naive guard is load-bearing, not decoration: `tests/hastub`'s `dt_util.now()` returns a
**naive** datetime and `golden.START` is naive, so an unguarded `.astimezone()` would
stamp offsets into every fixture timestamp. The finder's "no golden drift (fixtures use
naive datetimes)" is right, but only for an implementation that keeps the naive branch.

**Scope completeness — the file list is right, the line list is short by two.**
`_price_series` (5728), `_weather_series` (5849) and `_forecast_arrays` (6034) are named;
these two are not, and carry the identical expression:

- `coordinator.py:5939` `_apply_open_meteo` — `step_start = midnight + timedelta(minutes=
  FORECAST_STEP_MINUTES * (step_offset + i))`, the wall-clock key for the Open-Meteo
  irradiance overlay;
- `coordinator.py:7407` `_horizon_step_starts` — `[solve_now + timedelta(hours=i*dt_hours)
  …]`, documented as "matching the optimizer's own", feeding manual pins and plan slots.

Two lesser wall-clock adds of the same class: `coordinator.py:5810`
(`end = starts[idx] + timedelta(hours=1)` for the last price entry in `_known_prices_for`)
and `coordinator.py:2158` (`timestamps[-1] + timedelta(hours=dt_hours)` for the last plan
slot's end). Reachability in real HA is not in doubt:
`async_run_optimization` calls `self._forecast_arrays(dt_util.now())` and real HA's
`dt_util.now()` is aware local — it is the *stub* that cannot exhibit this, which is why
the suite's only DST coverage (`tests/dst_checks.py`, run by features.py under
`HASTUB_TZ`) misses it: its solve-anchor section runs on 2026-08-26, a plain day, and its
transition section covers `_window_slot`/`window_factors`, not the plan grid. Killing
single-line production mutation: the shipped `coordinator.py:5728` expression itself.

**Vote: `verify` (medium).** Deciding numbers: **84 → 0** on six transition days with
0 → 0 on the plain control, and — with the full-scope fix — phantom energy
**6.000 → 0.000 kWh**, autumn step **75 → 15 min**, golden digest unchanged across all 55
captures, 1557/1557 + 19/19 checks green. Fix scope should gain
`_apply_open_meteo` and `_horizon_step_starts`.

---

## D2-04 (medium) — sysid confidence cannot reach its 0.3 gate at the default interval

**My number.** Finder's harness reproduced exactly: `sysid_clean_confidence_30min = 0.107`,
`_15min = 0.250`, ceilings 0.280 / 0.600, gate 0.300; `white_0` median UA bias
**+0.0000** with adopted fraction 0.000; `drift_0.10Kph` mean confidence **0.304**,
adopted fraction **1.000**, median UA error **−0.1216**; `drift_0.15Kph` **0.341** /
**1.000** / **−0.2368**; quantisation 0.1 K → UA +0.0008, 0.5 K → UA −0.0736, C +0.3841.
`thread_factor=1.000`, `load1=2.49`.

**My own metric** (`sysid_interval.py`): *max over the config flow's own interval range*
of `identify().confidence` on a noise-free exact first-order room, against the 0.3 gate —
the scope-complete version of "cannot reach its gate". The range is
`config_flow.py: _number(10, 120, 5, "min")`, i.e. 23 selectable values.

**Perturbation outcome — both move, in the stated directions.**

*Sampling interval* (a config change, `CONF_OPTIMIZATION_INTERVAL`), noise-free, monotone
across the whole slider:

| interval | samples | rows | confidence | ceiling | adopted |
|---|---|---|---|---|---|
| 10 min | 24 | 23 | **0.3695** | 0.800 | **yes** |
| 15 min | 16 | 15 | 0.2500 | 0.600 | no |
| 20 min | 12 | 11 | 0.1676 | 0.440 | no |
| **30 min (default)** | 8 | 7 | **0.1067** | **0.280** | no |
| 45 min | 6 | 5 | 0.0855 | 0.200 | no |
| ≥ 60 min | ≤ 4 | ≤ 3 | 0.0000 | ≤ 0.120 | not completed ("not enough samples") |

`sysid_clean_confidence_max_over_config_range = **0.3695** at 10 min`,
`sysid_clean_adopted_intervals = **1 of 23**`. The 30 → 15 min perturbation is confirmed
(0.1067 → 0.2500 up, ceiling 0.280 → 0.600 up), and the experiment shape that fixes the
row count is production, not a harness choice: `SysIdConfig.step_hours = 2.0`,
`relax_hours = 2.0`, `max_excursion_c = 0.8`.

*Noise* σ → 0, 200 seeds per cell, at both intervals: UA bias
−0.02785 (σ=0.10) → −0.02172 (0.05) → −0.01755 (0.02) → **+0.00000** (σ=0) at 30 min, and
−0.01143 → −0.01340 → −0.01482 → **+0.00000** at 15 min. To zero, confirmed; the estimator
is unbiased and the gate is what is wrong, as the finder says.

*Drift* rate → 0 at 15 min: confidence 0.3786 → 0.3411 → 0.3036 → 0.2661 → **0.2500** and
UA bias −0.3524 → −0.2368 → −0.1216 → −0.0300 → **+0.0000** for 0.20/0.15/0.10/0.05/0.00 K/h.
Monotone to zero; adoption crosses the gate between 0.05 and 0.10 K/h. The adverse
selection is exactly as claimed.

**Fix-shipability.** Nothing to test on the goldens: the fixtures never run
`SystemIdentification`, and the finder proposes a design change ("size the confidence to
the experiment the comfort bound allows … reject fits whose relax-phase residuals trend")
rather than an edit. `expected_golden_drift = []` is right.

**Scope completeness, and where the claim over-reaches.** The claim text —
"so no result is ever adopted" — is scoped to the default interval and is true there
(ceiling 0.280 < 0.300). Across the interval range the *user can actually select*, it is
false: at 10 min a clean experiment scores **0.3695** and is adopted with UA recovered
exactly (0.200000). Severity is bounded twice over:

1. **`DEFAULT_SYSID_ENABLED = False`** (`const.py:437`) — the whole path is opt-in and off
   by default; `_run_system_identification` is gated on it (`coordinator.py:10541`).
2. The adopted result is *blended*, not written:
   `blended = (1−conf)·current + conf·scale`, then clamped by
   `_apply_house_heat_loss_scale`. From my executed confidences and biases that is a
   one-shot **−3.69 %** shift in the learned house heat-loss scale at 0.10 K/h drift and
   **−8.08 %** at 0.15 K/h, with `_house_heat_loss_samples` floored at 6.

Same class elsewhere: the confidence law is local to `sysid.py:453-459`; the four learner
chokepoints are clamp-guarded (`learner_clamps.py`: 4 learners, 0 violations) and share no
gate with this one. The named files (`sysid.py`, `coordinator.py`) are the right two.

**Vote: `weaken(low)`.** The mechanism, the arithmetic and every claimed number reproduce
exactly and I do not dispute them. Deciding numbers for the severity:
`sysid_clean_confidence_max_over_config_range = **0.3695 ≥ 0.300**` (1 of 23 selectable
intervals clears the gate, so the ceiling is a default-value problem rather than a
structural one) and `DEFAULT_SYSID_ENABLED = **False**` with a bounded, clamped,
one-shot **−3.7 % / −8.1 %** consequence. It takes a conjunction — the owner enables an
experimental feature *and* the sensor drifts ≥ 0.10 K/h — to reach the live model. Low.

---

## D2-05 (low) — `wood_share` is discontinuous at the flow curve

**My number.** `wood_share_max_jump = **1.0000**` at `hp_temp = 45.000`
(w(flow−1e-6) = 0.000 → w(flow) = 1.000), `wood_share_jump_cells = 21`,
`drop_most_favourable = 0.9500`, `wood_share_times_drawn_jump = **13.4400 kW**` of a
13.440 kW draw, `wood_share_vec_parity = 0.000e+00`, `range_ok = 1`.
Identical to the report. `thread_factor=1.000`, `load1=2.50`.

**Metric definition.** |w(flow_set, hp, flow_set, floor) − w(flow_set − 1e-6, hp, flow_set,
floor)| over 21 `hp_temp` cells in [flow_set − margin, flow_set], flow_set 45 °C,
floor 21 °C, `WOOD_TANK_MIN_MARGIN = 2.0`.

**Perturbation outcome — moves to zero.** `model_sanity.py --perturb`:
`wood_share_max_jump` 1.0000 → **0.0000**, `wood_share_times_drawn_jump` 13.4400 →
**0.0000 kW**, `drop_most_favourable` 0.9500 → 0.0000. Not void. Method note: the
harness's `--perturb` rebinds only its own module-level `wood_share`, leaving
`tm.wood_share` and `_wood_share_vec` untouched — so the `wood_share_vec_parity = 0`
it prints under `--perturb` is measuring the *unperturbed* pair. I therefore re-ran the
change as a real production edit.

**The fix as a production edit** (`/tmp/verify-D2-3/repo_wood`: region 3 becomes
`max(wood − hp, wood − flow_set + margin)/margin` in **both** `wood_share` and
`_wood_share_vec`'s `v3`):

- `wood_share_max_jump` **1.0000 → 0.0000**;
- across the *full* hp range (501 cells, 20–70 °C, not just the 21-cell margin window):
  `wood_cliff_max` **1.000000e+00 → 1.004157e-05**, cells with a jump above 1e-3
  **20 → 0**; by region, the cliff is entirely region 3 (hp ≤ flow_set)
  `1.000000e+00 → 5.000000e-07` while region 2 (hp > flow_set) was already continuous and
  stays at 1.004157e-05 — both residuals are just the 1e-6 K probe step, i.e. genuinely
  continuous;
- scalar/vector parity preserved: `wood_share_vec_parity = 0.000e+00` after both edits;
  `range_ok = 1`; 0 monotonicity violations in `wood_temp`.

**It changes nothing else on the 101×101 grid.** `wood_grid.py` compares the edited law
against an independent reference implementation of the shipping law over
`wood_temp × hp_temp ∈ [20,70]²` at 101×101 = **10201 cells**:

| | baseline | fixed |
|---|---|---|
| `wood_grid_cells_moved` | 0 | **12** |
| `wood_grid_max_abs_delta` | 0.0000 | 0.7500 |
| moved in region 1 / region 2 | 0 / 0 | **0 / 0** |
| moved in region 3 | 0 | 12 |
| moved **outside** the switch corner | 0 | **0** |

All 12 moved cells lie in the switch corner (region 3 with `hp > flow_set − margin`,
200 cells of the 2550 region-3 cells) — which is the corner the finding is about.
Nothing in region 1, nothing in region 2, nothing outside.

**Fix-shipability: exactly one golden moves, not three.** Golden digests under the wood
fix vs baseline: `golden_digest_all` `2c6bef38…40547d` → `5a785e0f…3b6d`, with
**1 of 55** captures changed — `wood_two_tank_smart_write`. `wood_two_tank` and
`wood_coil`, both on the finder's `expected_golden_drift` list, are **byte-identical**.
The fix costs one fixture re-record.

**Scope completeness.** Both copies of the law are in the named file and both must move
together (the finder's `proposed_fix_scope` says so; the harness's perturbation does not).
Other discontinuous share laws: the neighbouring `dhw_coil_draw_reduction` is continuous
(`conservation.py`: 28 of 1426 cells off by 4.441e-16, ulp-level), and the one other
genuine cliff in this area is the defrost derate's bucket edge —
`derate_jump_at_0C_edge = 0.2000`, a 20 % COP step across 1e-9 K, which the finder
correctly files as bucketed-by-design in the non-findings table rather than as a second
finding. No third instance found.

**Vote: `verify` (low).** Deciding numbers: `wood_share_max_jump` **1.0000 → 0.0000** and
`wood_cliff_max` **1.000000e+00 → 1.004157e-05** under the production edit, with
**12 of 10201** grid cells moved and **0 outside the switch corner**, and **1 of 55**
golden captures moved (`wood_two_tank_smart_write` only — `expected_golden_drift`
over-lists `wood_two_tank` and `wood_coil`).

---

## Summary

| finding | vote | deciding number |
|---|---|---|
| D2-01 | `verify` (high) | parity 2.536e+74 → 0 and objective gap 53.8845 → 0.0000 under the fix; golden digest byte-identical on all 55 captures; features.py 1557/1557 |
| D2-02 | `verify` (medium), fix scope refuted | perturbation 7 → 0, but the proposed formula leaves 6 of 6 cells non-monotone and differs from shipping by 6.661e-16 over the fixture domain — no fix, and no drift in the nine listed fixtures |
| D2-03 | `verify` (medium) | 84 → 0 on six transition days, 0 → 0 on the plain control; full-scope fix takes phantom energy 6.000 → 0.000 kWh and the 75-min step → 15 min with 0 of 55 goldens moved |
| D2-04 | `weaken(low)` | max clean confidence over the configurable range is 0.3695 ≥ the 0.300 gate (1 of 23 intervals), and `DEFAULT_SYSID_ENABLED = False`; consequence is a clamped one-shot −3.7 % / −8.1 % |
| D2-05 | `verify` (low) | jump 1.0000 → 0.0000; 12 of 10201 grid cells moved, 0 outside the switch corner; 1 of 55 goldens moved, not 3 |
