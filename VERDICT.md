Fix review: blocked 89f4b0324b442b4875d7c8790fc90baf62d5a2e2 class-open: axis numeric options that an earlier release stored as non-numbers unenumerated (e.g. day_start_hour)

bus-nonce: 7f12accf7f8af5227bf5f8c2e90dfac0

Round 4 of this PR, the re-cut. Rounds 1 to 3 blocked at 40328a85 (`class-open: wood_fuel.lighting_window`, one site) and at 98cb43e7 (`mutation-vacuous`). This is the first block on this axis, so the open-axis rule's escalation (addendum item 10) does not apply yet. Review scope: full; the packet was rendered with no `--reviewed-head`.

## Block

- class-open, axis `numeric options that an earlier release stored as non-numbers`, the body's own set. Its rule is `entry_config._DEFAULTED_NUMBERS` (`finite_float`, `_nonzero_number`, `_interval_minutes`, `_lead_minutes`). The body's only residue is `_refused_number` ("`_refused_number` keys are left alone"). The seven `EntryConfig` fields parsed by `_whole` are numeric options, and neither the rule nor a stated residue category covers them: `day_start_hour`, `day_end_hour`, `day_start_hour_weekend`, `day_end_hour_weekend`, `holiday_day_start_hour`, `holiday_day_end_hour`, `ecl110_mqtt_qos`.
  - The finding's own failure reproduces on six of them at the head. The driver is the finder's `config_fuzz.run` scenario at version 5, with each key added to `HEALTHY` and then set to `"abc"`, `None`, `[v]` or `{"v": v}` (ev/whole-keys-census-all-head.txt). The result is `RESULT census_fail=24 of 32`: migrate `ok`, build `ok`, and both cycles `UpdateFailed: Error updating data: could not convert string to float: 'abc'` (or the `float() argument must be ...` variant). The merge base fails the same way, `census_fail=12 of 16` for the hour keys probed there (ev/whole-keys-census-head-base.txt).
  - Null controls: the unmutated entry with the extra keys gives `CTRL` ok at both ends. `ecl110_mqtt_qos` and `silent_mode_power_fraction` survive all four ops.
  - Mechanism (ev/comfort-band-probe-head.txt): `coordinator._update_current_state` calls `_audit_comfort_band`, which calls `comfort_band.violations({}, ctx._config)`. `comfort_band.effective` returns `float(current.get(key, default))` on the raw stored value, so `int(eff(CONF_DAY_START_HOUR, ...))` raises. At the head, `EntryConfig.from_mapping({"day_start_hour": "abc"}).day_start_hour` is `7` (the parse defaults it), while `number_repairs({"day_start_hour": "abc"})` is `{}`, so the migration leaves the text stored. Numeric text (`"7"`) passes.
  - This is the reader the body itself names for D1-s2-05 ("`comfort_band.effective` read it raw"). The pinned test's selector `_mig_defaulted` requires `type(_twelve) is float`, which excludes every `_whole` field by construction. The finder's `config_fuzz.HEALTHY` holds 18 keys and none of the seven, so its `permanent_cycle_fail ... all 0` at the head cannot reach this part of the set.
  - To close it: extend the rule to the `_whole` keys (`int` of numeric text, drop the rest), or state a residue category that holds them with its reason. Pin it with the same shape as the existing check, plus a null control.

## Findings

none

## Evidence

- Head measured: 89f4b0324b442b4875d7c8790fc90baf62d5a2e2, the PR head and the head the body names (ev/HEAD.txt). Merge base: f269ecccb5f1dfd21eca03a3d5dcc43b3a145603. `dev/governance/roles/` matches between the merge base and origin/main except for main's newer `fix-review.md`/`fixer.md`. I followed main's copy (the role pack rendered at origin/main f88ec8f8).
- Merge: `git merge-tree --write-tree origin/main <head>` rc=0, no conflict (ev/merge-tree.txt).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/` and `*budgets.json`: the three-dot diff is empty, and no claim file is touched.
- Finder's harnesses from the plan export 819aa2e3 (parsers_fuzz sha1 74da66cd, config_fuzz sha1 c0ecf63a, both matching the body), merge base f269ecc then head (ev/finder-harness-base-head.txt, raw output in ev/raw/). The body measured its base at e893cd3d. Every figure re-derives here:
  - `pump_nonfinite_flag_true` 10 then 0; `pump_nonfinite_freeze_fault` 5 then 0; `pump_null_control_zero_flag_true` 0 at both ends.
  - `openmeteo_year1_solve_failures` 3 then 0; `openmeteo_healthy_solve_failures` 0 at both ends.
  - `unit_mismatches` 0 and 0; `temperature_roundtrip_disagreements` 0 and 0 of 35 probes; `above_max_accepted` 0 and 0 of `keys=15`.
  - config_fuzz v1..v6: `build_fail` 8, 11, 10, 9, 5, 11 then all 0; `permanent_cycle_fail` 17, 14, 16, 12, 17, 12 then all 0; `migrate_fail` 0 and `CTRL` ok at both ends.
- Reviewer's mutants at the head, each restored with porcelain empty (driver ev/mutation_driver.sh, output ev/mutants-head.txt). All killed:
  - `kept` = every index; `len(kept) < 1`; the floor without `+ resolution` (tests/open_meteo.py);
  - lead parsed by `finite_float`; lead ceiling dropped; lead floor strict (tests/wood_advisor.py);
  - `parse_bool` reverted; `_begin` guard off; `plausible_c` one-sided (features.py block "Non-numeric inputs (v5.3.0)", clean `ALL 44 FEATURES BLOCK PASSED`).
  - The `tests/entities.py` kills (`if repairs:`, `_interval_minutes` bounds) were not re-run and are cited from the ledger records in the diff.
- The interval/lead reader census at the head: every reader of `optimization_interval` and `wood_lighting_lead_minutes` goes through the `EntryConfig` field. `sysid.py:1359` reads the constant.
- Step 16: the diff adds no path that skips an actuator write.
- Instruments built by this reviewer, not the finder: ev/census_driver.py (it imports the finder's `config_fuzz` and adds keys to `HEALTHY`) and ev/mutation_driver.sh.
- CI: `merge_train.py classify` exits 3 with `WAIT 89f4b0324b442b4875d7c8790fc90baf62d5a2e2 pending: gate red: none` (ev/ci-classify-poll.log). The block above is on code, not on CI. The packet's digest `gate failure` is the aggregate; classify reads no red.
- Closing self-audit: `carry_audit.py check` rc=0, `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`. The `--body` input was the live body's `## Forward-carry` and `## Friction` sections, copied by hand because this seat has no `gh`.
