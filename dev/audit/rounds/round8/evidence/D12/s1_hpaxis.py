"""D12 s1 -- heat-pump axis: modulating versus on/off (min power == max power).

Metric: for one full coordinator cycle per pump type and price profile, the
energy the plan books for space heating (sum power_schedule * dt) against the
energy the on/off switch actuation delivers for the same plan
(sum heat_pump_on_schedule * p_max * dt, the only thing a switch-controlled
fixed-speed pump can do); RESULT actuated_over_planned per cell, and the count
of steps planned strictly between 0 and min_electrical_power (duty-cycled
steps). Key: optimizer:HeatPumpOptimizer._power_to_heat_pump_schedule and the
OptimizationResult the real coordinator cycle publishes.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/s1_hpaxis.py
Expected: see REPORT-s1.md (exact on this box, float ratios to 3 dp).
Null control: the flat price profile arm of each pump.
Perturbation: min power 3.0 -> 0.5 (modulating) moves submin_steps.
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

BASE = {
    "name": "Home",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.heat_pump",
    const.CONF_DHW_ENABLED: False,
    const.CONF_HEAT_PUMP_MAX_POWER: 3.0,
}


def price(profile, h):
    if profile == "flat":
        return 0.8
    return round(0.5 + 0.6 * ((h % 24) in (7, 8, 17, 18, 19)) + 0.05 * (h % 3), 3)


async def cell(pmin, profile, outdoor, now):
    start = now.replace(minute=0, second=0, microsecond=0)
    hass = FakeHass({
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(), "value": price(profile, h)}
            for h in range(48)]}),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState(str(outdoor), unit="°C"),
        "switch.heat_pump": FakeState("on"),
    })

    async def _forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": outdoor + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", _forecasts)
    entry = FakeEntry(data={**BASE, const.CONF_HEAT_PUMP_MIN_POWER: pmin})
    await ha_setup_entry(integration, hass, entry)
    coord = entry.runtime_data
    await coord._async_update_data()
    res = coord._optimization_result
    dt = coord._ctx._opt_config.dt_hours
    p = np.asarray(res.power_schedule, dtype=float)
    on = np.asarray(res.heat_pump_on_schedule, dtype=bool)
    pmax = coord._ctx._thermal_params.max_electrical_power
    planned = float(p.sum() * dt)
    actuated = float(on.sum() * pmax * dt)
    submin = int(np.sum((p > 1e-3) & (p < pmin - 1e-6)))
    await coord.async_shutdown()
    return {"planned": planned, "actuated": actuated, "submin": submin,
            "steps": len(p), "on": int(on.sum())}


def main():
    real_solve = coordinator_mod._await_optimize

    async def solve_inline(hass, optimizer, state, *positional, **keywords):
        return optimize_in_process(optimizer, state, positional, keywords)

    coordinator_mod._await_optimize = solve_inline
    now = dt_util.now().replace(minute=7, second=0, microsecond=0)
    real_now = dt_util.now
    dt_util.now = lambda *a, **k: now
    t0p, t0t = time.process_time(), time.thread_time()
    try:
        for pmin in (0.5, 3.0):
            for profile in ("peaky", "flat"):
                for outdoor in (-8.0, 0.0, 6.0):
                    r = asyncio.run(cell(pmin, profile, outdoor, now))
                    tag = f"pmin{pmin}_{profile}_out{outdoor:+.0f}"
                    ratio = r["actuated"] / r["planned"] if r["planned"] > 1e-6 else float("nan")
                    print(f"RESULT {tag}_planned_kwh={r['planned']:.3f} kWh")
                    print(f"RESULT {tag}_actuated_kwh={r['actuated']:.3f} kWh")
                    print(f"RESULT {tag}_actuated_over_planned={ratio:.3f} ratio")
                    print(f"RESULT {tag}_submin_steps={r['submin']} of {r['steps']} steps")
    finally:
        coordinator_mod._await_optimize = real_solve
        dt_util.now = real_now
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as fh:
        sw = [l for l in fh if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
