"""D4-s2 harness: the CONFIG flow's device pre-fill page shows keys its own
translation namespace does not carry.

Metric (one line): over the real ``HeatPumpOptimizerConfigFlow.async_step_device_prefill``
driven with a name-matched heat-pump device, the number of rendered field keys with
no label in ``config.step.device_prefill.data`` plus the number of returned error keys
with no text in ``config.error`` -- counted per language file (en, sv).

Count key: the keys the production step RETURNS (``data_schema`` field names and
``errors`` values), looked up in the translation file the Home Assistant frontend
resolves a config-flow page against (``component.<domain>.config.step.<step>.data.<key>``
and ``component.<domain>.config.error.<key>``). The options flow's twin page
(``options.step.modbus_prefill`` / ``options.error``) is NOT consulted: that is the
namespace the frontend never reads for a config flow.

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/prefill_config_strings.py
    ... --perturb     # in-memory translation fix: copy the options twin's labels and
                      # error texts into the config namespace -> every count goes to 0

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT unlabelled_fields_en=3, unlabelled_fields_sv=3,
    RESULT untranslated_errors_en=1, untranslated_errors_sv=1,
    RESULT options_twin_unlabelled=0 (null control: same keys resolve in the options namespace)
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
import copy
import json
import pathlib
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()

COMP = pathlib.Path("custom_components/heatpump_optimizer")
PERTURB = "--perturb" in sys.argv

FILES = {
    "en": json.loads((COMP / "translations/en.json").read_text()),
    "sv": json.loads((COMP / "translations/sv.json").read_text()),
}
if PERTURB:
    # The one-edit fix, in memory: the config namespace gets the options twin's
    # labels, descriptions and error texts for the keys it lacks.
    for tree in FILES.values():
        c_step = tree["config"]["step"]["device_prefill"]
        o_step = tree["options"]["step"]["modbus_prefill"]
        for kind in ("data", "data_description"):
            for k, v in o_step.get(kind, {}).items():
                c_step.setdefault(kind, {}).setdefault(k, v)
        for k, v in tree["options"]["error"].items():
            tree["config"]["error"].setdefault(k, v)

FIRST_SCREEN = {
    "name": "Heat Pump Optimizer",
    # An entity price source, so the first screen needs no Tibber round trip.
    const.CONF_PRICE_SOURCE: "entity",
    const.CONF_PRICE_ENTITY: "sensor.nordpool",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
}

# A pump no source table knows (localtuya), read by the name fallback: the
# ordinary unbranded install the fallback exists for.
DEVICE = [
    # (entity_id, original_name, device_class, unit, state)
    ("sensor.pump_outdoor_temperature", "Outdoor temperature", "temperature", "°C", "-2.0"),
    ("sensor.pump_compressor_frequency", "Compressor frequency", "frequency", "Hz", "48"),
    ("number.pump_dhw_minimum_temperature", "DHW minimum temperature", None, "°C", "42"),
    ("number.pump_legionella_temperature", "Legionella temperature", None, "°C", "65"),
]
NOTHING = [("sensor.utility_humidity", "Utility humidity", "humidity", "%", "40")]


def _hass() -> FakeHass:
    hass = FakeHass(states={})
    dreg, ereg = dr.async_get(hass), er.async_get(hass)
    for dev, rows in (("dev_generic", DEVICE), ("dev_nothing", NOTHING)):
        dreg.add(dev, name="Pump" if dev == "dev_generic" else "Utility meter cupboard")
        for eid, name, dc, unit, state in rows:
            ereg.add(
                eid,
                unique_id=eid.replace(".", "_"),
                device_id=dev,
                platform="localtuya",
                original_name=name,
                original_device_class=dc,
                unit_of_measurement=unit,
            )
            hass.states.set(eid, FakeState(state))
    hass.config_entries.entries.append(
        FakeEntry(data={}, options={const.CONF_PREFILL_OFFER: True})
    )
    return hass


def _fields(result) -> list[str]:
    schema = result.get("data_schema")
    return [str(getattr(k, "schema", k)) for k in (schema.schema if schema else {})]


async def _drive() -> dict:
    # Arm A: a readable device -> the preview form with the suggested keys.
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = _hass()
    first = await flow.async_step_user(
        {k: v for k, v in FIRST_SCREEN.items() if k != const.CONF_HEAT_PUMP_SWITCH_ENTITY}
    )
    if first.get("step_id") == "user_sensors":
        first = await flow.async_step_user_sensors(
            {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a"}
        )
    print(f"# first screen -> {first.get('type')}/{first.get('step_id')} errors={first.get('errors')}")
    offered = first.get("step_id") == "device_prefill"
    preview = await flow.async_step_device_prefill({config_flow._PREFILL_DEVICE: "dev_generic"})
    # Arm B: a device nothing resolves -> the page's own refusal.
    flow_b = config_flow.HeatPumpOptimizerConfigFlow()
    flow_b.hass = _hass()
    flow_b._data.update(FIRST_SCREEN)
    refused = await flow_b.async_step_device_prefill(
        {config_flow._PREFILL_DEVICE: "dev_nothing"}
    )
    return {"offered": offered, "preview": preview, "refused": refused}


out = asyncio.run(_drive())
preview, refused = out["preview"], out["refused"]
keys = _fields(preview)
errors = sorted(set((refused.get("errors") or {}).values()))
print(f"# offered from user_sensors: {out['offered']}")
print(f"# preview step={preview.get('step_id')} fields={keys}")
print(f"# refusal step={refused.get('step_id')} errors={refused.get('errors')}")

for lang, tree in FILES.items():
    step = tree["config"]["step"]["device_prefill"]
    missing = [k for k in keys if k not in step.get("data", {})]
    missing_desc = [k for k in keys if k not in step.get("data_description", {})]
    bad_err = [e for e in errors if e not in tree["config"]["error"]]
    print(f"# {lang}: unlabelled={missing} no_help={missing_desc} untranslated_errors={bad_err}")
    print(f"RESULT unlabelled_fields_{lang}={len(missing)} count")
    print(f"RESULT no_help_fields_{lang}={len(missing_desc)} count")
    print(f"RESULT untranslated_errors_{lang}={len(bad_err)} count")

# Null control: the same keys against the options twin page and options.error --
# the namespace the options flow's own copy of this page reads.
twin = FILES["en"]["options"]["step"]["modbus_prefill"]["data"]
twin_missing = [k for k in keys if k not in twin]
twin_err = [e for e in errors if e not in FILES["en"]["options"]["error"]]
print(f"RESULT options_twin_unlabelled={len(twin_missing)} count")
print(f"RESULT options_twin_untranslated_errors={len(twin_err)} count")
print(f"RESULT preview_fields={len(keys)} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
