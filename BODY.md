R10-REPLAY-COST-BUDGET round 3 (repair of the round-2 review's block). The replay lane's `cycle_cost` check graded each run on its own BLAS ruler, so one runner drawn on CI could be graded on a class its population does not hold. Job 127046649273 (run 41966183843, PR 3219) is a ref46-population runner: its doubled arms ran at ref_ms 47.28 and 48.13. Its clean run's ruler drifted to 50.94, past the 49.60 border, and the lane refused it as `cpu_ratio 2.256 over its budget 2.081` (ref53). This tree makes two changes:

- **The ruler is the job's.** `job_rulers` takes the median `ref_ms` and `loop_ref_ms` over every run of the lane in the job (each fixture's clean run and doubled arms). `grade_ran` grades the whole job on that one class.
- **Every band and budget comes from one stated rule.** `derive_cost_classes` runs over every CI draw on record, committed as `tests/replay_cost_draws.tsv`. That file is harvested by `tools/audit/seat/replay_draws.py`. The `cycle_cost:class_rule` control refuses any table the rule does not return.

The rule:

- Sort the synthetic fixture's jobs by job ruler and split them into classes at every gap of at least `COST_CLASS_GAP_MS` (2.0 ms).
- A border is that gap's midpoint. The outer edges are the extreme job rulers widened 5 %. The bands are half-open, `[lo, hi)`.
- A metric that one budget can hold (its largest clean draw is under 2 x its smallest) takes one budget. Any other metric is keyed by class.
- Every budget is sqrt(2) x the geometric midpoint of the clean draws it holds.
- The loop figure is re-normalised to the job's loop ruler before it is graded (`pooled_figures`).

On the committed draws, the largest step left inside a class is 1.70 ms (job 126631977357 to job 127046649273). The smallest step the rule cuts is 2.10 ms (job 127046649273 to job 125051003592).

**What this round corrects in the round-2 body (disclosed self-correction).** Round 2 said "ref53 has no new draw in this window" and "offend on 0 of 51". Both were false. The window holds 78 synthetic clean replay jobs, not 51. Job 127046649273 is in it, and at round 2's head it offended. The re-derived counts are in `## Figures`.

**Findings, each built in this round** (commits on this branch, each pinned by a check that runs in `tests/entities.py` through `replay.controls()` and in the lane):

- **Block, the ref46/ref53 border.** Built in 6715d9733. That commit added the job ruler, the classes cut by rule, and the draw set. The block draw's job ruler is 50.07, which lands in class ref47 `[42.96, 51.12)`. It passes clean there and each doubled arm is refused. Pinned by `control:cycle_cost:draws`, which grades every job of the draw set as the lane does. Its null moves job 127046649273 over the ref53 border and moves job 125051003592 under it; each is mis-graded and named. Also pinned by `control:cycle_cost:lane_prints_notice`, built in 2c015f5c1: it drives `grade_ran`, the lane's own grading, on that job. It holds the job at its own ruler and goes red moved over the border.
  - Residual margin: the job ruler sits 1.05 ms under the ref47/ref53 border (51.12). A ref47 job drawing a ruler over 51.12 would be graded on ref53's budget. The rule moves the border when such a draw is appended.
  - Alternative not taken: merging adjacent classes whose union one budget holds. ref47 and ref53 would merge (2.476 < 2 x 1.444), at the cost of the 1.5x margin on ref53. It lost because the rule kept here leaves every class's 2x detection and 1.5x margin as measured.
- **1. Loop-ruler outlier**, job 127310664875 (run 42046303116): clean `loop_ref_ms` 279.78 against 158.40-161.42 on its arms. Built in 6715d9733 by `pooled_figures`. Re-normalised to the job's loop ruler of 159.5, the clean figure is 0.0594 x 279.78 / 159.5 = 0.104, inside the one loop budget of 0.1527. Pinned by `control:cycle_cost:draws`. With the pooling removed (mutant M6 below), that control and `control:cycle_cost:class_rule` fail.
- **2. Window table re-derived.** Built in 078780e68: `replay_draws.py window` grades each window job at the tree. The window rule is the 800 most recent ci.yml runs created up to 2026-11-05T23:59:59Z. They span 2026-11-02T10:31:19Z .. 2026-11-05T23:58:54Z and hold 78 synthetic clean `tests / replay` jobs. The job ids are printed by that command and are rows of the committed draw set.
  - The fresh harvest made 0 failed requests over 1400 runs, so the run 41831302984 page that returned 502 to the reviewer is included this time.
  - Every row it parsed up to 2026-11-05 is a row of the committed set.
- **3. ref24 budget.** The class is now ref23 `[19.36, 25.63)`, holding 18 jobs with clean cpu_ratio 1.959-3.597. Its budget is the rule's value, 3.7539, and the rule is the reason; headroom is not. Built in 6715d9733 and pinned by `control:cycle_cost:class_rule`, whose null sets ref23 back to 3.630 by hand and is named. Restoring 3.630 by hand (mutant M5) fails it.
  - Measured over ref23's 18 clean draws, with a budget of b:
    - b = 3.630 holds all 18, refuses every doubling, and lets 3 of the 1.5x draws pass.
    - b = 3.7539 (the rule) holds all 18, refuses every doubling, and lets 4 of the 1.5x draws pass.
    - b = round 2's 4.167 lets 7 of the 1.5x draws pass and no longer refuses every doubling (2 x 1.959 = 3.918 < 4.167).
  - The extra 1.5x draw that passes is the stated cost of keeping a rule over a hand-set literal.
- **4. `fallback_budget`.** Code and docstring both changed in 6715d9733. The pooled loop figure fits one budget across every CI draw (0.0883-0.132, 1.50x), so `loop_cpu_ratio` is keyed by no class, and round 2's 0.1278/0.1813 split is gone. The fallback is each class-keyed metric at its largest class budget and every other metric at its one `COST_BUDGETS` value: cpu_ratio 3.9874, loop 0.1527, peak_kib 2686.0. A ref24-population runner on an unbanded ruler is graded on loop 0.1527, which is over its CI maximum.
  - Pinned by `control:cycle_cost:runner_class_fallback`, which asserts the fallback loop equals `COST_BUDGETS`' value and that cpu equals the largest class budget.
  - Also pinned by `control:cycle_cost:class_rule`, which refuses a metric keyed both flat and by class. Its null is a flat `cpu_ratio` added beside the class keys.
- **5. Stale comment.** Built in 6715d9733. The "every reading 69-72 %" comment is deleted; the rule is stated in its place (`derive_cost_classes`). The per-class percentages are in `## Figures`.
- **6. AWAY_COVERED and export.py credential-refusal pins.** Already built before this round and running at this head; nothing routes to a later round. The checks are `ok control:away:covered_names_are_committed`, `ok AWAY_COVERED names committed fixtures` and `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url`, all in the local lane run in `## Figures`.
- **7. Mutation gaps.** Built in 6715d9733 and 2c015f5c1:
  - band `<=` to `<` is killed by `control:cycle_cost:band_edges`;
  - the ref24 edge back to 22.64 and a hand-set 3.630 are killed by `control:cycle_cost:class_rule`;
  - the dropped notice print is killed by `control:cycle_cost:lane_prints_notice`, which drives `grade_ran` and reads its stdout.

  Counts are in `## Mutation proof`.

**In-code replay budgets** (no `*_budgets.json` touched). Each value below is the rule's, against origin/main's:

- synthetic `loop_cpu_ratio`: 0.1278, plus a ref24 key of 0.1813, becomes one 0.1527.
- owner `cpu_ratio`: 337.8 becomes 332.7976.
- owner `loop_cpu_ratio`: 0.249 becomes 0.2154.
- owner `peak_kib` 3740.0 and synthetic `peak_kib` 2686.0 are unchanged.
- synthetic `cpu_ratio` by class:
  - main: ref24 3.630, ref30 3.934, ref46 3.357, ref53 2.081;
  - this tree: ref23 3.7539, ref28 3.189, ref31 3.2877, ref38 3.4579, ref40 3.9874, ref47 3.3424, ref53 2.076.

The raises against main are the synthetic loop 0.1278 to 0.1527 and ref24's 3.630 to ref23's 3.7539. Both are the rule's values over the draws. A doubled arm is refused on every CI draw on record (`control:cycle_cost:draws`).

`VERSION`, the manifest version, the RELEASE_NOTES heading and both claim files are byte-identical to origin/main.

## Head

130769e1db383e4c6e98b01c4a90b31173693cb7

## Mutation proof

Each production line is mutated in the tree and `replay.controls()` is run, then the line is restored (driver: a scratch replacement loop, one mutant at a time):

- M1: `job_rulers` returns the first run's rulers instead of the median. 1 failing: `control:cycle_cost:class_rule`.
- M2: band `lo <= ref_ms < hi` changed to `lo < ref_ms < hi`. 1 failing: `control:cycle_cost:band_edges`.
- M3: ref23 low edge 19.36 changed to 22.64. 1 failing: `control:cycle_cost:class_rule`.
- M4: `print(f"  {line}")` in `grade_ran` dropped. 1 failing: `control:cycle_cost:lane_prints_notice`.
- M5: ref23 cpu_ratio 3.7539 changed to 3.630. 1 failing: `control:cycle_cost:class_rule`.
- M6: the loop figure is not pooled (`loop_cpu_ratio * 1.0`). 2 failing: `control:cycle_cost:class_rule`, `control:cycle_cost:draws`.

The block draw is shown at the instrument:

- `replay_draws.py grade --job 127046649273` prints that clean passes in ref47 and the cpu, loop and memory arms are refused; rc=0.
- With `--ruler 52.12` (moved over the border) clean is refused, `cpu_ratio 2.256 over its budget 2.076`; rc=1.
- With `--clean-from cpu` (the doubled arm graded as clean) it is refused, `cpu_ratio 4.444 over its budget 3.342`; rc=1.

The loop outlier at the same instrument:

- `grade --job 127310664875` gives rc=0.
- `--clean-from loop` gives `loop_cpu_ratio 0.2074 over its budget 0.1527`; rc=1.

## Null control

At round 2's head 009edde68 the reviewer's grading of the same window refuses 2 of 78 in-window synthetic clean draws, and origin/main refuses 13 of 78 (`ev/window-offenders.txt` on refs/heads/probe/rev-3234-c9b474ca, commit d506ad0a21b5). At this head `replay_draws.py window` refuses 0 of 78, rc=0.

The `--ruler` and `--clean-from` runs above are the instrument's own null: the same grading names the draw red once it is moved across the border or doubled.

## Figures

- Draw set: 116 jobs, 565 runs (`control:cycle_cost:draws` prints them; `PYTHONPATH=tests/hastub python3 tests/replay.py`). The harvest was `python3 tools/audit/seat/replay_draws.py fetch --cache DIR` then `python3 tools/audit/seat/replay_draws.py parse --cache DIR --out FILE`: 1200 ci.yml and 200 nightly.yml runs listed at 2026-11-06T09:11Z, `failed requests 0`. Null: every parsed row up to 2026-11-05 is a row of the committed file (a sorted diff of the two gave 0 rows only in the fresh parse). The reviewer's 535-row `ev/draws.tsv` equals the 535 rows round 3 first committed (sorted diff empty), and this round appends 30.
- Window: `PYTHONPATH=tests/hastub python3 tools/audit/seat/replay_draws.py window --cache DIR --runs 800 --until 2026-11-05T23:59:59Z` prints `window jobs 78, not in replay_cost_draws.tsv: []; by class {'ref31': 20, 'ref47': 41, 'ref23': 14, 'ref40': 1, 'ref38': 2}; clean offending 0`, rc=0. Under the reviewer's round-2 classes the same 78 read ref24 14, ref30 18, ref46 40, ref53 1, unbanded 5. Here the ref53 one is job 127046649273, now in ref47 by its job ruler, and the 5 unbanded fall in ref31 (2), ref38 (2) and ref40 (1).
- Per class over every clean draw of the set, as `class: jobs, cpu_ratio range, budget, readings as % of budget, 1.5x draws passing`:
  - ref23: 18 jobs, 1.959-3.597, 3.7539, 52-96 %, 4;
  - ref28: 2 jobs, 1.892-2.687, 3.189, 59-84 %, 1;
  - ref31: 33 jobs, 1.761-3.069, 3.2877, 54-93 %, 6;
  - ref38: 2 jobs, 2.417-2.474, 3.4579, 70-72 %, 0;
  - ref40: 2 jobs, 2.759-2.881, 3.9874, 69-72 %, 0;
  - ref47: 48 jobs, 2.256-2.476, 3.3424, 67-74 %, 0;
  - ref53: 11 jobs, 1.444-1.493, 2.076, 70-72 %, 0.

  Pooled synthetic loop is 0.0883-0.132 against 0.1527. Owner fixture: 101 clean draws, cpu_ratio 204.2-271.2 against 332.7976. These were computed from `replay.cost_draws()` and `replay.draw_rulers()` by a scratch one-liner. Null: `control:cycle_cost:class_rule` names a table set by hand.
- Class seams (fixer step 8). The rule is "every CI draw graded on a budget its population holds", enumerated by `control:cycle_cost:draws` over all 116 jobs, each clean run and each doubled arm. At round 2's head it returns 2 seams, 127046649273 (border) and 127310664875 (loop ruler), and at this head none (`offenders []`). Both seams are closed in this diff; its null names both moved jobs.
- `tests / nightly-status` cause: `PYTHONPATH=tests/hastub python3 tools/audit/seat/replay_draws.py grade --job 126971378040`. This is the 2026-11-05 nightly `slow` job, refused on main as unbanded ref_ms 40.1 and owner `loop_cpu_ratio 0.1232: budget 0.249 cannot see a 2x cycle`. Here it reads ref40 and owner, clean passes, every arm is refused, rc=0.
- Local lane: `PYTHONPATH=tests/hastub python3 tests/replay.py` on this box prints `ALL 197 replay checks PASSED`, rc=0, at job ruler 28.82 (class ref28).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D` prints `MODE: SCOPED -- 3 script(s) run, 30 scoped out.` (debug_collect.py, entities.py, features.py), against origin/main 7e8939d38 (fetched 2026-11-06). With `PYTHONPATH=tests/hastub`: `python3 tests/debug_collect.py` prints `ALL 162 DEBUG COLLECT CHECKS PASSED`; `python3 tests/entities.py` prints `ALL 2635 ENTITY CHECKS PASSED`; `python3 tests/features.py` prints `ALL 4876 FEATURE CHECKS PASSED`; `python3 tests/env_drift.py --claims-only` at the merge base prints `claims hygiene: ... ok`; `python3 tests/closure.py selftest` prints `ALL 118 closure shrink pins PASSED`.

- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` prints `cloud-setup check: OK`.

## Red checks

- `tests / nightly-status` (job 127659541092, run 42146565424) is red on PR head 009edde68. It is the only concluded red across every check-run page of that head: 1 failure, 45 success, 22 skipped. Its log reads `NIGHTLY FAILED: slow failed 1 night ago`, naming scheduled run 41943946464 job 126971378040. That job is the main-side red this group repairs (unbanded ruler 40.1, and the owner loop budget 0.249 too loose for 0.1232); at this head it grades clean, as in `## Figures`.
  - The check asks for a `nightly.yml` dispatch on main after the fix lands. That is the orchestrator's, after the merge; this seat dispatches nothing.
  - Cheaper detector: `control:cycle_cost:draws` grades every committed nightly and PR draw on every gate run of `tests/entities.py`. Its standing cost is appending new jobs' rows (`replay_draws.py fetch`/`parse`) when a runner class appears.
- `tests / closures`: predicted INERT READS for `tools/audit/seat/replay_draws.py`, repaired in the diff by `tools/pr/ci_predict.py --apply-inert`. The UNCLASSIFIED `tests/replay_cost_draws.tsv` is repaired by recording `tests/entities.py`'s closure (`tests/derive_closures.sh --single tests/entities.py`).

## Forward-carry

none

## Friction

none
