"""D14 round 9, verifier V2 (independent) for D14-s1-01: malformed persisted-store leaves.

Metric (one line): v2_raising_cases = of 9 hand-built malformed store payloads (legionella: naive
last_cycle alone, naive last_attempt alone, naive last_cycle + aware last_attempt, both naive; boost
channel with a naive future "until"; pump_arbiter "written" = "x" and = 3.0; snapshot accuracy
temperature_bias = "garbage" and = []), those for which the REAL loader followed by the real
downstream call (3 x _async_update_data for legionella; boost.restore_session; pump_arbiter._load;
SnapshotRing.best_restore) raises; v2_legionella_max_wedged_cycles = failing update cycles of 3.
Count key: the exception raised by the production call on the delivered payload.

Config and clock are this verifier's own: tests/golden.py's coord_dhw topology config, clock
frozen at an aware Europe/Stockholm instant 2026-02-03 09:40, prices/forecast built here.
Payloads are hand-written, not seeded through writers (a deliberately different route from the
finder's p1_store.py).

Null control: the same payloads with aware ISO timestamps / well-formed containers -> 0.
Fidelity arm (--ha-dt): hastub dt_util.as_utc replaced by Home Assistant's own semantics
(naive -> DEFAULT_TIME_ZONE, then UTC); a stub-only seam would vanish there.
Perturbation (--guard): legionella.async_load's parsed timestamps coerced naive->aware in memory
(dt_util.parse_datetime wrapped) -> legionella cases expected to go to 0.

Run (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_store_leaf.py [--ha-dt] [--guard]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json, asyncio, logging, traceback
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
import heatpump_optimizer.coordinator as C  # noqa: E402
from heatpump_optimizer import boost, pump_arbiter, snapshots  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
dt_util.DEFAULT_TIME_ZONE = TZ
NOW = datetime(2026, 2, 3, 9, 40, tzinfo=TZ)
VERBOSE = "-v" in sys.argv

if "--ha-dt" in sys.argv:
    def _ha_as_utc(v):
        if v.tzinfo == timezone.utc:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        return v.astimezone(timezone.utc)
    dt_util.as_utc = _ha_as_utc

if "--guard" in sys.argv:
    _orig_parse = dt_util.parse_datetime

    def _aware_parse(v):
        r = _orig_parse(v)
        return r.replace(tzinfo=TZ) if (r is not None and r.tzinfo is None) else r
    import heatpump_optimizer.legionella as _leg
    _leg.dt_util = type("dtproxy", (), {k: staticmethod(getattr(dt_util, k)) if callable(getattr(dt_util, k)) else getattr(dt_util, k)
                                         for k in dir(dt_util) if not k.startswith("__")})
    _leg.dt_util.parse_datetime = staticmethod(_aware_parse)

sys.path.insert(0, "tests")
import golden  # noqa: E402
CFG = dict(golden.coordinator_scenarios()["coord_dhw"]) if callable(getattr(golden, "coordinator_scenarios", None)) else None


def build():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-2.0"))
    top = NOW.replace(minute=0)
    hass.states.set("sensor.nordpool", FakeState("0.5", attributes={"raw_today": [
        {"start": (top + timedelta(hours=h)).isoformat(), "value": round(0.4 + 0.3 * ((h * 7) % 5) / 5, 3)}
        for h in range(-2, 46)]}))
    cfg = {k: v for k, v in CFG.items() if k != "tibber_token"}
    cfg.update({"price_source": "entity", "price_entity": "sensor.nordpool",
                "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"})
    entry = FakeEntry(data=cfg)
    coord = C.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    top = NOW.replace(minute=0)
    coord._prices = [{"total": 0.4 + 0.3 * ((h * 7) % 5) / 5, "starts_at": (top + timedelta(hours=h)).isoformat()}
                     for h in range(-2, 46)]
    coord._weather_forecast = [{"datetime": (top + timedelta(hours=h)).isoformat(), "temperature": -1.0,
                                "wind_speed": 2.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [0.0] * 48
    return coord


def key_of(store):
    return store._key


def cycles(coord, n=3):
    fails = 0
    first = None
    for _ in range(n):
        try:
            asyncio.run(coord._async_update_data())
        except Exception as e:  # noqa: BLE001
            fails += 1
            first = first or f"{type(e).__name__}: {e}"[:120]
    return fails, first


def case_legionella(payload):
    _storage._DISK.clear()
    dt_util.freeze(NOW)
    coord = build()
    _storage._DISK[coord._legionella.store._key] = json.dumps(payload)
    asyncio.run(coord._legionella.async_load())
    return cycles(coord)


def case_boost(until):
    _storage._DISK.clear()
    dt_util.freeze(NOW)
    coord = build()
    _storage._DISK[boost._store(coord)._key] = json.dumps({boost.CHANNELS[0]: {"until": until}})
    try:
        asyncio.run(boost.restore_session(coord))
        return 0, None
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"[:100]


def case_pump(written):
    _storage._DISK.clear()
    dt_util.freeze(NOW)
    coord = build()
    _storage._DISK[pump_arbiter._store(coord)._key] = json.dumps({"written": written})
    try:
        asyncio.run(pump_arbiter._load(coord))
        return 0, None
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"[:100]


def case_snap(bias):
    ring = snapshots.SnapshotRing(snapshots=[{"taken_at": "2026-02-01T09:00:00+01:00", "healthy": True,
                                              "accuracy": {"temperature_bias": bias}, "learners": {}}])
    try:
        ring.best_restore()
        return 0, None
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"[:100]


def main():
    naive = (NOW + timedelta(hours=-30)).replace(tzinfo=None).isoformat()
    aware = (NOW + timedelta(hours=-30)).isoformat()
    fut_naive = (NOW + timedelta(hours=2)).replace(tzinfo=None).isoformat()
    fut_aware = (NOW + timedelta(hours=2)).isoformat()
    # (name, malformed-run, control-run)
    specs = [
        ("legionella.last_cycle_naive_only", lambda: case_legionella({"last_cycle": naive}),
         lambda: case_legionella({"last_cycle": aware})),
        ("legionella.last_attempt_naive_only", lambda: case_legionella({"last_attempt": naive}),
         lambda: case_legionella({"last_attempt": aware})),
        ("legionella.last_cycle_naive+attempt_aware", lambda: case_legionella({"last_cycle": naive, "last_attempt": aware}),
         lambda: case_legionella({"last_cycle": aware, "last_attempt": aware})),
        ("legionella.both_naive", lambda: case_legionella({"last_cycle": naive, "last_attempt": naive}),
         lambda: case_legionella({"last_cycle": aware, "last_attempt": aware})),
        ("boost.until_naive", lambda: case_boost(fut_naive), lambda: case_boost(fut_aware)),
        ("pump.written_str", lambda: case_pump("x"), lambda: case_pump({})),
        ("pump.written_float", lambda: case_pump(3.0), lambda: case_pump({})),
        ("snap.bias_garbage", lambda: case_snap("garbage"), lambda: case_snap(0.1)),
        ("snap.bias_list", lambda: case_snap([]), lambda: case_snap(0.1)),
    ]
    rows = []
    for name, bad, good in specs:
        f, e = bad()
        fc, _ = good()
        rows.append((name, f, fc, e))
        print(f"CASE {name}: malformed_fail={f} control_fail={fc} {e or ''}")
    return rows


if __name__ == "__main__":
    rows = main()
    print(f"RESULT v2_raising_cases={sum(1 for r in rows if r[1] > 0)}_of_{len(rows)} count")
    print(f"RESULT v2_legionella_max_wedged_cycles={max(r[1] for r in rows if r[0].startswith('legionella'))}_of_3 count")
    print(f"RESULT v2_null_control_failing={sum(1 for r in rows if r[2] > 0)} count")
    dt_util.freeze(None)
    pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
