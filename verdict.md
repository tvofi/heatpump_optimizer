Fix review: blocked 98cb43e750457b41ae6feb9a0c56cf1d6728e201 mutation-vacuous: open_meteo.py _parse_block len(kept) < 2 loosened to < 1 survives every _parse_block caller and is not equivalent

bus-nonce: 9067c8bbf58c0d6c4f2d781b8a9243f8

## Block

- Round 3 of this PR (round 2 blocked at 40328a85, `class-open: wood_fuel.lighting_window`). Review scope: full. The packet rendered with no `--reviewed-head`.
- Survivor: `custom_components/heatpump_optimizer/open_meteo.py:256`, the line this PR adds, `if len(kept) < 2:` mutated to `if len(kept) < 1:`. Under the mutant these all stay green: `tests/open_meteo.py` (`ALL OPEN-METEO CHECKS PASSED`), `tests/solar_alignment.py` (`ALL SOLAR ALIGNMENT CHECKS PASSED`), and features.py's block `P1/P2/N-min-gap ... feed parsers`, which is the only other `_parse_block` caller (`ALL 7 FEATURES BLOCK PASSED`). See `ev/m12_closure_runs.txt`. I did not run the other 20 scripts in open_meteo.py's measured closure. None of them calls `_parse_block` (scout locate over `tests/` and `tools/`).
- The body says round 1's reviewer dismissed this mutant (round 1's M14) "as equivalent under `mean_over`'s coverage rule". It is not equivalent: `ev/m12_probe.txt` (driver `ev/m12_probe.py`, run on a `git archive` of the head):
  - Block `{"time": ["0001-01-01T00:00", "2026-08-21T00:00"], "shortwave_radiation": [1.0, 100.0]}`.
  - At the head, the block parses to an empty series. `mean_over` reads `None` for 23:00-00:00, 23:30-00:00 and 22:00-01:00.
  - Under the mutant, it parses to a one-sample series `(2026-08-21 00:00, 100.0)` with `resolution 739848 days, 0:00:00`. Its span `(t - resolution, t]` reaches back to year 1. `mean_over` then reads `100.0` for all three windows.
  - The guard is what refuses a lone survivor whose resolution was inferred from a gap to the dropped stamp. That case always has a span back to year 1: with two stamps and one dropped, the single gap is at least the survivor's distance from year 1.
- The finder's harness does not separate the mutant. `parsers_fuzz.py --arm openmeteo` reads `openmeteo_year1_solve_failures=0` at the head and also under the mutant (`ev/finder_openmeteo_mb_head_m12.txt`). This survivor is therefore a test gap, not a regression of D1-s3-03's metric.
- Remedy, owed by the fixer: a `tests/open_meteo.py` check that the two-stamp block above parses to no samples (or that `mean_over` reads `None` over a window it would otherwise claim), with its null control. The rest of the review holds, and a re-review is the delta.

## Findings

- Residual: features.py's P8 block (`R.section("P8 — a price or temperature entity's unit is read at the seam (#1513)")`) does not run alone under `tools/audit/seat/features_block.py`, even with the `_r9f41_const` prelude: `NameError: name '_Coord' is not defined` after the D7-s3-01 check. The D7-s3-01 check reads `ok` at the head and `FAIL` under its mutant before the NameError, so the proof stands, but the block cannot be run whole. Carry: dismissed: a seat-instrument convenience, `--emit-prelude` derives the missing prelude; nothing in this PR's code or tests depends on it.
- Note: paperwork: the body's `## Unpinned sites` row for `entry_config.py:52` still names `_MAX_INTERVAL_MINUTES`, which the repair renamed `_MAX_PLAN_MINUTES`. Carry: dismissed: a stale name in the body, settled by the fixer's next body edit on this PR.

## Evidence

- Head reviewed: 98cb43e750457b41ae6feb9a0c56cf1d6728e201 (`ev/HEAD.txt`). Merge base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111.
- `git merge-tree --write-tree origin/main 98cb43e7...` rc=0, no conflict (`ev/merge-tree.txt`).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/`, `tests/*budgets.json`: three-dot diff empty (`ev/untouched.txt`).
- Mutation proof, one at a time, worktree at the head, with `git status --porcelain` empty after each (`ev/mutants_*.log`, driver `ev/mutant_driver.py`). Killed:
  - M1, `parse_bool` back to `float(token) != 0.0`: `FAIL parse_bool reads no non-finite number as a flag (D1-s3-01)`.
  - M2, `_begin`'s `isinstance(entity_id, str)` guard deleted: the block dies with `TypeError: cannot use 'dict' as a dict key`.
  - M3, `kept` = every index: `FAIL a stamp with no representable span is dropped, and the block still averages`.
  - M4, `repairs = {}`: `FAIL an old entry's non-numbers under numeric options are repaired, with one warning naming them`.
  - M6, `_attach_windows` reading the raw option with `max(0.0, finite_float(...))`: `FAIL a stored lead outside [0, a day] is the default 60 min`.
  - M7, `_interval_minutes`'s range guard dropped: `FAIL an optimization interval outside (0, a day] parses as the default`.
  - M8, `temperature_from_c` multiplying by the factor: `FAIL temperature_from_c inverts every unit row the reader converts (D7-s3-01)`.
  - M9, `plausible_c` one-sided: `FAIL every plausible window refuses a reading one degree past either end (D1-s2-51)`.
  - M11, `repaired_numbers` keeping keys mapped to None: `FAIL an old entry's non-numbers ... repaired`.
  - M13, the lead floor made strict: `FAIL a lead inside [0, a day] is its own`.
  - M5, `_lead_minutes` dropped from `_DEFAULTED_NUMBERS`: `FAIL every option whose parse defaults text it cannot read is repaired by the migration [unrepaired: ['wood_lighting_lead_minutes']]`.
  - M10, `number_repairs`'s bool branch dropped: `FAIL an old entry's non-numbers ... repaired` (`cop_scale: True` left stored).
  - M14, the `mixing_valve_target` declaration deleted: the same check (`mixing_valve_target: 'abc'` left stored).
- Survivor: M12 (above).
- The finder's harnesses, from the plan export 819aa2e3 (`parsers_fuzz.py` sha1 74da66cd7b0beac627cb2a636e6c0364c1ddc019), merge base then head (`ev/finder_*.txt`). Each matches the body:
  - `pump_nonfinite_flag_true`: 10 then 0. `pump_nonfinite_freeze_fault`: 5 then 0. `pump_null_control_zero_flag_true`: 0 then 0.
  - `openmeteo_year1_solve_failures`: 3 then 0. `openmeteo_healthy_solve_failures`: 0 then 0.
  - `config_fuzz.py --versions 2`: `build_fail` 11 then 0, `permanent_cycle_fail` 14 then 0. `--versions 5`: 5 then 0 and 17 then 0. I re-ran v2 and v5 only; v1, v3, v4 and v6 were not re-run.
- Body figure "47 fields" re-derived: the selection by parse behaviour returns 47 fields, with parses exactly `_interval_minutes`, `_lead_minutes`, `_nonzero_number` and `finite_float`. It equals the `_DEFAULTED_NUMBERS`-declared set (difference empty).
- Class step: every production reader of `optimization_interval` and `wood_lighting_lead_minutes` reads the parsed `EntryConfig` field (`coordinator.py`, `supply_hold.py:101`, `__init__.py:179`, `early_cutoff.py:172`, `heat_curve.py:348`, `wood_fuel.py:560`). `sysid.py:1359` reads the constant default. No raw reader is left. I found no seam beyond the body's dispositions.
- Step 16: no new path skips an actuator write.
- CI, live classify on this head, polled every ~60 s since 22:49 UTC: still WAIT at the verdict, last line `WAIT 98cb43e750457b41ae6feb9a0c56cf1d6728e201 pending: gate red: none` (`ev/classify_poll.log`). The block above is on tests, not CI. The digest's `tests / mutation` red is in the `owed-reds` set and is answered in the body's `## Red checks`; I checked that it was answered, not the answer.
