"""Reproduce the class on PRODUCTION code (not copied expressions).

Every arm: seed the real store with an instant written while the clock ran
400 days ahead (T0+400d), restart (real loader) at the corrected clock T0, and
read the real gate 30 days later. Null arm: the same with an honest stamp.
Clamp arm: the stored stamp replaced by min(stamp, T0) -- what a clamp at the
restore site would load -- to check the clamp is the fix for that seam.
Run from repo root: PYTHONPATH=tests/hastub python3 <this>
"""
import asyncio, datetime as dt, json, logging, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path[:0] = [str(ROOT/"tests"), str(ROOT/"tests/hastub"), str(ROOT/"custom_components")]
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry
from heatpump_optimizer import const, boost, pump_arbiter
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.helpers import storage
from homeassistant.util import dt as dt_util

T0 = dt.datetime(2026, 1, 1, 12, 0, 0)
AHEAD = T0 + dt.timedelta(days=400)
D30 = T0 + dt.timedelta(days=30)
run = asyncio.run

def coord(extra=None):
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0}
    cfg.update(extra or {})
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))

def key_of(store):
    return store._key

out = {}

# --- legionella (NOT in S7's sweep: parse_datetime, not fromisoformat) ------
def legionella(stamp):
    storage._DISK.clear(); dt_util.freeze(T0)
    c = coord()
    storage._DISK[key_of(c._legionella.store)] = json.dumps({"last_cycle": stamp.isoformat()})
    run(c._legionella.async_load())
    c._thermal_params.dhw_legionella_enabled = True
    c._legionella._params = c._thermal_params if not callable(getattr(type(c._legionella), "_params", None)) else c._legionella._params
    dt_util.freeze(D30)
    return c._legionella.due_in_hours()
try:
    out["legionella_due_h_null"] = legionella(T0 - dt.timedelta(days=20))
    out["legionella_due_h_ahead"] = legionella(AHEAD)
    out["legionella_due_h_clamped"] = legionella(min(AHEAD, T0))
except Exception as e:
    out["legionella_err"] = repr(e)

# --- boost until (an EXPIRY: legitimately future) ----------------------------
def boost_active(stamp, at=D30):
    storage._DISK.clear(); dt_util.freeze(T0)
    c = coord()
    storage._DISK[key_of(boost._store(c))] = json.dumps({"dhw": {"until": stamp.isoformat()}})
    run(boost.restore(c))
    return boost.held_for(c).active("dhw", at)
out["boost_null_active_d30"] = boost_active(T0 + dt.timedelta(hours=1))
out["boost_ahead_active_d30"] = boost_active(AHEAD)
out["boost_clamp_to_now_active_d30"] = boost_active(min(AHEAD, T0))
# the regression a clamp-to-now parser would introduce on a LEGIT boost:
out["boost_legit_1h_left_active_after_restart_T0+30min"] = boost_active(T0 + dt.timedelta(hours=1), T0 + dt.timedelta(minutes=30))
out["boost_legit_clamped_to_now_active_T0+30min"] = boost_active(min(T0 + dt.timedelta(hours=1), T0), T0 + dt.timedelta(minutes=30))

# --- pump arbiter echo grace ------------------------------------------------
def echo_stamp_after_load(stamp):
    storage._DISK.clear(); dt_util.freeze(T0)
    c = coord()
    storage._DISK[key_of(pump_arbiter._store(c))] = json.dumps({"written": {"dhw_setpoint": [55.0, stamp.isoformat()]}})
    run(pump_arbiter._load(c))
    at = pump_arbiter.state_for(c).written["dhw_setpoint"][1]
    return (D30 - at).total_seconds() < pump_arbiter.ECHO_GRACE_S
out["echo_grace_open_d30_null"] = echo_stamp_after_load(T0 - dt.timedelta(minutes=5))
out["echo_grace_open_d30_ahead"] = echo_stamp_after_load(AHEAD)
out["echo_grace_open_d30_clamped"] = echo_stamp_after_load(min(AHEAD, T0))

# --- _detect_outage: restore and read share ONE now -------------------------
def outage(stamp, restart_at):
    dt_util.freeze(restart_at)
    c = coord({const.CONF_OUTAGE_RECOVERY_ENABLED: True})
    c._outage_recovery_until = None
    c._detect_outage(stamp.isoformat())
    return c._outage_recovery_until is not None
R6 = T0 + dt.timedelta(hours=6)   # restart after a real 6 h power cut
out["outage_flagged_null"] = outage(T0, R6)
out["outage_flagged_ahead"] = outage(AHEAD, R6)
out["outage_flagged_clamped_same_now"] = outage(min(AHEAD, R6), R6)

# --- heavy-snow damping ------------------------------------------------------
import numpy as np
def snow(stamp):
    dt_util.freeze(T0)
    c = coord({const.CONF_SNOW_ROOF_FACTOR_ENABLED: True})
    c._last_heavy_snow = stamp
    c._snow_accum_last = None
    c._snow_accum_cm = 0.0
    return c._update_snow_memory(D30, np.zeros(4))
out["snow_damped_d30_null"] = snow(T0)
out["snow_damped_d30_ahead"] = snow(AHEAD)
out["snow_damped_d30_clamped"] = snow(min(AHEAD, T0))

# --- immersion recency -------------------------------------------------------
def immersion(stamps):
    dt_util.freeze(D30)
    c = coord({const.CONF_IMMERSION_FEEDBACK_ENABLED: True})
    c._immersion_events = [s.isoformat() for s in stamps]
    fn = [n for n in dir(c) if "immersion" in n and callable(getattr(c, n))]
    return fn
out["immersion_methods"] = immersion([AHEAD]*3)
for k, v in out.items():
    print(f"RESULT {k}={v}")
