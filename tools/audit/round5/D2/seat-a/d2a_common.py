"""Shared helpers for round-5 D2 seat-a harnesses.

Runs from the repository export root with PYTHONPATH=tests/hastub. No writes
outside this seat directory and /tmp/audit-5/tmp/d2a.
"""
import os
import sys

# Thread pin BEFORE any numpy import (harness contract; tests/stress.py's pin).
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

# Private plan-data root for any Node-adjacent path (README trap list).
os.environ.setdefault("HPO_PLANDATA", "/tmp/audit-5/tmp/d2a/plandata.json")

_REPO_ROOT = os.path.abspath(os.getcwd())
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

SEAT_TMP = "/tmp/audit-5/tmp/d2a"
BASELINE_SHA = "1cc89e020fff9040a9d0090a27bf22bc1dd497f0"
MACHINE = "8-core Apple M1 (arm64), macOS 25.6.0, Python 3.11, numpy/OpenBLAS"


def epilogue(label: str = "") -> None:
    """thread_factor / load1 / swapins RESULT block every harness must print."""
    import time

    proc = time.process_time()
    try:
        import resource

        thread = time.thread_time()
        factor = proc / thread if thread > 0 else float("nan")
        ru = resource.getrusage(resource.RUSAGE_SELF)
        swapins = getattr(ru, "ru_nswap", 0) + getattr(ru, "ru_nsessions", 0)
    except Exception:
        factor, swapins = float("nan"), -1
    with open("/tmp/audit-5/tmp/d2a/load1.txt") as fh:
        load1 = float(fh.read().strip()) if os.path.exists(
            "/tmp/audit-5/tmp/d2a/load1.txt"
        ) else -1.0
    print("RESULT thread_factor=%.4f" % factor)
    print("RESULT load1=%.2f" % load1)
    print("RESULT swapins=%d" % int(swapins))


def concurrent_test_procs() -> int:
    import subprocess

    try:
        out = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, timeout=10
        ).stdout
        return sum(
            1 for ln in out.splitlines()
            if ("stress.py" in ln or "tests/run.sh" in ln) and "grep" not in ln
        )
    except Exception:
        return -1


def build_families():
    """The D2-a simulation families: every branch of the step functions.

    Returns (name -> dict with model/state/outdoor/wind/rain/solar), built
    through tests/golden.py:make so the configs are the audited ones.
    """
    from dataclasses import replace
    from tests.golden import make

    fams = {}
    fams["single_zone"] = make(two_zone=False, dhw=False)
    fams["two_zone"] = make(two_zone=True, dhw=False)
    fams["valve_store"] = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    )
    fams["valve_small"] = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 35.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    )
    fams["valve_direct_slab"] = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "topology_layout": "valve_upper_direct_slab",
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    )
    fams["wood_two_tank"] = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": 500.0,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0, "wood_tank_temperature": 55.0,
        },
    )
    fams["wood_coil"] = make(
        two_zone=True, dhw=True,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": 500.0,
            "dhw_wood_coil_enabled": True,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0, "wood_tank_temperature": 55.0,
        },
    )
    fams["flow_curve"] = make(
        two_zone=False, dhw=False,
        config_overrides={
            "flow_curve_cop_enabled": True, "heat_pump_max_power": 3.0,
            "upper_floor_heat_loss": 0.2, "lower_floor_heat_loss": 0.2,
        },
        param_overrides={"flow_curve_bias": 5.0},
    )
    return fams


def ext_forecast(n: int, peak: float = 8.0) -> "np.ndarray":
    """The detector's forecast shape (tests/golden.py:external_heat_for)."""
    import numpy as np

    steps = min(n, int(2.0 / 0.25))
    arr = np.zeros(n)
    for i in range(steps):
        arr[i] = peak * (1.0 - i / max(steps, 1))
    return arr
