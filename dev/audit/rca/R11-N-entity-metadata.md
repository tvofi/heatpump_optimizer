# RCA: entity metadata that does not describe the value

Seat: round-11 root-cause, class `N-entity-metadata` (production). Instances R11 2, 2 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P8`) as one (`fold_ledger.py` `_group_counts`): `N-entity-metadata`, `N-missing-unit-scale`, `N-objective-as-money`, 7 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Entity metadata is declared as class attributes and inherited. `_AccumulatingSensor` sets
`state_class = MEASUREMENT`, and the three energy accumulators inherit it beside `device_class =
ENERGY`. Home Assistant rejects that pair: it warns on every state write and keeps the sensors out
of the Energy dashboard (D8-s3-01, 36 of 36 cells). D10-s2-04: three temperature-difference sensors
publish degC with no device class, though core 2025.11 added `TEMPERATURE_DELTA`. Home Assistant
publishes the legal device-class, state-class and unit combinations. The integration checks a few
of them by name.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D10-s2-04` (verified, low): planted copy: unit_without_device_class=14 (3 delta sensors); --perturb-delta 14 -> 13; perturbation: 2.
- `R11 D8-s3-01` (verified, medium): planted copy: state_class_impossible=36 (3 accumulators x 6 cells x 2 cycles); perturb -> 0; perturbation: --perturb accum-total-increasing: sensor._AccumulatingSensor._attr_state_class = SensorStateClass.TOTAL_INCREASING (in memory).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/entity_census.py` took 0.7 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-entity-metadata.json`) lists 3 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/entity_metadata_seams.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

`tests/entities.py` checks state classes. The judge's note on D8-s3-01 names its existing
`TOTAL_INCREASING` check, which reads the subclasses that declare a state class themselves. The
accumulators inherit theirs, so the check never reads them. D8's per-entity step
(`dev/governance/dimensions/D8.md:25-26`: device_class, state_class, unit) ran in round 10 over
`sensor.py` (D8 s1) and did not report the pair. The checks ran and were green. Their unit was a
declared attribute, and the defect is in the inherited one.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 2 instances over the 148 releases they accumulated in, 0.014 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.014 x 15660 s | 212 s/release |
| form | extend the existing `tests/entities.py` entity check to resolve each sensor's effective (inherited) metadata and test it against Home Assistant's own device-class tables |
| catch share q | 1.0: the tables are Home Assistant's own; every sensor class is instantiated |
| expected benefit, q x cost | 212 s/release |
| arm time | 0.7 s (`dev/audit/rounds/round11/D10/s2/entity_census.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 11 s/release |
| verdict | passes by 18.6x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm reads `DEVICE_CLASS_STATE_CLASSES` and `DEVICE_CLASS_UNITS` from the stub or core,
which is the same contract Home Assistant enforces at runtime. It must show red on this baseline,
the 3 accumulators, and green after the fix. The delta-sensor half depends on the running core
version, so it is a warning row, not a refusal. The fix PR owns the extension.
