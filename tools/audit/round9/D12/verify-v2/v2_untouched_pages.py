"""D12 verify-v2 for D12-s1-02: untouched options pages over a real "Finish setup now" entry.

Metric: over the entry the shipping initial flow creates on user ->
user_sensors (indoor + outdoor mapped) -> finish_setup -> "Finish setup now"
-> overview submit (built by driving HeatPumpOptimizerConfigFlow, not typed
by hand), open every options page of HeatPumpOptimizerOptionsFlow in
_TOP_MENU + _ADVANCED_MENU that renders a form, submit it untouched the way
the frontend does (defaults posted, sections nested; v2_flowlib), and count
the pages after whose save ThermalParameters.from_config(data|options)
.dhw_enabled or .two_zone_enabled differs from the unsaved entry. Count key:
the model parameters the coordinator builds, not the stored keys. For every
flipping page, one coordinator cycle is run and its plan's DHW steps (> 1e-6
kW) and kWh reported.

Perturbation --fallback: add CONF_DHW_WINDOWS and CONF_DHW_TANK_VOLUME to
config_flow._ABSENT_FALLBACKS at their shipped defaults (treat an untouched
default as unchanged). Expected: flipping pages -> 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_untouched_pages.py [--fallback]
Expected: flipping pages = 2 (hot_water, hot_water_tank), exact; 0 under --fallback.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 vCPU, CPython 3.14.0rc2.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v2_flowlib import post_untouched  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import config_flow as cf, const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from golden import START  # noqa: E402

logging.disable(logging.CRITICAL)
if "--fallback" in sys.argv:
    cf._ABSENT_FALLBACKS[const.CONF_DHW_WINDOWS] = const.DEFAULT_DHW_WINDOWS
    cf._ABSENT_FALLBACKS[const.CONF_DHW_TANK_VOLUME] = const.DEFAULT_DHW_TANK_VOLUME


async def _ok(*_a, **_k):
    return "ok"


cf.validate_tibber_token = _ok

STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("0.0", unit="°C"),
          "weather.home": FakeState("cloudy")}


async def finish_now_entry():
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass(dict(STATES))
    form = await flow.async_step_user(None)
    post = post_untouched(form)
    post.update({const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"})
    r = await flow.async_step_user(post)
    assert r.get("step_id") == "user_sensors", r.get("step_id")
    post = post_untouched(r)
    flat = cf._flatten_section_input(post)
    flat.update({"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"})
    r = await flow.async_step_user_sensors(flat)
    assert r.get("step_id") == "finish_setup", r.get("step_id")
    r = await flow.async_step_finish_now(None)
    r = await flow.async_step_setup_overview({})
    assert r["type"] == "create_entry", r
    return dict(r["data"])


def plant(cfg):
    p = ThermalParameters.from_config(cfg)
    return (bool(p.dhw_enabled), bool(p.two_zone_enabled))


def one_cycle(cfg):
    async def _prices(self):
        self._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                        for h in range(48)]
        self._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                   "temperature": 0.0, "wind_speed": 2.0, "precipitation": 0.0,
                                   "humidity": 80.0} for h in range(48)]

    async def _noop(self):
        return None
    C = cm.HeatPumpOptimizerCoordinator
    saved = (C._fetch_tibber_prices, C._fetch_weather_forecast, C._fetch_solar_forecast)
    C._fetch_tibber_prices, C._fetch_weather_forecast, C._fetch_solar_forecast = _prices, _noop, _noop
    dt_util.freeze(START)
    try:
        hass = FakeHass(dict(STATES))
        entry = FakeEntry(data=dict(cfg))
        asyncio.run(integ.async_setup_entry(hass, entry))
        coord = entry.runtime_data
        asyncio.run(coord.async_refresh())
        res = coord._optimization_result
        sched = [float(x) for x in (res.dhw_power_schedule or [])] if res else []
        return sum(1 for x in sched if x > 1e-6), round(sum(sched) * 0.25, 2)
    finally:
        dt_util.freeze(None)
        C._fetch_tibber_prices, C._fetch_weather_forecast, C._fetch_solar_forecast = saved


async def page(data, step):
    entry = FakeEntry(data=dict(data))
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass(dict(STATES))
    h = getattr(flow, f"async_step_{step}", None)
    if h is None:
        return None, "no_step"
    try:
        form = await h(None)
    except Exception as e:  # noqa: BLE001
        return None, f"open_error:{type(e).__name__}"
    if form.get("type") != "form":
        return None, f"not_form:{form.get('type')}"
    try:
        r = await h(post_untouched(form))
    except Exception as e:  # noqa: BLE001
        return None, f"submit_error:{type(e).__name__}:{e}"
    if r.get("type") == "form" and r.get("errors"):
        return None, f"refused:{r.get('errors')}"
    return {**entry.data, **entry.options}, "saved"


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    data = asyncio.run(finish_now_entry())
    base = plant(data)
    print(f"ENTRY keys={sorted(data)} dhw_enabled_key={const.CONF_DHW_ENABLED in data} plant={base}")
    ctrl_steps, ctrl_kwh = one_cycle(data)
    print(f"RESULT control_unsaved_dhw_steps={ctrl_steps} count")
    print(f"RESULT control_unsaved_dhw_kwh={ctrl_kwh} kWh")
    steps = list(cf.HeatPumpOptimizerOptionsFlow._TOP_MENU) + list(cf.HeatPumpOptimizerOptionsFlow._ADVANCED_MENU)
    flips, tried = [], 0
    for s in steps:
        cfg, why = asyncio.run(page(data, s))
        if cfg is None:
            print(f"PAGE {s}: {why}")
            continue
        tried += 1
        pl = plant(cfg)
        added = sorted(k for k in cfg if k not in data)
        moved = pl != base
        print(f"PAGE {s}: saved plant={pl} moved={moved} added={added}")
        if moved:
            n, kwh = one_cycle(cfg)
            print(f"RESULT page_{s}_dhw_steps={n} count")
            print(f"RESULT page_{s}_dhw_kwh={kwh} kWh")
            flips.append(s)
    print(f"RESULT pages_saved_untouched={tried} count")
    print(f"RESULT pages_flipping_plant={len(flips)} count ({','.join(flips)})")
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
