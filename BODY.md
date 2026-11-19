R11-SEAM-actuation-release (round 11, size L), per the approved design `design/R11-SEAM-actuation-release` at 349d6277f25fb6855b58395bcb7f055f2e40d86d (verdict `design-verdict/R11-SEAM-actuation-release` at 4554fc2d66447b82a2f54b9aae36defb421d5786), ADR-004 and ADR-001 arm `notice` at plan 819aa2e354b4e5baaf824b8568fd72bea8168a75, findings at register 0a7ea717c6d99fd179af08f31484390d0080cb01. `dev/audit/rounds/round11/ISSUES.json` there records no issue number for any of the six findings (`number` is null on every entry), so this body closes none.

- **Registry (D16-s3-04, D1-s2-04).** `off_restore.py` restores in registration order, one attempt per armed key, skips a key whose restore is in flight and refuses an arm of it, saves only when the armed set changed, and takes a lock across the record's first read with `loaded` set after it lands. `async_cycle`, called once per cycle from `_apply_action` before its Off and stale returns, restores every armed key while the mode is Off (the retry) and the `stale=True` keys while a plan mode's plan is stale. `register_release` is the second registration form, armed as a neutral entry; the stored document and store version are unchanged.
- **Consumers (D16-s3-02, D16-s3-01, D16-s1-04).** Supply switch (`pump_arbiter.SUPPLY`, on, stale), the arbiter's row (`pump_arbiter.ROW`, by `_release_row`), both circulation pumps (new `circulation.py`: the write, the per-entry record, the restore; the space pump stale), compressor frequency and valve target (reading before the first write, stale). The supply registers before the row. `pump_arbiter.release` writes nothing.
- **Baseline row (D16-s3-03).** `pump_arbiter.baseline_row` builds it with `disinfecting` false and no `dhw_reason`, space set-point excluded; Off and unload both reach it through the registry.
- **Notice arm (D7-s1-05, ADR-001).** `LegionellaGuard._interval_notice` formats both day-count notices.
- **Re-pin.** The `R10-ARBITER-OFF-RESTORE` check that Off writes the space baseline "and nothing else" is re-pinned to `dev/governance/dimensions/D16.md`'s ruling of 2026-11-15 (each written entity returned to its baseline once); its null control (duty observe) is unchanged. The R10 removal check (C4) is re-pinned too, as the design's registry bullet requires: a neutral entry still armed at removal was dropped silently and is now named once, with no value. `docs/configuration.md` states the new rule, `docs/architecture.md` the new module.

Departures from the design note, each pending owner confirmation:

- **Frequency and valve owners' glue is not in `freq_control.py` / `mixing_valve.py`.** Both are pure modules and `fixer.md` step 17 reads "no `homeassistant` import added to model, optimizer or learner modules". The write's tail (dedupe, arm, send, record) is beside the record as designed, `FrequencyWatchdog.command` and `mixing_valve.ValveTarget.command`, with `arm` and `send` passed in; the registration and the entry-keyed owner table are in `coordinator.py` at module scope. Control under Figures: the design's placement reads `layer_violations 13->15` and `import_cycle_modules 0->3`. decision: orchestrator.
- **Unload restores twice**, before and after `async_shutdown` (design note item 3): a write landing during a later key's restore re-arms a key the first pass has passed, and only the latch stops further arms.
- **Unload writes the row whatever the power switch reads** (verdict item 9 keeps Off deferring it): an unload has no next cycle, and the base's `release` wrote it unconditionally.
- **Stale-plan release of frequency, valve and space pump is kept as designed** (`decision: owner` in the design note). The finder's `cells.py` null arm `baseline-on` now reads `FAIL [stale]` on that one restore write of `number.hp_freq`; see Figures. Narrowing to the supply switch is `stale=True` removed at `coordinator.py`'s `_register_number_restore` and `circulation.py`'s `_register(SPACE, ...)`.
- **A frequency or valve entity with no readable state is no longer written**: the registry refuses a write whose baseline it cannot capture (`off_restore.async_arm`, the rule the space set-point already follows). Two existing valve checks changed for it (`tests/features.py` `_df_valve` "climate on degF, no target", and `_write_coord`'s seeded states).

## Head

`5dd27cfd07c5a5c655d1429be3fac51200d089b7`, measured at it against the merge base `8751943e17ef4d3ec699e7859ae829b4528d8ce7`; `origin/main` at `1723f9fdc9d8a6e6987190d2887686297a621dd4` (2026-11-19T00:57Z), which `git merge-tree --write-tree origin/main HEAD` merges with no conflict.

## Mutation proof

Each mutant applied in a detached worktree at the head, the `R11-SEAM-actuation-release` section of `tests/features.py` run alone (`tools/audit/seat/features_block.py` from its first line to the `R10-HOTFIX-FLOW-SETPOINT-STUCK` marker; the rest of the file is CI's `tests / mutation`), restored. Unmutated the section passes. `SUMMARY killed=32 survived=0`:

- M01 `off_restore.py`: loaded set before the read lands: KILLED by "D1-s2-04: an off restore running while another caller's first read of the record is in flight waits for it: the baseline 3.0 is written back once, the"; "D1-s2-04: the record reads as not loaded while its first read is in flight".
- M02 `off_restore.py`: no lock on the first read: KILLED by "D1-s2-04: the record reads as not loaded while its first read is in flight".
- M03 `off_restore.py`: cycle entry: Off restores only stale keys: KILLED by "D16-s3-01: Off returns the pump's mode select to the baseline row on the Tuya arm (the arbiter had written the hot-water duty)"; "D16-s3-04: a restore of number.water_set that raised at the change into Off is retried by the Off cycles: exactly one write lands and the entity reads" (+2 more).
- M04 `off_restore.py`: cycle entry: stale plan restores nothing: KILLED by "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl"; "D16-s1-04: a second stale cycle writes nothing to the four restored entities, and the restore is recorded as plan_stale" (+2 more).
- M05 `off_restore.py`: restore does not skip an in-flight key: KILLED by "two restores running at once on one entry send a key's restore write once, the summed count being 1".
- M06 `off_restore.py`: arm not refused while the restore is in flight: KILLED by "in-flight guard: async_arm refuses (False) a key while that key's restore write is awaited, and accepts it again (True) once the restore has finished"; "a circulation pump's off command whose restore cannot be armed is not sent and not recorded".
- M07 `off_restore.py`: save on every restore pass: KILLED by "registry (d): a pass that restores nothing does not save the store, one that restores saves it once".
- M08 `off_restore.py`: armed order, not registration order: KILLED by "registry (a): restores run in registration order, though the keys were armed in reverse".
- M09 `off_restore.py`: stale_only filter dropped: KILLED by "D16-s1-04: a second stale cycle writes nothing to the four restored entities, and the restore is recorded as plan_stale"; "D16-s1-04: a third stale cycle writes nothing at all" (+2 more).
- M10 `off_restore.py`: a release answering False is disarmed: KILLED by "D16-s3-01: Off returns the pump's mode select to the baseline row on the Tuya arm (the arbiter had written the hot-water duty)"; "verdict item 9: Off taken on an idle step sends the supply switch on but writes no mode select while the switch still reads off, and the row stays arm" (+2 more).
- M11 `circulation.py`: circulation: off write not armed: KILLED by "D16-s3-02: after off the supply switch, the frequency, the valve and the circulation pump read what they read before the optimizer's first write, each"; "D16-s3-02: after unload the supply switch, the frequency, the valve and the circulation pump read what they read before the optimizer's first write, e" (+2 more).
- M12 `circulation.py`: circulation: restore keeps the record: KILLED by "design invariant 2, hot-water circulation pump: after Off the record has no entry for the pump, and after On its next off command is sent again"; "a stale-plan cycle switches the space circulation pump back on and empties its record".
- M13 `circulation.py`: circulation: space pump not restored on a stale plan: KILLED by "a stale-plan cycle switches the space circulation pump back on and empties its record".
- M14 `circulation.py`: circulation: failed command recorded: KILLED by "a circulation pump command whose service call raised is not recorded, and the same command is sent again".
- M15 `pump_arbiter.py`: baseline row keeps the cycle flags: KILLED by "D16-s3-03: unloaded while the integration holds the pump's disinfection (the arbiter raised the tank to the cycle target 60), the tank set-point reads"; "D16-s3-03: the baseline row under a disinfection hold carries the configured 50".
- M16 `pump_arbiter.py`: supply off write not armed: KILLED by "D16-s3-02: after off the supply switch, the frequency, the valve and the circulation pump read what they read before the optimizer's first write, each"; "D16-s3-02: after unload the supply switch, the frequency, the valve and the circulation pump read what they read before the optimizer's first write, e" (+2 more).
- M17 `pump_arbiter.py`: arbiter row not armed: KILLED by "D16-s3-01: Off returns the pump's mode select to the baseline row on the Tuya arm (the arbiter had written the hot-water duty)"; "D16-s3-01: Off returns the tank set-point to the configured 50 on the Modbus arm (space-only steps had gated it)" (+2 more).
- M18 `pump_arbiter.py`: row written while the switch reads off: KILLED by "D16-s3-01: Off returns the pump's mode select to the baseline row on the Tuya arm (the arbiter had written the hot-water duty)"; "D16-s3-01: Off returns the tank set-point to the configured 50 on the Modbus arm (space-only steps had gated it)" (+2 more).
- M19 `pump_arbiter.py`: unload defers the row like Off: KILLED by "D16-s3-03: unloaded while the integration holds the pump's disinfection (the arbiter raised the tank to the cycle target 60), the tank set-point reads"; "verdict item 8: a pass that forgets the arbiter's record between two slot writes of the row's restore does not stop it: the restore completes, the row" (+1 more).
- M20 `pump_arbiter.py`: row release keeps the arbiter record: KILLED by "verdict item 8: a pass that forgets the arbiter's record between two slot writes of the row's restore does not stop it: the restore completes, the row"; "verdict item 8 null control: without the interleaving the end state is the same".
- M21 `pump_arbiter.py`: supply not restored on a stale plan: KILLED by "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl".
- M22 `coordinator.py`: frequency written on a stale plan: KILLED by "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl"; "D16-s1-04: a second stale cycle writes nothing to the four restored entities, and the restore is recorded as plan_stale".
- M23 `coordinator.py`: cycle entry not called: KILLED by "D16-s3-01: Off returns the pump's mode select to the baseline row on the Tuya arm (the arbiter had written the hot-water duty)"; "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl" (+2 more).
- M24 `coordinator.py`: valve restore keeps the record: KILLED by "design invariant 2, valve: after Off then On the same planned target 20 is sent again, and the record of the last write is empty right after the resto".
- M25 `coordinator.py`: frequency restore keeps the record: KILLED by "design invariant 2, frequency: after Off then On the same target is sent again, and the watchdog's commanded value is None right after the restore".
- M26 `coordinator.py`: valve written on a stale plan: KILLED by "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl"; "D16-s1-04: a second stale cycle writes nothing to the four restored entities, and the restore is recorded as plan_stale" (+1 more).
- M27 `legionella.py`: interval notice always raised: KILLED by "D7-s1-05 null control: the same call with no day count clears the issue".
- M28 `__init__.py`: no second unload pass: KILLED by "design note 3 (later key): an off write of the supply switch landing during a later key's unload restore is handed back by the unload's second restore".
- M30 `circulation.py`: circulation: off sent though the arm was refused: KILLED by "a circulation pump's off command whose restore cannot be armed is not sent and not recorded".
- M31 `circulation.py`: circulation: restorer's neutral is not on: KILLED by "the two circulation pumps and the supply switch are restored to on (neutral 1.0) on the entity the config names, and an entity not configured has no r".
- M32 `coordinator.py`: space pump driven on a stale plan: KILLED by "on a stale plan in a plan mode the space circulation pump is not driven: the let-go predicate holds it".
- M29 `coordinator.py`: frequency/valve not restored on a stale plan: KILLED by "D16-s1-04: a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycl".

M05, M13, M14 and M28 survived the section's first cut and each got a check with its null control before this run. M30, M31 and M32 are the three survivors `prepr.sh`'s diff-mutant draw found among its first 40 (`MUTANT_CMD` the same section, `MUTANT_IN_PLACE=1`); each got a check too.

## Null control

- The unmodified tree (a worktree of `origin/main` 8751943e17ef holding this head's `tests/features.py`, the section run by the same `features_block.py` command): `52 of 65 FEATURES BLOCK FAILED`, no crash; the head passes all 65. The 13 that pass at the base are checks the base must pass: the three D16-s3-02 nulls, the D16-s3-01 null, the D16-s3-03 no-hold null, the D16-s1-04 precondition, its null and its two "writes nothing" checks (the base writes nothing on a stale plan at all), the two D16-s3-04 nulls, the D1-s2-04 serial null and the serial null of the two-restores check.
- `m6_restore.py` null arms (commands equal to each baseline), base / head: `null_unrestored_off` 0 / 0; `null_unrestored_unload` 0 / 0; `null_unrestored_remove` 0 / 0; `null_unrestored_duty_change` 0 / 0; `null_unrestored_off_modbus` 0 / 0; `null_unrestored_off_disinfecting` 0 / 0; `null_unrestored_unload_disinfecting` 0 / 0; `null_unrestored_remove_disinfecting` 0 / 0; `null_unrestored_duty_change_disinfecting` 0 / 0.
- `m5_holds.py` without the failure, base / head: `null_restore_without_failure_later_writes` and `null_space_final` in the Figures line.
- `off_restore_race.py --serial`: 0 at both ends.
- Goldens: no solver path changes; `git diff 8751943e17ef4d3ec699e7859ae829b4528d8ce7...HEAD -- tests/golden` prints nothing and both claim files are byte-identical.

## Figures

Harness export: `git archive 0a7ea717c6d99fd179af08f31484390d0080cb01 dev/audit/rounds/round11` into `$EXPORT`, run from the checkout root; base is `origin/main` 8751943e17ef, head is the head above. sha1: m6_restore d4618082e2014163c7dc0fcbebbcb147d1253932, m5_holds 4ac4d570aa4ea46d910e03dc09e84740dcc86b2f, cells 407d2f87c6d837b383f29044f9b972a1fb3bdb61, off_restore_race bb009fa9134355b419863b093c2c53726a509ae2 (with d1s2_lib 0b462292329e0ca27a5f855f0e9a800220488c7b), m7_prototypes a652f3160d8060557990a905b401f96057132ef1. Every pair below is base / head.

- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D16/s3/m6_restore.py`: `unrestored_off` 5 / 0; `unrestored_unload` 4 / 0; `unrestored_remove` 4 / 0; `unrestored_duty_change` 7 / 7; `unrestored_off_modbus` 4 / 0; `unrestored_off_disinfecting` 6 / 0; `unrestored_unload_disinfecting` 5 / 0; `unrestored_remove_disinfecting` 5 / 0; `unrestored_duty_change_disinfecting` 8 / 7. The two `duty_change` arms are the finder's own expectation under `--perturb all` (the observe-mode reload writes again). `restored_more_than_once_off` 0 / 0; `restored_more_than_once_unload` 0 / 0; `restored_more_than_once_remove` 0 / 0; `restored_more_than_once_duty_change` 0 / 0; `restored_more_than_once_off_modbus` 0 / 0; `restored_more_than_once_off_disinfecting` 0 / 0; `restored_more_than_once_unload_disinfecting` 0 / 0; `restored_more_than_once_remove_disinfecting` 0 / 0; `restored_more_than_once_duty_change_disinfecting` 0 / 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D16/s3/m5_holds.py`: `writes_again_off_restore_failed_while_off` 0 / 1; `space_setpoint_final_while_off` 25 / 45; `writes_again_off_restore_neutral_failed_while_off` 0 / 1; `heat_curve_offset_final_while_off` 3 / 0; `person_toggle_restores` 1 / 0; `person_toggle_restores_neutral` 1 / 0; `null_restore_without_failure_later_writes` 0 / 0; `null_space_final` 45 / 45. Other lines that moved: none.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D16/s1/cells.py --no-gates`: `baseline_switch_off` 5 / 0; `clause_switch` 5 / 0; `clause_stale` 0 / 0; `failing_rows` 55 / 50; `fail_cells` 418 / 380; `arbiter_value_rows_failing` 4 / 4; `clause_grid` 50 / 50; `cold_tank_charge` 2 / 2; `boost_indoor_between` 2 / 2; `unavailable_recorded` 5 / 5; `cells` 532 / 532; `examined` 532 / 532; `unattributed_calls` 0 / 0. Head null rows: NULL fork-flow baseline-on FAIL [stale] plan-driven writes after the plan went stale: [('number.hp_freq', 40)]; NULL gchv-flow baseline-on FAIL [stale] plan-driven writes after the plan went stale: [('number.hp_freq', 40)]; NULL fork-indoor baseline-on FAIL [stale] plan-driven writes after the plan went stale: [('number.hp_freq', 40)]; NULL gchv-indoor baseline-on FAIL [stale] plan-driven writes after the plan went stale: [('number.hp_freq', 40)]; NULL fork-flow-pc baseline-on FAIL [stale] plan-driven writes after the plan went stale: [('number.hp_freq', 40)]. The `baseline-on` arm fails at the head on one write, the frequency's restore to its pre-write reading 40: the harness keys `[stale]` on any frequency write after the plan went stale and cannot tell a restore from a plan-driven write. Companion at the head, applying the rule the row states to the same drive: the section's checks "a stale plan returns the supply switch to on and the frequency and valve to their pre-write readings 70 and 22, one write each in that cycle" and "a third stale cycle writes nothing at all"; at the base the first fails and M22, M26 and M29 above are its perturbations.
- `PYTHONPATH=tests/hastub python3 $COPY/off_restore_race.py`, `$COPY` being `$EXPORT/dev/audit/rounds/round11/D1/s2` copied to the same path under the checkout (its library requires a repository root above it) and removed after: `consequences` 2 / 0; `--serial` 0 / 0.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only notice`: at the base the arm reads `duplication_copies 18 -> 17`, dS +0.6964 (its header's figure); at the head it stops on `anchor occurs 0 times`, the two `set_issue` bodies it replaces being gone, and the score line below carries the same term.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: Architecture score: dS +2.9709 IMPROVES ; shared_inplace_writes 3 -> 2 +2.2590 ; duplication_copies 18 -> 17 +0.6964 ; coord_footprint 2507 -> 2504 +0.0017 ; coordinator_multiassigned_attrs 104 -> 103 +0.0138. Against the merge base, not `origin/main`'s tip: main has since lowered `layer_violations` from 13 to 6 on its own, which a two-dot reading shows as this branch raising it. `coord_footprint` falls by three statements, not ADR-004's six: the cycle entry, the two let-go gates and the owner table's registration are statements the prototype did not have.
- Control for the first departure: `from . import off_restore` added to `freq_control.py` and read by `FrequencyWatchdog.command`, `python3 tools/audit/archscore/score.py --diff origin/main` taken while `origin/main` was the merge base: `dS +0.7783 WORSENS (inadmissible: import_cycle_modules 0->3; layer_violations 13->15)`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: no row breached; `class_excess_loc`, `coordinator_attrs`, `coordinator_multiassigned_attrs` and `max_class_loc` fell and are re-recorded (the commit message carries it). The first cut breached `duplication_copies`, `functions_cc_over_15`, `name_kept_members` and `coordinator_private_reach`; paid by one restore tail (`off_restore._land`), `async_arm` split from `_arm_restorer`, and the entry-keyed owner table in place of a read of the coordinator's private attributes.
- Write sites, `python3 tools/audit/enumerate.py d16-writes | grep '^write'` at the head, each with its disposition:
  - `write custom_components/heatpump_optimizer/circulation.py:43 _send domain=homeassistant`
  - `write custom_components/heatpump_optimizer/coordinator.py:10909 HeatPumpOptimizerCoordinator._command_frequency domain=number`
  - `write custom_components/heatpump_optimizer/coordinator.py:3482 _disinfection_switch domain=?`
  - `write custom_components/heatpump_optimizer/heat_curve.py:234 publish_ecl110_topics domain=mqtt`
  - `write custom_components/heatpump_optimizer/heat_curve.py:252 publish_ecl110_topics domain=mqtt`
  - `write custom_components/heatpump_optimizer/inputs.py:729 write_setpoint domain=?`
  - `write custom_components/heatpump_optimizer/pump_arbiter.py:1624 _write domain=?`
  - `write custom_components/heatpump_optimizer/pump_arbiter.py:1984 _send_supply domain=?`
  - `circulation.py _send`, `coordinator.py _command_frequency`, `pump_arbiter.py _send_supply`: closed in this diff.
  - `pump_arbiter.py _write`: mode, tank set-point and silent closed in this diff (`ROW`); the space set-point already registered; the GCHV night registers are the forward-carry below.
  - `inputs.py write_setpoint`: the sender under the valve (closed in this diff), the space set-point and the heat-curve entity (already registered).
  - `heat_curve.py publish_ecl110_topics` (two): already registered.
  - `coordinator.py _disinfection_switch`: `disinfection.py`'s own record and `release_blind`, already guarded; `m6_restore.py`'s three `*_disinfecting` arms write `switch.dis` and read it restored at both ends.
- Lazy-load flags, `grep -nE '\.loaded = True|_loaded = True' custom_components/heatpump_optimizer/*.py`: four. `off_restore.py` closed in this diff; `pump_arbiter.py` already guarded by `held.lock`; `coordinator.py` `_snapshots_loaded` and `frontend.py` are other seams' records, unmeasured here.
- Let-go sites, `grep -n '_plan_is_stale()\|_plan_let_go(' custom_components/heatpump_optimizer/coordinator.py`: the predicate `_plan_let_go` and its four readers (`_space_pump_to_drive`, `_apply_action`, `_command_frequency`, `_command_valve_target`), closed in this diff; three publications of the flag (`handover`, `arbiter_inputs`, the payload), no gate.

<!-- figure-block: scope-line mb=8751943e17ef4d3ec699e7859ae829b4528d8ce7 head=5dd27cfd07c5a5c655d1429be3fac51200d089b7 -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->

- Every script whose recorded closure holds `coordinator.py` was re-recorded with `tests/derive_closures.sh --single` on this branch, which is also that script's run; each recording's `done ... (exit 0)` line is the pass. Rule for the set: the keys of `tests/closures.json`'s `closures` whose list holds `custom_components/heatpump_optimizer/coordinator.py`, all of which now hold `circulation.py`. `python3 tools/pr/ci_predict.py` at the head: no closures, fast or ledger red; 79 added unpinned sites (below).

## Unpinned sites

- `custom_components/heatpump_optimizer/circulation.py:39 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/circulation.py:57 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/circulation.py:60 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/circulation.py:60 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/circulation.py:78 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:767 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:778 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:783 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:790 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:3521 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:3534 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:3534 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:4556 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:7769 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:7801 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:7833 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:7835 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:10890 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/freq_control.py:319 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/freq_control.py:319 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/freq_control.py:319 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/freq_control.py:321 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/freq_control.py:325 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:237 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:237 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:237 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:239 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:242 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/mixing_valve.py:244 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:157 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:160 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:163 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:166 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:209 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:209 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:212 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:214 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:216 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:219 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:227 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:229 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:230 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:233 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:233 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:235 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:238 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:247 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:266 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:286 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:286 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:290 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:309 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:309 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:318 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:330 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:332 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:332 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:342 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:345 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:345 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:358 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/off_restore.py:360 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1616 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1629 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1633 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1721 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1723 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1759 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1760 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1998 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2181 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2194 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2197 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2197 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2199 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2204 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2206 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2311 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:2318 GUARD_OFF`: pinned by `mutation-autofix`

## Red checks

- `mutation` at 5dd27cfd07c5: red by construction on the 79 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. Cheaper detector: `tools/pr/ci_predict.py` lists the sites before the push in seconds, and the pinning lane is CI's (`ci-autofix.md`), so none is built.

## Forward-carry

- `tests/features.py`: design invariant 2, for the group that reads the held record after a release. After a restore lands the owner's record of the entity is empty (`ValveTarget.commanded_c`, `FrequencyWatchdog.commanded`, `circulation.commanded(entry)`, the arbiter's non-space slots), so the first write after On is sent, not deduplicated. Control: the section's "design invariant 2" checks, whose nulls (no Off between two cycles) send no second write; M12, M20, M24 and M25 are the perturbations. Re-measure with the section at your own merge base. Carry: dismissed: owed to R11-SEAM-actuation-writes (the group that reads the held record after a release; the orchestrator writes it onto that group's brief)
- `custom_components/heatpump_optimizer/pump_arbiter.py`: the GCHV night-schedule registers (`_write_night_schedule`) arm `ROW` but are not written back, because the row holds no value for them and nothing captures their reading before the first write. D16-s3-01's property names them; no harness at 0a7ea717c6d9 measures them. Carry: dismissed: owed to R11-SEAM-actuation-writes (the arbiter's write path owns the night registers; the orchestrator writes it onto that group's brief)
- `custom_components/heatpump_optimizer/pump_arbiter.py`: shared with R11-SEAM-kernel-step with no edge; the second of the two to merge re-runs the finder's restore harness, the first command under Figures (design note section 6). Carry: dismissed: owed to R11-SEAM-kernel-step (the second of the two to merge re-runs the harness; the orchestrator writes it onto that group's brief)

## Friction

design-note-section-2: contradiction: the approved note places the frequency and valve owners' registration in two pure modules, which `fixer.md` step 17 and the `layer_violations` gate refuse; the control is under Figures. Carry: dismissed: recorded above as pending owner confirmation
fixer-step-3: cost: `off_restore_race.py` imports a library that requires a repository root above it, so it cannot run from `$EXPORT`; the export's directory was copied under the checkout and removed. Carry: dismissed: one harness, stated with its command
finding-propagation: contradiction: the dispatch brief lists `R11-SEAM-actuation-writes` and `R11-SEAM-kernel-step` as valid carry targets, `carry_audit.py`'s group token admits upper case only and reads them as no marker (`UNROUTED`), and upper-cased they are refused as no group of `origin/main`'s roster or of `origin/handoff/audit-r10-roster`: no roster this checkout can read holds a round-11 group, so the three items under Forward-carry could not pass the audit from this seat; the orchestrator ruled them written as dismissed items owed to the named groups, which it writes onto those groups' briefs. Carry: dismissed: reported to the relay with the audit's output
ci-autofix: cost: a new production module leaves every script that loads the coordinator UNDER-SCOPED and `body_push.sh` refuses a closures red, so 22 closures were re-recorded before the handoff; `tests/card.mjs` records only after `tests/plan_view.py`, which the predictor's one-script-at-a-time line does not say. Carry: dismissed: repaired in this diff
