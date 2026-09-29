"""L4 lead (raised by D0-s1) for D2-s2 / D2.M3 -- the comfort floor a two-zone plan ships below.

Metric (one line): floor_deg_steps = sum over steps and zones of max(0, min_temp - T_zone) of the
  SHIPPED plan (OptimizationResult.upper/lower_temp_trajectory[1:] on two-zone, room_temp_trajectory[1:]
  on single-zone), degree-steps (K x 15-min steps); per-zone for two-zone, room for single-zone.
  Count key: the trajectory the production optimize() returns (production seam), never an input.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/leads/l4_zone_floor.py [--perturb]
Grid: {single, two-zone} x DHW {on, off} x prices {winter_typical, winter_extreme, winter_moderate,
  winter_narrow, shoulder, flat} x weather winter_cold, 24 h, tests/golden.py:make (the stock house).
Perturbation (--perturb): optimizer._COMFORT_FLOOR_L1 2.0 -> 4.0 in memory, which gives each zone of
  the averaged two-zone penalty (0.5 x sum) the per-zone linear floor price single-zone already has.
  Expected direction: two-zone floor_deg_steps down (towards the single-zone arm).
Null control: the single-zone arm of every cell (same house, same prices), and the flat-price cells.
Expected (baseline 1936d5ca, box: 4-vCPU Linux container): two_zone_floor_deg_steps_sum=2.4672 (2 of 12
  cells, max 1.3144), single-zone 0.1471, flat 0; --perturb 0.8574. Deterministic on one BLAS build,
  +-0.05 degree-steps across builds.
Instrumented: optimizer:HeatPumpOptimizer.optimize, optimizer:HeatPumpOptimizer._comfort_terms (via
  the module constant _COMFORT_FLOOR_L1 it reads, as does _comfort_terms_batch).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

PRICES = ["winter_typical", "winter_extreme", "winter_moderate", "winter_narrow", "shoulder", "flat"]
if "--perturb" in sys.argv:
    optmod._COMFORT_FLOOR_L1 = 4.0


def cell(two_zone, dhw, pp):
    b = golden.make(two_zone=two_zone, dhw=dhw, price_profile=pp, weather_profile="winter_cold")
    opt = b["optimizer"]
    res = opt.optimize(b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"], b["solar"], golden.START)
    floor = float(opt.config.min_temp)
    if two_zone:
        u = np.asarray(res.upper_temp_trajectory[1:]); lo = np.asarray(res.lower_temp_trajectory[1:])
        du = float(np.maximum(0, floor - u).sum()); dl = float(np.maximum(0, floor - lo).sum())
        return du + dl, du, dl, float(min(u.min(), lo.min())), float(res.predicted_cost), floor
    rm = np.asarray(res.room_temp_trajectory[1:])
    d = float(np.maximum(0, floor - rm).sum())
    return d, d, 0.0, float(rm.min()), float(res.predicted_cost), floor


def main():
    t0, th0 = time.process_time(), time.thread_time()
    two, one = {}, {}
    for pp in PRICES:
        for dhw in (True, False):
            for tz in (False, True):
                tot, a, bb, tmin, cost, floor = cell(tz, dhw, pp)
                name = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}"
                (two if tz else one)[name] = tot
                print(f"CELL {name:30s} floor {floor:.1f} deg_steps {tot:8.4f} (upper/room {a:.4f} lower {bb:.4f}) "
                      f"coldest {tmin:.3f} C cost {cost:.3f}", flush=True)
    tv = np.array(list(two.values())); ov = np.array(list(one.values()))
    priced = np.array([v for k, v in two.items() if "|flat" not in k])
    print(f"RESULT two_zone_floor_deg_steps_sum={tv.sum():.4f} degree-steps")
    print(f"RESULT two_zone_cells_breaching={int((tv > 0.05).sum())} of {len(tv)}")
    print(f"RESULT two_zone_floor_deg_steps_max={tv.max():.4f} degree-steps")
    print(f"RESULT two_zone_floor_deg_steps_min={tv.min():.4f} degree-steps")
    print(f"RESULT two_zone_mean_drop_most_favourable={np.sort(tv)[:-1].mean():.4f} degree-steps (mean {tv.mean():.4f})")
    print(f"RESULT two_zone_priced_sum={priced.sum():.4f} degree-steps")
    print(f"RESULT two_zone_flat_sum={sum(v for k, v in two.items() if '|flat' in k):.4f} degree-steps")
    print(f"RESULT single_zone_floor_deg_steps_sum={ov.sum():.4f} degree-steps (null arm)")
    print(f"RESULT single_zone_cells_breaching={int((ov > 0.05).sum())} of {len(ov)}")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
