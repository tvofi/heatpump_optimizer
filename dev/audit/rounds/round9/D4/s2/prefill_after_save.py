"""D4-s2 harness: the setup wizard's pre-fill preview shows an options-only "After saving" control.

Metric (one line): on the real CONFIG flow's device_prefill preview, the number of
``after_save`` choices whose submit changes where the wizard goes next (distinct
next step_ids across the choices, minus one), and whether a non-default choice
leaks into the entry the wizard creates.

Count key: the ``step_id``/``type`` the production
``HeatPumpOptimizerConfigFlow.async_step_device_prefill`` RETURNS for each
``after_save`` value its own rendered SelectSelector offers, and the
``create_entry`` data after ``finish_now``/``setup_overview``. The field's help
text (config.step.device_prefill.data_description.after_save) says it "chooses
where the dialog goes next".

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/prefill_after_save.py [--perturb]
    --perturb  one-line production edit, in memory on config_flow.py's source: the
               config-flow preview drops the options flow's after-save row
               (``_prefill_schema(suggested, suggested)`` builds without ``CONF_AFTER_SAVE``)
               -> after_save_rendered goes to 0.
Null control: the OPTIONS flow's own pre-fill page, where the same control routes
(menu vs close) -> options_distinct_destinations=2.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT after_save_rendered=1, RESULT config_distinct_destinations=1,
    RESULT after_save_leaks_into_entry=1, RESULT options_distinct_destinations=2
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

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402

import heatpump_optimizer  # noqa: E402,F401
from heatpump_optimizer import const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
SRC = pathlib.Path("custom_components/heatpump_optimizer/config_flow.py")

if PERTURB:
    text = SRC.read_text()
    old = "                _prefill_schema(suggested, suggested), notes, {}\n"
    assert text.count(old) == 1, "perturbation anchor moved"
    text = text.replace(old, (
        "                vol.Schema({k: v for k, v in _prefill_schema(suggested, suggested).schema.items()"
        " if str(k) != CONF_AFTER_SAVE}), notes, {}\n"
    ))
    spec = importlib.util.spec_from_loader("heatpump_optimizer.config_flow", loader=None)
    cf = importlib.util.module_from_spec(spec)
    cf.__file__ = str(SRC)
    cf.__package__ = "heatpump_optimizer"
    sys.modules["heatpump_optimizer.config_flow"] = cf
    exec(compile(text, str(SRC), "exec"), cf.__dict__)
else:
    from heatpump_optimizer import config_flow as cf  # noqa: E402

AFTER = const.CONF_AFTER_SAVE
DEVICE = [
    ("sensor.pump_outdoor_temperature", "Outdoor temperature", "temperature", "°C", "-2.0"),
    ("sensor.pump_compressor_frequency", "Compressor frequency", "frequency", "Hz", "48"),
]
FIRST = {"name": "HPO", const.CONF_PRICE_SOURCE: "entity",
         const.CONF_PRICE_ENTITY: "sensor.nordpool", const.CONF_WEATHER_ENTITY: "weather.home"}


def _hass():
    hass = FakeHass(states={})
    dr.async_get(hass).add("dev_generic", name="Pump")
    for eid, name, dc, unit, state in DEVICE:
        er.async_get(hass).add(eid, unique_id=eid.replace(".", "_"), device_id="dev_generic",
                               platform="localtuya", original_name=name,
                               original_device_class=dc, unit_of_measurement=unit)
        hass.states.set(eid, FakeState(state))
    return hass


def _choices(result):
    for key, value in result["data_schema"].schema.items():
        if str(key) == AFTER:
            return list(value.config["options"])
    return []


async def _config(choice):
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = _hass()
    flow._data.update(FIRST)
    preview = await flow.async_step_device_prefill({cf._PREFILL_DEVICE: "dev_generic"})
    if choice is None:
        return preview
    nxt = await flow.async_step_device_prefill({AFTER: choice})
    await flow.async_step_finish_now()
    created = await flow.async_step_setup_overview({})
    return nxt, created


async def _options(choice):
    flow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
    flow.hass = _hass()
    await flow.async_step_modbus_prefill({cf._PREFILL_DEVICE: "dev_generic"})
    return await flow.async_step_modbus_prefill({AFTER: choice})


preview = asyncio.run(_config(None))
choices = _choices(preview)
print(f"# config preview fields={[str(k) for k in preview['data_schema'].schema]} after_save choices={choices}")
dest, leaked = set(), 0
for c in choices:
    nxt, created = asyncio.run(_config(c))
    dest.add(f"{nxt.get('type')}/{nxt.get('step_id')}")
    stored = (created.get("data") or {}).get(AFTER)
    leaked |= stored is not None and stored != const.AFTER_SAVE_MENU
    print(f"#   config after_save={c!r} -> {nxt.get('type')}/{nxt.get('step_id')}; entry stores after_save={stored!r}")
print(f"RESULT after_save_rendered={int(bool(choices))} count")
print(f"RESULT config_distinct_destinations={len(dest)} count")
print(f"RESULT after_save_leaks_into_entry={int(leaked)} count")

odest = set()
for c in ("menu", "close"):
    r = asyncio.run(_options(c))
    odest.add(f"{r.get('type')}/{r.get('step_id')}")
    print(f"#   options after_save={c!r} -> {r.get('type')}/{r.get('step_id')}")
print(f"RESULT options_distinct_destinations={len(odest)} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
