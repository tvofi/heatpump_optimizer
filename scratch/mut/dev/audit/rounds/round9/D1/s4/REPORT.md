# Round 9 — D1 (robustness and stability), seat D1-s4

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), export `/home/claude/audit-r9-baseline`, box B6.
Cells: D1.M1–M6 over `optimizer.py`, `thermal_model.py`, `defrost.py`, `flow_lift.py`, `process_worker.py`.
Exposure: none. No earlier-round evidence (`tools/audit/round3..round8`) was read or cited.

All numbers are counts (contention-immune), taken with up to three finders sharing the box
(load1 2.5–7.1). Every harness runs from the export root with
`PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/<name>.py [--perturb]`.

## Method

- **M1 (spot)**: `worker_protocol.py` drives `process_worker.run_worker` over real pipes with six job kinds. The coordinator lifecycle (setup/reload/unload mid-solve) belongs to D1-s2's cells.
- **M2 (deep)**: `store_fuzz.py` loads 250 seeded mutants per arm through `DefrostDerate.from_dict` and `FlowCurveBias.from_dict`, then runs 24 healthy folds per bucket.
- **M3 (deep)**: `defrost_clock.py` drives `DefrostWindow` through DST in both directions, clock jumps, unreadable flags and naive/aware mixes.
- **M4 (deep)**: `snapshot_race.py` runs a real `ThreadPoolExecutor` solve from `_solve_snapshot` while the main thread rewrites every live input.
- **M5 (deep)**: `solve_guard.py` injects an L-BFGS-B failure and observes it through the real `async_run_optimization`, plus a 15-cell grid of non-finite inputs. `guard_sites.py` covers the DHW LP guard.
- **M6 (spot)**: `flow_inputs.py` sends hostile supply/return readings into the flow-bias learner. No other parser in these files reads an external payload.

## Findings

### D1-s4-01 (medium, P1): non-finite or out-of-range defrost duty loads silently, and the bucket pins at 0.55 permanently
`DefrostDerate.from_dict` casts the `duty` grid with a bare `float`, so the strings `"nan"` and `"inf"` get through. It does not bound the grid either. The sibling `factors` grid is re-clamped on load.

`derate_from_duty` maps a NaN or huge duty to `DERATE_MIN` = 0.55. `observe_duty`'s EWMA cannot wash it out. After 200 healthy zero-duty folds the NaN bucket still gives factor 0.5500, where a healthy one gives 1.0000.

Results over 250 duty-targeted mutants:
- `duty_targeted_stuck` = 53; 42 of these are pinned at 0.55 and all 53 are silent.
- Sibling control (the same 250 draws aimed at `factors`): 0 stuck.
- `--perturb` (a bounded cast on load): 0 stuck.

### D1-s4-02 (medium, P2): a failed solve is published as a plan and counted as a success
When every L-BFGS-B start raises, `_optimize_space_only` (≈ optimizer.py:4025) and `_solve_space` (≈ :3496) log ERROR. They then return the heuristic `initial_power` with status `failed (...)`. The same happens when one nan or inf horizon step makes every start non-finite.

`async_run_optimization` treats only an exception as failure. It adopts that result, resets `_solve_failures` to 0 and never raises the `solve_failures` repair issue.

| config | arm | `_solve_failures` after 3 cycles | repair issues | failed plans published |
|---|---|---|---|---|
| coord_minimal / coord_dhw | guarded (the injected fault) | 0 | 0 | 3 |
| coord_minimal / coord_dhw | null control (the same fault raised in `_forecast_arrays`) | 3 | 1 | 0 |
| coord_minimal / coord_dhw | `--perturb` (optimize raises on a "failed" status) | 3 | 1 | 0 |

A second trigger in the same harness puts a one-step nan, inf or -inf in each of the five horizon inputs (15 cells):
- Baseline: 9 cells return a failed plan and 2 raise.
- `--perturb`: 0 return a failed plan and 11 raise.

### D1-s4-03 (low, P1): one bad cell in a v2 defrost store discards all 12 measured buckets and is reported as a v5.3.0 upgrade
`_grid_of` drops the whole grid when a single cast fails. The else-branch then sets `migrated` because `factors` is present, without checking `version`, and logs "a pre-v5.3.0 store was upgraded".

Across 250 one-bad-cell v2 payloads, 226 are flagged `migrated` and 2712 measured buckets are discarded (the other 24 held a value that still casts). `--perturb-label` brings the flagged count to 0.

## Non-findings (what held)

| claim | harness | value |
|---|---|---|
| `FlowCurveBias.from_dict` rejects and re-clamps every mutant | store_fuzz.py | 0 raised and 0 bad of 250 |
| `DefrostDerate.from_dict` never raises | store_fuzz.py | 0 raised of 250 |
| The `factors` grid is re-clamped on load | store_fuzz.py | 0 stuck of 250 |
| `DefrostWindow` measures correctly under DST, naive/aware mixes and unreadable flags | defrost_clock.py | bad=0 of 9; with `as_utc` removed, bad=3 |
| A backwards clock jump gives seconds=0 | defrost_clock.py | the settle window rejects it, but that window lives in coordinator.py and was not measured here |
| Snapshot deep copies isolate the in-process solve from loop-side writes | snapshot_race.py | torn=0 of 6; with identity deepcopy, torn=6 |
| The worker answers raising and unpicklable jobs with an `err` frame and keeps serving | worker_protocol.py | well_formed=1, answers_next=1 |
| The worker answers a garbage frame with `load-err` and a clean exit | worker_protocol.py | well_formed=1, rc=0 |
| A job that prints corrupts the reply channel (stdout carries the replies) | worker_protocol.py | UnpicklingError; no `print(` anywhere in the package, so this is a hazard, not a finding |
| The DHW cost-LP guard falls back to the greedy planner cleanly | guard_sites.py | degrades_cleanly=1, logged at DEBUG only |
| Hostile water temperatures never push the flow bias past its clamp | flow_inputs.py | 0 raised and 0 out of clamp of 300; with the clip removed, 174 |

## Leads (outside these cells)

- **D1-s2, `coordinator.py`, the `internal_gains_profile` loader**
  - It uses `float(g)`, which admits "nan".
  - A NaN in the profile makes every optimizer start non-finite, which leads into D1-s4-02.
- **D1-s2, `_shutdown_process_pool` and `_run_in_process`**
  - `_run_in_process` holds the lock for the whole solve, and nothing puts a timeout on `pickle.load`.
  - So HA stop waits for any solve already in flight.
- **D1-s2, `_forecast_arrays`**
  - The optimizer has no guard on its own inputs: a single non-finite step gives a failed plan, and nan or inf wind raises at an `int()` cast.
  - This needs a check that upstream neutralises every non-finite value.
- **Owner unknown, `tests/hastub` Store**
  - The stub round-trips NaN through stdlib json, while production (orjson) writes null.
  - So the stub's persistence path differs from production for any NaN learner cell. This is P11-shaped.

## Harnesses

`store_fuzz.py`, `solve_guard.py`, `snapshot_race.py`, `defrost_clock.py`, `worker_protocol.py` (+ `worker_jobs.py`), `guard_sites.py`, `flow_inputs.py`, all under `tools/audit/round9/D1/s4/`.

## Unfinished

- **D1.M1**: the real-loop reload/unload-mid-solve cycle is D1-s2's (coordinator/`__init__`). From here only the worker's framing was driven. The shutdown-lock question above is still open.
