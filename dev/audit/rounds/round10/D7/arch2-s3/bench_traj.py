"""Can the scalar trajectory be the batch on one row? Bit parity and per-call CPU, per plant shape.

The census joins ``thermal_model._simulate_step_single`` / ``_simulate_step_two_zone`` /
``simulate_trajectory_batch`` (and ``simulate_trajectory`` / ``simulate_trajectory_with_dhw``). The
cheapest merge that removes a twin is ``simulate_trajectory = simulate_trajectory_batch on one row``;
this measures whether that costs CPU, which is the brief's bar (a merge that slows the solve on a
Raspberry-Pi-class host is not sound).

Metric: per plant shape (1z, 2z, 2z valve, 1z learned gains), thread CPU per call of
``ThermalModel.simulate_trajectory`` (scalar) and of ``simulate_trajectory_batch`` with B=1, n=96,
median of 7 blocks x 40 calls; ratio = batch_B1 / scalar. Plus ``parity_mismatch`` = arrays (room,
slab, upper, lower, buffer, refused) whose bytes differ between the scalar tuple and the B=1 row.
Null control: the same scalar call timed twice in interleaved blocks (``scalar_vs_scalar``), whose
ratio is the noise floor. Second null: B=1 batch against itself.

Perturbation: --perturb multiplies the scalar path's work by running it twice per timed call; its
ratio against the batch must halve (moves down by ~2x).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/bench_traj.py [--root DIR] [--perturb]

Provisional (CPU timing): carries load1 and thread_factor. Thread-pinned. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else None
perturb = "--perturb" in sys.argv
if root is not None:
    os.chdir(root)
sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
from profiles import house, weather  # noqa: E402
sys.path.insert(0, "custom_components")
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)

START = __import__("datetime").datetime(2026, 1, 15)
N = 96


def model_for(two_zone: bool, valve: bool, gains: bool) -> ThermalModel:
    cfg = house(two_zone=two_zone, dhw=False)
    if valve:
        cfg["mixing_valve_mode"] = "manual"  # mixing_valve.MODE_MANUAL, a throttling mode
    p = ThermalParameters.from_config(cfg)
    if gains:
        p.internal_gains_profile = [0.3 + 0.02 * h for h in range(24)]
    return ThermalModel(p)


def main() -> int:
    out, wind, rain, solar = (np.asarray(a, dtype=float)[:N] for a in weather("winter_cold", START))
    ws = WeatherSeries(outdoor_temps=out, wind_speeds=wind, precipitation=rain, solar_radiation=solar)
    init = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(out[0]),
                        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                        buffer_tank_temperature=40.0)
    rng = np.random.default_rng(7)
    power = rng.uniform(0.0, 4.0, N)
    shapes = {"1z": (False, False, False), "2z": (True, False, False), "2z_valve": (True, True, False),
              "1z_gains": (False, False, True)}
    ratios, nulls = [], []
    mism_total = 0
    for name, args in shapes.items():
        m = model_for(*args)

        def scalar():
            r = m.simulate_trajectory(init, power, ws, start_hour=0.0)
            if perturb:
                r = m.simulate_trajectory(init, power, ws, start_hour=0.0)
            return r

        def batch1():
            return m.simulate_trajectory_batch(init, power[None, :], ws, start_hour=0.0)

        s, b = scalar(), batch1()
        pairs = [(s[0], b["room"][0]), (s[1], b["slab"][0]), (s[2], b["upper"][0]), (s[3], b["lower"][0]),
                 (s[4], b["buffer"][0]), (s[5], b["refused"][0])]
        mism = sum(1 for x, y in pairs if np.asarray(x, float).tobytes() != np.asarray(y, float).tobytes())
        mism_total += mism

        def block(fn):
            t = time.thread_time()
            for _ in range(40):
                fn()
            return (time.thread_time() - t) / 40 * 1e6

        ts, tb, ts2 = [], [], []
        for _ in range(7):
            ts.append(block(scalar))
            tb.append(block(batch1))
            ts2.append(block(scalar))
        ms, mb, ms2 = statistics.median(ts), statistics.median(tb), statistics.median(ts2)
        ratios.append(mb / ms)
        nulls.append(ms2 / ms)
        print(f"{name:10s} scalar {ms:9.1f} us  batch_B1 {mb:9.1f} us  ratio {mb / ms:6.3f}  "
              f"null {ms2 / ms:5.3f}  parity_mismatch {mism}")
    print(f"RESULT batch_B1_over_scalar_median={statistics.median(ratios):.3f} ratio")
    print(f"RESULT batch_B1_over_scalar_range={min(ratios):.3f}..{max(ratios):.3f} ratio")
    print(f"RESULT scalar_vs_scalar_null_range={min(nulls):.3f}..{max(nulls):.3f} ratio")
    print(f"RESULT parity_mismatch={mism_total} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.0 (thread_time, single-threaded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
