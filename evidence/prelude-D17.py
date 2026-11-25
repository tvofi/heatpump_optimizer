from heatpump_optimizer.const import MODE_AUTO as _MODE_AUTO
import asyncio as _asyncio
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _Coord,
)
from homeassistant.util import dt as dt_util
_METER = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
    "sensor.house_power": FakeState("6500", unit="W"),
    "sensor.hp_power": FakeState("2000", unit="W"),
}
def _t2_coord(states=None, **extra):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **extra,
    }
    return _Coord(_FakeHass(dict(_METER, **(states or {}))), _FakeEntry(data=cfg))
from heatpump_optimizer import pump_schedule as _ps
