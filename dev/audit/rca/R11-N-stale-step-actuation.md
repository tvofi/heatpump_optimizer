# RCA: an actuator commanded from the previous step

Seat: round-11 root-cause, class `N-stale-step-actuation` (production). Instances R11 4, 4 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`N-no-expiry`) as one (`fold_ledger.py` `_group_counts`): `N-stale-step-actuation`, `N-unbounded-retention`, `N-uncleared-issue`, `N-unreleased-hold`, 16 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Plan steps are 15 min long and the solve cycle is 30 min. Writes that depend on the step
(compressor frequency, ECL110 MQTT displace, heat-curve offset, valve target) are cut once per
cycle from the cycle's action, and the one-minute step tick does not re-derive them. So the command
in force belongs to another step for 45-57 % of graded minutes (D16-s2-01). The disinfection switch
follows the same shape. It reads the input series, not the adopted action, so it turns on one
cycle after its booked window: 0 of 30 minutes inside it (D16-s2-02). The supply and mode channels
do re-cut on the tick and are the null channels. The tick exists, but only some channels use it.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D16-s2-01` (weakened, medium): worktree: stale share mqtt 0.5732, curve 0.4644, freq 0.4480; leave-one-out drop-most-favourable stays > 0.4 (mqtt LOO 0.41-0.73); perturbation: mqtt 0.0000, curve 0.0000, frequency 0.0000.
- `R11 D16-s2-02` (weakened, medium): worktree: on_in_window=0 of 30 min (long window 59/90); perturb -> 29/30 and 89/90; perturbation: on_in_window 29 of 30, on_outside 1, mode Heating + DHW 29 of 30.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s2/timing.py` took 2.4 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-stale-step-actuation.json`) lists 7 seams. The ledger carries 2 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/sweep_stale_step.py custom_components/heatpump_optimizer`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

No brief graded write timing against plan steps before D16 (2026-11-15). The step tick was
added for the channels that needed it at the time, and no rule names which channels must use it.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 4 instances over the 148 releases they accumulated in, 0.027 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.027 x 15660 s | 423 s/release |
| form | one step-boundary write path for every step-dependent channel, plus a `tests/` arm asserting a stale share of 0 over `D16/s2/timing.py`'s channels |
| catch share q | 0.9: a channel added to the path is covered; the residue is a channel written outside it |
| expected benefit, q x cost | 381 s/release |
| arm time | 2.4 s (`dev/audit/rounds/round11/D16/s2/timing.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 39 s/release |
| verdict | passes by 9.8x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm must show the stale shares (mqtt 0.57, curve 0.46, frequency 0.45) on this
baseline, 0 after the fix, and 0 on the supply and mode null channels. The fix PR owns the path and
the arm.
