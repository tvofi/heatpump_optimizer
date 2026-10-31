"""D2-s2-01's ruling step 2 (#201 comment 6240984157): re-select the cell of
tests/optimality.py's stop-rule (ftol) check when its own cell stops
separating.

Metric, one line: per candidate cell, the gap by which each loosened-ftol
arm's plan costs more than production's, on the check's own cost rule, under
whichever BLAS kernel the run selects (OPENBLAS_CORETYPE).

A cell is (two_zone, price profile, weather profile) on the check's house,
DHW on, the check's initial state and start date. The arms are the ones
k1725_blas_kernel_gap.py races at the check's cell:
  prod      -- the production solve (ftol 1e-6 at both sites);
  both_1e2 / both_1e3 -- every _scoped_minimize call, multi-start refinement
              and restart polish alike, at the loosened ftol;
  loose_1e3 -- the round-4 single-site class (multi-start refinement
              loosened, restart restored to production's ftol).
A gap is 100 * (arm - prod) / arm, the check's own expression; a cell can
carry the check only if every loosened arm's gap is positive on every kernel,
and the bound is half the smallest of them (the ruling's derivation).

Null control: `--perturb` loosens PRODUCTION itself to the both-sites 1e-2
stop rule (the failure the check exists to catch); every gap of the cell the
check is moved to must then read zero for both_1e2, the construction by which
the check goes red.

Run from the repository root, once per kernel:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_ftol_cell_search.py [--perturb] [--cells tz:price:weather,...]

It prints an environment line, one RESULT line per cell, and the contract's
thread_factor/load1/swapins lines (dev/audit/README.md).
"""
import argparse
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = str(repo_root(__file__))
os.chdir(ROOT)
for _part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(ROOT, _part))

import numpy as np  # noqa: E402

from profiles import DT, house, prices, solve_inputs, weather  # noqa: E402
from heatpump_optimizer import optimizer as optm  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)

PRICES = ("winter_typical", "winter_extreme", "winter_moderate",
          "winter_narrow", "shoulder", "flat")
WEATHERS = ("winter_cold", "winter_mild", "shoulder")
START = datetime(2026, 1, 15)


def env_line():
    core = os.environ.get("OPENBLAS_CORETYPE") or ""
    env = dict(os.environ, OPENBLAS_VERBOSE="2")
    p = subprocess.run([sys.executable, "-c", "import numpy"], env=env,
                       capture_output=True, text=True, timeout=60)
    for line in p.stderr.splitlines():
        if "Core:" in line:
            core = line.split("Core:", 1)[1].strip()
    cpu = "unknown"
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith(("model name", "Hardware")):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                             capture_output=True, text=True).stdout.strip()
    print(f"environment: core={core} cpu={cpu} numpy={np.__version__} "
          f"python={sys.version.split()[0]}", flush=True)


def setup(two_zone, price, wx):
    """optimality.py's _dhw_setup, with the price and weather profiles free."""
    p = ThermalParameters.from_config(house(two_zone=two_zone))
    p.dhw_enabled = True
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price, START)
    ot, wi, ra, so = weather(wx, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st


def score(m, pw, st, ot, wi, ra, so, pr, min_t=16.5):
    """optimality.py's score_plan cost and comfort violation."""
    room = m.simulate_trajectory(st, pw, WeatherSeries(
        outdoor_temps=ot, wind_speeds=wi, precipitation=ra,
        solar_radiation=so), dt_hours=DT)[0]
    return (float(np.sum(pr * pw * DT)),
            float(np.maximum(0, min_t - room[1:]).sum()))


full_scoped = optm._scoped_minimize
full_ms = optm._multi_start_minimize
full_restart = optm._lbfgsb_restart


def _ftol_scoped(ftol):
    def wrap(*a, **kw):
        kw = dict(kw)
        opts = dict(kw.get("options") or {})
        opts["ftol"] = ftol
        kw["options"] = opts
        return full_scoped(*a, **kw)
    return wrap


def _restart_tight(*a, **kw):
    with mock.patch.object(optm, "_scoped_minimize", full_scoped):
        return full_restart(*a, **kw)


def _loose_ms(ftol):
    def wrap(objective, starts, bounds, *a, **kw):
        with mock.patch.object(optm, "_lbfgsb_restart", _restart_tight):
            with mock.patch.object(optm, "_scoped_minimize", _ftol_scoped(ftol)):
                return full_ms(objective, starts, bounds, *a, **kw)
    return wrap


def _both_ms(ftol):
    def wrap(objective, starts, bounds, *a, **kw):
        with mock.patch.object(optm, "_scoped_minimize", _ftol_scoped(ftol)):
            return full_ms(objective, starts, bounds, *a, **kw)
    return wrap


ARMS = (("both_1e2", _both_ms(1e-2)), ("both_1e3", _both_ms(1e-3)),
        ("loose_1e3", _loose_ms(1e-3)))


def solve(cell, ms_patch):
    o, m, pr, ot, wi, ra, so, st = setup(*cell)
    kw = dict(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
              precipitation=ra, solar_radiation=so, start_time=START)
    if ms_patch is None:
        r = o.optimize(inputs=solve_inputs(**kw))
    else:
        with mock.patch.object(optm, "_multi_start_minimize", ms_patch):
            r = o.optimize(inputs=solve_inputs(**kw))
    return score(m, np.asarray(r.power_schedule, dtype=float),
                 st, ot, wi, ra, so, pr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true",
                    help="loosen production itself to the both-sites 1e-2 rule")
    ap.add_argument("--cells", default="",
                    help="tz:price:weather,... (tz 1 or 0); default every cell")
    a = ap.parse_args()
    if a.cells:
        cells = [(c.split(":")[0] == "1", c.split(":")[1], c.split(":")[2])
                 for c in a.cells.split(",")]
    else:
        cells = [(tz, p, w) for tz in (True, False) for p in PRICES
                 for w in WEATHERS]
    env_line()
    prod_patch = _both_ms(1e-2) if a.perturb else None
    for cell in cells:
        t0 = time.perf_counter()
        c0, v0 = solve(cell, prod_patch)
        parts = [f"prod={c0:.4f}"]
        gaps = []
        viol = v0
        for name, patch in ARMS:
            c, v = solve(cell, patch)
            viol = max(viol, v)
            g = 100.0 * (c - c0) / c if c else 0.0
            gaps.append(g)
            parts.append(f"{name}={c:.4f} gap_{name}={g:+.3f}")
        tz, p, w = cell
        print(f"RESULT cell={int(tz)}:{p}:{w} {' '.join(parts)} "
              f"min_gap={min(gaps):+.3f} max_viol={viol:.4f} "
              f"perturb={int(a.perturb)} wall={time.perf_counter() - t0:.1f}s",
              flush=True)
    factor = (time.process_time() / time.thread_time()
              if time.thread_time() else 1.0)
    print(f"RESULT thread_factor={factor:.3f}", flush=True)
    try:
        with open("/proc/loadavg") as fh:
            load1 = fh.read().split()[0]
    except OSError:
        load1 = "unknown"
    print(f"RESULT load1={load1}", flush=True)
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}",
          flush=True)


if __name__ == "__main__":
    main()
