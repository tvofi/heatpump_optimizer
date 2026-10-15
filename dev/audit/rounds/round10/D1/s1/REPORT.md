# D1-s1 report (round 10, baseline 17f1c55fad1b)

Cells: D1.M1, D1.M4 over `**`. Box B4 (load1 28-44 during all runs; every
number below is a count, contention-immune).

## Method
`rig.py` subclasses `tests/harness.py:FakeHass` (real `ThreadPoolExecutor`,
real `asyncio` tasks, loop exception handler recorded). The solve is the
production `optimize_in_process` run on the executor behind a threading gate, so
"mid-solve" is deterministic. Prices/weather injected at the fetch seams.
Lifecycle through `ha_setup_entry` / `ha_unload_entry`.

## Findings
### D1-s1-01 (M1, medium, bug) every unload leaks the torn-down coordinator via early_cutoff._STATES
`early_cutoff.arm` stores `CutoffInputs(inputs=coord.arbiter_inputs, ...)` in the
`WeakKeyDictionary` value keyed by that coordinator; `release` never clears
`held.wiring`, so the value strongly references its key and the entry never dies.
`m1_reload_leak.py`: 5 setup->cycle->unload rounds -> `torn_alive=5`
(2 rounds -> 2); registry_early_cutoff_torn_keys=5. Perturbation `--perturb`
(pop the entry at shutdown) -> `torn_alive=0`, all registries 0.
The whole coordinator (learners, histories, stores, numpy arrays) survives
every reload (options save) for the life of the process.
Seam rule: `grep -n "WeakKeyDictionary\[" custom_components/heatpump_optimizer/*.py`
then check each value type for a reference back to its key.

### D1-s1-02 (M4, medium, bug) a mode write during the solve is overwritten by the in-flight AUTO plan
`async_run_optimization` re-checks only `_entry_released` after the executor
await; a `async_set_mode(COMFORT|BOOST, refresh=False)` (the climate entity's
path) landing mid-solve is followed by `boost.adopt_plan(<auto action>)` and
`_apply_action` / `async_publish_current_action` of the AUTO plan.
`m4_mode_midsolve.py`: torn_midsolve_total=2 of 2 cells, tail publishes of the
AUTO action after the mode write=2; null control (same mode written before the
cycle) torn=0. Perturbation `--perturb` (re-run the fixed-mode branch when the
mode left AUTO during the await) -> 0. The torn state lasts until the next
refresh (not measured: under upstream HA a request made while the interval
refresh holds the debouncer lock is dropped). OFF is not keyable by this metric.

## Non-findings
- `m1_lifecycle.py`: setup -> solve -> reload mid-solve -> unload mid-solve ->
  setup: leaked_tasks=0, exceptions=0, new_cycle_ok=1, gated_solves=4; the
  only torn coordinator still alive is the D1-s1-01 one.

## Unfinished
- M4: only the `_mode` writer was raced. Remaining: enumerate every `self._*`
  read by `_solve_record`/`_solve_hubs` (by construction on the loop, deep
  copied) and the arrays passed by reference into the in-process fallback
  (`horizon.*`, `limits.*`) against loop-side writers.
- M1: `tests/harness.py:ha_unload_entry` calls `async_on_unload` callbacks and
  drops a returned coroutine (RuntimeWarning "async_shutdown was never
  awaited"); real HA schedules it. Instrument divergence, not yet quantified.

## Exposure
None.
