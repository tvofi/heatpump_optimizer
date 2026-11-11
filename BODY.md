R10-HOTFIX-REPLAY-CLASS-CUT: the scheduled nightly at d08ed31049 (run 42934263129, job 130240315059) read the synthetic clean cpu_ratio 1.7266 at a job ruler of 40.22 ms (class ref40), under the floor 1.9937 of the ref40 budget 3.9874, which rested on two draws of 2026-11-04/05 (2.7594, 2.8809). Both predate 17bb738485 (one BLAS ThreadpoolController, #3349), which cut the cycle's CPU on CI's runners to 0.61-0.66x. An improvement, not a regression.

Every class is re-recorded one-sided down. tests/replay_cost_draws.tsv gains job 130240315059's rows, and COST_CUTS declares the cut (17bb738485, from 2026-11-08T17:14:34Z, factor 0.6339, the geometric midpoint of CI's 0.6124 at ref40 and 0.6562 at ref47). cost_draws projects every pre-cut synthetic cpu_ratio by that factor.

Per class, old -> new synthetic cpu_ratio budget: ref23 3.7539 -> 2.3796; ref28 3.189 -> 2.0215; ref31 3.2877 -> 2.0841; ref38 3.4579 -> 2.192; ref40 3.9874 -> 2.5112; ref47 2.7713 -> 2.1188; ref53 2.076 -> 1.316. No budget rises; bands, the flat loop_cpu_ratio 0.1527 and the owner fixture's budgets do not move.

Countermeasure (R10-RCA-REPLAY-CLASS-RERECORD, state c): level_shift_offenders, the cycle_cost:level_shift control, names any class that rests wholly on draws before a shift another class shows. field_coverage.mjs registers the cut as the replay_cuts arm.

Closures were skipped locally (`PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh`, owner ruling on record); CI's closures job records them. Locally, the closures recording reported tests/entities.py and tests/features.py failures inside prepr; features.py fails identically at the merge base on the combi census, and entities.py passes alone at the head.

## Head

bd93b5634bd7cd9cb7614121132b1597966154fc

## Mutation proof

Dropping the COST_CUTS entry (no projection of pre-cut draws) turns the level_shift control and the per-class budget re-derivation checks in tests/replay.py red: ref40 is centred on pre-cut readings again and the budget returns to 3.9874. Doubling the cpu arm stays over the new ref40 budget (3.5914 > 2.5112).

## Null control

The unmodified tree keeps the ref40 budget 3.9874, whose floor 1.9937 sits above the post-cut clean 1.7266, so the nightly reads a false cpu regression. An A/A interleave (17bb738485^ against itself, 6 pairs) reads 1.0090.

## Figures

- 0.6339 / 0.6124 / 0.6562: python3 tools/audit/seat/replay_draws.py parse
- 2.2978 -> 2.0026, 0.8715x on one 4-core box, 12 pairs: python3 tools/audit/seat/replay_draws.py interleave
- level shift over the table: python3 tools/audit/seat/replay_draws.py shift

## Red checks

none owned by this change. If they show, `tests / fast (3.14)` (combi census, fixed by PR #3466) and `governance / instrument-self-tests` (fixed by R10-HOTFIX-PUSHER-CENSUS) are main's, not this diff's.

## Forward-carry

- Carry 1 (the replay class re-record RCA, state c) is answered in part. Built here: the `cycle_cost:level_shift` control over tests/replay_cost_draws.tsv (`level_shift_offenders` prints the classes examined; a planted-shift null control sits in tests/replay.py), the declared cut (COST_CUTS, factor 0.6339, with its interleaved evidence), and its registration as the `replay_cuts` arm in tools/policy/field_coverage.mjs. The RCA write-up is not in this diff: its source text, the orchestrator's session scratch, was out of this seat's reach, and the red/green demonstration across the three historical tables was not re-run here. Carry: R10-HOTFIX-REPLAY-CLASS-CUT | dismissed: RCA write-up needs orchestrator scratch text unavailable to this seat

## Friction

none
