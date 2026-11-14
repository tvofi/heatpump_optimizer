# Appendix C: candidates and cost tests (R11-PRE-PARALLEL-PIPELINE)

Baseline figures are `BASELINE.md`'s (B-ids). Two replays carry the cost test;
each prints its own null control.

- **R-pipe**: `harness/replay_pipeline.py [proof wall in minutes ...]`, over
  the recorded 215 merges. Kept from the record: each pull request's verdicts,
  the first green `ci.yml` run at its reviewed head, its merge time, and
  whether main's `gate` went red at its merge. Output: `out/replay_pipeline.txt`.
- **R-prog**: `harness/replay_programme.py`, which runs `tools/plan/replan.py`
  over round 10's whole roster (495 groups, every one reset to not-started, 20
  slots, coordinator cap 3, fixed start) and applies a candidate only as an
  edit to the measured terms of `tools/plan/durations.json`. Output:
  `out/replay_programme.txt`.

## Figures

| id | figure | literal | enumerator |
|---|---|---|---|
| C-null-1 | R-pipe, today's rules on the same data | 7.60 h, equal to B6 | R-pipe, line "today" |
| C-null-2 | R-prog, unedited durations; an edit to a term the planner does not read | 714.05 h; 714.05 h | R-prog, first two lines |
| C-floor | first merge verdict to "approved and green at the reviewed head" | mean 2.50 h, p50 0.24 h, p90 4.15 h | R-pipe, line "floor" |
| C-floor-s | the same when the 74 heads with no recorded green take the p75 of the recorded waits | 2.84 h | `FALLBACK_Q=.75` R-pipe |
| C1-wall | C1, first merge verdict to main, proof wall 45 / 60 / 75 / 105 min | 3.45 / 3.67 / 3.88 / 4.33 h | R-pipe, lines "C1" |
| C1-proofs | C1, batch proofs added per window | 84 to 102 | R-pipe |
| C2-land | C2, first merge verdict to landed | 2.50 h at every proof wall | R-pipe, lines "C2 ... landed" |
| C2-lag | C2, main lags a landing by, mean / p90 / max, at 45 / 60 / 75 / 105 min | 1.12 / 1.62 / 2.19; 1.67 / 2.43 / 5.53; 2.29 / 3.08 / 7.78; 4.24 / 10.14 / 17.53 h | R-pipe, lines "main lags" |
| C2-proofs | C2, proofs for the 215 changes at 45 / 60 min, bisection proofs among them | 149 (2) / 134 (8) | R-pipe |
| C2-culprit | C2, culprit known after, mean / max, at 45 / 60 min | 1.28 / 1.68 h; 2.38 / 4.18 h | R-pipe |
| C2-worst | C2 with all 20 reds treated as real, 60 min: lag mean / max, proofs | 2.29 / 9.53 h, 173 | `ALL_REAL=1` R-pipe |
| P-C1 | R-prog, C1 (first-round hours less 3.0 and 3.4 h) | 645.93 and 636.72 h: -9.5 % and -10.8 % | R-prog |
| P-C2a | R-prog, C2 taken off first-round hours (5.1 h) | 599.60 h: -16.0 % | R-prog |
| P-C2b | R-prog, C2 taken as review turns removed (extra rounds x 0.71) plus 2.2 h | 572.68 h: -19.8 % | R-prog |
| P-B11 | R-prog, the assumed round-11 baseline | 551.40 h | R-prog |
| P-B11-C1 | on it, C1 | 473.08 h: -14.2 % of P-B11 | R-prog |
| P-B11-C2 | on it, C2 | 435.20 h: -21.1 % of P-B11 | R-prog |
| P-B11-C4 | on it, the repair round at 2.5 h | 485.92 h: -11.9 % of P-B11 | R-prog |
| P-B11-C2C4 | on it, both | 373.87 h: -32.2 % of P-B11 | R-prog |
| P-slots | R-prog, 26 slots, nothing else changed | 703.72 h: -1.4 % | R-prog |

## What each replay assumes

R-pipe.
- A change is ready when it holds a merge verdict and a `ci.yml` run at the
  reviewed head has concluded success. 141 of 215 have that run on record; the
  other 74 take the median of the recorded waits (C-floor-s gives the p75).
- A pull request blocked after its first approval keeps its real repair: its
  clock runs from its last merge verdict. 22 such blocks are kept.
- Red: the recorded red-streak starts (B19). One red followed by green at the
  next merge with no fix between is treated as transient and costs half a
  proof wall for a re-run of the failed jobs; the others are bisected over
  prefixes, three prefix proofs in parallel a round, the culprit evicted and
  kept on today's clock. C2-worst treats all as real.
- One proof at a time; a proof covers every change landed when it starts.
- C1: an entry in a serial class waits for the next batch proof; a batchable
  entry merges when ready; claim and conflict entries (15) keep today's time.
- The proof wall is an input, not a result. B22 gives its range. R-pipe does
  not model the wall falling as load falls.

R-prog.
- The planner's own model: a group's hours are first-round hours plus extra
  rounds times the hours of a round; 20 slots; the roster's `after` edges.
- A candidate's saving is applied once per group, though a group with several
  parts saves it per pull request: conservative.
- The round-11 baseline is ASSUMED, not measured: the R11-PRE groups are
  taken to cut extra rounds to 0.77 (B11's mechanical classes), a round from
  5.65 to 4.0 h, and the first round by 1.0 h. C4's 2.5 h round is likewise an
  assumption between B9's mean and its p10 plus review.

## The cost test, per candidate

| | C1 heads stop moving | C2 integration branch with promotion | C4 repair-loop requirements |
|---|---|---|---|
| programme wall clock, round 10 replayed | P-C1 | P-C2a to P-C2b | not replayed on round 10's baseline alone beyond a 4.15 h round: 630.03 h, -11.8 % |
| programme wall clock, assumed round-11 baseline | P-B11-C1 | P-B11-C2 | P-B11-C4; with C2, P-B11-C2C4 |
| hours a change, approval to slot freed | B6 less C1-wall: 3.3 to 4.2 h | B6 less C2-land: 5.1 h (4.8 h under C-floor-s) | 1.5 h a round, assumed |
| CI runner-minutes (estimate from B23's class costs times this window's counts) | about -10 %: -19 % for runs no longer invalidated or cut by a merge of main, +9 % for C1-proofs at 197 runner-minutes each | about -33 % with the push run at a proved sha skipped; about -19 % without the skip | none |
| review turns | fewer re-issued verdicts, not counted | -78 of 481 (B7), -16 % | none |
| main red starts | unchanged (B19) | 0 by construction: a red proof does not move main | none |
| right-first-time | unchanged | the 22 post-approval blocks become reds of a proof or vanish | the lever is the PRE groups' |
| tokens | not measured: no token ledger exists yet (R11-PRE-TOKEN-LEDGER); proxy is review turns | same proxy | same |
| new standing machinery | one refusal in three instruments | one branch, one state file, a proof scheduler, a bisector, one promotion writer, one audit job | one enumerator |
| failure modes added | a stale-base head merges and reddens main as today | an instrument defect can move main (see the note's section 4); a rebuild changes merge shas of unproved landings; a stamp must order against a promotion | none |
| build | 2 groups, S and S | 3 more groups, L, M and S | carries to 4 existing groups |

## Against the bar (over 20 % on a measured baseline with a null control)

- **Cleared by measurement:** CI runner-minutes under C2 with the push-run
  skip (about -33 %, an estimate built from measured class costs and measured
  counts, not a replay of jobs), and main red starts (24 to 0, by
  construction). Without the skip C2's CI figure is about -19 %: under the bar.
- **Reached only under an assumption:** programme wall clock. Replayed on
  round 10: 16.0 % to 19.8 %, under the bar. On the assumed round-11 baseline:
  21.1 %. With C4's requirements met: 32.2 %, an estimate.
- **The weakest assumption** is C-floor: that a head approved and green lands
  with no further wait. It rests on 141 recorded green times and a median for
  the other 74. At the p75 (C-floor-s) the saving is 4.8 h a change and P-C2a
  reads 604.43 h, -15.4 % (`out/replay_programme_floor_p75.txt`). The second weakest is the proof wall: at
  105 min (B22's worst days) landing is unaffected and main trails by 4.2 h
  mean, 17.5 h max (C2-lag).
- **C1 alone does not clear it** on any measure.
