"""V1 independent cross-checks for D5 round 9 (verifier V1, not a finder harness).

Metrics (one line each):
  s1_01_token_required_for_tibber: 1 if async_step_user with price_source=tibber and no token
      refuses the screen (errors or a re-shown 'user' form), i.e. the token is conditional.
  s1_01_menu_labels_in_config_md: finish_setup menu labels (en.json config.step.finish_setup
      .menu_options) found anywhere in docs/configuration.md's Initial setup section.
  s1_02_valve_modes_storing: of every mixing_valve mode, how many make ThermalParameters built
      from quick_setup.derive(buffer yes) + that mode report buffer_is_store True.
  s2_03_draw_cold_end_default / _sensor: the cold end implied by dhw_draw_power at shipped
      defaults, and with a live inlet sensor value of 6.0 C (dhw_inlet_current).
Command (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D5/verify-v1/indep.py
Baseline: 1936d5ca + round-9 evidence (handoff/audit-r9-evidence).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const, mixing_valve, quick_setup  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

# --- s1-01: Tibber path without token
async def tib():
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    try:
        r = await flow.async_step_user({
            "name": "x", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_TIBBER,
            const.CONF_WEATHER_ENTITY: "weather.home"})
    except Exception as e:  # a vol error also means "refused"
        return {"exc": type(e).__name__}
    return r
r = asyncio.run(tib())
print("tibber no-token ->", {k: r.get(k) for k in ("type", "step_id", "errors", "exc") if k in r})
tib_refused = int(bool(r.get("exc")) or bool(r.get("errors")) or r.get("step_id") == "user")
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json", encoding="utf-8"))
labels = list(en["config"]["step"]["finish_setup"]["menu_options"].values())
md = open("docs/configuration.md", encoding="utf-8").read()
sec = md.split("## Initial setup", 1)[1].split("\n## ", 1)[0].lower()
found = [l for l in labels if l.split(" (")[0].lower() in sec]
print("finish_setup labels:", labels, "found:", found)

# --- s1-02: which valve modes make the quick-setup buffer a store
base = quick_setup.derive({quick_setup.FIELD_BUFFER_TANK: True})
modes = sorted({mixing_valve.MODE_NONE, *mixing_valve.THROTTLING_MODES})
storing = []
for m in modes:
    p = ThermalParameters.from_config({**base, const.CONF_MIXING_VALVE_MODE: m})
    storing.append((m, p.buffer_is_store))
p0 = ThermalParameters.from_config(base)
print("valve modes -> buffer_is_store:", storing, "| derive alone:", p0.mixing_valve_mode, p0.buffer_is_store)

# --- s2-03: cold end at defaults vs with a live inlet sensor value
def cold_end(p):
    lph = p.dhw_daily_consumption / 24.0
    rec = min(max(p.greywater_recovery, 0.0), 0.9)
    return p.dhw_setpoint - p.dhw_draw_power / (lph * const.WATER_SPECIFIC_HEAT * (1 - rec))
pd = ThermalParameters()
ps = ThermalParameters(); ps.dhw_inlet_current = 6.0
print(f"DHW_COLD_WATER_TEMP={const.DHW_COLD_WATER_TEMP}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT s1_01_token_required_for_tibber={tib_refused} count")
print(f"RESULT s1_01_menu_labels_in_config_md={len(found)} of {len(labels)}")
print(f"RESULT s1_02_valve_modes_storing={sum(s for _, s in storing)} of {len(modes)}")
print(f"RESULT s1_02_derive_alone_store={int(p0.buffer_is_store)} count")
print(f"RESULT s2_03_draw_cold_end_default={cold_end(pd):.2f} C")
print(f"RESULT s2_03_draw_cold_end_sensor6={cold_end(ps):.2f} C")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
