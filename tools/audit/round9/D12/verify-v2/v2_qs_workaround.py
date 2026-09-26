"""D12 verify-v2 severity check for D12-s1-02 / D12-s3-01: does the options Quick setup page undo a phantom DHW plant?

Metric: ThermalParameters.from_config(data|options) (dhw_enabled, two_zone_enabled)
on a "Finish setup now" entry (v2_untouched_pages.finish_now_entry) after
(1) an untouched save of the options "hot_water" page, then (2) the options
"quick_setup" page submitted untouched except the hot-water-tank question = no.
Count key: the model parameters, not the stored keys.
Perturbation: skip step (2) (--no-quick): the plant must stay (True, False).

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_qs_workaround.py [--no-quick]
Expected: after_hot_water=(True, False), after_quick_setup=(False, False); exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 vCPU, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_untouched_pages as u  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf, quick_setup  # noqa: E402


async def go():
    data = await u.finish_now_entry()
    entry = FakeEntry(data=dict(data))
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass(dict(u.STATES))
    f = await flow.async_step_hot_water(None)
    await flow.async_step_hot_water(u.post_untouched(f))
    after_hw = u.plant({**entry.data, **entry.options})
    if "--no-quick" not in sys.argv:
        flow2 = cf.HeatPumpOptimizerOptionsFlow(entry)
        flow2.hass = FakeHass(dict(u.STATES))
        f = await flow2.async_step_quick_setup(None)
        post = u.post_untouched(f)
        post[quick_setup.FIELD_DHW_TANK] = False
        await flow2.async_step_quick_setup(post)
    return after_hw, u.plant({**entry.data, **entry.options})


t0, tt0 = time.process_time(), time.thread_time()
a, b = asyncio.run(go())
print(f"RESULT after_hot_water_plant={a} (dhw_enabled, two_zone_enabled)")
print(f"RESULT after_quick_setup_plant={b} (dhw_enabled, two_zone_enabled)")
pc, tc = time.process_time() - t0, time.thread_time() - tt0
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
