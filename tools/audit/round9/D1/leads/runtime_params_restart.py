"""D1-s2-53: set_thermal_parameters changes are silently lost at the next restart.

Metric: of the set_thermal_parameters fields whose call changes coordinator state (non-empty
footprint), count those whose footprint does not survive a restart. Footprint of a field = the
simple-typed attributes of coord._thermal_params, coord._opt_config and the coordinator itself
that HeatPumpOptimizerCoordinator.async_update_thermal_params changed when called with that field
alone. Survival = after a restart on the same entry and the same store disk, with every startup
load landed, each footprint attribute holds the value the call set. Count key: the restarted
coordinator's own attributes.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/runtime_params_restart.py [--persist]
Expected: lost=24 of 26 changed fields (exact; dhw_cooling_rate and buffer_cooling_rate survive
through the thermal-learning store; radiator_power_fraction and dhw_windows leave no simple-typed
footprint on this single-zone rig). --persist (perturbation: the call's fields are also written
into entry.options, the fix's shape) -> lost=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio
from harness import FakeHass, FakeEntry
from homeassistant.helpers import storage
from heatpump_optimizer import const

PERSIST = "--persist" in sys.argv
VALUES = {
    "house_thermal_mass": 12.0, "house_heat_loss_coefficient": 0.2, "slab_thermal_mass": 9.0,
    "slab_heat_transfer": 1.7, "heat_pump_cop_nominal": 3.7, "upper_floor_thermal_mass": 6.0,
    "lower_floor_thermal_mass": 7.0, "inter_zone_heat_transfer": 0.9, "radiator_power_fraction": 0.4,
    "window_area": 11.0, "solar_heat_gain_coefficient": 0.35, "dhw_tank_volume": 150.0,
    "dhw_setpoint": 52.0, "dhw_min_temperature": 42.0, "dhw_daily_consumption": 7.0,
    "dhw_cooling_rate": 0.7, "buffer_cooling_rate": 1.1, "dhw_schedule_enabled": False,
    "dhw_windows": "06:00-07:00", "dhw_idle_min_temperature": 38.0, "dhw_legionella_enabled": False,
    "dhw_legionella_temperature": 62.0, "dhw_legionella_interval_days": 10,
    "wind_sensitivity_factor": 0.05, "rain_heat_loss_multiplier": 1.2,
    "ecl110_pid_time_constant_hours": 0.6, "ecl110_displace_min": -3.0, "ecl110_displace_max": 5.0,
}


class LoopHass(FakeHass):
    def async_create_task(self, coro):
        return asyncio.Task(coro, loop=asyncio.get_running_loop(), eager_start=True)


def snap(c):
    out = {}
    for tag, obj in (("tp", c._thermal_params), ("oc", c._opt_config), ("co", c)):
        for k, v in vars(obj).items():
            if isinstance(v, (int, float, str, bool)) and not k.startswith("_store") and k != "_last_update_success_time":
                out[(tag, k)] = v
    return out


async def boot(options):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = LoopHass()
    hass.states.set("sensor.indoor", _rig.FakeState("21.0"))
    hass.states.set("sensor.outdoor", _rig.FakeState("-3.0"))
    cfg = _rig.base_config(**{const.CONF_DHW_TANK_VOLUME: 180.0})
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, options=dict(options)))
    _rig.no_fetch(c)
    _rig.inject_series(c)

    async def _no_refresh(*a, **k):  # the call's follow-up re-solve is not what is measured
        return None
    c.async_request_refresh = _no_refresh
    await asyncio.sleep(0.05)
    for t in list(c._background_tasks):
        await t
    return c


async def one(field, value):
    storage._reset_store_disk()
    a = await boot({})
    s0 = snap(a)
    await a.async_update_thermal_params({field: value})
    for t in list(a._background_tasks):
        await t
    s1 = snap(a)
    foot = [k for k in s1 if s0.get(k) != s1[k]]
    if not foot:
        return None
    opts = {field: value} if PERSIST else {}
    b = await boot(opts)
    s2 = snap(b)
    return all(s2.get(k) == s1[k] for k in foot), foot


def main():
    _rig.freeze()
    changed = lost = 0
    lost_names, kept_names = [], []
    for f, v in VALUES.items():
        r = asyncio.run(one(f, v))
        if r is None:
            continue
        changed += 1
        if r[0]:
            kept_names.append(f)
        else:
            lost += 1
            lost_names.append(f)
    print(f"RESULT changed_fields={changed} of_{len(VALUES)}")
    print(f"RESULT lost={lost} of_changed")
    print("RESULT survived=" + (",".join(kept_names) or "none"))
    print("RESULT lost_fields=" + ",".join(lost_names))


main()
_rig.tail()
