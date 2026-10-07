The nightly Tests run 37595831734 (schedule, at `be0cb821`, 2026-10-07) failed two jobs because `tests/boost_drift_replay.py` ran past 1576 s:

- `mutation-nightly` (job 112708109605): `MUTATION TABLE INCONCLUSIVE`, `baseline tests/boost_drift_replay.py: rc=124 failed=0 1576s`.
- `mutation-ledger` (job 112708109541): `MUTATION TABLE REFUSED -- the null control custom_components/heatpump_optimizer/climate.py:45 NULL_COMMENT was timed out under tests/boost_drift_replay.py`. That job's baseline finished at 1573 s.

That run's third red job, `record-autofix`, was fixed by #2011 (`f060cb4c`). Its push run 37616617293 shows `record-autofix` green (job 112776379131). This PR does not touch it.

This is round 2. Round 1 was blocked at `e6e9b775` for three reasons: the fork alone did not get the replay under 1576 s; the branch added an `inert_reads` gap; and `check_fork` checked only arithmetic. Each is answered below.

**Cause.** `tests/mutation_table.py`'s `driver_timeout` is `max(--timeout 1200, 3 x seconds)`. Until a run has measured a script's baseline, `seconds` is the script's `recorded` entry in `tests/closures.json`. For this script that entry was 525.3 s, so the limit was 1576 s. `drive_baselines` queues the baseline and the null control together, so both ran under that limit. The 525.3 s was recorded by `82a8791a`, #1935's `--single` run on the fixer's Darwin seat. That machine is roughly three times faster than CI's slow runner class. No later commit made the replay slower. It has been the slowest script on every main push since #1935 merged it (`81071813`, 2026-10-05): 38 runs, 817 to 1756 s each, 2.49 to 2.87 times `features.py` in the same run. GitHub's pool has a fast runner class (about 860 s for this script) and a slow one (about 1700 s). On the slow class the replay reaches or passes the limit.

**The fix has two parts.**

1. **Pay part of the cost back.** The three arms run one code path until the first boosting cycle, day 5 at 07:00 (cycle 254 of 432). That prefix now runs once, and each arm continues from a `copy.deepcopy` of its state. This was predicted to save 38 % from the solve count. CI measured about 10 %: `fast` job 112889727516 ran the forked replay in 1534 s, against about 1700 s before. The CI closures recordings took 1478 s and 1634.2 s. The prediction assumed every solve costs the same, using one day profiled locally. The measurement shows the post-fork cycles cost more per solve. The fork stays: reviewer `r9c-rev-2026` proved it equivalent independently, and it saves real time.
2. **Correct the limit at its root.** `recorded["tests/boost_drift_replay.py"].seconds` changes from the Darwin 525.3 to 1634.2. That is CI's own Linux recording of the forked replay, from closures job 112889923161 (run 37649590113, at `e6e9b775`), `closure-recordings` artifact: `seconds=1634.2, rc=0, how=audithook+sys.modules+strace`. It is the higher of the two CI recordings; job 112864782144 took 1478 s. The limit becomes `max(1200, 3 x 1634.2)` = 4903 s. This replaces a measurement taken on the wrong machine with CI's own. It is not a raise to hide slowness: `TIMEOUT_SCALE` and the 1200 s floor are unchanged. The orchestrator decided this under the owner's mandate. The detector under **Root cause** is what keeps this figure honest from now on.

**Effect on the nightly's total budget.** `mutation-nightly` uses `--budget-minutes 270` with a 330-minute job timeout. The 270-minute deadline admits a mutant only if its estimated sweep fits, and the estimate comes from measured seconds, not from the timeout. So the larger limit admits no extra work. It matters only if a mutant hangs the replay. A replay started at the deadline could then run up to 4903 s, and 270 + 82 = 352 minutes would pass the 330-minute job timeout. Under the old limit the same worst case was 270 + 26 = 296. In the ordinary case the precedent is the 2026-10-06 nightly, which ran this script's baseline at 1627 s (job 112192036397). That job took 09:03:06 to 12:55:11, about 232 minutes, and ended `MUTATION TABLE PASSED (partial: 27 evaluated, 0 timed out, 13 not started for the budget)`. The replay's coverage is not trimmed to fit.

**`inert_reads`.** `tests/harness_headers.py` reads every file in `tools/audit/harnesses/`, and this branch adds two. The dispatched `closures` job 112864782144 failed with `INERT READS UNDER-APPROXIMATED` on `tools/audit/harnesses/boost_replay_fork_parity.py` and `tools/audit/harnesses/ci_script_seconds.py`. Both are now under `inert_reads["tests/harness_headers.py"]`, the same route #2022 took for `eg_b7_seam_hubs.py`. #2015 will move `tools/audit/harnesses/` to `dev/audit/harnesses/`, and these two entries are re-keyed when that lands (by merge, never rebase).

**The fork guard now checks behaviour.** `check_fork` still checks that `fork_cycle()` is the first boosting cycle. It now also drives each surface's arm through `cycle()` itself over the pre-fork cycles, with one real production plan returned for every solve (`_OneSolve`). Each arm's per-cycle trace must equal the surface-free arm's (`prefix_trace`: action, mode, overlay held state, freeze reason, fold counts and scale, the true house, the accuracy record's last sample). An arm-specific action or input planted ahead of the window now fails the guard, which the shared prefix would otherwise erase silently. The check costs one solve.

**Root cause** (`defect-root-cause.md`, red-check trigger; this red reached main's nightly).
- Cause: a 3x timeout scaled from a per-script `seconds` recorded on a machine about three times faster than CI's slow runner class, applied to a script whose CI time already met that limit when it merged.
- Process state: **(d)**. `driver_timeout` (R9-F10.12) assumes `recorded.seconds` describes CI's machine. A Darwin `--single` recording breaks that assumption and nothing notices, because `closures` checks a recording's file set and never its seconds.
- Why no PR check caught a 1576 s replay before the nightly did: the only per-script limit is in the nightly mutation drive, and it uses the recorded figure. `fast` has no per-script limit, and #1935's scoped `mutation` check never drove the replay.
- Cheaper detector: on every main push, compare each script's `fast` seconds with `3 x recorded.seconds` and fail when a script exceeds it. Standing cost: one pass over `run.sh`'s timing table, under a second per run. It would not have fired on #1935's own PR, whose `fast` ran the replay but compared it with nothing. It would not have fired on #1935's own merge push either (`81071813`, a fast runner, 887 s against the 1576 s limit). It would have fired on the next push, `130c7808`, five minutes later, where the replay took 1657 s. That was more than a day before the nightly. Not built here: it changes `tests.yml` or `run.sh`, which is gate policy, and it is owed to a separate `root-cause.md` seat beside this fix (handed to the orchestrator).

## Head

`baa6c237fc4591bb3b57d71310fb93613ed78889`

## Mutation proof

`check_fork` with planted perturbations, on this head's tree, cheap (no replay; one solve per run). Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 -c '<wrap cycle(), plant, then b.check_fork(); raise SystemExit(b.R.close("FORK"))>'`:
- None planted: `ALL 3 FORK PASSED`, rc=0.
- Channel boost entered at cycle 100 on the channel arm (the reviewer's `guard_gap.py` plant): `FAIL the channel surface acts on nothing before the fork ... [first differing cycle 100 of 254]`, rc=1.
- Mode set to boost at cycle 50 on the mode arm: `FAIL the mode surface acts on nothing before the fork ... [first differing cycle 50 of 254]`, rc=1.
- An input perturbation, `draw += 0.5` at cycle 120 on the channel arm: `FAIL the channel surface ... [first differing cycle 120 of 254]`, rc=1.
- `fork_cycle()` plus 1: `FAIL the fork is the first boosting cycle ... [fork=255 first boosting cycle=254]`, and both surface checks fail at `first differing cycle 254 of 255`. rc=1.

The guard's arithmetic half also fails at `fork_cycle()` minus 1 (round 1, unchanged).

## Null control

- With nothing planted, the behavioural guard passes (above). The surface arms' pre-fork traces equal the surface-free arm's over all 254 cycles.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/harnesses/boost_replay_fork_parity.py` at `dca94a6475383dd15e1c72e78420b589ec9f8502`, whose `replay`/`cycle` code this head keeps: `fork: PARITY (fork=1)`, `control: DIFFERS (fork=2)`, `BOOST REPLAY FORK PARITY PASSED`, exit 0. The reviewer's own equivalence harness separately read 5/5 arms EQUAL over the full 9-day schedule with a stub solver, and 3/3 EQUAL with production solves on a 12-cycle schedule (round-1 verdict).

## Figures

- `python3 tools/audit/harnesses/ci_script_seconds.py 2026-10-04 tests/boost_drift_replay.py tests/features.py tests/stress.py`, run 2026-10-07T15:05Z: `rows=73 unreadable=3`. 38 rows carry a replay time, the first `81071813` at 887 s. Over those 38: replay 817 to 1756 s, replay/features 2.49 to 2.87, and the replay was the slowest of the three in 38 of 38. The ratios are worked from the printed rows.
- CI at round 1's code (`dca94a64` / `e6e9b775`), read from the job logs and API: `mutation-nightly` job 112864826007 `baseline tests/boost_drift_replay.py: rc=124 failed=0 1576s`. `fast (3.14)` job 112889727516 `ok python3 tests/boost_drift_replay.py (1534s)`. `closures` job 112864782144 recorded the replay 15:29:18 to 15:53:56 (1478 s). `closures` job 112889923161's `closure-recordings` artifact gives `seconds=1634.2`.
- `driver_timeout(1200, 1634.2)` = 4903, against `driver_timeout(1200, 525.3)` = 1576 at the base.
- Job 112192036397 (2026-10-06 nightly): `2026-10-06T09:03:06Z` to `2026-10-06T12:55:11Z`, from `gh api repos/tvofi/heatpump_optimizer/actions/jobs/112192036397`.
- CI at this head: Tests run 37654541009, dispatched with `gh workflow run tests.yml --ref handoff/r9-nightly-bdr`, runs `mutation-nightly` and `closures` at `baa6c237`. Pending when this body was pushed. CI's result goes here when the jobs complete.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2198 ENTITY CHECKS PASSED`.
- `python3 tests/closure.py no-copies`: `closure: no test file defines a symbol production also defines`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 2 script(s) run, 30 scoped out.` `scope.run` names `tests/boost_drift_replay.py` and `tests/entities.py`. `entities.py` ran locally. The replay is left to CI under the owner's 2026-10-07 rule that heavy scripts run in CI.
- `env -u GIT_AUTHOR_NAME PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, with the seat venv first on PATH: `PRE-PR: baa6c237fc4591bb3b57d71310fb93613ed78889 000000000000000000000000`. Closures at this head is CI's, in run 37654541009.

## Red checks

- `closures`, dispatched run 37642546223 (job 112864782144): `INERT READS UNDER-APPROXIMATED`. Two of the three pairs it named are this branch's new files. Round 1 attributed that red to #2022 and said the diff changed no closure input; both statements were wrong. Fixed in `baa6c237` (above). The third pair, `eg_b7_seam_hubs.py`, was main's and was fixed by #2022. Cheaper detector: `tools/pr/prepr.sh`'s closures step, which records the scoped scripts, not `harness_headers.py`; it did not catch this. The check that would have caught it is a `tests/harness_headers.py` recording with `tests/closure.py check`, a Linux `strace`-only dimension, so none runs on this Mac seat. The cheapest detector is CI's `closures` job itself.
- `mutation-nightly`, same run (job 112864826007): `MUTATION TABLE INCONCLUSIVE`, replay `rc=124 1576s`. This is the defect itself, still present at round 1's head. Answered by the limit correction above. The cheaper detector is the root-cause detector described above.
- `delivery-status` and `nightly-status` grade `main`. This diff touches none of their scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, or any row, so their red is main's (`defect-root-cause.md`, Enforcement).

## Forward-carry

- The detector under **Root cause**: compare `fast` per-script seconds with `3 x recorded.seconds` after a merge. Handed to the orchestrator for a `root-cause.md` seat.
- #2015 (RO-8) moves `tools/audit/harnesses/`. This branch's two new harness files and their `inert_reads` keys move with it. Whichever of #2015 and this PR merges second carries the re-key.

## Friction

- gate-scoping.md: cost: the scope selects the 1500 to 1750 s replay, which under the 2026-10-07 owner rule cannot run locally, so its result at any head is CI's alone.
- fixer.md: cost: round 1's body predicted the fork's saving from a uniform per-solve cost and one profiled day, and stated it as about 1050 s. CI measured 1534 s. A prediction now stays labelled as one until CI measures it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
