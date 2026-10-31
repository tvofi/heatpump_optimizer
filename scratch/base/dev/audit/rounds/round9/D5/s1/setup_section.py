"""D5-s1 harness: docs/configuration.md "Initial setup" against the real first-run flow.

Metric (one line): stale_facts = the menu entries the real ConfigFlow shows after the two
required screens that the "## Initial setup" section of docs/configuration.md never names,
plus 1 if that flow completes its first screen with no Tibber token while the section
marks the token "(**required**)" / "Only two answers are genuinely required: a Tibber
API token and a weather entity".
Count key: the result dicts HeatPumpOptimizerConfigFlow.async_step_user /
async_step_user_sensors return (type, step_id, menu_options) -- the production seam --
never the doc's own shape.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/setup_section.py [--perturb]
--perturb swaps, in memory, async_step_finish_setup for async_step_temperature (the
    pre-v6.6.5 straight-line wizard the section draws). Expected: stale_facts down (4 -> 1:
    the menu vanishes; the token claim stays wrong).
Expected at baseline: menu_entries=3, named_in_section=0, stale_facts=4 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    config_flow.HeatPumpOptimizerConfigFlow.async_step_finish_setup = (
        config_flow.HeatPumpOptimizerConfigFlow.async_step_temperature)

text = open("docs/configuration.md", encoding="utf-8").read()
section = text.split("## Initial setup", 1)[1].split("\n## ", 1)[0]


async def run():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    first = await flow.async_step_user({
        "name": "Heat Pump Optimizer",
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.nordpool",
        const.CONF_WEATHER_ENTITY: "weather.home",
    })
    second = await flow.async_step_user_sensors({})
    return first, second

first, second = asyncio.run(run())
tokenless_ok = first.get("step_id") == "user_sensors" and not first.get("errors")
menu = dict(second.get("menu_options") or {})
print("first screen ->", first.get("type"), first.get("step_id"), first.get("errors"))
print("after sensors ->", second.get("type"), second.get("step_id"), menu)
named = [lbl for lbl in menu.values() if re.sub(r"\s*\(.*?\)", "", lbl).lower() in section.lower()]
token_required_claim = bool(re.search(r"Tibber API token \| — \(\*\*required\*\*\)", section)) or \
    "genuinely required: a Tibber API token" in text
stale = (len(menu) - len(named)) + (1 if (tokenless_ok and token_required_claim) else 0)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT first_screen_accepted_without_token={int(tokenless_ok)} count")
print(f"RESULT doc_claims_token_required={int(token_required_claim)} count")
print(f"RESULT menu_entries={len(menu)} count")
print(f"RESULT named_in_section={len(named)} count")
print(f"RESULT stale_facts={stale} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
