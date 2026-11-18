"""D1-s2-54: apply_manual_plan accepts an expires_at beyond the horizon, breaking the
'override shorter than horizon' invariant const.MANUAL_PLAN_WINDOW_HOURS states.

Metric: free (PIN_FREE) steps of the 96-step (24 h x 15 min) space channel, read from the
coordinator's installed override via ManualOverride.channel_pins, at the moment of apply and 23 h
later (just before a daily re-apply), for space_slots=[] and a given expires_at. Count key: the
pins the production override delivers to the solve.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/manual_plan_expiry.py [--clamp]
Expected: expires_at=now+48h -> free_at_apply=0, free_at_23h=0 (the optimizer owns no step for a whole
day); null control (no expires_at, the 20 h default) -> free_at_apply=16, free_at_23h=96.
--clamp (perturbation: expires_at clamped to now + MANUAL_PLAN_WINDOW_HOURS inside the handler) ->
the 48 h arm matches the default arm.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio
from datetime import timedelta
from harness import FakeServiceCall
from homeassistant.config_entries import ConfigEntryState
from homeassistant.util import dt as dt_util
from heatpump_optimizer import services, const
from heatpump_optimizer.manual_plan import PIN_FREE

CLAMP = "--clamp" in sys.argv
_parse = dt_util.parse_datetime


def clamped_parse(v):
    p = _parse(v)
    cap = dt_util.now() + timedelta(hours=const.MANUAL_PLAN_WINDOW_HOURS)
    return min(p, cap) if p is not None else None


def arm(expires):
    _rig.freeze()
    hass, entry, coord = _rig.make_coord()

    async def _noop(*a, **k):
        return None
    coord.async_request_refresh = _noop
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    data = {"space_slots": []}
    if expires is not None:
        data["expires_at"] = (_rig.NOW + timedelta(hours=expires)).isoformat()
    if CLAMP:
        dt_util.parse_datetime = clamped_parse
    try:
        asyncio.run(services.handle_apply_manual_plan(hass, FakeServiceCall("heatpump_optimizer", "apply_manual_plan", data)))
    finally:
        dt_util.parse_datetime = _parse
    ov = coord._manual_override
    out = []
    for offset_h in (0, 23):
        t0 = _rig.NOW + timedelta(hours=offset_h)
        steps = [t0 + timedelta(minutes=15 * i) for i in range(96)]
        pins = ov.channel_pins("space", steps)
        out.append(sum(1 for p in pins if p != p))  # PIN_FREE is NaN
    return out


a48 = arm(48)
a0 = arm(None)
print(f"RESULT free_at_apply_48h={a48[0]} steps_of_96")
print(f"RESULT free_at_23h_48h={a48[1]} steps_of_96")
print(f"RESULT control_default_free_at_apply={a0[0]} steps_of_96")
print(f"RESULT control_default_free_at_23h={a0[1]} steps_of_96")
_rig.tail()
