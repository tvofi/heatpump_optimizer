"""Every instance through its REAL store and loader, then its real gate.
Run on a tree from the repository root: PYTHONPATH=tests/hastub python3 <this>
Stamp written 400 d ahead (AHEAD); restart at T0; gate read at T0+30 d
(or as stated). Null: the same with an honest stamp."""
import asyncio, datetime as dt, json, logging, sys
from pathlib import Path
sys.path[:0] = [str(Path.cwd()/"tests"), str(Path.cwd()/"tests/hastub"), str(Path.cwd()/"custom_components")]
logging.disable(logging.CRITICAL)
import numpy as np
from harness import FakeHass, FakeEntry
from heatpump_optimizer import const, boost, pump_arbiter
from heatpump_optimizer.ledger import month_key
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.helpers import storage
from homeassistant.util import dt as dt_util
T0 = dt.datetime(2026, 1, 1, 12); AHEAD = T0 + dt.timedelta(days=400); D30 = T0 + dt.timedelta(days=30)
run = asyncio.run
def coord(**extra):
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0, const.CONF_OUTAGE_RECOVERY_ENABLED: True,
           const.CONF_SNOW_ROOF_FACTOR_ENABLED: True, const.CONF_IMMERSION_FEEDBACK_ENABLED: True,
           const.CONF_MAIN_FUSE_A: 25}
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
def seed(store, payload):
    storage._DISK[store._key] = json.dumps(payload)

def legionella(stamp):
    storage._DISK.clear(); dt_util.freeze(T0); c = coord()
    seed(c._legionella.store, {"last_cycle": stamp.isoformat()}); run(c._legionella.async_load())
    c._thermal_params.dhw_legionella_enabled = True; dt_util.freeze(D30)
    return c._legionella.due_in_hours()
def boost_active(stamp, at):
    storage._DISK.clear(); dt_util.freeze(T0); c = coord()
    seed(boost._store(c), {"dhw": {"until": stamp.isoformat()}}); run(boost.restore(c))
    return boost.held_for(c).active("dhw", at)
def echo(stamp):
    storage._DISK.clear(); dt_util.freeze(T0); c = coord()
    seed(pump_arbiter._store(c), {"written": {"dhw_setpoint": [55.0, stamp.isoformat()]}}); run(pump_arbiter._load(c))
    return (D30 - pump_arbiter.state_for(c).written["dhw_setpoint"][1]).total_seconds() < pump_arbiter.ECHO_GRACE_S
def thermal(payload, at):
    storage._DISK.clear(); dt_util.freeze(T0); c = coord()
    seed(c._thermal_learning_store, payload); run(c._async_load_thermal_learning()); dt_util.freeze(at)
    return c
def snow(stamp):
    c = thermal({"last_heavy_snow": stamp.isoformat()}, D30)
    c._snow_accum_last = None; c._snow_accum_cm = 0.0
    return c._update_snow_memory(D30, np.zeros(4))
def immersion(stamp):
    c = thermal({"immersion_events": [stamp.isoformat()] * 3}, D30)
    return c._immersion_dhw_margin(D30)
def outage(stamp):
    storage._DISK.clear(); R6 = T0 + dt.timedelta(hours=6); dt_util.freeze(R6); c = coord()
    seed(c._energy_store, {"last_tick": stamp.isoformat()}); run(c._async_load_energy_totals())
    return c._outage_recovery_until is not None
def fuse(stamp, at):
    """Restart (and the lazy ledger read) at T0; the gate read again at ``at``."""
    storage._DISK.clear(); dt_util.freeze(T0); c = coord()
    seed(c._ledger_store, {"fuse_advisor": {"month": month_key(T0), "candidate_kw": 1.0}, "fuse_advisor_at": stamp.isoformat()})
    for when in (T0, at):
        dt_util.freeze(when)
        before = c._fuse_advisor_at
        try: run(c._maybe_run_fuse_advisor())
        except Exception: pass
    return c._fuse_advisor_at == before  # True: the second read was still held by the cooldown

H = T0 - dt.timedelta(days=20)
rows = [
  ("legionella_due_in_h_at_d30", lambda s: legionella(s), H),
  ("boost_active_at_d30", lambda s: boost_active(s, D30), T0 + dt.timedelta(hours=1)),
  ("boost_legit_1h_active_at_T0+30min", lambda s: boost_active(s, T0 + dt.timedelta(minutes=30)), T0 + dt.timedelta(hours=1)),
  ("echo_grace_open_at_d30", echo, T0 - dt.timedelta(minutes=5)),
  ("snow_damped_at_d30", snow, H),
  ("immersion_margin_at_d30", immersion, H),
  ("outage_flagged_after_6h_cut", outage, T0),
  ("fuse_gated_at_d10_same_month", lambda s: fuse(s, T0 + dt.timedelta(days=10)), T0),
]
for name, fn, honest in rows:
    stamp = AHEAD if "legit" not in name else honest
    print(f"RESULT {name} null={fn(honest)} skewed={fn(stamp if 'fuse' not in name else T0 + dt.timedelta(days=5))}")
