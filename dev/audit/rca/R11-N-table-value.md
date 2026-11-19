# RCA: a wrong constant in a production data table

Seat: round-11 root-cause, class `N-table-value` (instrument). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I5`) as one (`fold_ledger.py` `_group_counts`): `N-comment-style`, `N-orphan-doc`, `N-table-value`, 103 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`presets.derive`'s `house_heat_loss_coefficient` is not monotone in building era.
`low_energy` (0.85 W/m2K) is above both `post_2005` (0.55) and `1980_2005` (0.80), so a low-energy
house is modelled 1.55x leakier than a post-2005 one in every cell (36 of 36). The table dates from
the presets module's first commit (`df7db8215`, 2026-08-22). No test reads its values against an
ordering or a source.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s1-51` (verified, medium): verifier: 36 of 36 cells derive 1.55x the post-2005 heat loss for 'low energy'.

The finding arrived as a converted lead with no finder harness. The judge used the verifier's executed number, and this seat has no harness to re-run.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-table-value.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/table_value/enumerate.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

D2 checks the formulas. A table's literal values sit outside every brief step and every test.
The finding arrived as a converted lead in this round and was judged on the verifier's executed
number.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier checking production tables against an oracle |
| catch share q | 0.1: the sweep enumerated 37 module-level numeric tables, and an oracle exists only where an ordering or a source is known; it found no second wrong value |
| expected benefit, q x cost | 11 s/release |
| arm time | 0.5 s (an estimate for an ordering check over the enumerated tables) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 1.3x |

### Decision not to build a class barrier

Decision: no class barrier. The fix corrects the coefficient and pins the era ordering in
its own regression test, which is the one oracle this table has. A general table oracle needs a
reference per table that the tree does not hold.

The cost test passes (passes by 1.3x) only on a catch share this seat estimated rather than measured, and the margin is inside that estimate's error. The refusal rests on the reason above, not on the arithmetic.
