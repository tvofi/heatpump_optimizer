"""D17-v1 verifier's own minimal rig (independent of the finders' rig.py files).

A real coordinator set up through __init__.async_setup_entry on tests/harness
FakeHass, with a deterministic price entity and a frozen clock. Run from the
export root with PYTHONPATH=tests/hastub.
"""
import asyncio
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path[:0] = ["tests", "custom_components"]
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="v5d17_"))

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry, ha_unload_entry  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

T0 = datetime(2026, 2, 3, 6, 0, tzinfo=timezone.utc)  # a Tuesday morning


def freeze(t=T0):
    dt_util.freeze(t)


def prices(base=1.0, hours=48, shape=(0.0, 0.3, -0.2, 0.5)):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    return [{"start": (now + timedelta(hours=h)).isoformat(),
             "value": round(base + shape[h % len(shape)], 3)} for h in range(hours)]


def make_hass(indoor=20.8, outdoor=-5.0, price_base=1.0, extra=None):
    hass = FakeHass()
    tasks = []

    def ct(coro, *a, **k):
        t = asyncio.get_running_loop().create_task(coro)
        tasks.append(t)
        return t
    hass.async_create_task = ct
    hass.async_create_background_task = lambda c, *a, **k: ct(c)
    hass.bus.async_fire = lambda *a, **k: None
    hass._v5tasks = tasks
    hass.states.set("sensor.t_in", FakeState(str(indoor)))
    hass.states.set("sensor.t_out", FakeState(str(outdoor)))
    hass.states.set("sensor.spot", FakeState(str(price_base), attributes={"raw_today": prices(price_base)}))
    for k, v in (extra or {}).items():
        hass.states.set(k, v)
    return hass


def base_data(**kw):
    d = {"price_source": "entity", "price_entity": "sensor.spot",
         const.CONF_INDOOR_TEMP_ENTITY: "sensor.t_in",
         const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.t_out"}
    d.update(kw)
    return d


async def settle(hass, n=20):
    for _ in range(n):
        p = [t for t in hass._v5tasks if not t.done()]
        if not p:
            await asyncio.sleep(0)
            if not [t for t in hass._v5tasks if not t.done()]:
                return
            continue
        await asyncio.gather(*p, return_exceptions=True)


async def setup(data, options=None, hass=None, entry_id="v5"):
    hass = hass or make_hass()
    entry = FakeEntry(data=data, options=options or {}, entry_id=entry_id)
    ok = await ha_setup_entry(integration, hass, entry)
    assert ok
    await settle(hass)
    return hass, entry, entry.runtime_data


async def solve(coord):
    await coord.async_refresh()
    return coord.data


def schedule_kw(data):
    """The published plan's per-step space power (kW) from coord.data."""
    for key in ("schedule", "plan", "power_schedule"):
        v = data.get(key) if isinstance(data, dict) else None
        if v:
            return v
    return None
