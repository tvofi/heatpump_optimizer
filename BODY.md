R10-HOTFIX-SELFTEST-TIMEOUT. `governance / instrument-self-tests` ran its steps in line under `timeout-minutes: 30` and spent most of its wall time in five self-tests: prepr.sh's, beatd.py's, and pr_args.sh's alone and again through open_pr.sh and update_pr.sh, which each run it (open_pr.sh's `--self-test` arm, update_pr.sh's). Only prepr.sh's of the five keeps a core busy; the other four wait. They now start detached in the job's first step, each to its own log and exit-status file, and five steps at the end of the job, under their old names, print each log, fail on its status and grep the same tally lines. The job now lasts as long as the longer of its in-line steps and the detached work, instead of the sum of both. The timeout stays 30: no raise.

The three pr_args.sh callers run one after another in a single detached chain, and prepr.sh's self-test runs at `nice -n 10`. With all five at once, pr_args.sh's `mut:unlock` arm failed once in nine observations: it checks for a lock holder inside the 0.2 s poll the holder takes to notice that its parent has gone, and CPU contention shortens that window. Chained, they keep the order they had in line, and 9 of 9 passed (figures). Nine passes do not rule out a residual rate below about one in nine; that arm's dependence on load is pr_args.sh's, and is carried below.

Alternatives, and why each lost:
- **Matrix shards** of the job would rename its check runs to `governance / instrument-self-tests (<shard>)`. That name is read in tools/pr/ci_predict.py's `JOB` table and by tools/audit/round4/D11/governance_cost.py's `bare()`, and each shard repeats checkout. Separate jobs fail tests/entities.py's census, which ties governance.yml job ids to governance_cost.py's `GOV`, until a file outside this group names them.
- **Dropping the standalone pr_args.sh step** would remove a step, which the null control forbids, and would leave pr_args.sh's tally to two callers outside this file.
- **Cutting prepr.sh's own cost** was not needed for the headroom. It is about 400 CPU-s of work, and the detached run already removes it from the critical path.

`bg_wait` fails a test whose launcher exited with no status, instead of waiting out the timeout. The launcher writes each status through a temporary file and `mv`, so a reader never sees a partial status.

No CI probe run was taken for the head. tools/audit/seat/ci_probe.py pushes and dispatches only `ci-probe/*` refs, a branch write this seat's brief forbids, and `ci.yml` runs on no push but `main`'s. The head's wall time below is a step-by-step replay of the job, and the pull request's first `governance / instrument-self-tests` run is the CI probe.

## Head

Measured at 4611babffa6fbd30e9197cca8eaf07266754e6f4, merged with origin/main 41aa9050fc874f0bc394fba9188f9229fd9cb502. Then merged with origin/main f2a015142714383722bf49d7ab20d8398ec9674c (2026-11-07T02:40Z), whose delta from 41aa9050f is `dev/programme/delivery/*.md` alone (`git diff --name-only 41aa9050f f2a015142`), so no replay or timing figure below moves. The handoff head c8e3e7d0b adds the INERT READS entry `tools/pr/ci_predict.py --apply-inert` wrote to tests/closures.json for the new harness. The gate figures are re-taken there.

## Mutation proof

`python3 dev/audit/harnesses/r10_selftest_timeout.py` reads the `bg_run`/`bg_pid`/`bg_start`/`bg_wait` library out of the launcher step as committed and drives it over planted commands:
- M0, the library as committed: all 8 arms PASS.
- M1, `bg_wait` returning 0 in place of the recorded status: KILLED by `refuse chained bad` and `refuse bad`.
- M2, `bg_wait` returning 0 for a launcher gone with no status: KILLED by `refuse chain killed` and `refuse killed`.
- `RESULT survivors=0`.

A missing tally is refused by the grep each waiter step keeps (arm `refuse notally`).

## Null control

- Each refusal arm has its passing control in the same run (`control ok`, `control tally`, `control chained tally`); a library that refused everything fails them.
- Every one of the job's steps still runs and still greps its `checks, 0 failed` line: the five waiter steps keep the five step names, and their grep lines are byte-identical to the base's.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `118 self-testing, 118 wired, 0 unwired`, so the move dropped no self-test's run line.
- The base workflow replays the same steps in line, which is the before figure.

## Figures

- CI before, main run 42297617709: job 1785 s; prepr 321, beatd 275, PR opener 199, PR argument builder 199, PR updater 198. Main run 42291959742: job 1759 s; 332, 274, 194, 194, 194. Seconds are completedAt minus startedAt: `gh run view 42297617709 --json jobs --jq '.jobs[]|select(.name=="governance / instrument-self-tests")|.steps[]|[.name,.startedAt,.completedAt]|@tsv'`.
- The five self-tests one after another, locally: 475, 280, 223, 223, 224 s wall (sum 1424). All five at once: 478 s, every tally `0 failed`. Each was timed with bash `time` around its command, e.g. `time bash tools/pr/prepr.sh --self-test`. Serial CPU time (user+sys) was 467 s for prepr.sh and 50, 83, 82, 83 s for the other four.
- Job replay, base: `python3 dev/audit/harnesses/r10_selftest_timeout.py replay <(git show 41aa9050f:.github/workflows/governance.yml) all` gives `RESULT replay_seconds=1870 failed=0`. An earlier base replay on the same container, under a 1800 s background bound, was stopped inside the beatd step.
- Job replay, head: `python3 dev/audit/harnesses/r10_selftest_timeout.py replay .github/workflows/governance.yml all` gives `replay_seconds=737`, `744` and `702`, `failed=0` each, with the five waiter steps at 0.0 s each. The detached work ended before the in-line steps did, so the in-line steps are now the critical path.
- Projected CI wall time, not measured: base CI over base replay is 1785/1870, and applied to the slowest head replay (744 s) it gives about 710 s, 61% under the 1800 s timeout. The pull request's first run measures it.
- `mut:unlock` (pr_args.sh's check `mutant mut:unlock (its line deleted): the holder is still alive when the run returns`), all five at once: 1 FAIL in 9 observations. These are the three runs in the concurrency timing above, three in a launcher-and-waiters replay (`replay .github/workflows/governance.yml bg`), and three in a full head replay before the chain; the FAIL is `pr_args self-test: 174 checks, 1 failed` in update_pr.sh's log. Chained, at the head: 9 of 9 PASS, over the three head replays above, each running it three times.
- Scoped gate at c8e3e7d0b: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run`, tests/entities.py and tests/harness_headers.py. Both passed, as did run_always's env_drift `--claims-only`, `closure.py selftest` and `layout.py`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- pr_args.sh's `mut:unlock` arm passes only while its checker runs `kill -0` within the lock holder's 0.2 s parent poll, so CPU load can turn it red. Measured above: 1 in 9 with all five self-tests at once, 9 of 9 chained. This PR restores the load that arm passed under in line, and states the constraint at its site, the launcher step's comment in governance.yml, which every seat editing this job reads. A deterministic arm belongs to pr_args.sh, outside this group's owned file. Carry: dismissed: recorded at the launcher step's comment; a deterministic arm is pr_args.sh's

## Friction

- fixer.md-step-3: unenforced: a CI-time claim owes before and after on a probe run, but a fixer seat has no probe path: ci_probe.py takes only `ci-probe/*` refs, this seat may write no other branch, and `ci.yml` runs on no push but main's. The head figure is a replay, and the PR's first run is the probe. Carry: dismissed: the pull request's own first run is the probe
