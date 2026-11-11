# R10-DUTY-SWITCH-PLANNER-PRICE, part C: the planner prices a duty switch that stops the compressor

Revision 2, answering `Design review: revise 3c8ff9d843` (verdict 2a7919168a, points 1 to 6, marked [1] to [6] below). Base: origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf; every line cited was opened at that SHA unless marked. Predecessor R10-DUTY-SWITCH-RESTART-LEARNING: design abc575172ca1e6758c58ca8d1f265a2dc7c4fa23, verdict 76728006e64309da84806c3b17be520e7c90edca, build read at handoff-wip 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f (a merge of 12ddbb72bc with this base; no handoff head yet). The finding, table and reasoning are Bankaifan's, pull request 3420 (head 2599cc38ed), with thanks. No finder harness: outside report, owner-routed. The group has no roster entry; size L is assumed.

## Finding

`cycling_penalty_batch` (`optimizer.py:1614`) prices the swing of the combined draw (`optimizer.py:4783`, `:2893`), so a hot-water to space switch at constant draw costs nothing in the plan. On the contributor's install that switch stopped the compressor three times out of three after a real hot-water leg (off 8.2 min, 8.5 min, one censored) and never in the other direction. Part A learns that per direction and nothing reads it.

## Owning seam

**The legs a plan step is served in, the switches between them, and the running time a switch leaves: a new leaf module beside `plan_step.py`**, pure (numpy, `planned_draw_runs` from `thermal_model.py:1261`, `PLAN_STEP_MINUTES`), on `plan_step.py`'s own argument: two modules need one rule and neither may import the other. It owns:

1. **The leg rule**, moved out of `_share` (`pump_arbiter.py:1502`) with `SPLIT_MIN_MINUTES` (`pump_arbiter.py:230`): idle, one duty, or a both step whose hot-water minutes are step x dhw / (space + dhw), collapsed to one duty when either share is under the minimum, else two legs in a stated order (hot water first, today's). `_share` keeps its gates and its clock compare and calls the rule. A move, behaviour-identical.
2. **The switch weight** over a schedule, scalar and batch twin.
3. **The availability vector**: per step, the share of the step the compressor can run after a priced stop (1 everywhere else).

**Callers only:** `optimizer.py` (the objective closures, the realisation, `_solve_space`, `_co_optimize`), `pump_arbiter.py` (`_share`), `thermal_model.py` (`project_space_against` accepts a per-step band, [2]), `dhw_planner.py` (one keyword argument, [1]), and part B when built. **The learned values and their bound stay with the predecessor's learner**, which gains one read for the planner and the count cap. `optimizer.py` imports neither the arbiter nor the learner (both import Home Assistant, `fixer.md` step 17): the values travel as plain floats on `OptimizationConfig` (`optimizer.py:2095`), which also survives `optimize_in_process`.

## Shape

**The leg draw [5].** A leg runs at its step's combined realised draw c = space + dhw. That is what `_share` implies: hot water gets step x dhw / (space + dhw) minutes, so booking the step's dhw kW of energy in that time needs space + dhw kW, and the same for the space leg; a one-leg step runs at c for the whole step. For each pair of consecutive legs of different duty with no idle step between, in direction r:

    in a both step:            weight = p_r x c_i / p_max
    step i into step i+1:      weight = p_r x min(c_i, c_i+1) / p_max        term = cycling_cost x sum of weights

A stop at a switch turns the swing |a - b| that `cycling_penalty_batch` already prices into a + b; the difference, 2 x min(a, b), is min(a, b) / p_max cycles in that function's unit (2 x p_max per cycle), taken with the learned stop probability. Inside a step a = b = c, and the cycling term sees no swing there at all. The term goes inside the parenthesis `price_weight` multiplies at `optimizer.py:4783` and `:2893`, on the realised draws both lines already use, space and hot water held apart. With no hot-water plan it is zero by definition.

**How a non-smooth term enters the solve [5].** Between its edges the term is piecewise linear in the space draw, slope at most 2 x p x cycling_cost / p_max, like the L1 term beside it. It has three kinds of edge, all the arbiter's real behaviour and kept exact so planner and arbiter cannot disagree:

- the running threshold of `step_duty` (`pump_arbiter.py:468`): a boundary pair appears with a jump of p x cycling_cost x t / p_max, t the larger of `MIN_RUNNING_DRAW_KW` (`thermal_model.py:1197`) and the plan's duty floor;
- the two collapse edges of a both step, space = dhw / 2 and space = 2 x dhw. Crossing from two legs to one removes the in-step pair and re-pairs the step with one neighbour; worked through the six neighbour cases (the neighbouring leg is space, hot water or idle, for each collapse) the term never rises on collapse and falls by at most (p_dhw_space + p_space_dhw) x cycling_cost x (space + dhw) / p_max, which on the contributor's install (one direction, p = 1) is cycling_cost x 1.5 x dhw / p_max at the lower edge and cycling_cost x 3 x dhw / p_max at the upper.

Revision 1 said the gradient solver is not asked to cross these. That was wrong: the bounds at `optimizer.py:4335` are [0, headroom] and hold the lower edge whenever dhw < 2/3 x p_max and the upper whenever dhw < 1/3 x p_max. What the design relies on instead: the two-leg region is a raised plateau whose both exits are downward, so a finite-difference slope taken across an edge (`_LBFGSB_FD_EPS`) points out of the plateau, never into it, and the line search of L-BFGS-B accepts only a decrease. A start within the step size of an edge can still stall a line search; test 8 pins that this costs no score and no status. Where the hot-water block sits is combinatorial and is taken by candidate and score, the way `_co_optimize` (`optimizer.py:3268`) already works:

```
coordinator.py:6242 cycling_cost=... (+ one argument) <-- learner read: (p, off seconds) per direction, zeros unless latched
_solve_objectives (optimizer.py:4697): objective / objective_batch += switch term(space, dhw)                 [leaf]
avail = leaf(dhw plan, lost share)  -> headroom (optimizer.py:4321, :3297) = max(0, avail x p_max - dhw)
                                    -> _realize_draw (:4746, :4809), _realize_joint (:5238): band avail x [p_min, p_max]
_co_optimize, on each return path but the combi repair, only if the incumbent's switch term > 0:
    ban = steps where the incumbent's space runs in that step or the next
    candidate = planner._build_dhw_requirements(..., <placement ban>=ban)   # same off_steps as the incumbent
    adopt iff tank floor and disinfection step held as the incumbent holds them AND solve_space(candidate) scores lower (:3338)
```

**The ban's channel [1].** `off_steps` is not the door: a not-None value is read for its semantics (`dhw_planner.py:128`), moves the disinfection placement (`_legionella_off_mask`, `dhw_planner.py:140`, read at `:503`) and zeroes the schedule under a manual pin (`dhw_planner.py:1273`). `_build_dhw_requirements` (`dhw_planner.py:951`) gains one keyword argument, a placement ban, default none, OR'd into the local `forced_off` after `dhw_planner.py:1089`, the door the four placement stages already obey (`:1125`, `:1135`, `:1161`, `:1196`). With none passed `forced_off` is built as today. `design/R10-OUTSIDE-DHW-START-HYSTERESIS` (accd88e772, its item 3) ORs its own ban into the same local at the same point from inside the function, so the two groups share one channel and no parameter: whichever lands second adds its OR beside the first's. A manual force-on pin inside the ban still wins (`_apply_dhw_pins` runs after), as in that design. The other two callers (`optimizer.py:1454`, `:5144`) pass nothing.

The ban lets hot water sit only where a block ends into a planned stop or into more hot water. For a priced space to hot-water direction it mirrors (the previous step). One extra plan and one warm space solve, only on an install whose learner is latched and whose plan holds a priced switch.

**Lost running time, on the bound and on the realised draw [2].** phi = min(1, p x median off seconds / step seconds) for hot water to space; 0.56 on the contributor's two samples. It is charged to exactly one step per block end, the step holding the space leg that follows the hot-water leg: the hot-water step itself when a space share can still run there, else the next step. In that step avail = 1 - phi. The compressor is off for phi of the step and inside [p_min, p_max] for the rest, so the step-average band is avail x [p_min, p_max], and both readers take it: the solve's bound becomes max(0, avail x p_max - dhw), and `project_space_against` (`thermal_model.py:1717`) is called with avail x p_min and avail x p_max per step (it drops its two `float()` casts; `_onto_band`, `thermal_model.py:1703`, already takes arrays). `_realize_joint` (`optimizer.py:165`) and `_realize_draw` (`optimizer.py:152`) pass the vector through; with none they make today's call unchanged. A sub-minimum space draw in the charged step is then raised to avail x p_min - dhw, which is never above the bound, so the scored draw (`optimizer.py:4746`) cannot exceed the lost-time bound on any install; on a fixed-speed pump (p_min = p_max) the charged step's space draw is 0 or exactly avail x p_max - dhw. Hot water keeps the level its planner booked.

**The tank side [4].** The hot-water planner has two headroom lines of its own, `dhw_planner.py:1425` (`p_total_max - demand` in `_plan_dhw_min_cost`) and `:1682` (`p_dhw_max - plan` in `_repair_dhw_floor`). Neither is charged: a hot water to space stop shortens the space leg that follows it, and the only direction whose lost time would fall on a hot-water leg, space to hot water, has no measured off time on any install, so its phi is zero. That direction gets the price and no lost time. When an off time is first measured for it, these two lines are where it lands.

**The published start count [3].** `count_compressor_starts` (`optimizer.py:1572`, published at `:5078` as the result's compressor starts, shown on the card's receipt and written to the ledger) reads the combined draw and counts no start across a constant-draw switch. It stays as it is: its docstring pins it to the on schedule published beside it on the same result (which steps ran), a stop of probability p is not a step that did not run, and an integer cannot carry 0.56 of a start. The restarts that happen are counted by the measured start counter and by part A's published tallies. Test 9 pins that the count is unchanged by the pairs.

**Config and learner.** `OptimizationConfig` gains two fields beside `cycling_cost` (`optimizer.py:2138`): the stop probability and the off seconds, each a pair (hot water to space, space to hot water), default zeros; non-finite or out-of-range values read as zero. The coordinator passes them beside `coordinator.py:6242` from one learner function returning both pairs: zeros unless that direction's stored latch is on, and zero off time while no uncensored sample exists.

**Bound on the learned count (verdict item n11) [6].** After each booked episode, if n exceeds 10 (twice the predecessor's on-threshold) both decayed weights are scaled by 10 / n; p is unchanged by the scaling. At the cap a kept episode therefore multiplies p by 10/11, not 0.9. Derived against the predecessor's strict comparisons (latch drops on p < 0.3 or n < 2.5): with every episode kept after a firmware change, p falls from 1 to (10/11)^12 = 0.319 after twelve, still latched, and to (10/11)^13 = 0.290 after thirteen, dropped; 13 is the worst case, since n decayed under the cap between episodes makes each factor smaller. With no episodes n halves every 14 days and the latch drops just after 14 x log2(10 / 2.5) = 28 days. Stored weights stay inside the store's existing bounds.

**Composition with part B, so one stop is not paid twice.** The planner prices only switches the leg rule emits, and the arbiter serves the legs the same rule returns. B's order latch becomes the rule's order argument: the in-step switch turns into space to hot water (unpriced on this install) and the stop is counted once, at the boundary into the next space step. B's minimum share is one more collapse case in the same function. Against the cycling term there is no overlap: the weight is the swing a stop adds beyond |a - b|.

**Invariants.** Zero pairs build the objective operand for operand as today; with zero phi no availability vector exists and headroom, projection and realisation are today's calls bit for bit; `_co_optimize` generates no extra candidate; a planner call with no ban is today's call; scalar and batch terms agree bit for bit per row (`row_sums`, as `tests/features.py:7434` pins for cycling); a candidate is never adopted on a higher score, a worse tank floor or a moved disinfection step, and a refused candidate leaves the incumbent's requirement in place; no payload key and no entity attribute is added.

## Alternatives

- **A unit price per switch (p x cycling_cost on an indicator).** Zero slope everywhere and a full-size jump at the running threshold, so the solver could move only through enumerated bound masks; and it pays the swing |a - b| twice against the cycling term.
- **Step averages as leg draws (min(space, dhw) / p_max in a both step).** Continuous at both collapse edges, but it prices a stop the arbiter does not make and underprices the one it does by (space + dhw) / min(space, dhw): planner and arbiter would disagree by construction.
- **A term in the hot-water program** (`_plan_dhw_min_cost`): "hot water then space" needs a binary per step, the MILP the comment at `optimizer.py:2130` rules out, and the first plan is made before any space profile exists.
- **The ban through `off_steps`** (revision 1): changes the disinfection placement and the pin rule on an install with no Off window, [1].
- **Lost time on the bound only** (revision 1): void wherever p_min > p_max x (1 - phi), every fixed-speed pump, [2]. **Lost time inside the trajectory simulation:** changes the input of every row of `simulate_trajectory_batch`; a band is a constant per space solve.
- **Count the switches in `pump_arbiter.py`**, or re-implement `_share` in the optimizer: a Home Assistant import under the optimizer, or a duplicated shape (`D7.md` item 8) that B would edit twice.

## Sibling sites

`git grep -n -E "cycling\(|cycling_batch\(|cycling_batch=|p_max - dhw|headroom = |_realize_draw\(|_realize_joint\(|project_space_against\(|count_compressor_starts\(|SPLIT_MIN_MINUTES" -- custom_components/heatpump_optimizer` prints: the two objective sums (`optimizer.py:4783`, `:2893`, covered); the closures (`:3438`, `:3441`, `:4829`, wiring); the two space headroom sites (`:4321`, `:3297`, covered, one helper); the realisation chain (`:152`, `:162`, `:165`, `:181`, `:4746`, `:4809`, `:5238`, `thermal_model.py:1717`, covered, [2]); the tank-side headroom lines (`dhw_planner.py:1425`, `:1682`, out of scope with the reason above, [4]; `:1444` resets the first); the planned start count (`optimizer.py:1572`, `:5078`, unchanged with the reason above, [3]); the share rule (`pump_arbiter.py:230`, `:1517`, `:1519`, moved to the leaf). `git grep -n "_build_dhw_requirements(" -- custom_components/heatpump_optimizer` prints the three callers named above. The space-only path passes no hot-water plan and is unchanged. The set-point gate transport stays out of scope, as in part A.

## Evidence, by file

All in `tests/features.py`, failing today because the leaf, the two config fields, the ban argument and the learner read do not exist:

1. **The finding:** a hot-water step followed by a space step at equal draw has cycling penalty 0 and switch term p x cycling_cost x draw / p_max; an idle step between gives 0; the reverse order with a zero pair gives 0; a two-leg both step alone gives p x cycling_cost x (space + dhw) / p_max.
2. **Leg-rule agreement:** over a probe grid of (space, dhw, minute in step, duty floor set and unset), drive `step_duty` and then `_share`; the leaf's legs equal what they serve, both collapse edges and the floor on the grid.
3. Scalar and batch term bit for bit, per row; availability: one step charged per block end, the else-branch, and zero phi returning no vector.
4. **Null controls, each a full `optimize` twice with arrays compared equal:** an empty learner; one below the on-threshold; an install whose every switch was kept. And the golden lane: `tests/golden.py:306` builds its config without the fields, so `tests/golden/flat_prices.json` and every other fixture reproduce unchanged.
5. **Acceptance:** a fixture from the contributor's table (15 min steps, pair (1, 0), off 501 s). Against the plan solved with zero pairs: the summed switch weight is lower, and the new plan scores no higher than the old plan under the new objective. Null control: with the pair (0, 0) the two plans are the same arrays.
6. **Candidate guard:** a banned candidate that scores lower but holds the tank floor on fewer steps is refused, one whose `legionella_step` differs is refused, and after each refusal the optimizer's requirement is the incumbent's; with no priced switch the planner is called as often as today. **Ban channel [1]:** on an install with no Off window and a due disinfection, a planner call with a ban returns the same `legionella_step` as without, and a manual force-on pin inside the ban survives; both fail if the ban is routed through `off_steps`.
7. **Learner [6]:** n never exceeds the cap; from p = 1 at the cap the latch holds after 12 kept episodes and drops at the 13th; with no episodes it holds at 28 days and drops the day after; a capped record round-trips; the read returns zeros while unlatched.
8. **Edges [5]:** on a fixture with dhw < 1/3 x p_max, four warm starts placed 2 x `_LBFGSB_FD_EPS` on either side of each collapse edge, and one at the running threshold: each solve returns a score no higher than its start's, with a solver status no worse than the same start solved with zero pairs. Null control: with zero pairs the same starts return today's arrays.
9. **Clamped install [2], [3]:** on a fixed-speed fixture (p_min = p_max) with phi = 0.56, the realised space draw in the charged step is 0 or avail x p_max - dhw, never above the bound, and the realised total of that step is at most avail x p_max; `count_compressor_starts` of the plan equals its value with zero pairs on the same arrays.

**No golden moves; neither claim file is touched.** Mutation targets: the direction index, the `min`, the in-step weight's leg draw (c replaced by min(space, dhw)), the division by p_max, both collapse comparisons, the floor passed to the classification, the zero-pair early return, the one-step availability choice, avail dropped from the projection's p_min, the OR into `forced_off` moved to `off_steps`, the floor guard, the disinfection guard, the score comparison, the cap line, the coordinator's one line.

## Hot files, position, carries

After R10-DUTY-SWITCH-RESTART-LEARNING merges; part B after this group. Serial with R10-OUTSIDE-DHW-START-HYSTERESIS on `dhw_planner.py` (one function, one local, [1]) and `thermal_model.py` (it adds two pure functions; this group edits `project_space_against` only): either order works, the second rebases, and the order is the orchestrator's. Pull request 3398's edit to `dhw_planner.py` is one condition in `_dhw_legionella_due`, which nothing here reads. Hot: `optimizer.py`, `pump_arbiter.py`, `dhw_planner.py`, `thermal_model.py`, `coordinator.py` (one line), the learner module, the new leaf, `tests/features.py`, `tests/closures.json`, `docs/architecture.md`. Ten files; still L if the structure payment of item c1 is found. Not touched: `sensor.py`, `store.py`, `const.py`, `tests/golden/`.

## Decisions routed

- decision: orchestrator. The flat-price control is read as the recorded fixture with no learned values (test 4), as the verdict confirms; with a latched learner a flat-price plan that holds a priced switch may move, and should.
- decision: orchestrator. Landing order against R10-OUTSIDE-DHW-START-HYSTERESIS and pull request 3398 on `dhw_planner.py`.
- decision: owner, unchanged: B's minimum-share rule. This design composes with either answer.

## Notes for the fixer

- Every structure metric sits at zero headroom (`python3 tests/structure.py`). The new functions are module-level in the leaf; lines added inside the optimizer class, the planner's one argument and the coordinator's one line are paid in the same file, and the `_share` move should pay part of it. No payment found is a stop and ask before the push. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c1)
- `DhwPlan` (`dhw_planner.py:211`) carries no shortfall field. The floor guard needs the planner's own tank simulation of the candidate against `floor_temps`; if that needs a new planner method, raise it rather than re-simulate in the optimizer. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c2)
- The learner module imports Home Assistant at its top at 5289e1fee4; the planner read lives beside its registry, and the cap in the pure direction record's booking. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c5)
- `_share` reads the plan's stored schedules; the objective reads realised draws. Run the agreement test on realised values of a clamped install too. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c6)
- The cap of 10 and the phi rule are constants from one day on one install, as part A's are. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c7)
- Re-read every anchor after the predecessor merges; its `pump_arbiter.py` diff adds about 97 lines. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c8)
- The pull-request body thanks Bankaifan by name and pull request 3420. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c9)
- B's designer: the order and the minimum share go into the leaf's leg rule, nowhere else. Carry: dismissed: part B has no roster group yet; stated in this note's composition section (item c10)
- `step_duty` passes the plan's `duty_floor_kw` to `planned_draw_runs` as `modulation_floor`, and `_share` only sees a step already classed both: the leaf's classification takes the same floor, and test 2 drives `step_duty` then `_share`. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r1)
- The planner call at `optimizer.py:3316` assigns the optimizer's requirement as it builds a candidate; build the banned candidate into locals and assign on adoption only (test 6). Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r2)
- `_co_optimize` returns at `optimizer.py:3311` (combi repair), `:3314` (no pinned step, the common one), `:3333`, `:3339` and `:3343`; the banned candidate is tried on each but the first. One exit helper, not five copies. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r3)
- The disinfection guard compares `DhwPlan.legionella_step` of candidate and incumbent (test 6). Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r4)
- The availability vector multiplies p_min and p_max only where it exists; never multiply by a vector of ones on the null path, the invariant is that today's call is made. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item r6)
- Dropped from revision 1: item c3 is now test 8; item c4 was answered by the verdict (no fixture snapshots the config's field list). Carry: dismissed: both resolved in this revision (item c3)

Seat tokens, this revision: subagents 31365, 55137 and 53963; revision 1: 31753, 36256, 37016, 55283, 56195 and 41312; the harness reports no figure for the main loop.
