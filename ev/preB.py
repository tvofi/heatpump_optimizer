from types import SimpleNamespace
import asyncio as _asyncio
from harness import FakeEntry, FakeHass
_LC_DATA = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
}
from harness import FakeEntry as _DfEntry  # noqa: E402
_DF_IDS = __import__("itertools").count()
from homeassistant.util import dt as _sa_dt
from heatpump_optimizer import boost as _sa_boost
from heatpump_optimizer import pump_arbiter as _sa_pa
_SA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
