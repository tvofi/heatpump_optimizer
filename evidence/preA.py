from types import SimpleNamespace
import asyncio as _asyncio
from harness import FakeEntry, FakeHass
_LC_DATA = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
}
