import asyncio as _asyncio
from dataclasses import replace
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.util import dt as dt_util
_T5_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
_T5_NOW = datetime(2026, 2, 1, 12, 0, 0, tzinfo=UTC)
def _t5_coord(states=None, **config):
    """A live coordinator over the fake bus, with states and config applied."""
    return HeatPumpOptimizerCoordinator(
        FakeHass(states or {}), FakeEntry(data=dict(_T5_DATA, **config))
    )
def _t5_drive(coord, method, *args, **kwargs):
    """Await one coordinator method and capture anything that escapes it."""
    coord._t5_escaped = None
    try:
        coord._t5_returned = _asyncio.run(getattr(coord, method)(*args, **kwargs))
    except Exception as err:  # noqa: BLE001
        coord._t5_escaped = err
        coord._t5_returned = None
    return coord
_T5_SIM_MIDNIGHT = _T5_NOW.replace(hour=0, minute=0, second=0, microsecond=0)
def _t5_solve_spy(**config):
    """A solvable coordinator that records `min_temp` at the solve itself."""
    c = _t5_coord(**config)
    c._prices = [
        {
            "total": 0.6 + 0.5 * (h % 12) / 12.0,
            "starts_at": (_T5_SIM_MIDNIGHT + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    c._t5_floor_at_solve = []
    inner = c._solve_record

    def spy(*args, **kwargs):
        record = inner(*args, **kwargs)
        c._t5_floor_at_solve.append(record.config.min_temp)
        return record

    c._solve_record = spy
    return c
def _t5_run(c):
    """One solve at the fixed instant."""
    dt_util.freeze(_T5_NOW)
    try:
        return _t5_drive(c, "async_run_optimization")
    finally:
        dt_util.freeze(None)
from zoneinfo import ZoneInfo as _SiZone  # noqa: E402
_SI_STHLM = _SiZone("Europe/Stockholm")
dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
from heatpump_optimizer import rooms as _rm  # noqa: E402
from heatpump_optimizer.const import CONF_ROOM_TEMPERATURE_ENTITIES as _RM_KEY  # noqa: E402
_RM_NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
