"""V3 (reach and class) harness for D0-s1-01, round 9.

Metric (one line): per two-zone DHW-on cell, drop = (objective_value shipped by
production - objective_value shipped with a 0.20x anchor keyed on _solve_space's
OWN init_base energy appended to its cold-start candidates) / |shipped|, read
from HeatPumpOptimizer.optimize(...).objective_value. The finder keys the anchor
on the baseline thermostat energy; this keys it on the energy the DHW path
already anchors its other seeds on, so it is an independent seed definition.
Extra arm (reach attack, MPC): the same cell re-solved once more with
production's own warm start (#1295) -- `_prev_shipped_plan` = the shipped plan,
identical inputs, the most favourable case for the warm start closing the gap --
drop_mpc = (shipped - warm-resolved objective_value) / |shipped|.
Energy consequence: SEK/day of the plan's energy at the cell's prices.

Command (repo root; stub venv or real-HA venv):
  PYTHONPATH=tests/hastub /root/venv314/bin/python tools/audit/round9/D0/verify-v3/D0-s1-01_reach.py [--flat]
  HPO_V3_BARE_PKG=1 /root/venvha/bin/python tools/audit/round9/D0/verify-v3/D0-s1-01_reach.py [--flat]
Instrumented symbol: heatpump_optimizer.optimizer:HeatPumpOptimizer._solve_space
(wrapped; the anchor rides in h.extra_starts on the warm_start-is-None call).
Perturbation: the anchor arm itself; control --flat (flat prices) and the
single-zone twin (no-op by construction: drop exactly 0).
Expected: drop_max ~0.25 % at winter prices, ~0 at flat; tolerance +-0.05 pp.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-vCPU Linux cloud box, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse, dataclasses
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
if os.environ.get("HPO_V3_BARE_PKG"):
    # Real-HA venv: homeassistant 2026.2.3's config_entries import fails on
    # CPython 3.14.0rc2 (mashumaro reads typing.ByteString), so the package
    # __init__ (a config-entry import) cannot load there. Bind the package as a
    # bare namespace so the solver modules import against the genuine
    # homeassistant package and that venv's numpy/scipy.
    import types
    _pkg = types.ModuleType("heatpump_optimizer")
    _pkg.__path__ = [os.path.join("custom_components", "heatpump_optimizer")]
    sys.modules["heatpump_optimizer"] = _pkg
import numpy as np
from datetime import datetime
from unittest import mock
from profiles import prices as P_prices, weather as P_weather, house
import heatpump_optimizer.optimizer as om
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

START = datetime(2026, 1, 15)
REAL_SOLVE = HeatPumpOptimizer._solve_space


def build(tz, dhw, pp, wp, flat):
    p = ThermalParameters.from_config(house(two_zone=tz))
    p.dhw_enabled = dhw
    o = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0,
        min_temp=17.0, max_temp=23.0))
    pr = P_prices("flat" if flat else pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    return o, (st, pr, ot, wi, ra, so, START), pr


def anchored(self, dhw_plan, warm_start, h, p_max, n, dt, prs, init_base, *rest):
    if warm_start is None and self.model.params.two_zone_enabled:
        head = np.maximum(0.0, p_max - dhw_plan)
        e = float(np.sum(np.minimum(init_base, head)) * dt)
        seed = np.minimum(om._price_ranked_start(
            prs, e * om._DEEP_LOW_ENERGY_START_FRACTION, p_max, dt), head)
        h = dataclasses.replace(h, extra_starts=tuple(h.extra_starts or ()) + (seed,))
    return REAL_SOLVE(self, dhw_plan, warm_start, h, p_max, n, dt, prs, init_base, *rest)


def sek(r, pr):
    d = np.asarray(r.dhw_power_schedule, float) if r.dhw_power_schedule else 0.0
    return float(np.sum(pr * (np.asarray(r.power_schedule, float) + d)) * 0.25)


def cell(tz, pp, wp, flat):
    o, a, pr = build(tz, True, pp, wp, flat)
    ra = o.optimize(*a)
    o, a, _ = build(tz, True, pp, wp, flat)
    with mock.patch.object(HeatPumpOptimizer, "_solve_space", anchored):
        rb = o.optimize(*a)
    o, a, _ = build(tz, True, pp, wp, flat)
    o._prev_shipped_plan = np.asarray(ra.power_schedule, float).copy()
    rc = o.optimize(*a)
    fa, fb, fc = (float(r.objective_value) for r in (ra, rb, rc))
    return fa, fb, fc, sek(ra, pr), sek(rb, pr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--prices", default="winter_typical,winter_extreme,winter_narrow,winter_moderate")
    ap.add_argument("--weather", default="winter_cold,winter_mild")
    x = ap.parse_args()
    import numpy, scipy
    print(f"# numpy {numpy.__version__} scipy {scipy.__version__} "
          f"ha={'homeassistant' in sys.modules and getattr(sys.modules['homeassistant'], '__file__', '?')}")
    t0, th0 = time.process_time(), time.thread_time()
    drops, mpc, one = [], [], []
    pps = ["flat"] if x.flat else x.prices.split(",")
    for pp in pps:
        for wp in x.weather.split(","):
            fa, fb, fc, ea, eb = cell(True, pp, wp, x.flat)
            d, dm = (fa - fb) / abs(fa), (fa - fc) / abs(fa)
            drops.append(d); mpc.append(dm)
            print(f"CELL two|dhw|{pp}|{wp} prod {fa:.6f} anchor {fb:.6f} drop {100*d:+.4f}% "
                  f"| mpc-warm {fc:.6f} drop {100*dm:+.4f}% | SEK/day {ea:.3f}->{eb:.3f}", flush=True)
    # null: single-zone twin, anchor is a no-op by construction
    fa, fb, *_ = cell(False, pps[0], x.weather.split(",")[0], x.flat)
    one.append((fa - fb) / abs(fa))
    tag = "flat" if x.flat else "winter"
    print(f"RESULT {tag}_drop_max={100*max(drops):.4f} %")
    print(f"RESULT {tag}_drop_mean={100*np.mean(drops):.4f} %")
    print(f"RESULT {tag}_cells_over_0p1pct={sum(d > 1e-3 for d in drops)} count of {len(drops)}")
    print(f"RESULT {tag}_mpc_warm_drop_max={100*max(mpc):.4f} %")
    print(f"RESULT {tag}_single_zone_control_drop={100*one[0]:.4f} %")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
