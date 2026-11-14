R10-USER-DOCS-VERIFY, carry 17, second pass: the user docs re-read against round 10's last product heads, on a stacked base (the owner's ruling of 2026-11-14), and corrected where a sentence is stale. Every verdict below rests on executable code at the named head, never a comment, a docstring or a pull request body (owner rule of 2026-11-13). The first pass (the merges up to e23124ff6e) follows under "First pass", unchanged.

Pages re-read: README.md, docs/setup.md, docs/configuration.md, docs/how-it-works.md, docs/automations.md, docs/dashboard-card.md, docs/ecl110.md, re-measured at this branch's merge base with origin/main, 0f37833e21 (`git merge-base origin/main HEAD`).

Outside this pass: r10-sav-valuation-residue-p3 (the combi hot-water tile, which may edit docs/dashboard-card.md itself) and r10-sav-valuation-residue-p4 (the thermostat reference behind a throttling valve). A short second pass covers them.

Two instruments ran over every head, besides reading each diff (`git diff $(git merge-base origin/main <head>)...<head> -- custom_components/ docs/ README.md`):
- card phrases: every `*...*`, `"..."` and `“...”` phrase of docs/dashboard-card.md and README.md that occurs in the card's JavaScript at origin/main, re-looked-up in each card-touching head (3481, 3556, 3563, 3574, 3576, 3580): none is gone at any head.
- config-flow phrases: every bold, italic or quoted phrase and table first cell of the seven pages that occurs in strings.json at origin/main, re-looked-up in each strings-touching head (3481, 3532, 3561, 3562, 3564, 3567, 3576, 3580, 3581): gone only "The learned offset is capped at 15 °C" (3564) and "Buffer Tank Temperature (Model)" (3567). Both rows below.

| PR (head read) | what it changes for a user | pages, sentence changed: old → new, and the code that decides |
|---|---|---|
| 3532 fd5fe52fa7 (stacked) | the arbiter splits a both step by the duty-switch learner's latches: space first where only hot water to heating stops the compressor, and a short second share merged onto the first duty | docs/configuration.md Pump duty control, both-step bullet: "hot water first, for the step's hot-water power ... then heating for the rest" → hot water first unless the switch from hot water to heating has been learned to stop the compressor and the other has not, then heating first; a second share under 5 minutes plus the median off time stays with the first duty when the next step serves the second. Decided by `duty_legs.leg_rule` (`first = "space" if stop_probability[0] > 0 and not stop_probability[1] > 0`), `duty_legs.both_step_legs` (the `extra` merge on `next_duty in (second, "both")`), served by `pump_arbiter._share` through `duty_switch.both_step_duty`. The duty table's Both row likewise. Its own restore-paragraph hunk is left to it. |
| 3562 ced9b23358 (stacked) | a space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) | docs/configuration.md "Space-heating set-point entity" row: "Written only with Pump duty control at Control, and then with the plan's own number (see below)" → adds "or during a space boost or Boost mode on a flow or return set-point the entity's own maximum". Decided by `pump_arbiter._boost_ceiling_c`. Its own flow-ceiling row and boost bullet hunks are left to it. |
| 3556 fe11888ad6 (stacked) | a learner held by a boost, an open window or an unusable input shows *paused*, with the boost's end; the boost's settle tail scales with the boosted time | docs/dashboard-card.md, What the model has learned: Solar gain "with "Learning: 6 of about 30 samples"" (shown only when no phase is published, which `learner_progress_view` always publishes) → "with where its learning stands"; added the phase sentence (waiting, counting with days, settling, paused: after a space boost until a named time, 12 hours after a full two-hour boost, less after a shorter one; while Boost mode is selected; on an open window or unusable input until usable). Decided by `learner_progress.pauses`, `learner_progress.learner_progress`, `boost.learning_freeze`, `boost.settle_tail`, `BoostState.freeze_end` and the card's `learnerPhase`. |
| 3561 ebc8483673 | the restored baseline after an upgrade is the hold value, and the set-point is written from the first pass | its own docs/configuration.md hunk covers it (also carried by 3532); nothing else stale: the config-flow phrase lookup reads none gone. |
| 3574 97478d9785 | the savings baseline behind a valve is booked as simulated; `REFERENCE_BASIS` 1 → 2, so every month booked before the update states no saving | docs/dashboard-card.md savings table: added that a month booked wholly or in part against an earlier baseline keeps its two columns, states no saving and is badged *old basis*. True at main too (`old_basis = self.meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS` in `MonthlyLedger.savings_months`; badge `savings.old_basis`), so no stack. docs/automations.md's `saving_old_basis` stays true. |
| 3564 d6a7b00bba | strings only: config-flow descriptions corrected to the code | Corrected where a page repeats the old fact and the code agrees with the new string: docs/configuration.md flow-lift row "**The learned offset is capped at 15 °C**" → lowers the supply at most 15 K below the curve, raises it at most to a 75 °C supply, a reading above 75 °C not learned (`FlowCurveBias.observe`: `np.clip(blended, -FLOW_BIAS_CLAMP_K, max(FLOW_SUPPLY_MAX_C - curve_supply, 0.0))`, `measured_supply > FLOW_SUPPLY_MAX_C` returns); wood tank rows in docs/configuration.md (both sections) and docs/setup.md "Both are needed ... one alone is read conservatively" → the top alone reads 5 °C colder, the bottom alone gives no estimate (`external_heat.wood_mean_temperature`); Fixed transfer fee row "on top of any rules" → ignored while the fee mode is None (`GridFeeSchedule.from_config`, `if mode != MODE_NONE`); docs/how-it-works.md "the planned start count is published" → not published on any entity (no entity platform reads the plan's `compressor_starts`; configuration.md already said so). Read against code too, each a page repeating a fact the strings corrected: docs/setup.md quick setup "then the heat pump's entities are read automatically" → a page to pick the device and check its settings, empty to skip (`ConfigFlow.async_step_quick_setup` returns `async_step_device_prefill`, whose empty pick returns `async_step_finish_setup`); "Target indoor temperature" rows "The optimizer aims here" → the thermostat's temperature, the plan aiming at the comfort temperatures (`comfort_targets` from `get_comfort_temp`, the pull `room_t - comfort_targets`); setup.md "The gap between the target and the minimum" → the comfort temperatures (`comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)`); solar radiation sensor row "Lets the plan skip heating before a sunny afternoon" → the current reading the learners read, the forecast supplying the horizon (`reader.read(CONF_SOLAR_RADIATION_ENTITY)` sets `state.solar_radiation` only); "Upper floor heating" row "This sets how far ahead heat can usefully be shifted" → used only on a two-zone derivation (`presets.py` reads `upper_emitter` only under `preset.two_zone`; `heating_response_hours` is popped by `config_flow` and `quick_setup.derive`); house thermal mass row → the heavy floor is in the house mass on a one-zone radiator house (`if not preset.two_zone and preset.lower_emitter != EMITTER_FLOOR: house_mass += slow_mass`); pre-fill device row "A device the integration has no table for is refused" → name matching fills what no table maps (`device_prefill.resolve_with_fallback`); energy meter row "more accurate than adding up power readings" → its two readers (`observe_counters`' `elec_kwh`, the Measured Power sensor's `energy_meter`); Swedish DSO tariff row → also sets the fee mode to rules and switches the peak tariff on (`grid_fee.apply_catalog`); "Highest tank temperature to charge to" rows: a disinfection cycle goes above it (`dhw_hard_max_temp` from `dhw_cycle_temp = max(setpoint, disinfection)`). The "After saving" row is true (`config_flow` pops `CONF_AFTER_SAVE` and saves on either choice). |
| 3481 9a543f44d6 | the what-if money line is a steady-state estimate; price-tile solves per tile | its own hunks in docs/configuration.md, docs/dashboard-card.md and docs/how-it-works.md; the other what-if sentences (configuration.md `simulate_plan`, dashboard-card.md "Each answer is a real optimization solve", "Simulate these slots prices the draft against the plan currently in force") stay true: `handle_simulate_plan` still calls `coord.async_simulate(overrides, steady=True)`, a solve. Nothing stale. |
| 3569 57ee4591d0 | `Direction.decay` holds `n` at `N_CAP` | no page states the cap; nothing stale. |
| 3581 2c121b9e14 | a repair notice when the disinfection temperature falls between the hot-water set-point's steps | its own README row. It showed docs/configuration.md's disinfection bullet stale at main already: "on the entity's step rounded up" → "at or below that temperature, never above 70 °C or the entity's maximum: on a 5 °C step a 62 °C cycle writes 60 °C" (`thermal_model.dhw_step_target_c`: `grid.bounded(value, hi=params.dhw_hard_max_temp)`, `dhw_hard_max_temp = min(70.0, cycle temperature)`; driven: 60.0, where rounding up gives 65.0). True without 3581's code, so no stack. |
| 3563 16bed63da7 | card text and the Health pictures | card-phrase lookup: none gone; the Health alt text is 3580's hunk. Nothing stale. |
| 3567 ffd4304c00 | strings and README text | its own README hunks (the Buffer Tank Temperature rename). Left to it. |
| 3576 8317d9e1b2 | away hot water, free disinfection, circulation pump text | its own docs hunks. Left to it. |
| 3580 ec9645014c | config, card and setup text | its own docs hunks (entry name, away legionella, circulation pump, solar production, open window, main fuse, savings note, Health alt). Left to it. |
| #3531 7aac3e7c04 (merged on main after the first pass's base) | the pump's start hysteresis options and notice | its own docs/configuration.md and README hunks; nothing else stale. |

The stacked heads bring their own code and one RELEASE_NOTES.md body paragraph (3561's upgrade note, via 3532); no heading, VERSION or manifest line moves (`git diff origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json` is empty).

`tests/doc_claims.py` `check_late_delta_claims` pins the five corrections whose fact is a single symbol's answer, by driving it: `dhw_step_target_c` on a 5 °C `SetpointGrid`, `wood_mean_temperature` with one probe, `FLOW_BIAS_CLAMP_K` and `FLOW_SUPPLY_MAX_C`, `duty_legs.leg_rule` with only hot water to heating stopping, and `GridFeeSchedule.from_config` with no fee mode; each sentence must state the driven value, and each check is run against its pre-fix sentence as null control.

## First pass

R10-USER-DOCS-VERIFY, the late user-docs delta (carry 17). Pull request 3513 merged at 83e4e83d77 from base f44e761c19 (`git merge-base 83e4e83d77^1 83e4e83d77^2`); its own step commits are all on main (`git merge-base --is-ancestor 3246aa389f origin/main`), so what main lacks is only what the product merges after that base changed. Enumerated by `for c in $(git rev-list --first-parent f44e761c19..origin/main); do git diff --name-only $c^1 $c -- custom_components blueprints docs README.md; done`: #3524, #3530, #3534, #3441, #3505, #3536, #3512, #3526, #3511 (#3461 is before the base).

Disposition per merge, each read against code, never a comment:

- #3512 (R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE): the supply switch's 10-minute minimum run and pause (`supply_hold.MIN_RUN`, `MIN_PAUSE`, `hold_supply`, retried by `pump_arbiter.supply_tick`; `_passes` exempts modes other than auto and economy, boosts and system identification; `_ends_soon`/`tank_reason` the cold-tank and disinfection exception) was in no user page. Documented on the on/off switch row of docs/configuration.md.
- #3526 (R10-DUTY-SWITCH-PLANNER-PRICE): the solve now prices a learned duty switch (`optimizer._priced_stops`, `_switch_cost_fn`, `_stop_availability`, the placement candidate; `duty_switch.Direction._latch` with `N_ON`, `P_ON`, `SPAN_DAYS_ON`, `HALF_LIFE_DAYS`, `STOP_WINDOW_S`). The README's Compressor Starts row and how-it-works.md's cycling-cost section said nothing of it. Documented in docs/configuration.md (Pump duty control), docs/how-it-works.md and the README sensor row, with the `duty_switch_*` attributes `duty_switch.starts_attributes` publishes.
- #3524 (R10-DUTY-SWITCH-RESTART-LEARNING part B): `k` left the published attributes and `n` became whole episodes; no user page named either before this diff, so nothing went stale; the new row names `p` and `n`.
- #3530 (R10-MODE-BEFORE-SUPPLY-ON): `pump_arbiter.write_supply`/`_lead_mode` writes the step's mode before a switch-on under Control. Documented as a Pump duty control bullet.
- #3534, #3441, #3536: each edited its own user pages in the same merge (docs/ecl110.md; docs/dashboard-card.md and README.md; docs/configuration.md and README.md); re-read, no stale claim found.
- #3505, #3511: no user-visible change (`BOOST_SPACE_SETTLE_TAIL_HOURS` keeps the former 12 h; optimizer internals).

dev/audit/rounds/round4/D6/claims.json and claims.md are that harness's own output re-run at the head (`tests/harness_headers.py` refuses committed output that its run changes): C108 counts one more relative link, the new how-it-works.md link to `configuration.md#pump-duty-control`, with broken=[].

The brief's other carries, each already on main by pull request 3513 (its step commits are ancestors of origin/main by `git merge-base --is-ancestor 3246aa389f origin/main`), re-run here only where this diff reaches them:

- Carry 0: dismissed in the brief, superseded by Carry 1.
- Carry 1, Carry 2, Carry 3: marked implemented in the brief; at this head `python3 tests/doc_claims.py` passes both arms (Figures).
- Carry 4 (away mode and the mold floor), Carry 6 (the operating-mode row), Carry 7 (coffee.svg), Carry 9 (the Health section), Carry 14 and Carry 16 (the stratified combi probe): marked implemented in the brief; this diff touches none of those sentences.
- Carry 5, Carry 11, Carry 12, Carry 13, Carry 15: `python3 tests/doc_claims.py --markers --user` reads `0 user-doc marker(s), 0 due` at this head (Figures).
- Carry 8: dismissed in the brief (the owner's check on v7.1.12). Carry 10: dismissed in the brief, a duplicate of Carry 11.

Pages re-read: README.md, docs/setup.md, docs/configuration.md, docs/how-it-works.md, docs/automations.md, docs/dashboard-card.md, docs/ecl110.md.

Round 2, answering the fix review at probe/revt-r10-user-docs-verify-fd9c4779 (`Fix review: blocked 6295f868a4 doc-claim-false`). Its Findings section reads `none`; its Block has three items, each answered here.

- Block 1 (lost heat charged in one direction only): `duty_legs.lost_share` returns `min(1.0, stop_probability[0] * off_seconds[0] / ...)` (custom_components/heatpump_optimizer/duty_legs.py:161), index 0 being `dhw_space` in `duty_switch.DIRECTIONS` (duty_switch.py:62), the order `planner_pairs` reads (duty_switch.py:393-394). Both sentences now name the direction: docs/configuration.md "For a switch from hot water to heating it also expects the median measured off time as heat not delivered in the heating that follows; a switch the other way is priced but costs no heat", and docs/how-it-works.md "for a switch from hot water to heating it also counts the off time as heat not delivered".
- Block 2 (the cold-tank exemption needs a step that heats the tank): `supply_hold._ends_soon` returns `not (step_duty(inp.plan, now) in ("dhw", "both") and tank_reason(inp))` (supply_hold.py:156). The on/off switch row now reads "is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold)".
- Block 3 (the body's null control printed nothing for docs/how-it-works.md): the pattern `min\(a, b\) / p_max` is added; the control below prints a line for each of the three pages at the head, nothing at origin/main, and 0 for how-it-works.md with its added paragraph cut out.
- Both corrected sentences are now pinned by `tests/doc_claims.py` `check_duty_switch_claims`, which reads the facts from the code (the direction `duty_legs.lost_share` charges, driven per direction; `supply_hold._ends_soon` driven on a space step and a hot-water step with a cold tank and a run ending in 5 minutes, its collaborators `step_supply`, `step_duty`, `tank_reason` stubbed and restored) and refuses prose that disagrees; its in-check null controls are the two pre-fix sentences verbatim.

Every other sentence this branch adds or changes, re-checked against the code that decides it (owner ruling 2026-11-13: executable lines, never a comment or docstring):

- README Compressor Starts row, `duty_switch_*` attributes: `DutySwitchLearner.published` (duty_switch.py:367-386) emits `duty_switch_{dhw_space,space_dhw}_{p,n,stopped,kept,void,censored,median_off_s,span_days}`, read by `starts_attributes` (duty_switch.py:522-525).
- On/off row, "never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off": `MIN_RUN`, `MIN_PAUSE = timedelta(minutes=10)` (supply_hold.py:60-61); the second switch writer early_cutoff refuses a cut under `MIN_ON, MIN_OFF = MIN_RUN, MIN_PAUSE` (early_cutoff.py:92) in `_cycle_guard`.
- On/off row, "In auto and economy mode" and "A boost, the other modes and the measurement experiment are not held": `supply_hold._passes` (supply_hold.py:144-148), `inp.mode not in (MODE_AUTO, MODE_ECONOMY)`, `mode == "system_identification"`, `boosts.active(CHANNEL_SPACE|CHANNEL_DHW, now)`.
- On/off row, "a held switch is retried every minute": `_TICK = timedelta(minutes=1)` (pump_arbiter.py:258) driving `supply_tick` (pump_arbiter.py:1931).
- On/off row, "The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart": `switch_age` reads `last_changed` (supply_hold.py:130-141); the restart stamp is pinned by tests/ha_contract.py `_restart_stamps_last_changed`.
- On/off row, "the tank needs heat now (below its minimum, or a disinfection hold)": `tank_reason` (supply_hold.py:106-115), `inp.disinfecting` or `dhw_temperature < dhw_min_temp` with hot water enabled.
- Pump duty control, which switches count: an episode opens only on `direction is not None and running and _heated(direction, ctx) and ctx.target_demand and ctx.plan_stays and ctx.void_cause() is None` (duty_switch.py:299-300), `running` the settled compressor (duty_switch.py:487), `target_demand` the new duty's reading below its target (pump_arbiter.py:1549); a person's change voids it (`explained = ... ctx.mode_written_at != ep.at`, duty_switch.py:341-344). Round 1's "watches each switch it writes while the compressor runs" stated a subset as the whole; it now names those conditions as some among several.
- "a stop within 3 minutes": `STOP_WINDOW_S = 180.0` (duty_switch.py:66), closed kept past it (duty_switch.py:325-327, 345-346).
- "at least half of a weighted 5 or more switches, seen on at least two calendar days": `Direction._latch` `self.n >= N_ON and self.p >= P_ON and self.span_days >= SPAN_DAYS_ON` (duty_switch.py:204-210), `N_ON = 5.0`, `P_ON = 0.5`, `SPAN_DAYS_ON = 2` (duty_switch.py:75, 81, 82), `span_days = (last_day - first_day).days + 1` (duty_switch.py:177).
- "a switch weighs half after 14 days": `factor = 0.5 ** (age_s / (HALF_LIFE_DAYS * 86400.0))` (duty_switch.py:189), `HALF_LIFE_DAYS = 14.0` (duty_switch.py:74).
- "charges that switch a share of the Cost of one compressor start": `_switch_cost_fn` `cost * duty_legs.switch_weights_batch(...)` (optimizer.py:290-295), zero probability unless latched (`planner_pairs`, duty_switch.py:393).
- "tries to place hot water where no such switch follows it (not on a combi store)": `_avoid_priced_switches` returns the incumbent on `stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi`. "(not on a combi store)" is new in this round.
- "the median measured off time": `median_off_s` (duty_switch.py:180-182) via `planner_pairs`.
- "With the start cost at 0 only that lost heat is planned for": `_stop_availability` (optimizer.py:207-226) has no cost condition; `_switch_cost_fn` and `_avoid_priced_switches` return nothing unless `cycling_cost > 0`.
- "The mode goes first when the pump is switched on": `write_supply` awaits `_lead_mode` before `switch_supply` (pump_arbiter.py:1840-1848); `_lead_mode` returns unless `on` and `duty_mode(...) == DUTY_CONTROL` (pump_arbiter.py:1784) and `_pump_off` (switch state `"off"`, pump_arbiter.py:1991).
- how-it-works, "invisible to the cycling term, which prices swings in the total draw": `swing = row_sums(np.abs(np.diff(power_matrix, axis=1)))` on `space + dhw` (optimizer.py:1898-1899, 5075-5078).
- how-it-works, "`min(a, b) / p_max` cycles ... times that probability": `across = stops * np.minimum(level[_BEFORE], level[_AFTER])`, divided by `p_max` (duty_legs.py:126-133); inside a two-leg step both legs run at the step's level, so `min(a, b)` is that level.

Not re-derived by the round-1 review, re-stated rather than re-measured this round: #3534, #3441, #3536 "re-read, no stale claim found" and the carries marked implemented that this diff does not touch.

## Head

254f0ed03e62af64f05eb5bbe56e4857207ac15d, on origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439 (main's tip at 2026-11-14 10:22 UTC; `git merge-tree --write-tree origin/main HEAD` reports no conflict). Stacked heads, one merge commit each: 3532 fd5fe52fa788805433e1f1fe36b1824e0943838e, 3562 ced9b233580709f530d5dc402dc12344697fef87, 3556 fe11888ad6b48248728b74bc7a882e4039f4f90e. This pull request merges only after those three.

## Mutation proof

No production line changed. Second pass: `tests/doc_claims.py` run with each deciding symbol mutated in place, then restored (FAIL lines only):

- `external_heat.wood_mean_temperature` returning `top - 3.0`: rc=1, `FAIL docs/configuration.md wood: the sentence states what the code decides`, `FAIL docs/setup.md wood tank bottom sensor: one-probe readings as the code decides`.
- `dhw_step_target_c` calling `grid.bounded(float(value), rounding='up')`: rc=1, `FAIL docs/configuration.md cycle: the sentence states what the code decides` (driven write 65.0).
- `FLOW_BIAS_CLAMP_K = 10.0`: rc=1, `FAIL docs/configuration.md bias: ...`.
- `duty_legs.leg_rule` with `first = "dhw"`: rc=1, `FAIL docs/configuration.md split: ...`.
- `GridFeeSchedule.from_config` reading the fixed fee with mode None (`if True:`): rc=1, `FAIL docs/configuration.md fee: ...`.
- all restored: rc=0, ALL 368 checks PASSED; `git status --short custom_components` empty.

First pass, at b4617aa636:


No production line changed. The new detector `tests/doc_claims.py` `check_duty_switch_claims` was run with each pre-fix sentence put back and with each code fact mutated, then restored (output kept to its FAIL lines):

- docs/configuration.md on/off row restored to "is not started unless the tank needs heat now": rc=1, `FAIL docs/configuration.md on/off switch row: the not-started exception names the step heating the tank`.
- the Pump duty control bullet restored from 6295f868a4: rc=1, `FAIL docs/configuration.md: every 'heat not delivered' sentence names the direction lost_share charges (hot water to heating) and not the other`.
- docs/how-it-works.md restored from 6295f868a4: rc=1, `FAIL docs/how-it-works.md: every 'heat not delivered' sentence names the direction lost_share charges (hot water to heating) and not the other`.
- mutant `duty_legs.lost_share` reading index 1: rc=1, both pages FAIL naming "(heating to hot water)", so the direction is read from the code, not hard-coded.
- mutant `supply_hold._ends_soon` returning `not tank_reason(inp)`: rc=1, `FAIL supply_hold._ends_soon holds a cold-tank start on a space step and passes it on a hot-water step ... [space=False dhw=False]`.
- all restored: rc=0, ALL 356 checks PASSED.


## Null control

Second pass: each of the five `check_late_delta_claims` checks is run in the same pass against its own pre-fix sentence verbatim (`_LATE_DELTA_BAD`) and refuses it (five `ok ... refuses the pre-fix sentence (null control)` lines). The card-phrase and config-flow-phrase lookups each matched a non-empty set at origin/main (the lookup's own null control: an empty match set would read "none gone" for every head); the drop each reports is the set difference against origin/main.

First pass:


`git grep -c -E "less than 10 minutes after it came on|A switch that stops the compressor is priced|The mode goes first when the pump is switched on|duty_switch_\*|min\(a, b\) / p_max" <ref> -- README.md docs/configuration.md docs/how-it-works.md`: at e23124ff6e it prints nothing; at b4617aa636 it prints `README.md:1`, `docs/configuration.md:3`, `docs/how-it-works.md:1`. With the added how-it-works paragraph cut out of the head's page, the same pattern counts 0 there.

For the two corrected sentences the control is the detector above: green at the head, red with either pre-fix sentence put back.


## Figures

- `python3 tests/doc_claims.py` at 254f0ed03e: ALL 368 checks PASSED, rc 0 (first pass: 356; the 12 added are `check_late_delta_claims`).
- `python3 tests/doc_claims.py --markers --user`: `0 user-doc marker(s), 0 due`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Gate scope of this pass's own two commits, `python3 tests/closure.py select --diff 69afda819f --workdir "$D"` (69afda819f, the last stacked merge) at 254f0ed03e: `MODE: SCOPED`, scope.run naming tests/doc_claims.py, tests/entities.py, tests/harness_headers.py, tests/md_tables.mjs; each run locally with `PYTHONPATH=tests/hastub`:
  - tests/doc_claims.py: rc 0, ALL 368 checks PASSED
  - tests/entities.py: rc 0, ALL 2713 ENTITY CHECKS PASSED
  - tests/harness_headers.py: rc 0, ALL 115 HARNESS HEADER CHECKS PASSED
  - tests/md_tables.mjs: rc 0, doc_misrendered_lines=0
- The branch-wide scope (`--diff $(git merge-base origin/main HEAD)`) also selects the code suite, reached only through the three stacked product heads' own code, which their own pull requests' CI proves; this pass's diff is docs and `tests/doc_claims.py` only and cannot reach it, so it was not re-run here.
<!-- figure-block: scope-line mb=0f37833e2194739b431656a70c652b0679c8fa58 head=254f0ed03e62af64f05eb5bbe56e4857207ac15d -->
~~~text
MODE: SCOPED -- 30 script(s) run, 3 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `arch-score / arch-score`: red on 9e02464877, a commit of pull request 3562's branch, which this branch carries only through the stacked merge of 3562's head; not this pass's change and not in the owed set `merge_train.py owed-reds` prints. Its answer is 3562's, in that pull request. Cheaper detector for this branch: none owed, the commit is not this group's. Carry: dismissed: owned by pull request 3562
- `tests / fast (3.14)`: red on 04f8ab9fba and 9e02464877 (3562's branch), 30b069508f and a02783d44d (3532's branch), 0165e02aad (3556's branch); every one reaches this branch only through a stacked head, none is a commit of this pull request's own (`git merge-base --is-ancestor <sha> pr/<n>`). Answered by those pull requests at their own heads, whose own checks the train reads. Carry: dismissed: owned by pull requests 3532, 3556 and 3562
- `tests / mutation`: red on 49afbe9d01, a02783d44d, 6c5fc42f5e and 56eb07ae2a (3532's branch) and 9e02464877 (3562's branch), likewise only through the stacked heads. Carry: dismissed: owned by pull requests 3532 and 3562

This pull request's own commits (6295f868a4, 7312f605ee, 3fa750ea38 and this pass's) carry none of the three; the enumerator is the `red-history` record `policy_lint.mjs --pr-body` prints over `git rev-list $(git merge-base origin/main HEAD)..HEAD`, each red sha mapped to its branch by `git merge-base --is-ancestor`.

## Forward-carry

none: every lead this pass found is corrected here, in this group's own pages. Carry: dismissed: nothing changes a later stage

## Friction

none. Carry: dismissed: no friction recorded
