Closes #3786

R11-SEAM-wallclock-dst (class P7 residual). Four production seams carried a wall-clock hour across a DST change as if every day had 24 h:

- `ThermalModel.simulate_trajectory`, `simulate_trajectory_batch` and `simulate_trajectory_with_dhw` derived each step's hour of day as `start_hour + i * dt_hours`. On a transition day, from the change onward, every step read the learned internal-gains profile (and, for the DHW twin, the draw pattern) an hour off the step clock the optimizer builds (`optimizer._step_clock`, walked in UTC by `drift.utc_step_starts`). They now take that clock as `step_hours` and do no clock arithmetic of their own. Every production caller already held it (`h.step_hours`); `_optimize_with_dhw` no longer recomputes `start_time.hour + start_time.minute / 60`. With no clock, `simulate_trajectory_with_dhw` keeps its former default, a zoneless day from midnight.
- `dhw_schedule.hours_until_next_window` returned the wall-clock gap as a duration, which is 3.5 h from 00:30 to a 04:00 window when the spring-forward day holds 2.5 real hours. It now takes the aware `now` and builds the window's wall instant from its date and minute (`datetime.combine`, so no `+ timedelta` walks a zoned stamp). It measures the gap between the two instants with `drift.utc_elapsed_seconds`, which reads a naive instant through the kernel-step definition `drift.utc_instant`. Its three callers pass an instant: the coordinator's published countdown (`dt_util.now()`), the VVC pre-heat lead (`pump_schedule.vvc_should_run`, now taking `now`), and the planner's `next_window_in_hours`. The planner passes `h.start_time`, which its horizon protocol now declares.

The brief places the naive-instant definition "in const". Kernel-step landed it as `drift.utc_instant` (#3728), and this diff reads it there.

The brief's three instances are fixed, plus `simulate_trajectory_with_dhw`, which the issue's sweep lists (three times) and the brief omits. D15-s2-04 (unreproduced at judging) is recorded and not edited: its harness (`m5_zone.py --bundle B`) needs a diagnostics bundle the tree does not carry, and the register records `debug_replay.py` with 0 occurrences of `HASTUB_TZ`.

## Head

`57b249813e9f71bfeee329fc00106d109e8e7c46` merges the authored code head `efda938a30a6dcafa32fd23bbc41bf2966b3e73a`.

Repair commit on top of `352a829c6ae31e1022d4f47d08022a004d9013a3`: the survivor_triage entry for `dhw_schedule.py:618` (see `## Red checks

Red at head `57b24981` (`gh pr checks 3914`, run 46028388737).

- `tests / mutation`: `MUTATION TABLE REFUSED`: one stale disposition, flow_lift.py `FlowCurveBias.observe_temps` BOOLOP 04143c3f (old pin `if return_temp is not None and np.isfinite(return_temp)`). This diff does not touch flow_lift.py; the stale pin is on main and fixed by #3939. Inherited, no repair here. Unpinned sites, if any, are left to `mutation-autofix` (`mutation-pins` queued, unmeasured).
- `tests / fast (3.14, 2/4)`: `python3 tests/features.py` ended on `TypeError: ThermalModel.simulate_trajectory_batch() got an unexpected keyword argument 'start_hour'` at tests/features.py:7100. Cause: `_r11pp_batch` (landed on main by the plant-pins PR) still passes `start_hour=7.0` to the two trajectory entry points whose keyword this diff removes (see `## Forward-carry`); the merge with main left it. Repair commit 8bf9676b8a0f (branch handoff/r11-repair-3914b) passes `step_hours=(7.0 + arange(n)*0.25) % 24`, the same clock, to both calls; not run to completion locally.
- `gate`: follows `tests / mutation` and `tests / fast`.
- `tests / nightly-status`: reports the scheduled nightly, outside the owed set.

## Forward-carry

- The trajectory entry points (`simulate_trajectory`, `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`) take `step_hours`, the step clock, and no longer take `start_hour`. `hours_until_next_window` and `vvc_should_run` take an aware `now`, not a float hour. A branch cut before this merge that calls the old keyword or passes a float raises `TypeError` or `AttributeError`. The control is `dev/audit/harnesses/r11_wallclock_dst.py`, exit 1 on either transition day. The constraint detects itself: a stale call raises on its first use, under that group's own gate run. Carry: dismissed: a stale caller fails loudly under its own scoped gate, and the learners group cannot be named (see Friction)
- The same constraint for the DHW schedule callers: `hours_until_next_window(now, ...)` measures between instants, and a planner horizon must carry `start_time`. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Friction

- brief-citations: stale: the group's brief names "the one naive-instant zone definition R11-SEAM-kernel-step puts in const"; #3728 landed it as `drift.utc_instant`, and `const.py` holds no zone definition. Carry: dismissed: the brief is consumed by this pull request
- carry-audit: contradiction: `tools/audit/carry_audit.py`'s `GROUP_TOK` (`\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`) refuses every roster group id with a lower-case tail, so `Carry: R11-SEAM-learners`, the live group this brief lists as a valid target, reads UNROUTED, and the upper-cased spelling reads BAD-DEST. Carry: dismissed: tooling owned by the orchestrator, reported in the seat result





