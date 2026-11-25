Closes #3856. Builds the approved design `design/R11-OWNER-FAULT-HOLD` at `57d5d278f0c5` (verdict `design-verdict/R11-OWNER-FAULT-HOLD` `e9598ceb7e`, `Design review: approve`): while the pump's fault alarm has been on for 10 minutes, the integration stops commanding the pump.

## Summary

`fault_hold.py` (new, a leaf over `const`, `entry_config`, `inputs` and `issues`) owns a per-entry latch and the `pump_fault_hold` repair. It reads the fault slot with `inputs.UNBOUNDED`, so a push-only fault still reads at any age. The latch starts at the alarm's `last_changed`, bounded to now. A legible off resets it. Unavailable, unknown or not-boolean readings neither start a hold nor end one. Optimizer Off and the `fault_hold` option set to off clear it. An unloaded entry (`released`) answers False and raises nothing. The hold starts at `FAULT_HOLD_AFTER` (10 min).

While the latch holds:

- `pump_arbiter.apply` consults once per pass, before the duty-off return, so the latch moves for every install. In control, `_arbitrate` returns before `_adopt`, `hold`, `_command` and the night schedule (`_fault_stands`). It drops `space_before` and the pending retries and clears `pump_write_ignored`.
- `_lead_mode` writes no mode.
- An unload writes no baseline row: `off_restore`'s release of the row (`pump_arbiter._release_row`, main's since #3812) answers False for `reason == "unload"` while `fault_hold.unload_holds` reads true, so the row stays owed. `async_unload_entry` restores twice, before and after `async_shutdown`; `release` between them drops the latch and the repair, and `fault_hold.release` marks an entry that was holding, so the second restore leaves the row owed too. The entry's next consult (a set-up afresh) clears the mark. The space set-point's own restore still runs. Off ends the hold, so entering Off hands the row back at once.
- A stale plan's hand-back (`off_restore.async_cycle`'s stale half, #3812: supply on, frequency, valve, the row) is not run while the latch holds; it runs once the alarm clears.
- The cycle's and the step tick's switch gate (`fault_hold.gate`, after `supply_hold.hold_supply` in `_write_supply`) turns an OFF into "leave" and marks `supply_held`, so the step tick lands it after the clear. An ON passes.
- `early_cutoff.on_room_event` does not cut.
- `_command_frequency` returns.
- `heat_curve.publish`, the one sink of every displace (cycle, peak-guard engage and release), sends nothing.

The step ledger lives in `duty_ledger.py` (main's module since #3812; this group adds `observe`, `RUN_SETTLE` and the `faulted` mark there). A step in which any pass held is `device-fault`, decided before every other verdict. The onset step keeps its own verdict because a row closes when its step ends. The option `fault_hold` (default on) sits beside the Fault alarm entity. Docs: `docs/configuration.md` (two rows, the ledger line and a "A pump that reports a fault" section, which now says what a stale plan and an unload hand back under the hold), `docs/architecture.md` (module map and the HA boundary counts), the repair in `README.md`.

The design's carries, each built here:

- **skip-log**: the gate logs its own line; main's cooling gate (#3864, `supply_hold.supply_write`) prints its message only for a value it leaves, and it passed the OFF the fault gate holds.
- **multi-entry**: one domain-wide id, cleared only when no entry on the same `hass` holds.
- **hand-reset**: the repair text says to turn Optimizer active off first.
- **entry-released / publish-released**: `holding(released=...)`, with `publish` given `released=self._entry_released` on the coordinator's existing argument line.
- **supply-after-clear**: the held mark.
- **ignored-repair**: cleared in `_fault_stands`.
- **unload-row**: built, now in `_release_row` (see `## Merge resolution`).
- **onset-step**: docs ledger line.
- **cc-headroom**: `functions_cc_over_15` unchanged; the fault folds into `_arbitrate`'s existing return condition.
- **bundle-latch-count**: `dev/audit/harnesses/r11_owner_fault_latch.py bundle --timeline T`.
- **ledger-constants**: `TANK_RISE_C` and `RUN_SETTLE` live in `duty_ledger.py`; `duty_ledger` imports only `plan_step`.
- **publish-config**: `holding` builds its `InputReader` from `dict(config)`.
- **duty-off-latch-age**: `gate` and the cut-off call `consult`, which reads, so there is no lag.
- **reported-displace**: under the hold the coordinator still records the computed displace (`_ecl110_current_displace`). `docs/configuration.md` says the diagnostics report the computed displace, which was not sent, and shows the latch under `fault_hold`.
- **fallback-private-reach**: not needed; the coordinator class did not grow.
- **seam-actuation**: SEAM-ACTUATION-RELEASE merged first (#3812); this branch merges it, and `## Merge resolution` states each file.

Departures, raised: FROST-HOLD (`e91a4e30`), which the design orders ahead of this group, is not on main. So the gate chain is `hold_supply → fault_hold.gate`, and the cut-off consults `fault_hold` directly, with no frost hook to wrap. The frost composition is carried to FROST-HOLD below. The latch reads the alarm's `last_changed` directly. That is registered as a `state_age` disposition (`fault_hold.py::holding`) in `tests/entities.py`, for the same reason `supply_hold.switch_age` reads it: the value's age, not the entity's last report. Two behaviours are new with the merge and not in design `57d5d278`, which predates #3812's restore owner: the stale hand-back held under the latch, and Off's row handed back at the mode change.

## Head

`71af14b6d88998d59cef37e629dfde9ff5d05622`, measured against its merge base `d3d66c40408e76351ffc528686353cadf815a05c` (`origin/main` at the merge, #3864 merged). `git merge-tree --write-tree origin/main HEAD` exits 0.

Review round 2 (`review/3872` `66d0d4b2`, `verdict/3872` `9b11d200`) blocked `91cfc89fdade5cb556ad5e7fd3353ac4c3eae07b` as `unload-row-written`: the second unload restore, after `pump_arbiter.release` drops the latch, wrote the baseline row into the faulted pump. `fdde1320d3` answers it (`## Mutation proof`). The orchestrator's scope add (inbox `r11-merge-fault-hold`, command 1) put that fix in this merge pass.

The commits since the reviewed head, `git log --first-parent 91cfc89fdade..71af14b6d8`:

- `da1f90c785` Merge origin/main `d3d66c4040` into R11-OWNER-FAULT-HOLD: resolve against R11-OWNER-COOLING-GUARD (#3864)
- `fdde1320d3` R11-OWNER-FAULT-HOLD: the unload's second restore leaves the row owed under a held fault
- `0bbd4dd92c` R11-OWNER-FAULT-HOLD: `_release_row`'s docstring rewrapped one line shorter (`module_excess_loc` back to the merged tree's measure)
- `d8961f7a99` R11-OWNER-FAULT-HOLD: the harness's release-clears mutant re-texted around the unload mark
- `71af14b6d8` R11-OWNER-FAULT-HOLD: `tests/deployment_shape.py`'s #1218 note carries the census `tests/entities.py` derives

The reviewer's delta: `git diff 91cfc89fdade 71af14b6d8`; the code delta without main's: `git diff da1f90c785 71af14b6d8`. The earlier commits, rounds and merges are in this PR's history; the round-1 answer is `ce9619a4f4`.

## Merge resolution

Fifth merge, `da1f90c785` (`origin/main` `d3d66c4040`, #3864 R11-OWNER-COOLING-GUARD). `git merge-tree --write-tree` named six content conflicts (`README.md`, `coordinator.py`, `strings.json`, `translations/en.json`, `sv.json`, `de.json`), not four; `tests/structure_budgets.json` went through the ledger driver. Each, both sides read back in the merged artifact:

- `coordinator.py` `_write_supply` (semantic): #3864 moved the switch gate to `supply_hold.supply_write(held, inputs, on, signals)`, which reads cooling and raises `pump_mode_cooling`; this group's `fault_hold.gate` stays outermost around main's whole expression, so a cooling ON is left by main's gate and a fault-held OFF is left by this group's. Main dropped the coordinator's cooling debug branch, which `fault_hold.gate`'s docstring named; the docstring now names `supply_write`'s message.
- `strings.json`, `translations/en.json`, `sv.json`, `de.json`: both issues kept, `pump_fault_hold` then `pump_mode_cooling`; each file parses as JSON; `tests/entities.py` at this head passes "en.json has exactly strings.json's keys", the same for `sv.json` and `de.json`, and "en.json equals strings.json leaf for leaf".
- `README.md`: both notice rows kept, the fault row before the cooling row; each is true of the merged gate order above.
- `tests/structure_budgets.json`: `tests/structure.py` on the merged tree measures `module_excess_loc` 21728, the ledger driver's sum (21774 base; main -11, this branch -35); `class_excess_loc` and `max_class_loc` take main's lowered values. Recorded in the merge commit with its reason; no metric rose.
- `tests/deployment_shape.py`'s #1218 note: the branch head `91cfc89fdade` already derived 184 of 561 pairs at >= 0.80 against a note of 182 (`tests/entities.py` red there, found by the scoped gate here); the two pairs are `manual_plan.py` with `env_drift.py` and with `golden.py`, each closure gaining `fault_hold.py` alone. Derived by `tests/entities.py`'s `_d308_pairs` on the merged `tests/closures.json`; main derives 182.`git merge origin/main` (`af4d89f763`) into `ce9619a4f4` conflicted in 8 files and 4 mutation-ledger rows, all from #3812 (R11-SEAM-actuation-release), which moved the step verdicts into its own `duty_ledger.py` and the off/unload baseline row into `off_restore` (`_release_row`, `ROW`). Each file, both sides read back in the merged artifact:

- `custom_components/heatpump_optimizer/duty_ledger.py` (add/add): main's module is the base (its `_not_startable`, `_missed` and `step_verdict` are identical to ours but for the fault branch and the local name). This group's on top: `observe()` (the row fold `pump_arbiter._observe` delegates to), `RUN_SETTLE` (main kept `RUN_SETTLE = _TICK` in `pump_arbiter.py`, both one minute; it now lives here only), the `faulted` row key and `device-fault` first in `step_verdict`. The docstring opens with main's first line.
- `custom_components/heatpump_optimizer/pump_arbiter.py` (5 hunks): module docstring is main's ledger paragraph plus this group's fault paragraph; imports are main's plus `fault_hold`; `_observe` is this group's (delegating to `duty_ledger.observe` with `faulted`); `release()` is main's (writes nothing, persists) plus `fault_hold.release(coord.hass, coord.entry)`. This group's old in-`release` baseline write is gone with main's: the unload's row is `_release_row`'s, which gains `(reason == "unload" and fault_hold.held(coord.entry))` in its first guard. Main's `_arbitrate` Off comment is taken as is.
- `custom_components/heatpump_optimizer/coordinator.py` (2 hunks): the cycle keeps main's `stale = _plan_let_go(self)` and `off_restore.async_cycle(...)`, with this group's `entry=self.entry` on the cut-off arm; the stale half is passed as `stale and not fault_hold.held(self.entry)` (Off's half is not touched: Off's pass has already cleared the latch). `_command_frequency`'s guard is the union: `... or _plan_let_go(self) or fault_hold.held(self.entry)`.
- `docs/architecture.md` (3 hunks): main's map row for `duty_ledger.py` plus this group's `fault_hold.py` row; counts re-derived: 102 modules, 37 importing `homeassistant` at module level (main's 36 plus `fault_hold`).
- `tests/deployment_shape.py`: 121 package files (main's 120 plus `fault_hold.py`), history line extended.
- `dev/audit/rounds/round4/D6/claims.py`: main's, with the three expectation lines re-derived (102, 102, 37) and their history; `claims.json` and `claims.md` are main's.
- `tests/mutation_ledger/killed_by/duty_ledger.py/` rows `@module.CONST.647a1d0a`, `_missed.RETURN_DEL.0733b5f7`, `step_verdict.GUARD_OFF.00bf3d75` and `step_verdict.GUARD_OFF.d746330a`: main's. `ci_predict` then named three pins stale (`_command_frequency` GUARD_OFF `0bf30dbd`, `step_verdict` GUARD_OFF `d746330a`, `_release_row` GUARD_OFF `88e2f26e`: each line gained the fault clause); deleted by hand in `f8b1b7b9ea`, as `ci_predict` prescribes, for mutation-autofix to pin afresh.
- `tests/structure_budgets.json`: the ledger driver summed both sides' deltas to `module_excess_loc` 21690, counting the ledger move both branches made twice; the merge commit takes main's (21775), and `abc36b3f09` / `ed1b1ae98e` record the merged tree's 21740.
- `tests/closures.json`: merged as sets by the ledger driver, no conflict.
- `tests/features.py` (no textual conflict, three semantic repairs): section 12 drives main's unload and Off paths (`_pa_unload`, `_pa_enter_off`: `off_restore` then `release`) instead of `release` alone, which no longer writes; the early cut-off fixture passes `entry=` into `ArbiterInputs` (main's `switch_supply` now takes the entry); a new 12b drives a stale-plan cycle through the real coordinator (`_r11ar_*` fixtures of #3812).

Second merge, `e2e30e43ad` (`origin/main` `5594a34a49`, through #3825, #3880, #3886): no textual conflict. `origin/main` changed no file under `custom_components/` since `af4d89f763`. Two semantic repairs: the D6 claims register (`claims.json`, `claims.md`), which the first merge took from main, is now what `claims.py` writes on the merged tree (C32-C35: 102, 102, 37, `fault_hold.py` named); and #3825's new `tests/cycle_lane.py` reads `coordinator.py`, which imports `fault_hold` here, so its closure is re-recorded with `--single`, adding `fault_hold.py` alone.

Third merge, `9924e94422` (`origin/main` `f52e700df1`): conflicts in the count lines only, each the union of both additions. `docs/architecture.md`: 103 modules, 37 importing `homeassistant` at module level (#3738's `solve_gate.py` imports none). `tests/deployment_shape.py`: 122 package files, history extended (121 until `solve_gate.py`, 120 until `fault_hold.py`). `dev/audit/rounds/round4/D6/claims.py`: 103 with both history clauses; `claims.json` and `claims.md` regenerated by `claims.py` on the merged tree. Main's production changes in this range (#3738 `solve_gate.py`, `coordinator.py`; #3875 `store.py`, `boost.py`, `snapshots.py`) merged without conflict with this group's `coordinator.py` lines.

Fourth merge, `07223afa29` (`origin/main` `6a58ba5cb3`, through #3888 and the duty-switch, duty-legs and optimizer changes): no textual conflict outside the two ledger files, which the `ledgermerge` driver merged (`tests/closures.json` as sets; `tests/structure_budgets.json` `module_excess_loc` re-summed, `tests/structure.py` passes on the merged tree). Pushed because `body_push`'s predictor refused `9924e94422`: `governance / wave-script AGREEMENT UNMERGED`, since GitHub's merge has no ledger driver.

## Mutation proof

`python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`, at `d8961f7a99` (tree identical to `0c8bbfaa77`, where it ran; production unchanged since): 41 hand mutants, each deleting or weakening one production predicate in a `git archive` copy, driving the fault-hold block of `tests/features.py` and `tests/block_duty.py`. Unmutated baseline: `BASELINE 0 failing`. `RESULT mutants=41`, `RESULT survived=0`.

Round 2's block, failing first: `_pa_unload` (`tests/features.py`) now runs restore, `release`, restore, as `async_unload_entry` does. At `da1f90c785` (the merge, no fix) the fault-hold block reads `1 of 59 FEATURES BLOCK FAILED`, the failure `unload under the hold writes no baseline row, and drops the latch [([('select', 'select.pump_mode', 'Heating + DHW')], False)]`; with the fix, `ALL 61 FEATURES BLOCK PASSED`. A new check pins the mark's lifetime: after an unload under the hold, a consult (the entry set up afresh) and a second unload write the owed row; its null control, the same sequence with no consult, writes none.

Three new mutants, each killed: `unload mark set` (`fault_hold.release` marks nothing; 2 failing), `unload mark read` (`unload_holds` reads the latch only; 2 failing), `unload mark cleared` (the consult keeps the mark; 1 failing). `release row skip` and `Off row held too` re-texted to `unload_holds`; `release clears` re-texted around the mark (it read `STALE` at `fdde1320d3`, the text it mutated having gained the mark's line). Each still killed.

Round 1's four call-site mutants (`consult released`, `consult Off`, `publish mode_off`, `diagnostics since`) are in the 41 and killed.

## Null control

Every behaviour check is paired with today's behaviour on the same fixture: the alarm on for 9 minutes, reading off, or `fault_hold` off writes what the merge base writes. Section 12: unload with no fault writes the row; Off with no fault writes the same row as Off under the hold. Section 12b: the same stale cycle with no fault writes the supply switch back. The synthetic replay's null is `--opt-out`: `RESULT latched_actuating=260` against `0` with the hold; `RESULT repairs=0` against `1`; `RESULT short_held=0` both ways (measured at `5eb7083aaa`; the latch module is unchanged since).

Round 2: the two-pass unload check fails at `da1f90c785` (above), so the head separates; the mark-lifetime check's null control is the sequence with no consult between the unloads, which leaves the row owed.

## Figures

At `71af14b6d8` unless named:

- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=d3d66c40408e ./tests/run.sh` (`PYTHON=/opt/hpo/venv-ci/bin/python`, `PYTHONPATH=tests/hastub`), run on the working tree at `fdde1320d3` plus `0bbd4dd92c`'s docstring: `MODE: SCOPED -- 31 script(s) run, 3 scoped out`; `1 TEST SCRIPT(S) FAILED`, `tests/entities.py`, on the #1218 note alone (`## Merge resolution`). `tests/features.py` there: `ALL 6231 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (`timeout 2400`) at this head: `ALL 2763 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, every metric at or below the merged budget. At `fdde1320d3` it read `module_excess_loc 21729 > 21728 (+1)`; `0bbd4dd92c` paid it.
- `python3 tests/comment_ratchet.py`: `comment_ratchet: OK` (at `fd65e87415`, tree of `0bbd4dd92c`).
- The fault-hold block (`features_block.py`, markers as before): `ALL 61 FEATURES BLOCK PASSED` at `fdde1320d3`; `1 of 59 FEATURES BLOCK FAILED` at `da1f90c785`.
- `python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD`: `RESULT mutants=41`, `RESULT survived=0`.
- `python3 tools/pr/ci_predict.py`: `CI PREDICT: no closures, fast, governance or instrument red predicted against d3d66c40408e`; `CI PREDICT: 42 unpinned site(s) the diff adds` (each under `## Unpinned sites`).
- Not re-run in this pass: `tests/derive_closures.sh` (no closures red predicted), prepr's diff-mutant step, `tools/audit/archscore` (below).

## Architecture score

`python3 tools/audit/archscore/score.py --diff af4d89f76325 HEAD` at `f8b1b7b9ea`: `Architecture score: dS +0.0006 IMPROVES`, `coord_footprint` 2521 → 2520. No gate metric rises.

Not re-measured after the fifth merge and the unload fix: the fix adds one module-level set and one function to `fault_hold.py` and changes one call in `pump_arbiter.py`; `tests/structure.py` reads every gate metric flat.

## Red checks

- `tests / fast (3.14)` at `d6a54399a63b`: `tests/env_drift.py --all` ended `1 UNCLAIMED DRIFT(S)`, `config_flow`, three leaves `present on one side only` (`_seed.fault_hold`, `_seeded.entities_pump.fault_hold`, `entities_pump.fault_hold`): the new option was never re-recorded into `tests/golden/config_flow.json`. Answered in `8d8b30aabf`: `golden.py --record --only config_flow` (13 lines added, none removed) and one `config_flow` claim line in `tests/golden/claimed_drift.txt` stating the direction (ADDED). `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all af4d89f76325` at this head: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE`, config_flow `CLAIMED` with exactly those three leaves. The cheaper detector exists: `PYTHONPATH=tests/hastub python3 tests/golden.py --only config_flow`, seconds, reports the same DIFF; the fixer's lanes ran `tests/features.py` and the block but not `tests/golden.py`, and a scoped prepr (`PREPR_SKIP_CODE=1`) runs neither. Its standing cost is one golden run per head that adds an option key; the countermeasure is that run, recorded here, before every handoff of this branch.
- `tests / mutation` and `tests / mutation-autofix` at `d6a54399a63b`: red by construction on the sites under `## Unpinned sites`; mutation-autofix pins the killed sites after the push.
- `pr-contract` and `gate` at `d6a54399a63b`: the body there did not name the two reds above; `gate` aggregates the required checks. No CI has run at this head yet.
- Local `prepr.sh` step `self-test` (not a CI check; CI's `governance` job runs the self-test): `567 passed, 4 failed` on this host, the same 4 rows on plain `origin/main` `6a58ba5cb3`: "an ancestry no commit of which carries any check run skips, never refuses (got 0, wanted 3)", "and the skip line names the boundary (got 0, wanted 1)", "reds_arm refuses a body that leaves an ancestry red unanswered (P351) (got 0, wanted 1)", "and the refusal is the red gate's own sentence (got 0, wanted 1)". A host fault, not this head's: this update ran under a local overlay that skips that one step (logged as a workaround).
- `tests/entities.py` at `91cfc89fdade` (local scoped gate, not a CI run): the #1218 note's "182 of the 561" against the 184 the branch's closures derive. Answered at this head (`## Merge resolution`). The cheaper detector is that script, which the scoped gate selects for any diff touching `tests/closures.json`; the earlier merges re-recorded closures and did not run it. Its standing cost is one `tests/entities.py` run (about 11 minutes here) per closure re-record before a handoff.

## Unpinned sites

The sites `tools/pr/ci_predict.py` lists at this head. Every fault-hold predicate among them is killed by `r11_owner_fault_hold_mutants.py` above.

- custom_components/heatpump_optimizer/coordinator.py:7753 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10796 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:62 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:95 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_ledger.py:97 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:315 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:79 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:83 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:85 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:88 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:88 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:90 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:92 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:94 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:94 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:94 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:99 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:99 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:104 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:104 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:108 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:113 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:113 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:119 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:125 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:125 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:136 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:140 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:150 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:151 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:154 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/fault_hold.py:159 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:287 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1836 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1888 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1907 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1911 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1940 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2191 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2191 GUARD_OFF: pinned by mutation-autofix

## Forward-carry

- Carry 0 (from R11-OWNER-MODE-LEGS, body item 411606ae, the pin "the fault hold wins with a young leg latched"): not buildable here. MODE-LEGS' `_kept_leg` is not on main (`af4d89f76325`; its head is `handoff/r11-owner-mode-legs`). The hold returns before `_command` in `_arbitrate` (`_fault_stands`), downstream of `_served`, so a latched leg writes nothing under it by construction. Whichever of the two lands second owes the pin, as that body states; with this group first it is MODE-LEGS'. It lands in R11-OWNER-MODE-LEGS's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-MODE-LEGS
- Carry 2 (from R11-OWNER-FROST-HOLD, body item 0846c1b4, the composition owed by this group's merge if FROST-HOLD lands first): `frost_hold` is not on `origin/main` (`6a58ba5cb30b`; FROST-HOLD is #3882, open), so there is nothing to compose with at this head. FROST-HOLD's design (`e91a4e30`) places frost before this group, but this group lands on a main without `frost_hold`. Whichever of the two merges second composes them as design `57d5d278`'s "Interaction with the frost hold" states: `hold_supply → frost_hold.gate → fault_hold.gate` (frost's ON passes); frost's cut-off arm consulted after `fault_hold.consult` in `early_cutoff.on_room_event`; `device-fault` decided before `frost-hold` in `duty_ledger.step_verdict`; and no frost row written while `_fault_stands` holds. Lands in R11-OWNER-FROST-HOLD's `carry` in `dev/programme/rosters/wave-r11-groups.json`. Carry: R11-OWNER-FROST-HOLD
- Carry 1, FAULT-TEXT's carry (flag-prefill-reach): FAULT-TEXT has not merged (`origin/main` has no pre-fill Fault alarm text), and this group merges first, so per that carry FAULT-TEXT adds the hold's 10 minutes to the pre-fill rows on its rebase; it stands in this group's own `carry` in `dev/programme/rosters/wave-r11-groups.json` and lands in R11-OWNER-FAULT-TEXT's. Carry: R11-OWNER-FAULT-TEXT

## Friction

none
