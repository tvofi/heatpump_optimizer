"""D12 verify-v1 (round 9): D12-s1-02 workaround check -- after the untouched
hot_water / hot_water_tank save has stored the DHW key, can the options flow
itself take hot-water planning off again?

Metric (one line): per page, derived ThermalParameters.from_config(...).dhw_enabled
after (1) the untouched save and (2) a second save of the same page with the
stored DHW key's field left empty (omitted from user_input, as HA posts a cleared box).
Count key: the dhw_enabled the production presence rule derives from the stored config.
Also RESULT phantom_after_clear = pages whose DHW stays enabled after the clear attempt.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v1/phantom_undo.py
Perturbation: none of its own; the finder's --fallback-dhw moves step (1) to False.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round9 evidence tree 6f51db2c).
Machine: G2-V1 cloud container, 4 vCPU, Python 3.14. Counts only.
Root rule: cwd (repository root); reuses s1/phantom_dhw.py's INSTALL and s1/flow_pages.py's defaults_of.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
import time

sys.path.insert(0, "tools/audit/round9/D12/s1")
import phantom_dhw as ph  # noqa: E402
import flow_pages as fp  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

KEY = {"hot_water": const.CONF_DHW_WINDOWS, "hot_water_tank": const.CONF_DHW_TANK_VOLUME}


def enabled(entry):
    return ThermalParameters.from_config({**entry.data, **entry.options}).dhw_enabled


async def run(step):
    entry = FakeEntry(data=dict(ph.INSTALL))
    out = {"before": enabled(entry)}
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass()
    h = getattr(flow, f"async_step_{step}")
    await h(fp.defaults_of(await h(None)))
    out["after_untouched"] = enabled(entry)
    out["stored"] = {k: v for k, v in entry.options.items() if k in (const.CONF_DHW_WINDOWS, const.CONF_DHW_TANK_VOLUME)}
    flow2 = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow2.hass = FakeHass()
    h2 = getattr(flow2, f"async_step_{step}")
    posted = fp.defaults_of(await h2(None))
    posted.pop(KEY[step], None)
    try:
        r = await h2(posted)
        out["clear_result"] = r.get("type") if isinstance(r, dict) else str(r)
        out["clear_errors"] = r.get("errors") if isinstance(r, dict) else None
    except Exception as err:  # noqa: BLE001
        out["clear_result"] = f"raised {type(err).__name__}: {err}"
    out["after_clear"] = enabled(entry)
    out["stored_after_clear"] = {k: v for k, v in {**entry.data, **entry.options}.items() if k in (const.CONF_DHW_WINDOWS, const.CONF_DHW_TANK_VOLUME)}
    return out


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    stuck = 0
    for step in KEY:
        o = asyncio.run(run(step))
        print(f"PAGE {step} {o}")
        stuck += bool(o["after_clear"])
        print(f"RESULT {step}_dhw_after_untouched={int(o['after_untouched'])} flag")
        print(f"RESULT {step}_dhw_after_clear={int(o['after_clear'])} flag")
    print(f"RESULT phantom_after_clear={stuck} pages")
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
