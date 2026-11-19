# RCA: a configured input that changes nothing

Seat: round-11 root-cause, class `N-dead-input` (production). Instances R11 2, 2 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P6`) as one (`fold_ledger.py` `_group_counts`): `N-dead-input`, `N-partial-payload-parse`, 3 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

An option is accepted, stored and shown, but nothing carries it into the plan. D17-s2-02:
with a forecast present, the configured outdoor sensor is read and then overwritten by the
forecast's current hour. The plan is identical at -25, -3 and +10 C, though the field's
documentation says the sensor beats the forecast. D17-s2-04: a night-mode schedule kept on the
pre-fill page leaves the plan at full power, because its companion fraction defaults to 1.0 and the
setup page never offers it. In both cases a reader exists. The input still has no effect.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D17-s2-02` (verified, medium): planted copy: step0_outdoor_spread_K=0.000 with a forecast; no-forecast null 35 K; perturb -> 35 K, 5.124 kWh; perturbation: step0_outdoor_spread_K 0.0->35.0, plan_kwh_spread 0.0->5.124 kWh.
- `R11 D17-s2-04` (verified, medium): planted copy: kept_schedule_cap_delta_kW=0.000 (with fraction -2.0); perturb -> -2.0; perturbation: with_fraction_cap_delta_kW=-2.0; under --perturb kept_schedule_cap_delta_kW=-2.0.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/s2/outdoor_sensor.py` took 3.9 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-dead-input.json`) lists 2 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 -I dev/audit/rounds/round11/D14/sweep-N-dead-input/dead_input_enum.py custom_components/heatpump_optimizer`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

Checking a feature against its documented effect is D17's brief, and D17 first ran in this
round (2026-11-15). No earlier brief perturbed an option and asked whether the plan moved.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 2 instances over the 148 releases they accumulated in, 0.014 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.014 x 15660 s | 212 s/release |
| form | a static `tests/` arm requiring every options key to have a reader outside the flow |
| catch share q | 0.0: both judged inputs have readers; only a perturbation (change the option, see the plan move) sees the class, and that is a solve per option |
| expected benefit, q x cost | 0 s/release |
| arm time | 3.9 s (`dev/audit/rounds/round11/D17/s2/outdoor_sensor.py`, re-timed by this seat; a per-option sensitivity gate is that cost times the options count) |
| standing cost, arm x 16.3 PRs | 63 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. The cheap static form catches neither instance, and the form that
would (a per-option sensitivity run) costs a solve per option per PR. Each fix's own perturbation
test is the guard. D17's harnesses stay audit instruments, re-run each round.
