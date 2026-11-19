import json as _fi_json  # noqa: E402
from heatpump_optimizer import coordinator as _r9f13_cmod  # noqa: E402
import asyncio as _asyncio
import asyncio
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from unittest import mock as _src_mock  # noqa: E402
_SRC_T0 = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)
_src_clock = [_SRC_T0]
_SRC_SENSORS = {"sensor.indoor": 21.0, "sensor.outdoor": -3.0, "sensor.dhw": 50.0,
                "sensor.power": 1.2, "sensor.buffer": 40.0}
class _SrcHass(FakeHass):
    """Runs what the constructor spawns, so its loads are real tasks."""

    def async_create_task(self, coro, *_a, **_k):
        task = asyncio.ensure_future(coro)
        self._tasks.append(task)
        return task
import heatpump_optimizer as _integ
from harness import (
    ha_setup_component as _ha_setup_component,
    ha_setup_entry as _ha_setup_entry,
    ha_unload_entry as _ha_unload_entry,
)
def _seed_prices(hass, entity_id="sensor.prices", hours=48, base=0.5):
    """A Nord-Pool-style sensor with ``hours`` fresh hourly rows."""
    from datetime import timedelta

    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        entity_id,
        FakeState(
            str(base),
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(base + 0.1 * (h % 4), 3),
                    }
                    for h in range(hours)
                ]
            },
        ),
    )
_LC_DATA = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
}
