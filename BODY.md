The replay lane's `cpu_ratio` cap, 2.332 since #2212, is off-centre in its band. #2212 centred it on five nightlies projected by its own factor (0.671). R10-RCA-2205 (#2215) re-measured the solve-memo window at 0.656x and pointed out that the cap should be centred on every timed slow lane, not five. Re-derived here from the logs: projected by 0.656, all 36 pre-memo timed slow lanes read 1.256-1.853. The two post-memo runs measured 1.8804 (the 10-14 nightly) and **1.3908** (dispatch 38656447153 on main at 1005e27a6, the first run with #2212's exact-doubling arms). At 2.332 the bottom edge has 7.7 % headroom above the floor and the top edge 24.0 % below the cap. sqrt(2) x sqrt(1.2560 x 1.8804) = 2.173 leaves 15.6 % on both edges.

The new run confirms the projection, it does not contradict it. 1.3908 is on the slow runner class (ref_ms 52.70). Before the memo, the 23 runs with ref_ms 52.0-55.2 read 1.9147-2.2310, which projects to 1.256-1.464, and 1.3908 falls inside that range. It is inside the whole projected band (1.256, 1.880), so the band's edges, and the centre, do not move.

What changes: in `tests/replay.py`, `COST_BUDGETS["synthetic-dhw-only.json"]["cpu_ratio"]` goes from 2.332 to 2.173, and the comment above it now states the derivation. This is a **lowering** under the one-sided rule (re-record down when the cycle got cheaper). No other budget moves. `loop_cpu_ratio` 0.426 stays: R10-RCA-2205 shows it cannot be re-centred without a raise. No production file changes.

Alternatives considered:
- Leave 2.332. Rejected: the slowest projected runner (1.256, the 09-27 nightly's class) sits 7.7 % above the floor 1.166, which is less than the run-to-run spread inside one runner class.
- Centre on the post-memo measurements alone (1.3908, 1.8804, giving sqrt(2) x 1.6172 = 2.287). Rejected: two runs do not cover the 09-27 class, whose projection is lower than either measurement.

## Head

`fb85a2e976c2dc09195b1f19a2e49489afeccce7`

It is cut from `origin/main` `1005e27a6` (#2212's merge). There is one commit, which changes `tests/replay.py` only.

## Mutation proof

The fix is one recorded value, so the mutation is to the value. Each was applied to the committed head and restored with `git checkout -- tests/replay.py`.
- Survivor, the value reverted to 2.332. Written triage: centring changes the margin, not the verdict on any observed run. Every one of the 38 CI clean readings (36 projected plus 2 measured) lies inside both (1.166, 2.332] and (1.0865, 2.173]. Every measured doubled cpu arm since #2212 (2.8099 on 38656447153, and 4.0299/4.0395 locally) is over both caps. The value carries the headroom the band check depends on, not one run's verdict, so no single lane run can pin it. `prepr.sh` step 6d's unpinned-site list is answered by this triage.
- The lane's own floor check still fires on the new cap: `control:cycle_cost:loose_budget` and `control:cycle_cost:cpu` are pure functions of `cost_offenders`. They pass at the head in both lane runs below, and this diff does not touch them.

## Null control

- The unmodified tree (origin/main 1005e27a6) runs the same lane: `PYTHONPATH=tests/hastub python3 tests/replay.py` gave `ALL 91 replay checks PASSED` (clean 1.9045, cpu arm 4.0299 injected_ratio 1.0, loop arm 0.644 injected_ratio 1.0001, memory 3831.7 KiB, wall time 154.8 s).
- The centring rule, applied to #2212's factor 0.671 instead of 0.656, gives 2.207 (16.4 %/16.5 %). The direction is the same, a lowering, so the conclusion does not hinge on which of the two measured factors is used.

## Figures

All CI figures come from `/Users/timmalmstrom/.local/state/hpo/bin/python3 <scratch>/collect.py`. It lists `gh run list -R tvofi/heatpump_optimizer --workflow tests.yml --event {schedule,workflow_dispatch} --created '>=2026-09-25'`, reads each run's `slow` job through `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs`, and fetches the job log with `gh api .../actions/jobs/<id>/logs --allow-escape-sequences`. It parses the clean `cycles over ... cost {'cpu_ratio': ...}` line. It prints `FAILURES: list=0 jobs=0 log=0`. A first pass without `--allow-escape-sequences` printed `log=3`, and those three runs were re-fetched, not dropped.
- 126 runs listed (106 dispatched, 20 scheduled). 37 slow jobs printed a clean cost line through 10-14 (20 scheduled, 17 dispatched), matching R10-RCA-2205's 37. The others were skipped or cancelled slow jobs. 38656447153 is the 38th.
- Runner class: `grep -ho "cycles over .*'ref_ms': [0-9.]*" <logs>/*.log` over the 38 slow logs gives 23 pre-memo runs at ref_ms 52.0-55.2 (clean 1.9147-2.2310), and 13 at 22.2-43.1 (clean 2.3389-2.8244). The post-memo runs are 1.8804 at 23.8 ms and 1.3908 at 52.7 ms.
- Pre-memo and post-memo are split by `git merge-base --is-ancestor cb7cb25c7 <head>` (#2142's merge). That gives 36 pre-memo runs and 1 post-memo run, with 0 ancestry failures. 38656447153 (1005e27a6) is post-memo.
- Pre-memo clean is 1.9147-2.8244. x0.656 gives 1.2560-1.8528. The post-memo runs are 38530020347 at 1.8804 and 38656447153 at 1.3908.
- Centring: `<scratch>/centre.py <table> 0.656` prints `cap 2.332: floor 1.1660, bottom headroom 7.7%, top headroom 24.0%` and `cap 2.173: floor 1.0865, bottom headroom 15.6%, top headroom 15.6%` (lo 1.2560, hi 1.8804). With 0.671 it prints 2.207 (16.4 %/16.5 %).
- Run 38656447153, slow job 116167295751, finished `success`: `ALL 91 replay checks PASSED`. Clean cpu_ratio 1.3908 (ref_ms 52.70), loop_cpu_ratio 0.2693, peak 1914.7 KiB. The cpu arm read 2.8099 (injected_ratio 1.0), 29 % over 2.173. The loop arm read 0.5207 (injected_ratio 1.0001). The memory arm read 3831.1 KiB. Lane wall time was 62.6 s.
- Lane at head on this Darwin seat box: `PYTHONPATH=tests/hastub python3 tests/replay.py` gave `ALL 91 replay checks PASSED`. Clean 2.0268, cpu arm 4.0395 (injected_ratio 1.0), loop arm 0.6729 (injected_ratio 1.0001), memory 3831.5 KiB. load1 was about 60 (`uptime`). The seat box reads above every CI runner, so this run sits 7.2 % under the new cap. The cap is sized for the CI runners, the only lane that times it (nightly and dispatched `slow`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scoped gate: `python3 tests/closure.py select --diff 1005e27a6...` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/features.py). `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=1005e27a6 ./tests/run.sh` (seat venv python 3.14 first on PATH) printed `6 TEST SCRIPT(S) PASSED; 29 SCOPED OUT AND NOT RUN`, rc 0, at this head, with `ALL 4107 FEATURE CHECKS PASSED`, `ALL 2315 ENTITY CHECKS PASSED` and `ALL 109 HARNESS HEADER CHECKS PASSED`.
- Seams: `git grep -nw "2\.332" -- '*.py' '*.md' '*.json' '*.yml' '*.txt'` at the base returned only `tests/replay.py`'s comment and value, both changed here.

## Red checks

none

## Forward-carry

none

## Friction

none
