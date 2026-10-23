Design review: revise a858dfda0b5b62a506184bcc6ab7fcdf04adf863 class-open

Reviewed: dev/programme/designs/R10-LIVESTATE.md at a858dfda0 (detached worktree), round 2 of 3, against code at fd7e289d0 and the designer's unpushed spike (`livestate-spike.patch`, applied cleanly to fd7e289d0 in a throwaway clone). Round-1 points 2 and 3 are closed. Point 1 is closed for the manual plan and reopened only for the routing of the residue. Token count: not reported by this harness.

## Revise point

1. class-open. R10-LIVESTATE.md:82 ("Yes, per-cycle writers, unprobed, 10"). The criterion is right. The disposition is not, in both directions, and the note routes all 10 as "never a user command" into an issue the fixer's PR files.
   - **User commands the note says are absent:**
     - `_async_load_thermal_learning` (coordinator.py:3913) loads into the buffer-cooling and house-heat-loss learned state. `async_update_thermal_params`, the `set_thermal_parameters` service, writes the same state before any await: `_apply_house_heat_loss_scale(DEFAULT_HOUSE_HEAT_LOSS_SCALE)`, `_house_heat_loss_samples = 0`, `_apply_buffer_cooling_rate(...)`, `_buffer_cooling_samples = 0` (coordinator.py:6138-6143). Only its save waits for the read (coordinator.py:4178).
     - `dhw_learning.py` `async_load_profile` (dhw_learning.py:172) has a user writer too: `async_set_cooling_rate` writes `apply_cooling_rate`/`cooling_samples = 0` (dhw_learning.py:230-231) before its save.
     - Both have the same reachability as the manual plan, which the note took in scope: a service reaches the coordinator once `entry.runtime_data` is set (__init__.py:325), with the spawned load still possibly in flight.
     - The state belongs to the thermal-parameter owner. R10-PARAMS-OWNER is live and after this group, and its finding D7-s1-82 is `set_thermal_parameters`. The destination is therefore that group's brief (finding-propagation.md: a live roster group), not an issue.
   - **Writers the note claims that do not exist:**
     - `notifier.py` `async_setup_notifier` awaits `notifier.async_load()` (notifier.py:322) before `async_add_listener(_on_update)` registers `handle`.
     - `debugger.py` `async_setup_debugger` awaits `collector.async_load()` (debugger.py:662) before `_COLLECTORS[coordinator]` and the listener exist.
     - `pump_arbiter.py` `_load` runs under `held.lock` inside `apply`, ahead of `_arbitrate` (pump_arbiter.py:1049-1050). Its in-memory writers (pump_arbiter.py:889, :954) need checking for any other path outside that lock before it is counted.
     - An issue listing these as established is the filing CLAUDE.md's ruling refuses, and finding-propagation.md carries only measured findings.

   Fix wanted: re-disposition the 10 by reading each writer's registration order and lock. Route the two user-command sites to R10-PARAMS-OWNER as a carry (`Carry: R10-PARAMS-OWNER (item ...)`). Move the sites with no concurrent writer to "No". Have the fixer's issue list only sites with a probe and null (or name them as unprobed leads, not findings). No shape change is needed in this group.

## Verified (claims 1-3)

- **Manual plan.** The spike's `async_apply_manual_plan`/`async_clear_manual_plan` await `_manual_plan_store.async_wait_for_read()`. The port (`probe_manual_restore_port.py`) differs from the review's probe only by giving the stub store the real store's read future and wait, and running the clear as a task. It reads `lost_midload=1 lost_null=0` at fd7e289d0 and `lost_midload=0 lost_null=0` on the spike (re-run here). The ordering holds for the real store: the loader awaits `async_load` inline, so it resumes inside the same step that settles the read, and the waiting clear runs after it.
- **Residual (a write before the load task's first step): acceptable, not class-open.** It is unreachable through Home Assistant's surfaces. The loaders are spawned in the constructor (__init__.py:302), and services, entities and actions reach the coordinator only through `entry.runtime_data`, assigned after `await coordinator.async_config_entry_first_refresh()` (__init__.py:318, :325). By then every spawned loader has taken its first step, which sets `_reading` synchronously (store.py:686). State this reason in the note in place of "shared by every held store".
- **Publish signature** (claim 2). The spike's `publish(self, coord, state=None, /, **fields)` performs the rebind. `tests/structure.py` on the spike: `seam_cut_total=711`.
- **Payment** (claim 3). Spike, `cyclomatic_complexity`: `async_run_optimization` 14, `_mode_superseded` 2, `_async_drive_pumps` 15, `_update_current_state` 44, `async_set_mode` 5, `async_set_away` 8. structure.py: `functions_cc_over_15 30 <= 30`, `max_cc=44`, `max_class_loc=8453`, `class_excess_loc` 18213 (-20), `coordinator_attrs` 146, `coordinator_multiassigned_attrs` 114; "6 metric(s) IMPROVED and not yet recorded"; no row over its cap. The seam_map.json diff adds `_adopt_away_override` and `_fixed_mode_action` as `core` and moves one key; it relabels nothing.

## Two-page cap

designer.md step 8 ("one file, at most two pages") binds the designer, not this review. design-review.md's revise classes are seam, shape, sibling sites, evidence plan and cost, and length is none of them. The note is 2,899 words, roughly three times the cap. It is not a revise point. The orchestrator decides whether to waive the cap or have the designer cut. decision: orchestrator

## Carried observations (notes for the fixer)

- N6. `async_set_mode` clearing `_optimization_rerun_requested` also drops a re-run requested before an AUTO -> COMFORT -> AUTO round trip within one solve. Test that a mid-solve input change followed by such a round trip still re-runs, or state the loss in the PR. Carry: R10-LIVESTATE (item drev-06)
- N7. `restore_session` now calls `asyncio.get_running_loop()` from the constructor's spawn line. A test or harness that constructs the coordinator outside a running loop raises there. Keep construction inside the loop in the ported harnesses (drev-01). Carry: R10-LIVESTATE (item drev-07)
