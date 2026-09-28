"""D9 round 4 / verifier 2 -- an independent re-measurement of D9-05.

The finder's h9 measures `_comfort_terms`'s share of the solve by
accumulating `time.perf_counter()` inside a wrapper around the method.
This harness measures the SAME quantity a different way: a statistical
sampling profiler (SIGPROF delivered every 1 ms of process CPU via
`signal.setitimer(ITIMER_PROF)`) that walks the interrupted Python stack
and counts the samples whose stack contains a frame executing
`HeatPumpOptimizer._comfort_terms` (resp.
`ThermalModel.simulate_trajectory_batch`). Instrumentation accumulation
and stack sampling have different failure modes -- a wrapper exaggerates
a cheap-but-hot function, a sampler under-attributes long C calls -- so
agreement between them is evidence, not tautology.

METRIC (one line): share of the solve's CPU samples whose stack contains
`_comfort_terms`, over one two-zone+DHW `optimize()` call, in percent.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/verify2_h9_sample.py

EXPECTED (baseline ae2a60b == 7dd68dd for production files, M1, py 3.11):
  comfort_share_by_sampling_pct  25 - 40 (finder instrumented: 33.331,
  quiet window: 32.6895; band +-5 pp)
  simulate_batch_share_by_sampling_pct  33 - 45
  comfort_calls_per_gradient  96 - 99

No stress.py import; no lock required. Counts are FINAL; the shares are
CPU-share ratios inside one process and contention-tolerant by design,
though taken here without the gate running.
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
import signal  # noqa: E402
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
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

START = _dt.datetime(2026, 1, 15, 0, 0)
SAMPLES = {"total": 0, "comfort": 0, "batch": 0}
COUNTS = {"comfort_calls": 0, "batch_rows": 0, "njev": 0}


def result(name, value, unit=""):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


def _fit(arr, n):
    arr = np.asarray(arr, dtype=float)
    if len(arr) >= n:
        return arr[:n]
    return np.tile(arr, int(np.ceil(n / len(arr))))[:n]


def make_solve():
    cfg = house(two_zone=True)
    no_dhw = os.environ.get("V2_NO_DHW", "") == "1"
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = not no_dhw
    opt_cfg = OptimizationConfig(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    n = int(24 / DT)
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
    opt = HeatPumpOptimizer(ThermalModel(params), opt_cfg)
    return opt, initial, _fit(prices("winter_typical", START), n), outdoor, wind, rain, solar


def _on_sigprof(signum, frame):
    f = frame
    while f is not None:
        if f.f_code.co_name == "_comfort_terms":
            SAMPLES["comfort"] += 1
            break
        f = f.f_back
    f = frame
    while f is not None:
        if f.f_code.co_name == "simulate_trajectory_batch":
            SAMPLES["batch"] += 1
            break
        f = f.f_back
    SAMPLES["total"] += 1


def install_counters(optimizer_module, thermal_module):
    orig_ct = optimizer_module.HeatPumpOptimizer._comfort_terms
    orig_batch = thermal_module.ThermalModel.simulate_trajectory_batch
    orig_min = optimizer_module._scoped_minimize

    def ct(self, *a, **kw):
        COUNTS["comfort_calls"] += 1
        return orig_ct(self, *a, **kw)

    def batch(self, initial_state, power_matrix, *a, **kw):
        m = np.asarray(power_matrix)
        COUNTS["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        return orig_batch(self, initial_state, power_matrix, *a, **kw)

    def smin(*a, **kw):
        res = orig_min(*a, **kw)
        COUNTS["njev"] += int(getattr(res, "njev", 0) or 0)
        return res

    optimizer_module.HeatPumpOptimizer._comfort_terms = ct
    thermal_module.ThermalModel.simulate_trajectory_batch = batch
    optimizer_module._scoped_minimize = smin


def main():
    from heatpump_optimizer import optimizer as OPT
    from heatpump_optimizer import thermal_model as TM

    out = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    procs = sum(
        1
        for line in out.splitlines()
        if "grep" not in line and ("stress.py" in line or "tests/run.sh" in line)
    )
    print(f"# procs_at_start={procs} load1={os.getloadavg()[0]:.2f}")
    install_counters(OPT, TM)
    opt, state, price_series, outdoor, wind, rain, solar = make_solve()
    # warm-up: imports, dispatch caches; not sampled, not counted
    for k in COUNTS:
        COUNTS[k] = 0
    opt.optimize(state, price_series, outdoor, wind, rain, solar, START,
                 None, None, None, None, None, None, None)

    for k in SAMPLES:
        SAMPLES[k] = 0
    for k in COUNTS:
        COUNTS[k] = 0
    signal.signal(signal.SIGPROF, _on_sigprof)
    # setitimer's third argument is the REARM interval; without it the
    # timer is one-shot and fires exactly once (the earlier "macOS does
    # not deliver PROF ticks" note was this bug, measured: 1 sample).
    which = signal.ITIMER_PROF
    signal.setitimer(which, 0.001, 0.001)
    p0, t0, w0 = time.process_time(), time.thread_time(), time.perf_counter()
    opt.optimize(state, price_series, outdoor, wind, rain, solar, START,
                 None, None, None, None, None, None, None)
    wall = time.perf_counter() - w0
    proc = time.process_time() - p0
    thr = time.thread_time() - t0
    signal.setitimer(which, 0.0)

    total = SAMPLES["total"]
    result("sampled_cpu_ms_approx", float(total), "ms")
    result("comfort_samples", SAMPLES["comfort"], "samples")
    result("simulate_batch_samples", SAMPLES["batch"], "samples")
    result("comfort_share_by_sampling_pct",
           float(100.0 * SAMPLES["comfort"] / total) if total else float("nan"),
           "pct-of-cpu-samples")
    result("simulate_batch_share_by_sampling_pct",
           float(100.0 * SAMPLES["batch"] / total) if total else float("nan"),
           "pct-of-cpu-samples")
    result("comfort_calls_per_solve", COUNTS["comfort_calls"], "calls")
    result("comfort_calls_per_gradient",
           float(COUNTS["comfort_calls"] / max(COUNTS["njev"], 1)), "calls/grad")
    result("batch_rows_per_gradient",
           float(COUNTS["batch_rows"] / max(COUNTS["njev"], 1)), "rows/grad")
    result("njev", COUNTS["njev"], "grads")
    result("solve_wall_s_PROVISIONAL", float(wall), "s")
    result("solve_cpu_s_PROVISIONAL", float(proc), "s")
    result("thread_factor", float(proc / thr) if thr else float("nan"))
    result("load1", float(os.getloadavg()[0]))
    result("concurrent_gate_procs", procs)


if __name__ == "__main__":
    main()
