"""Lead probe (D1-s2, instrument): tests/harness.py:ha_unload_entry calls each async_on_unload
callback and drops a returned coroutine; Home Assistant's ConfigEntry schedules and runs it.

Metric: on a real setup -> unload of one entry, (a) on_unload callbacks whose returned coroutine
the harness drops unawaited, and (b) exceptions raised when those coroutines are run the way Home
Assistant runs them (after async_unload_entry's own explicit coordinator.async_shutdown).
Count key: the callbacks' return values and the exceptions the production coroutines raise.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/unload_coroutines.py
Expected: dropped=1 (the stub DataUpdateCoordinator's async_shutdown registration), raised_when_run=0
(the production shutdown is idempotent), so the divergence hides nothing at this baseline.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio, warnings
from harness import FakeHass, FakeEntry, ha_setup_entry
from homeassistant.config_entries import ConfigEntryState
import heatpump_optimizer as integration
sys.path.insert(0, "tests")



def main():
    _rig.freeze()
    hass = FakeHass()
    now = _rig.NOW.replace(minute=0)
    from harness import FakeState
    from datetime import timedelta
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "end": (now + timedelta(hours=h + 1)).isoformat(), "value": 0.5 + 0.01 * h}
        for h in range(48)]}))
    entry = FakeEntry(data={"price_source": "entity", "price_entity": "sensor.prices", "weather_entity": "weather.home"})
    dropped = raised = 0
    coros = []

    async def go():
        nonlocal dropped, raised
        await ha_setup_entry(integration, hass, entry)
        ok = await integration.async_unload_entry(hass, entry)
        for cb in list(entry._on_unload):
            r = cb()
            if asyncio.iscoroutine(r):
                coros.append(r)
        dropped = len(coros)
        for c in coros:  # what Home Assistant does with them
            try:
                await c
            except Exception:  # noqa: BLE001
                raised += 1
        entry.state = ConfigEntryState.NOT_LOADED
        return ok
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        asyncio.run(go())
    print(f"RESULT dropped={dropped} coroutines")
    print(f"RESULT raised_when_run={raised} of_{dropped}")


main()
_rig.tail()
