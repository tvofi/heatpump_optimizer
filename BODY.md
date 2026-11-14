R10-HOTFIX-BOOST-FLOW-CEILING: a production hotfix for a defect the owner (tvofi) reported on 2026-11-13 from his v7.1.15 install, a Tuya Rotenso Windmi under Pump duty control at Control with a flow set-point. After he released the stuck set-point by hand (R10-HOTFIX-FLOW-SETPOINT-STUCK), a live space boost wrote 41, then 43, and then rose gradually to 53 °C, instead of his maximum. His direction, verbatim: "it should not be hard coded to 55 but rather set at the maximum value (if sensible, otherwise today's gradual rise is ok)". On "sensible": "in a control and comfort sense".

This branch is stacked on the R10-HOTFIX-FLOW-SETPOINT-STUCK handoff head 90eb45f69f and merges after it.

**Cause.** A space boost and the global boost mode change the step's duty (`pump_arbiter._planned_duty`) but not the level the flow set-point maps. `_flow_target` mapped the plan's own `power_schedule` level through `thermal_model.flow_setpoint_for_level`. A boost over a step the plan books at a partial positive power therefore wrote floor + fraction × (ceiling − floor), and the floor (measured inlet + lift) climbed as the system water warmed. That is the gradual rise the owner saw. Only an idle step (level ≤ 0) or a step at the band top gave the ceiling. `boost.overlay` sets the action's power to the maximum, but the arbiter does not read the action's power: only the system-identification experiment overrides the plan's level. Latent since 0a58990088 (R9-SW-6, first shipped in v6.7.17), which made the set-point follow the planned level.

**Repair round (review verdict held at 7db7de155f; CI red at the pull-request head 9e02464877).** The delta from the reviewed head:
- the repaired lower branch merged in;
- #3404's harness M03 re-anchored on this branch's `boosted=False` arm line;
- one unit of `coord_footprint` paid (see `## Architecture score`);
- the pins and one equivalent-survivor triage.

No other production change: the payment removes `_space_boosted` and the `water` local and reads the same fact inline in `desired()`. The pump-duty arbiter block prints `ALL 61 FEATURES BLOCK PASSED` at this head.

## Design

**What a boost writes.** `_boost_ceiling_c(inp)` decides the target: the set-point entity's own maximum, capped by a heating ceiling (`flow_heat_c`) set to anything but its 55 °C default and by the controller's upper-limit sensor (`space_setpoint_high_limit_entity`, read through the `_setpoint_limits_c` the feedback loop already uses) where it reads. The maximum and the cap are both in the entity's own terms, so a return target is not moved: no offset is applied twice. The boost keeps following the planned level, as before, when the maximum does not read, sits at or below the gate, or sits above `FLOW_HEAT_C_MAX`. That constant is 70 °C, the options flow's own upper bound for `flow_heat_c`. It was a literal at config_flow.py and is now named in const.py and used there too. An entity reading 80 or 100 (a generic number helper) is no heating-flow set-point to drive to its top.

**Explicit versus default `flow_heat_c`.** An absent key reads as `DEFAULT_FLOW_HEAT_C`. `tests/config_flow_steps.py` proves that an untouched options page changes nothing (`_ABSENT_FALLBACKS is exactly the proven set`), which requires a stored default to behave exactly like no setting. A first cut that read the key's presence as "explicit" broke that proof (2 of 580 failed: `flow_heat_c` listed but unproven). So the ceiling caps a boost when it is anything but the default. The one thing lost: a person cannot cap a boost at exactly 55 °C through this option. 54.5 °C, or the controller's upper-limit sensor, does it. An upper-limit sensor reading at or below the gate leaves no heating value and is ignored, as the feedback loop's bounds ignore it.

**The seam is the level.** `_level_kw(inp, now, boosted)` is the one owner of the level a heating step maps:
- the experiment's commanded power, where the action is the experiment's;
- the band top under a boost with a ceiling to write;
- otherwise the plan step's level.

`_flow_target` maps that level with the boost's ceiling in place of the configured one. At the band top, `flow_setpoint_for_level` gives frac = 1 and returns the ceiling exactly, so "the maximum at once" and "the level at the band top" are the same write. `_bounded` then clamps it to the entity's range as for any heating write. `_space_boosted(coord, inp, now)` reads the fact from the live boost record and `inp.mode == MODE_BOOST`, only for a water set-point, so a caller with no coordinator on an indoor set-point (the °F checks) reads nothing. `_space_target` takes it as a required keyword, so every caller states it.

Two alternatives were refused:
- A special case at the write would bypass `_bounded`'s `lo`/`hi` and give the boost row a second formula.
- Reading the overlaid action's power would follow the cycle's snapshot, which lags the one-minute tick.

**Is stepping straight to the maximum sound control and comfort? Yes, on this evidence:**
- (a) Control. The arbiter's premise is that the set-point is a power command. `_full_draw_c` says "a supply target at the ceiling sits far above the water, so the pump may draw its top". The `FLOW_HEAT_C` comment says the heating set-point is high so "the pump's own water thermostat never cuts a planned heating step short", and that the supply "settles where the emitters take the pump's output". A higher target therefore buys the nameplate draw a boost is for (README: "apply maximum heat ... for two hours") and fewer thermostat cut-outs, not water overshoot.
  - The minimum run and minimum pause (supply_hold.py) govern only the supply switch, and `supply_hold._passes` exempts a boost.
  - The power-feedback loop is off under a boost (`_feedback_on`).
  - No set-point ramp exists on any path to protect: the gradual rise was a side effect of the partial level, not a mechanism.
- (b) Comfort. A boost lasts `boost.BOOST_HOURS` = 2 and expires on its own. On a flow or return set-point nothing trims it on the room temperature (the action's comfort-ceiling set-point reaches only an indoor-unit entity), and the model has no emitter limit. A step to the maximum can therefore overshoot the room target within the two hours. That exposure already existed at the fixed 55 and is the documented intent. The owner ruled it out of scope today (see Forward-carry). The guards a person controls are `flow_heat_c` set off its default and the upper-limit sensor; docs and the option's help text say to set `flow_heat_c` on a low-temperature floor heating.

**Docs.**
- docs/configuration.md: what a boost writes, under Pump duty control and in the `flow_heat_c` row.
- `flow_heat_c` help text in strings.json, en, sv and de.
- The sentence "Boost mode writes Heating + DHW with the heating-flow ceiling (55 °C, or `flow_heat_c`)" no longer holds and is corrected.
- README.md's "Boost Space Heating ... apply maximum heat on that channel" is now true and stands.

**Re-pinned, by name.** On the arbiter fixture's entity, whose maximum is 63, three checks pinned a boost writing 55. They now pin 63:
- `the global boost mode writes Heating + DHW and the set-point entity's maximum, 63 ...`
- `a boost writes its own single duty where the pump offers it ... a space boost writes the set-point entity's maximum, 63 ...`
- `R10-HOTFIX-FLOW-SETPOINT-STUCK: a boost over an idle step writes the entity's 63 maximum ...`

## Release note

### A space boost writes the set-point's maximum on every step (R10-HOTFIX-BOOST-FLOW-CEILING)

Under Pump duty control at Control with a flow or return set-point, Boost Space Heating and the global Boost mode used to write the full heating flow only on steps the plan left idle or booked at full power. On a step the plan booked at part power they wrote a set-point between the floor and the ceiling that rose slowly, for example 41, then 43, then 53 °C. Both boosts now write the set-point entity's own maximum on every step they cover. A heating flow ceiling set to anything but 55 °C, and the controller's maximum set-point sensor when configured, cap it. An entity whose maximum cannot be read, or one above 70 °C, keeps the previous behaviour.

## Root cause

Root cause per dev/governance/rules/defect-root-cause.md: the defect reached a release (v6.7.17 through v7.1.15).

- **Cause.** When 0a58990088 (R9-SW-6, 2026-10-06) made the flow set-point follow the planned level, it changed what a boost writes, and it covered only one of the two cases. Its `flow_setpoint_for_level` docstring states the idle case ("a boost over an idle plan still holds heat_c") and not the partial one. The boost changed the duty, but the level stayed the plan's.
- **Why the existing test passed.** The boost test (`the global boost mode writes Heating + DHW and the heating flow ...`, from 06bd2452f8, 2026-09-27) predates level-following. When it was written, any heating step wrote a fixed 55, so an idle plan was a full test. It stayed green after R9-SW-6 for two reasons, either sufficient: its plan is idle (`duties="--"`), and its `_PaCoord` fixture carries no `max_electrical_power`, so the band is not ready and the slide is skipped on every plan.
- **The cheaper detector.** It is the check added here: a boost on a step booked at a partial level with the band ready, for both boost surfaces, inside the existing pump-duty arbiter block. No new script or job.
- **Process state.** Nothing asked that a change to the level mapping re-run the duty rows (boost, experiment, comfort) on a partial level. Accepting the idle-only test was not a recorded decision: the test was right when written and went stale when the mapping changed under it. No separate countermeasure is proposed; the orchestrator decides whether a root-cause seat runs beside this fix.

## Head

72db7df7a0b41b1a238a01e7cb59eebaa5009437

The reviewed head was 7db7de155fef49a36118c10ca5747b1804babf32; this head fast-forwards it. Stacked on 2d99a7b04b4fff4db0b4168c913882121b2825c6 (the repaired R10-HOTFIX-FLOW-SETPOINT-STUCK handoff head, merged in); the merge base with origin/main is 154dbb4c61. `git merge-tree --write-tree origin/main HEAD` exits 0.

## Mutation proof

Failing first. Commit d6b439956e adds the partial-step boost check before any code. At it, the pump-duty arbiter block (`tools/audit/seat/features_block.py` from `R.section("pump-duty arbiter — mode and set-points per plan step` to `_pa_subs = _PaCoord(`) printed `1 of 59 FEATURES BLOCK FAILED`, with a channel boost and the global mode both writing `[42]` on the partial 1.0 kW step. At the head the block prints `ALL 61 FEATURES BLOCK PASSED`, and `tests/config_flow_steps.py` prints `ALL 580 checks PASSED`.

`python3 tools/audit/seat/mutant_run.py --diff 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1...HEAD --cmd 'bash <three blocks>'` diffs from the stuck-set-point head this branch stacks on. The command runs three blocks: the arbiter block, the water-setpoint feedback seam block (`# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380` to `_fb_floor = _fb_sim(clamp=(26.4`), and the R10-CEILING-PROBE block (`R.section("R10-CEILING-PROBE: the experiment` to `R.section("R10-PROD-RESIDUE-PINS`, with its prelude from `features_block.py --emit-prelude`). It generated 36 mutants at 20b310b063 (the same code as this head; later commits add checks and drop two pins) of the added production lines (pump_arbiter.py, const.py, config_flow.py). 34 are killed and 2 survive, both equivalent:

- `_boost_ceiling_c`'s `_gate_floor_c(...) < high` moved to `<=`. At `high` equal to the gate, the entity's own range clamps every heating write to the gate whichever branch runs, so no input can tell the two apart.
- `_arm_space`'s `_space_target(..., None, boosted=False)` with `boosted=True`. `boosted` reaches only the heating branch of `_flow_target` (duty `space` or `both`), and the arm asks for the baseline row, duty `None`.

Mutants this round's checks were added to kill:
- The upper-limit sensor's `limit > gate` moved to `>=` survived an earlier run. It is killed by the `max 60, limit at the gate` row: the mutant spec run printed SURVIVED NULL, then KILLED.
- The options range's 30 → 31 and `FLOW_HEAT_C_MAX` → `+ 1` survived `tests/config_flow_steps.py` alone. They are killed by `R10-HOTFIX-BOOST-FLOW-CEILING: the heating ceiling the options offer is 30 to FLOW_HEAT_C_MAX ...`, in the same mutant spec run.
- The experiment guard in `_level_kw` is killed by the CEILING-PROBE block.
- The upper bound's `<= FLOW_HEAT_C_MAX` moved to `<` (a second comparator on the same line, which `--diff` does not generate) is killed by the `max 70, the bound` row, in a spec run: SURVIVED NULL, then KILLED.

## Null control

- The same partial step with no boost writes its partial value, below each boost target.
- An entity maximum of 90, or none, leaves a boost on that same partial value.
- With no boost, a band-top step writes the heating flow, 55, and an idle step the gate, 25.
- The power-feedback loop is on for the partial step with no boost and off under the space boost.

The investigator's probe `probe/boost43.py` in the session's `seat/boost-43/` scratch directory (out of tree; the orchestrator holds the path) can be re-run by the reviewer against this head.

## Figures

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

none

## Architecture score

- `coord_footprint` 2505 -> 2506 (this seat's measure at merge base 154dbb4c61 and 416147bb56; CI read 2503 -> 2505 at 9e02464877 before the payment): `desired()` now passes the live boost fact to `_space_target` as a computed argument, `boosted=_flow_unit(inp.config) and (inp.mode == MODE_BOOST or boost.held_for(coord).active(...))`, where the call was a plain delegation the footprint does not charge. The fact needs the coordinator's boost record, and `desired()` is the one function that holds both it and the call. Payment tried: the first cut's `_space_boosted(coord, inp, now)` helper and `water` local charged 2 units (`pump_arbiter._space_boosted:1`, `desired` 7 -> 8); both are removed (commit "read the boost fact inline in desired()"), paying 1 of the 2. A local `boosted = ...` costs the same unit and turns the call back into plumbing, so it pays nothing. Carrying the fact on `ArbiterInputs` would move it into the coordinator's published builder, coordinator.py, held by open pull requests, and charge the builder instead. No payment that improves the architecture exists for the remaining unit (per-function measure: `tools/audit/archscore/metrics/footprint.py`'s `measure`, base and head, the only charged difference being `pump_arbiter.desired:7` -> `:8`).

## Red checks

Each check that was red on a commit of this branch (pull request #3562, head 9e024648777c), answered per dev/governance/rules/defect-root-cause.md:

- `arch-score / arch-score`: `dS -0.0012 WORSENS; unexplained: coord_footprint 2503->2505`. The cause is this branch's boost fact in `desired()`: the `_space_boosted` helper and `water` local, 2 units. One unit paid and one explained under `## Architecture score`. Cheaper detector: `python3 -I tools/audit/archscore/gate.py --base <merge base> --head HEAD --body <body>`, about 2 minutes locally; prepr does not run it. The handoff did not run it, which is why it reached CI. Standing cost: one run per handoff whose diff touches a function handed the coordinator.
- `tests / fast (3.14)`: `tests/doc_claims.py` failed `no user page carries a history phrase outside a reasoned exemption` on the "as before" in docs/configuration.md, a sentence the lower branch (#3561) added. It is fixed there and merged in here. Cheaper detector: `tests/doc_claims.py` itself, 9 s; it is answered in full in #3561's Red checks.
- `tests / mutation`: REFUSED, 21 unpinned sites added by this diff: 6 from #3561, which that branch now pins, and 15 of its own. The sites left at this head after the payment are now settled by `python3 tests/mutation_table.py --pin-killed --base origin/main` (features.py, config_flow_steps.py, guard_pins.py). Of 13 mutants, 11 are pinned killed. The two on the range test's line share one anchor: its `<= FLOW_HEAT_C_MAX` comparator is killed, and its gate comparator lives and is equivalent. That anchor is triaged `equivalent` in tests/mutation_ledger/survivor_triage/, with the reason. `ci_predict.py --base origin/main` now predicts no red. Two pins this branch's rewrite made stale (`_space_target` RETURN_DEL 268586e3, `desired` GUARD_OFF 0082e8a4) were already deleted. Cheaper detector: ci_predict's ADDED UNPINNED lines, printed as a WARN at the handoff. The body answered them "pinned by mutation-autofix", which the next row shows could not happen.
- `tests / mutation-autofix`: AUTOFIX skip-measure-failed. The shard jobs' baseline found `tests/doc_claims.py` red (the same sentence), so no mutant's verdict meant anything and no bot commit followed. No separate detector exists: it is the doc_claims red above.
- `governance / instrument-self-tests`, `tests / briefs`, `tests / nightly-status`: red on main commits that the pull-request branch's merges of origin/main brought into its ancestry, not on any commit of this diff. For example, `governance / instrument-self-tests` is red at main 154dbb4c61 itself. They grade `main` and are the orchestrator's there (`defect-root-cause.md`, Enforcement).
- `pr-contract` and `gate`: red at 9e02464877, aggregating the reds above. This section answers them.

## Forward-carry

- On a flow or return set-point a space boost is bounded only by its two-hour window (`custom_components/heatpump_optimizer/boost.py`, `BOOST_HOURS`): nothing trims it on the room temperature, and the model has no emitter limit, so a boost can overshoot the room target (pre-existing at the fixed 55 °C; a design question for the owner, not a hotfix). Carry: dismissed: owner ruling 2026-11-13, I need no further boost temperature trim

## Friction

none
