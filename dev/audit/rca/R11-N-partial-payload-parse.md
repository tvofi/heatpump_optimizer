# RCA: a parser that drops a sibling part of the payload

Seat: round-11 root-cause, class `N-partial-payload-parse` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P6`) as one (`fold_ledger.py` `_group_counts`): `N-dead-input`, `N-partial-payload-parse`, 3 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`price_model.prices_from_tibber_payload` iterates `period in ('today',)`. Tibber delivers
`today` and `tomorrow` (96+96 quarter rows), so the parser returns 96 rows, and a plan solved at
14:00 knows 40 of its 96 steps. The rest comes from the learned prior. The parser's fixture held
`today` only, so its tests could not see the missing half.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s3-03` (verified, high): planted copy: tibber_rows_dropped=96, known steps at 14h 40; --perturb tomorrow -> 0 dropped, 96 known; perturbation: --perturb tomorrow: the parser also folds priceInfo.tomorrow.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m4_tariff.py` took 22 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-partial-payload-parse.json`) lists 0 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/sweep_partial_payload.py [PACKAGE_DIR]`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D1's parser step (`dev/governance/dimensions/D1.md:56-58`) and D2's price-folding step
(`D2.md:42-43`) both cover this parser, and round 10's D2 s3 seat ran over the tariff chain. No
round-10 record reports a two-period payload. The steps were followed, and none of their inputs
carried the `tomorrow` part Tibber sends after about 13:00.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier over external-payload parsers |
| catch share q | 0.0: the sweep found 0 further seams; a dropped sibling is visible only against a fixture with the producer's full shape, which is per producer |
| expected benefit, q x cost | 0 s/release |
| arm time | 22 s (`dev/audit/rounds/round11/D2/s3/m4_tariff.py` (shared with N-missing-unit-scale and N-inverted-aggregate), re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 361 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. The fix iterates both periods and tests a two-period payload,
which is the guard. A parser for a new producer gets the same full-shape
fixture under the existing fix protocol, so no new rule is needed.
