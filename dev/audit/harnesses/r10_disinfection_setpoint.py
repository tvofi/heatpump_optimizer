#!/usr/bin/env python3
"""The hot-water set-point the arbiter writes, and the repair it meets (R10-OUTSIDE-DISINFECTION-SETPOINT).

Written by the group's fixer: the feature-triage seat's probe was not
committed. Drives the production ``pump_arbiter.desired`` and
``setpoint_check._dhw`` with the production ``ThermalParameters`` over every
row of ``desired`` (baseline, idle, space, dhw, both) and every way a step
books a cycle (none, the step's ``dhw_reason`` legionella, the disinfection
switch held, both), on a hot-water set-point number of range 30-65 degC,
step 1, no mode entity (so the space row is the hot-water gate). Run it from
a worktree root, at the base and at the head, and diff the two outputs:

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_disinfection_setpoint.py

One line per install, booking and row: ``write=<degC>`` the hot-water write,
then ``repair_own=`` / ``repair_none=`` the repair's Fix value (``-`` when it
stands down) with the pump reading the arbiter's own write, and with the same
reading on an install whose arbiter has written nothing. Installs:
  * ``stock`` -- everyday 55, disinfection 60, cycle enabled: the defect.
  * ``offstep`` -- disinfection 60.3: the rounding of the cycle's target.
  * ``null_disabled`` -- the cycle disabled (null control).
  * ``null_at`` / ``null_above`` -- everyday 60 / 62 (null controls).
  * ``null_noentity`` -- no hot-water set-point entity (null control).
Every ``null_*`` line is byte-identical at the base and the head; a
``stock`` line differing is the fix.

``--grid`` instead prints the census of the write's rounding paths, one
``grid`` line per arm, entity step (0.1, 0.5, 1, 2, 5; range 30-80 degC),
everyday set-point and disinfection temperature (below, at and above each
other, on and off each step, past the 70 degC cap). Arms: ``held`` (cycle
enabled, switch held: the cycle write), ``idle`` (cycle enabled, not running)
and ``disabled`` (cycle disabled, switch held): the everyday write.
``write=`` the dhw row's write; ``hard_max=`` the same parameters'
``dhw_hard_max_temp``, ``over=1`` where the write exceeds it; ``limit=`` the
charge limit ``dhw_max_temp``, ``over_limit=1`` where the write exceeds it;
``below_floor=1`` where the write is under ``dhw_min_temp`` plus
``DHW_MIN_TEMP_SETPOINT_MARGIN`` (no step between the two bounds); ``fix=``
the repair's Fix value with no arbiter write and the pump reading 30
(``-`` when it stands down), ``fix_over=1`` where it exceeds ``hard_max``.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import pump_arbiter as arb  # noqa: E402
from heatpump_optimizer import setpoint_check  # noqa: E402
from heatpump_optimizer.const import DHW_MIN_TEMP_SETPOINT_MARGIN, MODE_AUTO  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

NOW = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)
INSTALLS = {
    "stock": dict(configured=55.0, disinfection=60.0, cycle=True, entity="number.dhw"),
    "offstep": dict(configured=55.0, disinfection=60.3, cycle=True, entity="number.dhw"),
    "null_disabled": dict(configured=55.0, disinfection=60.0, cycle=False, entity="number.dhw"),
    "null_at": dict(configured=60.0, disinfection=60.0, cycle=True, entity="number.dhw"),
    "null_above": dict(configured=62.0, disinfection=60.0, cycle=True, entity="number.dhw"),
    "null_noentity": dict(configured=55.0, disinfection=60.0, cycle=True, entity=None),
}
BOOKINGS = {
    "none": ({}, False),
    "booked": ({"dhw_reason": "legionella"}, False),
    "held": ({}, True),
    "both": ({"dhw_reason": "legionella"}, True),
}
DUTIES = (None, "idle", "space", "dhw", "both")
GRID_STEPS = (0.1, 0.5, 1, 2, 5)
GRID_TEMPS = (50.0, 55.0, 57.0, 58.0, 60.0, 60.2, 60.3, 60.4, 60.7, 62.0, 69.6, 70.0, 72.0)


class _Coord:
    def __init__(self, snap):
        self._snap = snap

    def arbiter_inputs(self):
        return self._snap


def _snap(install, action, disinfecting, reading, attrs=None):
    params = ThermalParameters(
        dhw_setpoint=install["configured"], dhw_legionella_temp=install["disinfection"],
        dhw_legionella_enabled=install["cycle"], dhw_min_temp=40.0,
    )
    entity = install["entity"]
    states = {} if entity is None else {
        entity: FakeState(str(reading), attributes=attrs or {"min": 30, "max": 65, "step": 1}),
    }
    snap = arb.ArbiterInputs(
        hass=FakeHass(states), config={"pump_duty_mode": "control", "dhw_setpoint_entity": entity},
        mode=MODE_AUTO, plan=None, plan_stale=False, entry_released=False,
        state=SimpleNamespace(room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=50.0),
        thermal=None, params=params, action=action, measured_power_kw=None, disinfecting=disinfecting,
    )
    return snap


def _repair(snap, own):
    coord = _Coord(snap)
    if own is not None:
        arb.state_for(coord).written["dhw_setpoint"] = (own, NOW)
    setpoint_check._dhw(snap.hass, snap.config, snap.params, lambda pump: arb.dhw_gated(coord, pump))
    raised = [i for i in getattr(snap.hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW]
    return f"{raised[0][2]['data']['value']:g}" if raised else "-"


GRID_ARMS = {"held": (True, True), "idle": (True, False), "disabled": (False, True)}


def grid() -> int:
    for arm, (cycle, disinfecting) in GRID_ARMS.items():
        for step in GRID_STEPS:
            for everyday in GRID_TEMPS[:-1]:
                for disinfection in GRID_TEMPS:
                    install = dict(configured=everyday, disinfection=disinfection, cycle=cycle, entity="number.dhw")
                    attrs = {"min": 30, "max": 80, "step": step}
                    snap = _snap(install, {}, disinfecting, 0.0, attrs)
                    own = arb.desired(_Coord(snap), snap, "dhw", NOW).dhw_setpoint
                    p = snap.params
                    top, limit = p.dhw_hard_max_temp, p.dhw_max_temp
                    floor = p.dhw_min_temp + DHW_MIN_TEMP_SETPOINT_MARGIN
                    fix = _repair(_snap(install, {}, disinfecting, 30.0, attrs), None)
                    print(f"grid arm={arm} step={step} everyday={everyday} disinfection={disinfection} "
                          f"write={own} hard_max={top} over={int(own is not None and own > top + 1e-9)} "
                          f"limit={limit} over_limit={int(own is not None and own > limit + 1e-9)} "
                          f"below_floor={int(own is not None and own < floor - 1e-9)} "
                          f"fix={fix} fix_over={int(fix != '-' and float(fix) > top + 1e-9)}")
    return 0


def main() -> int:
    if sys.argv[1:] == ["--grid"]:
        return grid()
    for name, install in INSTALLS.items():
        for booking, (action, disinfecting) in BOOKINGS.items():
            for duty in DUTIES:
                snap = _snap(install, action, disinfecting, 0.0)
                own = arb.desired(_Coord(snap), snap, duty, NOW).dhw_setpoint
                reading = 55.0 if own is None else own
                with_own = _snap(install, action, disinfecting, reading)
                without = _snap(install, action, disinfecting, reading)
                print(f"{name} {booking} {duty} write={own} "
                      f"repair_own={_repair(with_own, own)} repair_none={_repair(without, None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
