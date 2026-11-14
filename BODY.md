R10-DISINFECTION-STEP-NOTICE: product ruling (2) of origin/handoff-body/r10-product-ruling-dhw-hard-max at d507c499 ("respect-and-surface"), completing outside pull request 3439's request. A disinfection cycle whose write the hot-water entity's step leaves under the credit threshold in force is named before it runs, with the configured, written and on-step temperatures, and credited nothing.

What changed, by owner:
- `pump_arbiter.py`: `cycle_write` exposes the cycle write for the parameters in force — `thermal_model.dhw_step_target_c` on a cycle step, on the hot-water entity's `inputs.SetpointGrid`, the one statement `_dhw_write` itself reads — with the disinfection temperature on the step down and up (`SetpointGrid.bounded`) and the entity's step (`SetpointGrid.step`); `None` outside control, with no set-point entity state, or with no cycle temperature. The quantisation has one owner (`SetpointGrid`) and the guard never restates it.
- `legionella.py`: `OffStepNotice`, a small class beside `LegionellaGuard`, in `check_ceiling`'s signature-and-`set_issue` shape, not persistent, raises `dhw_legionella_off_step`. Active when hot water and the cycle are active, the arbiter writes a set-point entity, and that write is under target less `CREDIT_INSTANT_MARGIN_K` (1.0), or less `CREDIT_HOLD_MARGIN_K` (0.5) under `dhw_free_disinfection_enabled`. The margins are the guard's own credit literals named, values unchanged, read by `async_track`, `async_track_cycle` and the notice alike.
- Which notice shows: the off-step one. Raising it clears `dhw_legionella_unreachable`, and `raise_unreachable_issue` clears instead of raising while it stands, so its immersion-heater advice never shows for a rounding gap.
- `strings.json`, `translations/en.json`, `de.json`, `sv.json`: the notice text (placeholders `legionella_temp`, `written`, `step`, `below`, `above`); `README.md`'s notice list beside "Hot water is not reaching the disinfection temperature". User-facing text for its own text review: it names the cause, says no hardware is needed, and offers the step above (at least as hot as chosen) before the step below.
- No change to the arbiter's write, `dhw_hard_max_temp`, the thresholds or `DHW_LEGIONELLA_RETRY_HOURS`.

Placement: the brief puts the notice "beside `check_ceiling`". A method on `LegionellaGuard` measured `class_excess_loc` +47 (the class is over `GOD_CLASS_LOC_LIMIT`); the notice is one concern with its own state, so it is its own class under the limit in the same module, and the guard holds it. The guard's remaining two wiring lines are paid by naming the margins in the peak-rule comment: re-recorded `class_excess_loc` -1, reason in the commit. Alternatives: a guard method (+47, a raise for no gain in code); a callable through the coordinator's constructor (adds to the coordinator class, also over the limit).

Carry 0 of the brief (from #3452, item 9ac8c410) is discharged here: the shortfall the hard maximum leaves is surfaced, the ceiling stays.

Carry 1 of the brief (the owner ruling of 2026-11-13 folding this outside-sourced group into round 10) is a scheduling ruling, not a change: this pull request is that fold, and it carries no code of its own.

## Head

`a07c37b273744ade8cc2c48d07d4a79c58365196` (measured `2026-11-14T00:56Z`, origin/main `50373173d486faf394b24637c177ab38b691b394`): the handed-off head `5c961851a2aa13501912dc5f959f8270ba7885c0` plus merge `a07c37b273744ade8cc2c48d07d4a79c58365196` of origin/main 50373173d4, the repair the opener's `merging origin/main into 5c961851a2 conflicts` refusal asked for. The reviewer's delta is `git diff 5c961851a2aa13501912dc5f959f8270ba7885c0 HEAD`, resolved file by file:
- `pump_arbiter.py` (content conflict, three hunks): main moved `_bounded`'s body into `inputs.SetpointGrid.bounded` (`_grid`, `setpoint_grid`) and `_dhw_write`'s cycle and everyday arms into `thermal_model.dhw_step_target_c` (`_dhw_target`), the same quantisation this branch had split into `_bounded_on` and `_cycle_c`. Union: main's import line, `_bounded`, `_grid`, `_dhw_write` and `_dhw_target` taken whole; this branch's `CycleWrite` and `cycle_write` kept with their contract, re-expressed on main's owners (`setpoint_grid` in place of `_bounded_on`'s entity-state check, `dhw_step_target_c(params, True, grid)` in place of `_cycle_c`, `grid.bounded(target, rounding=...)` for below and above, `grid.step` in place of `setpoint_step`). `_bounded_on`, `_cycle_c` and the `setpoint_step` import are gone: main's grid is their one owner. Read back: every main-side line of the three hunks is in the merged file (`git diff origin/main HEAD -- custom_components/heatpump_optimizer/pump_arbiter.py` is the `CycleWrite`/`cycle_write` addition alone), and the branch-side clauses survive as `cycle_write`'s three `None` arms and its four fields. One semantic delta, named: the branch's `cycle_write` returned `None` with no `dhw_cycle_temp` through `_cycle_c`; the merged one tests `params.dhw_cycle_temp is None` itself, since `dhw_step_target_c` falls back to the everyday target there.
- `tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.835d5167.json`, `_bounded.RETURN_DEL.f7af5135.json` (rename/delete): main's rows kept. The branch deleted their predecessors (`ebd65023`, `d4401a97`) because its `_bounded` changed; the merged `_bounded` is main's, and each row's `old` line is in the merged file (sha1 of the line, first 8 hex, is the row's suffix: `mutation_table.py` anchor rule). Re-derived by the ledger's own tool, not by hand: main's ledger checked out, then `python3 tests/mutation_table.py --carry-rows e23124ff6e45bac1d48b4a775dad555a37965355 5c961851a2aa13501912dc5f959f8270ba7885c0` printed `CARRIED` and left the ledger byte-identical to main's (`git status --short tests/mutation_ledger` lists only main's own staged rows): the six rows the branch deleted have no file in the merged tree.
- `tests/structure_budgets.json`: auto-resolved by the ledger merge driver (`class_excess_loc` 17514 + both deltas = 17502); `python3 tests/structure.py` at the merged head: `STRUCTURE RATCHET PASSED`, `class_excess_loc 17502 <= 17502`.
- `strings.json`, `translations/{en,de,sv}.json`, `README.md`: auto-merged, read back. Key parity across all four: 1509 leaf keys each, none missing or extra against `strings.json` (a `json` walk of each file). Main's #3531 and #3557 added the hysteresis entities and `dhw_minimum_above_start`; neither touches `legionella.py` (`git diff --stat e23124ff6e 50373173d4 -- custom_components/` lists no `legionella.py`). Re-verified sentence: the `dhw_legionella_off_step` description's "so it writes {written} °C", against the merged `cycle_write`, whose `written_c` is `dhw_step_target_c` on a cycle step, the value `_dhw_write` returns there; pinned by `55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step` in `tests/guard_pins.py`, passing at the merged head. Its "retried about a day later" reads `DHW_LEGIONELLA_RETRY_HOURS` in `legionella.py`, unchanged by main.

## Mutation proof

Each mutant applied to `legionella.py` alone, `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` run, restored (at 5c961851a2; `legionella.py` is unchanged by the merge):
- M1 threshold constants swapped between the two rules: FAIL `R10-DISINFECTION-STEP-NOTICE the slider grid raises 201 of 1750 under the instant rule`, `... 436 of 1750 under the hold rule`, `... the instant rule's 201 are all at step 5`, `... the harness grid raises 34 / 71 of 330 (instant / hold)`.
- M2 the write restated as `round(target / step) * step` in place of `cycle_write`'s: the same four FAIL.
- M3 cycle predicate dropped (`cycle = True`): FAIL `R10-DISINFECTION-STEP-NOTICE null: hot water disabled raises none`. With the cycle itself disabled the arbiter's answer is already `None` (`dhw_cycle_temp` is `None`), so the predicate's live arm is hot water disabled.
- M4 `raise_unreachable_issue` raising under the off-step notice: FAIL `R10-DISINFECTION-STEP-NOTICE the off-step notice shows, not the unreachable notice's hardware advice`.
- M5 the unreachable notice not cleared when the off-step notice rises: the same FAIL.
- The credit edges, through `LegionellaGuard.async_track` (`_credit_edges`): `>=` to `>` or `if False:` on the hold rule FAIL `... hold credit counts target less 0.5 and not 0.01 under`; `<` to `<=` or `elif False:` on the instant rule FAIL `... instant credit counts target less 1.0 and not 0.01 under`. The notice's memo `if False:` FAILs `... an unchanged off-step signature does not re-raise the notice`.

The merged `cycle_write`, at the merged head, `tests/guard_pins.py` (driver `/root/mut.sh`-shaped: `sed` one line, run, `cp` the original back, `cmp` confirms the mutant applied and the restore):
- `if grid is None or params.dhw_cycle_temp is None:` to `if False:`: rc=1, `AttributeError: 'NoneType' object has no attribute 'bounded'` in `cycle_write`.
- `dhw_step_target_c(params, True, grid)` to `grid.bounded(float(params.dhw_cycle_temp))` (the hard maximum dropped): FAIL the four count pins of M1.
- `grid.step` to `1.0`: FAIL `55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step`.
- `rounding="down"` dropped from `below_c` (nearest): **survives**, `ALL 79 GUARD PIN CHECKS PASSED`; the same survivor holds at 5c961851a2 (`_bounded_on(..., rounding="down")`), so the merge neither opens nor closes it, and this repair round, scoped to the conflict, adds no pin for it. Not a ledger operator site (`mutation_table.py` draws no keyword-argument mutant), so no ledger row or `## Unpinned sites` line names it; disclosed here for the fix reviewer's step 2 judgement.

Failing test first: the pins landed in 028dae841d ahead of the fix. The head's `tests/guard_pins.py` run against the base's production code: `8 of 79 GUARD PIN CHECKS FAILED`; at 5c961851a2 and at the merged head `ALL 79 GUARD PIN CHECKS PASSED`.

## Null control

In `tests/guard_pins.py`, `_off_step_notice_pins`, every count asserted beside the rows it drove (the census asserts its own preconditions): 0 notices over the 1314 on-step slider rows and over the 169 on-step harness-grid rows, under both rules; 0 at steps 0.1 and 0.5; 0 with the cycle disabled, with hot water disabled, with no set-point entity, and with an arbiter that writes nothing (`pump_duty_mode` observe); the stock 55/60 raises none on any step under either rule. All pass at the merged head.

Harness, base against 5c961851a2: `dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 6ced0aeb71d5fc00734eaf4098e65e5e665891e8, unchanged by this diff) run with `--grid` and in its default mode from the base worktree and the head worktree, compared by `cmp`: both byte-identical. Not re-run at the merged head: the merge changes no file the harness's credit thresholds come from.

## Figures

Rows: the slider grid is the config flow's integer sliders (everyday 40-65, disinfection 55-70, disinfection above everyday) on a 30-80 °C number of step 0.1, 0.5, 1, 2, 5; the harness grid is `r10_disinfection_setpoint.py`'s `GRID_TEMPS` cycle rows (disinfection above everyday, at most 70) on the same steps. A row raises when `OffStepNotice` raises after one `LegionellaGuard.async_observe` pass.
- `201 of 1750` slider rows under the instant rule, all at step 5; `436 of 1750` under the hold rule; `0 of 1314` on-step slider rows; `34 / 71 of 330` harness-grid rows; `0 of 169` on-step harness-grid rows: `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` (`ALL 79 GUARD PIN CHECKS PASSED` at the merged head)
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py`: `ALL 153 BLOCK DUTY CHECKS PASSED` at the merged head
- `class_excess_loc` 17502 <= 17502: `python3 tests/structure.py`
- Architecture score: dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff 50373173d486faf394b24637c177ab38b691b394`

Not measured: money (no flat-price arm); Fahrenheit entities, where `step` is in the entity's unit.

## Unpinned sites

- custom_components/heatpump_optimizer/legionella.py:56 CONST: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:57 CONST: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:92 BOOLOP: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:97 BOOLOP: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:97 CMP_BOUND: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:97 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:99 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:102 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:277 CMP_BOUND: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:277 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:296 CMP_BOUND: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/legionella.py:296 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:1224 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD

## Red checks

`mutation`: the diff adds sites no ledger pin names yet (the named margins, the new notice and `cycle_write`), so the mutation lane is red until mutation-autofix pins them after the push. The cheaper detector is prepr.sh step 6d, which listed every site before the push; its standing cost is one static read. The merge removed the branch's own `_bounded_on` and `_cycle_c` sites (main's `SetpointGrid` owns them), so the earlier body's `pump_arbiter.py` lines at 595-621, 1221 and 1259 are gone from the list, and main's `_bounded` rows stand.

`tests / closures` and `tests / fast (3.14)`: prepr's closures step was skipped at this head (PREPR_SKIP_CLOSURES=1) because tests/features.py's charge-start-dip day-type check ("a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked") reads the real clock and fails on Saturdays and Sundays at origin/main (from PR 3444); the fix is PR 3578, owned by R10-HOTFIX-FEATURES-WEEKEND-CLOCK; no cheaper detector in this group; CI's closures job judges the head once the hotfix is on main.

## Forward-carry

none

## Friction

none
