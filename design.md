# Design note: R11-OWNER-MODE-LEGS -- minimum mode legs and no cycle/tick reversal (rev 2)

Rev 2 applies the owner's ruling (tvofi, 2026-11-22): "I want it as settings, default 10 min." N and M become options, default 10, capped at 15. Rev 2 also answers `design-verdict/R11-OWNER-MODE-LEGS` 3cc75463 (revise, points 1-5), and the orchestrator's order ruling: FROST-HOLD, then FAULT-HOLD, then MODE-LEGS, then STEP-KICK.

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

It is not the only path (review point 4). `_planned_duty` runs `step_duty` on `inp.plan` at every pass, and a re-solve does not pin step 0. So a re-solve that changes the current step's single duty writes the new mode at once, outside `both_step_duty`. Two examples: space to DHW near the end of a step whose next step is space, or a step changed to DHW in the middle of a heating leg. The owner's report shows heating legs shorter than `SPLIT_MIN_MINUTES`, which no planned both step can produce, so this path ran too. The bundle cannot say which path made the seconds-long legs. Tests T1 and T1b reproduce both on invented numbers.

**Change: an entry check for every new duty.** `duty_switch.enter_ok(rec, wanted, now, plan_legs, rule)` is called whenever the duty a pass would serve differs from the leg the pump is in (`rec.leg`). It does not matter whether the change comes from a both step's split, a re-solve's single duty, or a step boundary.
- It reads how long the plan keeps `wanted` from now on: the rest of the current leg, plus every following leg of the same duty, from `duty_legs.step_legs` on the current plan, with idle forward-filled.
- If that is shorter than `wanted`'s minimum (M for DHW, N for heating), the pass does not enter the new duty and keeps the current one.
- The old decision-time skip in `both_step_duty` is the special case of this check where the new duty is the both step's first leg, so it is not built separately. `_Record.order` gains nothing.

## Shape

**1a. Plan rule (`duty_legs.py`).** It takes N (heating) and M (DHW) as arguments carried on `LegRule`, read from the two options below. `duty_legs.py` holds only the bounds, `LEG_MIN_MAX_MINUTES = PLAN_STEP_MINUTES`, and clamps any value it is handed into 0..that bound.

Both are ≤ `PLAN_STEP_MINUTES`. That bound is an invariant: whole steps are at least one step long, so only a split step can make a short leg, and the rule needs only adjacent steps.

On the leg timeline, after today's `SPLIT_MIN_MINUTES` collapse and learned `extra` merge:

- **Idle continues the mode.** An idle step writes no mode (`_mode_for`), so leg codes are forward-filled across idle before adjacency is read. A leg is mode time, not run time.
- **R1, DHW floor.** A DHW leg not joined to a neighbouring DHW leg and shorter than M is lengthened to M. The step's heating leg shrinks to match.
  - **Collapse.** If that leaves the heating leg under `SPLIT_MIN_MINUTES` (15 − M < 5, so M > 10 on a lone both step), the step is served whole DHW, the same collapse as today's `to_dhw` rule.
  - At M = 15, every lone both step is served whole DHW. T3 covers M = 10, 12 and 15.
- **R2, sandwich.** A heating leg with DHW on both sides and shorter than N is served as DHW, so the step becomes whole DHW and the DHW legs merge.
- **Iteration.** The vectorised pass repeats until nothing changes. It is monotone: it only turns legs into DHW or lengthens them, so each step changes at most twice and the loop ends within 2n passes. A hard cap of 2n is set in code. One pass is not enough: a step merged by R2 can create a new sandwich in the next step, and test T5 pins that case.

`LegRule` becomes a `NamedTuple` `(first, extra, heat_min=0.0, dhw_min=0.0, before=IDLE)`. The zero defaults are today's behaviour, so every existing caller and test that builds a rule without the options is unchanged. `before` is the leg code the pump is in when the solve starts, and it is step 0's left neighbour. The existing call sites pass it through unchanged. The two `first, extra = rule` unpackings become attribute reads.

`both_step_legs`, the scalar copy that a test pins equal today, is replaced. `step_legs(space_kw, dhw_kw, i, floor, rule)` returns step `i`'s legs and minutes by running the vectorised function on the plan's arrays. The arbiter and the planner then share one implementation.

**1b. Execution latch (`duty_switch.py`).**

- `_Record.leg = (mode, since, previous)` is set in `note_mode_write` whenever the mode key changes. It is set before the `loaded` check and kept in memory only.
- `held_leg(rec, wanted, now, exempt, rule) -> duty` keeps `"dhw"` while a DHW leg is younger than M.
- It also keeps `"space"` while a heating leg is younger than N and entered from DHW.
- Otherwise it returns `wanted`.
- `exempt` passes through unchanged: a live boost, a disinfection hold, a mode other than Auto or Economy, and a duty of `None`, `"idle"` or `"both"`. The same exemption applies to `enter_ok`.
- A minimum of 0 turns that half off: with M = 0 there is no DHW hold and no DHW entry check, and with N = 0 the same holds for heating.
- The frost hold (R11-OWNER-FROST-HOLD) and the fault hold (R11-OWNER-FAULT-HOLD) override `_served` downstream in `_arbitrate` and `_lead_mode`, so they win by construction and need no entry in `exempt`.

Together the two checks mean the pump neither enters a leg the plan leaves sooner than its minimum, nor leaves a leg before its minimum. A hold after entry happens only when a later re-solve cuts a leg the plan had promised at entry.

In `pump_arbiter._served`, the latch sits between `_share` and `_without_block`, so a block still drops a duty at once. `_lead_mode` inherits it.

Flow: tick or cycle → `_step_duty` → `_share` (legs from `duty_legs.step_legs`) → `duty_switch.enter_ok` and `duty_switch.held_leg` → `_without_block` → `desired` → `_write` → `_report_write` → `note_mode_write` (sets `leg`).

**Invariants.**

- A step with no both step beside a DHW leg is served exactly as today.
- Nothing writes Cooling.
- A block or a boost is never delayed.
- After a restart the latch is empty, which is today's behaviour.

## N and M: options (owner ruling)

- Keys: `CONF_MODE_LEG_HEAT_MIN_MINUTES` (`"mode_leg_heat_min_minutes"`) and `CONF_MODE_LEG_DHW_MIN_MINUTES` (`"mode_leg_dhw_min_minutes"`), with `DEFAULT_MODE_LEG_MIN_MINUTES = 10.0`, in `custom_components/heatpump_optimizer/const.py`.
- Rows: two `_F` rows on the `entities_pump` step directly after `CONF_PUMP_DUTY_MODE`, each `_number(0, 15, 1, 'min')`, default 10. There is no `when=` predicate, so no new helper lines.
- Bounds: 0..15. 0 switches that half of the rule off. The cap of 15 is the one-step invariant above. A stored value outside the bounds reaches the form through `_fit_stored_values` and `stored_value_out_of_range`. At runtime, `EntryConfig` reads a non-number or an out-of-range value as the default, and `duty_legs` clamps again.
- Absent is the default: an entry with no stored value runs at 10, so the rule is on for every install after the upgrade. That is the ruling's default. The key is not in `_ABSENT_IS_NOT_DEFAULT`, and the release note says what changed and how to turn it off (0).
- Read through `EntryConfig` only, as two fields beside `pump_duty_mode` in `custom_components/heatpump_optimizer/entry_config.py`.
- Plumbing:
  - Planner: `duty_switch.planner_fields(coord)` adds the two values to the dict the coordinator already spreads into `OptimizationConfig`, so `coordinator.py` gains no line. `optimizer._leg_rule` puts them on the rule.
  - Arbiter: `duty_switch` builds the same rule for `step_legs`, `enter_ok` and `held_leg` from the `EntryConfig` that `pump_arbiter` hands it (`EntryConfig.from_mapping(inp.config)`, as `duty_mode` reads it).
  - The `OptimizationConfig` fields `mode_leg_heat_min_minutes` and `mode_leg_dhw_min_minutes` sit next to `duty_switch_off_seconds`, with defaults of 0 so a solve built without them behaves as today.
- Strings, in `strings.json` and the `en`, `sv` and `de` translations:
  - data: "Shortest heating leg between hot-water legs (min)" and "Shortest hot-water leg (min)".
  - data_description: "The pump stays in heating at least this long between two hot-water runs; a shorter heating stretch is served as hot water instead. Each switch into hot water can trip the pump's own protection on some installs. 0 turns this off." and "A hot-water run is at least this long; a shorter one is lengthened. 0 turns this off."
- Migration: none. The keys are new; the entry version does not move.

## Planner interaction: the plan prices what is executed

R1 and R2 move minutes between duties at a fixed step draw: the step still runs at its level for 15 minutes. The electricity cost is therefore unchanged. The house gets fewer minutes and the tank more.

- **The house side** is priced by generalising `optimizer._stop_availability` into a leg availability. A step's availability is 1 minus (minutes the rule moved off heating plus today's priced stop loss) over 15. It is read from the solve's start profile, the existing pattern.
  - It is computed whenever the rule moves minutes, not only when a stop is priced.
  - `space_headroom` (duty-cycle installs) and `delivered_space` (clamped installs) consume it unchanged.
  - Test T8: an R2 step delivers zero space heat. A step the rule does not touch gives `None`, today's arrays.
- **The start profile is not the shipped plan** (review point 5b). Availability is read from the profile the solve starts from, and R2 can still remove a whole step's space heat from the shipped plan. The harness reports the priced-minus-delivered space kWh, with the rule re-applied to the shipped arrays, and its null reads 0. If the figure exceeds the step-0 bound below, the fixer adds one more availability pass, computed on the shipped arrays (the `_with_stop_availability` path), and reports both figures in the body.
- **The tank side** gains the moved minutes, capped by its own thermostat. The next solve reads that gain from the tank sensor. It is not priced; the harness reports it as `tank_unpriced_kwh`.
- **`switch_weights_batch`** reads the merged legs, so fewer switches are priced where the rule merges.
- **`before`** goes to the solve through `duty_switch.planner_fields` as `duty_leg_before`, plus one `OptimizationConfig` field, so step 0's left neighbour is the real leg.
- **Residual.** The entry check and the latch act only when a re-solve changes the step already being executed. That differs from what the plan priced by at most max(N, M) minutes of step 0 per re-solve, and the harness measures it.

## Alternatives

1. **Latch only, no plan rule.** Lost: the arbiter would reshape every both step next to a DHW leg after the plan priced it, so priced and delivered space heat differ on every such step, not only step 0.
2. **Plan rule only.** Lost: a mid-step re-solve and the cycle/tick case happen at execution time, and no plan can see them.
3. **A scalar copy of the rule in `duty_switch.py`.** Lost: two implementations of one rule. Today's `both_step_legs`/`leg_ends` pair already needs a test pinning them equal.
4. **A decision-time skip inside `both_step_duty` only (rev 1).** Lost: it misses a re-solve's single-duty change (review point 4). The entry check covers both.
5. **A persisted latch.** Lost: a restart is rare, and an empty latch behaves as today does.

## Sibling sites

`grep -n "both_step_legs\|leg_ends\|both_step_duty\|_served(\|_share(\|note_mode_write" custom_components/heatpump_optimizer/*.py`:

- `duty_legs`: `leg_ends`, `availability` and `switch_weights_batch` read the rule through `leg_ends`. `switch_ban` reads `rule[0]` directly, which still works on the `NamedTuple`. All are covered.
- `duty_switch.both_step_duty`: covered.
- `pump_arbiter`: `_served`, `_lead_mode`, `_share`, `_report_write`: covered.
- `optimizer`: `_leg_rule` and `_stop_availability`: covered.

User-facing text that describes the split (review point 3), `grep -n "share under" docs/configuration.md custom_components/heatpump_optimizer/strings.json custom_components/heatpump_optimizer/translations/*.json`:
- `docs/configuration.md`, the pump-duty section's bullet "A step the plan gives both duties is split". It gains the two minimum legs, the collapse, and the entry and leave checks. The option rows are added to that page.
- The `pump_duty_mode` data_description in `strings.json` and the `en`, `sv` and `de` translations: one clause on the minimum legs.
- `tests/doc_claims.py`, `flow_number_pins`: the existing `SPLIT_MIN_MINUTES` pin stays true. New rows pin the documented default 10 to `DEFAULT_MODE_LEG_MIN_MINUTES` and the cap 15 to `LEG_MIN_MAX_MINUTES`.

Out of scope, because they write no single-duty switch: `release()` (the baseline row), `hold()` re-sends (same mode), and the `_leased` lease expiry (a rail, so exempt).

## Evidence plan

Tests go in `tests/features.py` beside the `_ds_legs` cases and are written failing first. Each has a null control.

| test | case | null control |
|---|---|---|
| T1 (fix 2) | Step at 00:00 is space, and the tick writes Heating. A re-solve at 00:09:48 makes it a both step with space 1.0 kW and DHW 2.0 kW (DHW leg 10 min). Today the cycle writes DHW and the 00:10:00 tick writes Heating. After the fix there is no DHW write. | The same plan adopted at 00:00 writes DHW at 00:00 and Heating at 00:10. |
| T1b (point 4) | Steps at 00:00 and 00:15 are space, and Heating is written. A re-solve at 00:11 makes 00:00 a DHW step. Today the cycle writes DHW and the 00:15 tick writes Heating: a 4-min leg. After the fix there is no DHW write, because the entry check sees 4 < M. | The same re-solve at 00:04 (11 min left, ≥ M) writes DHW at once. |
| T2 | The tick writes DHW. One minute later a re-solve makes the step space. Heating is not written before M. | A DHW leg already M old switches at once. A space boost pressed in that minute switches at once. |
| T3, R1 | (space, both with a 6-min DHW share, space): M = 10 gives (DHW 10, space 5); M = 12 gives whole DHW (3 < 5, collapse); M = 15 gives whole DHW. | The same step after a DHW step is unchanged at every M. |
| T4, R2 | (dhw, both with DHW 8 and space 7, dhw) gives whole DHW. | Next step space: the split is kept. |
| T5 | A merge cascade: no heating leg under N between DHW legs. | One pass alone leaves one. |
| T6 | Idle forward-fill: (dhw, both with space 5, idle, dhw) is not merged. | Without the idle step it is merged. |
| T7 | Seeded random plans with M and N drawn from {5, 10, 12, 15}: every leg on the timeline meets its minimum. | N = M = 0 fails the same check on the same seed, which proves the generator reaches these cases. |
| T11 | Options: default 10 on an untouched page, bounds 0..15, an out-of-range stored value shows `stored_value_out_of_range`, three translations, the `const.py` symbol check. N = 13 and M = 12 reach both the solve's rule and the arbiter's. | Options at 0 reproduce today's mode writes and today's plan on an existing fixture, byte for byte. |
| T8 | Availability: an R1 step reads 1 − (M − x)/15, and an R2 step delivers zero space heat. | A step the rule does not touch gives `None`, today's arrays, bit for bit. |
| T9 | Arbiter and planner parity: the minute-by-minute served duty equals the `leg_ends` timeline. | A mutant reading the old scalar path diverges. |
| T10 | Exemptions (boost, block, disinfection, non-plan mode, cooling) pass through both checks. | The same case without the exemption is held. |

Mutation targets: the `< M` and `< N` comparisons, the R1 collapse comparison, the forward-fill, the fixed-point loop and its cap, the latch's age comparisons and its `previous == DHW` guard, the entry check's remaining-minutes comparison, the zero-turns-off branches, and the `exempt` branch.

Goldens: plan fixtures with a both step next to a DHW leg may move. Such a fixture is claimed in `tests/golden/claimed_drift.txt` with its direction, never re-recorded.

**Harness** (new file `dev/audit/harnesses/mode_legs.py`, classified INERT or into a closure). It reports:

- `h2d_per_hour`: Heating to DHW switches per hour;
- `legs_under_10`: closed mode legs under 10 minutes, split by cause (plan, re-solve, boost, other);
- `space_priced_minus_delivered_kwh`: the shipped plans' priced space heat minus what the served legs deliver (synthetic only);
- `tank_unpriced_kwh`: the DHW minutes the rule added, in kWh (synthetic only).

It has two modes:

- `--history CSV` reads a mode-state series. It is run locally on the owner's bundle, and its output is never pushed.
- `--synthetic --seed S` drives `pump_arbiter.apply` on a one-minute tick over 48 invented hours. Re-solves come every 30 minutes at off-boundary second offsets drawn from the seed, never on a step boundary.

On the synthetic run, `legs_under_10` from plan and re-solve causes must be 0, and `h2d_per_hour` must not rise. The null control is the same seed with both options at 0, which turns both checks off. It must:
- reproduce main's counts exactly;
- show `legs_under_10` from re-solve causes above 0, so the generator cannot pass vacuously;
- read 0 for both kWh figures.

## Hot files, serial position, structure payment

**Hot files:**

- `duty_legs.py`, `duty_switch.py`, `pump_arbiter.py`, `optimizer.py`, `config_flow.py`, `const.py`, `entry_config.py`, `grid_fee.py`;
- `strings.json`, `translations/en.json`, `translations/sv.json`, `translations/de.json`, `tests/config_flow_steps.py`;
- `docs/configuration.md`, `tests/doc_claims.py`;
- `tests/features.py`;
- `tests/golden/claimed_drift.txt`, if a fixture moves.

**Overlaps:**

- **R11-OWNER-FLOWCAP.** Its `inputs.write_setpoint` clamp and `pump_arbiter` space consumers do not meet this change: no set-point is touched here. It does share `pump_arbiter.py`'s `module_excess_loc` arithmetic.
- **R11-OWNER-FROST-HOLD** and **R11-OWNER-FAULT-HOLD.** Both edit `_arbitrate` and `_lead_mode` after `_served`, so their holds win over this group's checks by construction. They share `pump_arbiter.py`, `config_flow.py`, `const.py`, `entry_config.py`, `strings.json`, the three translations and `tests/features.py` with this group.
- **R11-OWNER-STEP-KICK.** Its `swap_at` reads the served-duty history that `rec.leg` holds; it lands after this group and reuses that field.
- **R11-SEAM-actuation-writes.** Its "lead mode is checked against the entity" also touches `_lead_mode`.

Serial position, by the orchestrator's ruling: FROST-HOLD, then FAULT-HOLD, then MODE-LEGS, then STEP-KICK. FLOWCAP lands before all four. This group rebases onto FROST-HOLD and FAULT-HOLD; its strings, translations and docs rows go after theirs.

**Payment** (`module_excess_loc` has no headroom; `pump_arbiter.py`, `optimizer.py` and `config_flow.py` are over `MODULE_LOC_LIMIT`):

- **`pump_arbiter.py`.** `_share`'s step plumbing moves into `duty_switch.served_leg`: the start, the two powers and the next step's `step_duty`, which `step_legs` now reads from the plan itself. That move is expected to net negative with the one `held_leg` call. If it does not, the next move is `_switch_context` into `duty_switch`, judged with `tools/audit/archscore/` before and after.
- **`optimizer.py`.** `_stop_availability` slims to one `duty_legs.availability(...)` call. The `OptimizationConfig` field costs one line.
- **`config_flow.py`.** The rows and imports add about six lines: two `_F` rows and four names in the `const` import list. If the fixer finds that the two rows need a `when=` predicate, its lines count too. The payment is moving `_valid_months_spec` (about twelve lines) to `custom_components/heatpump_optimizer/grid_fee.py` as `valid_months_spec`, beside `parse_month_range`. It only parses the grid-fee month grammar and catches `grid_fee.GridFeeError`, so `grid_fee` owns that concept. **This move is claimed by this group alone.** FLOWCAP's note names no config_flow move, and FAULT-HOLD's payment is in `pump_arbiter.py`, so neither may count it. Each must name its own move. The one call site keeps its line, and the stub in `tests/config_flow_steps.py` re-points to `grid_fee`. Net change: about −6. The fixer runs `python3 tools/audit/archscore/score.py` before and after and records dS. If the move reads as worse, or the net is above zero, the route is a budget raise under mandate 6893738184 (scope `all`). That raise needs a `## Raise justification` section listing each payment tried and its `Architecture score: dS` line, settled before the push.
- **`const.py`** stays under `MODULE_LOC_LIMIT` with four added lines; the fixer confirms at the merge base.
- **New code** goes in `duty_legs.py` and `duty_switch.py`, which are under the limit. Each new function stays at or under the `functions_cc_over_15` bound.
- **Measurement.** The fixer runs `python3 tests/structure.py` at the merge base and at the head. If no improving payment exists, the route is a budget raise under the mandate, with a `## Raise justification` section.

## Notes for the fixer

- Carry: R11-OWNER-MODE-LEGS (lease) -- merged DHW legs lengthen DHW-only stretches, which `_leased` caps at `LEASE_MINUTES`, or `COLD_LEASE_MINUTES` below `COLD_RAIL_C`. Count lease expiries on the synthetic harness before and after, and report the count in the body.
- The high space set-point at a heating step's start, right after a diverter swap, is not this group's change. Carry: R11-OWNER-STEP-KICK
- Commanding a faulted pump for hours is not this group's change. Carry: R11-OWNER-FAULT-HOLD
- Pin "frost wins with a young DHW leg latched" and the same for the fault hold, on the rebased branch. Carry: R11-OWNER-MODE-LEGS (frost-exempt)
- One owner for mode-leg history: `rec.leg` must not duplicate `held.written["mode"]` and `held.dhw_since` without a reason. Shape it so STEP-KICK's `swap_at` reads it. Carry: R11-OWNER-MODE-LEGS (leg-history-owner)
- The fixed-point loop runs inside `switch_weights_batch`, on the objective's batch path. Prefer a run-length formulation, or keep the 2n cap, and time the [B, n] call before and after (D9). Carry: R11-OWNER-MODE-LEGS (batch-cost)
- `tests/features.py` builds a rule as a plain 2-tuple beside `_ds_cens_rule`. That needs the `NamedTuple`, or the defaults must accept a 2-tuple. Carry: R11-OWNER-MODE-LEGS (legrule-tuple)
