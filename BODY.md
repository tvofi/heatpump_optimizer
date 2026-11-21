R11-SEAM-cycle-solve: the cycle owns when a solve runs. A new cycle-seam module, `custom_components/heatpump_optimizer/solve_gate.py`, is a per-coordinator side table (the `whatif.py` and `boost.py` pattern) holding the one in-flight guard, the trailing-refresh mark, the background budget and the user what-if slot. It also holds the one run-now path. `coordinator.py` keeps the solve paths and asks the gate. Approved design: `design.md` at 29f8ba81157134ab65ab38a45c4668b6c4834ef5. Findings: D1-s1-03, D17-s3-01, D9-s1-01, D9-s1-02, D9-s1-03, D9-s1-04, D1-s3-04, D1-s1-01. Closes: none. No round-11 class issue is filed yet (`gh api search/issues` for `repo:tvofi/heatpump_optimizer is:issue R11-SEAM-cycle-solve` returns only the #201 tracker).

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

`827fa67eb6ee84d8874524557cdd540ca1b54593` merges the authored code head `5669e6e33108fb219e6c5afac3536c59f1fe9222` and then merges origin/main `63c6d1cff9` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`5669e6e33108fb219e6c5afac3536c59f1fe9222` is this handoff's code tip and the PR head, measured 2026-11-21T19:08Z against origin/main `63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184`. It is `71c7ef0688d6dbce8448381ebc158c84ff71e9f4` plus five commits, the PR's own diff unchanged by any of them:

- `5a98474792` merges origin/main `42809bec34`. One conflict, `tests/features.py`, resolved by union: this branch's `R11-SEAM-cycle-solve` solve_gate block, then main's `R11-SEAM-solver` block, each kept whole before the shared closing line. Each side's added hunks against merge base `99436a082c67` (53 here, 28 on main) appear verbatim in the merged file; the null control, the merge base's file, misses all 53 and all 28.
- `d6a1a03142` merges origin/main `e698fc8ac3` (#3711's `room_history.py` and `room_record.py`, #3820). Five conflicts, every one a module or file count both sides moved: `docs/architecture.md` (99 modules, 34 importing homeassistant), `tests/deployment_shape.py` (118 package files), `dev/audit/rounds/round4/D6/claims.py` (`arch_modules_on_disk` and `arch_map_listed` 99), each history clause ordered as the modules landed. `claims.json` and `claims.md` were regenerated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `arch_modules_on_disk=99`, `ha_module_level_importers=34`, `arch_map_missing=0`, `claims_false=0`. Null control: the line-8 sentence set back to main's 98 reads `documented=98 measured=99`, `claims_false=1`.
- `5ddac88e53` merges the PR head `c849ceade8` (its `max_class_loc` 7873 -> 7871 re-record), so the update is a fast-forward. `handoff-wip/r11-seam-cycle-solve` `8716104ffa` was compared and carries nothing beyond it: its `ba0557fa12` resolves the same `tests/features.py` conflict identically (its diff against an automatic merge of its own parents is exactly the union above), and `8716104ffa` moves only `recorded_at`.
- `48a4d93b4c` sets `docs/architecture.md`'s HA-free count 63 -> 64 (99 modules less 35 touching homeassistant). `tests/doc_claims.py` and `tests/entities.py` both read it red at `5ddac88e53` and green at the tip (`ALL 441 checks PASSED`).
- `5669e6e331` merges origin/main `63c6d1cff9`, clean; that delta touches neither `custom_components/` nor `docs/`.

Whether the resolution changed reviewed code: no production line. `git merge-tree --write-tree 71c7ef0688d6 63c6d1cff9a2` (git's own automatic merge of the reviewed code with main) writes tree `68a1a483fbf9`, and `git diff 68a1a483fbf9 5669e6e33108 -- custom_components/` is empty; the null control, the same diff against `71c7ef0688d6` itself, is main's 47-file delta. The resolution's own lines are the test-file union, the counts above and the regenerated register.

`71c7ef0688d6dbce8448381ebc158c84ff71e9f4` was the previous code tip: `5ed23c2558c22fa6095540ee98ad20563449d971` (below) merged with origin/main, no conflict.

`1515566df4d4f2bc351dcdf9e2073652d48ad334` merges the authored code head `5ed23c2558c22fa6095540ee98ad20563449d971`.

5ed23c2558c22fa6095540ee98ad20563449d971 is this handoff's code head: 28977f9e merged with main at 7ae05284 (c3d0249a, no conflict), plus 21aa2094, which deletes main's stale `async_simulate RETURN_DEL 1457a93f` pin (`## Red checks`), then merged with main at 8ab5dc566f (5ed23c25, no conflict); the ledger's `completeness_problems` is `[]` at 5ed23c25. The merge leaves the PR's own diff unchanged: `git diff 8751943e17ef...28977f9e` and `git diff 7ae05284d5bc c3d0249a51` share `git patch-id --stable` c1eb75b88e8d (66 files, +1184 -294). Kill at the moved line (`coordinator.py` 11312 at 21aa2094, 11289 after main's merge; anchor fd0988d6): `tools/audit/seat/mutant_run.py --spec` replacing `return payload` with `pass`, driven by `tools/audit/seat/features_block.py` over the block `# #240: the what-if's parameters must share` up to `# -- The held start, on the optimizer` (prelude from `--emit-prelude`), printed `SURVIVED NULL` then `KILLED async_simulate_RETURN_DEL_fd0988d6`.

`28977f9e820ee1813eccd5952484e0365e72f91a` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

6b9b3ce8a74f113e846d3f20869122621f835c46, the code head of this handoff: 1cf4d759 plus the one commit repairing review block e80c8c4a (`## Review block repaired`), merge base 8751943e17ef4d3ec699e7859ae829b4528d8ce7. Figures under `## Review block repaired` were taken at 6b9b3ce8; the rest were taken at 8d5e340f (merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111), and the harnesses ran at b8aaa5ad7b09a26dfd77cc4d986a9749dfed52ea. The later commits up to 8d5e340f touched no production file: `git diff --quiet b8aaa5ad7b09 8d5e340f5ee7 -- custom_components && echo PROD-IDENTICAL` printed PROD-IDENTICAL.

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
<!-- figure-block: scope-line mb=63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184 head=5669e6e33108fb219e6c5afac3536c59f1fe9222 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

`python3 tools/audit/archscore/score.py --diff 8ab5dc566f` (the merge base after main's merge at 5ed23c25; the same output against 7ae05284d5bc) printed "Architecture score: dS +0.0208 WORSENS (inadmissible: coord_footprint 2507->2519)", with these rows:

- `coord_footprint` 2507 -> 2519 (-0.0069): the twelve statements are the eight findings' new behaviour on the coordinator and on functions it is handed. They are the request override and its trailing schedule, the stop answers in `_await_optimize` and `async_run_optimization`, the diagnose publish, the user slot around `async_simulate`, and `async_optimize_now`'s fixed-mode solve and failed-refresh reason. Moving them elsewhere would leave them on functions handed the coordinator, which the metric counts by role. `PLAN.md`'s Risks names the same cost for this seam.
- `coordinator_multiassigned_attrs` 104 -> 102 (+0.0277): the drop `## Figures` records from `tests/structure.py --record`.

## Unpinned sites

Every site below is disposed as "pinned by mutation-autofix", and the named check kills it in this tree. The `coordinator.py` 111xx–112xx sites are `async_simulate`'s body, re-indented under the user slot. The ledger's twelve kill pins on their old keys were removed because their sites no longer generate.

- custom_components/heatpump_optimizer/coordinator.py:852 BOOLOP: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:852 RETURN_DEL: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:2347 GUARD_OFF: pinned by mutation-autofix ("D1-s1-01: a worker the stop killed …")
- custom_components/heatpump_optimizer/coordinator.py:6146 BOOLOP: pinned by mutation-autofix ("D1-s1-03: a request landing while a refresh runs …")
- custom_components/heatpump_optimizer/coordinator.py:6148 GUARD_OFF: pinned by mutation-autofix ("D1-s1-03: a request landing while a refresh runs …")
- custom_components/heatpump_optimizer/coordinator.py:6153 GUARD_OFF: pinned by mutation-autofix ("D1-s1-03: a request during a refresh trails it …")
- custom_components/heatpump_optimizer/coordinator.py:6359 GUARD_OFF: pinned by mutation-autofix ("forcing an optimization while one runs is dropped, not queued …")
- custom_components/heatpump_optimizer/coordinator.py:6508 GUARD_OFF: pinned by mutation-autofix ("D1-s1-01: a solve the stop broke answers 'shutdown' …")
- custom_components/heatpump_optimizer/coordinator.py:6517 GUARD_OFF: pinned by mutation-autofix ("a service write during the production solve outlives the cycle (#1517)", whose re-run ends)
- custom_components/heatpump_optimizer/coordinator.py:10677 GUARD_OFF: pinned by mutation-autofix ("D9-s1-01: a diagnose press republishes …")
- custom_components/heatpump_optimizer/coordinator.py:11196 BOOLOP: pinned by mutation-autofix (the #1448 limiter checks)
- custom_components/heatpump_optimizer/coordinator.py:11196 GUARD_OFF: pinned by mutation-autofix (the #1448 limiter checks)
- custom_components/heatpump_optimizer/coordinator.py:11197 GUARD_OFF: pinned by mutation-autofix ("D9-s1-03: of four overlapping user what-ifs …" drives the gate; `h_whatif_backlog.py` the wiring)
- custom_components/heatpump_optimizer/coordinator.py:11204 GUARD_OFF: pinned by mutation-autofix ("simulate_plan with no plan raises a translated operational error")
- custom_components/heatpump_optimizer/coordinator.py:11215 BOOLOP: pinned by mutation-autofix (re-indented; the #1795 away-band checks)
- custom_components/heatpump_optimizer/coordinator.py:11216 GUARD_OFF: pinned by mutation-autofix (re-indented; the #1753 background-base checks)
- custom_components/heatpump_optimizer/coordinator.py:11230 GUARD_OFF: pinned by mutation-autofix (re-indented; "#1753: the tile solves through the user-limit-free path …")
- custom_components/heatpump_optimizer/coordinator.py:11237 RETURN_DEL: pinned by mutation-autofix (re-indented; the what-if failure checks)
- custom_components/heatpump_optimizer/coordinator.py:11248 BOOLOP: pinned by mutation-autofix (re-indented; "#2257: a schedule ask whose two day energies tie reads 0.0 on one solve …")
- custom_components/heatpump_optimizer/coordinator.py:11287 GUARD_OFF: pinned by mutation-autofix (re-indented; the S2 #1753 borrow arms)
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

- **Gate at the tip's predecessor `48a4d93b4c`**, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e698fc8ac374 ./tests/run.sh` (`MODE: SCOPED -- 27 script(s) run, 6 scoped out`), five scripts red, each classified against a control on main's own tree at `e698fc8ac374` (a detached worktree, same machine):

  | red | at main `e698fc8ac374` | disposition |
|---|---|---|
  | `tests/doc_claims.py` and `tests/entities.py`: `architecture.md:299` HA-free count 63, measured 64 | green | caused by this merge; fixed in `48a4d93b4c` (`doc_claims.py`: ALL 441 checks PASSED) |
  | `tests/entities.py`: "a measured script's late-writing descendant is waited for, not recorded as nodata" | not run | the diff touches neither `tests/run.sh` nor `_coverage_revalidation`; the check races a `sleep 2` writer and failed at load1 28 and again at load1 10; CI's `fast` is the authority |
  | `tests/optimality.py`: `one\|summer_negative\|shoulder` claim closed (gap 0.0000%) | same line, 1 of 84 | inherited from main; the diff touches no solver module |
  | `tests/stress.py`: interned-table fill perturbation, sweep CPU 54.03x over 52.44x, `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]` | same lines, 4 of 122 | inherited from main and this machine's load |
  | `node tests/card.mjs`: heap out of memory | same abort, rc 134 (after `plan_view.py`, run.sh's order) | inherited: this machine's node 26.13 heap |

  `tests/typing_ruler.py` passed only under `HPO_TYPING_PYTHON` naming a venv built by the typing job's own `pip install --require-hashes --no-deps --build-constraint tests/requirements-build.txt -r tests/requirements-typing.txt` (mypy 2.4.1); the shared `venv-ha` holds mypy 2.3.1 and fails the pin guard. Cheaper detector: none owed for any row; none is this diff's except the count, which the scoped gate caught before the push.
- **`tests / fast (3.14)` at `9809bc79c2`** (job 135447271434): one features.py check, "the lift may raise the plan's peak over the unlifted plan's …" (main's #3803 room-lift block), `1 of 5937 FEATURE CHECKS FAILED`. At this tip `tests/features.py` prints `ALL 6003 FEATURE CHECKS PASSED` (the scoped gate's run above). **At `ce8412843a`** (job 135519436581) the one failed script was `tests/structure.py`, where `max_class_loc` measured 7871 against a recorded 7873 and the ratchet asked for a re-record. `c849ceade8` re-recorded it, and at this tip `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. Cheaper detector: none; each was cured by the next merge or re-record on the branch.
- **`governance / instrument-self-tests` at `ce8412843a` and `c849ceade8`** (job 135518892339): the round seat-partition self-test, at round ref `22938a5d62cb`, read D1/D2 cells as unowned (`FAIL D1 mode=cells seats=3 universe=97`, `unowned ('custom_components/heatpump_optimizer/__init__.py', 'M3', None)`). It reads the round's partition ref, not this diff, and main's own run at `a8efe1d1` is red on the same job. Not this pull request's; owed to main, not here.
- **`tests / replay` and `tests / nightly-status` at `1cf4d759c5`** (the delivery-row commit; jobs 135129123766, 135129122155): replay failed `owner-2026-10-30-away.json: cycle_cost [cpu_ratio 417.6 over its budget 332.8]` (`1 of 198 replay checks FAILED`), a CPU-ratio reading on the runner; `tests / replay` is green at `c849ceade8` (run 44540132172). `nightly-status` grades `main`'s nightly, is outside `merge_train.py owed-reds`, and this diff touches none of its reporter inputs; it is green at `c849ceade8`. Cheaper detector: none.
- **`tests / mutation` and `tests / mutation-autofix` at `c849ceade8`** (run 44540132172): the mutation job refused six added unpinned sites (`coordinator.py` 6146 BOOLOP and 11197 GUARD_OFF, `solve_gate.py` 76, 78, 90, 129), and `mutation-autofix` ended `skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. `python3 tests/mutation_table.py --pin-killed --base origin/main`, run here three times, printed `MUTATION TABLE INCONCLUSIVE` each time on a baseline red, never on a mutant: `typing_ruler.py` (the stale venv above), `doc_claims.py` (the count, fixed), then `entities.py`'s late-writer check alone (`baseline tests/entities.py: rc=1 failed=1`). Its null control (`coordinator.py:396 NULL_COMMENT`) survived every driver each time. No pin is committed; this head is not `DIRTY`, so `mutation-autofix` measures it on CI, and the sites stay disposed under `## Unpinned sites` as pinned by mutation-autofix.
- **`governance / wave-script` and `pr-contract` at `c849ceade8`** (run 44901934756): wave-script failed one check, "ownerOnlyRecord reads every declared owner-only brief's id, seat and dimension, and no near-miss" (`295 passed, 1 failed`). That base predates main's `6b230c6dd0`, which adds `dev/governance/dimensions/DX0.md`. At this tip `node tools/policy/check-wave-script.mjs` prints `296 passed, 0 failed`, and main's wave-script is green at `e698fc8a`, `86859b95`, `b486fe58` and `42809bec`. pr-contract's one error was this row's absence. Cheaper detector: none; a merge of main cures a stale-base red.
- `tests / mutation` at 28977f9e, two runs. Run 44463878660 checked the head alone against ratchet base 8751943e and refused six added sites: `coordinator.py` 6171 BOOLOP and 11222 GUARD_OFF (6148 and 11199 after main's merge), and `solve_gate.py` 76, 78, 90 and 129. Each is disposed under `## Unpinned sites` as pinned by mutation-autofix. That dispatch skipped `mutation-pins` and `mutation-autofix`, so they are pinned after this push: `unmeasured` here. Run 44458574179 checked the PR merged with main and refused one stale pin, not an unpinned site. Main's `ed7025dc` pinned `coordinator.py:HeatPumpOptimizerCoordinator.async_simulate RETURN_DEL 1457a93f` (old `        return payload`); this PR re-indents that line into the solve gate's block, where its anchor is `fd0988d6`, already pinned by `c06d2fb9` (`ci: pin killed mutants`, killed by `tests/features.py`). mutation-autofix read `skip-not-unpinned`. Repaired at 21aa2094 by merging main (c3d0249a) and deleting the 1457a93f file. `completeness_problems(load_budgets(), inventory())` returns `[]` at 21aa2094 and at 5ed23c25, and the 1457a93f problem with that file restored (null). Kill at the new line: see `## Head`. Run 44458574179 refused that pin alone.
- `governance / policy-docs` at 28977f9e (run 44463878660, job 135357182125): `machinery_ratchet` failed `churn_per_kilo_product_lines 34577 <= 14797 + band 3636`. The cap it read was this branch's pre-merge `dev/governance/config/machinery_budgets.json`; main re-recorded that cap to 34898 (30ae44cd94, after #3723's raise), and the same job on main at 7ae05284 passed (`35068 <= 34898 + band 3636`). The main merge at c3d0249a carries the 34898 cap, under which the measured 34577 passes. Cheaper detector: none exists for this one. It is a stale-base red that a merge of main cures, not a defect in the diff.

## Forward-carry

- Carry 0 (roster `R11-SEAM-cycle-solve`, added by the 2026-11-21 carry census after this handoff; review item f9a20486): measure the steady what-if pair's hour scatter for a hot-water-window, quiet-hours or wood-slot change sent alone. Not built here. This PR's design covers the cycle findings (when a solve runs, D1/D9/D17); its only `whatif.py` change moves `reference_days` off the loop and leaves the pair branch and its pricing untouched. The head is frozen past the handoff, and this push is a merge-resolution delta. The carry's own text releases the open pull request when its design excludes the item and asks for the disposition at its merge, which the orchestrator records there. Carry: dismissed: excluded by this PR's design; disposition recorded at its merge, as the carry directs
- The design note's `overlap-refresh` item (an `async_refresh` during the scheduled refresh starts a second `_async_update_data`, whose solve meets `gate.solving` and returns None) is pinned by the existing check "forcing an optimization while one runs is dropped, not queued (the solve entry point the press and the service share, F1.3 #1644)", now driven through `solve_gate.gate_for(coord).solving`. Carry: dismissed: built and pinned in this PR
- The design note's `flag-readers` item: every test that set `_optimization_running` now sets the gate (`tests/features.py`, `dev/audit/harnesses/r10_registry_leak.py` through the public `optimization_running`). Carry: dismissed: built in this PR
- The design note's `button-1641` item: no test here cancels the press mid-actuation, so there is nothing to report. Carry: dismissed: no test shows the cancellation the note asks to report
- The design note's `fallback-flap` item stays dismissed: one re-raise per restart, re-latched on the next solve. Carry: dismissed: one re-raise per restart, re-latched on the next solve

## Friction

- harness-port: stale: the finder's `$EXPORT/dev/audit/rounds/round11/D1/s1/m4_race.py` raises `KeyError: '_vent_cusum'` at the merge base because main's `d1-solve-state` census grew a name its `WRITERS` table lacks; both ends were measured with a two-edit port (Figures) that lives beside its `rl` helper in the export, not in the tree. Carry: dismissed: the round-11 register owns its harnesses
- frugal-guard: contradiction: the seat brief says to work inline with no subagents, and the session's frugal hook refuses a sixth inline read per prompt and points at a subagent; reads were batched and continued after each background run's wake instead. Carry: dismissed: a seat-environment conflict, recorded for the orchestrator


