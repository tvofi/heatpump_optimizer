# D7 round-2 — verifier seat 2 (consequence and reachability)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D7-2` (the finder's harnesses copied
in under `tools/audit/round2/D7/`, untracked; nothing under `custom_components/` or `tests/`
edited). Interpreter
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python`,
`PYTHONPATH=tests/hastub`, five BLAS thread variables pinned to 1 before every numpy import.
Machine: 8-core Apple M1, 8 GB, shared. Every number below is a count, a ratio or a
deterministic simulation value; none is a timing, so the `load1` of 3–11 during the runs does
not make any of them provisional (`thread_factor=1.0` throughout).

My seat's question, per finding: **what does a user lose, in a real Home Assistant, if this
stays as it is?** — and **is the path reachable outside the test stub?**

My harnesses are in `/private/tmp/claude-501/audit-scratch/D7-2/`:
`d7_01_consequence.py`, `d7_02_consequence.py`, `d7_02_money.py`, `d7_03_consequence.py`,
`d7_02_robust.py`, `d7_02_fixtest.py`, `d7_02_finder_pert.py`, `d7_04_reach.py`,
`d7_05_seams.py`, `d7_06_dead.py`. Each carries the harness-contract header
(metric definition, command, baseline SHA, instrumented symbol, perturbation, thread pin,
`RESULT`/`thread_factor`/`load1`/`swapins` lines).

---

## D7-01 — Active system identification cannot identify the production plant

**Re-run.** `sysid_plant.py`, exact match on every headline number:

```
RESULT cells=24  RESULT admitted_cells=0  RESULT aborted_at_production_bound=4
RESULT peak_excursion_max_at_production_bound=0.9204 C
RESULT control_cells=8  RESULT control_admitted=4  RESULT control_abs_bias_pct_max=8.056
RESULT thread_factor=1.0  RESULT load1=8.70  RESULT swapins=0
```

**Perturbation.** The finding's stated perturbation *is* the harness's positive control
(`typical_slab` with `slab_thermal_mass` 0.5 / `slab_heat_transfer` 5): `admitted_cells`
0 → `control_admitted=4`. The number moves. Not a constant.

**My own number** — `d7_01_consequence.py`. Metric, one line: *the extra electricity cost in
SEK of the five hours the production `SystemIdentification.step` overrides (1 h settle at the
holding power, 2 h forced to 0.6 × `max_electrical_power`, 2 h forced to 0 kW) against the
un-overridden plan for the same five hours, priced at `winter_typical` from 23:00 and
simulated through the production `ThermalModel`; plus whether `arm()` succeeds on the default
configuration.*

```
RESULT armed_default_config=0        RESULT armed_option_enabled=1
RESULT armed_within_min_days=0       RESULT armed_after_min_days=1
RESULT min_days_between_runs=30 days
RESULT experiment_extra_cost=-0.5623 SEK_per_experiment
RESULT experiment_energy_kwh=-0.9070 kWh
RESULT experiment_room_excursion_down=1.1387 C
```

**Attacks and what they showed.**

- *Reachability.* Reachable in real HA, but doubly gated: `DEFAULT_SYSID_ENABLED` is `False`
  (`const.py:437`), `arm()` returns `False` when the option is off (`armed_default_config=0`),
  the only caller is the `run_system_identification` **button** (`button.py:114`) — nothing
  re-arms it — and `min_days_between_runs=30` blocks a second run inside a month
  (`armed_within_min_days=0`). No executor boundary: `_run_system_identification` runs on the
  event loop after the solve (`coordinator.py:4791`), so `FakeHass`'s synchronous executor
  hides nothing.
- *Consequence, corrected.* The report's prose says the experiment is spent "on every
  qualifying night". It is not: at most once per 30 days, behind an option and a button. And
  it does **not** waste energy — my number is **−0.56 SEK and −0.91 kWh** per experiment,
  because the two forced-off hours more than pay for the two hours at 3.6 kW against a 2.03 kW
  hold. What it costs is comfort: **1.14 °C** below the baseline, against the 0.8 °C bound the
  experiment claims to enforce (the finder's `peak_excursion=0.9204 C` measures the same thing
  at the sample instants).
- *Null / leave-one-out.* The positive control passes (4 of 8 admitted, |bias| ≤ 8.06 %), so
  the harness can pass; the 24-cell leave-one-out is degenerate (all zero) but honest.

**Vote: `verify` (medium).** The severity is earned by consequence, not by argument: a shipped
feature that admits **0 of 24** cells while a first-order control admits 4 of 8, at the price of
a 1.14 °C comfort dip. It is bounded (once per 30 days, default off, no money), which is
exactly `medium` and not `high`. Two prose corrections for the register: the cadence is
30 days behind a button, not "every qualifying night", and the electricity cost is
**−0.5623 SEK**, i.e. a small saving, not waste.

---

## D7-02 — The defrost flag freezes the COP learner but not the fabric learners

**Re-run.** `learner_gates.py`, exact match:

```
RESULT ingest_house_loss_defrost=1        RESULT ingest_lower_floor_loss_defrost=1
RESULT ingest_measured_cop_defrost=0
RESULT defrost_scale_tz_f00=1.000000  tz_f20=1.041379  tz_f50=1.095282
RESULT defrost_scale_sz_f50=1.000000
RESULT thread_factor=1.0  RESULT load1=3.08  RESULT swapins=0
```

**My own number** — `d7_02_consequence.py`. Metric, one line: *terminal
`house_heat_loss_scale` after 400 real 30-min `_async_learn_house_heat_loss` cycles against a
plant whose delivered heat is cut by the **production** defrost law
(`1 − duty × DEFROST_LOSS_MULTIPLIER`, `defrost.py:115`) on a fraction f of intervals, in four
arms — (A) no defrost entity and the derate never taught, the finder's configuration;
(A2) no defrost entity but the **full production cycle** run, so `_settle_defrost` falls back
to the inferred `delivered_ratio` estimator; (B) a configured `heat_pump_defrost_entity`, the
full cycle: `_defrost_window.observe` (per-cycle level plus the listener's transitions),
`_record_accuracy` → `_settle_defrost` → `DefrostDerate.observe_duty`, which
`ThermalModel.compute_cop` then applies to the learner's own replay; (C) the finding's own
proposed gate applied on an install with no defrost entity; plus (D) the estimator's noise
floor with no defrost at all, indoor sensor quantised to 0.1 °C plus 0.05 °C noise, 5 seeds.*

```
                                    f=0.0       f=0.2       f=0.5
A   no derate (finder's arm)      1.000000    1.063476    1.150903
A2  no defrost entity, full cycle 1.000000    1.063476    1.150903   (derate stays 1.000000)
B   defrost entity, full cycle    1.000000    0.999432    1.001429   (derate 0.918 / 0.809)
C   finder's proposed gate, no
    defrost entity                1.000000    1.063476    1.150903
D   noise floor, no defrost: max |dev| 0.020293, span 0.017327 over 5 seeds
```

and the money — `d7_02_money.py`. Metric, one line: *SEK per 24 h lost = the cost of the
schedule the production `HeatPumpOptimizer` produces with the learned
`house_heat_loss_scale`, minus the cost of the schedule it produces at scale 1.0, both priced
on the same real series, over 6 price profiles × 2 weather profiles × {one zone, two zone} =
24 cells, with both schedules also simulated through the **true** model so over-heating is
visible.*

```
scale       mean SEK/day   max     min    mean %   drop-most-favourable   flat-price cell
1.000000      0.0000      0.0000  0.0000   0.000        0.0000              0.0000   (null)
1.150903     +8.8132     26.3058  1.8503  19.148       +8.0526             +7.5481
1.001429     +0.1187      2.3474 -1.0533   0.375       +0.0218             (noise)
1.020293     +0.8350      5.6006 -5.1452   1.612       +0.6278             -0.0760   (noise floor)
```

Room temperature under the 1.150903 plan runs **0.2–1.2 °C warmer** than under the honest
plan in all 24 cells, so the money is waste, not borrowed comfort.

**Perturbation — this is the decisive result.** The finding's stated perturbation is *"add the
COP learner's gate (`in_frost_band(outdoor)` and `self._defrost_window.peek(now).any_defrost`
→ return) at the top of `_async_learn_house_heat_loss`"*, with direction `to_zero` on
`defrost_scale_tz_f50`. I ran it two ways.

*(i) On the finder's own harness function* — `d7_02_finder_pert.py` installs that exact gate on
the production `HeatPumpOptimizerCoordinator._async_learn_house_heat_loss` and calls
`learner_gates.defrost_bias(0.5, two_zone=True)`, the very function the finding's number comes
from:

```
RESULT finder_defrost_scale_tz_f50_unpatched=1.095282 ratio
RESULT finder_defrost_scale_tz_f50_with_proposed_gate=1.095282 ratio
RESULT finder_perturbation_delta=+0.000000000 ratio
```

*(ii) In my own harness* (arm C against arm A): 1.150903 before, **1.150903 after**, to six
decimals.

`DefrostObservation.any_defrost` is
`self.observed and (events > 0 or duty > 0)` (`defrost.py:528-530`), and `observed` is only
ever true when a `heat_pump_defrost_entity` is configured — which the magnitude harness never
configures — `defrost_bias` never calls `_defrost_window.observe` at all. The proposed gate
cannot fire in the configuration the magnitude was measured in.

I do **not** call the finding void on this. The harness is not measuring a constant: its number
moves with its own null control (f = 0 → 1.000000, f = 0.2 → 1.041379, f = 0.5 → 1.095282).
What is void is the finding's stated **perturbation** — a schema-required element — and with it
the causal link between the ingest asymmetry the title names and the magnitude the finding
reports.

**The proposed fix, run where it CAN fire** — `d7_02_fixtest.py` and `d7_02_robust.py`.
Arm B's near-perfect cancellation at f = 0.5 holds exactly when the plant's true loss per unit
of defrost duration equals production's own belief of 1.5, and degrades when the physics
disagrees. The shipped code beats the finding's fix at multipliers 1.0 and 1.5 and loses to it
at 2.0 and 2.5 — so the fix is not uniformly wrong, but it is wrong at the nominal case.
`|scale − 1|` against the noise floor 0.020293:

```
plant loss     A: no derate    B: shipped, derate     B + the finding's proposed gate
multiplier     |dev|           |dev|   (x floor)      |dev|   (x floor)   delta
   1.0         0.095282        0.046202  (2.28x)      0.089014  (4.39x)   +0.042812  WORSE
   1.5 *       0.150903        0.001429  (0.07x)      0.071071  (3.50x)   +0.069643  WORSE
   2.0         0.213112        0.054683  (2.69x)      0.051230  (2.52x)   -0.003454
   2.5         0.283159        0.114628  (5.65x)      0.029160  (1.44x)   -0.085468
* production's own DEFROST_LOSS_MULTIPLIER
```

At the nominal physics the fix takes a converged, correct learner (1.001429, 0.07x the noise
floor) and biases it to **0.928929** — a 7.1 % UA **under**-estimate, 3.5x the noise floor,
which under-heats rather than over-heats. The reason is the failure `defrost.py`'s own module
docstring names for the COP scale and the derate: *"if both fold in the same interval, one
shortfall is corrected twice and plans in the band overshoot the compensation."* The derate is
applied to the whole temperature/humidity bucket, so dropping the defrost intervals from the
fabric learner leaves it only the intervals on which the derate over-corrects.

**Attacks and what they showed.**

- *The finding welds two different configurations into one mechanism.* The ingest table's
  defrost arm **sets** the flag (`CONTAMINATE["defrost"]` calls `_defrost_window.observe(now,
  True)`); the magnitude arm never touches the window at all. In the ingest arm's own
  configuration — a real defrost entity, the full cycle — the magnitude is **1.001429**, not
  1.095282: the production `DefrostDerate` learns duty 0.125 → factor 0.809, `compute_cop`
  applies it to the learner's replay, and the residual becomes zero-mean. 1.001429 is
  **14× inside the estimator's own noise floor** (0.020293) and its money, +0.119 SEK/day, is
  **7× below** the noise floor's own +0.835 SEK/day.
- *Reachability.* `CONF_HEAT_PUMP_DEFROST_ENTITY` is an optional v5.3.0 slot
  (`const.py:102`). Without it every `observe` call takes `flag=None`, the interval is marked
  dark, `observed` is `False` — and then (i) `_learn_measured_cop` freezes on the **whole**
  0–5 °C band (`if not window.observed or window.any_defrost: return`,
  `coordinator.py:2807-2809`), not on defrost intervals, so the asymmetry the title names does
  not exist in the form stated; (ii) `_settle_defrost` falls back to the inferred estimator,
  which `defrost.py`'s own docstring says is structurally blind to a defrost — arm A2 confirms
  it executes to a derate of exactly **1.000000**; and (iii) the proposed fix is inert.
  Both learners run on the event loop inside `_update_current_state`
  (`coordinator.py:5250-5251`), so `FakeHass`'s synchronous executor is not implicated.
- *Null control.* f = 0 holds at 1.000000 exactly in every arm; the money null at scale 1.0 is
  0.000000 SEK in all 24 cells. The flat-price cell keeps +7.55 SEK/day, which is correct and
  worth stating plainly: the mechanism is **extra energy**, not price arbitrage, so surviving
  the flat control is expected here rather than disqualifying.
- *Leave-one-out.* 24 money cells, range 1.85 → 26.31, mean with the most favourable cell
  dropped 8.05 — not carried by one cell.
- *Is the drift inside the estimator's noise?* No, in arm A: 0.1509 against a 0.0203 noise
  floor (7.4×), 8.81 SEK/day against 0.84 SEK/day (10.5×). Yes, in arm B: 0.0014 against
  0.0203 (0.07×).

**Vote: `weaken(low)`.** Decisive number: **the finding's own perturbation, applied to the
finding's own function, moves the finding's own number by `+0.000000000`.** Alongside it:
`scale_production_derate_f50 = 1.001429` against a `0.020293` noise floor, and the same gate
applied where it *can* fire moves the learner from 1.001429 to 0.928929. The finding as
written is a hygiene-grade inconsistency: adding the COP learner's defrost gate to the fabric
learners changes nothing where the harm is (no defrost entity → the gate cannot fire) and
makes the estimate *worse* at the nominal physics where the gate can fire. The 1.0953
magnitude and the medium severity rest on a configuration in which the mechanism the title
names is not present.

My arm B is not unconditionally clean — at a plant loss multiplier of 2.5 the shipped code
leaves 5.65x the noise floor — so a finding about the frost band is defensible. But it is a
finding about `DEFROST_LOSS_MULTIPLIER` being a fixed constant, not about a missing gate, and
the fix is not the one proposed.

*For the judge, not part of my vote:* the harness did uncover a real, separate phenomenon
worth re-scoping — on a flagless install the frost-band shortfall is modelled by **nobody**
(the inferred derate is blind, the COP learner is frozen band-wide, the fabric learners eat
it) and costs a measured **+8.81 SEK/day, 19.1 % of the day's cost**, on a two-zone radiator
house. That is a `medium` finding, but it is not this one, and its fix is not this one's.

---

## D7-03 — The accuracy tracker records through open-window and external-heat intervals

**Re-run.** `learner_gates.py`, exact match:

```
RESULT ingest_accuracy_record_open_window=1   RESULT ingest_accuracy_record_external_heat=1
RESULT ingest_accuracy_record_pump_offline=0
RESULT learners_ingesting_open_window=1       RESULT learners_ingesting_external_heat=1
```

**My own number** — `d7_03_consequence.py`. Metric, one line: *the shift in the three
statistics the integration publishes and acts on — `AccuracyTracker.temperature_bias()` (the
drift alarm's input, band `BIAS_BAND_C = 0.5 °C`), `temperature_mae()` and `trust()` (the
`_confidence_margins` damp) — between the shipped `_record_accuracy` and the same run with the
proposed guard `_learning_frozen(CONF_INDOOR_TEMP_ENTITY) is None`, over one full 672-sample
window (14 days × 30 min = `HISTORY_LENGTH`, the deque's maxlen) of a real coordinator driven
against a real two-zone `ThermalModel` plant with blocked, realistic contamination: a window
aired for one interval a day at 5× ventilation UA and a wood stove burning four evening hours
on three days a week at +2 kW thermal, swept over a duty multiplier.*

```
contaminated   bias shift   mae shift   trust shift   margin shift @ sigma 0.5   alarm ship/gate
  0.0 %        +0.0000      +0.0000      +0.0000            +0.0000                 0 / 0   (null)
  9.2 %        +0.0140      +0.0240      +0.0000            +0.0000                 0 / 0
 14.9 %        +0.0300      +0.0450      +0.0000            +0.0000                 0 / 0
 19.0 %        +0.0600      +0.0700      +0.0000            +0.0000                 0 / 0
 19.0 % (noisy install, plant UA 25 % off, sensor sigma 0.4 C, so trust() < 1)
              +0.0470      +0.0460      -0.0263            +0.0131                 0 / 0
```

**Perturbation.** Duty multiplier → 0: every shift to `+0.0000` exactly. The number moves; not
a constant.

**Attacks and what they showed.**

- *Consequence.* The worst measured shift in the published bias is **+0.060 °C**, against a
  drift-alarm band of **0.5 °C** — 8.3× below it. `bias_alarm_shipped` equals
  `bias_alarm_gated` equals 0 in every arm: the contamination never changes the alarm's
  verdict. The opt-in confidence margin moves by at most **+0.0131 °C** against a
  `CONFIDENCE_MARGIN_CAP_C` of 0.8 °C, and `DEFAULT_CONFIDENCE_MARGINS_ENABLED` is `False`.
- *The mechanism is overstated.* The finding says the recorded error "feeds
  `_confidence_margins` (`sigma(lead) × (1 − trust)`)". `sigma(lead)` comes from
  `lead_sigma`, filled by `score_lead_predictions`, which is **already** gated three
  statements earlier by `_learning_frozen(CONF_INDOOR_TEMP_ENTITY)`
  (`coordinator.py:9214-9220`). The only route from `record()` to the margin is `trust()`, and
  `trust()` is clipped to exactly 1.0 for any `temperature_mae ≤ 0.25 °C`, at which point
  `_confidence_margins` returns `None` outright — which is why the clean-install margin shift
  is 0.0000 rather than small.
- *The rollback is already protected.* `_snapshot_ring.observe_bias(now, bias, healthy)` takes
  `healthy = _inputs_healthy()`, which is `_learning_frozen(INDOOR, OUTDOOR, POWER) is None`
  (`coordinator.py:8754-8762`) — and that predicate **does** cover `_external_heat_active` and
  `_vent_cusum.tripped`. So a contaminated bias cannot make `auto_rollback_justified` true.
- *Reachability.* Event loop, no executor boundary; the stub is not doing any work here.

**Vote: `verify` (low).** Decisive number: **bias shift `+0.0600 °C` against a `0.5 °C` alarm
band, and margin shift `+0.0131 °C` against a `0.8 °C` cap on an opt-in that defaults off.**
The gate is genuinely missing and the fix is one line, but nothing a user can see moves: I
would record the stop-rule class as **hygiene** rather than `bug`, and drop the
`_confidence_margins` clause from the mechanism as measured-false.

---

## D7-04 — `last_buffer_trajectory` is a 5 SEK side channel with one poison

**Re-run.** `trajectory_order.py`, exact match:

```
RESULT tc_delta_abs_max=5.416717 SEK   RESULT tc_delta_rel_to_energy=0.070771
RESULT null_delta_abs=0.000000 SEK     RESULT poison_raises=1
RESULT writer_sites=3  reader_sites_optimizer=4  readers_with_model_call_between=0
RESULT thread_factor=1.0  RESULT load1=8.99  RESULT swapins=0
```

**Perturbation.** Config `mixing_valve_mode → none`: `null_delta_abs=0.000000`. Moves.

**My own number** — `d7_04_reach.py`. Metric, one line: *`stale_reads` — over real
`HeatPumpOptimizer.optimize` runs on four topologies, every `simulate_trajectory` /
`simulate_trajectory_with_dhw` return is recorded as `room_array → buffer_array` (strong
references on both sides, because `id()` is recycled the moment numpy frees an array) at the
moment it writes `last_buffer_trajectory`, and every invocation of the closure
`_terminal_cost` returns is checked for `map[room_arg] is buffer_arg`; `stale_reads` counts
the invocations where the buffer trajectory did not come from the same simulation call as the
room trajectory it is scoring.*

```
config          buffer_is_store  terminal_cost reads  from the batch path  STALE
no_valve             False              791                  768             0
store_manual         True               791                  768             0
dhw                  False              889                  864             0
store_dhw            True               889                  864             0
perturbed (one intervening simulate_trajectory per objective call)           23
RESULT configs_buffer_is_store=2 of 4
```

**Attacks and what they showed.**

- *Runtime, not AST.* Zero stale reads over 791–889 terminal-cost invocations per config, and
  **23** under the perturbation — the number moves, so it is not a constant. This confirms the
  finder's static `readers_with_model_call_between=0` dynamically and independently.
- *Reachability in real HA.* Stronger than the finder allowed for. The solve runs in an
  executor thread over a **private** optimizer and model:
  `solve_state, solve_optimizer = self._solve_snapshot()` (`coordinator.py:4733`), whose
  docstring names this exact hazard — *"the solve's per-step scratch (the buffer trajectory,
  the refused-heat carry) never lands on the live model the event loop's `simulate_step`
  callers are walking"* (`coordinator.py:4498-4501`). Real HA's real thread therefore cannot
  interleave two solves on one model, which is the case `FakeHass`'s synchronous executor
  would otherwise have hidden. The hazard is confined to a single-threaded solve, where the
  writer and the reader are adjacent.
- *Note.* 768–864 of the ~800–890 terminal-cost invocations come from the batched path, which
  gets its buffer trajectories from `simulate_trajectory_batch`'s own return dict
  (`traj["buffer"][b]`, `optimizer.py:2814`), never from the attribute — the poison at
  `thermal_model.py:2652` is a guard that is working, not a live path.

**Vote: `verify` (low, hygiene).** Decisive number: **`stale_reads = 0` over 3,360
`_terminal_cost` invocations across four topologies, 23 under the perturbation.** A latent
hazard with a real magnitude if it ever fired, and a real cleanup; today it costs a user
nothing, and `_solve_snapshot` is a second line of defence the finder did not credit.

---

## D7-05 — `coordinator.py` has one cheap seam and no others

**Re-run.** `metrics_ast.py` and `coordinator_clusters.py`, exact match on all of it:

```
RESULT coordinator_class_lines=10269  coordinator_methods=256
RESULT coordinator_instance_attrs=174  coordinator_instance_attrs_multi_writer=132
RESULT cross_attr_fraction_seeded=0.3091  cross_call_fraction_seeded=0.6609
RESULT cross_attr_fraction_k10=0.33  seam_min_cut_name=manual/plan  seam_min_cut_cost=17
RESULT attr_max_fan_in=77  attrs_fan_in_ge_20=6
RESULT thread_factor=1.0  RESULT load1=7.59 / 16.53  RESULT swapins=0
```

**My own number** — `d7_05_seams.py`. Metric, one line, and it differs from the finder's, so
both are written down:

- *Finder's:* attribute references whose attribute is **owned** (first `_init_*` assignment) by
  a cluster other than the referencing method's, over all self-attribute references — a
  **full partition** of the class, homed on the `_init_*` groups.
- *Mine:* the **minimum extractable cut** — for every method taken as a seed, grow a method set
  S greedily (add at each step whichever method minimises the resulting cut), where
  `cut(S) = |attributes referenced by both S and its complement| + |self-call edges crossing
  the S boundary|`; report the smallest cut reached at `|S| ≥ 8`, and how many **distinct**
  such sets (pairwise overlap under 50 %) sit below a threshold. No `_init_*` homing, and the
  complement is not required to be a tidy partition.

```
RESULT min_extractable_cut=12  RESULT min_extractable_cut_size=8
RESULT distinct_sets_cut_lt_25=8  RESULT distinct_sets_cut_lt_40=8
   cut 12  grid fee      (_audit_grid_fee, _current_grid_fee, _fee_series, _grid_fee_entity_value, _grid_fee_schedule, ...)
   cut 12  DHW schedule  (_dhw_current_hour, _dhw_effective_windows, _dhw_in_demand_window, _dhw_legionella_due_in_hours, ...)
   cut 13  ledger/energy (_accumulate_energy, _async_save_ledger, _close_score_day, _contract_comparison, _fold_score_sample, ...)
   cut 14  forecast      (_apply_open_meteo, _forecast_arrays, _liquid_fraction, _prepare_forecast_data, _pv_surplus_series, ...)
   cut 15  manual plan   (_async_save_manual_plan, _horizon_step_starts, _manual_pins, _manual_plan_state, _solve_anchor, ...)
   cut 15  legionella    (_async_load_dhw_legionella, _async_save_dhw_legionella, _async_track_dhw_legionella, ...)
   cut 17  weather fetch (_comparable_ts, _current_humidity, _fetch_weather_forecast, _known_prices_for, ...)
   cut 18  price fetch   (_async_first_refresh_light, _async_learn_price_shape, _fetch_solar_forecast, _fetch_tibber_prices, ...)
RESULT hub_attr_max_fan_in=77
RESULT coordinator_pyc_bytes=446361  package_pyc_bytes=1522064  coordinator_pyc_share=0.2933
```

**Perturbation.** Drop the manual-plan methods from the parsed class: `n_methods` 256 → 249
and `min_extractable_cut` 12 → **11**. The number moves; not a constant.

**Attacks and what they showed.**

- *The headline claim is false under an independent method.* The finding says *"the only seam
  with cut cost under 40 is the manual-plan group (10 methods, cut 17)"*. My search finds
  **eight distinct sets of ≥ 8 methods with cut ≤ 18**, minimum **12** — and they are not
  exotic slices, they are grid fee, the DHW schedule, the ledger, the forecast assembly,
  legionella, the weather fetch and the price fetch. Two of them (weather fetch, legionella)
  are 8-method subsets of the *same functional groups* the finder priced at 42 and 63 — they
  come out cheaper because my search is not forced to take a whole `_init_*` home, nor to
  partition the rest of the class. "One cheap seam and no others" is a property of the seeded
  clustering, not of the class.
- *Consequence, which is what my seat is for.* Nothing. There is no runtime, money or comfort
  number here at all: the finding is a claim about future work. The only measurable cost is
  that 29.33 % of the package's compiled bytecode lives in one module and a change to
  `self._config` can reach 77 of 256 methods. Neither is something a user loses.
- *Severity.* I looked for an executed number that would support anything above hygiene and
  found none. The class's size does not appear in any published value, any solve result, or
  any cost. Severity `low`/`hygiene` is correct and could not be higher on this evidence.

**Vote: `refute`.** Decisive number: **`min_extractable_cut = 12` with
`distinct_sets_cut_lt_25 = 8`, against the finding's "the only seam with cut cost under 40".**
The finding's distinguishing claim is contradicted by an independent partition search, and the
decomposition ordering it proposes ("extract the six hub attributes into a context object
first, then peel seams in cut-cost order") rests on that claim. The *metrics* it reports
(10,269 lines, 256 methods, 174 attributes, 132 multi-writer, 0.3091 / 0.6609, fan-in 77)
all reproduce exactly and are worth keeping as non-findings; it is the seam reading that does
not survive.

---

## D7-06 — Five dead defs and six production functions only tests call

**Re-run.** `dead_code.py` re-runs the gate's thirteen scripts under a `sys.monitoring`
sentinel and needs the shared gate lock; the lock was held by another agent throughout my
window (`mkdir /tmp/hpo-gate.lock` refused on four attempts, ~50 min apart at the ends), so I
did **not** re-run it and do not report a re-run number for it. Everything below is my own.

**My own number** — `d7_06_dead.py`. Metric, one line: *for each candidate def, occurrences of
its bare name (word-boundary) anywhere in the repository outside its own `def` line — every
`.py`, `.mjs`, `.js`, `.json`, `.yaml`, `.md`, `.html`, `.txt` under the tree, so a dynamic
`getattr` name, a `services.yaml` key, a translation key or a card lookup would all show —
with `ThermalModel.compute_cop` carried as the positive control; plus a `sys.monitoring`
PY_START sentinel over `tests/golden.py`.*

```
RESULT references_set_configured=0        RESULT references__translated_text=0
RESULT references_optimization_result=0   RESULT references_current_state=0
RESULT references__floor_heated_area=0
RESULT references_control_compute_cop=54          <- the positive control
RESULT unreferenced_candidates=5 of 5
RESULT dead_lines=46  RESULT package_lines=37885  RESULT dead_share_of_package=0.001214

RESULT started_set_configured=0   RESULT started__translated_text=0
RESULT started_optimization_result=0   RESULT started_current_state=0
RESULT started__floor_heated_area=0    RESULT code_objects_started=4080
```

**Attacks and what they showed.**

- *Runtime, independently.* A `sys.monitoring` PY_START sentinel over `tests/golden.py`
  (`GOLDEN_MODE=drift`, `GOLDEN_REF=c398fc84`), which drives the coordinator, the optimizer and
  the model together across all 49 scenarios, started **4,080** distinct code objects and
  **none** of the five. Not a re-run of the finder's thirteen-script sentinel, but an
  independent one with a real end-to-end driver.
- *A wider net than the finder's.* The finder's census covers production and `tests/`; mine
  covers the whole tree including `custom_components/heatpump_optimizer/www/*.js`,
  `translations/*.json`, `services.yaml`, `strings.json` and `docs/`. Still **zero** hits for
  all five, while the control returns 54. Nothing reaches them through a data key or a card
  lookup either.
- *Consequence.* 46 lines of 37,885 = **0.12 %** of the package. Nothing a user loses; no
  wrong value, no cost, no risk. Two of the five are `@property` shadows on the coordinator
  (`optimization_result`, `current_state`) that HA never reads, which is the only place a
  framework hook could have hidden a use — and neither name appears in any manifest,
  services file or card.
- *Reachability.* Not applicable: nothing to reach.

**Vote: `verify` (low, hygiene).** Decisive number: **0 references for all five candidates
across the whole tree against 54 for the control, 0 of them started among 4,080 code objects
`tests/golden.py` starts, and 46 dead lines = 0.12 % of the package.** Correct, and correctly
rated hygiene. My re-run of the finder's own harness is missing because the gate lock never
came free in my window; the judge should re-take `dead_code.py` in the quiet window if the
thirteen-script figure matters to them, but my own static and runtime halves both agree with
it.

---

## Summary of what my numbers changed

| finding | finder | seat 2 | the number that decided it |
|---|---|---|---|
| D7-01 | medium, bug | **verify** (medium) | `admitted_cells=0/24` reproduced; consequence is −0.56 SEK and 1.14 °C, once per 30 days behind a button |
| D7-02 | medium, bug | **weaken(low)** | the finding's own perturbation on the finder's own function: delta **+0.000000000**; with a defrost entity the derate gives 1.001429 vs a 0.020293 noise floor |
| D7-03 | low, bug | **verify** (low, class → hygiene) | bias shift +0.0600 °C against a 0.5 °C alarm band; margin shift +0.0131 °C against a 0.8 °C cap, opt-in off by default |
| D7-04 | low, hygiene | **verify** (low) | `stale_reads = 0` over 3,360 runtime `_terminal_cost` invocations, 23 under the perturbation |
| D7-05 | low, hygiene | **refute** | `min_extractable_cut = 12`, 8 distinct sets of ≥ 8 methods under cut 25 |
| D7-06 | low, hygiene | **verify** (low) | 0 references tree-wide for all five, 54 for the control; 0.12 % of the package |
