# R11-OUTSIDE-START-APPROACH: a run's first steps draw what the pump draws, booked as energy and never as a fee

Designer seat, round 2, answering `Design review: revise 65d571d655167a2df9c9ab54529f8d883ad2d23b class-open` (design-verdict/R11-OUTSIDE-START-APPROACH at 4c0c286d03), point 1; everything under its "Checked, no point" is kept as round 1 wrote it and only re-anchored. Base and `origin/main`: 0e1eba2b4aafb5dbabbac7e0b0dc31b6ca1ad83e (`VERSION` 10.1.4). Neither predecessor is merged into it: R11-OUTSIDE-HONEST-DHW-RUNS is pull request 3805 at d74d12dd22, R11-SEAM-learners pull request 3835 at 7748bdc269. Every `path:line` below is at `origin/main` unless a head is named beside it. `git merge-tree --write-tree d74d12dd22 7748bdc269` still exits 1, so the lines move once more before the fixer starts (revalidation, last section). The finding, the series and every figure quoted as theirs are Bankaifan's (comment 6944433306 on pull request 3670), with thanks; read as data. No finder harness: outside report; the series are re-measured below and the failing cases are synthetic (Evidence).

## The four answers, measured

Spike s1 (in no tree; rule: 5-minute means of the comment's series A, D and H, excess = sum of (kW - 0.53) x 5/60, slope by least squares):

1. **The excess belongs to the entry into a low space level from a higher compressor state, not to the stop.** Series D, from off, 11:55 to 12:50: 0.377 kWh, slope -12.6 W/min. Series A, hot water to space with no stop, 22:25 to 23:45: 0.786 kWh, of which the loop's phase (22:25 to 22:45, out of scope) 0.379 and the pump's own wind-down (22:50 to 23:45, from 1.37 kW) 0.407 kWh at -14.8 W/min. In the plan's words the event is a **space-run entry**: a step with a space level after a step with none (off, or hot water only). A charge beside a space run is no start of the combined draw, yet it is an entry.
2. **The money is small; the booked energy is wrong by a factor.** Runs of 15, 30, 45 and 60 min from off (series D) meter 2.26, 2.07, 1.88 and 1.71 times a plan at the floor. The heat is delivered, so the loss is only the entry price against the price the heat would have been bought at, and the higher level's COP. A fee per start would charge for heat the house keeps. Not measured here: the closed-loop start count (Evidence 6).
3. **A learned level by run age, in a small module of its own beside `draw_range.py`; `runs.py` reads it as the draw of a run's first steps.** Nothing is added to the cycling cost or the duty-switch term: the energy cost and the heat read one received draw.
4. **The ramp-down counts into the run's energy, not its length.** Series H after the gate write at 07:30:28: 0.072 kWh over 330 s, one event. Booked in the first pause step. `MIN_PAUSE` (`runs.py:39`) is not moved (orchestrator ruling, last section).

**Null** (the brief's): series A, 00:25 to 03:05, 33 samples: excess -0.009 kWh, mean 0.527 kW.

## Owning seam

**A new learner module beside `draw_range.py` owns** the evidence: per age bin since a space-run entry, and since a run's end, the pump's draw while the ask sat at the floor in force; and the live run's age. **`runs.py` owns** what a plan's run draws given that profile (it already owns what a start is), for a whole plan and for the one live step. **Callers only:** `draw_range.py` (`fold`, `draw_range.py:849`, hands the interval on; `DrawRange.as_dict` and `from_dict` carry the leaves), `store.py` (declarations beside `draw/floor_kw`, `store.py:342`), `coordinator.py` (one field at each `compressor_running=` site, `coordinator.py:6274` and `:11266`; and the expected draw beside `_commanded_power`, next section), `optimizer.py` (`_shipped_and_received`, `optimizer.py:322`, and the published heat at `optimizer.py:5928`). `tests/seam_map.json` maps coordinator methods: the one new accessor owes its entry. Not touched: `pump_arbiter.py`, `duty_legs.py`, `dhw_planner.py`, `accuracy.py`, `defrost.py`, the kernel.

## Shape

**Learner (pure, numpy, no Home Assistant import).** State: two short arrays of kW by 5-minute age bin (after an entry; after a run's end), a sample count per bin, the age of the live space run. Fed once per fold with the metered draw, the split, the interval's end time and the gates `fold` already holds. An interval is an approach sample only if `is_running_space` (`draw_range.py:815`) admits it and the space ask is at or under the floor in force by `AGREE_TOLERANCE` (the comparison `at_running_floor` makes for the draw, `draw_range.py:779` at 7748bdc269). It is a ramp-down sample only if the previous interval ran space, this one asks nothing, and the draw is above `RUNNING_FLOOR_KW`. A bin's level is the median of its last samples and reads as none under a minimum count; a level under the floor in force reads as the floor; the profile ends at the first bin within `AGREE_TOLERANCE` of the floor. A changed configured range drops it (`DrawRange.observe`).

**Reading a plan (`runs.py`), one function and its batch twin, as `start_count` has.** Per step, the space draw the pump takes: inside a space run at age j, max(shipped, profile[j]), never above `p_max` less the hot water; in the first steps of a pause, the ramp-down level; elsewhere the shipped level. Run age is read off the space plan alone and at step 0 continues the live age. No profile, or an install that plans no runs: the shipped array itself, the same object.

**Objective (`optimizer.py`).** `_shipped_and_received` passes the shipped space plan through that function before `duty_legs.delivered_space` (`optimizer.py:343`), on the true objective only. `objective` already simulates the house on the received draw and costs `heat_power + dhw_plan_power` (`optimizer.py:5480`). The start term (`_start_cost_fn`, `optimizer.py:382`) and the switch term (`_switch_cost_fn`, `optimizer.py:346`) still read the shipped plan. **Generator (`runs.commit`, `runs.py:108`):** out of a pause the run action also moves the balance by, and pays the step's price for, the profile's energy above the level; with no profile it is `_shift` as it stands; masks stay proposals the true objective judges (`_best_runs`, `optimizer.py:641`).

**Expected draw (`coordinator.py`), the answer to revise point 1.** One accessor beside `_commanded_power` (`coordinator.py:4954`): the same `runs.py` function on the live step, returning the draw the plan expects of the meter (shipped total plus the profile's excess at the live age) and whether the live step sits inside the profile (an entry bin or a ramp-down bin that holds a level). With no profile it returns `_commanded_power()`'s own value and false. Each reader below takes one of three dispositions; the shipped figure, the asks and the actuator writes are unchanged.

```
fold(interval) -> learner.observe(drawn, space ask, floor in force, end time, gates)   persisted with the draw record
coordinator    -> SolveInputs: profile + live run age;  expected draw + inside-profile flag for the live step
runs           -> received(space, hot water, profile, age)        commit: entry energy on a move out of a pause
optimizer      -> _shipped_and_received: received -> delivered_space -> simulate + energy cost   (start, switch: shipped)
```

## The axis: every reader that pairs the plan's shipped draw with a meter

**Rule.** The shipped draw reaches a reader by four roads, each a command at `origin/main` over `custom_components`: (R1) `git grep -n "_commanded_power()\|_commanded_split()"`, 20 call lines in `coordinator.py`; (R2) `git grep -n "predicted_power_kw\|pending\[\"split\"\]\|pending.get(\"power\")"`, the settled interval's copy; (R3) `git grep -n "plan_promise(\|power_schedule"` in `accuracy.py` and `coordinator.py`, the horizon's copy; (R4) `git grep -n "action.get(\"power\"\|get(\"dhw_power\""` in `coordinator.py`, the direct reads and the pending split's second copy. Every line the four return has a disposition below; a line is on the axis only where a measured quantity stands in the same expression or callee, and the rest fall in category P. Pull request 3835 adds R1 lines that hand the split to `_space_evidence` only (`coordinator.py:968`, `:5335`, `:5771`, `:5931`, `:10996` at 7748bdc269): category W.

**E, reads the expected draw.**
- `coordinator.py:10055`, the pending prediction's power, which becomes `predicted_power_kw` (`coordinator.py:10000`). Its three readers follow with no line of their own: `delivered_ratio` (`accuracy.py:639`) into the defrost derate (`_settle_defrost`, `coordinator.py:9897`), `power_ratio` (`accuracy.py:381`), and the sample's predicted cost (`coordinator.py:10007`) into the cost error; and the ledger's plan line (`ledger.py:368`), whose `meter_calibration` divides metered by planned kWh and scales stored savings.
- `coordinator.py:4993`, `_interval_space_power`'s tracking gate: spike s3 reads 1.18, 0.82, 0.47 against the 0.3 gate on series D's first three 15-minute steps, so the fabric learner loses every entry today; it returns the metered figure, so only the gate's reference moves.
- `plan_promise`'s cost (`accuracy.py:571`): the coordinator files the promise from the space schedule passed through the `runs.py` function, the array the objective costed.

**G, gated off while the live step is inside the profile.**
- `coordinator.py:5292`, `_fold_measured_cop`: drawn over asked is no efficiency reading during a wind-down. Spike s3, 40 runs of series D's shape then 2 h at the floor, no draw window: 80 of 160 entry rows fold as an efficiency shift and the walking ratio peaks at 1.307; null (all rows at the floor) 1.000. The interval reads `COP_REFUSED_OFF_ASK` and does not walk the ratio.
- `coordinator.py:10056` into `draw_range.fold` (`coordinator.py:9965`): the interval goes to the new learner and adds no asked-drawn pair to the window (`DrawRange.observe`, `draw_range.py:485`), whose disagreement count and `ask_evidence` would read it as a pump that ignores its ask.

**Residue, by category, each unchanged.** **F, fallback:** the shipped figure stands in only where no meter reading exists (`coordinator.py:5182` external heat, `:8630` realised peak, `:8887` headroom, `:10261` the energy ledger, `:11021` the fit's settle sample); the learner has no evidence without a meter, so expected equals shipped there. **T, threshold:** the figure answers runs or not, or nameplate or not (`:963`, `:3552` and `:9056` `immersion_over`, `:4504`, `:5582`, `:9270`, `:10751`, `:10947`); a level at the floor answers as before, and the received draw is bounded by `p_max`. **W, weights:** the split apportions a measurement between space and hot water and no power magnitude is compared (`:970`, `:1002`, `:1096`, `:1137`, `:1175`, `:1262` with its two readers at `:1283` and `:10283`, `:5256`); a ramp-down under an all-zero split leaves 0.072 kWh per stop unattributed, stated, not fixed. **A, ask:** the figure is written to the pump (`:10800`, `:10839`); the ask is never raised. **P, plan only:** published, resampled or simulated with no measured quantity in the expression (`:2364`, `:3121`, `:3176`, `:4809`, `:10554`, `:10603`). **Record:** `room_record.House` (`:6076`) stores the split beside the meter; its readers in `room_history.py` fit the metered figure and read the split as runs or not. `:4971` is the accessor's own body. **Kept by ruling, named:** `_power_headroom` (`:8900`) subtracts the shipped schedule and a metered baseline from the limit (last section).

**The reviewer's example, measured (spike s2, at 7748bdc269).** `scale_response` is the install's standing verdict from the dither probe, not a reading of the interval: `MeasuredCop()` reads pending, 480 entry-and-floor rows leave it pending with no contrast, and `learning_freeze.reason` on `Sample.DELIVERED_RATIO` returns none unless the verdict already reads ignored. So `REASON_ASK_IGNORED` is not the gate. Series D's shape at 2 C, four runs a day, folded through `DefrostDerate.observe` under that gate: the derate reaches 0.930 (5-minute cycle) and 0.947 (15-minute); null at the floor 1.000.

## Alternatives

- **A fee per start:** charges for delivered heat (answer 2), is keyed to combined-draw starts, which miss the entry after a charge, and leaves every reader above comparing the meter with the floor.
- **Raise the shipped level along the profile:** the ask rises, the loop holds the pump up, the learner reads its own ask; a second writer of the level. It would close the axis for free, which is why it is named.
- **Gate every comparing reader (no E):** the defrost derate, the fabric learner and the accuracy panel lose the first hour of every run, most of the samples of an install that cycles; and `learning_freeze.py` gains a reason whose evidence the plan already knows.
- **Run age as kernel state:** rows grow from `sum(lengths)` to the profile's step count plus the pause in both programs; the judge is exact without it.
- **Inside `draw_range.py`:** a second concern in a module of over 1000 lines.

## Sibling sites

Objective side, `git grep -n "delivered_space(\|_shipped_and_received("`: `optimizer.py:343`, `:5463`, `:5529`, `:5928`; all covered. `git grep -n "start_count\(_batch\)\?(\|edge_count("`: `runs.py:92`, `optimizer.py:5775`, and `dhw_charges.py:392` at d74d12dd22; unchanged, they count starts. `observe_idle(`: its one call, `draw_range.py:885`; note s3. Meter side: the axis section. Out of scope with an owner: hot-water charges' own approach (no series); the loop's constants (the brief).

## Evidence, by file

`tests/features.py`, failing today:
1. **Failing case.** A clamped install, floor 0.53 kW, a profile of series D's shape, a plan of one 15-minute run at the floor: the objective's energy cost and simulated room temperature equal those of the received levels handed in as the plan. Mutation, the call removed from `_shipped_and_received`: today's figures.
2. **Entry is the space edge, not the start.** A charge followed by a space run with no gap: one entry booked, start count unchanged. Mutation, age read off the combined draw: no entry.
3. **Learner, both ends:** zero evidence reads none; a bin under its count reads none; series D folded n times reproduces 0.377 kWh within the bin width; a draw under a higher ask, a frozen, a distorted and a defrost interval fold nothing; a configuration change drops the profile; a stored profile with a bad cell costs only that cell.
4. **Ramp-down.** Series H's shape folded: the first pause step books it; with the previous interval not running, nothing.
5. **Generator.** `commit` with a profile leaves out later energy for the entry's; with none, masks equal the base's.
6. **Measured, not asserted** (new arm of `dev/audit/harnesses/r11_honest_starts_runs.py`, ours; no finder harness exists): the shipped plan scored with and without the profile; the plan solved with it; start count and worst comfort gap; a plant-in-the-loop arm printing starts per day and the steps whose received total passes a power cap.
7. **The axis (failing today, from spikes s2 and s3).** Series D's entry settled through `_record_accuracy` in the frost band with no defrost sensor and a learned profile: no derate moves, `power_ratio` and the cost error read 1 and 0 within the bin width, the fabric interval is kept, no COP row folds and the walking ratio stays at 1, the window gains no pair. Null: the same entry with no profile gives today's figures for each (0.947 for the derate), and a run at the floor moves nothing either way. Mutations: the pending power back to `_commanded_power()`; the inside-profile flag forced false; the promise filed from the shipped schedule.

Null controls, a full `optimize` twice, arrays equal: no profile; a profile at or under the floor; a plan whose runs sit above the profile; an unengaged install. `python3 tests/env_drift.py --all`: no golden carries evidence, so none may move and no claim line is owed. Solve time: `tests/stress.py` at base and head. **Mutation targets:** the floor-ask gate; the count gate; the median; the age reset; the live age at step 0; the max with the shipped level; the `p_max` bound; the ramp-down's previous-interval gate; the true-objective-only guard; the commit action's pause test; the published trajectory's call; the three of case 7.

## Hot files, position, carries

After R11-OUTSIDE-HONEST-DHW-RUNS and R11-SEAM-learners (received: the learner states which sample it folds and holds no facts). Hot: `runs.py`, `draw_range.py`, the new module, `store.py`, `optimizer.py`, `coordinator.py`, `sensor.py` (one status attribute beside `pump_min_power`, `sensor.py:2176`), `tests/features.py`, `tests/closures.json`, `tests/seam_map.json`, `tests/mutation_ledger/`, the harness, the D6 register. `accuracy.py` leaves the list: its readers move through the sample. No grader changes. Revalidated against both merged diffs before the fixer dispatches.

## Decisions, as ruled and as routed

- Ruled (orchestrator, mandate 6893738184): split p1/p2 if the file count stays above eight. It is seven production files now, so one pull request; if the fixer's count passes eight, p1 is the learner, its store and the attribute, p2 the received and expected draw.
- Ruled (same): `MIN_PAUSE`, the grid report (`optimizer.py:3958`) and the power cap keep reading the shipped total. The enumeration returns one reader on that ground, named for owner decision and not changed: `_power_headroom` (`coordinator.py:8900`) offers limit less shipped schedule less metered baseline, so on an entry step it offers up to 0.72 kW (series D, 1.25 less 0.53) the pump is already drawing. Nothing compares the projected peak with the realised one (`coordinator.py:8630` reads the meter; `git grep -n projected_peak_kw` returns a fuse margin, a log line and two publishes). Harness arm 6 prints the steps.
- decision: orchestrator. The group is in the roster on handoff/audit-r11-roster only; `git grep -l "R11-OUTSIDE-START-APPROACH" origin/main -- dev .claude` prints nothing.

## Notes for the fixer

- Spike s1's rule and figures land in the harness arm as printed figures, re-derived from the comment's series; they are one install's. Carry: R11-OUTSIDE-START-APPROACH (item s1)
- The bin width, the count gate, the sample depth and the profile's longest age are constants from one install: name them so. Carry: R11-OUTSIDE-START-APPROACH (item s2)
- `fold` hands an interval held at the gate with no hot water asked to `observe_idle` (`draw_range.py:512`); a ramp-down interval fits that description. Measure whether series H's draw reaches the idle store; if it does, the ramp-down gate goes ahead of it in `fold`. Carry: R11-OUTSIDE-START-APPROACH (item s3)
- `optimizer.py` and `coordinator.py` are past the module limit `tests/structure.py` prices, so every line added there is paid in the same file; none found is a stop and ask before the push. Carry: R11-OUTSIDE-START-APPROACH (item s4)
- The live run's age must survive a restart or read as unknown; unknown books no entry at step 0 and reads as not inside the profile. Carry: R11-OUTSIDE-START-APPROACH (item s5)
- Under a priced stop the received draw passes through `delivered_space` after the profile; pin the order. Carry: R11-OUTSIDE-START-APPROACH (item s6)
- Credit Bankaifan and comment 6944433306 on pull request 3670 by name in every commit message and the body. Carry: R11-OUTSIDE-START-APPROACH (item s7)
- Run the axis rule's four commands at the merge base and compare with the lines listed; a line the rule returns and no disposition names is a stop. Carry: R11-OUTSIDE-START-APPROACH (item s8)
- Spikes s2 and s3 (in no tree): series D's shape as 1.25 kW falling 12.6 W/min to 0.53, means per cycle, through `DefrostDerate.observe`, `MeasuredCop.walk_ratio` and the ratio gate; they become case 7. Carry: R11-OUTSIDE-START-APPROACH (item r1)

Seat tokens: the harness reports none for this seat; round 2's three scouts, 206795, 59293 and 46402 tokens.
