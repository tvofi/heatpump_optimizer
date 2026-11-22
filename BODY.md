Supersedes #3848, carried in place as every outside pull request is (decision 0017). Thank you, @Bankaifan: the first commit here is yours, with your authorship kept, and the replay in #3848 made the change easy to check.

On a re-plan the planner could put a new hot-water run on the first step. `drop_unstartable` and `startable_steps` always exempted the first step as "a charge already under way" (#3440, #3531), even when the compressor was heating or stopped. A run the pump would never start was kept: the arbiter wrote hot water only, heating was locked out, and the compressor stopped, which cost one extra start each time. The exemption now holds only while a charge actually runs (`ThermalState.dhw_charge_under_way`, set by `pump_signals.with_dhw_under_way` from the same running reading as `compressor_running`). Otherwise the first step is judged like any other. The default `True` keeps every caller that does not know the flag, such as harnesses and what-if, on the old behaviour.

On top of the contributor's commit:
- **dhw_start.py**: the start-condition helpers (`STARTABLE_ROUNDS`, `dhw_start_temps`, `startable_steps`, `drop_unstartable`, `place_startable`) move out of `dhw_planner.py` into their own module. It holds no state and reads only its arguments and `thermal_model`. This pays the `module_excess_loc` breach that #3848 met on main (+13 against #3735's budget) and records the row down from 21779 to 21676.
- **Classification**: `tests/closures.json` lists `dhw_start.py` beside `dhw_planner.py` in the 27 closures that list the planner, which imports it at module level. The 17 `killed_by` pins of the moved scopes move to `tests/mutation_ledger/killed_by/dhw_start.py/`, with anchors re-keyed and text and digests unchanged. 16 rows of `dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py` now name `dhw_start.py`.
- **Comment ratchet**: two docstring sentences over 40 words are split (`drop_unstartable`, `with_dhw_under_way`).
- **tests/features.py**: the `_repair_dhw_floor` stand-in `_lg_whole_tail_repair` takes `charge_running`. On #3848 it raised `TypeError` and ended the suite.
- **docs/architecture.md** and **tests/deployment_shape.py**: the module tree and counts (99 modules, 64 free of `homeassistant`; the #1218 note's 118 package files), and the D6 claims register re-run for them (C32, C33). `tests/doc_claims.py`, `tests/entities.py` and `dev/audit/rounds/round4/D6/claims.py` derive these from the tree.

Known residual (documented in the helper): when the running signal is unsettled or missing, `duty_switch.running_now` falls back to the planned draw, so the old behaviour remains there.

## Head

`1581a49b8bebac19dda827484d80eeddd5316aac`

## Mutation proof

- `python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py <worktree of the head>`: all 43 named mutants (M1-M43) print KILLED under `tests/block_duty.py`, none prints ANCHOR, and the NULL comment-only mutant SURVIVES. That includes the 16 rows re-pointed to `dhw_start.py` (M2, M5, M8, M10, M16-M21, M29, M35-M37, M42, NULL) and the planner's own (M4, M13, M22, M27).
- With the old first-step rule restored and the new signatures kept, `tests/block_duty.py` goes red on "a first-step charge on a warm tank with no charge under way is dropped, and nothing carries it on" (#3848's proof, re-run on the moved code by M19 and M42).

## Null control

- On #3848's base `40e513ee`, `tests/block_duty.py` passes 153 checks (the contributor's run); at this head it prints `ALL 156 BLOCK DUTY CHECKS PASSED`. The three new checks are the contributor's.
- The harness's NULL mutant (a comment-only change in `dhw_start.py`) survives, so the kills are the code's and not the harness's.
- The move alone changes no score: `python3 tools/audit/archscore/score.py --diff 3a98735a7e HEAD` and `--diff 3a98735a7e b116ae0e7c` (the contributor's commit alone) both print `dS -0.0006`.

## Figures

<!-- figure-block: structure-ratchet mb=3a98735a7ecc59e7ecc095a0429cdf6251d956ec head=1581a49b8bebac19dda827484d80eeddd5316aac -->
~~~text
STRUCTURE RATCHET PASSED
~~~
<!-- /figure-block -->

## Architecture score

Architecture score: dS -0.0006 (`python3 tools/audit/archscore/score.py --diff 3a98735a7e HEAD`)

- `coord_footprint` 2525 -> 2526: the solve record now asks whether a hot-water charge runs as the solve starts. The coordinator is the one place that holds both the pump signals and the running reading, so it makes that one `pump_signals.with_dhw_under_way` call there; the logic itself lives in `pump_signals`. The module move reads neutral (the same dS with and without it).

## Red checks

- `tests / mutation`: `ci_predict.py` (prepr step 6d) names 6 added unpinned sites, all on the contributor's new lines: `dhw_start.py:70` BOOLOP, `dhw_start.py:126` RETURN_DEL, `pump_signals.py:381` BOOLOP and CMP_BOUND, and `pump_signals.py:382` BOOLOP and RETURN_DEL. mutation-autofix (`tests/mutation_table.py --pin-killed`) records them on this branch after the push (ci-autofix.md). That job is the cheaper detector, at a standing cost of one bot commit.
- `arch-score`: the `coord_footprint` rise is answered under `## Architecture score`.

## Unpinned sites

- custom_components/heatpump_optimizer/dhw_start.py:70 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/dhw_start.py:126 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_signals.py:381 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_signals.py:381 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_signals.py:382 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_signals.py:382 RETURN_DEL: pinned by mutation-autofix

## Forward-carry

none

## Friction

none
