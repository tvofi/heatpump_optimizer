<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`. Run
`tools/pr/prepr.sh <this body>` before opening. -->

Bound the process worker's reply wait and the stop path's lock, and repair the three defects the round-1 review (verdict/3232, blocked) found in that change.

`_run_in_process` wrote the job and then blocked in `pickle.load(stdout)` with no deadline, inside `with _PROCESS_LOCK:`. A worker that is alive but silent never raises, so the #511 fallback (`ProcessWorkerUnavailable`) never fired. Every later solve queued on the lock, a config-entry reload did not help (the lock and the worker are module-level), and Home Assistant's stop ran into the supervisor timeout because `_shutdown_process_pool` could not take the lock either. The contributor observed this on one install (v7.1.2, HA 2026.10.4, Raspberry Pi 4) on 2026-11-05: no optimization completed between 09:02:28 and a restart at about 10:11, and the shutdown traces show `_run_in_process` parked in `pickle.load(stdout)` while `_shutdown_process_pool` waited on `_PROCESS_LOCK`.

**Contributor credit.** The deadline change is by the outside contributor Bankaifan, first opened as PR #3226 (head `ba704972f6494d4e6af520095e940b049d9afed3`). It is re-authored here as a seat pull request because decision 0011 gives an outside contributor no way to author one. The contributor's four commits (`61cec72ac`, `010534bbc`, `dd4416f1a`, `5088d3688`) are kept unchanged, each with its author Bankaifan: no squash, no edit, no rebase. The seat's repairs are new commits on top of them.

The contributor's change (`coordinator.py`):
- After writing the job, the reply is awaited with the deadline `PROCESS_REPLY_TIMEOUT_S` (1800 s). On expiry the worker is killed, its reap is bounded, `_PROCESS_WORKER` is cleared and `ProcessWorkerTimeout` (a `ProcessWorkerUnavailable`) is raised; the next call spawns a fresh worker.
- `_await_optimize` does not rerun a timed-out job in process. It raises a translated `UpdateFailed` (`process_worker_timeout`, in `strings.json`, `en.json` and `sv.json`), so the last plan stays in effect.
- `_shutdown_process_pool` takes the lock with `_SHUTDOWN_LOCK_TIMEOUT_S` (5 s), and skips the handle swap if it cannot.

The seat's repairs, one per review item:
1. **`select.select` refused a pipe fd >= 1024 (FD_SETSIZE).** Home Assistant raises its soft `RLIMIT_NOFILE` past that limit, so on such a host every solve fell back in process. The wait is now `_reply_ready`, a `selectors.DefaultSelector` (epoll on Linux) opened in a `with` block, which closes it on every exit path. The descriptor probe no longer compares `fileno() >= 0`, a value that is never negative; it only asks whether `fileno()` raises.
2. **N-log-flood barrier.** The `_await_optimize` timeout warning now goes through `log_held(hass, f"process_worker_timeout:{entry_id}", ...)`, cleared on the next solve the worker carries. I chose `log_held` over the reasoned list: the condition persists every cycle while the worker keeps timing out, and that is the case the barrier's comment routes to `log_held`. The owner is `hass` with the entry id in the key, because `_await_optimize` has no coordinator (the same scheme as the per-entry `_WORKER_FALLBACK_CAUSES`). The existing `forget_held(hass)` at unload resets it.
3. **`_await_off_loop` reran a timed-out job on the executor with no deadline.** It now re-raises `ProcessWorkerTimeout` and holds a per-job warning (`log_held(hass, "off_loop_timeout:<qualname>", ...)`, cleared when that job next completes). Each caller then uses the seam it already has. The interval replay (`_replay_interval`'s `except Exception` -> `None`) and the sensor advisor (`_with_sensor_advisor`'s `except Exception` -> no ranking) skip their job this cycle. The away-recovery estimate and the sysid step have no handler of their own, so the timeout reaches `async_run_optimization`'s `except Exception` -> `_note_solve_failure`: a held `solve_failure` ERROR, the repair issue at its threshold, and `solve_failed`, so the last plan stays. Alternatives considered: *bounding* the executor rerun is impossible, because a Python thread cannot be cancelled, so a bound would only stop waiting while the thread and its core stayed busy. *Swallowing* the timeout in `_await_off_loop` would need a made-up return value per job (a recovery-hours guess, a sysid override), which the architecture rules refuse. Re-raising takes neither route.

## Head

`c9614abb748fdc9158427cd86dd278ae20e898d4`. Every figure below was measured at this head unless it names another SHA. It descends from the PR head `e80a319c21f7b652fa579bab63e8997532aef22c` and merges origin/main at `8a39977cba2f9f0c798647e8fe1b793e4fcdf106`.

## Mutation proof

Each mutant was run with `PYTHONPATH=tests/hastub python3 tests/features.py` in its own worktree of the seat's fix commit, with the final `tests/features.py`:
- m1, `_reply_ready` back on `select.select([stream], [], [], timeout_s)`: `1 of 4868 FEATURE CHECKS FAILED`. The failing check is `a worker pipe at fd >= 1024 answers in time and still times out as a timeout`, with `warm raised ProcessWorkerUnavailable('process worker exited rc=None: filedescriptor out of range in select()'); stdout fd=-1`.
- m2, the `except ProcessWorkerTimeout` clause in `_await_off_loop` deleted: `1 of 4868 FEATURE CHECKS FAILED`. The failing check is `_await_off_loop raises a timeout to its caller instead of rerunning it on the executor`, with `raised None after 30.5 s; jobs=[_run_in_process, sleep]`.
- m3, the `_await_optimize` `log_held` call put back as `_LOGGER.warning(...)`: `1 of 4868 FEATURE CHECKS FAILED`. The failing check is `two timeouts in a row warn once, and the next solve logs the recovery`, with `latch records=[]`.
- The same three checks fail first on the pre-fix tree (`b0e9ac34c`, the PR head merged with main, carrying the new tests): `3 of 4868 FEATURE CHECKS FAILED`.
- The mutation table's own mutants, from `python3 tests/mutation_table.py --pin-killed --base origin/main` (two runs, Linux): 8 new sites, all killed by `tests/features.py` and pinned under `tests/mutation_ledger/killed_by/coordinator.py/`. That covers both CONST sites (the deadlines doubled), `_shutdown_process_pool` GUARD_OFF, `_run_in_process` BOOLOP and GUARD_OFF, `_reply_ready` RETURN_DEL, and `_await_off_loop` RAISE_DEL and RETURN_DEL.
- The contributor's own mutants (deadline removed: 3 checks red; stop-path `acquire()` unbounded: 1 red) were re-run by the reviewer at `e80a319c2` and are in verdict/3232.
- Residual, disclosed: the bounded reap `worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)` after a timeout's kill needs a child that survives SIGKILL, which no portable check can produce, so no check drives that branch. Carry: dismissed: the branch needs a child in uninterruptible sleep, which no portable test can produce; disclosed here and in verdict/3232

## Null control

- Each new check that passes at the head failed on the pre-fix tree (above). A check that passed on both trees would have proven nothing.
- The reviewer's probe (`evidence/probe.py` on verdict/3232, sha1 `d10fc5d0982d90356dcfc907307245a7c8e8a76b`) was run from each tree root:
  - `fd` mode, 1100 fds held. Pre-fix `b0e9ac34c`: `RESULT fd FAIL ProcessWorkerUnavailable: process worker exited rc=None: filedescriptor out of range in select()`. Head `35985625b`: `RESULT fd ok child=11908 stdout_fd=1106`.
  - `offloop` mode, a 0.5 s deadline and a 3 s job. Pre-fix: `returned None after 3.5s (job re-ran on executor)`. Head: `raised ProcessWorkerTimeout after 0.5s`.
  - `leak` mode, 10 timeouts. Both trees: `10 timeouts in 3.1s fds 7->5`, with no zombie child (the one listed child is the live worker, state `S`).
- The new section's own null controls: a job that answers inside the deadline returns and keeps its worker, and an off-loop job inside the deadline returns through the worker without touching the executor.
- The fd check's precondition is part of the check: it asserts that the worker's `stdout.fileno() >= 1024`. A run that never reached a high descriptor therefore fails rather than passes vacuously. That happened once during development, on m2's run with `stdout fd=16`, and led to the reap-before-fill reorder in `3391176d9`.

## Figures

- `ALL 4888 FEATURE CHECKS PASSED` at the head; the null control is origin/main `8a39977cb`, which reads `ALL 4876 FEATURE CHECKS PASSED`, so this PR adds 12 checks (6 contributor, 6 seat). Before the last main merge, `87d51d3dd` read 4870: verdict/3232's 4864 at `e80a319c2`, plus the seat's 6 checks (fd >= 1024, the held warning, the off-loop raise and its null control, and the two design values) — `PYTHONPATH=tests/hastub python3 tests/features.py`
- `ALL 2632 ENTITY CHECKS PASSED`, including `ok   R10 N-log-flood barrier` — `PYTHONPATH=tests/hastub python3 tests/entities.py`
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`
- 0 new unpinned sites against the base: `PIN KILLED: 2 pinned, 0 left unpinned` on the second run, after `PIN KILLED: 6 pinned, 3 left unpinned` on the first. The 3 left by the first run were paid by `2bd2b70eb`: two design-value checks and the dropped `>= 0` comparison — `python3 tests/mutation_table.py --pin-killed --base origin/main`
- `MODE: SCOPED -- 26 script(s) run, 7 scoped out` — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- toolchain: numpy 2.5.4 and scipy 1.18.1, equal to `tests/requirements-ci.txt`, after `bash tools/audit/seat/cloud-setup.sh`; `cloud-setup.sh --check` reports OK — `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'`
- the 1800 s deadline rests on the contributor's solve-time spread (median 18 s, p90 263 s, max 426 s; one install's HA recorder, 3 days). It cannot be re-derived in tree. The design-value check pins the band its comment derives: 4 x 426 s <= deadline <= 30 min.

## Unpinned sites

None. All 8 sites this diff adds are pinned by `tests/features.py` kills, recorded under `tests/mutation_ledger/killed_by/coordinator.py/` in `35985625b` (one seat commit). The two CONST pins are design-value checks: every timing check shortens the constants, so only a value check reads the shipped figures. That encodes a design choice (step 11): changing the deadline means changing its check.

## Red checks

`tools/pr/prepr.sh` ran clean at this head, and origin/main has not moved since that run (still `8a39977cb`).


none concluded at `c9614abb7`: the head has not run CI yet. The reds concluded at the previous head `e80a319c2` (run 42135610131), with causes from the logs:
- `tests / fast (3.14)`: the log ends `1 TEST SCRIPT(S) FAILED`, and the failing script's lines come before the tail I read. At that head, `tests/entities.py` fails `R10 N-log-flood barrier` (`1 of 2632 ENTITY CHECKS FAILED`, verdict/3232's run), which this head fixes (`ALL 2632 ENTITY CHECKS PASSED`). The cheaper detector exists and costs about 9 minutes: run `tests/entities.py` locally before the handoff. The re-author body skipped it; this body runs it.
- `tests / mutation` and `tests / mutation-autofix`: the autofix log says `mutation-autofix: skip-measure-failed -- THE REPAIR DID NOT HAPPEN ... Pin the new sites yourself`. That head left its added sites unpinned. This head pins all of them (`tests/mutation_ledger/killed_by/`, `35985625b`), so both checks are answered here. The cheaper detector is `tools/pr/prepr.sh` step 6d, run before the handoff.
- `tests / replay`: `cycle_cost ... runner class unknown: ref_ms 27.26 lies in no band of COST_RUNNER_CLASSES` (verdict/3232). That is a runner-calibration gap in the instrument and is not caused by this diff. No cheaper detector for this PR exists: it depends on which runner CI draws.
- `governance / delivery-status`: other PRs' OVERDUE rows. It is not a required context and not caused by this diff; no cheaper detector exists here.
- `tests / nightly-status`: reports the nightly's state, not this diff's; no cheaper detector exists here.
- `gate` and `pr-contract / pr-contract`: these aggregate the reds above, plus the re-author body's stale `## Head`. This body is checked by `prepr.sh`'s step 7.
- Code-scanning alerts could not be read from this seat: `prepr.sh` reports `code-scanning/analyses page 1: HTTP 403`. `pr-contract` lists any open alerts.

## Forward-carry

none

## Friction

- arch-score-plant: cost: `tests/arch_score.py` leaves `$RUNNER_TEMP/base` behind (a worktree of its `/tmp/archscore-plant-*` repo), so its next run in the same container fails `fatal: '<RUNNER_TEMP>/base' already exists` and `prepr.sh`'s closures step refuses `failed while being recorded: tests/arch_score.py (exit 1)`; CI's fresh RUNNER_TEMP never sees it, a cloud seat that runs it twice does. Measured here: run 1 rc=0 leaves `base`, run 2 rc=1 on that line, removing it makes run 3 rc=0 (`ALL 279 ARCHITECTURE SCORE CHECKS PASSED`). Carry: dismissed: tooling outside this PR's scope, recorded here for the orchestrator's friction triage
