"""R10-CEILING-PROBE: the duty and flow set-point the arbiter serves while the
system-identification experiment overrides the action.

At 3b4180dcc a 5.0 kW experiment step returned duty ``None`` (the baseline row,
curve or FLOW_HOLD_C) on every install, so a flow set-point install never
wrote its ceiling. Control: a plan action follows the plan's own duty.

Run from a worktree root:
  PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/ceiling_probe_duty.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace as NS

from custom_components.heatpump_optimizer import pump_arbiter as pa

NOW = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)
PLAN = NS(timestamps=[NOW], power_schedule=[0.0], dhw_power_schedule=[0.0], optimal_setpoints=[20.0])
FLOW = {"space_setpoint_unit": "flow"}


class Coord:
    """Weak-referenceable: the boost table keys on the coordinator."""


def inp(action, config):
    return pa.ArbiterInputs(
        hass=None, config=config, mode="auto", plan=PLAN, plan_stale=False,
        entry_released=False, state=None, thermal=None, params=None, action=action,
        measured_power_kw=None, disinfecting=False,
    )


for label, action, config in (
    ("sysid step 5.0 kW, flow set-point", {"mode": "system_identification", "power": 5.0}, FLOW),
    ("sysid relax 0.0 kW, flow set-point", {"mode": "system_identification", "power": 0.0}, FLOW),
    ("sysid step 5.0 kW, no flow unit", {"mode": "system_identification", "power": 5.0}, {}),
    ("null: plan action 5.0 kW", {"mode": "auto", "power": 5.0}, FLOW),
):
    print(f"{label:38s} -> duty {pa._planned_duty(Coord(), inp(action, config), NOW)!r}"
          f" | plan step_duty {pa.step_duty(PLAN, NOW)!r}")
print("sysid power is an input to _flow_target:", "_sysid_action" in pa._flow_target.__code__.co_names)
