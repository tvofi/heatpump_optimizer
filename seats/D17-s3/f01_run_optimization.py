"""D17-s3-01: the run_optimization action re-solves without fetching or publishing.

Metric: the electricity price the published plan carries for its first step
(``coordinator.data["schedule"][0]["price"]``), after the entry's price feed
is raised from 0.5 to 2.0 /kWh and the action is called. The documented
effect (docs/configuration.md "run_optimization fetches prices and weather and
re-solves the 24-hour plan immediately. The Optimize Now button does the same
thing."; README.md Services table "Fetch prices and weather and re-solve the
24 h plan now") is a published plan priced at 2.0. Also printed: whether the
published ``last_optimization`` moved at all after the call (the re-solve is
the plan the sensors show).

Key: the published payload's first-step price and last_optimization stamp,
i.e. what every plan sensor reads; never the coordinator's private result.

Arms:
  service  -- heatpump_optimizer.run_optimization through its registered schema
  button   -- button.heat_pump_optimizer_optimize_now ``async_press`` (null
              control: the documented twin, which reaches 2.0)
Perturbation (``--perturb``): ``services:handle_run_optimization`` followed
by ``coord.async_request_refresh()`` per entry, the button's own tail, swapped
in memory; the service arm's published price moves 0.5 -> 2.0 (up).

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/f01_run_optimization.py [--perturb]
Expected (baseline): RESULT service_published_price=0.5, service_plan_republished=0,
  button_published_price=2.0, button_plan_republished=1; exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared, 3 seats).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402  (thread pin first)

import asyncio  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402

from harness import FakeState  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv


async def arm(kind: str) -> tuple[float, int]:
    inst = rig.Install(entry_id=f"f01_{kind}")
    await inst.setup()
    await inst.cycle()
    stamp = inst.coord.data["last_optimization"]
    rig.advance(1)
    inst.hass.states.set(
        "sensor.prices",
        FakeState("2.0", attributes={"raw_today": rig.price_rows(48, 2.0)}),
    )
    if kind == "service":
        await inst.call("run_optimization")
    else:
        ents = await inst.all_entities()
        await ents["button.heat_pump_optimizer_optimize_now"].async_press()
        await inst.settle()
    data = inst.coord.data
    return float(data["schedule"][0]["price"]), int(data["last_optimization"] != stamp)


async def main() -> None:
    from heatpump_optimizer import services

    if PERTURB:
        orig = services.handle_run_optimization

        async def patched(hass, call):
            await orig(hass, call)
            for _eid, coord in services._loaded_coordinators(hass):
                await coord.async_request_refresh()

        services.handle_run_optimization = patched
    rig.freeze()
    t0, t1 = time.process_time(), time.thread_time()
    sp, sr = await arm("service")
    rig.freeze()
    bp, br = await arm("button")
    print(f"RESULT service_published_price={sp} SEK/kWh")
    print(f"RESULT service_plan_republished={sr} bool")
    print(f"RESULT button_published_price={bp} SEK/kWh")
    print(f"RESULT button_plan_republished={br} bool")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
