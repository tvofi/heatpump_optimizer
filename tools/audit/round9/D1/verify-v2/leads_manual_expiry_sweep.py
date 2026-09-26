"""V2 (independent) for D1-s2-54: sweep expires_at through the service handler and count the free
steps of the horizon the SOLVE actually plans over.

Metric: for expires_at offsets {12, 20 (default), 23.75, 24, 30, 48, 168} h, with space_slots=[],
after services.handle_apply_manual_plan installs the override and async_run_optimization solves,
the PIN_FREE (NaN) count of ManualOverride.channel_pins('space', result.timestamps) over the solve's
own timestamps; plus which offsets the handler refuses. Count key: the pins the production override
yields for the steps the production solve plans (not a hand-built 96-step grid).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_manual_expiry_sweep.py
Expected: refused=0 of 7; offsets_with_zero_free=4 of 7 (24, 30, 48, 168 h; exact); 12 h -> 48,
20 h -> 16, 23.75 h -> 1 free of 96 (horizon 24.00 h). Perturbation: --clamp caps the parsed expires_at at now + MANUAL_PLAN_WINDOW_HOURS in the
handler (in memory) -> offsets_with_zero_free=0 (every offset >= 20 h leaves 16 free).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import asyncio
from datetime import timedelta
from harness import FakeServiceCall
from homeassistant.config_entries import ConfigEntryState
from homeassistant.util import dt as dt_util
from heatpump_optimizer import services, const

CLAMP = "--clamp" in sys.argv
OFFSETS = (12, None, 23.75, 24, 30, 48, 168)
_parse = dt_util.parse_datetime


def capped(v):
    p = _parse(v)
    return None if p is None else min(p, dt_util.now() + timedelta(hours=const.MANUAL_PLAN_WINDOW_HOURS))


def cell(offset):
    rig.freeze()
    hass, entry, coord = rig.coordinator()

    async def _noop(*a, **k):
        return None
    coord.async_request_refresh = _noop
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    data = {"space_slots": []}
    if offset is not None:
        data["expires_at"] = (rig.NOW + timedelta(hours=offset)).isoformat()
    if CLAMP:
        dt_util.parse_datetime = capped
    try:
        async def go():
            await services.handle_apply_manual_plan(
                hass, FakeServiceCall(const.DOMAIN, "apply_manual_plan", data))
            await coord._update_current_state()
            await coord.async_run_optimization()
        asyncio.run(go())
    except services.ServiceValidationError:
        return None
    finally:
        dt_util.parse_datetime = _parse
    ts = list(coord._optimization_result.timestamps)
    pins = coord._manual_override.channel_pins("space", ts)
    free = sum(1 for p in pins if p != p)
    return free, len(ts), (ts[-1] - ts[0] + (ts[1] - ts[0])).total_seconds() / 3600.0


refused = zero = 0
for off in OFFSETS:
    r = cell(off)
    tag = "default20" if off is None else f"{off}h"
    if r is None:
        refused += 1
        print(f"RESULT expires_{tag}: refused")
        continue
    free, n, horizon_h = r
    zero += free == 0
    print(f"RESULT expires_{tag}: free={free} of_{n} solve_steps (horizon {horizon_h:.2f} h)")
print(f"RESULT refused={refused} of_{len(OFFSETS)}")
print(f"RESULT offsets_with_zero_free={zero} of_{len(OFFSETS)}")
rig.tail()
