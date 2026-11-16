"""D17-s3-02: set_thermal_parameters' house fields are accepted and do nothing in two-zone.

Metric: the absolute change in the published plan's total space-heating
energy (sum of ``coordinator.data["schedule"][i]["power"]`` over the 96
quarter-hour steps, kW summed = 4x kWh) between the solve before and the
solve after a ``heatpump_optimizer.set_thermal_parameters`` call that sets
one field, measured after the call and again after a restart (the value is
stored in the entry's options). Fields: ``house_heat_loss_coefficient``
0.15 -> 0.35 kW/°C and ``house_thermal_mass`` 10 -> 3 kWh/°C (strings.json:
"Overall heat loss coefficient in kW/°C. Lower values indicate better
insulation."; "Thermal mass of the house"; the service: "Supports
single-zone, two-zone, DHW, and weather sensitivity parameters").

Key: the published plan (what the solve delivered), not the stored
parameter -- the parameter object changes in every arm.

Arms: ``two_zone_mode`` absent (the default, "auto", which the install
resolves to two-zone here), "on", and "off" (single-zone, the null control
where the field must move the plan).
Perturbation (``--perturb``): ``two_zone_mode: off`` written into every
arm's entry data (a config change); the two-zone arms' delta moves from 0 up.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/f02_two_zone_inert.py [--perturb]
Expected (baseline): delta 0.000 for both fields in the auto and on arms,
  > 4 in the off arm; exact to 0.001.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared, 3 seats).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv
FIELDS = (("house_heat_loss_coefficient", 0.35), ("house_thermal_mass", 3.0))
ARMS = ("auto", "on", "off")


def total(d) -> float:
    return sum(float(x["power"]) for x in d["schedule"])


async def one(arm: str, field: str, value: float) -> tuple[float, float, bool]:
    extra = {} if arm == "auto" else {"two_zone_mode": arm}
    if PERTURB:
        extra = {"two_zone_mode": "off"}
    rig.freeze()
    inst = rig.Install(entry_id=f"f02_{arm}_{field}", data=rig.base_config(**extra))
    await inst.setup()
    before = await inst.cycle()
    two_zone = bool(before["two_zone_enabled"])
    await inst.call("set_thermal_parameters", {field: value})
    after = await inst.cycle()
    await inst.restart()
    restarted = await inst.cycle()
    return abs(total(after) - total(before)), abs(total(restarted) - total(before)), two_zone


async def main() -> None:
    t0, t1 = time.process_time(), time.thread_time()
    zero_cells = 0
    for arm in ARMS:
        for field, value in FIELDS:
            d_call, d_restart, tz = await one(arm, field, value)
            print(f"RESULT {arm}.{field}.two_zone={int(tz)} bool")
            print(f"RESULT {arm}.{field}.plan_delta={d_call:.3f} kW-steps")
            print(f"RESULT {arm}.{field}.plan_delta_after_restart={d_restart:.3f} kW-steps")
            if tz and d_call < 1e-3 and d_restart < 1e-3:
                zero_cells += 1
    print(f"RESULT two_zone_inert_cells={zero_cells} count")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
