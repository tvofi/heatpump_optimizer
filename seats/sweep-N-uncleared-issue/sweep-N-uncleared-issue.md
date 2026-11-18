# Class sweep: N-uncleared-issue (round 11, D14 steps 3-4)

Mechanism: a repair issue raised on a failure is never cleared by the recovery path, so it outlives the condition it reports.
Ledger status: the class is not yet a key of `dev/audit/config/bugclasses.json` at the register head; `barriered: false`.
Finding in the class: D1-s1-01 (weakened, low) -- `solve_worker_fallback` survives a restart because `_clear_worker_fallback` returns early on the empty module latch `_WORKER_FALLBACK_CAUSES`.

## Enumerator

`dev/audit/rounds/round11/D14/sweep/enum_uncleared_issue.py` (AST over the whole package). Seam rule widened from the finding's `grep -n 'is_persistent=True'`: every raised issue id that is persistent (`is_persistent=True` or `persistent=True` through `issues.set_issue`/`ConfigNotices.report`), has no clear site at all, or (persistent and) is cleared only behind a test of state a fresh process starts empty (an early return on a module global, or an enclosing `if` on an attribute an `__init__`/`_init*` initialiser sets to 0/None/False/empty).

Result at the register head: 25 issue ids raised, 10 seams, 3 flagged `restart_gated`.

Controls (`bash dev/audit/rounds/round11/D14/sweep/controls_uncleared_issue.sh`):
- positive: re-finds `solve_worker_fallback` as `persistent,restart_gated`;
- null: a clean fixture (raise + unconditional clear, not persistent) gives seams=0;
- perturbation: deleting the one line that clears `price_currency` moves seams 10 -> 11; neutralising `_clear_worker_fallback`'s early return moves restart_gated 3 -> 2.

## Dispositions

Instances (each probe exits 1 at the register head: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep/probe_uncleared_issue.py <probe>`):

| seam | file::symbol | probe | beyond finding |
|---|---|---|---|
| `solve_worker_fallback` | `custom_components/heatpump_optimizer/coordinator.py::_clear_worker_fallback` | PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep/probe_uncleared_issue.py worker_fallback  (fails: 1 left) | false |
| `solve_failures` | `custom_components/heatpump_optimizer/coordinator.py::HeatPumpOptimizerCoordinator.async_run_optimization` | PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep/probe_uncleared_issue.py solve_failures  (fails: clear gated on in-memory _solve_failures>=3, counter not restored) | true |
| `grid_fee_magnitude, grid_fee_sign` | `custom_components/heatpump_optimizer/coordinator.py::HeatPumpOptimizerCoordinator._audit_grid_fee` | PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep/probe_uncleared_issue.py grid_fee  (fails: the only audit path runs behind schedule.active, so an inactive fee layer never clears the persistent notices) | true |
| `dhw_disinfection_switch_lost_<entity>` | `custom_components/heatpump_optimizer/legionella.py::LegionellaGuard._drive_switch` | PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep/probe_uncleared_issue.py switch_lost  (fails: 0 clear sites) | true |

- `solve_failures` (persistent): raised at the third consecutive failure; the success path deletes it only `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT` (coordinator.py:6457), and the counter starts at 0 in `_init_runtime_state` and is never stored, so after a restart every healthy solve leaves the restored notice up -- the same mechanism as D1-s1-01 on a second issue. Probe is structural.
- `grid_fee_magnitude`, `grid_fee_sign` (persistent via ConfigNotices): `_audit_grid_fee` runs only from `_fee_series`, which `_price_series` calls only `if schedule.active` (coordinator.py:7273); switching the fee layer off (mode none, or no rules and a zero fixed fee) stops the audit, so the notice about a fee that no longer applies stays. Probe is structural (call-graph).
- `dhw_disinfection_switch_lost_<entity>` (persistent): raised when a disinfection-switch record is dropped as unreadable; no code path clears it, even once the switch reads off. The persistence is deliberate (legionella.py:516 comment); the missing withdrawal is the instance. Probe is structural.
- `solve_worker_fallback`: the judged site; probe is behavioural (fresh latch, restored notice, one healthy solve: 1 left).

Guarded / not applicable:

| seam | disposition | reason |
|---|---|---|
| accuracy_drift | guarded | cleared in _async_watch_learning_drift on a changed verdict with the ring not alarmed; the ring is persisted (_async_save_snapshots), so a fresh process can clear it |
| cop_degradation | guarded | cleared in _observe_cop_health; the CUSUM state it gates on is persisted (load ~4594, save ~4729) |
| freq_watchdog | guarded | enumerator flags it restart_gated (_freq_fallback initialised False) but the latch is restored from the store (coordinator.py:4623) and saved (4763): heuristic false positive; the notice tracks a latched fallback that is still in force |
| dhw_legionella_unreachable | guarded | clear_unreachable_issue runs on every credited cycle (legionella.py async_track), with last_cycle persisted; also cleared by OffStepNotice |
| dhw_legionella_unverified | guarded | clear_unverified_issue runs on the first credited cycle once a tank probe exists; while no probe is configured the reported condition still holds |
| ConfigNotices: floor_return_implausible, lower_floor_modelled, comfort_band_contradiction, valve_target_above_comfort | guarded | ConfigNotices.report(None) clears every cycle, unconditionally (its _raised dict only suppresses a repeat create, so an empty dict after restart does not block the clear) |
| store_version_<where> | not applicable | non-persistent: HA drops it at restart, and the condition is a load-time event that changes only across a restart |
| non-persistent issues (pump_mode_unreadable, price_feed_stale, pump_write_ignored, dhw_* in-memory-deduped notices, price_unit_*, price_currency, setpoint_check set_issue ids, floor_return_silent) | not applicable | not a seam: non-persistent issues do not outlive a restart and each has an in-process clear on its recovery branch (reviewed site by site: 25 raised ids, every create and delete call in the package) |

## Barrier (proposed)

A `tests/` check built on the enumerator: every persistent issue id must have a clear site not gated on fresh-process state and not behind a branch that stops running when the condition's input goes away; an allow-list names the deliberate exceptions. Cost: one AST pass over the package, well under a second of gate time.

`instances` = 3 (seams beyond the finding); `instance_list` also carries the judged site with `beyond_finding: false`.
