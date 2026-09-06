"""Pump set-point consistency detector — stub; raise/clear lands in the fix.

#408. Witnesses in tests/features.py import ``evaluate`` and the issue ids.
"""
from __future__ import annotations

from typing import Any

from .const import (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_UNIT,
    DEFAULT_SPACE_SETPOINT_UNIT,
    MIXING_VALVE_WRITE_EPSILON,
    SPACE_SETPOINT_UNITS,
)

ISSUE_DHW = "dhw_setpoint_below_disinfection"
ISSUE_SPACE = "space_setpoint_unreadable"

# Names the real detector reads. Referenced here so the stub is not a
# pocket of dead CONF_ keys while the failing witnesses run.
_CONF = (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_UNIT,
    DEFAULT_SPACE_SETPOINT_UNIT,
    SPACE_SETPOINT_UNITS,
    MIXING_VALVE_WRITE_EPSILON,
)


def evaluate(coord: Any) -> None:
    """Read optional set-point entities and raise or clear the two issues.

    Stub: the failing witnesses pin the raise/clear contract before the
    detector exists.
    """
    _ = _CONF, coord
    return
