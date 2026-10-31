# D7 — verifier 3 of 3, round 3. Stance: refute-first.

Tree: a copy of baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (VERSION
6.3.20). Box: 8-core Apple M1, python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1,
five BLAS thread vars pinned to `"1"` before the numpy import in every harness.
All three finder harnesses were run from the repository root with
`PYTHONPATH=tests/hastub`, exactly as their headers say, and all three resolve
their root **relatively** (`sys.path.insert(0, "tests")` /
`Path("custom_components")`), so they measured this tree and not the file's own
checkout — the `tools/audit/README.md` trap does not apply to the round-3 set.

**Every number on both sides is a count or a ratio.** No wall, CPU or RSS figure
appears anywhere in this report, so contention cannot move any of it and nothing
needs a quiet-window re-take. `load1` and `thread_factor` per run:

| run | load1 | thread_factor |
|---|---|---|
| `sysid_plant.py` | 5.72 | 1.001 |
| `model_state_sentinel.py` | 6.54 | 1.001 |
| `learner_freeze_matrix.py` | 6.43 | 1.000 |
| `verify-3/v3_sizing_error.py` (mine) | 6.75 | 1.002 |
| `verify-3/v3_poison_reader.py` (mine) | 6.39 | 1.002 |
| `verify-3/v3_freq_folds.py` (mine) | 9.00 | 1.000 |

The tree under audit was not edited: `find custom_components tests -newer
VERSION` lists nothing after all six runs. My own harnesses are under
`tools/audit/round3/D7/verify-3/` with their raw output beside them.

My assigned line of attack was **the metric itself** — whether each harness
measures what its claim names. I wrote my own harness for all three findings,
each with a metric definition different from the finder's.

---

## D7-01 — sysid sized by a one-state model of a two-state plant. VOTE: `verify`, severity `high`

### Reproduction

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/sysid_plant.py` reproduced
**every** RESULT line at the header's stated value, most of them exactly:

```
excursion_ratio_worst=0.092   excursion_ratio_best=0.729   loo_worst=0.092
excursion_c_worst=0.0733      cells_below_stated_noise_0.10=6   grid_cells=9
completed_cells=1             admitted_cells=0
completed_cells_noise0.02=1   admitted_cells_noise0.02=1
completed_cells_noise0.10=3   admitted_cells_noise0.10=2
null_excursion_ratio_worst=0.996  null_completed_cells=9  null_admitted_cells=9
null_ua_bias_pct_worst=0.00   secondorder_ua_bias_pct_worst=0.000
perturb_massless_slab_ratio_worst=0.816  _completed=9  _admitted=9
```

### My own metric

`tools/audit/round3/D7/verify-3/v3_sizing_error.py`.

> **sizing_overprediction** = the room excursion `sysid._predict_step_excursion`
> predicts for the step power `_size_step_power` actually chose, divided by the
> excursion the production `ThermalModel` actually produced under that same
> power in the same experiment.

This never touches `max_excursion_c`, so unlike the finder's `excursion_ratio`
it does not depend on whether the comfort allowance is a target or a cap. It is
a model-vs-plant ratio; the finder's is a fraction of an allowance.

```
RESULT sizing_overprediction_worst=10.920 ratio      (typical_slab@-4C)
RESULT sizing_overprediction_best=1.368 ratio        (light_new@+8C)
RESULT sizing_overprediction_median=9.360 ratio
RESULT perturb_sizing_overprediction_worst=1.221 ratio
```

The one-state sizing model believes it is buying up to **10.9x** the room
movement the two-state plant delivers, and the finder's own perturbation
collapses that to 1.22. The mechanism the claim names is the mechanism I
measured.

### Attacks run

1. **Was the number taken under contention?** Not applicable — every figure is a
   count or a ratio from a deterministic seeded run. `thread_factor` 1.001–1.002.

2. **Is the chosen step already at the pump's ceiling?** *(the refutation
   candidate — if it were, a correct two-state sizer could not have injected
   more and the low excursion would be a pump-capacity limit, not a
   sizing-model error.)* **It is not.**
   `RESULT step_power_saturated_cells=0 count` — the largest step in the grid is
   4.719 kW against `max_electrical_power` 6.00 kW. `_size_step_power` walks
   `q_max*i/steps` upward and keeps the **largest** q whose predicted peak fits
   the bound, so it stopped because its own prediction said it had spent the
   allowance, not because it ran out of pump. The refutation fails and the
   causal claim survives.

3. **Does the massless-slab limit change anything else that matters?** This was
   the assigned attack. Measured, base arm vs `slab_thermal_mass x 0.01` arm,
   cell by cell:
   - `perturb_cells_with_identical_step_power=9` of 9. The sizing inputs are
     `house_ua`, `room_thermal_mass`, `internal_gains` (confirmed at
     `coordinator.py:10574-10582`); none is a function of slab mass, so the
     injected power is **bit-identical** in both arms.
   - `perturb_cells_with_identical_usable_rows=9` of 9 — 11 usable rows in both
     arms. The limit buys no extra data.
   - Both arms are noise-free, so the noise floor is untouched.
   - The limit does **not** make the experiment trivially easy: confidence in
     the perturbed arm is 0.497–0.752, well below the null arm's 0.833, and the
     UA bias stays at −1.70 % to −26.50 % rather than collapsing to the null's
     0.00 %.
   So the 0→9 adoption swing is attributable to the plant's response to an
   unchanged stimulus. The perturbation holds.

4. **Is the null control load-bearing?** Only partly, and the finder's report
   over-reads it. The `first_order` arm integrates the room with *literally the
   exponential `_predict_step_excursion` is derived from*, so its 0.996–1.000
   ratio and 0.00 % UA bias are a self-consistency check — the estimator
   recovering its own generating process. It cannot separate plant order from
   any other difference between the exact exponential and `simulate_step`.
   The work of that separation is done by the perturbation arm (item 3), which
   keeps the production `simulate_step` and moves one parameter — and that arm
   holds. I read `_simulate_step_single` (`thermal_model.py:1804-1857`) and with
   wind, precipitation and solar at zero and `hour_of_day=None` it is exactly the
   linear two-state system the harness's second-order reconstruction assumes, so
   there is no third mechanism hiding in it.

5. **Is the aggregate a grid artefact?** No — it gets worse off the grid. I
   re-aggregated over the full `SysIdConfig` outdoor band at 11 points x 3
   presets (33 cells):
   ```
   wide_grid_cells=33   wide_completed_cells=2   wide_adopted_production_gate_cells=0
   wide_step_power_saturated_cells=0
   wide_sizing_overprediction_worst=10.973   _best=1.338
   wide_cells_below_0.10degC=21
   ```

6. **Is the adoption gate really what the finder re-implemented?** The harness
   computes `admitted` as `completed and confidence >= 0.3`, which is a
   re-implementation. I measured it through the **real production function**
   instead — `HeatPumpOptimizerCoordinator._adopt_system_identification` called
   on a shim carrying the attributes it touches, scoring adoption by whether
   `_apply_house_heat_loss_scale` was actually invoked:
   `RESULT adopted_production_gate_cells=0 count` (and 9 of 9 in the perturbed
   arm). The real function has two further early returns the re-implementation
   omits (`base_u <= 1e-6`, `heat_loss_kw_per_c is None`), both of which only
   make adoption less likely, so the re-implementation was an upper bound and
   the 0 is real.

7. **Is the severity earned by consequence?** `DEFAULT_SYSID_ENABLED = False`
   (`const.py:463`) and `min_days_between_runs = 30.0`, so this is opt-in and
   infrequent — the discounts the finder already applied. Against that: when a
   user does opt in, the feature commands a five-hour plan override through the
   one route that bypasses mode bounds (the production docstring at
   `coordinator.py:10546-10550` says so itself), two hours of it with the pump
   commanded off, and on the default noise-free plant returns nothing adoptable
   in 33 of 33 cells; and the one arm that does adopt (0.10 °C noise, 2 of 9)
   blends a structurally wrong UA into `house_heat_loss_scale`, which drives
   every plan and is persisted. `high` is earned.

### Where the finding is wrong

**The exit-reason attribution does not survive.** The finding states the fit
"exits at `fitted gains outside plausible bounds` in 8 of 9 cells". The harness
prints, and my independent run confirms:

```
RESULT distinct_exit_reasons=3 count
RESULT exit_reason[fitted_gains_outside_plausible_bounds]=6 count
RESULT exit_reason[fitted_parameters_outside_plausible_bounds]=2 count
RESULT exit_reason[ok]=1 count
```

It is **6** of 9 at that reason, not 8, and the other two failures exit at a
different guard entirely (`sysid.py:794`, the `0.1 <= tau <= 200` / `0.01 <= ua
<= 5` bound, versus `sysid.py:744`, the `-0.5 <= gains_kw <= 2.0` bound). The
two are `light_new@+0C` and `light_new@+8C` — the cells with the **largest**
excursions in the grid (0.671 and 0.729 of the allowance). So under-excitation
explains 6 of the 8 failures; the other two fail with plenty of room movement,
and the single completed cell (`light_new@-4C`, ratio 0.660) fails adoption on
confidence 0.173, not on excursion. On the wide grid the split is 22 / 9 / 2.

This does not touch any headline number — `excursion_ratio_worst`,
`completed_cells`, `admitted_cells`, the null and the perturbation all stand,
and the perturbation rescues the `light_new` cells too, so plant order still
explains them, just through a different door. It is a narrative error in the
causal attribution, and the judge should strike the "8 of 9 / same reason"
sentence rather than the finding.

---

## D7-02 — a guard over an empty set beside a live dead write. VOTE: `verify`, severity `medium`

### Reproduction

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/model_state_sentinel.py`
reproduced every RESULT exactly, including
`sentinel_total_writes=27062` (the header's central value, not merely inside
±4000) and `prod_unread_instance_write_fraction=0.4042`:

```
dead_instance_writes=1   dead_attr_names=last_dhw_refused   dead_attr_bytes_retained=880
guard_subject_present_before=0   guard_subject_present_after=0
ast_readers_last_dhw_refused=0   ast_writers_last_dhw_refused=1
ast_writers_last_buffer_trajectory=0
ast_readers_last_buffer_trajectory_outside_guard=0   guard_asserts_over_empty_set=1
control__step_buffer_refused_writes=12288   control__step_dhw_refused_ast_readers=5
perturb_deadwrite_removed_dead_instance_writes=0      (falls from 1)
```

### My own metric

`tools/audit/round3/D7/verify-3/v3_poison_reader.py`.

> **live_touches** = the number of times ANY access of ANY kind (attribute get,
> `len`, `iter`, `getitem`, `__array__`, `bool`, `eq`, `repr`, `format`,
> `__reduce_ex__`, `__deepcopy__`) reaches the VALUE written to
> `ThermalModel.last_dhw_refused` while production code runs a real
> `HeatPumpOptimizer.optimize()`.

This is the direct answer to my assigned attack. The finder counts AST readers
of the **name**, and that census is blind to a reader that never spells it —
`vars(obj)`, `obj.__dict__`, a `locals()` sweep, an f-string over the instance
dict, or serialisation that walks the instance. Poisoning the **value** catches
every one of those by construction, because each has to touch the object.

```
RESULT live_touches=0 count
RESULT poison_writes=1 count
RESULT instrument_control_touches=4 count     POSITIVE CONTROL (instrument fires)
```

Nothing touches it. The positive control — the same `Poison` class placed on
`params`, an attribute production code reads — records 4 touches from a single
`compute_cop` call, so the 0 is a measurement and not a dead instrument. **The
assigned refutation finds no missed reader.**

### Attacks run

1. **AST census false negatives, by inspection as well as by poison.** The only
   instance sweeps anywhere in `custom_components/` are
   `coordinator.py:984-994` (`self.__dict__`, the coordinator's own, not the
   model's) and `sensor.py:297` (`cls.__dict__.get(name)` over
   `("native_value", "extra_state_attributes")` on sensor classes). Neither can
   reach a `ThermalModel` instance attribute. `tests/` has two `vars()` calls,
   over a `BuildingPreset` (`stress.py:775`) and over captured HTTP calls
   (`frontend.py:313`).

2. **Wider than the finder's census.** The finder's AST pass covers
   `custom_components/` + `tests/` `.py` only. I grepped the whole repository,
   every file type: `last_dhw_refused` occurs in exactly **two** places, both in
   `thermal_model.py` — the class-level annotation at `:1328` and the write at
   `:2938`. No `.mjs`, `.json`, `.yaml` or doc reader exists either.
   `last_buffer_trajectory` occurs in **no production file at all**: only
   `tests/rolling.py:577` (the guard itself), `docs/plan-open-issues.md:264` and
   `tools/audit/briefs/D7.md`. The assertion is over an empty set.

3. **Is the guard really out of the default gate?** Yes. `tests/run.sh:401-404`
   gates `tests/rolling.py` behind `SLOW=1` and otherwise prints a skip.

4. **Does a live reader exist behind pickle?** New datum, and it partly cuts
   against the finding's *consequence*: `RESULT pickle_reachable=1` — the value
   is carried by the production process-worker transport, since
   `coordinator._await_optimize` pickles the `optimizer` and the optimizer holds
   the model (`optimizer.py:6454`, `coordinator.py:844`). But that is the route
   that also **undermines "retained indefinitely"**: on the real HA path the
   write happens inside the worker child, against the child's per-job unpickled
   copy, and dies with it; the parent's instance keeps the class default `None`.
   The 880 bytes are retained only on the in-process fallback route
   (`hass.async_add_executor_job(optimize_in_process, optimizer, ...)`,
   `coordinator.py:932-934`) and under `FakeHass`, which runs the executor
   inline. The retention consequence is narrower than the report states. The
   **deadness** — which is the finding — is untouched.

5. **Is the severity earned?** The runtime cost is near zero, and item 4 shrinks
   the retention story further. What carries `medium` is the other half: a
   committed assertion that holds on every possible tree, in a script the
   default gate does not run, sitting on the very class that has since grown a
   new side channel — and `optimizer.py:859` still documenting the removed
   mechanism as live. A guard that cannot fail reads to the next reviewer as
   coverage. `medium` stands; a panel calibrating severity purely by runtime
   consequence could defend `low`, and I would not fight it.

---

## D7-03 — two persisted learners ingest on all five contamination arms. VOTE: `weaken` to `low`

### Reproduction

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/learner_freeze_matrix.py`
reproduced every RESULT exactly:

```
contaminated_arms=5   arms_with_freeze_reason=5
freq_map_ingests_contaminated=5      start_counter_ingests_contaminated=5
accuracy_ingests_contaminated=0      cop_scale_ingests_contaminated=0
clean_arm_ingests_freq_map=2  _start_counter=2  _accuracy=1  _cop_scale=1
ungated_learners=2 (freq_map|start_counter)   gated_learners=2 (accuracy|cop_scale)
freq_map_cooling_ingests=2
perturb_gated_freq_map_ingests_contaminated=0   perturb_gated_clean_arm_ingests_freq_map=2
```

The mechanical core is independently confirmed: `self._learning_frozen(` has
**9 call sites in 6 functions** (`_learn_measured_cop`,
`_reanchor_house_heat_loss_scale` x3, `_track_curve_comfort`, `_inputs_healthy`,
`_record_accuracy` x2, `_dhw_probe_temperature`) and neither
`_observe_frequency` (the fold at `coordinator.py:10326-10329`) nor
`_observe_compressor_start` (`:9764`) is among them. (In passing: the report's
"Five call sites consult it" is itself off by four.)

### My own metric

`tools/audit/round3/D7/verify-3/v3_freq_folds.py`.

> **freq_map_folds[arm]** = the increase in the total sample count held in
> `FrequencyMap.buckets` (`sum(entry[1])`) over one coordinator interval with
> contamination signal `arm` asserted — how many readings the map actually
> ABSORBED, not how many times its ingest method was entered.

### Attacks run

1. **Does `observe` filter internally — is a call a fold?** This was the assigned
   attack, and **it fails at the rig's reading**. `FrequencyMap.observe`
   (`freq_control.py:73-97`) does have three early returns, and my guard probe
   proves it: `RESULT observe_calls_refused_inside=5` of 6 probe cases (0 Hz,
   below `hz_min`, above `hz_max*1.05`, `kw <= 0.05`, non-finite kW all refused;
   only 55 Hz / 2 kW folds). But under the finder's own rig
   `RESULT calls_equal_folds_healthy=1` — calls equal folds on every arm:

   ```
   freq_map_folds_contaminated_healthy=5   clean_arm_folds_healthy=2
   freq_map_cooling_folds=2
   start_counter_lifetime_delta_contaminated_healthy=5
   ```

   Five contaminated arms genuinely fold, and the wear ledger books five real
   compressor starts. The finding is **not** refuted at its own metric.

2. **What the metric does hide.** The rig asserts contamination only through
   coordinator flags while feeding every arm the *same healthy reading* —
   `sensor.freq = "55"`, `sensor.hp_power = "2000"`, `coord._measured_power =
   2.0`. So the arms never reach `observe`'s guards, and the equality in item 1
   is an accident of that one reading rather than a property of the code. Fed
   what a stopped compressor actually reports:

   ```
   RESULT freq_map_folds_contaminated_stopped=0 count
   RESULT clean_arm_folds_stopped=0 count
   RESULT start_counter_state_changed_contaminated_stopped=0 count
   RESULT calls_equal_folds_stopped=0 count
   ```

   At 0 Hz / 0 W nothing folds on any arm. The `pump_offline` arm — where the
   compressor is by definition not turning — is already refused by `observe`'s
   own `hz < max(1.0, hz_min)` and `kw <= 0.05` guards, and so is
   `pump_fault` whenever the fault stops the compressor. Two of the five arms
   need no gate; the harness only shows them ingesting because it holds the
   frequency sensor at 55 Hz while asserting "heat pump offline", which is a
   state the hardware cannot be in.

3. **Is the un-gated fold a corruption at all?** `_learning_frozen`'s own
   docstring (`coordinator.py:5594-5599`) scopes it: *"a learner that trains on
   a flatline or on heat it did not supply corrupts a parameter that is
   persisted to disk"* — house thermal parameters. `FrequencyMap` learns
   electrical kW per compressor Hz, a **device** characteristic; `StartCounter`
   counts physical compressor starts. A wood furnace or an open window changes
   the house's heat balance, not the compressor's power curve, and a start
   during a fault or in cooling is still a real start that wears the compressor
   — gating the wear counter on `_learning_frozen` would arguably *lose* true
   events. So `external_heat`, `open_window` and the whole start-counter column
   are not demonstrated corruptions; they are demonstrated non-consultations.

4. **What survives.** Exactly the arm the finder itself called "the one with
   teeth": `pump_cooling`. There the compressor really is turning, 55 Hz / 2 kW
   is a physically honest reading, `freq_map_cooling_folds=2`, and the kW-per-Hz
   ratio measured in reverse cycle does fold into the map that
   `_command_frequency` later writes to the compressor while heating. That is
   one learner on one arm.

5. **Is the severity earned?** The finder's own bounds hold — the map is
   consulted only in `freq_control_mode: control`, `recommend()` returns `None`
   on a map with no evidence, `_command_frequency` never turns `None` into a
   write, and the watchdog stands the stage down on divergence. On top of those,
   my measurements cut the exposure from "2 learners x 5 arms" to **1 learner x
   1 arm**, with the bias self-correcting under control's own feedback (the
   class docstring says so, and `FREQ_EWMA_ALPHA` re-learns within days).
   `medium` is not earned by that. **`low`.**

6. **Is the perturbation sound?** Yes, and it reproduces: gating the fold takes
   `freq_map_ingests_contaminated` 5 → 0 while `clean_arm_ingests_freq_map`
   stays 2. The number moves under its own perturbation, so the finding is not
   void — it is over-scoped.

A note the judge may want: the "2" in every clean-arm cell is a rig artefact.
`run_interval` calls `_record_accuracy` twice (once to arm a prediction, once to
settle it) and `_record_accuracy` calls `_observe_frequency` and
`_observe_compressor_start` each time. One production interval is one fold, not
two. It does not affect any cross-arm comparison.

---

## Summary

| finding | vote | severity | my executed number |
|---|---|---|---|
| D7-01 | `verify` | `high` (as filed) | `sizing_overprediction_worst = 10.920`, → 1.221 under the perturbation; `step_power_saturated_cells = 0`; `adopted_production_gate_cells = 0` of 9 and 0 of 33 |
| D7-02 | `verify` | `medium` (as filed) | `live_touches = 0` with `instrument_control_touches = 4` |
| D7-03 | `weaken` | `low` (filed `medium`) | `freq_map_folds_contaminated_stopped = 0` against `..._healthy = 5`; `observe_calls_refused_inside = 5` of 6 |
