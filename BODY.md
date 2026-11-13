R10-OUTSIDE-DHW-START-HYSTERESIS: the pump's own start condition as an optional input per duty, rebuilt on main from the prototype in outside pull request 3440 (Bankaifan, fork head cbbd14e006). Dispatched design-exempt; the forks a design note would have decided are decided here, each with its measurement.

**Round 2: the answer to `Fix review: blocked 1884d3885f48531106e58e23f7177f87f991c87b architecture-unsound` (refs/heads/verdict/3531).**

1. *One concept, two owners.* `thermal_model.dhw_step_target_c` is now the one statement of the two values and the two bounds, and `pump_arbiter._dhw_write` reads it: `_dhw_write` is `_dhw_target` where the entity has a state, and `_dhw_target` is `dhw_step_target_c(params, cycle, grid)`. The check `_dhw_write states no value and no bound of its own` reads the function's syntax tree and refuses any of the four parameter names in it; `the arbiter's hot-water write is dhw_step_target_c on the entity's grid` compares the two over 4 step sizes, 5 set-points, 4 disinfection temperatures, the cycle on and off and the three bookings. The reviewer's O3 and O4 are M32 and M33 here, killed by 10 and 4 checks. Alternatives that lost: the planner calling the arbiter (a model module importing the Home Assistant glue, step 17's second bullet); the written targets copied onto the state each cycle (a second copy of a function of the parameters, stale for any solve run on other parameters).
2. *The plan judges against what is written.* The owner takes the set-point entity's grid, `inputs.SetpointGrid` (unit, step and range as plain values; `quantise_setpoint_c` and the arbiter's `_bounded` are now its two methods, the arithmetic moved line for line), and `inputs.read_start_hysteresis` puts it on `ThermalState.dhw_setpoint_grid` beside the hysteresis, so `dhw_planner.dhw_start_temps`, the ledger and the notice all quantise as the write does. Measured, not argued: the harness gained `--setpoint` and `--step`, and an everyday 58 on a 5 °C step (written 55) with 4 K left 13 of 57 planned runs beginning at or above 51 °C at the round-1 head and leaves 0 of 63 at this one (Figures).
3. *The notice on an install with hot water disabled.* `setpoint_check._dhw_start` is gated on `params.dhw_enabled`; the check `with hot water disabled no minimum raises it, whatever the hysteresis reads` is the reviewer's case (20 K, minimum 45), with the enabled twin raising as its control. M31.
4. *O2.* The `| on` term is deleted, on a measurement: it is reachable (57 cells over the 18 solves at 4 K where it alone made a step startable, 53 of them step 0) and it is harmful. The step-0 cells change no plan (variants b and c below print the same `plan_sha1` at 1, 2, 4, 6 and 10 K), and the later cells are steps of a charge the next round drops, where the repair bought heat for nothing: at 1 K the term left 741.05 K·steps under the minimum against 727.48 without it. The same defect sat in the neighbouring term (the step after any charging step, O1's line), so `startable_steps` now carries a charge on only where it is under way: from a step that opens below its start temperature, or from the first step; 708.95 at 1 K and 798.83 against 802.66 at 2 K, the other three unchanged (Figures). M35, M36, M37 and M42 pin the rule; M42 is the deleted term put back.

**Hot water, plan around (not actuate).** With `dhw_hysteresis_entity` read, `dhw_planner.place_startable` drops, in time order, each charge that begins on a tank at or above its step's start temperature, and `_repair_dhw_floor` re-buys what the floor still needs only on `startable_steps`. The step's start temperature is the target the arbiter writes on that step less the hysteresis (`thermal_model.dhw_step_target_c`, `dhw_start_below_c`): the disinfection temperature on the cycle's step, the everyday target elsewhere, each on the entity's step. Actuating instead (writing a target that starts the charge) was refused on the measurement `write_to_start_max_c` below: the unstartable runs would need a set-point above the user's charge limit, which the write exists not to exceed.

**Feasibility.** A hot-water minimum above the start temperature cannot be held by such a pump; the plan then shows the tank under it and `setpoint_check._dhw_start` raises `dhw_minimum_above_start` (strings, en, de, sv; README names it), with hot water enabled only.

**Heating.** `thermal_model.start_flow_min_lift_k` is the floor's one lift: the configured lift, never below `space_hysteresis_entity`. `pump_arbiter._flow_target` reads it and nothing else reads `configured_flow_min_lift_k` (census check in `tests/block_duty.py`).

**One input family.** `inputs.read_temperature_delta_k` reads a temperature difference (K and °C as they stand, °F scaled by 5/9, outside 0 to 20 K no reading); `inputs.read_start_hysteresis` puts both on the cycle's `ThermalState`. An install that has only the absolute start threshold (a Luxtronik's Demand border, input 10107) serves the same option with a template sensor of the return target minus the threshold (docs/configuration.md, the option's description); no second start option is needed.

**Deviations from the prototype, each with its reason.**
- Post-pass drop replaced by placement under the start condition with a re-buy: the feature-triage ruling in the brief, and measured (`floor_deficit_k_steps`, mutant M4 below).
- A run is judged against its own step's target, with no exemption for the run holding the disinfection step: the brief's ruling.
- The start temperature is the written target less the hysteresis, the entity's step and bounds included, in the plan, the ledger and the notice, not the configured set-point.
- The lift's owner sits in `thermal_model.py`, not at one call site in the arbiter: the brief's ruling. The author's stated limit (the plan's modulation floor prices the configured lift) describes nothing at this base: no module but `pump_arbiter.py` reads a floor lift, and the plan prices the floor step at the band's minimum power whatever lift is written.
- The reader refuses a unit outside the temperature family (the prototype took any unit as it stood) and takes a unit-less number as K; a hysteresis of 0 is no start condition (the product rule: 0 equals unset).
- A new top-up is not placed at step 0 on a warm tank; an existing run at step 0 is kept, as the prototype keeps it, and the step behind it continues it.
- Both options are read once per cycle onto the state by `inputs.py`; the prototype read the heating one inside the arbiter.
- The structure ratchet is paid by code, not by rewrapping comments: `DhwPlanner._ctx_clamp` folds the clamp-then-zero idiom three sites repeated, `_ctx_temps` two tank simulations; `class_excess_loc` is re-recorded down (commits `f10a662460`, `e32a306431`, and this round's one line).

Kept from the prototype: the two option keys, the step-0 rule, the ledger's `not-startable` verdict, the card labels.

Carry 0 (from r10-duty-switch-planner-price: a group adding its own start ban ORs into the placement-ban channel `_with_placement_ban` beside `forced_off` in `_build_dhw_requirements` and adds no parameter) is not taken as written, on two grounds. `git grep _with_placement_ban` over `custom_components` and `tests` prints nothing at this head or at origin/main caacd43b4e, so there is no channel in the tree to OR into. And the start condition is not a step mask known before placement: whether a step starts the pump depends on the tank trajectory under the plan being built, which every top-up changes (repair_rounds_max under Figures). It is read inside the repair's own round (`startable_steps` on that round's trajectory) and handed in as one keyword, `start_below`, only when a hysteresis is read. `forced_off` and what it means are untouched, so that channel can land beside it without meeting this one.

The reviewer's non-blocking findings, each answered:
- No design note exists for this size-L group, so step 15 had none to compare against. The dispatch was design-exempt by the orchestrator, who holds that record; this seat cannot write it into the tree and built against the brief's four forks. Carry: dismissed: the orchestrator dispatched it design-exempt and holds that record
- The brief's plan-prices-the-written-lift test is a census check here. No plan-side reader of a floor lift exists at this head (`git grep -n -E 'start_flow_min_lift_k|configured_flow_min_lift_k|modulation_floor_flow_c' -- custom_components` names `pump_arbiter.py` and the owner `thermal_model.py` only), so there is no price to compare; the census check fails the day a second reader appears. Carry: dismissed: no plan-side reader of a floor lift exists to test, and the census check fails the day one is added
- The harness is the builder's, and its 18 solves hold no disinfection cycle placed after step 0, so the cycle-step rule is proven at unit level only (M8, M18, M21, and on a stepped entity the 56 °C cycle step of `on a stepped entity each step's start temperature is the written target less the hysteresis`). No finder harness exists for an outside request; the limit stands as disclosed. Carry: dismissed: disclosed limit of the instrument, the unit checks kill the cycle-step mutants

Closes nothing by keyword.

## Head

356511ac9d92afa11f7e1d0dc6580000bbf759b6

Resumed from refs/pull/3531/head feb0f3f42c3dc538a4a259fdcdbcf2b9fede011c (the round-1 handoff 1884d3885f merged with main, the delivery row, and the bot's `ci: re-record closures` and `ci: pin killed mutants`). The pull request's branch moved during the round (`ci: merge main`, a06dc2fe68), so the head is this round's last code commit 497c8133f5 merged with it, never rebased; merge base bc58019d01b3072e02bfd30cdf052dd715f2945c, origin/main caacd43b4ee1b1ce849fbc92590e0b2191e6c02c when taken, `git merge-tree --write-tree origin/main HEAD` exits 0. Every figure below was taken or re-taken at this head unless it names another.

## Mutation proof

Failing first: commit `0357bbf34a` holds this round's checks before the code; `PYTHONPATH=tests/hastub python3 tests/block_duty.py` there printed `11 of 149 BLOCK DUTY CHECKS FAILED` (the owner tie, the syntax-tree check, the grid, the stepped planner and its end-to-end solve, the disabled notice, the stepped notice, the state's grid), and the three under-way checks failed against the round-1 `startable_steps` before its rewrite (`3 of 152`); the floor check of `SetpointGrid.bounded` was added on a survivor (below).

`python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py <worktree at the head>` applies each mutant to a worktree, runs `tests/block_duty.py` and restores. At the head M1 to M43 are KILLED (43 lines), none prints ANCHOR, and the null one SURVIVED. Changed or new this round:

- M5 `startable_steps` `<` to `<=`: `a tank exactly at the start temperature, not charging, does not start`
- M8 the cycle step judged against the everyday target: `each step's start temperature is its own target less the hysteresis, the cycle step the cycle's`
- M13 the planner ignores the hysteresis: `with a 4 K hysteresis no planned charge after step 0 begins at or above 51 degC`
- M14 the ledger's start ignores the written target: `the ledger's start temperature on the stepped entity is the planner's`
- M23 no step is a cycle step for the write or the ledger: `a commanded or held disinfection cycle writes its temperature, not the configured set-point` and 14 more
- M25 the notice judges the cycle's target: `the start temperature is the everyday target's even with a disinfection cycle active`
- M28 the write and the ledger ignore the entity's grid: `an off-step disinfection temperature above the everyday set-point is written on the step at or below it, never above the tank's hard maximum` and 9 more
- M29 the planner ignores the entity's grid: `on a stepped entity each step's start temperature is the written target less the hysteresis`, `handed the 5 degC entity's grid, no planned charge after step 0 begins at or above 51 degC`
- M30 the notice ignores the entity's grid: `the notice judges the written target: an everyday 58 on a 5 degC step starts below 51, not 54`
- M31 the notice is raised with hot water disabled: `with hot water disabled no minimum raises it, whatever the hysteresis reads`
- M32 the everyday target ignores the charge limit (the reviewer's O3): 10 checks, among them `no no-cycle write exceeds the charge limit (dhw_max_temp), the cycle enabled and not running or disabled, over every step size and everyday set-point on and off the step`
- M33 the cycle's target ignores the hard maximum (O4): 4 checks, among them `the cycle's step target never exceeds the tank's hard maximum (70 over a 72 disinfection temperature)`
- M34 the input read leaves the grid off the state: `the coordinator's input read puts the hot-water set-point entity's grid into the state` and the two M29 names
- M35 the step after a charge the pump would not start is startable: `a charge begun after the first step on a warm tank is one the pump does not start: neither its steps nor the step after it are startable`
- M36 a charge at the first step carries nothing on, and M42 the deleted `| on` term put back at step 0 (O2): `the step after a charge kept at the first step continues it; the kept step itself is not added to`
- M37 no charge under way carries on (O1): `a step is startable where it opens on a tank below its start temperature or follows a charge under way`
- M38 an entity with no state has a grid: `a set-point entity with no state has no grid, and the target is then the one before any step`
- M39 with no entity the target ignores its bound: `the everyday step target never exceeds the charge limit (dhw_max_temp, 70 over a 72 set-point)`
- M40 the hot-water write goes to an entity with no state: `null control: no hot-water set-point entity is no hot-water write on any row`
- M41 the bound is handed to the grid as the value's own: `a charge limit below the entity's minimum writes the entity's minimum, never a value it refuses`
- M43 the notice is never raised (O14): `a minimum above the start temperature raises dhw_minimum_above_start with its figures`

Unchanged from round 1 and re-run at this head:

- M1 the lift owner returns the configured lift: `a heating hysteresis above the configured lift is the lift`, `a heating hysteresis above the lift moves the floor write to return + hysteresis`
- M2 `drop_unstartable` `>=` to `>`: `a tank exactly at the start temperature does not start`
- M3 the ledger's not-startable branch removed: `an idle hot water step on a tank above the start temperature is not-startable` and the exactly-at check
- M4 the repair places without the start mask: `what the start condition bars is re-bought where the pump starts: the tank is no further under its minimum with a 4 K hysteresis than with none`
- M6 a zero hysteresis is a start condition: `no target, or a hysteresis that is missing, zero or negative, is no start temperature`, `with no or zero hysteresis no step has a start temperature`
- M7 the difference reader ignores the unit's scale: `a hysteresis in degF is scaled by 5/9, not offset`
- M9 the notice at a minimum equal to the start temperature: `a minimum exactly at the start temperature raises nothing`
- M10 `place_startable` returns without the final drop: `a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds`
- M11 the coordinator does not read the options: `the coordinator's input read puts both hysteresis sensors into the state`
- M12 the floor write ignores the hysteresis: `a heating hysteresis above the lift moves the floor write to return + hysteresis`
- M15 the reader accepts above the maximum: `a hysteresis outside 0 to 20 K, unavailable, in a non-temperature unit, unset or unknown is no reading`
- M16 a run at step 0 is judged too: `a run at the first step is kept on a warm tank, with nothing planned at the horizon's end`
- M17 the round bound is nine: `a repair that never settles is asked the documented eight rounds, and what leaves still holds no unstartable charge`
- M18 a cycle on the first step is not a cycle step, and M21 a cycle past the horizon is written: `a cycle on the first step is judged against its own target; one past the horizon moves no step`
- M19 a run at the second step is not judged: `a run that begins at the second step on a warm tank is dropped`
- M20 the loop never ends early: `a repair that changes nothing ends the loop: one round to drop, one to see the plan stand`
- M22 the shared clamp zeroes a step on the runnable block: `a step the capacity clamp leaves below a runnable block is zeroed; one on the block, to the 1e-9 the rule allows, is kept`
- M24 the set-point check never reaches the start notice: `the set-point check's own entry raises it: evaluate() reaches the start notice`
- M26 a hysteresis under one kelvin is none: `a hysteresis under one kelvin is still a start condition`
- M27 pinned hot water is not held to the tank's capacity: `a day with hot water pinned on at every step is still held to the tank's charge limit of 55 degC`
- NULL a comment-only change: SURVIVED, 0 failing.

The reviewer's own driver, `python3 ev/reviewer_own_mutants.py <worktree at the head>` from refs/heads/probe/revt-r10-outside-dhw-start-hysteresis-97f1be7f, run unedited: O5 to O13 and O15 KILLED, NULL SURVIVED, no SURVIVED line among O1 to O15. Five print `ANCHOR x0` because this round rewrote their lines; each has its mutant on the new line in the tracked driver: O1 is M37, O2 is M42 (the term is gone; M42 restores it), O3 is M32, O4 is M33, O14 is M43.

## Unpinned sites

Each is an added production line the committed ledger cannot yet name (`python3 tools/pr/ci_predict.py`, the ADDED UNPINNED lines). `tests/block_duty.py` drives every function they sit in, and the lane pins what it kills after the push. The 16 pins `ci_predict.py` named STALE PIN (lines this round rewrote, among them main's pins on `quantise_setpoint_c` and `_bounded`, whose bodies moved onto `SetpointGrid`) are deleted in commit `63cc533d77`, as its repair line says.

- `custom_components/heatpump_optimizer/dhw_planner.py:207 CONST`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:228 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:247 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:250 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:254 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:269 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:272 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:276 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:516 CONST`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:644 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:645 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:646 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:647 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:649 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:666 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:672 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:672 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:672 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:690 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:692 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:705 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:593 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:595 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:600 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1181 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1193 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1685 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1700 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1702 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/setpoint_check.py:122 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1891 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1919 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1920 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1921 RETURN_DEL`: pinned by mutation-autofix

Survivors. `tools/audit/seat/mutant_run.py --diff feb0f3f42c3dc538a4a259fdcdbcf2b9fede011c...HEAD --path custom_components --cmd "env PYTHONPATH=tests/hastub python3 tests/block_duty.py" --max-mutants 400 --report-only`, every mutant of the production lines this round added or changed, lists 57 mutants at 497c8133f5. At 63cc533d77 it printed two SURVIVED lines, both statement deletions inside `SetpointGrid.bounded` of lines moved unchanged from main's `_bounded`, and both also survived `tests/features.py` (`ALL 5362 FEATURE CHECKS PASSED` under each). Both are answered in the tree, and at 497c8133f5, the last commit that touches production code, the same command prints no SURVIVED line:

- the clamp to the caller's floor (`value = max(value, floor, ...)`): a killing check, `a grid holds a write at its caller's floor, which is no part of the entity's range, and at the entity's minimum where that is higher`; with the statement replaced by `pass`, `tests/block_duty.py` prints `1 of 153 BLOCK DUTY CHECKS FAILED`.
- the clamp to the entity's maximum (`value = min(value, high) ...`): dead code, deleted (commit `497c8133f5`). The step's own ceiling always holds the entity's maximum, rounded down, and takes the lower, so clamping the value first changed no result; a scratch comparison of `bounded` with and without the line over 974592 cases (three units, four steps, three minima, four maxima, 94 values, three roundings, three floors, two `lo`, four `hi`) printed `differing=0`. Not in the tree: a one-off whose subject is gone.

`prepr.sh`'s own draw (the first 40 mutants of the whole diff, `MUTANT_CMD="env PYTHONPATH=tests/hastub timeout 150 python3 tests/block_duty.py"`; the `timeout` because one drawn mutant of `drop_unstartable`'s loop never returns, which without it held the step past its limit, and a run that never ends is a kill) leaves three survivors, the three round 1 answered. They sit outside every planner script and die in `tests/config_flow_steps.py`, each re-run at this head with the statement replaced by `pass`:

- `custom_components/heatpump_optimizer/const.py:1046 STMT_DEL`: a value check, `tests/config_flow_steps.py` exits 1 on `ImportError: cannot import name 'CONF_SPACE_HYSTERESIS_ENTITY'`
- `custom_components/heatpump_optimizer/const.py:1047 STMT_DEL`: a value check, the same script exits 1 on `ImportError: cannot import name 'CONF_DHW_HYSTERESIS_ENTITY'`
- `custom_components/heatpump_optimizer/config_flow.py:1676 STMT_DEL`: a value check, the same script exits 1 on `NameError: name '_OPTION_FIELDS' is not defined`

The round-1 account of the other survivors of the whole diff stands for the lines this round did not touch.

## Null control

With neither option set, and with a hysteresis of 0, the 18 solves print the `plan_sha1` the merge-base export prints, on the default set-point and on 58 with a 5 °C step alike (Figures); `tests/env_drift.py --all` against the merge base reads every plan fixture byte-identical, the one fixture that moves being the float-free `config_flow`, which gains the two pickers and is claimed in `tests/golden/claimed_drift.txt`. With neither option set `_repair_dhw_floor` is called with main's arguments (`place_startable` hands it the start condition only when there is one), `start_flow_min_lift_k` returns `configured_flow_min_lift_k`, and a ledger row's `start_below` is `None`, so `_missed` returns the verdict main returned. The write itself is main's arithmetic through one more call: the checks of `disinfection_checks` (main's, on the written value over every step size) pass unedited (the gate's `tests/features.py` too), and what ties the write to the owner is M28, M32, M33 and M41.

## Figures

`$MB` is `git archive bc58019d01b3072e02bfd30cdf052dd715f2945c | tar -x -C $MB`, the merge base, and `$R1` the same of feb0f3f42c3dc538a4a259fdcdbcf2b9fede011c, the round-1 code; the harness is `dev/audit/harnesses/r10_dhw_start_hysteresis.py` at this head (sha1 a63a75b7251f97638e8ae3128859489a04c7aac8), run with `PYTHONPATH=tests/hastub` from the tree it measures, each figure a sum over its 18 solves by the rule in its header.

- Before, `python3 $H $MB`: runs_not_at_step0=114, runs_at_or_above_minus_2k=53, runs_at_or_above_minus_4k=64, runs_at_or_above_minus_6k=65, kwh_planned=97.28, kwh_at_or_above_minus_4k=12.63, write_to_start_max_c=58.9, floor_deficit_k_steps=805.30, dhw_cost=120.13, plan_sha1=4743e9638f485f3087887be84ff951ce2886cb21.
- Null at the head, `python3 $H .` and the same with `--hysteresis 0`: plan_sha1=4743e9638f485f3087887be84ff951ce2886cb21 both. It would have differed had either path touched a plan: `--hysteresis 2` prints cae511be1ac4be5dc533130ab134cc51037cc81c.
- After, `--hysteresis 4`: runs_not_at_step0=84, runs_at_or_above_minus_4k=0, kwh_planned=97.39, kwh_at_or_above_minus_4k=0.00, floor_deficit_k_steps=751.01, dhw_cost=122.35, plan_sha1=be1691057cf9e80ad2ba54a659addd10556493bc (round 1: c79ab9ed608a with the same six figures; the plans differ in steps of charges the term topped up and the next round dropped). The control for the 0: the same command on `$MB` prints `hysteresis=unsupported` and 64.
- After, `--hysteresis 2`: runs_at_or_above_minus_2k=0 (53 before), floor_deficit_k_steps=798.83 (round 1: 802.66), dhw_cost=120.85 (120.81).
- After, `--hysteresis 1`: floor_deficit_k_steps=708.95, dhw_cost=120.84, repair_rounds_max=4 of 28; `$R1`, its own harness copy, same flag: 741.05, 120.65, 5 of 28.
- Block item 2, an everyday 58 on a 5 °C step, `--hysteresis 4 --setpoint 58 --step 5` (written=55, counts against 55 less K): at `$R1`, which prints `step=5 unsupported`, runs_not_at_step0=57, runs_at_or_above_minus_4k=13, kwh_at_or_above_minus_4k=8.40 of 105.50, plan_sha1=0f77b29016e3; at the head 63, 0, 0.00 of 104.85, plan_sha1=1fc6f15033a6. floor_deficit_k_steps is 389.46 at `$R1` and 425.11 at the head: judged against 55 the pump starts 3 K later than the round-1 plan assumed, and the plan now shows the sag it had hidden. Control that the grid is what moved it: the head with `--setpoint 58` and no `--step` prints the `$R1` plan, 0f77b29016e3. Null on this arm: the head with `--setpoint 58 --step 5` and no hysteresis, the same with `--hysteresis 0`, and `$MB` all print plan_sha1=c880bcc82f43.
- Block item 4, the rule's variants, a scratch probe that replaces `dhw_planner.startable_steps` under the same harness (not in the tree: a one-off, step 18), floor_deficit_k_steps at 1, 2, 4, 6, 10 K: (a) round 1's rule 741.05, 802.66, 751.01, 733.54, 870.55; (b) without `| on` 727.48, 802.66, 751.01, 733.54, 870.55; (c) `on` at step 0 only: (b)'s five `plan_sha1`; (d) the rule built 708.95, 798.83, 751.01, 733.54, 870.55. The count of cells where `| on` alone decided, same probe at round 1's rule: 57 at 4 K (53 at step 0), 156 at 1 K (0 at step 0).
- The round bound: repair_rounds_max=3 of 26 placements at 4 K, 3 of 28 at 2 K, 4 of 28 at 1 K, none with no hysteresis; `STARTABLE_ROUNDS` is 8.
- The re-buy, mutant M4 applied to a worktree and `--hysteresis 4` run there: floor_deficit_k_steps=2180.74, kwh_planned=87.22 (751.01 and 97.39 with the mask).
- The seams of block item 1 (step 8: the property, every statement or reader of the hot-water target on the pump, not the instance), `git grep -n -E 'dhw_step_target_c\(|"dhw_setpoint"|dhw_start_below_c\(' -- 'custom_components/heatpump_optimizer/*.py'` and `git grep -n -E 'dhw_hard_max_temp|dhw_max_temp' -- custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/setpoint_check.py custom_components/heatpump_optimizer/inputs.py`: `pump_arbiter._dhw_write` and `_dhw_target` (closed in this diff: read the owner), `dhw_planner.dhw_start_temps` (closed: reads it on the state's grid), `pump_arbiter._dhw_start_below_c` (closed: `_dhw_target`), `setpoint_check._dhw_start` (closed: reads it on the entity's grid), `pump_arbiter.desired`'s space-only row (`DHW_GATE_C`: the gate that keeps the tank thermostat off, not a target, main's and untouched), `setpoint_check._dhw` (the disinfection floor's repair bounded by `dhw_hard_max_temp`: main's, already guarded by `the hot-water repair's Fix never exceeds the tank's hard maximum it is judged against`). The second command prints `setpoint_check._dhw`'s two lines and nothing in `pump_arbiter.py`: the arbiter names neither bound. The other hits are the option key, the write slot's name and published attributes.
- Fixture drift, `python3 tests/env_drift.py --all bc58019d01b3072e02bfd30cdf052dd715f2945c`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s)`.
- `python3 tools/audit/archscore/score.py --diff bc58019d01b3072e02bfd30cdf052dd715f2945c`: dS +0.0000 NULL; the same against feb0f3f42c: dS +0.0000 NULL.
- `python3 tests/structure.py`: passes; `class_excess_loc` re-recorded 17516 to 17515 this round (17526 at the merge base of round 1), `name_kept_members` unmoved at 38 (the untyped read of `SetpointGrid.bounded` it first counted is typed), no other row moved.
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py`: 153 checks pass (134 at round 1).
- The scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=bc58019d01b3072e02bfd30cdf052dd715f2945c ./tests/run.sh` first at fdf0b9911f: every script the scope names passed but `tests/entities.py`, 1 of 2709, `the lane's docstring records those measured numbers as the selection-cost note (#1218)`: the note in `tests/deployment_shape.py` said 148 pairs and the closures the bot re-recorded on this branch give 154 (`tests/block_duty.py`'s closure, 72 to 89 production files, since its coordinator check). The note is corrected in this diff; `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` then prints `ALL 2709 ENTITY CHECKS PASSED`. Run again on the merged head: `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, exit 0, `tests/stress.py` and `tests/entities.py` among the 32. (A run at 497c8133f5 before the merge had passed every lane when the container restarted inside `tests/stress.py`; that script and `tests/harness_headers.py` were then run alone there and passed.)

The brief's gap figures were taken at a7628041dc (54, 64, 65 of 114; 12.60 of 86.34 kWh); the Before line is the same rule re-measured at this merge base.

<!-- figure-block: scope-line mb=bc58019d01b3072e02bfd30cdf052dd715f2945c head=356511ac9d92afa11f7e1d0dc6580000bbf759b6 -->
~~~text
MODE: SCOPED -- 30 script(s) run, 3 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

Architecture score: dS +0.0000 NULL

## Red checks

- `tests / mutation` at 356511ac9d92: red by construction on the 34 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.
- `tests / closures`: red on the pull request at a head before this one; `prepr.sh` step 7 read it, and this seat read no CI log (the dispatch's quota rule), so the kind is inferred from the branch: the bot's `ci: re-record closures` (a35771fab0) followed the round-1 push and re-recorded `tests/block_duty.py`'s closure from 72 to 89 production files, which is `UNDER-SCOPED` and its autofix (`ci-autofix.md`). Cheaper detector: none exists here. `prepr.sh` step 6b prints `the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden`, and `tools/pr/ci_predict.py` at this head prints `no closures, fast, governance or instrument red predicted`.
- `tests / fast (3.14)`: red in the branch's ancestry; `prepr.sh`'s ancestry arm names it, and this seat read no CI log (the dispatch's quota rule), so the failure is the one reproduced here: at fdf0b9911f, whose `tests/closures.json` and `tests/deployment_shape.py` are feb0f3f42c's, `tests/entities.py` fails 1 of 2709, `the lane's docstring records those measured numbers as the selection-cost note (#1218)` (the note said 148 pairs, the bot's re-recorded closures give 154). Fixed in this diff (commit 9dce06c392); `tests/entities.py` passes at this head. Cheaper detector: the check is a count over `tests/closures.json` against one docstring and runs in under a second, but the commit that turned it was the bot's `ci: re-record closures`, pushed after the fixer's handoff, so no fixer-side run could have seen it; the place for it is the `closures-autofix` job, re-running that one check on what it re-records, at under a second per autofix run. Not built here: a workflow change is outside this group's files.
- `tests / nightly-ha (2025.2.0)`, `tests / nightly-ha (stable)`, `tests / nightly-status`: red in the ancestry; they grade `main` and are the orchestrator's there (`defect-root-cause.md`, Enforcement), outside the owed set and not this branch's.

## Forward-carry

- No module but `pump_arbiter.py` reads a floor lift (`tests/block_duty.py`, the census check "configured_flow_min_lift_k is referenced by no module but its owner"), so there is no plan-side price of the lift for this group to move: the plan books a floor step at the solve band's minimum power, and a heating hysteresis above the configured lift raises only the write. Carry: dismissed: no later stage is narrowed; a plan-side price of the written lift would be a new model term, which no roster group plans
- `drop_unstartable` judges a run by its first step alone: a run that begins on a warm tank and has a later step opening below the start temperature is dropped whole, though the pump would start it there. It errs toward dropping, the repair re-buys on `startable_steps`, and the 18 solves at 1, 2, 4, 6 and 10 K and the stepped arm leave no planned run after step 0 at or above its start temperature (`runs_at_or_above_minus_4k=0` at 4 K, `_2k=0` at 2 K), so nothing was measured that a later stage must work around. Carry: dismissed: argued from `dev/audit/harnesses/r10_dhw_start_hysteresis.py`'s rule, no measured loss; an unmeasured observation is not carried

## Friction

none
