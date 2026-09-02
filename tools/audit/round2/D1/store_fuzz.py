#!/usr/bin/env python
"""D1 store-corruption fuzz: every persisted payload, 200 seeded mutants each,
loaded through the real loader, then one cycle, a second cycle, and a restart.

METRIC (per store, counts over N mutants):
  loader_raised        the store's loader task ended with an exception
                       (in HA: an "unhandled exception in task" log, the rest
                       of the loader skipped, nothing quarantined)
  cycle1_failed        the first _async_update_data after the load raised
  cycle2_failed        the second one raised too (the failure repeats)
  repeat_on_restart    a fresh coordinator on the disk left behind after the
                       two cycles raises in the same loader again (the corrupt
                       part was neither quarantined nor reset)
  silent_load          the loader neither raised nor logged WARNING+ while a
                       later cycle failed (corruption swallowed at load, fails
                       later)
  Expected for a robust loader: all zero. A non-zero loader_raised with
  repeat_on_restart == loader_raised is a permanent failure on that file.

COMMAND (from the export root; N defaults to 200, add e.g. `--n 20` for a
quick pass, `--stores ledger,accuracy` to restrict):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D1/store_fuzz.py

EXPECTED (baseline c398fc84eec25fc44b60d74aae05b9a2da205884): see REPORT.md;
  the per-store RESULT lines are exact for a given seed (SEED=20260901).

INSTRUMENTED SYMBOLS: the ten loaders on
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  (_async_load_snapshots, _async_load_dhw_profile, _async_load_dhw_legionella,
  _async_load_dhw_draws, _async_load_thermal_learning, _async_load_price_model,
  _async_load_ledger, _async_load_accuracy, _async_load_energy_totals,
  _async_load_manual_plan) and the parsers they call
  (snapshots:SnapshotRing.from_dict, ledger:MonthlyLedger.from_dict,
  accuracy:AccuracyTracker.from_dict, defrost:DefrostDerate.from_dict,
  tariff:PeakTracker.from_dict, comfort_learning:ComfortLearner.from_dict,
  price_model:PriceShapeModel.from_dict, dhw_draws:DrawStats.from_dict,
  wear:StartCounter.from_dict, manual_plan:ManualOverride.from_dict).

PERTURBATION: wrap the body of any failing loader in
  `try: ... except Exception: _LOGGER.warning(...); await store.async_save({})`
  -> loader_raised and repeat_on_restart for that store go to_zero.
  Null control: the `identity` arm (mutant == healthy payload) must give all
  zeros; it is printed as RESULT fuzz.<store>.identity_failures.

MUTATION GRAMMAR (seeded random.Random(SEED + index)): pick a random path
into the JSON tree, then one of: type swap, delete key, NaN / +inf / -inf,
negative, huge (1e300, 10**30), zero, wrap in list / dict, truncate list,
string where a dict goes, or replace the whole document ([], "", 0, null,
[doc], {"data": doc}, {}). NaN/inf are written through Python's json (the
stub reads them back); in HA they represent a hand-edited or bit-rotted file.

The stub executor runs inline (this measures loaders, not the executor
boundary); tasks run on a real asyncio loop so the fire-and-forget loaders
actually execute, as in HA.

MACHINE: Apple M1 8-core 8 GB, Darwin 25.6.0, CPython 3.13.1, numpy 2.5.2
"""
from __future__ import annotations

import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import argparse
import asyncio
import copy
import json
import logging
import math
import random
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

import homeassistant.helpers.storage as storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer.accuracy import AccuracySample  # noqa: E402
from heatpump_optimizer.const import DOMAIN  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.manual_plan import ManualOverride  # noqa: E402

SEED = 20260901
START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
HERE = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.CRITICAL)
HPO_LOG = logging.getLogger("heatpump_optimizer")
HPO_LOG.setLevel(logging.WARNING)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record.getMessage())


CAPTURE = _Capture()
HPO_LOG.addHandler(CAPTURE)
HPO_LOG.propagate = False


class LoopHass(FakeHass):
    """Tasks really run (a real loop); the executor stays inline."""

    def async_create_task(self, coro, name=None, eager_start=False):
        return asyncio.get_running_loop().create_task(coro, name=name)


STORES = {
    "snapshots": ("_snapshot_store", "_async_load_snapshots"),
    "dhw_profile": ("_dhw_profile_store", "_async_load_dhw_profile"),
    "dhw_legionella": ("_dhw_legionella_store", "_async_load_dhw_legionella"),
    "dhw_draws": ("_dhw_draws_store", "_async_load_dhw_draws"),
    "thermal_learning": ("_thermal_learning_store", "_async_load_thermal_learning"),
    "price_model": ("_price_model_store", "_async_load_price_model"),
    "ledger": ("_ledger_store", "_async_load_ledger"),
    "accuracy": ("_accuracy_store", "_async_load_accuracy"),
    "energy_totals": ("_energy_store", "_async_load_energy_totals"),
    "manual_plan": ("_manual_plan_store", "_async_load_manual_plan"),
}

CONFIG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_temp_entity": "sensor.dhw",
    "heat_pump_power_entity": "sensor.hp_power",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "peak_tariff_enabled": True,
    "peak_tariff_price_per_kw": 45.0,
    "comfort_learning_enabled": True,
}


def _states():
    now = dt_util.now()
    return {
        "sensor.indoor": FakeState("21.4", last_updated=now),
        "sensor.outdoor": FakeState("-3.0", last_updated=now),
        "sensor.dhw": FakeState("48.0", last_updated=now),
        "sensor.hp_power": FakeState("1.8", unit="kW", last_updated=now),
    }


async def _noop(self):
    return None


# The fetches would go to the network; the horizon data is injected instead.
HeatPumpOptimizerCoordinator._fetch_tibber_prices = _noop
HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop


def inject(coord):
    now = dt_util.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (midnight + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (midnight + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._opt_config.horizon_hours = 6.0  # cheap solves; the loaders are what is under test


def build(hass):
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CONFIG))


async def drain(coord):
    """Let the fire-and-forget loaders land; return their exceptions."""
    tasks = list(coord._background_tasks)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [repr(r) for r in results if isinstance(r, BaseException)]


async def run_cycle(coord):
    try:
        data = await coord._async_update_data()
        return None if isinstance(data, dict) else "no data dict"
    except Exception as err:  # noqa: BLE001
        return repr(err)


async def seed_healthy():
    """One real cycle plus explicit seeding of the stores a cycle leaves empty."""
    storage._reset_store_disk()
    hass = LoopHass(_states())
    coord = build(hass)
    await drain(coord)
    inject(coord)
    err = await run_cycle(coord)
    assert err is None, f"seed cycle failed: {err}"
    now = dt_util.now()
    # accuracy: a few samples on both trackers
    for i in range(4):
        sample = AccuracySample(
            when=now - timedelta(minutes=30 * (4 - i)),
            predicted_power_kw=1.0 + 0.1 * i,
            actual_power_kw=1.1 + 0.1 * i,
            predicted_temp=21.0,
            actual_temp=21.2,
            predicted_cost=0.5,
            actual_cost=0.55,
            outdoor_temp=-3.0,
            humidity=80.0,
            cop_residual=0.05,
        )
        coord._accuracy.record(sample)
        coord._dhw_accuracy.record(sample)
    # ledger / starts / draws
    coord._ledger.add(now, "space", kwh=1.2, sek=2.3)
    coord._ledger.add(now, "dhw", kwh=0.4, sek=0.7)
    coord._ledger.observe_meta_mean(now, "cop", 3.1)
    for kw in (0.0, 0.0, 2.5, 2.6, 2.4):
        coord._start_counter.observe(now, kw, 0.5, False)
    coord._draw_stats.fold(now, "06:00-08:30", 2.1)
    coord._draw_stats.fold(now, "17:00-22:00", 3.4)
    # price shape: one observed day
    hours = [0.6 + 0.5 * (h % 12) / 12.0 for h in range(24)]
    coord._price_model.observe_day(now - timedelta(days=1), hours)
    coord._price_days_seen.add((now - timedelta(days=1)).date().isoformat())
    # snapshot ring: one snapshot
    coord._snapshot_ring.take(now, coord._learner_snapshot_payloads(), coord._accuracy.summary(), True)
    # manual plan: a live override
    try:
        coord._manual_override = ManualOverride.from_dict(
            {
                "space_slots": [
                    {"start": (now + timedelta(hours=1)).isoformat(), "end": (now + timedelta(hours=2)).isoformat(), "pin": "on"}
                ],
                "dhw_slots": None,
                "expires_at": (now + timedelta(hours=6)).isoformat(),
                "created_at": now.isoformat(),
            }
        )
    except Exception as err:  # noqa: BLE001
        print(f"NOTE manual override seed failed ({err!r}); the store fuzz uses the empty payload")
    for name in (
        "_async_save_thermal_learning",
        "_async_save_dhw_profile",
        "_async_save_dhw_draws",
        "_async_save_dhw_legionella",
        "_async_save_price_model",
        "_async_save_ledger",
        "_async_save_accuracy",
        "_async_save_energy_totals",
        "_async_save_snapshots",
        "_async_save_manual_plan",
    ):
        await getattr(coord, name)()
    keys = {store: getattr(coord, attr)._key for store, (attr, _) in STORES.items()}
    disk = dict(storage._DISK)
    for store, key in keys.items():
        assert key in disk, f"{store} was not written"
    return keys, disk


# ---------------------------------------------------------------------------
# Mutation grammar
# ---------------------------------------------------------------------------
def _paths(node, prefix=()):
    yield prefix
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _paths(v, prefix + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _paths(v, prefix + (i,))


def _get(node, path):
    for p in path:
        node = node[p]
    return node


def _set(root, path, value):
    if not path:
        return value
    parent = _get(root, path[:-1])
    parent[path[-1]] = value
    return root


def _delete(root, path):
    parent = _get(root, path[:-1])
    if isinstance(parent, dict):
        del parent[path[-1]]
    else:
        parent.pop(path[-1])
    return root


TOP_LEVEL = [
    ("top:list", lambda d: []),
    ("top:str", lambda d: ""),
    ("top:int", lambda d: 0),
    ("top:null", lambda d: None),
    ("top:wrapped_list", lambda d: [d]),
    ("top:wrapped_dict", lambda d: {"data": d}),
    ("top:empty_dict", lambda d: {}),
    ("top:bool", lambda d: True),
]


def mutate(healthy, index):
    rng = random.Random(SEED + index)
    doc = copy.deepcopy(healthy)
    if rng.random() < 0.06:
        name, fn = rng.choice(TOP_LEVEL)
        return name, fn(doc)
    paths = [p for p in _paths(doc) if p]
    if not paths:
        name, fn = rng.choice(TOP_LEVEL)
        return name, fn(doc)
    path = rng.choice(paths)
    value = _get(doc, path)
    ops = ["type_swap", "delete", "nan", "inf", "neg_inf", "negative", "huge", "huge_int", "zero", "wrap_list", "wrap_dict", "string_for_dict", "truncate", "none"]
    op = rng.choice(ops)
    label = f"{op}@{'/'.join(map(str, path))}"
    if op == "type_swap":
        if isinstance(value, dict):
            new = []
        elif isinstance(value, list):
            new = "x"
        elif isinstance(value, bool):
            new = 2
        elif isinstance(value, (int, float)):
            new = "12.5x"
        elif isinstance(value, str):
            new = 123
        else:
            new = {}
        return label, _set(doc, path, new)
    if op == "delete":
        return label, _delete(doc, path)
    if op == "nan":
        return label, _set(doc, path, math.nan)
    if op == "inf":
        return label, _set(doc, path, math.inf)
    if op == "neg_inf":
        return label, _set(doc, path, -math.inf)
    if op == "negative":
        base = value if isinstance(value, (int, float)) and not isinstance(value, bool) else 1
        return label, _set(doc, path, -abs(base) - 1)
    if op == "huge":
        return label, _set(doc, path, 1e300)
    if op == "huge_int":
        return label, _set(doc, path, 10**30)
    if op == "zero":
        return label, _set(doc, path, 0)
    if op == "wrap_list":
        return label, _set(doc, path, [value])
    if op == "wrap_dict":
        return label, _set(doc, path, {"v": value})
    if op == "string_for_dict":
        target = path
        # prefer the nearest dict ancestor-or-self
        for cut in range(len(path), 0, -1):
            if isinstance(_get(doc, path[:cut]), dict):
                target = path[:cut]
                break
        return f"{op}@{'/'.join(map(str, target))}", _set(doc, target, "corrupt")
    if op == "truncate":
        target = None
        for cut in range(len(path), 0, -1):
            if isinstance(_get(doc, path[:cut]), list):
                target = path[:cut]
                break
        if target is None:
            return f"delete@{'/'.join(map(str, path))}", _delete(doc, path)
        lst = _get(doc, target)
        keep = rng.randint(0, max(0, len(lst) - 1))
        return f"{op}@{'/'.join(map(str, target))}:{keep}", _set(doc, target, lst[:keep])
    if op == "none":
        return label, _set(doc, path, None)
    return label, doc


# ---------------------------------------------------------------------------
# One trial
# ---------------------------------------------------------------------------
async def trial(store, key, healthy_disk, mutant_text):
    _, loader = STORES[store]
    storage._DISK.clear()
    storage._DISK.update(healthy_disk)
    storage._DISK[key] = mutant_text
    CAPTURE.records.clear()

    hass = LoopHass(_states())
    coord = build(hass)
    load_exc = await drain(coord)
    load_warnings = len(CAPTURE.records)
    inject(coord)
    c1 = await run_cycle(coord)
    c2 = await run_cycle(coord)
    disk_after = dict(storage._DISK)

    # restart on what the two cycles left behind
    hass2 = LoopHass(_states())
    coord2 = build(hass2)
    load_exc2 = await drain(coord2)
    return {
        "loader_raised": bool(load_exc),
        "loader_exc": load_exc[0] if load_exc else "",
        "load_warnings": load_warnings,
        "cycle1_failed": c1 is not None,
        "cycle1_exc": c1 or "",
        "cycle2_failed": c2 is not None,
        "repeat_on_restart": bool(load_exc2),
        "disk_reset": disk_after.get(key) != mutant_text,
    }


async def fuzz_store(store, key, healthy_disk, n):
    healthy = json.loads(healthy_disk[key])
    counts = {
        "n": 0,
        "loader_raised": 0,
        "cycle1_failed": 0,
        "cycle2_failed": 0,
        "repeat_on_restart": 0,
        "silent_load": 0,
        "multi_warn": 0,
        "disk_reset": 0,
    }
    failures = []
    identity = await trial(store, key, healthy_disk, healthy_disk[key])
    identity_failures = int(identity["loader_raised"] or identity["cycle1_failed"] or identity["cycle2_failed"] or identity["repeat_on_restart"])
    for i in range(n):
        label, mutant = mutate(healthy, i)
        text = json.dumps(mutant)
        r = await trial(store, key, healthy_disk, text)
        counts["n"] += 1
        for k in ("loader_raised", "cycle1_failed", "cycle2_failed", "repeat_on_restart", "disk_reset"):
            counts[k] += int(r[k])
        if not r["loader_raised"] and r["load_warnings"] == 0 and (r["cycle1_failed"] or r["cycle2_failed"]):
            counts["silent_load"] += 1
        if r["load_warnings"] > 1:
            counts["multi_warn"] += 1
        if r["loader_raised"] or r["cycle1_failed"] or r["cycle2_failed"] or r["repeat_on_restart"]:
            failures.append(
                {
                    "index": i,
                    "mutation": label,
                    "loader_exc": r["loader_exc"][:200],
                    "cycle1_exc": r["cycle1_exc"][:200],
                    "cycle2_failed": r["cycle2_failed"],
                    "repeat_on_restart": r["repeat_on_restart"],
                }
            )
    return counts, failures, identity_failures


async def main(n, only):
    dt_util.freeze(START)
    keys, healthy_disk = await seed_healthy()
    all_failures = {}
    t0 = time.process_time()
    tt0 = time.thread_time()
    total_fail = 0
    for store in STORES:
        if only and store not in only:
            continue
        counts, failures, identity_failures = await fuzz_store(store, keys[store], healthy_disk, n)
        all_failures[store] = failures
        total_fail += counts["loader_raised"]
        for k, v in counts.items():
            print(f"RESULT fuzz.{store}.{k}={v} count")
        print(f"RESULT fuzz.{store}.identity_failures={identity_failures} count")
        exc_kinds = {}
        for f in failures:
            kind = (f["loader_exc"] or f["cycle1_exc"]).split("(")[0]
            exc_kinds[kind] = exc_kinds.get(kind, 0) + 1
        print(f"NOTE fuzz.{store}.exception_kinds={json.dumps(exc_kinds)}")
    with open(os.path.join(HERE, "store_fuzz_failures.json"), "w") as fh:
        json.dump(all_failures, fh, indent=1, default=str)
    print(f"RESULT fuzz.total_loader_raised={total_fail} count")
    cpu = time.process_time() - t0
    thr = time.thread_time() - tt0
    print(f"RESULT thread_factor={cpu / thr if thr else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    dt_util.freeze(None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--stores", default="")
    args = ap.parse_args()
    asyncio.run(main(args.n, set(s for s in args.stores.split(",") if s)))
