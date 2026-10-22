R10-CI-LAYOUT-P2 sub-PR P2a, unit U0b (Part of #2495): the sweep, `tools/ci/sweep.py`, and its probe driver, `tools/audit/seat/sweep_driver.py`. Offline; no GitHub write, no live call.

## Head

`65514d9977ffdd9cdd62389672bdabf5c06e8e01` on `handoff/r10-ci-layout-p2a-u0b`, cut from `origin/main` `738d950aa981` (two commits, no roster merge).

## Unit

U0b. Files, `git diff --stat origin/main...HEAD`: 8 files, +756.
- Production: `tools/ci/sweep.py` 167, `tools/audit/seat/sweep_driver.py` 150 (317 lines, inside the ~400 bound).
- Tests and harness: `tools/ci/sweep_selftest.py` 131, `tools/audit/seat/sweep_driver_selftest.py` 126, `dev/audit/harnesses/r10_sweep_driver_arm.py` 144.
- Wiring and records: the `INSTRUMENTS.md` row, three `sweep_driver-N` mutants in `r10_seat_selftests_mutants.py`, two `tests/closure.py` lines (`GATE_FILES`: `sweep.py`, `sweep_selftest.py`), three `inert_reads` entries in `tests/closures.json` (written by `ci_predict.py --apply-inert`).
- Not touched: `gate.py`, `ghapi.py`, `governance.yml`, `tests/entities.py`, `VERSION`.

## Interface

- `sweep.main(argv, get, post, out=print, sleep=time.sleep, clock=time.monotonic) -> int`. `argv` is `["--run", id]` (plus `--repo`, else `GITHUB_REPOSITORY`). `get(path, params=None)` and `post(path, body=None)` return `(status, headers, json)` as contract item 1 says; paths are `repos/<repo>/...` as ghapi takes them. Returns 0 done or skipped, 1 on `RATE-LIMITED`, 2 on usage.
- `RateLimited`: a local shim with `reset_epoch`. A raised exception is recognised **by class name**, so ghapi's real `RateLimited` propagates through unchanged and the integration seat needs no swap. Outcome words are first tokens: `SWEEP ...`, `SKIP ...`, `SWEEP-DONE`, `RATE-LIMITED reset_epoch=N`, `FAIL usage`.
- U0a's argparse needs only `sweep.main(argv, get, post)`; the keyword arguments exist for the self-test.
- `sweep_driver.py --repo O/R --pr N --nochain|--chain [--gate <tree>/tools/ci/gate.py] [--poll 60] [--idle 900]`, `--self-test`. It only reads (`gh api -i <path>`, no method or field flag); the child's re-runs are the only writes.
- Decisions: `covers_newest` (V's gate green, completed, started after every run at the head was created), `must_rerun` (completed, not success, attempt < 44 so a re-run never reaches 45), `pollable` (queued, waiting, pending, requested, in_progress: N5-4).
- Poll: 60 s floor (`--poll` under 60 is refused), one runs listing per poll, 600 s bound, each run re-run at most once, stops when the PR head moves or V's gate is re-judged.
- Driver, per N5-1: for each run, each attempt up to `run_attempt` not yet swept is read through `actions/runs/<id>/attempts/<n>`; a completed one starts a concurrent child (`--nochain`: attempt 1 only); `superseded=1` is logged for one first seen already replaced; one log line per sweep; `/rate_limit` is read before each poll; back-off below 20 % remaining or on a 403/429; idle exit at 900 s with every run completed and no child alive.
- Design choices to confirm in review: a red `gate` in a run that is itself still running is left with a notice and not polled (the design polls only gate attempts that are not completed); `POLL`-time ordering of `created_at`/`started_at` strings is ISO-8601 so string comparison is time comparison.

## Controls

Environment: venv-ci python 3.14.7; the PATH default python was 3.11 and could not parse `tests/entities.py`.

Self-tests, each printing the contract's line:
- `python3 -I tools/ci/sweep.py --self-test` -> `sweep self-test: 21 checks, 0 failed`.
- `python3 -I tools/audit/seat/sweep_driver.py --self-test` -> `sweep_driver self-test: 15 checks, 0 failed`.

Plants the brief names, each paired with its null in the same self-test:
- a triggering run is never re-run: V with a red gate re-runs nothing (`SKIP`); the null is the same older red gate, re-run once V's gate is green.
- a green run is never re-run: a green older run's gate is never posted to.
- attempt 46 is refused (and 44; attempt 43 is re-run, the cap's null).
- a superseded attempt is logged: `superseded=1` on 2 attempts under `--chain`, 1 under `--nochain`.
- a stubbed 403: the driver starts no sweep; null: the same completion without the 403 IS swept. A `RateLimited` from `get` or from `post` prints `RATE-LIMITED`, exits 1, re-runs 0; null: the ordinary red IS re-run.
- polls: sleeps all >= 60 s, one listing per poll (4 listings for 3 sleeps, the first being the pre-poll read), the bound ends at 10 polls and at most 600 s.

Mutation proof, `python3 /tmp/w/mut/run.py` (scratchpad, one exact replacement each, restored; run with `PYTHONDONTWRITEBYTECODE=1` because a same-size mutant shared a stale `.pyc`, which showed up as two false survivors at first): 13 of 13 killed.
- sweep.py: cap `ATTEMPT_CAP - 1` -> `+ 5` (cap 44/46 checks); green `!=` -> `==` (null and cap checks); floor 60 -> 1 (poll checks); RateLimited recogniser -> False (crash, rc 1); `queued` dropped from the status set (the queued check); `live()` dropped from the poll (the moved-head check); `max` -> `min` in covers_newest (the not-covering check).
- sweep_driver.py: `--nochain` condition inverted; superseded flag forced False; 403 dropped from the back-off; LOW_FRACTION 0.20 -> 0.0; idle `>= self.idle` -> `>= 0`; poll floor check -> `< 0`.
- Equivalent mutant, stated: `r["id"] < v["id"]` -> `<=` is not killable, because the triggering run's gate is green by the entry guard, so `judge` returns before any re-run; two guards, one effect.
- The three `sweep_driver-N` ids in `r10_seat_selftests_mutants.py` kill only once the glue adds the `sweep_driver.py --self-test` step to `instrument-self-tests`; until then `step_for` has no step to run, and that harness is not wired into CI.

Oracle re-score, `python3 -I dev/audit/harnesses/r10_sweep_driver_arm.py` (`gate_sim.py` and `gate_model.py` read with `git show 1371a0a6:measure/rev/...`, the sweep's decisions replaced by `sweep.covers_newest`, `must_rerun`, `pollable`), rc 0:
- poll 5 s (the oracle's own): every one of the 16 latency x arm rows (20, 35, 65, 125 s; both arms) reads END-BAD 0, most attempts 41, 41, 35, 29, 22, 22, 22, 22, identical to `driver_arm.txt` row for row; no row past the window or the cap.
- poll 60 s (the floor): the same 16 rows, END-BAD 0, same attempt figures.
- null, the driver not running (`sweep` ablation): every-suite agrees on 16 of 34 in both arms, newest-created and newest-completed on 34 of 34.
- harness mutation: with `must_rerun` forced False the same command reads END-BAD 18 on every row, rc 1 (`/tmp/w/arm_mut2.txt`).

Ratchet and checks run: `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`; `python3 tests/throwaway_git.py --check` 0 refused; `tmp_paths.py --check` 0 refused; `ref_privacy.py --check` 0 refused (no push site added); `ci_predict.py --base origin/main` -> no closures or fast red predicted; `tests/harness_headers.py`: 56 of 109 fail on this container and 56 of 109 fail at `origin/main` (the baseline run), my one new seam (`parents[3]` in the arm harness) was fixed to the canonical `repo_root`, so the diff adds none. `selftest_wiring.py --check` reads 79 self-testing, 77 wired, **2 unwired**: `sweep.py` and `sweep_driver.py`; wiring is the glue's step, which this seat may not write.
- Scoped gate: the `tests/closure.py` edit makes the mode `MODE: FULL` (it changes the gate), so CI owns the suite; run here: the checks above and `tests/entities.py`. PREPR_SKIP_CLOSURES=1.
- `tests/entities.py` (venv-ci python, `PYTHONPATH=tests/hastub`): the check this unit owed, `every tracked file is either measured or deliberately classified`, reads `ok` (it failed with `tools/ci/sweep.py, tools/ci/sweep_selftest.py` before the two `closure.py` lines). The run had not printed its final return code when I stopped it, so I report no overall rc; of its 46 `FAIL` lines (hastub census plants such as `hb:*`, `a3:*`, `a8:*`, `a9:*`) none names a U0b file. I did not run `origin/main` through it for a baseline.

## Red checks

- `nightly-status`: not measured by this seat. U0b is offline and was told to spare the GitHub API, so nothing here reads main's ancestry. Answer owed by the integration seat from the live check list; this unit touches no file the nightly reads.
- No other check red on main's ancestry was read by this seat: none.

## Forward-carry

- Glue: add `python3 -I tools/ci/sweep.py --self-test` and `python3 -I tools/audit/seat/sweep_driver.py --self-test` as `instrument-self-tests` steps (`selftest_wiring.py --check` is 2 unwired until then, and the `sweep_driver-N` mutants need the second step). Carry: P2a glue.
- U0a's `tools/ci/` `GATE_FILES` prefix replaces my two per-file `closure.py` lines. Carry: P2a glue.
- P2b: the live status values seen (M-6) and whether a job-token re-run's completion fires `workflow_run`; `actions/runs/<id>/attempts/<n>` is assumed to return `status`, `conclusion` and `updated_at` as the run object does. Carry: P2b.

## Friction

`none`
