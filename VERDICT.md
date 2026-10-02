Fix review: blocked 2261e2a468eeae11c2e0b81532e87322ca620f90 contract: Payload declares two keys no producer sets (Insight.wear_price_per_start, top-level valve_target_schedule) and omits published keys (compressor_starts.wear_price_per_start, dhw_disinfection_switch); the cast hides all four

bus-nonce: 862c26e3a6baa3d31136240e6543bda9

Round 1. PR #1852 (R9-EG-B3a, Part of #1737). Measured head `2261e2a468eeae11c2e0b81532e87322ca620f90` (code `8eba0f4989d211e3111e6966bea4c2acdebff5c5`); base `af7660c74`. The live head was re-read when this verdict was posted and had not moved. Evidence: `evidence/` (the file `HEAD-2261e2a468eeae11c2e0b81532e87322ca620f90.txt` names the head). The review ran from a detached worktree. `fix-review.md` at origin/main has no diff against the merge base.

## Blocking findings (wrong types, not loose ones)

Every one passes the census, because `_build_data_dict` returns `cast(Payload, data)`.

1. **`Insight.wear_price_per_start` is in the wrong class.** The producer `_insight_view` (coordinator.py:10594-10600) writes it inside `compressor_starts` (`{"lifetime", "month", "wear_price_per_start"}`). `CompressorStarts` declares only `lifetime` and `month`, and `Insight` declares `wear_price_per_start` at its own level, where nothing writes it. All 5 goldens publish `insight.compressor_starts.wear_price_per_start`.
2. **Top-level `valve_target_schedule` is declared, but no producer sets it.** `_build_plan_views` writes it only as `space_plan["valve_target_schedule"]` (coordinator.py:3834-3836). The prototype counter, run on a version of the head it can trace, also lists it as declared but not produced.
3. **`dhw_disinfection_switch` is published and missing from `Payload`.** `_dhw_view` spreads `**self._legionella.disinfect.view()` (coordinator.py, `_dhw_view`), and `DisinfectionSwitch.view()` (disinfection.py:264) returns `{"dhw_disinfection_switch": {...}}` whenever a switch is configured. The body says `Payload` carries "every key `_build_data_dict` and `_with_sensor_advisor` can publish", so the body is wrong here. Two instruments miss this key: no golden configures a switch, and the prototype counter does not follow a spread across objects.

The probe (`evidence/_review_probe.py`, added to a copy of the head tree, census `evidence/probe_census.out`, 3 errors) shows how this behaves:
- `data["dhw_disinfection_switch"]` (published) gives `typeddict-item` error.
- `data["insight"]["compressor_starts"]["wear_price_per_start"]` (published) gives `typeddict-item` error.
- `data["insight"]["wear_price_per_start"]` and `data["valve_target_schedule"]` (never published) give **no error**.

So the contract rejects reads that are correct and accepts reads that are wrong. That is the reverse of the PR's stated purpose.

Fix: move `wear_price_per_start` into `CompressorStarts`, delete the top-level `valve_target_schedule` (it belongs to `space_plan`, which is B3b's), and add `dhw_disinfection_switch: dict[str, object]` (or a TypedDict). This is about 4 lines. Then state the enumeration rule in the body. A union of goldens plus a reading of producers missed a `**view()` spread. Grepping every `**self.<x>.<y>()` / `data.update(<call>)` in the views is a rule that would have found it.

## Claim findings (owed with the fix; not separately blocking)

4. **untyped_payload_keys 166→0 is a vacuous figure at this head.** I re-ran the prototype's v1 counter (`handoff/audit-r9-alt:handoff/round9/state/alt/archscore/a3/metrics/untyped_payload_keys.py`). This is my run of the finder's instrument, not the fixer's script.
   - `RESULT af7660c74 untyped=166 produced=166`
   - `RESULT 2261e2a46 untyped=0 produced=3`, with 130+ surface keys now "read_but_not_produced". The counter stops tracing at `return cast(Payload, data)`, so it reaches 0 because it lost the producer, not because it found typed keys.
   - `RESULT head-with-cast-removed untyped=0 produced=166`. On a traceable variant the 0 does hold under the counter's rule. But the counter shares finding 3's blind spot and counts `dict[str, object]` as typed.
   
   Stated plainly: 23 of the 173 top-level keys (plus 6 nested fields) are `dict[str, object]`. Under the issue's own rule ("an `Any` or `object` typed key is not progress", quoted in the body's item 6), 166→0 overstates the result. Under that rule, about 23 top-level keys are still not progress. The body discloses the 23 keys but quotes the figure without the produced=3 artefact. I did not re-derive delta-S +50.98 (I did not run the full `arch_score.py --delta`), so it is not verified.
5. **"A read of a key no producer sets is now a strict-census error" holds only for subscript reads or a typed use of the `.get()` result.** `data.get("horizon_hourz")` with an unused or `object`-accepting sink type-checks (probe line 28). M1 and M2 go red through `float(object)` (`arg-type`), not through a missing key.

## Re-run (mine)

- Census, pinned toolchain (`typing_ruler.py --print-requirements`: mypy 2.3.1, homeassistant-stubs 2026.9.3, Python 3.14.7, venv under the seat root): `RESULT head errors=0`, `RESULT base errors=0`. `typing_ruler.py --mypy` at head: ALL 9 checks PASSED.
- Mutants: `RESULT M1 (delete Payload.horizon_hours) errors=2`, `RESULT M2 (get("horizon_hourz") in sensor.py) errors=2`. Both reproduce the body's figures.
- Null control: `RESULT N2 (M2 rename at base af7660c74) errors=0`. Reproduced.
- Goldens against Payload (my instrument, `evidence/golden_vs_payload.py`, a runtime walk of `Payload` type hints over `tests/golden/coord_*.json` `data`): `RESULT golden_keys_missing_from_Payload 0`, `RESULT type_mismatch_paths 1` (finding 1). The 22 keys that are None in every golden are all declared Optional. All 5 goldens are `optimization_status: not_run`, so the solved-path shapes (`schedule`, `space_plan`, `dhw_plan`, `predictive_info`, `CurrentAction` from the solver) appear in no golden. I checked them by reading producers: the `CurrentAction` keys match `optimizer.get_current_action` / `_idle_action`, and `valve_target_schedule` is the error above.
- hastub `Generic[_DataT]`: the MRO gains `typing.Generic` only, there is no `__slots__`, and `__init__` is unchanged. The test MRO walks (`finite_boundary.py:413`, `entities.py:4892/10056/10695`) filter on module or `__dict__` membership, so they are unaffected. `ha_contract.py` at head under the stub: ALL 4 PASSED. I found no runtime behaviour change. The CI suite (Tests) is the full proof.
- Behavioural edits elsewhere: `_plan_outdoor_now` now treats a truthy non-list `forecast` as empty (previously iterated). `_advice` now ignores a non-dict truthy `night_advice`. `_data()` returns `Payload()` (that is, `{}`). The producers only emit lists and dicts there, so I see no observable change.
- `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden/`: untouched (three-dot). `git merge-tree --write-tree origin/main HEAD`: rc 0.
- Head CI (check-runs API, `evidence/check_runs_at_verdict.tsv`): no red. Two `cancelled` superseded duplicates of `budget-raise-gate` and `pr-contract` each have a `success` beside them. **Tests is still `pending`** and CodeQL python is in progress, so the suite, typing and mutation lanes are not yet reported for this head. No red check, so there is no root-cause trigger to answer.
- Forward-carry: the B3b destination is a roster group the orchestrator creates. B3b item 1 must also cover the shape of `space_plan.valve_target_schedule`.

Not run locally: entities.py and the numeric scripts (no scipy), full arch_score delta.
