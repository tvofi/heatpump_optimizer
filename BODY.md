<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`. Run
`tools/pr/prepr.sh <this body>` before opening. -->

Bound the process worker's reply wait and the stop path's lock.

`_run_in_process` wrote the job and then blocked in `pickle.load(stdout)` with no deadline, inside `with _PROCESS_LOCK:`. A worker that is alive but silent never raises, so the #511 fallback (`ProcessWorkerUnavailable`) never fired. Every later solve queued on the lock, a config-entry reload did not help (lock and worker are module-level), and Home Assistant's stop ran into the supervisor timeout because `_shutdown_process_pool` could not take the lock either.

Observed on one install (v7.1.2, HA 2026.10.4, Raspberry Pi 4), 2026-11-05: last completed optimization 09:02:28, none until a restart at ~10:11, five option saves in between without effect, and at shutdown:

```
Thread[SyncWorker_11] … coordinator.py, line 1909, in _run_in_process: status, payload = pickle.load(stdout)
Thread[SyncWorker_0]  … coordinator.py, line 1850, in _shutdown_process_pool: with _PROCESS_LOCK:
Shutdown stage 'stop integrations' / 'final write' / 'close': still running: async_register_worker_shutdown.<locals>._stop()
```

`systemmonitor` CPU use on that host rose from ~14–15 % (09:05–09:15) to a flat ~37–39 % (09:15–10:10) with memory flat at ~49 %: about one core busy for the whole window. Why the worker stopped answering, and why the kill at stop did not break the read, I could not establish.

Changes (`coordinator.py`):

- After writing the job, wait for the reply with `select()` and `PROCESS_REPLY_TIMEOUT_S` (1800 s). The worker serialises its whole reply before writing it (`process_worker._dump`), so a readable pipe means the job is done. On expiry the worker is killed, its reap bounded, `_PROCESS_WORKER` cleared, and `ProcessWorkerTimeout` (a `ProcessWorkerUnavailable`) is raised; the next call spawns a fresh worker. A stream without a descriptor (the in-memory test doubles) is read as before.
- `_await_optimize` does **not** rerun a timed-out job in process (the same job would hold an executor thread as long). It logs a warning and raises a translated `UpdateFailed` (`process_worker_timeout`), so the last plan stays in effect.
- `_shutdown_process_pool` takes the lock with `_SHUTDOWN_LOCK_TIMEOUT_S` (5 s) and skips the handle swap if it cannot; the child has already been killed above it.
- New exception key `process_worker_timeout` in `strings.json`, `en.json`, `sv.json`.

Deadline: solve times on the same install over three days (168 distinct `solve_time_ms` values from `sensor.heat_pump_optimizer_optimization_status`): median 18 s, 90th percentile 263 s, max 426 s. 1800 s is ~4× the max and well below the ~55-minute hang. Open question for you: `_await_off_loop` (diagnosis, sysid) still falls back to the executor on any `ProcessWorkerUnavailable`, the timeout included; I left it unchanged.

**Contributor credit.** This change is by the outside contributor Bankaifan, first opened as PR #3226 (https://github.com/tvofi/heatpump_optimizer/pull/3226, head `ba704972f6494d4e6af520095e940b049d9afed3`). It is re-authored here as a seat pull request because decision 0011 gives an outside contributor no way to author one: the contributor's commits are cherry-picked unchanged, each keeping its author (Bankaifan), onto origin/main with no squash and no edit, and the three-dot diff is the same patch as the original (identical patch-id). The measurements below are the contributor's, from their own head; the review of this pull request re-derives them.

## Head

`5088d3688c4793f9612cd7ab3cd866b806afd27b`

## Mutation proof

Two mutations, each run with `PYTHONPATH=tests/hastub python tests/features.py`. The first was measured at `585be114`, the second at `530457f6`; the head's last commit (`ba704972`, a bounded `worker.wait` after the kill on timeout, plus a comment) came after them and is not separately mutation-proven. No test drives a child that survives its kill.

- reply deadline removed (`if has_fd and not select.select(…)[0]:` → `if False:`): `3 of 4836 FEATURE CHECKS FAILED`
  - `a worker that gives no reply within the deadline raises ProcessWorkerTimeout` — `raised None after 30.0 s; returned None`
  - `and it frees the lock and the next job gets a fresh worker` — `lock_free=True before=4636 after=4636`
  - `_await_optimize keeps the last plan on a timeout: translated UpdateFailed, no in-process solve` — `raised None; returned ('slept', 4636, 'STATE')`
- stop-path lock timeout removed (`_PROCESS_LOCK.acquire(timeout=…)` → `_PROCESS_LOCK.acquire()`): `1 of 4836 FEATURE CHECKS FAILED`
  - `the stop path returns within its lock timeout while the lock is held` — `_shutdown_process_pool took 9.95 s with the lock held`

## Null control

On unmodified `main` (`e57dfbbe0`): `_run_in_process(time.sleep, (8,))` blocked for 8.0 s (no deadline attribute exists), and `_shutdown_process_pool()` with `_PROCESS_LOCK` held by another thread for 6 s took 6.0 s. In the new section two checks are null controls: a job that answers inside the deadline returns and keeps its worker, and a solve inside the deadline returns its plan through the worker.

## Figures

- `ALL 4836 FEATURE CHECKS PASSED` at the head — `PYTHONPATH=tests/hastub python tests/features.py`
- `STRUCTURE RATCHET PASSED`, every metric at or below its budget — `PYTHONPATH=tests/hastub python tests/structure.py`
- solve-time spread (median 18 s, p90 263 s, max 426 s) — HA recorder history of `sensor.heat_pump_optimizer_optimization_status`, attribute `solve_time_ms`, 3 days, one install
- CPU/memory during the hang — HA long-term statistics (5-minute mean) of `sensor.system_monitor_processor_use` / `sensor.system_monitor_memory_usage`

Environment caveat: CPython 3.14.6 with `tests/requirements-ci.txt` hash-pinned; `seat_venv.sh` asks for 3.14.7, which `uv` could not fetch here, so the mypy census and the full `GATE_SCOPE=auto ./tests/run.sh` were **not** run.

## Red checks

none: no check has concluded on this pull request yet (it was just opened); the reviewer reads every check-run of the head. The contributor's earlier note about `pr-contract` refusing the original author does not apply to this seat-authored pull request.
- `mutation` at 5088d3688c47: red by construction on the 6 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

none

## Friction

none
