I ran both of my steps (D8.M4 and D8.M5) across all 6 platform files in my scope and found one defect: the three lifetime energy sensors declare the wrong `state_class`. Their `device_class` is `energy` but their `state_class` is `measurement`, which Home Assistant rejects, so these meters can't be used in the Energy dashboard. The enabled-by-default check (M4) found nothing wrong.

**REPORT.json:** `~/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D8/s3/REPORT.json`. The finding is also in `findings/D8-s3-01.json` in the same directory. No commits, no pushes, no GitHub calls. I created the scratch dir `~/hpo-orch/r10s6/r11/scratch/D8-s3` but didn't need it.

---

# REPORT.md — D8 seat D8-s3 (round 11, box B6)

Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Exposure: none.

## Method
- **Cells:** from `check_scopes.py --seat D8-s3`, steps M4+M5 over 6 files: `binary_sensor.py`, `button.py`, `climate.py`, `entity.py`, `sensor.py`, `switch.py`. Universe 6, examined 6, not_reached empty, for both steps.
- **M4** (`dev/audit/rounds/round11/D8/s3/m4_enabled_default.py`):
  - Builds every entity through the real `async_setup_entry` on six platforms: sensor, binary_sensor, button, switch, climate, plus datetime (read only to resolve the card's ids).
  - Runs in the 5 `coordinator_scenarios()` cells, plus an "all-inputs-lit" cell (all features, with every probe configured and the mixing valve set to `manual`).
  - The "first hour" list is:
    - every entity id or `"_suffix"` the card source names, including the ones it builds at runtime through `statEntity`, `ADVISOR_SUFFIXES` and `HEALTH_*`;
    - the README table rows tagged "Card headline" or "Backs the card".
  - Each is compared with the registry default the entity actually reports.
- **M5** (`dev/audit/rounds/round11/D8/s3/m5_matrix.py`):
  - The matrix, written so it can become a `tests/` script: 6 cells × 2 cycles (prices, weather and solar changed between them) × every built entity, which is 984 triples.
  - One RESULT line per violation class: `measurement_non_numeric`, `timestamp_naive`, `enum_off_list`, `unit_on_non_numeric_class`, `state_class_impossible`, `not_json_serialisable`, `property_raised`, `stale_between_cycles`.
  - The whole matrix runs twice, and `matrix_nondeterministic` counts any difference between the runs. It uses no network.

## Findings
**D8-s3-01 (high, bug, class new, step D8.M5): the lifetime energy accumulators have an impossible state class.**
- **What's wrong:** `sensor.py:_AccumulatingSensor` sets `_attr_state_class = SensorStateClass.MEASUREMENT`. Its own docstring says TOTAL_INCREASING, and so does the `tests/entities.py` check "<name> is TOTAL_INCREASING". `SpaceEnergySensor`, `DHWEnergySensor` and `TotalEnergySensor` don't override it; the cost subclass correctly overrides to TOTAL.
- **Effect:** `energy` with `measurement` is not an allowed pair in Home Assistant, which warns on every state write. These meters can't be used in the Energy dashboard.
- **Evidence:** `RESULT state_class_impossible=36`, counted exactly.
  - It is 3 entities × 6 cells × 2 cycles.
  - Leave-one-out: 6 per cell, 30 with one cell dropped.
  - Instrumented symbol: `heatpump_optimizer.sensor:_AccumulatingSensor`.
- **Perturbation:** `--perturb accum-total-increasing` sets the state class to TOTAL_INCREASING in memory, and the count goes to 0.
- **Fix scope:** one line, TOTAL_INCREASING on the accumulator base.
- **Overlap:** D8-s1's M2 cell (state class vs device class) also covers this; the judge should dedupe.

## Non-findings (what was checked and held)
- **Card dependencies:** none is disabled by default where its gating input is configured: `card_disabled_where_input_lit=0`. The perturbation `--perturb-disable optimization_score` moves it to 1.
- **README first-hour rows:** none names an entity disabled where its input is lit: `readme_disabled_where_input_lit=0`.
- **Card dependencies disabled in unlit cells (21 across the 5 cells):** all are gated on an input by design and turn on when it is configured.
  - Probe or valve gated: `dhw_temperature`, `lower_floor_temperature`, `valve_target_recommendation`.
  - Gated on hot water (DHW): `plan_dhw_heating`, `dhw_setpoint_advisor`.
- **Card suffixes with no built entity (7):** these are the pre-#1227/#1333 legacy fallback ids, kept on purpose.
- **Enabled entities that neither the card nor a README first-hour row reads:** 38 in `coord_all_features`. They are the climate entity, switches, buttons, Energy-dashboard meters and diagnostics. These are reasonable defaults, not a defect.
- **Every other M5 class is 0** over 984 triples, and `matrix_nondeterministic=0`. The instrument does catch problems: `--perturb numpy` raises `not_json_serialisable` to 288.

## Harnesses
- `dev/audit/rounds/round11/D8/s3/m4_enabled_default.py`
- `dev/audit/rounds/round11/D8/s3/m5_matrix.py`

Both are counts, so the busy box doesn't affect them (load1 was about 200, thread_factor 1.000).

## Leads
- **owner unknown (a D6 claim check), `README.md` entities section:** the README says twenty entities are disabled by default. That is true for an install with hot water (20 disabled in `coord_dhw`), but an install without it has 28 disabled (`coord_minimal`).
- **D8-s1, `sensor.py:_AccumulatingSensor`:** the docstring and the code disagree on the state class. This is D8-s3-01; listed so the overlap can be deduped.

## Unfinished
None.