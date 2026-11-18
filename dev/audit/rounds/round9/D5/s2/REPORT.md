# Round 9 — D5-s2 (D5.M4, comments in code) — box B2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. 67 cells, all covered. The machine-readable report is `report.json` beside this file. The seat's write of this file was refused by its tool environment, so the box host transcribed it from the seat's final message, verbatim in substance.

## Method

1. **Do the identifiers a comment names exist?**
   - Python: every comment and docstring in the 66 modules, resolved against the whole package, then resolved again as qualified `module.name` or `Class.member` references (`scan_qualified_refs.py`).
   - Card: the TypeScript parser splits comments from code. Each `_name` a comment cites is resolved against:
     - the live card loaded through `tests/card_rig.mjs:loadCard` (its top-level bindings and the members of every class it defines);
     - the card's code tokens;
     - the backend's code tokens.

     This is `card_comment_names.mjs`.
2. **Do the numbers a comment cites match the code?**
   - A scan of numbers placed right after a constant's name (`scan_const_numbers.py`).
   - A scan of all 669 comment blocks longer than three lines against the literals on the next code line. It flagged 78 blocks, and each was reviewed by hand.
   - The claims that survived review are driven through the production symbols in `comment_numbers.py`, with five true claims as a control.
3. **Module docstrings.** All 66 were read in full, and the counts they state were checked against the code.

## Findings

### D5-s2-01 (low, hygiene, I5): card comments name 12 private members the card no longer has (17 mentions)

`card_stale_private_names=12`. Under `--perturb`, which applies the 7 renames in memory, the count falls to 5.

Renamed to module functions without the underscore:
- `_extraFields` (lines 30, 6634)
- `_fieldPoints` (4024)
- `_laneGroupInner` (5748)
- `_lineLabel` (1115, 4033, 4124)
- `_onSlotEdit` (8756)
- `_resolveEntity` (4568, 4620)
- `_seriesUnit` (1043)

No successor with that name; the work moved into other classes:
- `_applyView` (11533)
- `_refreshLayout` (2936, 10126)
- `_restoreSlotFocus` (5899)
- `_onWhatIfInput` and `_runWhatIf` (8756)

**Null control.** The same rule over the Python comments leaves 3 unresolved names, and none is a stale reference to current code:
- `_async_configure` is Home Assistant core.
- `_CERT_BARS` lives in `tests/optimality.py`.
- `_draftRuns` is cited as v3.2.0 history.

### D5-s2-02 (low, hygiene, I5): three comments cite a number the code does not deliver

`numeric_citation_mismatches=3`, and 0 under `--perturb`.

- `defrost.py:109-110` says "less than half" of rated output, but `DefrostDerate.observe` clamps at 0.55.
- `const.py:750` says the valve write recurs "every 15 minutes", but the coordinator's default update interval is 30 minutes.
- `coordinator.py:640` reasons about a "5-minute update interval", but the config flow's minimum for that selector is 10.

**Null control.** Five true claims give `hold_failures=0` of 5 in both arms.

### D5-s2-03 (low, hygiene, I5): `const.py:337-339` describes a coupling that no longer exists

The comment says the draw model "already assumes" `DHW_COLD_WATER_TEMP`. But `ThermalParameters.dhw_draw_power` heats from `dhw_inlet_reference`.

`draw_cold_end_off_constant` is 46 of the 47 inlet settings in the config flow's selector range, and 0 of 47 under `--perturb`. `thermal_model.py:1291-1297` itself documents that using the constant beside the new draw misallocated heat.

## Non-findings

The commands and values are in `report.json`.

- Python comment-named identifiers: no stale reference to current code.
- Qualified references: 19 rows, all false positives.
- Numbers placed after a constant's name: 2 of 2 match.
- Five numeric claims hold:
  - a fortnight of history;
  - 3 samples for the ventilation CUSUM to trip;
  - the 90-minute stale floor;
  - 8 weekly snapshots;
  - the 0.2 K curve step.
- Docstring counts hold:
  - 6 binary sensors, 4 buttons, 4 switches, 12 services and 6 platforms;
  - the boost, curve, frequency and guard constants.
- The only `file:line` citations point into the external tuya_heat_pump repository and cannot be checked from this export.

Seen but below the finding bar:
- `thermal_model.py:684-689` has "what" comments, one of which names `volume_flow`, which does not exist.
- `sysid.py:1662` writes `prior_rel = prior_w / data_w`, but the code computes `s_noise / prior_sd`.

## Harnesses

- `card_comment_names.mjs`
  - Command: `HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node tools/audit/round9/D5/s2/card_comment_names.mjs [--perturb]`
  - Needs `typescript` from `/opt/node22/lib/node_modules`, or a path in `TS_MODULE`.
- `comment_numbers.py`
  - Command: `PYTHONPATH=tests/hastub python tools/audit/round9/D5/s2/comment_numbers.py [--perturb]`
- `scan_qualified_refs.py` and `scan_const_numbers.py` are pure AST scans.

Every number is a count, so contention does not affect it. `load1` was 4.3 to 5.3 and `thread_factor` was 1.00.

## Unfinished

- Concision and precision were judged on a sample of about 60 of the 669 long blocks, not on all of them.
- The card's 2215 comment ranges were checked for names only, not read for numeric claims.

## Leads

- **Owner unknown.** In `tests/hastub/homeassistant/helpers/update_coordinator.py`, `DataUpdateCoordinator.__init__` drops `update_interval`, so no harness can read a coordinator's cadence.
- **D7-s2.** The `ThermalParameters.dhw_inlet_temp` default is a bare `10.0` (`thermal_model.py:469`), next to `DEFAULT_DHW_INLET_TEMP` and `DHW_COLD_WATER_TEMP`. That makes three copies of the cold-water default.

## Exposure

The seat read:
- the briefs;
- the toolkit README;
- `bugclasses.json`, which lists earlier instance ids;
- `round9/BASELINE.md`.

Code comments cite earlier finding ids; the seat treated them as context only. It did not read `docs/`, `RELEASE_NOTES.md` or GitHub. It opened no file under `tools/audit/round3` to `round8`, and saw those directory names only once, in an `ls` of `tools/audit/`.
