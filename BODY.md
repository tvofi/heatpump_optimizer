Supersedes #3848, carried in place as every outside pull request is (decision 0017). Thank you, @Bankaifan: the first commit here is yours, with your authorship kept, and the replay in #3848 made the change easy to check.

On a re-plan the planner could put a new hot-water run on the first step. `drop_unstartable` and `startable_steps` always exempted the first step as "a charge already under way" (#3440, #3531), even when the compressor was heating or stopped. A run the pump would never start was kept: the arbiter wrote hot water only, heating was locked out, and the compressor stopped, which cost one extra start each time. The exemption now holds only while a charge actually runs (`ThermalState.dhw_charge_under_way`, set by `pump_signals.with_dhw_under_way` from the same running reading as `compressor_running`). Otherwise the first step is judged like any other. The default `True` keeps every caller that does not know the flag, such as harnesses and what-if, on the old behaviour.

On top of the contributor's commit:
- **dhw_start.py**: the start-condition helpers (`STARTABLE_ROUNDS`, `dhw_start_temps`, `startable_steps`, `drop_unstartable`, `place_startable`) move out of `dhw_planner.py` into their own module. It holds no state and reads only its arguments and `thermal_model`. This pays the `module_excess_loc` breach that #3848 met on main (+13 against #3735's budget) and records the row down from 21779 to 21676.
- **Classification**: `tests/closures.json` lists `dhw_start.py` beside `dhw_planner.py` in the 27 closures that list the planner, which imports it at module level. The 17 `killed_by` pins of the moved scopes move to `tests/mutation_ledger/killed_by/dhw_start.py/`, with anchors re-keyed and text and digests unchanged. 16 rows of `dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py` now name `dhw_start.py`.
- **Comment ratchet**: two docstring sentences over 40 words are split (`drop_unstartable`, `with_dhw_under_way`).
- **tests/features.py**: the `_repair_dhw_floor` stand-in `_lg_whole_tail_repair` takes `charge_running`. On #3848 it raised `TypeError` and ended the suite.
- **docs/architecture.md** and **tests/deployment_shape.py**: the module tree and counts (99 modules, 64 free of `homeassistant`; the #1218 note's 118 package files), and the D6 claims register re-run for them (C32, C33).

Repair of the reds at `0814b685339c9d4b598b3abe8812c0734ab24c75` (CI run 45044399082). The production tree is unchanged from that head: `git diff 0814b685 HEAD -- custom_components/` prints nothing.
- **tests/features.py, the what-if pin**: the check "the what-if solve takes the reading the live plan was solved with, not a fresh one" required the text `compressor_running=duty_switch.running_now(...)` in `_solve_record`. This pull request binds that reading once (`running := duty_switch.running_now(...)`) and hands it to both `compressor_running` and `with_dhw_under_way`, so the keyword spelling was gone while the reading was the same. The `_solve_record` half now reads the call `duty_switch.running_now(duty_switch.record_for(self), self._current_action)`; the `_whatif_solve` half (`solved_running`) is unchanged, and the check above it (`_hsr_wired`) pins the reading by behaviour. Alternative not taken: rewrite `_solve_record` to keep the keyword spelling (the first repair commit here, reverted by the second). It added three coordinator lines and breached `class_excess_loc`, `max_class_loc` and `module_excess_loc` by +3 each, only to satisfy a source-text match.
- **tests/features.py, a new check**: nothing pinned that the coordinator hands the planner the under-way state. The check "the scheduled solve's state holds a hot-water charge under way only while the compressor runs in a mode serving hot water" drives `Coord._solve_record` with an observed mode and reads `inputs.state.dhw_charge_under_way`.
- **dev/audit/rounds/round4/D6/claims.py**: the `RESULT arch_modules_on_disk` and `arch_map_listed` header lines read 99, with `dhw_start.py` named in their history.
- **tests/mutation_ledger/killed_by/**: the six sites this diff added, each killed by `tests/block_duty.py`.

Known residual (documented in the helper): when the running signal is unsettled or missing, `duty_switch.running_now` falls back to the planned draw, so the old behaviour remains there.

## Head

`0fdc3d5ff72a065eeee4a4e5c6c65760ce5c97f0`, four commits on `0814b685339c9d4b598b3abe8812c0734ab24c75`, measured against origin/main `1207ee13b0e439a4acefccabace691785af2ebad` at 2026-11-22T19:33:58Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

The block run is `python3 tools/audit/seat/features_block.py --prelude 'exec(open("PRE").read())' "# The coordinator hands the reading" "# What the commit program is told"` with `PYTHONPATH=tests/hastub`. PRE is written by `features_block.py --emit-prelude PRE` with the same two markers.
- At this head: `ALL 3 FEATURES BLOCK PASSED`.
- With `coordinator.py` from `0814b685` and the old keyword pin, the what-if check FAILs (`1 of 2 FEATURES BLOCK FAILED`), as in CI.
- M1: the `with_dhw_under_way(...)` call replaced by `(state, running := ...)[0]`. The new check FAILs: `1 of 3 FEATURES BLOCK FAILED`.
- M2: the scheduled solve reads `duty_switch.record_for(self).solved_running` in place of `running_now(...)`. All three FAIL: `3 of 3 FEATURES BLOCK FAILED`. The relaxed pin still sees a scheduled solve that stops reading fresh.
- With `coordinator.py` from the base `8ef450936a` (before this pull request), the new check FAILs.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/block_duty.py` printed `PIN KILLED: 6 pinned, 0 left unpinned`. Each of the six sites took `tests/block_duty.py` from `rc=0 failed=0` to `rc=1`, and its comment-only null control at `dhw_start.py:21` survived. An earlier unrestricted `--pin-killed` run used every driver its closure selects. It reached the six sites but hit the 30-minute background limit while still running `tests/config_flow_steps.py`. The run before that one, on the first repair commit, refused as `INCONCLUSIVE` because `tests/structure.py` was red at its baseline.

## Null control

- The finder's harness, `python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py WORKTREE`, was run on a worktree of `0814b685` and on one of `0fdc3d5f`. Both print 43 KILLED, no ANCHOR, and `NULL comment-only change: SURVIVED`. The two ends read the same because the production tree is identical, and that is the expected result: the repair moves tests and ledger, not code.
- The new features check passes at this head and fails with the under-way call removed (M1) and at the base.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` prints `RESULT arch_modules_on_disk=99 modules` and `RESULT arch_map_listed=99 modules`. At `0814b685` CI's `tests/harness_headers.py` printed `header='98' printed='99'` for both. `git status --short` after the run is empty, so the committed outputs are byte-identical.

## Figures

- `python3 tests/structure.py` at `0fdc3d5f`: rc 0. At the first repair commit `109cd2350e` it printed `3 STRUCTURE BUDGET(S) BREACHED` (`class_excess_loc`, `max_class_loc`, `module_excess_loc`, +3 each), which is why that rewrite was reverted.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.

## Architecture score

Architecture score: dS -0.0006 (`python3 tools/audit/archscore/score.py --diff 3a98735a7e 0814b685`, carried: the production tree at `0fdc3d5f` is byte-identical to `0814b685`'s)

- `coord_footprint` 2525 -> 2526: the solve record now asks whether a hot-water charge runs as the solve starts. The coordinator is the one place that holds both the pump signals and the running reading, so it makes that one `pump_signals.with_dhw_under_way` call there; the logic itself lives in `pump_signals`. The module move reads neutral (the same dS with and without it).

## Red checks

- `tests / fast (3.14)` at `0814b685`: `tests/features.py` printed `1 of 6028 FEATURE CHECKS FAILED` on the what-if pin, and `tests/harness_headers.py` printed 2 FAILs on the claims.py header (98 against 99). Both came from this pull request's own tree, and both are repaired above. Cheaper detector: `tools/audit/seat/features_block.py` on the block that holds the check, under one second, and `python3 dev/audit/rounds/round4/D6/claims.py`, about 2 s. Both already exist, so nothing is built.
- `tests / mutation` at `0814b685`: `MUTATION TABLE REFUSED -- 1929 unpinned site(s) against 1923 ... 6 of them added by this diff`. The six are pinned above. Cheaper detector: `ci_predict.py` (prepr step 6d) names them before the push, at no standing cost; it existed already.
- `gate` at `0814b685`: derived from the two above.
- `arch-score`: the `coord_footprint` rise is answered under `## Architecture score`.

## Unpinned sites

- custom_components/heatpump_optimizer/dhw_start.py:70 BOOLOP: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json`)
- custom_components/heatpump_optimizer/dhw_start.py:126 RETURN_DEL: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json`)
- custom_components/heatpump_optimizer/pump_signals.py:381 BOOLOP: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json`)
- custom_components/heatpump_optimizer/pump_signals.py:381 CMP_BOUND: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json`)
- custom_components/heatpump_optimizer/pump_signals.py:382 BOOLOP: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json`)
- custom_components/heatpump_optimizer/pump_signals.py:382 RETURN_DEL: killed_by tests/block_duty.py (`tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json`)

## Forward-carry

none

## Friction

none
