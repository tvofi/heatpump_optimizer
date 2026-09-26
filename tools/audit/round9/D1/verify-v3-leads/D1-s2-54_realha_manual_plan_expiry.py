"""V3 verify of D1-s2-54: drive the REAL services.handle_apply_manual_plan through a REAL
HeatPumpOptimizerCoordinator on genuine Home Assistant 2026.2.3 (no tests/hastub).

Metric: PIN_FREE steps (of 96, the 24h x 15min space channel) in the installed override's
channel_pins at apply time and 23h later, for expires_at = now+48h vs the default (no
expires_at, MANUAL_PLAN_WINDOW_HOURS).

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-54_realha_manual_plan_expiry.py
Expected: 48h arm -- free_at_apply=0, free_at_23h=0; default arm -- free_at_apply=16,
free_at_23h=96 -- matching the stub's manual_plan_expiry.py.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402
import asyncio  # noqa: E402
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from heatpump_optimizer import services  # noqa: E402


class FakeServiceCall:
    def __init__(self, domain, service, data):
        self.domain = domain
        self.service = service
        self.data = data


async def arm(expires):
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator()
        from homeassistant.config_entries import ConfigEntryState
        coord.entry.state = ConfigEntryState.LOADED
        coord.entry.runtime_data = coord

        async def _noop(*a, **k):
            return None
        coord.async_request_refresh = _noop

        # Real HomeAssistant() leaves .config_entries None until the bootstrap
        # sequence sets it up; the service handler only needs
        # async_entries()/async_get_entry(), so those two are given directly
        # rather than running the full config-entries bootstrap.
        coord.hass.config_entries = SimpleNamespace(
            async_entries=lambda domain: [coord.entry],
            async_get_entry=lambda eid: coord.entry if eid == coord.entry.entry_id else None,
        )

        data = {"space_slots": []}
        if expires is not None:
            data["expires_at"] = (rig.NOW + timedelta(hours=expires)).isoformat()

        await services.handle_apply_manual_plan(
            coord.hass, FakeServiceCall("heatpump_optimizer", "apply_manual_plan", data)
        )
        ov = coord._manual_override
        out = []
        for offset_h in (0, 23):
            t0 = rig.NOW + timedelta(hours=offset_h)
            steps = [t0 + timedelta(minutes=15 * i) for i in range(96)]
            pins = ov.channel_pins("space", steps)
            out.append(sum(1 for p in pins if p != p))  # PIN_FREE is NaN
        return out
    finally:
        for p in stops:
            p.stop()


async def main():
    a48 = await arm(48)
    a0 = await arm(None)
    print(f"RESULT real_free_at_apply_48h={a48[0]} steps_of_96")
    print(f"RESULT real_free_at_23h_48h={a48[1]} steps_of_96")
    print(f"RESULT real_control_default_free_at_apply={a0[0]} steps_of_96")
    print(f"RESULT real_control_default_free_at_23h={a0[1]} steps_of_96")


asyncio.run(main())
rig.tail()
