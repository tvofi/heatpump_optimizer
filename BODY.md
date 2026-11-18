R11-SEAM-cycle-solve: the cycle owns when a solve runs. A new cycle-seam module, `custom_components/heatpump_optimizer/solve_gate.py`, is a per-coordinator side table (the `whatif.py` and `boost.py` pattern) holding the one in-flight guard, the trailing-refresh mark, the background budget and the user what-if slot. It also holds the one run-now path. `coordinator.py` keeps the solve paths and asks the gate. Approved design: `design.md` at 29f8ba81157134ab65ab38a45c4668b6c4834ef5. Findings: D1-s1-03, D17-s3-01, D9-s1-01, D9-s1-02, D9-s1-03, D9-s1-04, D1-s3-04, D1-s1-01. Closes: none. No round-11 class issue is filed yet (`gh api search/issues` for `repo:tvofi/heatpump_optimizer is:issue R11-SEAM-cycle-solve` returns only the #201 tracker).

What changes, per finding:

- **D1-s1-03.** The coordinator overrides `async_request_refresh`, and every writer reaches the override. `solve_gate.absorb_request` routes each request:
  - during a solve, it records the #1754 re-run;
  - during a refresh that is not solving, it marks one trailing refresh, which `_async_update_data`'s `finally` schedules through `_spawn`;
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

8d5e340f5ee79ac0c9bc15514c9de91818bc6a50, merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111, which is `origin/main`'s tip at 2026-11-18T16:33:14Z. The harnesses ran at b8aaa5ad7b09a26dfd77cc4d986a9749dfed52ea. The later commits touch no production file: `git diff --quiet b8aaa5ad7b09 8d5e340f5ee7 -- custom_components && echo PROD-IDENTICAL` printed PROD-IDENTICAL.

## Mutation proof

Each production edit was made alone in a scratch worktree at c8ead87, and the block of `tests/features.py` that pins it was run with `tools/audit/seat/features_block.py --prelude 'exec(open(PRELUDE).read())' START [END]`. The prelude came from `--emit-prelude`, and the file was restored after each run. Both blocks pass unmutated: `# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)` with rc 0 and 0 FAIL, and `# D10-s1-02: the press owes …` through `_r9f13_dt.freeze(None)` with rc 0 and 0 FAIL.

- `absorb_request`'s refreshing arm deleted → FAIL "solve_gate: an idle request is not absorbed and sets nothing; one during a refresh trails it once; …" and FAIL "D1-s1-03: a request during a refresh trails it, one during a solve re-runs it, and only an idle one reaches the debouncer …".
- The override's `if not solve_gate.absorb_request(...)` changed to `if True:` → FAIL "D1-s1-03: a request during a refresh trails it, …".
- The `finally`'s `take_trailing` guard changed to `if False:` → FAIL "D1-s1-03: a request landing while a refresh runs is answered by one more debounced refresh once it ends, …" `[(0, True)]`.
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
- Suites at the head:
  - `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL 5914 FEATURE CHECKS PASSED.
  - `tests/entities.py`: its FAIL lines equal the merge base's run line for line, apart from the `hb:positive_control` timing readings. The comparison was `diff` of the two runs' `^  FAIL` lines cut to 60 columns.
  - `tests/harness_headers.py`: only the committed-output check failed before the regenerated round-4 claims were committed.
- Gate scope: the block below, from the recorded closures; before they were recorded, `closure.py select --diff ae0ed64af898` read `MODE: FULL` (`solve_gate.py` was in no closure). Run locally of that scope: `features.py`, `entities.py`, `harness_headers.py`, `structure.py`, `worker_deadlines.py` and `debug_collect.py`; the rest is CI's (the brief's scoped-prepr rule). The closures were recorded by `tests/derive_closures.sh --single tests/config_flow_steps.py` and by `--scripts-from` over the 21 scripts whose closure read the coordinator, button, services or whatif module but not `solve_gate.py`, merged with `closure.py merge --partial`. After that, `python3 tools/pr/ci_predict.py` predicts no closures, fast, governance or instrument red.
- Structure: `python3 tests/structure.py --record`, against the base's budgets: `coordinator_attrs` 136 → 135, `coordinator_multiassigned_attrs` 104 → 102, `max_class_loc` 7875 → 7873, `class_excess_loc` 17382 → 17380. The reason is in the commit message.
<!-- figure-block: scope-line mb=ae0ed64af898d8923ac35afe6e9c031ac1e6b111 head=8d5e340f5ee79ac0c9bc15514c9de91818bc6a50 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

`python3 tools/audit/archscore/score.py --diff ae0ed64af898` printed "Architecture score: dS +0.0208 WORSENS (inadmissible: coord_footprint 2505->2517)":

- `coord_footprint` 2505 -> 2517: the twelve statements are the eight findings' new behaviour on the coordinator and on functions it is handed. They are the request override and its trailing schedule, the stop answers in `_await_optimize` and `async_run_optimization`, the diagnose publish, the user slot around `async_simulate`, and `async_optimize_now`'s fixed-mode solve and failed-refresh reason. Moving them elsewhere would leave them on functions handed the coordinator, which the metric counts by role. `PLAN.md`'s Risks names the same cost for this seam.

## Unpinned sites

Every site below is disposed as "pinned by mutation-autofix", and the named check kills it in this tree. The `coordinator.py` 112xx–113xx sites are `async_simulate`'s body, re-indented under the user slot. The ledger's twelve kill pins on their old keys were removed because their sites no longer generate.

- custom_components/heatpump_optimizer/coordinator.py:851 BOOLOP: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:851 RETURN_DEL: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:2346 GUARD_OFF: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:6171 BOOLOP: pinned by mutation-autofix ("D1-s1-03: a request landing while a refresh runs …")
- custom_components/heatpump_optimizer/coordinator.py:6171 GUARD_OFF: pinned by mutation-autofix ("D1-s1-03: a request landing while a refresh runs …")
- custom_components/heatpump_optimizer/coordinator.py:6176 GUARD_OFF: pinned by mutation-autofix ("D1-s1-03: a request during a refresh trails it …")
- custom_components/heatpump_optimizer/coordinator.py:6382 GUARD_OFF: pinned by mutation-autofix ("forcing an optimization while one runs is dropped, not queued …")
- custom_components/heatpump_optimizer/coordinator.py:6531 GUARD_OFF: pinned by mutation-autofix ("D1-s1-01: a solve the stop broke answers 'shutdown' …")
- custom_components/heatpump_optimizer/coordinator.py:6540 GUARD_OFF: pinned by mutation-autofix ("a service write during the production solve outlives the cycle (#1517)", whose re-run ends)
- custom_components/heatpump_optimizer/coordinator.py:10700 GUARD_OFF: pinned by mutation-autofix ("D9-s1-01: a diagnose press republishes …")
- custom_components/heatpump_optimizer/coordinator.py:11219 BOOLOP: pinned by mutation-autofix (the #1448 limiter checks)
- custom_components/heatpump_optimizer/coordinator.py:11219 GUARD_OFF: pinned by mutation-autofix (the #1448 limiter checks)
- custom_components/heatpump_optimizer/coordinator.py:11222 GUARD_OFF: pinned by mutation-autofix ("D9-s1-03: of four overlapping user what-ifs …" drives the gate; `h_whatif_backlog.py` the wiring)
- custom_components/heatpump_optimizer/coordinator.py:11227 GUARD_OFF: pinned by mutation-autofix ("simulate_plan with no plan raises a translated operational error")
- custom_components/heatpump_optimizer/coordinator.py:11238 BOOLOP: pinned by mutation-autofix (re-indented; the #1795 away-band checks)
- custom_components/heatpump_optimizer/coordinator.py:11239 GUARD_OFF: pinned by mutation-autofix (re-indented; the #1753 background-base checks)
- custom_components/heatpump_optimizer/coordinator.py:11253 GUARD_OFF: pinned by mutation-autofix (re-indented; "#1753: the tile solves through the user-limit-free path …")
- custom_components/heatpump_optimizer/coordinator.py:11260 RETURN_DEL: pinned by mutation-autofix (re-indented; the what-if failure checks)
- custom_components/heatpump_optimizer/coordinator.py:11271 BOOLOP: pinned by mutation-autofix (re-indented; "#2257: a schedule ask whose two day energies tie reads 0.0 on one solve …")
- custom_components/heatpump_optimizer/coordinator.py:11310 GUARD_OFF: pinned by mutation-autofix (re-indented; the S2 #1753 borrow arms)
- custom_components/heatpump_optimizer/solve_gate.py:67 RETURN_DEL: pinned by mutation-autofix ("the published optimization_running view reads the solve gate")
- custom_components/heatpump_optimizer/solve_gate.py:76 GUARD_OFF: pinned by mutation-autofix ("solve_gate: an idle request is not absorbed …")
- custom_components/heatpump_optimizer/solve_gate.py:78 RETURN_DEL: pinned by mutation-autofix ("solve_gate: an idle request is not absorbed …")
- custom_components/heatpump_optimizer/solve_gate.py:79 GUARD_OFF: pinned by mutation-autofix ("solve_gate: an idle request is not absorbed …")
- custom_components/heatpump_optimizer/solve_gate.py:81 RETURN_DEL: pinned by mutation-autofix ("solve_gate: an idle request is not absorbed …")
- custom_components/heatpump_optimizer/solve_gate.py:82 RETURN_DEL: pinned by mutation-autofix ("solve_gate: an idle request is not absorbed …")
- custom_components/heatpump_optimizer/solve_gate.py:90 GUARD_OFF: pinned by mutation-autofix ("solve_gate: … a second solve start is refused …")
- custom_components/heatpump_optimizer/solve_gate.py:94 RETURN_DEL: pinned by mutation-autofix ("solve_gate: … a second solve start is refused …")
- custom_components/heatpump_optimizer/solve_gate.py:101 RETURN_DEL: pinned by mutation-autofix ("solve_gate: … recorded as one re-run, taken once")
- custom_components/heatpump_optimizer/solve_gate.py:107 RETURN_DEL: pinned by mutation-autofix ("solve_gate: … one during a refresh trails it once …")
- custom_components/heatpump_optimizer/solve_gate.py:115 GUARD_OFF: pinned by mutation-autofix ("D9-s1-02: one background what-if per main solve …")
- custom_components/heatpump_optimizer/solve_gate.py:118 RETURN_DEL: pinned by mutation-autofix ("D9-s1-02: one background what-if per main solve …")
- custom_components/heatpump_optimizer/solve_gate.py:129 GUARD_OFF: pinned by mutation-autofix ("D9-s1-03: … a background caller never waits …")
- custom_components/heatpump_optimizer/solve_gate.py:138 GUARD_OFF: pinned by mutation-autofix ("D9-s1-03: of four overlapping user what-ifs …")
- custom_components/heatpump_optimizer/solve_gate.py:158 GUARD_OFF: pinned by mutation-autofix ("D17-s3-01: in a fixed mode, whose refresh solves nothing, …")
- custom_components/heatpump_optimizer/solve_gate.py:161 GUARD_OFF: pinned by mutation-autofix ("D17-s3-01: a refresh failed on prices that cover no step …")
- custom_components/heatpump_optimizer/solve_gate.py:164 RETURN_DEL: pinned by mutation-autofix ("D17-s3-01: a refresh failed on prices that cover no step …")
- custom_components/heatpump_optimizer/whatif.py:182 RETURN_DEL: pinned by mutation-autofix ("D9-s1-04: the reference days are one shippable function …")

## Red checks

- `mutation` at 8d5e340f5ee7: red by construction on the 38 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

- The design note's `overlap-refresh` item (an `async_refresh` during the scheduled refresh starts a second `_async_update_data`, whose solve meets `gate.solving` and returns None) is pinned by the existing check "forcing an optimization while one runs is dropped, not queued (the solve entry point the press and the service share, F1.3 #1644)", now driven through `solve_gate.gate_for(coord).solving`. Carry: dismissed: built and pinned in this PR
- The design note's `flag-readers` item: every test that set `_optimization_running` now sets the gate (`tests/features.py`, `dev/audit/harnesses/r10_registry_leak.py` through the public `optimization_running`). Carry: dismissed: built in this PR
- The design note's `button-1641` item: no test here cancels the press mid-actuation, so there is nothing to report. Carry: dismissed: no test shows the cancellation the note asks to report
- The design note's `fallback-flap` item stays dismissed: one re-raise per restart, re-latched on the next solve. Carry: dismissed: one re-raise per restart, re-latched on the next solve

## Friction

- harness-port: stale: the finder's `$EXPORT/dev/audit/rounds/round11/D1/s1/m4_race.py` raises `KeyError: '_vent_cusum'` at the merge base because main's `d1-solve-state` census grew a name its `WRITERS` table lacks; both ends were measured with a two-edit port (Figures) that lives beside its `rl` helper in the export, not in the tree. Carry: dismissed: the round-11 register owns its harnesses
- frugal-guard: contradiction: the seat brief says to work inline with no subagents, and the session's frugal hook refuses a sixth inline read per prompt and points at a subagent; reads were batched and continued after each background run's wake instead. Carry: dismissed: a seat-environment conflict, recorded for the orchestrator
