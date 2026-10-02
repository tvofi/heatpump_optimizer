import sys

sys.path.insert(
    0, "/tmp/claude-0/-home-user/67fb38f0-9f88-5c6b-9d2e-78b6cb07f57d/scratchpad"
)
from _common import S, show, datetime, asyncio, dt_util, FakeHass
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.thermal_model import ThermalParameters

g = LegionellaGuard(
    FakeHass(),
    "dst",
    ThermalParameters.from_config({}),
    {"dhw_temp_entity": "sensor.dhw"},
    action=lambda: {},
    disinfect=DisinfectionSwitch({}, None, None),
    dhw_blocked=lambda: False,
)
g.boost_active = True
g.boost_started = datetime(2026, 10, 25, 2, 50, tzinfo=S)  # 00:50Z
g.last_cycle = datetime(
    2026, 10, 25, 2, 10, tzinfo=S, fold=1
)  # 01:10Z: credited 20 true min AFTER the boost started
g.boost_peak = 60.0


async def run():
    async def noop(*a, **k):
        return None

    g._drive_switch = noop
    await g.async_track_cycle(60.0)


dt_util.freeze(datetime(2026, 10, 25, 2, 20, tzinfo=S, fold=1))
asyncio.run(run())
dt_util.freeze(None)
show(
    "legionella.py:344 credited cycle recognised (no spurious 'attempt' recorded)",
    g.attempt is None,
    True,
)
