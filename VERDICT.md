Fix review: blocked 29b763d7c2eb23a7f01f5cf10531caeeb866f7ca root-cause-unanswered: fast (3.14), mutation, closures went red on this PR's own diff (payload.py unclassified and missing from architecture.md, coverage and harness headers; stale entity._data mutation pin), unanswered

bus-nonce: f480ca19a80d54ed0f1234660c8e26f6

Round 2. PR #1852 (R9-EG-B3a, Part of #1737). Measured head `29b763d7c2eb23a7f01f5cf10531caeeb866f7ca` (code `684b5a1e354c875d380ec693f8ac58eb574b787a`). The live head was re-read when this verdict was posted and had not moved. The evidence directory names the head (`HEAD-29b763d7c2eb23a7f01f5cf10531caeeb866f7ca.txt`). CI job logs are in `evidence/ci/`.

The round-1 contract findings are fixed and the new check holds. The block is CI: Tests ran for the first time on this PR at this head (round 1's run never left `pending`), and four checks are red. Every red traces to this PR's diff. The body still says "## Red checks: none".

## Red checks at this head (check-runs API, `evidence/check_runs_r2.tsv`)

1. **`fast (3.14)`: 2 test scripts failed.**
   - `tests/entities.py`: 7 of 2063 checks failed. All 7 come from adding `payload.py`, and EG-B3 is not among them:
     - "every tracked file is either measured or deliberately classified": `payload.py` forces FULL. CLAUDE.md requires a new tracked file to go into a closure or onto `tests/closure.py`'s INERT list.
     - "and still covers every python file of the integration": `payload.py` is missing.
     - "the deployment-shape lane's closure is the whole tracked package": covers 68 modules is False.
     - Four `docs/architecture.md` checks: the opening counts (67/25 against 68/25), the module map (`payload.py` missing), the HA boundary (documented of 67), and the HA-free count (41 against 42).
   - `tests/harness_headers.py`: 6 of 94 checks failed.
     - `tools/audit/round4/D6/claims.py`: four headers moved for the same `architecture.md` reason (arch_modules_on_disk 67→68, arch_map_missing 0→1, claims_true 123→121, claims_false 0→2).
     - `tools/audit/round4/D10/qs_rules.py`: `declared_mismatch` went 0→1. I reproduced this locally: 1 at the head, 0 at base `af7660c74`. The `common-modules` rule looks for the substring `class HeatPumpOptimizerEntity(CoordinatorEntity)`, and the PR changed that line to `CoordinatorEntity["HeatPumpOptimizerCoordinator"]`. That is a false todo in the harness, caused by this diff. Either update the harness pattern or rewrite the base so it still matches, and say which in the body.
     - The committed output of `D6/claims.{json,md}` is not byte-identical.
2. **`mutation`: `MUTATION TABLE REFUSED`.** The ledger has a stale pin: `entity.py:HeatPumpOptimizerEntity._data RETURN_DEL 35920c59`, whose old pin is `return data`, and the PR rewrote that line. `mutation-autofix` repairs only unpinned sites, so the fixer owes the ledger re-key.
3. **`closures` (UNDER-SCOPED, 15 scripts now read `payload.py`) and `closures-autofix`:** "skip-failed-recording -- THE REPAIR DID NOT HAPPEN", because a script failed while it was being recorded. Per `ci-autofix.md`, this repairs itself once items 1 and 2 are green, so the body only has to name it.

Under `defect-root-cause.md`'s red-check trigger, the body must name each red check and answer it: the cheaper detector that existed, or the finding that none existed. Every red above would have shown locally in `tests/entities.py`, `tests/harness_headers.py` and `tests/mutation_table.py`. The body says entities.py was "not run locally (scipy)". The `mac-local-test-container` route exists for exactly that case.

## Contract re-review (passes)

- Probe (`evidence/probe_census_r2.out`, 3 errors) flips as it should. The published `compressor_starts.wear_price_per_start` and `dhw_disinfection_switch` now type-check. The never-published `Insight.wear_price_per_start` and `valve_target_schedule` now fail with `typeddict-item`. The remaining error is the deliberate typed-sink `.get` line.
- `DisinfectionSwitch` types match `disinfection.py` (`_readings: dict[str, tuple[bool | None, str | None]]`, so `state: bool | None`).
- Census: `RESULT errors=0` at the head. CI `typing`: success. M1 and M2 give `RESULT errors=2` each, and M1 also turns EG-B3 red (`egb3_fails 1`).
- Goldens against Payload (my instrument): `type_mismatch_paths 0`, `golden_keys_missing_from_Payload 0`.
- EG-B3 check, extracted and run standalone at the head: `RESULT egb3_fails 0 published 173 declared 173 unresolved []`. In CI it printed ok on all 3 lines. Null control with round 1's `payload.py`: `egb3_fails 2`, naming exactly the four keys.
- The body narrows both round-1 claims accurately (the 166→0 overstatement with produced=3, the 23 `dict[str, object]` keys, and the `.get` caveat). Delta-S is stated as not re-derived.

## The new enumeration check, attacked (non-blocking; owed to R9-EG-B3b, per the orchestrator)

I added a new key to the producers in 8 ways (`evidence/egb3_mutants_r2.out`):
- **Caught:** a `data["k"] =` store, a new `update(call)` spread (unresolved), and a non-literal view return. The last is caught only indirectly, and the `dict(kw=...)` call's own key is never seen.
- **Missed:** `data.setdefault("k", ...)`, `data |= {...}`, `data.update(k=...)`, and `data[NAME_CONST] =`.
- **Not seen by the check:** a store on `handover` in `_republish_handover_ages`. The census should catch that one, because `handover` is typed `Payload`, but I did not run the census on that mutant.

A scan of the current producers (`evidence/egb3_pattern_scan_r2.out`) finds none of the missed patterns in use, so the check is complete for this tree. Inside the cast, mypy does not see these patterns either. Removing the cast in B3b closes them.

## Other

- `structure.py`: STRUCTURE RATCHET PASSED.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/`: untouched (three-dot).
- `git merge-tree --write-tree origin/main HEAD`: rc 0.
- I ran the hastub check in round 1 and found no change. CI's `fast` ran every other script green, including FINITE BOUNDARY, DEPLOYMENT SHAPE and FEATURE.
