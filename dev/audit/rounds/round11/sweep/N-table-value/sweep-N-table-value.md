# Round 11 class sweep: N-table-value (box SW4)

**Class mechanism (judge):** a constant in a production data table (preset,
coefficient, rule) is wrong, so every install that selects it computes from a
false number. `N-table-value` has no entry in `dev/audit/config/bugclasses.json`
at the register tip: it is a new class this round, so its status is effectively
`open` with no detector or barrier yet.

**Finding in the class:** D2-s1-51 (verified, medium). The verifier measured
`_ERA_LOSS_W_PER_M2K['low_energy'] = 0.85`, which makes 36 of 36 derive() cells
1.55x leakier than post-2005.

**Result:** 37 seams; **0 instances beyond the finding**, 30 hold against an
oracle, 7 are not applicable. `instances` = 0.

## Judged site: not reproduced at the register tree

At the register tip `origin/handoff/audit-r11-register` (28b864af) the table
reads `ERA_LOW_ENERGY: 0.35` (`presets.py:112`). The same holds at the
recorded baseline 92d38ecb, at b98c78e0 and at origin/main. `git log -S` shows
the value has stood since df7db82152, when the table was added. The lead's own
harness on this tree prints `cells_inverted=0` and a low_energy/post_2005 ratio
of 0.636.

The 0.85 that D2-s1-51 measured therefore came from the finder export it ran
on (`audit-r11-leads-px`, B8). It is not in any tracked commit this seat can
reach. The judged site is listed with `beyond_finding: false`, and its probe
re-introduces the export value. **The orchestrator should reconcile this
before a fixer is dispatched.** On this tree there is nothing to fix; the
export copy that carried 0.85 is the thing to explain.

## Detector (D14 step 3)

- **Enumerator:** `dev/audit/rounds/round11/D14/table_value/enumerate.py`.
  - It parses every `custom_components/heatpump_optimizer/**/*.py` (www/ and
    translations/ excluded). It takes each module-level `Assign`/`AnnAssign`
    whose value is a dict/tuple/list/set literal, a comprehension, or a call
    wrapping one.
  - It imports the module under `tests/hastub` and keeps the name when the
    runtime value holds 3 or more numeric leaves (bool excluded, nested dicts,
    tuples, NamedTuples and dataclasses walked).
  - It reads runtime values, so names and arithmetic resolve as production
    computes them (for example `FLOW_UNIT_TO_KG_S` through `WATER_KG_PER_L`).
- **Disposition:** `oracle.py` holds each seam to an independent oracle (CHECK),
  or records why none applies (NA). A seam with neither is printed
  `UNDISPOSITIONED` and exits 1, so a new table cannot pass silently. One
  `DHW_HOURLY_DRAW_PATTERN` is assigned twice (lines 2805 and 2813, a
  renormalisation); the oracle de-duplicates it to one seam.
- **Positive control:** `--perturb _ERA_LOSS_W_PER_M2K` sets low_energy to the
  0.85 the verifier measured. The run reports INSTANCE, the table is not
  decreasing along ERAS, and the derived cells are inverted in **36 of 36**,
  which is the finding's exact count.
- **Null control:** `enumerate.py --root dev/audit/rounds/round11/D14/table_value/clean_fixture`
  finds **0** seams. The fixture holds a string dict, a 2-leaf tuple, a bool
  tuple and a class-scope table.
- **Perturbation:** append one line to the fixture,
  `NEW_TABLE = {"a": 1.0, "b": 2.0, "c": 3.0}`, and it finds 1; remove the
  line and it finds 0 again. Each production oracle family also moves from
  0 to 1 under a one-line in-memory edit:

| arm | edit | result |
|---|---|---|
| `POWER_UNIT_TO_KW` | `W` = 0.01 | INSTANCE |
| `_WIND_UNIT_TO_MS` | m/s = 3.6 | INSTANCE |
| `TEMP_EDGES` | two edges swapped | INSTANCE |
| `WOOD_KWH_M3` | loose = packed | INSTANCE |
| `_OPTION_FIELDS` | `flow_heat_c` default above its selector max | INSTANCE |
| `_UNITS_PER_SEK` | JPY = 2 | INSTANCE |

- **Cost:** about 1.1 s for the whole run.

## Disposition (D14 step 4)

### Instance (0 beyond the finding)

None at the register tree. The judged site holds there (see above).

### Not an instance: the value holds against an oracle (30)

**Guard:** only `runs.BANDS` is pinned by CI (`tests/features.py:93096`,
`== ((2, 6, 24), 4, 10.0)`). For every other row the only guard is the oracle
in this harness, which is not yet in the gate. An extractor grep of tests/
(`*.py`, `*.mjs`) found no value pin for the others: tests reach them only as
key sets, lengths or relations.

| seam | oracle |
|---|---|
| const.POWER_UNIT_TO_KW | SI prefixes |
| const.ENERGY_UNIT_TO_KWH | SI prefixes |
| const.PRICE_ENERGY_TO_KWH | price per X to per kWh |
| const.TEMPERATURE_UNIT_TO_C | °F (-32, 5/9), K (-273.15, 1) |
| const.FLOW_UNIT_TO_KG_S | via WATER_KG_PER_L in 0.95..1.0, litre/m³/hour arithmetic |
| coordinator._PRECIPITATION_UNIT_TO_MM | 25.4 mm/in |
| coordinator._WIND_UNIT_TO_MS | 0.44704 mph, 0.3048 ft/s, 1852/3600 kn |
| heat_curve._DELTA_PER_K | 1.8 °F/K |
| grid_fee._MONTHS, grid_fee._DAYS | calendar, en and sv |
| accuracy.LEAD_BUCKETS, defrost.TEMP_EDGES, defrost.HUMIDITY_EDGES, runs.BANDS | strictly increasing; humidity covers 0..100 % |
| presets._ERA_LOSS_W_PER_M2K | strictly decreasing along ERAS, and derive() strictly decreasing in all 36 cells |
| presets._STRUCTURE_MASS | non-decreasing light to heavy per column |
| presets._FOUNDATION_ADJUST | none = unit; loss factors 1.0..1.5; basement mass above crawlspace |
| thermal_model.DHW_HOURLY_DRAW_PATTERN | 24 entries, mean 1, morning above night |
| wood_fuel.WOOD_KWH_M3 | loose below packed; ratio 0.5..0.75; birch > mixed > pine; published packed bands |
| const.INPUT_MAX_AGE_MINUTES, const.INPUT_ON_CHANGE_MAX_AGE_MINUTES | positive; an on-change age is never below its polling age |
| const.INPUT_PLAUSIBLE_RANGE_C | each window contains the real room, outdoor and water range |
| coordinator._FORECAST_FIELD_RANGE | each window contains real values; humidity at most 100 |
| const.FUSE_LADDER_A | standard main-fuse ladder |
| const.COMBI_TANK_PRESETS | effectiveness in (0, 1]; tank-in-tank at least 100 L; an external station stores none |
| config_flow._NAMEPLATE_DEFAULTS | COP 2..6, 0 < min < max ≤ 30 kW |
| config_flow._OPTION_FIELDS | 73 numeric defaults inside their own NumberSelector min/max |
| store.DOMAINS, store._ACCURACY | lo ≤ hi for every Domain |
| currency._UNITS_PER_SEK | each code at least the approximate mid-2026 units per SEK and within 5x (an order-of-magnitude table, by its own comment) |

### Not applicable (7)

| seam | reason |
|---|---|
| config_flow._ABSENT_FALLBACKS | derived by comprehension from the `_OPTION_FIELDS` defaults; covered by that oracle |
| coordinator.SCORE_REFERENCE | grade zero-points of a dimensionless score; a presentation choice |
| device_prefill._TUYA_HEAT_PUMP | per-data-point scale factors whose truth is device firmware; **unverified, not cleared** (no offline oracle) |
| device_prefill._SOURCES | registry of the prefill tables; its numeric leaves are the `_TUYA_*` scales counted again |
| grid_fee.SWEDEN_CATALOG | dated published tariffs; **unverified, not cleared** (no offline oracle for a tariff figure) |
| modbus_prefill._TENTHS, modbus_prefill._RAW_ADDRESSES | register identifiers, not quantities |

## Proposed barrier (D14 step 5)

- **Where:** land `oracle.py` as a `tests/` script, a `table_values` check run
  under the scoped gate with presets/const/coordinator/... in its closure. It
  costs about 1.1 s, and its `UNDISPOSITIONED -> exit 1` rule forces each new
  numeric table to be given an oracle or a stated NA reason when it is
  written.
- **Gaps it leaves:**
  - Class-scope tables and tables built inside functions are outside the
    enumerator.
  - The two unverified NA rows need a dated source citation next to the data
    rather than an oracle.
- **Count:** with 0 instances beyond the finding, `defect-root-cause.md`
  prices this as a single defect, not a recurring class. The barrier is
  proposed, not owed. The judged instance itself needs the reconciliation
  above.
