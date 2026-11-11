# R10-DUTY-SWITCH-PLANNER-PRICE, part C: the planner prices a duty switch that stops the compressor

Base: origin/main f24d107bd7aa170bea7419251a4b7f4f48b732f6; every line cited is at that SHA unless marked. Predecessor R10-DUTY-SWITCH-RESTART-LEARNING: design abc575172ca1e6758c58ca8d1f265a2dc7c4fa23, verdict 76728006e64309da84806c3b17be520e7c90edca, build read at handoff-wip 12ddbb72bccf18191062ccb937acc2e018d28db0 (no handoff head yet; its merge base with main is 8f97247fc1, so its `pump_arbiter.py` lines differ from the ones here). The finding, table and reasoning are Bankaifan's, pull request 3420 (head 2599cc38ed when read), with thanks. No finder harness: outside report, owner-routed. The group has no roster entry; size L and its one-hour box are assumed from the predecessor's verdict.

## Finding

`cycling_penalty_batch` (`optimizer.py:1614`) prices the swing of the combined draw (`optimizer.py:4783`, `:2893`), so a hot-water to space switch at constant draw costs nothing in the plan. On the contributor's install that switch stopped the compressor three times out of three after a real hot-water leg (off 8.2 min, 8.5 min, one censored) and never in the other direction. Part A learns that per direction and nothing reads it.

## Owning seam

**The legs a plan step is served in, and the switches between them: a new leaf module beside `plan_step.py`**, pure (numpy, `planned_draw_runs` from `thermal_model.py:1256`, `PLAN_STEP_MINUTES`), on `plan_step.py`'s own argument: two modules need one rule and neither may import the other. It owns three things:

1. **The leg rule**, moved out of `_share` (`pump_arbiter.py:1502`) with `SPLIT_MIN_MINUTES` (`pump_arbiter.py:230`): idle, one duty, or a both step whose hot-water minutes are step x dhw / (space + dhw), collapsed to one duty when either share is under the minimum, else two legs in a stated order (hot water first, today's). `_share` keeps its gates (mode, boost, disinfection) and its clock compare and calls the rule for the shares. A move, behaviour-identical.
2. **The switch weight** over a schedule, scalar and batch twin.
3. **The space headroom** a hot-water plan leaves.

**Callers only:** `optimizer.py` (the objective closure, `_solve_space`, `_co_optimize`), `pump_arbiter.py` (`_share`), and part B when it is built. **The learned values and their bound stay with the predecessor's learner module**, which gains one read for the planner and the count cap. **`dhw_planner.py` gains no term**: it is steered through its existing `off_steps` argument (`dhw_planner.py:951`). `optimizer.py` imports neither the arbiter nor the learner (both import Home Assistant, `fixer.md` step 17): the values travel as plain floats on `OptimizationConfig` (`optimizer.py:2094`), which also survives `optimize_in_process`.

## Shape

**The price, in the cycling term's own unit.** For each pair of consecutive legs of different duty with no idle step between (inside a both step, or last leg of step i to first leg of step i+1), with draws a and b in kW and direction r:

    weight = p_r x min(a, b) / p_max        term = cycling_cost x sum of weights

A stop at the switch turns the swing |a - b| that `cycling_penalty_batch` already prices into a + b; the difference is 2 x min(a, b), which is min(a, b) / p_max cycles in that function's unit (2 x p_max per cycle), taken with the learned stop probability. The term goes inside the parenthesis `price_weight` multiplies at `optimizer.py:4783` and `:2893`, computed on the realised draws both lines already use, space and hot water held apart (`_solve_objectives`, `optimizer.py:4697`, has both). With no hot-water plan it is zero by definition.

**How a non-smooth term enters the solve.** The weight is continuous and piecewise linear in the space draw, like the L1 term beside it: it falls to zero with the smaller leg, so the 0.1 kW running threshold (`MIN_RUNNING_DRAW_KW`, `thermal_model.py:1192`) is no jump, and L-BFGS-B's batched finite difference sees a slope of p x cycling_cost / p_max. The only jumps left are the leg rule's own two share-collapse edges (space = dhw / 2 and space = 2 x dhw at today's constants), which are the arbiter's real behaviour and are kept exact so planner and arbiter cannot disagree. The gradient solver is not asked to cross them; the decision that matters, where the hot-water block sits, is combinatorial and is taken by candidate and score, the way `_co_optimize` (`optimizer.py:3268`) already works:

```
coordinator.py:6198 replace(...) <-- learner read: (p, off seconds) per direction, zeros unless latched
_solve_objectives: objective / objective_batch += switch term(space, dhw)        [leaf]
_solve_space (optimizer.py:4321), _co_optimize (:3297): headroom = leaf(dhw plan, p_max, lost share)
_co_optimize, after today's candidate, only if the incumbent's switch term > 0:
    off_steps' = off_steps + steps where the incumbent's space runs in that step or the next
    candidate = planner._build_dhw_requirements(..., off_steps=off_steps')
    adopt iff tank floor held as the incumbent holds it AND solve_space(candidate) scores lower (:3338)
```

The mask lets hot water sit only where a block ends into a planned stop or into more hot water (space, then hot water, then idle is the free order). For a priced space to hot-water direction the mask mirrors (the previous step). One extra plan and one warm space solve, and only on an install whose learner is latched and whose plan holds a priced switch.

**Lost headroom.** phi = min(1, p x median off seconds / step seconds) for hot water to space; 0.56 on the contributor's two samples. The lost time is charged to exactly one step per block end: the step holding the space leg that follows the hot-water leg under the leg rule's order. With hot water first that is the hot-water step itself, headroom max(0, p_max x (1 - phi) - dhw), when a share can still run there, else the next step, capped at p_max x (1 - phi). Both headroom sites call the one helper; they are two copies of one expression today. Space to hot water gets the price and no headroom: the tank side has no headroom line, and no install has measured an off time in that direction.

**Config and learner.** `OptimizationConfig` gains two fields beside `cycling_cost` (`optimizer.py:2138`): the stop probability and the off seconds, each a pair (hot water to space, space to hot water), default zeros; non-finite or out-of-range values read as zero. The coordinator passes them in the `replace` at `coordinator.py:6198`, one line, from one learner function returning both pairs: zeros unless that direction's stored latch is on, and zero off time while no uncensored sample exists.

**Bound on the learned count (verdict item n11).** After each booked episode, if n exceeds 10 (twice the on-threshold) both decayed weights are scaled by 10 / n. p is unchanged at the moment of scaling and thereafter moves as a mean over about the last ten episodes. Derived: with no episodes the latch drops within 14 x log2(10 / 2.5) = 28 days; with every episode kept after a firmware change, p falls from 1 under the 0.3 off-threshold in 12 episodes (0.9^12 = 0.28). Stored weights stay inside the store's existing bounds.

**Composition with part B, so one stop is not paid twice.** The planner prices only switches the leg rule emits, and the arbiter serves the legs the same rule returns. B's order latch becomes the rule's order argument: the in-step switch turns into space to hot water (unpriced on this install) and the stop is counted once, at the boundary into the next space step. B's minimum share is one more collapse case in the same function: the step has one leg, so no switch and no price. B edits one function and both readers follow; the agreement test below refuses a second copy. Against the cycling term there is no overlap either: the weight is the swing a stop adds beyond |a - b|.

**Invariants.** Zero pairs build the objective operand for operand as today (the closure adds nothing, as with a hot-water plan of `None`); headroom with phi = 0 is today's expression bit for bit; `_co_optimize` generates no extra candidate; the scalar and batch terms agree bit for bit per row (`row_sums`, as `tests/features.py:7426` pins for cycling); a candidate is never adopted on a higher score or a worse tank floor; no payload key and no entity attribute is added.

## Alternatives

- **A unit price per switch (p x cycling_cost on an indicator).** A jump at the running threshold: the finite-difference step (`_LBFGSB_FD_EPS`, 1e-4) reads zero slope everywhere and a spurious one at the edge, so the solver could move only through enumerated bound masks, one more multi-start solve each; and it pays the swing |a - b| twice against the cycling term.
- **A term in the hot-water program** (`_plan_dhw_min_cost`): "hot water then space" needs a binary per step, the mixed-integer problem the comment at `optimizer.py:2130` rules out for this hardware, and the first plan is made before any space profile exists.
- **Count the switches in `pump_arbiter.py`**, or re-implement `_share` in the optimizer: the first puts a Home Assistant import under the optimizer, the second is a duplicated shape (`D7.md` item 8) that B would have to edit twice.
- **Lost time inside the trajectory simulation:** it changes the input of every row of `simulate_trajectory_batch` and the scalar-batch parity with it; a bound is a constant per space solve and native to L-BFGS-B.
- **A planned idle step after each block:** a certain stop priced by the cycling term is never cheaper than a probable one.

## Sibling sites

`git grep -n -E "cycling\(|cycling_batch\(|cycling_batch=|p_max - dhw|SPLIT_MIN_MINUTES" -- custom_components/heatpump_optimizer` prints: the two objective sums (`optimizer.py:4783`, `:2893`, covered, one term each from the same leaf function); the closures (`:3438`, `:3441`, `:4829`, wiring); the two headroom sites (`:4321`, `:3297`, covered, one helper); the share rule (`pump_arbiter.py:230`, `:1517`, `:1519`, moved to the leaf); a docstring (`pump_arbiter.py:44`) and `thermal_model.py:1721` (the clamp projection's bound, which takes the headroom it is given: out of scope). The space-only path passes no hot-water plan and is unchanged. The set-point gate transport stays out of scope, as in part A: it has no single-duty legs.

## Evidence, by file

All in `tests/features.py`, failing today because the leaf module, the two config fields and the learner read do not exist:

1. **The finding:** a hot-water step followed by a space step at equal draw has cycling penalty 0 and switch term p x cycling_cost x draw / p_max; an idle step between gives 0; the reverse order with a zero pair gives 0.
2. **Leg-rule agreement:** over a probe grid of (space, dhw, minute in step), the leaf's legs equal what `_share` serves; both collapse edges on the grid.
3. Scalar and batch term bit for bit, per row; headroom: one step charged per block end, the else-branch, and phi = 0 equal to today's expression.
4. **Null controls, each a full `optimize` twice with arrays compared equal:** an empty learner; one below the on-threshold; an install whose every switch was kept (never latched). And the golden lane itself: `tests/golden.py` builds its config without the fields, so `tests/golden/flat_prices.json` and every other fixture must reproduce unchanged.
5. **Acceptance:** a fixture from the contributor's table (15 min steps, pair (1, 0), off 501 s). Against the plan solved with zero pairs: the summed switch weight is lower, and the new plan scores no higher than the old plan when both are scored by the new objective. Its null control: with the pair (0, 0) the two plans are the same arrays.
6. Candidate guard: a masked candidate that scores lower but holds the tank floor on fewer steps is refused; with no priced switch the planner is called exactly as often as today.
7. Learner: n never exceeds the cap; the 28-day and 12-episode bounds above, both ends (zero evidence, at the cap); a capped record round-trips; the read returns zeros while unlatched.

**No golden moves; neither claim file is touched.** Mutation targets: the direction index, the `min`, the division by p_max, both collapse comparisons, the zero-pair early return, the one-step headroom choice, the floor guard, the score comparison, the cap line, the coordinator's one line.

## Hot files, position, carries

After R10-DUTY-SWITCH-RESTART-LEARNING merges; part B after this group. Hot: `optimizer.py`, `pump_arbiter.py`, `coordinator.py` (one line), the learner module, the new leaf, `tests/features.py`, `tests/closures.json`, `docs/architecture.md`. Not touched: `dhw_planner.py`, `sensor.py`, `store.py`, `const.py`, `tests/golden/`.

## Decisions routed

- decision: orchestrator. The brief asks that the flat-price scenario leave the plan identical. That holds for the fixture as recorded (no learned values), which is test 4. With a latched learner it does not hold by construction: the term does not depend on prices, so a flat-price plan that holds a priced switch may move, and should. Confirm the control is the recorded fixture, or name the other reading.
- decision: owner, unchanged from round 1: B's minimum-share rule. This design composes with either answer.

## Notes for the fixer

- Every structure metric sits at zero headroom at the base (`python3 tests/structure.py`). The new functions are module-level in the leaf; lines added inside the optimizer class and the coordinator's one line are paid in the same class, and the `_share` move should pay part of it. No payment found is a stop and ask before the push. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c1)
- `DhwPlan` (`dhw_planner.py:211`) carries no shortfall field. The floor guard needs the planner's own tank simulation of the candidate against `floor_temps`; if that needs a new planner method, raise it rather than re-simulate in the optimizer. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c2)
- A start that sits exactly on a collapse edge gives the finite difference a slope of term / 1e-4. Test one such start and confirm the solve returns a plan scoring no higher than its start. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c3)
- Check that no fixture under `tests/golden/` snapshots the config's field list before adding the two fields. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c4)
- The learner module imports Home Assistant at its top at 12ddbb72bc (verdict item n13 asked otherwise); the planner read lives beside its registry, and the cap in the pure direction record. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c5)
- `_share` reads the plan's stored schedules; the objective reads realised draws. Run the agreement test on realised values of a clamped install too. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c6)
- The cap of 10 and the phi rule are constants from one day on one install, as part A's are. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c7)
- Re-read every anchor after the predecessor merges; its `pump_arbiter.py` diff adds about 90 lines above `_share`. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c8)
- The pull-request body thanks Bankaifan by name and pull request 3420. Carry: R10-DUTY-SWITCH-PLANNER-PRICE (item c9)
- B's designer: the order and the minimum share go into the leaf's leg rule, nowhere else. Carry: dismissed: part B has no roster group yet; stated in this note's composition section (item c10)

Seat tokens: subagents 31753, 36256, 37016, 55283, 56195 and 41312; the harness reports no figure for the main loop.
