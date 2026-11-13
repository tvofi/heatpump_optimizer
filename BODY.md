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

b4617aa63635c2269f1d12d1df242839dd11fce7, on origin/main e23124ff6e45bac1d48b4a775dad555a37965355 (merge base; main had not moved at 2026-11-13 21:01 UTC).

## Mutation proof

No production line changed. The new detector `tests/doc_claims.py` `check_duty_switch_claims` was run with each pre-fix sentence put back and with each code fact mutated, then restored (output kept to its FAIL lines):

- docs/configuration.md on/off row restored to "is not started unless the tank needs heat now": rc=1, `FAIL docs/configuration.md on/off switch row: the not-started exception names the step heating the tank`.
- the Pump duty control bullet restored from 6295f868a4: rc=1, `FAIL docs/configuration.md: every 'heat not delivered' sentence names the direction lost_share charges (hot water to heating) and not the other`.
- docs/how-it-works.md restored from 6295f868a4: rc=1, `FAIL docs/how-it-works.md: every 'heat not delivered' sentence names the direction lost_share charges (hot water to heating) and not the other`.
- mutant `duty_legs.lost_share` reading index 1: rc=1, both pages FAIL naming "(heating to hot water)", so the direction is read from the code, not hard-coded.
- mutant `supply_hold._ends_soon` returning `not tank_reason(inp)`: rc=1, `FAIL supply_hold._ends_soon holds a cold-tank start on a space step and passes it on a hot-water step ... [space=False dhw=False]`.
- all restored: rc=0, ALL 356 checks PASSED.

## Null control

`git grep -c -E "less than 10 minutes after it came on|A switch that stops the compressor is priced|The mode goes first when the pump is switched on|duty_switch_\*|min\(a, b\) / p_max" <ref> -- README.md docs/configuration.md docs/how-it-works.md`: at e23124ff6e it prints nothing; at b4617aa636 it prints `README.md:1`, `docs/configuration.md:3`, `docs/how-it-works.md:1`. With the added how-it-works paragraph cut out of the head's page, the same pattern counts 0 there.

For the two corrected sentences the control is the detector above: green at the head, red with either pre-fix sentence put back.

## Figures

- `python3 tests/doc_claims.py` at b4617aa636: ALL 356 checks PASSED, rc 0 (round 1: 348; the 8 added are `check_duty_switch_claims`).
- `python3 tests/doc_claims.py --markers --user`: `0 user-doc marker(s), 0 due`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` at the head: rc 0, claims.json and claims.md unchanged by the run.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`; each of `scope.run`'s scripts run locally with `PYTHONPATH=tests/hastub`:
  - tests/doc_claims.py: rc 0, ALL 356 checks PASSED
  - tests/entities.py: rc 0, ALL 2711 ENTITY CHECKS PASSED
  - tests/harness_headers.py: rc 0, ALL 115 HARNESS HEADER CHECKS PASSED
  - tests/plan_view.py: rc 0, plan reason codes, price provenance and slot energy OK
  - tests/md_tables.mjs: rc 0, doc_misrendered_lines=0
  - tests/card_drift.mjs: rc 0, identical in all 45 states
<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=b4617aa63635c2269f1d12d1df242839dd11fce7 -->
~~~text
MODE: SCOPED -- 6 script(s) run, 27 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none: no pull request exists, so no check has run on this branch. Carry: dismissed: no red check to answer

## Forward-carry

none: both defects were in this group's own sentences and are corrected here. Carry: dismissed: nothing changes a later stage

## Friction

none. Carry: dismissed: no friction recorded
