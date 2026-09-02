# D7 round-2 — verifier seat 1 (OWN-HARNESS stance)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D7-1` (verified clean at that SHA).
Harnesses re-run from a private root under
`/private/tmp/claude-501/audit-scratch/D7-1/root` whose `custom_components/` and `tests/`
are symlinks to that worktree (`diff -rq` against the finder's export
`audit-r2-baseline`: identical but for `__pycache__`), so no other seat's run and no
shared `*.json` output was touched. My own harnesses are in
`/private/tmp/claude-501/audit-scratch/D7-1/h/`:

| file | what it measures |
|---|---|
| `v1_sysid_residual.py` | D7-01: one- vs two-exponential fit of the captured step response; randomised admission sweep |
| `v23_learners.py` | D7-02: d(scale)/df with a power meter configured; D7-03: accuracy-vs-house-loss sample rate |
| `v4_traj_side_channel.py` | D7-04: terminal-cost spread over the schedules a real solve actually evaluates |
| `v4b_stale_runtime.py` | D7-04 non-finding: runtime staleness via a write-generation descriptor |
| `v5_hub_removal.py` | D7-05: largest connected component after hub-attribute removal (no clustering) |
| `v6_dead_sentinel.py` | D7-06: whole-tree lexical census + raising sentinel with a positive control |

Every number below is a count, a ratio or a deterministic simulation value; none is a
timing, so none is provisional under contention. `load1` during my runs was 3.4–15.3,
`thread_factor` 1.0, `swapins` 0 on every finder harness.

## Re-runs of the finder's harnesses

All five fast harnesses reproduce **exactly**, to the last printed digit.

| harness | key RESULTs I got | matches report |
|---|---|---|
| `metrics_ast.py` | `coordinator_lines=10902 coordinator_methods=256 coordinator_instance_attrs=174 …_multi_writer=132 max_cc=86 import_cycle_sccs_module_level=0` | yes |
| `coordinator_clusters.py` | `cross_attr_fraction_seeded=0.3091 cross_call_fraction_seeded=0.6609 cross_attr_fraction_k10=0.33 seam_min_cut_cost=17 attr_max_fan_in=77 attrs_fan_in_ge_20=6` | yes |
| `sysid_plant.py` | `cells=24 admitted_cells=0 aborted_at_production_bound=4 peak_excursion_max_at_production_bound=0.9204 control_cells=8 control_admitted=4 control_abs_bias_pct_max=8.056` | yes |
| `learner_gates.py` | `ingest_house_loss_defrost=1 ingest_measured_cop_defrost=0 defrost_scale_tz_f20=1.041379 tz_f50=1.095282 tz_f00=1.000000 sz_f50=1.000000 ast_learners_without_defrost_gate=15` | yes |
| `trajectory_order.py` | `tc_delta_abs_max=5.416717 tc_delta_rel_to_energy=0.070771 null_delta_abs=0.000000 poison_raises=1 readers_with_model_call_between=0` | yes |
| `dead_code.py` | `defs_total=1062 started_by_suite=983 dead_candidates=5 dead_candidate_lines=46 dynamic_reach_started_unreferenced=7` | yes |

---

## D7-01 — Active system identification cannot identify the production plant

**Re-run.** `admitted_cells=0` over `cells=24`; `aborted_at_production_bound=4`;
`peak_excursion_max_at_production_bound=0.9204 C`; `control_admitted=4` of 8,
`control_abs_bias_pct_max=8.056`. `thread_factor=1.0 load1=4.20 swapins=0`.

**My metric definition (one line).** For each production preset, the RMS
room-temperature residual and the lag-1 residual autocorrelation left by the *best-fit*
one-exponential LTI plant and by the *best-fit* two-exponential LTI plant, each fitted
by simulating its own ODE over the whole captured window (nonlinear least squares on the
trajectory, **not** a finite-difference regression like production's) against the room
trajectory `ThermalModel.simulate_step` produces under the sysid step/relax input; plus,
separately, the number of draws in a randomised sweep of experiment settings in which
`identify()` returns completed with confidence ≥ 0.3.

Comparability: production's `identify()` regresses `dT/dt` on `(T−T_out, Q, 1)` by OLS on
finite differences with a ridge on the intercept. My M1 fits the *same model class* by a
different estimator (trajectory-simulation NLS, no ridge, no finite differencing), so a
structured residual under M1 cannot be blamed on their regularisation or their
differencing. My M2 is the plant's own state structure, so it is the nested alternative
the F-test would use. The two definitions are comparable in model class, not in
estimator — which is the point: the failure survives a change of estimator.

**My numbers** (`v1_sysid_residual.py`):

| preset | room excursion | rms 1-exp | rms 2-exp | rms1 / excursion | lag-1 autocorr of 1-exp residual | sign runs |
|---|---|---|---|---|---|---|
| light_new | 4.120 °C | 0.532755 °C | **0.000000** | 12.9 % | **+0.9983** | 2 of 301 |
| heavy_old | 0.076 °C | 0.013196 °C | **0.000000** | 17.4 % | **+0.9966** | 3 of 301 |
| typical_slab | 0.328 °C | 0.049200 °C | **0.000000** | 15.0 % | **+0.9990** | 2 of 301 |

At the production 30-minute cadence the 1-exp residual is *larger*, not smaller
(0.679754 / 0.015173 / 0.057716 °C). So: the first-order fit leaves 13–17 % of the
achieved excursion as residual, that residual is essentially a single sign-coherent arc
(2–3 sign runs in 301 samples, lag-1 ≈ 0.998), and the second exponential removes
**100 %** of it. This is exactly the decisive question the panel prompt names, and it
answers yes.

Independent admission count: over **120 randomised experiment settings** (preset,
cadence ∈ {5,10,15,30} min, T_out ∈ [−5, 9.5] °C, excursion bound ∈ {0.8, 2, 5, 10} °C,
noise ∈ {0, 0.02, 0.05} °C, settle/step/relax hours drawn continuously),
`sweep_admitted_production_plant=0`. Reasons: implausible signs 53, gains outside bounds
37, excursion abort 29, `ok` 1 — and that single `ok` carried confidence < 0.3, so it
still fails the adoption gate. The finder's 24-cell grid is not the reason the answer is
zero.

**Perturbation** (report.json: collapse the slab store on the control; expected *up*).
Both of my numbers move, hard:

- relative structured residual 12.9 / 17.4 / 15.0 % → **2.0 / 2.3 / 2.1 %**;
- `sweep_admitted_collapsed_slab=59` of 120, up from 0.

The harness is not measuring a constant.

**Attacks run.**
- *Grid artefact.* Replaced the finder's 24-cell factorial with a 120-draw randomised
  sweep over a much wider setting space. Same answer (0 admitted). Leave-one-out is
  vacuous here because the aggregate is already 0/24 and 0/120.
- *Positive control.* Present and passes on both harnesses (finder 4/8 admitted; mine
  59/120 with the slab collapsed), so neither harness is structurally incapable of
  admitting.
- *Adoption gate.* I read `_adopt_system_identification` (coordinator.py:10607):
  `result.completed and result.confidence >= 0.3` — the finder's gate is the shipping
  gate.
- *Reachability / consequence.* `DEFAULT_SYSID_ENABLED = False` (const.py:437), and the
  only arm path is a **manual button press** (`button.py:114` →
  `async_arm_system_identification`), gated again by `CONF_SYSID_ENABLED`, by
  `min_days_between_runs=30`, and by `converged_samples=200` (the passive house learner
  reaches 200 samples in a few days, after which the experiment refuses to start). So the
  blast radius is: a user who sets the flag *and* presses the button, at most monthly,
  early in an install.
- *Model-vs-house caveat.* What is proved is that the identifier cannot identify the
  *production model*. Whether a real slab house is first order is not measured by either
  harness. It does not rescue the finding — the integration prices every plan through the
  two-store model and blends the sysid result into that same model's
  `_house_heat_loss_scale`, so the identifier and the plant disagreeing about model class
  is itself the defect — but it should be stated when the fix is scoped.

**Vote: `verify` (medium).** Decisive number: a first-order fit of the production plant's
own step response leaves rms 0.5328 °C with lag-1 residual autocorrelation +0.9983 and 2
sign runs in 301 samples, which the two-exponential fit takes to **0.000000 °C**; and
0 of 120 randomised experiment settings clear the adoption gate. Severity: the double
opt-in (flag off by default plus a manual button) is the one honest argument for `low`,
but a shipped feature that is structurally incapable of succeeding on every production
preset, that overrides the plan for five hours and forces the pump off for two of them,
and that reports the reason only in diagnostics, earns `medium` as the finder scoped it.

---

## D7-02 — Defrost freezes the COP learner but not the fabric learners

**Re-run.** `ingest_house_loss_defrost=1`, `ingest_lower_floor_loss_defrost=1`,
`ingest_measured_cop_defrost=0`, `ast_learners_without_defrost_gate=15`,
`defrost_scale_tz_f20=1.041379`, `tz_f50=1.095282`, null `tz_f00=1.000000`,
`sz_f50=1.000000`. `thread_factor=1.0 load1=3.68 swapins=0`.

**My metric definition (one line).** The slope d(`house_heat_loss_scale`)/d(defrost
fraction f), fitted over f ∈ {0, .1, .2, .3, .5, .8, 1.0} at 400 half-hour intervals,
measured on a coordinator that **has a power meter configured**
(`heat_pump_power_entity` set and `_measured_power` fed the *drawn* power, because a
defrosting pump keeps drawing while it stops delivering) — a configuration the finder
never ran, and a slope rather than three point values.

Comparability: same rig class (real coordinator, real learner, real model, real plant)
and the same readout variable, but seven f values instead of three, a fitted slope
instead of point values, and a metered arm the finder did not have. Directly comparable
where they overlap: my f = 0.2 and f = 0.5 reproduce the finder's 1.041379 and 1.095282
to six decimals.

**My numbers** (`v23_learners.py`):

| arm | f=0 | f=0.2 | f=0.5 | f=1.0 | d(scale)/df |
|---|---|---|---|---|---|
| two-zone, **metered** | 1.000000 | 1.041379 | 1.095282 | 1.223639 | **+0.219398** |
| two-zone, commanded | 1.000000 | 1.041379 | 1.095282 | 1.223639 | +0.219398 |
| single-zone, metered | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 |
| single-zone, commanded | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 |

Two results the finder did not have. First, the null holds at **exactly** 1.000000 and the
single-zone structural blindness holds at **exactly** 1.000000 across seven f values, not
three — so neither is an artefact of the chosen f. Second, **configuring a power meter
does not help**: the metered and commanded arms are bit-identical, because a defrosting
pump draws what it was commanded to draw and the meter therefore carries no information
about the delivery shortfall. `_interval_space_power`'s v4.0.5 shortfall guard is
precisely the guard that does not cover this case.

**Perturbation** (report.json: add the COP learner's frost-band/defrost gate at the top of
`_async_learn_house_heat_loss`; expected *to_zero*). Not separately re-run — my f = 0 arm
is the same edge of the same curve and holds at exactly 1.000000, and the finder's
executed to_zero is consistent with it. The number is not a constant: it moves
monotonically with f over seven points with slope 0.219.

**Attacks run.**
- *Is `duty=0.25` a fair defrost?* A 6–8 minute defrost inside a 30-minute interval is a
  20–27 % delivery shortfall for that interval, so `duty=0.25` is the right order. At the
  frost-band-realistic f ≈ 0.2–0.3, my curve gives 4.1–5.1 % — the low end of the
  finding's stated "4–10 %", which is honest.
- *Source.* `_async_learn_house_heat_loss` (coordinator.py:3215) gates only on
  `_learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)`; the COP learner
  (coordinator.py:2807) has the explicit `in_frost_band(...)` /
  `_defrost_window.peek(...).any_defrost` pair. The asymmetry is exactly as claimed.
- *Consequence.* Bounded (the learner walks back once defrosts stop), two-zone only, and
  the scale is a multiplicative prior on every plan's pricing. `medium` is earned.

**Vote: `verify` (medium).** Decisive number: d(`house_heat_loss_scale`)/df = **+0.219398**
per unit defrost fraction on a two-zone house **with a power meter configured**, from an
exact 1.000000 null at f = 0 and an exact 0.000000 slope in single zone.

---

## D7-03 — The accuracy tracker records through open-window and external-heat intervals

**Re-run.** `ingest_accuracy_record_open_window=1`, `…_external_heat=1`,
`…_pump_offline=0`; `learners_ingesting_open_window=1`,
`learners_ingesting_external_heat=1`. `thread_factor=1.0 load1=3.68`.

**My metric definition (one line).** Over **50 consecutive** intervals with the ventilation
CUSUM tripped, the number of accuracy samples recorded versus the number of house-loss
samples accepted — a rate over a run, not a single interval's binary ingest flag.

Comparability: same instrumented symbol (`_record_accuracy`) and the same contamination,
but a 50-interval rate against a paired control learner instead of one interval's 0/1.
Strictly stronger: a 1 in the finder's metric could in principle be one unlucky interval;
a 50/50 cannot.

**My numbers** (`v23_learners.py`):

| arm | accuracy samples | house-loss samples |
|---|---|---|
| production, 50 open-window intervals | **50** | **0** |
| production, 50 clean intervals | 50 | 49 |
| with the proposed gate, 50 open-window | **0** | 0 |
| with the proposed gate, 50 clean | 50 | 49 |

The tracker records **50 of 50** intervals that every thermal learner rejects.

**Perturbation** (report.json: guard `self._accuracy.record(sample)` with
`_learning_frozen(CONF_INDOOR_TEMP_ENTITY) is None`; expected *to_zero*). Applied in my
harness: open-window recording **50 → 0**, and the clean arm is untouched at 50. So the
proposed fix both works and does not starve the tracker.

**Attacks run.**
- *Source.* coordinator.py:9291 gates the record only on
  `self._pump_signals.freeze_reason is None`; three statements above, at :9216,
  `score_lead_predictions` already uses `_learning_frozen(CONF_INDOOR_TEMP_ENTITY) is
  None`. The two settlement paths in one method disagree — the finding reads the code
  correctly, and the fix is the predicate already in the method.
- *Severity.* `_confidence_margins` is opt-in and capped by `CONFIDENCE_MARGIN_CAP_C`,
  and `_inputs_healthy` separately gates the rollback decision. `low` is right; I would
  not raise it.

**Vote: `verify` (low).** Decisive number: **50 of 50** contaminated intervals recorded by
the accuracy tracker against **0 of 50** accepted by the house-loss learner in the same
run, going to **0** under the proposed one-predicate gate with the clean arm unchanged.

---

## D7-04 — `last_buffer_trajectory` is a 5 SEK side channel with one poison

**Re-run.** `tc_delta_abs_max=5.416717 SEK`, `tc_delta_rel_to_energy=0.070771`,
`null_delta_abs=0.000000`, `poison_raises=1`, `writer_sites=3`,
`reader_sites_optimizer=4`, `readers_with_model_call_between=0`,
`reader_max_line_distance=51`. `thread_factor=1.0 load1=3.40 swapins=0`.

**My metric definition (one line).** The terminal-cost error, in SEK, when the side channel
is taken from a schedule the optimizer **actually evaluates during a real `optimize()`
solve** rather than from a hand-picked extreme — reported as the off-by-one delta (the
previous evaluation's buffer trajectory, which is what an inserted model call would
actually leave behind) over every evaluated schedule, and as the worst cross-pairing.

Comparability: same instrumented pair (`ThermalModel.last_buffer_trajectory` read by
`_terminal_cost`) and the same unit, but the intervening schedule is drawn from the real
solve's own trajectory population instead of being constructed as coast / full / random.
This is the attack the finder's number invites — that 5.42 SEK is a max over extremes —
and it is the fair comparison.

**My numbers** (`v4_traj_side_channel.py`), 306 trajectories evaluated by one real solve
(two-zone, `mixing_valve_mode` manual, 200 L tank):

```
RESULT offbyone_max_store=4.818892 SEK      offbyone_median_store=0.000000 SEK
RESULT crosspair_max_store=4.548094 SEK     tc_sd_store=5.412009 SEK
RESULT offbyone_max_rel_energy_store=0.048834  (4.88 % of the schedule's 98.68 SEK)
RESULT offbyone_max_novalve=0.000000 SEK    crosspair_max_novalve=0.000000 SEK  (243 evaluated)
```

The extremes attack **fails**: realistic in-solve neighbours reproduce 4.82 SEK against
the finder's 5.42 SEK — within 11 %. The median off-by-one is 0.00 SEK, because most
consecutive evaluations are gradient perturbations whose buffer trajectories are nearly
identical; the tail is what matters and the tail is 4.8 SEK.

**Runtime check of the finding's own "not live today" clause** (`v4b_stale_runtime.py`,
a descriptor that stamps every write with a generation and checks it on every read —
a runtime method where the finder used AST line distance):

```
RESULT runtime_reads_space=305   runtime_stale_reads_space=0   runtime_reads_after_batch_space=0
RESULT runtime_reads_dhw=618     runtime_stale_reads_dhw=0     runtime_reads_after_batch_dhw=0
```

Zero stale reads in 923 reads across the space-only and the DHW paths. The finder's
`readers_with_model_call_between=0` holds by a second, independent method, and it holds
on the DHW path too, which they only checked statically.

**Perturbation** (report.json: `mixing_valve_mode` → none; expected *to_zero*). My own
no-valve arm: `offbyone_max_novalve=0.000000` and `crosspair_max_novalve=0.000000` over
243 evaluated trajectories. Exactly zero, so the harness is hooked to the store logic and
is not measuring a constant.

**Attacks run.**
- *Flat-price null control.* The panel's standing rule ("a gain at flat prices is not a
  gain") does not apply here and I record why: at the `flat` profile the number is
  `offbyone_max_flat=7.938242 SEK`, **larger**, not zero. The metric is a valuation of
  stored heat, not a price arbitrage, and the finding claims a hazard magnitude, not a
  saving. The applicable null is the configuration null, and that one is exactly zero.
- *Extremes.* Refuted above by the in-solve population.
- *Live defect?* No — 0 of 923 runtime reads stale. The finding says so itself.
- *Proposed fix.* "Return the buffer trajectory from `simulate_trajectory` / `_with_dhw`"
  — the docstring's stated reason ("nine call sites unpack a four-tuple",
  thermal_model.py:2270) is four production sites by my grep too
  (optimizer.py:2772, 2891, 4615, 4774), so the fix is smaller than the comment implies.

**Vote: `verify` (low).** Decisive number: **4.818892 SEK** off-by-one terminal-cost error
over the 306 trajectories a real solve evaluates (4.88 % of the plan's energy cost),
against **0.000000 SEK** in the no-valve configuration and **0 stale reads of 923** at
runtime today. Hygiene / low is exactly the right classification: the magnitude is real,
the defect is not live.

---

## D7-05 — `coordinator.py` has no cheap seam but one

**Re-run.** `metrics_ast.py` and `coordinator_clusters.py` reproduce every cited RESULT
exactly. Independently, my own AST script (written from scratch, `v5_hub_removal.py` plus
a one-off count) gives **10902** file lines, **10269** class lines, **256** methods,
**174** assigned instance attributes, **132** multi-writer — identical to the finder on
every one.

**My metric definition (one line).** In the graph whose nodes are the coordinator's methods
and whose edges join two methods that share at least one `self.<attr>` name (and,
separately, also join caller to callee), the size of the **largest connected component**
as a fraction of all methods after deleting the top-k attributes by method fan-in, for
k = 0, 3, 6, 10, 20, 40 — separability with **no clustering at all**: no k to choose, no
seed, no linkage, no embedding.

Comparability: not comparable term-by-term with `cross_attr_fraction` (theirs is a ratio
of *references* under a chosen partition; mine is a *connectivity* measure with no
partition). They test the same proposition from opposite directions: theirs says a chosen
cut is expensive, mine says no cut exists. The judge should treat mine as corroboration
of the claim, not of the number.

**My numbers** (`v5_hub_removal.py`):

| hubs dropped | edges = shared attrs | edges = shared attrs + calls |
|---|---|---|
| 0 | 242 / 256 (0.945), next component 1 | **256 / 256 (1.000)** |
| 3 | 214 (0.836), next 1 | 254 (0.992), next 1 |
| 6 | 200 (0.781), next 1 | 251 (0.980), next 1 |
| 10 | 191 (0.746), next 1 | 250 (0.977), next 1 |
| 20 | 175 (0.684), next 1 | 247 (0.965), next 1 |
| 40 | 143 (0.559), next 1 | 244 (0.953), next 1 |

The decisive column is "next component": at **every** k, on **both** edge definitions, the
second largest component is a **singleton**. Nothing of size > 1 ever detaches. Delete the
forty highest-fan-in attributes and 95.3 % of the class is still one connected piece. That
is a stronger statement than the finder's cross-fractions: the class is not merely
expensive to cut, it has no second lobe to cut *to*.

**Perturbation** (report.json: move the manual-plan group out; expected `n_methods` *down*
by 10 and `cross_attr_fraction_k10` down). My run: methods **256 → 249** (down ✓). But the
largest-component fraction stays at **1.000** — extracting that group removes seven nodes
and changes nothing about the remaining blob, which is consistent with the finding's own
reading ("the one cheap cut is the manual-plan group") and is worth recording: the cheap
seam is cheap because it is peripheral, not because it relieves the coupling.

**Attacks run.**
- *Is the manual-plan group 10 methods?* By name matching I find **7**
  (`_async_load_manual_plan`, `_async_save_manual_plan`, `_manual_pins`,
  `_manual_plan_state`, `_record_manual_release`, `async_apply_manual_plan`,
  `async_clear_manual_plan`). The finder's cluster of 10 includes methods whose names do
  not carry "manual". Not a defect — a different membership rule — but the "10 methods,
  152 lines" figure is theirs, not independently reproduced by me.
- *Spectral seed/k artefact.* Sidestepped entirely: my metric has neither.
- *Severity.* `hygiene / low` is right. This is a measurement that feeds a decomposition
  program; nothing misbehaves at runtime.

**Vote: `verify` (low).** Decisive number: after deleting the **40** highest-fan-in
attributes, **244 of 256** methods (0.953) remain in one connected component and every
other component is a **singleton** — there is no second cluster at any k.

---

## D7-06 — Five dead defs and six production functions only tests call

**Re-run.** `dead_candidates=5`, `dead_candidate_lines=46`, `defs_total=1062`,
`started_by_suite=983`, `dynamic_reach_started_unreferenced=7`,
`static_unreferenced_prod=63`. Reproduces the report exactly.

**My metric definition A (one line).** A def is dead if the **literal token** of its name
occurs exactly once in the whole repository tree — every `.py .js .mjs .json .yaml .yml
.md .sh .txt .cfg .toml` file under the root, that once being its own `def` line — so an
aliased import, a string dispatch, a `services.yaml` key, a card token, a translation
string or even a doc mention all count as a reference.

**My metric definition B (one line).** A def is unreached by the suite if a body replaced
by `raise AssertionError("D7SENTINEL:<name>")` is never tripped when all thirteen gate
Python scripts run on a tree copy — reachability **by exception**, not by
`sys.monitoring`.

Comparability with the finder's: their static axis is an AST census of `ast.Name`,
`ast.Attribute` and non-docstring string tokens over `custom_components/` and `tests/`
plus `services.yaml`, `strings.json` and the card JS; mine is a lexical token census over
the entire tree. Mine over-counts prose (a name mentioned in a doc paragraph counts) and
so is a *conservative* dead test — it can only ever call fewer things dead than theirs.
Their runtime axis is `sys.monitoring` PY_START; mine is an injected exception. The two
runtime methods are comparable; the two static methods are not identical, and the
difference is where the finding breaks.

**My numbers** (`v6_dead_sentinel.py`):

```
RESULT lexical_dead_tokens_eq1=5 count          (all five candidates: exactly 1 token in the tree)
RESULT sentinel_trips_dead_candidates=0 count   (13 gate scripts, all five sentinels installed)
RESULT alias_imports_total=230 count
RESULT alias_imports_hiding_a_d7_06_name=3 count
```

Positive control — the same sentinel installed on the six "test-only" defs **does** trip
(`features.py` exit 1 with 2 hits, `golden.py` exit 1 with 2 hits), so the method has
power and the zero above is a measurement, not a silence.

**The first half of the claim verifies.** All five candidates —
`comfort_learning.ComfortLearner.set_configured`, `config_flow._translated_text`,
`coordinator.HeatPumpOptimizerCoordinator.optimization_result`,
`…​.current_state`, `presets._floor_heated_area` — occur exactly once in the entire tree
and are never reached by the suite. Dynamic-reach check, which the panel prompt asks for
by name: production has exactly five `getattr` sites with a non-literal name
(`accuracy.py:246,247` on a sample's fields, `thermal_model.py:210` on
`ThermalParameters` field names, `thermal_model.py:814,835` on `const.CONF_*`/`DEFAULT_*`
names) and **no** `globals()`, `vars()`, `eval`, `exec`, `importlib` or `__getattr__`;
`sensor.py:183` is the only `__dict__` scan and it looks up the two literal names
`native_value` and `extra_state_attributes`. None of the five is an HA platform-hook name,
a `services.yaml` key or a card token. They are dead.

**The second half of the claim is wrong by one, and I can name the mechanism.**
`grid_fee.max_abs_component` (26 lines) is **not** test-only:

```
coordinator.py:351     max_abs_component as grid_fee_max_abs_component,
coordinator.py:6217        worst, source = grid_fee_max_abs_component(schedule, entity_value)
```

`coordinator.py:6217` sits inside `_audit_grid_fee`, called from `_fee_series`, which runs
on **every planning cycle**. Runtime confirmation:
`coordinator.grid_fee_max_abs_component is grid_fee.max_abs_component` → `True`.

Cause: the finder's `name_census` (dead_code.py:92) counts `ast.Name`, `ast.Attribute` and
string tokens. `from .grid_fee import max_abs_component as grid_fee_max_abs_component`
parses to an `ast.alias`, which is **neither**, so an aliased import contributes nothing to
the imported name's count and the call site only ever names the alias. The tree has
**230** aliased imports, **3** of which touch a D7-06 name. The same blind spot makes the
report say `match_layout` has `tests refs 0` while `tests/features.py:6013` imports it as
`_match_layout` and calls it seven times.

So the corrected second clause is **5 defs / 114 lines**, not 6 / 140. (The other five —
`_prepare_forecast_data`, `DrawStats.ready_energy`, `pv.piecewise_cost`,
`tariff.peak_penalty`, `topology.match_layout` — I confirmed unreferenced by production;
`piecewise_cost`'s three production hits are two prose comments in `optimizer.py`
explaining that it is deliberately inlined, plus its own def.)

**Perturbation** (report.json: delete one listed candidate; expected `dead_candidates`
*down* by 1 and the suite still passes). My sentinel run is the stronger version of the
second half: with all five candidates replaced by raising stubs the whole thirteen-script
gate is unchanged (`golden.py` exit 1 and `dst_checks.py` exit 1 are both pre-existing —
34 drift DIFFs and the `HASTUB_TZ` "dt_util carries the configured zone" check — and
neither log contains a sentinel string). The positive control moves the number, so the
harness is not measuring a constant.

**Vote: `weaken(low)`.** The headline number is right and I reproduced it two independent
ways, but the title's second clause is off by one and the cause is a systematic blind spot
in the census, not a rounding difference. Decisive number: **`coordinator.grid_fee_max_abs_component
is grid_fee.max_abs_component` → True**, with the call at `coordinator.py:6217` on every
planning cycle, against the finder's `ref_prod: 0` for that def; `alias_imports_total=230`
is the size of the hole. Severity stays `low`; the finding should be restated as
"5 dead defs (46 lines) and **5** production functions (114 lines) only tests call", and
the judge should treat every `ref_prod`/`ref_test` figure in `dead_code.json` as a lower
bound until the census counts `ast.alias`.

---

## Summary

| finding | re-run | my own number | vote |
|---|---|---|---|
| D7-01 | exact | 1-exp residual 0.5328 °C, lag-1 +0.9983, 2 sign runs / 301; 2-exp 0.000000; 0 of 120 randomised draws admitted | `verify` (medium) |
| D7-02 | exact | d(scale)/df = +0.219398, metered arm identical to commanded; f=0 null exactly 1.000000 | `verify` (medium) |
| D7-03 | exact | 50 of 50 contaminated intervals recorded vs 0 of 50 accepted by the learner; → 0 under the fix | `verify` (low) |
| D7-04 | exact | 4.818892 SEK off-by-one over 306 real-solve trajectories; 0.000000 in the no-valve null; 0 stale reads of 923 at runtime | `verify` (low) |
| D7-05 | exact | 244 of 256 methods still one component after dropping 40 hub attrs; second component a singleton at every k | `verify` (low) |
| D7-06 | exact | 5 lexically-dead defs, 0 sentinel trips over 13 gate scripts (positive control trips); but `max_abs_component` is called every planning cycle → 5, not 6 | `weaken(low)` |

Nothing voided: every harness's number moved under its stated perturbation.
