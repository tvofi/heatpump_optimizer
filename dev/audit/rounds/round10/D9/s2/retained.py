"""D9.M1 retained bytes (round 10, seat D9-s2).

Metric: deep sys.getsizeof of every attribute in a HeatPumpOptimizerCoordinator
instance's __dict__ (and of hass.states/bus listeners), sampled after cycle
N/2 and cycle N of a closed-loop run in which the frozen clock advances by the
optimization interval (30 min) per cycle and prices/forecast are re-injected
for now..now+48 h; reported as bytes/cycle slope over the second half, plus
tracemalloc current bytes slope. Key: per-attribute deep size of the
coordinator's own state, as production code leaves it after
HeatPumpOptimizerCoordinator.async_run_optimization.

Command (repo root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
      dev/audit/rounds/round10/D9/s2/retained.py [--cycles 192] [--config coord_all_features]
Perturbation: --cycles (96 -> 192): a bounded attribute keeps its slope near 0;
an untrimmed one keeps a constant positive slope and its absolute size doubles.
Expected (17f1c55fad1b, MacBook arm64): see REPORT.md; sizes are final, the
tracemalloc number is a byte count (final), wall time is provisional.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import gc
import sys
import time
import tracemalloc
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

ap = argparse.ArgumentParser()
ap.add_argument("--config", default="coord_all_features")
ap.add_argument("--cycles", type=int, default=192)
ap.add_argument("--top", type=int, default=10)
args = ap.parse_args()

t_cpu0, t_thr0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = golden.START


def deep(o, seen):
    i = id(o)
    if i in seen:
        return 0
    seen.add(i)
    if isinstance(o, np.ndarray):
        return o.nbytes + 112
    s = sys.getsizeof(o, 0)
    if isinstance(o, dict):
        for k, v in o.items():
            s += deep(k, seen) + deep(v, seen)
    elif isinstance(o, (list, tuple, set, frozenset)) or type(o).__name__ == "deque":
        for v in o:
            s += deep(v, seen)
    elif hasattr(o, "__dict__") and not isinstance(o, type) and \
            type(o).__module__.startswith("heatpump_optimizer"):
        s += deep(vars(o), seen)
    elif hasattr(o, "__slots__") and type(o).__module__.startswith("heatpump_optimizer"):
        for sl in getattr(type(o), "__slots__", ()):
            if hasattr(o, sl):
                s += deep(getattr(o, sl), seen)
    return s


SKIP = {"hass", "config_entry", "logger", "_listeners", "update_method",
        "_debounced_refresh", "_job"}


def sample(coord):
    out = {}
    for k, v in vars(coord).items():
        if k in SKIP:
            continue
        # fresh `seen` per attribute: shared sub-objects count in each owner
        out[k] = deep(v, set())
    return out


cfg = dict(golden.coordinator_scenarios()[args.config])
dt_util.freeze(START)
hass = FakeHass()
entry = FakeEntry(data=cfg)
coord = HeatPumpOptimizerCoordinator(hass, entry)


def inject(now):
    base = now.replace(minute=0, second=0, microsecond=0)
    coord._prices = [{"total": round(0.6 + 0.5 * ((base.hour + h) % 12) / 12.0, 4),
                      "starts_at": (base + timedelta(hours=h)).isoformat(),
                      "level": "NORMAL"} for h in range(48)]
    coord._weather_forecast = [{"datetime": (base + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0 + 3.0 * ((base.hour + h) % 24) / 24.0,
                                "wind_speed": 3.0, "precipitation": 0.0,
                                "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - ((base.hour + h) % 24)) / 12.0)) for h in range(48)]


half = args.cycles // 2
snaps = {}
tm = {}
tracemalloc.start()


async def run():
    now = START
    inject(now)
    await coord._update_current_state()
    coord.data = coord._build_data_dict()
    for c in range(1, args.cycles + 1):
        now = START + timedelta(minutes=30 * c)
        dt_util.freeze(now)
        inject(now)
        await coord._update_current_state()
        await coord.async_run_optimization()
        coord.data = coord._build_data_dict()
        if c in (half, args.cycles):
            gc.collect()
            snaps[c] = sample(coord)
            tm[c] = tracemalloc.get_traced_memory()[0]

asyncio.run(run())
dt_util.freeze(None)
tracemalloc.stop()

a, b = snaps[half], snaps[args.cycles]
n = args.cycles - half
growth = sorted(((b.get(k, 0) - a.get(k, 0), k) for k in b), reverse=True)
print(f"# top attributes by bytes/cycle over cycles {half}..{args.cycles}:")
for d, k in growth[:args.top]:
    print(f"#   {k} {a.get(k, 0)} -> {b[k]} ({d / n:.1f} B/cycle)")
print("# largest attributes at end:")
for k in sorted(b, key=lambda k: -b[k])[:args.top]:
    print(f"#   {k} {b[k]}")
tot_a, tot_b = sum(a.values()), sum(b.values())
print(f"RESULT cycles={args.cycles} count")
print(f"RESULT coord_deep_bytes_end={tot_b} bytes")
print(f"RESULT coord_slope_bytes_per_cycle={(tot_b - tot_a) / n:.1f} bytes")
print(f"RESULT top_growth_attr={growth[0][1]}")
print(f"RESULT top_growth_bytes_per_cycle={growth[0][0] / n:.1f} bytes")
print(f"RESULT tracemalloc_slope_bytes_per_cycle={(tm[args.cycles] - tm[half]) / n:.1f} bytes")
tf = (time.process_time() - t_cpu0) / max(1e-9, time.thread_time() - t_thr0)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=n/a")
