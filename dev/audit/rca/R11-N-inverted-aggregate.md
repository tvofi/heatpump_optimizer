# RCA: an aggregate taking the wrong order statistic

Seat: round-11 root-cause, class `N-inverted-aggregate` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P2`) as one (`fold_ledger.py` `_group_counts`): `N-duplicated-rule`, `N-entry-data-placement`, `N-inverted-aggregate`, `N-mode-coupled-write`, `N-wrong-law`, 8 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`tariff._one_per_day` kept an entry when `kw < best[day]`, so under `distinct_days` (the
default) PeakTracker recorded each day's smallest closed window. The billed peak read 1.93 kW
against 4.06 kW, 0.47-2.13 kW low on all 8 price shapes. The comparison came in with
`0377f5ceb` (2026-09-24). At this branch's head the line reads `kw > best[day][0]`, so the site is
already repaired here. The class record stands for the round.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s3-05` (verified, high): planted copy: tracker_peak_err_max=2.1268 kW; --perturb oneperday -> 0; perturbation: --perturb oneperday: _one_per_day keeps kw > best[day].

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m4_tariff.py` took 22 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-inverted-aggregate.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep_n_inverted_aggregate.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D2's tariff step asks that the capacity tariff charge the monthly peak exactly once
(`dev/governance/dimensions/D2.md:43-44`), and round 10's D2 s3 seat ran it. The step counts how
often a peak is charged. It does not ask which window was chosen as the peak, so a tracker that
picks the smallest window once a day passes it.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier over order-statistic aggregates |
| catch share q | 0.0: the sweep found 1 seam, the instance; a wrong comparison operator is not a syntactic shape |
| expected benefit, q x cost | 0 s/release |
| arm time | 22 s (`dev/audit/rounds/round11/D2/s3/m4_tariff.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 365 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. The fix's regression test uses two windows per day with
different peaks, so the wrong statistic picks a different window. The general lesson (an aggregate's fixture
must contain values the wrong statistic would choose) is a fixer step, and this record proposes it
to `fixer.md`'s test-first step through the owner rather than as a gate.
