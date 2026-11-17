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

prepr: passed rc=0 at 3a16b7a938b10b66a49c5c9fceb20835e9d06785
`3a16b7a938b10b66a49c5c9fceb20835e9d06785`

The code head merges `origin/main` at `2d7161a4b709` (`git merge-tree --write-tree origin/main 69dc1cd4f2` reported two conflicts). Both were the same count, which main's `runs.py` and this branch's `rooms.py` had each raised by one. They are resolved to both: `dev/audit/rounds/round4/D6/claims.py` reads `arch_modules_on_disk=96` and `arch_map_listed=96`. `tests/deployment_shape.py` reads 115 package files (`git ls-files custom_components/heatpump_optimizer | wc -l` prints `115`) and 167 closure pairs at 0.80. That figure comes from `tests/entities.py`'s `_d308_pairs` predicate, re-run over the merged `tests/closures.json` (164 over each parent's own file).

The merge also leaves `docs/architecture.md` one module short in two counts, which neither parent could see. `dev/audit/rounds/round4/D6/claims.py` refused `C32 docs/architecture.md: 45 modules` (95 against 96 on disk); the register now reads `claims_true=123`, `claims_false=0`. The first scoped gate at `59047cf347` then failed `tests/entities.py` (`1 of 2729 ENTITY CHECKS FAILED`, `architecture.md's HA-free count is the tree's [architecture.md says 61; 96 modules less 34 that touch homeassistant anywhere leaves 62]`) and `tests/doc_claims.py` (`1 of 410 checks FAILED`, the same count). Both read 96 and 62 now; at this head `ALL 2729 ENTITY CHECKS PASSED` and `ALL 410 checks PASSED`.

## Mutation proof

### This repair: the five sites CI run 43942831682 refused

`tests / mutation` at `69dc1cd4f2` refused `2177 unpinned site(s) against 2175 at the ratchet base 6f422812d5d8, 5 of them added by this diff`. Four of the five survived every check at 69dc1cd; the fifth (the lift's cap) was already killed by the existing cap check, but no ledger row recorded it. Each now has a check in `tests/features.py`'s rooms blocks and a `killed_by` row. Before and after, by a scratch driver not in the tree (each mutant applied in place, then the rooms blocks run through `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "import asyncio as _asyncio" --prelude 'exec(open("P").read())' 'R.section("#3616 R11-OUTSIDE-ROOMS-P1'`, with P from `features_block.py --emit-prelude P` and the same marker; then restored, `cmp` against the committed file printing `FEATURES_RESTORED`). "old" means 69dc1cd's `tests/features.py` and "new" this head's, both over the same mutated production file:

| site | mutant | old | new: the check that goes red |
|---|---|---|---|
| `inputs.py` `_scaled` CLAMP_DROP (min) | `max(float(scale), STALENESS_SCALE_MIN)` | `ALL 38 FEATURES BLOCK PASSED` | `FAIL the staleness scale is clamped at both ends ...` |
| `inputs.py` `_scaled` CLAMP_DROP (max) | `min(float(scale), STALENESS_SCALE_MAX)` | `ALL 38 FEATURES BLOCK PASSED` | `FAIL the staleness scale is clamped at both ends ...` |
| `rooms.py` `_margins` CLAMP_DROP | `np.asarray(base, dtype=float)[:n_steps]` | `ALL 38 FEATURES BLOCK PASSED` | `FAIL a negative confidence margin is read as zero ...` |
| `rooms.py` `resolve` CLAMP_DROP (floor) | `min(worst[0] - (target_c - house_c), ROOM_LIFT_CAP_C)` | `ALL 38 FEATURES BLOCK PASSED` | `FAIL a room less short of its target than the house is of its own holds a lift of zero ...` |
| `rooms.py` `resolve` CLAMP_DROP (cap) | `max(worst[0] - (target_c - house_c), 0.0)` | `6 of 38 FEATURES BLOCK FAILED` | the same six, the cap check `a room no shorter of its target ... lifts the 1.0 K cap` among them |

Null control: the unmutated head prints `ALL 41 FEATURES BLOCK PASSED` with the new checks, and 69dc1cd's file `ALL 38 FEATURES BLOCK PASSED`. Each new check carries its own control in the same predicate: `_scaled` at 0.5 and 10.0 passes through unchanged; a room 0.5 K shorter than the house holds 0.5 K; the margins with no confidence margin are what the negative one must equal.

Why the `_scaled` sites are new at all: the clamp moved out of `max_age_for` into `_scaled` in this diff, so its ledger anchor changed. Its two sites were unpinned at the base too; the old check compared `_scaled` to `max_age_for`, which calls `_scaled`, so a mutant moved both sides alike.

The ledger rows: `python3 tests/mutation_table.py --pin-killed --base 6f422812d5d8b918beace0283419c153f6df66ce --scripts tests/features.py --jobs 3` printed `PIN KILLED: 5 pinned, 0 left unpinned`. Its baseline was `tests/features.py: rc=0 failed=0`, and its null control `inputs.py:93 NULL_COMMENT survived tests/features.py`. It wrote `tests/mutation_ledger/killed_by/inputs.py/_scaled.CLAMP_DROP.8c7e424f.json`, `rooms.py/_margins.CLAMP_DROP.fcfbcf29.json` and `rooms.py/resolve.CLAMP_DROP.1af0ce3c.json`, two sites under each of the first and third anchors. The run was restricted to `tests/features.py` because each full-suite run takes about 13 minutes here; the first unrestricted run was stopped by the session's 30-minute background limit before it recorded anything.

### Earlier rounds of this branch


`python3 -I tools/audit/seat/mutant_run.py --diff "71609de6570ef91bcd846caee4158e16e7f1e339...HEAD" --cmd CMD --max-mutants 400`, CMD the phase 2 block of `tests/features.py`: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "import asyncio as _asyncio" --prelude 'exec(open("P").read())' 'R.section("#3616 R11-OUTSIDE-ROOMS-P2'`, P written by `features_block.py --emit-prelude P` with the same marker (the T5 rig swallows a `NameError`, so the prelude derivation cannot see the rig's own `_asyncio`; the first `--prelude` supplies it). Each mutant runs in a git-archive copy of the head.

75 mutants drawn (`--list`: 62 in `rooms.py`, 4 `payload.py`, 3 `const.py`, 3 `coordinator.py`, one each in `config_flow.py`, `entry_config.py`, `sensor.py`); the driver prints one line per survivor in diff mode and printed 7, rc 1; the other 68 made the block exit non-zero. Earlier in the branch the same command printed 19, then 9: each survivor in `rooms.py`, `const.py` and `coordinator.py` got a check in the block (commit `eaa706bd8f`), and two got better code (`_comfort_at` replaced a step count no input separates; `lifted` returns the base by truth, not by a boundary comparison).

Survivors of that command, and what kills or dispositions each:

- `config_flow.py:1693 STMT_DEL` (the driver deletes the whole `_OPTION_FIELDS` statement the added row sits in; the block does not import the options flow): `tests/config_flow_steps.py` is red on it, and with only the toggle's row removed its check `the room page offers the lift toggle, off by default, and saves it on beside the list ...` raises (measured in a git-archive copy).
- `payload.py:958`, `:959`, `:960`, `:979 STMT_DEL` (a `TypedDict` field each, no runtime read): `python3 tests/typing_ruler.py` is red on each, `FAIL errors did not grow  [recorded 0, measured 1 (+1)]`, `by_code[typeddict-unknown-key]` (each measured in a git-archive copy; the unmutated copy prints `ALL 12 typing-ruler source checks PASSED`).
- `rooms.py:35 GUARD_OFF` (`if TYPE_CHECKING:`): equivalent, triaged in `tests/mutation_ledger/survivor_triage/rooms.py/@module.GUARD_OFF.e1433e05.json`; the module's namespace hashes the same under the mutant and differently under an `if True:` control.
- `sensor.py:778 RETURN_DEL` (the spread sensor's attributes): `tests/entities.py` is red on it, `FAIL the room sensors read the payload's rooms block ...` and a `TypeError` at `the spread sensor's lift attribute ...` (measured in a git-archive copy).

`prepr.sh`'s own step at `59047cf347` (`MUTANT_CMD` the rooms blocks of `tests/features.py`, the first 40 mutants of the diff against `origin/main`'s merge base, in file order) reported `17 survivor(s) on the diff's added lines`. All 17 are in `config_flow.py`, which the features blocks do not import. Against their detector at this head, `python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --path custom_components/heatpump_optimizer/config_flow.py --cmd CFS --max-mutants 40 --report-only`, CFS `env PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`: 17 drawn (`--list`), no `SURVIVED` line, rc 0.

The failing test first: the head's `tests/features.py` over `71609de657`'s production code (a git-archive copy) fails at the block's first solve on the absent symbol (`AttributeError: module 'heatpump_optimizer.rooms' has no attribute 'hold'`).

The gates' predicates, by the check that goes red when each is removed (all in the block): `no lift, and the base array object itself ...` (the flag, Economy, window, away, pin, two-zone, holiday, empty list, HVAC mode, stale room, missing target, non-finite house), `a list under its quorum lifts nothing ...`, `the coordinator's signals each gate the lift ...` (the coordinator's own reads of each signal, on a production coordinator), `with the flag off, or never stored, a room list changes nothing ...`.

## Null control

- With no room list, and with a list and the toggle off, absent or None, the scheduled solve is given `min_temp_margins` None and its plan equals the no-list plan step for step, on a production coordinator (`with the flag off, or never stored ...`); the lifted plan differs, which is the control.
- Every gate returns the base array object by identity, with a base of None and with a confidence-margin array (`... the base array object itself (None stays None) ...`); room D in `heat` instead of `off` lifts, which is the control for the HVAC-mode rule.
- Through the production solver an all-zero margin array and every gated lift reproduce the unlifted plan's sha1, and the lift changes it (`dev/audit/harnesses/room_lift_solve.py`); `tests/edge.py` pins the zero array's schedule equal to the unlifted one and each gate's array None.
- A manual pin is why that gate exists: with a forced-off pin for hours 1 to 3 and the lifted array forced in, the solver releases pinned steps the unlifted plan keeps (`tests/edge.py`, `room lift: a pin is why it is gated`).
- Golden drift against the merge base, in the scoped gate at `59047cf347` below: `CLAIMED config_flow: 5 leaves moved` (phase 1's four and the seed's `room_lift_enabled`), `CLAIMED wood_coil: 1 leaves moved` (another lane's claim, inherited from main), then `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 2d7161a4b70923da910f9997e18db632c0d4ec2d` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. No solve fixture moves, and none stores the toggle.
- The mutation ratchet, by `python3 tests/mutation_table.py --scope changed --base <ref> --max 0 --jobs 1`. At `69dc1cd4f2` against `6f422812d5d8` it printed `MUTATION TABLE REFUSED -- 2177 unpinned site(s) against 2175`, the red CI read. At `7f7bbc5cb4` (the merge; the commits after it change only `docs/architecture.md` and the D6 register, no Python) it prints `2162 unpinned site(s) ... 2175 at the ratchet base 6f422812d5d8` and `2162 unpinned site(s) ... 2165 at the ratchet base 2d7161a4b709` (origin/main), each `MUTATION TABLE PASSED (empty pool)`.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=3a16b7a938b10b66a49c5c9fceb20835e9d06785 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- The scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, at `59047cf347` (one commit before this head): `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`, `2 TEST SCRIPT(S) FAILED` (`tests/entities.py`, `tests/doc_claims.py`), every other script `ok`. That includes `tests/features.py` (`ALL 5821 FEATURE CHECKS PASSED`), `tests/stress.py`, `tests/harness_headers.py`, `tests/golden.py`, `tests/env_drift.py --all`, `tests/config_flow_steps.py`, `tests/edge.py`, `tests/deployment_shape.py` and `tests/structure.py`. This head changes only `docs/architecture.md` after it (`git diff --stat 59047cf347 HEAD`). The two scripts re-run here: `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2729 ENTITY CHECKS PASSED`, and `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 410 checks PASSED`. `tests/card_browser.mjs` was not run: the diff touches no card file.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at `7f7bbc5cb4`, and prepr's `merged structure` step at `59047cf347` (`STRUCTURE RATCHET PASSED`, HEAD merged with origin/main). `tests/structure_budgets.json` differs from origin/main's only where the ledger merge driver took the lower `class_excess_loc` (17385 against main's 17407) and kept the older `recorded_at`; no metric moved up.
- `PYTHONPATH=tests/hastub:custom_components:tests OPENBLAS_NUM_THREADS=1 python3 dev/audit/harnesses/room_lift_solve.py`, re-run at `7f7bbc5cb4` with output byte-identical to `884555c9a6`'s (production solver, 24 h at 15 min from 12:00, floor 19.5, target 20.0, house 19.6, `weather("shoulder")`, `prices("winter_typical")`; the header states each row):

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

`python3 tools/audit/archscore/score.py --diff 71609de6570ef91bcd846caee4158e16e7f1e339`: `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2500->2502)`, measured at `884555c9a6`. This repair adds no production line: `diff <(git diff -U0 6f422812d5d8 69dc1cd4f2 -- custom_components/ | grep '^[-+]') <(git diff -U0 2d7161a4b7 HEAD -- custom_components/ | grep '^[-+]') && echo CHANGED_LINES_IDENTICAL` prints `CHANGED_LINES_IDENTICAL`; the same comparison without `-U0`, whose hunk context includes main's own edits nearby, differs.

- `coord_footprint` 2500 -> 2502: `rooms.hold`, the one side-table write a coordinator is handed (two statements: the write and the return that lets the build chain it). The design's seam keeps the held lift in a per-coordinator side table so the coordinator gains no attribute (`coordinator_attrs` is at its budget); the lift's logic, `resolve` and `lifted`, takes readings and a configuration, not the coordinator, as phase 1's carry asked. Before that split the same measurement read `coord_footprint 2500->2508; layer_violations 13->21; private_cross_module 10->12`: the mechanism of the improvement is the removed solver import and the two pure functions, and restoring `from .optimizer import _padded_nonneg, _step_clock` in `rooms.py` is its null control.
- Against `origin/main`'s merge base the figure also carries phase 1's own `coord_footprint` rise, explained in its body.

## Unpinned sites

None at this head. `python3 tools/pr/ci_predict.py --base origin/main` at `7f7bbc5cb4` lists no `ADDED UNPINNED` site and prints `CI PREDICT: no closures, fast, governance or instrument red predicted against 2d7161a4b709`. The ratchet count is under `## Null control`.

The 45 sites the previous body listed as `pinned by mutation-autofix` were not all pinned by it. Its commit `69dc1cd4f2` (`ci: pin killed mutants`) recorded the rest. The five sites in `## Mutation proof` stayed unpinned, which was the red. Those five are now `killed_by` `tests/features.py`, and `rooms.py`'s `if TYPE_CHECKING:` keeps its triage `tests/mutation_ledger/survivor_triage/rooms.py/@module.GUARD_OFF.e1433e05.json`.

## Red checks

The set `python3 tools/audit/seat/merge_train.py owed-reds` prints contains all three reds of CI run 43942831682 at `69dc1cd4f2`:

- `tests / mutation`: five sites this diff added were unpinned, `2177` against `2175`. Repaired here (`## Mutation proof`). Cheaper detector: `prepr.sh`'s step 6d and `tools/pr/ci_predict.py` both list `ADDED UNPINNED` sites before the handoff, at no standing cost beyond the prepr run. The previous handoff ran it and listed all five, and the body read them as owed to `mutation-autofix`. `ci-autofix.md` says that lane pins a killed site only; it says a survivor is red and a human triages it. That body's figures do not show whether a driver killed each listed site, so this red was reachable before the handoff. The root-cause seat owns the process state (`defect-root-cause.md`); this body records the trigger.
- `pr-contract / pr-contract`: an independent cause beside the mutation red. The body's registered figure block named head `95eae2dd6ff1` after the bot's `69dc1cd4f2` commit, `ERROR [figure-block] line 68: block scope-line names head=95eae2dd6ff1 ... this run is head=69dc1cd4f2e1`. Repaired here: this body's block is empty, and `body_push.sh` renders it at the new head. Cheaper detector: none. The block was right when it was pushed; the bot commit moved the head later, and `pr-contract`'s figure-block step is the first check that runs after that move.
- `gate`: a consequence only. Its log reads `FAIL tests / mutation: failure (this run)` and `pr-contract / pr-contract: failure (this run)`, with no other cause (`codeql / Analyze (python)` was `cancelled`, not red).

## Forward-carry

- The cap under the band (1.0 K, `rooms.ROOM_LIFT_CAP_C`) and phase 2 as its own opt-in toggle, default off, are built as the approved note recommends; both are routed `decision: owner` there and `dev/programme/RULINGS.md` holds no ruling on either (`git grep -n -i -E "room|3616" origin/main -- dev/programme/RULINGS.md` prints nothing). Pending owner confirmation. Carry: R11-OUTSIDE-ROOMS-P2
- A floor lifted to the comfort target raises the plan's peak above the unlifted plan's: `dev/audit/harnesses/room_lift_solve.py`'s `max_over_target_c`, `none` against `lift`, with `zeros` as the control. The note expected no rise. Whether the clip should stop short of the target (a headroom under it) or the rise is accepted is the owner's choice; re-measure with the harness at the deciding head. Pending owner ruling. Carry: R11-OUTSIDE-ROOMS-P2
- The why-now comfort-floor row and the daily narrative do not name the room lift (note item 5a1c0e06): both read the solve's result, which attributes no part of the floor to a room, and the note keeps `optimizer.py` out of phase 2. Precondition for whoever builds it: a per-step lift (or the held scalar) on the solve's result beside `comfort_floors`, read by `slot_drivers` and `narrative.py`, with card text in the three languages; the control is a solve with the toggle off, whose row must not change. Carry: R11-OUTSIDE-ROOMS-P3
- A new options field moves `tests/golden/config_flow.json` and the D5 harness header counts (`dev/audit/rounds/round3/D5/option_doc_coverage.py`, two RESULT lines), and a changed `rooms.published` call text moves `tests/entities.py`'s EG-B3 resolve table; `tests/harness_headers.py` and `tests/entities.py` refuse each. Phase 3's sensor and store meet the same three. Carry: R11-OUTSIDE-ROOMS-P3
- `tests/features.py` re-reads production source by line while it runs (`inspect.getsource`), so an edit to `coordinator.py` during a gate run fails checks that have nothing to do with the edit (measured here: two `FAIL` lines and a `SyntaxError` in a run the same tree then passed). Leave the tree still for the length of a gate run. Carry: dismissed: a working practice of this seat, no later stage's brief changes on it

## Friction

none
