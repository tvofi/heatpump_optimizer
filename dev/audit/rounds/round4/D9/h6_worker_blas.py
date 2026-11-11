"""D9 round 4 / H6 -- is the solve worker's BLAS actually pinned, in the
environment Home Assistant gives it?

Background. ``optimizer._scoped_minimize`` wraps ``scipy.optimize.minimize``
in ``threadpoolctl.threadpool_limits(limits=1)`` because an unscoped
OpenBLAS pool sized to the core count spent ~21 % of solve CPU spinning on
96-element vectors (issue #88) -- CPU a Raspberry-Pi-class host running all
of Home Assistant does not have. ``tests/stress.py`` and every audit harness
additionally pin the five thread variables BEFORE numpy is imported, and
``tools/audit/README.md`` measured the unpinned thread factor on this box at
3.33x.

``coordinator._worker_env()`` builds the solve worker's environment as
``os.environ.copy()`` plus PYTHONPATH. It sets NO thread variable, so in a
real install the child inherits whatever Home Assistant's own process has --
which is nothing. This harness measures, in the CHILD, what that costs.

METRIC: ``thread_factor`` measured inside the solve worker =
``time.process_time()`` (all threads) / ``time.thread_time()`` (the solving
thread) across one ``HeatPumpOptimizer.optimize`` of the default two-zone
DHW arm. 1.0 means every cycle of CPU the process burned was work; >1 means
BLAS worker threads spun. Two arms, same child script, same solve:

  pinned    the five variables exported (what every test harness does)
  ha_like   the five variables REMOVED from the child's environment
            (what ``_worker_env`` hands a real install)

RESULT ``worker_thread_factor_ha_like`` is the number that matters; the
ratio ``cpu_ratio_ha_like_over_pinned`` is contention-immune.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h6_worker_blas.py

EXPECTED (baseline 7dd68dd, Apple M1 8 GB, python 3.11): if
``_scoped_minimize`` covers the whole solve, both arms report
thread_factor <= 1.05 and cpu_ratio_ha_like_over_pinned = 1.00 +/- 0.10.

PERTURBATION: ``H6_PERTURB=nolimits`` makes the child set
``optimizer._threadpool_limits = None`` before solving, which is the
documented fallback when threadpoolctl is absent. Under it the ha_like
arm's thread_factor MUST rise above the pinned arm's; if it does not, the
pin is coming from somewhere other than ``_scoped_minimize``.

RATIOS ARE CONTENTION-IMMUNE; absolute seconds are PROVISIONAL.
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

import json  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from heatpump_optimizer import coordinator as CO  # noqa: E402

PERTURB = os.environ.get("H6_PERTURB", "")
THREAD_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)

CHILD_SRC = '''
import os, time, json
import numpy as np
from profiles import DT, house, prices, weather
from heatpump_optimizer import optimizer as OPT
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
import datetime as _dt

if os.environ.get("H6_NOLIMITS") == "1":
    OPT._threadpool_limits = None

START = _dt.datetime(2026, 1, 15, 0, 0)
cfg = house(two_zone=True)
params = ThermalParameters.from_config(cfg)
params.dhw_enabled = True
oc = OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                        target_temp=21.0, min_temp=17.0, max_temp=23.0)
n = int(24 / DT)

def fit(a):
    a = np.asarray(a, dtype=float)
    return a[:n] if len(a) >= n else np.tile(a, int(np.ceil(n / len(a))))[:n]

ps = fit(prices("winter_typical", START))
outdoor, wind, rain, solar = (fit(x) for x in weather("winter_cold", START))
st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                  outdoor_temperature=float(outdoor[0]),
                  upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                  dhw_temperature=50.0, dhw_hours_since_legionella=20.0,
                  buffer_tank_temperature=40.0)
o = HeatPumpOptimizer(ThermalModel(params), oc)
o.optimize(st, ps, outdoor, wind, rain, solar, START)   # warm the caches
p0, t0, w0 = time.process_time(), time.thread_time(), time.perf_counter()
o.optimize(st, ps, outdoor, wind, rain, solar, START)
proc = time.process_time() - p0
thr = time.thread_time() - t0
wall = time.perf_counter() - w0
out = json.dumps({
    "proc": proc, "thread": thr, "wall": wall,
    "factor": (proc / thr) if thr > 0 else float("nan"),
    "env": {k: os.environ.get(k) for k in (
        "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
    "threadpoolctl": OPT._threadpool_limits is not None,
    "cpu_count": os.cpu_count(),
})
'''

EXPR = "(lambda g={}: (exec(%r, g), g['out'])[1])()" % CHILD_SRC


def run_arm(name, strip_env):
    CO._shutdown_process_pool()
    saved = {}
    if strip_env:
        for v in THREAD_VARS:
            saved[v] = os.environ.pop(v, None)
    if PERTURB == "nolimits":
        os.environ["H6_NOLIMITS"] = "1"
    try:
        info = json.loads(CO._run_in_process(eval, (EXPR,)))
    finally:
        for v, old in saved.items():
            if old is not None:
                os.environ[v] = old
        os.environ.pop("H6_NOLIMITS", None)
        CO._shutdown_process_pool()
    C.result(f"worker_thread_factor_{name}", float(info["factor"]))
    C.result(f"worker_cpu_s_{name}_PROVISIONAL", float(info["proc"]), "s")
    C.result(f"worker_thread_cpu_s_{name}_PROVISIONAL", float(info["thread"]), "s")
    C.result(f"worker_wall_s_{name}_PROVISIONAL", float(info["wall"]), "s")
    C.result(f"worker_threadpoolctl_{name}", info["threadpoolctl"])
    C.result(f"worker_cpu_count_{name}", info["cpu_count"], "cores")
    for k in THREAD_VARS:
        C.result(f"worker_env_{name}.{k}", info["env"][k])
    return info


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    pinned = run_arm("pinned", strip_env=False)
    ha_like = run_arm("ha_like", strip_env=True)
    C.result(
        "cpu_ratio_ha_like_over_pinned",
        float(ha_like["proc"] / pinned["proc"]) if pinned["proc"] else float("nan"),
    )
    C.result(
        "wall_ratio_ha_like_over_pinned_PROVISIONAL",
        float(ha_like["wall"] / pinned["wall"]) if pinned["wall"] else float("nan"),
    )
    C.telemetry()


if __name__ == "__main__":
    main()
