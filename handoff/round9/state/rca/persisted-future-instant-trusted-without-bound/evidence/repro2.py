import asyncio, datetime as dt, json, logging, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path[:0] = [str(ROOT/"tests"), str(ROOT/"tests/hastub"), str(ROOT/"custom_components")]
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry
from heatpump_optimizer import const
from heatpump_optimizer.ledger import month_key
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.helpers import storage
from homeassistant.util import dt as dt_util
T0 = dt.datetime(2026, 1, 1, 12, 0, 0)
run = asyncio.run
def coord(extra=None):
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0}
    cfg.update(extra or {})
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))

# fuse advisor: the stored month is written by the SAME clock as the stamp.
def fuse(write_at, read_at, month_from=None):
    storage._DISK.clear(); dt_util.freeze(read_at)
    c = coord({const.CONF_MAIN_FUSE_A: 25})
    storage._DISK[c._ledger_store._key] = json.dumps({
        "fuse_advisor": {"month": month_key(month_from or write_at), "candidate_kw": 1.0},
        "fuse_advisor_at": write_at.isoformat()})
    try:
        run(c._maybe_run_fuse_advisor())
    except Exception as e:
        return f"ran-past-gate({type(e).__name__})"
    return "gated" if c._fuse_advisor_at == write_at else "ran-past-gate"
print("RESULT fuse_null_day6", fuse(T0, T0 + dt.timedelta(days=6)))
print("RESULT fuse_null_day8", fuse(T0, T0 + dt.timedelta(days=8)))
print("RESULT fuse_ahead400_sameclock_month_day30", fuse(T0 + dt.timedelta(days=400), T0 + dt.timedelta(days=30)))
print("RESULT fuse_ahead400_probe_assumed_month_day30", fuse(T0 + dt.timedelta(days=400), T0 + dt.timedelta(days=29), month_from=T0 + dt.timedelta(days=29)))
print("RESULT fuse_ahead5d_sameclock_day10", fuse(T0 + dt.timedelta(days=5), T0 + dt.timedelta(days=10)))
print("RESULT fuse_ahead5d_sameclock_day31(Feb1)", fuse(T0 + dt.timedelta(days=5), T0 + dt.timedelta(days=31)))

# immersion recency
def imm(stamps, at):
    dt_util.freeze(at)
    c = coord({const.CONF_IMMERSION_FEEDBACK_ENABLED: True})
    c._immersion_events = [s.isoformat() for s in stamps]
    return c._immersion_dhw_margin(at)
D30 = T0 + dt.timedelta(days=30); A = T0 + dt.timedelta(days=400)
print("RESULT immersion_margin_null", imm([T0]*3, D30))
print("RESULT immersion_margin_ahead", imm([A]*3, D30))
print("RESULT immersion_margin_ahead_one", imm([A] + [T0]*2, D30))
print("RESULT immersion_margin_clamped", imm([min(A, T0)]*3, D30))
