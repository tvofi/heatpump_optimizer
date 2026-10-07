The nightly Tests run 37595831734 (schedule, at `be0cb821`, 2026-10-07) went red in two jobs because `tests/boost_drift_replay.py` ran past 1576 s:

- `mutation-nightly` (job 112708109605): `MUTATION TABLE INCONCLUSIVE`, `baseline tests/boost_drift_replay.py: rc=124 failed=0 1576s`.
- `mutation-ledger` (job 112708109541): `MUTATION TABLE REFUSED -- the null control custom_components/heatpump_optimizer/climate.py:45 NULL_COMMENT was timed out under tests/boost_drift_replay.py`. In that job the baseline itself finished at 1573 s.

The run's third red job, `record-autofix`, was fixed by #2011 (merge `f060cb4c`). That push's run, 37616617293, has `record-autofix` green (job 112776379131). This PR does not touch it.

**Cause.** The timeout is `driver_timeout` in `tests/mutation_table.py`: `max(--timeout 1200, 3 x seconds)`. The seconds come from `tests/closures.json`'s `recorded` entry until the baseline in the same run has measured the script. For this script the entry is 525.3 s, so the limit is 1576 s. The baseline and the null control are queued together (`drive_baselines`), so both run under that limit. The replay was not slowed by a later commit. It has been the suite's slowest script on every main push since #1935 merged it (`81071813`, 2026-10-05). Across 38 such runs it took 817 to 1756 s, between 2.49x and 2.87x `features.py` and between 3.74x and 4.33x `stress.py` in the same run. GitHub's pool has a fast runner class (about 860 s for this script) and a slow one (about 1700 s). On the slow class the script meets or passes 1576 s. The 525.3 s in `closures.json` was recorded by `82a8791a` (#1935's `--single` on the fixer's Darwin seat). That is roughly a third of what the slow class takes. Nothing re-records `seconds` on Linux unless a closure is UNDER-SCOPED. The 2026-10-06 nightly passed because its replay baseline ran on the fast class (`mutation-ledger` job 112192036224, 770 s).

**Fix: pay the cost back.** A profile of one day of one arm (run before the owner's CI-only rule for heavy scripts) put 258.8 of 259.7 profiled seconds in `HeatPumpOptimizer.optimize`, 48 calls. Each cycle is one full production multi-start solve, and the script runs three arms for nine days of 48 cycles. The three arms run the same code path until the first boosting cycle, day 5 at 07:00. Before that, the channel surface is entered only on a boosting cycle, and the mode select is driven only when the mode it wants differs from auto. So the prefix now runs once. Each arm continues from a `copy.deepcopy` of that state (`replay`, with the fork at `fork_cycle()`). With `fork_cycle()` = 254 of 432 cycles, that takes the solves from 1296 to 432 + 2 x 178 = 788. `check_fork` checks in the gate that the fork is exactly the first boosting cycle. `tools/audit/harnesses/boost_replay_fork_parity.py` checks that the shared replay equals the unshared one. Its null control breaks the precondition and must read DIFFERS.

**Why not the timeout.** `TIMEOUT_SCALE` and the 1200 s floor were left alone. Raising either would cover a 29-minute script on every PR whose closure reaches the coordinator, not fix it. Re-recording `seconds` on Linux would move the limit to about 5100 s on the slow class, but the script would still cost the same. The alternatives that were dropped: fewer days or a coarser solve step change what the checks measure. Running the arms in parallel processes saves no CPU and contends with `run.sh`'s and the mutation runner's own workers. The expected limit after this change is under `## Figures`, and the CI measurement at this head is there once it lands.

**Root cause** (`defect-root-cause.md`, red-check trigger; this red reached main's nightly).
- Cause: a 3x timeout scaled from a per-script `seconds` recorded on a machine roughly 3x faster than CI's slow runner class, applied to a script whose CI time already reached that limit when it merged.
- Process state: **(d)**. `driver_timeout` (R9-F10.12) assumes `recorded.seconds` describes CI's machine. A Darwin `--single` recording breaks that, and nothing notices. The replay's own PR ran it in `fast` and passed, because `fast` has no per-script time limit. Its `mutation` check scopes to changed sites, and the replay was not one of their drivers on that PR. So no PR check runs the replay under the nightly's limit.
- Why no PR check caught a 1576 s replay before the nightly did: the only check with a per-script limit is the nightly mutation drive, and it uses a recorded figure no PR check compares with CI's real time. `fast` prints the 1700 s (`ci_script_seconds.py` reads it from every main run) but does not compare it with anything.
- Cheaper detector: compare each script's `fast` seconds on the main push with `3 x recorded.seconds`, and fail the post-merge run, not the next nightly, when a script exceeds it. Standing cost: one pass over `run.sh`'s timing table, under a second per main run. The countermeasure is not built in this PR. It changes `tests.yml` or `run.sh`, which is gate policy, and it belongs in a separate `root-cause.md` seat beside this fix (`defect-root-cause.md` "What is owed" 2). The finding goes to the orchestrator in this handoff's report.

## Head

`dca94a6475383dd15e1c72e78420b589ec9f8502`

## Mutation proof

The fix's precondition is `fork_cycle()`, the first cycle any surface acts on. Each mutation below was applied with a monkeypatch of `fork_cycle` and `check_fork()` was run alone (no solve). Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 -c 'import boost_drift_replay as b; f=b.fork_cycle; b.fork_cycle=lambda: f()+D; b.check_fork(); raise SystemExit(b.R.close("FORK"))'`, run at this head:
- D=+1: `FAIL the arms share exactly the cycles before the first boosting one ... [fork=255 first boosting cycle=254]`, `1 of 1 FORK FAILED`, rc=1.
- D=-1: the same FAIL with `[fork=253 first boosting cycle=254]`, rc=1.
- D=0: `ALL 1 FORK PASSED`, rc=0.

The parity harness's null control is the behavioural form of the D=+1 mutant. It forces the fork one cycle past the first boosting cycle, and the channel and mode arms then differ from the unshared replay (`## Null control`).

## Null control

`PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/harnesses/boost_replay_fork_parity.py` replays 8 half-hour cycles, with one window opening at 00:30. It runs each way: `fork=0` (every arm from its own fresh state) against the default fork. At `dca94a6475383dd15e1c72e78420b589ec9f8502` (this head) it printed, exit 0:
- `fork: PARITY (fork=1)`, with all three arms `equal` (`channel_boost` and `mode_boost` `tagged=4`, `null_no_boost` `tagged=0`).
- `control: DIFFERS (fork=2)`, with `channel_boost` and `mode_boost` `DIFFERENT` and `null_no_boost` `equal`, which is correct because the null arm has no surface to lose.
- `BOOST REPLAY FORK PARITY PASSED`.

The comparison covers each arm's daily scale rows, fold counts, final scale and every accuracy sample's `as_dict()`.

## Figures

- `python3 tools/audit/harnesses/ci_script_seconds.py 2026-10-04 tests/boost_drift_replay.py tests/features.py tests/stress.py`, run 2026-10-07T15:05Z, printed `rows=73 unreadable=3`. 38 of the rows carry a replay time. The first is `81071813`, the #1935 merge, at 887 s. 35 rows read `none` because they are older than the script. The 3 unreadable runs are `077f53af`, `50e1f116` and `b52adb67`. Over the 38 rows: replay 817 to 1756 s; replay/features 2.49 to 2.87; replay/stress 3.74 to 4.33. In 0 of 38 runs was the replay not the slowest of the three. The ratios are worked from the printed rows, and the range has no step after `81071813`. That is the no-regression finding: no commit after the merge moved the replay's time.
- `git show origin/main:tests/closures.json`, `recorded["tests/boost_drift_replay.py"]`: `{'seconds': 525.3, 'rc': 0}`, last changed by `82a8791a`. `driver_timeout(1200, 525.3)` = 1576.
- Mutation-runner logs, read with `gh run view --job <id> --log`: run 37595831734 `mutation-nightly` baseline `rc=124 1576s`, `features.py` `750s`. `mutation-ledger` baseline `rc=0 1573s`, null control timed out. 2026-10-06 run 37440269774: `mutation-ledger` baseline `770s` (fast class), `mutation-nightly` baseline `1627s`.
- Expected effect: the solves go from 1296 to 788 (`fork_cycle()` = 254 of 432 cycles per arm). That predicts about 1050 s on the slow class, against the unchanged 1576 s limit, and about 530 s on the fast class. This is a prediction, and CI measures it below.
- CI at this head: Tests run 37642546223 was dispatched with `gh workflow run tests.yml --ref handoff/r9-nightly-bdr`. It runs `mutation-nightly` (job 112864826007) on this head. `mutation-ledger` runs only on `main` and is skipped there, and `fast` is skipped on a dispatch. CI's result: pending when this body was pushed. The replay's `baseline` line from that job is added to this body when the job completes.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `env -u GIT_AUTHOR_NAME PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, with the seat venv first on PATH: `PRE-PR: dca94a6475383dd15e1c72e78420b589ec9f8502 000000000000000000000000`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 1 script(s) run, 31 scoped out.` `scope.run` names `tests/boost_drift_replay.py`. Under the owner's rule that heavy scripts run in CI (2026-10-07), it was left to CI's `fast` and is not run locally.
- `python3 tests/closure.py no-copies`: `closure: no test file defines a symbol production also defines`. The helper was renamed `arm_summary` because production has `summary` methods.

## Red checks

`delivery-status` and `nightly-status` grade `main`. This diff touches neither their scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, nor any row, so their red belongs to main (`defect-root-cause.md`, Enforcement). `nightly-status` is red on main because of the nightly run this PR fixes. A green nightly after the merge clears it. Closures: any `closures` red inherited from main is #2022's, which is fixing it. This diff changes no closure input: the script reads the same modules, and `tools/audit/` is INERT. `tools/pr/prepr.sh`'s closures step recorded the scoped script locally and refused with an empty detail line: `closure.py check` failed without printing an `UNDER-SCOPED` or `NOT A FILE` line for the step to show. That recording was a local run of the heavy replay, against the owner's CI-only rule, and it is not repeated. The PRE-PR line in `## Figures` comes from `PREPR_SKIP_CLOSURES=1`, so closures at this head is CI's `closures` job in run 37642546223 (job 112864782144).

## Forward-carry

The countermeasure in the description, comparing `fast` per-script seconds with `3 x recorded.seconds` after the merge, is handed to the orchestrator in this handoff's report for a `root-cause.md` seat. No later stage's brief needs to change to land this fix.

## Friction

gate-scoping.md: cost: `MODE: SCOPED` selects one script for this diff, the 860 to 1756 s replay. Under the 2026-10-07 owner rule it cannot run locally, so its pass at this head is CI's alone.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
