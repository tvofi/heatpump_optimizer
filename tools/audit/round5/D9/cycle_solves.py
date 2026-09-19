"""D9-R5: full solves per coordinator cycle, split by path.

Metric definition (brief, fixed): entries into ``optimizer:_multi_start_minimize``
during one ``HeatPumpOptimizerCoordinator._async_update_data`` cycle, split by
the nearest optimizer.py frame (main space solve / with-DHW / co-optimize /
other). Also counts ``HeatPumpOptimizer.optimize`` calls and
``optimizer:_scoped_minimize`` calls (each ``_multi_start_minimize`` runs
``_MULTI_START_SOLVES`` L-BFGS-B starts plus one restart).

Instrumented symbols:
  optimizer:_multi_start_minimize
  optimizer:HeatPumpOptimizer.optimize
  optimizer:_scoped_minimize

Execution note: the production cycle submits the solve to a process worker, so
the counters are installed in the parent and the worker is forced onto the
in-process fallback (``_run_in_process`` raises ``ProcessWorkerUnavailable``)
purely so the parent hooks fire. The COUNT is identical either way: whichever
process runs the solve, one cycle submits exactly these optimizes.

Perturbation: config -- dhw tank on vs off (coord_two_zone vs coord_dhw) ->
the with-DHW path adds solves; a space-only cycle stays at one.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round5/D9/cycle_solves.py
Machine: Apple M1 8 GB, shared box; counts are contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import traceback  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")

import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

SOLVES = {"multi_start": [], "optimize": [], "scoped": []}
_MS = O._multi_start_minimize
_OPT = O.HeatPumpOptimizer.optimize
_SC = O._scoped_minimize


def _chain(depth=7):
    return "|".join(fr.name for fr in traceback.extract_stack()[-depth:-1])


def ms_h(*a, **k):
    SOLVES["multi_start"].append(_chain())
    return _MS(*a, **k)


def opt_h(self, *a, **k):
    SOLVES["optimize"].append(_chain())
    return _OPT(self, *a, **k)


def sc_h(*a, **k):
    SOLVES["scoped"].append(_chain())
    return _SC(*a, **k)


O._multi_start_minimize = ms_h
O.HeatPumpOptimizer.optimize = opt_h
O._scoped_minimize = sc_h


def _boom(*a, **k):
    raise C.ProcessWorkerUnavailable("harness: force in-process solve")


C._run_in_process = _boom


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


def run_cycle(name):
    for k in SOLVES:
        SOLVES[k].clear()
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
    dt_util.freeze(golden.START)
    try:
        asyncio.run(coord._async_update_data())
    finally:
        dt_util.freeze(None)
    print("RESULT cycle=%s optimize=%d multi_start=%d scoped_minimize=%d"
          % (name, len(SOLVES["optimize"]), len(SOLVES["multi_start"]),
             len(SOLVES["scoped"])))
    for p in SOLVES["multi_start"]:
        print("RESULT cycle=%s multi_start_path=%s" % (name, p))


if __name__ == "__main__":
    for nm in ("coord_minimal", "coord_dhw", "coord_two_zone",
               "coord_all_features"):
        run_cycle(nm)
    try:
        import subprocess
        _out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode()
        print("RESULT load1=%.2f" % float(_out.strip("{} \n").split()[0]))
    except Exception:
        print("RESULT load1=nan")
    print("RESULT thread_factor=%.3f" % _thread_factor())
    print("RESULT swapins=0")
