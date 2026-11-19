# RCA: a window figure projected from its elapsed part with no coverage floor

Seat: round-11 root-cause, class `N-partial-window-extrapolation` (production). Instances R11 3, 3 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A window or period figure is extrapolated linearly from what has elapsed, and no rule
sets a minimum coverage. `power_guard.project_window_mean` does not weight the current draw by the
remaining minutes, which its own docstring says it does. The guard therefore disagrees with its
description in 69 of 300 minute-samples (D17-s1-05, high). `ledger.pro_rata_factor` scales the
first settled 15-minute interval of a month by 2688-2976, so Plan Monthly Savings swings by over
1700 in currency in its first hour (D8-s1-02). The two are different formulas with one omission:
neither checks how much of the window it is standing on.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D17-s1-05` (verified, high): planted copy: guard_wrong_minutes_total=69 over 5 draws (range 3-25, drop-most-favourable 44); perturb -> 0; perturbation: --perturb-docstring: project_window_mean = (mean*elapsed + current*remaining)/window, its docstring's rule.
- `R11 D8-s1-02` (verified, medium): planted copy: first_scale=2688 (Feb), swing 1728.39 currency; perturbation: --min-hours 24: MonthlySavingsSensor._waiting_for also waits until the open month has 24 settled hours (in memory).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/s1/h_guard.py` took 0.7 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-partial-window-extrapolation.json`) lists 3 seams. The ledger carries 1 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep_partial_window.py --controls --probe`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

D8 checks a sensor's value against its source, and it found the monthly swing in this round.
D17 checks a feature against its documented effect, and it first ran in this round (2026-11-15).
No step asks for a projection's behaviour at low coverage, and no test drives one.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 3 instances over the 148 releases they accumulated in, 0.020 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.020 x 15660 s | 317 s/release |
| form | a class barrier: a static arm over projection call sites |
| catch share q | 0.0: the two judged formulas share no call or idiom, so a static arm sees neither; a dynamic arm is per formula, which is each fix's own test |
| expected benefit, q x cost | 0 s/release |
| arm time | 0.7 s (`dev/audit/rounds/round11/D17/s1/h_guard.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 11 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. Each fix carries its own test: the guard's steady-draw test
above and below the line, and the monthly sensor's minimum-coverage test. A shared
projection helper with a coverage floor is the structural answer if a third formula appears, and
this record proposes it to the fix PR as an option, not as a gate.
