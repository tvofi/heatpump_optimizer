"""D12-s1: an untouched hot-water page invents a DHW tank on a no-DHW install (D12.M2).

Metric: for each seam that posts a hot-water page's own defaults back
untouched over an install that configured no hot water (the entry
"Finish setup now" creates: tibber token, weather, indoor/outdoor probes),
run the saved config through integration setup and one coordinator cycle and
count the plan steps whose OptimizationResult.dhw_power_schedule is > 0, plus
the planned DHW kWh. Count key: the published plan (coordinator
._optimization_result), not the stored keys.

Seams: options page hot_water, options page hot_water_tank
(HeatPumpOptimizerOptionsFlow._save_or_menu / _omit_unstored_defaults), and
the config-flow wizard step dhw (HeatPumpOptimizerConfigFlow.async_step_dhw).
Control: the same install with no page submitted (0 steps).
Perturbation --fallback-dhw: put CONF_DHW_WINDOWS and CONF_DHW_TANK_VOLUME
into config_flow._ABSENT_FALLBACKS at their form defaults (i.e. treat the
untouched default as "unchanged"): the two options seams must go to 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/s1/phantom_dhw.py [--fallback-dhw]
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B6 container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import logging
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix as m  # noqa: E402
import flow_pages as fp  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402

logging.disable(logging.CRITICAL)
if "--fallback-dhw" in sys.argv:
    config_flow._ABSENT_FALLBACKS[const.CONF_DHW_WINDOWS] = const.DEFAULT_DHW_WINDOWS
    config_flow._ABSENT_FALLBACKS[const.CONF_DHW_TANK_VOLUME] = const.DEFAULT_DHW_TANK_VOLUME

INSTALL = dict(m.BASE)


async def options_seam(step):
    entry = FakeEntry(data=dict(INSTALL))
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass()
    h = getattr(flow, f"async_step_{step}")
    await h(fp.defaults_of(await h(None)))
    return {**entry.data, **entry.options}


async def wizard_dhw_seam():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    flow._data = dict(INSTALL)
    form = await flow.async_step_dhw(None)
    posted = fp.defaults_of(form)
    flow.async_step_weather_sensitivity = _stop  # the next page is not under test

    await flow.async_step_dhw(posted)
    return dict(flow._data)


async def _stop(*a, **k):
    return {"type": "stopped"}


def plan_dhw(cfg):
    dt_util.freeze(m.START + timedelta(hours=10))
    try:
        hass = FakeHass(m.states_for(cfg))
        entry = FakeEntry(data=dict(cfg))
        asyncio.run(m.integ.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        asyncio.run(coord.async_refresh())
        res = coord._optimization_result
        sched = list(res.dhw_power_schedule or []) if res else []
        steps = sum(1 for p in sched if p and p > 1e-6)
        kwh = sum(float(p) * 0.25 for p in sched if p)
        return coord._thermal_model.params.dhw_enabled, steps, round(kwh, 2)
    finally:
        dt_util.freeze(None)


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    seams = {
        "control_no_save": lambda: dict(INSTALL),
        "options_hot_water": lambda: asyncio.run(options_seam("hot_water")),
        "options_hot_water_tank": lambda: asyncio.run(options_seam("hot_water_tank")),
        "wizard_dhw_step": lambda: asyncio.run(wizard_dhw_seam()),
    }
    inventing_options = 0
    for name, build in seams.items():
        cfg = build()
        added = sorted(k for k in cfg if k not in INSTALL)
        enabled, steps, kwh = plan_dhw(cfg)
        print(f"SEAM {name}: stored+={added} dhw_enabled={enabled} dhw_steps={steps} dhw_kwh={kwh}")
        print(f"RESULT {name}_dhw_plan_steps={steps} count")
        print(f"RESULT {name}_dhw_plan_kwh={kwh} kWh")
        if name.startswith("options_") and steps > 0:
            inventing_options += 1
    print(f"RESULT options_pages_inventing_dhw_plan={inventing_options} count")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
