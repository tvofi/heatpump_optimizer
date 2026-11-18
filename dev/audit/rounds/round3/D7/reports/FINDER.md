# D7 — Architecture and maintainability, round 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (VERSION 6.3.20).
Box: 8-core Apple M1, 8 GB, python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1,
OpenBLAS pinned to one thread in every harness. The box was shared with
eleven other sessions throughout; `load1` at the three measurement runs was
16.9, 56.2 and 62.5. **Every number below is a count or a ratio.** Nothing
here is a wall, CPU or RSS figure, so contention cannot move any of it, and
nothing needs a quiet-window re-take.

## Method

Three harnesses, all under `tools/audit/round3/D7/`, each runnable by the
single command in its own header, each hooking a named production symbol and
each carrying its own control:

| harness | drives | control |
|---|---|---|
| `sysid_plant.py` | `sysid.SystemIdentification.step/.identify` over `thermal_model.ThermalModel.simulate_step` | the one-state plant `sysid` assumes (null), and the same rows under a correct second-order fit |
| `model_state_sentinel.py` | one real `optimizer.HeatPumpOptimizer.optimize()` with a `ThermalModel` subclass recording every instance read and write, plus an AST census over `custom_components/` and `tests/` | two same-family scratch attributes that ARE read, so a zero read count is a measurement |
| `learner_freeze_matrix.py` | `coordinator.HeatPumpOptimizerCoordinator._record_accuracy` / `._learn_measured_cop` / `._observe_frequency` under each contamination signal `._learning_frozen` recognises | the clean arm, where each learner must ingest |

Both spot mutations were executed **in an rsync copy of the tree under a
private temp directory**, not in the tree under audit. No production or test
file in this export was modified at any point; `find custom_components tests
-newer VERSION` lists nothing.

Structural metrics were **not** re-derived: `tests/structure_budgets.json`
carries 24 (its 25 keys less `recorded_at`) and `tests/structure.py` measures
every one on each gate run. Two things below are a *reading* of what that file
already carries; one is a metric it does not carry.

---

## Findings

### D7-01 — the active experiment is sized by a one-state model of a two-state plant, and adopts nothing (high)

`ThermalModel._simulate_step_single` is second order: the pump's thermal output
enters the **slab** (`dT_slab = (thermal_power - q_slab_to_room)/slab_thermal_mass`)
and reaches the room only through `params.slab_heat_transfer`. Both halves of
`sysid.py` assume one state with the heat in the room —
`SystemIdentification._size_step_power` sizes the step through
`_predict_step_excursion(house_ua, house_capacity, house_gains)`, and
`coordinator._run_system_identification` passes exactly
`heat_loss_coefficient * house_heat_loss_scale`, `room_thermal_mass`,
`internal_gains`; `SystemIdentification.identify` then regresses the room's rate
on the pump's own thermal output.

Consequence, over a 3 preset x 3 outdoor-temperature grid (9 cells), each cell
one full five-hour experiment driven through the real state machine at the
production 30-minute cadence:

| | value |
|---|---|
| `excursion_ratio` (achieved room excursion / `max_excursion_c` = 0.8 degC) | worst **0.092**, best 0.729, range 0.637 |
| leave-one-out (single most favourable cell dropped) | worst 0.092, best 0.671 |
| smallest achieved excursion | **0.0733 degC** |
| cells moving the room less than the 0.10 degC noise `SysIdConfig`'s own docstring names as the case the fit must survive | **6 of 9** |
| `SysIdResult.completed` | **1 of 9** |
| passes `coordinator._adopt_system_identification`'s gate (`completed and confidence >= 0.3`) | **0 of 9** |
| with 0.02 degC sensor noise | completed 1, adopted 1 |
| with 0.10 degC sensor noise | completed 3, adopted 2 |

The experiment spends a whole night, two hours of it with the pump commanded
off (`step()` returns `0.0` through `PHASE_RELAX`, and
`_run_system_identification` writes it straight into `_current_action["power"]`,
bypassing mode bounds), and on the noise-free default install adopts nothing.

**Null control.** The same protocol on the plant `sysid` assumes — one state,
heat straight into the room, integrated by the exact exponential
`_predict_step_excursion` is derived from — gives `excursion_ratio` 0.996–1.000,
**9 of 9 completed, 9 of 9 adopted**, and a UA bias of **0.00 %**. The effect is
entirely a plant-order effect, not a protocol or arithmetic artefact.

**The rows are not the problem.** Fitting the *same* samples with the correct
second-order regression (eliminate the slab state; regress `Q` on
`[T'', T', (T - T_out), 1]`, linear in the parameters) recovers UA to
**0.000 %** on all nine cells. The information is in the data; the first-order
structure loses it.

**Perturbation.** `params.slab_thermal_mass x 0.01` — the massless-slab limit in
which the two-state plant collapses to the one-state model — moves
`excursion_ratio` worst from 0.092 to **0.816**, completed from 1 to **9**,
adopted from 0 to **9**.

Severity `high`: an opt-in feature that commands a five-hour plan override and
cannot produce an adoptable result on the default noise-free plant, while the
one arm that does adopt (0.10 degC noise, 2 of 9) adopts a fit whose structure
is wrong. Not `critical`: it is off by default (`DEFAULT_SYSID_ENABLED`), needs
an explicit arm, and the blend is confidence-weighted.

### D7-02 — a guard against retained simulation state is written against a name nothing uses, while a live one sits on the same class (medium)

`tests/rolling.py:577` asserts *"the thermal model retains no simulation
side-channels"* with the predicate
`not hasattr(_learner._thermal_model, "last_buffer_trajectory")`.
Measured over `custom_components/` and `tests/`: that name has **0 AST writers**
and **0 AST readers outside the assertion itself**. The assertion is over an
empty set — it holds on any tree. `hasattr` is False before *and* after a full
solve, which is what makes it unfalsifiable rather than satisfied. It is also
`SLOW=1`-only (`tests/run.sh:402-404`), so the default gate does not run even
the vacuous form. `optimizer.py:859` still documents the removed mechanism as
live: *"the model stashes the series on itself for the terminal-cost term"*.

The class has meanwhile grown one. `thermal_model.py:2938` ends
`simulate_trajectory_with_dhw` with `self.last_dhw_refused = dhw_refused` — an
`n_steps` float64 array published on the long-lived model instance. Over one
real `HeatPumpOptimizer.optimize()`:

| | value |
|---|---|
| `last_dhw_refused` writes / sentinel reads / AST readers anywhere | 1 / 0 / **0** |
| retained on the instance after the solve | 880 bytes, indefinitely |
| positive control `_step_buffer_refused` writes / reads / AST readers | 12288 / 12000 / 2 |
| positive control `_step_dhw_refused` writes / reads / AST readers | 3834 / 96 / 5 |
| sentinel total instance writes (the instrument is live) | 27062 across 6 attributes |

**Perturbation.** Removing the one line in a temp copy takes
`dead_instance_writes` from 1 to **0**, and nothing else changes.

Severity `medium`: bounded (one small array retained per model), but the
mechanism is a guard that cannot fail, and a guard that cannot fail is worse
than no guard because the next reviewer reads it as coverage.

### D7-03 — two persisted learners ingest every interval the freeze predicate rejects (medium)

`coordinator._learning_frozen` is the project's single freeze predicate — *"Fail
closed... a learner that trains on a flatline or on heat it did not supply
corrupts a parameter that is persisted to disk."* Five call sites consult it.
The frequency map does not, and neither does the compressor start counter, even
though `_apply_learner_payloads` resets `self._freq_map = FrequencyMap()` in the
same block as the curve learner and the solar aperture, commented *"T7: the
frequency map rolls back with its fellow learners."*

One interval per arm, counting calls into each learner's own ingest method:

| arm | `_learning_frozen` | freq_map | start_counter | accuracy | cop_scale |
|---|---|---|---|---|---|
| clean (control) | `None` | 2 | 2 | 1 | 1 |
| external_heat | `external_heat_source` | **2** | **2** | 0 | 0 |
| open_window | `ventilation` | **2** | **2** | 0 | 0 |
| pump_offline | `heat_pump_offline` | **2** | **2** | 0 | 0 |
| pump_fault | `heat_pump_fault` | **2** | **2** | 0 | 0 |
| pump_cooling | `heat_pump_cooling` | **2** | **2** | 0 | 0 |

`ungated_learners = 2`, `gated_learners = 2`, `arms_with_freeze_reason = 5`
(every contaminated arm really does make the predicate return a reason — the
positive control that the arms are contaminated at all).

The cooling arm is the one with teeth: the pump is running in reverse cycle,
every gated learner stops, and `FrequencyMap.observe` keeps folding kW-per-Hz
pairs measured in cooling into the map `coordinator._command_frequency` later
writes to the compressor while heating.

**Perturbation.** Adding one `if self._learning_frozen(CONF_POWER_ENTITY) is not
None: return` before the fold, in a temp copy, takes
`freq_map_ingests_contaminated` from 5 to **0** while
`clean_arm_ingests_freq_map` stays **2**.

Severity `medium`: it corrupts a learner that drives a hardware write, but the
map is only consulted in `freq_control_mode: control`, `recommend()` refuses a
map with no evidence, and the watchdog stands the whole stage down on
divergence — so there is a workaround and a bound.

---

## Non-findings (checked, held)

- **`last_buffer_trajectory` is genuinely gone from production.** AST writers 0,
  `hasattr` False before and after a real solve. The statefulness the brief
  named was removed; what remains is the guard, which is D7-02.
  `PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/model_state_sentinel.py --no-mutate`
  -> `ast_writers_last_buffer_trajectory=0`, `guard_subject_present_after=0`.
- **`simulate_trajectory` returns its refusal ledger rather than stashing it.**
  `buffer_refused` is element 6 of the return tuple (`thermal_model.py:2388`)
  and `_step_buffer_refused` shows 12288 writes against 12000 reads inside the
  same call — a scratch, not a channel. Same harness.
- **The terminal cost has no cross-call model state to reorder.** Grep over
  `optimizer.py` and `coordinator.py` for reads of `thermal_model._step*` or
  `.last_*` outside `thermal_model.py` returns nothing
  (`grep -n "_step_dhw_draw_kw\|_step_dhw_floor_injected\|model\._step\|\.last_" custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/coordinator.py` -> 0 hits).
  A reordering harness would therefore have measured zero by construction; the
  brief's item 4 is answered by the absence, not by a number, and I did not
  manufacture one.
- **The accuracy tracker and the COP scale are correctly frozen** on all five
  contamination arms while ingesting on the clean arm.
  `learner_freeze_matrix.py` -> `accuracy_ingests_contaminated=0`,
  `cop_scale_ingests_contaminated=0`, `clean_arm_ingests_accuracy=1`.
- **The sysid fit is not numerically broken.** On the plant it assumes, it
  recovers UA to 0.00 % at confidence 0.833 in 9 of 9 cells. Every failure
  measured in D7-01 is structural.
- **A metric `structure_budgets.json` does not carry:** 40.42 % of one solve's
  `ThermalModel` instance-attribute writes (10 939 of 27 062) are to attributes
  **no production code reads** — `_step_dhw_draw_kw`, `_step_dhw_floor_injected`
  (both test-only assertion channels, deliberate and documented) and
  `last_dhw_refused` (dead). The ratchet measures class and method size, not
  whether a class's own state is read, so this is invisible to it.
  `model_state_sentinel.py` -> `prod_unread_instance_write_fraction=0.4042`.
- **A reading of two metrics it does carry:** `coordinator_loc` 9604 equals
  `max_class_loc` 9604, so the coordinator class *is* the largest class in the
  tree and the ratchet's class-size cap and its coordinator cap are the same
  constraint at zero slack — lowering one requires lowering the other. And
  `wc -l custom_components/heatpump_optimizer/coordinator.py` = 10 899, so the
  class is 88.1 % of its file: there is no meaningful module-level headroom to
  reclaim without splitting the class itself.

## What I could not finish

- **Brief item 5 (this year's train, one spot mutation per addition).** Two spot
  mutations were executed (D7-02, D7-03), both with a direction and both
  reproduced. The full table — batched gradient and bounds gate, drift gate,
  scoped gate, card collaborators, stress budgets, weekly windows, topology
  catalogue, wood and coil variants, DHW confidence, Tuya, re-anchor law — needs
  one gate selection per mutation, and the dispatch conditions forbid a full
  `tests/run.sh` during the fan-out. Left for the quiet window; it is a
  `tests/closure.py select` per mutation plus the selected scripts, not new
  instrumentation.
- **The defrost derate's freeze behaviour is unmeasured.** `learner_freeze_matrix.py`
  reports 0 ingests on *every* arm including clean, because the rig never opens a
  defrost window. That is an instrument gap, not a result, and the harness header
  says so; do not read a 0 there as a gated learner.
- **The two-zone plant.** Everything in D7-01 is the single-zone path
  (`_simulate_step_single`). `_simulate_step_two_zone` has the same slab
  coupling and the same `_size_step_power` caller, so the mechanism should
  carry, but I did not measure it.

## exposure

None beyond the tree as exported. I read no GitHub, ran no `gh`, and opened no
`docs/audit-*.md`, `docs/backlog.md` or `RELEASE_NOTES.md` (all absent from this
export). Three production files carry `D<k>-nn` identifiers from earlier rounds
in their own comments and I read those comments as part of reading the code:
`sysid.py` (D7-01, D7-02, D2-01, D2-07, D2-08 in the `identify` and
`DEFAULT_MAX_EXCURSION_C` commentary), `coordinator.py` (D7-03/D7-05 at the
accuracy gate, D10-07/D10-09, D1-01, D6-03) and `thermal_model.py` (D6-03).
I treated them as context and did not go looking for what they referred to; my
`D7-01`/`D7-02`/`D7-03` ids in this report are round-3 ids assigned in order and
are not claims about those comments.
