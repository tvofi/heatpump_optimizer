Thank you, Bankaifan, for pull request 3456: the supply switch's minimum run and minimum pause are your design, and your production and test commit is the first commit here, authored by you. Our changes are later commits on top of it. Part of #201.

`_write_supply`, the one gate the cycle and the step tick write the supply switch through, enforced no minimum run and no minimum pause, so a re-solve or a cycle landing inside a step could stop a compressor minutes after the switch started it, or start it minutes after the switch stopped it. `supply_hold.py` now owns that rule, placed in `_write_supply` after `early_cutoff.allow_on` and `supply_write`. It only delays a write and never makes one. A write of `None`, a fixed mode, a live boost, system identification and an unreadable switch pass through unchanged. The step tick retries a held write with the step's own command, or with the action's command where the plan gives none. The two minimums are constants, `supply_hold.MIN_RUN` and `MIN_PAUSE`, and the early cut-off reads the same pair.

Changes on the contributor's commit, keyed to the brief:

- (a) One clock. A run's and a pause's age is the switch's own state and `last_changed`, the clock `early_cutoff._cycle_guard` already uses. The private `_Hold` record, its birth time and `ArbiterState.hold` are gone. `ArbiterState` keeps the held flag (`supply_held`) and gains `held_until`, the deadline the learners' freeze reads. A restart of Home Assistant builds a new state machine, and its first write stamps `last_changed` at the restart. The real-HA contract `homeassistant.core.StateMachine` in `tests/ha_contract.py` pins this, so a pump found running after a restart is held on for at most MIN_RUN. A reload of the integration does not touch the stamp, so an hour-old run is switched off at once.
- (b) `pump_arbiter.supply_tick` retries a held write that `step_supply` gives no command for (an empty plan) with the action's own value (`_action_supply`). It drops the write where the cycle itself would write nothing: a mode left, a stale plan or no action. System identification passes the gate unchanged.
- (c) Learners. The flow lift and the measured-COP denominator replay *commanded* power for an interval (`coordinator._commanded_power`), so a held interval would be read wrong. It is frozen through the existing reason path: `_tail_freeze` returns `supply_hold.FREEZE_HELD` through `supply_hold.freeze_reason`, until the deadline `hold_supply` fixed at the held write, two plan intervals on, as `early_cutoff.CutoffState.interval_cut` counts two cycles. No new seam, so this stays size M.
- (d) Running and stopped are read as `_pump_off` reads them: `off` is stopped, and any other readable state is running. Both now read the switch through one reader, `pump_arbiter.supply_switch`, so a `climate` target's run (`heat`) is held like a switch's.
- (e) The coordinator passes its `arbiter_inputs` builder, which the gate calls only for a write that is not `None`, and the gate's held flag through `held`. `_write_supply`'s docstring shrank to one line, and `max_class_loc` went down.
- (f) Rule three, as recommended: an ON that starts a run the plan ends within MIN_RUN is skipped, except on a hot-water step (`dhw` or `both`) whose tank is below its minimum or under a disinfection hold. That predicate is `supply_hold.tank_reason`, which `early_cutoff._plant_exempt` now calls too, so the exemption is one function, the early cut-off's.

**Rule three, for the owner's ruling.** It is built as recommended. The closed-loop harness shows what it costs and what it buys. With cycles landing inside steps, the gate removes every short run and short pause on every variant and both prices. Rule three's own share is the difference between the gate-on arm and the same arm with `supply_hold._ends_soon` forced `False` (`no_rule3.py` below):

- Its cost is heat the plan booked and the pump never delivered. On LIGHT winter prices that is 0.82 kWh/day against 0.02 kWh/day without the rule, with the room minimum at 17.68 against 17.90 degC. On HOT flat prices the plan books one isolated step at a time and every cycle lands seven minutes in. Rule three skips each of those starts, so the pump never runs that day: 0.0 against 1.0 kWh, room minimum 19.68 against 19.99 degC.
- What it buys is runs carried past a planned stop: 0.00 against 0.20 kWh/day (LIGHT winter) and 0.00 against 0.20 kWh/day (HOT flat).
- NULL and HOT on winter prices are identical with and without the rule.

The step tick does not rescue a skipped start, because a re-solve that books only the current step leaves the next step off. If the owner rules rule three out, `_ends_soon`, its exemption and `tank_reason`'s use in it go, and nothing else changes.

Writers of the supply switch, enumerated by `git grep -n 'switch_supply(' -- custom_components`, which returns two call sites and the definition:

| writer | disposition |
|---|---|
| the cycle (`_apply_action` -> `_write_supply`, coordinator.py) | gated |
| the step tick (`pump_arbiter.supply_tick` -> `SupplyWiring.write` = `_write_supply`) | gated; retries a held write |
| the early cut-off's cut (`early_cutoff.on_room_event` -> `switch_supply`) | not gated, by design: it writes only OFF and refuses a cut inside MIN_ON on the same clock (`switch_age`) and the same constants |
| unload (`pump_arbiter.release` -> `release_supply`) | not affected: drops the tick and writes no switch |

Learners, by `_learning_frozen`'s callers: the flow lift (`coordinator._commanded_power`) and the measured-COP denominator replay commanded power, so both are frozen now. The house heat-loss fallback with no power entity uses commanded power too, and is frozen by the same reason. The slab, draw-range, accuracy and defrost learners use `_measured_power` and are unaffected by a hold either way.

The main-tree fixtures this touches: `_sa_install` and `_sa_guarded` (#2492) stamped the switch off at the first cycle's own instant, which on the switch's clock is a pause zero minutes old, i.e. a restart. They now stamp it an hour back, and `_sa_install` re-stamps only on a state change, as `StateMachine.async_set` keeps `last_changed`. With the old fixtures, seven #2492 checks fail at this head. Every check passes with the fixtures fixed, and the checks' expected values are unchanged.

Dropped from the contributor's branch: the closures commit and the deployment-shape commit, both re-derived here. Also dropped: the commit's `#1752` rig change (`_r9egb9_make` starting its switch off), because a `FakeState` with no stamp is an unknown age, which holds nothing, so main's rig stands unchanged.

## Head

390113cc661e798b946ebabd877a800a2aa9f5ed, measured on origin/main 17ae732a4e8b26f05bca901041a2a4d78434c6b2 (which carries #3530) at 2026-11-13T07:40Z. It is the handoff head 3d56953499ef plus this reconcile round: 754a2b022d (the merge of origin/main 17ae732a) 1e1dae07d7 (the #3420 part E rows with the minimum pause engaged) and 390113cc661e (the merge of the pull request's head d5eb9f80e2ea, which `prepr.sh`'s push-order step required; it changes the tree only by the existing line in `dev/programme/delivery/3512.md`, so the figures taken at 1e1dae07d7 below describe this tree's code). The reviewer's delta is `git diff d5eb9f80e2ea 390113cc661e798b946ebabd877a800a2aa9f5ed`. `git merge-tree --write-tree origin/main HEAD` against main fa9479e059f2 printed no conflict, so no second merge was made.

### Reconcile with #3530 (R10-MODE-BEFORE-SUPPLY-ON)

The merge conflicted in one hunk, `coordinator._write_supply`: #3530 changed the switch call to `pump_arbiter.write_supply(self, switch_entity, value)`, which writes the step's mode ahead of a switch-on (`pump_arbiter._lead_mode`), and this branch had changed the next line to `elif switch_entity and not held.supply_held:`. Both are kept: `supply_hold.hold_supply` stays ahead of the call, so a switch-on the hold returns `None` for reaches no mode write, and the step tick's retry of a held write (`pump_arbiter.supply_tick` -> `SupplyWiring.write` = `_write_supply`) runs through the same call, so a retried switch-on that lands writes the mode first. `supply_hold.py`'s rule and `write_supply`'s mode-then-switch order are unchanged. Every other file merged without conflict.

Re-read at main 17ae732a, both groups' paths: `custom_components/heatpump_optimizer/pump_arbiter.py` (`write_supply`, `_lead_mode`, `switch_supply`, `supply_tick`), `coordinator.py` (`_apply_action`, `_write_supply`), `early_cutoff.py` (its cut writes OFF through `switch_supply` alone, and `_lead_mode` writes nothing for an OFF) and `tests/features.py`'s two sections. Writers of the supply switch after the merge, by `git grep -n -E 'switch_supply\(|write_supply\(' -- custom_components`, which also matches `_write_supply`'s own call in `_apply_action` and its definition: `write_supply` from `_write_supply` (gated, cycle and step tick), `switch_supply` from `write_supply` and from `early_cutoff`'s cut (OFF only, not gated, by design, as in the table below). No other caller.

`tests/features.py`: `_mb_run` (#3530's rig) stamped the switch's state at 06:00 itself, which on this branch's clock is a pause zero minutes old and would engage the hold on every cycle row; it now takes `since`, an hour back by default, so #3530's rows engage no hold and their expected values are unchanged, and `after`, the step ticks fired each minute after the write. Three rows are added after "a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back":

- "with the minimum pause engaged too, a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back" (switch off since 05:58);
- "a cycle switch-on the minimum pause holds back writes no mode and no switch";
- "a switch-on held on one tick and landing on a later one writes the mode immediately before the switch on that later tick": the ticks 06:01 to 06:12 write only at 06:08, MIN_PAUSE after 05:58, and write `select_option` then `turn_on`.

Null controls, in the same block: the same cycle with no hold engaged writes mode then switch on the first write ("null control: the same heating step with no cut on record writes the mode, then the switch", and "a cycle that switches the supply on writes the step's mode first, then the switch"), exactly as at #3530's head; the "null control, <case>: the service calls and their order are today's" rows (no mode entity, duty mode observe, supply already on) write nothing new.

### Earlier rounds

3d56953499ef23b0d51f2eee7d0cc782d05b572a, measured on origin/main 43e95474559ca8e2188830f8775c1ddf52df964a at 2026-11-12T19:22Z. It is the handoff head 701a18e26661 (review round 1's head 5dea8264f2c8, plus the repair commit d94be70cc39e, the merge of origin/main 6e100ef69802 (24b879dc7cb3), the `tests/entities.py` closure re-derived by `--single` (42c2717d0c0b), the merge of origin/main 2b4515dc5282 (ebf11f1265c5, seat tooling only), and the merge of origin/main 19baca76181c (701a18e26661).), plus this repair: 874cb0168230 (the learners' freeze as `supply_hold.freeze_reason`, which pays `coord_footprint`), 808f50df7f4c (`class_excess_loc` recorded one lower), the merge of the pull request's head b2dd262882a8 (mutation-autofix's pins), the merge of origin/main 43e95474559c (934f6d683eaf), a936a11d4604 (five pins whose sites 874cb0168230 removed) and 3d56953499ef (the four sites that replaced them, pinned). The reviewer's delta is `git diff 701a18e26661 3d56953499ef`.

The merge of origin/main conflicted in six files, because main's `duty_switch.py` and this branch's `supply_hold.py` were both added beside `pump_arbiter.py`. The counts are summed (`docs/architecture.md`: 90 modules, 32 importing `homeassistant`; `claims.py`'s three RESULT lines and its table regenerated by `claims.py`; `tests/deployment_shape.py`: 109 package files) and `tests/features.py` keeps both added sections. The closure-pair census in `tests/deployment_shape.py`'s docstring is re-measured under `## Figures`.

Re-run at this head: the six mutants below, the scoped gate, `tests/structure.py`, the architecture score, both `ha_contract.py` providers and the closed-loop harness. Not re-run: the 17-mutant block and the round-1 survivor blocks under `## Mutation proof`, whose lines this repair does not touch, and rule three's share.

## Mutation proof

Reconcile round, each mutant applied by hand to `coordinator._write_supply` at 1e1dae07d7 and run against the #3420 part E block (`features_block.py` from "# #3420 part E (Bankaifan)" to "# The pump_duty record's held slots are declared", 20 checks; baseline `ALL 20 FEATURES BLOCK PASSED`), then restored:

```
M1 the hold after the mode write (_lead_mode on the pre-hold value, then hold_supply, then the bare switch write)
  FAIL a cycle switch-on the minimum pause holds back writes no mode and no switch  [[('select', 'select_option')]]
  FAIL a switch-on held on one tick and landing on a later one writes the mode immediately before the switch on that later tick  [{1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [('switch', 'turn_on')], 9: [], 10: [], 11: [], 12: []}]
2 of 20 FEATURES BLOCK FAILED
M2 the retry of a held write calls the bare switch write (switch_supply when supply_held was set on entry)
  FAIL a switch-on held on one tick and landing on a later one writes the mode immediately before the switch on that later tick  [{1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [('switch', 'turn_on')], 9: [], 10: [], 11: [], 12: []}]
1 of 20 FEATURES BLOCK FAILED
```

M1 does not fail the cut-off row with the pause engaged: an early cut turns the switch-on into an OFF before the hold, and `_lead_mode` writes nothing for an OFF, so that row passes under either order. The row M1 fails is the pause-held one, where the hold alone is what stops the switch-on. Driver: a scratch `mut.py` holding the two replacements, one-off.

### Earlier rounds

Every predicate the fix adds or moves, mutated by hand one at a time and run against the group's mutation command. That command runs two `features_block.py` blocks: the supply-switch sections from "supply switch at step boundaries (#2492, R10-SAV-ACTUATION)" to the ceiling probe, and the early cut-off's section.

```
KILLED   supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(_ends_soon(inp, boosts, now))' | a re-solve three minutes into a pause does not switch the supply on; the step tick do
KILLED   supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(age < MIN_PAUSE) if value els' | rule three: a space step, ON at minute 7 before an OFF step -> (None, True)  [(True, 
KILLED   supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(age < MIN_PAUSE or _ends_soon' | a re-solve three minutes into a run does not switch the supply off; the step tick doe
KILLED   supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(age < MIN_PAUSE or _ends_soon' | a re-solve three minutes into a run does not switch the supply off; the step tick doe
KILLED   supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(age <= MIN_PAUSE or _ends_soo' | a re-solve three minutes into a pause does not switch the supply on; the step tick do
KILLED   supply_hold.py: 'or (inp.action or {}).get("mode") == "system_identificatio' -> '' | system identification: an OFF three minutes into a run is written at once  [[(7, 'tur
KILLED   supply_hold.py: '(state != "off") is value' -> '(state == "on") is value' | a climate target reading heat three minutes is held on until MIN_RUN  [[(0, 'turn_off
KILLED   supply_hold.py: 'if state in _UNREADABLE or' -> 'if' | stop: an OFF to a switch reading unavailable passes -> (False, False)  [(None, True)]
KILLED   supply_hold.py: 'return None if since > now else now - since' -> 'return now - since' | stop: an OFF to a switch stamped ahead of the clock passes -> (False, False)  [(None,
KILLED   supply_hold.py: 'return None if since > now else now - since' -> 'return None if since >= now el' | after a Home Assistant restart a supply found on is held for MIN_RUN of its restart s
KILLED   supply_hold.py: 'return not (step_duty(inp.plan, now) in ("dhw", "both") an' -> 'return True' | rule three: a hot-water step with the tank below its minimum -> (True, False)  [(None
KILLED   supply_hold.py: 'if nxt - now >= MIN_RUN or' -> 'if nxt - now > MIN_RUN or' | rule three: null control: the same ON at minute 5, MIN_RUN before the boundary -> (Tr
KILLED   supply_hold.py: 'if inp.disinfecting:\n        return "disinfecting"' -> '' | rule three: a hot-water step under a disinfection hold -> (True, False)  [(None, True
KILLED   pump_arbiter.py: 'on = _action_supply(inp)  # a held write the plan does not' -> 'pass' | with no plan, an OFF held three minutes into a run lands at MIN_RUN  [[]]
KILLED   coordinator.py: 'elif switch_entity and not held.supply_held:' -> 'elif switch_entity:' | a held OFF is not logged as the cooling or blocked-mode skip  [["Not switching switch
KILLED   early_cutoff.py: 'return tank_reason(inp)' -> 'return None' | a tank below its minimum exempts the step
KILLED   early_cutoff.py: 'if run is None or run < MIN_ON:' -> 'if run < MIN_ON:' | rc 1
17 of 17 killed
```

The block above was taken at 701a18e26661 and is not re-run. Five of its 22 mutants sat on lines the repair commit 874cb0168230 replaced (`interval_held`, `held_at`, `_tail_freeze`'s old branch) and are removed from it. Their successors, every predicate and assignment 874cb0168230 adds, were applied in place one at a time at 3d56953499ef and run against the group's mutation command, two `features_block.py` blocks: the supply-switch sections, from "supply switch at step boundaries (#2492, R10-SAV-ACTUATION)" to main's `duty_switch` import (the first line after this branch's sections), and the early cut-off's section. The last line each block prints is shown:

```
BASELINE rc 0 | ALL 60 FEATURES BLOCK PASSED
KILLED   supply_hold.py: 'held.supply_held, held.held_until = True, now + _freeze_span(inp.config)' -> 'held.supply_held = True' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   supply_hold.py: 'dt_util.as_utc(now or dt_util.now()) < until' -> 'dt_util.as_utc(now or dt_util.now()) <= until' | rc 1 | FAIL freeze_reason: null control: 60 minutes ago is not  ['supply_held']
KILLED   supply_hold.py: 'held_now = until is not None and ' -> 'held_now = ' | rc 1 | TypeError: '<' not supported between instances of 'datetime.datetime' and 'NoneType'
KILLED   supply_hold.py: 'return FREEZE_HELD if held_now else None' -> 'return None' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   supply_hold.py: 'return 2 * timedelta(minutes=EntryConfig' -> 'return 1 * timedelta(minutes=EntryConfig' | rc 1 | FAIL freeze_reason: a write held 59 minutes ago on a 30-minute interval is frozen  [None]
KILLED   coordinator.py: 'return supply_hold.freeze_reason(pump_arbiter.state_for(coord)) or learner_unmetered(' -> 'return learner_unmetered(' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
RESTORED rc 0 | ALL 60 FEATURES BLOCK PASSED
6 of 6 killed
```

`prepr.sh` step 6d' drew mutants of the added lines with the same command and listed 8 survivors at c64049f84b. Each now has a killing check, run as above:

```
KILLED   coordinator.py: 'elif switch_entity and not held.supply_held:' -> 'elif False:' | null control: an OFF both blocked channels skip writes nothing and is logged as the s
KILLED   pump_arbiter.py: 'if held.supply is None or (held.supply[0] == step and not ' -> 'if False:' | the step tick writes nothing inside a step whose boost starts mid-step
KILLED   pump_arbiter.py: '(held.supply[0] == step and not held.supply_held)' -> '(held.supply[1] == step and no' | the step tick writes nothing inside a step whose boost starts mid-step
KILLED   pump_arbiter.py: 'held.supply_held = False  # a held write dies with its com' -> 'held.supply_held = True  # a h' | step tick, held write: the optimizer switched off: no write, the hold dropped
KILLED   pump_arbiter.py: 'return bool(inp.action.get("heat_pump_on"))' -> 'return True' | with no plan, an OFF held three minutes into a run lands at MIN_RUN
KILLED   supply_hold.py: 'if value is None:\n        return value' -> '' | a write of None passes and marks nothing held
KILLED   supply_hold.py: 'if value is None:\n        return value' -> 'if False:\n        return value' | a write of None passes and marks nothing held
KILLED   supply_hold.py: 'float(inp.state.dhw_temperature) < float(' -> 'float(inp.state.dhw_temperatur' | rule three: a hot-water step with the tank exactly at its minimum (not below)
```

At 07a83211d7 step 6d' listed one more, `supply_hold.py` CONST_SWAP `getattr(params, "dhw_enabled", True)`. The check "rule three: a cold tank on params with no dhw_enabled field is not exempt" kills it: the mutant's block prints `1 of 76 FEATURES BLOCK FAILED`, the head's `ALL 76`. The `heat_pump_on` default's CONST_SWAP survivor is gone with the default: `_action_supply` reads the key with no default.

Command: `python3 mut_final.py mutant_cmd.sh` (scratch drivers, one-off; `mutant_cmd.sh` is the two `features_block.py` calls named in `## Figures`). `prepr.sh` step 6d' ran the same command over its drawn mutants (`MUTANT_CMD`).

Review round 1 returned `blocked: mutation-vacuous`: ten mutants of added or moved lines survived the group's mutation command and the whole `tests/features.py`. Each now has a killing check in `tests/features.py` ("which writes are held: ...", "step tick, held write: ...", "an install with no power switch: ..."), shaped on the reviewer's `probe_block.py`. The tenth, `supply_switch`'s `if entity else None`, is equivalent under `FakeStates`, whose `get(None)` is `None`. Upstream `StateMachine.get(None)` raises, because a miss retries `entity_id.lower()`. The new contract "StateMachine.get(None) raises" in `tests/ha_contract.py` pins that (`expect="real"`). The no-switch install drives `_write_supply` on a `Coord` with no `heat_pump_switch_entity`, through a states double that reads as upstream does. Each mutant was applied in place, one at a time, at the head, and run against the group's mutation command:

```
KILLED    1 supply_hold.py: 'return (inp.mode not in (MODE_AUTO, MODE_ECONOMY)' -> 'return (False' | FAIL which writes are held: a fixed mode (comfort) passes an OFF three minutes into a run -> (False, False)  [(None, True)]
KILLED    2 supply_hold.py: 'return (inp.mode not in (MODE_AUTO, MODE_ECONOMY)' -> 'return (inp.mode != MODE_AUTO' | FAIL which writes are held: economy is a plan mode: an OFF three minutes into a run is held -> (None, True)  [(False, False)]
KILLED    3 supply_hold.py: 'or boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNE' -> 'or boosts.active(CHANNEL_DHW, now))' | FAIL which writes are held: a live space boost passes an ON three minutes into a pause -> (True, False)  [(None, True)]
KILLED    4 supply_hold.py: 'or boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNE' -> 'or boosts.active(CHANNEL_SPACE, now))' | FAIL which writes are held: a live DHW boost passes an ON three minutes into a pause -> (True, False)  [(None, True)]
KILLED    5 supply_hold.py: 'in ("dhw", "both") and tank_reason' -> '== "dhw" and tank_reason' | FAIL which writes are held: rule three: a both step with the tank below its minimum is exempt -> (True, False, 'both')  [(None, True, 'both')]
KILLED    6 supply_hold.py: 'if nxt - now >= MIN_RUN or' -> 'if nxt - now >= MIN_RUN - timedelta(minutes=1) or' | FAIL which writes are held: rule three: an ON at minute 6, one tick inside MIN_RUN of an OFF step, is skipped -> (None, True)  [(True, False)]
KILLED    7 pump_arbiter.py: 'if on is None and held.supply_held and not inp.entry_release' -> 'if on is None and held.supply_held:' | FAIL step tick, held write: the entry released: no write, the hold dropped  [([False], True)]
KILLED    8 pump_arbiter.py: 'if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_sta' -> 'if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or not inp.acti' | FAIL step tick, held write: a stale plan: no write, the hold dropped  [([False], True)]
KILLED    9 pump_arbiter.py: 'if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_sta' -> 'if inp.mode != MODE_AUTO or inp.plan_stale or not inp.action' | FAIL step tick, held write: economy with no plan retries the action's OFF  [([], False)]
KILLED   10 pump_arbiter.py: 'heat_pump_switch_entity\n    return inp.hass.states.get(entit' -> 'heat_pump_switch_entity\n    return inp.hass.states.get(entit' | FAIL an install with no power switch: the gate writes and holds nothing, and raises nothing  [AttributeError("'NoneType' object has no attribute 'lowe
10 of 10 killed
```

Command: `python3 mut10.py mutant_cmd.sh`. `mut10.py` is a scratch driver, one-off, and holds the ten replacements the verdict names. The checks above it are unchanged at the head. `prepr.sh` step 6d' printed `no survivor among the diff's first 40 mutant(s)` at the head, under the same command run in its own working directory (`## Friction`). The ten were re-applied at this head with the same result.

Red without the fix, the contributor's design at the head's tests: the one-clock checks, the empty-plan retry, system identification, the climate target, the learners' freeze, rule three's tank exemption and the unreadable, unknown and future-stamped switch each name a mutant above that reverts that change.

## Null control

- **Every write on a step boundary, no restart, gate on against gate off (main's write).** The service calls and their order are identical in all three cases: writes on step boundaries, a plan the step tick moves, and no supply switch (`tests/features.py` "null control: ..., the gate issues main's service calls in main's order"). The perturbation is a re-solve inside a step (`_ms_short`), which the gate holds.
- **The early cut-off's own checks pass unchanged.** Its `features_block.py` block's output at the head is byte-identical to the merge base's: `diff ec_base.txt ec_head.txt && echo IDENTICAL` printed IDENTICAL, 60 checks.
- **Closed loop, cycles on step boundaries (`CYCLE_PHASE_MIN=0`).** The gate holds nothing, and gate on equals gate off on every line, for NULL, HOT and LIGHT on both prices.
- **Closed loop, default mode.** Output is byte-identical before and after the harness extension (`diff before.txt after.txt && echo IDENTICAL`, NULL variant).
- **Every quantified closed-loop figure has its flat-price twin** in the table below.
- **A restart.** The `homeassistant.core.StateMachine` contract passes against real Home Assistant 2026.11.0. Under the stub it is reported "still divergent", as an `expect="real"` contract must be. The perturbation that would fail it is a write carrying the restored stamp (`async_set(..., timestamp=restored)`).

## Figures

Re-taken at 1e1dae07d72c3dd62411decd93b37f9f71d9505f (tree equal to 390113cc661e798b946ebabd877a800a2aa9f5ed but for the delivery row) on merge base 17ae732a4e8b, 2026-11-13:

- Scoped gate: `GATE_SCOPE=auto bash tests/run.sh` printed `MODE: SCOPED -- 24 script(s) run, 9 scoped out.` and `1 TEST SCRIPT(S) FAILED`, the one being `tests/golden.py`, run without `GOLDEN_MODE=drift`. Re-run as the contract states, `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/golden.py` printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 17ae732a4e8b26f05bca901041a2a4d78434c6b2` and `NO STALE FIXTURE`, exit 0. `tests/features.py` passed inside the gate (488 s).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (with `env -u BASH_ENV`): `ALL 2709 ENTITY CHECKS PASSED`, inside the gate run.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget re-recorded or raised.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- The #3420 part E block alone (`features_block.py` from "# #3420 part E (Bankaifan)" to "# The pump_duty record's held slots are declared"): `ALL 20 FEATURES BLOCK PASSED`; the two mutants under `## Mutation proof` turn it red.
- The group's mutation command, two `features_block.py` blocks: from `R.section("supply switch at step boundaries (#2492` to `R.section("duty-switch restart learning, part A`, and the early cut-off's section to `R.section("°F set-points: one unit rule`: `ALL 108 FEATURES BLOCK PASSED` and `ALL 60 FEATURES BLOCK PASSED`.

Measured at 3d56953499ef and not re-taken (this round changes no line they read but `_write_supply`'s switch call):

- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) bash tests/run.sh`. `MODE: SCOPED -- 24 script(s) run, 9 scoped out` at the head, which prints `26 TEST SCRIPT(S) PASSED; 8 SCOPED OUT AND NOT RUN`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2709 ENTITY CHECKS PASSED` at the head, inside the scoped gate run. `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` at the merge recorded the closure's `rc` as 0 (it was 1) and changed nothing else.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head. `max_class_loc` was recorded at 7919, down from 7921. `duplication_copies` was held at its budget by `pump_arbiter.supply_switch`.
- `PYTHONPATH=tests/hastub python3 tests/ha_contract.py` and `/opt/hpo/venv-ha/bin/python tests/ha_contract.py --contracts-only`: 0 FAIL lines under either provider at the head. The new contract "StateMachine.get(None) raises" reads `ok` against real Home Assistant and "still divergent under the stub" under `tests/hastub`.
- Closures: `GOLDEN_REF=origin/main ./tests/derive_closures.sh --scripts-from scripts.txt --record-only --out-dir rec`, then `python3 tests/closure.py merge --in-dir rec --partial --allow-failures`, on Linux. `supply_hold.py` joins the 22 closures that read the coordinator or the early cut-off, and no closure loses a file (a set diff of `closures` against origin/main).
- Closed loop, phase 7: `SUPPLY_HOLD=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/early_cutoff_closed_loop.py NULL` (and `HOT`, `LIGHT`). sha1 of the harness at the head: 39a4867b2afda697d041add836d69a9fd3e37401. Re-run at 3d56953499ef: the twelve data rows of each of the phase-7 and phase-0 runs equal the rows of the two tables below (a row-by-row comparison of the harness output with this body's tables printed `PHASE7-IDENTICAL` and `PHASE0-IDENTICAL`; control: the same comparison of the phase-7 rows with the phase-0 rows printed `CONTROL-DISTINCT`).

```
NULL    winter_typical gate off held/day   0.0 episodes   0  writes   8  short runs  1 pauses  2  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.4 kWh  room min 19.99  tank min 35.00
NULL    winter_typical gate on  held/day  11.0 episodes   3  writes   8  short runs  0 pauses  0  booked-not-delivered   0.05 kWh  run-past-stop   0.05 kWh  pump    1.3 kWh  room min 19.97  tank min 35.00
NULL    flat           gate off held/day   0.0 episodes   0  writes   2  short runs  1 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    0.1 kWh  room min 19.69  tank min 35.00
NULL    flat           gate on  held/day   8.0 episodes   1  writes   0  short runs  0 pauses  0  booked-not-delivered   0.05 kWh  run-past-stop   0.00 kWh  pump    0.0 kWh  room min 19.68  tank min 35.00
HOT     winter_typical gate off held/day   0.0 episodes   0  writes   8  short runs  1 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    6.7 kWh  room min 20.95  tank min 35.00
HOT     winter_typical gate on  held/day   3.0 episodes   1  writes   8  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.30 kWh  pump    7.0 kWh  room min 20.95  tank min 35.00
HOT     flat           gate off held/day   0.0 episodes   0  writes   4  short runs  2 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.6 kWh  room min 20.18  tank min 35.00
HOT     flat           gate on  held/day   8.0 episodes   1  writes   0  short runs  0 pauses  0  booked-not-delivered   0.05 kWh  run-past-stop   0.00 kWh  pump    0.0 kWh  room min 19.68  tank min 35.00
LIGHT   winter_typical gate off held/day   0.0 episodes   0  writes  13  short runs  1 pauses  1  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   25.8 kWh  room min 17.93  tank min 35.00
LIGHT   winter_typical gate on  held/day  10.0 episodes   2  writes  11  short runs  0 pauses  0  booked-not-delivered   0.82 kWh  run-past-stop   0.00 kWh  pump   25.5 kWh  room min 17.68  tank min 35.00
LIGHT   flat           gate off held/day   0.0 episodes   0  writes  29  short runs  3 pauses  7  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   29.5 kWh  room min 18.97  tank min 35.00
LIGHT   flat           gate on  held/day  28.0 episodes   5  writes  16  short runs  0 pauses  0  booked-not-delivered   0.49 kWh  run-past-stop   0.00 kWh  pump   27.7 kWh  room min 18.90  tank min 35.00
```

- Closed loop, phase 0 (null control): `CYCLE_PHASE_MIN=0 SUPPLY_HOLD=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/early_cutoff_closed_loop.py NULL HOT LIGHT`

```
NULL    winter_typical gate off held/day   0.0 episodes   0  writes   4  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.5 kWh  room min 20.00  tank min 35.00
NULL    winter_typical gate on  held/day   0.0 episodes   0  writes   4  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.5 kWh  room min 20.00  tank min 35.00
NULL    flat           gate off held/day   0.0 episodes   0  writes   6  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    0.2 kWh  room min 19.72  tank min 35.00
NULL    flat           gate on  held/day   0.0 episodes   0  writes   6  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    0.2 kWh  room min 19.72  tank min 35.00
HOT     winter_typical gate off held/day   0.0 episodes   0  writes   4  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    7.5 kWh  room min 20.94  tank min 35.00
HOT     winter_typical gate on  held/day   0.0 episodes   0  writes   4  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    7.5 kWh  room min 20.94  tank min 35.00
HOT     flat           gate off held/day   0.0 episodes   0  writes   2  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.5 kWh  room min 20.15  tank min 35.00
HOT     flat           gate on  held/day   0.0 episodes   0  writes   2  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.5 kWh  room min 20.15  tank min 35.00
LIGHT   winter_typical gate off held/day   0.0 episodes   0  writes   6  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   24.5 kWh  room min 17.82  tank min 35.00
LIGHT   winter_typical gate on  held/day   0.0 episodes   0  writes   6  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   24.5 kWh  room min 17.82  tank min 35.00
LIGHT   flat           gate off held/day   0.0 episodes   0  writes  17  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   29.5 kWh  room min 19.02  tank min 35.00
LIGHT   flat           gate on  held/day   0.0 episodes   0  writes  17  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   29.5 kWh  room min 19.02  tank min 35.00
```

- Rule three's share, measured at 5dea8264f2c8 and not re-run: the same command run through `no_rule3.py`, a scratch driver that sets `supply_hold._ends_soon = lambda *_a: False` and then runs the harness.

```
NULL    winter_typical gate off held/day   0.0 episodes   0  writes   8  short runs  1 pauses  2  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.4 kWh  room min 19.99  tank min 35.00
NULL    winter_typical gate on  held/day  11.0 episodes   3  writes   8  short runs  0 pauses  0  booked-not-delivered   0.05 kWh  run-past-stop   0.05 kWh  pump    1.3 kWh  room min 19.97  tank min 35.00
NULL    flat           gate off held/day   0.0 episodes   0  writes   2  short runs  1 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    0.1 kWh  room min 19.69  tank min 35.00
NULL    flat           gate on  held/day   2.0 episodes   1  writes   2  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.03 kWh  pump    0.1 kWh  room min 19.70  tank min 35.00
HOT     winter_typical gate off held/day   0.0 episodes   0  writes   8  short runs  1 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    6.7 kWh  room min 20.95  tank min 35.00
HOT     winter_typical gate on  held/day   3.0 episodes   1  writes   8  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.30 kWh  pump    7.0 kWh  room min 20.95  tank min 35.00
HOT     flat           gate off held/day   0.0 episodes   0  writes   4  short runs  2 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump    1.6 kWh  room min 20.18  tank min 35.00
HOT     flat           gate on  held/day   2.0 episodes   1  writes   2  short runs  0 pauses  0  booked-not-delivered   0.00 kWh  run-past-stop   0.20 kWh  pump    1.0 kWh  room min 19.99  tank min 35.00
LIGHT   winter_typical gate off held/day   0.0 episodes   0  writes  13  short runs  1 pauses  1  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   25.8 kWh  room min 17.93  tank min 35.00
LIGHT   winter_typical gate on  held/day   6.0 episodes   3  writes  13  short runs  0 pauses  0  booked-not-delivered   0.02 kWh  run-past-stop   0.20 kWh  pump   25.0 kWh  room min 17.90  tank min 35.00
LIGHT   flat           gate off held/day   0.0 episodes   0  writes  29  short runs  3 pauses  7  booked-not-delivered   0.00 kWh  run-past-stop   0.00 kWh  pump   29.5 kWh  room min 18.97  tank min 35.00
LIGHT   flat           gate on  held/day   9.0 episodes   4  writes  22  short runs  0 pauses  0  booked-not-delivered   0.09 kWh  run-past-stop   0.35 kWh  pump   28.1 kWh  room min 18.92  tank min 35.00
```

The harness fixes the tank at 35.0 degC, so its tank minimum is not informative. Rule three's tank exemption is pinned by the `features.py` checks "rule three: a hot-water step ...", not by this harness.

- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL` at the head. Control: `score.py --diff 8c10361eb1fe b2dd262882a8` (the pull request's head against its merge base) prints `dS -0.0006 WORSENS (inadmissible: coord_footprint 2492->2493)`. The mechanism is 874cb0168230: `hold_supply`, which has the config in hand, fixes the freeze deadline in `ArbiterState.held_until`, so `_tail_freeze` no longer parses a config for `supply_hold` and reads one reason. `tests/structure.py`'s `class_excess_loc` was recorded one lower in 808f50df7f4c; no budget is raised.
- Unpinned sites: `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/features.py` at a936a11d4604 printed `PIN KILLED -- 4 new unpinned site(s)` and `PIN KILLED: 4 pinned, 0 left unpinned`, with the comment-only null control `supply_hold.py:59 NULL_COMMENT` surviving `tests/features.py`. Before a936a11d4604 the same command refused: `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory`, naming the five pins that commit drops.
- Closure-pair census (`tests/deployment_shape.py`'s docstring): pairs of scripts whose closures in `tests/closures.json` share a Jaccard index of 0.80 or more over their `custom_components/` files. The rule reads 148 at both parents of the merge (b2dd262882a8's side and origin/main), which is the figure each docstring carried, and 154 on the merged recording.

<!-- figure-block: scope-line mb=17ae732a4e8b26f05bca901041a2a4d78434c6b2 head=390113cc661e798b946ebabd877a800a2aa9f5ed -->
~~~text
MODE: SCOPED -- 24 script(s) run, 9 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

None at 3d56953499ef: the diff adds no site without a pin (`## Figures`, unpinned sites). The 35 sites listed at 701a18e26661 were pinned by mutation-autofix in b2dd262882a8. Five of those pins named sites 874cb0168230 removed (`_tail_freeze` GUARD_OFF and RETURN_DEL, `interval_held` CMP_BOUND, GUARD_OFF and RETURN_DEL) and are dropped. The four sites that replaced them are pinned in 3d56953499ef, each killed by `tests/features.py`: `supply_hold.py` `freeze_reason` BOOLOP, CMP_BOUND and RETURN_DEL, and `_freeze_span` RETURN_DEL.

## Red checks

Red at the pull request's head b2dd262882a8, read from its check runs:

- `arch-score / arch-score`: `FAIL: dS -0.0006 WORSENS; unexplained: coord_footprint 2492->2493`. Paid in 874cb0168230, not explained: the score reads NULL at 3d56953499ef (`## Figures`). Cheaper detector: `python3 tools/audit/archscore/score.py --diff <merge base>`, 57 s on this seat, which `fixer.md` step 17 names and neither `prepr.sh` nor `ci_predict.py` runs, so the red was reachable before the handoff and nothing on the local path looked. Process state (a) for that path. Standing cost if `prepr.sh` ran it: that 57 s per run.
- `tests / mutation` at 701a18e26661 (green at b2dd262882a8): 36 unpinned sites the diff added. mutation-autofix pinned them in b2dd262882a8; the four this repair adds are pinned in 3d56953499ef. No cheaper detector is owed: `prepr.sh` step 6d already predicts this red and `--pin-killed` is the repair, which ran here before the handoff.
- `pr-contract / pr-contract`: the body named 701a18e26661 under `## Head` while the head was b2dd262882a8, and answered no red for `arch-score`. This body answers both. No cheaper detector: `prepr.sh` step 7 is that detector and passed on the body at the head it was written for; the head then moved under it by the bot's commit.
- `gate`: red because the checks above are red; it aggregates them.
- `governance / instrument-self-tests`: not in the set `merge_train.py owed-reds` prints. Its failing step is not identified here: the job log's last 150 lines show `selftest_scope self-test: 117 checks, 0 failed` and `SELFTEST-SCOPE MUTANTS: every mutant refused`, and the job's steps in `governance.yml` name no file this diff touches. Whether it is red at the merge base was not read.
- `tests / nightly-ha (2025.2.0)` and `tests / nightly-status` at 701a18e26661: not required contexts; both come from the cancelled scheduled run 43130126209 and are skipped at b2dd262882a8.

## Forward-carry

none

## Friction

- prepr.sh: unclear: `MUTANT_IN_PLACE=1`, which `fixer.md` step 2 prescribes for a checkout, leaks from the caller into `prepr.sh --self-test`. Its assertion "a check needing a git checkout measures nothing in the archive copy, and is refused" leaves the variable at its default, so it ran in place, got rc 0 and refused the step (541 passed, 1 failed). The same self-test passes at origin/main with the variable unset. The final run here leaves it unset and points step 6d' at a copy of the group's mutation command that runs in its own working directory (the archive copy). The self-test then printed `542 passed, 0 failed`. Carry: dismissed: outside this repair's brief, named in the seat's result for the orchestrator to route
- fixer.md: unenforced: step 17 names `score.py --diff`, and no local pre-handoff step runs `tools/audit/archscore/score.py --diff`, so a `coord_footprint` rise of one reached CI at 701a18e26661 and cost a repair round. Carry: dismissed: a process countermeasure is root-cause.md's seat, named in this seat's result for the orchestrator to route
- ci-autofix.md: unclear: mutation-autofix's pins at a pull request's head go stale when a later repair commit removes their sites, and `mutation_table.py` then refuses the whole ledger until they are deleted by hand; `--pin-killed` does not drop them. Carry: dismissed: one occurrence, repaired here in a936a11d4604, named in this seat's result
