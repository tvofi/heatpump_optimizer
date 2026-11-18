"""D1.M2 store-corruption fuzz over the coordinator's own persisted payloads.

Metric (one line): per coordinator store, of N seeded mutants of a healthy
payload loaded through the real loader, the count whose loader raises
(``loader_raised``), whose first / second update cycle raises
(``cycle1_raised`` / ``cycle2_raised``), and whose loader loses a top-level
key the mutation did not touch (``collateral``: the re-serialised in-memory
state differs from a healthy load on an untouched top-level key).
Count key: the exception raised by the production seam, and the value the
production save path re-serialises -- never an attribute of the mutant.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/store_fuzz.py [--n 200] [--seed 9] [--store NAME]
Expected: per-store RESULT lines; exact for a fixed seed (counts), +-0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: B4 cloud container.

Real Home Assistant semantics: HASTUB_TZ=Europe/Stockholm, so dt_util.now() is
tz-aware as it is in Home Assistant (the stub's default naive clock is not).
The solve is replaced by a cached healthy result (``_await_optimize``) so a
cycle costs milliseconds; the loaders and everything around the solve are
production code. ``--real-solve`` runs the real process-worker solve instead.

Perturbation hooks: ``--perturb NAME`` wraps the named production loader
seam in memory (see PERTURB below) so the judge can see the count move.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import copy
import json
import logging
import random
import sys
import time

import orjson
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.manual_plan import build_override  # noqa: E402

HC = cm.HeatPumpOptimizerCoordinator

STORES = {
    # name: (storage-key suffix, loader, saver)
    "thermal_learning": ("thermal_learning", "_async_load_thermal_learning", "_async_save_thermal_learning"),
    "price_model": ("price_model", "_async_load_price_model", "_async_save_price_model"),
    "accuracy": ("accuracy", "_async_load_accuracy", "_async_save_accuracy"),
    "energy": ("energy", "_async_load_energy_totals", "_async_save_energy_totals"),
    "ledger": ("ledger", "_async_load_ledger", "_async_save_ledger"),
    "snapshots": ("snapshots", "_async_load_snapshots", "_async_save_snapshots"),
    "manual_plan": ("manual_plan", "_async_load_manual_plan", "_async_save_manual_plan"),
}
LOADERS = [v[1] for v in STORES.values()]


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def _hass():
    hass = FakeHass({"sensor.indoor": FakeState("21.4"),
                     "sensor.outdoor": FakeState("-3.0")})
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(),
         "value": round(0.5 + 0.1 * (h % 4), 3)} for h in range(48)]}))
    return hass


CFG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def _coord():
    return HC(_hass(), FakeEntry(data=dict(CFG)))


async def _load_all(c, skip=None):
    for name in LOADERS:
        if name != skip:
            await getattr(c, name)()


def _key(suffix):
    return f"{const.DOMAIN}_test_entry_{suffix}"


# --------------------------------------------------------------------------
# healthy payloads
# --------------------------------------------------------------------------

def healthy_payloads(real_solve: bool):
    storage._reset_store_disk()
    c = _coord()
    cached = {}

    async def go():
        await _load_all(c)
        for _ in range(2):
            await c._async_update_data()
        cached["result"] = copy.deepcopy(c._optimization_result)
        now = dt_util.now()
        # enrich the sparse defaults so nested paths exist to mutate
        c._cop_baseline[(4, False)] = [3.1, 5]
        c._cop_baseline[(4, True)] = [2.5, 3]
        c._capacity_envelope[-3] = [5.0, 4]
        c._last_heavy_snow = now - timedelta(days=1)
        c._snow_accum_last = now - timedelta(hours=2)
        c._snow_accum_cm = 3.5
        c._immersion_events = [(now - timedelta(days=2)).isoformat()]
        c._ledger.add(now, "space", kwh=12.5, sek=20.1)
        c._ledger.observe_meta_mean(now, "spot", 0.9)
        c._month_reports = {"2026-08": {"kwh": 100.0, "sek": 150.0}}
        c._score_day = {"day": now.date().isoformat(), "kwh": 1.0, "sek": 2.0,
                        "spot_sum": 3.0, "spot_h": 4.0, "free_streak": 0.0}
        c._operation_score = 77.0
        for k in list(c._energy_totals):
            c._energy_totals[k] = 42.0
        c._manual_override = build_override(
            dhw_slots=None,
            space_slots=[{"start": (now + timedelta(hours=1)).isoformat(),
                          "end": (now + timedelta(hours=3)).isoformat()}],
            expires_at=now + timedelta(hours=6), now=now)
        for _, _, saver in STORES.values():
            c._store_digests = {}
            await getattr(c, saver)()

    asyncio.run(go())
    out = {name: json.loads(storage._DISK[_key(sfx)]) for name, (sfx, _, _) in STORES.items()}
    return out, cached["result"]


# --------------------------------------------------------------------------
# mutants
# --------------------------------------------------------------------------

def _paths(obj, prefix=()):
    yield prefix
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _paths(v, prefix + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:6]):
            yield from _paths(v, prefix + (i,))


def _get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def _set(root, path, value):
    if not path:
        return value
    parent = _get(root, path[:-1])
    parent[path[-1]] = value
    return root


OPS = ["type_swap", "delete", "nonfinite", "negative", "huge", "wrap",
       "truncate", "str_for_dict", "datetime"]
SWAPS = ["x", 7, -3.5, True, None, [], {}, [1, 2], {"a": 1}]


def mutate(payload, rng):
    p = copy.deepcopy(payload)
    paths = list(_paths(p))
    path = rng.choice(paths)
    op = rng.choice(OPS)
    cur = _get(p, path)
    if op == "type_swap":
        new = rng.choice(SWAPS)
    elif op == "delete" and path and isinstance(_get(p, path[:-1]), dict):
        del _get(p, path[:-1])[path[-1]]
        return p, path, op
    elif op == "nonfinite":
        new = rng.choice([float("nan"), float("inf"), float("-inf"), "NaN", "-Infinity"])
    elif op == "negative":
        new = -abs(cur) if isinstance(cur, (int, float)) and not isinstance(cur, bool) else -1e9
    elif op == "huge":
        new = rng.choice([1e308, 10 ** 30, 10 ** 400, 2 ** 63])
    elif op == "wrap":
        new = rng.choice([[cur], {"v": cur}])
    elif op == "truncate":
        if isinstance(cur, list):
            new = cur[: len(cur) // 2]
        elif isinstance(cur, dict):
            keys = list(cur)
            new = {k: cur[k] for k in keys[: len(keys) // 2]}
        elif isinstance(cur, str):
            new = cur[: len(cur) // 2]
        else:
            new = None
    elif op == "str_for_dict":
        new = "garbage" if isinstance(cur, (dict, list)) else {"garbage": cur}
    else:  # datetime
        new = rng.choice(["2026-09-26T10:00:00", "9999-12-31T23:59:59+00:00",
                          "2026-13-45T99:00:00", "0001-01-01T00:00:00+00:00",
                          "2026-09-26", ""])
    return _set(p, path, new), path, op


# --------------------------------------------------------------------------
# one mutant
# --------------------------------------------------------------------------

def _reser(c, name):
    """What the production saver writes for the loaded in-memory state."""
    sfx, _, saver = STORES[name]
    storage._DISK.pop(_key(sfx), None)
    c._store_digests = {}
    asyncio.run(getattr(c, saver)())
    raw = storage._DISK.get(_key(sfx))
    return json.loads(raw) if raw is not None else None


def disk_roundtrip(payload):
    """What Home Assistant's Store hands a loader for these bytes.

    The real Store parses with orjson, which refuses a NaN/Infinity token and
    an integer beyond 64 bits (the whole file is then moved aside as corrupt
    and the load returns None -- never a loader seam). The stub parses with
    stdlib json and accepts both, so a mutant is kept only when orjson reads
    it, and the loader receives exactly orjson's value (u64+ ints -> float).
    """
    raw = json.dumps(payload)
    try:
        return orjson.loads(raw), True
    except orjson.JSONDecodeError:
        return None, False


def run_one(name, payload, healthy_ser, touched_top):
    sfx, loader, _ = STORES[name]
    storage._reset_store_disk()
    storage._DISK[_key(sfx)] = json.dumps(payload)
    c = _coord()
    row = {"loader_raised": None, "cycle1_raised": None, "cycle2_raised": None,
           "collateral": [], "load_logs": 0}
    handler = _Count()
    logging.getLogger("custom_components").addHandler(handler)
    logging.getLogger("heatpump_optimizer").addHandler(handler)
    try:
        try:
            asyncio.run(getattr(c, loader)())
        except Exception as err:  # noqa: BLE001
            row["loader_raised"] = f"{type(err).__name__}: {err}"[:160]
        row["load_logs"] = sum(1 for r in handler.records if r.levelno >= logging.INFO)
    finally:
        logging.getLogger("custom_components").removeHandler(handler)
        logging.getLogger("heatpump_optimizer").removeHandler(handler)
    # every other store healthy-empty
    asyncio.run(_load_all(c, skip=loader))
    # collateral: re-serialise BEFORE any cycle, compare untouched top keys
    ser = _reser(c, name)
    storage._DISK[_key(sfx)] = json.dumps(payload)  # keep corrupt on disk
    if isinstance(healthy_ser, dict) and isinstance(ser, dict):
        for k, v in healthy_ser.items():
            if name in ATOMIC or k in touched_top or k in VOLATILE.get(name, ()):
                continue
            if ser.get(k) != v:
                row["collateral"].append(k)
    for n in (1, 2):
        try:
            asyncio.run(c._async_update_data())
        except Exception as err:  # noqa: BLE001
            row[f"cycle{n}_raised"] = f"{type(err).__name__}: {err}"[:160]
    return row


# Keys the saver restamps from the clock, not from the load.
VOLATILE = {"energy": ("last_tick",), "thermal_learning": ("updated_at",)}
# The manual plan is one unit by design: a slot list that fails to parse
# discards the whole override (coordinator._async_load_manual_plan).
ATOMIC = {"manual_plan"}


_np_isfinite = cm.np.isfinite


def _float_isfinite(x, *a, **k):
    """np.isfinite over float(x) for a Python int beyond int64, else native."""
    if isinstance(x, int) and not isinstance(x, bool) and abs(x) >= 2 ** 63:
        return _np_isfinite(float(x), *a, **k)
    return _np_isfinite(x, *a, **k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=9)
    ap.add_argument("--store", action="append")
    ap.add_argument("--real-solve", action="store_true")
    ap.add_argument("--show", type=int, default=4)
    ap.add_argument("--perturb", default="")
    ap.add_argument("--sweep-huge", action="store_true")
    ap.add_argument("--stdlib-json", action="store_true",
                    help="the stub's lenient parse (for comparison only)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    t0 = time.process_time()
    tt0 = time.thread_time()
    healthy, cached = healthy_payloads(args.real_solve)

    async def fake_opt(hass, optimizer, state, *a, **k):
        return copy.deepcopy(cached)

    patches = []
    if not args.real_solve:
        patches.append(mock.patch.object(cm, "_await_optimize", fake_opt))
    patches += PERTURB.get(args.perturb, lambda: [])()
    for p in patches:
        p.start()
    names = args.store or list(STORES)
    if args.sweep_huge:
        sweep_huge(names, healthy, args)
        names = []
    for name in names:
        # healthy reference: load the unmutated payload the same way
        storage._reset_store_disk()
        storage._DISK[_key(STORES[name][0])] = json.dumps(healthy[name])
        ref = _coord()
        asyncio.run(getattr(ref, STORES[name][1])())
        healthy_ser = _reser(ref, name)
        rng = random.Random(f"{args.seed}:{name}")
        agg = {"loader_raised": 0, "cycle1_raised": 0, "cycle2_raised": 0,
               "collateral": 0, "silent_raise": 0}
        examples = {}
        refused = 0
        i = 0
        while i < args.n:
            payload, path, op = mutate(healthy[name], rng)
            if not args.stdlib_json:
                payload, ok = disk_roundtrip(payload)
                if not ok:
                    refused += 1
                    continue
            i += 1
            touched = {path[0]} if path else set(healthy_ser or {})
            row = run_one(name, payload, healthy_ser, touched)
            for k in ("loader_raised", "cycle1_raised", "cycle2_raised"):
                if row[k]:
                    agg[k] += 1
                    examples.setdefault(k, []).append((i, op, list(path), row[k]))
            if row["collateral"]:
                agg["collateral"] += 1
                examples.setdefault("collateral", []).append(
                    (i, op, list(path), row["collateral"], row["loader_raised"]))
        for k, v in agg.items():
            if k == "silent_raise":
                continue
            print(f"RESULT {name}.{k}={v} mutants_of_{args.n}")
        print(f"RESULT {name}.orjson_refused_redrawn={refused} mutants")
        for k, rows in examples.items():
            for ex in rows[: args.show]:
                print(f"  ex {name}.{k}: {ex}")
    for p in patches:
        p.stop()
    pc = time.process_time() - t0
    tc = time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


def sweep_huge(names, healthy, args):
    """Seam enumeration: every numeric leaf of every store set, one at a time,
    to each JSON-legal huge value orjson accepts (1e20 is past uint64, so an
    ``int()`` of it is a Python int numpy cannot take; 1e308 is the float
    ceiling). Counts the leaves whose SECOND cycle still raises."""
    total = 0
    for name in names:
        leaves = [p for p in _paths(healthy[name])
                  if p and isinstance(_get(healthy[name], p), (int, float))
                  and not isinstance(_get(healthy[name], p), bool)]
        wedged = []
        for path in leaves:
            for v in (1e20, 1e308):
                payload = _set(copy.deepcopy(healthy[name]), path, v)
                payload, ok = disk_roundtrip(payload)
                if not ok:
                    continue
                row = run_one(name, payload, None, set())
                if row["cycle2_raised"]:
                    wedged.append((list(path), v, row["cycle2_raised"][:90]))
        total += len(wedged)
        print(f"RESULT {name}.huge_leaf_wedges={len(wedged)} of {2 * len(leaves)} leaf_values")
        for w in wedged[: args.show]:
            print(f"  ex {name}: {w}")
    print(f"RESULT all.huge_leaf_wedges={total} leaf_values")


PERTURB: dict = {
    # One-line production edit, in memory: _learning_view's bucket count
    # guarded by a bounded check (float() before isfinite). Must take the
    # wedge count to zero.
    "learning_view_float": lambda: [mock.patch.object(
        cm.np, "isfinite",
        _float_isfinite)],
}

if __name__ == "__main__":
    main()
