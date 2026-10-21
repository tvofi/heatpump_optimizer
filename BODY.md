# Summary

The nightly `slow` lane has been red on main two nights running on one replay
check: `loop_cpu_ratio 0.1114 over its budget 0.111` (run 39387919507,
2026-10-20) and `0.1138 over its budget 0.111` (run 39563978649,
2026-10-21). That red is what `nightly-status` reports on every open pull
request. Part of #2272. `tests/replay.py` is code-owned.

This raises only `loop_cpu_ratio`, from 0.111 to **0.143**. That is the centre
of the figure's spread across every environment measured so far, recorded by
the rule `COST_BUDGETS` already uses for `cpu_ratio`.

**Round 2.** The first review blocked 0.120 (claim-refuted). On an idle
4-core Linux box, the head's own lane read 0.1206, with its memory arm at
0.1236. That box's ruler (172-190 ms) is slower than either CI class, so two
things the round-1 body relied on were wrong. First, the ratio is not set by
ruler speed. Second, 5.0 % (a clean/memory pair within one job) is not the
run-to-run spread. This head drops both:

- **The figure moves with the box, not the code.** The bisect is unchanged:
  three interleaved rounds on one box at each of five main commits, from
  `e3f3b312f` (the first post-#2339 nightly row) to `df6ca4bc6`, gave medians
  0.0837-0.0918 with no trend. `custom_components/` has not changed since.
  What does move it is the environment. I took 44 clean and memory-arm
  readings of the current loop code in four environments:
  - CI rows at `loop_ref_ms` 128-161: 0.0852-0.1030
  - CI rows at 79-84: 0.1081-0.1162
  - a loaded M1 (load average 30-60): 0.0823-0.0933
  - the reviewer's idle box: 0.1089-0.1236

  Across all four they read 0.0823-0.1236, a factor of 1.50. I did not find
  which property of the box sets the figure. Ruler speed does not predict it
  out of sample, and I am not claiming any other cause.
- **The cap comes from the spread between environments.** sqrt(2) x the
  geometric midpoint of 0.0823 and 0.1236 is 0.143. The largest reading sits
  13.6 % under the cap, the smallest 15.1 % over the floor (0.0715), and the
  smallest reading doubled 15.1 % over the cap.
- **Out of sample.** I left out each environment in turn and centred on the
  other three. That gives caps of 0.138-0.145, and the left-out environment
  has no offender under its cap (0 of 8, 4, 16, 16). The two earlier caps
  were each sized on fewer boxes and failed the next one: 0.111 reds 15 of
  the 44 readings, and 0.120 reds 3. A fifth run, after the cap was chosen,
  also lands inside: the head's full lane on the M1 at load average about
  550 read 0.0942, all 93 checks passed, and its loop-doubled arm read 0.1649,
  over 0.143.

This is the best a 2x band can do. It holds a spread under 2x, and the
measured spread is 1.50x. A box outside 0.0715-0.143 would red it again,
because what sets the figure is unexplained. The robust form is a reference
measured in the same job, so the box cancels instead of being budgeted. That
change is carried to R10-REPLAY-LANE (Forward-carry).

## Raise justification

The raise is under mandate 6175172275 (scope `all`), once no payment that
improves the code exists. Every payment considered:

1. **Cut loop CPU in the integration.** Not taken. The interleaved bisect
   shows no growth to pay back, and loop-CPU work is roster group
   R10-LOOP-CPU's (after R10-FREQ-DEFROST). A cut would shift every reading
   down but would not narrow the 1.50x spread between environments, which is
   what reds the band.
2. **Keep 0.111.** Not taken: it reds 15 of the 44 readings, including both
   CI red rows.
3. **0.120, the largest CI row plus 5.0 %** (round 1). Refuted by review: it
   reds 3 of the 44, the idle box's 0.1206 among them.
4. **0.124, sqrt(2) x the CI median** (this branch's first value). Not taken:
   it is sized on CI alone and reds the idle box's 0.1236 memory arm.
5. **Redesign the ruler, or keep one band per class.** Not taken. The idle
   box shows ruler speed is not the variable, so a ruler redesigned on that
   model has nothing to cancel. The ruler is also #2270's owner decision.
6. **A paired reference in the same job** (measure the loop against a fixed
   older tree, or against its own doubled arm, on the same runner). This is
   the sound design. Not taken here: it changes what the lane measures and
   what it reports nightly. That is R10-REPLAY-LANE's scope (the lane that
   gates the nightly replay), and this pull request has to keep the nightly
   green in the meantime. Carried there.

Architecture score: dS +0.0000 (NULL), from `python3
tools/audit/archscore/score.py --diff origin/main HEAD`. The change is a test
literal and its comment.

## Head

`a77d0628c8ef9477d0de61dd79a0b9160fa38bcc` (branch `handoff/r10-replay-cap`).
It continues the round-1 PR head `daac94b43` and is merged with `origin/main`
at `03b49e1521a2490335922093c9177aec8f6119d9`. Nothing the lane reads
(`custom_components`, `tests/replay.py` outside the literal and its comment,
`tests/hastub`, `tests/stress.py`) changed between `6961f0663` and that main.

## Mutation proof

The only production line is the `loop_cpu_ratio` literal. Each arm goes
through the lane's own `cost_offenders`, fed the reviewer's red cost line
(`cpu_ratio 1.3732, peak_kib 1917.3, loop_cpu_ratio 0.1206`) and the lowest
reading (0.0823):

- Head (0.143): no offender on either.
- Mutant 0.120 (round 1): `loop_cpu_ratio 0.1206 over its budget 0.12`, the
  reviewer's red.
- Mutant 0.111 (main): `loop_cpu_ratio 0.1206 over its budget 0.111`.
- Mutant 0.165: `loop_cpu_ratio 0.0823: budget 0.165 cannot see a 2x cycle;
  re-record 0.1164`. A cap padded past twice the lowest reading goes blind.

Across all 44 readings: 0.143 has 0 offenders and 0 unseen doublings, 0.120
has 3 offenders, 0.111 has 15, and 0.165 has 1 offender and 1 unseen
doubling. Every recorded loop-doubled arm is over 0.143: CI 0.2616 and
0.2264, the idle box 0.2492, and the M1 0.2024 and 0.1649.

## Null control

The cap rule's null control is leaving one environment out. If the 1.50x
were noise from the one box I measured locally, centring on any three
environments would miss the fourth. It does not: the left-out environment
has no offender in every case. The same test on the earlier rules fails.
0.111 was centred on one box and reds 15 of 44. 0.120 was sized on one CI
class and reds the idle box.

On the code: main with the budget unchanged at 0.111 reds on two
environments, CI's fast rows and the reviewer's base readings 0.1089-0.1121
(of which 0.1118 and 0.1121 are over). It stays green on the M1 (0.0854-0.0869). The
code reads the same at every commit since #2339 (bisect above), so main's
red comes from the box.

## Figures

- The CI series by ruler era: `python3
  dev/audit/harnesses/r10_replay_loopnorm.py --series` prints
  `new_post_spread=min0.0868_max0.1138_factor1.311`,
  `corr_new_post_ref_ms=-0.719 n=6` and `worst_post run=39563978649
  new=0.1138` (0 API failures, no new rows since round 1). The memory arms
  come from each slow job's `memory doubled: cost {...}` line (`gh run view
  <run> --repo tvofi/heatpump_optimizer --job <job> --log`): 0.0877, 0.0852,
  0.0868, 0.1030, 0.1162, 0.1081.
- The idle-box readings come from the round-1 verdict's evidence (`git fetch
  origin probe/rev-2548-a7501349`, `ev/finder_harness_head_n8.txt`,
  `ev/finder_harness_both_ends.txt`, `ev/replay_head_full.txt`), which came
  from the finder's harness and the lane itself. They are eight runs reading
  0.1094-0.1184, six interleaved reading 0.1089-0.1206, the lane's clean
  0.1206 and its memory arm 0.1236.
- The M1 readings are the interleaved bisect, run from each commit's worktree
  root: `python3 -c "import sys,json; sys.path[:0]=['tests','tests/hastub'];
  import replay; R=type('R',(),{'check':lambda *a: True})();
  print(json.dumps(replay.replay_one(R,
  replay.FIXTURES/'synthetic-dhw-only.json', None, None)['cost']))"`. They
  are e3f3b312f 0.0837, 0.0823, 0.0915; c35302773 0.0893, 0.0933, 0.0918;
  e8c67e1d3 0.0910, 0.0878, 0.0887; 0c298f6b5 0.0895, 0.0873, 0.0871;
  df6ca4bc6 0.0869, 0.0854, 0.0859; plus 0.0896 at round 1's head.
- The centre, the edges, the leave-one-out and the per-cap offender counts:
  `python3 -c "import math,sys; sys.path.insert(0,'tests'); import replay; E={'ci128':[0.0868,0.0877,0.0875,0.0852,0.0877,0.0868,0.0982,0.103],'ci80':[0.1114,0.1162,0.1138,0.1081],'m1':[0.0837,0.0823,0.0915,0.0893,0.0933,0.0918,0.091,0.0878,0.0887,0.0895,0.0873,0.0871,0.0869,0.0854,0.0859,0.0896],'idle':[0.1171,0.1175,0.1108,0.1094,0.1184,0.1153,0.1176,0.1155,0.1121,0.117,0.1089,0.1109,0.1118,0.1206,0.1206,0.1236]}; cen=lambda v: round(math.sqrt(2*min(v)*max(v)),3); A=[x for v in E.values() for x in v]; off=lambda c,v: sum(bool(replay.cost_offenders({'loop_cpu_ratio':x},{'loop_cpu_ratio':c})) for x in v); print(len(A),min(A),max(A),cen(A)); [print(k,cen([x for j,v in E.items() if j!=k for x in v]),off(cen([x for j,v in E.items() if j!=k for x in v]),E[k])) for k in E]; [print(c,off(c,A)) for c in (0.111,0.12,0.143,0.165)]"`
  prints `44 0.0823 0.1236 0.143`. Leave-one-out gives `ci128 0.143 0`,
  `ci80 0.143 0`, `m1 0.145 0` and `idle 0.138 0`. The per-cap offender
  counts are 15, 3, 0 and 1.
- The head's full lane on the M1, from the worktree root at load average
  about 550: `PYTHONPATH=tests/hastub python3 tests/replay.py` prints `cost
  {... 'loop_cpu_ratio': 0.0942 ...}`, `memory doubled: ... 0.0862`, `loop
  doubled: ... 0.1649` and `ALL 93 replay checks PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

At round 1's head every check concluded green, skipped or neutral, except
`nightly-status`. `nightly-status` and `delivery-status` grade `main`.
`nightly-status` is red because of the defect this pull request answers: the
`slow` lane's `loop_cpu_ratio` over 0.111 on runs 39387919507 and
39563978649. The cheaper detector is the lane's own `cost_offenders` check,
which found it at no extra cost (it reads the cost line the same job just
measured). No cheaper one exists, because the defect only appears on a
runner whose environment reads high. It stays red until the first scheduled
run after this merges.

## Forward-carry

- R10-REPLAY-LANE must not record a `loop_cpu_ratio` budget for the
  real-day fixture from one environment. The same code reads 0.0823-0.1236
  (1.50x) across four environments, and ruler speed does not predict it: an
  idle 4-core box with a 172-190 ms ruler reads 0.109-0.124. Either record
  at the centre of a spread measured in at least the two CI classes plus one
  box outside them, or replace the absolute band with a reference measured
  in the same job (the loop against a fixed tree, on the same runner) so the
  box cancels. Until then, 0.143 holds only the 1.50x measured here. Lands
  in the R10-REPLAY-LANE group's `carry` in
  `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-REPLAY-LANE

## Friction

none
