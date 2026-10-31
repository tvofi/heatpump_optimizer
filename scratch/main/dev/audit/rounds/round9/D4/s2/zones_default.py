"""D4-s2 harness: "leave defaults if you don't need the two-zone model" turns it on.

Metric (one line): the ``two_zone_enabled`` the production
``ThermalParameters.from_config`` reads from the entry the real
``HeatPumpOptimizerConfigFlow`` creates when every page of a path is submitted
with exactly the values the page itself pre-fills (1 = two-zone model on).

Count key: the delivered entry (``create_entry`` data) read through
``thermal_model.ThermalParameters.from_config`` -- the flag the planner uses --
not the presence of any key the harness looks for. Paths:
  expert   : user -> user_sensors -> finish_setup/temperature -> building/thermal
             -> zones -> dhw -> weather_sensitivity -> setup_overview -> create_entry
             (the zones page's own description: "Leave defaults if you don't need
             the two-zone model.")
  describe : the same, with building/building_describe -> building_extras instead of
             thermal/zones (null control: no zones page on the path -> 0)
Also printed: the setup overview's own house line, which the user reads before creating.

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/zones_default.py [--perturb]
    --perturb  one-line production edit, in memory on config_flow.py's source: in
               async_step_zones, ``self._data.update(user_input)`` stores the zone keys only
               when a value differs from the page's own default
               (``{k: v for k, v in user_input.items() if v != _ZONE_DEFAULTS.get(k, object())}``)
               -> expert goes to 0.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT two_zone_expert_defaults=1, RESULT two_zone_describe_defaults=0 (null control),
    RESULT two_zone_expert_defaults under --perturb = 0
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
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
SRC = pathlib.Path("custom_components/heatpump_optimizer/config_flow.py")

if PERTURB:
    text = SRC.read_text()
    anchor = (
        '        """Handle two-zone and solar configuration (optional step)."""\n'
        "        if user_input is not None:\n"
        "            self._data.update(user_input)\n"
    )
    assert text.count(anchor) == 1, "perturbation anchor moved"
    text = text.replace(anchor, anchor.replace(
        "self._data.update(user_input)",
        "self._data.update({k: v for k, v in user_input.items() if v != _ZONE_DEFAULTS.get(k, object())})",
    ))
    text += (
        "\n_ZONE_DEFAULTS = {CONF_UPPER_FLOOR_THERMAL_MASS: DEFAULT_UPPER_FLOOR_THERMAL_MASS,"
        " CONF_LOWER_FLOOR_THERMAL_MASS: DEFAULT_LOWER_FLOOR_THERMAL_MASS,"
        " CONF_INTER_ZONE_TRANSFER: DEFAULT_INTER_ZONE_TRANSFER,"
        " CONF_RADIATOR_POWER_FRACTION: DEFAULT_RADIATOR_POWER_FRACTION}\n"
    )
    spec = importlib.util.spec_from_loader("heatpump_optimizer.config_flow", loader=None)
    cf = importlib.util.module_from_spec(spec)
    cf.__file__ = str(SRC)
    cf.__package__ = "heatpump_optimizer"
    sys.modules["heatpump_optimizer.config_flow"] = cf
    exec(compile(text, str(SRC), "exec"), cf.__dict__)
else:
    from heatpump_optimizer import config_flow as cf  # noqa: E402


def _prefilled(result) -> dict:
    """What the page posts when the user presses Submit without editing."""
    out = {}
    for key in (result.get("data_schema").schema if result.get("data_schema") else {}):
        try:
            out[str(key.schema)] = key.default()
        except Exception:
            pass
    return out


async def _walk(branch: str) -> tuple[int, str, list[str]]:
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    trail = []
    result = await flow.async_step_user({
        "name": "Heat Pump Optimizer",
        const.CONF_PRICE_SOURCE: "entity",
        const.CONF_PRICE_ENTITY: "sensor.nordpool",
        const.CONF_WEATHER_ENTITY: "weather.home",
    })
    trail.append(result.get("step_id"))
    if result.get("step_id") == "user_sensors":
        result = await flow.async_step_user_sensors({})
        trail.append(result.get("step_id"))
    result = await flow.async_step_temperature(_prefilled(await flow.async_step_temperature()))
    trail.append(result.get("step_id"))
    if branch == "expert":
        page = await flow.async_step_thermal()
        result = await flow.async_step_thermal(_prefilled(page))
        trail.append(result.get("step_id"))
        result = await flow.async_step_zones(_prefilled(result))
    else:
        page = await flow.async_step_building_describe()
        result = await flow.async_step_building_describe(_prefilled(page))
        trail.append(result.get("step_id"))
        result = await flow.async_step_building_extras(_prefilled(result))
    trail.append(result.get("step_id"))
    result = await flow.async_step_dhw(_prefilled(result))
    trail.append(result.get("step_id"))
    result = await flow.async_step_weather_sensitivity(_prefilled(result))
    trail.append(result.get("step_id"))
    overview = (result.get("description_placeholders") or {}).get("setup_summary", "")
    house = next((ln for ln in overview.splitlines() if ln.startswith("House")), "?")
    created = await flow.async_step_setup_overview({})
    trail.append(created.get("type"))
    params = ThermalParameters.from_config(dict(created.get("data") or {}))
    return int(params.two_zone_enabled), house, trail


for branch in ("expert", "describe"):
    flag, house, trail = asyncio.run(_walk(branch))
    print(f"# {branch}: {' -> '.join(str(t) for t in trail)}; overview says {house!r}")
    print(f"RESULT two_zone_{branch}_defaults={flag} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
