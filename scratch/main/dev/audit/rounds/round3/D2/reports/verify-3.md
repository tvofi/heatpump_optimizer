# D2 panel — verifier 3 of 3, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Machine: 8-core Apple M1,
8 GB, shared box. Assigned line of attack: **the metric itself** — whether each
harness measures the thing its claim names.

Everything below is a count, an exact-integer comparison, a residual or a ratio
of pure arithmetic. **No wall, CPU or RSS number appears in this report**, so
contention cannot move any of it, and the three finder harnesses reproduced
**bit-identically** against the finder's own recorded output (`out_*.txt`) with
only the environment footer differing. `thread_factor` ran 0.10–0.98 on every
run: below 1.0 throughout, which is the process being descheduled under load
rather than a BLAS thread inflating `process_time`, and irrelevant here because
nothing timed is reported. `load1` 23.1–49.9 on my runs, against the finder's
recorded 21.6–99.7.

Constraints honoured: no `tests/stress.py`, no full `./tests/run.sh`, no gate
lock, no `gh`, no GitHub, no other verifier's output, no audit register. The
five BLAS variables were pinned to `"1"` before numpy on every run (via
`d2lib`, and again in the environment). Everything I wrote lives under
`tools/audit/round3/D2/verify-3/`; no production or test file was modified.

## Re-runs of the finder's harnesses, as their headers say

| harness | headline | finder recorded | I got | `thread_factor` | `load1` |
|---|---|---|---|---|---|
| `cop_monotonicity.py` | `violating_flow_temps` | `7_of_7` | `7_of_7` | 0.1835 | 48.35 |
| | `worst_drop_kelvin_band_-20_20` | 0.02093 | 0.02093 | | |
| `dst_window_factors.py` | `total_mismatched_cells` | `12_of_12` | `12_of_12` | 0.1051 | 48.48 |
| | `peak_cost_autumn unpriced` | +180.0000 | +180.0000 | | |
| `sysid_bias.py` | `driftgrid_d0.05_sigma0.02` adopted | −0.1340 (59/59) | −0.1340 (59/59) | 0.2219 | 43.45 |
| | `driftgrid_d0.1_sigma0.02` adopted | −0.2454 (57/57) | −0.2454 (57/57) | | |

Every RESULT line except the footer is byte-identical to the finder's recording
(`diff` output in `verify-3/rerun_*.txt`).

### Two stale harness headers — reported, not vote-changing

Both are in the `EXPECTED at baseline` block, which the audit README makes part
of the harness contract and which a judge re-running blind would key on:

* `cop_monotonicity.py` says `violating_flow_temps=6 of 7` and
  `worst_drop_kelvin_band_-20_20=0.15959`. The harness prints `7_of_7` and
  `0.02093`. The 0.15959 is within 5e-5 of the observed
  `band_flow_60 loss_peak_to_20C=0.15964`, so the header appears to carry a
  value recorded under a different name at an earlier revision.
* `dst_window_factors.py` says `total_mismatched_cells=8 of 12` and
  `mismatches_autumn_60min_peak_hours=2`. The harness prints `12_of_12` and
  `4_of_48_windows`.

`REPORT.md` carries the correct values in both cases, so this is header rot,
not an inflated finding. It should still be fixed before a judge re-runs.

---

## D2-01 — COP non-monotone in outdoor temperature under the Carnot flow ratio

**Vote: `verify`. Severity `medium`, as filed.**

### My own number and metric

Harness: `verify-3/v3_cop_reach.py`.

> **Metric (mine):** `dense_flow_violating_fraction` = the fraction of a dense
> flow grid above `cop_flow_reference_temp` (140 values, 35.05 → 70.00 °C, step
> 0.25) whose `compute_cop` strictly decreases somewhere on a 0.5 K outdoor
> sweep, with the minimum-lift-clamp regime excluded; and
> `batch_ratio_spread` = the relative spread of (marginal COP recovered from
> `simulate_trajectory_batch`) / (`marginal_cop(store="buffer")`) over that
> sweep.

The finder's metric counts strictly-decreasing adjacent pairs on a **7-point**
flow grid over −20 … +35 °C with the clamp regime included. The two are
comparable in direction; mine replaces the 7-point grid with a continuum and
takes the number from the integrator the solver actually runs.

```
dense_flow_full_-20_35 = 140 violating of 140   (fraction 1.0000)
dense_flow_band_-20_20 = 115 violating of 140   (fraction 0.8214)
   carnot_off arm:         0 of 140  in both ranges
batch_Tbuf45 = ratio_spread 1.769e-11, decreasing_pairs_band  6 of 80
batch_Tbuf55 = ratio_spread 1.792e-11, decreasing_pairs_band 14 of 80
batch_Tbuf65 = ratio_spread 3.362e-11, decreasing_pairs_band 18 of 80
   carnot_off arm: 0 of 80 at every buffer temperature
```

### Attacks run

**1. Is the "for every flow temperature" quantifier earned?** A claim over a
continuum executed on 7 points is where this repository has been caught before.
Executed on 140 flow values: **140 of 140** violate somewhere over −20 … +34 °C,
so the claim as written ("over part of its range") holds. Inside the
heating-relevant band it holds for **115 of 140** — the 25 that do not are the
flows from 35.05 to about 41 °C, which invert only above +20 °C. The finder
reports both ranges separately and does not lean on the band arm, so the
quantifier is not over-stated.

**2. Is the aggregate a clamp artefact?** The `max(ref + 273.15 - t_out, 1.0)`
minimum-lift clamp engages for any outdoor above 34 °C. Excluding that regime
entirely leaves the counts above unchanged, and
`flows_violating_only_via_min_lift_clamp = 0`. I checked the suspicious
`flow_36` cell directly (`peak_at=35C`, `worst_step=0.52670`): its
strictly-decreasing pairs all lie at outdoor **≥ 27 °C**, which is where the
nameplate factor hits its 1.5 cap — the mechanism the finding names. The
clamp then produces a spurious upward spike at 34.5/35 °C, which is a separate
artefact and is not what the count rests on. **Not a grid artefact.**

**3. Does the plan see it, or only a helper?** This was the sharpest attack
available, because `compute_cop` is not what the solver integrates. I recovered
the marginal COP **from `simulate_trajectory_batch` itself**: explicit Euler
evaluates every flux at the start state, so raising one step's power by `dP` and
differencing the resulting buffer temperature isolates `cop·dP·dt / C_buffer`
with every loss and valve draw cancelling. The ratio of that to
`marginal_cop(store="buffer")` is constant to **1.8e-11** across the whole
sweep, and the batch-implied curve carries **6 / 14 / 18** decreasing pairs of
its own at buffer temperatures 45 / 55 / 65 °C. The parameters came from
`ThermalParameters.from_config` on a real `mixing_valve_mode="manual"` config,
so `cop_flow_carnot` was set by production. **The inversion is in the path the
plan integrates, not only in a helper.**

**4. Perturbation.** `cop_flow_carnot = False` takes every arm to exactly zero —
dense grid 0 of 140 in both ranges, batch 0 of 80 at all three buffer
temperatures. The number moves under its own perturbation, in the stated
direction. Not void.

**5. Reachability in real HA, not the stub.** No `FakeHass` is used anywhere in
this arm; `ThermalParameters.from_config` and the model are driven directly.

**6. Severity by consequence.** Inside the heating band the relative loss from
peak to +20 °C is 1.07 % (45 °C flow), 5.73 % (55 °C), 9.66 % (65 °C), and the
worst single 0.5 K step is 0.02093 COP. The 63 % figure lives above +20 °C where
a heat pump is barely heating. A violated physical bound with a bounded cost and
no measured money consequence is `medium` on COMMON.md item 7. The finder
declined to assert a money figure, which is the right call. **`medium` earned;
I would not raise it.**

### One narrowing the finder's report should carry

`REPORT.md` says the expression "is inlined in `simulate_trajectory_batch`
(verified here to be bit-identical to the scalar one) … so the inversion reaches
the settlement terms as well as the simulation." The inline at
`thermal_model.py:2554` sits **inside the `if p.two_zone_enabled:` branch**. The
single-zone batch branch (`:2708` onward) computes
`cop = nameplate · min(factor,1.5) · scale` with the derate and applies **no
flow correction at all**. Measured: on a single-zone `manual`-valve config,
`from_config` still sets `cop_flow_carnot=True` — so `marginal_cop(store=
"buffer")` and every settlement term carry the inversion — while the batch
buffer state does not move at all (`single_zone_batch_Tbuf55 implied = 0.00000`
at both ends of the sweep; the buffer is not a state on that branch).

So on the single-zone throttling-valve topology the settlement price and the
simulation disagree about the flow-temperature cost. That is a different
phenomenon from D2-01 and I am not filing it; it belongs in whichever stage owns
the topology seam, by `finding-propagation.md`. It does not weaken D2-01 — it
narrows the sentence "reaches the simulation" to the two-zone topology, where I
measured it directly.

---

## D2-02 — the capacity-tariff mask walks the wall clock; the plan walks UTC

**Vote: `verify`. Severity `high`, as filed.**

This was the one I was told to break if any could be broken. It did not break.

### My own number and metric

Harness: `verify-3/v3_meter_vs_plan.py`.

> **Metric (mine):** `meter_vs_window_factors` = the number of ordinal metering
> windows over a 48 h horizon where the billing factor **`PeakTracker` actually
> recorded** for the window containing real instant `start + i·dt` differs from
> `window_factors(tariff, start, n, dt)[i]`. `meter_vs_utc_step_starts` is the
> same count against `sample_factor(_utc_step_starts(...)[i])`.

The finder's metric compares two pure functions and **nominates**
`_utc_step_starts` as the truth a priori. Mine takes the reference from the
realised state of the production object that sends the bill, and never calls
`sample_factor` on the meter side at all: the tracker is driven forward with
`observe(when, …)` at real instants — the way `coordinator.py:7719` drives it
with `dt_util.now()` — and the factor is read off `_window_factor` after
production set it.

```
TOTAL_meter_vs_window_factors   = 70
TOTAL_meter_vs_utc_step_starts  = 0
verdict_which_clock_the_meter_keeps = utc_step_starts
ordinal_misaligned = 0 in every one of the 12 cells
CONTROL (2026-10-18, ordinary Sunday) = 0 and 0
```

### Attacks run

**1. Does the sign flip? Is `window_factors` the correct clock and
`_utc_step_starts` the bug?** This is the question the finder's metric assumes
away, and if the answer were yes the proposed fix would *introduce* the defect.
It is not. `PeakTracker.observe` computes `slot = _window_slot(when, window)`
from the **real instant** and sets `self._window_factor = tariff.sample_factor(
slot)`; `_window_slot` transfers `when.fold` for windows of 60 minutes or less,
so the autumn transition's two passes of 02:00 produce two distinct window keys
and two separately metered windows. Driven forward over real instants the
tracker's realised factor sequence matches the UTC reference in **0 of 70**
disagreements and matches `window_factors` in **70**. The ordinal alignment is
sound — the meter's i-th window opens within one window length of the plan's
i-th step in every cell (`ordinal_misaligned = 0`), so the comparison is
well-formed rather than an off-by-one dressed up as a finding. **The sign does
not flip.**

**2. Is the plan's step clock really the UTC one?** Read, not assumed:
`coordinator.py:5996` aligns prices to `_utc_step_starts` by each entry's own
timestamp; `optimizer.py:2308` builds the comfort-band, temperature-bound and
DHW-window hour-of-day array from `_utc_step_starts`; `_Horizon.timestamps`
(`optimizer.py:1247`) is the same call. `window_factors` is the outlier. I
measured the resulting internal inconsistency: within one solve, the objective's
own step-hour array and the mask's window instants carry different hours for
**45 of 48** steps on the autumn day and **46 of 48** on the spring day
(`verify-3/v3_fix_blast_radius.py`) — indices 0–2 and 0–1 respectively agree,
everything from the transition onward is shifted by one hour. Two clocks inside
one objective.

**3. Would the golden fixtures move — is the fix larger than stated?**
`tests/golden.py:START` is `2026-01-15T00:00:00` with `tzinfo=None`, and there
are 49 scenarios. Executed against a candidate UTC-walked `window_factors` over
27 cells (3 window sizes × 3 masks — including the one masked golden topology's
`peak_months={11,12,1,2,3}`, `peak_hours=((7,19),)`, `weekdays_only=True`,
`offpeak_factor=0.5` — × 3 horizon lengths): `golden_start_cells_changed =
0_of_27`, and `0_of_9` even with `START` made zone-aware. Swept over all 365
local midnights of 2026: `ordinary_days_changed = 2`,
`transition_days_changed = 2`. The four days are **2026-03-28, 2026-03-29,
2026-10-24, 2026-10-25** — the two transitions plus the two days before, which a
48 h horizon reaches over; at a 24 h horizon only the transition days themselves
change. **No golden drifts. The fix does not drag the claim-file protocol in.**

**4. Is the path reachable in real Home Assistant, or only through the stub?**
No `FakeHass` anywhere in this arm. Production `start_time` is
`_solve_anchor(dt_util.now())` (`coordinator.py:4815`), and `dt_util.now()`
returns an aware datetime — confirmed under `HASTUB_TZ=Europe/Stockholm`:
`2026-09-11 00:56:37+02:00`, `tzinfo Europe/Stockholm`. An aware `start_time` is
what makes `slot0 + timedelta(...)` wall-clock arithmetic, so the defect fires on
the real path.

**5. Is the reach only the midnight start the harness uses?** No — it is wider
than the finder claims. Sweeping every quarter-hour solve anchor across the
three days around each transition (`verify-3/out_v3_solve_anchor_reach.txt`),
**172 of 288** anchors produce a mismatched factor vector, at both transitions;
the hours the plan scores free that the meter bills at full rate total 144
(autumn) and 248 (spring) across those anchors. So roughly 43 hours' worth of
solves per transition are affected, not one solve per year.

**6. Null control.** Re-taken independently: an ordinary Sunday gives 0 and 0 on
my metric, and the finder's `null_control_non_dst_day_mismatches=0` and
`unpriced=+0.0000` both reproduce. The second control (`no_mask_returns_none =
True`) reproduces, so the term really is inert unmasked. The number moves to
zero under its own stated perturbation. Not void.

**7. Is the existing coverage really blind to it?** `tests/dst_checks.py:287`
is the only `window_factors` check that touches a DST day, and it starts the
horizon at `datetime(2026, 10, 25, 13, 30)` with a 120-minute window — ten hours
after the 03:00 transition, so it never crosses the fold; it pins the *anchor*
behaviour, not the walk. `features.py` is the only other file that mentions
`window_factors`. The finder's coverage claim is accurate.

**8. Severity by consequence.** The plan charges 0 for hours the meter bills at
1.0, and the published `peak_cost` / `peak_kw` figures are wrong on those days —
a wrong published value, which is `high` on COMMON.md item 7. It is not
`critical`: it fires on four days a year, only for installs that configure a
mask, and the cost is bounded by one month's capacity-bill increment. The
closed loop is real, though, and worth recording: `coordinator.py:4845` feeds
`_peak_tracker.threshold_kw(tariff)` — built from the meter's realised,
correctly-labelled peaks — into `ctx._opt_config.peak_threshold_kw`, so the
plan and the meter share a bill while disagreeing about which hour sets it.
**`high` earned; I would not raise or lower it.**

### On the money arm

The finder's 180-currency figure scores a hand-built plan (9 kW parked in the
first free-but-billed hour). That is a constructed arm, not a solved one, and
the finder says so. I did not replace it, and I did not need it: my vote rests
on the 70-versus-0 clock number and the 172-of-288 reach, neither of which is a
money figure. A judge wanting a money number should get it from a real solve on
a transition day, which nobody on this panel has executed.

---

## D2-03 — a drifting room sensor lands in the identified heat-loss coefficient

**Vote: `verify`. Severity `high`, as filed — with one correction to the
report's consequence sentence.**

### My own number and metric

Harness: `verify-3/v3_sysid_adoption.py`.

> **Metric (mine):** `ua_scale_after_adoption` = the median over 60 seeds of
> `ThermalParameters.house_heat_loss_scale` **after the production
> `coordinator._adopt_system_identification()` has run**, on a real
> `HeatPumpOptimizerCoordinator` whose configured `heat_loss_coefficient` is the
> synthetic plant's true UA, so a perfect fit must land on exactly 1.000 and any
> deviation is the multiplicative error the planner then heats the house with.

The finder's metric stops at the estimator's own relative error and applies the
adoption gate as a re-implementation. Mine runs the gate, the confidence blend
and the clamp in production code and reads what the model ends up believing.

```
                          finder (estimator)   mine (model, after adoption)
sigma 0.02, drift 0.00      -0.0211  (null)      0.9835   (-1.65 %)
sigma 0.02, drift 0.02      -0.0662             0.9536   (-4.64 %)
sigma 0.02, drift 0.05      -0.1340             0.9034   (-9.66 %)
sigma 0.02, drift 0.10      -0.2454             0.8547  (-14.53 %)
sigma 0.02, drift 0.20      -0.4756             0.8541  (-14.59 %)
NULL CONTROL sigma 0, drift 0                   0.99999981
clamp_binding = False        perturbation_monotone_in_drift = True
```

### Attacks run

**1. Does the adoption path actually blend the biased coefficient in?** Yes,
executed end-to-end rather than read. `_adopt_system_identification`
(`coordinator.py:10599`) gates on exactly `result.completed and
result.confidence >= 0.3` — the harness's re-implementation is faithful —
computes `scale = result.heat_loss_kw_per_c / base_u`, and blends
`(1 - confidence)·current + confidence·scale` into
`_apply_house_heat_loss_scale`. Driving a real coordinator over
`FakeHass`/`FakeEntry` and calling the production method leaves
`_thermal_params.house_heat_loss_scale` at the values above, which
`effective_heat_loss_coefficient` (`thermal_model.py:1462`) multiplies on every
later solve. **The bias reaches the model.**

**2. Is there a later clamp that bounds the damage?** This was the stated
`weaken` condition and it is **not met**. `_apply_house_heat_loss_scale` clips to
`[HOUSE_HEAT_LOSS_SCALE_MIN, MAX] = [0.3, 3.0]` — two orders wider than the
effect — and `clamp_binding = False` on every one of the ten cells, meaning the
clip never engaged at all. A clamp that never fires is not a mitigation and
cannot be cited as one.

**3. What *does* attenuate it, and by how much?** The confidence blend, which
the finder names but does not quantify. Median confidence runs 0.742 at
σ = 0.02 for low drift and collapses to 0.329 at d = 0.20, so the model-level
error is roughly 60–65 % of the estimator-level error and **saturates near
−15 %**: at d = 0.20 the estimator is −47.6 % but the model only reaches
−14.59 %, because the gate stops adopting (27 of 46).

This is the one correction I would make to the report. The claim as filed — "a
0.05–0.10 °C/h drift makes **identified** UA 13–25 % too low" — reproduces
exactly and is correct. But `REPORT.md`'s consequence sentence, "A house
modelled as losing 13–25 % less heat than it does", overstates by about 1.7×:
the house is modelled as losing **9.7–14.5 %** less. The finding survives the
correction; the sentence should be restated.

**4. Null controls, re-taken.** σ = 0, d = 0 lands on 0.99999981 — the pipeline
recovers an exactly-generated plant. σ = 0.02, d = 0 lands on 0.9835, so white
noise alone costs 1.65 % and the remaining 8–13 % is the interaction with the
drift, not either alone. Both controls behave.

**5. Perturbation.** Raising the injected drift along the σ = 0.02 row moves my
number monotonically away from 1.000 (`perturbation_monotone_in_drift = True`),
one-signed and in the stated direction, until the confidence gate saturates it.
The number moves under its own perturbation. Not void.

**6. Is the aggregate a grid artefact?** The finder's grid is 20 cells with
range 0.5853 and a leave-one-out that drops the worst (d = 0.20, σ = 0.10, one
fit, zero adoptions) and lands on −0.4756. My ten cells are all one-signed and
the two the finding rests on (d = 0.05 and d = 0.10 at σ = 0.02) have
**59/59 and 57/57 adoption** — no cell selection is doing any work there.

**7. `FakeHass` caveat, stated rather than buried.** My coordinator is built on
`FakeHass`, but only to call one synchronous method; no executor boundary and no
event loop are involved, so the trap in the audit README does not apply. I did
stub `coordinator._spawn` to a no-op so the persistence coroutine is not
scheduled — that suppresses a write to the store and nothing else; the number is
read from `_thermal_params` before any persistence would matter.

**8. Two aggravating factors found while checking, recorded not filed.**
(a) `_adopt_system_identification` also sets `_house_heat_loss_samples =
max(current, int(20·confidence))`, which pins the passive learner's sample count
so later passive evidence corrects the biased scale more slowly.
(b) `sysid.py:770-780`'s excursion guard — added, by its own comment, because
"a 0.10 °C/h drift came to be adopted at confidence 1.000" — corrects the
excursion by subtracting the **estimated** drift, `deltas - drift_c_per_h ·
a[:,3]`. In exactly the cells this finding is about, that estimate has collapsed
to ≈ 0.000, so the guard designed to catch this failure is disabled by the same
collapse that causes it. That is why the biased fits are adopted at confidence
0.74 rather than being caught.

**9. Severity by consequence.** A house modelled as losing ~10–15 % less heat is
planned with too little heat: wrong comfort, silently, which would be `critical`
on COMMON.md item 7 — but `SysIdConfig.enabled` defaults to `False`
(`sysid.py:93`), so the feature is opt-in, and the blend bounds the damage near
−15 %. A defect with a workaround and a bounded cost sits between `medium` and
`critical`; the finder's `high` is the right call and is not inflated.
**`high` earned.**

---

## Summary

| id | vote | severity | my executed number | finder's number |
|---|---|---|---|---|
| D2-01 | verify | medium | 140 of 140 dense flows violate over −20…+34 °C (115 of 140 in band); batch-implied marginal COP 6/14/18 decreasing pairs, ratio spread 1.8e-11 | `violating_flow_temps=7_of_7`, worst band step 0.02093 |
| D2-02 | verify | high | meter vs `window_factors` = **70**; meter vs `_utc_step_starts` = **0**; 0 goldens move, 4 days a year change; 172 of 288 solve anchors affected | `total_mismatched_cells=12_of_12` |
| D2-03 | verify | high | `ua_scale_after_adoption` 0.9034 / 0.8547 (−9.66 % / −14.53 %) through production adoption; `clamp_binding=False` | −0.1340 / −0.2454 identified |

Nothing on this panel rests on a timing number, so nothing here is provisional
for contention. Three items a fixer or judge should carry forward: the two stale
harness `EXPECTED` headers; the narrowing of D2-01's reach sentence to the
two-zone batch branch (with the single-zone settlement/simulation divergence
propagated, not filed); and the restatement of D2-03's consequence figure from
13–25 % to 9.7–14.5 % at the model.

### Files

Harnesses I wrote, all under `tools/audit/round3/D2/verify-3/`:
`v3_meter_vs_plan.py`, `v3_fix_blast_radius.py`, `v3_cop_reach.py`,
`v3_sysid_adoption.py`. Outputs: `out_v3_*.txt`. Re-runs of the finder's
harnesses: `rerun_cop_monotonicity.txt`, `rerun_dst_window_factors.txt`,
`rerun_sysid_bias.txt`.
