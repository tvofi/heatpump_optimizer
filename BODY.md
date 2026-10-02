_Requested by **tvofi**_

Part of #1737 (R9-EG-B3a). The coordinator's published payload had no typed contract: `DataUpdateCoordinator` was unparameterised, so `.data` was `Any` and every read of a key was a bare string. This adds `custom_components/heatpump_optimizer/payload.py`, a `total=False` TypedDict (`Payload`) of every key `_build_data_dict` and `_with_sensor_advisor` can publish, parameterises `DataUpdateCoordinator[Payload]`, and has `entity._data()` return it. A subscript read of a key `Payload` does not declare, and a `.get()` whose result reaches a typed sink, is now a strict-census error; a bare `data.get("typo")` whose result goes to an `object`-accepting sink is not. No runtime change: the producers are untouched, `_build_data_dict` still builds a plain dict and returns it through `cast(Payload, ...)` (the producer side is B3b's).

The issue is split because the full contract (about 620 lines drafted) does not fit one PR. This is B3a; the rest is under "Owed to R9-EG-B3b" below. The issue stays open.

## For tvofi: a `tests/hastub` edit

`tests/hastub/homeassistant/helpers/update_coordinator.py`: `DataUpdateCoordinator` and `CoordinatorEntity` become `Generic[_DataT]`. Upstream's are Generic, and without it `DataUpdateCoordinator[Payload]` raises `TypeError` under the stub at import. It adds a base class and a `TypeVar`; it changes no behaviour.

## Round 2 (review of 2261e2a4 blocked on the contract)

Fixed: `wear_price_per_start` moved from `Insight` into `CompressorStarts`, where `_insight_view` writes it; the top-level `valve_target_schedule` is removed (only `space_plan["valve_target_schedule"]` exists, owed to B3b below); `dhw_disinfection_switch`, spread from `DisinfectionSwitch.view()`, is declared with its real type. The cast hid all four, so the cause is that no instrument compared `Payload` with the producers. `tests/entities.py` now does, with this rule: the keys of every dict a payload producer returns, assigns to what it publishes or passes to `update`, plus its `data["k"] =` stores; every `**x` or `update(x)` source resolves through a table that fails on a source it does not list, so a new spread cannot slip past. The producers are the assembler, the views it loops over, `_apply_result_payload`, `_apply_unsolved_payload` and `_with_sensor_advisor`, found from the AST. The check requires `Payload`'s keys to equal that set, and `Insight` and `CompressorStarts` to equal what `_insight_view` writes.

## Head

Code head `684b5a1e354c875d380ec693f8ac58eb574b787a`, on `origin/main` `4e2582e79` (2026-10-02T15:01Z).

## Mutation proof

The census is the check this PR adds, so the mutants run it. Production cost is zero lines of runtime change; the proof is that breaking the contract turns the census red:

- M1, delete the `horizon_hours` key from `Payload`: 2 strict errors.
- M2, rename the read `get("horizon_hours", ...)` in `sensor.py` to `get("horizon_hourz", ...)`: 2 strict errors. Both go red through `float(object)` (`arg-type`), not through a missing-key error, which is why the claim above is narrowed.
- Unmutated head: 0 errors.
- The new `tests/entities.py` check (EG-B3 rows): run against the round-1 `payload.py` it fails twice, naming `dhw_disinfection_switch` as published-not-declared, `valve_target_schedule` as declared-not-published, and `wear_price_per_start` on both `Insight` and `CompressorStarts`; against this head it passes. The block ran standalone here, because the full script needs scipy.

Command for each: `HPO_TYPING_PYTHON=$PWD/.venv/bin/python python3 tests/typing_ruler.py --mypy` reads the same invocation; the counts above are `mypy --strict --warn-unused-ignores --show-error-codes --python-version 3.14 custom_components/heatpump_optimizer | grep -c error:` with the pinned toolchain.

## Null control

Origin/main prints 0 errors under that command and has no `Payload` to delete a key from: its `DataUpdateCoordinator` is unparameterised, so `.data` is `Any` and a read with no producer type-checks. At this head the same deletion is 2 errors (M1 above). A larger control: deleting three keys (`horizon_hours`, `measured_cop`, `reading_ok`) moved the census 10 to 17 on the earlier, wider draft, with the 7 new errors in `binary_sensor.py`, `climate.py` and `sensor.py`.

## Figures

- Production lines: 404 added, 28 deleted under `custom_components/` (`git diff --numstat $(git merge-base origin/main HEAD) HEAD -- custom_components`); `payload.py` is 373 of them. The cap is fixer.md's "about 400".
- Strict census at this head: 0 errors, mypy 2.3.1 with homeassistant-stubs 2026.9.3, Python 3.14.7 (`python3 tests/typing_ruler.py --print-requirements` names the pins).
- Census on the first wired draft, before the 10 errors were fixed: 10 errors (coordinator 3, sensor 5, entity 1, binary_sensor 1). Fixed here: the missing `sensor_advisor` key, return types of `_async_update_data`, `_async_first_refresh_light` and `_republish_handover_ages`, `_reload_handover`, three helper parameters typed `Payload`, and narrowing in `sensor.py` and `binary_sensor.py`.
- Keys: 173 published, 173 declared, equal both ways under the rule in Round 2 (the EG-B3 rows of `tests/entities.py`; run standalone, 0 unresolved sources). The five `tests/golden/coord_*.json` fixtures alone were the first instrument and missed the conditional keys; that is why the rule above replaces them.
- Architecture score, instrument not in this tree: the prototype on branch handoff/audit-r9-alt (its b/arch_score.py with --delta, vectors from b/measure_vec.py over git archive exports of origin/main and the round-1 head, the red-team counters swapped in as score_proto.py does). It printed untyped_payload_keys 166 to 0 and delta-S +50.98. **That figure overstates the result and is not progress under the issue's rule.** The counter stops tracing at `return cast(Payload, data)`, so it reaches 0 because it lost the producer (the review measured produced=3 at that head), not by finding typed keys. And it counts `dict[str, object]` as typed: 23 of the 173 top-level keys, and 6 nested fields, are exactly that, and the issue says an `Any` or `object` typed key is not progress. The delta-S was not re-derived at this head. The score is report-only, and R9-EG-A1 owns the in-tree copy.
- Seams the new class could open (fixer.md step 8): no coordinator method added, so `tests/seam_map.json` and the coordinator rows of `tests/structure_budgets.json` do not move. `python3 tests/structure.py` passes.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, reason: no recorded closure mentions `payload.py`. That is the UNDER-SCOPED the autofix job repairs (`ci-autofix.md`); I did not run `derive_closures.sh`.

Not run locally, on CI: `tests/entities.py` and every numeric script, which need scipy this seat lacks. Run locally: `tests/structure.py`, `tests/ha_contract.py` (4 of 4), the typing ruler and the census above.

## Red checks

none.

## Forward-carry

none: the destination is a roster group, R9-EG-B3b, which the orchestrator creates from the section below on handoff/audit-r9-fixplan, a branch this tree does not carry. Placeholders typed dict[str, object] are named there so the next stage cannot read this one as complete.

## Owed to R9-EG-B3b

B3b must do exactly this, and the issue closes with it. Until it does, `untyped_payload_keys` is not honestly 0:

1. Give each of these a fixed-shape TypedDict in place of `dict[str, object]`, field types read from the producer and confirmed with `reveal_type`: `heat_pump_signals`, `battery`, `wood_fuel` (including `night_advice`, which `sensor.py` reads and `build_wood_fuel_view` does not set at the top level), `accuracy`, `price_prior`, `external_heat`, `system_identification`, `defrost_buckets` items, `comfort_learning`, `heat_curve`, `contract_comparison`, `power_headroom`, `pv`, `dhw_advisor`, `schedule` and `dhw_schedule` items, and `space_plan` / `dhw_plan` with their forecast and slot items, including `space_plan["valve_target_schedule"]` (a `list[float]` the producer sets only when a hold schedule was adopted, `_build_plan_views` in `coordinator.py`). `PeakTariff` is already typed here.
2. Confirm two shapes drafted from partial reads: the plan `slots` items (`_plan_slots`, `coordinator.py`) and `price_prior` (`PriceShapeModel.summary()` in `price_model.py`).
3. Decide, per key, which of these stay open-ended and say why in `payload.py`: `predictive_info`, `last_diagnosis`, `monthly_report`, `fuse_advisor`, `ecl110_last_payload`, `solar_diagnostics`, `sensor_advisor`, `FreqControl.map`, `SystemIdentification.result`, `Narrative.items`, `ManualPlan.released_space` and `released_dhw`. Each is built by a producer typed `dict[str, Any]` or through `_plain_types(...) -> Any`.
4. Remove `cast(Payload, data)` in `_build_data_dict`: give each view (`_thermal_view`, `_dhw_view`, `_learning_view`, `_measurement_view`, `_grid_view`, `_ecl110_view`, `_external_heat_view`, `_input_health_view`, `_mixing_valve_view`, `_plan_settings_view`, `_insight_view`, `_freq_view`, `_build_plan_views`, `_apply_result_payload`, `_apply_unsolved_payload`) a slice TypedDict return type, with `Payload` inheriting the slices, so mypy checks each producer against its slice. Many producer values are `Any` today (`result: Any`, `getattr(self, "_ctx", self)`), so this step needs those sources typed too, or each value read through a typed local.
5. Derive the hand-written payload shape `DATA` in `tests/entities.py` from `Payload` (issue #1737's third bullet), and make a read with no producer fail there.
6. Re-run `arch_score.py --delta` with the counters swapped in and report `untyped_payload_keys` where no key is `dict[str, object]`; per the issue, an `Any` or `object` typed key is not progress.

## Friction

none.
