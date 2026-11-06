Design review: approve 60d61fcf9d5aa75f8cf194a4a6aa28613c3d5bba

Round 3 (third note). Design SHA unmoved (detached worktree at 60d61fcf). Re-mint of dr-why-now's approve, whose push was refused for topic case; re-verified here.

## Base
- The note's base b88684a2 is an ancestor of origin/main 28482ece. 1449 commits lie between, but their diff over custom_components/, tests/golden/, tests/card*.mjs, tests/features.py and docs/img is only the 7.1.4 stamp: manifest.json and CARD_VERSION 7.1.3 -> 7.1.4, and the `claims-for:` and header lines of both claim files. card_claimed_drift.txt still holds no claims. No cited line moved.

## Prior revise points and carries answered
- Round-1 revise (evidence-plan, card footprint): §6 names it. `node tests/card_drift.mjs --list` prints 45 states at 28482ece; the claim is `score_open` only, in tests/golden/card_claimed_drift.txt, with its direction. Any other moved state is a stop (carry r2-a). docs/img/card figures are named: either byte-identical or committed.
- r1-a: the weights are now stated as signed percents with |w| summing to 100, not envelope_drivers' points. The reuse half is replaced by r3-a, which shares the sb-row markup through one `breakdownRow` helper instead of sending percents through `scoreDrivers`. That answers duplication_copies without a points path.
- r1-b: the step is selected in get_current_action, and the WhyNow build sits in slot_drivers.why_now_at. The coordinator's growth is one kwarg at two solve sites plus one key copy in the module-level `_apply_result_payload`, and HeatPumpOptimizerCoordinator gains no method body. The body must name this growth (carry r3-b).
- r1-c: the null control holds hlf and solar flat over L.

## Checked at 28482ece
- Seam: classify_space_steps optimizer.py:1608; _build_result :3014; _settlement_at :522; _Horizon :2186; SolveLimits.min_temp_floors :2319; _build_comfort_bounds :3964; _anticipatory_weights :2588; get_temp_bounds :2140; get_current_action :5801, whose comments name it the one owner of the current-step search. coordinator.py: _apply_result_payload :2848 (module-level), get_current_action call :6288, _fold_away :2271, _mold_floor_series :9022, min_temp_floors= solve sites :6153 and :11185. pump_arbiter._step_index :379 stays private. away.solve_bands :363. payload.CurrentAction :154. sensor.py _PlanSensorBase.extra_state_attributes :1441, SpaceHeatingPlanSensor :1593. Moving selection off `_step_index` and into get_current_action removes the round-2 second search. One owner per concern, and no new write path.
- R10-GRADE-DRIVERS reuse against the merged code (#3198): scoreDrivers :8940, scoreBreakdownHtml :8979, scoreRowTitle :9002, scoreLine :9007. The note reuses the row markup and keeps scoreDrivers for the score, which is sound.
- Mount: headlineHtml :9062, single call site :14697, `show_stats` gate :9063, empty return :9126, hl-narrative :9146.
- Clip-check carry: tests/card_browser.mjs unreachable :835 starts its walk at parentOf(run.el) :838, as the note says. planStates tests/card_rig.mjs:161.
- Evidence: the failing test can fail at the base (no space_drivers; AttributeError/KeyError). The null control (flat prices so the rank is 0.5 and the push 0, mid-band, flat weather) gives all-zero weights. The away=3 and mold-floor perturbations move it off zero. optimality.py is run before and after. The coord_* golden claim, "key added", is correct.
- Sibling sites: both min_temp_floors= sites are named. space_reasons consumers are unchanged, and the per-step readers in get_current_action are the whole class.
- Consistency: no open design/* note claims get_current_action, _apply_result_payload, SolveLimits, _Horizon, _build_result, headlineHtml or the score helpers. design/R10-ADVISOR-WHATIF (b50afa68) shares coordinator.py, optimizer.py and the card as hot files and edits the what-if path near :11185. This note only adds `away_floor_drop_c=None` there: a textual overlap, not one seam. design/r10-combi-tank's one "unreachable" is unrelated.
- Cost: one new module and the listed hot files fit L.

## Routed
- decision: orchestrator. The serial order of R10-WHY-NOW-WIDGET and R10-ADVISOR-WHATIF. Both hold www/heatpump-optimizer-card.js and coordinator.py hot, including the what-if solve at coordinator.py:11185. This note's §7 leaves the order to the orchestrator; restated from round 1.

## Notes for the fixer
Carry: R10-WHY-NOW-WIDGET (item r3-c). slot_drivers.py is a new tracked file: classify it into a measured closure or onto tests/closure.py INERT in the same PR, or tests/entities.py fails.
Carry: R10-WHY-NOW-WIDGET (item r3-d). The coord_* claim goes in tests/golden/claimed_drift.txt with `claims-for:` equal to VERSION at the PR's base. A stamp that lands mid-flight empties the list, so re-check it after any merge of main.
