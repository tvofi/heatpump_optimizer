"""Shared builders for the round-4 D9 harnesses.

NOT a harness: it prints nothing and measures nothing on its own. Every
harness in this directory pins the five BLAS thread variables in its own
first lines (before numpy is reachable) and then imports this module for
the path setup, the solve arms and the RESULT/telemetry printers.

No source-text cutting lives here: round 2's ``d9lib.py`` cut production
source by comment markers and its reproduction flickered as unrelated
files changed shape around it (tools/audit/README.md). Everything here
resolves production symbols by import.

Root rule: ``ROOT = os.getcwd()``. Every harness must be run from the
repository root with ``PYTHONPATH=tests/hastub``, which is also what
``tests/harness.py`` and ``tests/golden.py`` assume.
"""
from __future__ import annotations

import datetime as _dt
import os
import subprocess
import sys
import time

ROOT = os.getcwd()
for _p in (
    os.path.join(ROOT, "tests"),
    os.path.join(ROOT, "tests", "hastub"),
    os.path.join(ROOT, "custom_components"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer,
    OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

START = _dt.datetime(2026, 1, 15, 0, 0)
SEASON_PRICES = "winter_typical"
SEASON_WEATHER = "winter_cold"
FLAT_PRICES = "flat"


# --------------------------------------------------------------------------
# telemetry
# --------------------------------------------------------------------------
def result(name, value, unit=""):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


def load1():
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def concurrent_procs():
    """The count tools/audit/README.md asks to be printed beside a timing."""
    try:
        out = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:
        return -1
    n = 0
    for line in out.splitlines():
        if "grep" in line:
            continue
        if "stress.py" in line or "tests/run.sh" in line:
            n += 1
    return n


def swapins():
    try:
        out = subprocess.run(
            ["vm_stat"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:
        return -1
    for line in out.splitlines():
        if line.startswith("Swapins"):
            return int(line.split(":")[1].strip().rstrip("."))
    return -1


def thread_factor(work):
    """(factor, process_cpu, thread_cpu) over one call of ``work``."""
    p0, t0 = time.process_time(), time.thread_time()
    work()
    p1, t1 = time.process_time(), time.thread_time()
    proc, thr = p1 - p0, t1 - t0
    return (proc / thr if thr > 0 else float("nan")), proc, thr


def telemetry(tf=None):
    if tf is not None:
        result("thread_factor", float(tf))
    result("load1", load1())
    result("swapins", swapins())
    result("concurrent_gate_procs", concurrent_procs())


# --------------------------------------------------------------------------
# solve arms
# --------------------------------------------------------------------------
def _fit(arr, n):
    arr = np.asarray(arr, dtype=float)
    if len(arr) >= n:
        return arr[:n]
    return np.tile(arr, int(np.ceil(n / len(arr))))[:n]


def make_solve(
    two_zone=True,
    dhw=True,
    power_cap_kw=None,
    price_profile=SEASON_PRICES,
    horizon_hours=24,
):
    """Inputs for one ``HeatPumpOptimizer.optimize`` call.

    ``two_zone``/``dhw`` pick the topology; ``power_cap_kw`` below the DHW
    run power is the zero-range-bounds shape (a single-phase fuse guard),
    which is what ``_bounds_supported_by_batch`` used to refuse wholesale.
    ``price_profile="flat"`` is the null control.
    """
    cfg = house(two_zone=two_zone)
    if not dhw:
        for key in (
            "dhw_tank_volume",
            "dhw_setpoint",
            "dhw_min_temperature",
            "dhw_daily_consumption",
            "dhw_windows",
        ):
            cfg.pop(key, None)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = bool(dhw)
    opt_cfg = OptimizationConfig(
        horizon_hours=horizon_hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    n = int(horizon_hours / DT)
    price_series = _fit(prices(price_profile, START), n)
    outdoor, wind, rain, solar = (
        _fit(a, n) for a in weather(SEASON_WEATHER, START)
    )
    initial = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    caps = None if power_cap_kw is None else np.full(n, float(power_cap_kw))
    optimizer = HeatPumpOptimizer(ThermalModel(params), opt_cfg)
    return {
        "optimizer": optimizer,
        "state": initial,
        "prices": price_series,
        "outdoor": outdoor,
        "wind": wind,
        "rain": rain,
        "solar": solar,
        "caps": caps,
        "n": n,
    }


def run_solve(packed):
    o = packed
    return o["optimizer"].optimize(
        o["state"],
        o["prices"],
        o["outdoor"],
        o["wind"],
        o["rain"],
        o["solar"],
        START,
        None,
        None,
        None,
        None,
        None,
        None,
        o["caps"],
    )


def reference_solve():
    """``tests/stress.py:reference_solve`` -> (wall_s, proc_cpu_s, thread_cpu_s).

    Imported lazily: ``stress.py`` has a ``__main__`` guard, so importing
    it runs no sweep.
    """
    import stress

    return stress.reference_solve()
