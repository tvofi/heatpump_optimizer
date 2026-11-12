R10-OUTSIDE-DHW-START-HYSTERESIS: the pump's own start condition as an optional input per duty, rebuilt on main from the prototype in outside pull request 3440 (Bankaifan, fork head cbbd14e006). Dispatched design-exempt; the forks a design note would have decided are decided here, each with its measurement.

**Hot water, plan around (not actuate).** With `dhw_hysteresis_entity` read, `dhw_planner.place_startable` drops, in time order, each charge that begins on a tank at or above its step's start temperature, and `_repair_dhw_floor` re-buys what the floor still needs only on `startable_steps` (a tank below the start temperature, a step already charging, the step after one). The step's start temperature is the target the arbiter holds on that step less the hysteresis (`thermal_model.dhw_step_target_c`, `dhw_start_below_c`): the disinfection temperature on the cycle's step, the everyday target elsewhere. Actuating instead (writing a target that starts the charge) was refused on the measurement `write_to_start_max_c` below: the unstartable runs would need a set-point above the user's charge limit, which `pump_arbiter._dhw_write` exists not to exceed.

**Feasibility.** A hot-water minimum above the start temperature cannot be held by such a pump; the plan then shows the tank under it and `setpoint_check._dhw_start` raises `dhw_minimum_above_start` (strings, en, de, sv; README names it).

**Heating.** `thermal_model.start_flow_min_lift_k` is the floor's one lift: the configured lift, never below `space_hysteresis_entity`. `pump_arbiter._flow_target` reads it and nothing else reads `configured_flow_min_lift_k` (census check in `tests/block_duty.py`).

**One input family.** `inputs.read_temperature_delta_k` reads a temperature difference (K and °C as they stand, °F scaled by 5/9, outside 0 to 20 K no reading); `inputs.read_start_hysteresis` puts both on the cycle's `ThermalState`. An install that has only the absolute start threshold (a Luxtronik's Demand border, input 10107) serves the same option with a template sensor of the return target minus the threshold (docs/configuration.md, the option's description); no second start option is needed.

**Deviations from the prototype, each with its reason.**
- Post-pass drop replaced by placement under the start condition with a re-buy: the feature-triage ruling in the brief, and measured (`floor_deficit_k_steps`, mutant M4 below: without the start mask in the repair the 18 solves leave 2180.74 K·steps under the minimum against 751.01 with it).
- A run is judged against its own step's target, with no exemption for the run holding the disinfection step: the brief's ruling.
- The start temperature is the written target less the hysteresis (`_dhw_write`, the entity's step and bounds included) in the ledger, not the configured set-point.
- The lift's owner sits in `thermal_model.py`, not at one call site in the arbiter: the brief's ruling. The author's stated limit (the plan's modulation floor prices the configured lift) describes nothing at this base: no module but `pump_arbiter.py` reads a floor lift, and the plan prices the floor step at the band's minimum power whatever lift is written.
- The reader refuses a unit outside the temperature family (the prototype took any unit as it stood) and takes a unit-less number as K; a hysteresis of 0 is no start condition (the product rule: 0 equals unset).
- A new top-up is not placed at step 0 on a warm tank; an existing run at step 0 is kept, as the prototype keeps it.
- Both options are read once per cycle onto the state by `inputs.py`; the prototype read the heating one inside the arbiter.
- The structure ratchet is paid by code, not by rewrapping comments: `DhwPlanner._ctx_clamp` folds the clamp-then-zero idiom three sites repeated, `_ctx_temps` two tank simulations; `class_excess_loc` is re-recorded down (commits `f10a662460`, `e32a306431`).

Kept from the prototype: the two option keys, the step-0 rule, the ledger's `not-startable` verdict, the card labels.

Carry 0 (from r10-duty-switch-planner-price: a group adding its own start ban ORs into the placement-ban channel `_with_placement_ban` beside `forced_off` in `_build_dhw_requirements` and adds no parameter) is not taken as written, on two grounds. `git grep _with_placement_ban` over `custom_components` and `tests` prints nothing at this head or at origin/main f44e761c19, so there is no channel in the tree to OR into. And the start condition is not a step mask known before placement: whether a step starts the pump depends on the tank trajectory under the plan being built, which every top-up changes (repair_rounds_max under Figures: a placement needs up to three rounds). It is read inside the repair's own round (`startable_steps` on that round's trajectory) and handed in as one keyword, `start_below`, only when a hysteresis is read. `forced_off` and what it means are untouched, so that channel can land beside it without meeting this one.

Closes nothing by keyword.

## Head

1884d3885f48531106e58e23f7177f87f991c87b

## Mutation proof

`python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py <worktree at the head>` applies each mutant to a worktree, runs `tests/block_duty.py` and restores. At the head every named mutant is KILLED and the null one SURVIVED:

- M1 the lift owner returns the configured lift: `a heating hysteresis above the configured lift is the lift`, `a heating hysteresis above the lift moves the floor write to return + hysteresis`
- M2 `drop_unstartable` `>=` to `>`: `a tank exactly at the start temperature does not start`
- M3 the ledger's not-startable branch removed: `an idle hot water step on a tank above the start temperature is not-startable` and the exactly-at check
- M4 the repair places without the start mask: `what the start condition bars is re-bought where the pump starts: the tank is no further under its minimum with a 4 K hysteresis than with none`
- M5 `startable_steps` `<` to `<=`: `a tank exactly at the start temperature, not charging, does not start`
- M6 a zero hysteresis is a start condition: `no target, or a hysteresis that is missing, zero or negative, is no start temperature`, `with no or zero hysteresis no step has a start temperature`
- M7 the difference reader ignores the unit's scale: `a hysteresis in degF is scaled by 5/9, not offset`
- M8 the cycle step judged against the everyday target: `each step's start temperature is its own target less the hysteresis, the cycle step the cycle's`
- M9 the notice at a minimum equal to the start temperature: `a minimum exactly at the start temperature raises nothing`
- M10 `place_startable` returns without the final drop: `a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds`
- M11 the coordinator does not read the options: `the coordinator's input read puts both hysteresis sensors into the state`
- M12 the floor write ignores the hysteresis: `a heating hysteresis above the lift moves the floor write to return + hysteresis`
- M13 the planner ignores the hysteresis: `with a 4 K hysteresis no planned charge after step 0 begins at or above 51 degC`
- M14 the ledger's start ignores the written target: `the ledger's start temperature on a booked cycle step is the cycle's less the hysteresis`
- M15 the reader accepts above the maximum: `a hysteresis outside 0 to 20 K, unavailable, in a non-temperature unit, unset or unknown is no reading`
- M16 a run at step 0 is judged too: `a run at the first step is kept on a warm tank, with nothing planned at the horizon's end`
- M17 the round bound is nine: `a repair that never settles is asked the documented eight rounds, and what leaves still holds no unstartable charge`
- M18 a cycle on the first step is not a cycle step, and M21 a cycle past the horizon is written: `a cycle on the first step is judged against its own target; one past the horizon moves no step`
- M19 a run at the second step is not judged: `a run that begins at the second step on a warm tank is dropped`
- M20 the loop never ends early: `a repair that changes nothing ends the loop: one round to drop, one to see the plan stand`
- M22 the shared clamp zeroes a step on the runnable block: `a step the capacity clamp leaves below a runnable block is zeroed; one on the block, to the 1e-9 the rule allows, is kept`
- M23 the ledger's fallback target is unset: `with no set-point entity to write, the ledger's start is the plan step's target less the hysteresis`
- M24 the set-point check never reaches the start notice: `the set-point check's own entry raises it: evaluate() reaches the start notice`
- M25 the notice judges the cycle's target: `the start temperature is the everyday target's even with a disinfection cycle active`
- M26 a hysteresis under one kelvin is none: `a hysteresis under one kelvin is still a start condition`
- M27 pinned hot water is not held to the tank's capacity: `a day with hot water pinned on at every step is still held to the tank's charge limit of 55 degC`
- NULL a comment-only change: SURVIVED, 0 failing.

M4 and M16 survived the first test set and M17 to M27 answer the diff-mutant survivors listed under `## Unpinned sites`; the checks that kill them were added before the handoff.

## Unpinned sites

Each is an added production line the committed ledger cannot yet name. `tests/block_duty.py` drives every function they sit in (the named mutants above), and the lane pins what it kills after the push.

- `custom_components/heatpump_optimizer/dhw_planner.py:207 CONST`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:221 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:224 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:224 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:224 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:226 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:239 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:240 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:242 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:244 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:258 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:260 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:261 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:265 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:265 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:268 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:288 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:292 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:295 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:1703 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/dhw_planner.py:1703 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:516 CONST`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:532 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:535 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/inputs.py:535 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1703 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1718 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1718 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1723 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1725 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/setpoint_check.py:119 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/setpoint_check.py:119 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1891 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1891 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1904 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1905 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1906 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1906 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1919 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1919 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1921 RETURN_DEL`: pinned by mutation-autofix

Survivors. `prepr.sh` step 6c draws the first 40 mutants of the added lines, which here ends inside `dhw_planner.py`, so `tools/audit/seat/mutant_run.py --diff 43e95474559ca8e2188830f8775c1ddf52df964a...HEAD --cmd "env PYTHONPATH=tests/hastub python3 tests/block_duty.py" --max-mutants 400 --report-only` was run over the whole diff at 71d85feb3c as well. Against that one script the three runs left 23 survivors in all, answered as follows.

- Four sat on code that is gone: the on-mask cleared behind a dropped run, the floor on a horizon length that is never negative, the unit's unused zero in the difference reader (it takes the scale alone now), a `<=` against the configured lift that could not differ from `<` (the owner is a `max`).
- One sat on main's own ledger-row line, which this diff no longer touches (`start_below` is set beside it).
- Twelve have killing checks in `tests/block_duty.py`, under the named mutants M17 to M27 (M18 and M22 each answer two).
- Three are statement deletions of planner stages this diff folded onto `_ctx_clamp` and `_ctx_temps` and did not change; `tests/features.py`, run under each with the statement replaced by `pass`, exits 1: the clamp after the second greedy pass (8 checks fail, among them `the owner's 52/60 pair keeps the tank at or below the 52 °C limit on a day with no cycle due`), the clamp inside the floor repair (1 check), the repair's re-simulation (9 checks).
- Three are outside every planner script and die in `tests/config_flow_steps.py`, each run there with the statement replaced by `pass`:

- `custom_components/heatpump_optimizer/const.py:1046 STMT_DEL`: a value check, `tests/config_flow_steps.py` exits 1 on `ImportError: cannot import name 'CONF_SPACE_HYSTERESIS_ENTITY'`
- `custom_components/heatpump_optimizer/const.py:1047 STMT_DEL`: a value check, the same script exits 1 on `ImportError: cannot import name 'CONF_DHW_HYSTERESIS_ENTITY'`
- `custom_components/heatpump_optimizer/config_flow.py:1676 STMT_DEL`: a value check, the same script exits 1 on `NameError: name '_OPTION_FIELDS' is not defined`

## Null control

With neither option set, and with a hysteresis of 0, the 18 solves print the `plan_sha1` the merge-base export prints (Figures); `tests/env_drift.py --all` against the merge base reads every plan fixture byte-identical, the one fixture that moves being the float-free `config_flow`, which gains the two pickers and is claimed in `tests/golden/claimed_drift.txt`. With neither option set `_repair_dhw_floor` is called with main's arguments (`place_startable` hands it the start condition only when there is one), `start_flow_min_lift_k` returns `configured_flow_min_lift_k`, and a ledger row's `start_below` is `None`, so `_missed` returns the verdict main returned.

## Figures

`$EXPORT` is `git archive 43e95474559ca8e2188830f8775c1ddf52df964a custom_components tests/profiles.py tests/hastub | tar -x -C $EXPORT`, the merge base; the harness is `dev/audit/harnesses/r10_dhw_start_hysteresis.py`, run with `PYTHONPATH=tests/hastub`, each figure a sum over its 18 solves by the rule in its header.

- Before, `python3 dev/audit/harnesses/r10_dhw_start_hysteresis.py $EXPORT`: runs_not_at_step0=114, runs_at_or_above_minus_2k=53, runs_at_or_above_minus_4k=64, runs_at_or_above_minus_6k=65, kwh_planned=97.28, kwh_at_or_above_minus_4k=12.63, write_to_start_max_c=58.9, floor_deficit_k_steps=805.30, dhw_cost=120.13, plan_sha1=4743e9638f485f3087887be84ff951ce2886cb21.
- Null at the head, `python3 dev/audit/harnesses/r10_dhw_start_hysteresis.py` and the same with `--hysteresis 0`: plan_sha1=4743e9638f485f3087887be84ff951ce2886cb21 both. It would have differed had either path touched a plan: `--hysteresis 2` prints 38f9096b7098521743854d0d5c88804ff8e1e4aa.
- After, `python3 dev/audit/harnesses/r10_dhw_start_hysteresis.py --hysteresis 4`: runs_not_at_step0=84, runs_at_or_above_minus_4k=0, kwh_planned=97.39, kwh_at_or_above_minus_4k=0.00, floor_deficit_k_steps=751.01, dhw_cost=122.35, plan_sha1=c79ab9ed608aadbff5e3221f1d18ba3459af1e82. The control for the 0: the same command on `$EXPORT` prints `hysteresis=unsupported` and 64.
- After, `--hysteresis 2`: runs_at_or_above_minus_2k=0 (53 before), floor_deficit_k_steps=802.66, dhw_cost=120.81.
- The round bound, the same two commands: repair_rounds_max=3 of 26 placements at 4 K and 3 of 28 at 2 K, none with no hysteresis; `STARTABLE_ROUNDS` is 8.
- The re-buy, mutant M4 applied to a worktree and `--hysteresis 4` run there: floor_deficit_k_steps=2180.74, kwh_planned=87.22.
- Fixture drift, `python3 tests/env_drift.py --all 43e95474559ca8e2188830f8775c1ddf52df964a`: 56 fixtures compared, config_flow the only one that moves (6 leaves, each present on one side only and added at the head).
- `python3 tools/audit/archscore/score.py --diff 43e95474559ca8e2188830f8775c1ddf52df964a`: dS +0.0000 NULL.
- `python3 tests/structure.py`: passes; `class_excess_loc` re-recorded 17526 to 17516, no other row moved.
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py`: 134 checks, 64 of them this group's (`hysteresis_checks`).

The brief's gap figures were taken at a7628041dc (54, 64, 65 of 114; 12.60 of 86.34 kWh); the Before line is the same rule re-measured at this merge base.

<!-- figure-block: scope-line mb=43e95474559ca8e2188830f8775c1ddf52df964a head=1884d3885f48531106e58e23f7177f87f991c87b -->
~~~text
MODE: SCOPED -- 30 script(s) run, 3 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

Architecture score: dS +0.0000 NULL

## Red checks

- `mutation` at 1884d3885f48: red by construction on the 41 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

- No module but `pump_arbiter.py` reads a floor lift (`tests/block_duty.py`, the census check "configured_flow_min_lift_k is referenced by no module but its owner"), so there is no plan-side price of the lift for this group to move: the plan books a floor step at the solve band's minimum power, and a heating hysteresis above the configured lift raises only the write. Carry: dismissed: no later stage is narrowed; a plan-side price of the written lift would be a new model term, which no roster group plans

## Friction

none
