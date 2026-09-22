# D9 — CPU and memory efficiency (Raspberry-Pi-class target), round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), read from the
isolated worktree `/Users/timmalmstrom/audit-r6-D9`. Interpreter
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` (numpy 2.4.6,
scipy 1.17.1), `PYTHONPATH=tests/hastub`, run from the worktree root. All
commands below were run exactly as written.

Box: 8-core Apple M1, 8 GB, OpenBLAS. Shared with the D4 (Chromium) and D8
auditors, so `load1` sat between 4.5 and 8.8 throughout — every wall, CPU and
RSS figure is marked `provisional: true` wherever the harness prints it.
Counts, bytes and same-session CPU *ratios* against
`tests/stress.py:reference_solve` are final.

`exposure`: none. No earlier audit record, no `docs/audit-*.md`, no
`docs/backlog.md`, no `gh`, no `git log`, no GitHub. Two pre-existing harness
files under `tests/` (`stress.py`, `features.py`) were read as instruments;
neither is an earlier round's finding record.

## Method

One harness per metric the brief fixes, under `tools/audit/round6/D9/`, each
with the README's header contract (metric definition, exact command, expected
value, baseline SHA, machine), the `tests/stress.py` thread pin **before** the
numpy import, and `RESULT` lines plus `thread_factor`, `load1` and `swapins`.

| harness | metric | instrumented production symbols |
|---|---|---|
| `h1_gradient.py` | simulate-step-equivalents per gradient / per full solve; full solves per `optimize()` | `ThermalModel.simulate_step`, `ThermalModel.simulate_trajectory_batch`, `ThermalModel.simulate_dhw_only`, `optimizer._batch_fd_gradient`, `optimizer._multi_start_minimize` |
| `h2_payload.py` | published payload bytes split by `_unrecorded_attributes` | `sensor.async_setup_entry`, each entity's `_unrecorded_attributes`, `coordinator._build_data_dict` |
| `h3_retained.py` | retained bytes slope per cycle; loop-thread work per cycle | `coordinator.async_run_optimization`, `coordinator._build_data_dict`, `sensor.async_setup_entry` |
| `h4_gil.py` | longest contiguous GIL hold, starvation share, production yield total | `optimizer._multi_start_minimize` (yield sites), `HeatPumpOptimizer.optimize`, the stdlib `time` module both yield doors resolve to |

`tests/stress.py:reference_solve` is the ruler for every "share of a solve"
below. Two sampling quirks of the existing tooling had to be worked around and
are recorded because they cost real time:

* **`stress.build_case` re-patches the hooks you installed.** `SolverWork`
  assigns its own wrappers to `ThermalModel.simulate_step`,
  `simulate_trajectory_batch` and `optimizer._scoped_minimize` at
  `__enter__`. A harness that wraps those class attributes before calling
  `build_case` is silently overwritten: `h1_gradient.py`'s first version read
  **0 batch calls on a solve that makes 442**. The harness now disables
  `SolverWork.__enter__`/`__exit__` and counts the seams itself.
* **`h4_gil.py`'s own first version measured its heartbeat, not the GIL.**
  `--heartbeat-ms 1.0` was passed straight to `asyncio.sleep`, whose argument
  is seconds, so the "longest gap" came back at ~1010 ms — the heartbeat
  period. Corrected to `interval / 1000.0`; the corrected instrument is
  validated by the two controls below.

## Findings

### D9-01 — On the executor-hosted solve path the HA loop is starved for 97 % of the solve, and the solve's own GIL yields move that by 0.75 points

`optimizer.py` yields the GIL eight times per solve: `_lbfgsb_restart` sleeps
2 ms before each of its restarts, `_multi_start_minimize` sleeps 2 ms between
consecutive L-BFGS-B starts, and one more 2 ms at the DHW/space seam. Measured:
**8 yield calls totalling 32.000 ms per full solve** (two solves per run), which
is **1.08 % of the solve's wall time** and ~1.4 reference solves. The comment
at each site says the yield exists because "each L-BFGS-B run is Python-heavy
and holds the GIL even from an executor thread, so on the weak hardware Home
Assistant usually runs on a long solve starves the event loop".

On a real event loop (`h4_gil.py`, never `FakeHass`) with the production
`optimize()` on a `ThreadPoolExecutor` thread and a 1 ms heartbeat coroutine:

* longest contiguous GIL hold **36.9 ms**
* **starvation share 0.9737** — 97.4 % of the solve's wall time elapsed in
  heartbeat gaps longer than 5 ms
* 575 gaps over a 2.95 s solve

Removing all eight yields (`--perturb no-yields`) leaves the longest hold at
28.0 ms and moves the starvation share **up** to 0.9812. That is the whole
effect of the mitigation: 0.75 of a percentage point of starvation share for
1.08 % of the solve spent sleeping. The yields do not, and structurally
cannot, bound the hold — they sit *between* L-BFGS-B runs, and each run is
tens of milliseconds of contiguous hold, so the maximum gap is set by the
longest run and not by what happens between runs.

*Null control / positive controls, both executed:* a synthetic 300 ms
loop-thread block (`--perturb synthetic-block`) is reported as a longest hold
of **301.1 ms** and a starvation share of 1.0037, so the instrument reads a
known block correctly; running the solve on the loop thread
(`--perturb same-thread`) is reported as **2865.3 ms**, i.e. the whole solve.
The baseline's 36.9 ms is therefore a real hold and not a heartbeat artefact.

*Scope of the consequence.* The shipped path is not this one: `_await_optimize`
submits `optimize_in_process` to a **separate interpreter**
(`process_worker.py`), so on a healthy install the solve holds no GIL here at
all and this finding does not bite. It bites on the fallback the code names
itself — `_note_worker_fallback` logs "The plan is correct, but the solve
holds the GIL (#199 #290)" and re-solves with
`hass.async_add_executor_job(optimize_in_process, ...)` — i.e. exactly the
install whose worker cannot start. On that install every cycle stalls the whole
Home Assistant instance for the solve.

*Pi extrapolation.* The M1 number above is one core of an 8-core M1. A
Raspberry Pi 4 is roughly 4x slower per core and a Pi 5 roughly 2.5x (stated as
an **assumption**: no Pi was available on this box; the factor is not measured
here). Scaling the M1 hold of 36.9 ms by 4 gives ~150 ms of contiguous hold on
a Pi 4, and the starvation share — a ratio, so it carries over — means ~97 % of
a solve that on a Pi 4 would be ~12 s is time the event loop cannot run. The
M1 figure this scales from is `solve_wall_ms=2953.0`.

Severity `medium`: user-visible (the whole instance stalls for seconds every
cycle) but confined to the fallback installs, and bounded by
`WORKER_FALLBACK_CAP`, after which the last plan is kept instead. Stop-rule
class `bug`.

### D9-02 — The stress gate's simulate-work channel cannot see the DHW planner's own simulations

`tests/stress.py:SolverWork` counts simulate step-equivalents on exactly two
seams: `ThermalModel.simulate_step` and `ThermalModel.simulate_trajectory_batch`.
The DHW planner simulates through a third entry point,
`ThermalModel.simulate_dhw_only`, which `_dhw_plan_temps` reaches on every call
(and `_repair_dhw_floor` calls in a loop of up to 48 rounds). Measured per full
solve:

| scenario | counted step-equivalents (both seams) | `simulate_dhw_only` steps | uncounted share |
|---|---|---|---|
| `single_zone_dhw` | 5 472 | 2 304 (24 calls) | **29.6 %** |
| `two_zone_dhw` | 86 112 | 2 304 (24 calls) | 2.6 % |
| `zero_range_pin` | 83 808 | 2 304 (24 calls) | 2.7 % |
| `fuseguard_cap` | 61 824 | 1 152 (12 calls) | 1.8 % |
| `two_zone_space` | 64 512 | 0 | 0 % |

The five cells are the `--case` values of `h1_gradient.py`; the range across
them is 0 % to 29.6 %, and dropping the most favourable cell (0 %) leaves the
mean share at 9.2 %.

A synthetic 2x regression confined to the DHW planner's simulation — the exact
shape `SCENARIO_WORK_FACTOR` and `SCENARIO_KERNEL_FACTOR` exist to catch —
moves neither counted channel, and on the single-zone DHW solve nearly a third
of the simulated work is not on a counted seam at all. Why this is bounded
rather than dramatic: `simulate_dhw_only` is the cheap tank-only simulation,
so its CPU share is smaller than its step share, and 29.6 % of steps doubling
moves total solve cost by well under the gate's own noise floor. Severity
`low`, stop-rule class `hygiene`: the integration is not wrong; the instrument
has a hole in what it declares it can see.

`--perturb`: `--case two_zone_space` (the same solve with `dhw=False`, a config
change) drives the uncounted count to **0** while the counted channel stays
non-zero (64 512). Direction: `to_zero`.

## Non-findings (checked, held, with the number)

1. **The batched jac really is reached on every shape, including the
   zero-range-bound channel.** `h1_gradient.py --case zero_range_pin` (4
   manually pinned steps, one of them a `(0, 0)` bound):
   `batched_gradient_calls=431`, `batch_rows=41 376`,
   `scalar_simulate_step_calls=42 432` — **every** gradient is served by the
   batch, none by scipy's scalar FD. `--case fuseguard_cap` (`power_cap_kw=3.0`,
   the 16 A fuse channel): `batched_gradient_calls=316`, all batched. The 31.5x
   regression D9-01 (round 5) describes does not reproduce at this baseline.
   `--perturb cap` moves `simulate_step_equivalents_D9` from 86 112 to 61 824 —
   it moves, but as *a different solve*, not as a path switch.

2. **Simulate-step-equivalents per gradient is 96 on the batched path, and the
   objective's own evaluation is the other half of each L-BFGS-B iteration.**
   `equiv_per_gradient_D9` = 194.82 on `two_zone_dhw`, 210.46 single-zone,
   194.90 space-only; that figure is total-equivalents over gradient calls, so
   per gradient the batch contributes 96 (= `n_steps` rows) and the paired
   scalar objective evaluation contributes another ~96 (455 objective
   evaluations x 96 `simulate_step` calls = 43 680). The owner's "96
   simulate-step-equivalents per L-BFGS iteration, not ~9,300" holds for the
   *gradient*: scipy's own estimator would cost n = 96 scalar objective
   evaluations per gradient, i.e. 96 x 96 = 9 216 scalar `simulate_step` calls,
   against the batch's 96 rows. `--perturb horizon` (hours 24 -> 12) halves it
   as the direction requires: `equiv_per_gradient_D9` 194.82 -> **97.53**,
   `batch_rows` 42 432 -> 15 024.

3. **One full solve per `optimize()` per cycle.** `h1_gradient.py` reports
   `full_solves=1` for all five cases: `optimize()` enters
   `_multi_start_minimize` exactly once (4 candidate solves + 4 polish restarts
   = 8 `_scoped_minimize` entries), and `coordinator.async_run_optimization()`
   calls `_await_optimize` exactly once per cycle (counted at that seam in a
   driven cycle: 1 of 1). The DHW LP stage and `_co_optimize` add no further
   multi-start entry.

4. **No retained-object growth over coordinator cycles.**
   `h3_retained.py --cycles 15`: deep `sys.getsizeof` of the whole coordinator
   instance state is **269 982 B after cycle 1 and 269 982 B after cycle 15**
   (slope exactly 0.0 B/cycle, first half 0.0, second half 0.0), and the
   `gc.get_objects()` census grows by **0 tracked objects** (67 301 objects,
   3 562 lists, 6 765 dicts — flat; a separate 10-cycle census with a
   per-cycle dict/list/ndarray breakdown also grew by nothing). The two
   candidate append sites, `_poll_immersion`'s `_immersion_evidence` /
   `_immersion_events`, are trimmed by `del self._immersion_evidence[:-6]` and
   `del self._immersion_events[:-20]`.

   **Gap, named.** `tracemalloc`'s `traced_current` slope over the same 15
   cycles is **+18 843 B/cycle and does not flatten** (223 386 -> 273 641 over
   10 cycles in a separate run), while the gc census shows no growth at all, so
   the growth is in untracked (str/bytes) allocations; a
   `compare_to(..., 'traceback')` attributes the top entries to the
   `isoformat()` calls inside `_build_data_dict`'s `space_forecast` /
   `dhw_forecast` comprehensions and to `dhw_schedule.append({...})`. I could
   not make those blocks survive: `dicts_with_space_power` and
   `dicts_with_dhw_power` are **0** live objects at every census, so nothing
   holds those dicts. I did not find a retained object, and I am not calling
   the traced slope a leak on evidence a census contradicts.

5. **`--perturb no-immersion-trim` did not move the retained-byte slope, so the
   arm is not evidence either way.** The perturbation applies (1 method
   patched, located by symbol) but the number stays 0.0 B/cycle, because the
   cycle this harness can drive — `async_run_optimization()` plus the publish
   path — never reaches the immersion poll: it needs a measured power reading
   and a non-default gate. `_async_update_data` itself is not driven, because
   it begins with `_fetch_tibber_prices` and `_fetch_weather_forecast`, which
   need network. Harness limitation, not a refutation of the trim.

6. **Payload bytes, split by the recorder exclusion set.**
   `h2_payload.py --config coord_two_zone` (59 entities registered through the
   real `sensor.async_setup_entry`): `data_dict_bytes=7 932 B`;
   `attributes_recorded_bytes_per_cycle=4 486 B`;
   `attributes_excluded_bytes_per_cycle=12 246 B`; recorded share **0.2681**.
   At the coordinator's 15-minute interval that is
   `recorded_bytes_per_day=430 656 B`, `excluded_bytes_per_day=1 175 616 B`.
   The exclusion set does most of the work: the two plan sensors declare
   6 120 B each as `projection`/`slots`/`manual_override`/`dhw_windows`
   unrecorded, and the largest *recorded* attribute anywhere is
   `thermal_battery.components` at 587 B, then
   `predictive_insight.dhw_usage_profile` at 458 B. **Caveat, so this is not
   overread:** the recorder deduplicates identical attribute payloads into
   `state_attributes` rows, and those two change per solve, so genuinely new
   bytes are ~1 KB/cycle and the rest may collapse; the recorder's own dedup
   was not measured.

7. **The payload harness's declared `--perturb drop-exclusion` arm did not
   move, and is reported as such.** Removing `"schedule"` from every sensor
   class that declares it unrecorded moves the recorded count 4 486 -> 4 488 B
   and the excluded count 12 246 -> 12 244 B — a +2 B artefact: no entity
   registered under any of the five `coordinator_scenarios()` configs publishes
   an attribute literally keyed `"schedule"`, so the removal has nothing to
   expose. The perturbation `h2_payload.py` actually rests on is `--config`,
   which does move: `--config coord_all_features` gives
   `data_dict_bytes=8 785` (from 7 932), `attributes_recorded_bytes_per_cycle=5 081`
   (from 4 486), `recorded_bytes_per_day=487 776` (from 430 656).

8. **Loop-thread work per cycle is small.** `h3_retained.py --cycles 15`:
   `loop_thread_cpu_ms_mean=43.67 ms`, max 48.18 ms, against a reference solve
   of 23.8 ms — **1.84 reference solves of loop-thread CPU per cycle**, over the
   solve submit/await, `_build_data_dict()` and every entity's `native_value` +
   `extra_state_attributes`. At 96 cycles/day that is ~4.2 s of event-loop CPU
   per day; scaled by the same assumed Pi-4 factor of 4, ~17 s/day. Not a
   defect.

9. **`maxiter` is not a binding knob.** `h1_gradient.py --perturb maxiter`
   (doubling `maxiter` on every `_multi_start_minimize` entry) moves *nothing*:
   `batch_rows=42 432` and `simulate_step_equivalents_D9=86 112`, identical to
   the baseline. So neither the four candidate solves nor the four polish
   restarts truncate at the 300-iteration cap, and the restarts are genuinely
   short runs rather than second full solves. Reported as a lead that did
   **not** move.

10. **The `sleep(0.002)` calls are inert on the shipped path, not merely
   small.** The yield sites are inside the solve, and the shipped solve runs in
   `process_worker.py` — a different interpreter — so on a healthy install the
   32 ms per solve buys nothing at all. They are not removed here because the
   fallback path in D9-01 is real; recorded as context for that finding's scope.

## What I could not finish

* **"Does the stress gate as shipped detect a synthetic 2x regression?"** — not
  answered by execution. `stress.py` takes the gate lock, needs exclusivity by
  process (`ps aux | grep -E "[s]tress\.py|[t]ests/run\.sh"`) and runs the
  51-scenario sweep; the box was at `load1` 4.5–8.8 with D4's Chromium and D8
  running, and `tests/audit/README.md` records that three `stress.py`
  processes at load 6.5 once corrupted the budget table itself. It needs the
  quiet window. D9-02 is the executed *part* of the answer — what the gate's
  counted channels structurally cannot see — and it was found without the
  sweep.
* **The `coord_all_features` / `coord_minimal` payload arms** of `h2_payload.py`
  are implemented and runnable but were not taken in this session; only
  `coord_two_zone` was.
* **`_repair_dhw_floor`'s 48-round loop** was located and its simulation entry
  point counted (D9-02), but its round count per solve was not measured
  separately from the 24 `simulate_dhw_only` calls reported.

## Handoff notes

* `tools/audit/round6/D9/` is four new tracked files under `tools/`. Per
  `CLAUDE.md`, a new tracked file must be in a measured closure or on
  `tests/closure.py`'s `INERT` list; that classification belongs to whoever
  commits these, not to this seat.
* Every wall/CPU/RSS `RESULT` in these harnesses is marked
  `provisional: true` in its own output and needs the quiet-window re-take.
  Counts, bytes and ratios are final.
