Part of #3885 (L3, the measurement); closes nothing, since other parts of #3885 remain open.

The prelude now prints one machine-readable line on every exit after the argument check, to the job log (stderr, because stdout is `GITHUB_OUTPUT`) and to `GITHUB_STEP_SUMMARY`:

    PRELUDE-TIMING {"outcome":"defer","attempt":2,"wall_s":..,"api_s":..,"api_calls":..,"sleep_s":..,"naps":[[path,s],..],"local_s":..,"defer":[40,41]}

- `api_s` / `api_calls`: wall time inside GitHub GETs (`ghapi.Meter`, which times each transport attempt).
- `sleep_s` / `naps`: time in `RETRY_5XX` backoffs, each nap with the API path that caused it. Since W1 (#3935) this is the only sleeping the prelude does.
- `local_s`: what is left of `wall_s` (git, shards, codeql_scope).
- `defer`: the run ids a deferral waits on. A deferral holds no runner. The wait it starts is the gap between this `attempt` and attempt + 1, which the sweep starts.

Decisions do not change. `outputs`, `busy_sources`, same-head binding, rerun-attempt reads, the cycle rules and fail-closed API/rate-limit handling are untouched: `main` hands `outputs` a metered `get` with the same signature, and exit codes and stdout are the same. If the summary file cannot be written, a `NOTE` is printed and the job does not fail.

Alternatives and why each lost (fixer step 17):
- Timing a wrapper around `get` inside prelude alone. The backoffs happen inside `ghapi.get`, so the wrapper cannot separate sleep from API time. The owner of the backoff, `ghapi`, does the accounting.
- A module-level counter in `ghapi`. That is hidden process state, shared by every caller. A `Meter` object passed in is explicit, and each caller gets its own.
- Measuring the length of the deferred wait on attempt N+1 by reading attempt N's record. That costs an extra GET in a path that fails closed, to measure a wait that holds no runner. Printing `attempt` and `defer` lets anyone reading the log join the two attempts off-runner.

No `.github/` change was needed: the step's stderr is already in the job log, and Actions sets `GITHUB_STEP_SUMMARY` for every step.

## Head

8aace38e81fd60959c68863292714b3cecbc1101, measured on origin/main ac9045c223721608e684c8a2213831aa34c1fa4f at 2026-11-28 16:00 UTC.

## Mutation proof

Each mutant was applied alone to the head and the file's own `--self-test` was run, then restored (scratch driver `mut.py`). Every mutant was killed:

- `ghapi.get`: drop `meter.slept(path, clock() - t0)` -> `FAIL Meter: two attempts' transport time is API time, the backoff is sleep`
- `ghapi.get`: drop `meter.api_s += clock() - t0` -> that check, plus `FAIL Meter: an answer at once sleeps nothing (null control)`
- `Meter.__call__`: drop `self.api_s += self.clock() - t0` -> `FAIL Meter: an injected get's whole call is API time`
- `prelude.main`: pass the raw `get` to `outputs`, not the `meter` -> `FAIL L3: ... its GET time is API time, apart from local work and sleep`
- `prelude.main`: drop the `report(...)` call -> `FAIL L3: a deferring prelude prints ONE timing line` (and the two checks after it)
- `prelude.report`: drop the summary `fh.write` -> `FAIL L3: ... and the same line is in the step summary`
- `prelude.timing`: `"defer": []` -> `FAIL L3: ... naming the runs it deferred to, its attempt and outcome`
- `prelude.main`: outcome always `ok` -> the same check
- `prelude.main`: drop `outcome = "rate-limited"` -> `FAIL L3: a rate-limited prelude still reports, as rate-limited`

Diff mutants: `tools/audit/seat/mutant_run.py --diff ac9045c22372...HEAD --cmd "bash -c 'python3 -I tools/ci/ghapi.py --self-test && python3 -I tools/ci/prelude.py --self-test'" --max-mutants 40 --report-only --in-place`. The first run left two production survivors, `ghapi.py` `t0 = clock() if clock else 0.0` CONST_SWAP. That constant was dead (it is read only when metered), so it was removed (`t0 = clock and clock()`). The rerun at the head leaves no survivor on a production line. The four that remain are all on self-test lines in `ghapi.self_test`, and none of them is killable:
- `t = [0.0]` -> `1.0`: equivalent, because the meter reads clock differences only.
- `iter([502, 200])` -> `503`: equivalent, because every 5xx is retried alike (RETRY_5XX).
- CALL_DEL of the check `Meter: an answer at once sleeps nothing (null control)`, and CALL_DEL of the check `Meter: an injected get's whole call is API time`: deleting a check cannot be caught by a check. The production lines those checks guard are the hand mutants above, and both were killed.

## Null control

- `Meter: an answer at once sleeps nothing (null control)`: a 200 on the first attempt gives `sleep_s` 0.0 and no naps. Read with the 502-then-200 check, this means sleep is counted only when a backoff runs.
- `L3 null: a prelude deferring to nothing names no run`: `defer` is `[]` and `outcome` is `ok`, against `[40, 41]` / `defer` over the same busy fake.
- The existing `rate limit fails closed` check still passes. Rate limits exit 3, and stderr's first token is still `RATE-LIMITED`.

## Figures

- `python3 -I tools/ci/ghapi.py --self-test`: `ghapi self-test: 36 checks, 0 failed`
- `python3 -I tools/ci/prelude.py --self-test`: `prelude self-test: 168 checks, 0 failed`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. It measures `custom_components/heatpump_optimizer/` only (its `PACKAGE_DIR`), and this diff touches nothing there, so no payment is owed and no budget file changes.
- `python3 tools/audit/archscore/score.py --diff ac9045c223721608e684c8a2213831aa34c1fa4f HEAD` (at 59c100b6, before the dead-constant removal): `Architecture score: dS +0.0000 NULL`
- `python3 tests/closure.py select --diff ac9045c223721608e684c8a2213831aa34c1fa4f`: `MODE: FULL` (`tools/ci/ghapi.py changes the gate itself`). The full suite is CI's. Run locally: `tests/layout.py`, `tests/harness_headers.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only` (all rc 0), and `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2794 ENTITY CHECKS PASSED` (at 59c100b6; the later commit changes only `ghapi.get`'s meter arm and one self-test argument).

## Unpinned sites

- `tools/ci/ghapi.py:355 CONST_SWAP`: on a self-test line, and equivalent, because the meter reads clock differences only.
- `tools/ci/ghapi.py:356 CONST_SWAP`: on a self-test line, and equivalent, because every 5xx retries alike (RETRY_5XX).
- `tools/ci/ghapi.py:367 CALL_DEL`: the deleted call is the check itself (`Meter: an answer at once sleeps nothing (null control)`). The production line it guards is killed by the hand mutant on `meter.api_s`.
- `tools/ci/ghapi.py:370 CALL_DEL`: the deleted call is the check itself (`Meter: an injected get's whole call is API time`). The production line it guards is killed by the hand mutant on `Meter.__call__`.

## Red checks

none

## Forward-carry

none

## Friction

none
