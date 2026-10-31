R10-HOTFIX-LEARNER-INPUTS: live user finding (tvofi, 2026-10-30), measure first, plus the owner's reset request. The probe at `handoff-body/r10-live-plan-energy` 7c4e639e49214592ef2ef2ddd48df522a3efd2cd traced the owner's ~67 kWh/day plan to an effective UA of 0.641 kW/K: the configured nameplates times a learned `house_heat_loss_scale` of 1.2356 and a learned `lower_floor_loss_ratio` of 1.943.

What lands:

- **(2) A zone-sensor swap voids the learner fitted on it. A defect: measured.** Changing `indoor_temp_entity` voided nothing, and neither did changing `lower_floor_temp_entity`. Evidence fitted against one sensor carried over to a sensor in another place (Figures, harness arm `move`). The thermal-learning payload now records `heat_loss_zone_entities`, the ids of the zone sensors. `_reanchor_house_heat_loss_scale` reads them on load and on snapshot restore, the same path and the same moment as the basis void. A changed id voids that learner alone: the indoor sensor voids the scale, the lower-floor sensor voids the ratio. Voiding sets the value to 1.0 and the samples, and with them the confidence, to 0. The other learner keeps its value and samples verbatim. The rule is `thermal_model.heat_loss_entity_voids` over `HEAT_LOSS_ZONE_ENTITIES`. An added or removed entity counts as a change. A store from before the record, or a key it does not hold, voids nothing, and the next save adopts the ids.
- **(3) The heat-loss reset action, Carry 1 on this group's roster entry (tvofi: "I can't find an option to reset the learners, that should be added asap").** It is a button, **Learning Reset Heat Loss**, beside Learning Reset Comfort Weight, and a service, `reset_heat_loss_learners`, with `entry_id` and an optional `learners` list (`house_heat_loss_scale`, `lower_floor_loss_ratio`; empty means both). Both reach `HeatPumpOptimizerCoordinator.async_reset_heat_loss_learners`. That waits for the store read, calls the same `_void_heat_loss_learners` the sensor swap calls, and saves. The save re-derives the anchors and the basis from the configuration in force. The button then asks for a refresh off the action, as the comfort-weight reset does. The service awaits one. The plan re-solves at once on the reset values. `restore_learned_snapshot` is unchanged.
- **The owner's install needs the reset, not the swap rule.** The owner's store was written before `heat_loss_zone_entities` existed. On the first load it adopts the ids now configured and voids nothing (check `a store without recorded zone sensors keeps both learners and adopts the ids`). The 1.2356 and 1.943 fitted before the move therefore stay until the owner presses the button or calls the service. From then on, any later swap voids by itself.
- **(1) An estimated power entity: not recognisable, not built.** The rule is `thermal_model.heat_loss_basis`: the basis is `metered` exactly when `CONF_POWER_ENTITY` holds an id (`probe_install`: `measured_power=bool(cfg.get(const.CONF_POWER_ENTITY))`). A meter and the pump's own estimate give the same basis (Figures, harness `basis` arms). The read path, `InputReader.read_power_kw`, takes the state's value and its unit and nothing else. The config flow offers any `sensor` with device class `power`. A Home Assistant sensor state carries `device_class`, `state_class` and the unit, and none of them tells an estimate from a meter. So the integration cannot recognise an estimate-class entity from the entity. Only an owner declaration could, which means a new option, a new or lower-trust basis, and a store-basis migration. That is a design decision, outside a measure-first hotfix. How much the owner's estimate overstates is not measurable here: it needs the estimate against a meter over the same days. Both are under Forward-carry.

Design choices:

- **One void path.** `_void_heat_loss_learners(learners, why)` is the only writer the swap and the reset share. It logs one warning per voided learner. The options-service nameplate reset in `async_update_thermal_params` (scale to 1.0, samples to 0) was left on its own two lines. Routing it through the void path raises `seam_cut_total` 422 -> 423 (a new core -> learning call pair). That is a structure budget, and the orchestrator said not to raise any.
- **The other learner is kept verbatim, not re-expressed.** The alternative, after a scale void, keeps the lower zone's product: ratio' = ratio * old scale. It lost because the ratio's Newton step is taken about `lower * scale` (`_async_learn_lower_floor_loss`), so the ratio is relative to the scale in force. Once the scale relearns from the new sensor, a re-expressed ratio counts the scale twice. The brief's control also asks for the other learner untouched.
- **Payment in the coordinator class.** The new method, the reset and the swap call add 21 lines to `HeatPumpOptimizerCoordinator`, against zero headroom on `max_class_loc` and `class_excess_loc`. They are paid with spent re-anchor prose in the same seam. The #86 rationale was restated in four places: `_async_load_thermal_learning`, `_thermal_learning_payload`, `_apply_learner_payloads` and the `_reanchor_house_heat_loss_scale` docstring. It now stands once, in the docstring. The history-only clauses are gone ("v5.7.0", "four prior attempts recorded in dev/archive/backlog.md", "Round 1 of the re-anchor"). One `flow_bias` comment that repeated the T4b comment above it was folded. No budget was raised or re-recorded.

## Head

18a66328950debff47f245bc25d8cd2af4bfdd73, branch `r10-hotfix-learner-inputs`, one commit on merge base cc930cdd1a3cfb005ba7ec557f4451ff5e53e364 (origin/main when the seat started). At 2026-10-30T23:33Z origin/main was at 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447. `git merge-tree --write-tree origin/main HEAD` exits 0, its ledger driver merging `tests/closures.json` as a set, so main was not merged in (`fixer.md` step 6). Every figure below was taken at this head unless a line says otherwise. The two claim files are byte-identical to origin/main.

## Mutation proof

Each mutant is one replacement in a copy of the head 18a663289 (`custom_components/` and `tests/`). The new section of `tests/features.py` was run up to `R.section("Runtime parameter updates")`. Where a line names `tests/entities.py`, it ran in a scratch worktree whose tree is the head's (`git rev-parse HEAD^{tree}` = 6a64898ef563eb9e6c6e014d00f391f09d3748de). The failing check names are pasted.

- Swap gate: `heat_loss_entity_voids`'s `if key in was and (was[key] or None) != now.get(key)` -> `if False` gives 4 FAIL: `a lower-floor sensor swap voids the ratio and leaves the scale intact`, `an indoor sensor swap voids the scale and leaves the ratio intact`, `moving a sensor from indoor to the lower floor voids both learners`, `a reload over the swapped sensor voids nothing more`.
- The record: drop `"heat_loss_zone_entities": heat_loss_zone_entities(ctx._config),` from `_heat_loss_anchors` -> 7 FAIL, the five swap and adoption checks above plus `an unrelated options change keeps both learners verbatim and writes nothing` and `and a second load over the reseeded configuration re-anchors nothing`.
- Void path: drop `self._lower_floor_loss_samples = 0` from `_void_heat_loss_learners` -> 8 FAIL, among them `the reset returns both learners to 1.0 with no samples, and saves it`, `resetting the ratio alone leaves the scale and its samples intact` and `the next fold after a reset starts from the configuration`.
- Reset save: drop `await self._async_save_thermal_learning()` from `async_reset_heat_loss_learners` -> FAIL `the reset returns both learners to 1.0 with no samples, and saves it`.
- Service subset: `learners = tuple(data.get("learners") or HEAT_LOSS_LEARNERS)` -> `learners = HEAT_LOSS_LEARNERS` -> FAIL `the service's learners field resets one learner alone`.
- Service refresh: drop `await coord.async_request_refresh()` from `handle_reset_heat_loss` -> FAIL `the service resets both by default, then re-plans on the reset values`, `the service's learners field resets one learner alone`.
- Button refresh: drop `off_the_action(self, self.coordinator.async_request_refresh())` from `ResetHeatLossButton.async_press`, run `tests/entities.py` -> FAIL `the heat-loss reset button reaches the coordinator, then asks for one refresh`.

## Null control

- The unmodified tree. Base production code (merge base) was run under this head's tests (`custom_components/` from cc930cdd1, `tests/` from the head, without the head's one `_LearnPersist` line that names the new method). Results: FAIL on the three swap checks, the adoption check and the reload check. `an unrelated options change keeps both learners verbatim and writes nothing` passes. Then `AttributeError: 'HeatPumpOptimizerCoordinator' object has no attribute 'async_reset_heat_loss_learners'`.
- The options-change null control in the tests. Changing the outdoor entity and the comfort weight keeps both learners at (1.567, 1.922, 310, 147) with 0 saves, at the head.
- The reset null control. `_learner_snapshot_payloads()` is compared before and after a reset that follows a non-default COP scale (1.13) and comfort evidence (-1.4). Every learner other than the two heat-loss learners is equal. Excluded: their four keys, the zone-total anchor their ratio enters (re-derived on save, as the reset brief asks) and the `updated_at` save stamp. Without the anchor exclusion the check fails on `thermal_learning/house_heat_loss_anchor` alone.
- One learner alone. A ratio-only reset leaves (scale, samples) at (1.567, 310). A scale-only reset leaves (ratio, samples) at (1.922, 147).

## Figures

- Harness `dev/audit/harnesses/learner_inputs_swap.py`. Run as `python3 -I dev/audit/harnesses/learner_inputs_swap.py [TREE]` at the head 18a663289 (TREE omitted) and over a `git archive` export of cc930cdd1 (`custom_components`, `tests`). Stock two-zone house, store written with indoor=`sensor.t6`, scale 1.2356, ratio 1.943, 400 samples each. Columns are (scale, ratio, n_scale, n_ratio, UA kW/K):

```
arm                                    base                                 head
unchanged sensors                      (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.943, 400, 400, 0.3396)
move: indoor=bthome, lower=t6          (1.2356, 1.943, 400, 400, 0.3396)    (1.0, 1.0, 0, 0, 0.19)
lower only: lower=t6                   (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.0, 400, 0, 0.2348)
null: outdoor + comfort_weight edit    (1.2356, 1.943, 400, 400, 0.3396)    (1.2356, 1.943, 400, 400, 0.3396)
zero evidence (1.0, 1.0, n=0), move    (1.0, 1.0, 0, 0, 0.19)               (1.0, 1.0, 0, 0, 0.19)
on the clamp (3.0, 3.0, n=400), move   (3.0, 3.0, 400, 400, 1.11)           (1.0, 1.0, 0, 0, 0.19)
basis: no power entity (null)          commanded                            commanded
basis: power = a revenue meter         metered                              metered
basis: power = the pump's own estimate metered                              metered
```

  Both ends of the input range: an install with zero evidence is unchanged by a move (nothing to void), and one on the 3.0 clamp lands on the configuration.
- What the owner's reset buys, on the owner's nameplates. Taken from the probe's own table at 7c4e639e4, not re-run here; this PR does not change the solve. Arm 1 (learned scale and ratio) plans 51.67 kWh at UA 0.641. Arm 4 (configured nameplates, no learned scale or ratio) plans 24.00 kWh at UA 0.330. Arms s1 and s2 split it: scale alone +6.7 kWh, ratio alone +16.8 kWh. The plan after a reset is arm 4's until the learners refit on the new sensors.
- Red tree: a scratch driver (not landed, one `exec` of `tests/features.py` cut before its `Runtime parameter updates` section) was run over two trees. Over base code with head tests: 5 FAIL, then the AttributeError above. Over the head: 14 ok, 0 FAIL in the new section.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at the head printed `MODE: SCOPED -- 31 script(s) run, 2 scoped out.` (`tests/ha_contract.py` scoped out, `tests/layout.py` run_always). `GATE_SCOPE=auto GOLDEN_MODE=drift tests/run.sh` at the head printed `4 TEST SCRIPT(S) FAILED`: `entities.py`, `optimality.py`, `card.mjs` and `stress.py`. Each is this machine's, and each is shown failing the same way at cc930cdd1 under `## Red checks`. Every other script passed, among them `ALL 4619 FEATURE CHECKS PASSED`, `ALL 108 FINITE BOUNDARY CHECKS PASSED`, `ALL 203 checks PASSED` (doc_claims) and `STRUCTURE RATCHET PASSED`.
- `python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED. Before the payment, the coordinator class stood at +21 lines: `max_class_loc` 8086 > 8065 and `class_excess_loc` 17693 > 17672.
- `python3 tools/pr/ci_predict.py` at the head: `no closures, fast, governance or instrument red predicted against cc930cdd1a3c`, and 7 unpinned sites (below).
- `tests/entities.py` locally: 1485 ` ok ` lines on the head's tree, 1482 at cc930cdd1, and no non-fixture FAIL line in either. Both runs then stop on the same `PermissionError: Cannot get task port`, a macOS entitlement in a late check. CI runs the rest.

Class enumeration (`fixer.md` step 8). The rule: the entity keys each heat-loss learner's own freeze consult names, `awk` over `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss` for `_learning_frozen(` (`coordinator.py`), plus the power entity its replay reads (`_replay_gate`'s `CONF_POWER_ENTITY` freeze). Seams returned, each with its disposition:

- `indoor_temp_entity` -> scale: closed in this diff.
- `lower_floor_temp_entity` -> ratio: closed in this diff.
- `indoor_temp_entity` -> ratio (it seeds the upper-zone state the ratio's replay starts from, not the residual): not voided. A design choice: the ratio's residual is on the lower sensor.
- `outdoor_temp_entity` -> both: not voided. A moved outdoor sensor would bias ΔT for both learners; unmeasured. Forward-carry (dismissed with its reason).
- `thermal_power_entity` -> both: adding one earns the `measured_heat` basis, which already voids (`_async_earn_heat_basis`). A swap between two heat meters is not voided. Forward-carry (dismissed with its reason).
- `heat_pump_power_entity` -> both: candidate (1). Adding one voids through the basis order (`commanded` -> `metered`). Removing one keeps evidence by G-ID-3's recorded design. A swap from an estimate to a meter keeps evidence. Forward-carry (dismissed with its reason).

## Unpinned sites

Each was mutated by the tree's own kind (`tests/mutation_table.py`) and killed locally. All are under `custom_components/`, so the mutation-autofix lane pins them after the push.

- `custom_components/heatpump_optimizer/coordinator.py:5180 GUARD_OFF`: pinned by mutation-autofix. Killed: 5 FAIL in `tests/features.py`, e.g. `an indoor sensor swap voids the scale and leaves the ratio intact`.
- `custom_components/heatpump_optimizer/coordinator.py:5183 GUARD_OFF`: pinned by mutation-autofix. Killed: 8 FAIL, e.g. `a lower-floor sensor swap voids the ratio and leaves the scale intact`.
- `custom_components/heatpump_optimizer/coordinator.py:5188 RETURN_DEL`: pinned by mutation-autofix. Killed: the two single-swap checks fail on their one save.
- `custom_components/heatpump_optimizer/services.py:1176 RETURN_DEL`: pinned by mutation-autofix. Killed: `tests/entities.py` FAIL `reset_heat_loss_learners reaches the coordinator and reports what it reset` (`[None]`).
- `custom_components/heatpump_optimizer/thermal_model.py:1488 RETURN_DEL`: pinned by mutation-autofix. Killed: 3 FAIL plus `AttributeError: 'NoneType' object has no attribute 'get'` in `tests/features.py`.
- `custom_components/heatpump_optimizer/thermal_model.py:1500 GUARD_OFF`: pinned by mutation-autofix. Killed: `tests/features.py` exits on `TypeError: argument of type 'NoneType' is not a container or iterable`, raised loading a store with no record.
- `custom_components/heatpump_optimizer/thermal_model.py:1504 BOOLOP`: pinned by mutation-autofix. Killed: 16 FAIL, e.g. `a metered store reloaded metered keeps both learners verbatim`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff cc930cdd1a3cfb005ba7ec557f4451ff5e53e364 HEAD` at the head: `dS -0.0036 WORSENS (inadmissible: coord_footprint 2381->2387)`.

- `coord_footprint` 2381 -> 2387: the six logic statements of the new void path, the reset action and the swap call inside the coordinator. They are the fix's own statements, where the learner state lives (`_house_heat_loss_scale`, `_lower_floor_loss_ratio` and their sample counts are coordinator attributes). The pure part, which entity voids which learner, is in `thermal_model.heat_loss_entity_voids`. Moving the state into its own learner object is the R10-ARCH extraction's, not a hotfix's.

## Red checks

- `mutation`: red by construction on the 7 sites under `## Unpinned sites`. mutation-autofix pins killed sites after the push.
- `arch-score`: the `coord_footprint` rise, explained under `## Architecture score`.
- No CI check has run. In the local scoped gate on an earlier, unpushed state of this branch, four scripts went red because of this diff, and all four are fixed in the head. `finite_boundary.py` failed 3 of 108: `heat_loss_zone_entities` was undeclared in `store.DOMAINS`, now declared. `harness_headers.py` failed 3 of 112: D6 `claims.py` C20 and C21 lacked the new service in its `SCHEMAS` catalogue, which is added, and the outputs are regenerated (`claims_true=123`, `claims_false=0`). `doc_claims.py` failed 1 of 203: the `services.py` docstring said thirteen, now fourteen. `entities.py` failed the README and architecture counts, now updated. The cheaper detector exists and ran: the scoped gate, before any push.
- Not this diff's, and red the same way at cc930cdd1 on this machine (each run in a detached worktree at the merge base): `optimality.py` `one|summer_negative|shoulder: a recorded claim still has a gap (not stale)` (1 of 84 FAILED at both). `stress.py` `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]` (1 of 113 FAILED at both, the same 4.67 vs 3.96). This is a pure `HeatPumpOptimizer` solve, and no optimizer or solve-path line changed. `card.mjs` died on a Node OOM (rc 134) at both, after `tests/plan_view.py`. `entities.py` stopped on the task-port `PermissionError` at both. None of them is CI's canonical environment.

## Forward-carry

- R10-FACTORY-RESET's learners scope: the single void path its brief names is `HeatPumpOptimizerCoordinator.async_reset_heat_loss_learners(learners)`, which waits for the thermal store's read, calls `_void_heat_loss_learners` and saves. Learner names are `const.HEAT_LOSS_LEARNERS`. The caller asks for the refresh, off the action for an entity and awaited for a service (`tests/features.py`'s RC2 rows refuse an entity action that awaits the solve). Its snapshot before the reset must be taken before this call. Carry: R10-FACTORY-RESET
- Candidate (1), an estimated power entity treated as a meter: no Home Assistant attribute tells an estimate from a meter (Figures, `basis` arms), so recognising one needs a new owner-declared option and a basis for it, a design proposal and not a fix. The reset action this PR adds is the owner's remedy once a real meter is fitted. Carry: dismissed: not recognisable from the entity; the orchestrator may put the declaration option to proposal triage
- Power-meter, heat-meter and outdoor-sensor swaps keep fitted evidence: seams of the class above, not voided automatically. Carry: dismissed: the reset action this PR adds is the remedy after such a change, and auto-voiding would also wipe converged learners on a like-for-like sensor replacement, which no measurement here prices

## Friction

none
