R10-SETPOINT-BOOST: a heating floor above the gate, a draw window that knows what capped it, and whole-degree set-points

Part of #201. Closes no filed issue: the group comes from the owner's v7.0.1 report (tvofi, 2026-10-19): "now heating slots are planned with a flow temperature of only 25 degrees set instead of 35 before the fix". Builds on #2445 (R10-SETPOINT-POWER) and on #2065 (live power clamp 7a, owner decision on #201 comment 6067353918 item 3).

The diff fixes three defects on installs whose pump is driven through a flow set-point. It changes no solve: every plan is byte-identical at the merge base and the head (Null control).

- **A. The heating floor equalled the off value (thermal_model.py, pump_arbiter.py).** A step that does not heat writes the gate, `FLOW_GATE_C` (25 °C) or the entity's own minimum. #2445 made the floor of a heating step `inlet + FLOW_MIN_LIFT_K` and bounded it at the gate. On a tank at or below 20 °C, a heating step at the floor therefore wrote exactly the gate: the command for "heat at the floor" and the one for "off" were the same number. On the owner's install the export shows 25.0 written and a planned space step that the pump left idle. `modulation_floor_flow_c(inlet, gate)` now lifts from the higher of the inlet and the gate. The arbiter's `_gate_c` is the one owner of the gate value: the idle write, the floor's anchor, and `flow_command`'s report all read it.
- **B. The draw window learned the set-points it was written (draw_range.py, store.py, accuracy.py, pump_arbiter.py, one argument in coordinator.py).** On a set-point-driven install the metered draw is capped by the set-point the arbiter writes. #2065's window read every under-draw as evidence that the configured maximum was overstated, so it engaged on draws that only show the commands. The owner says the real maximum is near 3 kW and that "the integration has never run or measured the pump at max power". The window also counted the circulation and controller draw (about 0.3 kW on this pump, above `RUNNING_FLOOR_KW`) as runs. Now:
  - each sample stores the flow set-point the arbiter held and its ceiling, `pump_arbiter.flow_command`. That is `None` unless the arbiter commands a flow set-point under Control on an install whose plan does not write the compressor frequency;
  - evidence that the pump draws less than asked, and the 90th-percentile maximum, come only from samples written at the ceiling or not commanded at all;
  - intervals held at the gate with no hot water asked feed a learned idle draw, and readings at or below 1.25 times it are not runs;
  - a record stored before commands existed is dropped by the first commanded sample, the same way a changed configuration drops one, and kept by an uncommanded one.

  Nothing reads `planned_range` in a solve: decision 6067353918 item 3's application (7b) is **not** in this PR. Censoring meant it would have locked the bug in: a low set-point gives a low draw, which gives a clamp, which gives a low set-point.
- **C. Decimal set-points (inputs.py, pump_arbiter.py, coordinator.py's module-level valve helper).** tvofi: "Only write whole integer set-points to the heat pump; mine (and many others) don't accept decimals." `inputs.write_setpoint`, the one service call, now sends the value on the entity's step. The step is read from `target_temp_step` (climate) or `step` (number), defaulting to 1.0, and a whole value goes out as an integer. `quantise_setpoint_c` rounds by meaning, in the entity's own unit after #2285's conversion: a heating floor up, the gate and the ceiling down, levels in between to nearest, monotone in planned power. The arbiter's `_bounded` and the smart_write valve target (a cap, so down) call it. The arbiter's former fixed half-degree rounding is gone. The default step is 1.0 on every install whose entity states none, so a write that was a tenth or a half before is now whole. Four existing checks pinned decimals and now expect whole degrees in the entity's unit: the GCHV hot-water gate ("40", not "40.0"), the degF delivery cells (21 °C reaches a degF entity as 70, not 69.8), the smart_write valve cap (23.5 °C goes out as 23, or 74 on degF), and the degF minimum clamp (a 44.6 °F minimum gives 45 °F, the first whole degree inside the range). One fixture of an existing check also moved. #2445's `_SP_READ` tank readings went from 22/24/26/31 to 27/29/32/36 °C, so each anchor keeps its own lift above the gate. The sub-gate case is pinned separately ("an 18 degC tank ..."). `repairs.py`'s disinfection-floor write also goes through `write_setpoint` at nearest. On a °F entity, floors of 48/53/58/63 °C go out up to 0.22 K low, which is inside `MIXING_VALVE_WRITE_EPSILON` (0.25), so the notice still clears.

Alternatives, and why each lost:
- **Wiring `planned_range` into the solve (7b)**, the first proposal. Refuted by the owner's evidence: the export's window holds no sample written at the ceiling, so its maximum is the set-points, not the pump.
- **Raising the floor to `FLOW_HOLD_C` (35 °C).** Pre-#2445 samples asked at p_min under 35 °C drew a median of about a third of p_min too, so it re-introduces the old command without separating it from the gate.
- **Keying the latch on the ceiling.** A config tuple holding the ceiling clears the window whenever the entity's range is briefly unreadable. A per-sample command, plus a one-way legacy drop, does not.
- **Quantising per caller.** Each caller would need its own rounding, and the service call would still send whatever arrived. Rounding happens once at the write owner (nearest, idempotent), and the arbiter's bounding states the direction.

## Head

`890fba053bdf3b3c7611f6a860be528665278259`, branched from origin/main `4a3cbcf62e6f5e7b6594d376d714388caf2915cf` (v7.0.1 plus #2460). Every figure below was taken at the head unless a line says merge base, which is a `git archive` of `4a3cbcf62` in seat scratch. `date -u`: 2026-10-19T23:52Z.

## Mutation proof

Hand mutants, `$SCRATCH/mut/mutants.py` (sha1 b2c6e6b7d7576e08c2ac2c08c6bdee347259b7d0). Each one is applied to a `git archive` copy of the head and run through `tools/audit/seat/features_block.py` over the draw_range 7a block and this group's block, then restored; `diff -rq` against the head reads identical afterwards. M0 (no mutation) is `ALL 68 FEATURES BLOCK PASSED`. Every mutant exits 1.

| Mutant | Production edit | Goes red |
|---|---|---|
| M1 | `modulation_floor_flow_c` ignores the gate | "a step that heats at the floor writes strictly above the gate ...", "an 18 degC tank writes the gate plus the lift at the floor, not the gate" |
| M2 | `_flow_target` passes no gate to the floor | the same 2 |
| M3 | every sample counts as ceiling-commanded | "a window commanded below the ceiling never engages and learns no maximum ..." |
| M4 | idle-level readings count as runs | "readings at the learned idle draw are not runs ..." |
| M5 | `fold` learns no idle draw | "a gate-held interval folds one idle reading ..." |
| M6 | the coordinator passes no command to `fold` | "the per-cycle fold records the held flow set-point and its ceiling under Control" |
| M7 | a frequency-writing install counts as commanded | "null control: Observe, an indoor set-point, or a plan that writes the compressor frequency ... records no command" |
| M8 | legacy evidence is kept by a commanded sample | "a record stored without commands is dropped by the first commanded sample ..." |
| M9 | the service call rounds to tenths again | "no decimal reaches the service call on an entity that states no step ..." |
| M10 | the floor rounds to nearest | "a floor rounds up, a ceiling down ...", "a Fahrenheit entity is quantised in Fahrenheit ..." |
| M11 | the ceiling rounds to nearest | "a floor rounds up, a ceiling down ..." |
| M12 | the entity's step attribute is ignored | "no decimal reaches the service call ..." (the 0.5 and 0.1 step arms) |
| M13 | quantised in °C on a °F entity | "a Fahrenheit entity is quantised in Fahrenheit ..." |
| M14 | commands are not stored | "the commands and the idle readings survive the store ..." |

The ledger record of these sites is `mutation-autofix`'s (`dev/governance/rules/ci-autofix.md`). The 20 STALE PINs `ci_predict.py` names (the edited lines in `draw_range.py`, `inputs.py`, `pump_arbiter.py`, `thermal_model.py` and `_valve_write_problem`) are deleted by hand in this diff, so the bot pins the edited lines afresh.

## Null control

- **No solve moves: plans are byte-identical at the merge base and the head**, on 16 synthetic installs at a spread price day and at its flat mean (32 plans, sha1 per plan). Measured with `dev/audit/harnesses/r10_setpoint_boost.py` at both trees and compared with `diff`. The cells are UA scale 0.6/1.7, a 750 L manual-valve buffer or none, hot water off/on, set-point-driven (levels ship rounded) or duty-cycling. The flat-price null holds as identity and savings against the always-on baseline are unchanged on every cell, because none of A, B or C is read by a solve.
- **A, nulls:** a tank above the gate keeps its own lift (26 °C writes 31, 30 °C writes 35); full power keeps the ceiling; no inlet keeps `FLOW_HOLD_C`; an idle step still writes the gate.
- **B, nulls:**
  - an uncommanded window (Observe, an indoor set-point, Off, the pump's own controller) engages at the same percentiles as before the guard;
  - a ceiling-commanded window whose draw disagrees with the ask engages, and its 90th percentile is the maximum;
  - a frequency-writing install, which can duty-cycle and whose draw is the plan's echo, records no command, so its window is unchanged.
- **C, nulls:** an already-whole write sends the same whole number; a 0.5-step entity keeps halves; a 0.1-step entity keeps tenths.

## Figures

`$SCRATCH` is this seat's scratch directory. `$EXPORT` is the owner's private diagnostics export, read locally only; only aggregates are stated and nothing from it is committed. Commands run with `PYTHONPATH=tests/hastub:custom_components:tests`.

- `python3 dev/audit/harnesses/r10_setpoint_boost.py --no-solves`, head then merge base:
  - `floor: cells 155 heating floor at or below the gate 0` at the head; `... 63` at the merge base (inlets 10-40 °C by entity minimum none/20/25/28/30).
  - `window plan:` the owner-shaped synthetic pump (configured 1.5-5.0 kW, true maximum 3.0 kW, idle 0.30 kW, draw a function of the written set-point and the tank). At the head: `engaged False observed (0.8999999999999999, None) idle 0.3 planned None`. At the merge base: `engaged True observed (0.8999999999999999, 2.034) idle None planned (0.8999999999999999, 2.034)`. The merge base learns a 2.03 kW "maximum" for a 3.0 kW pump.
  - `window probe:` every sample written at the ceiling. `engaged True observed (2.9399999999999995, 3.0)` at both trees. This is what R10-CEILING-PROBE needs, and the guard admits it.
- `python3 dev/audit/harnesses/r10_setpoint_boost.py` (with solves), head and merge base, `diff` of the per-plan sha1 lines: identical. Relaxed-start control (#2445), by each cell's own objective: `spread: cells 16 relaxed start objective lower 8 higher 0 identical plan 8` and `flat: cells 16 relaxed start objective lower 0 higher 0 identical plan 16` on this seat. The reviewer's machine reads `flat: cells 16 relaxed start objective lower 2 higher 0 identical plan 14` at both trees: cells 0.6/750/no hot water/rounded and 0.6/none/no hot water/rounded, each with a relaxed delta of -1.814 and a different plan sha1 from this seat's. So the flat-day relaxed-start figure depends on the solver environment. It concerns #2445's relaxed start, not this diff: on each machine the base and head plans are byte-identical. The 8 lower are the set-point-driven cells, and the duty-cycling cells are identical by construction. On the spread day the near-floor share of space kWh in steps above the median price is 0.000 on all 16 cells, and the cheapest quarter takes 0.948-1.000 of space kWh. `failures 0`.
- Owner export, aggregates computed locally from `$EXPORT`:
  - the draw window holds 54 running samples and the highest ask is just under p_max, which the pre-#2445 mapping writes at about 54 °C, so **no sample was written at the ceiling**;
  - 41 of 54 samples were asked p_min, and the last 24 drew 0.33-0.73 kW;
  - the written set-point is 25.0, equal to `FLOW_GATE_C`;
  - the samples carry no timestamp or set-point, so pairing a draw with its write was not possible from the export.
- Local green at the head:
  - `tests/features.py`: `ALL 4247 FEATURE CHECKS PASSED`;
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`;
  - the light scripts `scope.run` names: each exits 0, `tests/entities.py` reads `ALL 2351 ENTITY CHECKS PASSED` and the typing ruler `ALL 9 typing-ruler checks PASSED` / `ALL 12 typing-ruler source checks PASSED`;
  - `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against 4a3cbcf62e6f`.
  - `tests/backtest.py`, `tests/golden.py`, `tests/stress.py`, `tests/optimality.py`, `tests/arch_score_head.py` and the two `card*.mjs` are CI's.

## Measured limitation (not fixed here)

- **The mapping reads the water temperature only at the floor.** The floor is relative to the inlet, the ceiling is absolute, and the levels between are linear in configured power. A pump's draw follows the set-point minus the water temperature, and it saturates. So the same level commands a different power at every tank temperature, and the gain between set-point and draw is unidentified on a set-point-driven install. Its effect is booked-vs-delivered heat, which R10-DEMAND-OVERBOOK's brief names. No roster group owns identifying the set-point-to-draw gain itself; R10-DEMAND-OVERBOOK is the nearest owner, and the orchestrator may re-route it. Carry: R10-DEMAND-OVERBOOK
- **Reaching the real maximum** needs either p_max configured at its true value (an owner question for tvofi, who is adjusting the config) or a deliberate ceiling probe. The probe is R10-CEILING-PROBE, folded into the cheap-night system-identification experiment (`sysid.py`). B is its prerequisite: the window now admits ceiling-commanded evidence only. Carry: R10-CEILING-PROBE

## Architecture score

n/a: no gate metric rises. `python3 tools/audit/archscore/vector.py` at the merge base and at the head returns the same value for every key (`coord_footprint` 2498 at both). `tests/structure.py` passes at the recorded budgets, `seam_cut_total` 719 included. `functions_cc_over_15` was paid by moving the idle-record parse out of `DrawRange.from_dict` into `_stored_idle`. `coordinator.py`'s class gains no line: the fold call takes one more argument on its existing line. `flow_command(coord)` is plumbing, and its decision lives in `_flow_command`, which is not handed the coordinator. The valve helper's rounding is in a module-level function.

## Red checks

- `arch-score`: red at the earlier pushed head `a3aee5945`, "coord_footprint 2498->2505". The new `pump_arbiter.flow_command(coord)` was handed the coordinator and held 7 logic statements. Repaired at this head: `flow_command(coord)` is plumbing only (an alias of `coord.arbiter_inputs()`, an alias of `state_for(coord)`, and a delegating return), and the decision moved to `_flow_command(inp, state)`, which is handed neither. `python3 tools/audit/archscore/vector.py` at the merge base and at this head reads `coord_footprint` 2498 at both, and no key of the vector differs. Cheaper detector: none is missing, because `vector.py` runs locally and I had not run it before the first push. Standing cost: one local run per head that touches a function the coordinator is handed.
- `pr-contract`: red at the PR head `345cdf586`. `carry_audit.py` read 3 unrouted items: the two under `## Measured limitation` and a `## Forward-carry` that said "none" while naming owner decisions. Each item now ends in `Carry: <group>`. Measured on this body: against `origin/handoff/audit-r10-roster` (`d8250cd44`) it reads `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`. Against `origin/main` it reads `CARRY-AUDIT: 6 finding item(s): 0 routed, 0 unrouted, 6 bad destination(s)`, because none of the four groups is on main's roster yet. So `pr-contract` stays red until the roster PR merges. Cheaper detector: `python3 -I tools/audit/carry_audit.py check --body` runs locally in seconds. prepr did not run it on this body, so the standing cost is one local run per body.
- `mutation`: red at `a3aee5945` and predicted red at this head, because the added sites under `## Unpinned sites` have no ledger pin until `mutation-autofix` pins them on CI's run after the push. Cheaper detector: none is missing, because `tools/pr/ci_predict.py` already names every one locally before the push, at the cost of one local run. The hand mutants M1-M14 above kill each function's behaviour in this group's block. The red clears when the autofix pins land (`dev/governance/rules/ci-autofix.md`).

## Forward-carry

The destinations are groups in `dev/programme/rosters/wave-r10-groups.json` as it stands on `handoff/audit-r10-roster` (`d8250cd44`), which a roster PR into main is about to land. Until it merges, `carry_audit` against main's roster reports these as bad destinations, and this PR merges after it. Each item below routes to one of them:

- **Idle draw can absorb compressor draw.** If the gate is not truly off (the compressor runs at the gate on a cold inlet), the learned idle median takes in compressor draw. The reviewer measured that at a gate-held draw of 1.4 kW, 24 of 72 running samples drop and the low end moves from 1.35 to 1.8 kW. `follows_ask` uses the same filter. The ceiling probe's controls should include a gate-held draw above idle. Carry: R10-CEILING-PROBE
- **Demand is over-booked about 8 times.** The plan books about 38 kWh/day electric for space against a metered October average of about 8.6 kWh/day for space and hot water, and the learned UA implies far more loss than metered delivery supports. Root-cause by replay on synthetic installs. Carry: R10-DEMAND-OVERBOOK
- **The manual-valve buffer is not used as a store.** In this PR's census, a 750 L manual-valve buffer publishes the same plans as no buffer, and the tank stays at its start temperature. Carry: R10-BUFFER-STORE
- **The COP model has no part-load or burst term.** It keys only on the outdoor temperature and the tank or weather-curve flow, so neither tvofi's near-floor hypothesis nor the short-burst one can move a plan. Measure first. Carry: R10-COP-PARTLOAD

## Unpinned sites

`python3 tools/pr/ci_predict.py --base origin/main` lists 56 added lines, which are 59 mutation sites: three `CMP_BOUND*2` lines count twice. CI's `mutation` job at the earlier head `a3aee5945` counted 58 over 55 lines. The extra line here is the `RETURN_DEL` on `flow_command`'s plumbing return, added by the arch-score repair below. `mutation-autofix` pins each one on CI's run. The hand mutants above show that this group's block kills each function's behaviour; M6 covers the plumbing return as well:
- `custom_components/heatpump_optimizer/coordinator.py:669 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:77 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:79 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:82 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:85 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:87 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:123 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:123 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:138 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:140 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:145 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:154 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:154 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:159 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:160 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:170 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:170 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:185 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:186 CMP_BOUND*2`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:188 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:188 CMP_BOUND*2`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:188 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:201 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:202 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:210 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:273 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:273 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:292 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:302 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:302 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:317 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:317 CMP_BOUND*2`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:385 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:385 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:432 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:446 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:446 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:446 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:457 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:458 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:490 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:491 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:492 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:493 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:495 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/inputs.py:532 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:539 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:560 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:587 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:589 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:622 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:711 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:718 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1469 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1472 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1472 RETURN_DEL`: pinned by `mutation-autofix`

## Approval

Merged under the mandate on #201, comment 6175172275, quoted verbatim: "MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z"

## Friction

none
