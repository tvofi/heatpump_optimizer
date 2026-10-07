"""D4-s2 harness: finishing "Quick setup (recommended)" lands on the menu that offers it again.

Metric (one line): after the real config flow's quick path (user -> user_sensors
-> finish_setup: quick_setup -> device_prefill), the number of options on the
menu the user lands on that re-offer a path already completed (quick_setup),
and whether that menu is option-for-option identical to the one they chose from.

Count key: the ``menu_options`` (keys and labels) the production
``HeatPumpOptimizerConfigFlow.async_step_finish_setup`` RETURNS after
``async_step_device_prefill`` hands back to it, against the ``_data`` the quick
path stored (``quick_setup.derive`` output, which carries the questionnaire keys).

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/quick_menu.py [--perturb]
    --perturb  one-line production edit, in memory on config_flow.py's source: the
               finish_setup menu's quick_setup entry is offered only while the quick
               answers are absent (``CONF_BUILDING_STRUCTURE not in self._data``) -> 0.
Null control: the same menu reached first (before any path) -> repeated_options=0.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT repeated_completed_options=1, RESULT menu_identical_after_quick=1,
    RESULT null_repeated_options=0; --perturb: 0 and 0.
Machine: B9 cloud container (4 cores, Linux); counts are contention-immune.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib.util
import pathlib
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass  # noqa: E402

import heatpump_optimizer  # noqa: E402,F401
from heatpump_optimizer import const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
SRC = pathlib.Path("custom_components/heatpump_optimizer/config_flow.py")

if PERTURB:
    text = SRC.read_text()
    old = '                    "quick_setup": "Quick setup (recommended)",\n'
    assert text.count(old) == 1, "perturbation anchor moved"
    text = text.replace(old, (
        '                    **({} if CONF_BUILDING_STRUCTURE in self._data else '
        '{"quick_setup": "Quick setup (recommended)"}),\n'
    ))
    spec = importlib.util.spec_from_loader("heatpump_optimizer.config_flow", loader=None)
    cf = importlib.util.module_from_spec(spec)
    cf.__file__ = str(SRC)
    cf.__package__ = "heatpump_optimizer"
    sys.modules["heatpump_optimizer.config_flow"] = cf
    exec(compile(text, str(SRC), "exec"), cf.__dict__)
else:
    from heatpump_optimizer import config_flow as cf  # noqa: E402


def _prefilled(result):
    out = {}
    for key in (result.get("data_schema").schema if result.get("data_schema") else {}):
        try:
            out[str(key.schema)] = key.default()
        except Exception:
            pass
    return out


async def _run():
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    r = await flow.async_step_user({
        "name": "Heat Pump Optimizer", const.CONF_PRICE_SOURCE: "entity",
        const.CONF_PRICE_ENTITY: "sensor.nordpool", const.CONF_WEATHER_ENTITY: "weather.home",
    })
    if r.get("step_id") == "user_sensors":
        r = await flow.async_step_user_sensors({})
    first = dict(r.get("menu_options") or {})
    # Null control, computed: on the first menu the quick answers are not stored yet,
    # so its quick_setup entry re-offers nothing completed.
    global NULL
    NULL = int("quick_setup" in first and const.CONF_BUILDING_STRUCTURE in flow._data)
    page = await flow.async_step_quick_setup()
    r = await flow.async_step_quick_setup(_prefilled(page))
    trail = [r.get("step_id")]
    if r.get("step_id") == "device_prefill":
        # No pump device in this install: the user leaves the pick empty, as the page says.
        r = await flow.async_step_device_prefill({cf._PREFILL_DEVICE: None})
        trail.append(r.get("step_id"))
    return first, r, trail


NULL = -1
first, after, trail = asyncio.run(_run())
menu = dict(after.get("menu_options") or {})
print(f"# first menu:  {first}")
print(f"# quick path:  quick_setup -> {' -> '.join(map(str, trail))}")
print(f"# lands on:    {after.get('type')}/{after.get('step_id')} {menu}")
print(f"RESULT repeated_completed_options={int('quick_setup' in menu)} count")
print(f"RESULT menu_identical_after_quick={int(menu == first and after.get('step_id') == 'finish_setup')} count")
print(f"RESULT null_repeated_options={NULL} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
