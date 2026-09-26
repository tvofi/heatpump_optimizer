# Sweep: "compatibility duplicate entity enabled by default"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D8-s3-03
(verified, low). Not a ledger class (new).

## Enumerator

`enumerate.py` re-runs D8-s3-03's own seam_rule
(`_attr_entity_registry_enabled_default = False` lines, cross-checked
against the payload gate each value needs) and widens it: every
`*Sensor` class in `sensor.py` whose docstring language suggests it
republishes another entity's raw value, checked for whether it ships
enabled by default.

```
$ python3 tools/audit/round9/D14/sweep/compat_duplicate_entity/enumerate.py
RESULT candidate_duplicate_classes=3
  UpperFloorTempSensor enabled_by_default=True
  ContractComparisonSensor enabled_by_default=False
  MixedHotWaterSensor enabled_by_default=True
```

## Positive control

`UpperFloorTempSensor` (sensor.py:918-958): its own docstring states it
"has always published, to the last decimal, the value Indoor Temperature
publishes" and there is no `UPPER_FLOOR_TEMP` configuration key anywhere in
the package (grep confirms zero hits) — a byte-for-byte duplicate, shipped
enabled.

## Null control / disposition of the widened candidates

The regex over-matches on generic "value" wording; both other hits are
false positives on inspection, not duplicates:

- `ContractComparisonSensor` (sensor.py:2174): a derived load-profile
  comparison across contract types, its own distinct computation — matched
  only because its docstring contains the word "value". `enabled_by_default=False`
  here reflects `_WaitsForEvidenceMixin`'s settle-gate, unrelated to
  duplication.
- `MixedHotWaterSensor` (sensor.py:2329): a derived transform
  (`V·(T_tank − T_inlet)/(40 − T_inlet)` litres), not a byte-duplicate of
  another entity — its docstring says it "carries the same **gate**"
  (availability), not the same value.

## Perturbation

Direction check: if `UpperFloorTempSensor` were given
`_attr_entity_registry_enabled_default = False` (matching the fix shape),
`enumerate.py`'s own `enabled_by_default` field would read `False`; the
detector's boolean is derived directly from grepping that one class
attribute, so it moves by construction under that one-line edit (not
separately re-run, since it is definitionally the toggle being asked about).

## Baseline vs main

`custom_components/heatpump_optimizer/sensor.py` is unchanged between
`1936d5ca` and `origin/main` (not in the 4-file diff). The seam still
exists on main.

## Disposition

| seam | disposition |
|---|---|
| sensor.py:918-958 `UpperFloorTempSensor` | instance — D8-s3-03 |
| sensor.py:2174 `ContractComparisonSensor` | not applicable — a distinct computed value, not a duplicate; regex false positive on generic wording |
| sensor.py:2329 `MixedHotWaterSensor` | not applicable — a derived transform of the DHW reading, not a byte-duplicate; regex false positive |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). A lint rule flagging any sensor class whose
`native_value` reads exactly the same `coordinator.data` key as another
entity, with no distinct config key behind it, would need a positive list
of intentional duplicates (this one) to avoid false-positive churn — left
as a lead, not built.

## Gate seconds

~0.01s (one file regex scan).
