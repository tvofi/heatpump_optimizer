Fix review: blocked bfaf5486a66f2f10a835b9d668d30999521a9364 root-cause-unanswered: fast (3.14) went red at the head (tests/boost_drift_replay.py: TypeError cannot pickle 'mappingproxy' object -- EntryConfig cannot be deep-copied), unanswered; also metric-gamed: structure max_class_loc fits only by joining two wrapped calls (re-wrapped: 8823 > 8819)

bus-nonce: f3bc35b1f1672a5695e15f27ce424a0e

Reviewer seat r9c-rev-2025, round 4. I reviewed the delta 0dfb63a8..bfaf5486 from a fresh detached worktree, /Users/timmalmstrom/hpo-seats/r9c-rev-2025-r4. The live head was re-read at posting and had not moved. The merge base with main is 2d8cab3f, and `git merge-tree --write-tree origin/main bfaf5486` exits 0.

## Blocking 1: fast (3.14) is red at this head, it is this PR's, and the body does not answer it

The check is `fast (3.14)`, job 113048537751 in this head's run. The gate prints `[22:31:39] FAILED python3 tests/boost_drift_replay.py (131s)`. The traceback is `replay()` line 381, `st = copy.deepcopy(shared)`, which ends in `TypeError: cannot pickle 'mappingproxy' object`.

Reproduced locally at the head:
- `copy.deepcopy(EntryConfig.from_mapping({...}))` raises TypeError.
- `pickle.dumps` raises TypeError.
- `copy.copy` is ok.

The cause is `EntryConfig.raw`, a `types.MappingProxyType`, which cannot be pickled. Main's newer boost_drift_replay (dca94a64/baa6c237: "solve the pre-boost prefix once", forking by deepcopy) deep-copies replay state that now holds an EntryConfig. Main's own tree has no EntryConfig, so this is the PR's red. It is a product property too: any deepcopy or pickle of a coordinator context now raises. I found no production deepcopy of the context. The what-if simulation deep-copies OptimizationConfig, not EntryConfig.

The fix is cheap: give EntryConfig `__deepcopy__`/`__reduce__`, or hold `raw` as a frozen dict-like that pickles. Pin it with a deepcopy/pickle round-trip check in entities.py.

`## Red checks` still lists only a390f589's jobs. It names `fast (3.14)` as job 112880876855 (the manual_plan stand-in). This head's `fast` red is not named.

## Blocking 2: max_class_loc is paid by line-joins, not code (fix-review.md step 14, metric-gamed)

The body and dispatch say "max_class_loc paid 8823→8819 in code". The conflict merge 236b8f18 joined `ctx._thermal_params.dhw_schedule_enabled = bool(params[CONF_DHW_SCHEDULE_ENABLED])` from 3 lines into 1. df9131ab, titled "collapse one call to hold max_class_loc under the merged budget", joined `await self._dhw_learner.async_set_cooling_rate(float(params[CONF_DHW_COOLING_RATE]))` from 3 lines into 1. Both statements are 3-line in main 8d7903e6 and in e0f0b6fb.

I planted the reverse with `plant_rewrap.py`, re-wrapping only those two statements and changing nothing else:
- `RESULT max_class_loc=8823`, `FAIL max_class_loc 8823 > 8819 (+4)`.
- That is also above the ledger-merged budget of 8821 (`LEDGER-MERGE: max_class_loc: 9104 + both deltas = 8821`).
- Head unplanted: 8819 <= 8819, PASSED.

So the 4-line "payment" is exactly the two joins. Nothing in the class improved. The honest options:
- a real payment that moves code out of HeatPumpOptimizerCoordinator, or
- a +2 raise over the merged 8821 with tvofi's approval (budget-raise-gate).

The movement 8821 -> 8820 -> 8819 recorded in 455da7ff/d81907ad rides on the same joins.

The 157-char `out = quiet_windows.configured_specs(...)` line is main's own text and not the branch's move. My first plant re-wrapped it too and read 8826. I discarded that figure; only the two-statement plant above is cited.

## The conflict resolutions (236b8f18, merging main 8d7903e6/#1987): neither side dropped

- **coordinator imports.** Main's side shows `CONF_TIBBER_TOKEN`, `CONF_SILENT_MODE_FRACTION`, `CONF_PRICE_ENTITY`, `CONF_PRICE_SOURCE` and `DEFAULT_PRICE_SOURCE` only as conflict context. They were present at e0f0b6fb, and the branch had removed them with their readers. Head use: 0 each. My scan reports `UNDEFINED {}`, `ATTR-NOT-A-FIELD 0` and `HOLDER-MAPPING-READS 0`.
- **configured_quiet_windows.** It takes main's `quiet_windows.configured_specs`, whose `str(config.get(K) or "")` is semantically the branch's `_spec` (`str(v) if v else ""`).
  - My driver after the live apply: `live_spec='09:00-09:30' live_off_steps=2 reloaded=0`, and the rebuilt coordinator gives the same.
  - Null: unchanged, `reloaded=0`.
  - quiet_windows.py and debugger.py are byte-identical to main 2d8cab3f.
- **diagnostics.** Main's `debugger` import and the branch's `CONF_COP_SCALE` are both kept.
- **Main's added lines survive.** Every line main 8d7903e6 added to coordinator.py (9), diagnostics.py (7), services.py (23) and store.py (25) is present at the head: `missing_at_head=0` each (`main_side_check`).
- **The branch's side vs round 3.** The changed-line delta across custom_components, harness, ledger, entities.py and features.py differs only by:
  - the configured_specs delegation,
  - the two joins above,
  - the debugger.py `_EC_RESIDUAL` disposition (an options-only flag EntryConfig does not declare; reasonable).
- **D6 claims / docs / deployment_shape.** 73 modules (debugger.py + entry_config.py), 27 HA importers, 91 package files.
- **closures.json.** Ledger-merged as sets. debug_collect's closure gains entry_config.py.

## CI at bfaf5486 (run of jobs 1130485xxxxx; `checkruns_head_at_post.tsv`)

- typing: success (113048537721).
- coverage: success.
- pr-contract: success x2.
- budget-raise-gate: one success, one cancelled twin.
- fast (3.14): **failure** (above). Every other script in the lane is ok, including features ALL 3845, entities ALL 2215, env_drift --all and structure.
- closures: in_progress at posting (113048634686). Not cited.
- mutation: failure. "56 not started for --budget-minutes", nothing measured. The dispatch says 46; CI's line says 56. Accepted as the R9-CI-1 condition the dispatch sets.
- delivery-status and nightly-status: not this PR's.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev4 (HEAD.txt, checkruns_head*.tsv, joblog_113048537751.txt (fast), joblog_113048538119.txt (mutation), remerge_236b8f18.diff, main_added_*.txt, branch_delta_r3_vs_r4.diff, scan_head.txt, quiet_reload.txt, entryconfig_copy.txt, structure_head.txt, structure_plant_rewrap2.txt, plant_rewrap.py (reviewer-built), structure_plant_rewrap.txt (the discarded three-statement plant), pr-body.md). Rounds 1-3: r9c-rev-2025-ev, -ev2, -ev3.
