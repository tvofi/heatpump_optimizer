# R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges shipped as runs, committed on the planner's own store

Designer seat, round 2, answering `Design review: revise` at design-verdict 9e83557135 on f7d50191e3. Group B of design/R11-OUTSIDE-HONEST-STARTS-RUNS at a63a2ca6cd (ruling c3's table, ruling b; `Design review: approve` at design-verdict 6e5cc74429). Base, code read and `origin/main`: 5854e4f69e361d841d7590ae0f868eea6758655f; `git diff --stat b425502da8 5854e4f69e -- custom_components tests/features.py tests/seam_map.json` prints nothing, so every line cited in round 1 stands and is cited at this base. Pull request 3602 (group A, merge 2c84a85c8c) is in it. Predecessor R11-OUTSIDE-HONEST-STARTS-RUNS-P2: no handoff head; its work in progress, handoff-wip dbc806ce5f, changes `tests/features.py` only and pins each half of the tie break. Outside pull request 3529 by Bankaifan read as data at 1f9daef4d93f (`git ls-remote origin refs/pull/3529/head`, 2026-11-16), build commit 7eeb7cd676; the finding, the store program, the tail rule and every figure quoted as theirs are the contributor's, with thanks. No finder harness: outside report; the failing case is reproduced below.

## Round 2: the verdict's three points

1. **The lifted plan passes the acceptance; only the uncommitted plan is unconditional. Accepted as asked.** Every candidate but the uncommitted plan, the lifted plan included, is ranked or shipped only if both clauses hold (Shape, acceptance). Measured here (spike, note s1): the start rule injected at ten hysteresis values from 0.5 to 10 K on `cycling_cost` and `everything_on`, 20 cells: the lifted plan loses no charge to `drop_unstartable` in any, and neither does the uncommitted plan. The failure is therefore not reproduced on a golden; the clause rests on the mechanism `place_startable` names (`dhw_planner.py:300`) and is pinned on a synthetic walk (test 2c). **A correction to round 1's table, row 3**, found by the same spike: the lifted plan was judged there under `_clamp_dhw_to_capacity` alone. Under the planner's own clamp (`_ctx_clamp`, `dhw_planner.py:1712`, which zeroes what the rating leaves under `min_run_power`), `cycling_cost` with the start rule off: charges 9 to 8, worst gap under the requirement 0.886 K against the uncommitted plan's 0.557 K. The lifted plan fails the shortfall clause there, start rule or no; `everything_on` passes (0.522 against 0.550, no step under the floor). Round 1's "holds 2 of 2" was 1 of 2 as the planner clamps.
2. **Test 2 is three arms, each with the observable its own mutation moves** (Evidence 2a, 2b, 2c).
3. **One advance and one read-back, the leaf's, generalised over a transition its caller supplies.** `runs._advance` (`runs.py:210`) and the read-back in `commit` (`runs.py:156`) become the one kernel both programs call (Shape, kernel). Spike (note s7), in no tree: `commit` rebuilt on the generalised kernel returns the mask of `runs.commit` on 1200 of 1200 random cases (three step lengths, three floors, forced steps, caps under the floor, `running` both ways, three start costs, each band of `BANDS`); an affine store with hard bounds and two on levels on the same kernel equals an exhaustive search's cost on 60 of 60 nine-step cases at 400 cells, 59 of 60 at 100 and at 20, and 0 of 60 with the bounds ignored (the null). Two kernels, the verdict's other arm, lost: the cheapest-arrival, exact-value and back-pointer lines would exist twice (`D7.md` item 8) with an agreement test to hold them together, where the spike shows one body serves both. **Churn on `runs.py`:** the kernel's signature and about a third of its 38 lines; six lines of `commit`'s loop (its two step tuples become two calls and a cell rule); the five read-back lines become a leaf function. `commit`'s signature, contract and masks do not move. P2's work in progress leaves `runs.py` untouched and its tie-break pins must stay green on B.

## Finding, reproduced

`_plan_dhw_min_cost` (`dhw_planner.py:1429`) is a linear program with no start term and no lower level; the passes after it raise a step to `min_run_power` (`dhw_planner.py:1141`), 0.6 of the pump's floor; `_realize_joint` (`optimizer.py:175`) returns the hot-water plan untouched on an install that can duty-cycle; the candidate stage pins every hot-water step on (`optimizer.py:544`). One box (x86_64), `PYTHONPATH=tests/hastub:custom_components:tests`:

- `dev/audit/harnesses/r11_honest_starts_runs.py fixtures`: `cycling_cost` space steps under the 1.0 kW floor 0, combined 11; `everything_on` 0 and 4.
- Spike (note s1; wraps `place_startable`, changes no production code), re-run at this base, the finished hot-water plan, `cycling_cost` / `everything_on`: charges 9 / 5, steps under the floor 14 / 10, worst gap 0.557 / 0.550 K.

Round 1's deciding measurement stands (its table, f7d50191e3): the leaf's `commit` as generator, at the plan's energy within a band or never behind it, holds the floors the plan held on 0 of 14 masks (worst gap 0.83 to 19.97 K), because an energy balance carries neither the floor nor the ceiling at a step. The generator is the planner's program on its own store.

## Owning seam

**`dhw_planner.py` owns** the commit of its plan to charges, the store, the transition, the bounds and the acceptance. **`runs.py` owns** the run and pause lengths, the move rule, the tie break, the start count, and the kernel (advance and read-back) on an opaque scalar. **Callers only:** `optimizer.py` (one constructor argument at `optimizer.py:4372`; one keyword on `_dhw_build`, `optimizer.py:401`; the last lines of `_combi_flux_exchange`, `optimizer.py:2040`). `tests/seam_map.json` maps coordinator units only; no entry is owed. Not touched: `thermal_model.py`, `duty_legs.py`, `coordinator.py`, `pump_arbiter.py`, the candidate stage.

## Shape

**Kernel (leaf).** The advance takes, per step: the moves; for running and for pausing a list of actions, each a call from the cells' scalars to the new scalars and what the action pays (infinite refuses); and a cell rule, a call from a scalar to its cell and any extra cost. It keeps the cheapest arrival per cell, that path's exact scalar, and the origin state, cell and action. The read-back returns, per step, on or off and the action taken. `commit` hands it one action each way and its band as the cell rule; the planner hands it the store. The leaf reads no temperature: the scalar's meaning, its grid and its bounds are the caller's calls. `_moves` (`runs.py:191`) gets a public name and one more argument, whether a start may be made at this step, default yes; the tie-break pair becomes one function both programs call.

**Store program (planner).** State (run or pause length, tank temperature on a grid). Transition: the one linear store the linear program builds inline (`dhw_planner.py:1496`: `tank_decay`, the draw and the combi flux in the free trajectory under it), moved to one planner helper both read (binding 2). Bounds, in the cell rule: floors min(requirement, the uncommitted plan's walk), ceilings max(per-step maximum, that walk). Running actions: at the floor and at the run power (carry 2). On an install that can duty-cycle, a charge that would pass the ceiling ends inside its last step (the contributor's tail), as a third action whose level reads the cell's temperature.

**Acceptance (planner), one function beside `drop_unstartable`**, taking a candidate, the start temperatures, the walk as a call, and the uncommitted plan's shortfall: true only if `drop_unstartable` (`dhw_planner.py:270`) returns the candidate unchanged on the candidate's own walk and `_dhw_shortfall` (`dhw_planner.py:1655`) is at no step above the uncommitted plan's (0.05 K, its tolerance). Each candidate is clamped by `_ctx_clamp` first.

**Commit stage, its own planner method** (verdict item r6), called after `place_startable` (`dhw_planner.py:1301`) returns the uncommitted plan P on walk W, only when engaged:
1. boolean = `startable_steps` (`dhw_planner.py:245`) of P on W;
2. program(boolean) proposes a plan; accepted, it is a candidate; refused for a start, that step is cleared in the boolean and the program runs again, at most `STARTABLE_ROUNDS`;
3. the lifted plan (each step of P under the floor raised to it) is a candidate if accepted;
4. candidates are ranked by energy at the planning prices plus `cycling_cost` x `start_count` of `space_demand` plus the candidate, with the running reading of `SolveInputs` (binding 4: a charge beside a space run is no start; the planner adds no stop term, so the duty-switch term stays the only price of a switch);
5. no candidate: P ships, today's plan, the only unconditional fallback. `place_startable` returns it through `drop_unstartable`, so it is startable by construction.
Pins, the Off window, a block and external-heat suppression are forced steps handed in and restated after, as today.

**Engaged or not.** The optimizer passes `_engaged` (`optimizer.py:194`), the cost and the running reading as one argument, default none. None: the planner's arrays are today's, object for object.

**Combi (binding 3).** Unchanged from round 1: the rounds of `_combi_flux_exchange` keep their order, cap and convergence test and run uncommitted; after them one committed build on the settled flux, kept only where the walk under the committed plan's own flux (one more `_combi_dhw_exo` and `combi_space_net_kw`) falls no further under the requirement than the round's plan; else the round's plan. Base, `dev/audit/harnesses/r10_combi_tank.py exchange`: 3 rounds, worst shortfall -1.455 K (round 1's reading). The contributor's recorded finding for R10-COMBI-TANK and the settle: Decisions.

```
optimizer: DhwPlanner(..., engaged) ; _dhw_build(first, replan, switch-ban: committed | exchange rounds: uncommitted, then one committed)
planner:   LP -> greedy -> min run -> clamp -> place_startable(repair)   = uncommitted plan P, walk W
  commit:  boolean = startable_steps(P, W)
           loop <= STARTABLE_ROUNDS: leaf kernel(moves(boolean), store actions, bounds) -> plan -> clamp -> accept? else clear the refused start
           lifted(P) -> clamp -> accept?
           rank accepted by price x energy + cycling_cost x runs.start_count(space_demand + plan) ; none accepted -> P
candidate stage (group A, unchanged): hot-water steps forced on, space committed around them
```

**Invariants.** Unengaged: identical. Engaged: every shipped plan is P or passed the acceptance, so every charge begins startable and no floor P held is lost, on every path; no shipped step lies between `MIN_RUNNING_DRAW_KW` and the floor but a tail on a duty-cycle install, or where P ships; `runs.commit`'s masks are the base's; no payload key, entity attribute or store key is added.

## The three body items (binding 6)

- **Unengaged combi double heating, and the settle: not built in B** (round 1's reason stands: the settle rewrites the space plan, the candidate stage's seam, a second owner; the contributor's 14.5 to 12.2 kWh is one install's and unmeasured here). Routed (Decisions).
- **A tail on a clamped install: not shipped.** `project_planned_levels` (`optimizer.py:190`) raises any level under the floor to it, so a tail there changes the contract R10-DUTY-SWITCH-PLANNER-PRICE's tests pin, in another owner. Measured by test 7; the owner decides.
- **A second level at the floor: built** (store program). Measured by test 4.

## Alternatives

- **The leaf's `commit` as generator:** 0 of 14 masks hold the floors.
- **Two kernels with an agreement test:** point 3 above.
- **The store as a value inside a program in `runs.py` (as built in 7eeb7cd676):** decay, drift, heat and bounds a second time beside `store_step` (`thermal_model.py:2138`) and the planner; the generalised kernel takes them as calls and holds none.
- **The lifted plan as the unconditional fallback (round 1):** refused by point 1; it loses a floor on `cycling_cost` as measured.
- **Raise `min_run_power` to the floor, nothing else:** no start is ever priced in the planner, and it is the lifted plan by another route.
- **The start rule per temperature cell inside the program:** a second copy of the comparison in `startable_steps`, which ruling b forbids.

## Sibling sites

`git grep -n "_dhw_build(" 5854e4f69e -- custom_components`: `optimizer.py:462`, `:2064` (exchange), `:3984`, `:5747`; all commit but the exchange's rounds. `git grep -n "min_run_power" 5854e4f69e -- custom_components`: `dhw_planner.py` only; the passes keep their quantum. `git grep -n "DhwPlanner(" 5854e4f69e -- custom_components`: `optimizer.py:4372`. `git grep -n "_advance(\|_moves(" 5854e4f69e -- custom_components`: `runs.py` only (one call each, in `commit`). Out of scope with an owner: space runs (A), the floor's value (R11-OUTSIDE-HONEST-METERED-FLOOR), the arbiter's own start rule (`pump_arbiter.py`).

## Evidence, by file

`tests/features.py`, failing today (the argument, the stage and the generalised kernel do not exist):
1. **Failing case:** a duty-cycle install, `cycling_cost` above zero: no shipped hot-water step between `MIN_RUNNING_DRAW_KW` and the floor but a run's last step; shortfall at no step above the uncommitted plan's; the start count of the combined draw no higher. Today: 14 and 10 steps under the floor.
2. **Ruling b**, on a synthetic fixture with the hysteresis set (no golden sets one):
   - **2a, the boolean.** The program's free first plan opens a charge on a step the walk refuses. Asserted: the shipped plan is a committed one (no step under the floor) and the program was called more than once and fewer than `STARTABLE_ROUNDS` times (the test wraps the program and counts). Mutation, the boolean not handed to the move rule: the same plan every round, none accepted, P ships; both assertions go red.
   - **2b, the start clause.** The acceptance called directly with a plan whose second charge opens at its start temperature on the supplied walk: refused. Mutation, the clause removed: accepted.
   - **2c, the lifted plan (point 1).** A walk where raising P's first charge to the floor warms the second charge's opening step to its start temperature, the program handed no feasible plan: P ships, byte for byte. Mutation, the lifted plan exempt from the acceptance: a charge `startable_steps` refuses ships. The same fixture with the lift's energy halved accepts the lifted plan (its null).
   - **2d, the shortfall clause.** `cycling_cost`'s shape (a clamped tail zeroed, 0.886 against 0.557 K): the lifted plan is not shipped. Mutation, the clause removed: it ships.
3. **Kernel:** `runs.commit` on the leaf's existing cases and P2's tie-break pins, unchanged; the read-back's action index on a two-level case; the exhaustive-search agreement of note s7 on small cases, with the bounds-ignored null.
4. **Two levels:** a fixture where the long charge at the floor is cheaper; with the floor action removed it ships dearer.
5. **Pricing:** a charge adjacent to a space run counts no start; `space_demand` none counts the charge's own.
6. **Combi:** the rounds' count equals the base's; the committed build kept, and refused, by the walk under its own flux, one fixture each.
7. **Measured, not asserted:** starts with the clamped tail allowed against refused on the three installs of `r11_honest_starts_runs.py` and the combi fixture, printed by the harness.
8. **Program cases** (the contributor's): a store full at a step gives a tail; a tail refused on a clamped install; forced steps kept; lengths at a 5-minute step.

Null controls, a full `optimize` twice, arrays equal: unengaged with and without the argument; engaged with a plan already at the floor or above and no start priced; a space-only solve at base and head (the kernel's churn moves no mask). `python3 tests/env_drift.py --all`: every fixture not claimed reproduces, and the run with one claim line removed goes red. **Goldens:** `cycling_cost`, `everything_on`, `coord_all_features` and any other as measured: each a line in `tests/golden/claimed_drift.txt`, a card fixture in `tests/golden/card_claimed_drift.txt` (verdict item r5), under the `claims-for:` live at build time (`VERSION` is 10.0.2 at the base), direction in the reason, none re-recorded, none claimed on expectation. No space-only fixture may move. Solve time: `tests/stress.py` at base and head. **Mutation targets:** the engaged guard; the boolean handed to the move rule (2a); the start clause (2b); the lifted plan's pass through the acceptance (2c); the shortfall clause (2d); the bounds in the cell rule; the floor action; the tail's install guard; the ranking's start term and its `space_demand`; the fallback to P; the kernel's cheapest-per-cell line and action index; the exchange's uncommitted keyword and its acceptance.

## Hot files, position, carries

After R11-OUTSIDE-HONEST-STARTS-RUNS (merged) and R11-OUTSIDE-HONEST-STARTS-RUNS-P2 (binding 5: B calls the tie break P2 rules and owns none); revalidated against P2's merged diff before the fixer dispatches. Hot: `dhw_planner.py`, `runs.py`, `optimizer.py`, `tests/features.py`, `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`, `tests/closures.json`, `tests/mutation_ledger/`, a new harness under `dev/audit/harnesses/`. Closures and the deployment shape re-derived on Linux. No grader changes: no p1/p2 split. Carries received: 0, 1 (acceptance and boolean), 2 (floor action). The verdict's items r1 to r6 stand as carried to the fixer.

## Decisions routed

- decision: orchestrator. Size: still three production files, one test file and one harness; `runs.py`'s churn is point 3's, and the verdict leaves sizing it to the orchestrator.
- decision: orchestrator. The settle and the unengaged double heating: a group of their own on the candidate stage's seam, design first, its first step the measurement (an arm of `r10_combi_tank.py`: the kWh the walk refuses at the store's limit, engaged and unengaged, zero exchange rounds as the null). The verdict records that combined draw under the floor can still ship on an engaged combi install after B, as it does at the head; item s5 prints it.
- decision: owner. The clamped tail, after test 7's figures.
- decision: orchestrator. `git grep -l "HONEST-DHW-RUNS" 5854e4f69e -- dev/programme` prints nothing: the dispatch payload is this group's only brief.

## Notes for the fixer

- The spike's readings (the finished plan's levels; the leaf's masks on the walk; the lifted plan under both clamps and under the start rule at each injected hysteresis) land in the new harness as printed figures. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s1)
- The program's grid, level set and any band are constants from one install: name them so. The grid decides optimality only (59 of 60 at 100 cells); the walk decides acceptance. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s2)
- Every structure metric may only move down; the shared store helper, the one kernel and the commit stage as its own method are the payment. None found is a stop and ask before the push. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s3)
- The exchange's committed build was not measured; if the walk refuses it on the combi fixture, report the shortfall and stop, do not widen the tolerance. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s4)
- The space plan is solved around the first committed plan and a re-plan may move a charge; print the published start count against the stage's on the fixtures. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s5)
- Credit Bankaifan and pull request 3529 by name in every commit message and the body. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s6)
- The kernel spike's two arms (mask equality with `runs.commit` over random cases; exhaustive-search agreement with its bounds-ignored null) land as test 3 and a harness arm; in the kernel the extra cost of the cell rule is added after the concatenation, as the fine is today, or the masks move in the last bit. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s7)
- The lifted plan lost its floor on `cycling_cost` through one tail the clamp zeroed; print, per fixture, which candidates the acceptance refused and by which clause. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item s8)

Seat tokens: the harness reports none for this seat; no scouts this round.
