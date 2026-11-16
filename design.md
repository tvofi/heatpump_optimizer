# R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges shipped as runs, committed on the planner's own store

Designer seat, round 1. Group B of design/R11-OUTSIDE-HONEST-STARTS-RUNS at a63a2ca6cd (ruling c3's table, ruling b; `Design review: approve` at design-verdict 6e5cc74429). Base, code read and `origin/main`: b425502da8d15c43f9494412e686a3d852b74358; pull request 3602 (group A, merge 2c84a85c8c, 38c254f3fb an ancestor) is in it. No predecessor handoff head: R11-OUTSIDE-HONEST-STARTS-RUNS-P2 is dispatched and unmerged, no `handoff/` ref (`git ls-remote origin 'refs/heads/handoff*/r11-outside-honest-starts-runs-p2*'` answers its comms ref only). Outside pull request 3529 by Bankaifan read as data at 1f9daef4d93f (`git ls-remote origin refs/pull/3529/head` on 2026-11-16 answers it), build commit 7eeb7cd676, merge base 870238eb21; the finding, the store program, the tail rule and every figure quoted as theirs are the contributor's, with thanks. No finder harness: outside report; the failing case is reproduced below. Every line cited is at the base.

## Finding, reproduced

`_plan_dhw_min_cost` (`dhw_planner.py:1429`) is a linear program with no start term and no lower level; the passes after it raise a step to `min_run_power` (`dhw_planner.py:1141`), 0.6 of the pump's floor, never to the floor; `_realize_joint` (`optimizer.py:175`) returns the hot-water plan untouched on an install that can duty-cycle; and the candidate stage pins every hot-water step on (`optimizer.py:544`) and commits space around it. Measured here, one box (x86_64), `PYTHONPATH=tests/hastub:custom_components:tests`:

- `dev/audit/harnesses/r11_honest_starts_runs.py fixtures`: `cycling_cost` space steps under the 1.0 kW floor 0, combined 11; `everything_on` 0 and 4.
- Own spike, in no tree (note s1): it wraps `_build_dhw_requirements` and `place_startable`, changes no production code, and judges a plan by `_clamp_dhw_to_capacity`, the planner's walk and `startable_steps`. The finished hot-water plan, `cycling_cost` / `everything_on`: charge steps 19 / 15, under the floor 14 / 10 (the last step of a run: 5 / 2), charges 9 / 5, 7.08 / 6.20 kWh, worst gap under the requirement 0.557 / 0.550 K, start count of the combined draw 5.90 / 5.66. The start rule is off in both fixtures.

## The measurement that decides the shape

Ruling b reads as generate and test: the leaf's `commit` (`runs.py:108`) proposes masks, the planner's walk accepts. Measured on the same two plans, each mask run at the larger of the plan's level and the floor under the run power:

| generator | masks | hold every floor the plan held | worst gap, K |
|---|---|---|---|
| `runs.candidates` as merged (energy within 2, 6, 24 floor steps either side) | 6 | 0 | 4.36 to 19.97 |
| the same program, never behind the plan's energy, 1, 2, 4, 8 floor steps ahead (a copy in the spike) | 8 | 0 | 0.83 to 9.21 |
| each step under the floor raised on its own, no program | 2 | 2 | 0.522, 0.522 |

Why, in the code: the leaf's state is electrical energy against the plan, and a floor step of it (0.25 kWh) is kelvins of this tank; a mask behind the plan misses a deadline, and a mask ahead is cut by the rating clamp (`_ctx_clamp`, `dhw_planner.py:1712`) and is behind afterwards. No band of an energy balance carries the two facts that decide a charge, the floor at a step and the ceiling at a step. So the leaf's commit is not B's generator. The third row holds the floors and bundles nothing (charges 9 / 5 unchanged, 7.56 / 6.91 kWh, 4 / 0 steps under the floor left, all tails).

## Owning seam

**`dhw_planner.py` owns** the commit of its plan to charges, the store it walks them on, and the acceptance. **Callers only:** `optimizer.py` (one constructor argument at `optimizer.py:4372`; one keyword on `_dhw_build`, `optimizer.py:401`; the last lines of `_combi_flux_exchange`, `optimizer.py:2040`), `runs.py` (called; two of its private rules become callable, below). `tests/seam_map.json` maps coordinator units only; no entry is owed. Not touched: `thermal_model.py`, `duty_legs.py`, `coordinator.py`, `pump_arbiter.py`, the candidate stage.

## Shape

**The store program, the planner's.** The contributor's program, built where the tank lives: a dynamic program over the steps with the state (run or pause length, tank temperature on a grid), each cell keeping the exact temperature of its cheapest path. It reads the one linear store the linear program already builds inline (`dhw_planner.py:1498`: `_tank_decay`, draw, combi flux): that block becomes one planner helper both read, so decay, drift, heat and bounds have one holder (binding 2). Floors are min(requirement, the uncommitted plan's walk) and ceilings max(per-step maximum, that walk), so the program is never asked for more than the plan kept. Three actions a step: off, on at the floor, on at the run power (carry 2: the long part-load charge of a modulating pump comes from the program). A charge that would pass the ceiling ends inside its last step (the contributor's tail) on an install that can duty-cycle only.

**What the leaf gives, and all it gives.** The run and pause lengths (`MIN_RUN`, `MIN_PAUSE`, `steps_at_least`); the move rule `_moves` (`runs.py:191`) under a public name with one more argument, whether a start may be made at this step, default yes, read by `commit` as today; the tie-break pair of `commit` (what a step pays for leaving the plan's own on/off reading) as one function both programs call; `start_count`. The leaf reads no temperature and holds no store.

**Ruling b, as calls.** The commit has the repair's calling shape and replaces nothing: after `place_startable` (`dhw_planner.py:1301`) returns, the planner computes `startable_steps` (`dhw_planner.py:245`) of the plan on its own walk and hands the boolean to the move rule. A committed plan is accepted only if `drop_unstartable` (`dhw_planner.py:270`) returns it unchanged on the plan's own walk and `_dhw_shortfall` (`dhw_planner.py:1655`) is at no step above the uncommitted plan's (0.05 K, its own tolerance). A refused start clears that step of the boolean and the program runs again, at most `STARTABLE_ROUNDS`. The program plans on the linear store; only the simulation accepts.

**What ships.** Candidates: each accepted committed plan, and the lifted plan (row 3; on a clamped install a tail goes to the floor or to zero). Ranked by energy at the planning prices plus `cycling_cost` x `start_count` of `space_demand` plus the candidate, with the running reading of `SolveInputs` (binding 4): a charge beside a space run is no start, and the planner adds no stop term, so the duty-switch term of the true objective stays the only price of a switch. Where nothing is accepted, the lifted plan if it holds the floors, else today's plan: never a refusal. Pins, the Off window, a block and external-heat suppression are handed in as forced steps and restated after, as today.

**Engaged or not.** The optimizer passes `_engaged` (`optimizer.py:194`), the cost and the running reading as one argument, default none. None: the planner's arrays are today's, object for object.

**Combi (binding 3).** The rounds of `_combi_flux_exchange` keep their order, their cap and their convergence test, and run uncommitted (the keyword on `_dhw_build`): a committed plan moves in whole steps and `np.allclose` on it need not settle. After the rounds, one committed build on the settled flux; it is kept only where the planner's walk under the committed plan's own flux (one more `_combi_dhw_exo` and `combi_space_net_kw`) falls no further under the requirement than the round's plan; else the round's plan lifted. Base, `dev/audit/harnesses/r10_combi_tank.py exchange`: 3 rounds, worst shortfall -1.455 K. Not measured here: the committed build on that fixture.

```
optimizer: DhwPlanner(..., engaged argument) ; _dhw_build(first, replan, switch-ban: committed | exchange rounds: uncommitted, then one committed)
planner:   LP -> greedy -> min run -> clamp -> place_startable(repair)            = uncommitted plan P, walk W
           engaged: boolean = startable_steps(P, W) -> store program (leaf: moves, lengths, tie break) -> masks
                    each mask: clamp -> walk -> drop_unstartable unchanged? shortfall <= P's?  -> accepted
                    rank accepted + lifted by price x energy + cycling_cost x runs.start_count(space_demand + plan)
candidate stage (group A, unchanged): hot-water steps forced on, space committed around them
```

**Invariants.** Unengaged: identical. Engaged: no shipped hot-water step lies between `MIN_RUNNING_DRAW_KW` and the floor but a tail on a duty-cycle install, or where today's plan ships as the fallback; no floor the uncommitted plan held is lost; every charge begins startable; no payload key, entity attribute or store key is added.

## The three body items (binding 6)

- **Unengaged combi double heating, and the settle pass: not built in B.** Reason: the settle rewrites the space plan, the candidate stage's and R10-COMBI-TANK's seam in `optimizer.py`, a second owner; and the finding itself says an unengaged plan holds it, so it is no part of runs. It is not measured here: the contributor's figure (14.5 to 12.2 kWh, one install) is unverified, and `finding-propagation.md` carries nothing unmeasured. Routed with its measurement (Decisions).
- **A charge ending inside its last step on a clamped install: not shipped.** Reason: `_realize_joint` raises any level under the floor to it (`project_planned_levels`, `optimizer.py:190`), so a tail cannot reach a clamped install's shipped plan without changing the contract R10-DUTY-SWITCH-PLANNER-PRICE's tests pin, in another owner. The fixer measures it (test 7) and the owner decides.
- **A second level at the floor: built** (Shape, three actions). Measured by test 4.

## Alternatives

- **The leaf's `commit` as generator (ruling b read literally):** 0 of 14 masks hold the floors (table).
- **The store as a value handed to a program in `runs.py` (as built in 7eeb7cd676):** its idle step, topped step and bounds are the tank's dynamics a second time; `store_step` (`thermal_model.py:2138`) and the planner would each have to change with it.
- **Raise `min_run_power` to the floor, nothing else:** holds the floors (row 3) and leaves 9 and 5 charges, the start count of the combined draw 4.39 and 5.00 (from 5.90 and 5.66); no start is ever priced in the planner (cause 4 stands). Kept as the fallback candidate, not the design.
- **Keep the exchange round that holds the store best (as built):** chooses among up to `_COMBI_EXCHANGE_ROUNDS` pairs each planned against the previous plan's flux; one committed build and one walk have one pair to verify (reasoned from the loop, not measured).
- **The start rule evaluated per temperature cell inside the program:** a second copy of `temps < start_below` beside `startable_steps`, what ruling b forbids.

## Sibling sites

`git grep -n "_dhw_build(" b425502da8 -- custom_components`: `optimizer.py:462` (the priced-switch ban's re-plan), `:2064` (exchange), `:3984` (pin and coil re-plan), `:5747` (first build); all commit but the exchange's rounds. `git grep -n "min_run_power" b425502da8 -- custom_components` prints 18 lines, all `dhw_planner.py`: the passes keep their quantum (they build the uncommitted plan; changing it moves unengaged fixtures). `git grep -n "DhwPlanner(" b425502da8` : `optimizer.py:4372` only. Out of scope with an owner: space runs (A), the floor's value (R11-OUTSIDE-HONEST-METERED-FLOOR), the arbiter's own start rule (`pump_arbiter.py`, reads `dhw_start_below_c` itself).

## Evidence, by file

`tests/features.py`, failing today (the argument and the program do not exist):
1. **Failing case:** a duty-cycle install, `cycling_cost` above zero, a plan like the spike's: no shipped hot-water step between `MIN_RUNNING_DRAW_KW` and the floor but a run's last step; the walk's shortfall at no step above the uncommitted plan's; the start count of the combined draw no higher.
2. **Ruling b:** with the start rule on (hysteresis set; the two goldens have it off, so a synthetic fixture), every charge begins on a step `startable_steps` passes on the shipped plan's own walk; with the boolean ignored a named fixture ships an unstartable charge.
3. **Program:** the contributor's cases (a store full at a step gives a tail; a tail refused on a clamped install; forced steps kept; run and pause lengths at a 5-minute step).
4. **Two levels:** a fixture where the long charge at the floor is cheaper than the run power's; with the floor action removed it ships dearer.
5. **Pricing:** a charge adjacent to a space run counts no start; `space_demand` none counts the charge's own.
6. **Combi:** the rounds' count equals the base's; the committed build is kept or refused by the walk under its own flux, one fixture each.
7. **Measured, not asserted:** starts with the clamped tail allowed against refused on the three installs of `r11_honest_starts_runs.py` and the combi fixture, printed by the harness.

Null controls, a full `optimize` twice, arrays equal: unengaged with and without the argument; engaged with a plan already at the floor or above and no start priced. `python3 tests/env_drift.py --all`: every fixture not claimed reproduces, and the control is run once with a claim line removed and goes red. **Goldens:** `cycling_cost` and `everything_on` move (11 and 4 steps at the base), `coord_all_features` and any clamped hot-water fixture as measured; each a claim line in `tests/golden/claimed_drift.txt` under the `claims-for:` live at build time (`VERSION` is 10.0.2 at the base), direction in the reason, none re-recorded, none claimed on expectation. Solve time: `tests/stress.py` at base and head. **Mutation targets:** the engaged guard; the boolean handed to the move rule; each acceptance clause; the floor and ceiling bounds; the floor action; the tail's install guard; the ranking's start term and its `space_demand`; the fallback order; the exchange's uncommitted keyword and its acceptance.

## Hot files, position, carries

After R11-OUTSIDE-HONEST-STARTS-RUNS (merged) and R11-OUTSIDE-HONEST-STARTS-RUNS-P2: P2 may change the tie break in `runs.py`, and B calls it and owns none (binding 5); this note is revalidated against P2's merged diff before the fixer dispatches. Hot: `dhw_planner.py`, `runs.py`, `optimizer.py`, `tests/features.py`, `tests/golden/claimed_drift.txt`, `tests/closures.json`, `tests/mutation_ledger/`, a new harness under `dev/audit/harnesses/`. Closures and the deployment shape re-derived on Linux. No grader changes: no p1/p2 split. Carries received: 0 (this group), 1 (Shape, ruling b), 2 (three actions).

## Decisions routed

- decision: design reviewer. Ruling b is kept as acceptance and as the boolean; its generator is the planner's program, not the leaf's commit, on the table's measurement.
- decision: orchestrator. The settle pass and the unengaged double heating need a group of their own on the candidate stage's seam, design first; its first step is the measurement (an arm of `r10_combi_tank.py`: the kWh the walk refuses at the store's limit, engaged and unengaged, with zero exchange rounds as the null).
- decision: owner. The clamped tail, after test 7's figures.
- decision: orchestrator. At the base no file under `dev/programme/rosters/` holds this group, P2 or the metered floor; the dispatch payload is this group's only brief.

## Notes for the fixer

- The spike's three readings (the finished plan's levels, the leaf's masks on the walk, the lifted plan) land in the new harness as printed figures, with its two-sided and never-behind arms as the perturbation. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s1)
- The program's grid, its level set and any band are constants from one install: name them so. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s2)
- Every structure metric may only move down; the shared store helper and the public move rule are the payment. None found is a stop and ask before the push. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s3)
- The exchange's committed build was not measured; if the walk refuses it on the combi fixture, report the shortfall and stop, do not widen the tolerance. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s4)
- The space plan is solved around the first committed plan and a re-plan may move a charge; print the published start count against the stage's on the fixtures. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s5)
- Credit Bankaifan and pull request 3529 by name in every commit message and the body. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s6)

Seat tokens: three read-only scouts, 90748, 95329 and 92892 (harness figures); the harness reports none for the main loop.
