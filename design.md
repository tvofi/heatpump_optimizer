# R11-OUTSIDE-START-APPROACH: a run's first steps draw what the pump draws, booked as energy and never as a fee

Designer seat, round 1. Base and `origin/main`: d3d66c40408e76351ffc528686353cadf815a05c (`VERSION` 10.1.3). Neither predecessor is merged into it; code read at their handoff heads, R11-OUTSIDE-HONEST-DHW-RUNS at 6f48176bb6 (`runs.py`, `optimizer.py`, `duty_legs.py`) and R11-SEAM-learners at 6a4b37067e (`draw_range.py`, `learning_freeze.py`). Every `path:line` below is at the head named beside it. `git merge-tree --write-tree 6f48176bb6 6a4b37067e` exits 1: the two conflict with each other, so the lines move once more before the fixer starts (revalidation, last section). The finding, the series and every figure quoted as theirs are Bankaifan's (comment 6944433306 on pull request 3670), with thanks; read as data. No finder harness: outside report; the series are re-measured below and the failing case is synthetic (Evidence).

## The four answers, measured

Spike s1 (in no tree; rule: 5-minute means of the comment's series A, D and H, excess = sum of (kW - 0.53) x 5/60, slope by least squares):

1. **The excess belongs to the entry into a low space level from a higher compressor state, not to the stop.** Series D, from off, 11:55 to 12:50: 0.377 kWh, slope -12.6 W/min. Series A, hot water to space with no stop, 22:25 to 23:45: 0.786 kWh, of which the loop's phase (22:25 to 22:45, out of scope) 0.379 and the pump's own wind-down (22:50 to 23:45, from 1.37 kW) 0.407 kWh at -14.8 W/min. Same descent, with and without a stop. In the plan's words the event is a **space-run entry**: a step with a space level after a step with none (off, or hot water only). A start of the combined draw is a different set: a charge beside a space run is no start, yet it is an entry.
2. **The money is small; the booked energy is wrong by a factor.** Runs of 15, 30, 45 and 60 min from off (series D) meter 2.26, 2.07, 1.88 and 1.71 times a plan at the floor. The heat is delivered, so the loss is only the entry price against the price the heat would have been bought at, and the higher level's COP: zero at a flat price and equal COP. What the plan gets wrong is how much each run delivers, which is why runs end early. A fee per start would charge for heat the house keeps. Not measured here: the closed-loop start count (Evidence 6).
3. **A learned level by run age, in a small module of its own beside `draw_range.py`; `runs.py` reads it as the draw of a run's first steps.** Nothing is added to the cycling cost or the duty-switch term, so nothing is priced twice: the energy cost and the heat read one received draw.
4. **The ramp-down counts into the run's energy, not its length.** Series H after the gate write at 07:30:28: 0.072 kWh over 330 s, one event, the last 240 s at 0.1 kW resolution. Booked the same way, in the first pause step. `MIN_PAUSE` (`runs.py:39` at 6f48176bb6) is not moved: decision below.

**Null** (the brief's): series A, 00:25 to 03:05, 33 samples: excess -0.009 kWh, mean 0.527 kW.

## Owning seam

**A new learner module beside `draw_range.py` owns** the evidence: per age bin since a space-run entry, and since a run's end, the pump's draw while the ask sat at the floor in force. **`runs.py` owns** what a plan's run draws given that profile (it already owns what a start is). **Callers only:** `draw_range.py` (`fold`, `draw_range.py:861` at 6a4b37067e, hands the interval on; `DrawRange.as_dict` and `from_dict` carry the leaves), `store.py` (declarations beside `draw/floor_kw`, `store.py:340` at 6a4b37067e), `coordinator.py` (one field at each of the two `compressor_running=` sites, `coordinator.py:6274` and `:11273` at 6f48176bb6), `optimizer.py` (`_shipped_and_received`, `optimizer.py:331` at 6f48176bb6, and the published heat at `optimizer.py:5968`). `tests/seam_map.json` maps coordinator methods only; no new method, no entry owed. Not touched: `pump_arbiter.py` (the loop and its constants), `duty_legs.py`, `dhw_planner.py`, the kernel (`advance`, `state_moves`, `read_back` at 6f48176bb6).

## Shape

**Learner (pure, numpy, no Home Assistant import).** State: two short arrays of kW by 5-minute age bin (after an entry; after a run's end), a sample count per bin, the age of the live space run in seconds. Fed once per fold with the metered draw, the split, the interval's end time and the gates `fold` already holds. An interval is an approach sample only if `is_running_space` (`draw_range.py:827` at 6a4b37067e) admits it and the space ask is at or under the floor in force by `AGREE_TOLERANCE`, the comparison `at_running_floor` (`draw_range.py:779` at 6a4b37067e) makes for the draw: a draw under a higher ask says nothing of the lowest the pump would go. It is a ramp-down sample only if the previous interval ran space, this one asks nothing, and the draw is above `RUNNING_FLOOR_KW`. A bin's level is the median of its last samples and reads as none under a minimum count; a level under the floor in force reads as the floor; the profile ends at the first bin within `AGREE_TOLERANCE` of the floor. A changed configured range drops it, as it drops the window (`DrawRange.observe`).

**Reading a plan (`runs.py`), one function and its batch twin, as `start_count` has.** From a space plan, the hot water beside it, the profile resampled to the plan's step and the live run's age: per step, the space draw the pump takes. Inside a space run at age j it is max(shipped, profile[j]) and never above `p_max` less the hot water; in the first steps of a pause, the ramp-down level; elsewhere the shipped level. Run age is read off the space plan alone (a step with no space level resets it), and at step 0 continues the live age. No profile, or an install that plans no runs: the shipped array itself, the same object.

**Objective (`optimizer.py`).** `_shipped_and_received` passes the shipped space plan through that function before `duty_legs.delivered_space` (`duty_legs.py:270` at 6f48176bb6), on the true objective only (a descent prices no edge, as it prices no start). `objective` already simulates the house on the received draw and costs `heat_power + dhw_plan_power` (`optimizer.py:5503` at 6f48176bb6), so electricity is paid at the entry step's price and the heat is credited by the model at that level, with no new term. The start term (`_start_cost_fn`, `optimizer.py:391`) and the switch term (`_switch_cost_fn`, `optimizer.py:355`) still read the shipped plan.

**Generator (`runs.commit`, `runs.py:117` at 6f48176bb6).** Its run action already receives whether the cell it leaves was running. Out of a pause it also moves the balance by, and pays the step's price for, the profile's energy above the level over the `lengths[0]` steps every run lasts. No kernel line changes; with no profile the action is `_shift` as it stands. The masks stay proposals the true objective judges (`_best_runs`, `optimizer.py:650`).

```
fold(interval) -> learner.observe(drawn, space ask, floor in force, end time, gates)   persisted with the draw record
coordinator    -> SolveInputs: profile + live run age, beside compressor_running
runs           -> received(space, hot water, profile, age)        commit: entry energy on a move out of a pause
optimizer      -> _shipped_and_received: received -> delivered_space -> simulate + energy cost   (start, switch: shipped)
shipped plan, asks, actuator writes: unchanged
```

**Invariants.** The ask is never raised: the shipped plan stays at the floor, so the loop asks what it asks today and the learner never learns from a level it caused. No evidence: every array equal to the base's, object for object. The received draw is never under the shipped one inside a run. One new status attribute beside `pump_min_power` (`sensor.py:2176` at 6f48176bb6), the learned entry energy in kWh at the floor, and the store leaves; no other payload key.

## Alternatives

- **A fee per start (learned kWh x price, beside the cycling cost):** charges for delivered heat (answer 2), and is keyed to combined-draw starts, which miss the entry after a charge (answer 1) and so would need a second term beside the duty-switch one, the double pricing the brief forbids.
- **Raise the shipped level along the profile:** the ask rises, the loop holds the pump up, the learner reads its own ask and the profile ratchets; a second writer of the level beside the candidate stage.
- **Run age as kernel state (exact for runs of any length in the generator):** rows grow from `sum(lengths)` to the profile's step count plus the pause (2 to 5 at a 15-minute step, 4 to 14 at 5 minutes) in both programs, on a kernel the predecessor just generalised; the judge is exact without it.
- **A slew limit on every step down (previous level as state):** continuous state; and no series shows a step down inside a space run under a known ask (A 03:45 to 04:40 and D 13:45 to 14:05 descend at -6.7 and -10.6 W/min, ask not in the report).
- **Inside `draw_range.py`:** a second concern in a module of over 1000 lines; step 17 names a small new one.

## Sibling sites

`git grep -n "delivered_space(\|_shipped_and_received(" 6f48176bb6 -- custom_components`: `optimizer.py:352`, `:5503`, `:5569`, `:5968`; all four covered (the objective, its batch twin, the published trajectory). `git grep -n "start_count\(_batch\)\?(\|edge_count(" 6f48176bb6 -- custom_components`: `dhw_charges.py:392`, `optimizer.py:5815`, `runs.py`; unchanged, they count starts. `git grep -n "observe_idle(" 6a4b37067e -- custom_components`: its one call, inside `fold`; measured first (note s3). Out of scope with an owner: the grid report's peak on the shipped total (`optimizer.py:3999`; decision below); hot-water charges' own approach (no series); the loop's constants (the brief).

## Evidence, by file

`tests/features.py`, failing today (the function, the learner and the input do not exist):
1. **Failing case.** A clamped install, floor 0.53 kW, a profile of series D's shape, a plan of one 15-minute run at the floor: the objective's energy cost and simulated room temperature equal those of the received draw's levels handed in as the plan, and differ from today's by the entry energy x price. Mutation, the call removed from `_shipped_and_received`: today's figures.
2. **Entry is the space edge, not the start.** A charge followed by a space run with no gap: one entry booked, start count unchanged. A level change inside a space run: none. Mutation, age read off the combined draw: no entry after the charge.
3. **Learner, both ends** (`fixer.md` step 3): zero evidence reads none; a bin under its count reads none; the comment's series D folded n times reproduces 0.377 kWh within the bin width; a draw under a higher ask, a frozen, a distorted and a defrost interval fold nothing; a level above the configured maximum is held to it; a configuration change drops the profile; a stored profile with a bad cell costs only that cell, declared so in `store.py`.
4. **Ramp-down.** Series H's shape folded: the first pause step books it; with the previous interval not running, nothing.
5. **Generator.** `commit` with a profile leaves out later energy for the entry's; with none, masks equal the base's on the leaf's existing cases.
6. **Measured, not asserted** (new arm of `dev/audit/harnesses/r11_honest_starts_runs.py`, on its installs): the shipped plan scored with and without the profile in the received draw (what today's plan costs against what it books); the plan solved with it; start count and worst comfort gap of each; and a plant-in-the-loop arm, the plant applying the profile and the planner knowing or not, printing starts per day. The harness is ours: no finder harness exists.

Null controls, a full `optimize` twice, arrays equal: no profile, with and without the input; a profile at or under the floor; a plan whose runs sit above the profile; an unengaged install. `python3 tests/env_drift.py --all`: no golden carries evidence, so none may move and no claim line is owed; one that moves is a defect, not a claim. Solve time: `tests/stress.py` at base and head. **Mutation targets:** the floor-ask gate; the count gate; the median; the reset of age at a step with no space level; the live age at step 0; the max with the shipped level; the `p_max` bound; the ramp-down's previous-interval gate; the true-objective-only guard; the commit action's pause test; the published trajectory's call.

## Hot files, position, carries

After R11-OUTSIDE-HONEST-DHW-RUNS (owns the kernel and `_shipped_and_received`'s neighbours) and R11-SEAM-learners (owns the gates `fold` hands on; received: the learner states which sample it folds and holds no facts, `learning_freeze.py` at 6a4b37067e). Hot: `runs.py`, `draw_range.py`, the new module, `store.py`, `accuracy.py`, `optimizer.py`, `coordinator.py`, `sensor.py`, `tests/features.py`, `tests/closures.json`, `tests/mutation_ledger/`, the harness, the D6 register (one attribute). No grader changes: no p1/p2 split. Revalidated against both merged diffs before the fixer dispatches.

## Decisions routed

- decision: orchestrator. Files: the roster lists `runs.py` and `draw_range.py`; the shape needs the eight production files above, most by one call or one declaration. A split, if wanted: p1 the learner, its store and the attribute (no plan moves); p2 the received draw and the generator.
- decision: owner. `MIN_PAUSE` is measured from the gate write; on this install the compressor stops about 5 min later, so a 10-minute planned pause is about 5 min of standstill. Not changed here.
- decision: owner. The grid report and a total power cap read the shipped total; an entry draws above it for up to an hour. The harness arm prints how many steps pass a cap; whether the cap reads the received draw is a product call.
- decision: orchestrator. The group is in the roster on handoff/audit-r11-roster (c02eba79d0) only; `git grep -l "R11-OUTSIDE-START-APPROACH" d3d66c4040` prints nothing.

## Notes for the fixer

- Spike s1's rule and figures land in the harness arm as printed figures, re-derived from the comment's series; they are one install's. Carry: R11-OUTSIDE-START-APPROACH (item s1)
- The bin width, the count gate, the sample depth and the profile's longest age are constants from one install: name them so, each beside the learner. Carry: R11-OUTSIDE-START-APPROACH (item s2)
- `fold` hands an interval held at the gate with no hot water asked to `observe_idle` (`draw_range.py:512` at 6a4b37067e); a ramp-down interval fits that description. Measure whether series H's draw reaches the idle store before changing anything; if it does, the ramp-down gate goes ahead of it in `fold`. Carry: R11-OUTSIDE-START-APPROACH (item s3)
- `optimizer.py` and `coordinator.py` are past the module limit `tests/structure.py` prices, so every line added there is paid in the same file; none found is a stop and ask before the push. The new module is classified in a closure. Carry: R11-OUTSIDE-START-APPROACH (item s4)
- The live run's age must survive a restart or read as unknown; unknown books no entry at step 0 while the compressor runs. Carry: R11-OUTSIDE-START-APPROACH (item s5)
- Under a priced stop the received draw passes through `delivered_space` after the profile; pin the order with a charge-to-space switch whose stop takes part of the entry step. Carry: R11-OUTSIDE-START-APPROACH (item s6)
- Credit Bankaifan and comment 6944433306 on pull request 3670 by name in every commit message and the body; nothing is written to the contributor's fork. Carry: R11-OUTSIDE-START-APPROACH (item s7)

Seat tokens: the harness reports none for this seat; two scouts, 68752 and 24857 tokens.
