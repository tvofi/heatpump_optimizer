R10-DISINFECTION-STEP-NOTICE: product ruling (2) of origin/handoff-body/r10-product-ruling-dhw-hard-max at d507c499 ("respect-and-surface"), completing outside pull request 3439's request. A disinfection cycle whose write the hot-water entity's step leaves under the credit threshold in force is named before it runs, with the configured, written and on-step temperatures, and credited nothing.

What changed, by owner:
- `pump_arbiter.py`: `cycle_write` exposes `_dhw_write`'s cycle arm (`_cycle_c`) for the parameters in force, with the disinfection temperature on the step down and up and the entity's step; `None` outside control or with no set-point entity state. `_bounded` delegates to `_bounded_on` (hass and configuration, no pass snapshot), so the quantisation has one owner and the guard never restates it.
- `legionella.py`: `OffStepNotice`, a small class beside `LegionellaGuard`, in `check_ceiling`'s signature-and-`set_issue` shape, not persistent, raises `dhw_legionella_off_step`. Active when hot water and the cycle are active, the arbiter writes a set-point entity, and that write is under target less `CREDIT_INSTANT_MARGIN_K` (1.0), or less `CREDIT_HOLD_MARGIN_K` (0.5) under `dhw_free_disinfection_enabled`. The margins are the guard's own credit literals named, values unchanged, read by `async_track`, `async_track_cycle` and the notice alike.
- Which notice shows: the off-step one. Raising it clears `dhw_legionella_unreachable`, and `raise_unreachable_issue` clears instead of raising while it stands, so its immersion-heater advice never shows for a rounding gap.
- `strings.json`, `translations/en.json`, `de.json`, `sv.json`: the notice text (placeholders `legionella_temp`, `written`, `step`, `below`, `above`); `README.md`'s notice list beside "Hot water is not reaching the disinfection temperature". User-facing text for its own text review: it names the cause, says no hardware is needed, and offers the step above (at least as hot as chosen) before the step below.
- No change to the arbiter's write, `dhw_hard_max_temp`, the thresholds or `DHW_LEGIONELLA_RETRY_HOURS`.

Placement: the brief puts the notice "beside `check_ceiling`". A method on `LegionellaGuard` measured `class_excess_loc` +47 (the class is over `GOD_CLASS_LOC_LIMIT`); the notice is one concern with its own state, so it is its own class under the limit in the same module, and the guard holds it. The guard's remaining two wiring lines are paid by naming the margins in the peak-rule comment: re-recorded `class_excess_loc` -1, reason in the commit. Alternatives: a guard method (+47, a raise for no gain in code); a callable through the coordinator's constructor (adds to the coordinator class, also over the limit).

Carry 0 of the brief (from #3452, item 9ac8c410) is discharged here: the shortfall the hard maximum leaves is surfaced, the ceiling stays.

## Head

`5c961851a2aa13501912dc5f959f8270ba7885c0` (branch cut from origin/main e23124ff6e45bac1d48b4a775dad555a37965355; measured `2026-11-13T21:38Z`)

## Mutation proof

Each mutant applied to `legionella.py` alone, `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` run, restored:
- M1 threshold constants swapped between the two rules: FAIL `R10-DISINFECTION-STEP-NOTICE the slider grid raises 201 of 1750 under the instant rule`, `... 436 of 1750 under the hold rule`, `... the instant rule's 201 are all at step 5`, `... the harness grid raises 34 / 71 of 330 (instant / hold)`.
- M2 the write restated as `round(target / step) * step` in place of `cycle_write`'s: the same four FAIL.
- M3 cycle predicate dropped (`cycle = True`): FAIL `R10-DISINFECTION-STEP-NOTICE null: hot water disabled raises none`. With the cycle itself disabled the arbiter's answer is already `None` (`dhw_cycle_temp` is `None`), so the predicate's live arm is hot water disabled.
- M4 `raise_unreachable_issue` raising under the off-step notice: FAIL `R10-DISINFECTION-STEP-NOTICE the off-step notice shows, not the unreachable notice's hardware advice`.
- M5 the unreachable notice not cleared when the off-step notice rises: the same FAIL.
- The credit edges, through `LegionellaGuard.async_track` (`_credit_edges`): `>=` to `>` or `if False:` on the hold rule FAIL `... hold credit counts target less 0.5 and not 0.01 under`; `<` to `<=` or `elif False:` on the instant rule FAIL `... instant credit counts target less 1.0 and not 0.01 under`. The notice's memo `if False:` FAILs `... an unchanged off-step signature does not re-raise the notice`.
- `pump_arbiter.py`, run with `tests/block_duty.py`: `_bounded`'s delegate `return` deleted FAILs `a commanded or held disinfection cycle writes its temperature, not the configured set-point`; `_bounded_on`'s `hi >=` to `>` FAILs `a charge limit below the entity's minimum writes the entity's minimum, never a value it refuses`; `_dhw_write`'s cycle `return` deleted FAILs `every row a cycle step can take writes the cycle's temperature, the idle and baseline rows too`.

Failing test first: the pins landed in 028dae841d ahead of the fix. The head's `tests/guard_pins.py` run against the base's production code (`cd <base worktree> && PYTHONPATH=tests/hastub python3 <head>/tests/guard_pins.py`): `8 of 79 GUARD PIN CHECKS FAILED`, the named case (everyday 55, disinfection 62, step 5, write 60) absent, the four counts, the which-shows pin, the dedupe and the clear; at the head `ALL 79 GUARD PIN CHECKS PASSED`.

## Null control

In `tests/guard_pins.py`, `_off_step_notice_pins`, every count asserted beside the rows it drove (the census asserts its own preconditions): 0 notices over the 1314 on-step slider rows and over the 169 on-step harness-grid rows, under both rules; 0 at steps 0.1 and 0.5; 0 with the cycle disabled, with hot water disabled, with no set-point entity, and with an arbiter that writes nothing (`pump_duty_mode` observe); the stock 55/60 raises none on any step under either rule.

Harness, base against head: `dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 6ced0aeb71d5fc00734eaf4098e65e5e665891e8, unchanged by this diff) run with `--grid` (2340 lines) and in its default mode (120 lines) from the base worktree and the head worktree, compared by `cmp`: both byte-identical (`cmp grid_base grid_head && cmp def_base def_head && echo BOTH-IDENTICAL` printed `BOTH-IDENTICAL`). The credit thresholds' values do not move: the three literals became the two named constants at the same values.

## Figures

Rows: the slider grid is the config flow's integer sliders (everyday 40-65, disinfection 55-70, disinfection above everyday) on a 30-80 °C number of step 0.1, 0.5, 1, 2, 5; the harness grid is `r10_disinfection_setpoint.py`'s `GRID_TEMPS` cycle rows (disinfection above everyday, at most 70) on the same steps. A row raises when `OffStepNotice` raises after one `LegionellaGuard.async_observe` pass.
- `201 of 1750` slider rows under the instant rule, all at step 5; `436 of 1750` under the hold rule; `0 of 1314` on-step slider rows; `34 / 71 of 330` harness-grid rows; `0 of 169` on-step harness-grid rows: `PYTHONPATH=tests/hastub python3 tests/guard_pins.py`
- harness lines byte-identical base against head: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_disinfection_setpoint.py --grid`
- `class_excess_loc` 17514 -> 17513: `python3 tests/structure.py`
- Architecture score: dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff e23124ff6e45bac1d48b4a775dad555a37965355`

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=5c961851a2aa13501912dc5f959f8270ba7885c0 -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

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
- custom_components/heatpump_optimizer/pump_arbiter.py:595 RETURN_DEL: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:611 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:615 CLAMP_DROP: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:621 BOOLOP: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:621 CMP_BOUND: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:621 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:1221 RETURN_DEL: pinned by mutation-autofix; killed locally by `tests/block_duty.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:1257 GUARD_OFF: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD
- custom_components/heatpump_optimizer/pump_arbiter.py:1259 RETURN_DEL: pinned by mutation-autofix; killed locally by `tests/guard_pins.py` under prepr.sh's MUTANT_CMD

## Red checks

`mutation`: the diff adds sites no ledger pin names yet (the moved `_bounded` body, the named margins, the new notice and `cycle_write`), so the mutation lane is red until mutation-autofix pins them after the push. The cheaper detector is prepr.sh step 6d, which listed every site before the push; its standing cost is one static read. The six stale `pump_arbiter.py` pins on `_bounded` and `_dhw_write` were deleted here for the same move, as ci_predict prescribes.

## Forward-carry

none

## Friction

none
