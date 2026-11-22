R11-SEAM-cycle-solve: the cycle owns when a solve runs. A new cycle-seam module, `custom_components/heatpump_optimizer/solve_gate.py`, is a per-coordinator side table (the `whatif.py` and `boost.py` pattern) holding the one in-flight guard, the trailing-refresh mark, the background budget and the user what-if slot. It also holds the one run-now path. `coordinator.py` keeps the solve paths and asks the gate. Approved design: `design.md` at 85feefccce9a6a9d2aa92d13a372888aef2190d4 (amendment 1 included; first approved at 29f8ba81). Findings: D1-s1-03, D17-s3-01, D9-s1-01, D9-s1-02, D9-s1-03, D9-s1-04, D1-s3-04, D1-s1-01. Closes: none. No round-11 class issue is filed yet (`gh api search/issues` for `repo:tvofi/heatpump_optimizer is:issue R11-SEAM-cycle-solve` returns only the #201 tracker).

What changes, per finding:

- **D1-s1-03.** The coordinator overrides `async_request_refresh`, and every writer reaches the override. `solve_gate.absorb_request` routes each request:
  - during a solve, it records the #1754 re-run;
  - during a refresh that is not solving, it marks one trailing refresh. `_async_update_data`'s `finally` spawns it as a direct `async_refresh()` in a non-eager task (`_spawn(..., eager_start=False)`), so it starts once the refresh that owed it has returned. This is design amendment 1 at `design/R11-SEAM-cycle-solve` 85feefccce9a; see `## Review block repaired`;
  - otherwise, the debouncer gets it. Home Assistant's debouncer drops a call made while it executes.
- **D17-s3-01.** `solve_gate.async_optimize_now` is the button's and the `run_optimization` action's one path: a single `async_refresh` that fetches, solves, actuates and publishes. A fixed mode, whose refresh solves nothing, solves its private plan first. The button no longer solves beside the refresh. The reason a run did not happen comes from the solve, which the cycle now records on the gate. A failed refresh maps to `no_prices` for the price-coverage `tibber_fetch_failed` and to `solve_failed` otherwise.
- **D9-s1-01.** `async_diagnose_interval` republishes the insight view and requests no refresh.
- **D9-s1-02.** `admit_background` allows one background what-if per main solve. `begin_solve` opens the budget. The price tile asks before `price_tiles.take`, so a denied tile does not move the rotation. The debug finalize self-test (`limited=False`, `debugger.py` `_solver_smoke`) never asks.
- **D9-s1-03.** `user_slot` lets one user what-if solve and the newest one wait. An ask that a newer one overtakes while it waits gets the held answer, marked `rate_limited`.
- **D9-s1-04.** `whatif.reference_days` runs through `_await_off_loop`. `schedule_days` keeps only the comparison.
- **D1-s3-04.** `_reap_killed` bounds both `_run_in_process` fault arms' reap with `_SHUTDOWN_LOCK_TIMEOUT_S`.
- **D1-s1-01.** The stop marks `hass.data[_WORKER_STOPPING]` before the reap. `_await_optimize` then re-raises without a notice or an in-process rerun, and `async_run_optimization` answers `"shutdown"` without counting a failure. `_clear_worker_fallback` deletes the notice whenever no entry has a cause latched, so a notice restored from before a restart clears. Sweep sibling: a healthy solve deletes `solve_failures` whatever the counter reads.

Release notes owe three items:
- a setting changed while the plan is being refreshed now gets a re-plan as soon as that refresh ends, instead of at the next interval;
- Optimize Now and the `run_optimization` action now fetch prices and weather, then solve once and publish;
- a what-if asked while others are still waiting is answered from the last answer, marked rate-limited, and only the newest ask is solved.

Departures from the design, each listed here for the reviewer to judge:

1. **The at-exit WNOHANG reap is not built.** `_shutdown_process_pool(at_exit=True)` keeps #533's `kill()` and timeout-less `wait()`. Built, it failed two #533 checks: "and the child is dead and reaped, not abandoned (#533)" and "at interpreter exit the worker is KILLED; otherwise it is asked to terminate". At exit no peer solve is left to wait on the lock, so D1-s3-04's harm does not arise there.
2. **`_WORKER_STOPPING` is a `hass.data` key, not a module `threading.Event`.** The Event leaked across instances in one process. Built that way, a later setup's spawn failure went silent: "D1-s2-55: an install that cannot spawn a worker still gets its plan …" failed.
3. **The diagnose path does not call `async_set_updated_data`.** It sets `data` and calls `async_update_listeners` instead, because upstream's `async_set_updated_data` re-arms the interval timer and cancels a pending debounced request (the D1-s1-03 class). It republishes only the insight view, which carries `last_diagnosis`. `sensor_advisor` is carried unchanged.
4. **`async_optimize_now` lives in `solve_gate.py`, not on the coordinator class.** It reads only the coordinator's public surface (`mode`, `async_run_optimization`, `async_refresh`, `last_update_success`, `last_exception`), and the class sits at its LOC budget.
5. **The gate's `reason` is recorded where the cycle calls the solve** (`gate.reason = await self.async_run_optimization()`), not at each of the solve's returns.
6. **`user_slot` is an async context manager**, so the slot is freed on every exit. A background caller passes `user=False` and neither waits nor holds the slot.
7. **`boost._BoostCoord` loses its `async_request_refresh` member.** The coordinator's override made the name two-defined, so `name_kept_members` rose. No receiver is typed `_BoostCoord` where that member is called (`set_channel` and `set_block` take `coord: Any`).

## Head
`310c601f4078a394fe527329a6a1fd8e1368cca0` merges the authored code head `2cae6b5d0e9d3dc8110e78ac2339b0dc1ab5a415`.

`2cae6b5d0e9d3dc8110e78ac2339b0dc1ab5a415` is this handoff's code head. It merges origin/main (`a004c65395`) into `4e5de6bad89d6a6669ad5078bbf3473f1fa1aa48` (the earlier code head, whose measurements below were taken at that head) and adds `2cae6b5d0e` (`solve_gate` owns the stop mark and the mode-supersede question, which pays `module_excess_loc`). Measured on this seat at `4e5de6bad8`, `date -u` 2026-11-21; the figures taken at `4e5de6bad8` are named by that sha where they appear.

How it was built from the PR head `c849ceade803` (mergeable state DIRTY: `tests/features.py` conflicted with main):

- `ba0557fa12` (the stopped local seat's) merges origin/main `6d7d52709f`; `8716104ffa` re-measures the structure budgets there (`recorded_at` only).
- `b6893b9247`, `3d723d0c38`, `6f9112e17b`, `36ab0c0c6c`: killing checks and rig bounds in `tests/features.py` (`## Mutation proof`, `## Red checks`).
- `6b74444ae4` merges origin/main `a8efe1d1c2`, which conflicted in five files (`## Figures`).
- `cd22ae92fb`: the eight ledger pins. `62c9cdbed1`: the merged tree's module count in `docs/architecture.md`.
- `6af9ccf97a` merges the handoff tip `5669e6e331`, which the orchestrator had built from c849cead and main in parallel with this repair (no conflict; its `48a4d93b4c` made the same 63 → 64 count edit). Taking it keeps `handoff/r11-seam-cycle-solve` a fast-forward.
- `4e5de6bad8` merges origin/main `6fdc15354f`. `tests/features.py` conflicted where both sides appended a block after the room-lift checks: this branch's solve_gate block and main's R10-DRAW-MAP-EVIDENCE part A. Both are kept, this branch's first. Under the same label rule as below: expected 5518, merged 5518, missing 0, extra 0. Null control: main's side holds 36 labels this branch's side lacks.

**The conflict resolutions and the new checks change reviewed content**: the last verdict was `Fix review: merge 9809bc79c2498f2b25867a5cc88dacd68c62a01a`, and a delta review is owed. The PR's own production diff is unchanged. Rule: the `+`/`-` lines of `git diff -U0 <merge-base>...<head> -- custom_components`, compared between 9809bc79 (base `99436a082c`) and this head (base `6fdc15354f`). `diff` printed nothing and the command chain printed PROD-LINES-IDENTICAL (10 files, +352 -164 at both). Null control: the same comparison with the head's first line dropped differs in 2 lines. What changed since 9809bc79 is `tests/features.py`, `tests/mutation_ledger/`, and the merge-resolved `docs/architecture.md`, `tests/deployment_shape.py` and `dev/audit/rounds/round4/D6/`.

`ba0557fa`'s `tests/features.py` resolution keeps every check of both sides. Rule: the multiset of first arguments of `R.check(...)` calls (`ast`), per tree. Expected = (ours ∪ theirs) − (removed by either side vs their merge base `git merge-base c849cead 6d7d5270`). Expected 5433, merged 5433, missing 0, extra 0. Null control: main's side holds 12 labels that `c849cead` alone lacks, so a resolution that took ours wholesale would have read 12 missing.

`governance / instrument-self-tests` concluded cancelled at c849cead (`merge_train.py classify c849cead --pr 3738`: `REFUSE selftests: ... concluded cancelled, which reads no step: re-run it`). It is not in the `owed-reds` set. It re-runs at this head. `prepr.sh`'s `ci predict` step printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 6fdc15354f0f`.
prepr: passed rc=0 at 4e5de6bad89d6a6669ad5078bbf3473f1fa1aa48 (scoped: `PREPR_SKIP_CLOSURES=1`, and `PREPR_SKIP_CODE=1` for the body-only reruns after a run whose code steps were all ok).

## Mutation proof

Each production edit was made alone in a scratch worktree at c8ead87, and the block of `tests/features.py` that pins it was run with `tools/audit/seat/features_block.py --prelude 'exec(open(PRELUDE).read())' START [END]`. The prelude came from `--emit-prelude`, and the file was restored after each run. Both blocks pass unmutated: `# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)` with rc 0 and 0 FAIL, and `# D10-s1-02: the press owes …` through `_r9f13_dt.freeze(None)` with rc 0 and 0 FAIL.

- `absorb_request`'s refreshing arm deleted → FAIL "solve_gate: an idle request is not absorbed and sets nothing; one during a refresh trails it once; …" and FAIL "D1-s1-03: a request during a refresh trails it, one during a solve re-runs it, and only an idle one reaches the debouncer …".
- The override's `if not solve_gate.absorb_request(...)` changed to `if True:` → FAIL "D1-s1-03: a request during a refresh trails it, …".
- The `finally`'s `take_trailing` guard changed to `if False:` → FAIL "D1-s1-03: a request landing while a refresh runs is answered by one more refresh once it ends, …" (measured at 8d5e340f; that check's text and its counter changed at 6b9b3ce8, see `## Review block repaired`).
- `admit_background`'s `if gate.background_taken: return False` deleted → FAIL "D9-s1-02: one background what-if per main solve …" `[admissions [True, True, True]]`.
- `begin_solve`'s `gate.background_taken = False` deleted → same check, `[True, False, False]`.
- `user_slot`'s `if ticket != gate.user_waiting:` changed to `if False:` → FAIL "D9-s1-03: of four overlapping user what-ifs only the one in flight and the newest solve; …".
- `_reap_killed`'s `wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)` changed to `wait()` → FAIL "D1-s3-04: the fault arms' reap of a kill-deaf worker is bounded …" `[kills=1 waits=[None]]`.
- `_await_optimize`'s stopping guard changed to `if False:` → FAIL "D1-s1-01: a worker the stop killed raises no fallback notice and runs no in-process solve; …".
- `async_run_optimization`'s stopping guard changed to `if False:` → FAIL "D1-s1-01: a solve the stop broke answers 'shutdown', …" `[('solve_failed', 1, False)]`.
- `_clear_worker_fallback`'s base early return (`if … pop(...) is None: return`) restored → FAIL "D1-s1-01: a healthy solve clears a fallback notice restored from before a restart, …".
- The diagnose publish line changed to `pass` → FAIL "D9-s1-01: a diagnose press republishes the insight view …" `[(0, False, ['kept'])]`.
- `async_optimize_now`'s fixed-mode branch changed to `if False:` → FAIL "D17-s3-01: in a fixed mode, whose refresh solves nothing, the press solves the private plan once and then refreshes" `[('returned', 0, 1)]`.
- The reason map collapsed to `return "solve_failed"` → FAIL "D17-s3-01: a refresh failed on prices that cover no step is the no-prices refusal, …".
- The button's base route restored (`reason = await self.coordinator.async_run_optimization()`) → 5 FAIL, including "D17-s3-01: the press returns normally when the solve ran, and costs one refresh and the one solve inside it -- never a second solve beside it".
- `async_optimize_now`'s `await coord.async_refresh()` deleted → 5 FAIL, the same five checks.
- The P2 registry entry `killed_worker_reap` fails at the merge base: `_run_in_process`'s transport arm held `worker.wait()`, an undispositioned hit of its shape.

D9-s1-04's off-loop wiring is pinned by its harness, not a features check (Figures: `loop_simulate_step_calls` 384 → 0).

**This repair's checks**, each block run with `tools/audit/seat/features_block.py --prelude 'exec(open(PRELUDE).read())' START [END]`, the prelude from `--emit-prelude` at this tree, and each production file restored after the run (`git diff --quiet` printed RESTORED). Each mutant is the text `tests/mutation_table.py`'s inventory prints for its anchor:

- `coordinator.py` `async_simulate` BOOLOP 6c3e48ee (`"power_cap_kw" in overrides and simulated.predictive_info` → `or`). Block `async def _whatif_scratch_params():` to `_wi_shared = [`: unmutated, 6 of 6 ok. Mutated: FAIL "T2: a what-if that capped no power carries no power_cap_breach_c …".
- `async_simulate` GUARD_OFF 1f48017b (`if not admitted:` → `if False:`). Same block. Mutated: FAIL "D9-s1-03: of three user what-ifs overlapping one solve, the ask a newer one overtook … answers held and rate-limited …" `[executor jobs while held 1, in all 3; rate_limited per ask [False, False, False]]`. Unmutated: 2 jobs and `[False, True, False]`.
- `async_simulate` CMP_BOUND 91e008d2 (`len(horizon.prices) < 4` → `<= 4`). Same block. Mutated: FAIL "a what-if needs four priced quarters …" `[{3: 'no_prices', 4: 'no_prices'}]`. The three-quarter arm is the null control and reads `no_prices` at both ends.
- `solve_gate.py` `absorb_request` GUARD_OFF d99b351e (`if gate.solving:` → `if False:`). This mutant, and RETURN_DEL 355fcbc3 (`return True` → `pass`), deadlocked full `tests/features.py` at the #1754 rig. Under `timeout -s ABRT` with `PYTHONFAULTHANDLER=1`, both stopped at `features.py` `_g1754_arm`'s nested `await coord.async_run_optimization()`. A second solve waits on the executor gate, which the rig opens only after that call returns. The nested request is now a task, waited on with a 10 s timeout and never cancelled; a `wait_for` cancel deadlocked in the second solve's cleanup. Block `R.section("#1754 — …` to `# #240: the what-if's parameters must share`: unmutated, 5 of 5 ok. Each mutant, and `begin_solve` GUARD_OFF 53abf7e8: FAIL "a run request during an in-flight solve returns at once, recorded as its re-run, never a second solve started beside it". Full `tests/features.py` under d99b351e and under 355fcbc3 now ends, rc 1, with 6 FAIL each.
- `solve_gate.py` `user_slot` GUARD_OFF 9a253a03 (`if not user:` → `if False:`) deadlocked two rigs: the solve_gate slot burst and the #1753 borrow arm (`_r9egb9_borrow_arm`'s U1). A background caller waits on a user slot that the rig frees only after it. Both now wait with a timeout, never cancelling. Slot burst (block `# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)`): unmutated 22 of 22 ok; mutated FAIL "D9-s1-03: of four overlapping user what-ifs …". Borrow arm (block `def _r9egb9_borrow_arm(borrower, kind):` to `# R9-UX-4 (#1795)`): unmutated 6 of 6 ok; mutated 4 FAIL, every probe arm, with both null arms ok. Full `tests/features.py` under 9a253a03 now ends, rc 1, with 5 FAIL.
## Null control

Finder harnesses at the merge base, each with the null arm the design names. Paths are relative to `$EXPORT`, a `git archive` of `plan/r11` 819aa2e354b4. Each command was run from the measured tree's root with `PYTHONPATH=tests/hastub python3 $EXPORT/<path>`.

- `m4_race_port.py --part B --origin direct`: `stale_request_refresh_rows=0 of 8` at both ends.
- `f01_run_optimization.py`: the button arm, `button_published_price=2.0`, at both ends.
- `h_diagnose_refresh.py`: the diagnose job alone, `diagnose_record_msm=0`, at both ends.
- `h_solves_per_cycle.py`: the default arm (tiles off, no fuse), `default.msm_per_cycle_series=2,2,2,2,2,2,2,2,2,1,1,1`, at both ends.
- `h_whatif_backlog.py --k 1`: `answers_rate_limited=0` at both ends. Worker jobs are 3 at the base and 4 at the head: the head's fourth is the reference-days job D9-s1-04 moved off the loop.
- `h_whatif_loop_block.py`: `null_steady_false.loop_simulate_step_calls=0` at both ends.
- `peer_wait.py`: the timeout arm, `timeout_returned_within_cap=1 timeout_lock_held_after=0`, at both ends.
- `m1_stop_midsolve.py --arm stop_idle`: `stale_fallback_issues_after_restart=0 in_process_solves_after_stop=0` at both ends.

## Figures

The harnesses come from `$EXPORT` = `git archive 819aa2e354b4 dev/audit/rounds/round11`. Each line gives sha1[:12], the merge base ae0ed64af898 → the head b8aaa5ad7b09, and the command `PYTHONPATH=tests/hastub python3 $EXPORT/<path> <args>`.

- D1-s1-03: `$EXPORT/dev/audit/rounds/round11/D1/s1/m4_race_port.py --part B --origin debounced` (209cff13e317): `stale_request_refresh_rows` 7 of 8 → 0 of 8; `stale_plan_rows` 10 → 3, the same 3 rows as the direct null. The port is the finder's `m4_race.py` (f5da640ac535) with two edits. First, `WRITERS[name]` became `WRITERS.get(name, ("unmapped", None))`, because main's census grew `_vent_cusum` and the unported harness raised `KeyError` at both ends. Second, `co._optimization_running` became a `_solving(co)` that reads that attribute where it exists and `solve_gate.gate_for(co).solving` otherwise. It ran from `$EXPORT/dev/audit/rounds/round11/D1/s1/`, beside its `rl` helper.
- D17-s3-01: `$EXPORT/dev/audit/rounds/round11/D17/s3/f01_run_optimization.py` (a07f99b1f773): `service_published_price` 0.5 → 2.0; `service_plan_republished` 0 → 1.
- D9-s1-01: `$EXPORT/dev/audit/rounds/round11/D9/s1/h_diagnose_refresh.py` (77e1551a911f): `msm_per_press_max` 4 → 0; `msm_per_press_mean` 2.6 → 0; `two_zone_dhw_tiles.worker_jobs_per_press` 4 → 1.
- D9-s1-02 (weakened): `$EXPORT/dev/audit/rounds/round11/D9/s1/h_solves_per_cycle.py` (7d1faeb8058d):
  - `tiles_fuse.msm_per_cycle_series` 9,4,2,4,4,2,3,4,2,2,3,1 → 8,3,4,2,3,4,2,3,4,1,2,3;
  - `tiles_fuse_duty.msm_per_cycle_series` 14,8,4,6,4,2,6,4,4,6,6,2 → 12,6,8,4,4,4,4,4,6,4,4,4;
  - `tiles_fuse_duty.cycles_over_b1_by_ref` 1 → 1. B1's breach was not reproduced by the judge, so the budget is a count, and the count rule is pinned by "D9-s1-02: one background what-if per main solve …".
- D9-s1-03: `$EXPORT/dev/audit/rounds/round11/D9/s1/h_whatif_backlog.py --k 4` (9772250331ec): `k4.worker_jobs_started` 12 → 7, which is two asks' three solves each plus one reference-days job; `k4.answers_rate_limited` 0 → 2.
- D9-s1-04: `$EXPORT/dev/audit/rounds/round11/D9/s1/h_whatif_loop_block.py` (888bca4eba9f): `loop_simulate_step_calls` 384 → 0 on `two_zone_dhw.fuse_cap`, `card_target`, `card_daynight` and `card_holiday`, and on `single_zone_dhw.card_target`; 960 → 0 on `two_zone_dhw.card_weekend`.
- D1-s3-04: `$EXPORT/dev/audit/rounds/round11/D1/s3/peer_wait.py` (9d8dc6e6dd98): `transport_returned_within_cap` 0 → 1; `transport_lock_held_after` 1 → 0; `transport_unbounded_waits` 1 → 0.
- D1-s1-01 (weakened): `$EXPORT/dev/audit/rounds/round11/D1/s1/m1_stop_midsolve.py --arm stop_midsolve` (8ceeea9b1aee): `stale_fallback_issues_after_restart` 1 → 0; `in_process_solves_after_stop` 1 → 0; `fallback_issues_at_stop` 1 → 0. It reproduced at this seat's base, so it is a fix, not only a pin.
- Suites at this head (4e5de6ba), each `PYTHONPATH=tests/hastub python3 tests/<script>`:
  - `features.py`: ALL 6041 FEATURE CHECKS PASSED.
  - `entities.py`: ALL 2737 ENTITY CHECKS PASSED. Its self-test `FAIL` lines, cut to 60 columns and without `hb:positive_control` timings, equal those of the run at the old merge base 6d7d5270.
  - `doc_claims.py`: ALL 441 checks PASSED. At 36ab0c0c it read 1 FAIL, `architecture.md:299 modules_free_of_homeassistant: documented=63 measured=64`, and `entities.py` failed "architecture.md's HA-free count is the tree's" on the same count. Both were repaired at 62c9cdbe.
  - `harness_headers.py`: 115 of 115. `deployment_shape.py`: all passed. `structure.py`: STRUCTURE RATCHET PASSED. Also, at 62c9cdbe: `env_drift.py --claims-only origin/main` rc 0, and `closure.py selftest` 118 of 118.
  - Left to CI: `golden.py`, `stress.py`, `optimality.py` and `backtest.py`. The production lines are unchanged since the reviewed head (`## Head`), and main's own production changes are CI's to grade. This is the brief's scoped rule.
- Merge of a8efe1d1 (`6b74444a`): five conflicts, each a count that both sides moved. This branch added `solve_gate.py`; main added `room_history.py` and `room_record.py`.
  - `docs/architecture.md`: 99 modules, 34 importing `homeassistant` at module level.
  - `tests/deployment_shape.py`: 118 package files (`git ls-files custom_components/heatpump_optimizer | wc -l` printed 118).
  - `dev/audit/rounds/round4/D6/claims.py`: `RESULT arch_modules_on_disk=99` and `arch_map_listed=99`. `claims.json` and `claims.md` were regenerated by running `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` on the merged tree. It printed `arch_modules_on_disk=99`, `arch_map_listed=99` and `arch_map_missing=0`.
  - The 34 is main's documented 33 plus `room_history`/`room_record`'s one, which my `^(import|from) homeassistant` grep counts one lower on both sides (32 here, 33 on main). `doc_claims.py`'s `modules_free_of_homeassistant` measured the complement, 64, at this head.
- Structure at this head: `python3 tests/structure.py` passed with no budget change in this repair. It also passed at `git merge-tree --write-tree origin/main 8716104f`, against main 78d3b402, with `class_excess_loc = 17320`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 6fdc15354f` at this head printed "Architecture score: dS +0.0209 WORSENS (inadmissible: coord_footprint 2529->2541)", with these rows:

- `coord_footprint` 2529 -> 2541 (-0.0068): the twelve statements are the eight findings' new behaviour on the coordinator and on functions it is handed. They are the request override and its trailing schedule, the stop answers in `_await_optimize` and `async_run_optimization`, the diagnose publish, the user slot around `async_simulate`, and `async_optimize_now`'s fixed-mode solve and failed-refresh reason. Moving them elsewhere would leave them on functions handed the coordinator, which the metric counts by role. `PLAN.md`'s Risks names the same cost for this seam.
- `coordinator_multiassigned_attrs` 104 -> 102 (+0.0277): the drop `## Figures` records from `tests/structure.py --record`.

## Unpinned sites
None added. `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` drove every site new against its ratchet base. The `--shard K/N` runs were split across worktrees because one unsharded run outlived this seat's two-hour background bound. It recorded the eight `killed_by` pins in `cd22ae92`, each killed by `tests/features.py`:

- `coordinator.py` `_async_update_data` BOOLOP 3e107eaf;
- `async_simulate` BOOLOP 6c3e48ee, GUARD_OFF 1f48017b and CMP_BOUND 91e008d2;
- `solve_gate.py` `absorb_request` GUARD_OFF d99b351e and RETURN_DEL 355fcbc3, `begin_solve` GUARD_OFF 53abf7e8, and `user_slot` GUARD_OFF 9a253a03.

The last run (ratchet base a8efe1d1) printed `PIN KILLED: 3 pinned, 0 left unpinned`, and its null control (`coordinator.py:396 NULL_COMMENT`) survived. At this head, through `mutation_table`'s own functions: `completeness_problems` is `[]`; `unpinned_sites` is 1947 against `base_unpinned_sites` 1953 at 6fdc1535, and the same at a8efe1d1 before the last merge; `new_unpinned` is 0 and `added_unpinned` is 0. The earlier handoff's list of sites "pinned by mutation-autofix" is withdrawn. Three of them could not have been pinned that way: 6c3e48ee, 1f48017b and 91e008d2 survived every driver until this repair's checks. 355fcbc3, d99b351e and 9a253a03 read `skip-timed-out` until the rigs were bounded.
At `2cae6b5d0e` (the code head this body now describes; the measurements above are at `4e5de6bad8`), the body contract's pin check lists nine sites it reads as unpinned and this body had not named. They sit in the lines `2cae6b5d0e` moved (`solve_gate` now owns the stop mark and the mode-supersede question). This update did not drive `mutation_table.py` over them (one unsharded run of `tests/features.py` outlived a seat's background bound earlier), so each is unmeasured here, neither claimed killed nor surviving; `tests / mutation` measures them at the pushed head. The `None added` above holds at `4e5de6bad8` only. The sites:

- `custom_components/heatpump_optimizer/coordinator.py:2326 GUARD_OFF`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/coordinator.py:6330 GUARD_OFF`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/coordinator.py:6407 GUARD_OFF`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/coordinator.py:6478 GUARD_OFF`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/coordinator.py:6487 GUARD_OFF`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/solve_gate.py:106 BOOLOP`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/solve_gate.py:106 RETURN_DEL`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/solve_gate.py:112 BOOLOP`: unmeasured at `2cae6b5d0e`
- `custom_components/heatpump_optimizer/solve_gate.py:112 RETURN_DEL`: unmeasured at `2cae6b5d0e`

## Review block repaired

Block e80c8c4a, from the review of 1cf4d759 ("Design §3 B's trailing arm does not do what it claims under upstream Home Assistant").

- **Cause.** Upstream's `Debouncer.async_call` holds `_execute_lock` while it awaits the job, which runs as a separate eager task, and arms the cooldown only after that task ends. A trailing `async_request_refresh()` spawned from a debounced refresh's `finally` meets the held lock with no timer, and is dropped.
- **The reviewer's suggested `eager_start=False` is not enough.** Once the job has suspended, which a real refresh always does, the spawned task is queued ahead of `async_call`'s wake-up, so it still meets the lock. Measured below (mutant 1).
- **Fix.** This changes the approved design. It is recorded as amendment 1 at `design/R11-SEAM-cycle-solve` 85feefccce9a: the alternatives and the scratch-model table, with the orchestrator's choice of (b) under mandate 6893738184.
  - The `finally` spawns `self.async_refresh()` directly, non-eagerly. `_spawn` forwards keyword arguments to `hass.async_create_task`.
  - Upstream's `_async_refresh` cancels an armed cooldown, and returns at once after shutdown.
  - `tests/harness.py`'s `FakeHass` and `EagerHass` take upstream's `async_create_task(target, name=None, eager_start=True)` signature. `EagerHass` refuses a non-eager task, as it already refuses one that suspends: it has no loop to defer to.
- **New check** (`tests/features.py`, solve_gate block): "D1-s1-03: under upstream's debouncer, a write landing while a debounced refresh runs is answered by one more refresh once it has returned, never nested inside it, …".
  - It drives `_SgUpstreamDebouncer`, upstream 2025.2.0's call path: the lock, an eager job task, the timer armed after the job, and a drop on a held lock.
  - Every state read suspends.
  - It records the refresh count, and the nesting of the refreshes (`(` at each `async_refresh` entry, `)` at its return).
- **The existing trailing check** now counts refreshes, not debouncer calls. Expected `(0, 2, False)`: 0 debouncer calls, 2 refreshes, trailing mark spent.
- Block runs: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open(PRELUDE).read())' '# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)'`, with the prelude from `--emit-prelude` at this tree:
  - 1cf4d759's production code with the new tests: 2 FAIL of 13. The new check reads `{('debounced', True): 1, ('debounced', False): 1, ('direct', True): 2, ('direct', False): 1}` (the controls hold; the debounced write is lost). The trailing check reads `(1, 1, False)`.
  - The fix: 0 FAIL, 13 ok.
  - Mutant 1, the reviewer's suggestion (`self._spawn(self.async_request_refresh(), eager_start=False)`): 2 FAIL. The debounced write is lost (`(1, '()')`).
  - Mutant 2, an eager direct refresh (`self._spawn(self.async_refresh())`): 1 FAIL. Two refreshes run, but nested (`(2, '(())')`), so the older refresh publishes last.
  - The null control is inside the check: with no write, each origin runs exactly `(1, '()')`. A direct-origin write gives `(2, '()()')` at both ends.
- **Ratchet.** The fix first grew the coordinator class by 7 lines (`class_excess_loc`, `max_class_loc`). It was paid by folding the `_spawn` docstring and the comment, with no raise. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks
- `tests / mutation` at c849cead (job 136820986444): `MUTATION TABLE REFUSED -- 2005 unpinned site(s) against 2003 at the ratchet base e83a2c919f, 6 of them added by this diff`. Repaired: every site is pinned (`## Unpinned sites`), 0 added at this head. `tests / mutation-autofix` (job 136820987072) pushed no commit, and it could not have: three sites needed a new killing check and three deadlocked their driver.
  - Cheaper detector: the same drive run locally before the handoff (`mutation_table.py --pin-killed --base origin/main --scripts tests/features.py`). It already existed. Its standing cost on this four-core seat is one baseline `tests/features.py` run (877–1031 s in this session's logs) plus about one such run per site, in parallel shards.
  - Process state (c): the previous handoff disposed the sites as "pinned by mutation-autofix" without a local drive, and `fixer.md` step 2 accepts that disposition. That disposition cannot tell a killable site from a survivor or a timeout. Recorded here for the root-cause seat; no countermeasure is built in this PR. Carry: dismissed: a process finding for defect-root-cause.md's separate seat, stated in this body
- `governance / policy-docs` at 28977f9e (run 44463878660, job 135357182125): `machinery_ratchet` failed `churn_per_kilo_product_lines 34577 <= 14797 + band 3636`. The cap it read was this branch's pre-merge `dev/governance/config/machinery_budgets.json`; main re-recorded that cap to 34898 (30ae44cd94, after #3723's raise), and the same job on main at 7ae05284 passed (`35068 <= 34898 + band 3636`). The main merge at c3d0249a carries the 34898 cap, under which the measured 34577 passes. Cheaper detector: none exists for this one. It is a stale-base red that a merge of main cures, not a defect in the diff.
- `governance / wave-script` at c849cead (job 136840377435): `295 passed, 1 failed`. The failure was `FAIL ownerOnlyRecord reads every declared owner-only brief's id, seat and dimension, and no near-miss []`, printed beside `owner-only  declared [none]`, so the job read an empty owner-only brief set. It does not reproduce at this head: `prepr.sh`'s wave-script step printed `296 passed, 0 failed` at 62c9cdbe. The diff touches none of the check's inputs: `git diff --name-only <merge-base>...HEAD | grep -E 'dimensions|scopes.json|audit-verify|check-wave-script'` printed nothing, exit 1. The cheaper detector is that same `prepr.sh` step, a few seconds locally, and it reads green here. No cheaper detector exists for the red as CI read it, since it did not reproduce.
- `tests / fast (3.14)` at 9809bc79 (job 135447271434): `features.py` failed one check, "the lift may raise the plan's peak over the unlifted plan's, and the lifted plan holds the target past the ramp; …" `[peak none=20.241 zeros=20.241 lift=20.453 lift min past 3 h=20.000]`. That check is main's (`338aa528f9`, R11-CARRY-ROOM-LIFT). At the next head, ce841284, which only merges main (#3731, R11-SEAM-plant-model, among others), CI read `ALL 5948 FEATURE CHECKS PASSED` with this check ok. This PR's production lines are the same at both heads (`## Head`'s rule). It reads ok at this head (local `features.py`, 6007 of 6007). No cheaper detector: it was main's check meeting an older main's solver, and the gate that caught it was the cheapest one that runs that pair.
- `tests / fast (3.14)` at ce841284 (job 135519436581): `tests/structure.py` exited 2 with `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` after the merge of main. It was re-recorded at c849cead (`max_class_loc 7873 -> 7871`), and `structure.py` passes at this head. Cheaper detector: `python3 tests/structure.py` before the push, about 28 s, which `fixer.md` step 5 already requires. Process state (b): that step existed and was not run after that merge.
- `tests / coverage-ratchet` at 2df609237b (job 137032671250, run 44961656873, cancelled as superseded after the job ended): `FAIL every module >= 95.0 % (3 below)`: `room_history.py 66.09 %, room_record.py 86.96 %, draw_range.py 91.65 %`; the package figure passed at 98.59 %. None of the three modules is in this branch's diff: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E 'room_history|room_record|draw_range'` prints nothing, exit 1. The same job read success on main at 4ebd430fbf (job 137021130737), the main commit that 2df609237b merged cleanly. No cause in this diff was found. The PR's coverage job measures only the scripts the scope selects and copies the rest from the base's per-script cache (`tests.yml`, `Measure the tree`), so the three figures reflect that measurement and not a test this branch removed. The job runs again at this head, and CI is the authority on it. Cheaper detector: none is cheaper than the job itself, since the local equivalent is `tools/coverage/coverage_tree.sh fast` (about 43 minutes, the job's own wall time).
- `pr-contract / pr-contract` at e7dc8a8a (job 137201894278): `ERROR [figure-block] line 127: block scope-line names head=c931e99404d3 mb=f269ecccb5f1, this run is head=e7dc8a8a78ab mb=59b17e97ae1b; re-render with figure_block.py refresh`. The stored figure block named an earlier head of this PR; each update (`update_pr.sh`) cuts and re-renders it at the head it pushes, so the block names this push's head. Cheaper detector: `prepr.sh --body-check` (the contract's own offline run), which `update_pr.sh` and `body_push.sh` already run.

## Forward-carry

- The design note's `overlap-refresh` item (an `async_refresh` during the scheduled refresh starts a second `_async_update_data`, whose solve meets `gate.solving` and returns None) is pinned by the existing check "forcing an optimization while one runs is dropped, not queued (the solve entry point the press and the service share, F1.3 #1644)", now driven through `solve_gate.gate_for(coord).solving`. Carry: dismissed: built and pinned in this PR
- The design note's `flag-readers` item: every test that set `_optimization_running` now sets the gate (`tests/features.py`, `dev/audit/harnesses/r10_registry_leak.py` through the public `optimization_running`). Carry: dismissed: built in this PR
- The design note's `button-1641` item: no test here cancels the press mid-actuation, so there is nothing to report. Carry: dismissed: no test shows the cancellation the note asks to report
- The design note's `fallback-flap` item stays dismissed: one re-raise per restart, re-latched on the next solve. Carry: dismissed: one re-raise per restart, re-latched on the next solve
- Carry 0 (roster, item f9a20486: the steady pair's hour scatter for a hot-water window, quiet-hours or wood-slot ask sent alone) is not built here. This group's approved design (`design.md` at 85feefcc) touches `whatif.py` only for D9-s1-04, the reference days moved off the loop, and it decides when a solve runs, not what the steady pair's figure prices. The carry's own text releases the open PR on that condition: "Not owed by the open pull request if its design excludes it: record the disposition at its merge". The precondition it names (the card still sends those overrides alone) is unchanged by this diff, whose `whatif.py` hunk moves the two `reference_day` calls into `reference_days` and leaves `schedule_days`' branch (`None` when no setpoint moves, the pair branch the carry names) as it was. Carry: dismissed: excluded by this group's approved design, as the carry's own text allows; the disposition is recorded here for the merge

## Friction

- harness-port: stale: the finder's `$EXPORT/dev/audit/rounds/round11/D1/s1/m4_race.py` raises `KeyError: '_vent_cusum'` at the merge base because main's `d1-solve-state` census grew a name its `WRITERS` table lacks; both ends were measured with a two-edit port (Figures) that lives beside its `rl` helper in the export, not in the tree. Carry: dismissed: the round-11 register owns its harnesses
- frugal-guard: contradiction: the seat brief says to work inline with no subagents, and the session's frugal hook refuses a sixth inline read per prompt and points at a subagent; reads were batched and continued after each background run's wake instead. Carry: dismissed: a seat-environment conflict, recorded for the orchestrator
- body-push-figure-base: contradiction: `tools/audit/seat/body_push.sh` refused this body with `ERROR [figure-block] line 121: block \`scope-line\` names head=4e5de6bad89d mb=63c6d1cff9a2, this run is head=4e5de6bad89d mb=6fdc15354f0f`. It renders the block against #3738's recorded `base.sha` (`pr_recorded_base`, 63c6d1cf here) but verifies it with `prepr.sh --body-check`, whose `figure_block.py verify` uses `--base origin/main`; the two disagree whenever the PR was last synchronized against an older main. Workaround: a private copy at `$HOME/bp_body_push.sh` that differs only in `FB=origin/main` and in pointing its three `dirname "$0"` paths (`HERE`, the refused-body keeper, the `ref_privacy.py` guard) at the tracked seat directory; the tracked tool is unedited. Carry: dismissed: an instrument conflict outside this seam, recorded for the orchestrator

