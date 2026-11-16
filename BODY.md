Refs #3616: the planning defect its diagnostics showed, not the issue's multi-zone request, which stays open for the room-level steps the owner's reply lists. No `Closes`.

A floor-return reading seeded the slab estimate every cycle (`ThermalModel.update_slab_from_return_temp`, merged 0.7 sensor / 0.3 model) behind only the `FLOOR_WATER_RANGE_C` range check. A heat-pump return on a buffer plant in that field reads far above any floor loop, so the slab estimate believes heat is stored and the plan holds none. New pure module `slab_seed.py` owns the decision:

- **Bound** `SLAB_SEED_MAX_ABOVE_ROOM_K = 12.0` (argued in its comment): floor-loop water runs 3-9 K above room air (the band the `lower_floor_modelled` repair already states); EN 1264's surface limits (29 C occupied, 33 C bathroom, over 20 / 24 C design rooms) put the floor 9 K above its room; 3 K margin for a manifold sensor and a peripheral zone. A reading more than 12 K above the room is refused.
- **Model estimate**: a refused reading leaves the slab to the model's own estimate, by the exact path an install with no floor-return sensor takes (`_async_learn_interval(slab_unsensed=True)`, then `_propagated_slab` or the room+1 K first seed). Measured identical below (refused arm == unconfigured arm, slab trajectory and plan).
- **Hot-water runs and defrost**: a reading is refused while the pump's observed mode is hot water alone (`slab_seed.hot_water_run`: `mode_observed`, `dhw`, not `space_heat`) or a defrost is flagged (asked of the `defrost_standoff` owner, `freq_control.defrost_interval`, per `tests/entities.py`'s P2 registry).
- **Repair** `floor_return_implausible`, a `ConfigNotices` warning naming the sensor, its reading, the room and the bound; raised on the level alone (a hot-water or defrost refusal is the plant working, not a wrong sensor) and cleared on the next plausible cycle. No stored option is migrated.
- **Texts**: the floor-return option description (config and both options pages, en/de/sv) says which sensor belongs there and states the bound; README's sensor table says the Optimal Setpoint is the step's planned power scaled onto the coldest..warmest acceptable range (`HeatPumpOptimizer._power_to_setpoints`), not a target temperature, and its repair list gives the new repair a home.

Timing (decision): the coordinator seeds the published state before this cycle's pump signals are read, so the first call (`slab_seed.seed`) judges on last cycle's signals, and `slab_seed.judge`, after the signals are read, re-decides on this cycle's before the slab is finalised. Alternatives that lost: moving the pump-signal read above the floor-return read reorders the reader's health snapshot and every learner between; seeding only after the signals are read moves what the learners between see, so plausible installs would not stay byte-identical.

The bound is one-sided: a reading below the room is not refused. That direction plans more heat, not none, and no report shows it; out of this fix's scope.

## Head

`74a57885a3ef178f2556b4b105063a2b3a2edd9a` is this PR's head: `59070bb608` (the delivery row) plus the `mutation-autofix` commit `74a57885a3` (`ci: pin killed mutants`, ledger files under `tests/mutation_ledger/` only, no production line). The code below is unchanged from the measured tree; this body re-renders the figure block at this head against the PR's recorded base `5825e1346c14eecace5c87c046558774145a94dc` (origin/main at the re-render is 6aa7ddc712, which `git merge-tree --write-tree` merges with this head without a conflict; 2026-11-16T02:05Z).

a902e7fad4046ecbbcb115186ef4fdd5cc770aed, measured against merge base cb19070965d76b84d9a221d4dfb05c7c9b8efbf7, origin/main's tip (committed 2026-11-15T22:29:46+01:00) at 2026-11-15T22:15Z. The branch was cut at 66865be375 and merged origin/main cb19070965 (conflicts in the package counts, resolved in the merge commit's message); the evidence below is re-taken at that head unless it names another tree.

## Mutation proof

Block: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" '# --- #3616: an implausible slab seed'`, prelude from `features_block.py --emit-prelude <prelude> '# --- #3616: an implausible slab seed'`. Unmutated: `ALL 9 FEATURES BLOCK PASSED`.

- Failing first (the coordinator, strings and translations at the merge base, `slab_seed.py` present but unwired): `6 of 9 FEATURES BLOCK FAILED`: `#3616: a 38 C heat-pump return ... no longer plans zero space heating` (`planned 0.000 kWh, slab [37.47, 38.54, 38.86, 38.96, 38.99, 39.0]`), `and a refused reading leaves the slab to the model exactly as an install with no floor-return sensor does`, `and a repair issue names the sensor and the bound`, `a hot-water-only run does not seed the slab from the return`, `nor does a defrost`, `every floor-return option text names the bound the guard applies`. The null control and the two predicate checks passed.
- Bound removed (`above_room` returns `False`): `4 of 9 FAILED`, the zero-plan, model-equivalence, repair and bound checks.
- Early gate removed (the first call seeds unconditionally): `3 of 9 FAILED`, model-equivalence, hot-water and defrost.
- Defrost arm off: `1 of 9 FAILED`, `nor does a defrost`. Hot-water arm off: `1 of 9 FAILED`, `a hot-water-only run does not seed the slab from the return`.
- Diff drive: `PYTHONPATH=tests/hastub python3 tools/audit/seat/mutant_run.py --diff 66865be375...HEAD --path custom_components --max-mutants 80 --report-only --cmd '<the block command>'` at ac80188f36 (slab_seed.py and coordinator.py as at the head) drafts 27 mutants (`--list` counts them) and prints one line, `SURVIVED custom_components/heatpump_optimizer/slab_seed.py:59 RETURN_DEL`, rc 0: an equivalent mutant (`refusal`'s trailing `return None`), triaged in `tests/mutation_ledger/survivor_triage/slab_seed.py/refusal.RETURN_DEL.da9e8e97.json`.

## Null control

- A plausible floor-loop return (26 C, 6.4 K above a 19.6 C room) still seeds the slab unchanged: it converges on the merge's return + 1 K fixed point (`[26.55, 26.86, 26.96, 26.99, 27.0, 27.0]` at both ends), raises no repair, and plans 11.22 kWh at the merge base and at the head.
- A heating mode with the defrost flag off seeds exactly as with no pump signals.
- Existing installs: `GOLDEN_MODE=drift GOLDEN_REF=cb19070965 python3 tests/golden.py` (inside the scoped gate run below) prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, so every golden plan, those with a floor-return sensor among them (`coord_*` fixtures), is unchanged; both claim files are byte-identical to the merge base.
- The features.py checks pinning the floor-return slab merge (room 21 C, return 28 C: `and the floor return still does its real job: the slab estimate`; the r9f12 mapped arm, return 27 C) are 7 and 6 K above the room, inside the bound, and pass unchanged in CI's whole-script run.

## Figures

- Reproduction, merge base: return 38 C, room 19.6 C, comfort 22 C, outdoor 6 C, six hourly closed-loop cycles through `async_setup_entry` / `async_refresh` (the block's `_ssg_cycles`): planned space heating `0.000 kWh`, slab `[37.47 .. 39.0]`. Head: `12.689 kWh`, slab equal to the unconfigured install's.
- Bound edge: `slab_seed.above_room(32.0, 20.0)` False, `(32.1, 20.0)` True (the block's bound check; the `>=` mutant is killed there).
- Seams of the class, by `awk '/async def _update_current_state/,/def _refresh_model_corrections/' custom_components/heatpump_optimizer/coordinator.py | grep -oE "reader\.read[a-z_]*\(CONF_[A-Z_]+" | sort | uniq -c`: 13 reads. The class is a reading that seeds a model state for a different physical quantity than it measures. `FLOOR_RETURN_TEMP` (water, seeding the slab): closed here. `INDOOR_TEMP`, `LOWER_FLOOR_TEMP`, `OUTDOOR_TEMP`, `DHW_TEMP`, `BUFFER_TANK_TEMP`, `WOOD_TANK_TOP`, `WOOD_TANK_BOTTOM`: each seeds the quantity it measures, outside the class. `MIXING_VALVE_TARGET` (a set-point read as a room temperature): already guarded by the `valve_target_above_comfort` repair. `SOLAR_RADIATION`, `ENERGY`, `POWER`, `HOUSE_POWER`: not temperatures, seed no thermal state.
- Structure: `python3 tests/structure.py` passes every row at the head; the first draft breached `class_excess_loc` +9, `max_class_loc` +9 and `max_cc` +1, paid by moving the decision into `slab_seed` (`seed`, `judge`) and correcting the coordinator's last-resort comment, which predated refused readings.
- Typing: `python3 tests/typing_ruler.py` `ALL 9 ... PASSED`, `ALL 12 ... PASSED` (a first draft added one `arg-type`: `seed` now takes `float | None`).
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=cb19070965 ./tests/run.sh` at 12fc864c4a (the merge): `MODE: SCOPED -- 23 script(s) run`, 22 ok, `tests/entities.py` red on one check, `the lane's docstring records those measured numbers as the selection-cost note` (`163 of the 528` pairs now, 162 written), corrected at the head; `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head `ALL 2723 ENTITY CHECKS PASSED`. `tests/features.py` whole script ok in that run (714 s), the #3616 block included. `tests/doc_claims.py` `ALL 410 checks PASSED`. `tests/harness_headers.py` passes with the round-4 D6 header and output re-recorded for 94 modules (main's `running_signal.py` and this branch's `slab_seed.py`).
- Closures: `DERIVE_LANES=4 ./tests/derive_closures.sh --scripts-from <the 22 scripts whose closure holds coordinator.py> --record-only --out-dir D`, `closure.py merge --in-dir D --partial --allow-failures` (`entities.py` failed only on the classification the merge supplies), then `derive_closures.sh --single tests/entities.py`; `slab_seed.py` joins 22 closures.
- Architecture score: `python3 tools/audit/archscore/score.py --diff cb19070965` prints `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2495->2496)` at the head against cb19070965 as against 66865be375, answered under `## Architecture score`.

<!-- figure-block: scope-line mb=5825e1346c14eecace5c87c046558774145a94dc head=74a57885a3ef178f2556b4b105063a2b3a2edd9a -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

## Architecture score

- `coord_footprint` 2495 -> 2496: the coordinator gains one orchestration statement, the `slab_seed.judge` call that decides on this cycle's pump signals before the slab is finalised; the decision itself, the bound and the repair live in `slab_seed.py`. Folding the call into the `_async_learn_interval` argument with a walrus would read flat and only hide the statement.

## Red checks

- `tests / mutation` (predicted by `tools/pr/ci_predict.py` step 6d and red on an earlier commit of this branch; `mutation-autofix`'s `74a57885a3` pinned the sites): the 12 added sites `## Unpinned sites` lists have no pin in `tests/mutation_ledger/` until `mutation-autofix` commits one. The cheaper detector already exists and ran: step 6d of `tools/pr/prepr.sh` (`ci_predict.py`'s `mutants` arm, seconds per run, in every seat's pre-handoff path) predicted all 12 here, and every one is killed by the block locally (`## Mutation proof`). No further countermeasure: the pin is `mutation-autofix`'s by `ci-autofix.md`, so a fixer-side pin would duplicate its commit.
- `pr-contract / pr-contract` and `gate` (which follows it), red at `74a57885a3`: `figure_block.py verify` refused the `scope-line` block, rendered at `59070bb608` before `mutation-autofix` committed `74a57885a3` on top (`block scope-line names head=59070bb6083f ... this run is head=74a57885a3ef`). Repaired by re-rendering the block at this head (`figure_block.py refresh`, run by `body_push.sh`). Cheaper detector: none earlier than the gate that found it. The stale block was made by a bot commit on CI after the body was set, and `pr-contract` is the first run that reads the body at the new head; locally the same verify takes seconds, but no seat runs between the bot commit and that check.

## Unpinned sites

The 12 sites `tools/pr/ci_predict.py` lists (`slab_seed.py` and `coordinator.py:if not slab_sensed`) are each killed by the block: the diff drive above prints no `SURVIVED` line for any site it drafts, and the three BOOLOP sites it does not draft were driven by `mutant_run.py --spec` (`and` to `or`) at the same tree, each `KILLED`; each is left to `mutation-autofix`, whose lane mutates `custom_components/`. `slab_seed.py:59 RETURN_DEL` is triaged equivalent in `tests/mutation_ledger/survivor_triage/`.

- `custom_components/heatpump_optimizer/coordinator.py:6848 GUARD_OFF`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:38 CMP_BOUND`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:38 RETURN_DEL`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:48 RETURN_DEL`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:53 GUARD_OFF`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:55 GUARD_OFF`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:57 GUARD_OFF`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:68 BOOLOP`: pinned by mutation-autofix; killed locally by the block (`mutant_run.py --spec`, `and` to `or`: `KILLED`, beside `SURVIVED NULL`)
- `custom_components/heatpump_optimizer/slab_seed.py:68 GUARD_OFF`: pinned by mutation-autofix; killed locally by the block (the diff drive)
- `custom_components/heatpump_optimizer/slab_seed.py:82 BOOLOP`: pinned by mutation-autofix; killed locally by the block (`mutant_run.py --spec`, `and` to `or`: `KILLED`, beside `SURVIVED NULL`)
- `custom_components/heatpump_optimizer/slab_seed.py:92 BOOLOP`: pinned by mutation-autofix; killed locally by the block (`mutant_run.py --spec`, `and` to `or`: `KILLED`, beside `SURVIVED NULL`)
- `custom_components/heatpump_optimizer/slab_seed.py:92 RETURN_DEL`: pinned by mutation-autofix; killed locally by the block (the diff drive)

## Forward-carry

none

## Friction

none

