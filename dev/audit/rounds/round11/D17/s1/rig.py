"""D17-s1 shared rig: an entry saved through the real options flow, and a
coordinator rebuilt from it (a restart) that runs full cycles on injected
series with the solve inline. Imported by the D17-s1 harnesses; not a harness.

Run from the export root with PYTHONPATH=tests/hastub. Thread pin first.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

sys.path[:0] = ["tests", "custom_components"]
_TMP = tempfile.mkdtemp(prefix="d17s1-")
os.environ.setdefault("HPO_PLANDATA", _TMP)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

STRINGS = json.loads(Path("custom_components/heatpump_optimizer/strings.json").read_text())
OPT_STEPS = STRINGS["options"]["step"]

BASE_DATA = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
BASE_STATES = {"sensor.indoor": "21.0", "sensor.outdoor": "-3.0"}


def thread_factor():
    pc, tc = time.process_time(), time.thread_time()
    return round(pc / tc, 3) if tc > 0 else 1.0


def load1():
    try:
        return os.getloadavg()[0]
    except OSError:
        return -1.0


def new_flow(data=None, options=None, entry_id="d17s1"):
    """A fresh install: the stub's process-wide store disk is emptied first, so no
    arm inherits another arm's persisted state (a restart inside one arm keeps it)."""
    from homeassistant.helpers import storage
    storage._reset_store_disk()
    hass = FakeHass()
    entry = FakeEntry(data=dict(data if data is not None else BASE_DATA),
                      options=dict(options or {}), entry_id=entry_id)
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
    flow.hass = hass
    return flow, entry, hass


def schema_defaults(form):
    """The form's own defaults, nested by section as HA submits them."""
    out = {}
    sch = form.get("data_schema")
    if sch is None:
        return out
    for key, val in sch.schema.items():
        name = str(key)
        if type(val).__name__ == "section":
            inner = {}
            for k2 in val.schema.schema:
                d = getattr(k2, "default", None)
                if d is not None and d is not __import__("voluptuous").UNDEFINED:
                    inner[str(k2)] = d() if callable(d) else d
            out[name] = inner
        else:
            d = getattr(key, "default", None)
            if d is not None and d is not __import__("voluptuous").UNDEFINED:
                out[name] = d() if callable(d) else d
    return out


def field_section(form, field):
    """The section name holding ``field`` in the form, or None for top level."""
    sch = form.get("data_schema")
    for key, val in sch.schema.items():
        if type(val).__name__ == "section":
            if any(str(k2) == field for k2 in val.schema.schema):
                return str(key)
        elif str(key) == field:
            return None
    return False


async def submit(flow, step, answers):
    from homeassistant.data_entry_flow import AbortFlow
    try:
        return await getattr(flow, f"async_step_{step}")(answers)
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


async def save_option(step, field, value, data=None, options=None, extra=None):
    """Open ``step``, submit its defaults with ``field`` set to ``value``.

    Returns (result, entry). ``extra`` maps further top-level/section fields."""
    flow, entry, hass = new_flow(data, options)
    form = await getattr(flow, f"async_step_{step}")(None)
    answers = schema_defaults(form)
    # a prerequisite that is a field of this page is submitted as its answer:
    # saving the page re-writes its own fields from the answers
    own = {k: v for k, v in (options or {}).items() if field_section(form, k) is not False}
    pairs = list(own.items()) + ([(field, value)] if field is not None else []) + list((extra or {}).items())
    for f, v in pairs:
        sec = field_section(form, f)
        if sec is False:
            answers[f] = v  # not rendered at this state: submit it anyway
        elif sec is None:
            answers[f] = v
        else:
            answers.setdefault(sec, {})[f] = v
    res = await submit(flow, step, answers)
    if res.get("type") == "create_entry" and res.get("data") is not None:
        entry.options = dict(res["data"])
    return res, entry


NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)  # a Thursday


def prices(now, n=50, flat=False):
    hour = now.replace(minute=0, second=0, microsecond=0)
    return [{"total": 0.8 if flat else round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (hour + timedelta(hours=h - 2)).isoformat(), "level": "NORMAL"}
            for h in range(n)]


def build_coord(entry, states=None, now=NOW, flat=False, seed=None):
    """A restart: a fresh coordinator from the entry's data and options."""
    dt_util.freeze(now)
    hass = FakeHass()
    for eid, st in {**BASE_STATES, **(states or {})}.items():
        hass.states.set(eid, st if isinstance(st, FakeState) else FakeState(str(st)))
    hass.config_entries.entries.append(entry)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = prices(now, flat=flat)
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -5.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

    async def _noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    if seed is not None:
        seed(coord)
    return hass, coord


async def _inline(hass, optimizer, inputs):
    return optimize_in_process(optimizer, inputs)


def run_cycles(coord, n=1):
    with mock.patch.object(cmod, "_await_optimize", _inline):
        async def go():
            out = None
            for _ in range(n):
                out = await coord._async_update_data()
            return out
        return asyncio.run(go())


def EntryConfig_of(coord):
    """The parsed configuration the coordinator was built with."""
    from heatpump_optimizer.entry_config import EntryConfig
    e = coord.entry
    return EntryConfig.from_mapping({**e.data, **e.options})


async def run_cycles_async(coord, n=1):
    with mock.patch.object(cmod, "_await_optimize", _inline):
        out = None
        for _ in range(n):
            out = await coord._async_update_data()
        return out
