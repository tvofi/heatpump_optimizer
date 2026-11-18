R11-SEAM-inputs-guards: every value entering through `inputs.py` is tested finite and in domain. The fixes are a boolean parser that refuses non-finite codes, an irradiance parser that keeps only representable sample spans, entity slots that accept only text, and numeric options that an earlier release stored as non-numbers, repaired at migration. Of the six findings, three reproduce at the merge base and are fixed here. Three read 0 there and get a regression pin only (owner precedent 1, 2026-11-18): "not reproduced at main, pinned".

| finding | at merge base | here |
|---|---|---|
| D1-s3-01 `inputs.parse_bool` reads `nan`/`inf`/`1e309` as a fault and a defrost | reproduced | fixed: `finite_float` before the numeric arm |
| D1-s3-03 a year-1 Open-Meteo stamp makes `IrradianceSeries.mean_over` raise for every step | reproduced | fixed: `_parse_block` drops a sample whose span `(t - resolution, t]` is not representable |
| D1-s2-05 a non-number under a numeric option of an earlier-version entry fails setup or every cycle | reproduced | fixed: `async_migrate_entry` applies `entry_config.number_repairs`; `InputReader._begin` reads a non-text slot as unset |
| D2-s3-02 minor-unit price scale | not reproduced at main, pinned | the existing `_P8_FACTORS` check is the pin (mutation below) |
| D7-s3-01 Fahrenheit inverse | not reproduced at main, pinned | new round-trip check over every `TEMPERATURE_UNIT_TO_C` row |
| D1-s2-51 plausible window upper edge | not reproduced at main, pinned | new check: every window refuses one degree past either end |

Design, D1-s2-05. `EntryConfig` already parses each declared numeric key once (`finite_float`, or `_nonzero_number` for the tank volume). But `EntryConfig.__getitem__` returns the stored value, and the thermal table (`thermal_model._tabled_values`, `ThermalParameters.from_config`, `_flow_curve_values`) and `comfort_band.effective` read it raw. Three alternatives were considered:

- **Coerce at every raw reader.** Patches enumerated cases where a structural fix exists, in a four-group hot file (`thermal_model.py`).
- **Make `__getitem__` return the parse.** Changes what every `config.get(key, default)` in the package reads, for instance `None` where a default was read. That is a behaviour change across the package, far outside this seam.
- **Repair the stored entry at migration** (taken). Plan Tradeoff T4 (SCENARIOS.md): "a strict boundary rejects values an earlier release stored, which then needs a migration rather than a refusal".

`number_repairs` is keyed on the declared parses alone, restricted to the two parses under which a refused value and an absent key parse alike. Numeric text is stored as its number, and anything else is dropped. This is a design choice the check encodes: no parsed field moves. `_refused_number` keys (where a stored refusal deliberately differs from absent) are left alone. A list or dict entity slot is outside `EntryConfig` (`outdoor_temp_entity` is not a field), so it is refused at the one reader edge, `InputReader._begin`.

## Head

fe297f1b14ac6107174c41ef8ecea58d6871570d, on merge base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f (origin/main at ae0ed64af898d8923ac35afe6e9c031ac1e6b111 at 2026-11-18T14:31:41Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict).

## Mutation proof

Each fix line was reverted, its check run, and the file restored (`git status --porcelain` empty after each):

- `parse_bool` restored to `float(token) != 0.0`: `FAIL parse_bool reads no non-finite number as a flag (D1-s3-01)` (features block "Non-numeric inputs (v5.3.0)", 1 of 42 failed).
- `_begin`'s `isinstance(entity_id, str)` guard deleted: the same block dies with `TypeError: cannot use 'dict' as a dict key (unhashable type: 'dict')` at the check "a slot holding a dict or a list reads as unset, not a raise (D1-s2-05)".
- `_parse_block`'s `kept` filter replaced by every index: `FAIL a stamp with no representable span is dropped, and the block still averages` (`tests/open_meteo.py`, 1 failed).
- `async_migrate_entry`'s `repairs` replaced by `{}`: `FAIL an old entry's non-numbers under numeric options are repaired` (`tests/entities.py`).
- `number_repairs` mapping every key to `None`: the same check fails (the tank volume's `"200"` is dropped, not stored as `200.0`).
- Pin D2-s3-02, `/ 100.0` removed from `normalize_price_per_kwh`'s minor branch: `FAIL normalize_price_per_kwh takes each unit to major currency per kWh` and `FAIL the price entity's today/tomorrow rows are read in their unit` (features P8 block).
- Pin D7-s3-01, `temperature_from_c` multiplying by the factor: `FAIL temperature_from_c inverts every unit row the reader converts (D7-s3-01)`.
- Pin D1-s2-51, `plausible_c` one-sided (`window[0] <= value_c`): `FAIL every plausible window refuses a reading one degree past either end (D1-s2-51)`.

## Null control

Each new check carries its own null control, which passes unmutated:
- `parse_bool("0")`, `("1")` and `("0.0")` still read.
- `plausible_c` accepts every window's midpoint.
- The year-1 block averages to the clean block's mean over the same three hours.
- The migration's no-parsed-field-moves check covers the repair, and the existing "an old entry is stamped forward without touching its data" covers a healthy entry.
- The healthy control `CTRL vN` of `config_fuzz.py` reads ok for v1 to v6 at both ends.
- `parsers_fuzz.py` prints `pump_null_control_zero_flag_true` and `openmeteo_healthy_solve_failures`, both 0 at both ends.

Reach of the D1-s2-05 repair: `async_migrate_entry` runs for `entry.version < CONFIG_ENTRY_VERSION`, the reach the judge recorded for the finding (current-version input is validated by the options flow).

`plausible_upper.py` reads `above_max_accepted=0` at the merge base under its `--perturb` arm too, so it reads flat at both ends. Its companion is the new window check above, which reads the defect under the one-sided mutant and not at the head.

## Figures

Each harness runs from the plan export (`EXPORT=$(mktemp -d); git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11 | tar -x -C $EXPORT`), cwd the tree measured, merge base then head:

- `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py` (sha1 2798c36ffd4249510a855e85e57531890b7cd312), `RESULT unit_mismatches`: 0 then 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only temperature_roundtrip` (sha1 aaef9a3b34b9c3d8a523eb24410ff97f7ce6b0d1), `RESULT temperature_roundtrip_disagreements` of `temperature_roundtrip_probes=35`: 0 then 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/s3/parsers_fuzz.py --arm pump` (sha1 74da66cd7b0beac627cb2a636e6c0364c1ddc019):
  - `RESULT pump_nonfinite_flag_true`: 10 then 0
  - `RESULT pump_nonfinite_freeze_fault`: 5 then 0
  - `--perturb parse_bool_finite` at the merge base: 0
- `... parsers_fuzz.py --arm openmeteo`, `RESULT openmeteo_year1_solve_failures`: 3 then 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/leads/plausible_upper.py` (sha1 9b1e8fe8e0bb3d18ef6f78538861df6666219fc2), `RESULT above_max_accepted` of `keys=15`: 0 then 0.
- `PYTHONPATH=tests/hastub:tests python3 $EXPORT/dev/audit/rounds/round11/D1/s2/config_fuzz.py --versions N` for N in 1..6 (sha1 c0ecf63a890da1586d08436ad77d8df455b51af6; it needs `tests` on the path for `harness`):

  | `RESULT vN_` | merge base, v1..v6 | head, v1..v6 |
  |---|---|---|
  | `build_fail` | 8, 11, 10, 9, 5, 11 | all 0 |
  | `permanent_cycle_fail` | 17, 14, 16, 12, 17, 12 | all 0 |

  The first head cut (non-numbers dropped, numeric text kept) left `permanent_cycle_fail` 1 at v2 and 2 at v5, all `op=str_of_num key=dhw_tank_volume`. Numeric text is now stored as its number.
- Class seams (fixer.md step 8). The round's P1 enumerator (the sweep's `enumerate_p1` script) and its probes are named in `sweep-P1.md` but present at no fetched ref: not at the plan export, not at any `dispatch/sweep-r11-SW*` or `dispatch/verify-r11-J1-evidence`. In its place, the enumeration is `sweep-P1.json`'s `instance_list` at the plan export, each against its disposition:
  - `quiet_windows.measured_ceiling_kw` `CONF_COMPRESSOR_FREQ_MIN_HZ` / `CONF_COMPRESSOR_FREQ_MAX_HZ`: closed for an earlier-version entry by the same repair. `number_repairs({k: "abc"})` maps each to `None`, and `{k: 42.0}` maps to `{}` (the null).
  - `topology._slot_extras` (`manual_setpoint`, stored key `mixing_valve_target`): closed for an earlier-version entry. The key was undeclared in `EntryConfig` (`number_repairs({"mixing_valve_target": "abc"})` printed `{}` at the first head cut); it is now declared with `finite_float` and its default, and the migration test stores `"abc"` there and reads it dropped.
  - `early_cutoff.arm` `optimization_interval` domain (1e12, -5, 0 passed): closed here. `EntryConfig` parses the interval with `_interval_minutes`, which reads a value outside `(0, a day]` as the default. The options flow's narrower 10 to 120 stays the flow's to own (`config_flow.option_range`), and `entry_config.py` sits below the flow. The day bound is physical: past it the plan outlives the day-ahead prices it was solved against. Pinned by "an optimization interval outside (0, a day] parses as the default" and its null control (10, 120 and 1440 read as stored).
  - `thermal_model._tabled_values` / `_flow_curve_values` / `ThermalParameters.from_config`, `comfort_band.effective`: closed here (D1-s2-05, `config_fuzz.py` above).
  - `inputs.parse_bool`: closed here (D1-s3-01).
  - `open_meteo._parse_block`: closed here (D1-s3-03).
  - `inputs.plausible_c`: already guarded, pinned here (D1-s2-51).
  - `boost._restore_settle`: distinct finding D1-s2-06, not this group's.
  - `coordinator._parse_ecl110_state`: distinct finding D1-s3-02, carried by R11-SEAM-inputs-freshness per the plan.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`. Local runs at the head tree, each green:
  - `tests/entities.py`
  - `tests/open_meteo.py`
  - `tests/finite_boundary.py`
  - `tests/guard_pins.py`
  - `tests/config_flow_steps.py`
  - `tests/env_drift.py`
  - `GOLDEN_MODE=drift tests/golden.py` ("NO UNCLAIMED DRIFT")
  - `tests/structure.py` ("STRUCTURE RATCHET PASSED")
  - the two features blocks, through `tools/audit/seat/features_block.py`

  The rest of `scope.run` is left to CI (brief: scoped prepr, CI is the authority).

<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=fe297f1b14ac6107174c41ef8ecea58d6871570d -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`. `python3 tests/ci_ratchet.py` grades every `archscore.*` row at or under its budget. The one budget this diff touches is the `tests/entities.py` N-log-flood reasoned list: `("__init__.py", "async_migrate_entry")` goes from 1 to 2. That site is the migration's one-shot repair warning, which fires once per upgraded entry, under the list's existing "a transition notice" reason. It is not a persisting condition.

## Unpinned sites

- custom_components/heatpump_optimizer/__init__.py:229 GUARD_OFF: pinned by mutation-autofix; killed by "a healthy old entry migrates with no repair warning (null control)" (`tests/entities.py`)
- custom_components/heatpump_optimizer/inputs.py:966 RETURN_DEL: pinned by mutation-autofix; killed by "and the codes either side of it still read (null control)" (`tests/features.py`)
- custom_components/heatpump_optimizer/inputs.py:1035 GUARD_OFF: pinned by mutation-autofix; every slot then reads unset, killed by "a fresh sensor reads normally" (`tests/features.py`)
- custom_components/heatpump_optimizer/open_meteo.py:255 CMP_BOUND: pinned by mutation-autofix; killed by "a stamp with no representable span is dropped, and the block still averages" (the year-1 01:00 stamp sits exactly on the floor) (`tests/open_meteo.py`)
- custom_components/heatpump_optimizer/open_meteo.py:256 CMP_BOUND: pinned by mutation-autofix; killed by "the floor keeps a stamp exactly one resolution past year 1, and two kept samples are a series" (`tests/open_meteo.py`)
- custom_components/heatpump_optimizer/open_meteo.py:256 GUARD_OFF: pinned by mutation-autofix; killed by "a stamp with no representable span is dropped, and the block still averages" (`tests/open_meteo.py`)
- custom_components/heatpump_optimizer/entry_config.py:52 CMP_BOUND*2: pinned by mutation-autofix; `0.0 <` loosened is killed by "an optimization interval outside (0, a day] parses as the default" (0 reads as stored), `<= _MAX_INTERVAL_MINUTES` tightened by "and one inside it, both ends' neighbours included, is read as stored (null control)" (1440 reads as default) (`tests/entities.py`)
- custom_components/heatpump_optimizer/entry_config.py:52 GUARD_OFF: pinned by mutation-autofix; every interval then reads as the default, killed by the same null control (`tests/entities.py`)
- custom_components/heatpump_optimizer/entry_config.py:54 RETURN_DEL: pinned by mutation-autofix; an in-domain interval then reads `None`, killed by the same null control (`tests/entities.py`)

## Red checks

- `mutation`: red by construction on the 9 sites under `## Unpinned sites`; mutation-autofix pins killed sites after the push. No cheaper detector exists: the ledger pin is written only from CI's own mutant run (ci-autofix.md).

## Forward-carry

none

## Friction

- fixer: stale: fixer.md step 8, the class enumerator the brief names as the fitness function (`D14/sweep-P1/enumerate_p1.py`) and its probes are at no fetched ref, so this body enumerates from `sweep-P1.json`'s `instance_list` instead. Carry: dismissed: the absence is recorded under Figures, and the round-end triage reads it there.
- brief: contradiction: dispatch 85e4ae3af9, "Do your work inline, with no subagents" against the frugal inline-read guard. The seat blocked on this (b3487530). Carry: dismissed: answered by the orchestrator's inbox ruling, line 1 of refs/heads/inbox/r11-seam-inputs-guards.
