"""D9 round 4 / H4 -- what one coordinator retains per cycle, and what the
out-of-process solve worker costs in resident memory.

METRIC (D9.md, verbatim): "Retained bytes = tracemalloc and deep
``sys.getsizeof`` of every coordinator collection after N cycles, as a
slope per cycle, plus ``ru_maxrss`` in a subprocess."

Also measured, because the shipped solve route is a SECOND INTERPRETER
(``coordinator._ensure_worker`` -> ``process_worker.py``, #199 #290):
  * the worker child's RSS after the first solve and after N solves
    (``ps -o rss=``), i.e. the standing memory price of the process route;
  * the pickle bytes crossing the pipe per solve, both directions, by
    wrapping ``coordinator._run_in_process``'s job and reply.

Cycles are driven through the real ``_async_update_data`` with the
network fetches replaced by no-ops and the price/weather series seeded as
``tests/golden.py:_capture_coordinator`` seeds them.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h4_retained.py

EXPECTED (baseline 7dd68dd, Apple M1 8 GB, python 3.11, H4_CYCLES=8):
  coord_deep_bytes_slope_per_cycle  |slope| < 20 000 B/cycle
  worker_rss_mb_after_first         60 - 140 MiB (PROVISIONAL, RSS)
  worker_rss_slope_mb_per_solve     < 1.0 MiB (PROVISIONAL, RSS)
  job_pickle_bytes_per_solve        5 000 - 60 000 B (FINAL, bytes)
  reply_pickle_bytes_per_solve      20 000 - 200 000 B (FINAL, bytes)

PERTURBATION: ``H4_PERTURB=leak`` appends one 96-float list to
``coord._prices`` per cycle from the harness; ``coord_deep_bytes_slope_per_cycle``
must rise by ~800 B/cycle, proving the slope instrument is not flat by
construction. ``H4_CYCLES`` changes N.

BYTES ARE FINAL; RSS MiB are PROVISIONAL.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import asyncio  # noqa: E402
import pickle  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tracemalloc  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as CO  # noqa: E402

CYCLES = int(os.environ.get("H4_CYCLES", "8"))
PERTURB = os.environ.get("H4_PERTURB", "")

PIPE = {"job": 0, "reply": 0, "solves": 0}


def install_pipe_probe():
    orig = CO._run_in_process

    def probe(fn, args):
        try:
            PIPE["job"] += len(
                pickle.dumps((fn, args), protocol=pickle.HIGHEST_PROTOCOL)
            )
        except Exception:  # noqa: BLE001
            pass
        out = orig(fn, args)
        try:
            PIPE["reply"] += len(
                pickle.dumps(("ok", out), protocol=pickle.HIGHEST_PROTOCOL)
            )
        except Exception:  # noqa: BLE001
            pass
        PIPE["solves"] += 1
        return out

    CO._run_in_process = probe


def worker_rss_kb():
    w = CO._PROCESS_WORKER
    if w is None or w.poll() is not None:
        return -1
    try:
        out = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(w.pid)],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        return int(out) if out else -1
    except Exception:  # noqa: BLE001
        return -1


def deep_size(obj, seen=None, depth=0):
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen or depth > 8:
        return 0
    seen.add(oid)
    try:
        size = sys.getsizeof(obj)
    except Exception:  # noqa: BLE001
        return 0
    if isinstance(obj, np.ndarray):
        return int(obj.nbytes) + size
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            size += deep_size(k, seen, depth + 1) + deep_size(v, seen, depth + 1)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for v in list(obj):
            size += deep_size(v, seen, depth + 1)
    elif hasattr(obj, "__dict__") and not isinstance(obj, type):
        size += deep_size(vars(obj), seen, depth + 1)
    return size


def coord_collections(coord):
    out = {}
    for name, val in list(vars(coord).items()):
        if not name.startswith("_"):
            continue
        if isinstance(val, (list, dict, set, tuple)) or isinstance(val, np.ndarray):
            out[name] = val
    return out


def build_coordinator():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 200.0,
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08,
        "lower_floor_heat_loss": 0.07,
    }
    entry = FakeEntry(data=cfg)
    coord = CO.HeatPumpOptimizerCoordinator(hass, entry)
    start = C.START
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (start + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (start + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    async def _noop(*a, **kw):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._skip_solve_once = False
    return coord


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}  cycles={CYCLES}")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    install_pipe_probe()
    dt_util.freeze(C.START)
    tracemalloc.start()
    coord = build_coordinator()
    traced = []
    deep = []
    rss_worker = []
    try:
        for i in range(CYCLES):
            asyncio.run(coord._async_update_data())
            if PERTURB == "leak":
                coord._prices.append({"total": 0.0, "pad": [0.0] * 96})
            cur, _peak = tracemalloc.get_traced_memory()
            traced.append(cur)
            cols = coord_collections(coord)
            deep.append(sum(deep_size(v) for v in cols.values()))
            rss_worker.append(worker_rss_kb())
    finally:
        dt_util.freeze(None)
    peak_traced = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    for i, (t, d, r) in enumerate(zip(traced, deep, rss_worker)):
        C.result(f"cycle{i}.traced_bytes", t, "bytes")
        C.result(f"cycle{i}.coord_deep_bytes", d, "bytes")
        C.result(f"cycle{i}.worker_rss_kb_PROVISIONAL", r, "kB")

    def slope(series):
        tail = series[2:]
        if len(tail) < 2:
            return float("nan")
        n = len(tail)
        xs = list(range(n))
        mx = sum(xs) / n
        my = sum(tail) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, tail))
        den = sum((x - mx) ** 2 for x in xs)
        return num / den if den else float("nan")

    C.result("coord_deep_bytes_final", deep[-1], "bytes")
    C.result("coord_deep_bytes_slope_per_cycle", float(slope(deep)), "bytes/cycle")
    C.result("traced_bytes_slope_per_cycle", float(slope(traced)), "bytes/cycle")
    C.result("traced_peak_bytes", peak_traced, "bytes")
    C.result("parent_ru_maxrss_mb_PROVISIONAL",
             float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576.0),
             "MiB")
    live_rss = [r for r in rss_worker if r > 0]
    if live_rss:
        C.result("worker_rss_mb_after_first_PROVISIONAL",
                 float(live_rss[0] / 1024.0), "MiB")
        C.result("worker_rss_mb_final_PROVISIONAL",
                 float(live_rss[-1] / 1024.0), "MiB")
        C.result("worker_rss_slope_mb_per_solve_PROVISIONAL",
                 float(slope(live_rss) / 1024.0), "MiB/solve")
    C.result("solves_through_process_worker", PIPE["solves"], "solves")
    if PIPE["solves"]:
        C.result("job_pickle_bytes_per_solve",
                 PIPE["job"] // PIPE["solves"], "bytes")
        C.result("reply_pickle_bytes_per_solve",
                 PIPE["reply"] // PIPE["solves"], "bytes")
        C.result("pipe_bytes_per_day",
                 (PIPE["job"] + PIPE["reply"]) // PIPE["solves"]
                 * (24 * 60 // const.DEFAULT_OPTIMIZATION_INTERVAL), "bytes")

    cols = coord_collections(coord)
    ranked = sorted(((deep_size(v), k, len(v) if hasattr(v, "__len__") else -1)
                     for k, v in cols.items()), reverse=True)
    for size, name, n in ranked[:12]:
        C.result(f"collection.{name}", f"{size} bytes len={n}")
    C.telemetry()
    CO._shutdown_process_pool()


if __name__ == "__main__":
    main()
