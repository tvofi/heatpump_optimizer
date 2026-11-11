Design review: revise 0573f2806e2e3d79e3fffe93fb6de151e4da46de architecture-unsound

Round 2 of 3. Reviewed `design.md` at 0573f2806e from a detached worktree; the ref still read 0573f2806e when this was written. Every anchor below was opened at cbd23f1c8b; the learner at 5289e1fee4. Nothing was rerun. Of round 1's six points, five are answered and point 2 is still open in a new form. What round 1 held is kept.

## Revise

1. architecture-unsound, `design.md:50`, `:39`, `:89` (round-1 point 2; the shipped level). The band avail x [p_min, p_max] now reaches `project_space_against` (`thermal_model.py:1717`; `_onto_band`, `:1703`, takes arrays), so the scored draw no longer exceeds the bound. But the same band goes to `_realize_joint` at `optimizer.py:5238`, which ships the plan, and a clamped install's plan carries `duty_floor_kw` = p_min (`_duty_floor`, `optimizer.py:134`, set at `:3265`). `step_duty` reads each circuit alone against that floor (`pump_arbiter.py:495`, `planned_draw_runs`, `thermal_model.py:1294`): a shipped space level under p_min is not space duty. On a fixed-speed pump the charged step ships 0 or avail x p_max - dhw, always under p_min, so the arbiter serves it as idle or hot water only and the heat the plan booked there is switched off (the #1955 loss, `thermal_model.py:1195`); and the leaf, which takes the same floor (item r1), reads the charged step as holding no space leg, so the pair it was charged for has an idle step between and weighs 0. Test 9 pins exactly that level. `project_space_against`'s contract is a total in {0} or [p_min, p_max]; the note breaks it without saying so. Fix wanted: the shipped schedule stays in {0} or [p_min, p_max] and the lost time is charged where the score reads it, or the note says how `step_duty` serves a level under the plan's floor; either way test 9 drives `step_duty` on the fixed-speed fixture and shows the charged step served as space and its pair still priced.

## Round-1 points, against the tree

- Point 1, answered. `off_steps` is read for its semantics (`dhw_planner.py:128`, `:140`, `:503`, `:1273`); the local `forced_off` is complete at `:1089` and the four stages take it (`:1125`, `:1135`, `:1161`, `:1196`); `_apply_dhw_pins` runs after (`:1251`). The sibling note at accd88e772 ORs its ban into the same local (its `design.md:64`, `:178`). The three callers are `optimizer.py:1454`, `:3316`, `:5144`. Hot files name the sibling and the serial position.
- Point 2, still open: above.
- Point 3, answered. `count_compressor_starts` (`optimizer.py:1572`) is pinned by its docstring to the on schedule on the same result and is published at `:5078`; the reason to leave it holds, and test 9 pins it.
- Point 4, answered. `dhw_planner.py:1425` is in `_plan_dhw_min_cost` (`:1326`), `:1682` in `_repair_dhw_floor` (`:1605`), `:1444` resets the first; both are listed and the false reason is gone.
- Point 5, answered. The share at `pump_arbiter.py:1516` gives each leg the combined draw; the six neighbour cases were re-derived here and the term never rises on collapse, falling by at most the stated amount; the bounds at `optimizer.py:4335` hold the edges as the note now says; `_LBFGSB_FD_EPS` is `optimizer.py:1034`; test 8 is in Evidence with mutation targets.
- Point 6, answered. `duty_switch.py:65-67` (half-life 14 days, off under n < 2.5 or p < 0.3, on at n >= 5), strict at `:184`, one weight per episode at `:191`: (10/11)^12 = 0.319 holds, (10/11)^13 = 0.290 drops, and n = 2.5 exactly at 28 days holds. Test 7 agrees with the rule.

## Decisions routed

- decision: orchestrator. Landing order against R10-OUTSIDE-DHW-START-HYSTERESIS on `dhw_planner.py` and `thermal_model.py`, and against pull request 3398, as the note asks (`design.md:100`).

## Notes for the fixer

- `avail` is built from the hot-water plan alone (`design.md:38`), but which step holds the space leg after a block is the solve's own variable: with space at 0 in the block's last step and running in the next, the charge sits on an unused bound and the step the stop shortens is uncharged; the term's own slope pushes space out of that step. Build the vector from the space profile the solve starts from (the warm start, the incumbent in `_co_optimize`), and pin it with a plan whose space starts the step after the block. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r7)
- The disinfection step is placed before `forced_off` exists (`dhw_planner.py:1040-1050`, `:1065`), so a ban through `forced_off` cannot move `legionella_step`: the guard of item r4 cannot fire and its mutant has no honest kill. What a ban can do is forbid the run-up steps. Guard on the requirement the planner returns beside the plan (`dhw_planner.py:1056`, it includes the run-up), not on the floor alone. This replaces item r4. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r8)
- No test pins that the candidate holds no hot water on a banned step. Add it, with the min-run stage (`dhw_planner.py:1138`) on the fixture, since that stage runs between two stages that take `forced_off`. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r9)
- `step_duty` compares each circuit alone against the floor (`pump_arbiter.py:495-496`), so on a clamped install a both step needs space and hot water each at or above p_min; on a fixed-speed pump the leaf never returns two legs. Test 2's grid should hold that case with the floor set. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r10)
- Items r1, r2, r3 and r6 stand as the note carries them. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r11)

## Checked and held

Round 1's holds stand: the leaf seam, the config transport, the price's unit and its non-overlap with the cycling term, the candidate-and-score route, the null controls. Step 3: the note's grep was run at cbd23f1c8b and prints the sites it lists and no other. Step 5: no second open design claims the seam beyond the sibling above. Step 6: ten hot files, L if item c1's payment is found.

Seat tokens: no subagents; the harness reports no figure for the main loop.
