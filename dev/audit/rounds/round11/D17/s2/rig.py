"""D17-s2 shared rig: walk the real initial config flow, build a coordinator
from the entry it creates, run one real cycle, fingerprint what is observable.

Not a harness on its own (no RESULT lines); imported by the harnesses beside it.
Run from the export root with PYTHONPATH=tests/hastub.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d17s2-"))
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)  # a Thursday


class _Resp:
    def __init__(self, status, payload):
        self.status, self._p = status, payload

    async def json(self):
        return self._p

    async def __aenter__(self):
        return self

    async def __aexit__(self, *e):
        return False


class _Session:
    def post(self, *a, **k):
        return _Resp(200, {"data": {"viewer": {"name": "Home"}}})


config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _Session()

FIRST = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "tok-a",
         const.CONF_WEATHER_ENTITY: "weather.home"}
SENSORS = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}
TEMPERATURE = {const.CONF_TARGET_TEMP: 21.0, const.CONF_MIN_TEMP: 19.0, const.CONF_MAX_TEMP: 23.0,
               const.CONF_COMFORT_TEMP_DAY: 21.0, const.CONF_COMFORT_TEMP_NIGHT: 19.5,
               const.CONF_DAY_START_HOUR: 7, const.CONF_DAY_END_HOUR: 22}
THERMAL = {const.CONF_HOUSE_THERMAL_MASS: 10.0, const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.15,
           const.CONF_SLAB_THERMAL_MASS: 5.0, const.CONF_SLAB_HEAT_TRANSFER: 0.8,
           const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5, const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
           const.CONF_HEAT_PUMP_MIN_POWER: 1.0, const.CONF_OPTIMIZATION_INTERVAL: 30,
           const.CONF_PRICE_WEIGHT: 1.0, const.CONF_COMFORT_WEIGHT: 5.0}
ZONES = {"two_zone": False, const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
         const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0, const.CONF_UPPER_FLOOR_HEAT_LOSS: 0.08,
         const.CONF_LOWER_FLOOR_HEAT_LOSS: 0.07, const.CONF_INTER_ZONE_TRANSFER: 0.1,
         const.CONF_RADIATOR_POWER_FRACTION: 0.4, const.CONF_UPPER_FLOOR_AREA_RATIO: 0.5,
         const.CONF_BUFFER_TANK_VOLUME: 35.0, const.CONF_WINDOW_AREA: 10.0,
         const.CONF_SOLAR_ORIENTATION_FACTOR: 1.0, const.CONF_SOLAR_HEAT_GAIN_COEFF: 0.6}
DHW = {const.CONF_DHW_ENABLED: True, const.CONF_DHW_TANK_VOLUME: 200.0, const.CONF_DHW_SETPOINT: 52.0,
       const.CONF_DHW_MIN_TEMP: 42.0, const.CONF_DHW_DAILY_CONSUMPTION: 200.0,
       const.CONF_DHW_COOLING_RATE: 0.2, const.CONF_DHW_SCHEDULE_ENABLED: True,
       const.CONF_DHW_WINDOWS: "06:00-08:30, 17:00-22:00", const.CONF_DHW_IDLE_MIN_TEMP: 20.0,
       const.CONF_DHW_LEGIONELLA_ENABLED: True, const.CONF_DHW_LEGIONELLA_TEMP: 60.0,
       const.CONF_DHW_LEGIONELLA_INTERVAL_DAYS: 7}
WEATHER = {const.CONF_WIND_SENSITIVITY: 0.03, const.CONF_RAIN_HEAT_LOSS_MULTIPLIER: 1.15}
QUESTIONNAIRE = None  # filled lazily (presets import)
EXTRAS = {const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5, const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
          const.CONF_HEAT_PUMP_MIN_POWER: 1.0}


def questionnaire():
    from heatpump_optimizer.presets import (EMITTER_FLOOR, EMITTER_RADIATORS, ERA_1980_2005,
                                            FOUNDATION_NONE, STRUCTURE_TIMBER_SLAB)
    return {const.CONF_BUILDING_STRUCTURE: STRUCTURE_TIMBER_SLAB, const.CONF_BUILDING_ERA: ERA_1980_2005,
            const.CONF_BUILDING_FOUNDATION: FOUNDATION_NONE, const.CONF_HEATED_AREA: 140.0,
            const.CONF_UPPER_EMITTER: EMITTER_RADIATORS, const.CONF_LOWER_EMITTER: EMITTER_FLOOR}


async def _submit(flow, step, answers):
    try:
        return await getattr(flow, f"async_step_{step}")(dict(answers) if answers is not None else None)
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


async def _walk(path, ov):
    """Walk one path; ov maps step -> overrides for that page. Returns (result, flow)."""
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    pages = {"user": dict(FIRST), "user_sensors": dict(SENSORS), "temperature": dict(TEMPERATURE),
             "thermal": dict(THERMAL), "zones": dict(ZONES), "dhw": dict(DHW), "weather_sensitivity": dict(WEATHER),
             "building_describe": questionnaire(), "building_extras": dict(EXTRAS)}
    for step, o in ov.items():
        pages.setdefault(step, {}).update(o)
        for k in [k for k, v in o.items() if v is _DROP]:
            del pages[step][k]
    r = await _submit(flow, "user", pages["user"])
    assert r.get("step_id") == "user_sensors", r
    r = await _submit(flow, "user_sensors", pages["user_sensors"])
    assert r.get("step_id") == "finish_setup", r
    if path == "finish_now":
        r = await _submit(flow, "finish_now", {})
    elif path.startswith("quick"):
        qs = {**questionnaire(), "two_zone": False, "buffer_tank": False, "dhw_tank": True,
              "wood_furnace": False, "wood_buffer_tank": False, **pages.get("quick_setup", {})}
        r = await _submit(flow, "quick_setup", qs)
        assert r.get("step_id") == "device_prefill", r
        r = await _submit(flow, "device_prefill", {})
        assert r.get("step_id") == "finish_setup", r
        if path == "quick_continue":
            r = await _submit(flow, "temperature", pages["temperature"])
            for s in ("building_extras",):
                pass
            assert r.get("step_id") == "building", r
            for s in ("building_describe", "building_extras", "dhw", "weather_sensitivity"):
                r = await _submit(flow, s, pages[s])
        else:
            r = await _submit(flow, "finish_now", {})
    else:
        r = await _submit(flow, "temperature", pages["temperature"])
        assert r.get("step_id") == "building", r
        if path == "expert":
            for s in ("thermal", "zones", "dhw", "weather_sensitivity"):
                r = await _submit(flow, s, pages[s])
        else:  # questionnaire
            for s in ("building_describe", "building_extras", "dhw", "weather_sensitivity"):
                r = await _submit(flow, s, pages[s])
    assert r.get("step_id") == "setup_overview", r
    r = await _submit(flow, "setup_overview", {})
    assert r.get("type") == "create_entry", r
    return r, flow


_DROP = object()


def walk(path="expert", **ov):
    return asyncio.run(_walk(path, ov))[0]["data"]


def series(coord, outdoor=-5.0, wind=3.0, rain=0.0, solar=None, price=None):
    coord._prices = [{"total": (price(h) if price else round(0.6 + 0.5 * (h % 12) / 12.0, 4)),
                      "starts_at": (NOW + timedelta(hours=h - 2)).isoformat(), "level": "NORMAL"}
                     for h in range(50)]
    coord._weather_forecast = [{"datetime": (NOW + timedelta(hours=h)).isoformat(),
                                "temperature": outdoor, "wind_speed": wind,
                                "precipitation": rain, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = solar if solar is not None else [
        max(0.0, 300.0 * (1 - abs(12 - ((h + 6) % 24)) / 6.0)) for h in range(48)]


async def _noop(*a, **k):
    return None


async def _inline(hass, optimizer, inputs):
    return optimize_in_process(optimizer, inputs)


def build(data, states=None, options=None, hass=None, entry_id="d17s2", **series_kw):
    hass = hass or FakeHass()
    base = {"sensor.indoor": "21.0", "sensor.outdoor": "-3.0"}
    base.update(states or {})
    for k, v in base.items():
        hass.states.set(k, v if isinstance(v, FakeState) else FakeState(v))
    entry = FakeEntry(data=data, options=options or {}, entry_id=entry_id)
    coord = cmod.HeatPumpOptimizerCoordinator(hass, entry)
    series(coord, **series_kw)
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    return hass, entry, coord


def cycle(coord, now=NOW):
    """One real cycle: input read + solve (inline transport) + data dict."""
    dt_util.freeze(now)
    orig = cmod._await_optimize
    cmod._await_optimize = _inline
    try:
        asyncio.run(coord._update_current_state())
        reason = asyncio.run(coord.async_run_optimization())
        data = coord._build_data_dict()
    finally:
        cmod._await_optimize = orig
    return reason, coord._optimization_result, data


def _r(v):
    if isinstance(v, float):
        return None if not math.isfinite(v) else round(v, 4)
    if isinstance(v, (list, tuple)):
        return [_r(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _r(x) for k, x in v.items()}
    if isinstance(v, (int, str, bool)) or v is None:
        return v
    if isinstance(v, datetime):
        return v.isoformat()
    return repr(type(v).__name__)


PLAN_FIELDS = ("power_schedule", "room_temp_trajectory", "slab_temp_trajectory", "optimal_setpoints",
               "dhw_power_schedule", "upper_temp_trajectory", "lower_temp_trajectory",
               "solar_gain_trajectory", "buffer_temp_trajectory", "heat_pump_on_schedule",
               "predicted_cost", "baseline_cost")


def plan_fp(result):
    if result is None:
        return {}
    return {f: _r(getattr(result, f, None)) for f in PLAN_FIELDS}


def diff_keys(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
