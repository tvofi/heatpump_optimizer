# D7 panel — verifier 1 of 3, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (VERSION 6.3.20).
Box: 8-core Apple M1, 8 GB, python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1,
OpenBLAS pinned to one thread in every harness.
`thread_factor` 1.000–1.005 on every run; `load1` 5.18–30.16 across the session.
**Every number in this report is a count or a ratio.** No wall, CPU or RSS
figure appears, so contention cannot move any of it and nothing needs a
quiet-window re-take. No `tests/stress.py`, no `./tests/run.sh`, no gate lock
was taken; `ps aux | grep -E "[s]tress\.py|[t]ests/run\.sh"` was empty at the
start of the session.

I am the own-harness seat. Every finding below carries a number produced by an
instrument I wrote, with my own metric definition, alongside the finder's
re-run. My harnesses are under `tools/audit/round3/D7/verify-1/`:

| file | what it measures |
|---|---|
| `v1_sizer_mismatch.py` | D7-01 — the production sizer/predictor against the production simulator, no protocol, no fit |
| `v1_coordinator_sysid_e2e.py` | D7-01 — the same experiment end-to-end through the **real coordinator**, measuring the production parameter it moves |
| `v1_orphan_attrs.py` | D7-02 — widest-net orphan census plus a `__setattr__` trap on the production class |
| `v1_freeze_gate_census.py` | D7-03 — static gate census, class-level fold count on production freeze constants, and the consequence in Hz |

Outputs are the `.txt` files beside them. All three finder harnesses were
re-run in this tree with the command in their own headers.

---

## D7-01 — the sysid experiment is sized by a one-state model of a two-state plant

**Vote: `verify`. Severity `high`, as filed.**

### Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/sysid_plant.py`
reproduced **every** headline figure exactly, not within tolerance —
`excursion_ratio_worst=0.092`, `excursion_ratio_best=0.729`,
`excursion_c_worst=0.0733`, `cells_below_stated_noise_0.10=6`,
`completed_cells=1`, `admitted_cells=0`, `null_*` 0.996 / 9 / 9 / 0.00 %,
`secondorder_ua_bias_pct_worst=0.000`, perturbation 0.816 / 9 / 9.
`thread_factor=1.000`, `load1=5.18`.

### My own number, route 1 — the two modules compared directly

**Metric (mine, one line):** `sizer_overprediction` = the peak room excursion
the production `sysid._predict_step_excursion` predicts for the step power the
production `SystemIdentification._size_step_power` chooses, given exactly the
three house arguments `coordinator._run_system_identification` passes, divided
by the peak room excursion the production `ThermalModel.simulate_step`
actually delivers for that same step power over `step_hours` then
`relax_hours` from the plan's own steady state. **Agreement is 1.0.**

This drives no state machine, fits nothing, and reuses none of the finder's
`excursion_ratio`. It asks only whether the two halves of the tree agree about
the plant.

```
RESULT sizer_overprediction_worst=10.80 ratio
RESULT sizer_overprediction_best=1.37 ratio
RESULT sizer_overprediction_median=9.30 ratio
RESULT sizer_overprediction_loo_worst=10.80 ratio     (single best cell dropped)
RESULT capacity_ratio_worst=4.14 ratio                (C_room+C_slab)/C_room
RESULT slab_retained_fraction_worst=0.928 fraction
RESULT slab_retained_fraction_best=0.451 fraction
RESULT null_sizer_overprediction_worst=1.00 ratio     NULL CONTROL
RESULT null_sizer_overprediction_best=1.00 ratio      NULL CONTROL
RESULT perturb_massless_slab_overprediction_worst=1.19 ratio
RESULT perturb_massless_slab_overprediction_best=1.06 ratio
RESULT default_sysid_enabled=0 bool
RESULT sysidconfig_enabled_default=0 bool
```

The sizer overpredicts the excursion its own step will cause by **10.80x** on
`typical_slab@-4C` and by **9.30x** at the median. The null control is
**exactly 1.00x on all nine cells** — the instrument is not measuring its own
arithmetic. The perturbation collapses it to 1.06–1.19x, the stated direction.
`slab_retained_fraction` says why in one number: on the two floor-emitter
presets **92.8 %** of the pump's extra thermal energy is still sitting in the
slab when the step phase ends.

### My own number, route 2 — end to end through the real coordinator

**Metric (mine):** `adopted_scale_shift_cells` = how many of the 9 cells move
`coordinator._house_heat_loss_scale` away from its starting value after a full
experiment driven entirely through `_run_system_identification` (which chooses
sysid's `house_ua`/`house_capacity`/`house_gains` itself) and
`_adopt_system_identification`. The consequence measured is the production
parameter the feature exists to move, not a fit quality.

```
RESULT completed_cells=1 count
RESULT adopted_scale_shift_cells=0 count
RESULT max_abs_scale_shift=0.00000 ratio
RESULT null_completed_cells=9 count                        NULL CONTROL
RESULT null_adopted_scale_shift_cells=9 count              NULL CONTROL
RESULT perturb_massless_slab_adopted_cells=9 count
RESULT noise010_completed_cells=3 count
RESULT noise010_adopted_scale_shift_cells=2 count
RESULT noise010_max_abs_scale_shift_pct=5.70 percent
RESULT noise010_adopted_ua_bias_pct_worst=17.32 percent
```

**0 of 9** through the real wiring. The coordinator route reproduces the
finder's `admitted_cells=0` and its noise arm (completed 3, adopted 2) without
using the finder's rig, and adds a consequence figure the report did not
carry: the two cells that do adopt at the 0.10 degC noise the `SysIdConfig`
docstring names carry a **UA bias of up to 17.3 %** and walk
`house_heat_loss_scale` **5.70 %** off. On the six slab cells the production
guard refuses outright (`sensor noise dominates the excursion`), so the
corruption does not reach them — the guards fail closed exactly where the
plant mismatch is worst.

### Attacks run, and what they returned

1. **Derive the plant independently rather than take the finder's account.**
   Read `thermal_model.py:1804-1860`: `thermal_power = cop * electrical_power
   + external_heat` enters `dT_slab = (thermal_power - q_slab_to_room) /
   p.slab_thermal_mass`; the room sees only `q_slab_to_room = p.slab_heat_transfer
   * (T_slab - T_room)`. The account is correct. **Attack failed.**
2. **Is `_simulate_step_single` the path a real experiment takes?**
   `simulate_step` (`thermal_model.py:2216-2228`) dispatches to it whenever
   `two_zone_enabled` is false, sub-stepping for stability. It is the path.
   **Attack failed.**
3. **Does the coordinator really hand sysid a room-only capacity?**
   `coordinator.py:10560-10576` passes `house_capacity=ctx._thermal_params.
   room_thermal_mass` and `house_ua=heat_loss_coefficient * house_heat_loss_scale`.
   The finder's harness passes the bare `heat_loss_coefficient`; on a fresh
   install `house_heat_loss_scale` is 1.0, so the two agree — I confirmed
   `_house_heat_loss_scale == 1.0` on a freshly built coordinator. On an
   install whose passive learner has already moved that scale the sized step
   differs; neither of us measured that, and it is worth a line in any fix.
   **Attack failed, one unmeasured corner recorded.**
4. **Grid artefact — are the three presets cherry-picked toward slabs?** No.
   They are byte-identical to `tests/stress.py:BUILDINGS` (lines 675-693), the
   repository's own canonical sweep. Leave-one-out drops the single most
   favourable cell and `excursion_ratio_loo_worst` stays 0.092;
   `sizer_overprediction_loo_worst` stays 10.80. **Attack failed.**
5. **Null control present and passing?** Yes, on both routes and on mine:
   exactly 1.00x sizer agreement and 9/9 adoption on the one-state plant. A
   protocol or arithmetic artefact would have shown there. **Attack failed.**
6. **Reachability — the question I was told to ask.** `const.py:463`
   `DEFAULT_SYSID_ENABLED = False`; `sysid.py:93` `SysIdConfig.enabled = False`.
   Arming needs the config option **and** a button press
   (`button.py:109 -> coordinator.async_arm_system_identification`), which
   re-reads the flag, so a press with the option off does nothing. The defect
   cannot occur on a stock install. This is the one attack that lands — and
   the finder had already applied it, declining `critical` for exactly this
   reason. **Attack lands on `critical`, not on `high`.**
7. **Is the severity earned by consequence?** `docs/how-it-works.md:1079-1086`
   sells the feature as *"the fastest way to a good model"*, getting the loss
   coefficient *"in days rather than the weeks passive learning needs"*. A
   user who follows that documented path spends a five-hour night, two hours
   of it with the pump commanded off, and my end-to-end run says the
   production parameter moves by **0.00000** on 9 of 9 cells. At realistic
   sensor noise it moves **5.70 %** in the wrong direction on a structurally
   wrong fit. A documented feature that delivers the opposite of its promise
   on every cell of the repository's own sweep earns `high`. **Severity
   stands.**
8. **The one assumption I cannot discharge.** Both the finder's harness and
   mine treat the project's `ThermalModel` as the house. That is a model, not
   a measurement of a real building. It does not weaken the finding, because
   the defect I measured is *internal*: two modules in the same tree disagree
   about the plant, and `capacity_ratio` (up to 4.14x) and
   `sizer_overprediction` (up to 10.80x) quantify that disagreement without
   any claim about reality. A judge should read the finding as "the sizer and
   the simulator contradict each other", which is exactly what it is.

---

## D7-02 — a side-channel guard whose subject nothing can create

**Vote: `weaken`. Severity `low`, not `medium`.** Every number verifies; the
grade does not.

### Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/model_state_sentinel.py`
reproduced every figure exactly: `dead_instance_writes=1`,
`dead_attr_names=last_dhw_refused`, `dead_attr_bytes_retained=880`,
`ast_readers_last_dhw_refused=0`, `ast_writers_last_buffer_trajectory=0`,
`guard_asserts_over_empty_set=1`, `prod_unread_instance_write_fraction=0.4042`,
controls 12288/2 and 3834/5, perturbation 1 -> 0.
`thread_factor=1.005`, `load1=5.66`.

### My own number

**Metric (mine, one line):** `orphan_published_attributes` = `ThermalModel`
instance attributes that a `__setattr__` trap installed on the **production
class** (not a subclass) observes being written during one real
`HeatPumpOptimizer.optimize()`, and whose identifier occurs in **no read
position anywhere in the repository** — every AST `Attribute`/`Name` load,
every string constant, and every bare textual occurrence in any of 365 tracked
`.py .mjs .js .json .md .yaml .yml .sh .txt` files, excluding only the
statements that create the attribute (instance writes and the class-body
declaration of the same name). The net is deliberately *wider* than the
finder's, which searched `custom_components/` and `tests/` by AST plus
`getattr`/`hasattr`/`setattr` literals — so mine can only ever find fewer
orphans, never more.

```
RESULT orphan_published_attributes=1 count
RESULT orphan_attr_names=last_dhw_refused names
RESULT reader_net_files=365 count
RESULT vacuous_guard_subjects=1 count
RESULT vacuous_guard_subject_names=last_buffer_trajectory names
RESULT control__step_buffer_refused_read_occurrences=2 count  POSITIVE CONTROL
RESULT control__step_dhw_refused_read_occurrences=5 count     POSITIVE CONTROL
RESULT perturb_line_deleted_orphan_writes=0 count
```

And the cleanest statement of the whole finding, from a separate five-line run
after a real solve (`own_D7-02_retention.txt`):

```
RESULT v1_retained_arrays_after_solve=1 count      (last_dhw_refused, 96 float64, 768 B)
RESULT v1_guard_predicate_value=True               the guard PASSES
RESULT v1_guard_covers_retained_arrays=0 count     it covers none of them
```

The model instance ends a real solve holding exactly one retained simulation
array; the guard that claims *"the thermal model retains no simulation
side-channels"* evaluates `True` and covers **zero** of them. (768 B is
`ndarray.nbytes`; the finder's 880 B is `sys.getsizeof`, which adds the
112-byte header. Same array.)

### Attacks run

1. **Verify the census myself, including dynamic lookups.** Done, wider than
   the finder: raw text over 365 files catches any `getattr("last_dhw_refused")`,
   any JSON key, any `.mjs` reference, any doc mention. **Attack failed.**
2. **A methodological trap I hit and fixed, which a judge should know about.**
   My first pass reported `orphan_published_attributes=0`, because
   `thermal_model.py:1328` declares `last_dhw_refused: np.ndarray | None = None`
   in the class body and a naive textual net counts that as a reader. It is a
   declaration of the same attribute, not a use. `ThermalModel` is a plain
   class, not a dataclass, so the line is a default, not a field. Excluding
   class-body declarations of the name restores 1. **Anyone re-deriving this
   number must exclude that line or they will get 0.**
3. **Does a *test* read it, even though production does not?** No — zero
   readers anywhere, tests included. The distinction matters for the two
   neighbours: `_step_dhw_draw_kw` (4 readers) and `_step_dhw_floor_injected`
   (2 readers) are read **only** by `tests/features.py`. The finder's
   `dead_instance_writes` correctly counts a test reader as a reader and
   excludes them; its separate `prod_unread_instance_write_fraction=0.4042`
   correctly does not. Both rules are defensible and the report states which
   is which. **On the right rule:** for "is this dead code", any reader counts,
   so `dead_instance_writes=1` is the right headline and 0.4042 is a different,
   clearly-labelled statistic. **Attack failed.**
4. **Is a regression guard legitimately "over an empty set"?** This is the
   finding's weakest joint and it deserves saying plainly. A guard that asserts
   *absence* is supposed to be satisfied today; that alone does not make it
   vacuous. What makes this one vacuous is that its subject has **0 assignment
   sites repo-wide** — no code path can create `last_buffer_trajectory`, so no
   regression it is watching for can be expressed. Meanwhile the sentence it
   is written under names a *class property* ("retains no simulation
   side-channels") that is now false by one. The finder's framing survives.
   **Attack failed, but the finding would be stronger stated as "the predicate
   tests one dead name while the sentence claims a class property".**
5. **Is the severity earned?** No. The runtime consequence is 768 bytes on one
   long-lived object, and the guard is `SLOW=1`-only (`tests/run.sh:401-402`),
   so the default gate never executes even the vacuous form. There is no
   present defect — the cost is that a future reviewer reads a guard as
   coverage. That is real and it is exactly D7's remit, but in a four-band
   scheme where `medium` is doing work like D7-03's corruption of a
   hardware-write path, this is `low`. The stale comment at `optimizer.py:859`
   ("the model stashes the series on itself") belongs in the same fix.
   **Attack lands: severity `low`.**

---

## D7-03 — two persisted learners ignore the project's single freeze predicate

**Vote: `verify`. Severity `medium`, as filed.**

### Re-run of the finder's harness

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/learner_freeze_matrix.py`
reproduced every figure exactly: `freq_map_ingests_contaminated=5`,
`start_counter_ingests_contaminated=5`, `clean_arm_ingests_freq_map=2`,
`accuracy_ingests_contaminated=0`, `cop_scale_ingests_contaminated=0`,
`arms_with_freeze_reason=5`, `ungated_learners=2`, `gated_learners=2`,
perturbation 5 -> 0 with the clean arm at 2.
`thread_factor=1.002`, `load1=6.50`.

### My own numbers — three metrics, one static, one runtime, one consequence

**Metric 1 (mine, static):** `ungated_ingest_methods` = coordinator methods
that call a persisted learner's ingest method and contain no reference to
`_learning_frozen` anywhere in their own body (AST, enclosing `FunctionDef` of
each call site). A method that never mentions the predicate cannot be gated by
it — no runtime rig involved.

**Metric 2 (mine, runtime):** `freq_map_folds_while_frozen` = calls into
`FrequencyMap.observe` counted by wrapping the **class** method, so an instance
the coordinator swaps cannot hide a fold, during one interval's pass through
`coordinator._record_accuracy`, per arm. Arms are asserted with the
**production constants** `pump_signals.FREEZE_OFFLINE` / `FREEZE_FAULT` /
`FREEZE_COOLING` and a real `pump_mode.capability("cooling")`.

**Metric 3 (mine, consequence):** `freq_recommend_shift_hz` = how far
`FrequencyMap.recommend` moves for a fixed 1.6 kW target over a 20–100 Hz
range after one contaminated hour of folds at a draw ratio `r`, against the
same map with those folds withheld. `r = 1.0` is the null control.

```
RESULT freq_map_folds_while_frozen=5 count
RESULT arms_with_production_freeze_reason=5 count
RESULT clean_arm_freq_map_folds=2 count                 POSITIVE CONTROL
RESULT ungated_ingest_methods=2 count
RESULT ungated_ingest_method_names=_observe_compressor_start->_start_counter.observe|_observe_frequency->_freq_map.observe
RESULT gated_ingest_method_names=_record_accuracy->_accuracy.record
RESULT freq_recommend_shift_hz_null_r1.0=0.0 hz         NULL CONTROL
RESULT freq_recommend_shift_hz_r0.7=16.0 hz
RESULT freq_recommend_shift_hz_r1.3=8.0 hz
RESULT freq_recommend_shift_hz_r1.6=16.0 hz
RESULT freq_recommend_shift_hz_r2.0=24.0 hz
RESULT perturb_gated_freq_map_folds_while_frozen=0 count
RESULT perturb_gated_clean_arm_freq_map_folds=2 count
```

The static census and the runtime count agree without sharing any machinery:
two ingest methods never mention the predicate, and both fold on all five
arms. Every folded pair was `(55 Hz, 2.00 kW)` — I printed the arguments, not
just the count.

### Attacks run

1. **Do the five arms really contaminate?** Yes, and by a better route than
   the finder's. The finder forced `freeze_reason` to the strings
   `"heat_pump_offline"` / `"heat_pump_fault"` / `"heat_pump_cooling"` via
   `object.__setattr__`. **Those strings do not exist in the tree**:
   `pump_signals.py:80-82` defines `"pump_offline"`, `"pump_fault"`,
   `"pump_cooling"`. Because `_learning_frozen` only tests `is not None`, the
   count is unaffected — but the finder's arm table reports labels production
   never produces. I rebuilt every arm from the production constants and a
   real cooling `ModeCapability` and got the same 5. **Attack lands on the
   finder's rig, not on its number; the labels in the report's table should be
   corrected to `pump_offline` / `pump_fault` / `pump_cooling`.**
2. **Is the frequency map keyed so heating and cooling separate?** **No.**
   `freq_control.py:53-96`: `buckets[decile] = [kw_per_hz_ewma, count]`, keyed
   by frequency decile index and nothing else. There is no mode dimension, no
   heating/cooling split, no outdoor-temperature key. A reverse-cycle sample
   folds into the same bucket a heating sample would, and `recommend()` reads
   it back for the heating write path at `coordinator.py:10342`. The claim's
   mechanism is confirmed. **Attack failed.**
3. **Is a cooling fold actually harmful?** Only conditionally, and I measured
   the condition. The map stores *electrical* kW per Hz — a machine
   characteristic. If a reverse-cycle compressor draws the same kW at the same
   Hz, the null control says the cost is **exactly 0.0 Hz**. A 1.6x draw
   mismatch shifts the recommended frequency by **16 Hz of an 80 Hz span**;
   2.0x shifts it 24 Hz. So the harm is real but proportional to a difference
   neither the finder nor I measured against a real unit. **Partial: the
   mechanism holds, the magnitude is bounded by an unmeasured physical ratio.**
4. **Does "all five" overstate it?** Somewhat, and a judge should hear this.
   Two of the five arms — `external_heat_source` and `ventilation` — cannot
   corrupt a kW-per-Hz map at all: a wood burn or an open window changes the
   *house*, not the compressor's electrical draw at a given speed. The three
   with teeth are `pump_offline` (a pinned/stale reading is the flatline case
   the predicate's own docstring names), `pump_fault`, and `pump_cooling`.
   The finder's report already says "the cooling arm is the one with teeth",
   so this is a framing note, not a contradiction. The count of 5 is correct
   and is a count of *gate* coverage, which is what the finding is about.
5. **Are these learners really persisted?** Yes — `_freq_map` round-trips
   through `as_dict`/`from_dict` (`coordinator.py:2568, 2642`) and
   `_start_counter` likewise (`7235, 7280`). The freeze predicate's own
   rationale ("corrupts a parameter that is persisted to disk") applies.
   **Attack failed.**
6. **Is the consequence bounded, as the finder claims?** Yes, and more tightly
   than stated. `DEFAULT_FREQ_CONTROL_MODE = "observe"` (`const.py:863`) and
   `_command_frequency` returns immediately unless the mode is `control`. But
   the **fold has no mode gate at all**, so the map is learned and persisted in
   `observe` mode too: a user who later switches to `control` inherits whatever
   the contaminated intervals taught. That is the path that earns `medium`.
   **Attack failed.**
7. **Perturbation reproduced** in an rsync copy under a private temp root, by
   re-executing my own harness inside the mutated tree: 5 -> 0 with the clean
   arm unchanged at 2. No file in this export was modified; both mutations
   (this one and D7-02's) ran only in temp copies.

---

## Method notes a judge should carry

- **Root rule.** My harnesses use `Path.cwd()` / relative `sys.path.insert`
  and were run from the root of this export, so they measured *this* tree.
  The round-2 `D7/sysid_plant.py` trap (resolving from `__file__` and
  silently measuring the tag) does not apply: the round-3 harness uses
  relative paths too, and I ran everything from the export root.
- **The one number a re-deriver will get wrong.**
  `orphan_published_attributes` comes out 0, not 1, unless the class-body
  declaration `last_dhw_refused: np.ndarray | None = None`
  (`thermal_model.py:1328`) is excluded from the reader net. See D7-02 attack 2.
- **Counts my instrument and the finder's differ on, harmlessly.** The finder
  reports `sentinel_distinct_attrs=6` and 27 062 writes; my trap reports 5 and
  40 369. Two reasons, both understood: the finder subclasses and so catches
  `self.params` in `__init__`, while my trap is installed after construction;
  and my solve uses a different price/weather series, so the solver takes a
  different number of steps. Neither figure is load-bearing — both are
  "the instrument is live" positive controls, and both are large.
- **Nothing here is a timing number**, so no verdict rests on a noisy box and
  nothing needs re-taking. `load1` is quoted per run above.
