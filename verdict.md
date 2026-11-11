Design review: approve 439d17c9305b6829c7426faa4c305edab7392d74

Round 3 of 3. Reviewed `design.md` at 439d17c930 from a detached worktree; the ref still read 439d17c930 when this was written. Every anchor below was opened at cbd23f1c8b, still the tip of main. Nothing was rerun. Round 2's one item is closed, its notes r7 to r11 are folded in, and the five answered points stand.

## Round-2 item, against the tree

- Closed, `design.md:56`, `:58`, `:97`. The band is withdrawn and the shipped schedule makes today's calls: `_realize_joint` (`optimizer.py:165`, identity when not clamped at `:178`, `project_space_against` at `:181`, called at `:5238`) and `project_space_against` (`thermal_model.py:1717`, total in {0} or [p_min, p_max] by its docstring, `_onto_band` at `:1703`) are not edited. `step_duty` (`pump_arbiter.py:468`) reads `duty_floor_kw` and calls `planned_draw_runs` on each circuit alone (`:493`, `:494`; the floor zeroes a total under it, `thermal_model.py:1294-1298`). On a fixed-speed pump the tank projects to 0 or p_max, so a step with hot water leaves space 0 and the charged step is a space-only step shipping p_max: served as space, and the leaf with the same floor reads a space leg, so its pair stays priced. The lost time moves to a delivered draw applied after `_realize_draw` in both closures (`optimizer.py:4746`, `:4809`) to the simulation input (`:4751`, `:4815`) and the energy operand (`:4766`, `:2890`), and after `:5238` to the published simulation (`:5253`) and the predicted cost (`:5281`; `dhw_planner.py:403-404`); cycling and capacity (`:4783`, `:2893`) keep the level. Test 9 does what round 2 asked: a full `optimize` on the fixed-speed fixture, `step_duty` inside the charged step returns space, the pair's weight is p x 1, and the published trajectory equals the simulation at avail x p_max and differs from one at p_max. The alternative round 2 offered (`step_duty` serving a sub-floor level) is refused with a reason.

## Round-1 points

- Points 1, 3, 4, 5 and 6: the paragraphs are unchanged from 0573f2806e except point 1's adoption guard, which now follows item r8. Their anchors were reopened: `dhw_planner.py:951` (parameters), `:1065-1089` (`forced_off`), `:1125`, `:1135`, `:1161`, `:1196`, `:1251`, `:1273`, `:1425`, `:1444`, `:1682`; `optimizer.py:1454`, `:3316`, `:5144` (the three callers, no fourth); `:1572`, `:5078`; `:1034`; `pump_arbiter.py:230`, `:1512-1521`. All hold.
- Point 2: closed above.

## Round-2 notes r7 to r11

- r7: in Shape (`design.md:53`, the profile `_solve_space` starts from, `optimizer.py:4321-4333`), test 3 and the carry. r8: the guard is on the returned requirement (`dhw_planner.py:1056`; the step is placed at `:1035-1050`, before `:1065`), in the invariants, test 6 and the carry; item r4 is replaced. r9: test 6 holds the min-run stage, whose call at `dhw_planner.py:1138-1148` takes no `forced_off`; the carry says a write into the ban refuses the candidate and is reported, not built. r10: test 2's grid and the carry. r11: carried, with r6 reworded for the delivered draw.

## Decisions routed

- decision: orchestrator. Pull request 3398 is merged: it is cbd23f1c8b, this design's base. The landing-order question at `design.md:103` and `:108` now names R10-OUTSIDE-DHW-START-HYSTERESIS alone.

## Notes for the fixer

- The closures realise with `_scores_rounded` (`optimizer.py:184`: clamped and not `_levels_relaxed`), not with `clamp_planned_levels`, while the delivered draw keys on `_duty_floor` (`:134`). On a relaxed start of a clamped install the delivered draw is therefore applied to an unrounded value. Say which reading the relaxed solve gets and pin it with one relaxed start carrying a vector. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r14)
- The achieved objective (`optimizer.py:5266`) is called with the arrays of `:5238` and the closure applies the delivered draw itself. Hand it the shipped arrays: if the publication rebinds `optimal_space` to the delivered draw before `:5266`, the lost time is charged twice and the candidate comparison across valve schedules moves. Add that rebinding to the mutation targets. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r15)
- "A charged step ships a space level at or above p_min" (`design.md:56`) holds on a fixed-speed pump by arithmetic and elsewhere only because the leaf picks the charged step with the floor: on a modulating clamped install `project_space_against` raises space to p_min - dhw, under p_min, beside hot water. Test 3 or 9 should hold a modulating clamped fixture (p_min < p_max) and show that no charged step has shipped space under the floor. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r16)
- `tests/features.py:7433-7436` pins scalar against batch cycling bit for bit but does not name `row_sums` (no such name in that file); the helper is in `cycling_penalty_batch` (`optimizer.py:1614`). Build the switch term's batch twin on the same helper and pin it the way that check does. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r17)
- Items c1, c2, c5 to c9, r1 to r3, r6 to r13 stand as the note carries them. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r18)

## Checked and held

Step 1: the leaf seam, one owner per concern; `thermal_model.py` is no longer edited and no new write path is added (the vector rides beside its plan, item r12). Step 2: the delivered draw is the brief's "learned off time enters as lost headroom" on the install class where a level cannot carry it. Step 3: the note's grep was run at cbd23f1c8b and prints the sites the note lists, plus `optimizer.py:4323`, `:4329` (caps on the same headroom, inside the one helper's site), `pump_arbiter.py:44` (a docstring) and `:819` (an unrelated flow-lift flag). Step 4: tests 1 and 9 fail on today's code; each quantified claim has its null control; no golden and no claim file is named to move. Step 5: of the open `design/*` notes only R10-OUTSIDE-DHW-START-HYSTERESIS (accd88e772) shares the seam, on the one `forced_off` local, as the note records. Step 6: nine hot files, L if item c1's payment is found.

Seat tokens: subagent 71490; the harness reports no figure for the main loop.
