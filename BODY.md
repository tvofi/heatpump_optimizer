The nightly `slow` lane went red on main because of two things together. Neither is a CPU regression. First, #2142's solve memo made the coordinator cycle cheaper (0.671x). That left the replay's `cpu_ratio` cap of 3.576 at the floor of its band. Second, the lane's cpu-doubled perturbation was never a 2x of what `cpu_ratio` times. It spun inside `_async_update_data`, while `cpu_ratio` times the update, its executor jobs and the entity sweep (the module docstring says so). On the six nightlies of 10-09..10-14 it read 1.895-1.966x (Figures). On 2026-10-14 that under-doubled arm read 3.5628 against the 3.576 cap, and `cycle_cost sees a doubled cycle cpu` failed. The only offender it printed was the loop figure. That line is where the issue title "cpu doubles" came from, but it was the perturbation's own spin, not the clean cycle. The clean arm passed on the same night (1.8804).

Verdict (b): an instrument and budget artefact behind a real speedup. No production file changes. Closes #2205.

What changes, all in `tests/replay.py`:
- The cpu and loop arms now spin in one place in `run_fixture`, using `_spin`. Each spins exactly the clean span its metric times: process CPU of update, jobs and sweep for `cpu`, and the loop thread's own work for `loop`. `inject_cost` keeps only the memory arm.
- Each arm's spin is metered (`_INJECTED_CPU`), and the lane checks `the <arm> arm doubles the whole span <metric> times` through `short_doubling` (injected over the clean span must be >= 1). Two new controls run on every pull request through `tests/entities.py`.
- `cpu_ratio` is re-recorded DOWN, 3.576 -> 2.332. This is the one-sided rule's re-record when the cycle got cheaper. It is not a raise. The value is centred the way `loop_cpu_ratio` was (method under Figures).

Alternatives considered (fixer step 17):
- Re-record only the budget, leaving the arm as it was. Rejected: the arm would still under-double, so the check stays one runner-class spread away from the next false red.
- Lower the cap with no centring (sqrt(2) x 1.8804 = 2.659). Rejected: that puts the projected slow-runner class (1.446) under its floor of 1.330 by only 9 %.
- Fix only the arm. Rejected: 4 of 10 local clean runs of this package read under 3.576's floor (1.788), so the clean arm itself goes red.

## Head

`d7bfeb0dd6803eb9348ded16facdc7b164915961`

The branch is cut from `origin/main` 17f1c55fa. Commits: the failing check first (b0c8862b7), the fix (2dd929d86), the controls pinned apart (b32af7386), two harness-only commits (342f6895a, 2db7605ee), a merge of `origin/main` 554e2ecfa (056577124), and the harness listed among `harness_headers.py`'s inert reads in `tests/closures.json` (d7bfeb0dd).

The merge brought no change under `tests/` or `custom_components/` (`git diff --stat 2db7605ee d7bfeb0dd -- tests custom_components` lists only this branch's own `tests/closures.json` line). So the replay figures below, taken at 2db7605ee and before, describe this head's `tests/replay.py` and package bytes. `structure.py` and the scoped gate were re-run at this head.

## Mutation proof

Each mutation was applied to the committed head, run, then restored with `git checkout -- tests/replay.py`. Logs are in the seat scratch.
- M1, the fix line reverted (`if inject in ("cpu", "loop"):` -> `if inject == "loop":`, so the cpu arm spins nothing). `PYTHONPATH=tests/hastub python3.13 tests/replay.py` gave `2 of 80 replay checks FAILED`: `synthetic-dhw-only.json: cycle_cost sees a doubled cycle cpu` (cpu_ratio 1.8437 against clean 1.6554) and `synthetic-dhw-only.json: the cpu arm doubles the whole span cpu_ratio times` (`injected 0 x the clean span`).
- M2, the pre-fix spin inside `_async_update_data`. This is the test-first commit b0c8862b7, run the same way. `the cpu arm doubles the whole span cpu_ratio times` FAILED: the cpu arm's `injected_ratio` was 0.9293, against 1.0001 for the loop arm. A first draft of the same check, keyed on share, reproduced the nightly failure verbatim: `3 of 79 replay checks FAILED`, including `cycle_cost sees a doubled cycle cpu [cpu_ratio 3.4821 against clean 1.9144: loop_cpu_ratio 2.05 over its budget 0.426]`.
- M3, `short_doubling`'s threshold set to `>= 0.9`. `control:cycle_cost:short_doubling` FAILED (bad=[] good=[]).
- M4, the threshold set to `> 1.0`. `control:cycle_cost:unmetered_doubling` FAILED (good=['injected 1 x the clean span ...']).
- Survivor, the budget value reverted to 3.576. One lane run passed all 80 checks: that run's clean arm read 1.9618, above the old floor. Written triage: the re-record is load-bearing on the clean band, not on one run. Across the 10 local clean readings of this package (origin/main 17f1c55fa's package, which this diff does not touch: base harness 1.8133/1.7813/1.6841, lane runs 1.9144/1.731/1.6554/1.9618, head harness 1.8731/1.7927/1.864), 4 fall under the old floor of 1.788 and 0 fall outside the new band (1.166, 2.332]. The same holds for the projected slow-runner class (Figures).

## Null control

- The unmodified tree (origin/main 17f1c55fa, same package as the first red nightly's 9111acce): `the replay ran to the end` passes on every arm, and the clean arm's own checks are green. Only the perturbation arm fails, as on CI.
- The memory arm is untouched (no `injected_ratio`). Its peak doubles at base and at head (1913 -> 3832-3838 KiB). Its cpu_ratio hot/clean stays at 0.98-1.07 on the base harness run.
- The loop arm's `injected_ratio` is 1.0001 at the test-first commit and at head. Moving its spin into `_spin` changed nothing it measures.
- Bisect null: `loop_cpu_ratio` does not move at #2142 (0.345/0.363 before, 0.337/0.328 after), while `cpu_ratio` drops by a third. #2142 moved the cycle's executor or solve share, not the loop.

## Figures

All local runs are on this Darwin box (8 cores). BLAS is pinned to 1 thread by `tests/stress.py`'s setdefault (`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_*_NUM_THREADS=1`). The reference solve's thread_factor is 1.0, printed by the harness's `RESULT thread_factor` line. load1 ran 12-92 during these runs and is printed per row. `cpu_ratio` is the mean cycle process CPU over the median reference-solve CPU. `injected_ratio` is the summed arm spin over the summed clean span, both on the arm metric's own clock.
- CI, last green nightly against first red. Command: `gh run view <run> -R tvofi/heatpump_optimizer --log --job <slow job>` on 38376595322/115226421873 (59b76606) and 38530020347/115739400655 (9111acce). Clean cpu_ratio was 2.1758 (ref 53.3 ms) and 1.8804 (ref 23.8 ms). The cpu arm read 4.2073 and 3.5628; hot/clean 1.934 and 1.895. The five green nightlies 10-09..10-13 (runs 37909555545, 38038305969, 38126689594, 38229000848, 38376595322) read clean 2.1955/2.5992/2.7689/2.1559/2.1758 and hot/clean 1.966/1.910/1.953/1.937/1.934, all under 2. Lane wall time was 38.1-110.8 s.
- Bisect, clean cpu_ratio by merge commit. Two interleaved local rounds, extracted with `git archive <sha> tests custom_components`, each run with `PYTHONPATH=tests/hastub:custom_components:tests python3.13 tests/replay.py --one tests/replay/synthetic-dhw-only.json`:

  | commit | cpu_ratio | loop_cpu_ratio |
  |---|---|---|
  | 59b76606 | 2.9824/3.0312 | 0.3449/0.3628 |
  | cb7cb25c7 (#2142) | 2.0061/2.0269 | 0.3371/0.328 |
  | d5f584152 (#2167) | 1.8752/2.1086 | |
  | 9a6e0d9dd | 1.8186/1.8494 | |
  | 8b495603a | 1.902/1.8654 | |
  | 6cdf90ac0 (entities 79 -> 81) | 1.75/1.7301 | |
  | adc0ae5f3 | 1.9159/1.7538 | |
  | 9111acce | 1.9049/1.849 | 0.3761/0.3616 |

  The single step is #2142: 3.0068 -> 2.0165 mean, factor 0.6706. Every other merge is flat within the same run's noise. That is the null for the step.
- Budget: the five pre-#2142 nightlies x 0.6706 project to 1.446-1.857. The first post-#2142 nightly read 1.8804, on the ref-23.8-ms class whose pre value 2.7689 projects to 1.857. sqrt(2) x sqrt(1.4458 x 1.8804) = 2.3319, recorded as 2.332. Floor 1.166. 1.8804 sits 19.4 % under the cap and 1.4458 sits 24 % over the floor (python arithmetic shown in the seat log). The old cap's floor of 1.788 sits above every projected ref-53-ms-class runner (1.446-1.473), which was 4 of the last 6 nightlies' runner class.
- Head lane: `PYTHONPATH=tests/hastub python3.13 tests/replay.py` gave `ALL 80 replay checks PASSED` (clean 1.731; cpu arm 3.8501 with injected_ratio 1.0001; loop arm 0.7376 with injected_ratio 1.0001; memory 3835.2 KiB).
- Harness at head: `PYTHONPATH=tests/hastub:custom_components:tests python3.13 dev/audit/harnesses/r10_2205_replay_cost_arms.py 3`, giving clean 1.7927-1.8731; cpu arm hot/clean 1.934-2.148 with injected_ratio 1.0/1.0/1.0; loop arm injected_ratio 1.0002 x3; memory hot/clean 0.98-1.079. load1 was 77-119 on this run. The same harness at the base: clean 1.6841-1.8133; cpu hot/clean 1.973-2.135 (cross-process, load1 20-29). The base prints no injected_ratio.
- `python3.13 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` with python3.13 first on PATH printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/features.py), then `6 TEST SCRIPT(S) PASSED; 29 SCOPED OUT AND NOT RUN`, rc 0, at this head: `ALL 4107 FEATURE CHECKS PASSED`, `ALL 2305 ENTITY CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED`. The previous harness commit failed `harness_headers.py`'s depth-seam check (`parents[3]`); the canonical `repo_root` walk replaced it.
- Seams (fixer step 8). The rule `git grep -n -e "inject-cost" -e "def inject_cost" -e "_spin(" -- tests` enumerates the perturbation sites. They are `tests/replay.py`'s three arms only: cpu and loop closed in this diff, memory already exact (2.00x peak). `tests/stress.py`'s DETECTION_TARGET budgets perturb nothing at runtime.

### Root cause (defect-root-cause.md, first trigger: shipped in v7.0.0)

- Cause: the cpu perturbation doubled `_async_update_data` and not the span `cpu_ratio` times. It read under 2x on all six nightlies whose logs were read (10-09..10-14), and it went red as soon as a real speedup (#2142) carried the clean cycle to the cap's floor.
- Process state: **(c) the process was followed and did not produce the intended result.** The band rule plus a perturbation arm ran every night as designed. The arm only proved "a 1.9x cycle is over budget", and it fired before the clean arm's floor check. So the speedup surfaced as "cycle_cost sees a doubled cycle cpu", which the issue then read as a doubled CPU. The second contributing cause is the lane being nightly-only (a recorded decision in `tests.yml`'s replay step). #2142 could not see its own effect on the band, though its effect was an improvement.
- Countermeasure built here: the exact-doubling arms plus `short_doubling`. A speedup now surfaces as the clean arm's own `budget X cannot see a 2x cycle; re-record Y` line, which names the remedy. The detector is shown to detect: M2 fails at b0c8862b7 and passes at head. Standing cost: zero seconds per pull request, because the two controls run inside entities.py's existing replay section.
- Cost test for the second cause (a per-PR timed replay on a package diff), not built: it is a `tests.yml` change, so the separate root-cause seat owes the process analysis. Numbers for it: 13 package-touching merges in the v6.7.17..v7.0.0 cycle (`git log --first-parent --oneline v6.7.17..v7.0.0 -- 'custom_components/heatpump_optimizer/*.py'`) x 38-111 s CI lane wall = 8-24 min per cycle. Defect cost: one red nightly day, record PR #2202 blocked, and roughly 3 seat-hours (this fixer and its review). P(recurrence) per cycle is estimated at 0.5: the budget was re-recorded at bc0583545 and 960681c12 and drifted here, about once per round, and no class frequency is measured. 3 h x 0.5 = 90 min against 8-24 min, which favours it before counting per-PR timing noise. That noise is unmeasured, and the runner-class spread is 1.28x inside a 2x band.

## Red checks

`nightly-status` is red on main from schedule run 38530020347. This PR is its fix: the failing step was `Replay recorded days through the real coordinator`, `1 of 77 replay checks FAILED`. The cheaper detector is the per-PR timed replay, priced under Root cause above (8-24 min CI per release cycle) and not built here. `nightly-status` grades main and this diff does not touch what it reads, so it stays red until the next nightly or a dispatched `tests.yml` on main runs the lane.

## Forward-carry

none

## Friction

none
