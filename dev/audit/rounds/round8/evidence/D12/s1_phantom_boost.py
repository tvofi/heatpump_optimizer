"""D12 s1 -- a hot-water boost invents a DHW tank on an install without one.

Metric: count of no-DHW plant cells in which, after the integration's own
"Hot water boost" switch (switch:BoostDhwSwitch.async_turn_on) is turned on and
one full coordinator cycle runs, the delivered action carries hot-water power
(coordinator._current_action["dhw_power"] > 0, which feeds
coordinator:HeatPumpOptimizerCoordinator._commanded_power and the published
``dhw_heating_active``). Key: the action and data dict the cycle delivers, not
the config. Also prints the phantom kW and the commanded-power delta against
the same cell's no-boost cycle.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/s1_phantom_boost.py [--fix-arm]
Expected at baseline cdf82daa: RESULT phantom_dhw_cells=8 of 8 no-DHW cells
(exact); RESULT null_dhw_cells_phantom=0 (the same 8 cells with DHW configured,
where the boost is legitimate, are not counted).
Perturbation 1 (shrinking plant): dropping DHW from a cell moves it from the
null arm (0) into the counted arm (1 each): 0 -> 8.
Perturbation 2 (--fix-arm): a one-line production edit in boost.apply that
drops the DHW channel when params.dhw_enabled is False -> phantom_dhw_cells
to_zero. Applied in memory, restored in finally.
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import inspect
import itertools
import sys
import textwrap
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402
from heatpump_optimizer import switch as switch_mod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

BASE = {
    "name": "Home",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.heat_pump",
}


def cfg_for(zones, dhw, wood, pv):
    cfg = dict(BASE)
    cfg[const.CONF_TWO_ZONE_MODE] = "on" if zones == 2 else "off"
    if zones == 2:
        cfg.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0})
    cfg[const.CONF_DHW_ENABLED] = dhw
    if dhw:
        cfg.update({const.CONF_DHW_TANK_VOLUME: 200.0, "dhw_windows": "06:00-08:30, 17:00-22:00"})
    cfg[const.CONF_WOOD_FURNACE_ENABLED] = wood
    if wood:
        cfg[const.CONF_EXTERNAL_HEAT_ENABLED] = True
        cfg[const.CONF_EXTERNAL_HEAT_ENTITY] = "binary_sensor.stove"
    cfg[const.CONF_PV_ENABLED] = pv
    if pv:
        cfg[const.CONF_PV_PEAK_KW] = 6.0
    return cfg


def make_hass(now):
    start = now.replace(minute=0, second=0, microsecond=0)
    hass = FakeHass({
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(),
             "value": round(0.5 + 0.4 * ((h % 24) in (7, 8, 17, 18, 19)), 3)}
            for h in range(48)]}),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-2.0", unit="°C"),
        "switch.heat_pump": FakeState("on"),
        "binary_sensor.stove": FakeState("off"),
    })

    async def _forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -4.0 + 4.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", _forecasts)
    return hass


async def run(cfg, now):
    hass = make_hass(now)
    entry = FakeEntry(data=dict(cfg))
    await ha_setup_entry(integration, hass, entry)
    coord = entry.runtime_data
    coord.data = await coord._async_update_data()
    before = coord._commanded_power() or 0.0
    added = []
    await switch_mod.async_setup_entry(hass, entry, added.extend)
    sw = [e for e in added if type(e).__name__ == "BoostDhwSwitch"][0]
    offered = bool(sw.available)
    await sw.async_turn_on()
    coord.data = await coord._async_update_data()
    act = coord._current_action or {}
    after = coord._commanded_power() or 0.0
    out = {
        "dhw_enabled": coord._thermal_params.dhw_enabled,
        "offered": offered,
        "phantom_kw": float(act.get("dhw_power", 0.0) or 0.0),
        "published_active": bool(coord.data.get("dhw_heating_active")),
        "commanded_delta_kw": after - before,
    }
    await coord.async_shutdown()
    return out


def patch_fix():
    src = textwrap.dedent(inspect.getsource(boost_mod.apply))
    needle = "held.expire(now)\n"
    assert needle in src
    src = src.replace(needle, needle + "    if not coord._thermal_model.params.dhw_enabled: held.until.pop(CHANNEL_DHW, None)\n", 1)
    ns = {}
    exec(compile(src, boost_mod.__file__, "exec"), boost_mod.__dict__, ns)
    orig = boost_mod.apply
    boost_mod.apply = ns["apply"]
    return orig


def main():
    fix = "--fix-arm" in sys.argv
    real_solve = coordinator_mod._await_optimize

    async def solve_inline(hass, optimizer, state, *positional, **keywords):
        return optimize_in_process(optimizer, state, positional, keywords)

    coordinator_mod._await_optimize = solve_inline
    now = dt_util.now().replace(minute=7, second=0, microsecond=0)
    real_now = dt_util.now
    dt_util.now = lambda *a, **k: now
    orig = patch_fix() if fix else None
    t0p, t0t = time.process_time(), time.thread_time()
    counted = null = 0
    n_cells = 0
    kws = []
    try:
        for zones, wood, pv in itertools.product((1, 2), (False, True), (False, True)):
            n_cells += 1
            for dhw in (False, True):
                r = asyncio.run(run(cfg_for(zones, dhw, wood, pv), now))
                tag = f"z{zones}_{'wood' if wood else 'nowood'}_{'pv' if pv else 'nopv'}_{'dhw' if dhw else 'nodhw'}"
                print(f"  {tag:<28} dhw_enabled={r['dhw_enabled']} boost_offered={r['offered']} "
                      f"dhw_power={r['phantom_kw']:.2f} kW published_active={r['published_active']} "
                      f"commanded_delta={r['commanded_delta_kw']:+.2f} kW")
                phantom = (not r["dhw_enabled"]) and (r["phantom_kw"] > 1e-6 or r["published_active"])
                if not dhw:
                    counted += int(phantom)
                    if phantom:
                        kws.append(r["phantom_kw"])
                else:
                    null += int(phantom)
    finally:
        coordinator_mod._await_optimize = real_solve
        dt_util.now = real_now
        if orig is not None:
            boost_mod.apply = orig
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT arm={'fix' if fix else 'baseline'}")
    print(f"RESULT phantom_dhw_cells={counted} of {n_cells} no-DHW cells")
    print(f"RESULT null_dhw_cells_phantom={null} of {n_cells} DHW cells")
    if kws:
        print(f"RESULT phantom_dhw_kw_min={min(kws):.3f} kW")
        print(f"RESULT phantom_dhw_kw_max={max(kws):.3f} kW")
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as fh:
        sw = [l for l in fh if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
