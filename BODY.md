_Requested by **tvofi**_

Part of #1737 (R9-EG-B3a). The coordinator's published payload had no typed contract: `DataUpdateCoordinator` was unparameterised, so `.data` was `Any` and every read of a key was a bare string. This adds `custom_components/heatpump_optimizer/payload.py`, a `total=False` TypedDict (`Payload`) of every key `_build_data_dict` and `_with_sensor_advisor` can publish, parameterises `DataUpdateCoordinator[Payload]`, and has `entity._data()` return it. A read of a key no producer sets is now a strict-census error. No runtime change: the producers are untouched, `_build_data_dict` still builds a plain dict and returns it through `cast(Payload, ...)` (the producer side is B3b's).

The issue is split because the full contract (about 620 lines drafted) does not fit one PR. This is B3a; the rest is under "Owed to R9-EG-B3b" below. The issue stays open.

## For tvofi: a `tests/hastub` edit

`tests/hastub/homeassistant/helpers/update_coordinator.py`: `DataUpdateCoordinator` and `CoordinatorEntity` become `Generic[_DataT]`. Upstream's are Generic, and without it `DataUpdateCoordinator[Payload]` raises `TypeError` under the stub at import. It adds a base class and a `TypeVar`; it changes no behaviour.

## Head

Code head `8eba0f4989d211e3111e6966bea4c2acdebff5c5`, on `origin/main` `af7660c74` (2026-10-02).

## Mutation proof

The census is the check this PR adds, so the mutants run it. Production cost is zero lines of runtime change; the proof is that breaking the contract turns the census red:

- M1, delete the `horizon_hours` key from `Payload`: 2 strict errors.
- M2, rename the read `get("horizon_hours", ...)` in `sensor.py` to `get("horizon_hourz", ...)`: 2 strict errors.
- Unmutated head: 0 errors.

Command for each: `HPO_TYPING_PYTHON=$PWD/.venv/bin/python python3 tests/typing_ruler.py --mypy` reads the same invocation; the counts above are `mypy --strict --warn-unused-ignores --show-error-codes --python-version 3.14 custom_components/heatpump_optimizer | grep -c error:` with the pinned toolchain.

## Null control

Origin/main prints 0 errors under that command and has no `Payload` to delete a key from: its `DataUpdateCoordinator` is unparameterised, so `.data` is `Any` and a read with no producer type-checks. At this head the same deletion is 2 errors (M1 above). A larger control: deleting three keys (`horizon_hours`, `measured_cop`, `reading_ok`) moved the census 10 to 17 on the earlier, wider draft, with the 7 new errors in `binary_sensor.py`, `climate.py` and `sensor.py`.

## Figures

- Production lines added: 396 added, 28 deleted under `custom_components/` (`git diff --numstat origin/main HEAD -- custom_components`); `payload.py` is 365 of them. The cap is fixer.md's "about 400".
- Strict census at this head: 0 errors, mypy 2.3.1 with homeassistant-stubs 2026.9.3, Python 3.14.7 (`python3 tests/typing_ruler.py --print-requirements` names the pins).
- Census on the first wired draft, before the 10 errors were fixed: 10 errors (coordinator 3, sensor 5, entity 1, binary_sensor 1). Fixed here: the missing `sensor_advisor` key, return types of `_async_update_data`, `_async_first_refresh_light` and `_republish_handover_ages`, `_reload_handover`, three helper parameters typed `Payload`, and narrowing in `sensor.py` and `binary_sensor.py`.
- Keys: `Payload` carries every top-level key in the five `tests/golden/coord_*.json` fixtures, plus the conditional ones none publishes. The rule: parse `Payload` with `ast` and compare with the union of the goldens' `data` keys; the goldens' 163 are all present.
- Architecture score, instrument not in this tree: the prototype on branch handoff/audit-r9-alt (its b/arch_score.py with --delta, vectors from b/measure_vec.py over git archive exports of origin/main and this head, the red-team counters swapped in as score_proto.py does). It prints untyped_payload_keys 166 to 0 (the counter-hardened v2 reads 166 to 0 as well), delta-S +50.98, admissible, verdict IMPROVES, no metric rising; it lists three metrics as missing from the delta (coord_footprint_v1, a1_coord_writers_multi, import_cycle_modules_v1), which that prototype does not measure. The score is report-only, and R9-EG-A1 owns the in-tree copy. **Caveat:** 23 of the 173 Payload keys, and 6 nested fields, are typed dict[str, object]. The counter does not count those as untyped, because object inside a dict[...] is not a bare object; they are weakly typed. B3b below removes them.
- Seams the new class could open (fixer.md step 8): no coordinator method added, so `tests/seam_map.json` and the coordinator rows of `tests/structure_budgets.json` do not move. `python3 tests/structure.py` passes.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, reason: no recorded closure mentions `payload.py`. That is the UNDER-SCOPED the autofix job repairs (`ci-autofix.md`); I did not run `derive_closures.sh`.

Not run locally, on CI: `tests/entities.py` and every numeric script, which need scipy this seat lacks. Run locally: `tests/structure.py`, `tests/ha_contract.py` (4 of 4), the typing ruler and the census above.

## Red checks

none.

## Forward-carry

none: the destination is a roster group, R9-EG-B3b, which the orchestrator creates from the section below on handoff/audit-r9-fixplan, a branch this tree does not carry. Placeholders typed dict[str, object] are named there so the next stage cannot read this one as complete.

## Owed to R9-EG-B3b

B3b must do exactly this, and the issue closes with it:

1. Give each of these a fixed-shape TypedDict in place of `dict[str, object]`, field types read from the producer and confirmed with `reveal_type`: `heat_pump_signals`, `battery`, `wood_fuel` (including `night_advice`, which `sensor.py` reads and `build_wood_fuel_view` does not set at the top level), `accuracy`, `price_prior`, `external_heat`, `system_identification`, `defrost_buckets` items, `comfort_learning`, `heat_curve`, `contract_comparison`, `power_headroom`, `pv`, `dhw_advisor`, `schedule` and `dhw_schedule` items, and `space_plan` / `dhw_plan` with their forecast and slot items. `PeakTariff` is already typed here.
2. Confirm two shapes drafted from partial reads: the plan `slots` items (`_plan_slots`, `coordinator.py`) and `price_prior` (`PriceShapeModel.summary()` in `price_model.py`).
3. Decide, per key, which of these stay open-ended and say why in `payload.py`: `predictive_info`, `last_diagnosis`, `monthly_report`, `fuse_advisor`, `ecl110_last_payload`, `solar_diagnostics`, `sensor_advisor`, `FreqControl.map`, `SystemIdentification.result`, `Narrative.items`, `ManualPlan.released_space` and `released_dhw`. Each is built by a producer typed `dict[str, Any]` or through `_plain_types(...) -> Any`.
4. Remove `cast(Payload, data)` in `_build_data_dict`: give each view (`_thermal_view`, `_dhw_view`, `_learning_view`, `_measurement_view`, `_grid_view`, `_ecl110_view`, `_external_heat_view`, `_input_health_view`, `_mixing_valve_view`, `_plan_settings_view`, `_insight_view`, `_freq_view`, `_build_plan_views`, `_apply_result_payload`, `_apply_unsolved_payload`) a slice TypedDict return type, with `Payload` inheriting the slices, so mypy checks each producer against its slice. Many producer values are `Any` today (`result: Any`, `getattr(self, "_ctx", self)`), so this step needs those sources typed too, or each value read through a typed local.
5. Derive the hand-written payload shape `DATA` in `tests/entities.py` from `Payload` (issue #1737's third bullet), and make a read with no producer fail there.
6. Re-run `arch_score.py --delta` with the counters swapped in and report `untyped_payload_keys` where no key is `dict[str, object]`; per the issue, an `Any` or `object` typed key is not progress.

## Friction

none.
