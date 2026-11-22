# Design note: R11-OWNER-MODE-LEGS -- minimum mode legs and no cycle/tick reversal

Code read at `origin/main` 3a98735a7ecc59e7ecc095a0429cdf6251d956ec; no predecessor handoff.
Evidence: the owner's report from a private diagnostics bundle, not committed.
**No finder harness: owner report.** The owner's account, in general terms:

- Every Heating to DHW switch on his pump is followed by a short P3 protection trip, because the hot tank return reaches the inlet probe first.
- Heating legs of a few minutes between DHW legs multiply these trips, and a cluster of them came right before a latched fault.
- Twice, a cycle pass wrote DHW and the minute tick wrote Heating seconds later, and a fault followed both times.

The owner approved two fixes: (1) minimum mode-leg lengths, and (2) no reversal of a cycle-pass write by the tick. Every number below is invented.

## Owning seam

Mode selection is owned by `custom_components/heatpump_optimizer/pump_arbiter.py`. `_step_duty` picks the duty, `_served` (through `_share`) picks the duty a pass serves, `_mode_for` maps it to a mode, and `_write` is the only mode writer. `_lead_mode` reaches the same path through `_served`.

How a both step splits into legs is a separate concern, already owned by the leaf `custom_components/heatpump_optimizer/duty_legs.py`, which is "one rule for the arbiter ... and the planner". The arbiter serves that rule through `duty_switch.both_step_duty`, and `optimizer.py` prices it through `leg_ends`, `availability` and `switch_weights_batch`.

The minimum-leg rule is a leg rule, so it lives in `duty_legs.py`, and both consumers read the one implementation. The execution-time latch lives in `custom_components/heatpump_optimizer/duty_switch.py`, which already hears every landed mode write (`note_mode_write`) and latches each both step's legs (`_Record.order`). `pump_arbiter.py` only calls it. One concern, one owner each: there is no split.

## Root cause of the seconds-long leg (fix 2)

`duty_switch.both_step_duty` latches a step's legs at the first pass in the step, and then measures them from the step's **start**. Suppose a re-solve turns the current step into a both step mid-step, and the DHW-first leg ends just after the cycle pass. Then the cycle pass serves DHW, a mode write, and the next tick crosses `start + legs[0][1]` and serves Heating. Both passes read the same plan.

This is the only path found by reading `_served` and `_share`:

- A both step present in the plan before the cycle would have served DHW from the step's start, so the cycle would have written nothing.
- Lease expiry and a stale plan give the baseline (Heat + DHW), not Heating.

The bundle cannot confirm the path. The failing test below reproduces it on invented numbers, and the latch in fix 1b closes every other cause anyway.

**Change.** `_Record.order` gains the time the latch was decided. A first leg whose remaining time at that moment is under its minimum is skipped: the step serves its last leg.

## Shape

**1a. Plan rule (`duty_legs.py`).** Two module constants:

- `HEAT_LEG_MIN_MINUTES = 10.0` (N)
- `DHW_LEG_MIN_MINUTES = 10.0` (M)

Both are ≤ `PLAN_STEP_MINUTES`. That bound is an invariant: whole steps are at least one step long, so only a split step can make a short leg, and the rule needs only adjacent steps.

On the leg timeline, after today's `SPLIT_MIN_MINUTES` collapse and learned `extra` merge:

- **Idle continues the mode.** An idle step writes no mode (`_mode_for`), so leg codes are forward-filled across idle before adjacency is read. A leg is mode time, not run time.
- **R1, DHW floor.** A DHW leg not joined to a neighbouring DHW leg and shorter than M is lengthened to M. The step's heating leg shrinks to match.
- **R2, sandwich.** A heating leg with DHW on both sides and shorter than N is served as DHW, so the step becomes whole DHW and the DHW legs merge.
- **Iteration.** The vectorised pass repeats until nothing changes. It is monotone: it only turns legs into DHW or lengthens them, so it ends within the plan's step count. One pass is not enough: a step merged by R2 can create a new sandwich in the next step, and test T5 pins that case.

`LegRule` becomes a `NamedTuple` `(first, extra, before=IDLE)`. `before` is the leg code the pump is in when the solve starts, and it is step 0's left neighbour. The existing call sites pass it through unchanged. The two `first, extra = rule` unpackings become attribute reads.

`both_step_legs`, the scalar copy that a test pins equal today, is replaced. `step_legs(space_kw, dhw_kw, i, floor, rule)` returns step `i`'s legs and minutes by running the vectorised function on the plan's arrays. The arbiter and the planner then share one implementation.

**1b. Execution latch (`duty_switch.py`).**

- `_Record.leg = (mode, since, previous)` is set in `note_mode_write` whenever the mode key changes. It is set before the `loaded` check and kept in memory only.
- `held_leg(rec, wanted, now, exempt) -> duty` keeps `"dhw"` while a DHW leg is younger than M.
- It also keeps `"space"` while a heating leg is younger than N and entered from DHW.
- Otherwise it returns `wanted`.
- `exempt` passes through unchanged: a live boost, a disinfection hold, a mode other than Auto or Economy, a duty of `None`, `"idle"` or `"both"`, and (once R11-OWNER-FROST-HOLD lands) a frost hold.

In `pump_arbiter._served`, the latch sits between `_share` and `_without_block`, so a block still drops a duty at once. `_lead_mode` inherits it.

Flow: tick or cycle → `_step_duty` → `_share` (legs from `duty_legs.step_legs`, latched with their decision time) → `duty_switch.held_leg` → `_without_block` → `desired` → `_write` → `_report_write` → `note_mode_write` (sets `leg`).

**Invariants.**

- A step with no both step beside a DHW leg is served exactly as today.
- Nothing writes Cooling.
- A block or a boost is never delayed.
- After a restart the latch is empty, which is today's behaviour.

## N and M: defaults, not options

Both are constants in `duty_legs.py`, not config-flow options:

- The rule's one-step neighbourhood needs N and M ≤ 15. An option would have to carry that bound.
- `config_flow.py` is over `MODULE_LOC_LIMIT`, and `module_excess_loc` has no headroom.
- No install is known to need other values.

Promoting them to options later is a config-flow row and an `EntryConfig` read. **Open for the owner:** constants (recommended), or options bounded to 0..15, where 0 means off.

## Planner interaction: the plan prices what is executed

R1 and R2 move minutes between duties at a fixed step draw: the step still runs at its level for 15 minutes. The electricity cost is therefore unchanged. The house gets fewer minutes and the tank more.

- **The house side** is priced by generalising `optimizer._stop_availability` into a leg availability. A step's availability is 1 minus (minutes the rule moved off heating plus today's priced stop loss) over 15. It is read from the solve's start profile, the existing pattern.
  - It is computed whenever the rule moves minutes, not only when a stop is priced.
  - `space_headroom` (duty-cycle installs) and `delivered_space` (clamped installs) consume it unchanged.
  - Test T8: an R2 step delivers zero space heat. A step the rule does not touch gives `None`, today's arrays.
- **The tank side** gains the moved minutes, capped by its own thermostat. The next solve reads that gain from the tank sensor. It is not priced: this is stated, and the harness counts it.
- **`switch_weights_batch`** reads the merged legs, so fewer switches are priced where the rule merges.
- **`before`** goes to the solve through `duty_switch.planner_fields` as `duty_leg_before`, plus one `OptimizationConfig` field, so step 0's left neighbour is the real leg.
- **Residual.** The latch acts only when a re-solve changes the step already being executed. That differs from what the plan priced by at most max(N, M) minutes of step 0 per re-solve, and the harness measures it.

## Alternatives

1. **Latch only, no plan rule.** Lost: the arbiter would reshape every both step next to a DHW leg after the plan priced it, so priced and delivered space heat differ on every such step, not only step 0.
2. **Plan rule only.** Lost: a mid-step re-solve and the cycle/tick case happen at execution time, and no plan can see them.
3. **A scalar copy of the rule in `duty_switch.py`.** Lost: two implementations of one rule. Today's `both_step_legs`/`leg_ends` pair already needs a test pinning them equal.
4. **Measuring legs from the latch time alone (fix 2 only).** Lost: it covers the one mechanism, not re-solve flips at a cycle pass.
5. **A persisted latch.** Lost: a restart is rare, and an empty latch behaves as today does.

## Sibling sites

`grep -n "both_step_legs\|leg_ends\|both_step_duty\|_served(\|_share(\|note_mode_write" custom_components/heatpump_optimizer/*.py`:

- `duty_legs`: `leg_ends`, `availability`, `switch_weights_batch`, `switch_ban`. All read the rule through `leg_ends` and are covered.
- `duty_switch.both_step_duty`: covered.
- `pump_arbiter`: `_served`, `_lead_mode`, `_share`, `_report_write`: covered.
- `optimizer`: `_leg_rule` and `_stop_availability`: covered.

Out of scope, because they write no single-duty switch: `release()` (the baseline row), `hold()` re-sends (same mode), and the `_leased` lease expiry (a rail, so exempt).

## Evidence plan

Tests go in `tests/features.py` beside the `_ds_legs` cases and are written failing first. Each has a null control.

| test | case | null control |
|---|---|---|
| T1 (fix 2) | Step at 00:00 is space, and the tick writes Heating. A re-solve at 00:09:48 makes it a both step with space 1.0 kW and DHW 2.0 kW (DHW leg 10 min). Today the cycle writes DHW and the 00:10:00 tick writes Heating. After the fix there is no DHW write. | The same plan adopted at 00:00 writes DHW at 00:00 and Heating at 00:10. |
| T2 | The tick writes DHW. One minute later a re-solve makes the step space. Heating is not written before M. | A DHW leg already M old switches at once. A space boost pressed in that minute switches at once. |
| T3, R1 | (space, both with a 6-min DHW share, space) gives (DHW 10, space 5). | The same step after a DHW step is unchanged. |
| T4, R2 | (dhw, both with DHW 8 and space 7, dhw) gives whole DHW. | Next step space: the split is kept. |
| T5 | A merge cascade: no heating leg under N between DHW legs. | One pass alone leaves one. |
| T6 | Idle forward-fill: (dhw, both with space 5, idle, dhw) is not merged. | Without the idle step it is merged. |
| T7 | Seeded random plans: every leg on the timeline meets its minimum. | N = M = 0 fails the same check on the same seed, which proves the generator reaches these cases. |
| T8 | Availability, as under the planner section. | — |
| T9 | Arbiter and planner parity: the minute-by-minute served duty equals the `leg_ends` timeline. | A mutant reading the old scalar path diverges. |
| T10 | Exemptions (boost, block, disinfection, non-plan mode, cooling) pass through. | — |

Mutation targets: the `< M` and `< N` comparisons, the forward-fill, the fixed-point loop, the latch's age comparisons and its `previous == DHW` guard, the decision-time skip in `both_step_duty`, and the `exempt` branch.

Goldens: plan fixtures with a both step next to a DHW leg may move. Such a fixture is claimed in `tests/golden/claimed_drift.txt` with its direction, never re-recorded.

**Harness** (new file `dev/audit/harnesses/mode_legs.py`, classified INERT or into a closure). It reports two numbers:

- `h2d_per_hour`: Heating to DHW switches per hour;
- `legs_under_10`: closed mode legs under 10 minutes, split by cause (plan, re-solve, boost, other).

It has two modes:

- `--history CSV` reads a mode-state series. It is run locally on the owner's bundle, and its output is never pushed.
- `--synthetic --seed S` drives `pump_arbiter.apply` on a one-minute tick over 48 invented hours with a re-solve every 30 minutes.

On the synthetic run, `legs_under_10` from plan and re-solve causes must be 0, and `h2d_per_hour` must not rise. The null control is the same seed with N = M = 0 and the latch off, which reproduces main's counts exactly.

## Hot files, serial position, structure payment

**Hot files:**

- `duty_legs.py`, `duty_switch.py`, `pump_arbiter.py`, `optimizer.py`;
- `tests/features.py`;
- `tests/golden/claimed_drift.txt`, if a fixture moves.

**Overlaps:**

- **R11-OWNER-FLOWCAP.** Its `inputs.write_setpoint` clamp and `pump_arbiter` space consumers do not meet this change: no set-point is touched here. It does share `pump_arbiter.py`'s `module_excess_loc` arithmetic.
- **R11-OWNER-FROST-HOLD.** It adds `ArbiterState` fields and a `frost_holding` read in `_arbitrate` and `_lead_mode`, which make the served duty `"space"`. The frost hold must win over the latch: it is listed in `exempt`, and the test is written once both have landed.
- **R11-SEAM-actuation-writes.** Its "lead mode is checked against the entity" also touches `_lead_mode`.

Serial position: after FLOWCAP and FROST-HOLD. This group rebases onto both.

**Payment** (`module_excess_loc` has no headroom; `pump_arbiter.py` and `optimizer.py` are over `MODULE_LOC_LIMIT`):

- **`pump_arbiter.py`.** `_share`'s step plumbing moves into `duty_switch.served_leg`: the start, the two powers and the next step's `step_duty`, which `step_legs` now reads from the plan itself. That move is expected to net negative with the one `held_leg` call. If it does not, the next move is `_switch_context` into `duty_switch`, judged with `tools/audit/archscore/` before and after.
- **`optimizer.py`.** `_stop_availability` slims to one `duty_legs.availability(...)` call. The `OptimizationConfig` field costs one line.
- **New code** goes in `duty_legs.py` and `duty_switch.py`, which are under the limit. Each new function stays at or under the `functions_cc_over_15` bound.
- **Measurement.** The fixer runs `python3 tests/structure.py` at the merge base and at the head. If no improving payment exists, the route is a budget raise under the mandate, with a `## Raise justification` section.

## Notes for the fixer

- Carry: R11-OWNER-MODE-LEGS (lease) -- merged DHW legs lengthen DHW-only stretches, which `_leased` caps at `LEASE_MINUTES`, or `COLD_LEASE_MINUTES` below `COLD_RAIL_C`. Count lease expiries on the synthetic harness before and after, and report the count in the body.
- The high space set-point at a heating step's start, right after a diverter swap, is not this group's change. Carry: dismissed: no owner ruling names it; the investigation routes it to a design of its own.
- Commanding a faulted pump for hours is a separate investigation recommendation. Carry: dismissed: not in this group's approved scope.
