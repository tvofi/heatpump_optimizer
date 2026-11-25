# RCA: a tie broken by set iteration order

Seat: round-11 root-cause, class `N-unordered-tiebreak` (instrument). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I4`) as one (`fold_ledger.py` `_group_counts`): `N-instrument-locator`, `N-unordered-tiebreak`, `N-untranslated-splice`, 11 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`plan_slots` names a slot's reason with `max(set(codes), key=codes.count)`. On a 2:2 tie the
winner is whichever code set iteration yields first, and that order depends on `PYTHONHASHSEED`.
The same plan publishes two different reasons across seeds 1-12. The plan itself is unchanged; only
the label moves. The idiom reads as deterministic and is not.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D1-s1-51` (verified, low): verifier: distinct_tie=2 over PYTHONHASHSEED 1..12 (null 1, perturb 1).

The finding arrived as a converted lead with no finder harness. The judge used the verifier's executed number, and this seat has no harness to re-run.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-unordered-tiebreak.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/unordered_tiebreak.py custom_components`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

No brief asks whether a published choice is stable across hash seeds, and no test runs under
more than one seed. The finding arrived as a converted lead in this round and was judged on the
verifier's executed number (2 distinct reasons over 12 seeds, null 1).

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a static `tests/` arm refusing `max`/`min` over a `set(...)` with a `key=` |
| catch share q | 0.1: the shape-matcher sees one idiom; the sweep's walk over the package found 1 seam, the instance, and a tie broken by dict, set or `sorted` on a partial key takes other spellings |
| expected benefit, q x cost | 11 s/release |
| arm time | 0.5 s (an estimate for one AST pass) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 1.3x |

### Decision not to build a class barrier

Decision: no class barrier. The fix (break the tie on a declared order, `sorted(set(codes),
key=...)` with a secondary key) carries its own regression test, run under two seeds. The
benefit side would justify an arm only if it caught more than the one idiom, and nothing
measured says it would. The effect is a label, not a plan. Re-open if a second instance appears
in another spelling.

The cost test passes (passes by 1.3x) only on a catch share this seat estimated rather than measured, and the margin is inside that estimate's error. The refusal rests on the reason above, not on the arithmetic.
