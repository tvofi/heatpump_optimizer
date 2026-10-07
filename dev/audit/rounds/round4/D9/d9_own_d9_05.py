"""VERIFIER-OWN harness for D9-05 (seat verify-0-1, round 4).

Independent re-measurement of the D9-05 claim with a DIFFERENT instrument
from the finder's h9: h9 accumulated ``time.perf_counter`` (wall) inside
``_comfort_terms`` and divided by solve WALL; this harness accumulates
``time.process_time`` (CPU) inside the same hook and divides by solve CPU.
Under a loaded box (other verifier panels running) a wall share can drift;
a CPU share cannot. It also builds its own solve inputs directly from
``tests/profiles.py`` -- no d9common import -- so a bug in the shared
builder cannot propagate.

METRIC DEFINITIONS (one line each):
  own_comfort_calls_per_gradient = hooked count of
      HeatPumpOptimizer._comfort_terms entries / sum(njev) over every
      _scoped_minimize result in the solve            (count, FINAL)
  own_comfort_cpu_share_pct = 100 * process_time accumulated inside the
      _comfort_terms hook / whole-solve process_time  (CPU ratio)
  own_batch_cpu_share_pct   = the same for
      ThermalModel.simulate_trajectory_batch          (CPU ratio)
  own_rows_per_gradient     = hooked batch rows / sum(njev) (count, FINAL)

Null control: the same solve at the ``flat`` price profile -- the loop is a
property of the batch shape, so the shares must not move.

PERTURBATION: ``OWN_HORIZON=12`` halves the horizon; calls per gradient
must halve (the count tracks the batch width, not a constant).

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/d9_own_d9_05.py

EXPECTED (against the D9-05 claim): own_comfort_calls_per_gradient
96-99; own_comfort_cpu_share_pct 25-40; null-control delta within 5 pp.

Counts FINAL; CPU shares are ratios (contention-tolerant); no absolute
seconds are claimed.
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

import datetime as _dt  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

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
from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

START = _dt.datetime(2026, 1, 15, 0, 0)
HORIZON = float(os.environ.get("OWN_HORIZON", "24"))

S = {"ct_calls": 0, "ct_cpu": 0.0, "batch_calls": 0, "batch_rows": 0,
     "batch_cpu": 0.0, "njev": 0, "minimize_calls": 0}


def result(name, value, unit=""):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


def load1():
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def concurrent_procs():
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


def _fit(arr, n):
    arr = np.asarray(arr, dtype=float)
    if len(arr) >= n:
        return arr[:n]
    return np.tile(arr, int(np.ceil(n / len(arr))))[:n]


def build_and_solve(price_profile):
    """My own two-zone DHW solve, built directly from tests/profiles.py."""
    cfg = house(two_zone=True)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    n = int(HORIZON / DT)
    opt_cfg = OptimizationConfig(
        horizon_hours=HORIZON,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    price_series = _fit(prices(price_profile, START), n)
    outdoor, wind, rain, solar = (
        _fit(a, n) for a in weather("winter_cold", START)
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
    optimizer = HeatPumpOptimizer(ThermalModel(params), opt_cfg)
    p0 = time.process_time()
    optimizer.optimize(
        initial, price_series, outdoor, wind, rain, solar, START,
        None, None, None, None, None, None, None,
    )
    return time.process_time() - p0


def install_hooks():
    orig_ct = OPT.HeatPumpOptimizer._comfort_terms
    orig_batch = TM.ThermalModel.simulate_trajectory_batch
    orig_min = OPT._scoped_minimize

    def ct(self, *a, **kw):
        t0 = time.process_time()
        try:
            return orig_ct(self, *a, **kw)
        finally:
            S["ct_cpu"] += time.process_time() - t0
            S["ct_calls"] += 1

    def batch(self, initial_state, power_matrix, *a, **kw):
        m = np.asarray(power_matrix)
        S["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        S["batch_calls"] += 1
        t0 = time.process_time()
        try:
            return orig_batch(self, initial_state, power_matrix, *a, **kw)
        finally:
            S["batch_cpu"] += time.process_time() - t0

    def smin(*a, **kw):
        res = orig_min(*a, **kw)
        S["minimize_calls"] += 1
        S["njev"] += int(getattr(res, "njev", 0) or 0)
        return res

    OPT.HeatPumpOptimizer._comfort_terms = ct
    TM.ThermalModel.simulate_trajectory_batch = batch
    OPT._scoped_minimize = smin


def reset():
    S.update(ct_calls=0, ct_cpu=0.0, batch_calls=0, batch_rows=0,
             batch_cpu=0.0, njev=0, minimize_calls=0)


def arm(name, price_profile):
    reset()
    solve_cpu = build_and_solve(price_profile)
    njev = S["njev"] or 1
    result(f"{name}.own_comfort_calls_per_solve", S["ct_calls"], "calls")
    result(f"{name}.own_comfort_calls_per_gradient",
           float(S["ct_calls"] / njev), "calls/grad")
    result(f"{name}.own_rows_per_gradient",
           float(S["batch_rows"] / njev), "rows/grad")
    result(f"{name}.own_njev", S["njev"], "grads")
    result(f"{name}.own_minimize_calls", S["minimize_calls"], "calls")
    # the non-batch calls: everything _comfort_terms does outside a batch row
    result(f"{name}.own_comfort_calls_minus_rows",
           S["ct_calls"] - S["batch_rows"], "calls")
    result(f"{name}.own_comfort_cpu_share_pct",
           float(100.0 * S["ct_cpu"] / solve_cpu), "pct")
    result(f"{name}.own_batch_cpu_share_pct",
           float(100.0 * S["batch_cpu"] / solve_cpu), "pct")
    result(f"{name}.own_comfort_over_batch_cpu",
           float(S["ct_cpu"] / S["batch_cpu"]) if S["batch_cpu"]
           else float("nan"))
    return dict(cpu=solve_cpu, ct=S["ct_cpu"], calls=S["ct_calls"],
                njev=S["njev"])


def main():
    print(f"# verifier-own D9-05 harness; baseline=7dd68dd; horizon={HORIZON}h")
    print(f"# procs_at_start={concurrent_procs()} load1={load1():.2f}")
    install_hooks()
    build_and_solve("winter_typical")  # warm caches; untimed
    a = arm("winter_typical", "winter_typical")
    b = arm("flat_NULL", "flat")
    result("own_null_control_share_delta_pp",
           float(100.0 * (b["ct"] / b["cpu"] - a["ct"] / a["cpu"])), "pp")
    result("own_null_control_calls_per_grad_delta",
           float(b["calls"] / max(b["njev"], 1)
                 - a["calls"] / max(a["njev"], 1)), "calls/grad")
    result("thread_factor", float("nan"))  # single-threaded CPU metric; see report
    result("load1", load1())
    result("swapins", swapins())
    result("concurrent_gate_procs", concurrent_procs())


if __name__ == "__main__":
    main()
