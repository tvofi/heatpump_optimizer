Main went red at f3ffb1c63: `tests / ci-ratchet` (CI job 121295715608, run 40230380300) printed `GREW critical_path_minutes: 59.583 (budget 54.825)`, and `gate` failed on it. Every other metric was ok.

**Cause: runner queue, not work. No merge grew the tests critical path.** The metric was the median wall of the last 8 push runs: from run creation to the last `tests / *` job's end. That wall counts the time a job waits for a runner. Under the overlapping merge train, three or four pushes to main land within two minutes (19:16 to 19:18Z, 20:18 to 20:21Z) and share the account's runner pool. Run 40225415246 created its heavy lanes at +0.5 min, and they started at +17.9 to +24.8 min. The lanes themselves took the usual ~30 to 32 min, so a 32.1-minute critical path read as a 59.7-minute wall. Run da12aa37d, which waited for nothing, read 34.2 wall and 33.8 work. In every one of the 40 most recent CI push runs on main, the work is flat at 20.1 to 34.65 min. Over the same runs the wall ranges from 20.6 to 91.8 min. This is state (b) of the brief: the metric was not stable, and widening the budget would not fix it.

**Fix (an instrument fix).** `run_minutes` in `tests/ci_ratchet.py` now replays each run's jobs with the queue taken out:

- The API creates a job when its last need finishes, so `created_at` is the job's ready time. `started_at - created_at` is its queue, and `completed_at - started_at` is its work.
- A job's zero-queue end is its work plus the zero-queue end of the job that finished last at its ready time. This is `ci_critpath.py`'s walk-back rule (follow the need that ended last).
- The metric is the latest zero-queue end among the run's `tests / *` jobs.
- A run with a cancelled counted job leaves the window, because its work was cut short.

Grading stays the median of the 8-run window. `--record` now writes the p90. `--gather-runs FILE --window N` lets a record read a wider window. The module docstring once claimed a p75 headroom that the code never applied. The docstring now states what the code does.

**Re-record (deliberate, CLAUDE.md rule 2; a lowering, not a raise):** `critical_path_minutes` 54.825 -> 34.267. The new value is the p90 of `--gather-runs --window 40` taken at main f3ffb1c63, under the new definition. The old row was a 2026-10-12 median of walls. Kept, it would hide about 22 minutes of growth in real work. No other row moves. The archscore rows already read lower than their budgets at this tree; re-recording them is not this fix's job.

**Root cause (defect-root-cause.md).** Process state **(d)**: the measurement was sound while pushes to main ran one at a time. Its precondition changed when the train began landing overlapping batches (`--overlap`), and contention entered the wall. Cheaper detector: no check could have read this on a pull request. The metric is defined over main's own push runs, which exist only after the merges. The countermeasure is in this diff: self-test checks that pin queue insensitivity. They run offline in seconds in the same job, against a queued fixture taken from run 40225415246 and a null-control fixture with no queue.

## Head

c8c77b82e

## Mutation proof

Each mutant was applied to `tests/ci_ratchet.py` and then `python3 -I tests/ci_ratchet.py --self-test` was run, with a restore after each. The baseline reads `38 checks, 0 failed`.

- M1, work measured from `created_at` (queue counted as work): 5 FAIL, including `a run whose lanes queued for runners reads its work, not its wall` and `the same work with no queue reads the same 32.1, its wall (the null control)`
- M2, `base = 0.0` (needs ignored): 5 FAIL, the same two plus `a slower job on the critical path still grows the metric`
- M3, cancelled run kept: 1 FAIL, `a run with a cancelled tests / * job is not in the window`
- M4, record at median: 1 FAIL, `derive grades the median and a --record derive writes the p90`
- M5, p90 replaced by max: 2 FAIL, `the grade is the window's median, a record its p90 ...` and the derive check
- M7, jobs gathered on CI runs only: 1 FAIL, `--gather-runs keeps the newest 8 push runs ... jobs on every run`
- M8, the earliest need instead of the latest: 5 FAIL
- M9, the last job instead of the max: 4 FAIL
- M10, `--window` parsed and ignored (CLI argv wiring only): **survives**. No self-test drives `main()`'s argv path into a live `gh`. It was exercised by hand: `--gather-runs FILE --window 40` printed `push runs: 40 (40 CI)`.

Failing test first: the three queue, slow-job and cancelled checks went red on the unmodified `run_minutes` (`got 59.7`, `got 69.7`, `got 59.0`). The p90 check raised a TypeError on the old signature.

## Null control

On the unmodified tree, `critical_path_minutes` over the live 8-run window reads 59.642, which reproduces the red against 54.825. At the head it reads 32.5. For a run with no runner wait, wall and work agree: in run da12aa37d the wall is 34.2 and the work 33.8, and the self-test's no-queue fixture reads 32.1 under both. Had the metric still read queue, the queued fixture would read 59.7, which M1 shows.

## Figures

- Base (wall) and head (work) median, plus head p90, over the same live windows taken at main f3ffb1c63 on 2026-10-25 (UTC): `python3 -I tests/ci_ratchet.py --gather-runs w8.json`, `--gather-runs w40.json --window 40`, then `critical_path_minutes` from `git show origin/main:tests/ci_ratchet.py` and from the head. w8: base 59.642, head 32.5, p90 33.5. w40: base 34.592, head 32.55, p90 34.267. These are sliding-window figures and go stale as main moves; the rule is the instrument's.
- Work range 20.1 to 34.65 and wall range 20.6 to 91.8 over the 40 runs: the same w40 file, `run_minutes` at the head, and job created/started/completed from the jobs API.
- Self-test: `python3 -I tests/ci_ratchet.py --self-test` prints `38 checks, 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run` (tests/entities.py).

## Red checks

`tests / ci-ratchet` on main (job 121295715608): answered above. No cheaper detector exists, because the metric reads main's own push runs, which exist only after the merges. The countermeasure is the queue-insensitivity self-test checks in this diff.

## Forward-carry

- `.github/workflows/tests.yml`, the comment above the "Fetch the recent push runs' durations" step, still says the critical path is "a CI run's span to its last `tests / *` job". It should say "a run's work to its last `tests / *` job with runner queue removed (see tests/ci_ratchet.py run_minutes)". It is left out of this hotfix on purpose, because a tests.yml edit forces MODE: FULL. It rides the next live group whose files already include tests.yml. Carry: R10-FLOW-RECORD-PITCH

## Friction

none
