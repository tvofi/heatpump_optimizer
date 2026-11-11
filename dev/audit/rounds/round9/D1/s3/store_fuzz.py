"""D1-s3 M2: seeded corruption of the four stores in this seat's files, loaded
through the real loader, then two consumer cycles.

Metric: per store, mutants (of N seeded) whose SECOND consumer cycle still
raises -- a corrupt record that became a permanent per-cycle failure instead of
being quarantined/reset. Count key: an exception escaping the production
consumer call (never a label the harness assigns to its own record).

Stores and their production loader -> consumer (per cycle):
  pump_duty  pump_arbiter._load (inside apply)   -> pump_arbiter.apply(coord, now)
  boost      boost.restore                       -> boost.apply(coord); held_for(coord).as_dict()
  away       away.restore_override               -> coordinator._resolve_away()
  legionella DHWLegionellaTracker.async_load     -> async_track(61.0); hours_since(); due_in_hours()
(async_track/_resolve_away are what the coordinator cycle calls each poll, and
an exception there escapes _async_update_data as UpdateFailed.)

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/store_fuzz.py [--n 200] [--seed 9] [--perturb]
  --perturb  in-memory fix: every ISO-datetime parse in the four loaders is
             normalised to an aware local instant (dt_util.as_local), and
             pump_arbiter._load drops a non-numeric set-point value. Expect
             repeat failures -> 0 for every store.
  --naive-clock  control: run with the stub's naive clock (HASTUB_TZ unset).
             Real HA's dt_util.now() is always aware; under a naive clock the
             naive-datetime mutants stop failing and the ALREADY-HEALTHY aware
             payloads start failing -- the stub artefact this harness avoids.
Expected (default arm, seed 9, n 200): repeat_fail pump_duty=25, boost=0, away=13, legionella=10;
loader_raise pump_duty=34, boost=14 (exact; deterministic); --perturb: repeat_fail 0 everywhere, healthy_repeat=0 for every store.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
if "--naive-clock" in sys.argv:
    os.environ.pop("HASTUB_TZ", None)
else:
    os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio
import copy
import json
import random
import time
from collections import Counter
from datetime import datetime, timedelta
from unittest import mock
import logging
logging.disable(logging.CRITICAL)

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import pump_arbiter, boost, away  # noqa: E402
from heatpump_optimizer import legionella as legionella_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402

def _arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default

N = _arg("--n", 200)
SEED = _arg("--seed", 9)
PERTURB = "--perturb" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()

TZ = dt_util.DEFAULT_TIME_ZONE
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=TZ) if TZ else datetime(2026, 1, 10, 6, 0)
_IDS = iter(range(10**9))


def _coord():
    states = {
        "sensor.indoor": FakeState("21.4"),
        "sensor.outdoor": FakeState("-3.0"),
        "select.pump_mode": FakeState("Heating + DHW", attributes={
            "options": ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]}),
        "number.dhw_set": FakeState("40", attributes={"min": 40, "max": 63}),
        "number.water_set": FakeState("25", attributes={"min": 25, "max": 63}),
    }
    cfg = {
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0,
    }
    c = HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg, entry_id=f"fz{next(_IDS)}"))
    c._mode = MODE_AUTO
    return c


def _key(c, store):
    e = c.entry.entry_id
    return {"pump_duty": f"heatpump_optimizer_{e}_pump_duty",
            "boost": f"heatpump_optimizer_{e}_boost",
            "away": f"heatpump_optimizer_{e}_away",
            "legionella": c._legionella.store._key}[store]


async def _healthy(store):
    """The payload production itself writes, captured from the stub disk."""
    c = _coord()
    dt_util.freeze(T0)
    if store == "pump_duty":
        await pump_arbiter.apply(c, T0)
    elif store == "boost":
        boost.held_for(c).set("space", True, T0)
        boost.held_for(c).set("dhw", True, T0)
        await boost.persist(c)
    elif store == "away":
        c._away_state.migrated_helpers = True
        await c.async_set_away(active=True, return_time=(T0 + timedelta(days=3)).isoformat(), refresh=False)
    elif store == "legionella":
        leg = c._legionella
        leg.last_cycle = T0 - timedelta(days=2)
        leg.attempt = T0 - timedelta(days=1)
        leg.attempt_peak = 57.5
        await leg.async_save()
    return json.loads(_storage._DISK[_key(c, store)])


async def _load(c, store):
    if store == "pump_duty":
        await pump_arbiter._load(c)
    elif store == "boost":
        await boost.restore(c)
    elif store == "away":
        await away.restore_override(c)
    elif store == "legionella":
        await c._legionella.async_load()


async def _cycle(c, store, k):
    now = T0 + timedelta(minutes=2 * k)
    dt_util.freeze(now)
    if store == "pump_duty":
        await pump_arbiter.apply(c, now)
    elif store == "boost":
        boost.apply(c)
        boost.held_for(c).as_dict()
    elif store == "away":
        c._resolve_away()
    elif store == "legionella":
        leg = c._legionella
        await leg.async_track(61.0)
        leg.hours_since()
        leg.due_in_hours()


# ---- mutation operators --------------------------------------------------
def _leaves(o, path=()):
    if isinstance(o, dict):
        out = [(path, o)]
        for k, v in o.items():
            out += _leaves(v, path + (k,))
        return out
    if isinstance(o, list):
        out = [(path, o)]
        for i, v in enumerate(o):
            out += _leaves(v, path + (i,))
        return out
    return [(path, o)]


def _is_iso(v):
    if not isinstance(v, str):
        return False
    try:
        datetime.fromisoformat(v)
        return True
    except ValueError:
        return False


OPS = ["naive_dt", "type_swap_str", "type_swap_num", "delete", "nan", "inf",
       "negative", "huge", "wrap_list", "wrap_dict", "truncate", "str_for_dict",
       "none", "far_future_dt", "bool"]


def _mutate(payload, rng):
    p = copy.deepcopy(payload)
    op = rng.choice(OPS)
    nodes = [(path, v) for path, v in _leaves(p) if path]
    if op == "naive_dt" or op == "far_future_dt":
        cand = [(path, v) for path, v in nodes if _is_iso(v)]
        if cand:
            path, v = rng.choice(cand)
            d = datetime.fromisoformat(v)
            new = (d.replace(tzinfo=None).isoformat() if op == "naive_dt"
                   else d.replace(year=2099).isoformat())
            _set(p, path, new)
            return p, op
        op = "type_swap_str"
    if op == "delete":
        path, _ = rng.choice(nodes)
        _del(p, path)
        return p, op
    if op == "truncate":
        return json.dumps(p)[: rng.randint(1, max(2, len(json.dumps(p)) - 1))], op
    if op == "str_for_dict":
        dicts = [(path, v) for path, v in nodes if isinstance(v, dict)] or [((), p)]
        path, _ = rng.choice(dicts)
        if not path:
            return "garbage", op
        _set(p, path, "garbage")
        return p, op
    path, v = rng.choice(nodes)
    new = {
        "type_swap_str": lambda: str(v),
        "type_swap_num": lambda: 42,
        "nan": lambda: float("nan"),
        "inf": lambda: float("inf"),
        "negative": lambda: -1e9,
        "huge": lambda: 1e308,
        "wrap_list": lambda: [v],
        "wrap_dict": lambda: {"v": v},
        "none": lambda: None,
        "bool": lambda: True,
    }[op]()
    _set(p, path, new)
    return p, op


def _set(o, path, v):
    for s in path[:-1]:
        o = o[s]
    o[path[-1]] = v


def _del(o, path):
    for s in path[:-1]:
        o = o[s]
    if isinstance(o, list):
        o.pop(path[-1])
    else:
        o.pop(path[-1], None)


def _to_disk(key, payload):
    # json.dumps writes NaN/Infinity exactly as a corrupted file would carry them.
    _storage._DISK[key] = payload if isinstance(payload, str) and not payload.startswith(("{", "[", '"')) and False else json.dumps(payload) if not isinstance(payload, str) or payload == "garbage" else payload


async def _run_one(store, payload):
    c = _coord()
    key = _key(c, store)
    _storage._DISK[key] = json.dumps(payload) if not isinstance(payload, str) or payload == "garbage" else payload
    fails = []
    try:
        dt_util.freeze(T0)
        await _load(c, store)
        fails.append(None)
    except Exception as e:  # a loader that raises is a failure too
        fails.append(type(e).__name__)
    for k in (1, 2):
        try:
            await _cycle(c, store, k)
            fails.append(None)
        except Exception as e:
            fails.append(type(e).__name__)
    return fails


# ---- perturbation: the fix, in memory ------------------------------------
def _aware(d):
    return dt_util.as_local(d) if d is not None and d.tzinfo is None else d


class _AwareDT(datetime):
    @classmethod
    def fromisoformat(cls, s):
        return _aware(datetime.fromisoformat(s))


_orig_prt, _orig_pu, _orig_pd = away._parse_return_time, boost._parse_until, dt_util.parse_datetime
_orig_load = pump_arbiter._load


async def _load_fixed(coord):
    await _orig_load(coord)
    held = pump_arbiter.state_for(coord)
    for slot, (value, at) in list(held.written.items()):
        if slot != "mode" and not (isinstance(value, (int, float)) and not isinstance(value, bool)):
            del held.written[slot]
        elif slot == "mode" and not isinstance(value, str):
            del held.written[slot]


async def main():
    summary = {}
    rng = random.Random(SEED)
    for store in ("pump_duty", "boost", "away", "legionella"):
        healthy = await _healthy(store)
        h = await _run_one(store, healthy)
        by_op = Counter()
        first = repeat = loadfail = 0
        errs = Counter()
        lerrs = Counter()
        for _ in range(N):
            m, op = _mutate(healthy, rng)
            f = await _run_one(store, m)
            loadfail += f[0] is not None
            if f[0] is not None:
                lerrs[f"{op}:{f[0]}"] += 1
            first += f[1] is not None
            if f[1] is not None and f[2] is not None:
                repeat += 1
                by_op[op] += 1
                errs[f[2]] += 1
        summary[store] = (h, first, repeat, loadfail, dict(by_op), dict(errs), dict(lerrs))
    return summary


if PERTURB:
    with mock.patch.object(away, "_parse_return_time", lambda r: _aware(_orig_prt(r))), \
         mock.patch.object(boost, "_parse_until", lambda r: _aware(_orig_pu(r))), \
         mock.patch.object(pump_arbiter, "datetime", _AwareDT), \
         mock.patch.object(pump_arbiter, "_load", _load_fixed), \
         mock.patch.object(dt_util, "parse_datetime", lambda v: _aware(_orig_pd(v))):
        summary = asyncio.run(main())
else:
    summary = asyncio.run(main())

print(f"arm={'perturb' if PERTURB else 'default'} clock={'aware' if TZ else 'naive'} n={N} seed={SEED}")
for store, (h, first, repeat, loadfail, by_op, errs, lerrs) in summary.items():
    print(f"  {store}: healthy={h} first_cycle_fail={first} loader_raise={loadfail} repeat_by_op={by_op} errors={errs}")
    print(f"    loader_raise_by_op={lerrs}")
    print(f"RESULT {store}_loader_raise={loadfail} count_of_{N}")
    print(f"RESULT {store}_healthy_repeat={int(h[1] is not None and h[2] is not None)} count")
    print(f"RESULT {store}_repeat_fail={repeat} count_of_{N}")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
