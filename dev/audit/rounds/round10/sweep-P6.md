# Round 10 class sweep: P6 (finding D7-s2-60)

**Class P6** in `dev/audit/config/bugclasses.json` has `status: barriered`. Its barrier is
the P6 section of `tests/entities.py`, which checks that every read has a producer. **D7-s2-60**
does not fall under that barrier's property. Every payload key it reads has a producer. The
defect is that one payload number reaches Home Assistant through several guards that answer
differently. `True` is published as `1`, `True` or `None`. A numeric string `'21.5'` raises
`TypeError`, passes through raw, or becomes `None`. The finder put it in P6 as a *guess*
(`class_guess: P6`). The mechanism fits P6's silent-fallback stretch only loosely. That mapping
is the judge's call, and this sweep does not settle it. `barriered` is `false` below because no
check in the tree refuses a new divergent guard.

## Enumerator (D14 method step 3)

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P6/enumerate.py`

- **Seam rule.** The finding's seam rule is `shape_payload_guard.py family()`, which covers
  `sensor.py` only. This sweep widens it to every module under `custom_components/heatpump_optimizer/`
  and to every entity state property (`native_value`, `is_on`, `current_temperature`,
  `target_temperature`, `current_option`, `current_operation`) that reads `self.coordinator.data`
  or `self._data()`. A return shape outside the four known guards is enumerated as family
  `other`, so no seam is dropped.
- **Probe.** The sweep drives each seam on the real class with a stub coordinator. Each probe
  value is placed at the property's own `.get()` path. The key order follows the key literal's
  source position, so chained `_mapping(...).get()` reads are driven correctly. A base class
  that reads `self._data_key` is driven through every concrete subclass. Two seams are pinned
  by hand in the script, each with its reason: `OutdoorTempSensor` reads its value through
  `_effective_outdoor`, and `CompressorStartsSensor` is an integer count.
- **Contract.** The package's own owner, `sensor._as_float`, sets the expected answers:
  `True -> None` and `'21.5' -> None`.

## Controls (measured 2026-10-15 at `handoff/audit-r10-register` 9355f107d)

| control | command | result |
|---|---|---|
| sweep, working tree | (default) | seams=56: instance=31, guarded=5, not_applicable=20; 3 modules; 6 distinct bool/str answer vectors |
| positive (finding baseline 554e2ecfa7ad, a detached worktree) | `--tree <checkout>` | identical: 56 / 31 / 5 / 20. The 35 non-`other` seams are exactly the finding's `implementations=35`, and every one is re-found |
| null | `--fixture clean` (two sites, both through `_as_float`) | instance=0, guarded=2 (the universe is not empty) |
| perturbation | `--fixture reintro` (one line changed to `round(v, 1) if v is not None`) | instance 0 -> 1; families 1 -> 2 |

`sensor.py` is unchanged between the baseline and HEAD. That is why the positive control
returns the same numbers as the working-tree sweep.

## Disposition of every seam

The probe for each `instance` is the enumerator's own line for that seam. The seam fails
because `True` or `'21.5'` does not answer `None`.

| disposition | seam | guard family | answer / reason |
|---|---|---|---|
| not_applicable | `binary_sensor:InputHealthBinarySensor.is_on` L98 | other | does not publish the payload float as a number (21.456 -> True) |
| not_applicable | `binary_sensor:VentilationBinarySensor.is_on` L139 | other | does not publish the payload float as a number (21.456 -> True) |
| not_applicable | `binary_sensor:ExternalHeatBinarySensor.is_on` L259 | other | does not publish the payload float as a number (21.456 -> True) |
| not_applicable | `binary_sensor:AwayModeBinarySensor.is_on` L292 | other | does not publish the payload float as a number (21.456 -> True) |
| not_applicable | `binary_sensor:WoodCheaperBinarySensor.is_on` L326 | other | does not publish the payload float as a number (21.456 -> False) |
| not_applicable | `climate:HeatPumpOptimizerClimate.current_temperature` L134 | other | does not publish the payload float as a number (21.456 -> None) |
| not_applicable | `sensor:OptimizationModeSensor.native_value` L425 | other | does not publish the payload float as a number (21.456 -> 'unknown') |
| not_applicable | `sensor:OptimizationStatusSensor.native_value` L441 | other | does not publish the payload float as a number (21.456 -> 'not_run') |
| instance | `sensor:PredictedSavingsSensor.native_value` L478 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:SavingsPercentageSensor.native_value` L543 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:PredictedCostSensor.native_value` L573 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:BaselineCostSensor.native_value` L589 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:CurrentPriceSensor.native_value` L608 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| guarded | `sensor:CurrentSetpointSensor.native_value` L625 | _as_float | rejects bool and str (the _as_float contract) |
| not_applicable | `sensor:CurrentPowerSensor.native_value` L654 | other | does not publish the payload float as a number (21.456 -> AttributeError) |
| not_applicable | `sensor:CurrentCOPSensor.native_value` L677 | round_if_number | no literal payload path; computed state |
| instance | `sensor:IndoorTempSensor.native_value` L713 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:OutdoorTempSensor.native_value` L741 | round_if_not_none | True -> 1.0, '21.5' -> 21.5 |
| instance | `sensor:SolarIrradianceSensor.native_value` L783 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:SlabTempSensor.native_value` L833 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| not_applicable | `sensor:NextOptimizationSensor.native_value` L849 | other | does not publish the payload float as a number (21.456 -> None) |
| not_applicable | `sensor:LastOptimizationSensor.native_value` L864 | other | does not publish the payload float as a number (21.456 -> None) |
| not_applicable | `sensor:HeatPumpActionSensor.native_value` L880 | other | does not publish the payload float as a number (21.456 -> 'unknown') |
| not_applicable | `sensor:ScheduleSensor.native_value` L939 | other | does not publish the payload float as a number (21.456 -> TypeError) |
| not_applicable | `sensor:ScheduleStepsSensor.native_value` L976 | other | does not publish the payload float as a number (21.456 -> TypeError) |
| instance | `sensor:UpperFloorTempSensor.native_value` L1031 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:LowerFloorTempSensor.native_value` L1072 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:FloorReturnTempSensor.native_value` L1105 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:SolarHeatGainSensor.native_value` L1126 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:BufferTankTempSensor.native_value` L1170 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:DHWTemperatureSensor.native_value` L1209 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| not_applicable | `sensor:DHWScheduleSensor.native_value` L1255 | other | does not publish the payload float as a number (21.456 -> AttributeError) |
| instance | `sensor:DHWHeatingCostSensor.native_value` L1319 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| not_applicable | `sensor:PredictiveInsightSensor.native_value` L1352 | other | does not publish the payload float as a number (21.456 -> TypeError) |
| instance | `sensor:ECL110DisplaceSensor.native_value` L1419 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:ECL110EffectiveDisplaceSensor.native_value` L1445 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:MeasuredPowerSensor.native_value` L1734 | round_if_not_none | True -> 1, '21.5' -> TypeError |
| instance | `sensor:ObservedCOPSensor.native_value` L1782 | other | True -> True, '21.5' -> '21.5' |
| instance | `sensor:_AccumulatingSensor.native_value` L1836 | round_if_number | True -> 1, '21.5' -> None |
| guarded | `sensor:PredictionAccuracySensor.native_value` L1992 | _as_float | rejects bool and str (the _as_float contract) |
| not_applicable | `sensor:ModelStatusSensor.native_value` L2089 | other | does not publish the payload float as a number (21.456 -> 'attention') |
| instance | `sensor:MonthlyPeakSensor.native_value` L2160 | other | True -> True, '21.5' -> '21.5' |
| guarded | `sensor:PVSurplusSensor.native_value` L2221 | _as_float | rejects bool and str (the _as_float contract) |
| guarded | `sensor:ThermalBatterySensor.native_value` L2264 | _as_float | rejects bool and str (the _as_float contract) |
| guarded | `sensor:ThermalBatteryEnergySensor.native_value` L2293 | _as_float | rejects bool and str (the _as_float contract) |
| instance | `sensor:ValveTargetRecommendationSensor.native_value` L2382 | isinstance_number | True -> True, '21.5' -> '21.5' |
| instance | `sensor:ComfortWeightSensor.native_value` L2416 | round_if_number | True -> 1, '21.5' -> None |
| instance | `sensor:ContractComparisonSensor.native_value` L2463 | isinstance_number | True -> True, '21.5' -> None |
| instance | `sensor:PowerHeadroomSensor.native_value` L2516 | isinstance_number | True -> True, '21.5' -> None |
| instance | `sensor:DHWSetpointAdvisorSensor.native_value` L2570 | isinstance_number | True -> True, '21.5' -> None |
| instance | `sensor:MixedHotWaterSensor.native_value` L2626 | isinstance_number | True -> True, '21.5' -> None |
| not_applicable | `sensor:DHWHeavyDaySensor.native_value` L2673 | other | does not publish the payload float as a number (21.456 -> AttributeError) |
| not_applicable | `sensor:PlanNarrativeSensor.native_value` L2719 | other | does not publish the payload float as a number (21.456 -> None) |
| instance | `sensor:OptimizationScoreSensor.native_value` L2776 | isinstance_number | True -> True, '21.5' -> None |
| instance | `sensor:CompressorStartsSensor.native_value` L2830 | isinstance_number | True -> True, '21.5' -> None |
| instance | `sensor:FrequencyAdvisorSensor.native_value` L2885 | isinstance_number | True -> True, '21.5' -> None |
Notes on the `not_applicable` rows:
- `binary_sensor:*.is_on` and the string or enum sensors (`OptimizationMode`, `Status`,
  `HeatPumpAction`, `ModelStatus`, `PlanNarrative`, the schedules and timestamps) publish a
  boolean, text or datetime state by design. A number guard does not apply to them.
- `CurrentPowerSensor`, `DHWScheduleSensor`, `DHWHeavyDaySensor` and `PredictiveInsightSensor`
  read a structured value (an action, a schedule or an insight block). They do not read a
  payload float.
- `CurrentCOPSensor` publishes the model's `compute_cop` output. That is a computed value, not
  a payload read.
- `climate:HeatPumpOptimizerClimate.current_temperature` cannot be driven from one path,
  because it reads `_measured(...)` first. A code reading (climate.py L134-147) shows that it
  excludes `bool` explicitly on both branches. It is **guarded** by that inline check. The
  enumerator lists it as not_applicable only because it could not drive it.

## Counts

- **Judged sites** (`beyond_finding: false`): the 29 instances among the finding's 35 guard-family
  seams in `sensor.py`. Of the remaining 6, five are guarded by `_as_float` and one (`CurrentCOP`)
  is not applicable.
- **Beyond the finding** (`beyond_finding: true`): **2**. `ObservedCOPSensor.native_value` and
  `MonthlyPeakSensor.native_value` use a guard shape outside the finder's four families. Both
  publish `True` and `'21.5'` raw, the widest answer of any seam.
- No other platform module has a numeric seam that is an instance.

## Proposed barrier (step 5)

This needs one owner and one test. Route every numeric payload read in `sensor.py` through
`_as_float`. Patches 00-02 of `D7/arch-s2/patches` already collapse 35 implementations to 13.
That patch set still has to cover `ObservedCOP` and `MonthlyPeak`. Then add this enumerator's
probe as a `tests/` arm that asserts `instance == 0`. Its cost is one import of `sensor.py` plus
about 170 property calls, well under 1 s of gate time. The bool policy for the residue is the
owner's decision, as the finder recorded.
