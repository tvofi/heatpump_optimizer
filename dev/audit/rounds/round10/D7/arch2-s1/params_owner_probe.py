#!/usr/bin/env python3
"""ARCH2-s1 (round 10, D7): what one owner of the thermal parameters protects against, at runtime.

Metric: three counts on a real coordinator (FakeHass), each read from the live objects.
  holder_mutated   -- a reference to the parameters taken before a learner adopts a value
                      (what a solve record, a learner mid-await or a diagnostics read holds)
                      changed underneath its holder: 1 aliasing, 0 isolated.
  torn_at_await    -- requested fields of one set_thermal_parameters call whose value, read by
                      another task at the call's first await, differs from the call's final
                      value: >0 is a torn read across the await, 0 is one whole snapshot.
  unclamped_at_await -- divisor masses below THERMAL_MASS_FLOOR visible at that await.
  consumers_current -- of the live model, the DHW learner and the legionella guard, how many
                      read the value the learner just adopted (must stay 3 on both trees).
Count key: field names of ThermalParameters; values compared with ==.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._apply_cop_scale,
          .async_update_thermal_params, ._async_save_thermal_learning (the await, spied).
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s1/params_owner_probe.py [--null]
          run from the repository root of the tree under test (it imports that tree's package).
Perturbation: the tree. origin/main 9061fbd3d710: holder_mutated=1, torn_at_await=6,
          unclamped_at_await=1; with P1_thermal_params_single_owner.patch: 0, 0, 0
          (expected_direction to_zero); consumers_current=3 on both.
Null control: --null requests every field at the value it already holds; torn_at_await and
          unclamped_at_await must read 0 on both trees (the counter counts requested changes
          that are not yet visible, not noise), and holder_mutated is skipped.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import copy  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import THERMAL_MASS_FLOOR  # noqa: E402

MASSES = ("room_thermal_mass", "slab_thermal_mass", "upper_floor_thermal_mass", "lower_floor_thermal_mass")


def coordinator() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "dhw_tank_volume": 200.0, "upper_floor_thermal_mass": 3.0,
    }))


def current(reader):
    """A consumer's view: the object it holds, or what its reader returns."""
    return reader() if callable(reader) else reader


def main(argv: list[str]) -> int:
    null = "--null" in argv
    t_cpu, t_thr = time.process_time(), time.thread_time()
    coord = coordinator()

    if not null:
        held = coord._thermal_params
        before = held.cop_scale
        coord._apply_cop_scale(1.2 if abs(before - 1.2) > 1e-9 else 1.1)
        print(f"RESULT holder_mutated={int(held.cop_scale != before)} count")
        adopted = coord._cop_scale
        views = (coord._thermal_model.params, current(coord._dhw_learner._params),
                 current(coord._legionella._params))
        print(f"RESULT consumers_current={sum(v.cop_scale == adopted for v in views)} count (of 3)")

    p = coord._thermal_params
    if null:
        request = {"house_heat_loss_coefficient": p.heat_loss_coefficient,
                   "house_thermal_mass": p.room_thermal_mass,
                   "dhw_legionella_temperature": p.dhw_legionella_temp,
                   "dhw_idle_min_temperature": p.dhw_idle_min_temp,
                   "dhw_schedule_enabled": p.dhw_schedule_enabled,
                   "ecl110_displace_min": p.ecl110_displace_min}
    else:
        request = {"house_heat_loss_coefficient": 0.3,
                   "house_thermal_mass": 1e-6,  # below the divisor floor
                   "dhw_legionella_temperature": 63.0,
                   "dhw_idle_min_temperature": 41.0,
                   "dhw_schedule_enabled": not p.dhw_schedule_enabled,
                   "ecl110_displace_min": -4.5,
                   "dhw_windows": "05:00-07:00, 18:00-21:00"}
    fields = ("heat_loss_coefficient", "room_thermal_mass", "dhw_legionella_temp", "dhw_idle_min_temp",
              "dhw_schedule_enabled", "ecl110_displace_min", "dhw_windows")
    seen: dict = {}
    real_save = coord._async_save_thermal_learning

    async def spy() -> None:
        # Another task reading the hub while the service call is suspended here.
        if not seen:
            live = coord._thermal_params
            seen.update({f: copy.deepcopy(getattr(live, f)) for f in (*fields, *MASSES)})
        await real_save()

    coord._async_save_thermal_learning = spy
    asyncio.run(coord.async_update_thermal_params(request))
    final = coord._thermal_params
    if not seen:
        print("RESULT torn_at_await=unobserved (the call never awaited the save)")
        return 1
    requested = [f for f in fields if f != "dhw_windows" or "dhw_windows" in request]
    torn = [f for f in requested if seen[f] != getattr(final, f)]
    unclamped = [m for m in MASSES if float(seen[m]) < THERMAL_MASS_FLOOR]
    print(f"RESULT torn_at_await={len(torn)} count ({', '.join(torn) or 'none'})")
    print(f"RESULT unclamped_at_await={len(unclamped)} count ({', '.join(unclamped) or 'none'})")
    print(f"RESULT final_room_thermal_mass={final.room_thermal_mass} kWh/K")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
