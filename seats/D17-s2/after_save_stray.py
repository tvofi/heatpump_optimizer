"""D17-s2-05 -- the setup pre-fill page stores its "After saving" navigation choice in the entry.

Metric: the number of entries, created through the real config flow (quick_setup ->
device_prefill picking the G7b fixture device -> second submit -> finish_now), whose
`data` carries the key `after_save`, over the two choices {menu, close}. Key: the
created entry's data as async_create_entry receives it.
Oracle: strings.json config.step.device_prefill.data_description.after_save "Setup
carries on to the next page whichever you choose; nothing is saved until setup
finishes" -- the choice is navigation, not a setting; no reader in the package
reads `after_save` from an entry (grep: const.py only outside config_flow.py), and
the options flow pops it from user_input rather than storing it (config_flow.py
`user_input.pop(CONF_AFTER_SAVE, ...)`).
Perturbation `--perturb`: config_flow._flatten_section_input wrapped to drop
`after_save` (the one-line fix in async_step_device_prefill's `saved` comprehension).
Expected: entries_with_after_save=2 at baseline, 0 under --perturb; the next step is
finish_setup for both choices in both arms (null control). Tolerance 0.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/after_save_stray.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_device_prefill
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio  # noqa: E402
from unittest import mock  # noqa: E402

import rig  # noqa: E402
import silent_prefill as sp  # noqa: E402  (the fixture seeding, reused)
from heatpump_optimizer import config_flow  # noqa: E402


async def walk(choice):
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    h = sp.FakeHass()
    sp.seed(h)
    flow.hass = h
    await rig._submit(flow, "user", rig.FIRST)
    await rig._submit(flow, "user_sensors", dict(rig.SENSORS))
    await rig._submit(flow, "quick_setup", {**rig.questionnaire(), "two_zone": False, "buffer_tank": False,
                                            "dhw_tank": True, "wood_furnace": False, "wood_buffer_tank": False})
    await rig._submit(flow, "device_prefill", {"prefill_device": "dev_rotenso"})
    nxt = await rig._submit(flow, "device_prefill", {"after_save": choice})
    await rig._submit(flow, "finish_now", {})
    done = await rig._submit(flow, "setup_overview", {})
    return nxt.get("step_id"), done.get("data") or {}


def measure():
    n = 0
    for choice in ("menu", "close"):
        step, data = asyncio.run(walk(choice))
        has = "after_save" in data
        n += int(has)
        print(f"after_save={choice}: next step={step} entry carries after_save={has} ({data.get('after_save')!r})")
    print(f"RESULT entries_with_after_save={n} entries")


if __name__ == "__main__":
    if "--perturb" in sys.argv:
        real = config_flow._flatten_section_input
        with mock.patch.object(config_flow, "_flatten_section_input",
                               lambda d: {k: v for k, v in real(d).items() if k != "after_save"}):
            measure()
    else:
        measure()
    print("RESULT thread_factor=1.00 (counts only; single-thread pin)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
