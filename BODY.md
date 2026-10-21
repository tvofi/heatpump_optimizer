# Summary

The nightly `slow` lane has been red on main two nights in a row on one replay
check: `loop_cpu_ratio 0.1114 over its budget 0.111` (run 39387919507,
2026-10-20) and `loop_cpu_ratio 0.1138 over its budget 0.111` (run
39563978649, 2026-10-21). That red is what `nightly-status` reports on every
open pull request.

The cause is the runner class. The loop did not grow. Both red rows ran on
the fast runner class, where the pure-Python ruler is twice as fast
(`loop_ref_ms` 84 and 79, against 128-161 on the green rows). The loop's own
CPU on those runners also fell, to 9.4 and 9.0 ms from 11-15 ms, but by
less than the ruler did. So the ratio rises by about 1.28x on a fast runner. To rule out
code growth, I measured the five main commits behind the nightly rows (from
`e3f3b312f`, the first post-#2339 row, to the tip `df6ca4bc6`), interleaved
three rounds on one box. The medians are 0.0837 to 0.0918 with no trend, and
the tip is the second lowest.

This raises only `loop_cpu_ratio`, from 0.111 to **0.120**. 0.120 is the
largest CI row (0.1138) plus the measured within-run noise band (5.0 %). That
is lower than the 0.124 this branch carried before (sqrt(2) x median), which
added headroom no measurement called for. `cpu_ratio` and `peak_kib` stay as
they are. The merge with main keeps #2514's diagnosis in the comment block
above `COST_BUDGETS` and replaces only its recording note, which the two red
rows falsified.

Part of #2272. `tests/replay.py` is code-owned.

## Raise justification

The raise is approved under mandate 6175172275 (scope `all`), once no
payment that improves the code exists. Every payment considered:

1. **Cut loop CPU in the integration.** Not taken: there is nothing to cut
   that caused this. The interleaved bisect above shows no growth across the
   commits behind the series. Loop-CPU work belongs to roster group
   R10-LOOP-CPU (not started, after R10-FREQ-DEFROST). A cut there would
   lower the figure but would not remove the 1.28x class factor that put
   these rows over the cap.
2. **Re-centre down, or keep 0.111.** Not taken: two consecutive scheduled
   rows are over 0.111, so main stays red on every fast-class night.
3. **Re-centre on the band rule the file uses for `cpu_ratio`** (sqrt(2) x the
   geometric midpoint of 0.0868 and 0.1138, which is 0.1406). Not taken: it
   pads 24 % above the largest row, and its floor of 0.0703 would red a local
   run at the old twelve-run minimum of 0.0618.
4. **Keep 0.124** (this branch's previous value, sqrt(2) x the median 0.0877).
   Not taken: it is 9 % above the largest row, and the measured noise band
   is 5.0 %.
5. **Remove the residual class factor in the ruler**, either with a workload
   whose memory profile matches the loop's or with a per-class budget. This
   would make the check robust instead of re-capped. Not taken here: the
   ruler is #2270's owner decision, and changing it resets every historical
   ratio (`_loop_reference_work`'s own rule). It belongs to the lane that
   gates the nightly replay. Carry: R10-REPLAY-LANE
6. **Make the band one-sided for this metric.** The lane's nightly
   loop-doubled arm already proves detection on the same runner. Not taken:
   it changes `COST_DETECTION`'s two-sided rule, which `cpu_ratio` and
   `peak_kib` share, and 0.120 fits every measured reading inside the
   two-sided band anyway.

Architecture score: dS +0.0000 (NULL), `tools/audit/archscore/score.py --diff
origin/main HEAD`. The change is a test-file literal and its comment.

## Head

`7d659d6027ac92d0dfa64b97801e29a3704c5a37` (branch `handoff/r10-replay-cap`):
`38aec7bf0` merged with `origin/main`, re-merged at
`6961f06637964001a2ed544e495ea0312eeefa37`. The replay figures below were
taken at `48aeb3cef`. `git diff --stat 48aeb3cef 7d659d602 -- custom_components
tests/replay.py tests/hastub tests/stress.py` is empty, so nothing the lane
reads changed between the two heads.

## Mutation proof

The only production line is the `loop_cpu_ratio` literal in `COST_BUDGETS`.
Each arm runs through the lane's own `cost_offenders`, fed the full cost line
from the 2026-10-21 red run (`cpu_ratio 1.7194, peak_kib 1911.6,
loop_cpu_ratio 0.1138`):

- Head (0.120): no offender.
- Mutant cap 0.111 (main's value): `loop_cpu_ratio 0.1138 over its budget
  0.111`, which is the red.
- Mutant cap 0.25: `loop_cpu_ratio 0.1138: budget 0.25 cannot see a 2x cycle;
  re-record 0.1609`. The lowest reading doubled (0.1704) is no longer seen,
  so a padded cap goes blind.

On the head, the lane's own loop-doubled arm (`replay_one(..., "loop")`) read
`loop_cpu_ratio 0.2024 over its budget 0.12`. The clean arm read 0.0896 with
no offender.

## Null control

Main's tree, with the budget unchanged at 0.111, measured three times on this
box: 0.0869, 0.0854, 0.0859. All are inside main's own band, so the
unmodified tree is green here. The defect is the CI fast-class row, not a
local one. The same tree on CI reads 0.1138 (run 39563978649 at `c77f89dc6`,
whose `custom_components/` matches `df6ca4bc6`). The commits behind the green
CI rows (`e3f3b312f`, `c35302773`) read 0.0823-0.0933 on this box in the same
interleaved rounds, the same range as the tip. The figure is flat across the
code and moves with the runner.

## Figures

- The CI series, split by ruler era and class:
  `python3 dev/audit/harnesses/r10_replay_loopnorm.py --series` prints
  `new_post_spread=min0.0868_max0.1138_factor1.311 median=0.0930` and
  `corr_new_post_ref_ms=-0.719 n=6`, and `worst_post run=39563978649
  new=0.1138 loop_cpu_ms=9.04 loop_ref_ms=79.44` (0 API failures).
- The memory-arm noise band: each slow job prints `memory doubled: cost {...}`
  beside its clean line (`gh run view <run> --repo tvofi/heatpump_optimizer
  --job <job> --log`). Clean/memory pairs: 0.0868/0.0877, 0.0875/0.0852,
  0.0877/0.0868, 0.0982/0.1030, 0.1114/0.1162, 0.1138/0.1081. The largest
  deviation is 5.0 % (0.1081 against 0.1138, job 119101702593). The memory
  arm adds ballast only on the odd tracemalloc cycles, which are never
  timed (`inject_cost`), so its loop figure is a second reading of the same
  quantity.
- The interleaved bisect, three rounds at each of `e3f3b312f`, `c35302773`,
  `e8c67e1d3`, `0c298f6b5`, `df6ca4bc6` (a detached worktree each, order
  rotated per round, load average 30-60). From each root:
  `python3 -c "import sys,json; sys.path[:0]=['tests','tests/hastub']; import replay; R=type('R',(),{'check':lambda *a: True})(); print(json.dumps(replay.replay_one(R, replay.FIXTURES/'synthetic-dhw-only.json', None, None)['cost']))"`.
  Readings: e3f3b312f 0.0837, 0.0823, 0.0915; c35302773 0.0893, 0.0933,
  0.0918; e8c67e1d3 0.0910, 0.0878, 0.0887; 0c298f6b5 0.0895, 0.0873, 0.0871;
  df6ca4bc6 0.0869, 0.0854, 0.0859. All 15 runs read 0.0823-0.0933.
- The head's arms: the same command at the head, then with `"loop"` for the
  last argument. They print `loop_cpu_ratio 0.0896` with `[]`, and `0.2024`
  with `['loop_cpu_ratio 0.2024 over its budget 0.12']`.
- The band at the head, every recorded reading and its doubling:
  `python3 -c "import sys; sys.path.insert(0,'tests'); import replay; b=replay.COST_BUDGETS['synthetic-dhw-only.json']; print([(v, replay.cost_offenders({'loop_cpu_ratio':v}, b), replay.cost_offenders({'loop_cpu_ratio':2*v}, b)) for v in (0.0852,0.0868,0.0875,0.0877,0.0982,0.103,0.1081,0.1114,0.1138,0.1162,0.0618,0.0823)])"`.
  Every reading is clean, and every doubling (lowest 0.1236) is over 0.12.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

`nightly-status` and `delivery-status` grade `main`, not this branch.
`nightly-status` is red because of the defect this pull request answers: the
`slow` lane's `loop_cpu_ratio` over 0.111 on runs 39387919507 and
39563978649. The cheaper detector is the lane's own per-run `cost_offenders`
check, which is the one that found it. It costs nothing extra (it reads the
cost line the same job has just measured), and no cheaper one exists, because
the defect only appears on a fast-class CI runner. `nightly-status` stays red
until the first scheduled run after this merges.

## Forward-carry

- When R10-REPLAY-LANE records the real-day fixture's `loop_cpu_ratio`
  budget, it must record it from both CI runner classes, not from local runs
  or one class. The pure-Python ruler leaves a residual class factor of about
  1.28x: the fast class (`loop_ref_ms` about 80) reads 0.111-0.116, the slow
  class (128-161) reads 0.085-0.103, and corr with `ref_ms` is -0.72 over
  n=6. Removing that factor (a ruler with the loop's memory profile, or a
  per-class band) is what lets 0.120 re-centre down. Lands in the R10-REPLAY-LANE
  group's `carry` in `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-REPLAY-LANE

## Friction

none
