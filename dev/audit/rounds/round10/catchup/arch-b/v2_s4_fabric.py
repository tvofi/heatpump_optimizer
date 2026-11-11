"""Catch-up verifier arch-b, V2 for D7-s4-82: does the split (lower-floor) learner starve over MANY cycles,
in the production order and in the swapped order?

Metric: lower_samples_after_N = the production counter ``_lower_floor_loss_samples`` after N=12
consecutive replayable intervals, the house learner itself advancing the shared baseline each cycle
(only the clock is moved: ``_last_house_sample_time`` is set 0.5 h back before each cycle, as 0.5 h of
wall time would). The state drifts 0.1 K down per interval with 2 kW on.
Arms: order lower,house (production, coordinator.py _update_current_state) and house,lower (swap).
On a P3 tree (``_close_fabric_interval`` present) the interval is closed once and handed to both.
Null control: the house learner's own counter must read N in both arms.
Perturbation: the swap is the perturbation; on main lower_samples must fall N -> 0.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-b/v2_s4_fabric.py [--root DIR]

Expected at baseline 9061fbd3d: lower,house -> lower N(=12)?, house 12; house,lower -> lower 0.
Machine: seat macOS box; counts only. Writes nothing.
"""
import asyncio
import os
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path.cwd()
sys.path.insert(0, str(Path.cwd() / "tests"))
sys.path.insert(0, str(root / "custom_components"))

import homeassistant.util.dt as dt_util  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
       "outdoor_temp_entity": "sensor.outdoor", "upper_floor_thermal_mass": 3.0,
       "lower_floor_thermal_mass": 8.0, "lower_floor_temp_entity": "sensor.lower"}
N = 12


def run(order):
    c = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=dict(CFG)))
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=20.0,
                      slab_temperature=27.0, outdoor_temperature=-5.0)
    c._last_house_sample = st
    c._current_action = {"power": 2.0}
    learners = {"lower": c._async_learn_lower_floor_loss, "house": c._async_learn_house_heat_loss}

    async def go():
        nonlocal st
        for i in range(N):
            c._last_house_sample_time = dt_util.now() - timedelta(hours=0.5)
            st = replace(st, room_temperature=st.room_temperature - 0.1,
                         upper_floor_temperature=st.upper_floor_temperature - 0.1,
                         lower_floor_temperature=st.lower_floor_temperature - 0.07)
            c._current_state = st
            if hasattr(c, "_close_fabric_interval"):
                iv = c._close_fabric_interval()
                for n in order:
                    await learners[n](iv)
            else:
                for n in order:
                    await learners[n]()
    asyncio.run(go())
    return c._lower_floor_loss_samples, c._house_heat_loss_samples


tree = "P3" if hasattr(HeatPumpOptimizerCoordinator, "_close_fabric_interval") else "main"
print(f"RESULT tree={tree}")
for order in (("lower", "house"), ("house", "lower")):
    lo, ho = run(order)
    print(f"RESULT {'_'.join(order)}_lower_samples_after_{N}={lo} count")
    print(f"RESULT {'_'.join(order)}_house_samples_after_{N}={ho} count")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
