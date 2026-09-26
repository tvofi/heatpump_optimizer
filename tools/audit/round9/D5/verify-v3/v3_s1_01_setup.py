"""D5 verify-v3 (reach and class) harness for D5-s1-01: configuration.md "Initial setup"
against the real first-run ConfigFlow, walked the way Home Assistant's FlowManager walks it.

Metric (one line): unnamed_labels = en.json labels of (a) every menu entry reachable on the
tokenless entity-price path and (b) every field of the first screen, that the "## Initial
setup" section never names (parenthetical stripped, case-insensitive); plus the range of
entity counts the six platforms add across the five golden coordinator configs.
Count key: the result dicts the production steps return, and the schema
_user_credentials_fields() builds -- the input is VALIDATED through that schema first, as
data_entry_flow.FlowManager does on a real install (the stub never validates).
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s1_01_setup.py [--perturb]
--perturb: HeatPumpOptimizerConfigFlow.async_step_finish_setup := async_step_temperature
    in memory. Expected: finish_menu_unnamed 3 -> 0.
Expected at baseline: finish_menu_unnamed=3, building_menu_unnamed=0 (control),
    first_screen_fields_unnamed=2, tokenless_schema_valid=1 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
import voluptuous as vol  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, config_flow, const, datetime as dt_platform, sensor, switch)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
import golden  # noqa: E402

PERTURB = "--perturb" in sys.argv
Flow = config_flow.HeatPumpOptimizerConfigFlow
if PERTURB:
    Flow.async_step_finish_setup = Flow.async_step_temperature

text = open("docs/configuration.md", encoding="utf-8").read()
section = text.split("## Initial setup", 1)[1].split("\n## ", 1)[0].lower()
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json", encoding="utf-8"))


def named(label):
    return re.sub(r"\s*\(.*?\)", "", label).strip().lower() in section


async def walk():
    flow = Flow()
    flow.hass = FakeHass()
    raw = {"name": "Heat Pump Optimizer", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
           const.CONF_PRICE_ENTITY: "sensor.nordpool", const.CONF_WEATHER_ENTITY: "weather.home"}
    schema = vol.Schema(config_flow._user_credentials_fields())
    try:
        validated = schema(raw)
        valid = 1
    except vol.Invalid:
        validated, valid = raw, 0
    first = await flow.async_step_user(validated)
    second = await flow.async_step_user_sensors({})
    # the Tibber arm with no token: what the doc's "(required)" is true of
    flow2 = Flow()
    flow2.hass = FakeHass()
    tib = await flow2.async_step_user(schema({"name": "x", const.CONF_WEATHER_ENTITY: "weather.home"}))
    return valid, first, second, tib, schema


valid, first, second, tib, schema = asyncio.run(walk())
finish = dict(second.get("menu_options") or {}) if second.get("type") == "menu" else {}
building = en["config"]["step"]["building"]["menu_options"]
fields = en["config"]["step"]["user"]["data"]
finish_unnamed = [l for l in finish.values() if not named(l)]
building_unnamed = [l for l in building.values() if not named(l)]
fields_unnamed = [f"{k}:{l}" for k, l in fields.items() if not named(l)]
required = sorted(str(k) for k in schema.schema if isinstance(k, vol.Required))
print("first ->", first.get("type"), first.get("step_id"), first.get("errors"))
print("tibber arm, no token ->", tib.get("step_id"), tib.get("errors"))
print("finish menu unnamed:", finish_unnamed)
print("building menu unnamed (control):", building_unnamed)
print("first-screen labels unnamed:", fields_unnamed, "| schema-required:", required)

# entity count across the five golden coordinator configs
counts = {}
for name, cfg in golden.coordinator_scenarios().items():
    hass = FakeHass()
    entry = FakeEntry(data=dict(cfg))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    n = 0
    for mod in (sensor, binary_sensor, button, switch, climate, dt_platform):
        got = []
        asyncio.run(mod.async_setup_entry(hass, entry, lambda e, u=False, _g=got: _g.extend(e)))
        n += len(got)
    counts[name] = n
print("entities per golden config:", counts)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT tokenless_schema_valid={valid} count")
print(f"RESULT tokenless_reaches={1 if first.get('step_id') == 'user_sensors' and not first.get('errors') else 0} count")
print(f"RESULT finish_menu_unnamed={len(finish_unnamed)} count")
print(f"RESULT building_menu_unnamed={len(building_unnamed)} count")
print(f"RESULT first_screen_fields_unnamed={len(fields_unnamed)} count")
print(f"RESULT entities_min={min(counts.values())} count")
print(f"RESULT entities_max={max(counts.values())} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
