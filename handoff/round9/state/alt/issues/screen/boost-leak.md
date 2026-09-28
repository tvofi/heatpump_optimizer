**Source:** the #1736 shape screen ([SCREEN-1736-SHAPES.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/SCREEN-1736-SHAPES.md)). A read-only screen seat found it, and a probe seat confirmed it with a null control. This is not a judged audit finding. Measured at origin/main `3490cb16` (v6.7.10).

## What

`boost.overlay` (`boost.py:108`) writes boost values **in place** into `coordinator._current_action`, via `boost.apply` from the update cycle (`coordinator.py:4749`). The values are `power`, `setpoint`, `mode`, `displace_value`, `heat_pump_on`, `boost_space`, `dhw_power` and `dhw_heating_active`. Nothing removes them.

The dict is replaced only when a solve succeeds or a fixed mode rebuilds it. A cycle that ends in `no_prices` or `solve_failed` keeps it, and so does a busy cycle. After a boost is cancelled or expires, that kept dict still carries the boost, and the next cycle actuates it. It is the same object as `data["current_action"]` (`coordinator.py:7189`), so every reader of the published action sees it too. By contrast, the sysid path builds a copy (`{**self._current_action, ...}`, `coordinator.py:10629`).

**Probe** (`S1.py`): a real coordinator on `tests/harness.py`'s `FakeHass`, auto mode, a 5 kW plant.
- Cycle 1 has the space boost on and solves.
- The boost is then cancelled the way the switch cancels it.
- Cycle 2 ends as each arm says.

| cycle 2 | action mode | power kW | ECL displace sent | pump switch sent |
|---|---|---|---|---|
| probe: `no_prices` | boost | 5.0 | 20 (max) | turn_on |
| probe: `solve_failed` | boost | 5.0 | 20 (max) | turn_on |
| null: solve succeeds | off | 0.0 | -3 | turn_off |
| null: never boosted, `no_prices` | off | 0.0 | -3 | turn_off |

- **DHW boost:** it leaks the same way. `dhw_power` stays at 4.0 kW and `dhw_heating_active` stays True, where the null arm has 0.0 and False.
- **Price outage, clock stepped 30 min per cycle:** the pump is switched `turn_on` at max displace for 3 cycles (90 min) until the plan-stale gate stops actuation. Mode `boost` stays published indefinitely. The boost switch reads **off** the whole time.

## Blast radius

- **Actuation** at nameplate power and max displace, through the supply switch and the ECL110 MQTT displace, after the user cancelled the boost.
- **Every reader of `current_action`:**
  - recommended power;
  - heat-pump action;
  - climate `hvac_action`;
  - the frequency command;
  - `_pending_prediction` (`coordinator.py:9412-9437`), which books boost energy under the plan's reasons into accuracy and the T6 ledger.
- **It lasts until the next successful solve.** Price outages and solver failures are exactly the cycles that keep the old action.
- **Introduced** by `07bdc557` (#733, the boost switches, 2026-09-10). **First release v6.4.0**, and present through v6.7.10.

**Severity: high.** It is unrequested physical actuation at maximum, and the cancel control reads as off while the pump runs. It needs a boost, then a cancel or expiry, then a cycle that keeps the plan.

## Class

This is a new object in the #1736 class (`N-shared-config` in the v2 register): a long-lived shared object carries an operation's value in place, and a reader sees the wrong meaning. R9-EG-B1's per-solve record does not cover `_current_action`, so this is fixed on its own.

## Root cause owed

It reached released versions, which is trigger 1 of `.claude/rules/defect-root-cause.md`. The fix PR's issue carries a Root cause section. The class-level cause and process state are RCA-1736's; the section owes the instance's own escape and cost.

## Evidence

`S1.py`, `S1.out` and `rig.py` in [the evidence directory](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/evidence/screen). Run from the repo root: `PYTHONPATH=tests/hastub:custom_components:tests:<dir> python3 <dir>/S1.py`.

## Fix shape (R9-EG-B9)

- Keep the last solve's action as its own base value.
- Build the published and actuated action each cycle as `overlay(copy(base))`, as sysid already does, so a cancelled or expired boost disappears on the next cycle whatever the solve outcome.
- Failing test first: the `no_prices` and `solve_failed` arms must send `turn_off` and displace -3, the null arm's result.
- Mutation proof as `fixer.md` requires.
- No golden moves: goldens never boost.

## Disposition

Scheduled: **R9-EG-B9**, after R9-F1.5 (the in-flight F1-lane PR on the cycle), and before R9-EG-B1 (plan principle 3).
