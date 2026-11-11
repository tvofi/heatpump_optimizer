"""D0 round 8, seat s1: is the MPC warm-start candidate (#1295) aligned to the horizon it seeds?

Metric (one line): for a solve at t1 = t0 + interval, the objective J (production's own
captured objective at the seam's delivered x) of the refined warm-start candidate, and of
the shipped plan, with the previous plan handed over by coordinator._warm_seeded
UNSHIFTED (production) versus shifted by k = interval/15 min steps (the aligned seed).

Count key: which candidate index wins inside production's _multi_start_minimize (the
warm candidate is index 0 of the starts list, ahead of the structural seeds), and the
shipped OptimizationResult.objective_value.

Command (from the tree root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python3 tools/audit/round8/D0/s1_warm.py [--dhw 0|1] [--interval 30] [--prices ..] [--weather ..]

Arms at t1 (same optimizer inputs, only the seed differs):
  none     no warm start (cold)                       -- the null arm for the seed itself
  prod     coordinator._warm_seeded(coord, opt): previous power_schedule, unshifted
  aligned  the same plan rolled forward k steps (tail padded with its last value)
The perturbation (--perturb align) makes production's _warm_start_starts roll the plan by k
steps inside a try/finally; the count 'warm_misaligned' must go to zero.

Expected (baseline cdf82daa, 4-vCPU cloud container): see REPORT-s1.md.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
from datetime import timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from unittest import mock
from types import SimpleNamespace
from profiles import prices, weather
from heatpump_optimizer import optimizer as O
from heatpump_optimizer import coordinator as C
from heatpump_optimizer.thermal_model import ThermalState
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_race import setup, START, PRICES, WEATHER  # noqa: E402

ORIG_MS = O._multi_start_minimize
ORIG_WSS = O.HeatPumpOptimizer._warm_start_starts


def solve(opt, st, t, pp, wp, per_candidate):
    pr = prices(pp, t)
    ot, wi, ra, so = weather(wp, t)
    info = {}

    def cap(objective, cands, bounds, *a, **k):
        r = ORIG_MS(objective, cands, bounds, *a, **k)
        if "first" not in info:
            args = k.get("args", a[0] if a else ())
            info["first"] = True
            info["J"] = float(objective(r.x, *args))
            if per_candidate:
                info["per"] = [float(objective(ORIG_MS(objective, [c], bounds, *a, **k).x, *args))
                               for c in cands]
                info["pre"] = [float(objective(c, *args)) for c in cands]
        return r

    with mock.patch.object(O, "_multi_start_minimize", cap):
        res = opt.optimize(st, pr, ot, wi, ra, so, t)
    return res, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dhw", default="0")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default=",".join(WEATHER))
    ap.add_argument("--perturb", default="none")
    a = ap.parse_args()
    k = a.interval // 15
    cpu0, th0 = time.process_time(), time.thread_time()
    rows = []
    for pp in a.prices.split(","):
        for wp in a.weather.split(","):
            opt, m, pr, ot, wi, ra, so, st = setup(pp, wp, a.dhw == "1")
            r0, _ = solve(opt, st, START, pp, wp, False)
            t1 = START + timedelta(minutes=a.interval)
            n = int(round(a.interval / 15))
            ot1 = weather(wp, t1)[0]
            st1 = ThermalState(
                room_temperature=float(r0.room_temp_trajectory[n]),
                slab_temperature=float(r0.slab_temp_trajectory[n]),
                outdoor_temperature=float(ot1[0]),
                upper_floor_temperature=float(r0.room_temp_trajectory[n]),
                lower_floor_temperature=float(r0.room_temp_trajectory[n]),
                buffer_tank_temperature=(float(r0.buffer_temp_trajectory[n])
                                         if r0.buffer_temp_trajectory else 40.0))
            coord = SimpleNamespace(_optimization_result=r0)
            out = {}
            for arm in ("none", "prod", "aligned"):
                o1, *_ = setup(pp, wp, a.dhw == "1")
                if arm != "none":
                    C._warm_seeded(coord, o1)  # the production seat
                if arm == "aligned":
                    prev = np.asarray(o1._prev_shipped_plan, float)
                    o1._prev_shipped_plan = np.r_[prev[k:], np.full(k, prev[-1])]
                if a.perturb == "align" and arm == "prod":
                    def wss(self, n_steps, _k=k):
                        got = ORIG_WSS(self, n_steps)
                        if got is None:
                            return got
                        p = got[0]
                        return (np.r_[p[_k:], np.full(_k, p[-1])],)
                    with mock.patch.object(O.HeatPumpOptimizer, "_warm_start_starts", wss):
                        res, info = solve(o1, st1, t1, pp, wp, True)
                else:
                    res, info = solve(o1, st1, t1, pp, wp, arm != "none")
                out[arm] = (res, info)
            rp, ip = out["prod"]; ra_, ia = out["aligned"]; rn, inn = out["none"]
            # warm candidate is index 0; refined J of it vs refined J of the aligned seed
            wp_J, wa_J = ip["per"][0], ia["per"][0]
            struct_best = min(ip["per"][1:])
            row = dict(cell=f"{pp}|{wp}", Jn=rn.objective_value, Jp=rp.objective_value,
                       Ja=ra_.objective_value, warm_prod=wp_J, warm_al=wa_J,
                       struct=struct_best, pre_prod=ip["pre"][0], pre_al=ia["pre"][0],
                       costp=rp.predicted_cost, costa=ra_.predicted_cost,
                       win_prod=int(np.argmin(ip["per"])), win_al=int(np.argmin(ia["per"])))
            rows.append(row)
            print(f"CELL {row['cell']} J none={row['Jn']:.6f} prod={row['Jp']:.6f} aligned={row['Ja']:.6f} "
                  f"| warm-cand refined prod={wp_J:.6f} aligned={wa_J:.6f} struct_best={struct_best:.6f} "
                  f"| pre prod={row['pre_prod']:.4f} aligned={row['pre_al']:.4f} "
                  f"| win prod={row['win_prod']} aligned={row['win_al']} "
                  f"| cost {row['costp']:.3f} vs {row['costa']:.3f}")
    rel = np.array([(r["Jp"] - r["Ja"]) / abs(r["Jp"]) for r in rows])
    relw = np.array([(r["warm_prod"] - r["warm_al"]) / abs(r["warm_prod"]) for r in rows])
    prew = np.array([r["pre_prod"] - r["pre_al"] for r in rows])
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT warm_misaligned={sum(1 for r in rows if r['pre_prod'] != r['pre_al'])} count")
    print(f"RESULT warm_prescore_worse_cells={int(np.sum(prew > 1e-9))} count")
    print(f"RESULT warm_prescore_worse_median={float(np.median(prew)):.4e} objective_units")
    print(f"RESULT warm_refined_worse_cells_gt_1e-4={int(np.sum(relw > 1e-4))} count")
    print(f"RESULT warm_wins_prod={sum(1 for r in rows if r['win_prod'] == 0)} count")
    print(f"RESULT warm_wins_aligned={sum(1 for r in rows if r['win_al'] == 0)} count")
    print(f"RESULT shipped_gap_cells_gt_1e-4={int(np.sum(rel > 1e-4))} count")
    print(f"RESULT shipped_gap_cells_lt_-1e-4={int(np.sum(rel < -1e-4))} count")
    print(f"RESULT shipped_gap_max={rel.max():.4e} ratio")
    print(f"RESULT shipped_gap_min={rel.min():.4e} ratio")
    if len(rel) >= 5:
        print(f"RESULT shipped_gap_mean={rel.mean():.4e} ratio")
        print(f"RESULT shipped_gap_mean_drop_best={np.delete(rel, int(np.argmax(rel))).mean():.4e} ratio")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
