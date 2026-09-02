"""D9 metric 5: bytes retained by the coordinator per cycle.

Metric (binding, tools/audit/briefs/D9.md): after N coordinator cycles,
``tracemalloc`` traced bytes and a deep ``sys.getsizeof`` walk of every
attribute in ``vars(coordinator)`` (numpy arrays by ``nbytes``), reported as
a slope per cycle over the second half of the run, with the attributes that
grew most; plus ``ru_maxrss`` from a subprocess that runs N cycles (N = 12
and N = 48, the perturbation), and the persistence traffic the cycle causes
(Store saves per cycle and bytes per save, from the honest Store stub).

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h5_retained_bytes.py

Expected (baseline c398fc8; bytes, final -- deterministic inputs):
    deep-size slope of the coordinator's own collections a few KB per cycle
    or less (the trims in accuracy.py / coordinator.py hold); tracemalloc
    slope of the same order; top growers named
    perturbation N 12 -> 48: total retained delta grows in proportion to N
    where a slope exists, and ru_maxrss differs by less than the tracemalloc
    delta (numpy/scipy arena effects dominate RSS)

Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator (all
attributes), homeassistant.helpers.storage.Store (stub: SAVE_COUNTS/_DISK).
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import asyncio
import gc
import os
import resource
import subprocess
import sys
import tracemalloc
import types
from collections import deque
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as storage_stub  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
CONFIG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
}
SKIP_ATTRS = {"hass", "_background_tasks", "_unsub_timer", "_unsub_defrost", "pool"}
OPAQUE = (types.ModuleType, type, types.FunctionType, types.MethodType,
          types.BuiltinFunctionType, types.CoroutineType)


def deep_size(obj, seen: set) -> int:
    oid = id(obj)
    if oid in seen:
        return 0
    seen.add(oid)
    if isinstance(obj, OPAQUE):
        return 0
    if isinstance(obj, np.ndarray):
        return int(obj.nbytes) + sys.getsizeof(obj)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            size += deep_size(k, seen) + deep_size(v, seen)
    elif isinstance(obj, (list, tuple, set, frozenset, deque)):
        for x in obj:
            size += deep_size(x, seen)
    elif hasattr(obj, "__dict__"):
        size += deep_size(vars(obj), seen)
    elif hasattr(obj, "__slots__"):
        for s in obj.__slots__:
            if hasattr(obj, s):
                size += deep_size(getattr(obj, s), seen)
    return size


def make():
    hass = FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CONFIG))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    return hass, coord


def sizes_by_attr(coord) -> dict[str, int]:
    out = {}
    for name, value in vars(coord).items():
        if name in SKIP_ATTRS:
            continue
        out[name] = deep_size(value, set())
    return out


def run_cycles(n: int, instrument: bool, hook=None):
    hass, coord = make()
    hist_traced, hist_deep, per_attr = [], [], []
    saves_before = dict(storage_stub.SAVE_COUNTS)
    for i in range(n):
        dt_util.freeze(START + timedelta(hours=8, minutes=3 + 30 * i))
        coord.data = asyncio.run(coord._async_update_data())
        if instrument:
            gc.collect()
            hist_traced.append(tracemalloc.get_traced_memory()[0])
            by_attr = sizes_by_attr(coord)
            # Kept only at the two attribution cycles: retaining every
            # cycle's dict made the harness's own bookkeeping the largest
            # tracemalloc grower (6.5 KB/cycle) in the first version.
            if i in (n // 2, n - 1):
                per_attr.append(by_attr)
            hist_deep.append(sum(by_attr.values()))
            if hook is not None:
                hook(i)
    dt_util.freeze(None)
    saves = {k: v - saves_before.get(k, 0) for k, v in storage_stub.SAVE_COUNTS.items()}
    disk = {k: len(v) for k, v in storage_stub._DISK.items()}
    return coord, hist_traced, hist_deep, per_attr, saves, disk


def slope(ys: list[float]) -> float:
    half = ys[len(ys) // 2:]
    if len(half) < 2:
        return 0.0
    x = np.arange(len(half), dtype=float)
    return float(np.polyfit(x, np.asarray(half, dtype=float), 1)[0])


if len(sys.argv) > 2 and sys.argv[1] == "--child":
    n = int(sys.argv[2])
    run_cycles(n, instrument=False)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux kilobytes.
    print(f"CHILD maxrss_bytes={rss if sys.platform == 'darwin' else rss * 1024}")
    sys.exit(0)

N = 16
# tracemalloc makes the numpy-heavy solve ~15x slower (measured: 0.6 s -> 10 s
# a cycle), which is why N is 16 here and the RSS children run untraced.
tracemalloc.start(1)
SNAPS = {}


def _snap_hook(i):
    if i in (N // 2 - 1, N - 1):
        SNAPS[i] = tracemalloc.take_snapshot()


with d9lib.Clocks() as c:
    coord, traced, deep, per_attr, saves, disk = run_cycles(N, instrument=True, hook=_snap_hook)
tracemalloc.stop()

d9lib.result("cycles", N, "count")
d9lib.result("traced_after_cycle1", traced[0], "bytes")
d9lib.result(f"traced_after_cycle{N}", traced[-1], "bytes")
d9lib.result("traced_slope_second_half", slope(traced), "bytes_per_cycle")
d9lib.result("deep_after_cycle1", deep[0], "bytes")
d9lib.result(f"deep_after_cycle{N}", deep[-1], "bytes")
d9lib.result("deep_slope_second_half", slope(deep), "bytes_per_cycle")
mid, last = per_attr[0], per_attr[-1]
growth = sorted(((last[k] - mid.get(k, 0)) / (N - N // 2), k) for k in last)
for g, k in growth[-8:][::-1]:
    d9lib.result(f"grower.{k}", g, "bytes_per_cycle")
    d9lib.result(f"size.{k}", last[k], "bytes")
biggest = sorted(((v, k) for k, v in last.items()))[-6:][::-1]
for v, k in biggest:
    d9lib.result(f"largest.{k}", v, "bytes")
for key, count in sorted(saves.items()):
    d9lib.result(f"store_saves_per_cycle.{key}", count / N, "count")
    d9lib.result(f"store_bytes.{key}", disk.get(key, 0), "bytes")
d9lib.result("store_saves_per_cycle.total", sum(saves.values()) / N, "count")
d9lib.result("store_bytes_per_cycle.total",
             sum(disk.get(k, 0) * cnt for k, cnt in saves.items()) / N, "bytes")
d9lib.result("instrumented_cycle_cpu_mean", c.proc_ms / N, "ms_provisional")
# Who allocated the growth between the mid and final snapshots, by line:
# the integration's own lines first, then the top lines overall.
# The harness's own allocations and tracemalloc's are filtered out, so the
# growth reported is the integration's plus the libraries it calls.
_filters = [tracemalloc.Filter(False, __file__), tracemalloc.Filter(False, tracemalloc.__file__)]
a = SNAPS[N // 2 - 1].filter_traces(_filters)
b = SNAPS[N - 1].filter_traces(_filters)
stats = b.compare_to(a, "lineno")
own = [st for st in stats if "custom_components" in str(st.traceback)]
for st in own[:6]:
    frame = st.traceback[0]
    d9lib.result(f"growth_own.{os.path.basename(frame.filename)}:{frame.lineno}",
                 st.size_diff / (N - N // 2), "bytes_per_cycle")
for st in stats[:4]:
    frame = st.traceback[0]
    d9lib.result(f"growth_any.{os.path.basename(frame.filename)}:{frame.lineno}",
                 st.size_diff / (N - N // 2), "bytes_per_cycle")
d9lib.result("growth_total_traced_excl_harness", sum(st.size_diff for st in stats) / (N - N // 2), "bytes_per_cycle")
d9lib.result("growth_own_total", sum(st.size_diff for st in own) / (N - N // 2), "bytes_per_cycle")

for n in (12, 48):
    env = dict(os.environ)
    out = subprocess.run([sys.executable, __file__, "--child", str(n)],
                         capture_output=True, text=True, env=env, timeout=1800)
    line = [ln for ln in out.stdout.splitlines() if ln.startswith("CHILD")]
    value = int(line[0].split("=")[1]) if line else -1
    d9lib.result(f"ru_maxrss_after_{n}_cycles", value, "bytes_provisional")
d9lib.closing(c.thread_factor)
