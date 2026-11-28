from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.util import dt as dt_util
_T2_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
def _t2_coord(**config):
    """A live coordinator over the fake bus, with config overrides applied."""
    return HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data=dict(_T2_DATA, **config))
    )
from zoneinfo import ZoneInfo as _SiZone  # noqa: E402
_SI_STHLM = _SiZone("Europe/Stockholm")
dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
