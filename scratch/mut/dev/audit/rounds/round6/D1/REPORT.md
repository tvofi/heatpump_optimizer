# D1 - robustness and stability, audit round 6

Baseline: `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), exported at
`~/audit-r6-baseline`. Interpreter
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` (numpy 2.4.6,
scipy 1.17.1), `PYTHONPATH=tests/hastub`, run from the export root.
Machine: 8-core Apple M1, 8 GB, shared with the other round-6 auditors.
`load1` was 51-97 throughout the fan-out; every number below is a **count** or
a **ratio**, neither of which contention moves, and no wall/CPU/RSS figure is
reported. `thread_factor` is printed by each harness and is 1.00.

## Method, and what it was pointed at

The brief's six methods, in the order they were worked:

1. **Store-corruption fuzzing** (methods 2 and part of 5) - two harnesses.
   * `store_fuzz.py` - for each of the nine stores a live coordinator writes,
     220 seeded random structural mutants (type swaps, deleted and renamed
     keys, truncation, `NaN`/`+/-inf`/1e308 leaves, wrong nesting), each loaded
     through the **real** loader, then scanned for a non-finite value left on
     a named live attribute. 1 980 mutants, **0** escaped a loader.
   * `store_fuzz2.py` - a systematic pass instead of a random one: for each of
     the eleven stores, **every numeric leaf of the healthy payload in turn**
     is replaced by each of nine non-finite substitutions, so no key can be
     missed by bad luck. This is the pass that found both findings. It walks
     `HeatPumpOptimizerCoordinator._thermal_params` - the object the solver
     reads - and `_build_data_dict()` - the object every entity reads.
2. **Staleness** (method 3) - `staleness_probe.py`, a ten-cell grid of frozen
   and jumped clocks against `InputReader.read`. Held; see non-findings.
3. **Guards** (method 5) - folded into the two fuzzers' "does the corrupt part
   get quarantined or reset, with a log line?" arm, plus a log capturer in both
   finding harnesses that counts WARNING-or-worse records the integration emits
   while a corrupt store is loaded.
4. **Executor boundary** (method 4) - **not completed**. See *What I could not
   finish*.
5. **External-input parsers** (method 6) - **not completed**. See the same
   section.
6. **Real-loop lifecycle** (method 1) - **not completed**. See the same
   section.

Numbers, not arguments, throughout. Group by phenomenon: the two findings share
one root mechanism - *a persisted scalar is converted with `float()` and no
finiteness test, so a non-finite stored value is neither quarantined nor reset*
- and are reported separately because each has its own instrumented symbol, its
own one-line perturbation and its own consequence, so the fix wave can take
them as independent one-line changes. The shared root is stated in each.

---

## Finding D1-01 - a non-finite persisted tank cooling rate reaches the live model and is never reset

**Severity** high - **stop-rule class** bug

**Claim.** A DHW-profile store whose `cooling_rate` is `NaN` (or the string
`"NaN"`) installs a non-finite value on the live
`ThermalModel.params.dhw_cooling_rate`; it is never quarantined, never reset,
and emits no log line, so `ThermalModel.dhw_hold_hours()` - the lead-time the
DHW planner reads as `max_lead_hours` - is non-finite too, the non-finite
value is republished in the coordinator's payload, and it is written back
non-finite on every later save.

**Mechanism.** `DhwProfileLearner.async_load_profile` parses the stored rate
with `float(rate)` under `(TypeError, ValueError, OverflowError)`;
`float("nan")` and `float("NaN")` raise nothing. It then calls
`apply_cooling_rate`, which is `float(np.clip(rate, MIN, MAX))` - and `np.clip`
**propagates** NaN. The same absence is not present one module over: the four
sibling learned scalars dispatched from `_async_load_thermal_learning`
(`buffer_cooling_rate`, `house_heat_loss_scale`, `lower_floor_loss_ratio`,
`cop_scale`) are each wrapped in `coordinator:_refuses_non_finite`, whose own
docstring names this exact hazard - *"`float('nan')` raises nothing ... a
corrupted store reaches `np.clip`, which propagates NaN onto the live model"*.
`apply_cooling_rate` is the fifth seam of that family and is the one without
the guard. Once installed the value is self-perpetuating: the learner's own
EWMA is `(1-alpha)*self.cooling_rate + alpha*observed`, and `NaN` absorbs it,
so every later fold leaves the rate non-finite and `async_save_profile` writes
it straight back. Reachability is not a special topology: `dhw_enabled` is true
whenever a tank volume, a DHW temperature entity or DHW windows is configured
(`thermal_model:_dhw_enabled_from_config`), which is the ordinary install.

**Instrumented symbol.** `dhw_learning:DhwProfileLearner.apply_cooling_rate`,
driven through `dhw_learning:DhwProfileLearner.async_load_profile`; read back
through `thermal_model:ThermalModel.dhw_hold_hours` and
`coordinator:HeatPumpOptimizerCoordinator._build_data_dict`.

**Perturbation.** Wrap `apply_cooling_rate` so a non-finite argument is dropped
instead of clamped - one line, the guard its four siblings already have
(`coordinator:_refuses_non_finite`). Expected direction **down, to zero**. The
harness applies it by monkey-patch and reverts it in a `finally`; the fix
belongs in `dhw_learning.py` (which cannot import the coordinator's decorator
without a cycle, so a local `math.isfinite` test).

**Metric definition.** `nonfinite_live` - the number of non-finite values among
`DhwProfileLearner.cooling_rate`, `ThermalModel.params.dhw_cooling_rate`,
`ThermalModel.dhw_hold_hours()`, `data["dhw_cooling_rate"]` and
`data["dhw_hold_hours"]` after a reload of the corrupted store.

**Evidence.** `tools/audit/round6/D1/dhw_cooling_ratchet.py`

```
PYTHONPATH=tests/hastub python3 tools/audit/round6/D1/dhw_cooling_ratchet.py

RESULT log_warnings_on_corrupt_load=0 count
RESULT nonfinite_live=5 count
RESULT nonfinite_live_perturbed=0 count
RESULT resaved_nonfinite=1 count
RESULT resaved_nonfinite_perturbed=0 count
RESULT ewma_fold_nonfinite=1 count
RESULT ewma_fold_nonfinite_perturbed=0 count
RESULT null_control_finite=0 count
RESULT substitution_cells=6 count
RESULT substitution_min=0 count
RESULT substitution_max=5 count
RESULT substitution_drop_most_favourable=0 count
RESULT thread_factor=1.0000
RESULT load1=74.97
```

Per substitution cell (`nonfinite_live`): `float('nan')` **5**, `'NaN'` **5**,
`float('inf')` 0, `float('-inf')` 0, `'Infinity'` 0, `1e309` 0. The four
infinities are clamps, not refusals - `np.clip(+/-inf, MIN, MAX)` lands on the
bound - so this hole is NaN-shaped, and a fix that only clamped would not close
it.

*Null control.* The same measurement with the healthy payload's own rate and
with `0.42`: `nonfinite_live=0` and `resaved_finite=True`. The count is a
property of the corrupt input, not of the load path.

*Leave-one-out.* Six substitution cells, min 0, max 5; dropping the single most
favourable cell leaves 0. That is reported as it is: the phenomenon is carried
by the two NaN-shaped cells, and the grid is dominated by the four `inf` cells
that `np.clip` already handles. The judge should read the five landing sites,
not the grid mean.

*Permanence.* One real learner fold on top of the installed rate:
baseline `nan` (non-finite), perturbed `0.312` (finite). The store is never
rewritten with a finite default, so the next cycle repeats the failure -
which is the criterion the brief sets.

**Files.** `custom_components/heatpump_optimizer/dhw_learning.py`
(`async_load_profile` ~l.186, `apply_cooling_rate` l.202),
`custom_components/heatpump_optimizer/thermal_model.py` (`dhw_cooling_rate` l.439,
`dhw_coast_hours` l.1763, `dhw_hold_hours` l.1747),
`custom_components/heatpump_optimizer/optimizer.py` l.4689
(`max_lead_hours = self.model.dhw_hold_hours()`).

**Proposed fix scope.** One guard in `DhwProfileLearner.apply_cooling_rate`
(drop a non-finite rate, leaving the previous finite value in place, and log it
once) plus the same test in `async_load_profile`. No golden fixture should move
- the healthy path is byte-identical.

---

## Finding D1-02 - a non-finite persisted defrost duty silently becomes the floor derate

**Severity** high - **stop-rule class** bug

**Claim.** An accuracy store carrying `NaN` in one cell of `defrost.duty`
survives the load, is never quarantined or reset, emits no log line, and makes
the model price *every* step in that temperature/humidity bucket at 55 % of the
COP it should use - `DERATE_MIN`, the module's own "this is not physics, your
sensor is broken" floor - for as long as the store is kept.

**Mechanism.** `DefrostDerate.from_dict` builds both grids through a shared
local `_grid_of(key, cast)` helper that does `cast(v) for v in row` with no
finiteness test. It is then asymmetric in exactly the way that hides the bug:
the **sibling** grid, `factors`, is re-clamped with `min(DERATE_MAX,
max(DERATE_MIN, v))` on the next lines, and Python's `max(DERATE_MIN, nan)`
happens to return `DERATE_MIN` - a bound, not a NaN - so `factors` is safe by
accident. `duty` gets no such clamp, and `float("nan")` raises nothing, so the
NaN lands on `ThermalModel.params.defrost_derate.duty[t][h]`. The reader,
`derate_from_duty`, is the second half of the trap: its `min(max(float(duty),
0.0), DEFROST_DUTY_MAX)` **also** returns the bound for NaN, so the NaN becomes
`DERATE_MIN = 0.55` rather than a NaN, and the failure is silent rather than
loud. A bucket only needs `duty_counts[t][h] >= 1` for the measured estimator
to be consulted (`DefrostDerate._decide`), and the store keeps its counts
beside its duty, so a store that had genuinely learned a duty there carries
them.

**Instrumented symbol.** `defrost:DefrostDerate.from_dict`, driven through
`coordinator:HeatPumpOptimizerCoordinator._async_load_accuracy`; read back
through `thermal_model:ThermalModel.compute_cop`.

**Perturbation.** Give `_grid_of`'s `duty` call the finiteness test its sibling
grid already gets by accident - one line in `DefrostDerate.from_dict`. Expected
direction: `cop_ratio` **up, to 1.0** and `nonfinite_duty_live` **down to 0**.
Applied by monkey-patch and reverted in a `finally`.

**Metric definition.** `cop_ratio` - `ThermalModel.compute_cop(T, H)` at the
poisoned bucket after loading the corrupted store, divided by the same call
from the same code with the healthy store.

**Evidence.** `tools/audit/round6/D1/defrost_duty_floor.py`

```
PYTHONPATH=tests/hastub python3 tools/audit/round6/D1/defrost_duty_floor.py

RESULT log_warnings_on_corrupt_load=0 count
RESULT cop_ratio=0.550000 ratio
RESULT cop_ratio_perturbed=1.000000 ratio
RESULT cop_ratio_null_control=1.000000 ratio
RESULT derate_floor=0.550 ratio
RESULT nonfinite_duty_live=1 count
RESULT nonfinite_duty_live_perturbed=0 count
RESULT substitution_cells=8 count
RESULT substitution_min=0.550000 ratio
RESULT substitution_max=0.550000 ratio
RESULT substitution_drop_most_favourable=0.550000 ratio
RESULT thread_factor=1.0000
RESULT load1=70.65
```

*Null control.* The healthy payload through the same loader:
`cop_ratio_null_control=1.000000` by construction, `nonfinite_duty_live=0`.
The ratio is a property of the corrupt cell, not of the measurement.

*Leave-one-out.* Eight cells (six temperature buckets at RH 50, two humidity
buckets at RH 85), min 0.550000, max 0.550000, drop-most-favourable 0.550000.
The effect is flat across buckets, so no single cell carries it.

**Consequence, executed.** At the poisoned bucket `compute_cop` returns
1.106875 against a healthy 2.012500 (bucket -30..-5 degC), 1.732500 against
3.150000 (2..5 degC) and so on - **0.55x at every one of the eight cells**. The
`_decide` summary reads `factor=0.550` for each. Every price the plan derives
in that band is therefore built on a COP 45 % below the model's own nameplate
curve, and `_settle_defrost` will go on folding real measured duty into the
neighbouring cells while this one stays poisoned.

**Files.** `custom_components/heatpump_optimizer/defrost.py`
(`from_dict` l.375, the `_grid_of` helper l.405, `derate_from_duty` l.149,
`DERATE_MIN` l.97), `custom_components/heatpump_optimizer/coordinator.py`
(`_async_load_accuracy` l.7141), `custom_components/heatpump_optimizer/thermal_model.py`
l.1474 and l.2623 (every COP a plan is priced through).

**Proposed fix scope.** One finiteness test in `DefrostDerate.from_dict`'s duty
grid (`v if math.isfinite(v) else 0.0`), matching what `factors` gets by
accident and what `duty_counts` gets for free. No golden fixture should move.

---

## Non-findings - what was checked and held

| claim | command | value |
|---|---|---|
| No store loader lets an exception escape on a random structural mutant: 9 stores x 220 seeded mutants | `PYTHONPATH=tests/hastub python3 tools/audit/round6/D1/store_fuzz.py` | `RESULT loader_escape_total=0 count` over `RESULT mutants_per_store=220 count` x 9 |
| No store loader lets an exception escape on a *systematic* sweep either: every numeric leaf of 11 stores x 9 non-finite substitutions | `PYTHONPATH=tests/hastub python3 tools/audit/round6/D1/store_fuzz2.py` | `RESULT loader_escape_total=0 count` |
| The four learned scalars guarded by `coordinator:_refuses_non_finite` hold against every non-finite substitution | same as above (store `thermal_learning`) | `model_poison_total` attributable to the thermal store = **0** of 207 mutants |
| `price_model`, `ledger`, `energy`, `manual_plan`, `snapshots`, `dhw_draws`, `away` leave nothing non-finite on the live model or in the published payload | same as above | 0 for each (`RESULT stores_swept=11 count`, poison concentrated in `accuracy` 96 and `dhw_profile` 2 of 4 379 mutants) |
| `InputReader.read` rejects every hostile stamp on a ten-cell clock grid: 4-hour-old report, report stamped 1 h and 7 d ahead of now, a 2-day forward clock jump and a 2-day backward clock jump (`#775`), and the raw states `unknown`/`unavailable`/`None` | `PYTHONPATH=tests/hastub python3 tools/audit/round6/D1/staleness_probe.py` | `RESULT accepted_cells=2 count` of `RESULT cells=10 count`, `RESULT cells_disagreeing_with_the_grid=0 count`; only the 5-minute-old stamp under a still clock and the untimestamped one are accepted |
| The three files' loaders emit **no** log line when they silently accept a non-finite scalar | both finding harnesses | `RESULT log_warnings_on_corrupt_load=0 count` - this is the brief's acceptance criterion failing, and it is what makes D1-01 and D1-02 defects rather than notes |

## What I could not finish

Three of the brief's six methods were not carried out, and their absence is
recorded rather than papered over.

- **The real-loop lifecycle harness (method 1).** The valid form needs the
  config-entry state machine, and `ha_setup_entry` drives
  `async_config_entry_first_refresh`, which reaches `_fetch_tibber_prices` and
  needs a price source configured with a state fixture. My smoke attempt raised
  `ConfigEntryNotReady: no HTTP session available in the test stub` and I did
  not get a working fixture within the budget. `tests/golden.py:_capture_coordinator`
  is the right builder and its `_prices` injection is the missing piece; the
  trap the brief names - *a race reproduced only by calling a lifecycle method
  directly is a stub artefact* - is why I stopped rather than reporting a
  direct-call result.
- **The executor boundary (method 4).** Read, not executed. `_solve_snapshot`
  deep-copies `_current_state`, `_thermal_params` and `_opt_config` **on the
  event loop, immediately before** `await _await_optimize`, and `_warm_seeded`
  copies `_optimization_result.power_schedule` rather than retaining the
  coordinator, so the solve shares no mutable state with the loop. That is an
  argument from reading, and it is reported as one; no number here.
- **The external-input parsers (method 6).** Not driven. `_parse_ecl110_state`
  was visibly hardened for exactly this class (`#1090`: NaN and malformed
  payloads dropped whole), and `InputReader` for the sensor states, but the
  Tibber, Open-Meteo and weather-forecast responses were not fuzzed.

Two harness gaps worth naming for the next round:

- **`dhw_legionella` produced no healthy payload.** `LegionellaTracker.async_save`
  returns early while `last_cycle is None`, so the saved-store round trip the
  other ten stores go through could not be built by the same route. Its loader
  was still driven by the random fuzzer (0 escapes) but not swept
  leaf-by-leaf.
- **`manual_plan` and `boost` swept 0 numeric leaves**, because the healthy
  payloads are `{}` - a fresh coordinator has no override and no held boost.
  Those two stores were exercised for *type* corruption only. A next round
  should seed an override and a boost channel first.

`ComfortLearner.from_dict` also accepts a non-finite `learned_weight` (the
systematic pass found 16 published-payload mutants through it), but it is
**not** reported as a finding: the value's only reader is
`ComfortWeightSensor.extra_state_attributes`, which
`HeatPumpOptimizerSensorBase.__init_subclass__` scrubs, and
`_apply_comfort_weight` only pushes it into `_opt_config.comfort_weight` when
`CONF_COMFORT_LEARNING_ENABLED` is set, which defaults to `False`. Recorded
here so the next round does not re-derive it, and so the guard can be added
when the flag is turned on.

`_load_t4b_learners` accepts a non-finite `internal_gains_profile` and no
finiteness test is applied, unlike its sibling `solar_aperture` in the same
five lines; it is not reported because the profile only reaches
`_opt_config`/`ThermalModel` when `CONF_INTERNAL_GAINS_LEARNING_ENABLED` is
set, which also defaults to `False`. The asymmetry is real and worth one line
of the same fix.

## Exposure

None. This dimension's brief points at the tree's own harnesses and builders;
no earlier audit record, `docs/audit-*.md`, `docs/backlog.md`, `gh` call or
GitHub page was read, and `tools/audit/round{3,4,5}/` was not opened.

## Harnesses

- `tools/audit/round6/D1/store_fuzz.py`
- `tools/audit/round6/D1/store_fuzz2.py`
- `tools/audit/round6/D1/dhw_cooling_ratchet.py`
- `tools/audit/round6/D1/defrost_duty_floor.py`
- `tools/audit/round6/D1/staleness_probe.py`

Each carries the header the harness contract requires (metric definition, the
single command, the expected value, the baseline SHA, the machine), pins the
BLAS thread count before importing numpy, runs from the repository root, writes
only under its own directory or the in-memory `tests/hastub` store, prints one
`RESULT <name>=<value> <unit>` per number, and prints `thread_factor` and
`load1` at the end. None of them `cd`s, resolves a root from `__file__`,
invokes a Node harness, or touches `HPO_PLANDATA`.
