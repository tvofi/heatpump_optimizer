#!/usr/bin/env python3
"""ARCH2-s4 (round 10, D7): whether the two fabric learners' call order decides if one of them learns.

Metric:   lower-floor split samples learned from ONE replayable two-zone interval when the cycle runs
          the two fabric learners in a given order (count, 0 or 1). Count key: the production
          learner's own counter ``_lower_floor_loss_samples`` after the call, never the order label.
Cells:    order "lower,house" (production order, the null control: 1 on every tree) and order
          "house,lower" (the reordering the source comment warns about).
Cycle:    on a tree with ``_close_fabric_interval`` (P3) the cycle closes the interval once and hands
          it to both learners, as ``_update_current_state`` does there; on main it calls the two
          learners bare, as ``_update_current_state`` does on main. The order is the only change.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss,
          coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss, and on P3
          coordinator:HeatPumpOptimizerCoordinator._close_fabric_interval.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s4/fabric_order.py
Perturbation: the reordering is the perturbation (one swapped line in the cycle): on main the
          learned count must fall to 0 (to_zero); on P3 it must not move.
Expected (baseline 9061fbd3d710, Apple M1, darwin): main lower,house=1 house,lower=0;
          P3 lower,house=1 house,lower=1. Exact (counts).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import homeassistant.util.dt as dt_util  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "lower_floor_temp_entity": "sensor.lower",
}


def one_interval(order: tuple[str, str]) -> tuple[int, int]:
    """(lower samples, house samples) after one replayable interval in ``order``."""
    c = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=dict(CFG)))
    base = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.0, slab_temperature=27.0,
        outdoor_temperature=-5.0,
    )
    c._last_house_sample = base
    c._last_house_sample_time = dt_util.now() - timedelta(hours=0.5)
    c._current_state = replace(base, room_temperature=20.9, upper_floor_temperature=20.9,
                               lower_floor_temperature=19.9)
    c._current_action = {"power": 2.0}
    learners = {"lower": c._async_learn_lower_floor_loss, "house": c._async_learn_house_heat_loss}

    async def cycle():
        if hasattr(c, "_close_fabric_interval"):
            interval = c._close_fabric_interval()
            for name in order:
                await learners[name](interval)
        else:
            for name in order:
                await learners[name]()

    asyncio.run(cycle())
    return c._lower_floor_loss_samples, c._house_heat_loss_samples


def main() -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    tree = "P3" if hasattr(HeatPumpOptimizerCoordinator, "_close_fabric_interval") else "main"
    print(f"RESULT tree={tree}")
    for order in (("lower", "house"), ("house", "lower")):
        lower, house = one_interval(order)
        tag = "_".join(order)
        print(f"RESULT lower_samples_{tag}={lower} count")
        print(f"RESULT house_samples_{tag}={house} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
