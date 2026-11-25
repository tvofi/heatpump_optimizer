Supersedes #3848, carried in place as every outside pull request is (decision 0017). Thank you, @Bankaifan: the first commit here is yours, with your authorship kept, and the replay in #3848 made the change easy to check.

On a re-plan the planner could put a new hot-water run on the first step. `drop_unstartable` and `startable_steps` always exempted the first step as "a charge already under way" (#3440, #3531), even when the compressor was heating or stopped. A run the pump would never start was kept: the arbiter wrote hot water only, heating was locked out, and the compressor stopped, which cost one extra start each time. The exemption now holds only while a charge actually runs (`ThermalState.dhw_charge_under_way`, set by `pump_signals.with_dhw_under_way` from the same running reading as `compressor_running`). Otherwise the first step is judged like any other. The default `True` keeps every caller that does not know the flag, such as harnesses and what-if, on the old behaviour.

On top of the contributor's commit:
- **dhw_start.py**: the start-condition helpers (`STARTABLE_ROUNDS`, `dhw_start_temps`, `startable_steps`, `drop_unstartable`, `place_startable`) move out of `dhw_planner.py` into their own module. It holds no state and reads only its arguments and `thermal_model`. This pays the `module_excess_loc` breach that #3848 met on main (+13 against #3735's budget); after the merge of main below, the row reads 21672 against main's 21775.
- **Classification**: `tests/closures.json` lists `dhw_start.py` beside `dhw_planner.py` in the 27 closures that list the planner, which imports it at module level. The 17 `killed_by` pins of the moved scopes move to `tests/mutation_ledger/killed_by/dhw_start.py/`, with anchors re-keyed and text and digests unchanged. 16 rows of `dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py` now name `dhw_start.py`.
- **Comment ratchet**: two docstring sentences over 40 words are split (`drop_unstartable`, `with_dhw_under_way`).
- **tests/features.py**: the `_repair_dhw_floor` stand-in `_lg_whole_tail_repair` takes `charge_running`. On #3848 it raised `TypeError` and ended the suite.
- **docs/architecture.md** and **tests/deployment_shape.py**: the module tree and counts (102 modules, 65 free of `homeassistant`; the #1218 note's 121 package files), and the D6 claims register re-run for them (C32, C33).

Repair of the reds at `0814b685339c9d4b598b3abe8812c0734ab24c75` (CI run 45044399082). This pull request's production delta is the same patch as at that head: `git diff <merge-base> <head> -- custom_components/ | git patch-id --stable` prints `3dbca811e3fab036c0aee2084e4ad773999d3147` both for `0814b685` against its merge base with origin/main and for this head against its own.
- **tests/features.py, the what-if pin**: the check "the what-if solve takes the reading the live plan was solved with, not a fresh one" required the text `compressor_running=duty_switch.running_now(...)` in `_solve_record`. This pull request binds that reading once (`running := duty_switch.running_now(...)`) and hands it to both `compressor_running` and `with_dhw_under_way`, so the keyword spelling was gone while the reading was the same. The `_solve_record` half now reads the call `duty_switch.running_now(duty_switch.record_for(self), self._current_action)`; the `_whatif_solve` half (`solved_running`) is unchanged, and the check above it (`_hsr_wired`) pins the reading by behaviour. Alternative not taken: rewrite `_solve_record` to keep the keyword spelling (the first repair commit here, reverted by the second). It added three coordinator lines and breached `class_excess_loc`, `max_class_loc` and `module_excess_loc` by +3 each, only to satisfy a source-text match.
- **tests/features.py, a new check**: nothing pinned that the coordinator hands the planner the under-way state. The check "the scheduled solve's state holds a hot-water charge under way only while the compressor runs in a mode serving hot water" drives `Coord._solve_record` with an observed mode and reads `inputs.state.dhw_charge_under_way`.
- **dev/audit/rounds/round4/D6/claims.py**: the `RESULT arch_modules_on_disk` and `arch_map_listed` header lines read 102 after the merge of main, with `dhw_start.py` named in their history.
- **tests/mutation_ledger/killed_by/**: the six sites this diff added, each killed by `tests/block_duty.py`.

Known residual (documented in the helper): when the running signal is unsettled or missing, `duty_switch.running_now` falls back to the planned draw, so the old behaviour remains there.

Merge of main, 2026-11-25. The head merges origin/main `0f63320c96cb4e1926a584c89d0dfe920d1778ab` into `72ea4049b99698a1694b9bf5d36fea83b6beb92a`, which merged main `24e3f37620` into the previous head `699cc32e6a` and resolved its conflicts in `dev/audit/rounds/round4/D6/claims.{json,md,py}`, `docs/architecture.md` and `tests/deployment_shape.py`. The second merge had no conflict. One commit follows it:
- **docs/architecture.md**: "The other 64 modules are deliberately free of it" reads 65. Main moved that count from 63 to 64 with its own new module, and this pull request adds `dhw_start.py`, which imports no `homeassistant`. Both sides edited the count one line apart, so the merge kept 64. `tests/entities.py` (the `The other (\d+) modules are deliberately free` check) and the `tests/doc_claims.py` prose-count census both derive the count from the tree: 102 modules less the 37 that import `homeassistant` (36 at module level, one inside a function).
- The claim files `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are byte-identical to origin/main: `git diff --quiet origin/main HEAD -- <file>` exits 0 for each.

## Head

`859dda1c385f66ff956cd6cde0734d5871d92724`, one commit on the merge `b45c72ba20751a63c4d5b5bf89d2eddf47795887` of origin/main `0f63320c96cb4e1926a584c89d0dfe920d1778ab`, measured at 2026-11-25T01:03:39Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

The block run is `python3 tools/audit/seat/features_block.py --prelude 'exec(open("PRE").read())' "# The coordinator hands the reading" "# What the commit program is told"` with `PYTHONPATH=tests/hastub`. PRE is written by `features_block.py --emit-prelude PRE` with the same two markers.
- At this head (`859dda1c38`): `ALL 3 FEATURES BLOCK PASSED`.
- With `coordinator.py` from `0814b685` and the old keyword pin, the what-if check FAILs (`1 of 2 FEATURES BLOCK FAILED`), as in CI.
- M1: the `with_dhw_under_way(...)` call replaced by `(state, running := ...)[0]`. The new check FAILs: `1 of 3 FEATURES BLOCK FAILED` (re-run at `859dda1c38`, `coordinator.py` restored after).
- M2: the scheduled solve reads `duty_switch.record_for(self).solved_running` in place of `running_now(...)`. All three FAIL: `3 of 3 FEATURES BLOCK FAILED`. The relaxed pin still sees a scheduled solve that stops reading fresh.
- With `coordinator.py` from the base `8ef450936a` (before this pull request), the new check FAILs.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/block_duty.py` printed `PIN KILLED: 6 pinned, 0 left unpinned`. Each of the six sites took `tests/block_duty.py` from `rc=0 failed=0` to `rc=1`, and its comment-only null control at `dhw_start.py:21` survived. An earlier unrestricted `--pin-killed` run used every driver its closure selects. It reached the six sites but hit the 30-minute background limit while still running `tests/config_flow_steps.py`. The run before that one, on the first repair commit, refused as `INCONCLUSIVE` because `tests/structure.py` was red at its baseline.

## Null control

- The finder's harness, `python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py WORKTREE` (sha1 `b333680a2d91aa5f655d707594d41dc074b51745` at this head), was run earlier on worktrees of `0814b685` and `0fdc3d5f`: both printed 43 KILLED, no ANCHOR, and `NULL comment-only change: SURVIVED`. Re-run at `859dda1c38` on a clean worktree: 42 KILLED, `M3 ledger not-startable branch removed: ANCHOR x0`, `NULL comment-only change: SURVIVED rc=0 0 failing`. Control: main's own copy of the harness on a worktree of origin/main `0f63320c` prints the same three readings (42 KILLED, M3 ANCHOR x0, NULL SURVIVED). M3's anchor names `pump_arbiter.py`; main's `e9922bc1c3` moved that branch to `duty_ledger.py:32` (`git log -S'_not_startable(row)' 699cc32e6a..origin/main`), so M3 now reads as unproven at both ends. That is main's change and this pull request leaves it alone.
- The new features check passes at this head and fails with the under-way call removed (M1) and at the base.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` prints `RESULT arch_modules_on_disk=102 modules` and `RESULT arch_map_listed=102 modules` at `859dda1c38`. At `0814b685` CI's `tests/harness_headers.py` printed `header='98' printed='99'` for both. `git status --short` after the run is empty, so the committed outputs are byte-identical.

## Figures

- `python3 tests/structure.py` at `859dda1c38`: `STRUCTURE RATCHET PASSED`. At the first repair commit `109cd2350e` it printed `3 STRUCTURE BUDGET(S) BREACHED` (`class_excess_loc`, `max_class_loc`, `module_excess_loc`, +3 each), which is why that rewrite was reverted.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at `859dda1c38`, merge base `0f63320c`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` at `859dda1c38`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` at `859dda1c38`: `PRE-PR: 859dda1c385f66ff956cd6cde0734d5871d92724 ... rc=0`, with `CI PREDICT: no closures, fast, governance or instrument red predicted against 0f63320c96cb`. Its diff-mutant step skipped (`MUTANT_CMD` unset): the production patch is the one whose six added sites are pinned under `## Unpinned sites`.

## Architecture score

Architecture score: dS -0.0006 (`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` at `859dda1c38`, merge base `0f63320c`)

- `coord_footprint` 2521 -> 2522: the solve record now asks whether a hot-water charge runs as the solve starts. The coordinator is the one place that holds both the pump signals and the running reading, so it makes that one `pump_signals.with_dhw_under_way` call there; the logic itself lives in `pump_signals`. The module move reads neutral (the same dS with and without it).

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
