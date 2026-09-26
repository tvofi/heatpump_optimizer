"""V3 verify of D1-s2-53: a real Store round trip across a restart, on genuine Home Assistant
2026.2.3 (no tests/hastub) -- the real on-disk .storage files, the real orjson Store, a second
real HeatPumpOptimizerCoordinator built against the same config dir standing in for "restart".

Metric: of the fields set_thermal_parameters can change, count whose effect is absent from a
freshly built coordinator (real Store loads landed) pointed at the same on-disk config/.storage
as the first, after the first coordinator's async_update_thermal_params call changed them.

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-53_realha_runtime_params_restart.py
Expected: lost=24 of 26 changed fields (only dhw_cooling_rate, buffer_cooling_rate persist),
matching the stub's runtime_params_restart.py.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402
import asyncio  # noqa: E402
import tempfile  # noqa: E402
import homeassistant.core as core  # noqa: E402
from harness import FakeEntry  # noqa: E402
from heatpump_optimizer.const import CONF_DHW_COOLING_RATE, CONF_BUFFER_COOLING_RATE  # noqa: E402

CHANGES = {
    "house_thermal_mass": 12345.0, "slab_thermal_mass": 9999.0, "slab_heat_transfer": 321.0,
    "heat_pump_cop_nominal": 4.4, "upper_floor_thermal_mass": 555.0, "lower_floor_thermal_mass": 666.0,
    "inter_zone_heat_transfer": 77.0, "radiator_power_fraction": 0.66, "window_area": 42.0,
    "solar_heat_gain_coefficient": 0.5, "dhw_tank_volume": 250.0, "dhw_setpoint": 52.0,
    "dhw_min_temperature": 44.0, "dhw_daily_consumption": 180.0,
    "ecl110_pid_time_constant_hours": 3.0, "wind_sensitivity_factor": 0.2,
    "rain_heat_loss_multiplier": 1.5,
    CONF_DHW_COOLING_RATE: 0.09, CONF_BUFFER_COOLING_RATE: 0.07,
    "house_heat_loss_coefficient": 250.0,
}


def snapshot(coord):
    ctx = getattr(coord, "_ctx", coord)
    out = {}
    for name in CHANGES:
        if name == CONF_DHW_COOLING_RATE:
            out[name] = coord._dhw_learner.cooling_rate
        elif name == CONF_BUFFER_COOLING_RATE:
            out[name] = coord._buffer_cooling_rate
        else:
            attr = coord._THERMAL_PARAM_FIELDS.get(name, name)
            out[name] = getattr(ctx._thermal_params, attr, None)
    return out


class FixedDirHass(core.HomeAssistant):
    def __new__(cls, d):
        return super().__new__(cls, d)

    def __init__(self, d):
        super().__init__(d)


async def build(d):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = FixedDirHass(d)
    hass.states = core.StateMachine(hass.bus, hass.loop)
    ts = rig.NOW.timestamp()
    hass.states.async_set("sensor.indoor", "21.0", timestamp=ts)
    hass.states.async_set("sensor.outdoor", "-3.0", timestamp=ts)
    entry = FakeEntry(data=rig.base_config())
    return HeatPumpOptimizerCoordinator(hass, entry)


async def main():
    stops = rig.freeze_now()
    try:
        d = tempfile.mkdtemp()
        coord1 = await build(d)
        before = snapshot(coord1)
        await coord1.async_update_thermal_params(dict(CHANGES))
        await asyncio.sleep(0.05)  # let the thermal-learning save land
        after1 = snapshot(coord1)
        changed = [k for k in CHANGES if after1[k] != before[k]]

        await asyncio.sleep(0.3)  # let any startup loads on coord1 finish before "restart"
        coord2 = await build(d)  # same on-disk config dir/.storage: a restart
        await asyncio.sleep(0.3)  # let coord2's startup loads land
        after2 = snapshot(coord2)

        lost = [k for k in changed if after2[k] != after1[k]]
        survived = [k for k in changed if after2[k] == after1[k]]
        print(f"RESULT real_changed_fields={len(changed)} of_{len(CHANGES)}")
        print(f"RESULT real_lost={len(lost)} of_changed")
        print("RESULT real_survived=" + ",".join(survived))
        print("RESULT real_lost_fields=" + ",".join(lost))
    finally:
        for p in stops:
            p.stop()


asyncio.run(main())
rig.tail()
