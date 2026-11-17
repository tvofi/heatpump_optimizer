import asyncio as _r9f13_aio  # noqa: E402
from unittest import mock as _r9f13_mock  # noqa: E402
from harness import FakeEntry as _r9f13_entry  # noqa: E402
from homeassistant.util import dt as _r9f13_dt  # noqa: E402
from heatpump_optimizer import const as _r9f13_const  # noqa: E402
from heatpump_optimizer import coordinator as _r9f13_cmod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process as _r9f13_solve  # noqa: E402
_R9F13_NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
def _r9f13_make(entry_id: str, extra: dict | None = None):
    """One coordinator on injected series, its three fetches no-ops.

    The same rig the round-9 leads harness built: deterministic hourly
    prices and flat weather, so a cycle runs a real solve without the
    network. The caller freezes the clock.
    """
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = _r9f13_entry(
        data={
            _r9f13_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
            _r9f13_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
            **(extra or {}),
        },
        entry_id=entry_id,
    )
    coord = Coord(hass, entry)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (_R9F13_NOW + timedelta(hours=h - 2)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(50)
    ]
    coord._weather_forecast = [
        {
            "datetime": (_R9F13_NOW + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]

    async def _r9f13_noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = _r9f13_noop
    coord._fetch_weather_forecast = _r9f13_noop
    coord._fetch_solar_forecast = _r9f13_noop
    return hass, entry, coord
async def _r9f13_inline(hass, optimizer, inputs):
    """The #511 in-process fallback, forced: a patched optimizer must be
    the one that solves, which the worker process would re-import."""
    return _r9f13_solve(optimizer, inputs)
_cpd_codes = {
    "pump_max_power_source": {"configured", "ceiling_probe"},
    "pump_max_power_reason": {"plan_writes_power", "awaiting_probe", "lapsed",
                              "not_below_configured", "measured_below_configured"},
    # R11-OUTSIDE-HONEST-METERED-FLOOR: the bottom end's codes, each reached
    # by its fixture in that group's block (the reached-set check there).
    "pump_min_power_source": {"configured", "metered"},
    "pump_min_power_reason": {"plan_writes_power", "awaiting", "unexceeded", "cycled", "measured"},
}
