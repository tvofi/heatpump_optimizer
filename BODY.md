On a US-customary Home Assistant, a degF climate set-point was written in degC. The pump-duty arbiter converted each set-point with the entity's `unit_of_measurement`. A climate entity never declares one: its target is an attribute in the instance's unit system. So a 50 degC hot-water target reached the pump as 50 degF, which is 10 degC (D12-s3-01, high, verified; the judge merged D7-s6-91 into it). The same seam had two more defects, both verified by the catch-up judge:
- L1: the smart_write valve target (`_command_valve_target`) never converted at all.
- L2: `pump_arbiter._bounded` read `min`/`max`, which a climate state does not carry, so a climate set-point slot was never clamped.

This PR is roster group R10-FAHRENHEIT (wave 1, lane SP).

Part of #2243. This PR fixes D12-s3-01 and the two `_command_valve_target` sweep rows. D14-s3-01, the currency seam, is R10-CURRENCY's.
Part of #2242. This PR fixes L2, a P6 instance: `_bounded` reads a key a climate producer never writes, and falls back to "unbounded" without saying so. The `sensor.py` guard family is R10-SENSOR-PAYLOAD's.
Part of #2247. This PR lands ARCH3-s6 P1, the issue-writer leaf. P4 and ARCH2-s4 P1 are R10-LEAF-IMPORTS'.

The roster's `fixes` list for this group is empty, so no issue gets a closing keyword.

What changes:
- `custom_components/heatpump_optimizer/issues.py` is new (ARCH3-s6 P1, as exported). It is the repair-notice writer (`create_issue`, `set_issue`, `clear_issue`, `DOCUMENTATION_URL`) and imports only `const`. store, legionella, notifier and the arbiter now raise notices through it, so they no longer import setpoint_check. The arbiter's private `_clear` is gone. The gain is import time for tests and tools only, because Home Assistant loads the coordinator anyway; no runtime speed-up is claimed.
- `inputs.py` becomes the set-point read and write owner (ARCH3-s6 P2, amended):
  - `setpoint_and_unit`, `read_setpoint`, `write_setpoint` and `write_setpoint_c` as P2 had them.
  - **New:** `setpoint_unit` chooses the unit by **domain**. A climate entity is read and written in the instance's unit whether or not a target attribute is present. P2 as exported fell back to the state's unit when that attribute was missing or None, which is the residual the catch-up judge recorded (CATCHUP-JUDGE.md at 33ffa7aa9).
  - **New:** `setpoint_range_c` reads the range from the attributes the domain carries (`min_temp`/`max_temp` on a climate, `min`/`max` otherwise), in that same unit.
  - setpoint_check's two private readers and repairs' private `_write_setpoint` are removed, and both modules use the owner.
- `coordinator._command_valve_target` writes through `write_setpoint_c` (L1). P2 wired it to the raw `write_setpoint`, which keeps the defect. The commanded value it remembers stays degC, so the unchanged-target guard still compares degC with degC.
- `pump_arbiter._bounded(inp, slot, value, floor)` reads its range through `setpoint_range_c` (L2). `_space_target`'s "indoor entity with a flow minimum" probe read the same `min` key and now uses the same reader. `_flow_target` loses its unused `state` parameter.
- `tests/features.py`: a new section, "°F set-points: one unit rule for every set-point write (D12-s3-01, L1, L2)", with 4 checks. The two `_flow_target` checks now pass the slot entity through `hass` instead of positionally.
- `dev/audit/harnesses/r10_fahrenheit_setpoints.py` is a companion harness (fixer.md step 18). The finders' harnesses each read one private symbol that this diff moves. The companion drives only entry points both trees share, and compares against the physical conversion.

Alternatives considered:
- Land P2 as exported. Rejected: it leaves the no-target residual and L1. The block's own run on the P1+P2 tree read 3 of 4 checks failed (below).
- Fix L2 by adding `min_temp`/`max_temp` as fallback keys inside `_bounded`, which is the L2 harness's own perturbation. Rejected: it keeps reading a climate range in the state's unit, so a degF climate range would be read as degC (44.6 degF as 44.6 degC). It would also leave the arbiter as a second owner of the range rule next to `inputs`.
- Keep `_bounded(state, ...)` and derive the domain from `state.entity_id`. Rejected: the read path keys on the entity id, the stub states carry none, and two keys for one rule is the duplication this group removes.

## Head

`55fd737d9ac86a0fff482ca59653d65979c5f759`

It is cut from `origin/main` 5603ee319 (#2245's merge) and has two commits: the fix, and `record: max_class_loc 8705 -> 8690`.

## Mutation proof

Each mutant was applied to the committed fix and restored with `git checkout --`. Each was run with `python3 tools/audit/seat/features_block.py "°F set-points: one unit rule"`:
- M1, `setpoint_unit`'s climate predicate → `if False:` (GUARD_OFF): 3 of 4 failed. The checks that went red were `a degF climate with no target attribute is still written in degF`, `the smart_write valve target is written in the entity's unit, once, and remembered in degC (L1)` and `a climate set-point slot is clamped to its own min_temp/max_temp, read in the instance's unit (L2)`.
- M2, `write_setpoint_c` writes `value_c` unconverted: 3 of 4 failed (D12-s3-01 with 6 of 12 cells misdelivered, no-target, and L1).
- M3, `_command_valve_target` calls the raw `inputs.write_setpoint`, which is P2's wiring: 1 of 4 failed (L1).
- M4, `_RANGE_KEYS` emptied: 1 of 4 failed (L2).

Dropped pins: 11 `killed_by` entries whose `old` lines this diff moves or rewrites. `tests/mutation_table.py` listed each as "disposition names no site the inventory generates":
- 6 in `pump_arbiter.py`: `_bounded`, `_flow_target`, `_observed`, `_space_target`, and two in `desired`.
- 5 in `setpoint_check.py`: `_read_setpoint`, two in `_setpoint_and_unit`, and two in `set_issue`.

The same guards now live in `issues.set_issue` and `inputs.setpoint_and_unit`/`read_setpoint`. They are unpinned sites until mutation-autofix pins the kills.

## Unpinned sites

Every site `prepr.sh` step 6d lists. The predicates this fix adds are shown killed by `tests/features.py` in M1-M4 above. The rest are the moved bodies of guards main had pinned at their old anchors (the 11 dropped pins). A survivor that the autofix reports comes back to this seat for a written triage.

- `custom_components/heatpump_optimizer/coordinator.py:7298 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:368 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:379 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:381 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:391 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:395 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:399 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:403 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:409 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:420 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:425 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:435 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:441 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/inputs.py:455 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/issues.py:44 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/issues.py:53 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:399 GUARD_OFF`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:433 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:515 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:598 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:605 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:756 RETURN_DEL`: pinned by mutation-autofix (`ci-autofix.md`).

## Null control

- On a degC instance, the companion harness reads 0 at both ends: `write_cells_degC_null`, `valve_degC_null` and `range_number_degC_null`.
- `surface_units.py`'s `null_misdelivered_cells` reads 0 of 6 at both ends.
- `setpoint_unit.py`'s `roundtrip_error_null_K` reads 0.000 at both ends.
- `realha_climate.py`'s `null_metric` reads `delivered_error_K=0.000` at both ends.
- The new features block at the merge base: 4 of 4 checks fail, and every degC cell in their output is already correct. Only the degF cells and the climate range differ.
- The companion's `--perturb` (the domain rule removed in memory, at the head) moves `no_target_degF` 0 → 2 of 2 and `range_climate_degF` 0 → 2 of 4. Every degC null stays 0.

## Figures

Harness sha1s: `surface_units.py` d741b52a (`dev/audit/rounds/round10/D12/s3/` at the merge base), `setpoint_unit.py` 386e5afb (`dev/audit/rounds/round10/D7/arch3-s6/` on `handoff/audit-r10-arch3-s6` at 532d8d09d), and the catch-up harnesses on `handoff/audit-r10-catchup-verify` at 33ffa7aa9: `l1_valve_unit.py` a9fadaed, `l2_bounded_climate.py` 5ff600f1, `cross.py` fda8e220, `realha_climate.py` 459f055b. Each was run from a `git archive` export of the merge base and from the head worktree, with `PYTHONPATH` as its docstring states. load1 on this seat was 42-50 throughout; nothing timed is claimed.

- D12-s3-01, `surface_units.py`: base `misdelivered_cells=2 cells (of 6)`, null 0. Base `--perturb` reads 0 / 0.
  At the head, the harness's two private names moved, so it runs through a wrapper. The wrapper aliases `setpoint_check._read_setpoint` to `inputs.read_setpoint` (cross.py arm a's alias) and restores `pump_arbiter.state_unit` as an alias, because the harness patches it even unperturbed. Neither alias is on the write path. Head: `misdelivered_cells=0 cells (of 6)`, null 0.
- D7-s6-91, `setpoint_unit.py`: base `roundtrip_error_defect_K=42.222`, null 0.000. Head: 0.000 / 0.000.
- Real Home Assistant oracle, `realha_climate.py`: base imperial `payload=55.0 device_C=12.778 delivered_error_K=42.222`. Head imperial `payload=131.0 device_C=55.000 delivered_error_K=0.000`. Metric is 0.000 at both ends.
- L1, `l1_valve_unit.py`: base `main arm_climate_on_degF_instance ... abs_err=48.8` and `arm_number_degF_on_degC_instance ... abs_err=48.8`, nulls 0.0, perturbed 0.0.
  Head: main arms `abs_err=0.0` on all four. Its perturbed arm then stops with `AssertionError: anchor moved`, because it splices source into the method this diff rewrote, so its sibling arm does not run at the head. That sibling, the arbiter's climate write, is `setpoint_unit.py`'s and the companion's `write_cells` above.
- L2, `l2_bounded_climate.py`: base `main arm_climate out_of_range=3 of 4`, null 0, perturbed 0, and reach `command.dhw=55.0 outside_range=1`. At the head it stops with `TypeError` on `_bounded(state, v)`, because the signature changed, so the companion's `range` arms stand in for it.
- Companion, `dev/audit/harnesses/r10_fahrenheit_setpoints.py` (sha1 7a7a2ac3 as run; its docstring then gained the Expected line), at the merge base and the head:
  - write cells degF: 2 → 0 of 6
  - write cells degC null: 0 → 0 of 6
  - no-target degF: 2 → 0 of 2
  - valve degF: 2 → 0 of 2
  - valve degC null: 0 → 0 of 2
  - range climate degF: 3 → 0 of 4
  - range climate degC: 3 → 0 of 4
  - range number degC null: 0 → 0 of 4
- New features block: merge base `4 of 4 FEATURES BLOCK FAILED`. The P1+P2 tree as exported: `3 of 4 FEATURES BLOCK FAILED` (the D12 cells pass; no-target, L1 and L2 fail). Head: `ALL 4 FEATURES BLOCK PASSED`.
- Seams, rule `git grep -nE 'set_temperature|"set_value"|temperature_from_c\(|state_unit\(|get\("(min|max|min_temp|max_temp)"\)' -- custom_components` at the head. Every hit and its disposition:
  - `inputs.py` 355-357, 381, 455: the owner, closed here.
  - `setpoint_check.py:95`: the DHW Fix value, whose unit now comes from `setpoint_and_unit`. Closed here.
  - `coordinator.py:1945`, `1963`: price units. Not temperature; out of class.
  - `coordinator.py:2010`: the DHW inlet *sensor*, which declares its own unit. Already guarded.
  - `coordinator.py:10718`, `freq_control.py:97`: compressor Hz, number domain. Not temperature.
  - `config_flow.py:712-713`: the options UI's number-selector bounds. Not an entity.
  - `inputs.py:931`: a flow sensor. Not temperature.
  - `climate.py:334`: the integration's own climate entity receiving writes; Home Assistant converts into its declared `temperature_unit`. Already guarded.
  - `pump_arbiter.py:812`: GCHV night-mode hours. Not temperature.
  - The `strings.json` and translation hits are a translation key.
- `python3 tests/structure.py --record`: `max_class_loc` 8705 → 8690. No other row moved; reason in the record commit. `python3 tests/structure.py` then exits 0.
- `python3 tools/audit/archscore/score.py --diff 5603ee319`: `Architecture score: dS +0.0028 IMPROVES`, `coord_footprint 2580 -> 2575`.
- `python3 tests/typing_ruler.py`: `ALL 9 typing-ruler checks PASSED`. The first draft added 3 mypy errors in `inputs.py`, fixed by an early return on a missing entity id.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Scope: `python3 tests/closure.py select --diff 5603ee319 ...` printed `MODE: FULL`, because "no recorded closure mentions custom_components/heatpump_optimizer/issues.py". The new module is recorded by `closures-autofix` (`ci-autofix.md`), not by a Darwin re-derivation. Until then, 28 recorded closures reach a changed file.
  Run locally under `PYTHONPATH=tests/hastub` with the seat venv:
  - `tests/features.py` `ALL 4111 FEATURE CHECKS PASSED`. This ran on the pre-squash tree, before the typing early return; that edit is a no-op on every check's inputs, and CI re-runs it at the head.
  - `tests/guard_pins.py` `ALL 50 GUARD PIN CHECKS PASSED`
  - `tests/config_flow_steps.py` `ALL 499 checks PASSED`
  - `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`
  - `tests/doc_claims.py` `ALL 169 checks PASSED`
  - `tests/entities.py` `3 of 2318 ENTITY CHECKS FAILED`. All 3 are issues.py's classification ("these force the FULL suite when touched: custom_components/heatpump_optimizer/issues.py", and the two whole-package coverage checks). The autofix's recording closes them.

  Left to CI as heavy (golden with `GOLDEN_MODE=drift` against 5603ee319, optimality, stress, backtest). No golden claim is filed: no plan value reads a set-point unit, and FakeHass has no unit system.

## Red checks

none yet. `prepr.sh`'s CI PREDICT expects 3 reds on `closures` and `fast` against 5603ee319, all from the new `issues.py`: `closures` UNDER-SCOPED, and `tests/entities.py`'s classification checks (the same 3 that fail locally, above). Under `ci-autofix.md` these are the `closures-autofix` bot's to record. They are named here and answered by its commit, not by hand. Their cheaper detector is `prepr.sh` itself, which already caught them before the push.

## Forward-carry

none. Nothing found here changes how a later stage works. The one constraint the roster carried into this group (P1 before P2, and P4 going to R10-LEAF-IMPORTS) is already in that group's brief.

## Friction

- brief-mechanics: contradiction: the shared FIXER-BRIEF said "closing keyword ... one per line", while the roster's group entry says closing keywords only for `fixes`, which is empty here. Each of #2243, #2242 and #2247 also holds another group's finding, so this body uses Part of.
- l2-harness: cost: the catch-up harnesses for L1 and L2 call `_bounded(state, v)` and splice source into `_command_valve_target`. Any fix that changes either signature or body cannot re-run them at its head, so a companion was needed.
