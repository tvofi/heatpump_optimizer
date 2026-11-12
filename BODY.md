Thank you, Bankaifan, for pull request 3456: the supply switch's minimum run and minimum pause are your design, and your production and test commit is the first commit here, authored by you. Our changes are later commits on top of it. Part of #201.

`_write_supply`, the one gate the cycle and the step tick write the supply switch through, enforced no minimum run and no minimum pause, so a re-solve or a cycle landing inside a step could stop a compressor minutes after the switch started it, or start it minutes after the switch stopped it. `supply_hold.py` now owns that rule, placed in `_write_supply` after `early_cutoff.allow_on` and `supply_write`. It only delays a write and never makes one. A write of `None`, a fixed mode, a live boost, system identification and an unreadable switch pass through unchanged. The step tick retries a held write with the step's own command, or with the action's command where the plan gives none. The two minimums are constants, `supply_hold.MIN_RUN` and `MIN_PAUSE`, and the early cut-off reads the same pair.

Changes on the contributor's commit, keyed to the brief:

- (a) One clock. A run's and a pause's age is the switch's own state and `last_changed`, the clock `early_cutoff._cycle_guard` already uses. The private `_Hold` record, its birth time and `ArbiterState.hold` are gone. `ArbiterState` keeps the held flag (`supply_held`) and gains `held_until`, the deadline the learners' freeze reads. A restart of Home Assistant builds a new state machine, and its first write stamps `last_changed` at the restart. The real-HA contract `homeassistant.core.StateMachine` in `tests/ha_contract.py` pins this, so a pump found running after a restart is held on for at most MIN_RUN. A reload of the integration does not touch the stamp, so an hour-old run is switched off at once.
- (b) `pump_arbiter.supply_tick` retries a held write that `step_supply` gives no command for (an empty plan) with the action's own value (`_action_supply`). It drops the write where the cycle itself would write nothing: a mode left, a stale plan or no action. System identification passes the gate unchanged.
- (c) Learners. The flow lift and the measured-COP denominator replay *commanded* power for an interval (`coordinator._commanded_power`), so a held interval would be read wrong. It is frozen through the existing reason path: `_tail_freeze` returns `supply_hold.freeze_reason`'s `FREEZE_HELD` until `ArbiterState.held_until`, which `hold_supply` sets two plan intervals past the held write, as `early_cutoff.CutoffState.interval_cut` counts two cycles. No new seam, so this stays size M.
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

a936a11d461cdf08ef8b9e098c3da27cecf9e249, measured against merge base 43e95474559ca8e2188830f8775c1ddf52df964a; origin/main was 870238eb2194c99ae1ad6f1f78e0665e838c70f3 at 2026-11-12T18:58Z, and `git merge-tree --write-tree origin/main HEAD` exits 0 there, so that tip is not merged. It is the reviewed handoff head 701a18e26661 plus a repair for the conflict `update_pr.sh` stopped on:

- 62a0d672ff, the merge of origin/main 8c10361eb1. Six files conflicted: `tests/features.py`, `tests/deployment_shape.py`, `docs/architecture.md` and the three `dev/audit/rounds/round4/D6/claims.*` files. Every resolved hunk is a module count, a module list or a fixture this pull request already changed. `git diff 701a18e26661 62a0d672ff` removes no line of this branch from those files, and the lines of main it replaces are the counts (88 -> 89 modules and the like) and the `_sa_install` and `_sa_guarded` stamps described above.
- 874cb01682 and 808f50df7f. At the bare merge `python3 tools/audit/archscore/score.py --diff 8c10361eb1` printed `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2492->2493)`. The payment: `supply_hold.freeze_reason` replaces `interval_held`, and `hold_supply` fixes the freeze deadline (`ArbiterState.held_until`, two plan intervals) from the config it already holds, so `_tail_freeze` parses no config per learner query. `class_excess_loc` is re-recorded one lower.
- 4662745d2f, the merge of mutation-autofix's pin commit b2dd262882 from the pull request's branch.
- 934f6d683e, the merge of origin/main 43e95474559c, which brings #3461 (`duty_switch.py`). The same count and list lines conflicted and now read 90 modules, 32 importing `homeassistant`, with both `supply_hold` and `duty_switch` named. No production file conflicted in either merge.
- a936a11d46 drops the five ledger pins whose sites 874cb01682 removed (`mutation_table.py` refuses a pin naming no generated site).

The commits above were pushed to the step ref by an earlier container of this seat, which stopped before its handoff. This container resumed from that ref and added no commit. Every figure below was re-taken at this head unless it says otherwise.

## Mutation proof

Every predicate the fix adds or moves, mutated by hand one at a time at this head and run against the group's mutation command. That command runs two `features_block.py` blocks: from the section "supply switch at step boundaries (#2492, R10-SAV-ACTUATION)" to the ceiling probe's section (147 checks, which now include #3461's duty-switch sections), and the early cut-off's section (60 checks).

```
KILLED   1 supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(_ends_soon(inp, boosts, now)) if value' | rc 1 | FAIL a re-solve three minutes into a pause does not switch the supply on; the step tick does at MIN_PAUSE  [
KILLED   2 supply_hold.py: '(age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value' -> '(age < MIN_PAUSE) if value' | rc 1 | FAIL a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)  [phase 0: ['delivered', 'd
KILLED   3 supply_hold.py: 'if value else age < MIN_RUN' -> 'if value else False' | rc 1 | FAIL a re-solve three minutes into a run does not switch the supply off; the step tick does at MIN_RUN  [[(0, 'turn_on'), (3, 'tur
KILLED   4 supply_hold.py: 'if value else age < MIN_RUN' -> 'if value else age <= MIN_RUN' | rc 1 | FAIL a re-solve three minutes into a run does not switch the supply off; the step tick does at MIN_RUN  [[(0, 'turn_on'), (11, 'tu
KILLED   5 supply_hold.py: '(age < MIN_PAUSE or' -> '(age <= MIN_PAUSE or' | rc 1 | FAIL a re-solve three minutes into a pause does not switch the supply on; the step tick does at MIN_PAUSE  [[(0, 'turn_on'), (12,
KILLED   6 supply_hold.py: '            or (inp.action or {}).get("mode") == "system_i' -> '' | rc 1 | FAIL system identification: an OFF three minutes into a run is written at once  [[(7, 'turn_off')]]
KILLED   7 supply_hold.py: '(state != "off") is value' -> '(state == "on") is value' | rc 1 | FAIL a climate target reading heat three minutes is held on until MIN_RUN  [[(0, 'turn_off')]]
KILLED   8 supply_hold.py: 'if state in _UNREADABLE or (state' -> 'if (state' | rc 1 | FAIL stop: an OFF to a switch reading unavailable passes -> (False, False)  [(None, True)]
KILLED   9 supply_hold.py: 'return None if since > now else now - since' -> 'return now - since' | rc 1 | FAIL stop: an OFF to a switch stamped ahead of the clock passes -> (False, False)  [(None, True)]
KILLED   10 supply_hold.py: 'return None if since > now else now - since' -> 'return None if since >= now else now - s' | rc 1 | FAIL after a Home Assistant restart a supply found on is held for MIN_RUN of its restart stamp, then switched off  [[(0,
KILLED   11 supply_hold.py: 'return not (step_duty(inp.plan, now) in ("dhw", "both") an' -> 'return True' | rc 1 | FAIL rule three: a hot-water step with the tank below its minimum -> (True, False)  [(None, True)]
KILLED   12 supply_hold.py: 'if nxt - now >= MIN_RUN or' -> 'if nxt - now > MIN_RUN or' | rc 1 | FAIL rule three: null control: the same ON at minute 5, MIN_RUN before the boundary -> (True, False)  [(None, True)]
KILLED   13 supply_hold.py: '    if inp.disinfecting:\n        return "disinfecting"\n' -> '' | rc 1 | FAIL rule three: a hot-water step under a disinfection hold -> (True, False)  [(None, True)]
KILLED   14 supply_hold.py: 'held.supply_held, held.held_until = True, now + _freeze_sp' -> 'held.supply_held = True' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   15 supply_hold.py: 'until is not None and dt_util' -> 'dt_util' | rc 1 | TypeError: '<' not supported between instances of 'datetime.datetime' and 'NoneType'
KILLED   16 supply_hold.py: 'dt_util.now()) < until' -> 'dt_util.now()) > until' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   17 supply_hold.py: 'dt_util.now()) < until' -> 'dt_util.now()) <= until' | rc 1 | FAIL freeze_reason: null control: 60 minutes ago is not  ['supply_held']
KILLED   18 supply_hold.py: 'return 2 * timedelta(minutes=EntryConfig' -> 'return 1 * timedelta(minutes=EntryConfig' | rc 1 | FAIL freeze_reason: a write held 59 minutes ago on a 30-minute interval is frozen  [None]
KILLED   19 supply_hold.py: 'return FREEZE_HELD if held_now else None' -> 'return None' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   20 supply_hold.py: '    if value is None:\n        return value\n' -> '    if False:\n        return value\n' | rc 1 | FAIL a write of None passes and marks nothing held  [(None, True, datetime.datetime(2026, 1, 10, 7, 7, tzinfo=datetime.tim
KILLED   21 supply_hold.py: 'return (inp.mode not in (MODE_AUTO, MODE_ECONOMY)\n' -> 'return (False\n' | rc 1 | FAIL which writes are held: a fixed mode (comfort) passes an OFF three minutes into a run -> (False, False)  [(None, True)]
KILLED   22 supply_hold.py: 'return (inp.mode not in (MODE_AUTO, MODE_ECONOMY)\n' -> 'return (inp.mode != MODE_AUTO\n' | rc 1 | FAIL which writes are held: economy is a plan mode: an OFF three minutes into a run is held -> (None, True)  [(False, Fals
KILLED   23 supply_hold.py: 'or boosts.active(CHANNEL_SPACE, now) or boosts.active(CHAN' -> 'or boosts.active(CHANNEL_DHW, now))' | rc 1 | FAIL which writes are held: a live space boost passes an ON three minutes into a pause -> (True, False)  [(None
KILLED   24 supply_hold.py: 'or boosts.active(CHANNEL_SPACE, now) or boosts.active(CHAN' -> 'or boosts.active(CHANNEL_SPACE, now))' | rc 1 | FAIL which writes are held: a live DHW boost passes an ON three minutes into a pause -> (True, False)  [(None
KILLED   25 supply_hold.py: 'in ("dhw", "both") and tank_reason' -> '== "dhw" and tank_reason' | rc 1 | FAIL which writes are held: rule three: a both step with the tank below its minimum is exempt -> (True, False, 'both')  [(None, Tr
KILLED   26 supply_hold.py: 'getattr(params, "dhw_enabled", False)' -> 'getattr(params, "dhw_enabled", True)' | rc 1 | FAIL rule three: a cold tank on params with no dhw_enabled field is not exempt -> (None, True)  [(True, False)]
KILLED   27 pump_arbiter.py: 'on = _action_supply(inp)  # a held write' -> 'pass  # a held write' | rc 1 | FAIL with no plan, an OFF held three minutes into a run lands at MIN_RUN  [[]]
KILLED   28 pump_arbiter.py: '(held.supply[0] == step and not held.supply_held)' -> '(held.supply[0] == step)' | rc 1 | FAIL a re-solve three minutes into a run does not switch the supply off; the step tick does at MIN_RUN  [[(0, 'turn_on')]]
KILLED   29 pump_arbiter.py: 'held.supply_held = False  # a held write dies' -> 'held.supply_held = True  # a held write ' | rc 1 | FAIL step tick, held write: the optimizer switched off: no write, the hold dropped  [([], True)]
KILLED   30 pump_arbiter.py: 'if on is None and held.supply_held and not inp.entry_relea' -> 'if on is None and held.supply_held:' | rc 1 | FAIL step tick, held write: the entry released: no write, the hold dropped  [([False], True)]
KILLED   31 pump_arbiter.py: 'return bool(inp.action.get("heat_pump_on"))' -> 'return True' | rc 1 | FAIL with no plan, an OFF held three minutes into a run lands at MIN_RUN  [[(1, 'turn_on')]]
KILLED   32 pump_arbiter.py: '(MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or not inp.act' -> '(MODE_AUTO, MODE_ECONOMY) or not inp.act' | rc 1 | FAIL step tick, held write: a stale plan: no write, the hold dropped  [([False], True)]
KILLED   33 pump_arbiter.py: 'heat_pump_switch_entity\n    return inp.hass.states.get(entity) if entity else None' -> '...get(entity)' | rc 1 | FAIL an install with no power switch: the gate writes and holds nothing, and raises nothing  [AttributeError("'NoneType' object has no attribute 'lowe
KILLED   34 pump_arbiter.py: 'if on != last or held.supply_held:' -> 'if on != last:' | rc 1 | FAIL a re-solve three minutes into a run does not switch the supply off; the step tick does at MIN_RUN  [[(0, 'turn_on')]]
KILLED   35 coordinator.py: 'return supply_hold.freeze_reason(pump_arbiter.state_for(co' -> 'return learner_unmetered(' | rc 1 | FAIL an interval in which the gate held a write freezes the learners with the supply_held reason  [None]
KILLED   36 coordinator.py: 'elif switch_entity and not held.supply_held:' -> 'elif switch_entity:' | rc 1 | FAIL a held OFF is not logged as the cooling or blocked-mode skip  [["Not switching switch.hp off: mode Unknown is cooling or bloc
KILLED   37 early_cutoff.py: 'return tank_reason(inp)' -> 'return None' | rc 1 | FAIL a tank below its minimum exempts the step
KILLED   38 early_cutoff.py: 'if run is None or run < MIN_ON:' -> 'if run < MIN_ON:' | rc 1 | TypeError: '<' not supported between instances of 'NoneType' and 'datetime.timedelta'
KILLED   39 supply_hold.py: 'if nxt - now >= MIN_RUN or' -> 'if nxt - now >= MIN_RUN - timedelta(minutes=1) or' | rc 1 | FAIL which writes are held: rule three: an ON at minute 6, one tick inside MIN_RUN of an OFF step, is skipped -> (None, True)
KILLED   40 pump_arbiter.py: 'if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_s' -> 'if inp.mode != MODE_AUTO or inp.plan_stale or not inp.action:' | rc 1 | FAIL step tick, held write: economy with no plan retries the action's OFF  [([], False)]
40 of 40 killed
```

Command: `python3 mut.py <worktree> mutant_cmd.sh`, a one-off scratch driver holding the replacements printed above; it first requires the unmutated tree to pass (`BASELINE rc 0`). Mutants 15 and 38 die on a `TypeError`, the rest on the named check. Mutant 33 was run singly, because its text occurs twice in the file. Mutants 14 to 19 and 35 are the `freeze_reason` change's.

Review round 1 returned `blocked: mutation-vacuous` on ten surviving mutants of added or moved lines. They are 21 to 25, 30, 32, 33, 39 and 40 above, all killed at this head. The tenth, `supply_switch`'s `if entity else None` (33), is equivalent under `FakeStates`, whose `get(None)` is `None`; upstream `StateMachine.get(None)` raises, which the contract "StateMachine.get(None) raises" in `tests/ha_contract.py` pins (`expect="real"`), and the no-switch install drives `_write_supply` through a states double that reads as upstream does.

Red without the fix: each change of the contributor's design named in the lead (one clock, the empty-plan retry, system identification, the climate target, the learners' freeze, rule three's tank exemption, the unreadable and future-stamped switch) has a mutant above that reverts it.

## Null control

- **Every write on a step boundary, no restart, gate on against gate off (main's write).** The service calls and their order are identical in all three cases: writes on step boundaries, a plan the step tick moves, and no supply switch (`tests/features.py` "null control: ..., the gate issues main's service calls in main's order"). The perturbation is a re-solve inside a step (`_ms_short`), which the gate holds.
- **The early cut-off's own checks pass unchanged.** Its `features_block.py` block's output at the head is byte-identical to the merge base's: `diff ec_base.txt ec_head.txt && echo IDENTICAL` printed IDENTICAL, 60 checks, re-run at this head against merge base 43e95474559c.
- **Closed loop, cycles on step boundaries (`CYCLE_PHASE_MIN=0`).** The gate holds nothing, and gate on equals gate off on every line, for NULL, HOT and LIGHT on both prices.
- **Closed loop, default mode.** Output is byte-identical before and after the harness extension (`diff before.txt after.txt && echo IDENTICAL`, NULL variant).
- **Every quantified closed-loop figure has its flat-price twin** in the table below.
- **A restart.** The `homeassistant.core.StateMachine` contract passes against real Home Assistant 2026.11.0. Under the stub it is reported "still divergent", as an `expect="real"` contract must be. The perturbation that would fail it is a write carrying the restored stamp (`async_set(..., timestamp=restored)`).

## Figures

- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) bash tests/run.sh` exits 0 at the head and prints `26 TEST SCRIPT(S) PASSED; 8 SCOPED OUT AND NOT RUN`; its mode line is in the figure block below.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2709 ENTITY CHECKS PASSED`, exit 0, at the head.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head, and at the bare merge 62a0d672ff too, so the payment above answers the architecture score and not the ratchet.
- `python3 tools/audit/archscore/score.py --diff 43e95474559ca8e2188830f8775c1ddf52df964a`: `Architecture score: dS +0.0000 NULL` at the head. The control is the bare merge's `WORSENS` line under `## Head`.
- `PYTHONPATH=tests/hastub python3 tests/ha_contract.py` and `/opt/hpo/venv-ha/bin/python tests/ha_contract.py --contracts-only` (Home Assistant 2026.11.0): both exit 0 with no FAIL line. "StateMachine.get(None) raises" and "a restart's first write stamps last_changed anew" read `ok` against real Home Assistant and "still divergent under the stub" under `tests/hastub`.
- Closed loop, phase 7: `SUPPLY_HOLD=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/early_cutoff_closed_loop.py NULL HOT LIGHT`. sha1 of the harness at the head: 39a4867b2afda697d041add836d69a9fd3e37401. Re-run at this head: the phase-7 and phase-0 tables are byte-identical to those measured at 701a18e26661 (`diff old7.txt n7.txt && echo PHASE7-IDENTICAL` printed PHASE7-IDENTICAL, and the same for phase 0).
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

<!-- figure-block: scope-line mb=43e95474559ca8e2188830f8775c1ddf52df964a head=a936a11d461cdf08ef8b9e098c3da27cecf9e249 -->
~~~text
MODE: SCOPED -- 24 script(s) run, 9 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

Each site is in `freeze_reason` or `_freeze_span`, is killed by the group's mutation command (mutants 15 to 19 under `## Mutation proof`; `prepr.sh` step 6d' drew no survivor at the head) and is pinned by `mutation-autofix` after the push.

- `custom_components/heatpump_optimizer/supply_hold.py:94 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/supply_hold.py:94 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/supply_hold.py:95 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/supply_hold.py:103 RETURN_DEL`: pinned by mutation-autofix

## Red checks

- `tests / mutation` at 701a18e26661: red by construction on the site(s) under `## Unpinned sites`; mutation-autofix pinned the killed ones in b2dd262882, merged here. No cheaper detector is owed: `prepr.sh` step 6d' already drives these sites locally with the group's mutation command.
- `arch-score / arch-score`: red on the pull request once main moved under the handoff head. Measured here at the bare merge 62a0d672ff: `python3 tools/audit/archscore/score.py --diff 8c10361eb1` printed `dS -0.0006 WORSENS (inadmissible: coord_footprint 2492->2493)`; 874cb01682 pays it and the head reads `dS +0.0000 NULL` against its merge base. No cheaper detector exists: the score is a function of main's tip, the same command was run before the handoff against the base of that time, and it takes seconds wherever it runs.

## Forward-carry

none

## Friction

- prepr.sh: unclear: `MUTANT_IN_PLACE=1`, which `fixer.md` step 2 prescribes for a checkout, leaks from the caller into `prepr.sh --self-test`, whose assertion "a check needing a git checkout measures nothing in the archive copy, and is refused" then runs in place and fails. The run here leaves the variable unset. Carry: dismissed: outside this repair's brief, named in the seat's result for the orchestrator to route
