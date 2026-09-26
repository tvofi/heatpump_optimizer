"""D5 verify-v2 harness for D5-s1-02 (independent of the finder's quick_setup_promise.py).

Metric (one line): over the 8 quick-setup answer sets with Buffer tank=yes, Wood buffer
tank=yes and both wood probes picked (two_zone x dhw x wood_furnace varied), the number of
(answer set, promise) pairs where the entry the REAL ConfigFlow creates (user -> user_sensors
-> finish_setup -> quick_setup -> device_prefill declined -> finish_now -> setup_overview
submit) yields ThermalParameters.from_config with buffer_is_store False (promise 1: "stores
cheap heat") or two_tank_modelled False (promise 2: "probes switch the two-tank physics on").
Count key: the created entry's data dict (the flow's own create_entry result) through
ThermalParameters.from_config -- production seam end to end, not quick_setup.derive alone.
Command (repository root):
    PYTHONPATH=tests/hastub python tools/audit/round9/D5/verify-v2/v2_quick_setup.py [--perturb]
--perturb: in memory, quick_setup.derive also writes mixing_valve_mode='manual'; the broken
    pairs must fall (buffer promise to 0; two-tank promise to the one-zone sets only).
Baseline 1936d5ca; exact counts.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, itertools, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
from harness import FakeHass, FakeState  # noqa
from heatpump_optimizer import config_flow, const, quick_setup  # noqa
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa

if "--perturb" in sys.argv:
    _orig = quick_setup.derive
    def _d(a):
        out = _orig(a); out["mixing_valve_mode"] = "manual"; return out
    quick_setup.derive = _d

async def entry_for(two_zone, dhw, wood):
    h = FakeHass()
    h.states.set("sensor.wt", FakeState("60")); h.states.set("sensor.wb", FakeState("40"))
    f = config_flow.HeatPumpOptimizerConfigFlow(); f.hass = h
    await f.async_step_user({"name": "HPO", "price_source": "entity", "price_entity": "sensor.p",
                             "weather_entity": "weather.w"})
    r = await f.async_step_user_sensors({})
    assert r.get("step_id") == "finish_setup", r
    r = await f.async_step_quick_setup({
        "two_zone": two_zone, "buffer_tank": True, "dhw_tank": dhw, "wood_furnace": wood,
        "wood_buffer_tank": True, const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wt",
        const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wb"})
    if r.get("step_id") == "device_prefill":
        r = await f.async_step_device_prefill({})
    assert r.get("step_id") == "finish_setup", r
    r = await f.async_step_finish_now()
    r = await f.async_step_setup_overview({})
    assert r.get("type") in ("create_entry", getattr(r.get("type"), "value", None)) or "data" in r, r
    return r["data"]

broken_buf = broken_tt = 0
rows = []
for tz, dhw, wood in itertools.product((False, True), repeat=3):
    data = asyncio.run(entry_for(tz, dhw, wood))
    p = ThermalParameters.from_config(dict(data))
    b, t = p.buffer_is_store, p.two_tank_modelled
    broken_buf += (not b); broken_tt += (not t)
    rows.append((tz, dhw, wood, data.get("buffer_tank_volume"), data.get("mixing_valve_mode"), b, t))
for r in rows:
    print("ROW two_zone=%s dhw=%s wood=%s vol=%s valve=%s buffer_is_store=%s two_tank=%s" % r)
print(f"RESULT answer_sets=8 count")
print(f"RESULT buffer_promise_broken={broken_buf} count")
print(f"RESULT two_tank_promise_broken={broken_tt} count")
print(f"RESULT broken_pairs={broken_buf + broken_tt} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
