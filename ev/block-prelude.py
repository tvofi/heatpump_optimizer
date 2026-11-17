import asyncio as _r9f12_aio  # noqa: E402
from harness import FakeEntry as _r9f12_entry  # noqa: E402
from homeassistant.util import dt as _r9f12_dt  # noqa: E402
import heatpump_optimizer as _r9f12_integ  # noqa: E402
_r9f12_seed_cfg = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_daily_consumption": 150.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
}
def _r9f12_seed_prices(hass, now):
    now = now.replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        "sensor.prices",
        FakeState(
            "0.5",
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(0.5 + 0.1 * (h % 4), 3),
                    }
                    for h in range(48)
                ]
            },
        ),
    )
