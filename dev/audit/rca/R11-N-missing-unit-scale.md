# RCA: a recognised unit whose scale factor is never applied

Seat: round-11 root-cause, class `N-missing-unit-scale` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P8`) as one (`fold_ledger.py` `_group_counts`): `N-entity-metadata`, `N-missing-unit-scale`, `N-objective-as-money`, 7 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`inputs.normalize_price_per_kwh` recognises every unit in `PRICE_MINOR_UNITS` (ore, cent)
and returns `value*per_kwh` without the /100. An ore/kWh price series is therefore read as major
currency, 100x too high, on every install with a minor-unit price entity (critical). The branch was
added with `PRICE_MINOR_UNITS` (`56cb00279`, 2026-09-24). `tests/features.py`'s `_P8_FACTORS`
check already states the factor contract.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s3-02` (verified, critical): planted copy: unit_mismatches=8; --perturb minor -> 0; perturbation: --perturb minor: normalize_price_per_kwh divides a minor-unit result by 100 (the documented factor).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m4_tariff.py` took 22 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-missing-unit-scale.json`) lists 0 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/N-missing-unit-scale/enumerate.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

A check of this contract exists, `tests/features.py`'s `_P8_FACTORS`, and it is green. It
checks the declared factors. It does not drive `normalize_price_per_kwh` with a minor-unit input,
so the branch that drops the factor is never executed under it. The check was followed and its
unit was the table, not the function. D2's step on currency conversion
(`dev/governance/dimensions/D2.md:45`) ran in round 10 (D2 s3) and did not drive the minor branch
either.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | extend `tests/features.py`'s `_P8_FACTORS` check to call `normalize_price_per_kwh` for every unit in `PRICE_MINOR_UNITS` and the energy prefixes |
| catch share q | 1.0: the arm drives every declared unit through the function that applies it |
| expected benefit, q x cost | 106 s/release |
| arm time | 0.1 s (an estimate: a few pure-function calls inside an existing script) |
| standing cost, arm x 16.3 PRs | 1.6 s/release |
| verdict | passes by 65.0x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The extension must show 8 unit mismatches on this baseline and 0 after the fix. It costs
almost nothing, because it adds calls to a script that already runs. The fix PR owns it.
