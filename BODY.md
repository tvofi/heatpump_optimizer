Part of #3616 (phase 2 of the owner's three; the issue stays open for phase 3)

R11-OUTSIDE-ROOMS-P2, built to the approved design `design/R11-OUTSIDE-ROOMS-P2` at `4784b5940e` (`Design review: approve 4784b5940e998aa8ef2d19436f763ff30daa46b2`, `design-verdict/R11-OUTSIDE-ROOMS-P2` `e59dcfd724`), on R11-OUTSIDE-ROOMS-P1's handoff head `71609de6570ef91bcd846caee4158e16e7f1e339`, which is this branch's first parent chain: `git diff 71609de657...HEAD` is phase 2 alone, and against `origin/main` the diff also carries phase 1 until it lands.

A room thermostat short of its own target raises the comfort floor the solve plans against, through `SolveLimits.min_temp_margins`, the array the solver already takes; `optimizer.py` and `thermal_model.py` are not edited. Opt-in: a toggle on the rooms page, off by default, and with it off a room list changes nothing in the plan.

## What it does

- **The lift** (`rooms.resolve`). Over the readable rooms whose thermostat is in `heat` or `auto` (the HVAC-mode rule phase 1 carried here): the largest shortfall, target less temperature, less the house's own shortfall against step 0's comfort target of the solve's configuration (verdict item v2c), clipped to [0, 1.0 K]. Held: it moves only when the rooms ask 0.2 K more or less than the lift the previous solve was given.
- **Per step** (`rooms.lifted`). The smallest of the held lift, a ramp from the house's margin over its floor at 0.25 K per hour, and what the step's band leaves over the confidence margin under its comfort target. The band is `get_comfort_temp` less `get_temp_bounds` of the solve's own configuration at `drift.utc_step_starts`, the calls `_build_comfort_bounds` makes (note item s2): the day and night rule is not restated. So the lifted floor never passes the target.
- **Gates**, each handing back the base array object itself: the toggle off, Economy, a tripped window detector (relax option on or off), away (`AwayState.active`, which covers recovery), a manual space pin, the two-zone model, an empty list, a list under its quorum, no room with a counting target, a house temperature that is not finite. **Holiday is treated like away** (the owner's ruling in this seat's dispatch): a solve starting on a holiday date takes no lift, and neither does any later step on one.
- **The what-if** takes the lift and anchor its baseline was solved with (`rooms.lift_of`), never a fresh one, and clips it to its own configuration's band (note item r4, verdict item v2b).
- **Published**: the rooms block's `lift` (size asked, the room that set it, the gate that zeroed it), an attribute of Room Temperature Spread.
- **State**: `rooms` has module state, two per-coordinator side tables (the readings, and the lift the last solve was given). No store, no migration; a restart starts from no lift.

The roster's carries to this group, each answered in this diff:

- Carry 0 (the HVAC-mode rule): built as `rooms.TARGET_COUNTS_IN`, read by `rooms.largest_shortfall`; its failing test and mutation target are here (`no lift, and the base array object itself ...`: room D off, in `cool` and in `heat_cool` lifts nothing; null control, D in `heat` lifts and is named).
- Carry 1 (a new options field moves `tests/golden/config_flow.json`): the fixture is re-recorded and `config_flow`'s line in `tests/golden/claimed_drift.txt` extended for the toggle; the drift run against the merge base is under `## Null control`.
- Carry 2 (`coord_footprint` charges a function handed the coordinator): `rooms.resolve` and `rooms.lifted` take readings, signals and a configuration; only `rooms.hold` and `rooms.lift_of` take the coordinator. `score.py --diff` at both ends is under `## Architecture score`.
- Carry 3 (the 1.0 K cap under the band and phase 2 as its own opt-in toggle, default off): built as the approved note recommends; the owner decision both await is the first `## Forward-carry` item.
- Carry 4 (a floor lifted to the comfort target raises the plan peak): measured with `dev/audit/harnesses/room_lift_solve.py`, not changed in this part; the owner choice is the second `## Forward-carry` item.

Departures from the note, each a consequence of a measurement below, none a change of design:

1. **The note's expected ramp fixture** (0.5 at every day step with the house at 19.6) is the verdict's v2a correction: the array is min(band, margin + rate x lead), and the test expects that.
2. **`rooms` does not import the solver module.** The first cut imported `_step_clock` and `_padded_nonneg` from `optimizer.py`; `score.py --diff` read that as a pure module reaching scipy (`layer_violations 13 -> 21`, `private_cross_module 10 -> 12`). It walks `drift.utc_step_starts` and fits the margins itself.
3. **The planned temperature does rise above the unlifted plan's peak.** The note's evidence asks that the planned temperature never exceed "target plus the pull's own overshoot in the unlifted plan". Measured on the note's mild day it does: see `## Figures`, the harness's `max_over_target_c`. The lifted floor is at or under the target at every step (the harness checks that), and a floor held at the target leaves the plan's stored heat above it. Not asserted in the suite; carried below as an owner question.
4. **The why-now row and the narrative do not name the room lift** (note item 5a1c0e06). Both read the solve's result (`slot_drivers` reads `comfort_floors`; `narrative.py` reads `classify_space_steps`' reasons), which carries one floor array and no part of it attributed; naming the lift there needs a field through `optimizer.py`'s result, which the approved note keeps out of phase 2, and card text in three languages. The lift is named where the note's phase 2 section puts it, on the spread sensor. Carried below.

## Head

`884555c9a64729ef096e1ce84fb5bd3c78dfaf81`

## Mutation proof

`python3 -I tools/audit/seat/mutant_run.py --diff "71609de6570ef91bcd846caee4158e16e7f1e339...HEAD" --cmd CMD --max-mutants 400`, CMD the phase 2 block of `tests/features.py`: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "import asyncio as _asyncio" --prelude 'exec(open("P").read())' 'R.section("#3616 R11-OUTSIDE-ROOMS-P2'`, P written by `features_block.py --emit-prelude P` with the same marker (the T5 rig swallows a `NameError`, so the prelude derivation cannot see the rig's own `_asyncio`; the first `--prelude` supplies it). Each mutant runs in a git-archive copy of the head.

75 mutants drawn (`--list`: 62 in `rooms.py`, 4 `payload.py`, 3 `const.py`, 3 `coordinator.py`, one each in `config_flow.py`, `entry_config.py`, `sensor.py`); the driver prints one line per survivor in diff mode and printed 7, rc 1; the other 68 made the block exit non-zero. Earlier in the branch the same command printed 19, then 9: each survivor in `rooms.py`, `const.py` and `coordinator.py` got a check in the block (commit `eaa706bd8f`), and two got better code (`_comfort_at` replaced a step count no input separates; `lifted` returns the base by truth, not by a boundary comparison).

Survivors of that command, and what kills or dispositions each:

- `config_flow.py:1693 STMT_DEL` (the driver deletes the whole `_OPTION_FIELDS` statement the added row sits in; the block does not import the options flow): `tests/config_flow_steps.py` is red on it, and with only the toggle's row removed its check `the room page offers the lift toggle, off by default, and saves it on beside the list ...` raises (measured in a git-archive copy).
- `payload.py:958`, `:959`, `:960`, `:979 STMT_DEL` (a `TypedDict` field each, no runtime read): `python3 tests/typing_ruler.py` is red on each, `FAIL errors did not grow  [recorded 0, measured 1 (+1)]`, `by_code[typeddict-unknown-key]` (each measured in a git-archive copy; the unmutated copy prints `ALL 12 typing-ruler source checks PASSED`).
- `rooms.py:35 GUARD_OFF` (`if TYPE_CHECKING:`): equivalent, triaged in `tests/mutation_ledger/survivor_triage/rooms.py/@module.GUARD_OFF.e1433e05.json`; the module's namespace hashes the same under the mutant and differently under an `if True:` control.
- `sensor.py:778 RETURN_DEL` (the spread sensor's attributes): `tests/entities.py` is red on it, `FAIL the room sensors read the payload's rooms block ...` and a `TypeError` at `the spread sensor's lift attribute ...` (measured in a git-archive copy).

`prepr.sh`'s own step (`MUTANT_CMD` both phases' rooms blocks, the first 40 mutants of the diff against `origin/main`'s merge base, in file order) reported `17 survivor(s) on the diff's added lines`: all 17 are in `config_flow.py`, 16 on phase 1's lines and one the `_OPTION_FIELDS` statement above, and the features blocks do not import the options flow. Against their detector, `python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --path custom_components/heatpump_optimizer/config_flow.py --cmd CFS --max-mutants 40 --report-only`, CFS `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`: 17 drawn (`--list`), no `SURVIVED` line, rc 0 (the unedited copy passes the command, or the driver exits 3).

The failing test first: the head's `tests/features.py` over `71609de657`'s production code (a git-archive copy) fails at the block's first solve on the absent symbol (`AttributeError: module 'heatpump_optimizer.rooms' has no attribute 'hold'`).

The gates' predicates, by the check that goes red when each is removed (all in the block): `no lift, and the base array object itself ...` (the flag, Economy, window, away, pin, two-zone, holiday, empty list, HVAC mode, stale room, missing target, non-finite house), `a list under its quorum lifts nothing ...`, `the coordinator's signals each gate the lift ...` (the coordinator's own reads of each signal, on a production coordinator), `with the flag off, or never stored, a room list changes nothing ...`.

## Null control

- With no room list, and with a list and the toggle off, absent or None, the scheduled solve is given `min_temp_margins` None and its plan equals the no-list plan step for step, on a production coordinator (`with the flag off, or never stored ...`); the lifted plan differs, which is the control.
- Every gate returns the base array object by identity, with a base of None and with a confidence-margin array (`... the base array object itself (None stays None) ...`); room D in `heat` instead of `off` lifts, which is the control for the HVAC-mode rule.
- Through the production solver an all-zero margin array and every gated lift reproduce the unlifted plan's sha1, and the lift changes it (`dev/audit/harnesses/room_lift_solve.py`); `tests/edge.py` pins the zero array's schedule equal to the unlifted one and each gate's array None.
- A manual pin is why that gate exists: with a forced-off pin for hours 1 to 3 and the lifted array forced in, the solver releases pinned steps the unlifted plan keeps (`tests/edge.py`, `room lift: a pin is why it is gated`).
- Golden drift against the merge base, in the scoped gate below: `CLAIMED config_flow: 5 leaves moved` (phase 1's four and the seed's `room_lift_enabled`), then `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`: no solve fixture moves, and none stores the toggle.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc head=884555c9a64729ef096e1ce84fb5bd3c78dfaf81 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- The block reads `MODE: FULL` because its registered instrument overlays `origin/main`'s `tests/closure.py` on the head's tree (`tools/pr/figure_registry.json`, `files`), and main's copy has moved past this branch's merge base (`git diff --quiet HEAD origin/main -- tests/closure.py || echo DIFFERS` prints `DIFFERS`), which `select` reads as a change to the gate itself. The head's own copy, the command above, prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`; CI grades the pull request's own merge.
- The scoped gate at the head, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`, `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, rc 0, on a tree left untouched for the run; `tests/features.py`, `tests/entities.py`, `tests/golden.py`, `tests/env_drift.py --all`, `tests/config_flow_steps.py`, `tests/edge.py`, `tests/stress.py`, `tests/typing_ruler.py` and `tests/harness_headers.py` among the 30. `tests/card_browser.mjs` was not run: the diff touches no card file.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `tests/structure_budgets.json` is byte-identical to `71609de657`'s (`git diff --quiet 71609de657 HEAD -- tests/structure_budgets.json && echo IDENTICAL` prints `IDENTICAL`). The first commit recorded `class_excess_loc` and `max_class_loc` two lines lower and a later one restored them: the two call sites net no line over phase 1.
- `PYTHONPATH=tests/hastub:custom_components:tests OPENBLAS_NUM_THREADS=1 python3 dev/audit/harnesses/room_lift_solve.py` (production solver, 24 h at 15 min from 12:00, floor 19.5, target 20.0, house 19.6, `weather("shoulder")`, `prices("winter_typical")`; the header states each row):

~~~text
none               space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
zeros              space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_enabled      space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_economy      space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_open_window  space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_away         space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_manual_pin   space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
gated_two_zone     space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=eda725c0be09 status=optimal
lift margins, first 8 steps and the largest: [0.1, 0.1625, 0.225, 0.2875, 0.35, 0.4125, 0.475, 0.5] 1.0
lift               space_kwh=  8.62 min_c=20.000 mean_c=20.165 max_over_target_c=+0.450 sha1=986a015f4945 status=optimal
none_pinned_off    space_kwh=  6.24 min_c=19.578 mean_c=19.895 max_over_target_c=+0.241 sha1=f6cd94a0b32e status=optimal
lift_pinned_off    space_kwh=  7.88 min_c=20.000 mean_c=20.194 max_over_target_c=+0.484 sha1=93e670785219 status=optimal
released space pins: unlifted=0 lifted=6
ok   zeros reproduce none
ok   every gate reproduces none
ok   the lift changes the plan
ok   the lift plans more space energy
ok   the lift raises the lowest planned temperature
ok   the lifted floor is at or under the comfort target at every step
~~~

  Null control in the same run: `zeros` and the six `gated_*` rows carry `none`'s sha1. The lift's cost on this day is the `space_kwh` difference between `none` and `lift`; the design's own table measured the same fixture before the code existed and is the designer's figure, not re-used here.
- Solve cost: no decision variable, constraint or objective term is added; `tests/stress.py` passed in the scoped gate above with `tests/stress_budgets.json` untouched (`git diff --quiet 71609de657 HEAD -- tests/stress_budgets.json && echo IDENTICAL` prints `IDENTICAL`). The lift's own work per solve is one pass over the horizon's steps calling the configuration's two comfort methods, and nothing when no lift is held.
- Seam enumeration, every build of the margin array: `git grep -n "min_temp_margins=" -- custom_components/heatpump_optimizer/coordinator.py` returns the two `SolveLimits` builds; both go through `rooms.lifted` (closed in this diff). Every reader of the lift: `git grep -n -E "rooms\.(resolve|lifted|hold|lift_of|gate)" -- custom_components/` returns those two builds and `_build_data_dict`'s `rooms.published` call.
- Finder's harness: none. #3616 is an outside report and the design note names none (`No finder harness: owner report.`); `dev/audit/harnesses/room_lift_solve.py` is this fixer's, in the tree for the reviewer and for phase 3.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 71609de6570ef91bcd846caee4158e16e7f1e339`: `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2500->2502)`.

- `coord_footprint` 2500 -> 2502: `rooms.hold`, the one side-table write a coordinator is handed (two statements: the write and the return that lets the build chain it). The design's seam keeps the held lift in a per-coordinator side table so the coordinator gains no attribute (`coordinator_attrs` is at its budget); the lift's logic, `resolve` and `lifted`, takes readings and a configuration, not the coordinator, as phase 1's carry asked. Before that split the same measurement read `coord_footprint 2500->2508; layer_violations 13->21; private_cross_module 10->12`: the mechanism of the improvement is the removed solver import and the two pure functions, and restoring `from .optimizer import _padded_nonneg, _step_clock` in `rooms.py` is its null control.
- Against `origin/main`'s merge base the figure also carries phase 1's own `coord_footprint` rise, explained in its body.

## Unpinned sites

The 45 sites `python3 tools/pr/ci_predict.py --base origin/main` lists as `ADDED UNPINNED` at the head (phase 1's sites among them until it lands), each under `custom_components/`.

- custom_components/heatpump_optimizer/config_flow.py:2577 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:2578 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/config_flow.py:3319 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/coordinator.py:6842 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/entry_config.py:61 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:282 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:287 CLAMP_DROP*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:287 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1277 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1281 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1290 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1294 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1294 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1297 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/inputs.py:1302 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:40 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:63 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:82 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:82 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:104 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:111 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:125 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:143 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:152 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:157 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:161 CONST: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:185 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:191 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:211 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:222 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:244 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:245 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:247 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:264 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:272 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:274 CLAMP_DROP*2: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:276 CMP_BOUND: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:277 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:298 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:307 CLAMP_DROP: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:309 CLAMP_DROP*3: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/rooms.py:310 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/sensor.py:279 GUARD_OFF: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/sensor.py:755 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)
- custom_components/heatpump_optimizer/sensor.py:778 RETURN_DEL: pinned by mutation-autofix (its lane mutates `custom_components/`)

`rooms.py`'s `if TYPE_CHECKING:` guard is not among them: its triage is `tests/mutation_ledger/survivor_triage/rooms.py/@module.GUARD_OFF.e1433e05.json` (equivalent, measured against an `if True:` control).

## Red checks

- `tests / mutation`: predicted red at the head by the unpinned sites above, which `mutation-autofix` pins once the pull request exists (`ci-autofix.md`: never duplicated by the fixer). Cheaper detector: `prepr.sh`'s step 6d, which ran before the handoff and named every site, at no standing cost beyond the prepr run; the red is the lane's own pinning step, so none cheaper exists.

## Forward-carry

- The cap under the band (1.0 K, `rooms.ROOM_LIFT_CAP_C`) and phase 2 as its own opt-in toggle, default off, are built as the approved note recommends; both are routed `decision: owner` there and `dev/programme/RULINGS.md` holds no ruling on either (`git grep -n -i -E "room|3616" origin/main -- dev/programme/RULINGS.md` prints nothing). Pending owner confirmation. Carry: R11-OUTSIDE-ROOMS-P2
- A floor lifted to the comfort target raises the plan's peak above the unlifted plan's: `dev/audit/harnesses/room_lift_solve.py`'s `max_over_target_c`, `none` against `lift`, with `zeros` as the control. The note expected no rise. Whether the clip should stop short of the target (a headroom under it) or the rise is accepted is the owner's choice; re-measure with the harness at the deciding head. Pending owner ruling. Carry: R11-OUTSIDE-ROOMS-P2
- The why-now comfort-floor row and the daily narrative do not name the room lift (note item 5a1c0e06): both read the solve's result, which attributes no part of the floor to a room, and the note keeps `optimizer.py` out of phase 2. Precondition for whoever builds it: a per-step lift (or the held scalar) on the solve's result beside `comfort_floors`, read by `slot_drivers` and `narrative.py`, with card text in the three languages; the control is a solve with the toggle off, whose row must not change. Carry: R11-OUTSIDE-ROOMS-P3
- A new options field moves `tests/golden/config_flow.json` and the D5 harness header counts (`dev/audit/rounds/round3/D5/option_doc_coverage.py`, two RESULT lines), and a changed `rooms.published` call text moves `tests/entities.py`'s EG-B3 resolve table; `tests/harness_headers.py` and `tests/entities.py` refuse each. Phase 3's sensor and store meet the same three. Carry: R11-OUTSIDE-ROOMS-P3
- `tests/features.py` re-reads production source by line while it runs (`inspect.getsource`), so an edit to `coordinator.py` during a gate run fails checks that have nothing to do with the edit (measured here: two `FAIL` lines and a `SyntaxError` in a run the same tree then passed). Leave the tree still for the length of a gate run. Carry: dismissed: a working practice of this seat, no later stage's brief changes on it

## Friction

none
