"""D12 verify-v2 for D12-s3-01: which initial-flow paths create an entry that models a DHW tank or a second zone nobody affirmed.

Paths (driven through HeatPumpOptimizerConfigFlow, every form submitted the way
the frontend submits an untouched form -- v2_flowlib.post_untouched; the
user step fills token + weather, user_sensors maps indoor + outdoor; quick
setup answers every house question "no"):
  finish_now            user -> user_sensors -> finish_setup:finish_now -> overview
  wizard_describe       ... finish_setup:temperature -> building:building_describe -> building_extras -> dhw -> weather -> overview
  wizard_thermal        ... finish_setup:temperature -> building:thermal -> zones -> dhw -> weather -> overview
  quick_no_finish       ... finish_setup:quick_setup(no) -> device_prefill(no device) -> finish_setup:finish_now -> overview
  quick_no_wizard       ... quick_setup(no) -> device_prefill(no device) -> finish_setup:temperature -> describe path
Metric: paths whose created entry, after integration setup and one
coordinator cycle, publishes a DHW plan (any dhw_power_schedule step > 1e-6
kW) or runs the two-zone model (coordinator._thermal_model.params
.two_zone_enabled with non-empty OptimizationResult.upper_setpoints), with no
answer on that path affirming either. Count key: the coordinator's model and
plan, not the stored keys.

Perturbation --explicit: thermal_model._dhw_enabled_from_config patched to
honour only an explicit dhw_enabled (absent -> False), and
ThermalParameters.from_config fed two_zone_mode "off" when the key is absent.
Expected: invented paths -> 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_wizard_paths.py [--explicit]
Expected: invented paths = 2 (wizard_describe: DHW; wizard_thermal: DHW + two-zone), exact.
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
from heatpump_optimizer import config_flow as cf, const, quick_setup, thermal_model  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from golden import START  # noqa: E402

logging.disable(logging.CRITICAL)


async def _ok(*_a, **_k):
    return "ok"


cf.validate_tibber_token = _ok
cf._prefill_offer_stored = lambda *_a, **_k: False

if "--explicit" in sys.argv:
    thermal_model._dhw_enabled_from_config = lambda c: bool(c.get(const.CONF_DHW_ENABLED, False))
    _orig_fc = thermal_model.ThermalParameters.from_config.__func__

    def _fc(cls, config):
        return _orig_fc(cls, {const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_OFF, **config})
    thermal_model.ThermalParameters.from_config = classmethod(_fc)

STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("0.0", unit="°C"),
          "weather.home": FakeState("cloudy")}


async def drive(route):
    """route: list of menu choices taken, in order, whenever a menu shows."""
    flow = cf.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass(dict(STATES))
    r = await flow.async_step_user(None)
    choices = list(route)
    trail = []
    for _ in range(30):
        if r["type"] == "create_entry":
            return dict(r["data"]), trail
        if r["type"] == "menu":
            pick = choices.pop(0)
            assert pick in r["menu_options"], (pick, r["menu_options"])
            trail.append(f"{r['step_id']}:{pick}")
            r = await getattr(flow, f"async_step_{pick}")(None)
            continue
        step = r["step_id"]
        trail.append(step)
        post = post_untouched(r)
        if step == "user":
            post.update({const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"})
        elif step == "user_sensors":
            post = cf._flatten_section_input(post)
            post.update({"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"})
        elif step == "quick_setup":
            for q in quick_setup.FIELD_QUESTIONS:
                post[q] = False
        elif step == "device_prefill":
            post = {}
        elif step == "setup_overview":
            post = {}
        r = await getattr(flow, f"async_step_{step}")(post)
        if r["type"] == "form" and r.get("errors") and r["step_id"] == step:
            raise AssertionError(f"{step} refused: {r['errors']}")
    raise AssertionError(f"no create_entry: {trail}")


ROUTES = {
    "finish_now": ["finish_now"],
    "wizard_describe": ["temperature", "building_describe"],
    "wizard_thermal": ["temperature", "thermal"],
    "quick_no_finish": ["quick_setup", "finish_now"],
    "quick_no_wizard": ["quick_setup", "temperature", "building_describe"],
}


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
        dsteps = sum(1 for x in (res.dhw_power_schedule or []) if float(x) > 1e-6) if res else 0
        dkwh = round(sum(float(x) for x in (res.dhw_power_schedule or [])) * 0.25, 2) if res else 0
        tz = bool(coord._thermal_model.params.two_zone_enabled) and bool(res and res.upper_setpoints)
        return dsteps, dkwh, tz, (round(float(res.predicted_cost), 3) if res else None)
    finally:
        dt_util.freeze(None)
        C._fetch_tibber_prices, C._fetch_weather_forecast, C._fetch_solar_forecast = saved


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    invented = inv_dhw = inv_tz = 0
    for name, route in ROUTES.items():
        cfg, trail = asyncio.run(drive(route))
        dsteps, dkwh, tz, cost = one_cycle(cfg)
        flags = {k: cfg.get(k) for k in (const.CONF_DHW_ENABLED, const.CONF_TWO_ZONE_MODE, const.CONF_DHW_TANK_VOLUME)}
        bad = dsteps > 0 or tz
        invented += bad
        inv_dhw += dsteps > 0
        inv_tz += tz
        print(f"PATH {name}: trail={'>'.join(trail)} flags={flags} dhw_steps={dsteps} dhw_kwh={dkwh} two_zone={tz} cost={cost}")
        print(f"RESULT {name}_dhw_plan_steps={dsteps} count")
        print(f"RESULT {name}_two_zone_model={int(tz)} flag")
    print(f"RESULT paths={len(ROUTES)} count")
    print(f"RESULT invented_paths={invented} count")
    print(f"RESULT invented_dhw_paths={inv_dhw} count")
    print(f"RESULT invented_two_zone_paths={inv_tz} count")
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
