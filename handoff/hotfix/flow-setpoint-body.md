<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Production hotfix, outside the round-9 wave queue. 🤖 Generated with [Claude Code](https://claude.com/claude-code), https://claude.ai/code/session_011SX4Y1KNfrAnC3e4youhr5

Before: with **Pump duty control** at *Control* and the space set-point declared a *Flow temperature*, the optimizer wrote 25 °C to the pump's water set-point in almost any weather, and the house underheated (tvofi's report, 2026-09-26). Turning **Optimizer active** off still wrote the fallback row once.

After: a step the plan heats writes 55 °C (or the entity's maximum), a step it does not heat writes the gate (the entity's minimum, never below 25 °C), and the fallback while the optimizer is on writes 35 °C or the curve where higher. Turning the optimizer off, or leaving *Control*, writes nothing at all.

**Cause.** `pump_arbiter._space_target` wrote `ThermalModel.curve_flow_temp`, the curve the plan prices COP against. That curve sizes the emitters to the pump's full output at `emitter_design_delta_t` (15 K), so on default parameters it runs 21.8 °C at 15 °C outdoors and 25.0 °C at −10 °C; `FLOW_GATE_C` then floored it to 25 °C. Every arbiter check stubbed the curve at 34.2 °C, so no test ever saw the real one. The flow set-point is now a per-duty lever (`_flow_target`): high on a heating step so the pump's own water thermostat never cuts it short, the gate otherwise, and the W35 rating point as the fallback's hold.

**An indoor-declared entity that cannot hold the room target** (its own minimum above the planned room temperature) is no longer clamped up to that minimum, which wrote the same 25 °C to a flow entity declared indoor; it is not written, and a warning names the unit to set.

**Other write paths.** The mixing valve's `smart_write` with target kind *flow* converts through the same curve (`flow_target_for_indoor`: 25.3 °C at 5 °C outdoors for a 23 °C target on default parameters) and is not changed here. The power switch, ECL110 displace, frequency and valve writes while the optimizer is off are a separate follow-up hotfix. F4.1 (not yet merged) caps `curve_flow_temp` at 75 °C; the fallback here already clamps the curve to 35–55 °C, so the two are independent in either merge order.

## Head

`e2521decae02e9bb27e6a8237790d8ca98adca62` (the code head; the one later commit on this branch only adds this body under `handoff/`) (branch `handoff/flow-setpoint-hotfix-07sk6l`, cut from `origin/main` at `cbb8a271`).

## Mutation proof

Production edits reverted to `origin/main`'s `pump_arbiter.py` (with the two new constants added so the checks import), `tests/features.py` turns the new and updated checks red:

```
PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py
  FAIL on the real curve a space-heating step writes the heating flow, not the 25 degC floor  [... ('number', 'set_value', 25.0)]
  FAIL on the real curve the baseline holds the rated 35 degC flow, not the 25 degC floor  [... ('number', 'set_value', 25.0)]
  FAIL an indoor-declared entity that cannot hold the room target (min 25) is not written  [... ('number', 'set_value', 25.0)]
  FAIL an idle step writes no mode, and a flow set-point drops to the gate  [[]]
17 of 3379 FEATURE CHECKS FAILED
```

`tests/mutation_table.py --pin-killed --base origin/main`: every new candidate site in `pump_arbiter.py` killed by `tests/features.py` and pinned in `tests/mutation_ledger/killed_by/pump_arbiter.py/`. Across three runs 9, 3 and 1 sites were pinned (the first left 3 survivors, killed by two added checks and pinned by the second); 0 are left unpinned, and the last run printed `the ledger agrees with the deterministic inventory` and `PIN KILLED: 1 pinned, 0 left unpinned`. The seven retired rows each named a line this diff rewrote. Only this change's sites were driven; the rest is left to CI (tvofi, 2026-09-26).

## Null control

`null control: the model's real curve at 5 degC outdoors is below the 25 degC flow floor` passes on `origin/main` and here: the real curve at 5 °C is 23.1 °C, so the 25 °C write is the floor, not the curve. `unloading with the optimizer off writes nothing; null control: with it on, the baseline` pins the other side of the off rule. The mutation run's `NULL_COMMENT` at `pump_arbiter.py:148` survived every driver.

## Figures

- curve 21.8 / 22.4 / 23.1 / 23.7 / 24.3 / 25.0 / 26.3 °C at 15 / 10 / 5 / 0 / −5 / −10 / −20 °C outdoors: `PYTHONPATH=tests/hastub:custom_components:tests python3 -c "import harness; from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters; m=ThermalModel(ThermalParameters()); print([round(m.curve_flow_temp(o),1) for o in (15,10,5,0,-5,-10,-20)])"`
- valve flow 25.3 °C at 5 °C outdoors: `PYTHONPATH=tests/hastub:custom_components:tests python3 -c "import harness; from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters; print(round(ThermalModel(ThermalParameters()).flow_target_for_indoor(23.0, 5.0), 1))"`
- `ALL 3382 FEATURE CHECKS PASSED`: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py`
- `MODE: SCOPED -- 16 script(s) run, 10 scoped out.`, `18 TEST SCRIPT(S) PASSED`: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` (at 34339ad4; `stress.py`, `optimality.py`, `validate.py`, `open_meteo.py` scoped out, left to CI)

## Red checks

none

## Forward-carry

none

## Friction

none
