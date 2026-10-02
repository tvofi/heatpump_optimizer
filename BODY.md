_Requested by **tvofi**_

Closes #1737 (R9-EG-B3b, the remainder of the typed payload contract; B3a is #1852). `_build_data_dict` handed `cast(Payload, data)` out, so mypy never saw a producer. This removes the cast. Each assembler view now returns a slice TypedDict that `Payload` inherits, every fixed-shape report has its own TypedDict, and the typing job checks each producer's literal against the keys it may publish. The five store patterns the B3a enumeration check cannot see are mypy errors now (item 8 of the carried findings), so that check is not extended.

## What changed

- `payload.py`: one TypedDict per fixed-shape report named in the brief (`heat_pump_signals`, `battery`, `wood_fuel` with `night_advice`, `accuracy`, `price_prior`, `external_heat`, `system_identification`, `defrost_buckets` items, `comfort_learning`, `heat_curve`, `contract_comparison`, `power_headroom`, `pv`, `dhw_advisor`, the `schedule` and `dhw_schedule` items, `space_plan` / `dhw_plan` with forecast and slot items), plus the slices `Payload` inherits (`ThermalView`, `DhwView`, `LearningView`, `MeasurementView`, `GridView`, `Ecl110View`, `ExternalHeatView`, `InputHealthView`, `MixingValveView`, `AwayView`, `EnergyTotals`, `SolvedSlice`).
- The views, `_build_plan_views`, `_apply_result_payload` and `_apply_unsolved_payload` carry those return and parameter types. `_current_action` is a `CurrentAction` end to end (`optimizer.get_current_action`, `boost`, `legionella`).
- Producers outside the coordinator gained return types: `PumpSignals.as_dict`, `SystemIdentification.as_dict`, `AccuracyTracker.summary`, `ComfortLearner.summary`, `CurveLearner.summary`, `DefrostDerate.summary`, `PriceShapeModel.summary`, `ExternalHeatState.as_dict`, `VirtualBattery.as_dict`, `build_wood_fuel_view`, `pv.summarize`, `CapacityTariff.billing_summary`, `MonthlyLedger.savings_months`, `InputHealth.details`, `AwayState.as_dict`, `DisinfectionSwitch.view`, `narrative.build`, `FrequencyMap.summary`, `OpenMeteoSolar.diagnostics`, `topology.rank_sensor_advisor`.
- The slices join the payload through `data = {**data, **view()}`, not `data.update(view())`. Under the pinned ruler's flags (`--strict`, which turns `extra_checks` on) `update` takes the whole payload's keys and refuses a slice, and a display with a `**` item must cover every key, which `**data` does. The loop over the nine bound views is kept as it was.
- Open-ended keys, decided one by one and reasoned in the `payload.py` docstring: `predictive_info`, `last_diagnosis`, `monthly_report`, `fuse_advisor` (restored from the ledger store by `_stored_fuse_advisor`), `ComfortLearning.recent_overrides` and `ManualPlan.released_space` / `released_dhw` (stored records kept after an `isinstance(dict)` check). The first draft of this decision also kept `solar_diagnostics`, `ecl110_last_payload`, `sensor_advisor`, `FreqControl.map`, `Narrative.items` and `SystemIdentification.result` open; reading their producers showed each is a single fixed-shape literal, so they are typed.
- `tests/entities.py`: the EG-B3 enumeration reads `Payload`'s inherited keys (its own keys are only `sensor_advisor` now); four new EG-B3b checks pin what mypy cannot see (below). `DATA` lost a key no producer sets.
- `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._build_data_dict.RETURN_DEL.54602010.json` is deleted: it pinned the line `return cast(Payload, data)`, which no longer exists (`mutation_table.py` refuses an orphan pin).

## Findings from the carried review (item 7), re-measured at this merge base

Two of the four disagreements the #1852 review named were already gone at `03ba7f70f`: `Insight.wear_price_per_start` and the top-level `valve_target_schedule` are not in `Payload`, and `compressor_starts.wear_price_per_start` and `dhw_disinfection_switch` are declared. What was left, and a pair the review did not name, found by the same mypy run:

- `space_plan.valve_target_schedule` is `SpacePlan.valve_target_schedule: list[float]`; a misspelling of it is an `Extra key` error.
- `CurrentAction` lacked `boost_space` and `boost_dhw`, which `boost.overlay` writes into the published action. Added.
- `PeakTariff` declared twelve keys; `CapacityTariff.billing_summary` sets three (`price_per_kw`, `window_minutes`, `peaks_averaged`), and the other nine are the persisted peak store's keys (`store.py`). Trimmed to the three.
- `DATA["contract_comparison"]` carried `months`, a key no producer sets; it also made `ContractComparisonSensor` publish a `months` attribute in the entity sweep. Replaced by the declared `month`, and the expected attribute set follows.

## Head

Code head `25aa0c807c290e1642ddad1fa92761371150ec03` on `origin/main` `03ba7f70f007147bda32ac0fc5dd83b11499bbaf` (fetched 2026-10-02T22:45Z). `origin/main` had not moved since #1852 when this was written.

## Mutation proof

Run on detached worktrees of the head, each with one mutation, `tests/entities.py` only:

- M1, put `return cast(Payload, data)` back in `_build_data_dict`: 1 of 2085 checks red, `EG-B3b: _build_data_dict returns Payload and casts nothing`.
- M2, remove `MixingValveView` from `Payload`'s bases: 2 of 2085 red, `EG-B3: Payload declares exactly the keys the producers publish` (published-not-declared: `mixing_valve_mode`, `valve_target_recommendation`) and `EG-B3b: every view the assembler merges returns a slice Payload inherits`.
- M3 (typing census), a probe module with the five patterns the enumeration check misses, each on a `Payload`: `d.setdefault("zzz", 1)`, `d |= {"zzz": 1}`, `d.update(zzz=1)`, `d[_K] = 1` with `_K: Final = "zzz"`, and `handover["zzz"] = 1`. Mypy prints one error for each, five in all (codes `typeddict-item`, `misc`, `call-arg`, `typeddict-unknown-key` twice). The same probe also errors on `d["valve_target_schedule"] = []` and `i["wear_price_per_start"] = 1.0` on an `Insight`.
- The new `DATA` check, run on `DATA` plus the stale `contract_comparison.months`: names exactly `contract_comparison.months` (the check's own null control, in the check).

## Null control

The same planted edit at `origin/main` and at the head: two lines added to `_measurement_view`'s return, `"zzz_undeclared": 1` and `"measured_power": "wrong type"`. At `origin/main` mypy prints 0 errors, because the cast hid the view. At the head it prints 2, `Extra key "zzz_undeclared" for TypedDict "MeasurementView"` and `Incompatible types ... "measured_power" has type "float | None"`. Unmutated head: 0 errors.

Behaviour is unchanged by the typing: `python3 tests/env_drift.py` against `origin/main` reports NO UNCLAIMED DRIFT over the five golden scenarios (whose published dicts are what moved if anything did), and `tests/features.py` fails exactly the one check it fails at `origin/main` on this machine (R9-F2.1 P3, BLAS).

## Figures

- Strict census at the head: `env -u PYTHONPATH <venv-with-the-pinned-toolchain>/bin/python tests/typing_ruler.py --mypy`, errors did not grow, type_ignores did not grow. The toolchain is mypy 2.3.1 and homeassistant-stubs 2026.9.3 on Python 3.14.7 (`python3 tests/typing_ruler.py --print-requirements` names the pins); it was built here from those two pins plus the ruler's third-party names, not from the hash-pinned lock, which is Linux only.
- Structure ratchet: `python3 tests/structure.py` passes with no budget moved. The coordinator class sits at its recorded `max_class_loc` and `seam_cut_total`; both are at zero headroom, and an intermediate head that unrolled the view loop into nine calls raised `seam_cut_total` by 6 (the loop of bound methods hides those calls from the metric) and was abandoned for the `{**data, **view()}` loop instead of recording a raise.
- Production lines: `git diff --numstat $(git merge-base origin/main HEAD) HEAD -- custom_components`, of which `payload.py` is most. Over fixer.md's "about 400": the brief splits B3a from B3b for exactly this, and almost all of it is declarations.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`.
- Architecture score, instrument out of tree: the prototype's score script with its delta flag, and its vector script, both from branch handoff/r9-eg-archscore at b74fc1aa2, run over archive exports of `origin/main` and the head. `untyped_payload_keys` is 0 at both ends: the counter marks `dict[str, object]` as typed, because it rejects only a bare `Any` or `object`. By its rule the key count cannot show this PR. Counted by hand with `ast` over `payload.py`'s class bodies, annotations naming `dict[str, object]`: 29 at the merge base, 7 at the head, each of the 7 on the open-ended list above. The score's verdict is WORSENS on `coord_footprint` +1, a metric quirk: the footprint treats `return cast(Payload, data)` as a bare delegation (not counted) and `return data` as a logic statement (counted), so removing the cast is +1 statement in `_build_data_dict`. Every other term is flat.
- Run locally under Python 3.14.7 with numpy 2.5.3 and scipy 1.18.1 at this head: `tests/entities.py` (ALL 2085 PASSED), `tests/structure.py`, `tests/harness_headers.py` (ALL 94 PASSED), `tests/deployment_shape.py`, `tests/typing_ruler.py`, `tests/plan_view.py`, `tests/manual_plan.py`, `tests/wood_advisor.py`, `tests/edge.py`, `tests/guard_pins.py`, `tests/finite_boundary.py`, `tests/doc_claims.py`, `tests/config_flow_steps.py`, `tests/validate.py`, `tests/solar_alignment.py`, `tests/env_drift.py`, `tests/features.py` (1 of 3652 red, the same check at `origin/main`).
- Not run locally: `tests/golden.py`, `tests/optimality.py`, `tests/backtest.py`, `tests/stress.py` (BLAS-dependent, CI), the two `card` scripts (no card change), and `tests/mutation_table.py --scope changed` (it mutates the tree in place; CI's `mutation` job is its oracle, and it will pin the sites this diff rewrote).

## Red checks

none at this head by anything run here. What CI will record is mechanical and named so nobody repairs it by hand: `closures` (UNDER-SCOPED; about twenty producer modules now import `payload.py`) and `mutation` (new unpinned sites in the rewritten functions) are the autofix jobs' (`ci-autofix.md`); `tests/deployment_shape.py`'s selection-cost note passed here and follows the recorded closures.

## Forward-carry

none.

## Friction

structure-ratchet: unenforced: `seam_cut_total` counts only `self.method()` Call nodes, so the same coupling costs nothing as a tuple of bound methods and 6 as nine calls; it is why this PR keeps the loop (`tests/structure.py`, the seam-cut rule).
