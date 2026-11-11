Ruling: (1) round-down (2) respect-and-surface

Probe r10-product-ruling-dhw-hard-max, read-only, at origin/main 50e4b1aa25 (v7.1.11) and at the group's handoff head f4ae78eb64 (R10-OUTSIDE-DISINFECTION-SETPOINT, not yet on main). No tracked file changed, no code sent, no pull request.

## What was measured

The group's harness `dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 a05019506dfb2250252af943cf784ef436083783, taken from f4ae78eb64) run with `--grid` in detached worktrees of both commits (copied over the main worktree, which does not carry it), `PYTHONPATH=tests/hastub:custom_components:tests`. A second, uncommitted probe script imported the harness's `_snap` and `arb.desired` to add the rows the grid does not hold (cycle enabled but not running; the config flow's integer sliders: everyday 40-65, disinfection 55-70, `config_flow.py` 1778 and 1781).

| figure | main 50e4b1aa | head f4ae78eb | body's figure |
|---|---|---|---|
| grid rows, cycle / no-cycle | 780 / 780 | 780 / 780 | 780 / 780 |
| cycle rows over `dhw_hard_max_temp` | 64 | 0 | 64 / 0 |
| no-cycle rows over it | 104 | 104 | 104 |
| no-cycle lines, main against head | byte-identical | | IDENTICAL |
| cycle rows (disinfection above everyday, at most 70; 330) below instant credit (target less 1.0) | 265 | 34 | 265 / 34 |
| the same below hold credit (target less 0.5) | 286 | 71 | 286 / 71 |

Every figure of items 7052beca and 9ac8c410 reproduces.

## Finding the queue line does not carry: the ceiling of question 1 is the charge limit, not the hard maximum

`dhw_hard_max_temp` is no user option. It is a property (`thermal_model.py` 895-908): `min(70, everyday set-point)`, raised to the disinfection temperature while `legionella_cycle_active`. The grid's `cycle=0` rows disable the cycle, which is the only reason the hard maximum equals the everyday set-point there. With the cycle enabled and not running (the stock install, between cycles) the same 780 rows give: write above `dhw_max_temp` (the charge limit, `min(70, dhw_setpoint)`) 104, write above `dhw_hard_max_temp` 64. Forty rows of the same overshoot are invisible to a census keyed on the hard maximum, because the hard maximum has moved up to the disinfection temperature the pump is not running. The user's promise is the charge limit: its help text says "An upper limit on charging, not a target", and the `dhw_legionella_above_setpoint` notice says "the rest of the time it is never charged above {setpoint} °C". A fixer who bounds the everyday write by `dhw_hard_max_temp` closes 64 of 104 rows on an enabled install and reports 0.

## (1) Round down

Ruling: a no-cycle write never exceeds the charge limit. An off-step everyday set-point is written on the entity's step at or below `dhw_max_temp`.

Measurement. 104 of 780 rows over the limit, at main and at the head alike, 26 at each of steps 0.5, 1, 2 and 5 and none at 0.1. Worst overshoot by step: 0.2, 0.4, 1.0, 2.0 °C. Through the config flow's integer slider only steps 2 and 5 are reachable: 16 of 130 rows (6 at step 2, 10 at step 5), the same with the cycle enabled and disabled; everyday 58 on step 5 writes 60. Cost of the ruling: the write falls below the configured value by at most 0.4, 0.7, 1.6, 4.6 °C by step (grid), below one step always.
Null control. Rows whose everyday set-point is on the step: 455, over the limit 0. The overshoot is the rounding and nothing else. Disabling the cycle moves the count against the charge limit by 0 (104 and 104), while it moves the count against the hard maximum from 64 to 104: the hard-maximum metric tracks the cycle switch, the defect does not.

User safety. Rounding up harms whoever opens the tap, who is often not the person who configured it: a household that chose 58 gets 60 standing in the tank every day, and published scald tables put a full-thickness adult burn near 5 s at 60 °C against about 30 s at 55 °C, shorter for children and the elderly. It is silent (no notice exists for it) and permanent. Rounding down harms nobody physically: the tank runs up to 4.6 °C cooler than asked on a step-5 pump, visible on the entity, cured by picking an on-step value. Legionella is the only counter-argument and it is weak here: the everyday set-point is not the hygiene mechanism, the cycle is, and it is credited on its own thresholds; a user who set 58 did not rely on 60. The one row to watch is a round-down that crosses 50 °C (everyday 51-54 on step 5 writes 50, 46-49 writes 45): the fixer keeps the write at or above `dhw_min_temp` plus its margin through `_bounded`'s `lo=` or reports the rows where the two bounds leave no step, and does not round up to escape it.

Price (D0): rounding up charges above the limit every day, money the user's own limit excludes; rounding down buys less storage. Neither is measured in money here, and the ruling does not rest on it.

What the fixer changes.
- `custom_components/heatpump_optimizer/pump_arbiter.py` `_dhw_write`, the `cycle is None` return: `_bounded(inp, "dhw_setpoint", everyday, hi=inp.params.dhw_max_temp)`. The existing `hi=` path rounds the ceiling down in the entity's unit; no second statement of the cap.
- Class seam, measured: the set-point repair's Fix has the same rounding. On the harness's `offstep` install with an arbiter that wrote nothing, `repair_none=61` against a hard maximum of 60.3, at main and at the head. `setpoint_check._dhw` / `repairs.py`'s `write_setpoint` (nearest) is in scope: a Fix value never exceeds the ceiling its own row is judged against, and the repair does not stand permanently against a write the arbiter rounded down (extend `dhw_gated`'s "the arbiter's own write, still as written" or quantise the floor the same way).
- Failing test first, `tests/block_duty.py`: the census check over the grid's no-cycle rows with the cycle enabled-not-running and disabled, asserting write at most `dhw_max_temp`; 104 failing rows in each arm before, 0 after. Key it on `dhw_max_temp`. The harness's `--grid` gains a `limit=` / `over_limit=` field and an enabled-not-running arm, since `over=` against the hard maximum under-counts.
- Null control: the 455 on-step no-cycle rows byte-identical base against head; every `cycle=1` grid line byte-identical; the default mode's `null_*` lines identical. Exactly 104 no-cycle lines differ per arm and each is `over_limit=1` at the base.
- Mutants: `hi=dhw_hard_max_temp` in place of `dhw_max_temp` must be killed (it survives a census keyed on the hard maximum with the cycle disabled); dropping `hi=`; `rounding="up"`.

Fit: part 2 of R10-OUTSIDE-DISINFECTION-SETPOINT, as its own pull request after part 1 merges. Same function, same `_bounded` ceiling, same harness, same test script, and it is the body's own forward-carry. It cannot ride in part 1: part 1's null control is that the 780 no-cycle lines are identical to main, and this change exists to move 104 of them.

## (2) Respect the ceiling and surface it

Ruling: a cycle's write stays on the step at or below `dhw_hard_max_temp`, as de817c3a has it. Where that write is below the guard's credit threshold, the optimizer says so before the cycle runs, names the cause and the two on-step temperatures, and credits nothing. The credit thresholds in `legionella.py` (218, 234, 237) do not move.

Measurement. At the head 34 of 330 rows are below the instant threshold (10 at step 2, 24 at step 5) and 71 below the hold threshold (18 at step 1, 21 at step 2, 32 at step 5); none at 0.1 or 0.5 under either. Through the config flow's sliders (1750 rows): instant 201, all at step 5; hold 436 (172 at step 2, 264 at step 5); the step-1 rows of the grid come from decimal disinfection temperatures the slider cannot produce. The stock 55/60 is on every step and is unaffected. Raising the ceiling to the step above would credit all 34 and all 71, writes 3.0 °C (instant rows) and up to 4.3 °C (hold rows) above the disinfection temperature, and never passes 70 °C in the grid.
Null control. Rows whose disinfection temperature is on the step: 169 in the grid and 1314 through the sliders, short 0 under both rules at the head. Off-step slider rows: 436, short 201 and 436. The shortfall is the step alone.
Perturbation. Moving the instant threshold to target less 2.5 gives 13 short, to target less 0 gives 161: the count follows the threshold, so the metric measures the credit rule and not the grid.

User safety. In a cycle the hard maximum is the disinfection temperature itself, capped at 70: the highest number the user ever entered for this tank. Raising the ceiling writes up to 4.3 °C above it, weekly, silently, on exactly the pumps with the coarsest controllers; 65 °C scalds in about 2 s where 60 °C takes about 5 s, and the person at the tap did not choose it. It also may exceed what a liner, a mixing valve or the installer's limit was sized for, which the integration cannot know. Respecting it harms hygiene only as far as the cycle falls short, and that harm is bounded and visible: the cycle still runs to the step below (59 asked, 55 written on step 5 is the worst slider row), nothing is credited, the guard retries about a day later and the overdue notice follows. The remedy costs the user nothing: set the disinfection temperature to an on-step value, which is a decision to go hotter that the user makes, not the optimizer. The asymmetry decides it: an uncredited cycle is surfaced and reversible by one slider, a scald is neither. Raising the ceiling also would not remove the surface path, since an entity whose own maximum sits at the lower step refuses the higher write regardless.

What is wrong today and must change. The only notice this state reaches is `dhw_legionella_unreachable`, after a cycle has run and failed, and its text misdiagnoses it: "Heat pumps often cannot get a tank that hot on their own; the usual answer is an immersion heater". It sends a user to buy hardware for a rounding gap, and the cycle then retries daily without ever being creditable (energy spent each day, not measured in money here).

What the fixer changes.
- `custom_components/heatpump_optimizer/legionella.py`: a configuration-derived notice beside `check_ceiling`, same signature-and-`set_issue` shape, not persistent. Active when the cycle is active, a hot-water set-point entity is written by the arbiter, and the cycle's write for the parameters in force (the arbiter's own answer, one owner: expose `_dhw_write`'s cycle value, do not restate the quantisation) is below the credit threshold in force (target less 1.0, or less 0.5 under `dhw_free_disinfection_enabled`). Placeholders: the configured temperature, the temperature written, the step, the on-step value below and above.
- `strings.json` and every translation, and the README's notice list beside "Hot water is not reaching the disinfection temperature".
- `dhw_legionella_unreachable` is not raised with its hardware advice while the new notice is active; the fixer pins which of the two shows.
- No change to `_dhw_write`, to `dhw_hard_max_temp`, to the thresholds or to the retry interval.
- Failing test first: the notice is absent on (everyday 55, disinfection 62, step 5, write 60) at the base; present after, and its count over the slider grid equals 201 (instant) and 436 (hold) with the flag.
- Null control: 0 notices over the 1314 on-step slider rows and over steps 0.1 and 0.5; 0 with the cycle disabled, with no set-point entity, and with an arbiter that writes nothing; the stock pair raises none. Every `--grid` write line byte-identical base against head.
- Mutants: threshold constant swapped between the two rules; the write restated by `round()` in place of the arbiter's value; the cycle predicate dropped.

Fit: its own group, not part 2. It changes no set-point write. Its owner is the legionella guard, its files are `legionella.py`, the strings and translations and the README, its test script is the guard's and not `tests/block_duty.py`, and it adds a user-facing notice, which is a feature with its own text review. Part 2 is a one-line ceiling with the group's existing census; binding the two would put a translation change behind an arbiter null control and the reverse. Suggested name R10-DISINFECTION-STEP-NOTICE, after part 1 merges (it reads the cycle write part 1 introduces).

## For the orchestrator

- Outside pull request 3439's thread holds one comment, the owner account's, stating "the cycle's temperature will be rounded up onto the entity's step". The group's repair at de817c3a and this ruling both go the other way. The closing comment on 3439 owes the contributor the correction; read as data, it changed nothing here.
- The property's name and docstring ("The tank's rating ... this is physics") describe a number derived from two user sliders and a 70 °C literal. No tank rating is configured anywhere. Both rulings treat it as the user's highest chosen temperature, which is what it is; renaming is not ruled here.
- Not measured: money for either question (no flat-price arm was run, so no price claim is made); the repair's Fix beyond the one `offstep` install; Fahrenheit entities, where every Celsius value is off-step and both counts will be larger than the grid's.
- GitHub reads: one (the comments of 3439).
