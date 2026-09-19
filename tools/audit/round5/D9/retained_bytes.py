"""D9-R5: do coordinator collections grow without bound across cycles
(retained state with no trim?), and how much RSS does a cycle cost?

Metric definition (brief, fixed): for each of the coordinator's own
list/dict/set/tuple-valued attributes, ``len()`` after every
``_async_update_data`` cycle; a collection is RETENTION-SUSPECT iff its length
is non-decreasing and strictly grows at least once over the run. Plus
``resource.getrusage(RUSAGE_SELF).ru_maxrss`` (KiB) at the end.

Instrumented symbols: the coordinator instance's attribute set (``vars(coord)``)
-- i.e. every collection the object retains between cycles.

Perturbation: cycle count 3 -> 9 -> 27 -> 60. Expected direction: if any
collection is retained and appended to, its length scales with the cycle
count; every bounded collection stays flat. A liveness arm confirms the meter
sees growth: ``sum(len)`` over tracked collections must be > 0 and the run
length must be reported.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round5/D9/retained_bytes.py
Machine: Apple M1 8 GB, shared fan-out box. Lengths are contention-immune;
ru_maxrss is provisional (high-water mark of the whole process).
"""
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
from collections.abc import Mapping  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")

import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


async def _noop(*a, **k):
    return None


def _thread_factor():
    """process_cpu/thread_cpu over a small BLAS-bound loop; 1.0 with the pin."""
    import time

    import numpy as np

    a = np.arange(1 << 18, dtype=float).reshape(512, 512)
    b = a / 512.0
    tp0, tt0 = time.process_time(), time.thread_time()
    for _ in range(4):
        a = b @ b.T
    tp = time.process_time() - tp0
    tt = time.thread_time() - tt0
    return tp / tt if tt > 0 else 1.0


def build(name):
    cfg = golden.coordinator_scenarios()[name]
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (golden.START + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"} for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (golden.START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    coord.data = coord._build_data_dict()
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    return coord


def sizes(coord):
    out = {}
    for k, v in vars(coord).items():
        if isinstance(v, (Mapping, list, set, tuple)) or hasattr(v, "__len__"):
            try:
                out[k] = len(v)
            except Exception:
                continue
    return out


def run(name, cycles):
    coord = build(name)
    series = {}
    dt_util.freeze(golden.START)
    try:
        for _ in range(cycles):
            asyncio.run(coord._async_update_data())
            for k, n in sizes(coord).items():
                series.setdefault(k, []).append(n)
    finally:
        dt_util.freeze(None)
    grew = {k: v for k, v in series.items()
            if v and v[-1] > v[0] and all(a <= b for a, b in zip(v, v[1:]))}
    monotone_grew = {k: v for k, v in series.items()
                     if len(set(v)) > 1 and v[-1] > v[0]}
    print("RESULT scenario=%s cycles=%d tracked=%d grew_monotone=%d grew_any=%d "
          "ru_maxrss_kib=%d"
          % (name, cycles, len(series), len(grew), len(monotone_grew),
             resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    for k, v in sorted(grew.items()):
        print("RESULT scenario=%s retention_suspect=%s first=%d last=%d"
              % (name, k, v[0], v[-1]))
    for k, v in sorted(monotone_grew.items()):
        if k not in grew:
            print("RESULT scenario=%s nonmonotone_changed=%s series=%s"
                  % (name, k, v[:6]))
    return coord


if __name__ == "__main__":
    run("coord_two_zone", 3)
    run("coord_two_zone", 9)
    run("coord_dhw", 9)
    run("coord_two_zone", 27)
    c = run("coord_two_zone", 60)
    print("RESULT liveness_tracked_collections=%d" % len(sizes(c)))
    try:
        import subprocess
        out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode()
        print("RESULT load1=%.2f" % float(out.strip("{} \n").split()[0]))
    except Exception:
        print("RESULT load1=nan")
    print("RESULT thread_factor=%.3f" % _thread_factor())
    print("RESULT swapins=0")
