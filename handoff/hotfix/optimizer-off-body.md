<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Production hotfix, stacked on the flow set-point hotfix (code head `e2521dec`); merge after it. 🤖 Generated with [Claude Code](https://claude.com/claude-code), https://claude.ai/code/session_011SX4Y1KNfrAnC3e4youhr5

Before: with **Optimizer active** off, a Tuya pump a person had switched on was switched off again at the next update, about every 15 minutes (tvofi's report, 2026-09-26). The ECL110 displace, compressor frequency and circulation pumps were also still written while off.

After: with the optimizer off nothing is written to the pump over Tuya, Modbus or ECL110 (tvofi's rule, 2026-09-26).

**Cause.** The `MODE_OFF` branch of the update cycle builds an action with `heat_pump_on: False`, and `_apply_action` commands the configured power switch from it on every update. The same cycle then published the ECL110 displace and ran `_command_frequency` and `_async_drive_pumps`, none of which looked at the mode. The code dates from the first release, when "off" meant "hold the pump off", not "hand the pump back".

**The change.** Each coordinator writer returns while the mode is off: `_apply_action` (after the pump-duty arbiter, which the flow hotfix already made silent when off), `async_publish_current_action`, `_async_peak_guard_transition`, `_command_valve_target`, `_command_frequency` and `_async_drive_pumps`, and the legionella guard's view of the plan's action is empty while off, so a legionella action still current after the switch to off cannot turn the disinfection switch on. Each guard joins an existing line, so `coordinator_loc` stays at its budget; the circulation-pump guard sits in `_async_set_pump`, the one pump writer, and the two ECL110 methods bind the current action once, so the change lowers two coupling budgets rather than raising any; the legionella view shares one `planned()` closure with the DHW learner's, which keeps `cut_dhw` and `coordinator_loc` flat. Two writes remain while off, by design: the disinfection switch still releases a switch the optimizer itself turned on (left on, the tank would hold anti-legionella temperature indefinitely), and the DHW repair still writes on a person's confirm. Consequences: a boost does not run the pump while the optimizer is off, and the ECL110 keeps the displace last sent.

## Head

`36ad438986cd2644c8decd17d8b0f97bf6136c59` (the code head; the one later commit on this branch only adds this body under `handoff/`) (branch `handoff/optimizer-off-hands-off-07sk6l-b`, which supersedes `handoff/optimizer-off-hands-off-07sk6l` at `a66353e6`; stacked on `e2521dec` of `handoff/flow-setpoint-hotfix-07sk6l`).

## Mutation proof

`coordinator.py` restored to `e2521dec`, `tests/features.py` at this head:

```
PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py
  FAIL with the optimizer off, no writer issues any call: switch, ECL110, valve, frequency, circulation pump  [{'switch.p6_off_supply': [('switch', 'turn_on', ...), ('switch', 'turn_off', ...)], 'input_number.p6_off_valve': [('input_number', 'set_value', ...)], 'number.p6_off_f...
```

With only the ECL110 guards removed (`async_publish_current_action` and `_async_peak_guard_transition` back to `if not (action := self._current_action):`), the same check names the ECL110 publishes:

```
  FAIL with the optimizer off, no writer issues any call: ...  [{'mqtt.ecl110': [('mqtt', 'publish', {'topic': 'ecl/displace/set', 'payload': '2', ...}), ('mqtt', 'publish', ...)]}]
1 of 3384 FEATURE CHECKS FAILED
```

**The disinfection switch** (the compute helper's block on `a66353e6`): with only the legionella `action=` callable back to `lambda: self._current_action or {}`, the new check fails:

```
  FAIL with the optimizer off a legionella action still current never turns the disinfection switch on (null control above: on, it does)  [writes=[('turn_on', 'switch.pump_disinfection')]]
1 of 3386 FEATURE CHECKS FAILED
```

Its null control is the existing `control: the boost-start edge turns the switch ON exactly once across three commanded cycles, and owns it`, the same harness with the optimizer on.

**The reviewer's gap on #1705** (no check drove a heating-plus-hot-water step): `on the real curve a heating-plus-hot-water step writes Heating + DHW and the heating flow` is added here. With `both` dropped from `_flow_target`'s heating arm it fails, writing `('number', 'set_value', 25.0)`; restored, `ALL 3385 FEATURE CHECKS PASSED`.

`tests/mutation_table.py --pin-killed --base e2521dec --scripts tests/features.py`: `PIN KILLED: 4 pinned, 0 left unpinned` at `a66353e6`; at this head `PIN KILLED: nothing to pin` (the legionella callable generates no new site) and `the ledger agrees with the deterministic inventory`. Only this change's sites were driven; the rest is left to CI (tvofi, 2026-09-26).

## Null control

`null control: with the optimizer on, every writer issues a call` drives the same five writers with the optimizer on and requires a call from each, so the off check is not an empty walk.

## Figures

- `ALL 3386 FEATURE CHECKS PASSED`: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py`
- `MODE: SCOPED -- 16 script(s) run, 10 scoped out.`, `18 TEST SCRIPT(S) PASSED`: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` (at `36ad4389`)
- `STRUCTURE RATCHET PASSED` at this head; `cut_grid` 197 to 196 and `cut_views` 110 to 109, re-recorded in `tests/structure_budgets.json` because the ratchet refuses an unrecorded gain; no metric rises: `PYTHONPATH=tests/hastub python3 tests/structure.py`

## Red checks

none

## Forward-carry

none

## Friction

none
