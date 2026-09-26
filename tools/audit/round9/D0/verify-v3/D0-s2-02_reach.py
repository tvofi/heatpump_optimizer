"""V3 (reach and class) harness for D0-s2-02, round 9.

Metric (one line): per cell, gap = (objective_value shipped by production -
objective_value shipped when every production _multi_start_minimize call also
gets 13 bang-bang seeds at fractions LADDER of the bounds' max energy) /
|shipped|, read end to end from HeatPumpOptimizer.optimize(...).objective_value
at the production 24 h horizon. The finder races the FIRST seam call's recorded
objective with a re-polish; this measures the shipped plan with no polish arm,
so the stop-rule residue of D0-s2-01 is not folded in.
Extra arm (reach attack, MPC): production re-solved with its own warm start
(#1295, `_prev_shipped_plan` = shipped plan, identical inputs).
Energy consequence: SEK/day of the plan's energy at the cell's prices.

Command (repo root):
  PYTHONPATH=tests/hastub /root/venv314/bin/python tools/audit/round9/D0/verify-v3/D0-s2-02_reach.py [--prices shoulder|flat]
  HPO_V3_BARE_PKG=1 /root/venvha/bin/python tools/audit/round9/D0/verify-v3/D0-s2-02_reach.py
Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize
(candidates extended in memory). Perturbation: that extension.
Control: --prices flat. Expected: see the V3 report; tolerance +-0.05 pp.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-vCPU Linux cloud box, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
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
REAL_MS = om._multi_start_minimize
LADDER = (0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)


def build(tz, dhw, pp, wp, horizon):
    p = ThermalParameters.from_config(house(two_zone=tz))
    p.dhw_enabled = dhw
    o = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15, target_temp=21.0,
        min_temp=17.0, max_temp=23.0))
    pr = P_prices(pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    k, n = int(np.ceil(horizon / 24)), int(horizon * 4)
    pr, ot, wi, ra, so = (np.tile(a, k)[:n] for a in (pr, ot, wi, ra, so))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    return o, (st, pr, ot, wi, ra, so, START), pr


def make_ladder(pr):
    def ms(objective, candidates, bounds, *a, **kw):
        ub = np.array(bounds, float)[:, 1]
        n = len(ub)
        p = np.asarray(pr, float)[:n]
        extra = [np.minimum(om._price_ranked_start(
            p, float(ub.sum() * 0.25) * fr, float(ub.max()), 0.25), ub) for fr in LADDER]
        return REAL_MS(objective, list(candidates) + extra, bounds, *a, **kw)
    return ms


def sek(r, pr):
    d = np.asarray(r.dhw_power_schedule, float) if r.dhw_power_schedule else 0.0
    return float(np.sum(pr * (np.asarray(r.power_schedule, float) + d)) * 0.25)


def cell(tz, dhw, pp, wp, horizon):
    o, a, pr = build(tz, dhw, pp, wp, horizon)
    ra = o.optimize(*a)
    o, a, _ = build(tz, dhw, pp, wp, horizon)
    with mock.patch.object(om, "_multi_start_minimize", make_ladder(pr)):
        rb = o.optimize(*a)
    o, a, _ = build(tz, dhw, pp, wp, horizon)
    o._prev_shipped_plan = np.asarray(ra.power_schedule, float).copy()
    rc = o.optimize(*a)
    fa, fb, fc = (float(r.objective_value) for r in (ra, rb, rc))
    return fa, fb, fc, sek(ra, pr), sek(rb, pr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", default="shoulder")
    ap.add_argument("--weather", default="winter_cold,winter_mild,summer_cool,shoulder")
    ap.add_argument("--tz", default="0,1")
    ap.add_argument("--dhw", default="0,1")
    ap.add_argument("--horizon", type=int, default=24)
    x = ap.parse_args()
    import numpy, scipy
    print(f"# numpy {numpy.__version__} scipy {scipy.__version__} "
          f"ha={getattr(sys.modules.get('homeassistant'), '__file__', '?')}")
    t0, th0 = time.process_time(), time.thread_time()
    g, gm, de = [], [], []
    for pp in x.prices.split(","):
        for wp in x.weather.split(","):
            for tz in (bool(int(v)) for v in x.tz.split(",")):
                for dhw in (bool(int(v)) for v in x.dhw.split(",")):
                    fa, fb, fc, ea, eb = cell(tz, dhw, pp, wp, x.horizon)
                    d, dm = (fa - fb) / abs(fa), (fa - fc) / abs(fa)
                    g.append(d); gm.append(dm); de.append(ea - eb)
                    nm = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|h{x.horizon}"
                    print(f"CELL {nm:44s} prod {fa:10.5f} ladder {fb:10.5f} gap {100*d:+.4f}% "
                          f"| mpc-warm gap {100*dm:+.4f}% | SEK/day {ea:.3f}->{eb:.3f}", flush=True)
    g = np.array(g)
    print(f"RESULT gap_max={100*g.max():.4f} %")
    print(f"RESULT gap_min={100*g.min():.4f} %")
    print(f"RESULT gap_mean={100*g.mean():.4f} %")
    print(f"RESULT cells_over_0p1pct={int((g > 1e-3).sum())} count of {len(g)}")
    print(f"RESULT mpc_warm_gap_max={100*max(gm):.4f} %")
    print(f"RESULT energy_sek_saved_max={max(de):.4f} SEK/day")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
