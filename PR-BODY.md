R10-REPLAY-COST-BUDGET round 2: `tests/replay.py` `cycle_cost` refused every synthetic replay with `runner class unknown: ref_ms 21.8 to 22.3 lies in no band ... no budget is assumed` (main's push runs: `4 of 194 replay checks FAILED`, all `synthetic-dhw-only.json: cycle_cost`; main's nightly at ref_ms 40.1). The cause is structural: CI's runners draw `ref_ms` as a continuum, not four clusters, so a band set cannot cover it. This round (a) re-derives the bands from measured draws and (b) grades a ruler in no band on a fallback budget derived from the class table, printed loudly, instead of refusing.

## Head

Code head measured: `83a494b91` (merge of `origin/main` 7d95405e3 into `e52f3086d`; `date -u` of the rerun 2026-11-06). Measurements of the fix itself were taken at `e52f3086d`, whose only delta to this head is main's own merge (no `tests/replay.py` change from main: `git diff e52f3086d HEAD -- tests/replay.py` is empty).

## Mutation proof

Predicate mutated: in `class_budget`, `return fallback_budget(name), []` replaced by `return None, ["runner class unknown: no budget is assumed"]` (the old refusal). `replay.controls()` then fails `control:cycle_cost:runner_class_fallback`; restored, no control fails (`HEAD failing: []`). The old behaviour is thus the mutant.

## Null control

The unmodified head passes every control (`replay.controls()` returns no failing row) and the full `tests/replay.py` run on this tree reads 194 of 195 checks green (`1 of 195 replay checks FAILED`); the one failure is `synthetic-dhw-only.json: cycle_cost [loop_cpu_ratio 0.1459 over its budget 0.1278]` on the author's box, whose `ref_ms` is 36.2 and loop figure 0.1459 (a non-CI box; the code comment on `COST_BUDGETS` states "a box outside every class reads the loop figure higher; the lane never runs on one"; CI's three measured loners at 34.6-39.7 read loop 0.085-0.108). CI is the authority for the lane. Flat input control: the owner fixture is not class-keyed and its budget (cpu_ratio 337.8, peak_kib 3740.0, loop_cpu_ratio 0.249) is unchanged; its 51 CI readings are 224.3-269.8, inside (168.9, 337.8].

## Figures

Instrument: `tests/replay.py` itself (`controls()`, `class_budget`, `fallback_budget`) plus the draws table below, derived by listing every `tests / replay` job of the last 800 CI workflow runs listed 2026-11-05 (`gh api repos/tvofi/heatpump_optimizer/actions/workflows/389816862/runs`, pages 1-8, then `actions/runs/<id>/jobs`), fetching the 51 jobs that ran (the rest were `skipped`) with `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`, and parsing each `N cycles over ... cost {...}` line and each `cpu|memory|loop doubled: cost {...}` line.

Synthetic fixture, clean `cpu_ratio` by `ref_ms` (the ten new rows are now in `COST_CLASS_READINGS`; the loners in `COST_FALLBACK_READINGS`):

| class | jobs | ref_ms | clean cpu_ratio | doubled-cpu arm | budget |
|---|---|---|---|---|---|
| ref24 (band 19.51-25.53, was 22.64-25.53) | 10 + 1 prior | 20.54-23.94 | 2.414-3.597 (spread 1.49x) | 4.865-7.35 | 4.167 (was 3.630) |
| ref30 | 11 | 30.35-31.61 | 2.74-2.887 | 5.60-6.03 | 3.934 |
| ref46 | 27 | 45.86-48.90 | 2.306-2.476 | 4.62-4.95 | 3.357 |
| none (loners) | 3 | 34.61, 37.80, 39.74 | 3.069, 2.417, 2.759 | 5.76, 4.65, 5.42 | fallback 4.167 |

Why 4.167: sqrt(2) x the geometric midpoint of 2.414 and 3.597 (the existing centring rule, `COST_DETECTION` = 2); every reading is 58-86 % of it, the lowest doubled (4.83) over it. The old 3.630 refused the 3.597 draw's neighbours' 1.0 headroom; the draws at 21.58-22.28 sit below the old band and were refused outright. `loop_cpu_ratio` 0.1813 for ref24 holds the new readings 0.1109-0.1332 and their doubled arms 0.2255-0.2665, unchanged. ref53 has no new draw in this window and is unchanged.

Fallback: `fallback_budget` = per keyed metric the largest class budget (derived, not a literal: `cpu_ratio` 4.167), other metrics from `COST_BUDGETS` (loop 0.1278). Why not only re-band: three loners (34.61, 37.80, 39.74) and the nightly's 40.1 sit between bands and would need a class each from one reading, which the file's own rule forbids (a class is admitted only on its own readings). Why not only the fallback: the 20.5-22.3 draws read 3.4-3.6, which the fallback also holds, but the bands keep the tighter budget (3.357-3.934) for the 38 jobs that sit in ref30/ref46. Limit: a ruler in no band reading below cap/2 (2.08) is still refused by `cost_offenders` ("cannot see a 2x cycle"); the two earlier refused rulers 28.01 and 34.35 (1.89 and 1.87) are such draws, and `COST_RULERS_REFUSED` is removed because the fallback refuses them on the same measured ground.

Refusal rows by `ref_ms`, `class_budget` + `cost_offenders` at the tree (clean = measured reading, doubled = 2x it; "refuse" is a `cycle_cost` offender, which makes `replay.py` exit 1):

| ref_ms | where | budget | clean | doubled |
|---|---|---|---|---|
| 20.54 | in ref24 | 4.167 | pass | refuse (6.804) |
| 23.94 | in ref24 | 4.167 | pass | refuse (5.27) |
| 30.5 | in ref30 | 3.934 | pass | refuse (5.7) |
| 47 | in ref46 | 3.357 | pass | refuse (4.8) |
| 53 | in ref53 | 2.081 | pass | refuse (2.9) |
| 27 | between | 4.167 | pass | refuse (5.6) |
| 35 | between | 4.167 | pass | refuse (6.138) |
| 40.1 | between (nightly) | 4.167 | pass | refuse (5.52) |
| 21.8 | was below, now in ref24 | 4.167 | pass | refuse (7) |
| 15 | below lowest | 4.167 | pass | refuse (5.6) |
| 80 | above highest | 4.167 | pass | refuse (5.6) |

The planted 2x on a real replay: the lane's own `cpu doubled`, `memory doubled` and `loop doubled` arms (a whole-cycle spin, a doubled allocation, a doubled loop thread) run in `tests/replay.py` and read `ok synthetic-dhw-only.json: cycle_cost sees a doubled cycle cpu/memory/loop` on a ref_ms 35.4-36.2 box, i.e. on the fallback; the table above gives the arms' measured readings per class from the CI logs. New controls: `control:cycle_cost:runner_class_fallback` (every probe between, under and over the bands gets the fallback and a notice, NaN gets none, a banded ruler gets no notice) and `control:cycle_cost:fallback_budget` (the loners pass clean and every doubled arm is refused). No runner class went unprobed except ref53, which has no new draw.

Before and after of main's red: of the 51 clean synthetic readings, 8 lay in no band of the old table (and were refused with `no budget is assumed`); with the new table `class_budget` + `cost_offenders` offend on 0 of 51 (parsed table, one script over the draws; control: the same loop on the old tables refuses those 8).

No budget file raised other than the replay cost budgets: `COST_CLASS_BUDGETS` synthetic ref24 `cpu_ratio` 3.630 -> 4.167 (a raise, justified above by the 3.402-3.597 readings the old budget left no room for); `COST_RUNNER_CLASSES` ref24 low edge 22.64 -> 19.51. `tests/structure_budgets.json` untouched. Claim files byte-identical to origin/main (`prepr.sh` step: `claim files byte-identical to origin/main`); VERSION, manifest version and RELEASE_NOTES untouched.

## Red checks

None on this head at write time: no check runs exist for it before the pull request opens; `prepr.sh` ran clean at `e52f3086d` and is re-run at the merged head. Main's own red (the cause this PR repairs): `tests / replay` on main's push runs and job 127562699131 (PR 3220 head e70dfd64) failed `synthetic-dhw-only.json: cycle_cost` with `runner class unknown: ref_ms 21.8 to 22.3 lies in no band`, read from the job log; cause: bands fixed to four clusters while the runner pool draws a continuum. Cheaper detector: none exists before the draw (runner speed is not knowable pre-push); the standing cost of the countermeasure is that an unbanded ruler is now graded, not refused, and logs a `WARNING runner class unknown` line (`runner_notice`) so a new class is admitted by appending its readings.

## Forward-carry

The roster group's open carries: (1) re-centre 355.7 / 3740.0 / 0.249 on the second CI class: this tree's owner budget is 337.8 / 3740.0 / 0.249 and the 51 CI readings (224.3-269.8) sit inside it; the 385.3 reading was a fresh non-CI container, outside the lane — Carry: none, built (measured here). (2) Record the real day's cost budget: owner-fixture readings recorded in the table above, built as above. (3) `AWAY_COVERED` pin and `export.py` credential-refusal pin: not built here, small checks that belong with their own seams — Carry: R10-REPLAY-COST-BUDGET round 3 (routed, no code in this diff). (4) item 507ad27c from PR 3170: built by this PR (the runner-class refusal it names).

## Friction

none
