"""D0 round 8, verifier v1: is the ftol gap REALISED once the plan is re-made every hour?

Metric (one line): per cell, closed-loop over 24 h (re-plan every 1 h, plant = the
optimizer's own model, two-zone, DHW off): d_adj = settled SEK(prod) - settled SEK(arm),
settled = realised energy SEK - (E_end - E_start) * p25(price) / COP(mean outdoor), E =
production HeatPumpOptimizer._stored_thermal_energy with _settlement_caps (s2_rolling's rule), with realised comfort (degree-hours of min(upper, lower) below min_temp 17,
and below target 21) and end-of-day zone mean temperature reported beside it; the arm
differs from production only in L-BFGS-B ftol at optimizer:_scoped_minimize.

Arms: prod (as shipped, ftol 1e-6), ftol12 (ftol 1e-12 at the seam). Null control: flat.
Perturbation: --prod-ftol 1e-12 turns prod into the arm (d_cost -> 0 by construction).

Command (tree root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  python3 tools/audit/round8/D0/v1_mpc.py [--cells p|w,p|w]
Baseline cdf82daa; 4-vCPU shared cloud container; no timings used.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime, timedelta
from unittest import mock
from profiles import DT, house, prices, weather
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

START = datetime(2026, 1, 15)
ORIG = O._scoped_minimize
CELLS = ("winter_typical|winter_cold,winter_extreme|winter_mild,shoulder|shoulder,"
         "winter_narrow|winter_cold,flat|winter_cold")


def loop(pp, wp, ftol):
    cfg = house(two_zone=True, dhw=False)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    m = ThermalModel(p)
    opt = O.HeatPumpOptimizer(m, O.OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    H = int(24 / DT)
    total = int(24 / DT)
    pr1 = np.asarray(prices(pp, START), float)  # one 24 h day, tiled so every re-plan sees 24 h
    pr = np.concatenate([pr1, pr1])
    w = [np.asarray(x, float) for x in weather(wp, START)]
    w = [np.concatenate([x, x]) if len(x) < total + H else x for x in w]
    ot, wi, ra, so = w
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    every = int(1 / DT)
    nfev = [0]

    def scoped(*a, **k):
        o = dict(k.get("options", {}))
        if ftol is not None:
            o["ftol"] = ftol
        k["options"] = o
        r = ORIG(*a, **k)
        nfev[0] += int(r.nfev)
        return r

    s0 = st
    cost = below = pull = 0.0
    plan = None
    with mock.patch.object(O, "_scoped_minimize", scoped):
        for s in range(total):
            now = START + timedelta(hours=s * DT)
            if s % every == 0:
                plan = opt.optimize(st, pr[s:s + H], ot[s:s + H], wi[s:s + H], ra[s:s + H],
                                    so[s:s + H], now)
            u = float(plan.power_schedule[s % every])
            room, slab, up, lo, _, _, _ = m.simulate_trajectory(
                initial_state=st, power_schedule=np.array([u]), outdoor_temps=ot[s:s + 1],
                wind_speeds=wi[s:s + 1], precipitation=ra[s:s + 1],
                solar_radiation=so[s:s + 1], dt_hours=DT)
            st = ThermalState(room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
                              outdoor_temperature=float(ot[s]),
                              upper_floor_temperature=float(up[-1]),
                              lower_floor_temperature=float(lo[-1]),
                              dhw_temperature=st.dhw_temperature,
                              buffer_tank_temperature=st.buffer_tank_temperature,
                              wood_tank_temperature=st.wood_tank_temperature)
            z = min(float(up[-1]), float(lo[-1]))
            cost += u * DT * float(pr[s])
            below += max(0.0, 17.0 - z) * DT
            pull += max(0.0, 21.0 - z) * DT
    end_t = 0.5 * (st.upper_floor_temperature + st.lower_floor_temperature)
    # settlement (s2_rolling's rule): value the change in stored heat at the day's p25 / COP
    caps = opt._settlement_caps(ot[:total])
    de = opt._stored_thermal_energy(st, False, caps) - opt._stored_thermal_energy(s0, False, caps)
    cop = max(m.compute_cop(float(np.mean(ot[:total]))), 1e-3)
    adj = cost - de * float(np.percentile(pr[:total], 25)) / cop
    return dict(adj=adj, cost=cost, below=below, pull=pull, end=end_t, slab=st.slab_temperature,
                nfev=nfev[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default=CELLS)
    ap.add_argument("--prod-ftol", type=float, default=None)
    a = ap.parse_args()
    cpu0, th0 = time.process_time(), time.thread_time()
    rows = []
    for c in a.cells.split(","):
        pp, wp = c.split("|")
        b = loop(pp, wp, a.prod_ftol)
        t = loop(pp, wp, 1e-12)
        d = b["adj"] - t["adj"]
        rows.append((pp, d, b, t))
        print(f"CELL {c} prod cost={b['cost']:.3f} below={b['below']:.4f} pull={b['pull']:.3f} "
              f"end={b['end']:.3f} slab={b['slab']:.3f} nfev={b['nfev']} | ftol12 cost={t['cost']:.3f} "
              f"below={t['below']:.4f} pull={t['pull']:.3f} end={t['end']:.3f} slab={t['slab']:.3f} "
              f"nfev={t['nfev']} | adj prod={b['adj']:.3f} ftol12={t['adj']:.3f} d_adj={d:+.4f} SEK ({100 * d / max(b['adj'], 1e-9):+.3f}%) d_raw={b['cost'] - t['cost']:+.3f}",
              flush=True)
    nf = [r for r in rows if r[0] != "flat"]
    fl = [r for r in rows if r[0] == "flat"]
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT nonflat_d_adjcost_mean={np.mean([r[1] for r in nf]) if nf else float('nan'):.4f} SEK/day")
    print(f"RESULT nonflat_d_adjcost_pct_mean={np.mean([100 * r[1] / r[2]['adj'] for r in nf]) if nf else float('nan'):.3f} pct")
    print(f"RESULT flat_d_adjcost_mean={np.mean([r[1] for r in fl]) if fl else float('nan'):.4f} SEK/day")
    print(f"RESULT cells_arm_cheaper={sum(1 for r in rows if r[1] > 1e-6)} count")
    print(f"RESULT cells_arm_dearer={sum(1 for r in rows if r[1] < -1e-6)} count")
    print(f"RESULT d_below_total={sum(r[3]['below'] - r[2]['below'] for r in rows):.4f} degree_hours")
    print(f"RESULT d_pull_total={sum(r[3]['pull'] - r[2]['pull'] for r in rows):.4f} degree_hours")
    print(f"RESULT nfev_total_ratio={sum(r[3]['nfev'] for r in rows) / max(1, sum(r[2]['nfev'] for r in rows)):.3f} ratio")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
