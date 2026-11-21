# Round 11 class sweep: N-unbudgeted-background (box SW4)

**Class mechanism (judge):** background solves (what-ifs, advisors) stack onto
the main solve with no per-cycle budget or in-flight guard, so a burst
multiplies worker jobs and delays the scheduled solve. `N-unbudgeted-background`
has no entry in `dev/audit/config/bugclasses.json` at the register tip: it is a
new class this round (nearest P10), effectively `open`.

**Findings in the class:**

- **D9-s1-02** (weakened, low): the fuse advisor plus its steady pair plus the
  price tile stack after the main solve in one cycle.
- **D9-s1-03** (verified, medium): user what-ifs queue 3 solves each; the 3 s
  limiter has no in-flight guard.

**Result:** 17 seams; **0 instances beyond the findings**, 5 judged sites,
4 guarded, 8 not applicable. `instances` = 0.

## Detector (D14 step 3)

### Static enumerator

`dev/audit/rounds/round11/D14/background/enumerate.py` lists every call, inside
a package function, of a primitive that runs work off the event loop or starts
a solve:

- `_await_optimize`, `_await_process` and `_await_off_loop`. All three reach
  the one persistent worker under `_PROCESS_LOCK` (`coordinator.py:2072`);
  `_await_off_loop` falls back to the executor only on
  `ProcessWorkerUnavailable`.
- `async_simulate`, which is 1 to 3 full solves.
- `async_add_executor_job` and `run_in_executor`.

The bodies of the primitives themselves are excluded. Each seam carries:

- its enclosing function;
- name-based trigger roots, which are approximate;
- guard tokens in code only, with comments and docstrings stripped. A comment
  saying "never on its budget" at `coordinator.py:9001` and `:10695` matched
  before the strip and is not a guard.

The output is in `D14/background/seams.txt`.

### Runtime probe

`probe_burst.py --seam S --k K [--guard]` drives K concurrent calls of a seam on
the shipped worker, using the D9-s1 library `d9s1lib`. It counts
`_run_in_process` entries by job and reports the latency of a scheduled solve
submitted behind the burst, over its solo latency. The finding's own
`h_solves_per_cycle.py` (output in `D14/background/spc_out.txt`) supplies the
per-path cycle counts.

### Controls and perturbation

- **Positive control:**
  - The enumerator lists every judged site: `_maybe_run_fuse_advisor`
    (`coordinator.py:9004`), `_maybe_refresh_price_tile` (`:10709`),
    `async_simulate` (`:11239`), `_held_solve` (`:11245`) and
    `handle_simulate_plan` (`services.py:775`).
  - `probe_burst.py --seam whatif --k 4` re-finds D9-s1-03 on this tree:
    **12 worker jobs, scheduled solve 11.10x solo**. At K=1 it gives 3 jobs
    and 3.56x. The finding read 12.4x and the judge 12.04x.
  - `h_solves_per_cycle.py --cycles 4 --arms default,tiles_fuse` shows the
    D9-s1-02 stacking. In the default arm every cycle has 2 multi-start
    entries and only main jobs. In tiles_fuse the worst cycle has 9 entries,
    with fuse_advisor 1+2 jobs and price_tile 4 jobs (5.43 s CPU against the
    main solve's 4.40 s).
- **Null control:**
  - The enumerator on `D14/background/clean_fixture` (one background solve
    behind a `.done()` in-flight check) gives 1 seam, **0 unguarded**.
  - The probe at K=1 gives 3 jobs per what-if.
- **Perturbation:**
  - Replacing the fixture's guard line with `if False:` gives 1 unguarded;
    restoring it gives 0.
  - `probe_burst.py --seam whatif --k 4 --guard` adds a one-line in-flight
    guard in memory and drops the burst to **3 jobs, 3.80x**, the K=1 level.

## Disposition (D14 step 4)

### Judged sites (5, `beyond_finding: false`)

| seam | finding |
|---|---|
| `coordinator.py:9004` `_maybe_run_fuse_advisor` | D9-s1-02 |
| `coordinator.py:10709` `_maybe_refresh_price_tile` | D9-s1-02 |
| `coordinator.py:11239` `async_simulate` | D9-s1-03 |
| `coordinator.py:11245` `async_simulate._held_solve` (the steady pair) | D9-s1-03 |
| `services.py:775` `handle_simulate_plan` (the service entry) | D9-s1-03 |

### Guarded (4)

| seam | guard |
|---|---|
| `coordinator.py:6430` `async_run_optimization`, the main solve | `if self._optimization_running:` records a re-run and returns (`coordinator.py:6359-6363`), so concurrent requests coalesce into one |
| `coordinator.py:10675` `async_diagnose_interval` (diagnose_interval service and button, no in-flight flag) | Measured: `probe_burst.py --seam diagnose --k 4` gives 4 `diagnose_record` jobs, but still **1 solve job** with a scheduled-solve latency of **1.44x** (K=1: 1.56x). The refresh each call requests is coalesced by the coordinator's refresh and the running flag above. `diagnose_record` makes no optimizer call: it runs 1 + len(SWAPPABLE) single-step `simulate_step` calls (`diagnosis.py:75-156`), not a solve. A burst therefore does not stack solves. |
| `debugger.py:325` `_solver_smoke` (`async_simulate({}, limited=False)`) | Runs once per debug-collection stop: `_async_finish` is spawned by `finalize`. A second stop raises `ServiceValidationError` (`debugger.py:717`), the button is available only while `not collector.final` (`button.py:235`), and self-tests are bounded by `SELF_TEST_BUDGET` (`debugger.py:76`). Measured at 1 worker job per trigger. |
| `coordinator.py:2166` `_sysid_step_off_loop` | Once per cycle, inside `async_run_optimization` under the same running flag |

### Not applicable (8)

**Fixed per-cycle count, non-solve jobs (3):**

- `coordinator.py:1080` `_replay_interval` (learner interval replays).
- `coordinator.py:2206` `_with_sensor_advisor`, once per successful cycle at
  `coordinator.py:6141`.
- `coordinator.py:2184` `estimate`, the away-recovery estimate.

A fixed set of learners or advisors runs once per cycle; no user action or
burst multiplies them. Measured: all `_async_update_data`-path jobs together
are 7 worker jobs and **0.0087 s CPU over 4 cycles** in both arms, which is
negligible against the main solve's ~1.1 s per cycle.

**One-shot (2):**

- `coordinator.py:1959` `_stop` (worker shutdown).
- `frontend.py:193` `async_register_frontend` (setup).

**Not a solve and not the worker (3):**

- `debugger.py:595` `_read` (store files).
- `debugger.py:664` and `:672` `_async_replay`: one recorder query plus up to
  4 replay-document builds on HA's executor (`fit_replay`,
  `debugger.py:462-472`), triggered by a diagnostics download, with no
  optimizer call.

`_async_replay` has no in-flight guard either, but it neither holds
`_PROCESS_LOCK` nor delays the scheduled solve. **It is noted for D9
(executor load on repeated downloads), not counted in this class.**

## Proposed barrier (D14 step 5)

- **Runtime:** a `tests/` check built from `probe_burst.py`. For every seam the
  enumerator returns whose trigger is a user action or a per-cycle advisor,
  assert that a K=4 burst starts no more worker solve jobs than K=1 (an
  in-flight guard). For the cycle tail, assert that background solve CPU per
  cycle is at most a declared fraction of the main solve's.
- **Static:** `enumerate.py` as a lint that refuses a new seam whose path
  carries no guard token unless it is listed with its reason.
- **Cost:** about 60 s for the whatif arm and about 10 s for diagnose. The
  enumerator takes under 1 s.
- **Count:** with 0 beyond-finding instances, the class is the two judged
  findings, which share the cycle tail and `async_simulate`. The fix is one
  in-flight guard on `async_simulate`'s user path plus a per-cycle budget on
  the advisor tail; the barrier test pins both.
