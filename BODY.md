# Summary

The nightly `slow` lane's replay check went red on 2026-10-20: `loop_cpu_ratio
0.1114 over its budget 0.111` (run 39387919507, job 118512165515). #2339
re-centred this cap at 0.111 from twelve pre-era local runs; the nightly
`slow` series has since produced five post-era rows — 0.0868, 0.0875, 0.0877,
0.0982, 0.1114 — so the top row is over the cap and the median has moved up.

This raises only `loop_cpu_ratio`, 0.111 -> 0.124: sqrt(2) x the median 0.0877,
the smallest cap covering every post-era row. `cpu_ratio` (2.173) and
`peak_kib` (2686.0) are untouched, because neither is failing and a raise
without a measurement is padding. Part of #2272.

`tests/replay.py` is code-owned, so tvofi reviews this at merge.

## Approval

tvofi, 2026-10-20, after being shown the two measured options: **"yes, raise
the caps"**, with `0.124` recommended and `0.1575` offered as the alternative.
The confirmation was obtained before this branch was pushed, as `CLAUDE.md`
rule 2 requires.

Measured value `0.124` = sqrt(2) x the median (`0.0877`) of the five post-#2339
rows; the largest-record alternative, sqrt(2) x 0.1114 = 0.1575, also covers
every row but moves the 2x detection floor from 0.062 to 0.0788, reddening more
local runs for headroom the series does not need. Known margin, recorded in
the comment beside the value: the 2x floor becomes 0.062, 0.3 % above a
twelve-run local minimum of 0.0618, so a local run reading at that floor reds
on "cannot see a 2x" while the CI rows stay inside the band. Rollback: restore
`0.111`.

## Head

`38aec7bf09e0f757dfe4f718f52fb655f99964ce` (branch `handoff/r10-replay-cap`),
measured at merge base `e4d47457be15ebd993e11bd10d809ce269ff40ac`.

`tools/pr/prepr.sh` was run with `PREPR_SKIP_CLOSURES=1` under the owner's
ruling of 2026-10-20: the closures re-derivation step is skipped for this
handoff, and every other prepr step passes.

## Mutation proof

The fix's only production line is the budget literal in `COST_BUDGETS`
(`tests/replay.py`); the comment beside it carries the rule that produced it.
Both the base and the mutants are driven through the lane's own
`cost_offenders`, fed the full cost line the 2026-10-20 nightly printed.

At the base (cap 0.111) the recorded red row is over:

    loop_cpu_ratio 0.1114 over its budget 0.111

At the head (cap 0.124) the same row is clean: no offender.

Mutation 1, cap restored to 0.111 in a copy: the recorded row reds again with
`loop_cpu_ratio 0.1114 over its budget 0.111`.

Mutation 2, cap set to 0.25 in a copy: the 2x arm can no longer see the
doubling of the lowest row (0.0868 x 2 = 0.1736 < 0.25), which reports no
offender, and the clean row reds on the band instead:
`loop_cpu_ratio 0.0868: budget 0.25 cannot see a 2x cycle; re-record 0.1228`.

## Null control

The unmodified tree at the base is red on the recorded CI row, above, and
green on this box: the lane's own clean run reads 0.0961 against 0.111 (base
lane 524.2 s wall, head lane 485.1 s, load1 83-140 at launch), and the head's
clean run reads 0.1096 against 0.124, so the defect the body answers is the CI
row, not a local one. At the head's cap the 2x arm still fires on every post-era row
doubled: 0.1736, 0.175, 0.1754, 0.1964, 0.2228, each over 0.124, and the
head's own loop-doubled arm reads 0.1870. Mutation 2 above is the other end of
the same control: a cap past the doubling makes the arm blind.

## Figures

- The five post-#2339 rows, their median and the construction:
  `python3 -c "import math; v=[0.0868,0.0875,0.0877,0.0982,0.1114]; s=sorted(v); print(s, s[2], math.sqrt(2)*s[2])"`
  prints `[0.0868, 0.0875, 0.0877, 0.0982, 0.1114] 0.0877 0.124027...`,
  rounded to the recorded 0.124.
- The head's clean lane run under the raised cap:
  `PYTHONPATH=tests/hastub python3 tests/replay.py` prints `48 cycles over 81
  entities in 115.9 s; cost {... 'loop_cpu_ratio': 0.1096 ...}` (load1 83 at
  launch, rising to ~125) and `ALL 93 replay checks PASSED`; its loop-doubled
  arm reads 0.1870, over 0.124.
- The base's clean lane run, at merge base `e4d47457be` on this box:
  `PYTHONPATH=tests/hastub python3 tests/replay.py` printed `48 cycles over 81
  entities in 87.4 s; cost {... 'loop_cpu_ratio': 0.0961 ...}` (load1 140 at
  launch) and `ALL 93 replay checks PASSED`; its loop-doubled arm read 0.1799,
  over 0.111.
- The recorded red row: `gh run view 39387919507 --repo
  tvofi/heatpump_optimizer --job 118512165515 --log` prints `FAIL
  synthetic-dhw-only.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1114
  over its budget 0.111]`.
- The recorded CI row through the lane's own check, at the base and the head:
  `python3 -c "import sys; sys.path.insert(0,'tests'); import replay; b=replay.COST_BUDGETS['synthetic-dhw-only.json']; print(replay.cost_offenders({'cpu_ratio':1.9479,'peak_kib':1913.5,'loop_cpu_ratio':0.1114}, b))"`
  prints the offender at the base's 0.111 and `[]` at the head's 0.124; the two
  mutations are this command with the map's value substituted (0.111, 0.25).
- The other four rows, same command with each job id: run 39011974246 job
  117336255624 reads 0.0868; run 39106988523 job 117614882824 reads 0.0875;
  run 39218718759 job 117948683617 reads 0.0877; run 39256093598 job
  118071730008 reads 0.0982.

## Red checks

The nightly `slow` job's 2026-10-20 red — run 39387919507, job 118512165515,
`loop_cpu_ratio 0.1114 over its budget 0.111` — is the defect this answers.
The cheaper detector is the lane's own per-run `cost_offenders` budget check,
which is the one that found it: it runs inside the same job, reads only the
cost line it has just measured, and needs no second run. No other check turned
red on this branch.

## Forward-carry

none

## Friction

none
