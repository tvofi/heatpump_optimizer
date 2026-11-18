# Design: R11-SEAM-cycle-solve (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75; `PLAN.md` names no ADR,
only "owed: designer.md, for the one in-flight guard and budget (S14, T14)".
Code read at `origin/main` bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; no `after`
edge, so no predecessor head. No production code on this ref. Revision 2,
answering `design-verdict/R11-SEAM-cycle-solve` 4f955bdd67 (`revise`, round 1):
the finalize self-test's what-if is disposed in E, §5 searches the whole
package, and D1-s1-01 stays a fix (§1).

## 1. Findings (harnesses under `dev/audit/rounds/round11/`)

| finding | harness | base | perturbed |
|---|---|---|---|
| D1-s1-03 | `D1/s1/m4_race.py --part B --origin debounced` | 7/8 stale | 0 |
| D17-s3-01 | `D17/s3/f01_run_optimization.py` | 0.5 | 2.0 |
| D9-s1-01 | `D9/s1/h_diagnose_refresh.py` | 2-4 msm/press | 0 |
| D9-s1-02 (weakened) | `D9/s1/h_solves_per_cycle.py` | stacked | unstacked |
| D9-s1-03 | `D9/s1/h_whatif_backlog.py --k 4` | 12 jobs | 3 |
| D9-s1-04 | `D9/s1/h_whatif_loop_block.py` | 384 loop steps | 0 |
| D1-s3-04 | `D1/s3/peer_wait.py` | lock held 1 | 0 |
| D1-s1-01 (weakened) | `D1/s1/m1_stop_midsolve.py --arm stop_midsolve` | 1 | 0 |

The judge (`JUDGE.json`) reproduced D9-s1-02's stacking but not its B1 breach,
so the budget is a count (§4). D1-s1-01 reproduces at main: the design
reviewer read `--arm stop_midsolve` 1 and `--arm stop_idle` 0 at 8f39313a44,
whose worker path in `coordinator.py` is bc658f9's. H stays a fix. The fixer
re-takes the harness at both ends; if the fixer's own base reads 0, H's
D1-s1-01 parts (`_WORKER_STOPPING`, the restored-notice delete) become
regression pins and nothing more.

## 2. Owning seam

The cycle (`COMPONENTS.md`) owns when a solve runs. Owner: a new cycle-seam
module `custom_components/heatpump_optimizer/solve_gate.py`, a per-coordinator
side table (`whatif.py`'s and `boost.py`'s discipline) holding the one
in-flight guard and the one budget. `coordinator.py` keeps the solve paths and
asks the gate; `whatif.py` (solver seam) gains one pure function run in the
worker. Callers only: `services.py`, `button.py`. `price_tiles.py`,
`process_worker.py`, `optimizer.py`: no edit. No concern needs two owners.

## 3. Shape

**A. Guard.** `SolveGate` fields: `solving`, `rerun` (moved off the class:
today `_optimization_running`, `_optimization_rerun_requested`; the
`optimization_running` view reads `gate.solving`), `trailing`,
`background_taken`, `reason`, `user_running`, `user_waiting`. Functions:
`absorb_request(gate, refreshing) -> bool` (solving: set `rerun`, the #1754
latch; refreshing without a solve: set `trailing`; else False);
`take_trailing(gate)`; `admit_background(gate)` (True once per main solve);
`async user_slot(gate) -> bool` (one running, one waiting, newest supersedes).

**B. Requests (D1-s1-03 and its 16 sweep sites).** Coordinator override:
`async_request_refresh` returns when `absorb_request(gate, self._refresh_task
is not None)`, else `super()`. `_async_update_data`'s `finally`, on
`take_trailing` and an unreleased entry, schedules `async_request_refresh()` as
an entry background task, which lands after the debouncer's lock is free. Every
writer calls this one method.

```
write -> async_request_refresh -> absorb_request
  solving    -> rerun    -> in-flight solve's finally re-runs once (actuated this cycle)
  refreshing -> trailing -> refresh finally -> task -> debounced refresh
  idle       -> super()
```

**C. One run-now path (D17-s3-01; the button's double solve).**
`async_optimize_now() -> str | None`: in a fixed mode first
`async_run_optimization()` (today's private plan, which the refresh does not
solve there); then `await self.async_refresh()`; returns `gate.reason`, which
`async_run_optimization` records at each return, or on a failed refresh
`"no_prices"` for the price-coverage `UpdateFailed`, else `"solve_failed"`.
`handle_run_optimization` and `ForceOptimizationButton.async_press` both await
it; the button drops its second solve. Translation keys unchanged. The press
may await the refresh because 6c1834977a set the button platform's
`PARALLEL_UPDATES` to 0 (#1641's reason, a held slot, is gone): it stays 0,
pinned, and `off_the_action`'s docstring says the press now awaits.

**D. Diagnose publishes (D9-s1-01).** `_republish()`: `async_set_updated_data`
of `_build_data_dict()` with the last payload's `sensor_advisor` carried;
`async_diagnose_interval` calls it instead of `async_request_refresh`.

**E. Background budget (D9-s1-02).** One background what-if per main solve.
`_maybe_run_fuse_advisor` asks `admit_background` just before its
`async_simulate` (after its weekly gate); `_maybe_refresh_price_tile` asks
before `price_tiles.take`, so a denied tile does not move the rotation.
`debugger.py`'s `_solver_smoke` (the debug collection's finalize self-test,
`async_simulate({}, limited=False)`) is exempt and does not call
`admit_background`, so it neither asks nor takes the slot: it runs once per
finalize, never per cycle; `run_self_tests` already cuts it off at
`SELF_TEST_BUDGET`; and the self-test exists to report whether a what-if
equals the live plan, which a denial would replace with no answer. Being
`limited=False`, it never enters F's user slot either.

**F. User what-ifs (D9-s1-03).** The `limited` path keeps
`whatif.limited_answer`, then awaits `user_slot`; a superseded ask returns
`{**held.answer, "rate_limited": True}` unsolved. K overlapping asks solve at
most two: the one in flight and the newest.

**G. Off the loop (D9-s1-04).** `whatif.reference_days(live, sim)` returns
both `reference_day` pairs; `async_simulate` ships it via `_await_off_loop`
(the pairs already pickle: `_held_solve` ships them); `schedule_days` keeps only
the comparison.

**H. Worker arms (D1-s3-04, D1-s1-01).** `_reap_killed(worker)`: `kill()`,
`wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)`, used by both `_run_in_process` arms.
`_shutdown_process_pool(at_exit=True)`: `kill()` and one
`os.waitpid(pid, WNOHANG)`, no sleeping wait (#533 kept). `_WORKER_STOPPING`
(a `threading.Event`) set by `_stop` before the reap: `_await_optimize`
re-raises with no notice and no in-process rerun, and `async_run_optimization`
returns `"shutdown"` without `_note_solve_failure`. `_clear_worker_fallback`
also deletes the issue when no entry has a cause latched in this process (a
restored notice). Sweep sibling: a successful solve deletes `solve_failures`
whatever the in-memory counter reads.

**Invariants:** no request is lost and each costs at most one extra run; one
main solve in flight; no solver, tariff or model arithmetic moves; background
callers never touch the user slot or card cache (#1753); #1755's per-entry
causes keep their meaning.

## 4. Alternatives (lost on the code)

- `Debouncer` subclass arming a trailing call while executing: reads Home
  Assistant's private `_execute_lock`/`_execute_at_end_of_timer` (and
  `tests/hastub` must mirror them), and re-runs fetch and solve where the
  #1754 latch re-runs the solve inside the cycle that actuates.
- The finder's guard answering only from the held state: the card calls once
  and renders `rate_limited` as a note (`www/heatpump-optimizer-card.js`,
  `run()`), so the last draft is never priced (T14 in full).
- A CPU budget (main wall x (1+n) <= B1): the weekly fuse advisor starves on an
  install whose main solve exceeds B1/4, and it needs per-kind cost memory.
- Action keeps its solve and adds the button's refresh tail: two solves per
  call, through B's debounced path.
- Guard state on the coordinator class: grows `coord_footprint`, which
  `PLAN.md` Risks prices.

## 5. Sibling sites (commands)

- `grep -n 'async_request_refresh()' custom_components/heatpump_optimizer/*.py`:
  18 lines at bc658f9, all reach B's override.
- `grep -n 'async_run_optimization()' custom_components/heatpump_optimizer/*.py`:
  button and service (C); the cycle's two kept.
- `grep -n 'worker.wait()' custom_components/heatpump_optimizer/coordinator.py`:
  two, both H.
- `grep -n 'is_persistent=True' custom_components/heatpump_optimizer/*.py`:
  six; `solve_worker_fallback`, `solve_failures` covered; `_audit_grid_fee`
  (money) and `legionella.py` (actuation) out of scope, already in the
  register's N-uncleared-issue sweep.
- `grep -n 'async_simulate(' custom_components/heatpump_optimizer/*.py`:
  four calls and the definition: fuse, tile (E, budgeted), `debugger.py`
  `_solver_smoke` (E, exempt), service (F).
- The D14 probes `ISSUES.json` cites (`n_dropped_refresh`, P10 reach,
  N-solve-recompute enumerator) are in neither `plan/r11` nor
  `handoff/audit-r11-register` e7a8c56f51; the greps stand in.

## 6. Evidence plan

- Failing tests first. `tests/features.py`: a write during a debounced
  in-flight solve builds one more `_solve_record`; the action publishes the
  raised price and moves `last_optimization`; a press solves as often as one
  cycle, and a reset pressed while an optimize-now press awaits is not
  queued behind it (`PARALLEL_UPDATES` 0); a diagnose press enters `_multi_start_minimize` 0 times and publishes
  `last_diagnosis` and `sensor_advisor`; a fuse cycle with tiles runs one
  background what-if and leaves the tile cursor; a finalize self-test run
  after the cycle's background slot is taken still returns a `cost_delta` and
  leaves `background_taken` as it found it; K=4 user asks start <= 6 jobs
  and the last is answered fresh; a steady schedule ask makes 0 loop
  `simulate_step` calls. `tests/worker_deadlines.py`: the transport arm frees
  the lock on a kill-deaf child; a stop mid-solve raises no notice and runs no
  in-process solve; a restored notice clears on the first healthy solve.
- Finder's harnesses at both ends move to §1's perturbed column (D9-s1-03 to
  <= 6 by design, §4). Null controls stay: `m4_race.py --origin direct` 0;
  `f01_run_optimization.py` button arm 2.0; the diagnose job alone 0 msm;
  `h_solves_per_cycle.py` default arm; `h_whatif_backlog.py` K=1 3 jobs;
  `h_whatif_loop_block.py` `steady=False` 0; `peer_wait.py` timeout arm 1;
  `m1_stop_midsolve.py --arm stop_idle` 0.
- Goldens: none move; `tests/golden/claimed_drift.txt` and
  `tests/golden/card_claimed_drift.txt` byte-identical.
- Mutation targets: `absorb_request`'s branches, `take_trailing`,
  `admit_background`'s reset, `user_slot`'s supersede, `async_optimize_now`'s
  fixed-mode branch and reason mapping, `_republish`'s carry, `_reap_killed`'s
  timeout, the `_WORKER_STOPPING` test, `_clear_worker_fallback`'s new delete.

## 7. Hot files, serial position, carries

`PLAN.md` order: `coordinator.py` fourth (after kernel-step, plant-model,
actuation-release); `optimizer.py` third (no edit planned); `strings.json`,
`services.py` second (after plant-model); `README.md`, `docs/configuration.md`,
`button.py` first; `whatif.py` this group alone. `strings.json`'s
`run_optimization` "does not fetch new ones" becomes true to C; the README and
`docs/configuration.md` already say it fetches. Release notes owe the trailing
re-plan, one solve per press, and superseded what-ifs answered held. No p1/p2
split. `solve_gate.py` is a new tracked file: a measured closure
(`tests/closure.py`) and `tests/seam_map.json` in the same pull request.

### Notes for the fixer

- `async_refresh` during the scheduled refresh starts a second
  `_async_update_data`, whose solve meets `gate.solving` and returns None
  (today's "re-run recorded"); pin it. Carry: R11-SEAM-cycle-solve (item overlap-refresh)
- #1641 took the button's cycle off the press for the held slot that
  `PARALLEL_UPDATES` 0 removed (ruled in review). Report back only if a test
  shows that cancelling the press cancels the cycle mid-actuation. Carry: R11-SEAM-cycle-solve (item button-1641)
- Tests set `_optimization_running` directly:
  `grep -rn '_optimization_running\|_optimization_rerun_requested' tests/`,
  move them to the gate. Carry: R11-SEAM-cycle-solve (item flag-readers)
- H's delete can re-raise once per restart when entry A's cause is its own
  job's; A's next solve latches it again. Carry: dismissed: one re-raise per restart, re-latched on the next solve (item fallback-flap)
