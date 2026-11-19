# RCA: a solve-only adjustment published as currency

Seat: round-11 root-cause, class `N-objective-as-money` (production). Instances R11 4, 4 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P8`) as one (`fold_ledger.py` `_group_counts`): `N-entity-metadata`, `N-missing-unit-scale`, `N-objective-as-money`, 7 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

The optimizer's `_Horizon` carries one price series. With `price_risk_lambda > 0` that
series is the risk-adjusted one, and everything priced from it inherits the premium:
`predicted_cost`, `baseline_cost`, the deferred cost, the start-gap cost and the published per-step
prices. A figure no meter bills is published as currency, and the saving is inflated by 12.46 at
lambda 1 (25.06 at the maximum). The sweep adds the DHW planner's baseline economics. The type
cannot tell a solve weight from a bill.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s3-01` (weakened, medium): planted copy: savings_inflation_lambda1_price_risk=12.4574, max 25.0586 currency; perturb -> 0; perturbation: --perturb-raw: the risk premium stays in the solve, the published figures are priced on the raw series.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m3_risk.py` took 3.0 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-objective-as-money.json`) lists 4 seams. The ledger carries 3 of the seams as instances beyond the finding. Its enumerator is cited as `python3 -I dev/audit/rounds/round11/D14/enum_objective_as_money.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

The D2 brief states the invariant itself: `predicted_cost == Σ price·power·dt on every golden
fixture` (`dev/governance/dimensions/D2.md:35`). Round 10's D2 s3 seat ran it. The golden fixtures
run `price_risk_lambda` at its default 0, where the adjusted and raw series coincide, so the
invariant held. The step was followed, and its inputs could not express the class.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 4 instances over the 148 releases they accumulated in, 0.027 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.027 x 15660 s | 423 s/release |
| form | an invariant `tests/` arm: with `price_risk_lambda > 0`, every published cost equals the sum of raw price x power x dt |
| catch share q | 1.0: the invariant reads the published outputs, so any figure priced off the adjusted series fails it |
| expected benefit, q x cost | 423 s/release |
| arm time | 3.0 s (`dev/audit/rounds/round11/D2/s3/m3_risk.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 49 s/release |
| verdict | passes by 8.7x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The structural fix keeps the raw series beside the adjusted one in `_Horizon` and prices the
published figures on it. The arm must show 12.46 on this baseline and 0 after the fix. The fix PR
owns both.
