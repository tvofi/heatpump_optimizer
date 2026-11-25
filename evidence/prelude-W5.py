import asyncio as _asyncio
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
_T1_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
from heatpump_optimizer import button as _rc2_button  # noqa: E402
from homeassistant.util import dt as _rc2_dt_util  # noqa: E402
class _RC2Hass(FakeHass):
    """Upstream's background task: a real task, left pending here."""

    def async_create_task(self, coro):
        return _asyncio.get_running_loop().create_task(coro)
async def _rc2_boot(entry):
    coord = HeatPumpOptimizerCoordinator(FakeHass(), entry)
    coord.hass.config_entries.entries.append(entry)
    await coord._async_load_accuracy()
    await coord._async_load_thermal_learning()
    await boost_mod.restore_session(
        coord, coord._adopt_away_override, coord._config, coord._entity_state
    )
    await coord._async_load_manual_plan()
    return coord
