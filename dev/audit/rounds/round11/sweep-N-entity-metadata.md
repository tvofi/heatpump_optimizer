# Class sweep: N-entity-metadata (round 11, D14 steps 3-4)

Mechanism: an entity declares a device_class, state_class or unit that does not
describe its value, so Home Assistant converts, aggregates or offers it wrongly.
Findings: D8-s3-01 (accumulators MEASUREMENT under device_class energy) and
D10-s2-04 (three degC differences with no device class).
Ledger: the class has no row in `dev/audit/config/bugclasses.json` at
`handoff/audit-r11-register` (28b864af6d), so it has no recorded status yet.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/entity_metadata_seams.py [--plant-accum] [--clean]`

It walks every built entity type on every platform (82 types, via
async_setup_entry through `D10/s2/_census.py`) and prints:

- SC_IMPOSSIBLE: a state_class outside HA's DEVICE_CLASS_STATE_CLASSES.
- UNIT_MISMATCH: a unit the device class does not admit.
- DELTA_BARE: degC or K with no device class.
- CLASSABLE: a classless unit that some HA class admits together with the
  entity's state_class. These lines are candidates that need a judgement.

| run | seams | lines |
|---|---|---|
| as is | 3 | DELTA_BARE x3 |
| positive control `--plant-accum` (D8-s3-01 re-planted) | 6 | adds SC_IMPOSSIBLE for Space/DHW/TotalEnergySensor |
| null control `--clean` | 0 | none |
| perturbation `--clean --plant-accum` (one line) | 3 | SC_IMPOSSIBLE x3 |

Both findings are re-found. D10-s2-04's three sensors are found directly. D8-s3-01's
three accumulators are found under the plant: HEAD and baseline 92d38ecb both
carry TOTAL_INCREASING, and the finding itself reproduced on a planted copy.

## Dispositions

| seam | disposition |
|---|---|
| sensor.py ECL110DisplaceSensor | instance (finding site D10-s2-04); probe: its DELTA_BARE line |
| sensor.py ECL110EffectiveDisplaceSensor | instance (finding site D10-s2-04) |
| sensor.py PredictionAccuracySensor | instance (finding site D10-s2-04) |
| sensor.py SpaceEnergy/DHWEnergy/TotalEnergySensor state_class | guarded: `_AccumulatingSensor` is TOTAL_INCREASING, pinned by `tests/entities.py` (block at line 2144) |
| sensor.py `_AccumulatingCostSensor` family | guarded: TOTAL is admissible for monetary |
| CLASSABLE SavingsPercentageSensor (%) -> battery | not applicable: a savings share is not a battery level |
| CLASSABLE PVSurplusSensor (kWh) -> energy_storage | not applicable: a forecast surplus, not stored energy |
| CLASSABLE DHWHeavyDaySensor (kWh) -> energy_storage | not applicable: a learned demand per window, not stored energy |
| classless SEK, SEK/kWh and % sensors with MEASUREMENT | not applicable: monetary admits only TOTAL, and no class covers a price per kWh |

Instances beyond the findings: **0**. No CI check covers DELTA_BARE, so the
class is not barriered. State_class admissibility for the accumulators is pinned
by `tests/entities.py`. Proposed barrier: run the enumerator's SC_IMPOSSIBLE and
UNIT_MISMATCH rules in `tests/entities.py` over every built entity. It is a
count-only check that costs well under one gate second.
