# RCA: one write drives a second heat target the plant cannot separate

Seat: round-11 root-cause, class `N-mode-coupled-write` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P2`) as one (`fold_ledger.py` `_group_counts`): `N-duplicated-rule`, `N-entry-data-placement`, `N-inverted-aggregate`, `N-mode-coupled-write`, `N-wrong-law`, 8 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

On a pump whose mode select offers only `Heating + DHW` (GCHV), the arbiter's space-heat
row writes the tank set-point at the space gate (30 C). The tank reads 20 C with a 5 K start
hysteresis, so a step that booked no hot water asks the pump to charge the tank (2 of 2 such rigs).
`pump_arbiter.DHW_GATE_C` floors the tank write above the case. The rows assume a heating-only mode
exists, and on this plant none does.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D16-s1-02` (weakened, low): worktree: cold_tank_charge=2 rigs; --perturb dhw_gate -> 0; perturbation: --perturb dhw_gate: pump_arbiter.DHW_GATE_C = 10.0.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s1/cells.py --no-gates` took 9.0 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-mode-coupled-write.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/n_mode_coupled_write.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

Actuator writes against the plan had no brief until D16 first ran in this round
(`dev/governance/dimensions/D16.md`, first added 2026-11-15). The reach needs a pump with no
heating-only mode, which no test rig modelled before D16's cells.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier over mode-coupled writes |
| catch share q | 0.0: the sweep found 1 seam, the instance; the topology is one actuator layout, and a generic detector would have to know which plants couple which targets |
| expected benefit, q x cost | 0 s/release |
| arm time | 9.0 s (`dev/audit/rounds/round11/D16/s1/cells.py --no-gates`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 146 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. The fix gates the tank at the entity's minimum (or below the tank
reading less the hysteresis) on the mode-less space row, and carries D16-s1-02's `--perturb
dhw_gate` arm as its regression test. D16's cells harness stays an audit instrument for new plant
topologies. Re-open on a second topology.
